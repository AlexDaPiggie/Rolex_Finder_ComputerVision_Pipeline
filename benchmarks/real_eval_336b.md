# Real-photo benchmark

273 real photos (Wikimedia Commons, Flickr via Openverse) after removing non-watch images and duplicates. Full pipeline: detect watch, then the preprocessing variant shown. Labels come from titles and categories, so a few are wrong. Datejust and Daytona dominate the set, so read the macro column too.

| Model / preprocessing | Accuracy | 95% interval | Macro (families with 5+ photos) |
|---|---|---|---|
| ensemble(clip_head+effnet_real_aug)/dial | 67.4% | 62%-73% | 0.711 |
| ensemble(clip_head+effnet_real_aug)/crop | 66.7% | 61%-72% | 0.7 |
| ensemble(clip_head+effnet_cand)/dial | 66.3% | 60%-72% | 0.726 |
| effnet_real_aug/dial | 64.8% | 59%-70% | 0.684 |
| clip_head/avg(full,crop,dial) | 63.7% | 58%-69% | 0.645 |
| clip_head/dial | 62.6% | 57%-68% | 0.666 |
| effnet_real_aug/crop | 62.3% | 56%-68% | 0.642 |
| clip_head/crop | 59.3% | 53%-65% | 0.603 |
| ensemble(clip_head+effnet_base)/dial | 59.3% | 53%-65% | 0.666 |
| ensemble(clip_head+effnet_base)/crop | 59.0% | 53%-65% | 0.616 |
| effnet_cand/dial | 57.5% | 52%-63% | 0.639 |
| ensemble(clip_head+effnet_cand)/crop | 57.1% | 51%-63% | 0.607 |
| effnet_real_aug/aligned | 56.8% | 51%-62% | 0.606 |
| clip_head/aligned | 56.4% | 50%-62% | 0.569 |
| effnet_real_aug/full | 50.2% | 44%-56% | 0.547 |
| clip_head/full | 49.8% | 44%-56% | 0.492 |
| effnet_base/dial | 49.5% | 44%-55% | 0.548 |
| effnet_cand/crop | 49.1% | 43%-55% | 0.546 |
| effnet_base/crop | 45.8% | 40%-52% | 0.506 |
| effnet_cand/aligned | 45.4% | 40%-51% | 0.524 |
| effnet_cand/full | 42.1% | 36%-48% | 0.457 |
| effnet_base/aligned | 38.1% | 32%-44% | 0.445 |
| effnet_base/full | 35.5% | 30%-41% | 0.394 |

Retailer test split: {"weight_decay": 0.1, "val_clean": 0.9721, "val_aug": 0.9265, "test_clean": 0.9708, "test_aug": 0.9307}
