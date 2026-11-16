import numpy as np
from PIL import Image

from src.training.benchmark import (
    compute_metrics,
    confusion_matrix,
    expected_calibration_error,
    find_leakage,
    top_k_accuracy,
)

NAMES = ["a", "b", "c"]


def test_confusion_matrix_rows_are_true_classes():
    labels = np.array([0, 0, 1, 2])
    preds = np.array([0, 1, 1, 2])
    matrix = confusion_matrix(labels, preds, 3)
    assert matrix.tolist() == [[1, 1, 0], [0, 1, 0], [0, 0, 1]]


def test_top_k_accuracy_counts_second_choice():
    probs = np.array([[0.5, 0.4, 0.1], [0.1, 0.3, 0.6]])
    labels = np.array([1, 1])
    assert top_k_accuracy(probs, labels, 1) == 0.0
    assert top_k_accuracy(probs, labels, 2) == 1.0


def test_ece_is_zero_for_perfectly_calibrated_certain_predictions():
    probs = np.array([[1.0, 0.0], [0.0, 1.0]])
    assert expected_calibration_error(probs, np.array([0, 1])) == 0.0


def test_ece_is_high_for_confident_wrong_predictions():
    probs = np.array([[0.99, 0.01]] * 4)
    assert expected_calibration_error(probs, np.array([1, 1, 1, 1])) > 0.9


def test_compute_metrics_reports_expected_numbers():
    probs = np.array(
        [[0.9, 0.05, 0.05], [0.2, 0.7, 0.1], [0.1, 0.2, 0.7], [0.6, 0.3, 0.1]]
    )
    labels = np.array([0, 1, 2, 1])
    metrics = compute_metrics(probs, labels, NAMES)
    assert metrics["samples"] == 4
    assert metrics["top1_accuracy"] == 0.75
    assert metrics["top3_accuracy"] == 1.0
    assert metrics["most_confused"] == [{"true": "b", "predicted": "a", "count": 1}]
    by_class = {row["class"]: row for row in metrics["per_class"]}
    assert by_class["a"]["precision"] == 0.5 and by_class["a"]["recall"] == 1.0


def test_find_leakage_flags_near_duplicates(tmp_path):
    train, test = tmp_path / "train", tmp_path / "test"
    for folder in (train, test):
        (folder / "a").mkdir(parents=True)
    rng = np.random.default_rng(0)
    base = (rng.random((64, 64, 3)) * 255).astype("uint8")
    other = (rng.random((64, 64, 3)) * 255).astype("uint8")
    Image.fromarray(base).save(train / "a" / "x.png")
    Image.fromarray(base).save(test / "a" / "copy.png")      # exact duplicate
    Image.fromarray(other).save(test / "a" / "different.png")

    report = find_leakage(train, test)

    assert report["test_images"] == 2
    assert report["near_duplicates_in_train"] == 1
