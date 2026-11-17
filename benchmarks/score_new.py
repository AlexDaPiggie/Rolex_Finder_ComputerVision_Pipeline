import json, sys, time, requests, os
from collections import defaultdict
URL = "https://alexdapiggie--rolex-watch-recognizer-rolexwatchapi-web.modal.run/predict"
files = json.load(open("benchmarks/new_keep.json"))
rows = []
for i, f in enumerate(files):
    fam = f.split("/")[-2]
    for attempt in range(3):
        try:
            r = requests.post(URL, files={"file": (os.path.basename(f), open(f, "rb"), "image/jpeg")}, timeout=180)
            if r.status_code == 200: break
        except Exception as e: r = None
        time.sleep(5)
    if r is None or r.status_code != 200:
        rows.append({"file": f, "family": fam, "error": True}); continue
    j = r.json()
    rows.append({"file": f, "family": fam, "pred": j.get("predicted_class"), "conf": j.get("confidence"), "status": j.get("status")})
    if i % 20 == 0: print(i, flush=True)
json.dump(rows, open("benchmarks/new_scores.json", "w"), indent=0)
ok = [r for r in rows if "pred" in r]
print("n", len(rows), "answered", len(ok))
st = defaultdict(lambda: [0, 0])
for r in ok:
    st[r["family"]][0] += 1; st[r["family"]][1] += r["pred"] == r["family"]
tot = sum(v[1] for v in st.values()); print("top1", tot, "/", len(ok), round(tot/len(ok), 3))
for k, v in sorted(st.items()): print(k, v[1], "/", v[0])
