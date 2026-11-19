"""Máquina de clips virales: video largo -> clips verticales 9:16 con subtítulos animados.

Uso:
  python3 clip.py "https://www.youtube.com/watch?v=..."       # enlace directo
  python3 clip.py "https://www.twitch.tv/videos/..." --tramo 01:00:00-01:30:00
  python3 clip.py VIDEO.mp4                      # 5 clips, idioma auto
  python3 clip.py VIDEO.mp4 -n 8 --lang es --min 20 --max 50
  python3 clip.py VIDEO.mp4 --layout blur        # video completo con fondo difuminado (gameplay)
  python3 clip.py VIDEO.mp4 --at 01:23:10-01:23:45   # cortar un momento concreto

Salida: output/<nombre>/clip_XX.mp4, clip_XX.jpg (portada) y CLIPS.txt (títulos, hashtags, transcripción).
Usa solo contenido propio o con permiso del creador.
"""
import os, sys, re, json, math, argparse, subprocess, unicodedata
import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "models")
FONTS = os.path.join(os.path.dirname(HERE), "assets", "fonts")
W, H = 1080, 1920

HYPE = [
    # español
    "no mames", "no manches", "qué", "que pedo", "wey", "güey", "dios mío", "dios mio", "no puede ser", "vamos",
    "increíble", "loco", "locura", "mira", "chat", "jaja", "jajaja", "ay", "hermano", "bro", "brutal", "no way",
    "cállate", "qué onda", "ándale", "órale", "a huevo", "neta", "mano", "tío", "hostia", "joder", "flipa",
    # inglés
    "what", "oh my god", "omg", "let's go", "lets go", "bro", "yo", "chat", "insane", "crazy", "no way", "why",
    "dude", "holy", "hahaha", "haha", "wait", "stop", "run", "help", "speed", "w", "goat",
]

STOP = set("""el la los las un una unos unas de del al a y o que en es por para con no se lo le les me te mi tu su
ya pero como más mas muy eso esto esta este ese esa hay fue ser son está estoy the a an and or of to in is it i you
he she we they that this was for on with be are my your so just like oh yeah okay ok""".split())


def run(cmd):
    subprocess.run(cmd, check=True)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate:format=duration", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    s = j["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return int(s["width"]), int(s["height"]), float(num) / float(den), float(j["format"]["duration"])


def ts(t):
    return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def parse_ts(s):
    p = [float(x) for x in s.split(":")]
    return sum(v * 60 ** i for i, v in enumerate(reversed(p)))


# ------------------------------------------------------------------ audio + ASR
def extract_audio(video, wav):
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-ac", "1", "-ar", "16000", "-vn", wav])


def vad_segments(x, sr, max_len=12.0):
    import sherpa_onnx
    cfg = sherpa_onnx.VadModelConfig()
    cfg.silero_vad.model = os.path.join(MODELS, "silero_vad.onnx")
    cfg.silero_vad.min_silence_duration = 0.25
    cfg.silero_vad.min_speech_duration = 0.25
    cfg.silero_vad.max_speech_duration = max_len
    cfg.sample_rate = sr
    vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=120)
    win = cfg.silero_vad.window_size
    segs = []
    for i in range(0, len(x), win):
        vad.accept_waveform(x[i:i + win])
        while not vad.empty():
            seg = vad.front
            segs.append((seg.start / sr, seg.start / sr + len(seg.samples) / sr))
            vad.pop()
    vad.flush()
    while not vad.empty():
        seg = vad.front
        segs.append((seg.start / sr, seg.start / sr + len(seg.samples) / sr))
        vad.pop()
    return segs


_rec = {}


def recognizer(lang):
    import sherpa_onnx
    if lang not in _rec:
        m = os.path.join(MODELS, "sherpa-onnx-whisper-small", "small-")
        _rec[lang] = sherpa_onnx.OfflineRecognizer.from_whisper(
            encoder=m + "encoder.int8.onnx", decoder=m + "decoder.int8.onnx", tokens=m + "tokens.txt",
            language=lang, num_threads=os.cpu_count() or 4)
    return _rec[lang]


