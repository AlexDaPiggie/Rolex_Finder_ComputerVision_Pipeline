from src.api.main import get_model as get_classifier
from src.detection.watch_cropper import get_detector as get_watch_detector
from src.identify.clip_matcher import get_detector as get_clip_detector

def warm_models(): 
    get_classifier()
    get_watch_detector()
    get_clip_detector()