import json, math, os, re, subprocess, sys, urllib.parse, urllib.request, wave, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
WIDE = False
KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE = "onwK4e9ZLuTAKqWW03F9"
FD = "C:/Windows/Fonts/bahnschrift.ttf" if os.path.exists("C:/Windows/Fonts/bahnschrift.ttf") else "C:/Windows/Fonts/segoeuib.ttf"
FB = "C:/Windows/Fonts/segoeuib.ttf"
rng = np.random.default_rng(3)


def font(p, s):
    return ImageFont.truetype(p, s)


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode(errors="replace")[-600:])


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode().strip())


def tts(text, path):
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return
    try:
        body = {"text": text, "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.42, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True, "speed": 0.98}}
        req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128", data=json.dumps(body).encode(),
                                     headers={"xi-api-key": KEY, "Content-Type": "application/json", "Accept": "audio/mpeg"})
        open(path, "wb").write(urllib.request.urlopen(req, timeout=90).read())
    except Exception as e:
        import asyncio, edge_tts
        print("ElevenLabs failed, using free voice:", str(e)[:80])
        asyncio.run(edge_tts.Communicate(text, "en-US-AndrewNeural", rate="-4%").save(path))


def get_ai_image(prompt, path, seed):
    if os.path.exists(path):
        return
    q = urllib.parse.quote(prompt + ", cinematic, dramatic lighting, high detail, no text, no watermark")
    url = f"https://image.pollinations.ai/prompt/{q}?width=864&height=1632&nologo=true&model=flux&seed={seed}"
    for k in range(4):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read()
            if len(data) > 5000:
                tmp = path + ".raw.jpg"
                open(tmp, "wb").write(data)
                im = Image.open(tmp).convert("RGB")
                im = im.crop((0, 0, im.width, int(im.width * 16 / 9)))
                im = im.resize((1080, 1920), Image.LANCZOS)
                im.save(path, quality=92)
                return
        except Exception as e:
            print("image retry", k, str(e)[:60])
    raise RuntimeError("image failed: " + prompt[:40])


def _score(title):
    t = title.lower()
    bad = ["briefing", "conference", "interview", "live", "episode", " ep", "this week", "news", "press", "town hall", "panel", "webcast", "q&a", "talk", "lecture", "overview", "mission update", "podcast", "tour", "launch coverage", "countdown"]
    good = ["time-lapse", "timelapse", "time lapse", "views", "orbit", "flyover", "b-roll", "broll", "4k", "hd", "aurora", "night", "sunrise", "earth", "view from", "spacewalk", "footage", "raw"]
    sc = 0
    for g in good:
        if g in t:
            sc += 2
    for x in bad:
        if x in t:
            sc -= 5
    return sc


def get_nasa_video(query, path, skip=0):
    if os.path.exists(path):
        return
    s = json.loads(urllib.request.urlopen("https://images-api.nasa.gov/search?media_type=video&q=" + urllib.parse.quote(query), timeout=60).read().decode("utf-8"))
    items = sorted(s["collection"]["items"][:40], key=lambda it: -_score(it["data"][0]["title"]))[skip:skip + 12]
    for it in items:
        print("  nasa candidate:", it["data"][0]["title"][:70].encode("ascii", "replace").decode())
        href = it["href"].replace(" ", "%20")
        try:
            files = json.loads(urllib.request.urlopen(urllib.parse.quote(href, safe=":/%?=&@!,'()~"), timeout=60).read().decode("utf-8"))
        except Exception:
            continue
        mp4 = [f for f in files if f.lower().endswith(".mp4")]
        pick = next((f for f in mp4 if "~medium" in f), None) or next((f for f in mp4 if "~mobile" in f), None) or (mp4[0] if mp4 else None)
        if not pick:
            continue
        u = urllib.parse.quote(pick.replace("http://", "https://"), safe=":/%?=&@!,'()~")
        try:
            data = urllib.request.urlopen(u, timeout=180).read()
            open(path, "wb").write(data)
            return
        except Exception as e:
            print("nasa download retry", str(e)[:60])
    raise RuntimeError("no nasa video for " + query)


def _dl(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "FacelessVideoBot/1.0 (educational video project)"})
    open(path, "wb").write(urllib.request.urlopen(req, timeout=180).read())


