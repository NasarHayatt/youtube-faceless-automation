import json, os, sys, threading, subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state.json")
LOCK = threading.Lock()
JOB = {"running": False}


def load():
    if os.path.exists(STATE):
        return json.load(open(STATE, encoding="utf-8"))
    return {"rendered": {}, "uploaded": []}


def save(st):
    json.dump(st, open(STATE, "w", encoding="utf-8"), indent=1)


def render_job(n):
    JOB["running"] = True
    try:
        subprocess.run([sys.executable, "-I", os.path.join(HERE, "run_daily.py"), str(n)], cwd=HERE, capture_output=True)
    finally:
        JOB["running"] = False


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == "/health":
            return self.send_json({"ok": True, "rendering": JOB["running"]})
        if self.path == "/pending":
            with LOCK:
                st = load()
            items = [v for k, v in st["rendered"].items() if k not in st["uploaded"] and os.path.exists(v["file"])]
            wide = [v for v in items if v.get("kind") == "video"]
            short = [v for v in items if v.get("kind") != "video"]
            mixed = []
            while wide or short:
                if wide:
                    mixed.append(wide.pop(0))
                if short:
                    mixed.append(short.pop(0))
            items = mixed
            return self.send_json({"items": items[:4], "queue_dir_remaining": len([f for f in os.listdir(os.path.join(HERE, "queue")) if f.endswith(".json")]) - len(st["rendered"])})
        if self.path.startswith("/file/"):
            slug = os.path.basename(self.path[6:])
            with LOCK:
                st = load()
            it = st["rendered"].get(slug)
            if not it or not os.path.exists(it["file"]):
                return self.send_json({"error": "not found"}, 404)
            size = os.path.getsize(it["file"])
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Length", str(size))
            self.end_headers()
            with open(it["file"], "rb") as f:
                while True:
                    chunk = f.read(1 << 20)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
            return
        self.send_json({"error": "unknown"}, 404)

    def do_POST(self):
        if self.path.startswith("/uploaded/"):
            slug = os.path.basename(self.path[10:])
            with LOCK:
                st = load()
                if slug in st["rendered"] and slug not in st["uploaded"]:
                    st["uploaded"].append(slug)
                    save(st)
            return self.send_json({"ok": True})
        if self.path == "/queue":
            ln = int(self.headers.get("Content-Length", "0"))
            try:
                spec = json.loads(self.rfile.read(ln).decode("utf-8"))
                slug = "".join(c for c in spec["slug"] if c.isalnum() or c in "-_")[:80]
                assert slug and len(spec["scenes"]) >= 3 and spec.get("title") and spec.get("description")
                spec["slug"] = slug
                path = os.path.join(HERE, "queue", slug + ".json")
                if os.path.exists(path):
                    return self.send_json({"ok": False, "reason": "exists"})
                json.dump(spec, open(path, "w", encoding="utf-8"), indent=1)
                return self.send_json({"ok": True, "slug": slug})
            except Exception as e:
                return self.send_json({"ok": False, "error": str(e)[:200]}, 400)
        if self.path.startswith("/render"):
            n = 10
            if "n=" in self.path:
                n = int(self.path.split("n=")[1].split("&")[0])
            if JOB["running"]:
                return self.send_json({"ok": False, "reason": "already rendering"})
            threading.Thread(target=render_job, args=(n,), daemon=True).start()
            return self.send_json({"ok": True, "started": n})
        self.send_json({"error": "unknown"}, 404)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8300), H).serve_forever()
