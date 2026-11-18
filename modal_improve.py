"""
Modal jobs for improving the family classifier on real photos.

1. extract_split: CLIP embeddings of the retailer training images (studio view and dial-crop view),
   with real-look augmentation (backgrounds, close-ups, glare, blur, JPEG). Saved to the volume.
2. eval_real: runs real photos through detection (crop, align, dial) and saves, for every preprocessing
   variant, CLIP embeddings and the probabilities of the EfficientNet checkpoints.

Heads and comparisons are trained locally from the saved arrays (src/training/clip_head.py).

Setup (Git Bash: set MSYS_NO_PATHCONV=1 so /real is not rewritten):
    modal volume put -f rolex-training-data data/realworld_all /real
Run:
    modal run modal_improve.py::features        # about 10-15 min on an L4
    modal run modal_improve.py::real            # a few minutes
    modal volume get rolex-training-data /features features_out   # then train locally
"""
import io
import json
from pathlib import Path

import modal

APP_ROOT = Path(__file__).parent
app = modal.App("rolex-improve")
volume = modal.Volume.from_name("rolex-training-data", create_if_missing=True)
hf_secret = modal.Secret.from_name("rolex-huggingface", required_keys=["HF_TOKEN"])
DATA = "/data"
SPLITS = ("train", "val", "test")
VIEWS = ("full", "crop", "aligned", "dial")


def download_models():
    import os

    from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor, CLIPModel

    token = os.environ["HF_TOKEN"]
    AutoProcessor.from_pretrained("IDEA-Research/grounding-dino-base", token=token)
    AutoModelForZeroShotObjectDetection.from_pretrained("IDEA-Research/grounding-dino-base", token=token)
    CLIPModel.from_pretrained("openai/clip-vit-base-patch16", token=token)


image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libgl1", "libglib2.0-0")
    .pip_install_from_requirements(str(APP_ROOT / "requirements-api.txt"))
    .run_function(download_models, secrets=[hf_secret])
    .add_local_dir(APP_ROOT / "src", remote_path="/app/src", copy=True)
    .add_local_dir(APP_ROOT / "models", remote_path="/app/models", copy=True)
    .add_local_file(
        APP_ROOT / "data/processed/class_mapping.json", remote_path="/app/data/processed/class_mapping.json", copy=True
    )
    .env({"PYTHONPATH": "/app", "MODEL_DEVICE": "cuda", "HF_HOME": "/root/.cache/huggingface"})
    .workdir("/app")
)


def _class_names() -> list[str]:
    mapping = json.loads(Path("/app/data/processed/class_mapping.json").read_text(encoding="utf-8"))
    return [name for name, _ in sorted(mapping.items(), key=lambda kv: kv[1])]


def _load_clip():
    import torch
    from transformers import CLIPModel

    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch16", torch_dtype=torch.float16).to("cuda").eval()
    return model


@app.function(image=image, gpu="L4", cpu=8, memory=16384, timeout=3 * 3600, volumes={DATA: volume}, secrets=[hf_secret])
def extract_split(split: str, n_aug: int = 2) -> dict:
    """CLIP embeddings for one split. Train gets n_aug augmented copies per image and view."""
    import numpy as np
    import torch
    from PIL import Image
    from torch.utils.data import DataLoader, Dataset

    from src.inference.clip_embed import embed, preprocess
    from src.training.real_aug import real_look_pil

    names = _class_names()
    index = {name: i for i, name in enumerate(names)}
    roots = {"orig": Path(f"{DATA}/grouped") / split, "dial": Path(f"{DATA}/grouped_crops") / split}
    items = []  # (path, label, view, augmented)
    for view, root in roots.items():
        for path in sorted(root.glob("*/*.jpg")):
            label = index.get(path.parent.name)
            if label is None:
                continue
            items.append((path, label, view, False))
            copies = n_aug if split == "train" else 1  # val/test: one augmented copy to measure robustness
            items.extend((path, label, view, True) for _ in range(copies))
    print(split, len(items), "samples", flush=True)

    aug = real_look_pil()

    class DS(Dataset):
        def __len__(self):
            return len(items)

        def __getitem__(self, i):
            path, label, view, augmented = items[i]
            img = Image.open(path).convert("RGB")
            if augmented:
                img = aug(img)
            return preprocess(img), label, 0 if view == "orig" else 1, int(augmented)

    loader = DataLoader(DS(), batch_size=128, num_workers=8, shuffle=False)
    clip = _load_clip()
    feats, labels, views, augs = [], [], [], []
    with torch.no_grad():
        for n, (x, y, v, a) in enumerate(loader):
            f = clip.get_image_features(pixel_values=x.to("cuda").half())
            if not isinstance(f, torch.Tensor):
                f = f.pooler_output
            f = f / f.norm(dim=-1, keepdim=True)
            feats.append(f.float().cpu().numpy().astype("float16"))
            labels.append(y.numpy()); views.append(v.numpy()); augs.append(a.numpy())
            if n % 50 == 0:
                print(f"{split} batch {n}/{len(loader)}", flush=True)
    out = Path(f"{DATA}/features")
    out.mkdir(exist_ok=True)
    np.savez(out / f"{split}.npz", feats=np.concatenate(feats), labels=np.concatenate(labels),
             views=np.concatenate(views), augs=np.concatenate(augs))
    volume.commit()
    return {"split": split, "samples": len(items)}


