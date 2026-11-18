"""Construye un video completo: voz, música, efectos, animación, montaje, miniatura, SRT y ficha de subida.

Uso:  python3 build.py 1          (video 1)
      python3 build.py all
      python3 build.py 1 --preview   (solo 10 s a baja calidad)
"""
import os, sys, json, subprocess, shutil, math
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from PIL import Image, ImageDraw

import content
import tts
import audio
import render as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "videos")
WORK = os.environ.get("GTA_WORK", os.path.join(ROOT, ".work"))

PRE, GAP, POST = 0.55, 0.32, 0.45


def norm_lines(sc):
    out = []
    for l in sc["lines"]:
        out.append({"say": l} if isinstance(l, str) else l)
    return out


def build_timeline(v, wd):
    t = 0.0
    tl = []
    voice_clips = []
    for si, sc in enumerate(v["scenes"]):
        s = {"type": sc["type"], "t0": t, "items": [], "lines": [], **{k: sc[k] for k in sc if k not in ("lines", "type")}}
        t += PRE
        for li, l in enumerate(norm_lines(sc)):
            wav = os.path.join(wd, f"s{si:02d}_l{li:02d}.wav")
            if not os.path.exists(wav):
                d = tts.synth(l["say"], wav)
            else:
                d = sf.info(wav).duration
            if "item" in l:
                s["items"].append((t - s["t0"] - 0.05, l["item"]))
            s["lines"].append((t, t + d, l["say"]))
            voice_clips.append((t, wav))
            t += d + GAP
        t += POST
        if sc["type"] == "outro":
            t = max(t, s["t0"] + 4.5) + 1.0
        s["t1"] = t
        tl.append(s)
    return tl, t, voice_clips


def make_audio(v, tl, total, clips, wd):
    sr = audio.SR
    n = int((total + 1) * sr)
    voice = np.zeros(n)
    for t0, wav in clips:
        x, r = sf.read(wav)
        if x.ndim > 1:
            x = x.mean(1)
        x = resample_poly(x, sr, r)
        a = int(t0 * sr)
        voice[a:a + len(x)] += x[:n - a]
    sf.write(os.path.join(wd, "voice.wav"), voice.astype(np.float32), sr)
    mus = audio.music(total, v["hue"], seed=len(v["slug"]))[:n]
    audio.write(os.path.join(wd, "music.wav"), mus)
    sfx = np.zeros((n, 2))
    wh, pp, hh = audio.whoosh(), audio.pop(), audio.hit()
    def add(clip, t, g=1.0):
        a = int(t * sr)
        b = min(n, a + len(clip))
        if a < n:
            sfx[a:b] += clip[:b - a] * g
    add(hh, 0.05, 0.8)
    for s in tl:
        if s["t0"] > 0.1:
            add(wh, max(0, s["t0"] - 0.05), 0.7)
        for ti, _ in s["items"]:
            add(pp, s["t0"] + ti, 0.6)
    audio.write(os.path.join(wd, "sfx.wav"), sfx)
    mix = os.path.join(wd, "mix.m4a")
    fc = ("[0:a]highpass=f=70,equalizer=f=3000:t=q:w=1.2:g=3,acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2,"
          "aformat=channel_layouts=stereo,asplit=2[v1][v2];"
          "[1:a]volume=0.32[m];[m][v2]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=350[md];"
          "[2:a]volume=0.8[s];"
          "[v1][md][s]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(wd, "voice.wav"), "-i", os.path.join(wd, "music.wav"),
                    "-i", os.path.join(wd, "sfx.wav"), "-filter_complex", fc, "-map", "[out]", "-ar", "48000",
                    "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", mix], check=True)
    return mix


def render_video(v, tl, total, wd, preview=False):
    rr = R.Renderer(v, tl, total)
    fps = R.FPS
    nframes = int(total * fps) if not preview else int(min(total, 12) * fps)
    raw = os.path.join(wd, "video_noaudio.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{R.W}x{R.H}", "-r", str(fps),
           "-i", "-", "-c:v", "libx264", "-preset", "veryfast" if preview else "medium", "-crf", "30" if preview else "21",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", raw]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(nframes):
        p.stdin.write(rr.frame(i / fps).tobytes())
        if i % 300 == 0:
            print(f"  {v['slug']}: frame {i}/{nframes}", flush=True)
    p.stdin.close(); p.wait()
    return raw


def fmt_ts(t, srt=True):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    if srt:
        return f"{h:02d}:{m:02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
    return f"{m}:{int(s):02d}" if h == 0 else f"{h}:{m:02d}:{int(s):02d}"


def write_srt(tl, path):
    subs = []
    for s in tl:
        for (a, b, text) in s["lines"]:
            subs += R.chunk_subs(a, b, text)
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, text) in enumerate(subs, 1):
            f.write(f"{i}\n{fmt_ts(a)} --> {fmt_ts(b)}\n{text}\n\n")


