# Training data plan

Goal: a model that works on real phone photos, and a benchmark you can trust.

## Why the current numbers are optimistic

- Training data is one retailer (swisswatchexpo): clean studio photos.
- The website feeds the model tight dial crops, but training used full photos.
- The split was random per photo, so other photos of the same listing can sit in train and test
  (`docs/benchmark.md` leakage check: about 13% of test images have a near-duplicate in train).
- Classes are very uneven (Datejust 6,457 train images, Milgauss 136).

## Pipeline (run from the project root)

| Step | Command | Output |
|---|---|---|
| 1. Group-aware split | `python -m src.training.group_split` | `data/grouped/` (all photos of a listing share a split) |
| 2. Find label errors | `python -m src.training.find_label_errors` then `python -m src.training.label_review_page build` | `benchmarks/label_review.html`: decide per image, click Export, then `python -m src.training.label_review_page apply --decisions label_decisions.json --data-root data/grouped` (removed photos go to `data/grouped/_removed`) |
| 3. Crop like the website | `python -m src.training.prepare_crops --data-root data/grouped --out-root data/grouped_crops` | `data/grouped_crops/` + `crop_report.json`. Needs a GPU (about 10 s per image on CPU) |
| 4. Train | `python -m src.training.train --data-root data/grouped_crops --balance loss --device auto --output models/candidate.pt` | new checkpoint (does not overwrite the live model) |
| 5. Benchmark | `python -m src.training.benchmark --data-root data/grouped_crops --checkpoint models/candidate.pt --check-leakage` | `docs/benchmark.md` |
| 6. Real-world check | see below | the number that matters |

Compare step 5 against the numbers for the current model in `docs/benchmark.md` before replacing
`models/rolex_classifier_model.pt`. Expect the grouped, cropped test set to score lower than the old
99.2%: that is the honest number, not a regression.

## Real-world test set (most important, small, never train on it)

Collect 20-30 photos per family that are NOT from the retailer: wrist shots, angles, low light,
screenshots, marketplace and auction photos you are allowed to use, your own photos.

Layout:

```
data/realworld/
  class_mapping.json        (copy from data/processed/)
  test/
    daytona/*.jpg
    submariner/*.jpg
    ...
```

Run: `python -m src.training.benchmark --data-root data/realworld --split test --json-out benchmarks/realworld.json --md-out docs/benchmark_realworld.md`

Keep it frozen. Once you train on it, it stops being a test.

## Further ideas (not built yet)

- "Not a Rolex" negatives (Omega, Tudor, Seiko, non-watch images) to train and test out-of-scope rejection.
- Reference-level labels (116508, 126610LN) and nearest-neighbour retrieval instead of CLIP text prompts.
- A "wrong? tell us" button on the site, with consent, to collect hard examples.
- Temperature scaling on a held-out split so confidence matches accuracy.

## What was added in code

- `src/training/benchmark.py`: metrics, leakage check, markdown report.
- `src/training/group_split.py`, `prepare_crops.py`, `find_label_errors.py`: steps 1-3.
- `src/training/train.py`: `--data-root`, `--output`, `--device`, `--balance loss`, `--num-workers`.
- `src/training/dataset.py`: blur and JPEG-compression augmentation (phone-photo realism).

## Run steps 3-5 on a Modal GPU

`modal_train.py` does crop, train and benchmark (new model and current model on the same test split) in one command.
See the header of that file for setup, flags and cost. Short version:

```
modal run modal_train.py::upload     # after fixing labels in data/grouped
modal run modal_train.py::main      # results land in models/candidate.pt, docs/benchmark_candidate.md, ...
```
