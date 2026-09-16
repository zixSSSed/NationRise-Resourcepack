# -*- coding: utf-8 -*-
"""
Модели особых печей: три донатных и одна крафтовая.

Откуда текстуры
---------------
Мои рисованные версии выглядели самоделкой: осмысленная структура там была, но
попиксельная живопись без опыта даёт ровно то, за что её и ругали. Поэтому корпус
берётся из присланного .bbmodel — три готовые грани (перед, бок, верх), сделанные
художником. Их не перерисовываем.

Остальные три печи — те же самые грани с перекрашенной акцентной полосой. Так вся
четвёрка выглядит одной серией, а не набором разных блоков: меняется только цвет
свечения, геометрия и камень остаются авторскими.

Перекраска идёт по тону: у исходной текстуры акцент фиолетовый, и мы переносим
его пиксели в нужный оттенок, сохраняя их светлоту и насыщенность. Заменять по
списку конкретных цветов нельзя — в текстуре десятки оттенков фиолетового с
разной тенью, и половина осталась бы неперекрашенной.

Модель наследуется от minecraft:block/orientable: north = перед, up/down = верх,
остальное — бок. Ровно так же, как в присланном .bbmodel.

Запуск: py -3.13 build_furnaces.py  (после него pack_zip.py)
"""
import os, json, base64, io, colorsys
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
MC = os.path.join(ROOT, "pack", "assets", "minecraft")
TEX = os.path.join(MC, "textures", "block")
MODELS = os.path.join(MC, "models", "item")
ITEMS = os.path.join(MC, "items")
SRC = os.path.join(os.path.expanduser("~"), "Downloads", "GlubinPech.bbmodel")
for d in (TEX, MODELS, ITEMS):
    os.makedirs(d, exist_ok=True)

# Какая текстура из .bbmodel какой гранью работает (по faces в самом файле).
ROLE = {"ofen_forne_off.png": "front", "ofen_oben.png": "top", "ofen_seite.png": "side"}

# id -> (CMD, целевой тон акцента в градусах HSV; None — оставить как в оригинале)
KINDS = {
    "deep": (60714, None),   # авторский фиолетовый
    "fast": (60711, 25),     # оранжевый
    "fuel": (60712, 120),    # зелёный
    "both": (60713, 305),    # пурпурный
}

# Границы «фиолетового» в исходнике: всё, что попадает сюда, считается акцентом.
# Окно намеренно широкое: светлый блик на верхнем ребре полосы уходит в розовато-
# лавандовый, и при узком окне он оставался розовым на зелёной и оранжевой печи.
# Серый камень сюда не попадает — его спасает порог насыщенности.
ACCENT_HUE = (0.60, 0.95)
ACCENT_MIN_SAT = 0.12


def load_sources():
    with io.open(SRC, encoding="utf-8") as f:
        model = json.load(f)
    out = {}
    for t in model["textures"]:
        role = ROLE.get(t["name"])
        if role is None:
            continue
        raw = t["source"].split(",", 1)[1]
        out[role] = Image.open(io.BytesIO(base64.b64decode(raw))).convert("RGBA")
    missing = set(ROLE.values()) - set(out)
    if missing:
        raise SystemExit("в .bbmodel нет граней: " + ", ".join(sorted(missing)))
    return out


def recolor(im, hue_deg):
    """Перекрасить акцентные пиксели в заданный тон, сохранив их светлоту."""
    if hue_deg is None:
        return im.copy()
    target = hue_deg / 360.0
    out = im.copy()
    px = out.load()
    for x in range(out.width):
        for y in range(out.height):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if not (ACCENT_HUE[0] <= h <= ACCENT_HUE[1] and s >= ACCENT_MIN_SAT):
                continue
            nr, ng, nb = colorsys.hsv_to_rgb(target, s, v)
            px[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255), a)
    return out


src = load_sources()
accent_px = sum(
    1
    for x in range(src["front"].width)
    for y in range(src["front"].height)
    for h, s, _ in [colorsys.rgb_to_hsv(*[c / 255 for c in src["front"].getpixel((x, y))[:3]])]
    if ACCENT_HUE[0] <= h <= ACCENT_HUE[1] and s >= ACCENT_MIN_SAT
)
print("акцентных пикселей на передней грани:", accent_px)

entries = []
for kind, (cmd, hue) in KINDS.items():
    name = "nr_furnace_" + kind
    for role in ("front", "side", "top"):
        recolor(src[role], hue).save(os.path.join(TEX, "%s_%s.png" % (name, role)))
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