def get_nasa_image(query, path, skip=0):
    if os.path.exists(path):
        return
    s = json.loads(urllib.request.urlopen("https://images-api.nasa.gov/search?media_type=image&q=" + urllib.parse.quote(query), timeout=60).read().decode("utf-8"))
    n = 0
    for it in s["collection"]["items"][:30]:
        href = it["href"].replace(" ", "%20")
        try:
            files = json.loads(urllib.request.urlopen(urllib.parse.quote(href, safe=":/%?=&@!,'()~"), timeout=60).read().decode("utf-8"))
        except Exception:
            continue
        jpg = [f for f in files if f.lower().endswith(".jpg") and "~thumb" not in f and "~small" not in f]
        pick = next((f for f in jpg if "~large" in f), None) or next((f for f in jpg if "~medium" in f), None) or (jpg[0] if jpg else None)
        if not pick:
            continue
        if n < skip:
            n += 1
            continue
        print("  nasa image:", it["data"][0]["title"][:70].encode("ascii", "replace").decode())
        tmp = path + ".dl"
        try:
            _dl(urllib.parse.quote(pick.replace("http://", "https://"), safe=":/%?=&@!,'()~"), tmp)
            im = Image.open(tmp).convert("RGB")
            if im.height < 700:
                continue
            im.save(path, quality=92)
            return
        except Exception as e:
            print("  nasa image retry", str(e)[:60])
    raise RuntimeError("no nasa image for " + query)


def get_commons_image(query, path, skip=0):
    if os.path.exists(path):
        return
    url = ("https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&gsrlimit=25&format=json&prop=imageinfo"
           "&iiprop=url|size|mime|extmetadata&iiurlwidth=2200&gsrsearch=" + urllib.parse.quote(query + " filetype:bitmap"))
    req = urllib.request.Request(url, headers={"User-Agent": "FacelessVideoBot/1.0 (educational video project)"})
    data = json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))
    pages = sorted(data.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0))
    n = 0
    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]
        lic = (ii.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "") or "").lower()
        if not ("public domain" in lic or lic.startswith("pd") or "cc0" in lic):
            continue
        if ii.get("mime") not in ("image/jpeg", "image/png") or (ii.get("height", 0) < 700):
            continue
        if n < skip:
            n += 1
            continue
        print("  commons image:", p["title"][:70].encode("ascii", "replace").decode(), "|", lic)
        tmp = path + ".dl"
        try:
            _dl(ii.get("thumburl") or ii["url"], tmp)
            Image.open(tmp).convert("RGB").save(path, quality=92)
            return
        except Exception as e:
            print("  commons retry", str(e)[:60])
    raise RuntimeError("no commons image for " + query)


CAP_CREDITS = 50000
COST_PER_IMAGE = 60


def _ledger():
    lp = os.path.join(HERE, "image_ledger.json")
    if os.path.exists(lp):
        return lp, json.load(open(lp, encoding="utf-8"))
    return lp, {"spent_estimate": 0, "images": 0}


def get_image_api(prompt, path):
    if os.path.exists(path):
        return
    key = os.environ.get("IMAGE_API_KEY", "")
    if not key:
        raise RuntimeError("no IMAGE_API_KEY")
    lp, led = _ledger()
    if led["spent_estimate"] + COST_PER_IMAGE > CAP_CREDITS:
        raise RuntimeError("Image API credit cap reached")
    w, h = (1440, 810) if WIDE else (810, 1440)
    body = {"prompt": prompt + ", cinematic, high detail, no text, no watermark, no logos", "width": w, "height": h}
    base = os.environ.get("IMAGE_API_URL", "https://example.com/v1/text-to-image")
    hdr = {os.environ.get("IMAGE_API_HEADER", "x-api-key"): key, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "FacelessVideoBot/1.0"}
    r = json.loads(urllib.request.urlopen(urllib.request.Request(base, data=json.dumps(body).encode(), headers=hdr), timeout=60).read().decode())
    led["spent_estimate"] += COST_PER_IMAGE
    led["images"] += 1
    json.dump(led, open(lp, "w", encoding="utf-8"))
    d = r.get("data", r)
    tid = d["task_id"]
    import time
    for _ in range(60):
        time.sleep(3)
        g = json.loads(urllib.request.urlopen(urllib.request.Request(base + "/" + tid, headers=hdr), timeout=60).read().decode())
        gd = g.get("data", g)
        st = gd.get("status")
        if st == "COMPLETED":
            urls = gd.get("generated") or []
            if urls:
                tmp = path + ".dl"
                _dl(urls[0], tmp)
                Image.open(tmp).convert("RGB").save(path, quality=92)
                return
            break
        if st in ("FAILED", "ERROR"):
            break
    raise RuntimeError("image API failed")


