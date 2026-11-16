"""
Augmentations that make studio watch photos look like real-life photos.

Retailer photos are a watch on a plain white background. Real photos have wrists, desks, boxes, shop
lights, close-ups and phone noise. These transforms work on PIL images and are used to train the family
classifier so it copes with that gap.

    RandomBackground  replace the plain white background with a texture (wood, skin, cloth, dark, gradient)
    RandomMacro       zoom into part of the watch, like a close-up of the dial
    real_look_pil()   the full chain: background, macro, tilt, colour, glare, blur, JPEG
"""
import random
from io import BytesIO

import cv2
import numpy as np
from PIL import Image, ImageFilter
from torchvision import transforms


def _noise_texture(size: int, base: tuple[int, int, int], scale: int = 8, strength: float = 40.0) -> np.ndarray:
    """Smooth random blobs around a base colour (looks like skin, leather, cloth or a desk)."""
    small = np.random.rand(scale, scale).astype("float32")
    big = cv2.resize(small, (size, size), interpolation=cv2.INTER_CUBIC).reshape(size, size, 1)
    fine = np.random.rand(size, size, 1).astype("float32") * 0.15
    tex = np.array(base, dtype="float32")[None, None, :] + (big - 0.5) * strength * 2 + (fine - 0.075) * strength
    return np.clip(tex, 0, 255)


def make_background(size: int) -> np.ndarray:
    kind = random.choice(["skin", "wood", "dark", "cloth", "gradient", "leather", "marble", "color"])
    if kind == "skin":
        base = random.choice([(224, 172, 140), (198, 134, 100), (141, 85, 62), (240, 200, 170), (110, 70, 50)])
        return _noise_texture(size, base, scale=6, strength=18)
    if kind == "wood":
        base = random.choice([(120, 80, 50), (160, 110, 70), (90, 60, 40)])
        tex = _noise_texture(size, base, scale=5, strength=15)
        stripes = (np.sin(np.arange(size) / random.uniform(4, 14))[None, :, None] * 12).astype("float32")
        return np.clip(tex + stripes, 0, 255)
    if kind == "dark":
        base = random.choice([(20, 20, 24), (35, 30, 28), (10, 25, 20), (45, 45, 50)])
        return _noise_texture(size, base, scale=4, strength=10)
    if kind == "cloth":
        base = random.choice([(200, 190, 175), (120, 130, 150), (150, 40, 50), (30, 60, 45), (230, 230, 225)])
        tex = _noise_texture(size, base, scale=12, strength=14)
        weave = ((np.indices((size, size)).sum(axis=0) % 4 < 2)[..., None] * 8).astype("float32")
        return np.clip(tex + weave, 0, 255)
    if kind == "leather":
        base = random.choice([(60, 35, 25), (30, 30, 30), (90, 60, 40)])
        return _noise_texture(size, base, scale=16, strength=16)
    if kind == "marble":
        base = random.choice([(235, 235, 232), (210, 215, 220), (190, 190, 190)])
        return _noise_texture(size, base, scale=7, strength=14)
    if kind == "gradient":
        a = np.array([random.randint(30, 230) for _ in range(3)], dtype="float32")
        b = np.array([random.randint(30, 230) for _ in range(3)], dtype="float32")
        t = np.linspace(0, 1, size, dtype="float32")[:, None, None]
        grad = a[None, None, :] * (1 - t) + b[None, None, :] * t
        return np.repeat(grad, size, axis=1)
    return np.full((size, size, 3), [random.randint(20, 235) for _ in range(3)], dtype="float32")


