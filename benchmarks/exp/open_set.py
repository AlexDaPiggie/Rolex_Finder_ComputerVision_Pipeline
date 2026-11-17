"""
Unknown-watch (open-set) experiment: how well can we tell "a Rolex we know" from "another brand"?

    python -m benchmarks.exp.open_set

Positives: real Rolex photos (held-out, creator-grouped 5-fold heads, so no photo is scored by a head trained on it).
Negatives: other-brand photos (features_out/other.npz), scored with the deployed head.
Three scores (higher = more Rolex-like):
  conf   - top family probability of the CLIP head (mean of full, crop and dial views)
  prompt - CLIP zero-shot: "a photo of a Rolex watch" against other-brand prompts
  dist   - cosine similarity to the nearest Rolex training embedding (dial view)
Reports AUROC and, for each score, how many other-brand photos are caught when 2%, 5% and 10% of real Rolex photos
are wrongly rejected.
"""
import json
from pathlib import Path

import numpy as np
import torch

from src.training.clip_head import creator_groups, predict, train_head, with_real

FEAT = Path("features_out")
VIEWS = (0, 1, 3)
BRANDS = ["Omega", "Seiko", "Casio", "TAG Heuer", "Tissot", "Longines", "Patek Philippe", "Audemars Piguet", "Cartier",
          "Breitling", "IWC", "Panerai", "Hublot", "Citizen", "Tudor", "Garmin", "Timex", "Swatch", "Fossil", "Vacheron Constantin"]


def auroc(pos, neg):
    """Probability that a random Rolex photo scores higher than a random other-brand photo."""
    allv = np.concatenate([pos, neg])
    ranks = allv.argsort().argsort() + 1
    return float((ranks[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def caught(pos, neg, false_reject):
    """Threshold at the given share of Rolex photos rejected; share of other-brand photos rejected."""
    thr = np.quantile(pos, false_reject)
    return float((neg < thr).mean()), float(thr)


def text_features():
    from transformers import CLIPModel, CLIPProcessor
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch16").eval()
    proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")
    texts = ["a photo of a Rolex watch"] + [f"a photo of a {b} watch" for b in BRANDS] + ["a photo of a smartwatch", "a photo of a digital watch"]
    with torch.no_grad():
        f = model.get_text_features(**proc(text=texts, return_tensors="pt", padding=True))
    f = f if torch.is_tensor(f) else f.pooler_output
    return (f / f.norm(dim=-1, keepdim=True)).numpy()


def main():
    names = [n for n, _ in sorted(json.loads(Path("data/processed/class_mapping.json").read_text()).items(), key=lambda kv: kv[1])]
    tr = np.load(FEAT / "train.npz")
    real = np.load(FEAT / "real.npz", allow_pickle=False)
    other = np.load(FEAT / "other.npz", allow_pickle=False)
    excluded = set(json.loads(Path("benchmarks/real_exclude.json").read_text()))
    keep = np.array([f.replace("\\", "/") not in excluded for f in real["files"]])
    emb, labels = real["emb"][keep].astype("float32"), real["labels"][keep]
    groups = creator_groups(real["files"][keep])
    xtr, ytr = tr["feats"].astype("float32"), tr["labels"]
    oemb = other["emb"].astype("float32")
    print("rolex photos", len(labels), "other-brand photos", len(oemb), "detected", int(other["detected"].sum()))

    unique = sorted(set(groups))
    np.random.default_rng(0).shuffle(unique)
    fold = np.array([{g: i % 5 for i, g in enumerate(unique)}[g] for g in groups])

    pos_conf = np.zeros(len(labels))
    neg_conf = np.zeros(len(oemb))
    for k in range(5):
        train, test = fold != k, fold == k
        x, y = with_real(xtr, ytr, emb[train], labels[train], 10)
        head, scale = train_head(x, y, len(names), 0.1, epochs=60)
        pos_conf[test] = np.mean([predict(head, scale, emb[test][:, v]) for v in VIEWS], axis=0).max(axis=1)
        neg_conf += np.mean([predict(head, scale, oemb[:, v]) for v in VIEWS], axis=0).max(axis=1) / 5

    tf = text_features()

    def prompt(e):
        p = np.mean([torch.softmax(torch.tensor(100 * e[:, v] @ tf.T), dim=1).numpy()[:, 0] for v in (0, 1)], axis=0)
        return p

    def dist(e):
        return np.max([e[:, 3] @ xtr.T], axis=2)[0] if False else (e[:, 3] @ xtr.T).max(axis=1)

    scores = {
        "conf": (pos_conf, neg_conf),
        "prompt": (prompt(emb), prompt(oemb)),
        "dist": (dist(emb), dist(oemb)),
    }
    # combined: average of the rank-normalised scores
    allpos = {k: v[0] for k, v in scores.items()}
    allneg = {k: v[1] for k, v in scores.items()}

    def z(k, a):
        both = np.concatenate([allpos[k], allneg[k]])
        return (a - both.mean()) / both.std()
    scores["conf+prompt"] = tuple(z("conf", s) + z("prompt", t) for s, t in zip(allpos["conf"], allneg["conf"])) if False else (
        z("conf", allpos["conf"]) + z("prompt", allpos["prompt"]), z("conf", allneg["conf"]) + z("prompt", allneg["prompt"]))
    scores["all three"] = (
        sum(z(k, allpos[k]) for k in ("conf", "prompt", "dist")), sum(z(k, allneg[k]) for k in ("conf", "prompt", "dist")))

    out = {}
    print(f"{'score':14s} {'AUROC':>6s} | caught at 2% / 5% / 10% of real Rolex photos rejected")
    for name, (pos, neg) in scores.items():
        row = {"auroc": round(auroc(pos, neg), 3)}
        for fr in (0.02, 0.05, 0.10):
            c, thr = caught(pos, neg, fr)
            row[f"caught_at_{int(fr * 100)}pct"] = round(c, 3)
            row[f"thr_{int(fr * 100)}pct"] = round(thr, 4)
        out[name] = row
        print(f"{name:14s} {row['auroc']:6.3f} | {row['caught_at_2pct']:.2f} / {row['caught_at_5pct']:.2f} / {row['caught_at_10pct']:.2f}")
    Path("benchmarks/open_set.json").write_text(json.dumps({"n_rolex": int(len(labels)), "n_other": int(len(oemb)), "scores": out}, indent=1))
    np.savez("benchmarks/open_set_scores.npz", **{f"{k}_{s}": v[i] for k, v in scores.items() for i, s in enumerate(("pos", "neg"))})


if __name__ == "__main__":
    main()
