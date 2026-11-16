"""
Benchmark the family classifier on a held-out split and write metrics to disk.

Usage (from the project root):
    python -m src.training.benchmark
    python -m src.training.benchmark --split test --check-leakage
    python -m src.training.benchmark --data-root data/realworld --split test   # your own real-world photos

Writes:
    benchmarks/classifier_metrics.json   machine-readable numbers
    docs/benchmark.md                    readable summary for the README / model card

The metric helpers are pure functions (numpy only) so they can be unit tested.
"""
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

from src.training.dataset import load_class_names, make_image_folder
from src.training.models import create_model

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


# ---------------------------------------------------------------- metrics

def confusion_matrix(labels: np.ndarray, preds: np.ndarray, num_classes: int) -> np.ndarray:
    """Rows are true classes, columns are predicted classes."""
    matrix = np.zeros((num_classes, num_classes), dtype=np.int64)
    np.add.at(matrix, (labels, preds), 1)
    return matrix


def per_class_metrics(matrix: np.ndarray, class_names: list[str]) -> list[dict]:
    rows = []
    for index, name in enumerate(class_names):
        tp = int(matrix[index, index])
        support = int(matrix[index].sum())
        predicted = int(matrix[:, index].sum())
        precision = tp / predicted if predicted else 0.0
        recall = tp / support if support else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        rows.append(
            {
                "class": name,
                "support": support,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
            }
        )
    return rows


def top_k_accuracy(probabilities: np.ndarray, labels: np.ndarray, k: int) -> float:
    k = min(k, probabilities.shape[1])
    top_k = np.argsort(-probabilities, axis=1)[:, :k]
    return float((top_k == labels[:, None]).any(axis=1).mean())


def expected_calibration_error(probabilities: np.ndarray, labels: np.ndarray, bins: int = 10) -> float:
    """Gap between stated confidence and actual accuracy, averaged over confidence bins."""
    confidence = probabilities.max(axis=1)
    correct = (probabilities.argmax(axis=1) == labels).astype(float)
    edges = np.linspace(0.0, 1.0, bins + 1)
    ece = 0.0
    for low, high in zip(edges[:-1], edges[1:]):
        in_bin = (confidence > low) & (confidence <= high)
        if in_bin.any():
            ece += in_bin.mean() * abs(correct[in_bin].mean() - confidence[in_bin].mean())
    return float(ece)


def coverage_accuracy(probabilities: np.ndarray, labels: np.ndarray, thresholds=(0.5, 0.7, 0.9, 0.95)) -> list[dict]:
    """If the app only answered when confidence >= t, how much would it answer and how accurate would it be?"""
    confidence = probabilities.max(axis=1)
    correct = probabilities.argmax(axis=1) == labels
    rows = []
    for t in thresholds:
        keep = confidence >= t
        rows.append(
            {
                "threshold": t,
                "coverage": round(float(keep.mean()), 4),
                "accuracy": round(float(correct[keep].mean()), 4) if keep.any() else None,
            }
        )
    return rows


def most_confused_pairs(matrix: np.ndarray, class_names: list[str], limit: int = 8) -> list[dict]:
    pairs = []
    for true_index in range(len(class_names)):
        for pred_index in range(len(class_names)):
            if true_index != pred_index and matrix[true_index, pred_index] > 0:
                pairs.append(
                    {
                        "true": class_names[true_index],
                        "predicted": class_names[pred_index],
                        "count": int(matrix[true_index, pred_index]),
                    }
                )
    return sorted(pairs, key=lambda p: -p["count"])[:limit]


