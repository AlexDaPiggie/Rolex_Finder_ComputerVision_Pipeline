import json

from PIL import Image

from src.training.label_review_page import apply_decisions, build, find_image


def make_tree(tmp_path):
    root = tmp_path / "grouped"
    for split, label, name in [("train", "datejust", "a.jpg"), ("val", "datejust", "b.jpg"), ("train", "datejust", "c.jpg")]:
        folder = root / split / label
        folder.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (40, 40), "white").save(folder / name)
    return root


def test_apply_relabel_remove_keep_and_missing(tmp_path):
    root = make_tree(tmp_path)
    decisions = [
        {"path": "x/a.jpg", "given_label": "datejust", "action": "relabel", "new_label": "president"},
        {"path": "x/b.jpg", "given_label": "datejust", "action": "remove"},
        {"path": "x/c.jpg", "given_label": "datejust", "action": "keep"},
        {"path": "x/zzz.jpg", "given_label": "datejust", "action": "remove"},
    ]
    summary = apply_decisions(decisions, root)
    assert summary == {"relabelled": 1, "removed": 1, "kept": 1, "missing": 1}
    assert (root / "train" / "president" / "a.jpg").exists()
    assert (root / "_removed" / "datejust" / "b.jpg").exists()
    assert (root / "train" / "datejust" / "c.jpg").exists()


def test_dry_run_changes_nothing(tmp_path):
    root = make_tree(tmp_path)
    apply_decisions([{"path": "a.jpg", "given_label": "datejust", "action": "remove"}], root, dry_run=True)
    assert find_image(root, "datejust", "a.jpg") is not None


def test_build_page_embeds_items(tmp_path):
    img = tmp_path / "one.jpg"
    Image.new("RGB", (30, 30), "red").save(img)
    csv_path = tmp_path / "r.csv"
    csv_path.write_text(
        "split,path,given_label,model_says,confidence\n" f"train,{img.as_posix()},datejust,president,0.99\n",
        encoding="utf-8",
    )
    mapping = tmp_path / "m.json"
    mapping.write_text(json.dumps({"datejust": 0, "president": 1}), encoding="utf-8")
    out = tmp_path / "page.html"
    assert build(csv_path, out, mapping) == 1
    html = out.read_text(encoding="utf-8")
    assert "data:image/jpeg;base64," in html and "__ITEMS__" not in html
