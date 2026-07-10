# -*- coding: utf-8 -*-
"""Кастомные рыбы NationRise: 16x16 текстуры по редкостям + модели + items/cod.json (range_dispatch)."""
import os, json
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
MC = os.path.join(ROOT, "pack", "assets", "minecraft")
TEX = os.path.join(MC, "textures", "item")
MODELS = os.path.join(MC, "models", "item")
ITEMS = os.path.join(MC, "items")
for d in (TEX, MODELS, ITEMS):
    os.makedirs(d, exist_ok=True)

# ---- палитры редкостей (o=контур b=тело l=брюшко f=плавник a=акцент) ----
P = {
    "COMMON":    dict(o=(44, 52, 62), b=(150, 168, 184), l=(206, 218, 228), f=(98, 114, 130), a=(176, 190, 204)),
    "UNCOMMON":  dict(o=(28, 58, 24), b=(112, 182, 86), l=(186, 228, 156), f=(64, 122, 52), a=(150, 206, 112)),
    "RARE":      dict(o=(20, 52, 82), b=(78, 170, 226), l=(184, 226, 255), f=(46, 112, 170), a=(150, 210, 246)),
    "EPIC":      dict(o=(56, 28, 82), b=(178, 112, 226), l=(234, 202, 255), f=(120, 62, 178), a=(214, 164, 248)),
    "LEGENDARY": dict(o=(98, 70, 18), b=(242, 198, 82), l=(255, 240, 176), f=(202, 146, 46), a=(255, 226, 132)),
    "RELIC":     dict(o=(82, 22, 22), b=(226, 92, 92), l=(255, 194, 194), f=(170, 52, 52), a=(255, 156, 156)),
    "MYTHIC":    dict(o=(20, 16, 46), b=(98, 86, 162), l=(186, 170, 244), f=(58, 46, 112), a=(150, 255, 236)),
    "NETHER":    dict(o=(50, 18, 10), b=(226, 98, 42), l=(255, 202, 112), f=(170, 54, 26), a=(255, 212, 92)),
    "END":       dict(o=(24, 42, 46), b=(98, 202, 186), l=(210, 255, 246), f=(70, 142, 152), a=(206, 164, 255)),
}

def C(t): return (t[0], t[1], t[2], 255)

def draw_fish(pal, shape="classic", facing=1, pattern="none", glow=False):
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    O, B, L, F, A = C(pal["o"]), C(pal["b"]), C(pal["l"]), C(pal["f"]), C(pal["a"])
    if shape == "round":
        bx0, by0, bx1, by1 = 3, 3, 11, 12
        tail = [(10, 7), (15, 4), (15, 11)]
    elif shape == "long":
        bx0, by0, bx1, by1 = 1, 6, 11, 10
        tail = [(10, 8), (15, 5), (15, 11)]
    else:  # classic
        bx0, by0, bx1, by1 = 2, 5, 11, 11
        tail = [(9, 8), (15, 4), (15, 12)]
    cy = (by0 + by1) // 2
    # хвост
    d.polygon(tail, fill=F, outline=O)
    # верхний/нижний плавники
    d.polygon([(bx0 + 3, by0 + 1), (bx0 + 5, by0 - 2), (bx0 + 7, by0 + 1)], fill=F, outline=O)
    d.polygon([(bx0 + 3, by1 - 1), (bx0 + 5, by1 + 2), (bx0 + 7, by1 - 1)], fill=F, outline=O)
    # тело
    d.ellipse([bx0, by0, bx1, by1], fill=B, outline=O)
    # брюшко
    d.ellipse([bx0 + 1, cy, bx1 - 2, by1 - 1], fill=L)
    # узор
    if pattern == "stripe":
        for x in range(bx0 + 3, bx1 - 1, 2):
            for y in range(by0 + 2, by1 - 1):
                if im.getpixel((x, y))[3]: d.point((x, y), fill=A)
    elif pattern == "spot":
        for sx, sy in [(bx0 + 4, by0 + 2), (bx0 + 6, cy + 1), (bx0 + 3, cy)]:
            if 0 <= sx < 16 and 0 <= sy < 16 and im.getpixel((sx, sy))[3]: d.point((sx, sy), fill=A)
    # светящаяся кромка для высоких редкостей
    if glow:
        for x in range(bx0 + 1, bx1):
            if im.getpixel((x, by0))[3]: d.point((x, by0), fill=A)
    # глаз (голова слева)
    d.point((bx0 + 1, cy - 1), fill=(255, 255, 255, 255))
    d.point((bx0 + 2, cy - 1), fill=O)
    if facing == -1:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im

def draw_mystery():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    G, D = (170, 174, 186, 255), (70, 72, 84, 255)
    # «?» пиксельный
    q = [(5, 4), (6, 3), (7, 3), (8, 3), (9, 4), (10, 5), (10, 6), (9, 7), (8, 8), (8, 9), (8, 10), (8, 12)]
    for x, y in q:
        d.rectangle([x - 1, y - 1, x, y], fill=D)
    for x, y in q:
        d.point((x, y), fill=G)
    return im

