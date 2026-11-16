import os
import torch
from PIL import Image
from transformers import pipeline
from src.inference.device import resolve_device

'''
This file implement the logic of the zero-shot clip model. This comes in action after the deeplearning model has predicted the Rolex model. It checks the model variants in the file rolex_variants.json to tell which specific variant that model is.
'''

MODEL_NAME = 'openai/clip-vit-base-patch16'
_detector = None

def get_detector(): 
    '''
    This function is to create and return the CLIP image classification pipeline. It loads the CLIP model only once the first time, and store it inside the global _detector to reuse in the future
    '''
    global _detector
    if _detector is None: 
        device = resolve_device()
        is_cuda = device.type == "cuda"
        _detector = pipeline (
            task = 'zero-shot-image-classification',
            model = MODEL_NAME,
            token = os.getenv("HF_TOKEN"),
            device = 0 if is_cuda else -1,
            torch_dtype = torch.float16 if is_cuda else torch.float32,
        )
    return _detector

def rank_variants(
    image: Image.Image,
    variants: list[dict[str, object]],
    detector = None,
    top_k: int = 3,
):
    '''
    This function return the possible variant for the predicted Rolex model
    '''
    if not variants: 
        return {
            "variant_status": "no_variants_available",
            "variant_note": "No variant catalog is available for this model",
            "variant_candidates": [],
        }
    
    detector = detector or get_detector()
    labels = [str(variant["clip_text"]) for variant in variants]

    variants_by_label = {
        str (variant["clip_text"]): variant 
        for variant in variants
    }

    predictions = detector (image, candidate_labels = labels)
    # Every variant in the family with its score and catalog description, so the
    # front end can show how each description was weighed.
    all_scores = []
    for prediction in predictions:
        variant = variants_by_label[prediction["label"]]
        all_scores.append (
            {
                "id": variant['id'],
                "display_name": variant["display_name"],
                "score": float (prediction ["score"]),
                "description": str (variant["clip_text"]),
                "reference_examples": variant.get ("reference_examples", []),
            }
        )

    ranked = []
    for prediction in predictions[:top_k]: 
        variant = variants_by_label[prediction["label"]]
        ranked.append (
            {
                "id": variant['id'],
                "display_name": variant["display_name"],
                "score": float (prediction ["score"]),
                "reference_examples": variant.get ("reference_examples", []),
            }
        )

    top_score = ranked[0]['score'] if ranked else 0.0
    second_score = ranked[1]['score'] if len (ranked) > 1 else 0.0 
    if top_score < 0.35 or top_score - second_score < 0.08:
        return {
            "variant_status": "closest_known_matches",
            "variant_note": "The exact variant may not be in the catalog; these are the closest known matches",
            "variant_candidates": ranked,
            "variant_scores": all_scores,
        }
    return {
        "variant_status": "matched_known_variant",
        "variant_note": "The top result is the strongest match among known catalog variants, not a guaranteed exact reference",
        "variant_candidates": ranked,
        "variant_scores": all_scores,
    }

def _package (ranked: list, all_scores: list):
    top_score = ranked[0]['score'] if ranked else 0.0
    second_score = ranked[1]['score'] if len (ranked) > 1 else 0.0
    if top_score < 0.35 or top_score - second_score < 0.08:
        return {
            "variant_status": "closest_known_matches",
            "variant_note": "The exact variant may not be in the catalog; these are the closest known matches",
            "variant_candidates": ranked,
            "variant_scores": all_scores,
        }
    return {
        "variant_status": "matched_known_variant",
        "variant_note": "The top result is the strongest match among known catalog variants, not a guaranteed exact reference",
        "variant_candidates": ranked,
        "variant_scores": all_scores,
    }

def rank_variants_head (image: Image.Image, variants: list[dict[str, object]], head: dict, top_k: int = 3):
    '''
    Variant ranking with a trained head on the CLIP image embedding, mixed with the zero-shot text prompts
    (src/training/variant_head.py). Variants without training photos keep the zero-shot score only.
    '''
    if not variants:
        return rank_variants (image, variants)
    from src.inference.clip_embed import embed

    model = get_detector().model
    emb = torch.tensor (embed ([image], model, next (model.parameters()).device)[0])
    ids = head["variants"]
    idx = [ids.index (v["id"]) for v in variants]
    zero_shot = torch.softmax (100.0 * emb @ head["text"][idx].T, dim = -1)
    trained = torch.softmax (head["scale"] * (emb @ head["weight"][idx].T + head["bias"][idx]), dim = -1)
    use = head["has_data"][idx]
    mix = float (head["mix"])
    probs = torch.where (use, (1 - mix) * zero_shot + mix * trained, zero_shot)
    order = torch.argsort (probs, descending = True).tolist()
    entries = [
        {
            "id": variants[i]["id"],
            "display_name": variants[i]["display_name"],
            "score": float (probs[i]),
            "reference_examples": variants[i].get ("reference_examples", []),
        }
        for i in order
    ]
    all_scores = [dict (e, description = str (variants[order[k]]["clip_text"])) for k, e in enumerate (entries)]
    return _package (entries[:top_k], all_scores)
