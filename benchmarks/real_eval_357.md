# Real-photo benchmark

294 real photos (Wikimedia Commons, Flickr via Openverse) after removing non-watch images and duplicates. Full pipeline: detect watch, then the preprocessing variant shown. Labels come from titles and categories, so a few are wrong. Datejust and Daytona dominate the set, so read the macro column too.

| Model / preprocessing | Accuracy | 95% interval | Macro (families with 5+ photos) |
|---|---|---|---|
| ensemble(clip_head+effnet_real_aug)/dial | 68.4% | 63%-73% | 0.713 |
| ensemble(clip_head+effnet_cand)/dial | 66.7% | 61%-72% | 0.726 |
| ensemble(clip_head+effnet_real_aug)/crop | 66.3% | 61%-72% | 0.699 |
| effnet_real_aug/dial | 65.0% | 59%-70% | 0.681 |
| clip_head/avg(full,crop,dial) | 63.3% | 58%-69% | 0.636 |
| clip_head/dial | 62.6% | 57%-68% | 0.661 |
| effnet_real_aug/crop | 61.2% | 56%-67% | 0.636 |
| ensemble(clip_head+effnet_base)/dial | 59.5% | 54%-65% | 0.663 |
| clip_head/crop | 59.2% | 54%-65% | 0.597 |
| ensemble(clip_head+effnet_base)/crop | 58.2% | 52%-64% | 0.609 |
| effnet_cand/dial | 57.1% | 51%-63% | 0.639 |
| clip_head/aligned | 56.5% | 51%-62% | 0.564 |
| effnet_real_aug/aligned | 56.5% | 51%-62% | 0.605 |
| ensemble(clip_head+effnet_cand)/crop | 56.5% | 51%-62% | 0.604 |
| clip_head/full | 50.0% | 44%-56% | 0.492 |
| effnet_real_aug/full | 49.0% | 43%-55% | 0.547 |
| effnet_cand/crop | 48.6% | 43%-54% | 0.548 |
| effnet_base/dial | 48.6% | 43%-54% | 0.538 |
| effnet_base/crop | 45.2% | 40%-51% | 0.502 |
| effnet_cand/aligned | 45.2% | 40%-51% | 0.527 |
| effnet_cand/full | 41.2% | 36%-47% | 0.458 |
| effnet_base/aligned | 38.1% | 33%-44% | 0.443 |
| effnet_base/full | 35.4% | 30%-41% | 0.398 |

Retailer test split: {"weight_decay": 0.1, "val_clean": 0.9721, "val_aug": 0.9265, "test_clean": 0.9708, "test_aug": 0.9307}
