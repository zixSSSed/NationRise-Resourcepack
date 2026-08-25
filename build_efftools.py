# -*- coding: utf-8 -*-
"""Донат-инструменты «Эффективность X + Прочность V»: кирка/топор/лопата.
Конвертирует ../<bbmodel> (java_block из Blockbench) в модель пака + новый items/<base>.json.
Ключевое: геометрия НОРМАЛИЗУЕТСЯ в 16-куб (центр + подгон масштаба), иначе модель ~2×
и висит на весь экран. Старый формат overrides добавляет build_dualformat.py (запускать ПОСЛЕ)."""
import json, os, base64, re

ROOT = os.path.dirname(os.path.abspath(__file__))
MC = os.path.join(ROOT, "pack", "assets", "minecraft")

# (bbmodel, CMD, имя модели, базовый предмет, флип)
# flip="y180" — поворот геометрии на 180° вокруг вертикали (рабочая сторона смотрит в другую сторону):
#   топор — лезвие от игрока, лопата — совок к игроку.
TOOLS = [
    ("model.bbmodel",  60701, "nr_pick_ef10",   "netherite_pickaxe", None),
    ("axe.bbmodel",    60702, "nr_axe_ef10",    "netherite_axe",    "y180"),
    ("shovel.bbmodel", 60703, "nr_shovel_ef10", "netherite_shovel", "y180"),
]

# --- флип элемента на 180° вокруг Y относительно центра куба (8,8,8) ---
def flip_y180(el):
    f, t = el["from"], el["to"]
    el["from"] = [round(16 - t[0], 4), f[1], round(16 - t[2], 4)]
    el["to"]   = [round(16 - f[0], 4), t[1], round(16 - f[2], 4)]
    r = el.get("rotation")
    if r:
        o = r["origin"]
        r["origin"] = [round(16 - o[0], 4), o[1], round(16 - o[2], 4)]
        if r["axis"] in ("x", "z"): r["angle"] = -r["angle"]
    faces = el.get("faces", {})
    swap = {"north": "south", "south": "north", "east": "west", "west": "east"}
    nf = {}
    for fn, fo in faces.items():
        nn = swap.get(fn, fn)
        if fn in swap:  # боковые грани при 180° по горизонтали зеркалятся — флипаем U
            u = fo["uv"]; fo = {**fo, "uv": [u[2], u[1], u[0], u[3]]}
        else:  # up/down поворачиваются на 180°
            fo = {**fo, "rotation": ((fo.get("rotation", 0) + 180) % 360)}
        nf[nn] = fo
    el["faces"] = nf
    return el

# стандартные хват-трансформы ручного инструмента (расчёт на нормализованную ~14-модель)
DISPLAY = {
    "thirdperson_righthand": {"rotation": [0, -90, 55], "translation": [0, 4, 0.5], "scale": [0.85, 0.85, 0.85]},
    "thirdperson_lefthand":  {"rotation": [0, 90, -55], "translation": [0, 4, 0.5], "scale": [0.85, 0.85, 0.85]},
    "firstperson_righthand": {"rotation": [0, -90, 25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
    "firstperson_lefthand":  {"rotation": [0, 90, -25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
    "gui":    {"rotation": [30, 225, 0], "translation": [0, 0, 0], "scale": [1.0, 1.0, 1.0]},
    "ground": {"translation": [0, 3, 0], "scale": [0.45, 0.45, 0.45]},
    "fixed":  {"rotation": [0, 180, 0], "scale": [0.9, 0.9, 0.9]},
}
VALID_ANGLES = (-45.0, -22.5, 0.0, 22.5, 45.0)
TARGET = 14.0  # длиннейшую сторону подгоняем к этому размеру (запас в 16-кубе)


def build_tool(bbfile, cmd, name, base, flip=None):
    d = json.load(open(os.path.join(ROOT, "..", bbfile), encoding="utf-8"))
    res = d.get("resolution", {"width": 16, "height": 16})
    rw, rh = res.get("width", 16), res.get("height", 16)

    # текстура
    src = d["textures"][0]["source"]
    png = base64.b64decode(re.sub(r"^data:image/png;base64,", "", src))
    open(os.path.join(MC, "textures", "item", name + ".png"), "wb").write(png)

    els_raw = d.get("elements", [])
    # --- нормализация: bbox → центр в (8,8,8), масштаб так, чтобы длиннейшая сторона = TARGET ---
    xs, ys, zs = [], [], []
    for e in els_raw:
        if "from" in e and "to" in e:
            xs += [e["from"][0], e["to"][0]]; ys += [e["from"][1], e["to"][1]]; zs += [e["from"][2], e["to"][2]]
    cx, cy, cz = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2, (min(zs)+max(zs))/2
    maxdim = max(max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs)) or 16.0
    fit = TARGET / maxdim
    center = (cx, cy, cz)

    def nrm(p):  # нормализовать точку в 16-куб
        return [round(8 + (p[i] - center[i]) * fit, 4) for i in range(3)]

    def cuv(uv):  # bbmodel хранит uv в пикселях; vanilla ждёт 0-16
        return [round(uv[0]*16.0/rw, 4), round(uv[1]*16.0/rh, 4), round(uv[2]*16.0/rw, 4), round(uv[3]*16.0/rh, 4)]

    els = []
    for e in els_raw:
        el = {"from": nrm(e["from"]), "to": nrm(e["to"])}
        rot = e.get("rotation")
        if rot and any(abs(a) > 0.001 for a in rot):
            axis = max(range(3), key=lambda i: abs(rot[i]))
            # ваниль разрешает только 0/±22.5/±45 — свободные углы снапим (иначе клиент бракует ВСЮ модель)
            angle = min(VALID_ANGLES, key=lambda a: abs(a - rot[axis]))
            if angle:
                el["rotation"] = {"origin": nrm(e.get("origin", [8, 8, 8])), "axis": "xyz"[axis], "angle": angle}
        faces = {}
        for fn, f in e.get("faces", {}).items():
            if f.get("texture") is None: continue
            fo = {"uv": cuv(f["uv"]), "texture": "#0"}
            if f.get("rotation"): fo["rotation"] = f["rotation"]
            faces[fn] = fo
        el["faces"] = faces
        els.append(el)

    if flip == "y180":
        els = [flip_y180(el) for el in els]

    model = {
        "credit": f"NationRise — донат-инструмент ({bbfile}), нормализован в 16-куб",
        "textures": {"0": f"minecraft:item/{name}", "particle": f"minecraft:item/{name}"},
        "elements": els,
        "display": DISPLAY,
    }
    json.dump(model, open(os.path.join(MC, "models", "item", name + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # новый формат (1.21.4+): items/<base>.json — range_dispatch
    item = {"model": {"type": "minecraft:range_dispatch", "property": "minecraft:custom_model_data", "index": 0,
                      "fallback": {"type": "minecraft:model", "model": f"minecraft:item/{base}"},
                      "entries": [{"threshold": cmd, "model": {"type": "minecraft:model", "model": f"minecraft:item/{name}"}}]}}
    json.dump(item, open(os.path.join(MC, "items", base + ".json"), "w", encoding="utf-8"), indent=1)
    print(f"  {name}: elems={len(els)} maxdim={maxdim:.1f} fit={fit:.3f} CMD={cmd} base={base}")


print("build_efftools:")
for t in TOOLS:
    build_tool(*t)
print("ok")
