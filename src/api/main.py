import sys
from io import BytesIO
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.training.dataset import build_transforms
from src.training.models import create_model
from src.identify.clip_matcher import rank_variants
from src.identify.variants import load_catalog, variants_family
from src.identify.summary import format_model_name
from src.detection.watch_cropper import crop_watch
from src.inference.device import resolve_device
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from fastapi.staticfiles import StaticFiles

VARIANT_CATALOG_PATH = PROJECT_ROOT / 'src/identify/rolex_variants.json'
MODEL_PATH = PROJECT_ROOT / 'models/rolex_classifier_model.pt'
OUTPUT_IMAGE_DIR = PROJECT_ROOT / "output_image"

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

def decode_image (contents: bytes): 
    '''
    This function is to convert input image in to bytes for model to process
    '''
    try: 
        return Image.open (BytesIO(contents)).convert ('RGB')
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

def predict_image (image: Image.Image): 
    '''
    This function is to predict the Rolex model using Deep Learning model. And then, traverse through the variants description of that model to recognize the variant using zero-shot CLIP model. A summary of that data is also provided. 

    * result is first formatted with data output, including 3 tags: predicted_classs, confidence, and prob
    * result is then updaed with variant prediction using CLIP, (using rank_variants function)
    * result is eventually added with a summary of the output, providing concise semantic result instead of data
    '''
    if model is None or not class_names:
        get_model()

    transform = build_transforms(train = False)
    tensor = transform (image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(tensor)
        probabilities = torch.softmax(logits, dim = 1)[0].cpu()

    predicted_index = int (probabilities.argmax().item())
    probabilities = {
        class_name: float (probabilities[index].item())
        for index, class_name in enumerate(class_names)
    }
    probabilities = dict (
        sorted (
            probabilities.items(),
            key = lambda item: item[1],
            reverse = True,
        )
    )

    predicted_class = class_names[predicted_index]
    result =  {
        'predicted_class': predicted_class,
        'confidence': probabilities[class_names[predicted_index]],
        'probabilities': probabilities,
    }

    variants = variants_family(variant_catalog, predicted_class)
    result.update (rank_variants(image, variants))
    result['model_name'] = format_model_name(result)
    return result

def save_processed_image (image: Image.Image):
    OUTPUT_IMAGE_DIR.mkdir (parents = True, exist_ok=True)
    for existing_file in OUTPUT_IMAGE_DIR.iterdir():
        if existing_file.is_file():
            existing_file.unlink()
            
    timestamp = datetime.now().strftime ("%Y%m%d_%H%M%S_f")[:-3]
    output_path = OUTPUT_IMAGE_DIR / f"watch_{timestamp}.jpg"
    image.save(output_path, format="JPEG", quality = 95)
    return output_path

'''
FastAPI format to operate the project pipeline
'''
@app.post ('/predict')
async def predict (file: UploadFile = File(...)): 
    contents = await file.read()
    image = decode_image (contents)
    cropped_image, crop_info = crop_watch (image)
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
    
    result = predict_image (cropped_image)
    processed_image_path = save_processed_image (cropped_image)
    result["crop_info"] = crop_info
    result["processed_image_path"] = str(processed_image_path)
    return result


@app.get("/health")
async def health():
    """
    Check the health of the site
    """
    return {"status": "ok"}


FRONTEND_DIST_DIR = PROJECT_ROOT / "front_end" / "dist"
if FRONTEND_DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.api.main:app", host="localhost", port=port, reload=True)