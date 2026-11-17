"""
Collect photos of NON-Rolex watches by web image search (negative test set for unknown-watch handling).

    python -m src.collection.other_brands_web --per-brand 14

Several queries per brand (product shot, worn on wrist, model names) so the set is varied.
Writes data/otherwatches_web/<brand>/*.jpg and manifest.json. Personal project, not redistributed.
"""
import argparse
import json
import time
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

from src.collection.variant_photos_web import HEADERS, search

ROOT = Path(__file__).resolve().parents[2]
BRANDS = {
    "omega": ["Omega Seamaster watch", "Omega Speedmaster wrist", "Omega Constellation watch"],
    "seiko": ["Seiko 5 Sports watch", "Grand Seiko wrist", "Seiko Prospex diver watch"],
    "casio": ["Casio G-Shock watch", "Casio Edifice wrist", "Casio vintage digital watch"],
    "tag_heuer": ["TAG Heuer Carrera watch", "TAG Heuer Monaco wrist", "TAG Heuer Aquaracer watch"],
    "tissot": ["Tissot PRX watch", "Tissot Gentleman wrist", "Tissot Seastar watch"],
    "longines": ["Longines Master Collection watch", "Longines HydroConquest wrist"],
    "patek_philippe": ["Patek Philippe Nautilus watch", "Patek Philippe Calatrava wrist"],
    "audemars_piguet": ["Audemars Piguet Royal Oak watch", "Audemars Piguet Royal Oak Offshore wrist"],
    "cartier": ["Cartier Tank watch", "Cartier Santos wrist", "Cartier Ballon Bleu watch"],
    "breitling": ["Breitling Navitimer watch", "Breitling Superocean wrist"],
    "iwc": ["IWC Pilot watch", "IWC Portugieser wrist"],
    "panerai": ["Panerai Luminor watch", "Panerai Radiomir wrist"],
    "hublot": ["Hublot Big Bang watch", "Hublot Classic Fusion wrist"],
    "citizen": ["Citizen Eco-Drive watch", "Citizen Promaster wrist"],
    "tudor": ["Tudor Black Bay watch", "Tudor Pelagos wrist"],
    "apple_watch": ["Apple Watch on wrist", "Apple Watch Ultra"],
    "garmin": ["Garmin Fenix watch", "Garmin Forerunner wrist"],
    "timex": ["Timex Weekender watch", "Timex Expedition wrist"],
    "swatch": ["Swatch watch", "Swatch Sistem51 wrist"],
    "fashion": ["Fossil watch", "Daniel Wellington watch", "Michael Kors watch wrist"],
    "other_luxury": ["Vacheron Constantin Overseas watch", "Jaeger-LeCoultre Reverso watch", "Hamilton Khaki watch", "Oris Aquis wrist"],
    "generic": ["analog wristwatch on wrist", "men's wristwatch product photo", "women's wristwatch photo"],
}
BAD = ("rolex", "oyster perpetual", "submariner", "datejust", "daytona")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-brand", type=int, default=14)
    parser.add_argument("--out", type=Path, default=ROOT / "data/otherwatches_web")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    mpath = args.out / "manifest.json"
    manifest = json.loads(mpath.read_text(encoding="utf-8")) if mpath.exists() else {}
    for brand, queries in BRANDS.items():
        kept = manifest.setdefault(brand, [])
        folder = args.out / brand
        folder.mkdir(exist_ok=True)
        seen = {e["image"] for e in kept}
        for q in queries:
            if len(kept) >= args.per_brand:
                break
            try:
                results = search(q, 8)
            except Exception as exc:
                print("search failed", q, exc)
                time.sleep(5)
                continue
            for r in results:
                if len(kept) >= args.per_brand or r["image"] in seen:
                    continue
                seen.add(r["image"])
                if any(w in (r.get("title") or "").lower() for w in BAD):
                    continue
                try:
                    img = Image.open(BytesIO(requests.get(r["image"], headers=HEADERS, timeout=15).content)).convert("RGB")
                except Exception:
                    continue
                if min(img.size) < 300:
                    continue
                img.thumbnail((1000, 1000))
                name = f"{len(kept)}.jpg"
                img.save(folder / name, quality=88)
                kept.append({"file": f"{brand}/{name}", "image": r["image"], "page": r.get("url"), "title": r.get("title")})
            time.sleep(2)
        print(brand, len(kept), flush=True)
        mpath.write_text(json.dumps(manifest, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
