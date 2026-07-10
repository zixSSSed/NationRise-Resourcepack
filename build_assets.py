# -*- coding: utf-8 -*-
"""Генерация бренд-ассетов NationRise: логотип (эмблема+вордмарк) и иконки-глифы для ресурспака."""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
LOGODIR = os.path.join(ROOT, "logo")
GLYPHDIR = os.path.join(ROOT, "pack", "assets", "minecraft", "textures", "font")
os.makedirs(LOGODIR, exist_ok=True)
os.makedirs(GLYPHDIR, exist_ok=True)

# ---- палитра ----
DEEP   = (77, 34, 178)
DEEP2  = (58, 26, 138)
PUR_HI = (122, 74, 224)   # светлее для верха градиента бейджа
PURPLE = (140, 91, 232)
LILAC  = (201, 184, 242)
CREAM  = (247, 250, 219)
CREAM2 = (216, 219, 184)
WHITE  = (255, 255, 255)

LOGO_FONT = os.path.join(LOGODIR, "nationrise-logo.ttf")

# ======================================================================
# ОБЩИЕ ХЕЛПЕРЫ
# ======================================================================
def supersample(draw_fn, size, ss=4):
    """Рисует draw_fn(d, S) в RGBA на холсте size*ss и уменьшает до size (сглаживание)."""
    S = size * ss
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_fn(d, S)
    return img.resize((size, size), Image.LANCZOS)

def mask_icon(draw_fn, size=128, ss=4, color=WHITE):
    """Монохромная иконка: маска (255 — заливка, 0 — вырез), потом красим в color."""
    S = size * ss
    m = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(m)
    draw_fn(md, S)
    m = m.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (*color, 0))
    out.paste(color, (0, 0), m)
    out.putalpha(m)
    return out

def crown_points(x, y, w, h):
    """Силуэт короны (3 зубца) в прямоугольнике (x,y,w,h)."""
    def px(fx): return x + fx * w
    def py(fy): return y + fy * h
    return [
        (px(0.00), py(0.60)),
        (px(0.13), py(0.16)),
        (px(0.31), py(0.50)),
        (px(0.50), py(0.00)),
        (px(0.69), py(0.50)),
        (px(0.87), py(0.16)),
        (px(1.00), py(0.60)),
        (px(1.00), py(1.00)),
        (px(0.00), py(1.00)),
    ]

# ======================================================================
# ЛОГОТИП
# ======================================================================
def vgradient(w, h, top, bot):
    g = Image.new("RGB", (1, h))
    for j in range(h):
        t = j / max(1, h - 1)
        g.putpixel((0, j), tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3)))
    return g.resize((w, h))

def hgradient_rgba(w, h, left, right):
    g = Image.new("RGBA", (w, 1))
    for i in range(w):
        t = i / max(1, w - 1)
        g.putpixel((i, 0), tuple(int(left[k] + (right[k] - left[k]) * t) for k in range(3)) + (255,))
    return g.resize((w, h))

def rounded_mask(w, h, rad, ss=4):
    m = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=rad * ss, fill=255)
    return m.resize((w, h), Image.LANCZOS)

def draw_crown_color(base, x, y, w, h, fill=CREAM, gem=DEEP):
    """Цветная корона с камнями (для эмблемы), supersample."""
    layer = supersample(lambda d, S: _crown(d, S, fill, gem), max(w, h))
    layer = layer.resize((w, h), Image.LANCZOS)
    base.alpha_composite(layer, (int(x), int(y)))