def compute_metrics(probabilities: np.ndarray, labels: np.ndarray, class_names: list[str]) -> dict:
    preds = probabilities.argmax(axis=1)
    matrix = confusion_matrix(labels, preds, len(class_names))
    per_class = per_class_metrics(matrix, class_names)
    present = [row for row in per_class if row["support"] > 0]
    return {
        "samples": int(len(labels)),
        "top1_accuracy": round(float((preds == labels).mean()), 4),
        "top3_accuracy": round(top_k_accuracy(probabilities, labels, 3), 4),
        "macro_f1": round(float(np.mean([r["f1"] for r in present])), 4) if present else 0.0,
        "balanced_accuracy": round(float(np.mean([r["recall"] for r in present])), 4) if present else 0.0,
        "ece": round(expected_calibration_error(probabilities, labels), 4),
        "mean_confidence": round(float(probabilities.max(axis=1).mean()), 4),
        "coverage_vs_accuracy": coverage_accuracy(probabilities, labels),
        "per_class": per_class,
        "most_confused": most_confused_pairs(matrix, class_names),
        "confusion_matrix": matrix.tolist(),
    }


# ---------------------------------------------------------------- leakage check

def dhash(path: Path, size: int = 16) -> np.ndarray:
    """256-bit difference hash (packed bytes). Near-identical photos land a few bits apart.

    A coarse 8x8 hash flags most white-background product photos as duplicates, so use 16x16.
    """
    from PIL import Image

    with Image.open(path) as image:
        gray = image.convert("L").resize((size + 1, size))
        pixels = np.asarray(gray, dtype=np.int16)
    return np.packbits((pixels[:, 1:] > pixels[:, :-1]).flatten())


def find_leakage(train_dir: Path, test_dir: Path, max_distance: int = 6) -> dict:
    """Count test images that have a near-duplicate in the training set (Hamming distance on 256 bits)."""
    def hashes(folder: Path):
        out = []
        for path in sorted(folder.rglob("*")):
            if path.suffix.lower() in IMAGE_EXTENSIONS:
                try:
                    out.append((path, dhash(path)))
                except Exception:
                    continue
        return out

    train_hashes = hashes(train_dir)
    test_hashes = hashes(test_dir)
    train_matrix = np.stack([h for _, h in train_hashes])

    leaked = []
    for path, value in test_hashes:
        distances = np.unpackbits(train_matrix ^ value, axis=1).sum(axis=1)
        if distances.min() <= max_distance:
            leaked.append(str(path))
    return {
        "test_images": len(test_hashes),
        "train_images": len(train_hashes),
        "near_duplicates_in_train": len(leaked),
        "leak_rate": round(len(leaked) / len(test_hashes), 4) if test_hashes else 0.0,
        "max_hamming_distance": max_distance,
        "examples": leaked[:10],
    }


# ---------------------------------------------------------------- run

def run_model(data_root: Path, split: str, checkpoint_path: Path, batch_size: int, num_workers: int, device_name: str = "cpu"):
    device = torch.device(device_name)
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=True)
    class_names = checkpoint["class_names"]
    if class_names != load_class_names(data_root):
        raise ValueError("Checkpoint classes do not match class_mapping.json in the data root")

    dataset = make_image_folder(data_root, split, train=False)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    model = create_model(num_classes=len(class_names), pretrained=False).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    all_probs, all_labels = [], []
    start = time.perf_counter()
    with torch.no_grad():
        for images, labels in loader:
            all_probs.append(torch.softmax(model(images.to(device)), dim=1).cpu().numpy())
            all_labels.append(labels.numpy())
    elapsed = time.perf_counter() - start
    probabilities = np.concatenate(all_probs)
    labels = np.concatenate(all_labels)
    return probabilities, labels, class_names, elapsed / max(1, len(labels)) * 1000