@app.function(image=image, gpu="L4", cpu=8, memory=16384, timeout=2 * 3600, volumes={DATA: volume}, secrets=[hf_secret])
def extract_variants(n_aug: int = 3) -> dict:
    """CLIP embeddings of photos whose variant is known from the reference number in the retailer file name."""
    import numpy as np
    import torch
    from PIL import Image
    from torch.utils.data import DataLoader, Dataset

    from src.inference.clip_embed import preprocess
    from src.training.real_aug import real_look_pil

    labels = json.loads(Path(f"{DATA}/variant_labels.json").read_text())
    variants = sorted(set(labels.values()))
    items = []  # (path, split, variant index, view, augmented)
    for key, variant in labels.items():
        split, family, stem = key.split("/")
        for view, root in (("dial", "grouped_crops"), ("orig", "grouped")):
            path = Path(f"{DATA}/{root}/{split}/{family}/{stem}.jpg")
            if not path.exists():
                continue
            items.append((path, split, variants.index(variant), view, False))
            if split == "train":
                items.extend((path, split, variants.index(variant), view, True) for _ in range(n_aug))
    aug = real_look_pil()
    print(len(items), "variant samples", flush=True)

    class DS(Dataset):
        def __len__(self):
            return len(items)

        def __getitem__(self, i):
            path, split, label, view, augmented = items[i]
            img = Image.open(path).convert("RGB")
            return preprocess(aug(img) if augmented else img), label

    clip = _load_clip()
    feats = []
    with torch.no_grad():
        for x, _ in DataLoader(DS(), batch_size=128, num_workers=8):
            f = clip.get_image_features(pixel_values=x.to("cuda").half())
            if not isinstance(f, torch.Tensor):
                f = f.pooler_output
            feats.append((f / f.norm(dim=-1, keepdim=True)).float().cpu().numpy().astype("float16"))
    out = Path(f"{DATA}/features")
    out.mkdir(exist_ok=True)
    np.savez(out / "variants.npz", feats=np.concatenate(feats), labels=np.array([i[2] for i in items]),
             splits=np.array([i[1] for i in items]), views=np.array([i[3] for i in items]),
             augs=np.array([i[4] for i in items]), variants=np.array(variants))
    volume.commit()
    return {"samples": len(items), "variants": len(variants)}


@app.local_entrypoint()
def variants():
    print(extract_variants.remote())


@app.function(image=image, gpu="L4", cpu=4, memory=16384, timeout=2 * 3600, volumes={DATA: volume}, secrets=[hf_secret])
def eval_real(folder: str = "real", out_name: str = "real", known_only: bool = True) -> dict:
    """Detect, crop, align and dial-crop every real photo, then save embeddings and EfficientNet probabilities."""
    import numpy as np
    import torch
    from PIL import Image, ImageOps

    from src.detection.watch_cropper import crop_watch_stages
    from src.inference.clip_embed import embed
    from src.training.dataset import build_transforms
    from src.training.models import create_model

    names = _class_names()
    index = {n: i for i, n in enumerate(names)}
    clip = _load_clip()
    tf = build_transforms(train=False)

    nets = {}
    volume.reload()
    checkpoints = [("base", "/app/models/rolex_classifier_model.pt"), ("cand", "/app/models/candidate.pt")]
    checkpoints += [(p.stem, str(p)) for p in sorted(Path(f"{DATA}/models").glob("*.pt"))]  # models trained by train_real
    for tag, path in checkpoints:
        if Path(path).exists():
            ckpt = torch.load(path, map_location="cuda", weights_only=True)
            # EfficientNets were trained on the first 14 families; families added later (land_dweller) are CLIP-head only
            net = create_model(num_classes=len(ckpt.get("class_names", names[:14])), pretrained=False).to("cuda")
            net.load_state_dict(ckpt["model_state_dict"])
            nets[tag] = net.eval()

    files = sorted(p for p in Path(f"{DATA}/{folder}").glob("*/*.jpg") if (p.parent.name in index or not known_only))
    rec = {"files": [], "labels": [], "detected": [], "emb": [], **{f"eff_{t}": [] for t in nets}}
    for n, path in enumerate(files):
        img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        final, info, stages = crop_watch_stages(img)
        detected = info.get("reason") != "no_watch_detected"
        views = [img, stages.get("crop", img), stages.get("aligned", img), stages.get("dial", img)] if detected else [img] * 4
        rec["files"].append(str(path.relative_to(f"{DATA}/{folder}")))
        rec["labels"].append(index.get(path.parent.name, -1))
        rec["detected"].append(detected)
        rec["emb"].append(embed(views, clip, "cuda"))
        batch = torch.stack([tf(v) for v in views]).to("cuda")
        for tag, net in nets.items():
            with torch.no_grad():
                rec[f"eff_{tag}"].append(torch.softmax(net(batch), dim=1).cpu().numpy())
        if n % 20 == 0:
            print(f"{n}/{len(files)}", flush=True)
    out = Path(f"{DATA}/features")
    out.mkdir(exist_ok=True)
    np.savez(
        out / f"{out_name}.npz", files=np.array(rec["files"]), labels=np.array(rec["labels"]), detected=np.array(rec["detected"]),
        emb=np.stack(rec["emb"]).astype("float16"),
        **{f"eff_{t}": np.stack(rec[f"eff_{t}"]) for t in nets},
    )
    volume.commit()
    return {"images": len(files), "nets": list(nets)}


