"""
Benchmark variant matching (the "closest known variants" step) on retailer test photos.

Labels: retailer file names contain reference numbers (for example "...-126303-unworn-48652_..."). A reference that
belongs to exactly one catalog variant of the photo's family gives that photo a variant label.

The family is taken as known (oracle), so this measures the variant step alone. Images are the dial crops the
site feeds to the variant step.

    python -m src.identify.benchmark_variants
    python -m src.identify.benchmark_variants --limit 300      # quick run

Writes benchmarks/variants_metrics.json and docs/benchmark_variants.md.
"""
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image

from src.identify.clip_matcher import get_detector, rank_variants

REFERENCE = re.compile(r"(?<![0-9a-z])(\d{4,6}[a-z]{0,5})(?![0-9])")


def normalise(reference: str) -> str:
    return re.sub(r"[^0-9a-z]", "", reference.lower())


def reference_index(catalog: dict) -> dict[str, dict[str, set[str]]]:
    """family -> normalised reference -> set of variant ids that list it."""
    index: dict[str, dict[str, set[str]]] = {}
    for family, variants in catalog.items():
        refs: dict[str, set[str]] = defaultdict(set)
        for variant in variants:
            for reference in variant.get("reference_examples", []):
                refs[normalise(reference)].add(variant["id"])
        index[family] = refs
    return index


def variant_label(image_url: str, family: str, index: dict) -> str | None:
    """The one variant this file name points to, or None when it names none or several."""
    name = image_url.rsplit("/", 1)[-1].rsplit(".", 1)[0].lower()
    found = set()
    for token in REFERENCE.findall(name):
        found |= index.get(family, {}).get(normalise(token), set())
    return next(iter(found)) if len(found) == 1 else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", type=Path, default=Path("data/grouped_crops_local/test"))
    parser.add_argument("--manifest", type=Path, default=Path("data/manifests/images.csv"))
    parser.add_argument("--catalog", type=Path, default=Path("src/identify/rolex_variants.json"))
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--json-out", type=Path, default=Path("benchmarks/variants_metrics.json"))
    parser.add_argument("--md-out", type=Path, default=Path("docs/benchmark_variants.md"))
    args = parser.parse_args()

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    index = reference_index(catalog)
    urls = {}
    with args.manifest.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            urls[row["image_id"]] = row["image_url"]

    items = []
    for path in sorted(args.images.glob("*/*.jpg")):
        family = path.parent.name
        label = variant_label(urls.get(path.stem, ""), family, index)
        if label and len(catalog.get(family, [])) > 1:
            items.append((path, family, label))
    if args.limit:
        items = items[: args.limit]
    print(len(items), "labelled test photos", flush=True)

    detector = get_detector()
    stats = defaultdict(lambda: [0, 0, 0])  # family -> [n, top1, top3]
    wrong = Counter()
    for n, (path, family, label) in enumerate(items):
        result = rank_variants(Image.open(path).convert("RGB"), catalog[family], detector=detector, top_k=3)
        ranked = [c["id"] for c in result["variant_candidates"]]
        s = stats[family]
        s[0] += 1
        s[1] += ranked[:1] == [label]
        s[2] += label in ranked[:3]
        if ranked[:1] != [label] and ranked:
            wrong[(label, ranked[0])] += 1
        if n % 100 == 0:
            print(f"{n}/{len(items)}", flush=True)

    total = sum(s[0] for s in stats.values())
    top1 = sum(s[1] for s in stats.values()) / total
    top3 = sum(s[2] for s in stats.values()) / total
    chance = sum(s[0] / len(catalog[f]) for f, s in stats.items()) / total
    chance3 = sum(s[0] * min(3, len(catalog[f])) / len(catalog[f]) for f, s in stats.items()) / total
    report = {
        "photos": total, "top1": round(top1, 4), "top3": round(top3, 4),
        "chance_top1": round(chance, 4), "chance_top3": round(chance3, 4),
        "per_family": {f: {"n": s[0], "variants": len(catalog[f]), "top1": round(s[1] / s[0], 3), "top3": round(s[2] / s[0], 3)}
                       for f, s in sorted(stats.items())},
        "most_confused": [{"true": a, "predicted": b, "count": c} for (a, b), c in wrong.most_common(10)],
    }
    args.json_out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Variant matching benchmark", "",
        f"{total} retailer test photos whose file name names a reference number that belongs to exactly one catalog variant. "
        "Family is given (oracle), so this measures the CLIP text-prompt step only. Dial crops, as the site uses them. "
        "Labels come from file names, so a few are wrong. Studio photos, so real photos will score lower.", "",
        f"**Top-1: {top1:.1%}** (random guess {chance:.1%}). **Top-3: {top3:.1%}** (random guess {chance3:.1%}).", "",
        "| Family | Photos | Variants | Top-1 | Top-3 |", "|---|---|---|---|---|",
    ]
    for f, r in report["per_family"].items():
        lines.append(f"| {f} | {r['n']} | {r['variants']} | {r['top1']:.0%} | {r['top3']:.0%} |")
    lines += ["", "Most common mistakes (true variant -> predicted):", ""]
    lines += [f"- {m['true']} -> {m['predicted']}: {m['count']}" for m in report["most_confused"]]
    args.md_out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:8]))


if __name__ == "__main__":
    main()