def transcribe(x, sr, segs, lang, cache):
    if os.path.exists(cache):
        return json.load(open(cache))
    rec = recognizer(lang)
    words = []
    for k, (a, b) in enumerate(segs):
        s = rec.create_stream()
        s.accept_waveform(sr, x[int(a * sr):int(b * sr)])
        rec.decode_stream(s)
        text = s.result.text.strip()
        toks = text.split()
        if not toks:
            continue
        # tiempos aproximados por palabra, proporcionales a su longitud
        tot = sum(len(t) + 2 for t in toks)
        t = a
        for j, tk in enumerate(toks):
            d = (b - a) * (len(tk) + 2) / tot
            words.append({"w": tk, "s": round(t, 3), "e": round(t + d, 3), "first": j == 0})
            t += d
        if k % 25 == 0:
            print(f"  transcribiendo… {ts(a)}", flush=True)
    json.dump(words, open(cache, "w"), ensure_ascii=False)
    return words


# ------------------------------------------------------------------ highlight scoring
def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def loudness(x, sr, hop=0.25):
    n = int(sr * hop)
    m = len(x) // n
    rms = np.sqrt(np.mean(x[:m * n].reshape(m, n) ** 2, axis=1) + 1e-9)
    db = 20 * np.log10(rms)
    z = (db - np.median(db)) / (np.std(db) + 1e-6)
    return z, hop