def overlay_png(sc, path):
    sf = 0.85 if WIDE else 1.0
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    scr = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(scr)
    for y in range(H):
        a = 0
        if y < H * 0.27:
            a = int(150 * (1 - y / (H * 0.27)))
        if y > H * 0.47:
            a = max(a, int(215 * min(1, (y - H * 0.47) / (H * 0.36))))
        sd.line([(0, y), (W, y)], fill=a)
    im.paste((0, 0, 0, 255), (0, 0), scr)
    d = ImageDraw.Draw(im)
    big, label, sub = sc.get("big", ""), sc.get("label", ""), sc.get("sub", "")
    accent = tuple(sc.get("color", (255, 210, 90)))
    if label:
        d.text((W // 2, int(H * 0.615)), label.upper(), font=font(FB, int(52 * sf)), fill=(190, 195, 220, 255), anchor="mm")
    if big:
        size = int((250 if len(big) < 7 else 190 if len(big) < 10 else 140) * sf)
        f = font(FD, size)
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).text((W // 2, int(H * 0.724)), big, font=f, fill=accent + (255,), anchor="mm")
        glow = glow.filter(ImageFilter.GaussianBlur(int(26 * sf)))
        im = Image.alpha_composite(im, glow)
        d = ImageDraw.Draw(im)
        d.text((W // 2, int(H * 0.724)), big, font=f, fill=(255, 255, 255, 255), anchor="mm")
    if sub:
        f = font(FB, int(58 * sf))
        words, lines, cur = sub.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= W - 160:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
        y = int(H * 0.839)
        for ln in lines[:3]:
            d.text((W // 2, y), ln, font=f, fill=(255, 255, 255, 255), anchor="mm")
            y += int(78 * sf)
    title = sc.get("title")
    if title:
        d = ImageDraw.Draw(im)
        d.text((W // 2, int(H * 0.12)), title, font=font(FB, int(64 * sf)), fill=(255, 255, 255, 255), anchor="mm")
    im.save(path)


def make_bed(total, path):
    sr = 44100
    n = int(sr * total)
    t = np.arange(n) / sr
    drone = 0.5 * np.sin(2 * np.pi * 55 * t) + 0.35 * np.sin(2 * np.pi * 82.4 * t + 0.6 * np.sin(2 * np.pi * 0.2 * t)) + 0.25 * np.sin(2 * np.pi * 110.3 * t)
    drone *= 0.55 + 0.45 * np.sin(2 * np.pi * 0.11 * t)
    out = 0.16 * drone
    out = out / (np.abs(out).max() + 1e-6) * 0.5
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((out * 32000).astype(np.int16).tobytes())


def main(spec_path):
    global W, H, WIDE
    spec = json.load(open(spec_path, encoding="utf-8"))
    if spec.get("format") == "wide":
        W, H, WIDE = 1920, 1080, True
    slug = spec["slug"]
    work = os.path.join(HERE, "work", slug)
    os.makedirs(work, exist_ok=True)
    clips = []
    for i, sc in enumerate(spec["scenes"]):
        mp3 = f"{work}/v{i}.mp3"
        tts(sc["vo"], mp3)
        d = dur(mp3) + 0.6
        ov = f"{work}/ov{i}.png"
        overlay_png(sc, ov)
        bg = sc["bg"]
        clip = f"{work}/s{i}.mp4"
        frames = int(d * FPS)
        if bg["type"] == "ai_api":
            try:
                get_image_api(bg["prompt"], f"{work}/bg{i}.jpg")
            except Exception as e:
                print("image API fallback to plain:", str(e)[:100])
                bg = {"type": "plain", "c1": bg.get("c1", (10, 8, 40)), "c2": bg.get("c2", (70, 20, 90))}
        if bg["type"] in ("ai", "nasa_img", "commons", "plain", "ai_api"):
            img = f"{work}/bg{i}.jpg"
            if bg["type"] == "ai_api":
                pass
            elif bg["type"] == "ai":
                get_ai_image(bg["prompt"], img, 100 + i)
            elif bg["type"] == "nasa_img":
                get_nasa_image(bg["query"], img, bg.get("skip", 0))
            elif bg["type"] == "commons":
                get_commons_image(bg["query"], img, bg.get("skip", 0))
            else:
                g = Image.new("RGB", (W, H))
                gd = ImageDraw.Draw(g)
                c1, c2 = bg.get("c1", (14, 8, 40)), bg.get("c2", (90, 20, 90))
                for y in range(H):
                    gd.line([(0, y), (W, y)], fill=tuple(int(c1[k] + (c2[k] - c1[k]) * y / H) for k in range(3)))
                import random
                rs = random.Random(hash(bg.get("c2", (0, 0, 0)).__repr__()) % 1000 + i)
                glow = Image.new("RGB", (W, H), (0, 0, 0))
                gdr = ImageDraw.Draw(glow)
                for _ in range(7):
                    cx, cy, r = rs.randint(0, W), rs.randint(0, int(H * 0.6)), rs.randint(int(W * 0.15), int(W * 0.35))
                    col = tuple(min(255, int(c * 2.2) + 40) for c in c2)
                    gdr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
                glow = glow.filter(ImageFilter.GaussianBlur(int(W * 0.12)))
                g = Image.blend(g, Image.composite(glow, g, Image.new("L", (W, H), 255)), 0.45)
                gd = ImageDraw.Draw(g)
                step = int(W * 0.09)
                for x in range(0, W, step):
                    gd.line([(x, 0), (x, int(H * 0.55))], fill=tuple(min(255, c + 22) for c in c2), width=1)
                for y in range(0, int(H * 0.55), step):
                    gd.line([(0, y), (W, y)], fill=tuple(min(255, c + 22) for c in c2), width=1)
                g.save(img, quality=92)
            inp = ["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.2f}", "-i", img]
            if WIDE:
                chain = "[0:v]scale='max(2400,trunc(iw*1200/ih/2)*2)':-2,crop=1920:1080:x='(iw-1920)*(0.1+0.8*t/%.2f)':y='(ih-1080)*0.5',fps=30,eq=saturation=1.08:brightness=-0.03,setsar=1[bg]" % d
            else:
                pan = "x='(iw-1080)*(0.15+0.7*t/%.2f)':y=0" % d
                chain = f"[0:v]scale='max(1200,trunc(iw*2160/ih/2)*2)':-2,crop=1080:1920:{pan},fps=30,eq=saturation=1.08:brightness=-0.03,setsar=1[bg]" if bg["type"] != "plain" else "[0:v]scale=1080:1920,fps=30,setsar=1[bg]"
        else:
            vid = f"{work}/nasa{i}.mp4"
            get_nasa_video(bg["query"], vid, bg.get("skip", 0))
            inp = ["-ss", str(bg.get("start", 8)), "-stream_loop", "-1", "-t", f"{d:.2f}", "-i", vid]
            chain = "[0:v]scale=-2:1920,crop=1080:1920,fps=30,eq=brightness=-0.04:saturation=1.1,setsar=1[bg]"
        fc = f"{chain};[1:v]format=rgba,fade=t=in:st=0.25:d=0.5:alpha=1[ov];[bg][ov]overlay=0:0:format=auto,format=yuv420p,fade=t=in:st=0:d=0.25,fade=t=out:st={d-0.25:.2f}:d=0.25[v];[2:a]apad=whole_dur={d:.2f}[a]"
        run(["ffmpeg", "-y", *inp, "-loop", "1", "-t", f"{d:.2f}", "-i", ov, "-i", mp3, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-r", str(FPS),
             "-c:v", "libx264", "-preset", "medium", "-b:v", "2500k" if WIDE else "1800k", "-maxrate", "3000k" if WIDE else "2200k", "-bufsize", "4000k", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-t", f"{d:.2f}", clip])
        clips.append(clip)
        print("scene", i, "done", round(d, 1))
    open(f"{work}/list.txt", "w").write("".join(f"file '{c.replace(os.sep, '/')}'\n" for c in clips))
    joined = f"{work}/joined.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{work}/list.txt", "-c", "copy", joined])
    total = dur(joined)
    bed = f"{work}/bed.wav"
    make_bed(total, bed)
    out = os.path.join(HERE, f"{slug}.mp4")
    run(["ffmpeg", "-y", "-i", joined, "-i", bed, "-filter_complex", "[0:a][1:a]amix=inputs=2:weights=1 0.35:normalize=0,alimiter=limit=0.95[a]", "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out])
    print(out, round(dur(out), 1), "sec", round(os.path.getsize(out) / 1e6, 1), "MB")


main(sys.argv[1])
