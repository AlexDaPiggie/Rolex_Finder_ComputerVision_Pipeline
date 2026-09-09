from PIL import Image, ImageDraw

from src.detection.watch_cropper import align_watch_crop


def make_crop(size=(120, 120), box=(15, 50, 105, 70)):
    image = Image.new("RGB", size, color="white")
    draw = ImageDraw.Draw(image)
    draw.rectangle(box, fill="black")
    return image


def test_align_watch_crop_rotates_confident_horizontal_shape():
    image = make_crop(box=(15, 50, 105, 70))

    aligned, info = align_watch_crop(image)

    assert info["alignment_applied"] is True
    assert info["rotation_degrees"] == -90
    assert aligned.size == image.size


def test_align_watch_crop_leaves_confident_vertical_shape_unchanged():
    image = make_crop(box=(50, 15, 70, 105))

    aligned, info = align_watch_crop(image)

    assert info["alignment_applied"] is False
    assert info["rotation_degrees"] == 0
    assert aligned.size == image.size


def test_align_watch_crop_skips_nearly_square_shape():
    image = make_crop(box=(35, 35, 85, 85))

    aligned, info = align_watch_crop(image)

    assert info["alignment_applied"] is False
    assert info["rotation_degrees"] == 0
    assert aligned.size == image.size


def test_align_watch_crop_rotates_wide_crop_when_largest_contour_is_square():
    image = make_crop(size=(160, 100), box=(60, 25, 100, 65))

    aligned, info = align_watch_crop(image)

    assert info["alignment_applied"] is True
    assert info["rotation_degrees"] == -90
    assert info["reason"] == "wide_crop_rotated"
    assert aligned.size == (image.height, image.width)