def _crown(d, S, fill, gem):
    pad = S * 0.04
    pts = crown_points(pad, pad, S - 2 * pad, S - 2 * pad)
    d.polygon(pts, fill=fill)
    # лента-основание
    by0 = pad + (S - 2 * pad) * 0.60
    by1 = pad + (S - 2 * pad) * 0.80
    d.rectangle([pad, by0, S - pad, by1], fill=fill)
    # камни на зубцах
    r = S * 0.06
    for fx, fy in [(0.13, 0.16), (0.50, 0.02), (0.87, 0.16)]:
        cx = pad + (S - 2 * pad) * fx
        cy = pad + (S - 2 * pad) * fy + r
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=gem)
    # камни на ленте
    r2 = S * 0.05
    midy = (by0 + by1) / 2
    for fx in (0.27, 0.5, 0.73):
        cx = pad + (S - 2 * pad) * fx
        d.ellipse([cx - r2, midy - r2, cx + r2, midy + r2], fill=gem)

def build_emblem(size=512):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    rad = int(size * 0.22)
    # бейдж с вертикальным градиентом
    grad = vgradient(size, size, PUR_HI, DEEP2).convert("RGBA")
    mask = rounded_mask(size, size, rad)
    img.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(img)
    # двойная кремовая рамка
    inset = int(size * 0.055)
    d.rounded_rectangle([inset, inset, size - inset, size - inset],
                        radius=int(rad * 0.7), outline=CREAM, width=max(2, int(size * 0.016)))
    inset2 = int(size * 0.085)
    d.rounded_rectangle([inset2, inset2, size - inset2, size - inset2],
                        radius=int(rad * 0.55), outline=(*LILAC, 150), width=max(1, int(size * 0.006)))
    # корона
    cw = int(size * 0.52)
    ch = int(size * 0.40)
    draw_crown_color(img, (size - cw) / 2, size * 0.18, cw, ch, fill=CREAM, gem=DEEP)
    # монограмма NR
    try:
        f = ImageFont.truetype(LOGO_FONT, int(size * 0.30))
    except Exception:
        f = ImageFont.load_default()
    txt = "NR"
    tb = d.textbbox((0, 0), txt, font=f)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    tx = (size - tw) / 2 - tb[0]
    ty = size * 0.60 - tb[1]
    d.text((tx, ty), txt, font=f, fill=CREAM)
    return img

def gradient_text(text, font, pad=20):
    tmp = Image.new("RGBA", (10, 10))
    td = ImageDraw.Draw(tmp)
    bb = td.textbbox((0, 0), text, font=font)
    w, h = bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2
    layer = Image.new("L", (w, h), 0)
    ld = ImageDraw.Draw(layer)
    ld.text((pad - bb[0], pad - bb[1]), text, font=font, fill=255)
    grad = hgradient_rgba(w, h, PURPLE, CREAM)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(grad, (0, 0), layer)
    out.putalpha(layer)
    return out

def build_wordmark():
    f = ImageFont.truetype(LOGO_FONT, 300)
    wm = gradient_text("NationRise", f, pad=30)
    # маленькая корона над «i»? Просто корона слева сверху для акцента — добавим эмблему отдельно в lockup.
    return wm

