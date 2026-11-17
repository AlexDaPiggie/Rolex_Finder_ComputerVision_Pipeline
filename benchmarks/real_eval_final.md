# Real-photo benchmark

273 real photos (Wikimedia Commons, Flickr via Openverse) after removing non-watch images and duplicates. Full pipeline: detect watch, then the preprocessing variant shown. Labels come from titles and categories, so a few are wrong. Datejust and Daytona dominate the set, so read the macro column too.

| Model / preprocessing | Accuracy | 95% interval | Macro (families with 5+ photos) |
|---|---|---|---|
| clip_head/avg(full,crop,dial) | 98.2% | 96%-99% | 0.988 |
| clip_head/crop | 97.4% | 95%-99% | 0.98 |
| clip_head/full | 97.1% | 94%-98% | 0.982 |
| clip_head/dial | 95.2% | 92%-97% | 0.962 |
| clip_head/aligned | 94.1% | 91%-96% | 0.957 |
| ensemble(clip_head+effnet_real_aug)/crop | 81.7% | 77%-86% | 0.823 |
| ensemble(clip_head+effnet_real_aug)/dial | 80.2% | 75%-84% | 0.828 |
| ensemble(clip_head+effnet_base)/crop | 79.9% | 75%-84% | 0.82 |
| ensemble(clip_head+effnet_base)/dial | 79.5% | 74%-84% | 0.838 |
| ensemble(clip_head+effnet_cand)/dial | 75.5% | 70%-80% | 0.809 |
| ensemble(clip_head+effnet_cand)/crop | 74.7% | 69%-80% | 0.779 |
| effnet_real_aug/dial | 64.8% | 59%-70% | 0.684 |
| effnet_real_aug/crop | 62.3% | 56%-68% | 0.642 |
| effnet_cand/dial | 57.5% | 52%-63% | 0.639 |
| effnet_real_aug/aligned | 56.8% | 51%-62% | 0.606 |
| effnet_real_aug/full | 50.2% | 44%-56% | 0.547 |
| effnet_base/dial | 49.5% | 44%-55% | 0.548 |
| effnet_cand/crop | 49.1% | 43%-55% | 0.546 |
| effnet_base/crop | 45.8% | 40%-52% | 0.506 |
| effnet_cand/aligned | 45.4% | 40%-51% | 0.524 |
| effnet_cand/full | 42.1% | 36%-48% | 0.457 |
| effnet_base/aligned | 38.1% | 32%-44% | 0.445 |
| effnet_base/full | 35.5% | 30%-41% | 0.394 |

Retailer test split: {"weight_decay": 0.1, "val_clean": 0.9721, "val_aug": 0.9265, "test_clean": 0.9644, "test_aug": 0.9205}
