"""
Collect open-licence Rolex photos from Wikimedia Commons for real-world variety.

Commons photos are real photos (wrists, shops, museums, events) with a licence recorded per file, which makes
them a good source for a real-world TEST set and a small amount of extra training data.

Usage:
    python -m src.collection.commons                    # all families
    python -m src.collection.commons --families milgauss oysterquartz --limit 80

Writes images to data/commons/<family>/ and data/commons/manifest.csv (title, page url, author, licence).
Only CC0, public domain, CC BY and CC BY-SA files are kept. Attribution details are in the manifest: if you
redistribute images or models trained on CC BY-SA data, check the licence terms and credit the authors.

Labels are weak (they come from category and file name), so run the watch detector and the review page
before using these images. They are NOT mixed into training automatically.
"""
import argparse
import csv
import re
import time
from pathlib import Path

import requests

API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "WatchDatasetResearch/0.1 (open-licence image collection for a hobby ML project)"}

FAMILY_QUERIES = {
    "airking": {"categories": ["Rolex Air-King"], "words": ["air-king", "air king", "airking"]},
    "cellini": {"categories": ["Rolex Cellini"], "words": ["cellini"]},
    "datejust": {"categories": ["Rolex Datejust"], "words": ["datejust"]},
    "daytona": {"categories": ["Rolex Daytona"], "words": ["daytona"]},
    "explorer": {"categories": ["Rolex Explorer"], "words": ["explorer"]},
    "gmt_master": {"categories": ["Rolex GMT-Master", "Rolex GMT-Master II"], "words": ["gmt"]},
    "milgauss": {"categories": ["Rolex Milgauss"], "words": ["milgauss"]},
    "oyster_perpetual": {"categories": ["Rolex Oyster Perpetual"], "words": ["oyster perpetual"]},
    "oysterquartz": {"categories": ["Rolex Oysterquartz"], "words": ["oysterquartz", "oyster quartz"]},
    "president": {"categories": ["Rolex Day-Date"], "words": ["day-date", "daydate", "president"]},
    "sea_dweller": {"categories": ["Rolex Sea-Dweller", "Rolex Deepsea"], "words": ["sea-dweller", "sea dweller", "deepsea"]},
    "submariner": {"categories": ["Rolex Submariner"], "words": ["submariner"]},
    "turn_o_graph": {"categories": ["Rolex Turn-O-Graph"], "words": ["turn-o-graph", "turn o graph", "thunderbird"]},
    "yacht_master": {"categories": ["Rolex Yacht-Master"], "words": ["yacht-master", "yacht master", "yachtmaster"]},
}

ALLOWED_LICENCE = re.compile(r"^(cc0|public domain|pd|cc[ -]by(?!-nc)(?!-nd))", re.I)
SKIP_TITLE = re.compile(
    r"case ?back|back of|movement|calibre|caliber|logo|boutique|store|shop|building|sign|poster|"
    r"advert|race|car |crown only|box|packag|certificate|clock tower|museum label",
    re.I,
)


def get(url: str, **kwargs) -> requests.Response:
    """GET with a polite delay and back-off on 429/5xx (Commons rate-limits quick scripts)."""
    for attempt in range(6):
        response = requests.get(url, headers=HEADERS, timeout=60, **kwargs)
        if response.status_code in (429, 500, 502, 503, 504):
            wait = float(response.headers.get("Retry-After", 20 * (attempt + 1)))
            print(f"  waiting {wait:.0f}s ({response.status_code})", flush=True)
            time.sleep(wait)
            continue
        response.raise_for_status()
        time.sleep(1.0)
        return response
    response.raise_for_status()
    return response


def api(params: dict) -> dict:
    return get(API, params={"format": "json", **params}).json()


def file_info(titles: list[str]) -> list[dict]:
    out = []
    for start in range(0, len(titles), 40):
        data = api({
            "action": "query", "titles": "|".join(titles[start:start + 40]), "prop": "imageinfo",
            "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "1024",
        })
        for page in data.get("query", {}).get("pages", {}).values():
            if page.get("imageinfo"):
                out.append({"title": page["title"], **page["imageinfo"][0]})
    return out