def background_mask(rgb: np.ndarray) -> np.ndarray:
    """Pixels of the near-white background that touch the image border (True = background)."""
    height, width = rgb.shape[:2]
    near_white = ((rgb.min(axis=2) > 222) & ((rgb.max(axis=2).astype(int) - rgb.min(axis=2)) < 24)).astype("uint8")
    flood = near_white.copy()
    mask = np.zeros((height + 2, width + 2), np.uint8)
    background = np.zeros((height, width), dtype=bool)
    for seed in [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1), (width // 2, 0), (width // 2, height - 1)]:
        if flood[seed[1], seed[0]] == 1:
            tmp = flood.copy()
            m = np.zeros((height + 2, width + 2), np.uint8)
            cv2.floodFill(tmp, m, seed, 2)
            background |= tmp == 2
    return background


class RandomBackground:
    """Swap the plain white background for a random texture, with a soft shadow under the watch."""

    def __init__(self, p: float = 0.7):
        self.p = p

    def __call__(self, image: Image.Image) -> Image.Image:
        if random.random() > self.p:
            return image
        rgb = np.asarray(image.convert("RGB"))
        mask = background_mask(rgb)
        if mask.mean() < 0.05:  # nothing to replace (already a photo with a real background)
            return image
        height, width = mask.shape
        bg = make_background(max(height, width))[:height, :width]
        if random.random() < 0.5:  # depth of field
            bg = cv2.GaussianBlur(bg, (0, 0), random.uniform(1.5, 5))
        soft = cv2.GaussianBlur(mask.astype("float32"), (0, 0), 1.2)[..., None]
        shadow = cv2.GaussianBlur((~mask).astype("float32"), (0, 0), random.uniform(6, 14))
        shadow = np.roll(shadow, (random.randint(4, 14), random.randint(-8, 8)), axis=(0, 1))[..., None]
        bg = bg * (1 - 0.35 * shadow * soft)
        out = rgb.astype("float32") * (1 - soft) + bg * soft
        return Image.fromarray(np.clip(out, 0, 255).astype("uint8"))


class RandomMacro:
    """Zoom into a random part of the picture (close-up of the dial, bezel or bracelet)."""

    def __init__(self, p: float = 0.3, scale=(0.35, 0.75)):
        self.p = p
        self.scale = scale

    def __call__(self, image: Image.Image) -> Image.Image:
        if random.random() > self.p:
            return image
        width, height = image.size
        factor = random.uniform(*self.scale)
        crop_w, crop_h = int(width * factor), int(height * factor)
        # bias towards the centre where the dial is
        left = int((width - crop_w) * random.betavariate(2, 2))
        top = int((height - crop_h) * random.betavariate(2, 2))
        return image.crop((left, top, left + crop_w, top + crop_h)).resize((width, height), Image.BICUBIC)


class RandomGlare:
    def __init__(self, p: float = 0.3, strength=(0.25, 0.65)):
        self.p = p
        self.strength = strength

    def __call__(self, image: Image.Image) -> Image.Image:
        if random.random() > self.p:
            return image
        rgb = np.asarray(image.convert("RGB")).astype("float32")
        height, width = rgb.shape[:2]
        cx, cy = random.uniform(0.2, 0.8) * width, random.uniform(0.2, 0.8) * height
        radius = random.uniform(0.12, 0.4) * max(width, height)
        ys, xs = np.mgrid[0:height, 0:width]
        glow = np.exp(-(((xs - cx) ** 2 + (ys - cy) ** 2) / (2 * radius**2)))
        rgb = rgb + (255.0 - rgb) * (glow[..., None] * random.uniform(*self.strength))
        return Image.fromarray(np.clip(rgb, 0, 255).astype("uint8"))


class RandomJpeg:
    def __init__(self, quality=(25, 90), p: float = 0.5):
        self.quality = quality
        self.p = p

    def __call__(self, image: Image.Image) -> Image.Image:
        if random.random() > self.p:
            return image
        buffer = BytesIO()
        image.convert("RGB").save(buffer, format="JPEG", quality=random.randint(*self.quality))
        buffer.seek(0)
        return Image.open(buffer).convert("RGB")


class RandomBlur:
    def __init__(self, p: float = 0.35, radius=(0.5, 2.2)):
        self.p = p
        self.radius = radius

    def __call__(self, image: Image.Image) -> Image.Image:
        if random.random() > self.p:
            return image
        return image.filter(ImageFilter.GaussianBlur(random.uniform(*self.radius)))


def real_look_pil(size: int = 224) -> transforms.Compose:
    """PIL -> PIL chain. Apply before the model's own resize and normalise."""
    # Tilt and perspective first, filled with white, so the new corners become background too.
    return transforms.Compose(
        [
            transforms.RandomRotation(degrees=20, fill=(255, 255, 255)),
            transforms.RandomPerspective(distortion_scale=0.3, p=0.4, fill=(255, 255, 255)),
            RandomBackground(p=0.7),
            RandomMacro(p=0.3),
            transforms.ColorJitter(brightness=0.4, contrast=0.35, saturation=0.3, hue=0.04),
            RandomGlare(p=0.3),
            RandomBlur(p=0.35),
            RandomJpeg(p=0.5),
        ]
    )
