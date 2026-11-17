# Real-photo benchmark

133 real photos (Wikimedia Commons, Flickr via Openverse) after removing non-watch images and duplicates. Full pipeline: detect watch, then the preprocessing variant shown. Labels come from titles and categories, so a few are wrong. Datejust and Daytona dominate the set, so read the macro column too.

| Model / preprocessing | Accuracy | 95% interval | Macro (families with 5+ photos) |
|---|---|---|---|
| clip_head/avg(full,crop,dial) | 99.2% | 96%-100% | 0.997 |
| clip_head/full | 97.7% | 94%-99% | 0.991 |
| clip_head/crop | 97.7% | 94%-99% | 0.991 |
| clip_head/aligned | 94.7% | 90%-97% | 0.978 |
| clip_head/dial | 94.7% | 90%-97% | 0.978 |
| ensemble(clip_head+effnet_base)/crop | 75.9% | 68%-82% | 0.81 |
| ensemble(clip_head+effnet_real_aug)/crop | 75.9% | 68%-82% | 0.752 |
| ensemble(clip_head+effnet_base)/dial | 74.4% | 66%-81% | 0.833 |
| ensemble(clip_head+effnet_real_aug)/dial | 74.4% | 66%-81% | 0.817 |
| ensemble(clip_head+effnet_cand)/crop | 71.4% | 63%-78% | 0.757 |
| ensemble(clip_head+effnet_cand)/dial | 67.7% | 59%-75% | 0.73 |
| effnet_real_aug/dial | 54.1% | 46%-62% | 0.577 |
| effnet_real_aug/crop | 51.1% | 43%-60% | 0.485 |
| effnet_cand/dial | 51.1% | 43%-60% | 0.534 |
| effnet_real_aug/aligned | 47.4% | 39%-56% | 0.469 |
| effnet_cand/crop | 44.4% | 36%-53% | 0.444 |
| effnet_real_aug/full | 42.1% | 34%-51% | 0.4 |
| effnet_cand/aligned | 41.4% | 33%-50% | 0.419 |
| effnet_cand/full | 39.8% | 32%-48% | 0.373 |
| effnet_base/dial | 38.3% | 30%-47% | 0.422 |
| effnet_base/crop | 37.6% | 30%-46% | 0.396 |
| effnet_base/aligned | 30.1% | 23%-38% | 0.347 |
| effnet_base/full | 29.3% | 22%-38% | 0.304 |

Retailer test split: {"weight_decay": 0.1, "val_clean": 0.9721, "val_aug": 0.9265, "test_clean": 0.9698, "test_aug": 0.925}
