"""
Build the "not a Rolex I know" gate: CLIP zero-shot "Rolex vs other brand" score on the cropped watch.

    python -m src.training.open_set_gate

Saves models/open_set.pt (text vectors, threshold) and benchmarks/open_set_gate.json.
Threshold = the score that wrongly rejects 5% of real Rolex photos (reject below it).
Uses features_out/real.npz (real Rolex photos, crop view) and features_out/other.npz (other brands).
"""
import json
from pathlib import Path

import numpy as np
import torch

BRANDS = ["Omega", "Seiko", "Casio", "TAG Heuer", "Tissot", "Longines", "Patek Philippe", "Audemars Piguet", "Cartier",
          "Breitling", "IWC", "Panerai", "Hublot", "Citizen", "Tudor", "Garmin", "Timex", "Swatch", "Fossil", "Vacheron Constantin"]
OTHERS = ([f"a photo of a {b} watch" for b in BRANDS]
          + ["a photo of a watch from another brand", "a photo of a smartwatch", "a photo of a digital watch",
             "a photo of a cheap fashion watch", "a photo of a luxury watch that is not a Rolex"])
ROLEX = "a photo of a Rolex watch"
SCALE = 100.0
VIEW = 1  # the crop, the same image the API embeds
FALSE_REJECT = 0.05


def text_vectors():
    from transformers import CLIPModel, CLIPProcessor
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch16").eval()
    proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")
    with torch.no_grad():
        f = model.get_text_features(**proc(text=[ROLEX] + OTHERS, return_tensors="pt", padding=True))
    f = f if torch.is_tensor(f) else f.pooler_output
    return f / f.norm(dim=-1, keepdim=True)


def rolex_score(embedding: torch.Tensor, text: torch.Tensor) -> torch.Tensor:
    """Probability that the zero-shot prompts pick 'Rolex' over every other-brand prompt. embedding: (n, 512), L2-normalised."""
    return torch.softmax(SCALE * embedding @ text.T, dim=1)[:, 0]


def main():
    feat = Path("features_out")
    real, other = np.load(feat / "real.npz"), np.load(feat / "other.npz")
    excluded = set(json.loads(Path("benchmarks/real_exclude.json").read_text()))
    keep = np.array([f.replace("\\", "/") not in excluded for f in real["files"]])
    text = text_vectors()
    pos = rolex_score(torch.tensor(real["emb"][keep][:, VIEW], dtype=torch.float32), text).numpy()
    neg = rolex_score(torch.tensor(other["emb"][:, VIEW], dtype=torch.float32), text).numpy()
    thr = float(np.quantile(pos, FALSE_REJECT))
    brand = np.array([f.replace("\\", "/").split("/")[-2] for f in other["files"]])
    per = {b: round(float((neg[brand == b] < thr).mean()), 2) for b in sorted(set(brand))}
    ranks = np.concatenate([pos, neg]).argsort().argsort() + 1
    auroc = float((ranks[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))
    report = {"n_rolex": int(len(pos)), "n_other": int(len(neg)), "threshold": round(thr, 4), "auroc": round(auroc, 3),
              "rolex_rejected": round(float((pos < thr).mean()), 3), "other_rejected": round(float((neg < thr).mean()), 3),
              "other_rejected_by_brand": per}
    print(json.dumps(report, indent=1))
    Path("benchmarks/open_set_gate.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    torch.save({"text": text.cpu(), "threshold": thr, "scale": SCALE}, "models/open_set.pt")


if __name__ == "__main__":
    main()