@app.function(image=image, gpu="L4", cpu=8, memory=24576, timeout=4 * 3600, volumes={DATA: volume})
def train_real(epochs: int = 12, tag: str = "real_aug") -> dict:
    """Train EfficientNet-B0 on studio photos AND dial crops, made to look like real photos while training."""
    import shutil
    import subprocess
    import sys

    volume.reload()
    crops, orig = Path("/tmp/crops"), Path("/tmp/orig")
    for src, dst in ((f"{DATA}/grouped_crops", crops), (f"{DATA}/grouped", orig)):
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    shutil.copy2(f"{DATA}/grouped/class_mapping.json", crops / "class_mapping.json")
    shutil.copy2(f"{DATA}/grouped/class_mapping.json", orig / "class_mapping.json")
    out = Path(f"{DATA}/models")
    out.mkdir(exist_ok=True)
    command = [
        sys.executable, "-m", "src.training.train", "--data-root", str(crops), str(orig), "--real-aug",
        "--balance", "loss", "--device", "cuda", "--num-workers", "8", "--epochs", str(epochs),
        "--batch-size", "48", "--output", str(out / f"{tag}.pt"),
    ]
    print("$", " ".join(command), flush=True)
    subprocess.run(command, check=True, cwd="/app")
    volume.commit()
    return {"tag": tag, "epochs": epochs}


@app.function(image=image, gpu="L4", cpu=4, memory=16384, timeout=3600, volumes={DATA: volume})
def bench_retailer(tag: str) -> dict:
    """Benchmark a checkpoint on the retailer test split (dial crops), with the same code as docs/benchmark.md."""
    import shutil
    import subprocess
    import sys

    volume.reload()
    root = Path("/tmp/crops_test")
    if root.exists():
        shutil.rmtree(root)
    (root / "test").parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(f"{DATA}/grouped_crops/test", root / "test")
    shutil.copy2(f"{DATA}/grouped/class_mapping.json", root / "class_mapping.json")
    ckpt = f"{DATA}/models/{tag}.pt" if tag not in ("base", "cand") else (
        "/app/models/rolex_classifier_model.pt" if tag == "base" else "/app/models/candidate.pt")
    subprocess.run([sys.executable, "-m", "src.training.benchmark", "--data-root", str(root), "--checkpoint", ckpt,
                    "--device", "cuda", "--json-out", "/tmp/m.json", "--md-out", "/tmp/m.md"], check=True, cwd="/app")
    return json.loads(Path("/tmp/m.json").read_text())["metrics"]


@app.local_entrypoint()
def bench(tag: str = "real_aug"):
    m = bench_retailer.remote(tag)
    print({k: m[k] for k in ("samples", "top1_accuracy", "top3_accuracy", "macro_f1", "ece")})


@app.local_entrypoint()
def train(epochs: int = 12, tag: str = "real_aug"):
    print(train_real.remote(epochs, tag))


@app.local_entrypoint()
def features(n_aug: int = 2):
    results = list(extract_split.starmap([(s, n_aug) for s in SPLITS]))
    print(results)


@app.local_entrypoint()
def real():
    print(eval_real.remote())


@app.local_entrypoint()
def other():
    """Embeddings of non-Rolex watch photos (label -1), for unknown-watch handling.
    Setup: modal volume put -f rolex-training-data data/otherwatches/test /other"""
    print(eval_real.remote("other", "other", False))
