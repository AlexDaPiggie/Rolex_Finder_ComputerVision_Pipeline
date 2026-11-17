"""Open-set check: prompts that do NOT name the brand being tested. Run: python -m benchmarks.exp.open_set_unseen"""
import json
from pathlib import Path
import numpy as np, torch
from transformers import CLIPModel, CLIPProcessor
from benchmarks.exp.open_set import FEAT, auroc

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch16").eval()
proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")
def tf(texts):
    with torch.no_grad():
        f = model.get_text_features(**proc(text=texts, return_tensors="pt", padding=True))
    f = f if torch.is_tensor(f) else f.pooler_output
    return (f / f.norm(dim=-1, keepdim=True)).numpy()

real = np.load(FEAT / "real.npz"); other = np.load(FEAT / "other.npz")
ex = set(json.loads(Path("benchmarks/real_exclude.json").read_text()))
keep = np.array([f.replace("\\", "/") not in ex for f in real["files"]])
pe = real["emb"][keep].astype("float32"); oe = other["emb"].astype("float32")
brand = np.array([f.replace("\\", "/").split("/")[-2] for f in other["files"]])
GENERIC = ["a photo of a watch from another brand", "a photo of a smartwatch", "a photo of a digital watch",
           "a photo of a cheap fashion watch", "a photo of a luxury watch that is not a Rolex"]
NAMED = {"omega": "Omega", "seiko": "Seiko", "casio": "Casio", "tag_heuer": "TAG Heuer", "tissot": "Tissot", "longines": "Longines",
         "patek_philippe": "Patek Philippe", "audemars_piguet": "Audemars Piguet", "cartier": "Cartier", "breitling": "Breitling",
         "iwc": "IWC", "panerai": "Panerai", "hublot": "Hublot", "citizen": "Citizen", "tudor": "Tudor", "garmin": "Garmin",
         "timex": "Timex", "swatch": "Swatch", "fashion": "Fossil", "other_luxury": "Vacheron Constantin"}

def score(e, others):
    t = tf(["a photo of a Rolex watch"] + others)
    return np.mean([torch.softmax(torch.tensor(100 * e[:, v] @ t.T), 1).numpy()[:, 0] for v in (0, 1)], axis=0)

# 1) generic prompts only (no brand named at all)
p, n = score(pe, GENERIC), score(oe, GENERIC)
thr = np.quantile(p, 0.05)
print(f"generic prompts only: AUROC {auroc(p, n):.3f}, caught at 5% false reject {(n < thr).mean():.2f}")
# 2) leave-one-brand-out: brand prompts for every brand EXCEPT the one tested
rows = []
for b, name in NAMED.items():
    sel = brand == b
    if sel.sum() == 0: continue
    others = [f"a photo of a {v} watch" for k, v in NAMED.items() if k != b] + GENERIC
    p, n = score(pe, others), score(oe[sel], others)
    thr = np.quantile(p, 0.05)
    rows.append((b, int(sel.sum()), float((n < thr).mean())))
tot = sum(r[1] for r in rows)
print("unseen brand, caught at 5% false reject:")
for b, k, c in rows: print(f"  {b:16s} n={k:3d}  {c:.2f}")
print(f"  weighted mean {sum(k * c for _, k, c in rows) / tot:.2f}")
