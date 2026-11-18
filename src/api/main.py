import base64
import os
import sys
import time
from io import BytesIO
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.training.dataset import build_transforms
from src.training.models import create_model
from src.identify.clip_matcher import rank_variants, rank_variants_head
from src.identify.variants import load_catalog, variants_family
from src.identify.summary import format_model_name
from src.detection.watch_cropper import bracelet_edge_overlay, crop_watch_stages
from src.inference.device import resolve_device
from src.inference.timing import STARTUP, timed
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

VARIANT_CATALOG_PATH = PROJECT_ROOT / 'src/identify/rolex_variants.json'
MODEL_PATH = PROJECT_ROOT / 'models/rolex_classifier_model.pt'
HEAD_PATH = PROJECT_ROOT / 'models/clip_head.pt'
VARIANT_HEAD_PATH = PROJECT_ROOT / 'models/variant_head.pt'
OPEN_SET_PATH = PROJECT_ROOT / 'models/open_set.pt'

app = FastAPI(title = 'Rolex Classifier')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://rolex-finder.vercel.app",
        "https://rolexfinder.onrender.com",
    ],
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

variant_catalog = load_catalog(VARIANT_CATALOG_PATH)
device = resolve_device()
model = None
class_names = []

def load_model(): 
    '''
    This function is simply to load DL model to reuse it in the future
    '''
    global model, class_names
    if not MODEL_PATH.exists(): 
        return 
    checkpoint = torch.load (MODEL_PATH, map_location = device)
    class_names = checkpoint ['class_names']
    model = create_model (
        num_classes=len(class_names),
        pretrained=False,
    ).to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

_head = None

def get_head():
    '''
    Linear family head on CLIP image embeddings (trained by src/training/clip_head.py). It copes with real photos
    better than the EfficientNet. Set FAMILY_MODEL=effnet to use the EfficientNet instead.
    '''
    global _head
    if _head is None:
        _head = False
        if HEAD_PATH.exists() and os.getenv('FAMILY_MODEL', 'clip_head') != 'effnet':
            head = torch.load (HEAD_PATH, map_location = device, weights_only = True)
            _head = head
    return _head or None

_variant_head = None

def get_variant_head():
    '''Trained variant head (see src/training/variant_head.py). Set VARIANT_MODEL=zero_shot to use the text prompts only.'''
    global _variant_head
    if _variant_head is None:
        _variant_head = False
        if VARIANT_HEAD_PATH.exists() and os.getenv('VARIANT_MODEL', 'head') != 'zero_shot':
            _variant_head = torch.load (VARIANT_HEAD_PATH, map_location = 'cpu', weights_only = True)
    return _variant_head or None

_open_set = None

def get_open_set():
    '''
    Gate for photos of watches that are not a Rolex we know (src/training/open_set_gate.py). Off unless OPEN_SET=on.
    '''
    global _open_set
    if _open_set is None:
        if os.getenv('OPEN_SET', 'off') == 'on' and OPEN_SET_PATH.exists():
            _open_set = torch.load (OPEN_SET_PATH, map_location = 'cpu', weights_only = True)
        else:
            _open_set = {}
    return _open_set or None

def head_probabilities (embedding: torch.Tensor, head: dict):
    '''Softmax over scale * (embedding W^T + b). embedding is one L2-normalised CLIP vector.'''
    logits = head['scale'] * (embedding @ head['weight'].T + head['bias'])
    return torch.softmax (logits, dim = -1)

def decode_image (contents: bytes): 
    '''
    This function is to convert input image in to bytes for model to process
    '''
    try: 
        # Phone photos store rotation in EXIF; apply it so sideways photos reach the model upright
        return ImageOps.exif_transpose (Image.open (BytesIO(contents))).convert ('RGB')
    except:
        raise HTTPException(status_code=400, detail = "There's something wrong with the uploaded image")

def get_model():
    '''
    This function is simply to fetch the DL model
    '''
    global model
    if model is None: 
        load_model()
    return model

def predict_family (image: Image.Image):
    '''
    Run only the EfficientNet family classifier. Returns predicted_class, confidence and sorted probabilities.
    '''
    if model is None or not class_names:
        get_model()

    head = get_head()
    names = head['class_names'] if head is not None else class_names
    rolex_score = None
    if head is not None:
        from src.identify.clip_matcher import get_detector as get_clip
        from src.inference.clip_embed import embed
        with torch.no_grad():
            embedding = torch.tensor (embed ([image], get_clip().model, device)[0]).to(device)
            probabilities = head_probabilities (embedding, head).cpu()
        gate = get_open_set()
        if gate is not None:
            rolex_score = float (torch.softmax (gate['scale'] * embedding.cpu() @ gate['text'].T, dim = 0)[0])
    else:
        transform = build_transforms(train = False)
        tensor = transform (image).unsqueeze(0).to(device)
        with torch.no_grad():
            logits = model(tensor)
            probabilities = torch.softmax(logits, dim = 1)[0].cpu()

    predicted_index = int (probabilities.argmax().item())
    probabilities = {
        class_name: float (probabilities[index].item())
        for index, class_name in enumerate(names)
    }
    probabilities = dict (
        sorted (
            probabilities.items(),
            key = lambda item: item[1],
            reverse = True,
        )
    )

    predicted_class = names[predicted_index]
    result = {
        'predicted_class': predicted_class,
        'confidence': probabilities[names[predicted_index]],
        'probabilities': probabilities,
    }
    if rolex_score is not None:
        result['rolex_score'] = rolex_score
        result['unknown_watch'] = rolex_score < get_open_set()['threshold']
    return result

