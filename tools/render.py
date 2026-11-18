"""Motor de render: fondos synthwave animados + plantillas animadas por escena."""
import os, math, random
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "assets", "fonts")
W, H, FPS = 1920, 1080, 30
HORIZON = 650
LOOP = 30

PALETTES = {
    "sunset": dict(sky=["#0d0221", "#4a0e6b", "#ff6f61"], sun=["#ffe259", "#ff2f92"], grid="#ff2bd6", a1="#ffd23f", a2="#00e5ff"),
    "mint":   dict(sky=["#03141a", "#0b5e66", "#f6a6b2"], sun=["#ffe29a", "#ff5e9c"], grid="#23f0c7", a1="#ff4f9a", a2="#ffe066"),
    "cyber":  dict(sky=["#020024", "#1b1b8f", "#00b4e6"], sun=["#00f5d4", "#9b5de5"], grid="#00f5ff", a1="#f15bb5", a2="#fee440"),
    "fire":   dict(sky=["#160000", "#6e0b14", "#ff8c00"], sun=["#ffe066", "#ff3d00"], grid="#ff7b00", a1="#ffd000", a2="#ff3b6b"),
    "ocean":  dict(sky=["#00101d", "#00467f", "#27c0d6"], sun=["#ffe8a3", "#ff7e8b"], grid="#3df2ff", a1="#ffcc33", a2="#ff5c8a"),
    "retro":  dict(sky=["#12001f", "#5a189a", "#ff9e00"], sun=["#ffdd00", "#ff006e"], grid="#ff00a0", a1="#00f0ff", a2="#ffdd00"),
}


