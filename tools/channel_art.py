"""Banner (2560x1440) y avatar (800x800) del canal."""
import os
from PIL import Image
import render as R
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(ROOT, "canal"); os.makedirs(out, exist_ok=True)
pal = R.PALETTES["sunset"]
bg, _ = R.make_background("sunset", seed=11)
b = Image.fromarray(bg[0]).resize((2560, 1440), Image.LANCZOS).convert("RGBA")
t = R.text_img("MODO LEONIDA", "head", 220, fill="#ffffff", stroke=6, stroke_fill="#120018", glow=pal["grid"], glow_r=26)
b.alpha_composite(t, (1280 - t.width // 2, 720 - t.height // 2 - 40))
s = R.text_img("NOTICIAS · GUÍAS · SECRETOS DE GTA 6", "bold", 54, fill="#ffffff", stroke=4, stroke_fill="#000000")
b.alpha_composite(s, (1280 - s.width // 2, 860 - s.height // 2))
b.convert("RGB").save(os.path.join(out, "banner_2560x1440.jpg"), quality=92)
a = Image.fromarray(bg[0]).crop((560, 0, 1640, 1080)).resize((800, 800), Image.LANCZOS).convert("RGBA")
m = R.text_img("ML", "head", 400, fill="#ffffff", stroke=8, stroke_fill="#120018", glow=pal["grid"], glow_r=30)
a.alpha_composite(m, (400 - m.width // 2, 420 - m.height // 2))
a.convert("RGB").save(os.path.join(out, "avatar_800x800.png"))
print("ok")