def to_markdown(report: dict) -> str:
    m = report["metrics"]
    lines = [
        "# Classifier benchmark",
        "",
        f"Generated {report['generated_at']} on split `{report['split']}` of `{report['data_root']}` "
        f"({m['samples']} images).",
        "",
        "**What this measures:** the EfficientNet-B0 family classifier only, on crops from the same collection "
        "as the training data. It does not measure the full pipeline (detection, alignment, variant matching) "
        "or real-world phone photos, so treat it as an optimistic upper bound.",
        "",
        f"Device: {report.get('device', 'cpu')}.",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Top-1 accuracy | {m['top1_accuracy']:.1%} |",
        f"| Top-3 accuracy | {m['top3_accuracy']:.1%} |",
        f"| Macro F1 | {m['macro_f1']:.3f} |",
        f"| Balanced accuracy (mean recall) | {m['balanced_accuracy']:.1%} |",
        f"| Calibration error (ECE, lower is better) | {m['ece']:.3f} |",
        f"| Mean confidence | {m['mean_confidence']:.1%} |",
        f"| Latency per image (batched) | {report['latency_ms_per_image']:.1f} ms |",
        "",
    ]
    leak = report.get("leakage")
    if leak:
        lines += [
            "## Train/test leakage check",
            "",
            f"{leak['near_duplicates_in_train']} of {leak['test_images']} test images "
            f"({leak['leak_rate']:.1%}) have a near-duplicate in the training set "
            f"(256-bit dHash distance <= {leak['max_hamming_distance']}; a conservative count, similar photos of the same watch can be further apart). "
            "Accuracy on those images is inflated.",
            "",
        ]
    lines += [
        "## Per class",
        "",
        "| Class | Images | Precision | Recall | F1 |",
        "|---|---|---|---|---|",
    ]
    for row in sorted(m["per_class"], key=lambda r: r["f1"]):
        lines.append(
            f"| {row['class']} | {row['support']} | {row['precision']:.2f} | {row['recall']:.2f} | {row['f1']:.2f} |"
        )
    lines += ["", "## Most confused pairs", "", "| True | Predicted | Count |", "|---|---|---|"]
    for pair in m["most_confused"]:
        lines.append(f"| {pair['true']} | {pair['predicted']} | {pair['count']} |")
    lines += [
        "",
        "## If the app only answered when confident",
        "",
        "| Confidence threshold | Share answered | Accuracy on those |",
        "|---|---|---|",
    ]
    for row in m["coverage_vs_accuracy"]:
        accuracy = "n/a" if row["accuracy"] is None else f"{row['accuracy']:.1%}"
        lines.append(f"| >= {row['threshold']} | {row['coverage']:.1%} | {accuracy} |")
    lines.append("")
    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description="Benchmark the family classifier")
    parser.add_argument("--data-root", type=Path, default=Path("data/processed"))
    parser.add_argument("--split", default="test")
    parser.add_argument("--checkpoint", type=Path, default=Path("models/rolex_classifier_model.pt"))
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--device", default="cpu", help="cpu or cuda")
    parser.add_argument("--check-leakage", action="store_true", help="look for test images that also appear in train")
    parser.add_argument("--json-out", type=Path, default=Path("benchmarks/classifier_metrics.json"))
    parser.add_argument("--md-out", type=Path, default=Path("docs/benchmark.md"))
    return parser.parse_args()


def main():
    args = parse_args()
    probabilities, labels, class_names, latency = run_model(
        args.data_root, args.split, args.checkpoint, args.batch_size, args.num_workers, args.device
    )
    report = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "data_root": str(args.data_root).replace("\\", "/"),
        "split": args.split,
        "checkpoint": str(args.checkpoint).replace("\\", "/"),
        "latency_ms_per_image": round(latency, 2),
        "device": args.device,
        "class_names": class_names,
        "metrics": compute_metrics(probabilities, labels, class_names),
    }
    if args.check_leakage:
        report["leakage"] = find_leakage(args.data_root / "train", args.data_root / args.split)

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    args.md_out.write_text(to_markdown(report), encoding="utf-8")

    m = report["metrics"]
    print(f"top1={m['top1_accuracy']:.4f} top3={m['top3_accuracy']:.4f} macro_f1={m['macro_f1']:.4f} ece={m['ece']:.4f}")
    print(f"wrote {args.json_out} and {args.md_out}")


if __name__ == "__main__":
    main()
