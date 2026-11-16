"""
CLIP image embeddings for the family classifier head.

The site already loads CLIP B/16 for variant matching. A small linear head on top of its image embeddings
is a family classifier that copes better with real photos than a fine-tuned CNN, and costs one extra
matrix multiply at inference.

Preprocessing is a plain 224x224 resize (no centre crop), so tall watch photos keep their bracelet and bezel.
"""
import numpy as np
import torch
from PIL import Image
from torchvision import transforms

CLIP_MEAN = (0.48145466, 0.4578275, 0.40821073)
CLIP_STD = (0.26862954, 0.26130258, 0.27577711)

preprocess = transforms.Compose(
    [
        transforms.Resize((224, 224), interpolation=transforms.InterpolationMode.BICUBIC),
        transforms.ToTensor(),
        transforms.Normalize(CLIP_MEAN, CLIP_STD),
    ]
)


def embed(images: list[Image.Image], clip_model, device) -> np.ndarray:
    """L2-normalised CLIP image embeddings, shape (n, 512). clip_model is a transformers CLIPModel."""
    batch = torch.stack([preprocess(image.convert("RGB")) for image in images]).to(device)
    batch = batch.to(next(clip_model.parameters()).dtype)
    with torch.no_grad():
        features = clip_model.get_image_features(pixel_values=batch)
        if not isinstance(features, torch.Tensor):  # newer transformers return an output object
            features = features.pooler_output
        features = features / features.norm(dim=-1, keepdim=True)
    return features.float().cpu().numpy()
