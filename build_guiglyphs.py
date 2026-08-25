# -*- coding: utf-8 -*-
"""GUI-глифы: превращает эмодзи/символы в названиях и заголовках меню в чистые
белые монохром-иконки (тонируются §-цветом плагина → правок Java НЕ нужно).
Источник: Segoe UI Symbol (монохром) где есть глиф, иначе Segoe UI Emoji (силуэт)."""
import os, json
from PIL import Image, ImageDraw, ImageFont
from fontTools import ttLib

ROOT = os.path.dirname(os.path.abspath(__file__))
MC = os.path.join(ROOT, "pack", "assets", "minecraft")
FONTTEX = os.path.join(MC, "textures", "font")
DEFAULT = os.path.join(MC, "font", "default.json")
os.makedirs(FONTTEX, exist_ok=True)

SEGUISYM = r"C:\Windows\Fonts\seguisym.ttf"
SEGUIEMJ = r"C:\Windows\Fonts\seguiemj.ttf"
sym_cmap = set(ttLib.TTFont(SEGUISYM).getBestCmap().keys())
try:
    emj_cmap = set(ttLib.TTFont(SEGUIEMJ).getBestCmap().keys())
except Exception:
    emj_cmap = set()

# (имя-файла, кодпоинт) — пиктограммы из GUI, которые стоит сделать глифами.
# Пропущены: математика (-, ~=, >=, inf), бары (block/shade/parallelogram),
# нав-стрелки/буллеты (tri/circle), кружки-цифры — они и так рендерятся в ваниль-шрифте.
GUI = [
    ("swords",   0x2694), ("anchor",   0x2693), ("hammerpick",0x2692),
    ("chains",   0x26D3), ("pickaxe",  0x26CF), ("noentry",  0x26D4),
    ("peace",    0x262E), ("warning",  0x26A0), ("gear",     0x2699),
    ("comet",    0x2604), ("envelope", 0x2709), ("heart",    0x2764),
    ("hourglass",0x231B), ("pause",    0x23F8), ("info",     0x2139),
    ("fishpole", 0x1F3A3),("trophy",   0x1F3C6),("construction",0x1F3D7),
    ("slot",     0x1F3B0),("key",      0x1F511),("shop",     0x1F3EA),
    ("blood",    0x1FA78),("package",  0x1F4E6),("worm",     0x1FAB1),
    ("web",      0x1F578),("squid",    0x1F991),("book",     0x1F4D6),
    ("crystalball",0x1F52E),("lock",   0x1F512),("compass",  0x1F9ED),
    ("lockkey",  0x1F510),("fish",     0x1F41F),("milkyway", 0x1F30C),
    ("masks",    0x1F3AD),("bread",    0x1F35E),("boom",     0x1F4A5),
    ("loud",     0x1F4E2),("cityscape",0x1F3D9),("trash",    0x1F5D1),
    ("gift",     0x1F381),("chart",    0x1F4CA),("wave",     0x1F44B),
    ("castle",   0x1F3F0),("moneybag", 0x1F4B0),("busts",    0x1F465),
    ("bust",     0x1F464),("earth",    0x1F30D),("die",      0x1F3B2),
    ("mute",     0x1F507),("magnify",  0x1F50D),("backpack", 0x1F392),
    ("gem",      0x1F48E),("sleep",    0x1F4A4),("medal1",   0x1F947),
    ("medal2",   0x1F948),("medal3",   0x1F949),("handshake",0x1F91D),
    ("check",    0x2705),
]

CANVAS = 144
def render_mono(cp):
    """Чёткий белый монохром из Segoe UI Symbol."""
    f = ImageFont.truetype(SEGUISYM, 116)
    im = Image.new("RGBA", (CANVAS, CANVAS), (0,0,0,0)); d = ImageDraw.Draw(im)
    ch = chr(cp); bb = d.textbbox((0,0), ch, font=f)
    w,h = bb[2]-bb[0], bb[3]-bb[1]
    d.text(((CANVAS-w)//2-bb[0], (CANVAS-h)//2-bb[1]), ch, font=f, fill=(255,255,255,255))
    return im

def render_silhouette(cp):
    """Белый силуэт из цветного Segoe UI Emoji (альфа→белый)."""
    f = ImageFont.truetype(SEGUIEMJ, 109)
    im = Image.new("RGBA", (CANVAS, CANVAS), (0,0,0,0)); d = ImageDraw.Draw(im)
    ch = chr(cp); bb = d.textbbox((0,0), ch, font=f, embedded_color=True)
    w,h = bb[2]-bb[0], bb[3]-bb[1]
    d.text(((CANVAS-w)//2-bb[0], (CANVAS-h)//2-bb[1]), ch, font=f, embedded_color=True)
    alpha = im.split()[3].point(lambda a: 255 if a > 64 else 0)
    out = Image.new("RGBA", im.size, (255,255,255,0)); out.putalpha(alpha)
    return out

def finalize(im, size=16):
    bbx = im.getbbox()
    if bbx: im = im.crop(bbx)
    side = max(max(im.size), 1)
    sq = Image.new("RGBA", (side,side), (0,0,0,0))
    sq.alpha_composite(im, ((side-im.width)//2, (side-im.height)//2))
    return sq.resize((size,size), Image.LANCZOS)

done = []; previews = []
for name, cp in GUI:
    try:
        if cp in sym_cmap:
            im = render_mono(cp)
        elif cp in emj_cmap:
            im = render_silhouette(cp)
        else:
            print("no glyph in either font:", name, hex(cp)); continue
        im = finalize(im)
        if not im.getbbox():
            print("empty render:", name, hex(cp)); continue
        im.save(os.path.join(FONTTEX, f"nr_gui_{name}.png"))
        done.append((name, cp)); previews.append((name, im))
    except Exception as e:
        print("skip", name, hex(cp), repr(e))

# ---- default.json (идемпотентно: убрать старые nr_gui_, вставить перед ttf) ----
data = json.load(open(DEFAULT, encoding="utf-8"))
provs = [p for p in data["providers"] if not p.get("file","").startswith("minecraft:font/nr_gui_")]
ti = next(i for i,p in enumerate(provs) if p.get("type")=="ttf")
ins = [{"type":"bitmap","file":f"minecraft:font/nr_gui_{name}.png","ascent":8,"height":10,"chars":[chr(cp)]} for name,cp in done]
provs[ti:ti] = ins; data["providers"] = provs
json.dump(data, open(DEFAULT,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

# ---- превью (крем-тон, чтобы белые силуэты были видны) ----
pad, cell = 10, 48
cols = 10; rows = (len(previews)+cols-1)//cols
sheet = Image.new("RGBA", (cols*(cell+pad)+pad, rows*(cell+pad)+pad), (28,22,38,255))
for i,(name,im) in enumerate(previews):
    g = im.resize((cell,cell), Image.NEAREST)
    tint = Image.new("RGBA", g.size, (0,0,0,0)); tint.putalpha(g.split()[3])
    tint.paste((247,250,219,255),(0,0),g.split()[3]); tint.putalpha(g.split()[3])
    r,c = divmod(i, cols)
    sheet.alpha_composite(tint, (pad+c*(cell+pad), pad+r*(cell+pad)))
sheet.save(os.path.join(ROOT, "logo", "_guiglyphs_preview.png"))
print(f"GUI glyphs: {len(done)}/{len(GUI)} done")
print("skipped (not in fonts):", [hex(cp) for n,cp in GUI if (n,cp) not in done])
