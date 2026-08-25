# -*- coding: utf-8 -*-
"""
Модели особых печей: три донатных и одна крафтовая.

Печь в инвентаре рисуется не плоским спрайтом, а кубом, поэтому модель наследуется от
minecraft:block/orientable и подменяет три текстуры — перед, бок и верх. Так предмет в
руке и в меню выглядит настоящей печью, только своей.

Текстуры собираются здесь же, попиксельно: брать ванильные и перекрашивать нельзя —
их нет в репозитории, а тащить ресурсы игры в свой пак не стоит. Камень поэтому
рисуется шумом с фиксированным зерном (одинаковый результат при каждом запуске),
а перед — тёмная топка со свечением своего цвета и значком сверху.

Запуск: py -3.13 build_furnaces.py  (после него pack_zip.py)
"""
import os, json, random
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
MC = os.path.join(ROOT, "pack", "assets", "minecraft")
TEX = os.path.join(MC, "textures", "block")
MODELS = os.path.join(MC, "models", "item")
ITEMS = os.path.join(MC, "items")
for d in (TEX, MODELS, ITEMS):
    os.makedirs(d, exist_ok=True)

S = 16

# id -> (CMD, цвет свечения, цвет камня, значок)
KINDS = {
    "fast": (60711, (255, 150, 40), (104, 104, 108), "bolt"),
    "fuel": (60712, (90, 200, 110), (100, 106, 100), "drop"),
    "both": (60713, (215, 130, 255), (110, 104, 118), "star"),
    "deep": (60714, (90, 210, 220), (74, 74, 82), "gem"),
}

# Значки 5x5 в окне печи — те же формы, что на плашках ролей, только крупнее пикселем.
GLYPH = {
    "bolt": ["..#..", ".##..", "#####", "..##.", "..#.."],
    "drop": ["..#..", ".###.", "#####", "#####", ".###."],
    "star": ["..#..", "#####", ".###.", "#####", "..#.."],
    "gem":  [".###.", "#####", "#####", ".###.", "..#.."],
}


def stone(base, seed):
    """Шершавый камень: базовый тон плюс детерминированный шум."""
    rnd = random.Random(seed)
    im = Image.new("RGBA", (S, S))
    px = im.load()
    for y in range(S):
        for x in range(S):
            d = rnd.randint(-14, 14)
            px[x, y] = (max(0, base[0] + d), max(0, base[1] + d), max(0, base[2] + d), 255)
    return im


def bordered(im):
    """Тёмная рамка по краю — без неё соседние блоки сливаются в кашу."""
    px = im.load()
    for i in range(S):
        for x, y in ((i, 0), (i, S - 1), (0, i), (S - 1, i)):
            r, g, b, _ = px[x, y]
            px[x, y] = (int(r * 0.72), int(g * 0.72), int(b * 0.72), 255)
    return im


def front(base, glow, glyph, seed):
    """Перед печи: топка с подсветкой и значком вида."""
    im = bordered(stone(base, seed))
    px = im.load()
    # ниша топки
    for y in range(8, 14):
        for x in range(3, 13):
            edge = y == 8 or y == 13 or x == 3 or x == 12
            px[x, y] = (26, 22, 20, 255) if edge else (14, 12, 12, 255)
    # огонь внутри — три языка разной высоты
    for x, h in ((5, 2), (7, 3), (9, 2)):
        for k in range(h):
            y = 12 - k
            f = 1.0 - k * 0.22
            px[x, y] = (int(glow[0] * f), int(glow[1] * f), int(glow[2] * f), 255)
            px[x + 1, y] = (int(glow[0] * f * 0.7), int(glow[1] * f * 0.7), int(glow[2] * f * 0.7), 255)
    # значок вида сверху
    rows = GLYPH[glyph]
    ox, oy = (S - 5) // 2, 2
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "#":
                px[ox + x, oy + y] = (glow[0], glow[1], glow[2], 255)
    return im


def top(base, glow, seed):
    """Верх: камень с прорезями, чтобы не путался с боком."""
    im = bordered(stone(base, seed))
    px = im.load()
    for x in range(4, 12):
        px[x, 5] = (int(base[0] * 0.55), int(base[1] * 0.55), int(base[2] * 0.55), 255)
        px[x, 10] = (int(base[0] * 0.55), int(base[1] * 0.55), int(base[2] * 0.55), 255)
    px[7, 7] = px[8, 8] = (glow[0], glow[1], glow[2], 255)
    return im


entries = []
for kind, (cmd, glow, base, glyph) in KINDS.items():
    name = "nr_furnace_" + kind
    front(base, glow, glyph, hash(kind) & 0xFFFF).save(os.path.join(TEX, name + "_front.png"))
    bordered(stone(base, (hash(kind) >> 3) & 0xFFFF)).save(os.path.join(TEX, name + "_side.png"))
    top(base, glow, (hash(kind) >> 7) & 0xFFFF).save(os.path.join(TEX, name + "_top.png"))
    with open(os.path.join(MODELS, name + ".json"), "w", encoding="utf-8") as f:
        json.dump({
            "parent": "minecraft:block/orientable",
            "textures": {
                "front": "minecraft:block/" + name + "_front",
                "side": "minecraft:block/" + name + "_side",
                "top": "minecraft:block/" + name + "_top",
            },
        }, f, ensure_ascii=False, indent=1)
    entries.append({"threshold": cmd,
                    "model": {"type": "minecraft:model", "model": "minecraft:item/" + name}})

entries.sort(key=lambda e: e["threshold"])
with open(os.path.join(ITEMS, "furnace.json"), "w", encoding="utf-8") as f:
    json.dump({
        "model": {
            "type": "minecraft:range_dispatch",
            "property": "minecraft:custom_model_data",
            "index": 0,
            "fallback": {"type": "minecraft:model", "model": "minecraft:block/furnace"},
            "entries": entries,
        }
    }, f, ensure_ascii=False, indent=1)

print("печей:", len(KINDS), "— текстур:", len(KINDS) * 3, "моделей:", len(KINDS))
print("CMD:", ", ".join("%s=%d" % (k, v[0]) for k, v in KINDS.items()))