def build_lockup(emblem, wordmark):
    gap = 60
    eh = 460
    em = emblem.resize((eh, eh), Image.LANCZOS)
    scale = eh * 0.78 / wordmark.height
    wm = wordmark.resize((int(wordmark.width * scale), int(wordmark.height * scale)), Image.LANCZOS)
    W = em.width + gap + wm.width + 40
    H = max(em.height, wm.height) + 40
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(em, (20, (H - em.height) // 2))
    out.alpha_composite(wm, (20 + em.width + gap, (H - wm.height) // 2))
    return out

def on_dark(img, padfrac=0.16, bg=(21, 15, 31)):
    pad = int(max(img.size) * padfrac)
    out = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (*bg, 255))
    out.alpha_composite(img, (pad, pad))
    return out

# ======================================================================
# ИКОНКИ-ГЛИФЫ (монохром, белые — тонируются §-цветом в игре)
# ======================================================================
def g_crown(d, S):
    pad = S * 0.10
    d.polygon(crown_points(pad, pad + S * 0.05, S - 2 * pad, (S - 2 * pad) * 0.85), fill=255)
    by0 = pad + S * 0.05 + (S - 2 * pad) * 0.55
    by1 = by0 + (S - 2 * pad) * 0.22
    d.rectangle([pad, by0, S - pad, by1], fill=255)
    # вырез-камни на ленте
    r = S * 0.04
    midy = (by0 + by1) / 2
    for fx in (0.30, 0.5, 0.70):
        cx = pad + (S - 2 * pad) * fx
        d.ellipse([cx - r, midy - r, cx + r, midy + r], fill=0)

def g_crystal(d, S):
    cx, cy = S / 2, S / 2
    w, h = S * 0.32, S * 0.42
    d.polygon([(cx, cy - h), (cx + w, cy), (cx, cy + h), (cx - w, cy)], fill=255)
    # грани (вырезы тонкими линиями)
    d.line([(cx, cy - h), (cx, cy + h)], fill=0, width=max(1, int(S * 0.012)))
    d.line([(cx - w, cy), (cx + w, cy)], fill=0, width=max(1, int(S * 0.012)))

def g_sun(d, S):
    cx, cy = S / 2, S / 2
    r = S * 0.20
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    d.ellipse([cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55], fill=0)
    rl = S * 0.40
    for k in range(8):
        a = k * math.pi / 4
        x1, y1 = cx + math.cos(a) * r * 1.25, cy + math.sin(a) * r * 1.25
        x2, y2 = cx + math.cos(a) * rl, cy + math.sin(a) * rl
        d.line([(x1, y1), (x2, y2)], fill=255, width=max(2, int(S * 0.05)))

def g_house(d, S):
    cx = S / 2
    d.polygon([(cx, S * 0.16), (S * 0.86, S * 0.50), (S * 0.14, S * 0.50)], fill=255)  # крыша
    d.rectangle([S * 0.24, S * 0.48, S * 0.76, S * 0.86], fill=255)                    # стены
    d.rectangle([S * 0.43, S * 0.62, S * 0.57, S * 0.86], fill=0)                      # дверь

def g_star4(d, S):
    cx, cy = S / 2, S / 2
    o, i = S * 0.42, S * 0.14
    pts = []
    for k in range(8):
        a = -math.pi / 2 + k * math.pi / 4
        r = o if k % 2 == 0 else i
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    d.polygon(pts, fill=255)

def g_star5(d, S):
    cx, cy = S / 2, S / 2
    o, i = S * 0.42, S * 0.17
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        r = o if k % 2 == 0 else i
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    d.polygon(pts, fill=255)

def g_star_circle(d, S):
    cx, cy = S / 2, S / 2
    R = S * 0.44
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
    d.ellipse([cx - R * 0.82, cy - R * 0.82, cx + R * 0.82, cy + R * 0.82], fill=0)
    o, i = S * 0.30, S * 0.12
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        r = o if k % 2 == 0 else i
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    d.polygon(pts, fill=255)

def g_bank(d, S):
    # стопка монет
    cx = S / 2
    for k, yy in enumerate((0.66, 0.50, 0.34)):
        cy = S * (0.30 + 0.18 * k)
        d.ellipse([cx - S * 0.30, cy - S * 0.09, cx + S * 0.30, cy + S * 0.09], fill=255)
        d.ellipse([cx - S * 0.30, cy - S * 0.115, cx + S * 0.30, cy + S * 0.065], fill=255)
        d.ellipse([cx - S * 0.10, cy - S * 0.06, cx + S * 0.10, cy + S * 0.02], fill=0)

def g_flag(d, S):
    d.rectangle([S * 0.30, S * 0.14, S * 0.37, S * 0.88], fill=255)            # древко
    d.polygon([(S * 0.37, S * 0.16), (S * 0.84, S * 0.28), (S * 0.37, S * 0.46)], fill=255)  # полотно

def g_bolt(d, S):
    d.polygon([(S * 0.56, S * 0.10), (S * 0.30, S * 0.55), (S * 0.48, S * 0.55),
               (S * 0.40, S * 0.90), (S * 0.72, S * 0.40), (S * 0.52, S * 0.40)], fill=255)

def g_diamond(d, S):
    cx, cy = S / 2, S / 2
    r = S * 0.40
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=255)

def g_diamond_hollow(d, S):
    cx, cy = S / 2, S / 2
    r = S * 0.40
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=255)
    r2 = r * 0.55
    d.polygon([(cx, cy - r2), (cx + r2, cy), (cx, cy + r2), (cx - r2, cy)], fill=0)

def g_flower(d, S):
    cx, cy = S / 2, S * 0.52
    pr = S * 0.16
    for k in range(6):
        a = k * math.pi / 3
        px, py = cx + math.cos(a) * S * 0.22, cy + math.sin(a) * S * 0.22
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=255)
    d.ellipse([cx - S * 0.12, cy - S * 0.12, cx + S * 0.12, cy + S * 0.12], fill=0)

