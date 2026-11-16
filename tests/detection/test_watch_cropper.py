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
    assert abs(info["rotation_degrees"]) == 90
    assert aligned.size == image.size


def test_align_watch_crop_never_turns_more_than_90_degrees():
    # A tilted bracelet must take the short way round, not flip the watch upside down.
    for angle in range(0, 360, 15):
        image = make_crop(size=(200, 200), box=(20, 90, 180, 110)).rotate(
            angle, expand=True, fillcolor="white"
        )
        _, info = align_watch_crop(image)
        assert abs(info["rotation_degrees"]) <= 90, angle


def test_align_watch_crop_fills_rotated_corners_with_border_colour():
    image = Image.new("RGB", (200, 200), color=(200, 30, 30))
    ImageDraw.Draw(image).rectangle((30, 90, 170, 110), fill="black")
    image = image.rotate(30, expand=False, fillcolor=(200, 30, 30))

    aligned, info = align_watch_crop(image)

    assert info["alignment_applied"] is True
    assert aligned.getpixel((0, 0)) == (200, 30, 30)


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


def test_align_watch_crop_leaves_wide_crop_with_square_contour_unchanged():
    # A square dial gives too few bracelet edges to measure a tilt, so do not guess a rotation.
    image = make_crop(size=(160, 100), box=(60, 25, 100, 65))

    aligned, info = align_watch_crop(image)

    assert info["alignment_applied"] is False
    assert info["rotation_degrees"] == 0
    assert info["reason"] == "not_enough_bracelet_edges"
    assert aligned.size == image.size


def test_bracelet_edge_overlay_matches_thumbnail_size():
    from src.detection.watch_cropper import bracelet_edge_overlay

    image = make_crop(size=(1040, 780), box=(100, 300, 900, 480))

    overlay = bracelet_edge_overlay(image, max_side=520)

    assert overlay.mode == "RGBA"
    assert overlay.size == (520, 390)
    assert overlay.getchannel("A").getextrema()[1] > 0


def test_crop_watch_stages_returns_the_image_after_each_step(monkeypatch):
    import torch
    from src.detection import watch_cropper

    monkeypatch.setattr(
        watch_cropper,
        "detect_watch",
        lambda image: {
            "boxes": torch.tensor([[20.0, 20.0, 100.0, 100.0]]),
            "scores": torch.tensor([0.9]),
            "text_labels": ["watch"],
        },
    )
    image = make_crop(size=(120, 120), box=(50, 15, 70, 105))

    final, info, stages = watch_cropper.crop_watch_stages(image)

    assert set(stages) == {"crop", "aligned", "dial"}
    assert stages["dial"] is final
    assert info["crop_used"] is True
    assert "alignment" in info and "dial_crop" in info

    plain_final, plain_info = watch_cropper.crop_watch(image)
    assert plain_info == info and plain_final.size == final.size


def test_crop_watch_stages_is_empty_when_no_watch(monkeypatch):
    import torch
    from src.detection import watch_cropper

    monkeypatch.setattr(
        watch_cropper,
        "detect_watch",
        lambda image: {"boxes": torch.zeros((0, 4)), "scores": torch.zeros(0), "text_labels": []},
    )

    final, info, stages = watch_cropper.crop_watch_stages(make_crop())

    assert stages == {}
    assert info["reason"] == "no_watch_detected"


def test_dial_candidate_uses_height_for_box_bottom():
    from src.detection.watch_cropper import find_dial_candidate

    # Tall dial: with the old width-based bottom edge the box was too short.
    image = Image.new("RGB", (300, 300), color="white")
    ImageDraw.Draw(image).ellipse((100, 60, 200, 240), outline="black", width=6)

    candidate, info = find_dial_candidate(image)

    if candidate is not None:
        x1, y1, x2, y2 = candidate["box"]
        assert (y2 - y1) > (x2 - x1)
        assert "area_ratio" in info
