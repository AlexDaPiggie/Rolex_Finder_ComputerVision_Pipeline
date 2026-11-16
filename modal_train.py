"""
Run the training-data pipeline on a Modal GPU: crop -> train -> benchmark (candidate and current model).

One-time setup:
    pip install modal && modal setup
    modal run modal_train.py::upload           # copies data/grouped to a Modal volume (slow for 25k files)
    # or, faster and more reliable (set MSYS_NO_PATHCONV=1 in Git Bash so /grouped is not rewritten):
    modal volume put rolex-training-data data/grouped/train /grouped/train   # same for val and test, plus class_mapping.json

Run everything (needs the rolex-huggingface secret, same as modal_app.py):
    modal run modal_train.py::main                   # crop all images, train 10 epochs, benchmark, download results
    modal run modal_train.py::main --epochs 15
    modal run modal_train.py::main --skip-crop       # reuse crops already on the volume
    modal volume get rolex-training-data /results .   # fetch results if the client disconnected

Results are written next to the project files:
    models/candidate.pt                        new checkpoint (does NOT replace the live model)
    docs/benchmark_candidate.md                candidate on the grouped, cropped test split
    docs/benchmark_baseline_grouped.md         current live model on the same test split (fair comparison)
    benchmarks/*.json                          same numbers as JSON, plus crop_report.json

Rough cost on an L4: cropping about 25k images is the biggest part (roughly 1-2 GPU hours in total, spread
over parallel containers), training about 15-30 minutes. Expect a few dollars; check your Modal usage page.
Nothing here touches the deployed website.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import modal

APP_ROOT = Path(__file__).parent
app = modal.App("rolex-training")
volume = modal.Volume.from_name("rolex-training-data", create_if_missing=True)
hf_secret = modal.Secret.from_name("rolex-huggingface", required_keys=["HF_TOKEN"])

DATA = "/data"
SOURCE_DIR = f"{DATA}/grouped"
CROPS_DIR = f"{DATA}/grouped_crops"
SPLITS = ("train", "val", "test")


def download_detector():
    import os

    from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor

    token = os.environ["HF_TOKEN"]
    detector_id = "IDEA-Research/grounding-dino-base"
    AutoProcessor.from_pretrained(detector_id, token=token)
    AutoModelForZeroShotObjectDetection.from_pretrained(detector_id, token=token)


image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libgl1", "libglib2.0-0")
    .pip_install_from_requirements(str(APP_ROOT / "requirements-api.txt"))
    .run_function(download_detector, secrets=[hf_secret])
    .add_local_dir(APP_ROOT / "src", remote_path="/app/src", copy=True)
    .add_local_dir(APP_ROOT / "models", remote_path="/app/models", copy=True)
    .add_local_file(
        APP_ROOT / "data/processed/class_mapping.json",
        remote_path="/app/data/processed/class_mapping.json",
        copy=True,
    )
    .env({"PYTHONPATH": "/app", "MODEL_DEVICE": "cuda", "HF_HOME": "/root/.cache/huggingface"})
    .workdir("/app")
)


@app.function(image=image, gpu="L4", timeout=4 * 3600, volumes={DATA: volume}, secrets=[hf_secret], max_containers=6)
def crop_chunk(label: str, split: str) -> dict:
    """Crop every image of one class and split with the same pipeline the website uses. Resumable."""
    from src.detection.watch_cropper import crop_watch_stages
    from src.training.prepare_crops import run

    # on_miss=skip: images with no watch (boxes, papers, straps only) are dropped, as the site would reject them
    counts = run(Path(SOURCE_DIR), Path(CROPS_DIR), crop_watch_stages, splits=(split,), labels={label}, on_miss="skip")
    volume.commit()
    return {"label": label, "split": split, "counts": {k: dict(v) for k, v in counts.items()}}


def _run(command: list[str]):
    print("$", " ".join(command), flush=True)
    subprocess.run(command, check=True, cwd="/app")


@app.function(image=image, gpu="L4", timeout=4 * 3600, volumes={DATA: volume})
def train_and_benchmark(epochs: int, crop_summary: list) -> dict:
    """Train on the cropped data, then benchmark the new and the current model on the same test split."""
    volume.reload()
    local = Path("/tmp/crops")
    if local.exists():
        shutil.rmtree(local)
    shutil.copytree(CROPS_DIR, local)  # local disk is much faster than the volume for training
    shutil.copy2(f"{SOURCE_DIR}/class_mapping.json", local / "class_mapping.json")

    out = Path("/tmp/out")
    out.mkdir(exist_ok=True)
    candidate = out / "candidate.pt"

    _run([
        sys.executable, "-m", "src.training.train",
        "--data-root", str(local), "--epochs", str(epochs), "--batch-size", "32",
        "--device", "cuda", "--balance", "loss", "--num-workers", "4", "--output", str(candidate),
    ])
    _run([
        sys.executable, "-m", "src.training.benchmark",
        "--data-root", str(local), "--checkpoint", str(candidate), "--device", "cuda", "--check-leakage",
        "--json-out", str(out / "candidate_metrics.json"), "--md-out", str(out / "benchmark_candidate.md"),
    ])
    _run([
        sys.executable, "-m", "src.training.benchmark",
        "--data-root", str(local), "--checkpoint", "models/rolex_classifier_model.pt", "--device", "cuda",
        "--check-leakage",
        "--json-out", str(out / "baseline_grouped_metrics.json"), "--md-out", str(out / "benchmark_baseline_grouped.md"),
    ])

    files = {p.name: p.read_bytes() for p in out.iterdir()}
    files["crop_report.json"] = json.dumps(crop_summary, indent=2).encode()
    # Also keep results on the volume, so they survive if the local client disconnects
    results = Path(f"{DATA}/results")
    results.mkdir(exist_ok=True)
    for name, content in files.items():
        (results / name).write_bytes(content)
    volume.commit()
    return files


@app.local_entrypoint()
def upload(source: str = "data/grouped"):
    """Copy the grouped dataset to the Modal volume (run once, or again after fixing labels)."""
    with volume.batch_upload(force=True) as batch:
        batch.put_directory(source, "/grouped")
    print(f"uploaded {source} -> volume rolex-training-data:/grouped")


@app.local_entrypoint()
def main(epochs: int = 10, skip_crop: bool = False):
    mapping = json.loads((APP_ROOT / "data/processed/class_mapping.json").read_text(encoding="utf-8"))
    summary: list = []
    if not skip_crop:
        jobs = [(label, split) for label in mapping for split in SPLITS]
        for result in crop_chunk.starmap(jobs):
            summary.append(result)
            print(result, flush=True)

    files = train_and_benchmark.remote(epochs, summary)

    destinations = {
        "candidate.pt": APP_ROOT / "models/candidate.pt",
        "candidate_metrics.json": APP_ROOT / "benchmarks/candidate_metrics.json",
        "baseline_grouped_metrics.json": APP_ROOT / "benchmarks/baseline_grouped_metrics.json",
        "crop_report.json": APP_ROOT / "benchmarks/crop_report.json",
        "benchmark_candidate.md": APP_ROOT / "docs/benchmark_candidate.md",
        "benchmark_baseline_grouped.md": APP_ROOT / "docs/benchmark_baseline_grouped.md",
    }
    for name, path in destinations.items():
        if name in files:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(files[name])
            print("wrote", path)
