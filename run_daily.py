import json, os, subprocess, sys, datetime, glob

HERE = os.path.dirname(os.path.abspath(__file__))
Q = os.path.join(HERE, "queue")
OUT = os.path.join(HERE, "out")
STATE = os.path.join(HERE, "state.json")
os.makedirs(OUT, exist_ok=True)


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE, encoding="utf-8"))
    return {"rendered": {}, "uploaded": []}


def main(n):
    st = load_state()
    specs = sorted(glob.glob(os.path.join(Q, "*.json")))
    todo = []
    for p in specs:
        d = json.load(open(p, encoding="utf-8"))
        if d["slug"] in st["rendered"]:
            continue
        todo.append((p, d))
    wide = [x for x in todo if x[1].get("kind") == "video"]
    short = [x for x in todo if x[1].get("kind") != "video"]
    mixed = []
    while (wide or short) and len(mixed) < n:
        if wide:
            mixed.append(wide.pop(0))
        if short and len(mixed) < n:
            mixed.append(short.pop(0))
    manifest = []
    for p, d in mixed:
        slug = d["slug"]
        r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "doc_short.py"), p], capture_output=True, text=True, cwd=HERE)
        mp4 = os.path.join(HERE, slug + ".mp4")
        if r.returncode != 0 or not os.path.exists(mp4):
            print("FAILED", slug, r.stderr[-300:], file=sys.stderr)
            continue
        dest = os.path.join(OUT, slug + ".mp4")
        os.replace(mp4, dest)
        item = {"slug": slug, "title": d["title"][:100], "description": d["description"], "file": dest.replace(os.sep, "/"), "kind": d.get("kind", "short"), "made_for_kids": bool(d.get("made_for_kids", False))}
        st["rendered"][slug] = item
        manifest.append(item)
        json.dump(st, open(STATE, "w", encoding="utf-8"), indent=1)
    remaining = len(todo) - len(manifest)
    print(json.dumps({"date": datetime.date.today().isoformat(), "items": manifest, "queue_remaining": remaining}))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