def category_files(category: str, depth: int = 1) -> list[str]:
    titles, subcats = [], []
    cont: dict = {}
    while True:
        data = api({"action": "query", "list": "categorymembers", "cmtitle": f"Category:{category}",
                    "cmtype": "file|subcat", "cmlimit": "500", **cont})
        for member in data.get("query", {}).get("categorymembers", []):
            (subcats if member["ns"] == 14 else titles).append(member["title"])
        if "continue" not in data:
            break
        cont = data["continue"]
    if depth > 0:
        for sub in subcats[:40]:
            titles += category_files(sub.removeprefix("Category:"), depth - 1)
    return titles


def search_files(query: str, limit: int = 100) -> list[str]:
    data = api({"action": "query", "list": "search", "srsearch": query, "srnamespace": "6", "srlimit": str(limit)})
    return [hit["title"] for hit in data.get("query", {}).get("search", [])]


def plain(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value or "").strip()


def accept(info: dict, words: list[str]) -> tuple[bool, str]:
    meta = info.get("extmetadata", {})
    licence = plain(meta.get("LicenseShortName", {}).get("value", ""))
    if not ALLOWED_LICENCE.match(licence):
        return False, "licence"
    if info.get("mime") not in ("image/jpeg", "image/png"):
        return False, "type"
    if min(info.get("width", 0), info.get("height", 0)) < 400:
        return False, "small"
    title = info["title"]
    if SKIP_TITLE.search(title):
        return False, "title"
    text = (title + " " + plain(meta.get("ImageDescription", {}).get("value", ""))).lower()
    if not any(w in text for w in words):
        return False, "no family word"
    return True, licence


def collect(families: list[str], out_root: Path, limit: int):
    out_root.mkdir(parents=True, exist_ok=True)
    manifest_path = out_root / "manifest.csv"
    seen = set()
    if manifest_path.exists():
        with manifest_path.open(encoding="utf-8", newline="") as handle:
            seen = {row["title"] for row in csv.DictReader(handle)}
    new_file = not manifest_path.exists()
    with manifest_path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        if new_file:
            writer.writerow(["family", "title", "page_url", "image_url", "author", "licence", "width", "height", "file"])
        for family in families:
            spec = FAMILY_QUERIES[family]
            titles = []
            for category in spec["categories"]:
                titles += category_files(category)
            titles += search_files("Rolex " + spec["words"][0].replace("-", " "))
            titles = [t for t in dict.fromkeys(titles) if t not in seen and t.lower().endswith((".jpg", ".jpeg", ".png"))]
            kept, reasons = 0, {}
            for info in file_info(titles):
                if kept >= limit:
                    break
                ok, reason = accept(info, spec["words"])
                if not ok:
                    reasons[reason] = reasons.get(reason, 0) + 1
                    continue
                target = out_root / family / (re.sub(r"[^A-Za-z0-9._-]+", "_", info["title"].removeprefix("File:"))[:120])
                target = target.with_suffix(".jpg")
                target.parent.mkdir(parents=True, exist_ok=True)
                image_url = info.get("thumburl") or info["url"]
                try:
                    data = get(image_url)
                except requests.HTTPError:
                    continue
                from io import BytesIO

                from PIL import Image

                Image.open(BytesIO(data.content)).convert("RGB").save(target, quality=92)
                meta = info.get("extmetadata", {})
                writer.writerow([
                    family, info["title"], info.get("descriptionurl", ""), info["url"],
                    plain(meta.get("Artist", {}).get("value", "")), reason,
                    info.get("width"), info.get("height"), str(target).replace("\\", "/"),
                ])
                handle.flush()
                kept += 1
            print(f"{family:18s} candidates={len(titles):4d} kept={kept:3d} rejected={reasons}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Collect open-licence Rolex photos from Wikimedia Commons")
    parser.add_argument("--families", nargs="+", default=list(FAMILY_QUERIES))
    parser.add_argument("--out-root", type=Path, default=Path("data/commons"))
    parser.add_argument("--limit", type=int, default=120, help="max images per family")
    args = parser.parse_args()
    collect(args.families, args.out_root, args.limit)


if __name__ == "__main__":
    main()