def pick_clips(words, z, hop, dur, n, lo, hi):
    hype_norm = [norm(h) for h in HYPE]
    # empezar solo al inicio de frase: tras una pausa o tras punto/exclamación
    starts = []
    for i, w in enumerate(words):
        if w.get("first") or i == 0 or re.search(r"[.!?…]$", words[i - 1]["w"]):
            starts.append(max(0.0, w["s"] - 0.15))
    starts = sorted(set(round(s_, 2) for s_ in starts)) or [0.0]
    cands = []
    for st in starts:
        for L in (lo, (lo + hi) / 2, hi):
            en = min(dur, st + L)
            if en - st < lo * 0.8:
                continue
            ws = [w for w in words if st <= w["s"] < en]
            if len(ws) < 6:
                continue
            # cerrar en final de frase si hay una cerca
            for w in reversed(ws):
                if re.search(r"[.!?…]$", w["w"]) and w["e"] > st + lo * 0.8:
                    en = w["e"] + 0.3; break
            a, b = int(st / hop), int(en / hop)
            zz = z[a:b]
            if len(zz) == 0:
                continue
            text = norm(" ".join(w["w"] for w in ws))
            hype = sum(text.count(h) for h in hype_norm if len(h) > 2) + sum(1 for w in ws if norm(w["w"]).strip("¡!¿?.,") in hype_norm)
            excl = sum(w["w"].count("!") + w["w"].count("?") for w in ws)
            peaks = float(np.mean(np.sort(zz)[-max(1, len(zz) // 5):]))
            hook = float(np.max(z[a:a + int(3 / hop)])) if a < len(z) else 0
            density = len(ws) / (en - st)
            score = 1.6 * peaks + 0.8 * hook + 0.35 * hype + 0.25 * excl + 0.3 * min(density, 4)
            cands.append((score, st, en))
    cands.sort(reverse=True)
    chosen = []
    for sc, st, en in cands:
        if all(en <= c[1] - 2 or st >= c[2] + 2 for c in chosen):
            chosen.append((sc, st, en))
        if len(chosen) >= n:
            break
    return sorted(chosen, key=lambda c: c[1])


def hot_zones(z, hop, dur, k=30, win=80.0):
    """Zonas más intensas repartidas por todo el directo: la mejor ventana de cada tramo."""
    n = int(win / hop)
    if len(z) <= n:
        return [(0.0, dur)]
    # volumen relativo al contexto local (5 min) para no favorecer partes con más ruido de fondo
    ctx = int(300 / hop)
    pad = np.pad(z, (ctx, ctx), mode="edge")
    base = np.convolve(pad, np.ones(2 * ctx + 1) / (2 * ctx + 1), mode="valid")
    zr = z - base
    block = len(zr) / k
    zones = []
    for j in range(k):
        a, b = int(j * block), int((j + 1) * block) - n
        best, bi = -1e9, a
        for i in range(a, max(a + 1, b), int(5 / hop)):
            v = float(np.mean(np.sort(zr[i:i + n])[-n // 5:]))
            if v > best:
                best, bi = v, i
        zones.append((bi * hop, bi * hop + win))
    return zones


# ------------------------------------------------------------------ framing
def face_track(video, st, en, iw, ih, fps):
    """Devuelve (modo, datos). modo: 'face' (cara grande -> recorte que la sigue),
    'split' (facecam pequeña sobre gameplay -> cámara arriba, juego abajo) o None."""
    import cv2
    yunet = os.path.join(MODELS, "yunet.onnx")
    sc = 2 if ih >= 720 else 1
    if os.path.exists(yunet):
        fd = cv2.FaceDetectorYN.create(yunet, "", (iw // sc, ih // sc), 0.6, 0.3, 50)
        def detect(img):
            _, f = fd.detect(img)
            return [] if f is None else [tuple(r[:4]) for r in f]
    else:
        cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        def detect(img):
            return list(cas.detectMultiScale(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 1.1, 6, minSize=(24, 24)))
    cap = cv2.VideoCapture(video)
    det, times, allf = [], [], []
    t = st
    while t < en:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, fr = cap.read()
        if not ok:
            break
        faces = detect(cv2.resize(fr, (iw // sc, ih // sc)))
        allf.append([((x + w / 2) * sc, (y + h / 2) * sc, h * sc) for x, y, w, h in faces])
        if len(faces):
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            det.append(((x + w / 2) * sc, (y + h / 2) * sc, h * sc)); times.append(t)
        t += 0.5
    cap.release()
    nfr = max(1, len(allf))
    # 1) facecam: una cara pequeña que se repite en la misma posición cerca de un borde lateral
    flat = [f for fs in allf for f in fs]
    best, bc = None, 0
    for f in flat:
        c = sum(1 for fs in allf if any(abs(g[0] - f[0]) < 0.04 * iw and abs(g[1] - f[1]) < 0.04 * ih for g in fs))
        if c > bc:
            best, bc = f, c
    if best is not None and bc / nfr >= 0.4 and best[2] < 0.16 * ih and (best[0] > iw * 0.62 or best[0] < iw * 0.38):
        near = np.array([f for f in flat if abs(f[0] - best[0]) < 0.04 * iw and abs(f[1] - best[1]) < 0.04 * ih])
        cx, cy, fh = (float(np.median(near[:, k])) for k in range(3))
        bh = min(ih * 0.45, fh * 6.2); bw = min(iw, bh * 16 / 9)
        x0 = iw - bw if cx > iw / 2 else 0
        y0 = 0 if cy < ih / 2 else ih - bh
        box = refine_box(video, (st + en) / 2, iw, ih, cx, cy, fh, int(x0), int(y0), int(bw), int(bh))
        return "split", box
    # 2) cámara a pantalla completa: cara grande detectada en buena parte del clip
    big = [(tt, dd) for tt, dd in zip(times, det) if dd[2] >= 0.16 * ih]
    if len(big) < 0.4 * nfr:
        return None, None
    times = [tt for tt, _ in big]; d = np.array([dd for _, dd in big])
    grid = np.arange(st, en, 1 / fps)
    cx = np.interp(grid, times, d[:, 0])
    k = int(fps * 1.2)
    cx = np.convolve(np.pad(cx, (k, k), mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), mode="valid")
    return "face", cx


def refine_box(video, t, iw, ih, cx, cy, fh, x0, y0, bw, bh):
    """Ajusta el recuadro de la facecam buscando su marco (bordes fuertes y rectos)."""
    import cv2
    cap = cv2.VideoCapture(video); cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, fr = cap.read(); cap.release()
    if not ok:
        return (x0, y0, bw, bh)
    g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    gx = np.abs(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3))
    gy = np.abs(cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3))
    right = cx > iw / 2; top = cy < ih / 2
    # borde vertical interior (el lado hacia el centro de la pantalla)
    ya, yb = (0, int(cy + 2.5 * fh)) if top else (int(cy - 2.5 * fh), ih)
    ya, yb = max(0, ya), min(ih, yb)
    if right:
        xs = np.arange(int(max(0, cx - 7 * fh)), int(cx - 1.2 * fh))
    else:
        xs = np.arange(int(cx + 1.2 * fh), int(min(iw, cx + 7 * fh)))
    if len(xs) > 5:
        prof = gx[ya:yb, xs].mean(axis=0)
        xe = int(xs[int(np.argmax(prof))])
        if prof.max() > 3 * np.median(prof):
            if right: x0, bw = xe, iw - xe
            else: x0, bw = 0, xe
    # borde horizontal interior
    xa, xb = x0, x0 + bw
    ys = np.arange(int(cy + 1.2 * fh), int(min(ih, cy + 5 * fh))) if top else np.arange(int(max(0, cy - 5 * fh)), int(cy - 1.2 * fh))
    if len(ys) > 5:
        prof = gy[ys, xa:xb].mean(axis=1)
        ye = int(ys[int(np.argmax(prof))])
        if prof.max() > 3 * np.median(prof):
            if top: y0, bh = 0, ye
            else: y0, bh = ye, ih - ye
    return (int(x0), int(y0), int(max(32, bw)) // 2 * 2, int(max(32, bh)) // 2 * 2)


def render_clip(video, st, en, out, iw, ih, fps, layout, ass_path, hook_text=None):
    import cv2
    tmp = out + ".noaudio.mp4"
    cw = int(ih * 9 / 16) // 2 * 2
    cx, mode, box = None, None, None
    if layout in ("auto", "split") and iw > ih:
        mode, data = face_track(video, st, en, iw, ih, fps)
        if mode == "face" and layout == "auto":
            cx = data
        elif mode == "split":
            box = data
    use_crop = cx is not None or (layout == "crop" and iw > ih)
    if layout == "crop" and cx is None:
        cx = np.full(int((en - st) * fps) + 2, iw / 2)
    cap = cv2.VideoCapture(video)
    cap.set(cv2.CAP_PROP_POS_MSEC, st * 1000)
    step = 2 if fps > 40 else 1  # salida a ~30 fps: mitad de peso, igual de fluido en móvil
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                            "-r", f"{fps / step:.3f}", "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                            "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    nfr = int((en - st) * fps)
    for i in range(nfr):
        ok, fr = cap.read()
        if not ok:
            break
        if i % step:
            continue
        if iw <= ih:  # ya es vertical
            canvas = cv2.resize(fr, (W, int(ih * W / iw)))
            canvas = canvas[(canvas.shape[0] - H) // 2:][:H] if canvas.shape[0] >= H else cv2.copyMakeBorder(
                canvas, (H - canvas.shape[0]) // 2, H - canvas.shape[0] - (H - canvas.shape[0]) // 2, 0, 0, cv2.BORDER_CONSTANT)
        elif box is not None:  # facecam arriba, juego abajo
            x0, y0, bw, bh = box
            top_h = int(W * bh / bw) // 2 * 2
            top = cv2.resize(fr[y0:y0 + bh, x0:x0 + bw], (W, top_h))
            bot_h = H - top_h
            gw = int(ih * W / bot_h)
            gx = (iw - gw) // 2
            bot = cv2.resize(fr[:, gx:gx + gw], (W, bot_h))
            canvas = np.vstack([top, bot])
            canvas[top_h - 4:top_h + 4] = (0, 229, 255)
        elif use_crop:
            c = int(np.clip(cx[min(i, len(cx) - 1)] - cw / 2, 0, iw - cw))
            canvas = cv2.resize(fr[:, c:c + cw], (W, H), interpolation=cv2.INTER_LINEAR)
        else:  # blur: video entero en el centro, fondo ampliado y difuminado
            bg = cv2.resize(fr[:, (iw - cw) // 2:(iw + cw) // 2], (W // 8, H // 8))
            bg = cv2.GaussianBlur(bg, (0, 0), 6)
            bg = cv2.resize(bg, (W, H)) * 0.55
            fg_h = int(ih * W / iw)
            fg = cv2.resize(fr, (W, fg_h))
            canvas = bg.astype(np.uint8)
            y0 = (H - fg_h) // 2 - 120
            canvas[y0:y0 + fg_h] = fg
        enc.stdin.write(canvas.tobytes())
    enc.stdin.close(); enc.wait(); cap.release()
    fontsdir = FONTS.replace(":", r"\:")
    vf = f"ass={ass_path}:fontsdir={fontsdir}"
    run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-ss", f"{st:.3f}", "-t", f"{en - st:.3f}", "-i", video,
         "-map", "0:v", "-map", "1:a", "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-c:a", "aac", "-b:a", "160k", "-af", "loudnorm=I=-14:TP=-1.5", "-shortest", "-movflags", "+faststart", out])
    os.remove(tmp)


# ------------------------------------------------------------------ subtítulos animados (ASS)
def ass_time(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def make_ass(words, st, en, path, hook_text=None):
    ws = [w for w in words if st <= w["s"] < en]
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Anton,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,9,4,2,60,60,560,1
Style: Hook,Anton,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,3,18,0,8,60,60,230,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    # grupos de 1-3 palabras (cortes en puntuación)
    groups, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) >= 3 or re.search(r"[.,!?…]$", w["w"]) or sum(len(x["w"]) for x in cur) > 14:
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    for g in groups:
        for j, w in enumerate(g):
            a = w["s"] - st
            b = (g[j + 1]["s"] if j + 1 < len(g) else g[-1]["e"]) - st
            parts = []
            for k, x in enumerate(g):
                txt = x["w"].upper().replace("{", "").replace("}", "")
                if k == j:
                    parts.append(r"{\c&H00E5FF&\fscx112\fscy112}" + txt + r"{\c&HFFFFFF&\fscx100\fscy100}")
                else:
                    parts.append(txt)
            pop = r"{\fad(40,0)\t(0,90,\fscx108\fscy108)\t(90,160,\fscx100\fscy100)}" if j == 0 else ""
            lines.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{pop}{' '.join(parts)}")
    if hook_text:
        lines.append(f"Dialogue: 1,{ass_time(0)},{ass_time(3.5)},Hook,,0,0,0,,{{\\fad(150,250)}}{hook_text.upper()}")
    open(path, "w", encoding="utf-8").write(head + "\n".join(lines) + "\n")


# ------------------------------------------------------------------ portada + textos
def thumbnail(clip, z, hop, st, en, out, text):
    a, b = int(st / hop), int(en / hop)
    peak = st + (int(np.argmax(z[a:b])) * hop if b > a else 0)
    t = max(0.0, min(en - st - 0.1, peak - st))
    raw = out + ".raw.jpg"
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", clip, "-frames:v", "1", raw])
    from PIL import Image, ImageDraw, ImageFont
    im = Image.open(raw).convert("RGB")
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(os.path.join(FONTS, "Anton-Regular.ttf"), 120)
    words, lines, cur = text.upper().split(), [], ""
    for w in words:
        if f.getlength((cur + " " + w).strip()) > W - 120 and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    y = 260
    for ln in lines[:3]:
        x = (W - f.getlength(ln)) / 2
        d.text((x, y), ln, font=f, fill=(255, 229, 0), stroke_width=10, stroke_fill=(0, 0, 0))
        y += 150
    im.save(out, quality=92)
    os.remove(raw)


def suggest(ws):
    text = " ".join(w["w"] for w in ws)
    sents = [s.strip() for s in re.split(r"(?<=[.!?…])\s+", text) if len(s.split()) >= 3]
    hype_norm = [norm(h) for h in HYPE]
    best = max(sents or [text], key=lambda s: sum(norm(s).count(h) for h in hype_norm) + s.count("!") + s.count("?") - abs(len(s.split()) - 7) * 0.2)
    title = " ".join(best.split()[:10]).strip(" .,")
    kw = [norm(w["w"]).strip("¡!¿?.,\"'") for w in ws]
    kw = [k for k in kw if len(k) > 3 and k not in STOP]
    top = [k for k, _ in sorted({k: kw.count(k) for k in kw}.items(), key=lambda x: -x[1])[:4]]
    tags = ["#viral", "#clips", "#streamer", "#fyp"] + [f"#{t}" for t in top]
    return title, tags, text


def download(url, section=None, fmt="bv*[height<=1080]+ba/b[height<=1080]/b", name=None):
    """Descarga un enlace (YouTube, Twitch, Kick…) con yt-dlp a input/ (máx. 1080p)."""
    os.makedirs(os.path.join(HERE, "input"), exist_ok=True)
    tpl = os.path.join(HERE, "input", (name or "%(uploader,channel)s_%(id)s") + ("_" + section.replace(":", "").replace("-", "_") if section else "") + ".%(ext)s")
    cmd = [sys.executable, "-m", "yt_dlp", "-f", fmt, "--merge-output-format", "mp4", "-N", "8",
           "-o", tpl, "--print", "after_move:filepath", "--no-playlist", "--no-progress"]
    if section:
        cmd += ["--download-sections", "*" + section, "--force-keyframes-at-cuts"]
    env = dict(os.environ)
    if env.get("HTTPS_PROXY") and not env.get("http_proxy"):
        env["http_proxy"] = env["HTTPS_PROXY"]  # ffmpeg solo lee http_proxy
    out = subprocess.run(cmd + [url], capture_output=True, text=True, env=env)
    if out.returncode != 0:
        sys.exit("No se pudo descargar: " + out.stderr.strip().splitlines()[-1] if out.stderr.strip() else "error desconocido")
    return out.stdout.strip().splitlines()[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", help="archivo de vídeo o enlace (YouTube, Twitch, Kick…)")
    ap.add_argument("--tramo", help="solo descargar este tramo del enlace, p. ej. 01:00:00-01:30:00")
    ap.add_argument("-n", type=int, default=5, help="número de clips")
    ap.add_argument("--lang", default="", help="es, en… (vacío = automático)")
    ap.add_argument("--min", type=float, default=20)
    ap.add_argument("--max", type=float, default=45)
    ap.add_argument("--layout", default="auto", choices=["auto", "crop", "blur", "split"])
    ap.add_argument("--at", action="append", help="momento concreto HH:MM:SS-HH:MM:SS (repetible)")
    ap.add_argument("--hook", action="store_true", help="texto gancho arriba los primeros segundos")
    ap.add_argument("--rapido", action="store_true", help="directos largos: analiza en baja calidad, descarga solo los clips en 1080p")
    ap.add_argument("--zonas", type=int, default=30, help="modo rápido: zonas intensas a transcribir")
    a = ap.parse_args()
    url = None
    if re.match(r"https?://", a.video):
        url = a.video
        if a.rapido:
            print("Descargando versión ligera para analizar…", flush=True)
            a.video = download(url, a.tramo, fmt="worst[height>=144]/worst", name="analisis_%(id)s")
        else:
            print("Descargando…", flush=True)
            a.video = download(url, a.tramo)
        print("Descargado:", a.video)

    name = re.sub(r"[^\w-]+", "_", os.path.splitext(os.path.basename(a.video))[0])[:40]
    od = os.path.join(HERE, "output", name)
    os.makedirs(od, exist_ok=True)
    iw, ih, fps, dur = probe(a.video)
    print(f"{a.video}: {iw}x{ih} {fps:.1f}fps {ts(dur)}")
    wav = os.path.join(od, "audio16k.wav")
    if not os.path.exists(wav):
        extract_audio(a.video, wav)
    x, sr = sf.read(wav, dtype="float32")
    z, hop = loudness(x, sr)
    print("Detectando voz…")
    segs = vad_segments(x, sr)
    if a.rapido and not a.at:
        zones = hot_zones(z, hop, dur, a.zonas)
        segs = [s_ for s_ in segs if any(za <= s_[0] < zb for za, zb in zones)]
        print(f"Modo rápido: {len(zones)} zonas intensas")
    print(f"Transcribiendo {len(segs)} fragmentos…")
    words = transcribe(x, sr, segs, a.lang, os.path.join(od, "transcripcion.json"))
    if a.at:
        clips = [(0, parse_ts(s.split("-")[0]), parse_ts(s.split("-")[1])) for s in a.at]
    else:
        clips = pick_clips(words, z, hop, dur, a.n, a.min, a.max)
    report = [f"CLIPS DE: {os.path.basename(a.video)}", ""]
    for i, (sc, st, en) in enumerate(clips, 1):
        ws = [w for w in words if st <= w["s"] < en]
        title, tags, text = suggest(ws)
        ass = os.path.join(od, f"clip_{i:02d}.ass")
        make_ass(words, st, en, ass, title if a.hook else None)
        out = os.path.join(od, f"clip_{i:02d}.mp4")
        print(f"[{i}/{len(clips)}] {ts(st)} → {ts(en)}  (puntuación {sc:.2f})", flush=True)
        if url and a.rapido:
            hq = download(url, f"{ts(st - 1)}-{ts(en + 1)}", name=f"hq_{i:02d}_%(id)s")
            hw, hh, hfps, _ = probe(hq)
            make_ass([dict(w, s=w["s"] - st + 1, e=w["e"] - st + 1) for w in words], 1, en - st + 1, ass, title if a.hook else None)
            render_clip(hq, 1, en - st + 1, out, hw, hh, hfps, a.layout, ass)
        else:
            render_clip(a.video, st, en, out, iw, ih, fps, a.layout, ass)
        thumbnail(out, z, hop, st, en, os.path.join(od, f"clip_{i:02d}.jpg"), title)
        report += [f"=== CLIP {i:02d} · {ts(st)} → {ts(en)} ({en - st:.0f}s) · puntuación {sc:.2f}",
                   f"TÍTULO SUGERIDO: {title}", f"HASHTAGS: {' '.join(tags)}", f"TRANSCRIPCIÓN: {text}", ""]
    open(os.path.join(od, "CLIPS.txt"), "w", encoding="utf-8").write("\n".join(report))
    print(f"Listo → {od}")


if __name__ == "__main__":
    main()
