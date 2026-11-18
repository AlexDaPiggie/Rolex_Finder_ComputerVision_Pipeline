"""
Train and compare family classifiers from saved CLIP features (made by modal_improve.py).

    python -m src.training.clip_head --features features_out

Trains a linear head on CLIP image embeddings (studio and dial-crop views, with real-look augmentation),
then compares on three test sets:
  1. retailer test split (clean)            - what the old benchmark measured
  2. retailer test split (real-look aug)     - same photos with backgrounds, blur, glare, close-ups
  3. real photos (Wikimedia, Flickr)         - the number that matters, per preprocessing variant

Writes benchmarks/clip_head.pt (head weights), benchmarks/real_eval.json and docs/benchmark_realworld.md.
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np
import torch

VIEW_NAMES = ["full", "crop", "aligned", "dial"]


def class_weights(labels: np.ndarray, num_classes: int, power: float = 0.5) -> torch.Tensor:
    counts = np.bincount(labels, minlength=num_classes).astype("float64")
    weights = (1.0 / np.maximum(counts, 1.0)) ** power
    return torch.tensor(weights / weights.mean(), dtype=torch.float32)


def train_head(x: np.ndarray, y: np.ndarray, num_classes: int, weight_decay: float, epochs: int = 300, scale: float = 30.0):
    """Linear head on L2-normalised features. Logits = scale * (x W^T + b)."""
    torch.manual_seed(0)
    xt = torch.tensor(x, dtype=torch.float32)
    yt = torch.tensor(y, dtype=torch.long)
    head = torch.nn.Linear(x.shape[1], num_classes)
    optimizer = torch.optim.AdamW(head.parameters(), lr=3e-3, weight_decay=weight_decay)
    loss_fn = torch.nn.CrossEntropyLoss(weight=class_weights(y, num_classes), label_smoothing=0.05)
    for epoch in range(epochs):
        permutation = torch.randperm(len(xt))
        for start in range(0, len(xt), 4096):
            idx = permutation[start:start + 4096]
            optimizer.zero_grad()
            loss = loss_fn(scale * head(xt[idx]), yt[idx])
            loss.backward()
            optimizer.step()
    return head, scale


def predict(head, scale: float, x: np.ndarray) -> np.ndarray:
    with torch.no_grad():
        return torch.softmax(scale * head(torch.tensor(x, dtype=torch.float32)), dim=1).numpy()


def accuracy(probs: np.ndarray, labels: np.ndarray) -> float:
    return float((probs.argmax(axis=1) == labels).mean())


def wilson(correct: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    p = correct / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return centre - margin, centre + margin


def real_report(probs: np.ndarray, labels: np.ndarray, names: list[str]) -> dict:
    preds = probs.argmax(axis=1)
    per = {}
    for c in sorted(set(labels.tolist())):
        sel = labels == c
        per[names[c]] = {"n": int(sel.sum()), "acc": round(float((preds[sel] == c).mean()), 3)}
    big = [v["acc"] for v in per.values() if v["n"] >= 5]
    low, high = wilson(int((preds == labels).sum()), len(labels))
    return {
        "n": int(len(labels)),
        "acc": round(float((preds == labels).mean()), 3),
        "ci95": [round(low, 3), round(high, 3)],
        "macro_acc_families_5plus": round(float(np.mean(big)), 3) if big else None,
        "per_family": per,
    }


def creator_groups(files) -> np.ndarray:
    """Creator of each real photo (from the collector manifests), so cross-validation never splits one photographer."""
    import csv
    import os

    creator = {}
    for manifest, column in ((Path("data/realworld/manifest.csv"), "creator"), (Path("data/commons/manifest.csv"), "author"),
                       (Path("data/landdweller_final/manifest.csv"), "creator")):
        if manifest.exists():
            for row in csv.DictReader(manifest.open(encoding="utf-8")):
                creator[os.path.basename(row["file"])] = row[column]
    return np.array([creator.get(os.path.basename(f), "unknown") for f in files])


def with_real(x, y, emb, labels, weight: int, class_weight: dict | None = None):
    """Add real photos (full, crop and dial views) to the training features, repeated `weight` times.
    class_weight {label: times} overrides the weight for some classes (families with many real photos need fewer repeats)."""
    xs_all, ys_all = [x], [y]
    for cls in sorted(set(labels.tolist())):
        sel = labels == cls
        times = (class_weight or {}).get(cls, weight)
        xs = np.concatenate([emb[sel][:, v] for v in (0, 1, 3)])
        ys = np.concatenate([labels[sel]] * 3)
        xs_all += [xs] * times
        ys_all += [ys] * times
    return np.concatenate(xs_all), np.concatenate(ys_all)


def grouped_cv(xtr, ytr, emb, labels, groups, names, weight: int, folds: int = 5, epochs: int = 60, class_weight: dict | None = None) -> dict:
    """Held-out accuracy when real photos are added to training. Folds are split by creator."""
    unique = sorted(set(groups))
    np.random.default_rng(0).shuffle(unique)
    fold_of = {g: i % folds for i, g in enumerate(unique)}
    fold = np.array([fold_of[g] for g in groups])
    correct = np.zeros(len(labels), dtype=bool)
    for k in range(folds):
        train, test = fold != k, fold == k
        x, y = (xtr, ytr) if weight == 0 else with_real(xtr, ytr, emb[train], labels[train], weight, class_weight)
        head, scale = train_head(x, y, len(names), 0.1, epochs=epochs)
        correct[test] = predict(head, scale, emb[test][:, 3]).argmax(axis=1) == labels[test]
    low, high = wilson(int(correct.sum()), len(correct))
    return {"weight": weight, "acc": round(float(correct.mean()), 3), "ci95": [round(low, 3), round(high, 3)],
            "per_family": {names[c]: round(float(correct[labels == c].mean()), 2) for c in sorted(set(labels.tolist()))}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--class-weight", nargs="*", default=[], help="NAME=TIMES, e.g. land_dweller=4: real-photo repeats for one family")
    parser.add_argument("--real-weight", type=int, default=0, help="add real photos to the saved head, repeated this many times (0 = off)")
    parser.add_argument("--cv-weights", type=int, nargs="*", default=[], help="report creator-grouped CV with these real-photo weights")
    parser.add_argument("--features", type=Path, default=Path("features_out"))
    parser.add_argument("--exclude", type=Path, default=Path("benchmarks/real_exclude.json"))
    parser.add_argument("--out-json", type=Path, default=Path("benchmarks/real_eval.json"))
    parser.add_argument("--out-md", type=Path, default=Path("docs/benchmark_realworld.md"))
    parser.add_argument("--head-out", type=Path, default=Path("benchmarks/clip_head.pt"))
    args = parser.parse_args()

    names = [n for n, _ in sorted(json.loads(Path("data/processed/class_mapping.json").read_text()).items(), key=lambda kv: kv[1])]
    class_weight = {names.index(k): int(v) for k, v in (item.split("=") for item in args.class_weight)}
    tr = np.load(args.features / "train.npz")
    va = np.load(args.features / "val.npz")
    te = np.load(args.features / "test.npz")
    real = np.load(args.features / "real.npz", allow_pickle=False)
    print("train", tr["feats"].shape, "val", va["feats"].shape, "test", te["feats"].shape, "real", real["emb"].shape)

    excluded = set(json.loads(args.exclude.read_text())) if args.exclude.exists() else set()
    keep = np.array([f.replace("\\", "/") not in excluded for f in real["files"]])
    labels_real = real["labels"][keep]
    emb_real = real["emb"][keep].astype("float32")
    print("real photos kept:", int(keep.sum()), "of", len(keep))

    xtr, ytr = tr["feats"].astype("float32"), tr["labels"]
    results = {"retailer": {}, "real": {}}
    best = None
    for wd in (1e-4, 1e-2, 1e-1):
        head, scale = train_head(xtr, ytr, len(names), wd)
        vclean = va["augs"] == 0
        acc_clean = accuracy(predict(head, scale, va["feats"][vclean].astype("float32")), va["labels"][vclean])
        acc_aug = accuracy(predict(head, scale, va["feats"][~vclean].astype("float32")), va["labels"][~vclean])
        real_full = accuracy(predict(head, scale, emb_real[:, 0]), labels_real)
        print(f"wd={wd}: val clean {acc_clean:.4f} aug {acc_aug:.4f} | real(full view) {real_full:.3f}")
        # choose by the retailer validation (real photos stay untouched for the final comparison)
        score = acc_clean + acc_aug
        if best is None or score > best[0]:
            best = (score, wd, head, scale, acc_clean, acc_aug)
    _, wd, head, scale, acc_clean, acc_aug = best
    if args.cv_weights:
        groups = creator_groups(real["files"][keep])
        results["real_cv"] = [grouped_cv(xtr, ytr, emb_real, labels_real, groups, names, w, class_weight=class_weight) for w in args.cv_weights]
        for entry in results["real_cv"]:
            print("creator-grouped CV", entry)
    if args.real_weight:
        x, y = with_real(xtr, ytr, emb_real, labels_real, args.real_weight, class_weight)
        head, scale = train_head(x, y, len(names), wd)
        print(f"final head also trained on all {len(labels_real)} real photos (weight {args.real_weight}); real-photo numbers below are then NOT held out")
    torch.save({"weight": head.weight.detach(), "bias": head.bias.detach(), "scale": scale, "class_names": names}, args.head_out)

    tclean = te["augs"] == 0
    results["retailer"] = {
        "weight_decay": wd,
        "val_clean": round(acc_clean, 4),
        "val_aug": round(acc_aug, 4),
        "test_clean": round(accuracy(predict(head, scale, te["feats"][tclean].astype("float32")), te["labels"][tclean]), 4),
        "test_aug": round(accuracy(predict(head, scale, te["feats"][~tclean].astype("float32")), te["labels"][~tclean]), 4),
    }
    print("retailer", results["retailer"])

    # real photos: every model and preprocessing variant
    for vi, view in enumerate(VIEW_NAMES):
        results["real"][f"clip_head/{view}"] = real_report(predict(head, scale, emb_real[:, vi]), labels_real, names)
        for key in [k for k in real.files if k.startswith("eff_") and real[k].shape[-1] == len(names)]:
            results["real"][f"effnet_{key[4:]}/{view}"] = real_report(real[key][keep][:, vi], labels_real, names)
    # multi-view average for the head, and head + effnet ensembles
    mv = np.mean([predict(head, scale, emb_real[:, v]) for v in (0, 1, 3)], axis=0)
    results["real"]["clip_head/avg(full,crop,dial)"] = real_report(mv, labels_real, names)
    for key in [k for k in real.files if k.startswith("eff_") and real[k].shape[-1] == len(names)]:
        for vi, view in ((1, "crop"), (3, "dial")):
            ens = 0.5 * predict(head, scale, emb_real[:, vi]) + 0.5 * real[key][keep][:, vi]
            results["real"][f"ensemble(clip_head+effnet_{key[4:]})/{view}"] = real_report(ens, labels_real, names)

    args.out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    rows = sorted(results["real"].items(), key=lambda kv: -kv[1]["acc"])
    lines = [
        "# Real-photo benchmark",
        "",
        f"{len(labels_real)} real photos (Wikimedia Commons, Flickr via Openverse) after removing non-watch images and duplicates. "
        "Full pipeline: detect watch, then the preprocessing variant shown. Labels come from titles and categories, so a few are wrong. "
        "Datejust and Daytona dominate the set, so read the macro column too.",
        "",
        "| Model / preprocessing | Accuracy | 95% interval | Macro (families with 5+ photos) |",
        "|---|---|---|---|",
    ]
    for key, r in rows:
        lines.append(f"| {key} | {r['acc']:.1%} | {r['ci95'][0]:.0%}-{r['ci95'][1]:.0%} | {r['macro_acc_families_5plus']} |")
    lines += ["", f"Retailer test split: {json.dumps(results['retailer'])}", ""]
    args.out_md.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:30]))


if __name__ == "__main__":
    main()
