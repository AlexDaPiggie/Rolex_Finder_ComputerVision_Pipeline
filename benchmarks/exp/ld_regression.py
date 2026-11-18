"""Did adding the Land-Dweller family hurt the other 14? Same creator-grouped CV, with and without the new class.
Run: python -m benchmarks.exp.ld_regression"""
import json
from pathlib import Path
import numpy as np
from src.training.clip_head import creator_groups, grouped_cv

names15 = [n for n, _ in sorted(json.loads(Path("data/processed/class_mapping.json").read_text()).items(), key=lambda kv: kv[1])]
tr = np.load("features_out/train.npz"); real = np.load("features_out/real.npz")
ex = set(json.loads(Path("benchmarks/real_exclude.json").read_text()))
keep = np.array([f.replace("\\", "/") not in ex for f in real["files"]])
emb, lab, files = real["emb"][keep].astype("float32"), real["labels"][keep], real["files"][keep]
groups = creator_groups(files)
xtr, ytr = tr["feats"].astype("float32"), tr["labels"]
old = lab != 14
for name, sel, n in (("14 families, no Land-Dweller", old, names15[:14]), ("15 families, with Land-Dweller", np.ones(len(lab), bool), names15)):
    # same folds for both: folds come from the groups of the photos used
    r = grouped_cv(xtr, ytr, emb[sel], lab[sel], groups[sel], n, 10)
    other = lab[sel] != 14
    print(name, "overall", r["acc"], r["ci95"])
    print("  per family:", {k: v for k, v in r["per_family"].items()})
