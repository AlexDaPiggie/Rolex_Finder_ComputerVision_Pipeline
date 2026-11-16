"""
Build a single-file HTML page for reviewing likely label errors, and apply the decisions afterwards.

Usage:
    python -m src.training.label_review_page build                      # benchmarks/label_review.csv -> benchmarks/label_review.html
    # open the HTML in a browser, decide on each image, click "Export decisions" (downloads label_decisions.json)
    python -m src.training.label_review_page apply --decisions ~/Downloads/label_decisions.json --data-root data/grouped
    python -m src.training.label_review_page apply --decisions label_decisions.json --data-root data/grouped --dry-run

Decisions per image: keep (label is right), relabel (move to another class), remove (bad photo, moved to
<data-root>/_removed so it can be restored). Images are looked up by file name inside the class folder, so the
same decisions work on data/processed and data/grouped.
"""
import argparse
import base64
import csv
import json
import shutil
from io import BytesIO
from pathlib import Path

from PIL import Image

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Label review</title>
<style>
:root{--green:#0B2F23;--gold:#C9A348;--cream:#F6F2E8;--card:#FBFAF6;--line:rgba(11,47,35,.15);--bad:#b03a2e}
@media (prefers-color-scheme:dark){:root{--cream:#101a16;--card:#17241f;--green:#e9e2cc;--line:rgba(233,226,204,.18)}}
*{box-sizing:border-box}
body{margin:0;background:var(--cream);color:var(--green);font:16px/1.5 system-ui,sans-serif}
header{position:sticky;top:0;z-index:5;background:var(--cream);border-bottom:1px solid var(--line);padding:12px 20px;display:flex;flex-wrap:wrap;gap:12px;align-items:center}
header h1{font-size:18px;margin:0 auto 0 0}
.count{font-variant-numeric:tabular-nums}
button,select{font:inherit;border-radius:10px;border:1px solid var(--line);background:var(--card);color:inherit;padding:8px 14px;cursor:pointer}
button.primary{background:var(--gold);border-color:var(--gold);color:#032C22;font-weight:600}
button:focus-visible,select:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
main{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;padding:20px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;overflow:hidden;display:flex;flex-direction:column}
.card.decided{opacity:.6}
.card img{width:100%;aspect-ratio:1;object-fit:contain;background:#fff}
.body{padding:12px 14px;display:grid;gap:8px}
.meta{font-size:14px}
.tag{display:inline-block;padding:2px 9px;border-radius:99px;font-size:13px;font-weight:600;background:rgba(201,163,72,.25)}
.tag.model{background:rgba(176,58,46,.15)}
.actions{display:flex;flex-wrap:wrap;gap:6px}
.actions button{flex:1 1 auto;padding:8px 10px;font-size:14px}
.actions button.on{background:var(--green);color:var(--cream);border-color:var(--green)}
.row{display:flex;gap:6px}
.row select{flex:1}
.path{font-size:12px;opacity:.65;word-break:break-all}
.hide{display:none}
</style></head><body>
<header>
  <h1>Label review</h1>
  <span class="count" id="count"></span>
  <label><input type="checkbox" id="onlyOpen"> Only undecided</label>
  <button id="reset">Reset</button>
  <button class="primary" id="export">Export decisions</button>
</header>
<main id="grid"></main>
<script>
const ITEMS = __ITEMS__;
const CLASSES = __CLASSES__;
const KEY = "label_review_decisions_v1";
let decisions = {};
try { decisions = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) {}
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(decisions)); } catch (e) {} };
const nice = s => s.replaceAll("_", " ");
const grid = document.getElementById("grid");

function card(item, i) {
  const d = decisions[item.path];
  const el = document.createElement("article");
  el.className = "card" + (d ? " decided" : "");
  el.dataset.path = item.path;
  el.innerHTML = `
    <img src="${item.thumb}" alt="Image ${i + 1}" loading="lazy">
    <div class="body">
      <div class="meta">Labelled <span class="tag">${nice(item.given)}</span>
        model says <span class="tag model">${nice(item.model)}</span> (${item.confidence})</div>
      <div class="actions">
        <button data-a="keep">Label is right</button>
        <button data-a="relabel_model">Use model's label</button>
        <button data-a="remove">Remove photo</button>
      </div>
      <div class="row"><select aria-label="Other class"><option value="">Other class...</option>
        ${CLASSES.map(c => `<option value="${c}">${nice(c)}</option>`).join("")}</select></div>
      <div class="path">${item.split}: ${item.path}</div>
    </div>`;
  paint(el, item);
  el.querySelectorAll("[data-a]").forEach(b => b.onclick = () => decide(item, b.dataset.a, el));
  el.querySelector("select").onchange = e => { if (e.target.value) decide(item, "relabel", el, e.target.value); };
  return el;
}

function paint(el, item) {
  const d = decisions[item.path];
  el.classList.toggle("decided", !!d);
  el.querySelectorAll("[data-a]").forEach(b => b.classList.toggle("on", !!d && d.action === b.dataset.a));
  const sel = el.querySelector("select");
  sel.value = d && d.action === "relabel" ? d.new_label : "";
}

function decide(item, action, el, newLabel) {
  const current = decisions[item.path];
  if (current && current.action === action && action !== "relabel") { delete decisions[item.path]; }
  else if (action === "relabel_model") { decisions[item.path] = { action: "relabel", new_label: item.model }; }
  else if (action === "relabel") { decisions[item.path] = { action: "relabel", new_label: newLabel }; }
  else { decisions[item.path] = { action }; }
  save(); paint(el, item); update();
}

function update() {
  const done = ITEMS.filter(i => decisions[i.path]).length;
  document.getElementById("count").textContent = `${done} of ${ITEMS.length} decided`;
  const onlyOpen = document.getElementById("onlyOpen").checked;
  grid.querySelectorAll(".card").forEach(c => c.classList.toggle("hide", onlyOpen && !!decisions[c.dataset.path]));
}

ITEMS.forEach((item, i) => grid.appendChild(card(item, i)));
document.getElementById("onlyOpen").onchange = update;
document.getElementById("reset").onclick = () => {
  if (!confirm("Clear all decisions?")) return;
  decisions = {}; save(); grid.querySelectorAll(".card").forEach((c, i) => paint(c, ITEMS[i])); update();
};
document.getElementById("export").onclick = () => {
  const out = ITEMS.filter(i => decisions[i.path]).map(i => ({ path: i.path, split: i.split, given_label: i.given, ...decisions[i.path] }));
  const blob = new Blob([JSON.stringify(out, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = "label_decisions.json"; a.click();
};
update();
</script></body></html>
"""


def thumbnail_data_url(path: Path, size: int = 360) -> str:
    with Image.open(path) as image:
        image = image.convert("RGB")
        image.thumbnail((size, size))
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=80)
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def build(csv_path: Path, out_path: Path, class_mapping: Path):
    items = []
    with csv_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            path = Path(row["path"])
            if not path.exists():
                continue
            items.append(
                {
                    "path": row["path"],
                    "split": row["split"],
                    "given": row["given_label"],
                    "model": row["model_says"],
                    "confidence": row["confidence"],
                    "thumb": thumbnail_data_url(path),
                }
            )
    classes = list(json.loads(class_mapping.read_text(encoding="utf-8")))
    html = PAGE.replace("__ITEMS__", json.dumps(items)).replace("__CLASSES__", json.dumps(classes))
    out_path.write_text(html, encoding="utf-8")
    return len(items)


def find_image(data_root: Path, given_label: str, file_name: str) -> Path | None:
    for split in ("train", "val", "test"):
        candidate = data_root / split / given_label / file_name
        if candidate.exists():
            return candidate
    return None


def apply_decisions(decisions: list[dict], data_root: Path, dry_run: bool = False) -> dict:
    summary = {"relabelled": 0, "removed": 0, "kept": 0, "missing": 0}
    for decision in decisions:
        action = decision["action"]
        if action == "keep":
            summary["kept"] += 1
            continue
        file_name = Path(decision["path"]).name
        source = find_image(data_root, decision["given_label"], file_name)
        if source is None:
            summary["missing"] += 1
            continue
        split = source.parent.parent.name
        if action == "relabel":
            target = data_root / split / decision["new_label"] / file_name
            summary["relabelled"] += 1
        elif action == "remove":
            target = data_root / "_removed" / decision["given_label"] / file_name
            summary["removed"] += 1
        else:
            continue
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target))
    return summary


def main():
    parser = argparse.ArgumentParser(description="Label review page")
    sub = parser.add_subparsers(dest="command", required=True)

    b = sub.add_parser("build")
    b.add_argument("--csv", type=Path, default=Path("benchmarks/label_review.csv"))
    b.add_argument("--out", type=Path, default=Path("benchmarks/label_review.html"))
    b.add_argument("--class-mapping", type=Path, default=Path("data/processed/class_mapping.json"))

    a = sub.add_parser("apply")
    a.add_argument("--decisions", type=Path, required=True)
    a.add_argument("--data-root", type=Path, default=Path("data/grouped"))
    a.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()
    if args.command == "build":
        count = build(args.csv, args.out, args.class_mapping)
        print(f"{count} images -> {args.out}")
    else:
        decisions = json.loads(args.decisions.read_text(encoding="utf-8"))
        print(apply_decisions(decisions, args.data_root, args.dry_run))


if __name__ == "__main__":
    main()