# ---- спецификации текстур (id -> параметры) ----
SPECS = {
    "common_a":   ("COMMON", "classic", 1, "none", False),
    "common_b":   ("COMMON", "classic", -1, "spot", False),
    "common_c":   ("COMMON", "long", 1, "stripe", False),
    "uncommon_a": ("UNCOMMON", "classic", 1, "stripe", False),
    "uncommon_b": ("UNCOMMON", "classic", -1, "none", False),
    "uncommon_c": ("UNCOMMON", "round", 1, "spot", False),
    "rare_a":     ("RARE", "classic", 1, "stripe", False),
    "rare_b":     ("RARE", "long", -1, "stripe", False),
    "rare_c":     ("RARE", "classic", 1, "spot", False),
    "epic_a":     ("EPIC", "round", 1, "spot", False),
    "epic_b":     ("EPIC", "classic", -1, "stripe", True),
    "legend_a":   ("LEGENDARY", "classic", 1, "stripe", True),
    "legend_b":   ("LEGENDARY", "long", -1, "none", True),
    "relic_a":    ("RELIC", "classic", 1, "spot", True),
    "mythic_a":   ("MYTHIC", "round", 1, "stripe", True),
    "rare_nether_a": ("NETHER", "classic", 1, "stripe", False),
    "rare_nether_b": ("NETHER", "long", -1, "spot", True),
    "epic_nether":   ("NETHER", "round", -1, "spot", True),
    "legend_nether": ("NETHER", "classic", 1, "none", True),
    "relic_nether":  ("NETHER", "long", 1, "stripe", True),
    "rare_end_a": ("END", "classic", 1, "spot", False),
    "rare_end_b": ("END", "round", -1, "stripe", True),
    "epic_end":   ("END", "round", -1, "stripe", True),
    "legend_end": ("END", "classic", 1, "none", True),
    "relic_end":  ("END", "long", 1, "spot", True),
}

# ---- генерация текстур + моделей ----
imgs = {}
for fid, (pal, shape, facing, pattern, glow) in SPECS.items():
    im = draw_fish(P[pal], shape, facing, pattern, glow)
    im.save(os.path.join(TEX, f"nr_fish_{fid}.png"))
    imgs[fid] = im
mystery = draw_mystery()
mystery.save(os.path.join(TEX, "nr_fish_mystery.png"))
imgs["mystery"] = mystery

for fid in list(SPECS.keys()) + ["mystery"]:
    json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": f"minecraft:item/nr_fish_{fid}"}},
              open(os.path.join(MODELS, f"nr_fish_{fid}.json"), "w", encoding="utf-8"), indent=2)

# ---- items/cod.json: range_dispatch по custom_model_data ----
# (threshold, fish_id) — отсортировано по возрастанию
TH = [
    (1001, "common_a"), (1004, "common_b"), (1007, "common_c"),
    (2001, "uncommon_a"), (2005, "uncommon_b"), (2010, "uncommon_c"),
    (3001, "rare_a"), (3005, "rare_b"), (3010, "rare_c"),
    (4001, "epic_a"), (4007, "epic_b"),
    (5001, "legend_a"), (5007, "legend_b"),
    (6001, "relic_a"),
    (7001, "mythic_a"),
    (99999, "mystery"),
    (103001, "rare_nether_a"), (103004, "rare_nether_b"), (104001, "epic_nether"), (105001, "legend_nether"), (106001, "relic_nether"),
    (203001, "rare_end_a"), (203004, "rare_end_b"), (204001, "epic_end"), (205001, "legend_end"), (206001, "relic_end"),
]
cod = {
    "model": {
        "type": "minecraft:range_dispatch",
        "property": "minecraft:custom_model_data",
        "index": 0,
        "fallback": {"type": "minecraft:model", "model": "minecraft:item/cod"},
        "entries": [
            {"threshold": t, "model": {"type": "minecraft:model", "model": f"minecraft:item/nr_fish_{fid}"}}
            for t, fid in TH
        ],
    }
}
json.dump(cod, open(os.path.join(ITEMS, "cod.json"), "w", encoding="utf-8"), indent=2)

# ---- контактный лист для проверки ----
order = ["common_a", "common_b", "common_c", "uncommon_a", "uncommon_b", "uncommon_c",
         "rare_a", "rare_b", "rare_c", "epic_a", "epic_b", "legend_a", "legend_b",
         "relic_a", "mythic_a", "mystery", "rare_nether_a", "rare_nether_b", "epic_nether", "legend_nether",
         "relic_nether", "rare_end_a", "rare_end_b", "epic_end", "legend_end", "relic_end"]
cols, cell, sc = 8, 80, 4
rows = (len(order) + cols - 1) // cols
sheet = Image.new("RGBA", (cols * cell, rows * cell), (30, 24, 40, 255))
sd = ImageDraw.Draw(sheet)
for i, fid in enumerate(order):
    r, c = divmod(i, cols)
    big = imgs[fid].resize((16 * sc, 16 * sc), Image.NEAREST)
    sheet.alpha_composite(big, (c * cell + 8, r * cell + 6))
sheet.save(os.path.join(ROOT, "logo", "_fish_preview.png"))
print("fish:", len(SPECS) + 1, "textures + models | cod.json entries:", len(TH))