def g_florette(d, S):
    cx, cy = S / 2, S * 0.52
    pr = S * 0.13
    for k in range(8):
        a = k * math.pi / 4
        px, py = cx + math.cos(a) * S * 0.24, cy + math.sin(a) * S * 0.24
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=255)
    d.ellipse([cx - S * 0.10, cy - S * 0.10, cx + S * 0.10, cy + S * 0.10], fill=255)
    d.ellipse([cx - S * 0.045, cy - S * 0.045, cx + S * 0.045, cy + S * 0.045], fill=0)

def g_skull(d, S):
    cx = S / 2
    d.ellipse([cx - S * 0.30, S * 0.16, cx + S * 0.30, S * 0.66], fill=255)   # череп
    d.rectangle([cx - S * 0.20, S * 0.55, cx + S * 0.20, S * 0.78], fill=255) # челюсть
    d.ellipse([cx - S * 0.20, S * 0.34, cx - S * 0.04, S * 0.50], fill=0)     # глаз
    d.ellipse([cx + S * 0.04, S * 0.34, cx + S * 0.20, S * 0.50], fill=0)     # глаз
    d.polygon([(cx, S * 0.50), (cx - S * 0.05, S * 0.60), (cx + S * 0.05, S * 0.60)], fill=0)  # нос
    for off in (-0.12, 0, 0.12):
        d.line([(cx + off * S, S * 0.66), (cx + off * S, S * 0.80)], fill=0, width=max(1, int(S * 0.02)))

def g_snowflake(d, S):
    cx, cy = S / 2, S / 2
    L = S * 0.40
    w = max(2, int(S * 0.045))
    for k in range(6):
        a = k * math.pi / 3
        x2, y2 = cx + math.cos(a) * L, cy + math.sin(a) * L
        d.line([(cx, cy), (x2, y2)], fill=255, width=w)
        # ветви
        for t in (0.5, 0.78):
            bx, by = cx + math.cos(a) * L * t, cy + math.sin(a) * L * t
            for da in (-0.5, 0.5):
                d.line([(bx, by), (bx + math.cos(a + da) * L * 0.22, by + math.sin(a + da) * L * 0.22)],
                       fill=255, width=w)

def g_fire(d, S):
    cx = S / 2
    d.polygon([(cx, S * 0.10), (S * 0.74, S * 0.50), (S * 0.70, S * 0.74),
               (cx, S * 0.90), (S * 0.30, S * 0.74), (S * 0.26, S * 0.50)], fill=255)
    # внутренний вырез-пламя
    d.polygon([(cx, S * 0.40), (S * 0.60, S * 0.64), (cx, S * 0.80), (S * 0.40, S * 0.64)], fill=0)

