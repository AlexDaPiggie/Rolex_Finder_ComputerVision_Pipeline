"""
Collect open-licence photos of NON-Rolex watches. They are the negative test set for unknown-watch handling:
the model should say "not a Rolex I know" for these, not name the nearest Rolex family.

    python -m src.collection.other_brands --limit 12

Same sources, licences and rules as src/collection/openverse.py (private test set, never redistributed).
Titles that mention Rolex are skipped, so the labels are brands that are not Rolex. Writes data/otherwatches/.
"""
import argparse
import re
from pathlib import Path

from src.collection import openverse

BRANDS = {
    "omega": ["omega seamaster", "omega speedmaster", "omega watch"],
    "seiko": ["seiko watch", "seiko 5", "grand seiko"],
    "casio": ["casio g-shock", "casio watch"],
    "tag_heuer": ["tag heuer carrera", "tag heuer watch"],
    "tissot": ["tissot watch"],
    "longines": ["longines watch"],
    "patek_philippe": ["patek philippe", "patek philippe nautilus"],
    "audemars_piguet": ["audemars piguet royal oak"],
    "cartier": ["cartier tank watch", "cartier santos watch"],
    "breitling": ["breitling navitimer", "breitling watch"],
    "iwc": ["iwc pilot watch", "iwc portugieser"],
    "panerai": ["panerai luminor"],
    "hublot": ["hublot big bang"],
    "citizen": ["citizen eco-drive watch"],
    "tudor": ["tudor black bay", "tudor watch"],
    "apple_watch": ["apple watch wrist"],
    "garmin": ["garmin watch", "garmin fenix"],
    "timex": ["timex watch"],
    "swatch": ["swatch watch"],
    "generic": ["wristwatch", "analog wrist watch"],
}


def main():
    openverse.AUTH.update(openverse.load_token())
    # keep the usual skip words and also skip anything that mentions Rolex
    openverse.SKIP = re.compile(openverse.SKIP.pattern + "|rolex|oyster perpetual", re.I)
    for brand, queries in BRANDS.items():
        words = [brand.replace("_", " "), brand.replace("_", "-")] if brand != "generic" else ["watch"]
        openverse.FAMILIES[brand] = (queries, words)
    parser = argparse.ArgumentParser(description="Collect open-licence photos of non-Rolex watches")
    parser.add_argument("--brands", nargs="+", default=list(BRANDS))
    parser.add_argument("--out-root", type=Path, default=Path("data/otherwatches"))
    parser.add_argument("--limit", type=int, default=12, help="photos per brand")
    parser.add_argument("--per-creator", type=int, default=2)
    args = parser.parse_args()
    openverse.collect(args.brands, args.out_root, args.limit, args.per_creator)


if __name__ == "__main__":
    main()
