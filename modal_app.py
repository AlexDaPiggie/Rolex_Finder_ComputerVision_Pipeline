from pathlib import Path
import modal

APP_ROOT = Path(__file__).parent
app = modal.App ("rolex-watch-recognizer")
hf_secret = modal.Secret.from_name (
    "rolex-huggingface", 
    required_keys=["HF_TOKEN"],
)

def download_huggingface_models ():
    import os
    from transformers import(
        AutoModelForZeroShotObjectDetection,
        AutoProcessor,
        pipeline,
    )

    token = os.environ["HF_TOKEN"]
    detector_id = "IDEA-Research/grounding-dino-base"
    clip_id = "openai/clip-vit-base-patch16"
    AutoProcessor.from_pretrained(detector_id, token = token)
    AutoModelForZeroShotObjectDetection.from_pretrained(
        detector_id,
        token = token,
    )

    pipeline (
        task = "zero-shot-image-classification",
        model = clip_id,
        token = token,
        device = -1,
    )

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libgl1", "libglib2.0-0")
    .pip_install_from_requirements(str(APP_ROOT / "requirements.txt"))
    .run_function (
        download_huggingface_models,
        secrets = [hf_secret],
    )
    .add_local_dir (
        APP_ROOT / "src",
        remote_path = "/app/src",
        copy = True,
    )
    .add_local_dir (
        APP_ROOT / "models",
        remote_path= "/app/models",
        copy = True,
    )
    .add_local_file (
        APP_ROOT / "data/processed/class_mapping.json",
        remote_path = "/app/data/processed/class_mapping.json",
        copy = True,
    )
    .env ({
        "PYTHONPATH": "/app",
        "MODEL_DEVICE": "cuda",
        "HF_HOME": "/root/.cache/huggingface",
    })
    .workdir ("/app")
)

@app.cls (
    image = image,
    gpu = "L4",
    min_containers = 0,
    max_containers = 1,
    scaledown_window = 1200,
    timeout = 180,
    startup_timeout = 180,
    secrets = [hf_secret],
)

@modal.concurrent(max_inputs = 1)
class RolexWatchAPI:
    @modal.enter()
    def load_models (self):
        from src.inference.warmup import warm_models
        warm_models()

    @modal.asgi_app()
    def web(self): 
        from src.api.main import app as fastapi_app
        return fastapi_app