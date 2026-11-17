"""
Find one photo per Rolex variant by web image search (personal project, not redistributed as a dataset).

    python -m src.collection.variant_photos_web --limit 6

For every variant in src/identify/rolex_variants.json that has no photo in front_end/src/data/variantPhotos.json,
search "<display name> watch", download up to --limit candidates into data/variant_web/<id>/, and write
data/variant_web/manifest.json (source page, title) so the credit link can point to the page it came from.
"""
import argparse
import json
import time
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
HEADERS = {"User-Agent": "Mozilla/5.0 (RolexFinder hobby project)"}


def missing_variants():
    catalog = json.loads((ROOT / "src/identify/rolex_variants.json").read_text(encoding="utf-8"))
    have = json.loads((ROOT / "front_end/src/data/variantPhotos.json").read_text(encoding="utf-8"))
    return [(fam, v) for fam, vs in catalog.items() for v in vs if v["id"] not in have]


def search(query, n):
    from ddgs import DDGS
    with DDGS() as ddgs:
        return list(ddgs.images(query, max_results=n * 3, type_image="photo"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--out", type=Path, default=ROOT / "data/variant_web")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    manifest_path = args.out / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    todo = missing_variants()
    print(len(todo), "variants without photo")
    for fam, v in todo:
        vid = v["id"]
        if len(manifest.get(vid, [])) >= args.limit:
            continue
        refs = " ".join(v["reference_examples"][:1])
        query = f"{v['display_name']} {refs} wristwatch".strip()
        try:
            results = search(query, args.limit)
        except Exception as exc:
            print("search failed", vid, exc)
            time.sleep(5)
            continue
        folder = args.out / vid
        folder.mkdir(exist_ok=True)
        kept = manifest.setdefault(vid, [])
        for r in results:
            if len(kept) >= args.limit:
                break
            try:
                resp = requests.get(r["image"], headers=HEADERS, timeout=15)
                img = Image.open(BytesIO(resp.content)).convert("RGB")
            except Exception:
                continue
            if min(img.size) < 400:
                continue
            name = f"{len(kept)}.jpg"
            img.thumbnail((1000, 1000))
            img.save(folder / name, quality=88)
            kept.append({"file": f"{vid}/{name}", "page": r.get("url"), "title": r.get("title"),
                         "source": r.get("source")})
        print(vid, len(kept))
        manifest_path.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
        time.sleep(2)


if __name__ == "__main__":
    main()
