"""
Collect open-licence photos of NON-Rolex watches from Wikimedia Commons (negative test set for unknown-watch handling).

    python -m src.collection.other_brands_commons --limit 12

Same rules as src/collection/commons.py (CC0, public domain, CC BY, CC BY-SA). Titles that mention Rolex are skipped.
Writes data/otherwatches_commons/<brand>/ and manifest.csv.
"""
import argparse
import re
from pathlib import Path

from src.collection import commons

BRANDS = {
    "omega": (["Omega watches", "Omega Seamaster", "Omega Speedmaster"], ["omega"]),
    "seiko": (["Seiko watches", "Grand Seiko"], ["seiko"]),
    "casio": (["Casio watches", "G-Shock"], ["casio", "g-shock"]),
    "tag_heuer": (["TAG Heuer watches"], ["tag heuer", "heuer"]),
    "tissot": (["Tissot watches"], ["tissot"]),
    "longines": (["Longines watches"], ["longines"]),
    "patek_philippe": (["Patek Philippe watches"], ["patek"]),
    "audemars_piguet": (["Audemars Piguet watches"], ["audemars", "royal oak"]),
    "cartier": (["Cartier watches"], ["cartier"]),
    "breitling": (["Breitling watches"], ["breitling"]),
    "iwc": (["IWC watches"], ["iwc"]),
    "panerai": (["Panerai watches"], ["panerai"]),
    "hublot": (["Hublot watches"], ["hublot"]),
    "citizen": (["Citizen watches"], ["citizen"]),
    "tudor": (["Tudor watches"], ["tudor"]),
    "apple_watch": (["Apple Watch"], ["apple watch"]),
    "garmin": (["Garmin watches"], ["garmin"]),
    "timex": (["Timex watches"], ["timex"]),
    "swatch": (["Swatch watches"], ["swatch"]),
}


def main():
    commons.SKIP_TITLE = re.compile(commons.SKIP_TITLE.pattern + "|rolex", re.I)
    for brand, (categories, words) in BRANDS.items():
        commons.FAMILY_QUERIES[brand] = {"categories": categories, "words": words}
    parser = argparse.ArgumentParser(description="Collect open-licence photos of non-Rolex watches from Commons")
    parser.add_argument("--brands", nargs="+", default=list(BRANDS))
    parser.add_argument("--out-root", type=Path, default=Path("data/otherwatches_commons"))
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    commons.collect(args.brands, args.out_root, args.limit)


if __name__ == "__main__":
    main()
