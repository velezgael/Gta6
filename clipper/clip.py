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


# ------------------------------------------------------------------ framing
def face_track(video, st, en, iw, ih, fps):
    import cv2
    cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(video)
    xs, times = [], []
    t = st
    while t < en:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, fr = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(cv2.resize(fr, (iw // 2, ih // 2)), cv2.COLOR_BGR2GRAY)
        faces = cas.detectMultiScale(g, 1.15, 6, minSize=(ih // 20, ih // 20))
        if len(faces):
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            xs.append((x + w / 2) * 2); times.append(t)
        t += 0.5
    cap.release()
    if len(xs) < max(2, 0.25 * (en - st) / 0.5):
        return None  # casi no hay caras -> layout blur
    # interpolar + suavizar
    grid = np.arange(st, en, 1 / fps)
    cx = np.interp(grid, times, xs)
    k = int(fps * 1.2)
    cx = np.convolve(np.pad(cx, (k, k), mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), mode="valid")
    return cx


def render_clip(video, st, en, out, iw, ih, fps, layout, ass_path, hook_text=None):
    import cv2
    tmp = out + ".noaudio.mp4"
    cw = int(ih * 9 / 16) // 2 * 2
    cx = None
    if layout == "auto" and iw > ih:
        cx = face_track(video, st, en, iw, ih, fps)
    use_crop = cx is not None or (layout == "crop" and iw > ih)
    if layout == "crop" and cx is None:
        cx = np.full(int((en - st) * fps) + 2, iw / 2)
    cap = cv2.VideoCapture(video)
    cap.set(cv2.CAP_PROP_POS_MSEC, st * 1000)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                            "-r", f"{fps:.3f}", "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                            "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    nfr = int((en - st) * fps)
    for i in range(nfr):
        ok, fr = cap.read()
        if not ok:
            break
        if iw <= ih:  # ya es vertical
            canvas = cv2.resize(fr, (W, int(ih * W / iw)))
            canvas = canvas[(canvas.shape[0] - H) // 2:][:H] if canvas.shape[0] >= H else cv2.copyMakeBorder(
                canvas, (H - canvas.shape[0]) // 2, H - canvas.shape[0] - (H - canvas.shape[0]) // 2, 0, 0, cv2.BORDER_CONSTANT)
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


def download(url, section=None):
    """Descarga un enlace (YouTube, Twitch, Kick…) con yt-dlp a input/ (máx. 1080p)."""
    os.makedirs(os.path.join(HERE, "input"), exist_ok=True)
    tpl = os.path.join(HERE, "input", "%(uploader,channel)s_%(id)s" + ("_" + section.replace(":", "").replace("-", "_") if section else "") + ".%(ext)s")
    cmd = [sys.executable, "-m", "yt_dlp", "-f", "bv*[height<=1080]+ba/b[height<=1080]/b", "--merge-output-format", "mp4",
           "-o", tpl, "--print", "after_move:filepath", "--no-playlist", "--no-progress"]
    if section:
        cmd += ["--download-sections", "*" + section, "--force-keyframes-at-cuts"]
    out = subprocess.run(cmd + [url], capture_output=True, text=True)
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
    ap.add_argument("--layout", default="auto", choices=["auto", "crop", "blur"])
    ap.add_argument("--at", action="append", help="momento concreto HH:MM:SS-HH:MM:SS (repetible)")
    ap.add_argument("--hook", action="store_true", help="texto gancho arriba los primeros segundos")
    a = ap.parse_args()
    if re.match(r"https?://", a.video):
        print("Descargando…", flush=True)
        a.video = download(a.video, a.tramo)
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
    print("Detectando voz…")
    segs = vad_segments(x, sr)
    print(f"Transcribiendo {len(segs)} fragmentos…")
    words = transcribe(x, sr, segs, a.lang, os.path.join(od, "transcripcion.json"))
    z, hop = loudness(x, sr)
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
        render_clip(a.video, st, en, out, iw, ih, fps, a.layout, ass)
        thumbnail(out, z, hop, st, en, os.path.join(od, f"clip_{i:02d}.jpg"), title)
        report += [f"=== CLIP {i:02d} · {ts(st)} → {ts(en)} ({en - st:.0f}s) · puntuación {sc:.2f}",
                   f"TÍTULO SUGERIDO: {title}", f"HASHTAGS: {' '.join(tags)}", f"TRANSCRIPCIÓN: {text}", ""]
    open(os.path.join(od, "CLIPS.txt"), "w", encoding="utf-8").write("\n".join(report))
    print(f"Listo → {od}")


if __name__ == "__main__":
    main()
