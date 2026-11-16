import os
import time
from pathlib import Path
import modal

_PROCESS_START = time.time()

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
    .pip_install_from_requirements(str(APP_ROOT / "requirements-api.txt"))
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

# Keep this many containers warm. 0 = scale to zero (free when idle, ~40s cold start).
# Before showing the site to someone, redeploy with ROLEX_MIN_CONTAINERS=1 (an L4 costs roughly
# $0.80/hour while warm), then redeploy with 0 afterwards.
MIN_CONTAINERS = int(os.getenv("ROLEX_MIN_CONTAINERS", "0"))

@app.cls (
    image = image,
    gpu = ["L4", "T4", "A10G"],
    min_containers = MIN_CONTAINERS,
    max_containers = 3,  # one request per container; extra visitors get their own container instead of queueing
    scaledown_window = 1200,
    timeout = 180,
    startup_timeout = 180,
    secrets = [hf_secret],
)

@modal.concurrent(max_inputs = 1)
class RolexWatchAPI:
    @modal.enter()
    def load_models (self):
        from src.inference.timing import STARTUP, timed
        from src.inference.warmup import warm_models

        # Seconds between Python starting in this container and this method running
        # (image pull and container allocation happen before that and are not visible here).
        STARTUP["seconds_since_process_start"] = round(time.time() - _PROCESS_START, 2)
        with timed("warm_models_total", STARTUP):
            warm_models()

    @modal.asgi_app()
    def web(self): 
        from src.api.main import app as fastapi_app
        return fastapi_app