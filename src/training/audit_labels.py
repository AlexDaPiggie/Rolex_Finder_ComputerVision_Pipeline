"""
Audit labels with two independent signals, then fix the clear cases.

Signal 1 (text): the family named in the retailer image file name (for example "rolex-datejust-41-...").
Signal 2 (model): what the current classifier predicts for the image.

Policy (per image):
  - text names a different family than the label:
      model agrees with text (confident)  -> relabel to that family
      model agrees with the label         -> keep (some families overlap, e.g. a Datejust on a President bracelet)
      neither                             -> remove (the signals conflict, the image is not worth the risk)
  - no usable text, model confidently (>= 0.9) picks another family -> relabel
  - everything else -> keep

Usage:
    python -m src.training.audit_labels                 # scan data/grouped, write benchmarks/label_audit.csv (no changes)
    python -m src.training.audit_labels --apply         # also move/remove files (removed ones go to data/grouped/_removed)

Class probabilities are cached in benchmarks/grouped_probs.npz so re-runs are fast.
"""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np

# File-name keywords per family. Specific names beat the generic ones (oyster perpetual, datejust).
FAMILY_KEYWORDS = {
    "airking": ["air-king", "airking"],
    "cellini": ["cellini"],
    "daytona": ["daytona"],
    "explorer": ["explorer"],
    "gmt_master": ["gmt"],
    "milgauss": ["milgauss"],
    "oysterquartz": ["oysterquartz", "oyster-quartz"],
    "president": ["president", "day-date", "daydate"],
    "sea_dweller": ["sea-dweller", "seadweller", "deepsea", "deep-sea"],
    "submariner": ["submariner"],
    "turn_o_graph": ["turn-o-graph", "turnograph", "thunderbird"],
    "yacht_master": ["yacht-master", "yachtmaster"],
    "datejust": ["datejust", "date-just"],
    "oyster_perpetual": ["oyster-perpetual"],
}
GENERIC = {"datejust", "oyster_perpetual", "president"}  # overlap with other families in file names
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def text_family(image_url: str) -> str | None:
    """The single family named in the file name, or None when it names none or several clearly."""
    name = str(image_url).rsplit("/", 1)[-1].lower()
    hits = [family for family, words in FAMILY_KEYWORDS.items() if any(w in name for w in words)]
    if len(hits) == 1:
        return hits[0]
    specific = [h for h in hits if h not in GENERIC]
    if len(specific) == 1:  # e.g. "oyster-perpetual-air-king" -> airking
        return specific[0]
    return None


def decide(label: str, text: str | None, predicted: str, confidence: float, min_model: float = 0.8) -> tuple[str, str, str]:
    """Return (action, new_label, reason). action is keep, relabel or remove."""
    if text and text != label:
        if predicted == text and confidence >= min_model:
            return "relabel", text, "text and model agree"
        if predicted == label:
            return "keep", label, "model sides with label"
        return "remove", label, "text, model and label conflict"
    if predicted != label and confidence >= 0.9:
        return "relabel", predicted, "model very confident"
    return "keep", label, "ok"


def load_url_by_file(manifest: Path) -> dict[str, str]:
    urls = {}
    with manifest.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            urls[row["image_id"]] = row["image_url"]
    return urls


def scan(data_root: Path, checkpoint: Path, cache: Path):
    """Class probabilities for every image under data_root (cached)."""
    import torch
    from PIL import Image

    from src.training.dataset import build_transforms
    from src.training.models import create_model

    ckpt = torch.load(checkpoint, map_location="cpu", weights_only=True)
    class_names = ckpt["class_names"]
    files = sorted(p for p in data_root.glob("*/*/*") if p.suffix.lower() in IMAGE_EXTENSIONS and p.parts[-3] in ("train", "val", "test"))
    if cache.exists():
        cached = np.load(cache, allow_pickle=False)
        if list(cached["paths"]) == [str(p) for p in files]:
            return files, cached["probs"], class_names

    model = create_model(num_classes=len(class_names), pretrained=False)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    transform = build_transforms(train=False)
    probs = []
    for start in range(0, len(files), 64):
        batch = torch.stack([transform(Image.open(p).convert("RGB")) for p in files[start:start + 64]])
        with torch.no_grad():
            probs.append(torch.softmax(model(batch), dim=1).numpy())
        if (start // 64) % 20 == 0:
            print(f"scanned {start}/{len(files)}", flush=True)
    probs = np.concatenate(probs)
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez(cache, paths=np.array([str(p) for p in files]), probs=probs)
    return files, probs, class_names


def main():
    parser = argparse.ArgumentParser(description="Audit and fix labels")
    parser.add_argument("--data-root", type=Path, default=Path("data/grouped"))
    parser.add_argument("--manifest", type=Path, default=Path("data/manifests/images.csv"))
    parser.add_argument("--checkpoint", type=Path, default=Path("models/rolex_classifier_model.pt"))
    parser.add_argument("--cache", type=Path, default=Path("benchmarks/grouped_probs.npz"))
    parser.add_argument("--out", type=Path, default=Path("benchmarks/label_audit.csv"))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    files, probs, class_names = scan(args.data_root, args.checkpoint, args.cache)
    urls = load_url_by_file(args.manifest)

    rows, decisions = [], []
    for path, row in zip(files, probs):
        label = path.parent.name
        predicted = class_names[int(row.argmax())]
        action, new_label, reason = decide(label, text_family(urls.get(path.stem, "")), predicted, float(row.max()))
        if action == "keep":
            continue
        rows.append([path.parts[-3], str(path).replace("\\", "/"), label, new_label, action, reason, round(float(row.max()), 3)])
        decisions.append({"path": str(path), "given_label": label, "action": action, "new_label": new_label})

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["split", "path", "label", "new_label", "action", "reason", "model_confidence"])
        writer.writerows(rows)

    summary = Counter((r[4], r[5]) for r in rows)
    print(json.dumps({f"{a}: {r}": n for (a, r), n in summary.items()}, indent=2))
    print(f"{len(rows)} of {len(files)} images flagged -> {args.out}")

    if args.apply:
        from src.training.label_review_page import apply_decisions

        print(apply_decisions(decisions, args.data_root))


if __name__ == "__main__":
    main()