def predict_image (image: Image.Image, timings: dict | None = None): 
    '''
    This function is to predict the Rolex model using Deep Learning model. And then, traverse through the variants description of that model to recognize the variant using zero-shot CLIP model. A summary of that data is also provided. 

    * result is first formatted with data output, including 3 tags: predicted_classs, confidence, and prob
    * result is then updaed with variant prediction using CLIP, (using rank_variants function)
    * result is eventually added with a summary of the output, providing concise semantic result instead of data
    '''
    if model is None or not class_names:
        get_model()

    with timed ('classify', timings):
        result = predict_family (image)
    predicted_class = result['predicted_class']

    variants = variants_family(variant_catalog, predicted_class)
    with timed ('variant_match', timings):
        variant_head = get_variant_head()
        if variant_head is not None and variants:
            result.update (rank_variants_head (image, variants, variant_head))
        else:
            result.update (rank_variants(image, variants))
    result['model_name'] = format_model_name(result)
    return result

def encode_data_url (image: Image.Image, max_side: int = 520, quality: int = 82, png: bool = False):
    '''
    Shrink an image and return it as a data URL, so the front end can show it without a second request
    '''
    preview = image.copy()
    preview.thumbnail ((max_side, max_side))
    buffer = BytesIO()
    if png:
        preview.convert ('RGBA').save (buffer, format = 'PNG', optimize = True)
        mime = 'image/png'
    else:
        preview.convert ('RGB').save (buffer, format = 'JPEG', quality = quality)
        mime = 'image/jpeg'
    return f"data:{mime};base64,{base64.b64encode (buffer.getvalue()).decode ('ascii')}"

def build_steps (original: Image.Image, stages: dict, crop_info: dict):
    '''
    Describe what the pipeline did at each preprocessing step (detect, straighten, isolate the dial),
    with a small picture of each result. The front end plays these back while showing the answer.
    Returns None when there is nothing to show, so a failure here never breaks a prediction.
    '''
    if not stages:
        return None
    try:
        alignment = crop_info.get ('alignment', {})
        dial = crop_info.get ('dial_crop', {})
        return {
            'original_size': list (original.size),
            'detect': {
                'box': crop_info.get ('box'),
                'score': crop_info.get ('score'),
            },
            'alignment': {
                'applied': alignment.get ('alignment_applied', False),
                'rotation_degrees': alignment.get ('rotation_degrees', 0),
                'axis_angle_degrees': alignment.get ('bracelet_axis_angle_degrees'),
                'axis_confidence': alignment.get ('bracelet_axis_confidence'),
                'reason': alignment.get ('reason'),
            },
            'dial': {
                'used': dial.get ('dial_crop_used', False),
                'score': dial.get ('score'),
                'center_distance_ratio': dial.get ('center_distance_ratio'),
                'aspect_ratio': dial.get ('aspect_ratio'),
                'reason': dial.get ('reason'),
            },
            'images': {
                'crop': encode_data_url (stages['crop']),
                'edges': encode_data_url (bracelet_edge_overlay (stages['crop']), png = True),
                'aligned': encode_data_url (stages['aligned']),
                'dial': encode_data_url (stages['dial']),
            },
        }
    except Exception:
        return None

'''
FastAPI format to operate the project pipeline
'''
@app.post ('/predict')
async def predict (file: UploadFile = File(...), include_steps: bool = False): 
    '''
    include_steps=true also returns base64 images of each preprocessing step (debug only; the site does not use them).
    '''
    timings: dict = {}
    request_start = time.perf_counter()
    contents = await file.read()
    with timed ('decode', timings):
        image = decode_image (contents)
    with timed ('preprocess', timings):
        cropped_image, crop_info, stages = crop_watch_stages (image)
    if crop_info.get("reason") == "no_watch_detected":
        result = dict()
        predicted_class = "No Watch Detected"
        confidence = 0.0
        probabilities = {
            "cellini": 0.0,
            "daytona": 0.0,
            "explorer": 0.0,
            "yacht_master": 0.0,
            "submariner": 0.0,
            "president": 0.0,
            "airking": 0.0,
            "oyster_perpetual": 0.0,
            "milgauss": 0.0,
            "oysterquartz": 0.0,
            "date": 0.0,
            "sea_dweller": 0.0,
            "turn_o_graph": 0.0,
            "gmt_master": 0.0,
            "datejust": 0.0,
        }
        
        variant_note = "No watch was detected in the image. Please upload an image that clearly shows a watch"
        variant_candidates = [
            {
                "id": "None",
                "display_name": "None",
                "score": 0.0,
                "reference_examples": None
            },
            {
                "id": "None",
                "display_name": "None",
                "score": 0.0,
                "reference_examples": None
            },
            {
                "id": "None",
                "display_name": "None",
                "score": 0.0,
                "reference_examples": None
            },
        ]

        result["predicted_class"] = predicted_class
        result["confidence"] = confidence
        result["probabilities"] = probabilities
        result["variant_note"] = variant_note
        result["variant_candidates"] = variant_candidates

        return result
    
    result = predict_image (cropped_image, timings)
    result["crop_info"] = crop_info
    if include_steps:
        result["steps"] = build_steps (image, stages, crop_info)
    timings["total"] = round ((time.perf_counter() - request_start) * 1000, 1)
    print (f"[timing] request_total={timings['total']}ms", flush = True)
    result["timings_ms"] = timings
    return result


@app.get("/health")
async def health():
    """
    Check the health of the site
    """
    return {"status": "ok", "startup_timings_ms": STARTUP}


FRONTEND_DIST_DIR = PROJECT_ROOT / "front_end" / "dist"
if FRONTEND_DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.api.main:app", host="localhost", port=port, reload=True)