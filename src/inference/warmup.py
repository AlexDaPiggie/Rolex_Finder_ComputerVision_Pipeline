from PIL import Image

from src.api.main import get_model as get_classifier
from src.detection.watch_cropper import detect_watch, get_detector as get_watch_detector
from src.identify.clip_matcher import get_detector as get_clip_detector
from src.inference.timing import STARTUP, timed


def warm_models():
    """
    Load all three models, then push one dummy image through each.
    The dummy pass pays the one-off GPU costs (CUDA kernels, cuDNN autotune) at container
    start instead of on the first real request. Each phase is timed into STARTUP (see /health).
    """
    with timed("load_classifier", STARTUP):
        get_classifier()
    with timed("load_watch_detector", STARTUP):
        get_watch_detector()
    with timed("load_clip", STARTUP):
        clip = get_clip_detector()

    blank = Image.new("RGB", (640, 480), color="white")
    with timed("dummy_pass_detector", STARTUP):
        detect_watch(blank)
    with timed("dummy_pass_clip", STARTUP):
        clip(blank, candidate_labels=["a watch", "a photo"])
    with timed("dummy_pass_classifier", STARTUP):
        from src.api import main

        main.predict_family(blank)
