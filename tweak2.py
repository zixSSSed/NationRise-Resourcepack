# -*- coding: utf-8 -*-
import os, math, json
from PIL import Image, ImageDraw
from fontTools import ttLib
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(ROOT, "pack", "assets", "minecraft")
FONTDIR = os.path.join(PACK, "font")
GLYPHDIR = os.path.join(PACK, "textures", "font")
INC = os.path.join(ROOT, "incoming")

# ---------- 1. шрифт Montserrat 650 ----------
f = ttLib.TTFont(os.path.join(ROOT, "_mont_var.ttf"))
instantiateVariableFont(f, {"wght": 650}, inplace=True)
f.save(os.path.join(FONTDIR, "nationrise.ttf"))
print("font -> Montserrat 650 (is_variable=%s)" % ("fvar" in f))

# ---------- 2. лого: чистый ре-экспорт + ширина <=256 ----------
logo = Image.open(os.path.join(INC, "Logo.png")).convert("RGBA")
logo = logo.crop(logo.getbbox())
if logo.width > 256:
    h = round(256 * logo.height / logo.width)
    logo = logo.resize((256, h), Image.LANCZOS)
clean = Image.new("RGBA", logo.size, (0, 0, 0, 0))
clean.putdata(list(logo.getdata()))   # без icc/метаданных
clean.save(os.path.join(GLYPHDIR, "nr_logo.png"))
print("nr_logo re-export:", clean.size)

# ---------- 3. иконки-глифы (монохром, белые) ----------
def mask_icon(fn, size=128, ss=4):
    S = size * ss
    m = Image.new("L", (S, S), 0)
    fn(ImageDraw.Draw(m), S)
    m = m.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    out.putalpha(m)
    return out

def g_coin(d, S):
    cx, cy = S / 2, S / 2
    r = S * 0.40
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    rr = S * 0.30
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=0, width=int(S * 0.04))
    o, i = S * 0.15, S * 0.055
    pts = []
    for k in range(8):
        a = -math.pi / 2 + k * math.pi / 4
        rad = o if k % 2 == 0 else i
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    d.polygon(pts, fill=0)

def g_bank(d, S):
    d.polygon([(S * 0.50, S * 0.12), (S * 0.91, S * 0.35), (S * 0.09, S * 0.35)], fill=255)  # фронтон
    d.rectangle([S * 0.11, S * 0.35, S * 0.89, S * 0.43], fill=255)                          # архитрав
    cols = 4
    x0, x1 = S * 0.17, S * 0.83
    cw = (x1 - x0) / (cols * 2 - 1)
    x = x0
    for _ in range(cols):
        d.rectangle([x, S * 0.45, x + cw, S * 0.78], fill=255)
        x += cw * 2
    d.rectangle([S * 0.09, S * 0.78, S * 0.91, S * 0.88], fill=255)                          # стилобат

def g_medal(d, S):
    d.polygon([(S * 0.37, S * 0.12), (S * 0.52, S * 0.42), (S * 0.31, S * 0.48)], fill=255)  # лента
    d.polygon([(S * 0.63, S * 0.12), (S * 0.48, S * 0.42), (S * 0.69, S * 0.48)], fill=255)
    cx, cy, r = S * 0.5, S * 0.63, S * 0.26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)                                    # медаль
    o, i = S * 0.155, S * 0.065
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rad = o if k % 2 == 0 else i
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    d.polygon(pts, fill=0)                                                                   # звезда-вырез

mask_icon(g_coin).save(os.path.join(GLYPHDIR, "nr_sun.png"))     # баланс
mask_icon(g_bank).save(os.path.join(GLYPHDIR, "nr_bank.png"))    # банк
mask_icon(g_medal).save(os.path.join(GLYPHDIR, "nr_badge.png"))  # должность
# превью
sheet = Image.new("RGBA", (3 * 96, 96), (21, 15, 31, 255))
for idx, fn in enumerate([g_coin, g_bank, g_medal]):
    ic = mask_icon(fn).resize((64, 64), Image.LANCZOS)
    tint = Image.new("RGBA", ic.size, (247, 250, 219, 0)); tint.putalpha(ic.split()[3])
    sheet.alpha_composite(tint, (idx * 96 + 16, 16))
sheet.save(os.path.join(ROOT, "logo", "_new_icons_preview.png"))

# ---------- 4. default.json (детерминированно, + nr_badge ⚜) ----------
LOGO_CP = 0xE010
icons = [
    ("nr_crown", 0x265B, 7, 11), ("nr_crystal", 0x2756, 7, 10), ("nr_sun", 0x2600, 7, 10),
    ("nr_house", 0x2302, 7, 10), ("nr_star4", 0x2726, 7, 10), ("nr_bank", 0x26C1, 7, 10),
    ("nr_flag", 0x2691, 7, 10), ("nr_bolt", 0x26A1, 7, 11), ("nr_diamond", 0x25C6, 6, 9),
    ("nr_diamond_hollow", 0x25C7, 6, 9), ("nr_star_circle", 0x272A, 7, 10), ("nr_star5", 0x2605, 7, 10),
    ("nr_flower", 0x273F, 7, 10), ("nr_florette", 0x2740, 7, 10), ("nr_skull", 0x2620, 7, 10),
    ("nr_snowflake", 0x2744, 7, 10), ("nr_fire", 0x1F525, 7, 11), ("nr_biohazard", 0x2623, 7, 10),
    ("nr_yinyang", 0x262F, 7, 10), ("nr_badge", 0x269C, 7, 10),
]
providers = [
    {"type": "reference", "id": "minecraft:include/space"},
    {"type": "bitmap", "file": "minecraft:font/nr_logo.png", "ascent": 15, "height": 18, "chars": [chr(LOGO_CP)]},
]
for name, cp, asc, h in icons:
    providers.append({"type": "bitmap", "file": f"minecraft:font/{name}.png", "ascent": asc, "height": h, "chars": [chr(cp)]})
# Keep the vanilla Minecraft text face. NationRise wordmarks, symbols and GUI
# backgrounds are bitmap providers above and do not require a global TTF.
providers.append({"type": "reference", "id": "minecraft:include/default"})
json.dump({"providers": providers}, open(os.path.join(FONTDIR, "default.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("default.json rebuilt (+nr_badge U+269C, logo h18/asc15)")
