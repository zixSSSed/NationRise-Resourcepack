# -*- coding: utf-8 -*-
"""
Плашки: фон, свой пиксельный шрифт 5×5 и значки-эмодзи внутрь плашки.

Что изменилось против первой версии
-----------------------------------
1. КРАЙ. Раньше боковинка была просто куском фона со срезанными углами, и плашка
   выглядела размытым пятном. В образце по краю идёт столбец на тон темнее, а угол
   ступенькой уходит внутрь — именно это даёт ей форму. Теперь боковинка шириной
   два пикселя и рисует ровно такой край, отдельно левая и правая.

2. ШРИФТ. Ванильные заглавные высотой 7 в плашке высотой 9 упираются в нижний край:
   поля сверху один пиксель, снизу ноль. Кириллица вдобавок шире латиницы, поэтому
   «ОКТАВИАН» раздувало плашку. Свой шрифт 5×5 садится посередине и уже примерно
   на пятую часть. Буквы лежат в приватной области, плагин подменяет символы сам.

3. ЗНАЧКИ. Внутрь плашки слева ставится маленькая иконка — корона, молния, щит,
   искра, силуэт, самоцвет. Ровно как в присланном образце. Значок рисуется своим
   цветом, поэтому золотая корона остаётся золотой на красной плашке.

Фон по-прежнему серый: цвет текста в Minecraft умножается на текстуру, поэтому
одна и та же плашка красится в любой оттенок без перерисовки пака.

Запуск: py -3.13 build_plaques.py  (после него pack_zip.py)
"""
import os, json, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plaque_font_data import GLYPHS

ROOT = os.path.dirname(os.path.abspath(__file__))
MC = os.path.join(ROOT, "pack", "assets", "minecraft")
FONTTEX = os.path.join(MC, "textures", "font")
DEFAULT = os.path.join(MC, "font", "default.json")
os.makedirs(FONTTEX, exist_ok=True)

H = 9              # высота плашки, 1:1 без увеличения и сглаживания
SPLIT = 5          # с этой строки начинается тёмная полоса
TOP = 255          # светлая полоса
BOT = 194          # тёмная: те же 76% от светлой, что в образце
EDGE = 194         # боковой край — тон тёмной полосы
CORNER = 142       # угловой пиксель, ещё темнее (в образце 0.56 от светлого)

# ---------------------------------------------------------------- фон


def band(w):
    """Полоса фона шириной w: светлый верх, тёмный низ."""
    im = Image.new("RGBA", (w, H), (0, 0, 0, 0))
    px = im.load()
    for y in range(H):
        v = TOP if y < SPLIT else BOT
        for x in range(w):
            px[x, y] = (v, v, v, 255)
    return im


def cap(left=True):
    """
    Боковинка шириной 2 пикселя.

    Внешний столбец — тёмный край без верхнего и нижнего пикселя, внутренний —
    обычная полоса, у которой верхний пиксель затемнён до края, а нижний до угла.
    Вместе это и даёт скругление: не радиус, а ступенька в один пиксель.
    """
    im = Image.new("RGBA", (2, H), (0, 0, 0, 0))
    px = im.load()
    outer, inner = (0, 1) if left else (1, 0)
    for y in range(1, H - 1):
        v = CORNER if y == H - 2 else EDGE
        px[outer, y] = (v, v, v, 255)
    for y in range(H):
        if y == 0:
            v = EDGE
        elif y == H - 1:
            v = CORNER
        else:
            v = TOP if y < SPLIT else BOT
        px[inner, y] = (v, v, v, 255)
    return im


FILLS = [(1, 0xE03D), (2, 0xE03F), (4, 0xE040), (8, 0xE041), (16, 0xE042)]
CAP_L, CAP_R = 0xE03C, 0xE03E

parts = []
cap(True).save(os.path.join(FONTTEX, "nr_pill_capl.png"))
cap(False).save(os.path.join(FONTTEX, "nr_pill_capr.png"))
parts.append(("nr_pill_capl", CAP_L, 8, H))
parts.append(("nr_pill_capr", CAP_R, 8, H))
for w, cp in FILLS:
    band(w).save(os.path.join(FONTTEX, "nr_pill_%d.png" % w))
    parts.append(("nr_pill_%d" % w, cp, 8, H))

# ---------------------------------------------------------------- значки
# Рисуются в клетке высотой 9 с тем же ascent, что и плашка, поэтому садятся в неё
# без подгонки. Чернила занимают строки 1..7 — по пикселю поля сверху и снизу.

