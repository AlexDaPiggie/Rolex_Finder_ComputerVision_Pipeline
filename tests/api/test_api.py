from io import BytesIO
from fastapi.testclient import TestClient
from PIL import Image
import torch 
import torch.nn as nn
from src.api import main

class FixedModel (nn.Module):
    def forward (self, images):
        return torch.tensor ([[0.0, 3.0, 1.0]])
    
def make_upload_image():
    image = Image.new('RGB', (64, 64), color = 'white')
    buffer = BytesIO()
    image.save (buffer, format = 'JPEG')
    buffer.seek (0)
    return buffer

def test_predict_return_probabilities (monkeypatch): 
    monkeypatch.setattr(main, 'model', FixedModel())
    monkeypatch.setattr(main, 'class_names', ['datejust', 'gmt_master', 'submariner'])
    monkeypatch.setattr(
        main,
        'crop_watch',
        lambda image: (image, {"crop_used": True}),
    )
    monkeypatch.setattr(
        main,
        'rank_variants',
        lambda image, variants: {
            "variant_status": "matched_known_variant",
            "variant_note": "The top result is the strongest match among known catalog variants, not a guaranteed exact reference",
            "variant_candidates": [
                {
                    "id": "gmt_batman",
                    "display_name": "Rolex GMT-Master II Batman",
                    "score": 0.71,
                    "reference_examples": ["126710BLNR"],
                },
                {
                    "id": "gmt_pepsi",
                    "display_name": "Rolex GMT-Master II Pepsi",
                    "score": 0.22,
                    "reference_examples": ["126710BLRO"],
                },
            ],
        },
    )
    client = TestClient(main.app)
    response = client.post (
        '/predict',
        files = {'file': ('watch.jpg', make_upload_image(), 'iamge/jpeg')},
    )

    assert response.status_code == 200
    body = response.json()
    assert body['predicted_class'] == 'gmt_master'
    assert body['confidence'] > 0.8
    assert set(body['probabilities']) == {'datejust', 'gmt_master', 'submariner'}

def test_predict_returns_message_when_no_watch_detected(monkeypatch):
    def fail_predict_image(image):
        raise AssertionError("predict_image should not run when no watch is detected")

    monkeypatch.setattr(
        main,
        'crop_watch',
        lambda image: (
            image,
            {
                "crop_used": False,
                "reason": "no_watch_detected",
            },
        ),
    )
    monkeypatch.setattr(main, 'predict_image', fail_predict_image)

    client = TestClient(main.app)
    response = client.post (
        '/predict',
        files = {'file': ('not_watch.jpg', make_upload_image(), 'iamge/jpeg')},
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "no_watch_detected",
        "message": "No watch was detected in the image. Please upload an image that clearly shows a watch.",
        "crop_info": {
            "crop_used": False,
            "reason": "no_watch_detected",
        },
    }
    