def chapters(tl):
    ch = []
    for s in tl:
        name = s.get("chapter")
        if not name:
            continue
        if ch and s["t0"] - ch[-1][0] < 10:
            continue
        ch.append((0.0 if not ch else s["t0"], name))
    return ch


def write_upload(v, tl, total, path):
    ch = chapters(tl)
    lines = [
        "TÍTULO:", v["title"], "",
        "DESCRIPCIÓN:",
        v["desc"], "",
        "👉 Suscríbete para no perderte nada de GTA 6.", "",
        "CAPÍTULOS:",
    ]
    lines += [f"{fmt_ts(t, False)} {name}" for t, name in ch]
    lines += ["", "#GTA6 #GTAVI #GrandTheftAuto6", "", content.DISCLAIMER, "",
              "ETIQUETAS (pegar en 'Etiquetas'):", ", ".join(v["tags"]), "",
              f"DURACIÓN: {fmt_ts(total, False)}",
              "IDIOMA: Español · CATEGORÍA: Videojuegos · Contenido para niños: NO",
              "MÚSICA: original, generada para el canal (sin copyright).",
              "SUBTÍTULOS: sube el archivo subtitulos.srt en 'Subtítulos'."]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def make_thumbnail(v, rr_bg, path):
    pal = R.PALETTES[v["hue"]]
    im = Image.fromarray(rr_bg).convert("RGBA")
    # darken left for text
    shade = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for x in range(0, 1100, 4):
        sd.rectangle((x, 0, x + 4, R.H), fill=(0, 0, 0, int(190 * (1 - x / 1100))))
    im.alpha_composite(shade)
    big = R.text_img(v["thumb_big"], "head", 420 if len(v["thumb_big"]) <= 4 else 300, fill=pal["a2"], stroke=10,
                     stroke_fill="#120018", glow=pal["a2"], glow_r=30)
    big = big.rotate(-6, expand=True, resample=Image.BICUBIC)
    if big.width > 900:
        s = 900 / big.width
        big = big.resize((int(big.width * s), int(big.height * s)), Image.LANCZOS)
    R.blit(im, big, 1430, 560)
    y = 330
    for i, line in enumerate(v["thumb"]):
        col = "#ffffff" if i == 0 else pal["a1"]
        t = R.text_img(line, "head", 210, fill=col, stroke=12, stroke_fill="#000000", glow="#000000", glow_r=14)
        if t.width > 1150:
            s = 1150 / t.width
            t = t.resize((int(t.width * s), int(t.height * s)), Image.LANCZOS)
        R.blit(im, t, 70, y + i * 250, anchor="lm")
    tag = R.text_img("GTA 6", "head", 90, fill="#120018")
    R.blit(im, R.pill(tag.width + 50, 130, pal["grid"]), 80, 110, anchor="lm")
    R.blit(im, tag, 105, 110, anchor="lm")
    out = im.convert("RGB").resize((1280, 720), Image.LANCZOS)
    out.save(path, quality=92)


def build(idx, preview=False):
    v = content.VIDEOS[idx - 1]
    wd = os.path.join(WORK, v["slug"])
    od = os.path.join(OUT, v["slug"])
    os.makedirs(wd, exist_ok=True); os.makedirs(od, exist_ok=True)
    print(f"[{idx}] TTS…", flush=True)
    tl, total, clips = build_timeline(v, wd)
    print(f"[{idx}] duración {total:.1f}s; audio…", flush=True)
    mix = make_audio(v, tl, total, clips, wd)
    print(f"[{idx}] render…", flush=True)
    raw = render_video(v, tl, total, wd, preview)
    final = os.path.join(od if not preview else wd, "video.mp4" if not preview else "preview.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-i", mix, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "copy", "-shortest", "-movflags", "+faststart", final], check=True)
    if not preview:
        bg, _ = R.make_background(v["hue"], seed=sum(map(ord, v["slug"])))
        make_thumbnail(v, bg[0], os.path.join(od, "miniatura.jpg"))
        write_srt(tl, os.path.join(od, "subtitulos.srt"))
        write_upload(v, tl, total, os.path.join(od, "SUBIR.txt"))
        guion = os.path.join(od, "guion.txt")
        with open(guion, "w", encoding="utf-8") as f:
            for s in tl:
                f.write(f"\n[{fmt_ts(s['t0'], False)}] {s.get('chapter', s['type']).upper()}\n")
                for (a, b, text) in s["lines"]:
                    f.write(f"  {text}\n")
    print(f"[{idx}] listo → {final}", flush=True)
    return final


if __name__ == "__main__":
    os.environ.setdefault("PYTHONHASHSEED", "0")
    arg = sys.argv[1]
    preview = "--preview" in sys.argv
    ids = range(1, len(content.VIDEOS) + 1) if arg == "all" else [int(x) for x in arg.split(",")]
    for i in ids:
        build(i, preview)