ICONS = {
    "crown": [
        "#..#..#",
        "##.#.##",
        "#######",
        "#######",
        ".#####.",
    ],
    "bolt": [
        "..##",
        ".##.",
        "##..",
        "####",
        "..##",
        ".##.",
        "##..",
    ],
    # Щит и искра сперва были контурными и в девяти пикселях рассыпались: щит читался
    # как галочка, а восьмилучевая искра — как буква Ж. Мелкий значок должен быть
    # сплошным пятном, иначе на таком размере от него остаётся шум.
    "shield": [
        "#####",
        "#####",
        "#####",
        "#####",
        ".###.",
        ".###.",
        "..#..",
    ],
    "spark": [
        "..#..",
        "..#..",
        ".###.",
        "#####",
        ".###.",
        "..#..",
        "..#..",
    ],
    "bust": [
        ".###.",
        ".###.",
        "..#..",
        "#####",
        "#####",
        "#####",
        "#####",
    ],
    "gem": [
        "..###..",
        ".#####.",
        "#######",
        ".#####.",
        "..###..",
        "...#...",
    ],
    "star": [
        "...#...",
        "..###..",
        "#######",
        ".#####.",
        "..###..",
        ".##.##.",
        "#.....#",
    ],
    # Линия инспекторов. Сперва тут была лупа, но в семи пикселях круг с хвостиком
    # читался ровно как буква Q и вставал прямо перед подписью «α-INSP» — выходило
    # слово, а не значок. Галочка на таком размере ни с одной буквой не путается.
    "check": [
        ".....##",
        "....##.",
        "...##..",
        "#..##..",
        "####...",
        ".##....",
    ],
}

# Порядок задан явно и менять его нельзя: коды зашиты в Plaque.java. Раньше здесь
# стоял sorted(), и добавление одного значка сдвигало коды всем остальным — корона
# молча становилась галочкой.
ICON_ORDER = ["bolt", "bust", "crown", "gem", "shield", "spark", "star", "check"]
assert set(ICON_ORDER) == set(ICONS), "значок добавлен, но не вписан в ICON_ORDER"

ICON_CP = {}
cp = 0xE0A0
for name in ICON_ORDER:
    rows = ICONS[name]
    w = max(len(r) for r in rows)
    im = Image.new("RGBA", (w, H), (0, 0, 0, 0))
    px = im.load()
    top = (H - len(rows)) // 2            # по центру плашки
    for y, row in enumerate(rows):
        for x, chx in enumerate(row):
            if chx == "#":
                px[x, top + y] = (255, 255, 255, 255)
    im.save(os.path.join(FONTTEX, "nr_plq_%s.png" % name))
    parts.append(("nr_plq_%s" % name, cp, 8, H))
    ICON_CP[name] = cp
    cp += 1

# ---------------------------------------------------------------- шрифт 5×5
# Один атлас-сетка вместо семидесяти файлов: так же, как это делает сама игра.
# Клетка 6×8. Чернила — верхние 5 строк, остальное пусто: ascent обязан быть не
# больше height, иначе игра отказывается грузить провайдер.

CELL_W, CELL_H, INK_H = 6, 8, 5
FONT_BASE = 0xE200
order = [c for c in GLYPHS]
cols = 16
rows = (len(order) + cols - 1) // cols
atlas = Image.new("RGBA", (cols * CELL_W, rows * CELL_H), (0, 0, 0, 0))
ap = atlas.load()
adv = {}
grid = []
for r in range(rows):
    line = ""
    for c in range(cols):
        i = r * cols + c
        if i >= len(order):
            line += chr(0)      # пустая клетка сетки помечается NUL
            continue
        chx = order[i]
        line += chr(FONT_BASE + i)
        pat = GLYPHS[chx]
        ink = 0
        for y, row in enumerate(pat):
            for x, s in enumerate(row):
                if s == "#":
                    ap[c * CELL_W + x, r * CELL_H + y] = (255, 255, 255, 255)
                    ink = max(ink, x + 1)
        adv[chx] = ink + 1            # игра считает так же: ширина чернил плюс пиксель
    grid.append(line)
atlas.save(os.path.join(FONTTEX, "nr_plq_font.png"))

# ---------------------------------------------------------------- default.json

data = json.load(open(DEFAULT, encoding="utf-8"))
keep = [p for p in data["providers"]
        if not any(str(p.get("file", "")).startswith(x)
                   for x in ("minecraft:font/nr_pill_", "minecraft:font/nr_rank_",
                             "minecraft:font/nr_plq_"))]
ti = next((i for i, p in enumerate(keep)
           if p.get("type") == "reference" and "space" not in str(p.get("id", ""))), len(keep))
new = [{"type": "bitmap", "file": "minecraft:font/%s.png" % fid,
        "ascent": asc, "height": ht, "chars": [chr(c)]} for fid, c, asc, ht in parts]
new.append({"type": "bitmap", "file": "minecraft:font/nr_plq_font.png",
            "ascent": 6, "height": CELL_H, "chars": grid})
keep[ti:ti] = new
data["providers"] = keep
json.dump(data, open(DEFAULT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

for f in os.listdir(FONTTEX):
    if f.startswith("nr_rank_") or f == "nr_pill_cap.png":
        os.remove(os.path.join(FONTTEX, f))

# ---------------------------------------------------------------- для Plaque.java

print("фон:      левая/правая боковинки + куски 1/2/4/8/16")
print("значки:   " + ", ".join("%s=U+%04X" % (n, c) for n, c in ICON_CP.items()))
print("шрифт:    %d глифов, атлас %dx%d, база U+%04X" % (len(order), atlas.width, atlas.height, FONT_BASE))
print()
print("--- вставить в Plaque.java ---")
print('    private static final String FONT_CHARS = "%s";'
      % "".join(order).replace("\\", "\\\\").replace('"', '\\"'))
print('    private static final String FONT_ADV   = "%s";'
      % "".join("\\u%04x" % adv[c] for c in order))
print("    // значки:")
for n, c in ICON_CP.items():
    print("    public static final char ICON_%s = '\\u%04x';" % (n.upper(), c))
