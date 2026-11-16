"""
Collect open-licence real-life Rolex photos through the Openverse API (Flickr, Wikimedia Commons and others).

These photos (wrists, desks, shop windows, events) are for a real-world TEST set. They are not mixed into training.

Usage:
    python -m src.collection.openverse                       # all families, up to 40 photos each
    python -m src.collection.openverse --families milgauss --limit 30

Writes data/realworld/test/<family>/*.jpg and data/realworld/manifest.csv (title, creator, licence, source page).
All Creative Commons licences are kept, including NC and ND, because the set is private (git-ignored, never
redistributed, never used commercially). Do not publish these images. Creators and licences are in the manifest. Labels come from the title and tags, so look at the
contact sheets (python -m src.collection.contact_sheet) before trusting a family.
"""
import argparse
import csv
import re
import time
from io import BytesIO
from pathlib import Path

import numpy as np
import requests
from PIL import Image

API = "https://api.openverse.org/v1/images/"
HEADERS = {"User-Agent": "WatchDatasetResearch/0.1 (open-licence image collection for a hobby ML project)"}
# NC/ND licences are kept because this is a private test set that is never redistributed or used commercially.
ALLOWED = {"cc0", "pdm", "by", "by-sa", "by-nc", "by-nc-sa", "by-nd", "by-nc-nd"}

# query terms and words that must appear in title/tags for the label to be trusted
FAMILIES = {
    "airking": (["rolex air-king", "rolex airking"], ["air-king", "air king", "airking"]),
    "cellini": (["rolex cellini"], ["cellini"]),
    "datejust": (["rolex datejust"], ["datejust"]),
    "daytona": (["rolex daytona", "rolex daytona wrist"], ["daytona"]),
    "explorer": (["rolex explorer", "rolex explorer ii"], ["explorer"]),
    "gmt_master": (["rolex gmt-master", "rolex gmt master ii"], ["gmt"]),
    "milgauss": (["rolex milgauss"], ["milgauss"]),
    "oyster_perpetual": (["rolex oyster perpetual"], ["oyster perpetual"]),
    "oysterquartz": (["rolex oysterquartz"], ["oysterquartz", "oyster quartz"]),
    "president": (["rolex day-date", "rolex president"], ["day-date", "daydate", "president"]),
    "sea_dweller": (["rolex sea-dweller", "rolex deepsea"], ["sea-dweller", "sea dweller", "deepsea"]),
    "submariner": (["rolex submariner", "rolex submariner wrist"], ["submariner"]),
    "turn_o_graph": (["rolex turn-o-graph", "rolex thunderbird"], ["turn-o-graph", "turn o graph", "thunderbird"]),
    "yacht_master": (["rolex yacht-master"], ["yacht-master", "yacht master", "yachtmaster"]),
}
SKIP = re.compile(r"case ?back|back of|movement|calibre|logo|boutique|store|shop window|building|poster|advert|box|catalog|auction lot", re.I)


def get(url: str, **kwargs) -> requests.Response:
    for attempt in range(6):
        response = requests.get(url, headers=HEADERS, timeout=60, **kwargs)
        if response.status_code in (429, 500, 502, 503, 504):
            wait = float(response.headers.get("Retry-After", 15 * (attempt + 1)))
            print(f"  waiting {min(wait, 120):.0f}s ({response.status_code})", flush=True)
            time.sleep(min(wait, 120))
            continue
        response.raise_for_status()
        time.sleep(1.0)
        return response
    response.raise_for_status()
    return response


def dhash(image: Image.Image, size: int = 16) -> np.ndarray:
    gray = np.asarray(image.convert("L").resize((size + 1, size)), dtype=np.int16)
    return np.packbits((gray[:, 1:] > gray[:, :-1]).flatten())


def is_duplicate(h: np.ndarray, seen: list[np.ndarray], max_distance: int = 10) -> bool:
    return bool(seen) and int(np.unpackbits(np.stack(seen) ^ h, axis=1).sum(axis=1).min()) <= max_distance


def collect(families, out_root: Path, limit: int, per_creator: int):
    out_root.mkdir(parents=True, exist_ok=True)
    manifest = out_root / "manifest.csv"
    new = not manifest.exists()
    seen_hashes: list[np.ndarray] = []
    seen_ids = set()
    if not new:
        with manifest.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                seen_ids.add(row["openverse_id"])
                try:
                    seen_hashes.append(dhash(Image.open(row["file"])))
                except Exception:
                    pass
    with manifest.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        if new:
            writer.writerow(["family", "openverse_id", "title", "creator", "licence", "source", "page_url", "image_url", "file"])
        for family in families:
            queries, words = FAMILIES[family]
            kept, creators = 0, {}
            existing = len(list((out_root / "test" / family).glob("*.jpg"))) if (out_root / "test" / family).exists() else 0
            for query in queries:
                for page in range(1, 11):
                    if kept + existing >= limit:
                        break
                    try:
                        data = get(API, params={"q": query, "page": page, "page_size": 20, "license": ",".join(sorted(ALLOWED))}).json()
                    except requests.HTTPError:
                        break
                    for item in data.get("results", []):
                        if kept + existing >= limit:
                            break
                        text = (item.get("title") or "") + " " + " ".join(t.get("name", "") for t in item.get("tags") or [])
                        low = text.lower()
                        creator = item.get("creator") or "unknown"
                        if (item["id"] in seen_ids or not any(w in low for w in words) or SKIP.search(text)
                                or min(item.get("width") or 0, item.get("height") or 0) < 400
                                or creators.get(creator, 0) >= per_creator):
                            continue
                        try:
                            image = Image.open(BytesIO(get(item["url"]).content)).convert("RGB")
                        except Exception:
                            continue
                        image.thumbnail((1280, 1280))
                        h = dhash(image)
                        if is_duplicate(h, seen_hashes):
                            continue
                        target = out_root / "test" / family / f"{item['id']}.jpg"
                        target.parent.mkdir(parents=True, exist_ok=True)
                        image.save(target, quality=92)
                        seen_hashes.append(h)
                        seen_ids.add(item["id"])
                        creators[creator] = creators.get(creator, 0) + 1
                        writer.writerow([family, item["id"], item.get("title", ""), creator, item.get("license", ""),
                                         item.get("source", ""), item.get("foreign_landing_url", ""), item["url"],
                                         str(target).replace("\\", "/")])
                        handle.flush()
                        kept += 1
            print(f"{family:18s} kept={kept:3d} total={kept + existing}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Collect open-licence real-life Rolex photos")
    parser.add_argument("--families", nargs="+", default=list(FAMILIES))
    parser.add_argument("--out-root", type=Path, default=Path("data/realworld"))
    parser.add_argument("--limit", type=int, default=40, help="photos per family")
    parser.add_argument("--per-creator", type=int, default=4, help="max photos per creator and family")
    args = parser.parse_args()
    collect(args.families, args.out_root, args.limit, args.per_creator)


if __name__ == "__main__":
    main()
