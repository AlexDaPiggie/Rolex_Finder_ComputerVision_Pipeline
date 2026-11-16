"""
Remove val/test images that have a near-duplicate in train, so the benchmark measures real generalisation.

Usage:
    python -m src.training.dedupe_splits --data-root data/grouped            # moves them to <data-root>/_removed/leak
    python -m src.training.dedupe_splits --data-root data/grouped --dry-run

Near-duplicate = 256-bit dHash distance <= --max-distance (default 6). Moved files can be restored by hand.
"""
import argparse
import shutil
from pathlib import Path

import numpy as np

from src.training.benchmark import IMAGE_EXTENSIONS, dhash


def hashes(folder: Path):
    out = []
    for path in sorted(folder.rglob("*")):
        if path.suffix.lower() in IMAGE_EXTENSIONS:
            try:
                out.append((path, dhash(path)))
            except Exception:
                continue
    return out


def leaked_paths(train_dir: Path, other_dir: Path, max_distance: int = 6) -> list[Path]:
    train = hashes(train_dir)
    if not train:
        return []
    matrix = np.stack([h for _, h in train])
    leaked = []
    for path, value in hashes(other_dir):
        if np.unpackbits(matrix ^ value, axis=1).sum(axis=1).min() <= max_distance:
            leaked.append(path)
    return leaked


def main():
    parser = argparse.ArgumentParser(description="Remove val/test images that duplicate train images")
    parser.add_argument("--data-root", type=Path, default=Path("data/grouped"))
    parser.add_argument("--max-distance", type=int, default=6)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    total = 0
    for split in ("val", "test"):
        leaked = leaked_paths(args.data_root / "train", args.data_root / split, args.max_distance)
        print(f"{split}: {len(leaked)} near-duplicates of train images")
        total += len(leaked)
        if args.dry_run:
            continue
        for path in leaked:
            target = args.data_root / "_removed" / "leak" / split / path.parent.name / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(target))
    print(f"total {total}{' (dry run)' if args.dry_run else ' moved'}")


if __name__ == "__main__":
    main()
