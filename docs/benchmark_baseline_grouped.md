# Classifier benchmark

Generated 2026-11-16 on split `test` of `/tmp/crops` (2006 images).

**What this measures:** the EfficientNet-B0 family classifier only, on crops from the same collection as the training data. It does not measure the full pipeline (detection, alignment, variant matching) or real-world phone photos, so treat it as an optimistic upper bound.

Device: cuda.

| Metric | Value |
|---|---|
| Top-1 accuracy | 99.5% |
| Top-3 accuracy | 100.0% |
| Macro F1 | 0.994 |
| Balanced accuracy (mean recall) | 99.3% |
| Calibration error (ECE, lower is better) | 0.006 |
| Mean confidence | 99.1% |
| Latency per image (batched) | 3.8 ms |

## Train/test leakage check

6 of 2006 test images (0.3%) have a near-duplicate in the training set (256-bit dHash distance <= 6; a conservative count, similar photos of the same watch can be further apart). Accuracy on those images is inflated.

## Per class

| Class | Images | Precision | Recall | F1 |
|---|---|---|---|---|
| turn_o_graph | 48 | 1.00 | 0.96 | 0.98 |
| airking | 129 | 0.98 | 0.98 | 0.98 |
| oyster_perpetual | 128 | 0.97 | 0.99 | 0.98 |
| sea_dweller | 55 | 1.00 | 0.98 | 0.99 |
| president | 247 | 1.00 | 0.99 | 0.99 |
| submariner | 189 | 0.99 | 1.00 | 0.99 |
| datejust | 597 | 1.00 | 1.00 | 1.00 |
| cellini | 145 | 1.00 | 1.00 | 1.00 |
| daytona | 92 | 1.00 | 1.00 | 1.00 |
| explorer | 103 | 1.00 | 1.00 | 1.00 |
| gmt_master | 111 | 1.00 | 1.00 | 1.00 |
| milgauss | 19 | 1.00 | 1.00 | 1.00 |
| oysterquartz | 20 | 1.00 | 1.00 | 1.00 |
| yacht_master | 123 | 1.00 | 1.00 | 1.00 |

## Most confused pairs

| True | Predicted | Count |
|---|---|---|
| airking | oyster_perpetual | 3 |
| turn_o_graph | datejust | 2 |
| datejust | airking | 1 |
| datejust | president | 1 |
| oyster_perpetual | airking | 1 |
| president | oyster_perpetual | 1 |
| president | submariner | 1 |
| sea_dweller | submariner | 1 |

## If the app only answered when confident

| Confidence threshold | Share answered | Accuracy on those |
|---|---|---|
| >= 0.5 | 99.8% | 99.6% |
| >= 0.7 | 99.2% | 99.8% |
| >= 0.9 | 98.5% | 100.0% |
| >= 0.95 | 96.9% | 100.0% |
