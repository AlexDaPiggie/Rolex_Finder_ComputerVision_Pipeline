import json
import random
from io import BytesIO
from pathlib import Path
from PIL import Image
from torchvision import datasets, transforms

IMAGE_SIZE = 224 #resive for cnn models
IMAGENET_MEAN = (0.485, 0.456, 0.406) #normalizaation
IMAGENET_STD = (0.229, 0.224, 0.225) #standard deviation

def load_class_mapping (data_root: Path): 
    '''
    read the mapping from processded dataset and turn that to dictionary
    '''
    mapping_path = data_root / 'class_mapping.json'
    mapping = json.loads(mapping_path.read_text(encoding = 'utf-8'))
    return {str(label): int (index) for label, index in mapping.items()}

def load_class_names(data_root: Path):
    '''
    - Turn the .json files into a list of class names with correct numeric order
    - This is to verify the labels used in other steps
    '''
    mapping = load_class_mapping(data_root)
    return [label for label, _index in sorted (
        mapping.items(),
        key = lambda item: item[1]
    )]

class RandomJpeg:
    """Re-encode the image as a low-quality JPEG, like a photo sent through chat apps or social media."""

    def __init__(self, quality=(30, 90), p=0.4):
        self.quality = quality
        self.p = p

    def __call__(self, image: Image.Image):
        if random.random() > self.p:
            return image
        buffer = BytesIO()
        image.convert("RGB").save(buffer, format="JPEG", quality=random.randint(*self.quality))
        buffer.seek(0)
        return Image.open(buffer).convert("RGB")


class RandomGlare:
    """Add a soft bright reflection, like light on the crystal or a flash in a phone photo."""

    def __init__(self, p=0.25, strength=(0.25, 0.6)):
        self.p = p
        self.strength = strength

    def __call__(self, image: Image.Image):
        if random.random() > self.p:
            return image
        import numpy as np

        rgb = np.asarray(image.convert("RGB")).astype("float32")
        height, width = rgb.shape[:2]
        cx, cy = random.uniform(0.2, 0.8) * width, random.uniform(0.2, 0.8) * height
        radius = random.uniform(0.15, 0.4) * max(width, height)
        ys, xs = np.mgrid[0:height, 0:width]
        glow = np.exp(-(((xs - cx) ** 2 + (ys - cy) ** 2) / (2 * radius**2)))
        amount = random.uniform(*self.strength)
        rgb = rgb + (255.0 - rgb) * (glow[..., None] * amount)
        return Image.fromarray(np.clip(rgb, 0, 255).astype("uint8"))


def build_transforms (train: bool, real: bool = False):
    '''
    Build dataset engine:
    - only do data augmentation if it's train
    '''
    if train and real:
        # Studio photos made to look like real photos (backgrounds, close-ups, glare, blur, JPEG)
        from src.training.real_aug import real_look_pil

        return transforms.Compose(
            [
                real_look_pil(),
                transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
                transforms.ToTensor(),
                transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
                transforms.RandomErasing(p = 0.15, scale = (0.02, 0.1), ratio = (0.3, 3.3)),
            ]
        )

    if train:
        return transforms.Compose(
            [
                transforms.RandomResizedCrop(
                    IMAGE_SIZE,
                    scale = (0.75, 1.1),
                    ratio = (0.85, 1.5),
                ),
                transforms.RandomRotation(degrees=55),

                transforms.RandomPerspective(
                    distortion_scale=0.25,
                    p = 0.35,
                ),
                # phone-photo realism: blur and compression artefacts
                transforms.RandomApply(
                    [transforms.GaussianBlur(kernel_size=5, sigma=(0.1, 2.0))],
                    p = 0.3,
                ),
                RandomJpeg(quality = (30, 90), p = 0.4),
                RandomGlare(p = 0.25),
                transforms.ColorJitter(
                    brightness=0.25,
                    contrast = 0.25,
                    saturation = 0.15,
                    hue = 0.03,
                ),
                transforms.ToTensor(),
                transforms.Normalize(
                    IMAGENET_MEAN,
                    IMAGENET_STD,
                ),
                transforms.RandomErasing(
                    p = 0.2,
                    scale = (0.02, 0.12),
                    ratio = (0.3, 3.3),
                ),
            ]
        )
    
    return transforms.Compose(
        [
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]
    )

def make_image_folder (data_root: Path, split: str, train: bool, real: bool = False):
    '''
    This is to create a Pytorch dataset for one split
    '''
    split_root = data_root / split
    dataset = datasets.ImageFolder(
        split_root,
        transform = build_transforms(train = train, real = real),
    )
    expected_classes = load_class_names(data_root)
    if dataset.classes != expected_classes:
        raise ValueError(
            f"Class order in Image Folder: {dataset.classes} doesn't match classes order in class_mapping.json: {expected_classes}"
        )
    return dataset