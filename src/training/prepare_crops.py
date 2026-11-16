"""
Run the same preprocessing the website uses (detect watch -> crop -> align bracelet -> dial crop)
on every training image, so the model trains on what it sees at inference time.

Today the classifier trains on full retailer photos but is used on tight dial crops. This closes that gap.

Usage (needs the Grounding DINO model; use a GPU, CPU is about 10 s per image):
    python -m src.training.prepare_crops --data-root data/grouped --out-root data/grouped_crops
    python -m src.training.prepare_crops --limit 20            # quick smoke test

Resumable: images already written are skipped. Writes crop_report.json with how each image was handled.
When no watch is detected the original image is kept (--on-miss keep, default) or dropped (--on-miss skip).
"""
import argparse
import json
import shutil
from collections import Counter
from pathlib import Path

from PIL import Image, ImageOps

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def outcome_of(crop_info: dict) -> str:
    if crop_info.get("reason") == "no_watch_detected":
        return "no_watch_detected"
    if not crop_info.get("crop_used"):
        return crop_info.get("reason", "crop_not_used")
    dial = (crop_info.get("dial_crop") or {}).get("dial_crop_used")
    return "cropped_with_dial" if dial else "cropped_no_dial"


def process_image(source: Path, target: Path, crop_fn, on_miss: str = "keep") -> str:
    """Crop one image to `target`. Returns the outcome label."""
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
    cropped, info, _stages = crop_fn(image)
    outcome = outcome_of(info)
    if outcome == "no_watch_detected" and on_miss == "skip":
        return outcome
    target.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(target, format="JPEG", quality=95)
    return outcome


def run(data_root: Path, out_root: Path, crop_fn, splits=("train", "val", "test"), limit: int = 0, on_miss="keep", labels=None):
    counts: dict[str, Counter] = {}
    done = 0
    for split in splits:
        counts.setdefault(split, Counter())
        for source in sorted((data_root / split).rglob("*")):
            if source.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            label = source.parent.name
            if labels is not None and label not in labels:
                continue
            target = out_root / split / label / (source.stem + ".jpg")
            if target.exists():
                counts[split]["already_done"] += 1
                continue
            try:
                outcome = process_image(source, target, crop_fn, on_miss)
            except Exception as error:  # keep going on a bad file
                outcome = f"error:{type(error).__name__}"
            counts[split][outcome] += 1
            done += 1
            if done % 100 == 0:
                print(f"{done} images processed", flush=True)
            if limit and done >= limit:
                return counts
    return counts


def main():
    parser = argparse.ArgumentParser(description="Crop training images with the inference pipeline")
    parser.add_argument("--data-root", type=Path, default=Path("data/grouped"))
    parser.add_argument("--out-root", type=Path, default=Path("data/grouped_crops"))
    parser.add_argument("--limit", type=int, default=0, help="stop after this many images (0 = all)")
    parser.add_argument("--on-miss", choices=["keep", "skip"], default="keep")
    args = parser.parse_args()

    from src.detection.watch_cropper import crop_watch_stages

    counts = run(args.data_root, args.out_root, crop_watch_stages, limit=args.limit, on_miss=args.on_miss)
    args.out_root.mkdir(parents=True, exist_ok=True)
    mapping = args.data_root / "class_mapping.json"
    if mapping.exists():
        shutil.copy2(mapping, args.out_root / "class_mapping.json")
    report = {split: dict(counter) for split, counter in counts.items()}
    (args.out_root / "crop_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