def hexrgb(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


# ------------------------------------------------------------------ fonts / text
@lru_cache(None)
def font(name, size, weight=None):
    path = {"anton": "Anton-Regular.ttf", "bebas": "BebasNeue-Regular.ttf",
            "mont": "Montserrat.ttf", "oswald": "Oswald.ttf"}[name]
    f = ImageFont.truetype(os.path.join(FONTS, path), size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def F(kind, size):
    if kind == "head":
        return font("anton", size)
    if kind == "bold":
        return font("mont", size, 800)
    if kind == "semi":
        return font("mont", size, 600)
    return font("mont", size, 500)


def wrap(text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if fnt.getlength(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


@lru_cache(maxsize=4096)
def text_img(text, kind, size, fill="#ffffff", stroke=0, stroke_fill="#000000", glow=None, glow_r=14, maxw=None, align="center", spacing=0.08):
    fnt = F(kind, size)
    lines = wrap(text, fnt, maxw) if maxw else [text]
    asc, desc = fnt.getmetrics()
    lh = int((asc + desc) * (1 + spacing))
    widths = [fnt.getlength(l) for l in lines]
    pad = stroke + (glow_r * 3 if glow else 4)
    w = int(max(widths)) + pad * 2
    h = lh * len(lines) + pad * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    def draw_lines(d, color, sw, sf):
        for i, l in enumerate(lines):
            if align == "center":
                x = pad + (w - pad * 2 - widths[i]) / 2
            else:
                x = pad
            d.text((x, pad + i * lh), l, font=fnt, fill=color, stroke_width=sw, stroke_fill=sf)
    if glow:
        g = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw_lines(ImageDraw.Draw(g), hexrgb(glow), stroke + 4, hexrgb(glow))
        g = g.filter(ImageFilter.GaussianBlur(glow_r))
        im = Image.alpha_composite(im, g)
        im = Image.alpha_composite(im, g)
    d = ImageDraw.Draw(im)
    draw_lines(d, hexrgb(fill) if isinstance(fill, str) else fill, stroke, hexrgb(stroke_fill))
    return im


_alpha_cache = {}


def with_alpha(im, a):
    a = max(0.0, min(1.0, a))
    if a >= 0.999:
        return im
    key = (id(im), int(a * 24))
    r = _alpha_cache.get(key)
    if r is None:
        if len(_alpha_cache) > 3000:
            _alpha_cache.clear()
        r = im.copy()
        q = int(a * 24) / 24
        r.putalpha(im.getchannel("A").point(lambda v: int(v * q)))
        _alpha_cache[key] = r
    return r


def blit(base, im, x, y, a=1.0, anchor="mm", scale=1.0):
    if a <= 0.01:
        return
    if abs(scale - 1) > 0.01:
        s = round(scale, 2)
        im = _scaled(im, s)
    im = with_alpha(im, a)
    w, h = im.size
    if anchor[0] == "m": x -= w / 2
    elif anchor[0] == "r": x -= w
    if anchor[1] == "m": y -= h / 2
    elif anchor[1] == "b": y -= h
    x, y = int(x), int(y)
    # clip to canvas
    if x >= W or y >= H or x + w <= 0 or y + h <= 0:
        return
    if x < 0 or y < 0 or x + w > W or y + h > H:
        cx0, cy0 = max(0, -x), max(0, -y)
        cx1, cy1 = min(w, W - x), min(h, H - y)
        im = im.crop((cx0, cy0, cx1, cy1)); x += cx0; y += cy0
    base.alpha_composite(im, (x, y))


_scale_cache = {}


def _scaled(im, s):
    key = (id(im), s)
    r = _scale_cache.get(key)
    if r is None:
        if len(_scale_cache) > 2000:
            _scale_cache.clear(); _alpha_cache.clear()
        r = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
        _scale_cache[key] = r
    return r


def ease_out(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3


def ease_back(x):
    x = max(0.0, min(1.0, x)); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def prog(t, start, dur):
    return max(0.0, min(1.0, (t - start) / dur))


@lru_cache(maxsize=512)
def pill(w, h, color, alpha=255, radius=None, outline=None, ow=0):
    im = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = radius if radius is not None else h // 2
    d.rounded_rectangle((0, 0, w - 1, h - 1), r, fill=hexrgb(color, alpha), outline=hexrgb(outline) if outline else None, width=ow)
    return im


@lru_cache(maxsize=256)
def glow_circle(r, color, blur=18):
    s = int(r * 2 + blur * 6)
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    d.ellipse((c - r, c - r, c + r, c + r), fill=hexrgb(color))
    g = im.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(g, im)


@lru_cache(maxsize=256)
def ring(r, color, width=6, blur=8):
    s = int(r * 2 + blur * 6 + width * 2)
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    d.ellipse((c - r, c - r, c + r, c + r), outline=hexrgb(color), width=width)
    g = im.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(g, im)


# ------------------------------------------------------------------ background
def _grad(h, stops):
    cols = np.array([hexrgb(s)[:3] for s in stops], float)
    pos = np.linspace(0, 1, len(stops))
    y = np.linspace(0, 1, h)
    out = np.zeros((h, 3))
    for c in range(3):
        out[:, c] = np.interp(y, pos, cols[:, c])
    return out


def _palm(d, x, y, height, lean, scale, color):
    pts = []
    for i in range(60):
        t = i / 59
        pts.append((x + lean * (t ** 1.6) * height, y - t * height))
    left = [(px - (18 - 9 * i / 59) * scale, py) for i, (px, py) in enumerate(pts)]
    right = [(px + (18 - 9 * i / 59) * scale, py) for i, (px, py) in enumerate(pts)]
    d.polygon(left + right[::-1], fill=color)
    tx, ty = pts[-1]
    for ang in [-175, -150, -125, -100, -80, -55, -30, -5, 20, 200, 165]:
        a = math.radians(ang)
        L = 250 * scale
        up = -math.sin(a)  # >0 when frond points upward
        top, bot = [], []
        for k in range(20):
            s = k / 19
            cx = tx + math.cos(a) * L * s
            cy = ty + math.sin(a) * L * s * 0.6 + (s ** 2) * (70 + 60 * (1 - up)) * scale
            wdt = math.sin(math.pi * min(1, s * 1.1)) * 34 * scale * (1 - 0.5 * s)
            top.append((cx, cy - wdt)); bot.append((cx, cy + wdt * 0.5))
        d.polygon(top + bot[::-1], fill=color)
        # serrated leaflets
        for k in range(3, 19, 2):
            s = k / 19
            cx = tx + math.cos(a) * L * s
            cy = ty + math.sin(a) * L * s * 0.6 + (s ** 2) * (70 + 60 * (1 - up)) * scale
            d.line((cx, cy, cx + math.cos(a + 0.9) * 40 * scale * (1 - s), cy + 45 * scale * (1 - s * 0.5)), fill=color, width=max(2, int(5 * scale)))
    d.ellipse((tx - 24 * scale, ty - 20 * scale, tx + 24 * scale, ty + 20 * scale), fill=color)


def make_background(pal_name, seed=3):
    pal = PALETTES[pal_name]
    rng = random.Random(seed)
    sky = _grad(HORIZON, pal["sky"])
    sky_img = np.zeros((H, W, 3), np.float32)
    sky_img[:HORIZON] = sky[:, None, :]
    floor = _grad(H - HORIZON, ["#0a0014", "#05000a"]) * 1.0
    sky_img[HORIZON:] = floor[:, None, :]
    base = Image.fromarray(sky_img.clip(0, 255).astype(np.uint8)).convert("RGBA")

    # sun glow
    sun_c = (W // 2, 440); R = 290
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((sun_c[0] - R - 60, sun_c[1] - R - 60, sun_c[0] + R + 60, sun_c[1] + R + 60), fill=hexrgb(pal["sun"][1], 150))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    base = Image.alpha_composite(base, glow)

    stars = [(rng.randrange(W), rng.randrange(0, HORIZON - 250), rng.random(), rng.randint(1, 3)) for _ in range(170)]
    sun_grad = _grad(2 * R, pal["sun"])

    # skyline
    sky_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sky_layer)
    x = 0
    dark = tuple(int(c * 0.35) for c in hexrgb(pal["sky"][0])[:3]) + (255,)
    while x < W:
        bw = rng.randint(40, 120)
        bh = rng.randint(40, 230) if abs(x - W / 2) > 260 else rng.randint(20, 120)
        sd.rectangle((x, HORIZON - bh, x + bw, HORIZON), fill=dark)
        if rng.random() < 0.25:
            sd.rectangle((x + bw // 2 - 2, HORIZON - bh - 40, x + bw // 2 + 2, HORIZON - bh), fill=dark)
        for wy in range(HORIZON - bh + 10, HORIZON - 8, 16):
            for wx in range(x + 6, x + bw - 8, 14):
                if rng.random() < 0.18:
                    col = hexrgb(rng.choice([pal["a1"], pal["a2"], "#ffffff"]), rng.randint(90, 200))
                    sd.rectangle((wx, wy, wx + 5, wy + 7), fill=col)
        x += bw + rng.randint(0, 8)
    # palms
    palm_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(palm_layer)
    pc = (8, 0, 18, 255)
    _palm(pd, 150, H + 40, 760, 0.35, 1.25, pc)
    _palm(pd, 330, H + 60, 560, -0.25, 0.9, pc)
    _palm(pd, 1770, H + 40, 800, -0.3, 1.3, pc)
    _palm(pd, 1600, H + 80, 520, 0.2, 0.85, pc)

    vign = np.ones((H, W), np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    vign = np.clip(1.15 - 0.45 * dist ** 2, 0.35, 1.0)
    scan = np.ones((H, 1), np.float32); scan[::3] = 0.9
    shade = (vign * scan)[:, :, None]

    grid_col = hexrgb(pal["grid"])
    frames, frames_dim = [], []
    for k in range(LOOP):
        ph = k / LOOP
        im = base.copy()
        d = ImageDraw.Draw(im)
        for (sx, sy, p, r) in stars:
            b = 0.5 + 0.5 * math.sin(2 * math.pi * (ph * 2 + p))
            d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(255, 255, 255, int(60 + 180 * b)))
        # sun with stripes
        sun = np.zeros((2 * R, 2 * R, 4), np.uint8)
        yy2, xx2 = np.mgrid[0:2 * R, 0:2 * R]
        mask = ((xx2 - R) ** 2 + (yy2 - R) ** 2) <= R * R
        sun[..., :3] = sun_grad[:, None, :].astype(np.uint8)
        alpha = mask.astype(np.uint8) * 255
        for i in range(9):
            yc = R + 25 + ((i + ph) / 9) * R * 0.98
            th = 3 + 22 * ((yc - R) / R)
            alpha[int(yc - th / 2):int(yc + th / 2)] = 0
        sun[..., 3] = alpha
        sun_im = Image.fromarray(sun, "RGBA")
        im.alpha_composite(sun_im, (sun_c[0] - R, sun_c[1] - R))
        im.alpha_composite(sky_layer)
        # grid
        gl = Image.new("RGBA", (W, H - HORIZON + 2), (0, 0, 0, 0))
        g = ImageDraw.Draw(gl)
        for n in range(0, 60):
            dz = n + (1 - ph)
            if dz < 0.6: continue
            y = 430 / dz
            if y < 2: continue
            a = int(255 * min(1, y / 80))
            g.line((0, y, W, y), fill=grid_col[:3] + (a,), width=2 if y < 200 else 3)
        vx = W / 2
        for i in range(-24, 25):
            xb = vx + i * 150
            g.line((vx + i * 6, 0, xb, H - HORIZON), fill=grid_col[:3] + (200,), width=2)
        glow_l = gl.filter(ImageFilter.GaussianBlur(5))
        im.alpha_composite(glow_l, (0, HORIZON))
        im.alpha_composite(gl, (0, HORIZON))
        hl = Image.new("RGBA", (W, 40), (0, 0, 0, 0))
        ImageDraw.Draw(hl).rectangle((0, 18, W, 22), fill=hexrgb(pal["sun"][1], 255))
        hl = hl.filter(ImageFilter.GaussianBlur(6))
        im.alpha_composite(hl, (0, HORIZON - 20))
        im.alpha_composite(palm_layer)
        arr = (np.asarray(im.convert("RGB"), np.float32) * shade).clip(0, 255).astype(np.uint8)
        frames.append(arr)
        dim = Image.fromarray(arr).filter(ImageFilter.GaussianBlur(6))
        frames_dim.append((np.asarray(dim, np.float32) * 0.42).astype(np.uint8))
    return frames, frames_dim


# ------------------------------------------------------------------ silhouettes / map
@lru_cache(maxsize=32)
def silhouette(kind, color1, color2, w=520, h=680):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bg = _grad(h, [color1, color2])
    card = Image.fromarray(np.repeat(bg[:, None, :], w, 1).astype(np.uint8)).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 36, fill=255)
    im.paste(card, (0, 0), m)
    d = ImageDraw.Draw(im)
    sil = (10, 0, 22, 235)
    def person(cx, s, female=False):
        hr = 78 * s
        hy = h - 330 * s
        if female:
            d.ellipse((cx - hr * 1.25, hy - hr * 1.1, cx + hr * 1.25, hy + hr * 1.9), fill=sil)
        d.ellipse((cx - hr, hy - hr * 1.15, cx + hr, hy + hr * 1.05), fill=sil)
        d.rectangle((cx - hr * 0.42, hy + hr * 0.6, cx + hr * 0.42, hy + hr * 1.6), fill=sil)
        d.rounded_rectangle((cx - hr * 2.6, hy + hr * 1.45, cx + hr * 2.6, h + 60), int(hr * 1.4), fill=sil)
    if kind == "duo":
        person(w * 0.33, 0.82, True); person(w * 0.68, 0.9, True)
    else:
        person(w / 2, 1.0, kind == "f")
    border = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(border).rounded_rectangle((2, 2, w - 3, h - 3), 36, outline=(255, 255, 255, 200), width=4)
    im.alpha_composite(border)
    return im


MAP_BOX = (1000, 110, 1860, 880)
LAND = [(0.0, 0.10), (0.30, 0.07), (0.45, 0.05), (0.55, 0.10), (0.62, 0.08), (0.75, 0.12), (0.80, 0.25), (0.86, 0.45),
        (0.92, 0.63), (0.93, 0.79), (0.89, 0.88), (0.81, 0.91), (0.73, 0.87), (0.66, 0.76), (0.59, 0.61), (0.53, 0.46),
        (0.49, 0.33), (0.43, 0.23), (0.31, 0.20), (0.15, 0.22), (0.0, 0.20)]
REGIONS = {
    "vice":     ("VICE CITY", "Neón · Playas · Crimen", (0.89, 0.76)),
    "keys":     ("LEONIDA KEYS", "Islas · Barcos · Contrabando", (0.62, 0.965)),
    "grass":    ("GRASSRIVERS", "Pantanos · Caimanes", (0.76, 0.74)),
    "port":     ("PORT GELLHORN", "Puerto · Moteles", (0.17, 0.15)),
    "ambrosia": ("AMBROSIA", "Industria · Moteros", (0.63, 0.30)),
    "kalaga":   ("MOUNT KALAGA", "Bosques · Caza · Ríos", (0.42, 0.13)),
}


def map_xy(p):
    x0, y0, x1, y1 = MAP_BOX
    return x0 + p[0] * (x1 - x0), y0 + p[1] * (y1 - y0)


@lru_cache(maxsize=8)
def map_base(pal_name):
    pal = PALETTES[pal_name]
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pts = [map_xy(p) for p in LAND]
    keys = [(0.80, 0.95), (0.75, 0.97), (0.70, 0.985), (0.64, 0.995), (0.58, 0.997), (0.52, 0.99), (0.47, 0.98)]
    land = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(land)
    ld.polygon(pts, fill=(14, 40, 52, 235))
    for k in keys:
        x, y = map_xy(k); ld.ellipse((x - 16, y - 7, x + 16, y + 7), fill=(14, 40, 52, 235))
    # lake
    lx, ly = map_xy((0.76, 0.58)); ld.ellipse((lx - 30, ly - 24, lx + 30, ly + 24), fill=(8, 20, 40, 255))
    outline = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(outline)
    od.line(pts + [pts[0]], fill=hexrgb(pal["a2"]), width=4, joint="curve")
    for k in keys:
        x, y = map_xy(k); od.ellipse((x - 16, y - 7, x + 16, y + 7), outline=hexrgb(pal["a2"]), width=3)
    og = outline.filter(ImageFilter.GaussianBlur(8))
    im = Image.alpha_composite(im, og)
    im = Image.alpha_composite(im, land)
    im = Image.alpha_composite(im, outline)
    # roads
    rd = ImageDraw.Draw(im)
    road = (255, 255, 255, 50)
    for a, b in [((0.1, 0.15), (0.6, 0.14)), ((0.6, 0.14), (0.85, 0.45)), ((0.85, 0.45), (0.89, 0.78)),
                 ((0.6, 0.14), (0.56, 0.5)), ((0.56, 0.5), (0.85, 0.7)), ((0.89, 0.78), (0.62, 0.96))]:
        rd.line((map_xy(a), map_xy(b)), fill=road, width=3)
    t = text_img("MAPA ILUSTRATIVO · NO OFICIAL", "semi", 22, fill="#ffffff")
    im.alpha_composite(with_alpha(t, 0.6), (MAP_BOX[0] + 10, MAP_BOX[3] + 30))
    return im


# ------------------------------------------------------------------ frame renderer
class Renderer:
    def __init__(self, video, timeline, total):
        self.v = video
        self.pal = PALETTES[video["hue"]]
        self.tl = timeline  # list of scenes with t0, t1, items[(t, item)], lines[(t0,t1,text)]
        self.total = total
        self.bg, self.bg_dim = make_background(video["hue"], seed=sum(map(ord, video["slug"])))
        self.subs = []
        for sc in timeline:
            for (a, b, text) in sc["lines"]:
                self.subs += chunk_subs(a, b, text)
        self.logo = text_img("MODO LEONIDA", "head", 34, fill="#ffffff", glow=self.pal["grid"], glow_r=8)

    def frame(self, t):
        k = int(t * FPS) % LOOP
        sc = None
        for s in self.tl:
            if s["t0"] <= t < s["t1"]:
                sc = s; break
        if sc is None:
            sc = self.tl[-1]
        full_bg = sc["type"] in ("title", "outro")
        arr = self.bg[k] if full_bg else self.bg_dim[k]
        im = Image.fromarray(arr).convert("RGBA")
        lt = t - sc["t0"]
        getattr(self, "s_" + sc["type"])(im, sc, lt, t)
        self.overlay(im, sc, lt, t)
        return im.convert("RGB")

    # common overlay: logo, progress, subtitles, transition
    def overlay(self, im, sc, lt, t):
        blit(im, self.logo, 40, 34, 0.95, anchor="lt")
        p = t / self.total
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, int(W * p), 6), fill=hexrgb(self.pal["a1"]))
        for (a, b, text) in self.subs:
            if a <= t < b:
                img = text_img(text, "bold", 50, fill="#ffffff", stroke=6, stroke_fill="#000000", maxw=1500)
                pp = ease_back(prog(t, a, 0.18))
                blit(im, img, W / 2, 985, min(1, pp * 1.5), scale=0.9 + 0.1 * pp)
                break
        # wipe transition at scene start
        if lt < 0.45:
            x = (lt / 0.45) * (W + 1200) - 600
            bar = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            bd = ImageDraw.Draw(bar)
            for off, col in ((0, self.pal["a1"]), (180, self.pal["grid"])):
                xx = x - off
                bd.polygon([(xx, 0), (xx + 260, 0), (xx + 60, H), (xx - 200, H)], fill=hexrgb(col, 230))
            im.alpha_composite(bar)
        if t < 0.25:  # fade from black
            blk = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - t / 0.25))))
            im.alpha_composite(blk)
        if self.total - t < 0.6:
            blk = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - (self.total - t) / 0.6))))
            im.alpha_composite(blk)

    def items_until(self, sc, lt):
        return [(ti, it) for (ti, it) in sc["items"] if ti <= lt]

    def header(self, im, text, lt, y=150):
        img = text_img(text, "head", 92, fill=self.pal["a1"], glow="#000000", glow_r=10, maxw=1700)
        p = ease_out(prog(lt, 0.15, 0.5))
        blit(im, img, W / 2, y - 30 * (1 - p), p)
        wbar = int(min(img.width - 60, 900) * p)
        d = ImageDraw.Draw(im)
        d.rectangle((W / 2 - wbar / 2, y + 62, W / 2 + wbar / 2, y + 68), fill=hexrgb(self.pal["grid"]))

    # ---------------- templates
    def s_title(self, im, sc, lt, t):
        head = text_img(sc["head"], "head", 168, fill="#ffffff", stroke=4, stroke_fill="#120018", glow=self.pal["grid"], glow_r=22, maxw=1700)
        p = ease_back(prog(lt, 0.1, 0.55))
        breathe = 1 + 0.015 * math.sin(lt * 2)
        y = 400
        if lt < 0.7 and int(lt * 30) % 4 == 0:  # glitch split
            blit(im, text_img(sc["head"], "head", 168, fill="#00ffff", maxw=1700), W / 2 - 12, y, 0.5, scale=1.0)
            blit(im, text_img(sc["head"], "head", 168, fill="#ff0055", maxw=1700), W / 2 + 12, y, 0.5, scale=1.0)
        blit(im, head, W / 2, y, min(1, p * 1.4), scale=(0.6 + 0.4 * p) * breathe)
        sub = text_img(sc["sub"], "bold", 50, fill="#ffffff")
        ps = ease_out(prog(lt, 0.6, 0.5))
        pw = sub.width + 40
        blit(im, pill(pw, 92, "#000000", 170, outline=self.pal["a1"], ow=3), W / 2, y + 200 + 40 * (1 - ps), ps)
        blit(im, sub, W / 2, y + 200 + 40 * (1 - ps), ps)
        tag = text_img("GTA VI", "head", 48, fill="#120018")
        pt = ease_back(prog(lt, 0.9, 0.4))
        blit(im, pill(tag.width + 30, 74, self.pal["a1"]), W / 2, y - 190, pt, scale=0.5 + 0.5 * pt)
        blit(im, tag, W / 2, y - 190, pt, scale=0.5 + 0.5 * pt)

    def s_stat(self, im, sc, lt, t):
        its = self.items_until(sc, lt)
        if not its:
            return
        ti, it = its[-1]
        p = ease_back(prog(lt, ti, 0.5))
        v = it["v"]
        shown = v
        if v.isdigit():
            c = ease_out(prog(lt, ti, 0.9))
            shown = str(int(round(int(v) * c)))
        big = text_img(shown, "head", 330, fill=self.pal["a1"], stroke=5, stroke_fill="#120018", glow=self.pal["a1"], glow_r=26)
        unit = text_img(it["u"], "head", 150, fill=self.pal["a2"], glow=self.pal["a2"], glow_r=16) if it["u"] else None
        wtot = big.width + (unit.width - 40 if unit else 0)
        x0 = W / 2 - wtot / 2
        blit(im, big, x0 + big.width / 2, 430, min(1, p * 1.3), scale=0.7 + 0.3 * p)
        if unit:
            pu = ease_out(prog(lt, ti + 0.25, 0.4))
            blit(im, unit, x0 + big.width - 40 + unit.width / 2 + 40 * (1 - pu), 500, pu)
        lab = text_img(it["l"], "bold", 48, fill="#ffffff")
        pl = ease_out(prog(lt, ti + 0.35, 0.4))
        blit(im, pill(lab.width + 50, 90, "#000000", 180, outline=self.pal["grid"], ow=3), W / 2, 720, pl)
        blit(im, lab, W / 2, 720, pl)

    def s_clock(self, im, sc, lt, t):
        self.header(im, sc["head"], lt, y=140)
        colon = ":" if int(t * 2) % 2 == 0 else " "
        for i, ch in enumerate(["0", "0", colon, "0", "0"]):
            if ch == " ":
                continue
            img = text_img(ch, "head", 300, fill=self.pal["a2"], glow=self.pal["a2"], glow_r=26)
            p = ease_back(prog(lt, 0.3 + i * 0.08, 0.4))
            blit(im, img, W / 2 + (i - 2) * 170, 440, p, scale=0.6 + 0.4 * p)
        date = text_img("19 · NOVIEMBRE · 2026", "bold", 46, fill="#ffffff")
        pd = ease_out(prog(lt, 0.8, 0.4))
        blit(im, date, W / 2, 630, pd)
        if len(sc["lines"]) > 1:
            t1 = sc["lines"][1][0] - sc["t0"]
            for i, c in enumerate(["ESPAÑA", "MÉXICO", "ARGENTINA", "COLOMBIA", "CHILE"]):
                pc = ease_back(prog(lt, t1 + i * 0.25, 0.4))
                lab = text_img(c + " 00:00", "bold", 30, fill="#120018")
                x = W / 2 + (i - 2) * 345
                blit(im, pill(330, 70, self.pal["a1"]), x, 770, pc, scale=0.5 + 0.5 * pc)
                blit(im, lab, x, 770, pc, scale=0.5 + 0.5 * pc)

    def s_bullets(self, im, sc, lt, t):
        self.header(im, sc["head"], lt)
        its = self.items_until(sc, lt)
        n = len([1 for _, it in sc["items"]])
        gap = 118 if n <= 4 else 104
        y0 = 330 if n <= 4 else 300
        for i, (ti, it) in enumerate(its):
            p = ease_out(prog(lt, ti, 0.45))
            last = i == len(its) - 1
            y = y0 + i * gap
            x = 300 - 120 * (1 - p)
            box = pill(1320, 90, self.pal["a1"] if last else "#000000", 235 if last else 150, radius=18,
                       outline=None if last else self.pal["grid"], ow=2)
            blit(im, box, x, y, p, anchor="lm")
            num = text_img("✓" if False else str(i + 1), "head", 60, fill="#120018" if last else self.pal["a1"])
            blit(im, num, x + 55, y, p)
            txt = text_img(it, "bold", 50, fill="#120018" if last else "#ffffff")
            blit(im, txt, x + 110, y, p, anchor="lm")

    def s_text(self, im, sc, lt, t):
        self.header(im, sc["head"], lt)
        its = self.items_until(sc, lt)
        if not its:
            return
        ti, it = its[-1]
        p = ease_back(prog(lt, ti, 0.5))
        img = text_img(it.upper(), "head", 140, fill="#ffffff", stroke=4, stroke_fill="#120018", glow=self.pal["grid"], glow_r=20, maxw=1500)
        blit(im, img, W / 2, 520, min(1, p * 1.4), scale=0.75 + 0.25 * p)
        # index dots
        n = len(sc["items"])
        for i in range(n):
            col = self.pal["a1"] if i == len(its) - 1 else "#ffffff"
            blit(im, glow_circle(9, col, 6), W / 2 + (i - (n - 1) / 2) * 40, 800, 0.9 if i < len(its) else 0.3)

    def s_compare(self, im, sc, lt, t):
        pl = ease_out(prog(lt, 0.1, 0.5))
        for side, label, cx, col in (("L", sc["left"], 520, self.pal["a2"]), ("R", sc["right"], 1400, self.pal["a1"])):
            panel = pill(760, 560, "#000000", 160, radius=30, outline=col, ow=4)
            dx = (-1 if side == "L" else 1) * 200 * (1 - pl)
            blit(im, panel, cx + dx, 500, pl)
            lab = text_img(label, "head", 100, fill=col, glow="#000000", glow_r=8)
            blit(im, lab, cx + dx, 290, pl)
        vs = text_img("VS", "head", 90, fill="#ffffff", glow=self.pal["grid"], glow_r=16)
        pv = ease_back(prog(lt, 0.4, 0.4))
        blit(im, glow_circle(70, "#120018", 10), W / 2, 500, pv)
        blit(im, vs, W / 2, 500, pv, scale=0.5 + 0.5 * pv)
        rows = {"L": 0, "R": 0}
        for ti, it in self.items_until(sc, lt):
            side, text = it
            p = ease_back(prog(lt, ti, 0.45))
            if side == "B":
                img = text_img(text, "bold", 46, fill="#120018")
                blit(im, pill(img.width + 60, 86, self.pal["a1"]), W / 2, 845, p, scale=0.6 + 0.4 * p)
                blit(im, img, W / 2, 845, p, scale=0.6 + 0.4 * p)
                continue
            cx = 520 if side == "L" else 1400
            y = 420 + rows[side] * 150
            rows[side] += 1
            size = 74 if "USD" in text else 54
            img = text_img(text, "head" if "USD" in text else "bold", size, fill="#ffffff", maxw=640)
            blit(im, img, cx, y, min(1, p * 1.3), scale=0.7 + 0.3 * p)

    def s_timeline(self, im, sc, lt, t):
        self.header(im, sc["head"], lt)
        items = sc["items"]
        n = len(items)
        x0, x1, y = 200, 1720, 470
        xs = [x0 + (x1 - x0) * (i / (n - 1) if n > 1 else 0.5) for i in range(n)]
        d = ImageDraw.Draw(im)
        d.rectangle((x0, y - 4, x1, y + 4), fill=(255, 255, 255, 70))
        its = self.items_until(sc, lt)
        if its:
            k = len(its) - 1
            ti = its[-1][0]
            prev_x = xs[k - 1] if k > 0 else x0
            fill_x = prev_x + (xs[k] - prev_x) * ease_out(prog(lt, ti, 0.5))
            d.rectangle((x0, y - 4, fill_x, y + 4), fill=hexrgb(self.pal["a1"]))
        for i, (ti, it) in enumerate(items):
            on = ti <= lt
            active = on and i == len(its) - 1
            p = ease_back(prog(lt, ti, 0.4)) if on else 0
            blit(im, glow_circle(12, "#ffffff", 4), xs[i], y, 0.35)
            if on:
                blit(im, glow_circle(22 if active else 14, self.pal["a1"] if active else self.pal["grid"], 10), xs[i], y, 1, scale=0.4 + 0.6 * p)
                dl = text_img(it[0], "head", 44 if n > 4 else 54, fill="#ffffff" if active else "#bbbbbb")
                blit(im, dl, xs[i], y - 70, p if active else 0.7)
        if its:
            ti, it = its[-1]
            p = ease_back(prog(lt, ti, 0.5))
            big = text_img(it[0], "head", 120, fill=self.pal["a1"], glow="#000000", glow_r=10)
            blit(im, big, W / 2, 640, min(1, p * 1.3), scale=0.7 + 0.3 * p)
            txt = text_img(it[1], "bold", 58, fill="#ffffff", maxw=1400)
            pt = ease_out(prog(lt, ti + 0.2, 0.4))
            blit(im, txt, W / 2, 770 + 20 * (1 - pt), pt)

    def s_map(self, im, sc, lt, t):
        pm = ease_out(prog(lt, 0.0, 0.6))
        blit(im, map_base(self.v["hue"]), W / 2 + 200 * (1 - pm), H / 2, pm)
        its = self.items_until(sc, lt)
        cur = its[-1][1] if its else None
        seen = []
        for _, k in its:
            if k not in seen:
                seen.append(k)
        for key, (name, tag, pos) in REGIONS.items():
            x, y = map_xy(pos)
            if key == cur:
                continue
            blit(im, glow_circle(7, "#ffffff" if key in seen else "#777777", 4), x, y, 0.8)
            lb = text_img(name, "semi", 22, fill="#ffffff")
            blit(im, lb, x, y + 26, 0.75 if key in seen else 0.4)
        if cur:
            ti = its[-1][0]
            first_t = next(tt for tt, k in sc["items"] if k == cur)
            name, tag, pos = REGIONS[cur]
            x, y = map_xy(pos)
            p = ease_back(prog(lt, first_t, 0.5))
            for j in range(2):
                ph = ((lt * 0.8 + j * 0.5) % 1.0)
                blit(im, ring(int(30 + 90 * ph), self.pal["a1"], 5, 6), x, y, (1 - ph) * p)
            blit(im, glow_circle(16, self.pal["a1"], 12), x, y, 1, scale=0.3 + 0.7 * p)
            # left panel
            idx = list(REGIONS).index(cur) + 1
            zone = text_img(f"ZONA {idx}/6", "bold", 40, fill=self.pal["a2"])
            blit(im, zone, 140, 330, p, anchor="lm")
            nm = text_img(name, "head", 130, fill="#ffffff", glow=self.pal["grid"], glow_r=16, maxw=820, align="left")
            blit(im, nm, 140 - 60 * (1 - p), 450, min(1, p * 1.3), anchor="lm")
            tg = text_img(tag, "bold", 44, fill="#120018")
            pt = ease_out(prog(lt, first_t + 0.25, 0.4))
            blit(im, pill(tg.width + 50, 84, self.pal["a1"]), 140, 590, pt, anchor="lm")
            blit(im, tg, 165, 590, pt, anchor="lm")

    def s_char(self, im, sc, lt, t):
        its = self.items_until(sc, lt)
        if not its:
            return
        ti, (name, role, idx) = its[-1]
        p = ease_back(prog(lt, ti, 0.6))
        kinds = ["m", "f", "m", "m", "m", "duo", "m", "m"]
        cols = [("#ff2f92", "#2b0a3d"), ("#ffb347", "#5a0f3c"), ("#3dd6d0", "#0a2540"), ("#ffd23f", "#3a1200"),
                ("#9b5de5", "#140a3d"), ("#ff5c8a", "#2a0030"), ("#ff7b00", "#2a0a00"), ("#00e5ff", "#00203a")]
        c1, c2 = cols[idx % 8]
        card = silhouette(kinds[idx % 8], c1, c2)
        blit(im, card, 520 - 300 * (1 - p), 500, min(1, p * 1.5), scale=0.85 + 0.15 * p)
        num = text_img(f"{idx + 1:02d}/08", "head", 60, fill=c1)
        blit(im, num, 900, 250, p, anchor="lm")
        nm = text_img(name, "head", 120, fill="#ffffff", glow=c1, glow_r=16, maxw=960, align="left")
        pn = ease_out(prog(lt, ti + 0.15, 0.5))
        blit(im, nm, 900 + 80 * (1 - pn), 420, pn, anchor="lm")
        rl = text_img(role, "bold", 44, fill="#120018")
        pr = ease_out(prog(lt, ti + 0.35, 0.4))
        blit(im, pill(rl.width + 50, 84, c1), 900, 590, pr, anchor="lm")
        blit(im, rl, 925, 590, pr, anchor="lm")
        note = text_img("Ilustración del canal", "semi", 24, fill="#ffffff")
        blit(im, note, 520, 870, 0.5 * p)

    def s_outro(self, im, sc, lt, t):
        p = ease_back(prog(lt, 0.1, 0.6))
        title = text_img("¿NOS VEMOS EN LEONIDA?", "head", 120, fill="#ffffff", glow=self.pal["grid"], glow_r=20)
        blit(im, title, W / 2, 300, min(1, p * 1.3), scale=0.8 + 0.2 * p)
        click_t = 2.6
        subscribed = lt > click_t
        btn_col = "#cc0000" if not subscribed else "#444444"
        label = "SUSCRÍBETE" if not subscribed else "SUSCRITO"
        bt = text_img(label, "head", 80, fill="#ffffff")
        pulse = 1 + (0.04 * math.sin(lt * 6) if not subscribed else 0)
        pb = ease_back(prog(lt, 0.5, 0.5))
        press = 0.92 if click_t < lt < click_t + 0.15 else 1.0
        blit(im, pill(560, 140, btn_col), W / 2, 540, pb, scale=(0.6 + 0.4 * pb) * pulse * press)
        blit(im, bt, W / 2, 540, pb, scale=(0.6 + 0.4 * pb) * pulse * press)
        # cursor
        if lt > 1.3:
            pc = ease_out(prog(lt, 1.3, 1.2))
            cx = 1500 + (W / 2 + 120 - 1500) * pc
            cy = 900 + (560 - 900) * pc
            d = ImageDraw.Draw(im)
            d.polygon([(cx, cy), (cx, cy + 60), (cx + 16, cy + 46), (cx + 30, cy + 74), (cx + 40, cy + 69), (cx + 27, cy + 42), (cx + 46, cy + 42)],
                      fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
        sub = text_img("Nuevo video de GTA 6 cada día", "bold", 46, fill="#ffffff")
        ps = ease_out(prog(lt, 0.9, 0.5))
        blit(im, sub, W / 2, 720, ps)


def chunk_subs(a, b, text, maxc=44):
    words = text.split()
    chunks, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if len(t) > maxc and cur:
            chunks.append(cur); cur = w
        else:
            cur = t
        if cur.endswith((".", "?", "!", ":")) and len(cur) > 18:
            chunks.append(cur); cur = ""
    if cur:
        chunks.append(cur)
    total = sum(len(c) + 4 for c in chunks)
    out, t = [], a
    for c in chunks:
        d = (b - a) * (len(c) + 4) / total
        out.append((t, t + d, c)); t += d
    return out
