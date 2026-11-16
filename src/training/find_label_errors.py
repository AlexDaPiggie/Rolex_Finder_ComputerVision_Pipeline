"""
List images whose label is probably wrong, for manual review.

The model has seen the training images, so when it confidently disagrees with the label on one of them,
the label (or the photo) is usually the problem. Writes a CSV you can review and fix by hand.

Usage:
    python -m src.training.find_label_errors                           # train + val of data/processed
    python -m src.training.find_label_errors --data-root data/grouped_crops --min-confidence 0.9
"""
import argparse
import csv
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from src.training.dataset import build_transforms, load_class_names
from src.training.models import create_model

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def flag_disagreements(label_index: int, probs: np.ndarray, min_confidence: float) -> list[int]:
    """Row indices where the model confidently picks a class other than label_index."""
    predicted = probs.argmax(axis=1)
    confidence = probs.max(axis=1)
    return [int(i) for i in np.where((predicted != label_index) & (confidence >= min_confidence))[0]]


def main():
    parser = argparse.ArgumentParser(description="Find likely label errors")
    parser.add_argument("--data-root", type=Path, default=Path("data/processed"))
    parser.add_argument("--splits", nargs="+", default=["train", "val"])
    parser.add_argument("--checkpoint", type=Path, default=Path("models/rolex_classifier_model.pt"))
    parser.add_argument("--min-confidence", type=float, default=0.9)
    parser.add_argument("--out", type=Path, default=Path("benchmarks/label_review.csv"))
    args = parser.parse_args()

    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=True)
    class_names = checkpoint["class_names"]
    if class_names != load_class_names(args.data_root):
        raise ValueError("Checkpoint classes do not match class_mapping.json")
    model = create_model(num_classes=len(class_names), pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    transform = build_transforms(train=False)

    rows = []
    for split in args.splits:
        for label_index, label in enumerate(class_names):
            folder = args.data_root / split / label
            files = [p for p in sorted(folder.glob("*")) if p.suffix.lower() in IMAGE_EXTENSIONS]
            for start in range(0, len(files), 64):
                batch_files = files[start:start + 64]
                batch = torch.stack([transform(Image.open(p).convert("RGB")) for p in batch_files])
                with torch.no_grad():
                    probs = torch.softmax(model(batch), dim=1).numpy()
                for i in flag_disagreements(label_index, probs, args.min_confidence):
                    rows.append([
                        split,
                        str(batch_files[i]).replace("\\", "/"),
                        label,
                        class_names[int(probs[i].argmax())],
                        round(float(probs[i].max()), 3),
                    ])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["split", "path", "given_label", "model_says", "confidence"])
        writer.writerows(sorted(rows, key=lambda r: -r[4]))
    print(f"{len(rows)} images flagged -> {args.out}")


if __name__ == "__main__":
    main()
