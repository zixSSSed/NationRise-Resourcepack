# -*- coding: utf-8 -*-
"""
Головы миньонов v3 — оснащение автокрафта (17.09.2026): предметы «Чертёж автокрафта» и
«Автоплавка» показываются головами миньонов (PAPER + CMD 71005/71006).
  • инженер  — шахтёр (nr_minhead_miner) с перекрашенной каской: жёлтая → белая;
  • плавильщик — землекоп (nr_minhead_digger) с каской: коричневая → красно-оранжевая.
Перекраска по оттенку: меняем только пиксели «цвета каски», лицо и глаза не трогаем,
яркость сохраняем. Модель — та же, что у v2 (куб головы + hat-слой).
Запуск: py -3.13 gen_minion_heads_v3.py
"""
import json, os, colorsys
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(ROOT, "pack", "assets", "minecraft")
TEX = os.path.join(PACK, "textures", "item")
MODELS = os.path.join(PACK, "models", "item")

def faces(off):
    return {
        "north": {"uv": [2 + off, 8, 4 + off, 16], "texture": "#s"},
        "south": {"uv": [6 + off, 8, 8 + off, 16], "texture": "#s"},
        "west":  {"uv": [0 + off, 8, 2 + off, 16], "texture": "#s"},
        "east":  {"uv": [4 + off, 8, 6 + off, 16], "texture": "#s"},
        "up":    {"uv": [2 + off, 0, 4 + off, 8], "texture": "#s"},
        "down":  {"uv": [4 + off, 0, 6 + off, 8], "texture": "#s"},
    }

def model_json(src_model, tex):
    # копируем геометрию/display из исходной модели, меняем только текстуру
    with open(os.path.join(MODELS, src_model + ".json"), encoding="utf-8") as f:
        m = json.load(f)
    m["__comment"] = "Голова миньона (оснащение автокрафта), перекраска каски из " + src_model
    m["textures"] = {"s": f"minecraft:item/{tex}", "particle": f"minecraft:item/{tex}"}
    return m

def recolor(src, dst, hue_from, hue_tol, target_hsv, keep_light=True, v_max=1.01):
    """Пиксели с оттенком hue_from±tol (в градусах) → target (h,s) с сохранением яркости."""
    im = Image.open(os.path.join(TEX, src + ".png")).convert("RGBA")
    px = im.load()
    th, ts, tv = target_hsv
    n = 0
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a == 0: continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            hd = abs((h * 360 - hue_from + 180) % 360 - 180)
            if hd <= hue_tol and s > 0.25 and 0.15 < v <= v_max:
                nv = v if keep_light else tv
                nr, ng, nb = colorsys.hsv_to_rgb(th / 360, ts, min(1.0, nv * tv))
                px[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255), a); n += 1
    im.save(os.path.join(TEX, dst + ".png"))
    print(dst, "перекрашено пикселей:", n)

# инженер: жёлтая каска шахтёра (hue ~55°) → почти белая (низкая насыщенность, ярко)
recolor("nr_minhead_miner", "nr_minhead_engineer", 55, 18, (210, 0.08, 1.15))
# плавильщик: коричневая шляпа землекопа (hue ~30°) → красно-оранжевая
recolor("nr_minhead_digger", "nr_minhead_smelter", 30, 20, (10, 0.95, 1.35), v_max=0.78)   # лицо светлее — не трогаем

for src, tex in (("nr_minhead_miner", "nr_minhead_engineer"), ("nr_minhead_digger", "nr_minhead_smelter")):
    with open(os.path.join(MODELS, tex + ".json"), "w", encoding="utf-8") as f:
        json.dump(model_json(src, tex), f, ensure_ascii=False, indent=1)

# paper.json: CMD 71005/71006
pj = os.path.join(PACK, "items", "paper.json")
with open(pj, encoding="utf-8") as f:
    d = json.load(f)
entries = d["model"]["entries"]
have = {e["threshold"] for e in entries}
for cmd, tex in ((71005, "nr_minhead_engineer"), (71006, "nr_minhead_smelter")):
    if cmd not in have:
        entries.append({"threshold": cmd, "model": {"type": "minecraft:model", "model": f"minecraft:item/{tex}"}})
entries.sort(key=lambda e: e["threshold"])
with open(pj, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
print("paper.json:", len(entries), "entries")

# превью для проверки глазами
prev = Image.new("RGBA", (64 * 8, 16 * 8 * 2 + 8), (40, 40, 40, 255))
for i, n in enumerate(("nr_minhead_engineer", "nr_minhead_smelter")):
    im = Image.open(os.path.join(TEX, n + ".png")).convert("RGBA").resize((64 * 8, 16 * 8), Image.NEAREST)
    prev.paste(im, (0, i * (16 * 8 + 8)), im)
prev.save(os.path.join(ROOT, "_preview_heads_v3.png"))
