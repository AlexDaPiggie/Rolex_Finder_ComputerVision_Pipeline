# Classifier benchmark

Generated 2026-11-15 on split `test` of `data/processed` (3731 images, CPU).

**What this measures:** the EfficientNet-B0 family classifier only, on crops from the same collection as the training data. It does not measure the full pipeline (detection, alignment, variant matching) or real-world phone photos, so treat it as an optimistic upper bound.

| Metric | Value |
|---|---|
| Top-1 accuracy | 99.2% |
| Top-3 accuracy | 99.9% |
| Macro F1 | 0.985 |
| Balanced accuracy (mean recall) | 97.9% |
| Calibration error (ECE, lower is better) | 0.002 |
| Mean confidence | 99.3% |
| Latency per image (CPU, batched) | 21.7 ms |

## Train/test leakage check

494 of 3731 test images (13.2%) have a near-duplicate in the training set (256-bit dHash distance <= 6; a conservative count, similar photos of the same watch can be further apart). Accuracy on those images is inflated.

## Per class

| Class | Images | Precision | Recall | F1 |
|---|---|---|---|---|
| oysterquartz | 32 | 1.00 | 0.84 | 0.92 |
| turn_o_graph | 82 | 0.99 | 0.95 | 0.97 |
| oyster_perpetual | 251 | 0.95 | 0.99 | 0.97 |
| airking | 204 | 0.99 | 0.97 | 0.98 |
| milgauss | 30 | 1.00 | 0.97 | 0.98 |
| president | 467 | 0.98 | 1.00 | 0.99 |
| gmt_master | 181 | 0.99 | 0.99 | 0.99 |
| datejust | 1385 | 1.00 | 0.99 | 0.99 |
| cellini | 218 | 1.00 | 1.00 | 1.00 |
| submariner | 301 | 1.00 | 1.00 | 1.00 |
| daytona | 144 | 1.00 | 1.00 | 1.00 |
| explorer | 172 | 1.00 | 1.00 | 1.00 |
| sea_dweller | 77 | 1.00 | 1.00 | 1.00 |
| yacht_master | 187 | 1.00 | 1.00 | 1.00 |

## Most confused pairs

| True | Predicted | Count |
|---|---|---|
| datejust | oyster_perpetual | 7 |
| airking | oyster_perpetual | 5 |
| oysterquartz | president | 4 |
| turn_o_graph | datejust | 3 |
| datejust | president | 2 |
| airking | datejust | 1 |
| airking | turn_o_graph | 1 |
| cellini | president | 1 |

## If the app only answered when confident

| Confidence threshold | Share answered | Accuracy on those |
|---|---|---|
| >= 0.5 | 100.0% | 99.2% |
| >= 0.7 | 99.6% | 99.4% |
| >= 0.9 | 98.6% | 99.6% |
| >= 0.95 | 97.5% | 99.6% |
