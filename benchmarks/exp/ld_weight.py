"""Land-Dweller photo weight vs accuracy of the other families. Run: python -m benchmarks.exp.ld_weight"""
import json
from pathlib import Path
import numpy as np
from src.training.clip_head import creator_groups, predict, train_head

names = [n for n, _ in sorted(json.loads(Path("data/processed/class_mapping.json").read_text()).items(), key=lambda kv: kv[1])]
tr = np.load("features_out/train.npz"); real = np.load("features_out/real.npz")
ex = set(json.loads(Path("benchmarks/real_exclude.json").read_text()))
keep = np.array([f.replace("\\", "/") not in ex for f in real["files"]])
emb, lab, files = real["emb"][keep].astype("float32"), real["labels"][keep], real["files"][keep]
groups = creator_groups(files)
xtr, ytr = tr["feats"].astype("float32"), tr["labels"]
u = sorted(set(groups)); np.random.default_rng(0).shuffle(u)
fold = np.array([{g: i % 5 for i, g in enumerate(u)}[g] for g in groups])
def rows(e, l, w):
    xs = np.concatenate([e[:, v] for v in (0, 1, 3)]); ys = np.concatenate([l] * 3)
    return np.concatenate([xs] * w), np.concatenate([ys] * w)
for w_ld in (1, 2, 4, 10):
    correct = np.zeros(len(lab), bool)
    for k in range(5):
        trn, tst = fold != k, fold == k
        xs, ys = [xtr], [ytr]
        for is_ld, w in ((False, 10), (True, w_ld)):
            m = trn & ((lab == 14) == is_ld)
            if m.any():
                x, y = rows(emb[m], lab[m], w); xs.append(x); ys.append(y)
        head, scale = train_head(np.concatenate(xs), np.concatenate(ys), 15, 0.1, epochs=60)
        correct[tst] = predict(head, scale, emb[tst][:, 3]).argmax(1) == lab[tst]
    ld = lab == 14
    print(f"LD weight {w_ld:2d}: Land-Dweller {correct[ld].mean():.3f} | other 14 families {correct[~ld].mean():.3f}", flush=True)