def g_biohazard(d, S):
    cx, cy = S / 2, S / 2
    R = S * 0.16
    for k in range(3):
        a = -math.pi / 2 + k * 2 * math.pi / 3
        px, py = cx + math.cos(a) * S * 0.24, cy + math.sin(a) * S * 0.24
        d.ellipse([px - R, py - R, px + R, py + R], fill=255)
        d.ellipse([px - R * 0.45, py - R * 0.45, px + R * 0.45, py + R * 0.45], fill=0)
    d.ellipse([cx - S * 0.085, cy - S * 0.085, cx + S * 0.085, cy + S * 0.085], fill=255)
    d.ellipse([cx - S * 0.035, cy - S * 0.035, cx + S * 0.035, cy + S * 0.035], fill=0)

def g_yinyang(d, S):
    cx, cy = S / 2, S / 2
    R = S * 0.40
    d.pieslice([cx - R, cy - R, cx + R, cy + R], 90, 270, fill=255)   # левая половина белая
    d.ellipse([cx - R / 2, cy - R, cx + R / 2, cy], fill=255)         # верхний полукруг
    d.ellipse([cx - R / 2, cy, cx + R / 2, cy + R], fill=0)           # нижний вырез
    d.ellipse([cx - R * 0.12, cy - R * 0.62, cx + R * 0.12, cy - R * 0.38], fill=0)  # точка
    d.ellipse([cx - R * 0.12, cy + R * 0.38, cx + R * 0.12, cy + R * 0.62], fill=255)

# карта: имя файла -> функция
GLYPHS = {
    "nr_crown":   g_crown,
    "nr_crystal": g_crystal,
    "nr_sun":     g_sun,
    "nr_house":   g_house,
    "nr_star4":   g_star4,
    "nr_bank":    g_bank,
    "nr_flag":    g_flag,
    "nr_bolt":    g_bolt,
    "nr_diamond": g_diamond,
    "nr_diamond_hollow": g_diamond_hollow,
    "nr_star_circle": g_star_circle,
    "nr_star5":   g_star5,
    "nr_flower":  g_flower,
    "nr_florette": g_florette,
    "nr_skull":   g_skull,
    "nr_snowflake": g_snowflake,
    "nr_fire":    g_fire,
    "nr_biohazard": g_biohazard,
    "nr_yinyang": g_yinyang,
}

def build_glyphs(size=128):
    icons = {}
    for name, fn in GLYPHS.items():
        ic = mask_icon(fn, size=size)
        ic.save(os.path.join(GLYPHDIR, name + ".png"))
        icons[name] = ic
    return icons

def contact_sheet(icons):
    cols = 5
    cell = 96
    rows = (len(icons) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell, rows * cell), (21, 15, 31, 255))
    for idx, (name, ic) in enumerate(icons.items()):
        r, c = divmod(idx, cols)
        ic2 = ic.resize((64, 64), Image.LANCZOS)
        # тонируем в крем, как было бы §-цветом
        tint = Image.new("RGBA", ic2.size, (*CREAM, 0))
        tint.putalpha(ic2.split()[3])
        sheet.alpha_composite(tint, (c * cell + 16, r * cell + 16))
    return sheet

# ======================================================================
if __name__ == "__main__":
    emblem = build_emblem(512)
    emblem.save(os.path.join(LOGODIR, "emblem.png"))
    emblem.resize((128, 128), Image.LANCZOS).save(os.path.join(ROOT, "pack", "pack.png"))
    emblem.resize((64, 64), Image.LANCZOS).save(os.path.join(LOGODIR, "server-icon.png"))

    wm = build_wordmark()
    wm.save(os.path.join(LOGODIR, "wordmark.png"))
    lock = build_lockup(emblem, wm)
    lock.save(os.path.join(LOGODIR, "logo_lockup.png"))
    on_dark(lock, 0.12).save(os.path.join(LOGODIR, "logo_lockup_dark.png"))
    on_dark(emblem.resize((360, 360), Image.LANCZOS), 0.18).save(os.path.join(LOGODIR, "emblem_dark.png"))

    icons = build_glyphs(128)
    contact_sheet(icons).save(os.path.join(LOGODIR, "_icons_preview.png"))
    print("emblem, wordmark, lockup, server-icon, pack.png +", len(icons), "glyphs saved")
