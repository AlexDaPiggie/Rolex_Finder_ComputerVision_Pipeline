"""
Train a variant head on CLIP embeddings and compare it with the zero-shot text prompts.

Labels come from reference numbers in retailer file names (see src/identify/benchmark_variants.py).
Final score for a variant = (1 - mix) * zero-shot probability + mix * head probability, taken within the
photo's family. Variants with no training photos keep the zero-shot score only.

    python -m src.training.variant_head --features features_out/variants.npz

Writes models/variant_head.pt (head, text embeddings, mix) and docs/benchmark_variants_head.md.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import torch
from transformers import CLIPModel, CLIPTokenizer

CLIP_ID = "openai/clip-vit-base-patch16"


def text_embeddings(catalog: dict, variants: list[str]) -> np.ndarray:
    """L2-normalised CLIP text embedding of each catalog variant description, in `variants` order."""
    texts = {v["id"]: v["clip_text"] for fam in catalog.values() for v in fam}
    model = CLIPModel.from_pretrained(CLIP_ID).eval()
    tokenizer = CLIPTokenizer.from_pretrained(CLIP_ID)
    out = []
    with torch.no_grad():
        for start in range(0, len(variants), 16):
            batch = tokenizer([texts[v] for v in variants[start:start + 16]], padding=True, truncation=True, max_length=77, return_tensors="pt")
            f = model.get_text_features(**batch)
            if not isinstance(f, torch.Tensor):
                f = f.pooler_output
            out.append((f / f.norm(dim=-1, keepdim=True)).numpy())
    return np.concatenate(out)


def train_head(x, y, num_classes, weight_decay=0.1, epochs=200, scale=30.0):
    torch.manual_seed(0)
    xt, yt = torch.tensor(x, dtype=torch.float32), torch.tensor(y)
    counts = np.bincount(y, minlength=num_classes).astype("float64")
    weights = torch.tensor((1 / np.maximum(counts, 1)) ** 0.5, dtype=torch.float32)
    head = torch.nn.Linear(x.shape[1], num_classes)
    opt = torch.optim.AdamW(head.parameters(), lr=3e-3, weight_decay=weight_decay)
    loss_fn = torch.nn.CrossEntropyLoss(weight=weights / weights.mean(), label_smoothing=0.05)
    for _ in range(epochs):
        perm = torch.randperm(len(xt))
        for s in range(0, len(xt), 2048):
            i = perm[s:s + 2048]
            opt.zero_grad()
            loss_fn(scale * head(xt[i]), yt[i]).backward()
            opt.step()
    return head, scale


def scores(emb, family_idx, head, scale, text, mix, has_data, zs_scale=100.0):
    """Probabilities over one family's variants (indices in family_idx)."""
    zs = torch.softmax(torch.tensor(zs_scale * emb @ text[family_idx].T), dim=-1).numpy()
    with torch.no_grad():
        logits = scale * head(torch.tensor(emb[None], dtype=torch.float32))[0][family_idx]
    hd = torch.softmax(logits, dim=-1).numpy()
    use = has_data[family_idx]
    return np.where(use, (1 - mix) * zs + mix * hd, zs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", type=Path, default=Path("features_out/variants.npz"))
    parser.add_argument("--catalog", type=Path, default=Path("src/identify/rolex_variants.json"))
    parser.add_argument("--out", type=Path, default=Path("models/variant_head.pt"))
    parser.add_argument("--md", type=Path, default=Path("docs/benchmark_variants_head.md"))
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    d = np.load(args.features)
    variants = [str(v) for v in d["variants"]]
    family_of = {v["id"]: fam for fam, vs in catalog.items() for v in vs}
    all_ids = sorted(family_of)  # every catalog variant, so text embeddings cover variants with no photos
    index = {v: i for i, v in enumerate(all_ids)}
    labels = np.array([index[variants[i]] for i in d["labels"]])
    text = text_embeddings(catalog, all_ids)
    fam_idx = {fam: np.array([index[v["id"]] for v in vs]) for fam, vs in catalog.items()}

    feats = d["feats"].astype("float32")
    tr = d["splits"] == "train"
    head, scale = train_head(feats[tr], labels[tr], len(all_ids))
    has_data = np.bincount(labels[tr], minlength=len(all_ids)) >= 5
    print("variants with 5+ train photos:", int(has_data.sum()), "of", len(all_ids))

    def evaluate(split, mix, view="dial"):
        sel = np.where((d["splits"] == split) & (d["augs"] == 0) & (d["views"] == view))[0]
        top1 = top3 = 0
        per = {}
        for i in sel:
            fam = family_of[all_ids[labels[i]]]
            p = scores(feats[i], fam_idx[fam], head, scale, text, mix, has_data)
            order = fam_idx[fam][np.argsort(-p)]
            hit1, hit3 = order[0] == labels[i], labels[i] in order[:3]
            top1 += hit1; top3 += hit3
            r = per.setdefault(fam, [0, 0, 0]); r[0] += 1; r[1] += hit1; r[2] += hit3
        return top1 / len(sel), top3 / len(sel), per

    best = None
    for mix in (0.0, 0.3, 0.5, 0.7, 0.9, 1.0):
        v1, v3, _ = evaluate("val", mix)
        print(f"mix {mix}: val top1 {v1:.3f} top3 {v3:.3f}")
        if best is None or v1 + v3 > best[0]:
            best = (v1 + v3, mix)
    mix = best[1]
    t1, t3, per = evaluate("test", mix)
    z1, z3, _ = evaluate("test", 0.0)
    print(f"TEST mix={mix}: top1 {t1:.3f} top3 {t3:.3f} | zero-shot only: top1 {z1:.3f} top3 {z3:.3f}")
    torch.save({"weight": head.weight.detach(), "bias": head.bias.detach(), "scale": scale, "variants": all_ids,
                "text": torch.tensor(text), "mix": mix, "has_data": torch.tensor(has_data)}, args.out)
    lines = ["# Variant head benchmark", "",
             "Same test photos as `docs/benchmark_variants.md` (dial crops, family known). Labels from reference numbers in file names.", "",
             f"| Method | Top-1 | Top-3 |", "|---|---|---|",
             f"| Zero-shot text prompts (old) | {z1:.1%} | {z3:.1%} |", f"| Head + zero-shot mix {mix} (new) | {t1:.1%} | {t3:.1%} |", "",
             "| Family | Photos | Top-1 | Top-3 |", "|---|---|---|---|"]
    lines += [f"| {f} | {r[0]} | {r[1] / r[0]:.0%} | {r[2] / r[0]:.0%} |" for f, r in sorted(per.items())]
    args.md.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
