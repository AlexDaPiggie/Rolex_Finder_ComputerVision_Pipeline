"""
Collect photos of one Rolex family by web image search (for families the original dataset does not have).

    python -m src.collection.family_web land_dweller --per-query 40 \
        --queries "Rolex Land-Dweller 36" "Rolex Land-Dweller 40 on wrist" --require land-dweller land dweller

Keeps only results whose title contains one of the --require words (so a Datejust is not filed as a Land-Dweller).
Writes data/<family>_web/<family>/*.jpg and manifest.csv (file, creator = site, page, title). The site name is the
"creator", so cross-validation never splits photos from one site between train and test.
"""
import argparse
import csv
import hashlib
import time
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import requests
from PIL import Image

from src.collection.variant_photos_web import HEADERS, search

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("family")
    parser.add_argument("--queries", nargs="+", required=True)
    parser.add_argument("--require", nargs="+", default=[], help="title must contain one of these (lower case)")
    parser.add_argument("--per-query", type=int, default=30)
    parser.add_argument("--max-per-site", type=int, default=6)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    out = args.out or ROOT / f"data/{args.family}_web"
    folder = out / args.family
    folder.mkdir(parents=True, exist_ok=True)
    manifest = out / "manifest.csv"
    rows = list(csv.DictReader(manifest.open(encoding="utf-8"))) if manifest.exists() else []
    seen = {r["image"] for r in rows}
    seen_hash = set()
    per_site: dict[str, int] = {}
    for r in rows:
        per_site[r["creator"]] = per_site.get(r["creator"], 0) + 1
    for q in args.queries:
        try:
            results = search(q, args.per_query)
        except Exception as exc:
            print("search failed", q, exc)
            time.sleep(5)
            continue
        added = 0
        for r in results:
            title = (r.get("title") or "").lower()
            if r["image"] in seen or (args.require and not any(w in title for w in args.require)):
                continue
            site = urlparse(r.get("url") or "").netloc.removeprefix("www.") or "unknown"
            if per_site.get(site, 0) >= args.max_per_site:
                continue
            seen.add(r["image"])
            try:
                data = requests.get(r["image"], headers=HEADERS, timeout=15).content
                img = Image.open(BytesIO(data)).convert("RGB")
            except Exception:
                continue
            if min(img.size) < 400:
                continue
            h = hashlib.md5(img.resize((16, 16)).tobytes()).hexdigest()
            if h in seen_hash:
                continue
            seen_hash.add(h)
            img.thumbnail((1000, 1000))
            name = f"{args.family}_{len(rows):03d}.jpg"
            img.save(folder / name, quality=88)
            rows.append({"file": f"{args.family}/{name}", "creator": site, "page": r.get("url"), "title": r.get("title"),
                         "image": r["image"]})
            per_site[site] = per_site.get(site, 0) + 1
            added += 1
        print(f"{q!r}: +{added} (total {len(rows)})", flush=True)
        time.sleep(2)
    with manifest.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file", "creator", "page", "title", "image"])
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
