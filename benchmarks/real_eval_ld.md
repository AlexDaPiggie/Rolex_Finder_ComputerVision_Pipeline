# Real-photo benchmark

454 real photos (Wikimedia Commons, Flickr via Openverse) after removing non-watch images and duplicates. Full pipeline: detect watch, then the preprocessing variant shown. Labels come from titles and categories, so a few are wrong. Datejust and Daytona dominate the set, so read the macro column too.

| Model / preprocessing | Accuracy | 95% interval | Macro (families with 5+ photos) |
|---|---|---|---|
| clip_head/avg(full,crop,dial) | 98.9% | 97%-100% | 0.989 |
| clip_head/crop | 98.5% | 97%-99% | 0.981 |
| clip_head/full | 98.2% | 97%-99% | 0.985 |
| clip_head/dial | 97.4% | 95%-98% | 0.967 |
| clip_head/aligned | 96.0% | 94%-98% | 0.961 |

Retailer test split: {"weight_decay": 0.01, "val_clean": 0.8673, "val_aug": 0.7964, "test_clean": 0.9698, "test_aug": 0.919}
