import numpy as np
from PIL import Image

from src.training.dataset import RandomGlare, RandomJpeg, build_transforms
from src.training.find_label_errors import flag_disagreements
from src.training.group_split import group_key, split_groups
from src.training.prepare_crops import outcome_of, process_image, run
from src.training.train import class_weights


def test_group_key_ignores_hash_and_size_suffix():
    a = "https://cdn.x.com/p/rolex-datejust-steel-watch-179383-49067_f63a6_sm.jpg"
    b = "https://cdn.x.com/p/rolex-datejust-steel-watch-179383-49067_9b2c1_sm.jpg"
    assert group_key(a, "id1") == group_key(b, "id2")
    assert group_key("https://cdn.x.com/p/a.jpg", "fallback") == "fallback"


def test_split_groups_keeps_a_group_in_one_split_and_covers_all_splits():
    groups = [f"g{i}" for i in range(50)]
    assignment = split_groups(groups * 2)  # duplicates are the same group
    assert set(assignment) == set(groups)
    assert set(assignment.values()) == {"train", "val", "test"}
    assert list(assignment.values()).count("train") == 40


def test_class_weights_favour_rare_classes_and_average_one():
    weights = class_weights([1000, 100, 10])
    assert weights[2] > weights[1] > weights[0]
    assert abs(weights.mean() - 1.0) < 1e-9


def test_random_jpeg_changes_pixels_but_not_size():
    image = Image.fromarray((np.random.default_rng(0).random((64, 64, 3)) * 255).astype("uint8"))
    out = RandomJpeg(quality=(5, 10), p=1.0)(image)
    assert out.size == image.size
    assert np.asarray(out).tolist() != np.asarray(image).tolist()


def test_train_transform_outputs_tensor_of_expected_shape():
    image = Image.new("RGB", (300, 200), "gray")
    assert tuple(build_transforms(train=True)(image).shape) == (3, 224, 224)


def test_flag_disagreements_only_flags_confident_mismatches():
    probs = np.array([[0.95, 0.05], [0.4, 0.6], [0.05, 0.95]])
    assert flag_disagreements(0, probs, 0.9) == [2]


def test_outcome_labels():
    assert outcome_of({"reason": "no_watch_detected"}) == "no_watch_detected"
    assert outcome_of({"crop_used": True, "dial_crop": {"dial_crop_used": True}}) == "cropped_with_dial"
    assert outcome_of({"crop_used": True, "dial_crop": {"dial_crop_used": False}}) == "cropped_no_dial"


def test_prepare_crops_writes_cropped_image_and_resumes(tmp_path):
    src = tmp_path / "in" / "train" / "datejust"
    src.mkdir(parents=True)
    Image.new("RGB", (100, 100), "white").save(src / "a.jpg")

    def fake_crop(image):
        return image.crop((10, 10, 60, 60)), {"crop_used": True, "dial_crop": {"dial_crop_used": True}}, {}

    out = tmp_path / "out"
    counts = run(tmp_path / "in", out, fake_crop, splits=("train",))
    assert counts["train"]["cropped_with_dial"] == 1
    assert Image.open(out / "train" / "datejust" / "a.jpg").size == (50, 50)

    again = run(tmp_path / "in", out, fake_crop, splits=("train",))
    assert again["train"]["already_done"] == 1


def test_prepare_crops_can_skip_images_with_no_watch(tmp_path):
    source = tmp_path / "a.jpg"
    Image.new("RGB", (50, 50), "white").save(source)
    target = tmp_path / "out" / "a.jpg"
    outcome = process_image(source, target, lambda im: (im, {"reason": "no_watch_detected"}, {}), on_miss="skip")
    assert outcome == "no_watch_detected" and not target.exists()


def test_random_glare_brightens_but_keeps_size():
    image = Image.new("RGB", (80, 60), (40, 40, 40))
    out = RandomGlare(p=1.0, strength=(0.8, 0.8))(image)
    assert out.size == image.size
    assert np.asarray(out).mean() > np.asarray(image).mean()
