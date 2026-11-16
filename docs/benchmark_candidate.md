# Classifier benchmark

Generated 2026-11-16 on split `test` of `/tmp/crops` (2006 images).

**What this measures:** the EfficientNet-B0 family classifier only, on crops from the same collection as the training data. It does not measure the full pipeline (detection, alignment, variant matching) or real-world phone photos, so treat it as an optimistic upper bound.

Device: cuda.

| Metric | Value |
|---|---|
| Top-1 accuracy | 99.5% |
| Top-3 accuracy | 99.9% |
| Macro F1 | 0.992 |
| Balanced accuracy (mean recall) | 99.7% |
| Calibration error (ECE, lower is better) | 0.003 |
| Mean confidence | 99.6% |
| Latency per image (batched) | 3.7 ms |

## Train/test leakage check

6 of 2006 test images (0.3%) have a near-duplicate in the training set (256-bit dHash distance <= 6; a conservative count, similar photos of the same watch can be further apart). Accuracy on those images is inflated.

## Per class

| Class | Images | Precision | Recall | F1 |
|---|---|---|---|---|
| oysterquartz | 20 | 0.87 | 1.00 | 0.93 |
| president | 247 | 0.99 | 0.98 | 0.98 |
| turn_o_graph | 48 | 0.98 | 1.00 | 0.99 |
| oyster_perpetual | 128 | 0.99 | 0.99 | 0.99 |
| datejust | 597 | 1.00 | 0.99 | 0.99 |
| yacht_master | 123 | 0.99 | 1.00 | 1.00 |
| airking | 129 | 1.00 | 0.99 | 1.00 |
| cellini | 145 | 1.00 | 1.00 | 1.00 |
| daytona | 92 | 1.00 | 1.00 | 1.00 |
| explorer | 103 | 1.00 | 1.00 | 1.00 |
| gmt_master | 111 | 1.00 | 1.00 | 1.00 |
| milgauss | 19 | 1.00 | 1.00 | 1.00 |
| sea_dweller | 55 | 1.00 | 1.00 | 1.00 |
| submariner | 189 | 1.00 | 1.00 | 1.00 |

## Most confused pairs

| True | Predicted | Count |
|---|---|---|
| datejust | president | 3 |
| president | oysterquartz | 3 |
| airking | oyster_perpetual | 1 |
| datejust | turn_o_graph | 1 |
| oyster_perpetual | datejust | 1 |
| president | datejust | 1 |
| president | yacht_master | 1 |

## If the app only answered when confident

| Confidence threshold | Share answered | Accuracy on those |
|---|---|---|
| >= 0.5 | 100.0% | 99.5% |
| >= 0.7 | 99.7% | 99.6% |
| >= 0.9 | 99.1% | 99.8% |
| >= 0.95 | 98.4% | 99.9% |
