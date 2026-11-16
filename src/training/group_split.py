"""
Build a train/val/test split where all photos of one listing stay in the same split.

The current split is random per photo, so other photos of the same watch (same listing) can sit in
both train and test. That inflates test accuracy. Here images are grouped by listing and whole groups
are assigned to a split.

Usage:
    python -m src.training.group_split                       # writes data/grouped
    python -m src.training.group_split --out-root data/grouped --seed 7

Group key = image filename with the trailing hash and size tokens removed. This is a heuristic based on
the retailer URL pattern; the report prints group counts so you can sanity check it.
"""
import argparse
import csv
import json
import random
import re
import shutil
from collections import defaultdict
from pathlib import Path

SIZE_SUFFIX = re.compile(r"(_[0-9a-f]{4,6})?(_[a-z])?_sm$|_sm$")


def group_key(image_url: str, fallback: str) -> str:
    """Listing id for an image URL, or the image own id when the URL has no usable name."""
    name = str(image_url).rsplit("/", 1)[-1].rsplit(".", 1)[0]
    stem = SIZE_SUFFIX.sub("", name)
    return stem if len(stem) >= 8 else fallback


def split_groups(groups: list[str], fractions=(0.8, 0.1, 0.1), seed: int = 42) -> dict[str, str]:
    """Assign each group to train/val/test. Returns {group: split}."""
    ordered = sorted(set(groups))
    random.Random(seed).shuffle(ordered)
    total = len(ordered)
    n_train = int(round(total * fractions[0]))
    n_val = int(round(total * fractions[1]))
    # tiny classes: make sure val and test get at least one group when possible
    if total >= 3:
        n_val = max(1, n_val)
        n_train = min(n_train, total - n_val - 1)
    assignment = {}
    for index, group in enumerate(ordered):
        if index < n_train:
            assignment[group] = "train"
        elif index < n_train + n_val:
            assignment[group] = "val"
        else:
            assignment[group] = "test"
    return assignment


def build(manifest: Path, out_root: Path, class_mapping: Path, seed: int):
    rows = []
    with manifest.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            path = Path(row["local_path"].replace("\\", "/"))
            if row["status"] == "downloaded" and path.exists():
                rows.append((row, path))

    by_label = defaultdict(list)
    for row, path in rows:
        by_label[row["label"]].append((row, path))

    mapping = json.loads(class_mapping.read_text(encoding="utf-8"))
    report = {"classes": {}, "seed": seed}
    for label in mapping:
        items = by_label.get(label, [])
        keys = [group_key(row["image_url"], row["image_id"]) for row, _ in items]
        assignment = split_groups(keys, seed=seed)
        counts = {"train": 0, "val": 0, "test": 0}
        for (row, path), key in zip(items, keys):
            split = assignment[key]
            target = out_root / split / label
            target.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target / path.name)
            counts[split] += 1
        report["classes"][label] = {"images": len(items), "groups": len(set(keys)), **counts}

    out_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(class_mapping, out_root / "class_mapping.json")
    (out_root / "split_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description="Group-aware train/val/test split")
    parser.add_argument("--manifest", type=Path, default=Path("data/manifests/images.csv"))
    parser.add_argument("--out-root", type=Path, default=Path("data/grouped"))
    parser.add_argument("--class-mapping", type=Path, default=Path("data/processed/class_mapping.json"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    report = build(args.manifest, args.out_root, args.class_mapping, args.seed)
    for label, row in report["classes"].items():
        print(
            f"{label:18s} images={row['images']:5d} groups={row['groups']:5d} "
            f"train={row['train']:5d} val={row['val']:4d} test={row['test']:4d}"
        )


if __name__ == "__main__":
    main()
