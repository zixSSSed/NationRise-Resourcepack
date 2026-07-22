# -*- coding: utf-8 -*-
"""Головы-иконки для меню /events: 6 bbmodel-голов на базе FEATHER (CMD 60801-60806).
База — перо (не paper!): items/feather.json пишется ЦЕЛИКОМ этим скриптом и никем больше,
поэтому конфликтов с build_builditems.py (paper.json) нет по построению.
Оба формата (items/feather.json + models/item/feather.json overrides) пишутся здесь же —
build_dualformat.py запускать не нужно. Геометрия нормализуется в 16-куб (как build_efftools)."""
import json, os, base64, re

ROOT = os.path.dirname(os.path.abspath(__file__))
MC = os.path.join(ROOT, "pack", "assets", "minecraft")
BASE = "feather"

# (bbmodel, CMD, имя модели, ивент)
HEADS = [
    ("RicarHead.bbmodel",   60801, "nr_head_boss",  "боссы (рыцарь)"),
    ("CarGoriHead.bbmodel", 60802, "nr_head_koth",  "король горы"),
    ("ChestHead.bbmodel",   60803, "nr_head_loot",  "лут-сундуки"),
    ("FishHead.bbmodel",    60804, "nr_head_fish",  "рыбацкий турнир"),
    ("KBHead.bbmodel",      60805, "nr_head_br",    "королевская битва"),
    ("TntHead.bbmodel",     60806, "nr_head_tnt",   "TNT Run"),
]

DISPLAY = {
    "gui":    {"rotation": [25, 205, 0], "translation": [0, 0, 0], "scale": [0.95, 0.95, 0.95]},
    "ground": {"translation": [0, 3, 0], "scale": [0.4, 0.4, 0.4]},
    "fixed":  {"rotation": [0, 180, 0], "scale": [0.9, 0.9, 0.9]},
    "thirdperson_righthand": {"rotation": [0, 0, 0], "translation": [0, 3, 1], "scale": [0.55, 0.55, 0.55]},
    "firstperson_righthand": {"rotation": [0, -25, 0], "translation": [1.13, 3.2, 1.13], "scale": [0.6, 0.6, 0.6]},
}
VALID_ANGLES = (-45.0, -22.5, 0.0, 22.5, 45.0)
TARGET = 14.0
# Насколько крупной должна выглядеть иконка в слоте (в «блоковых» единицах, слот = 16).
# Раньше все модели просто ужимались в 14-куб — но в GUI видна ПРОЕКЦИЯ, и голова,
# у которой длинный хвост/перо по глубине, выглядела мелкой, а компактная — крупной.
# Поэтому scale в display.gui считаем по реальному экранному размеру каждой модели.
GUI_TARGET = 13.0


def gui_projected_size(elements, rot_deg):
    """Ширина/высота модели ТАК, КАК ЕЁ ВИДНО в слоте: поворот display.gui + ортопроекция.
    Minecraft крутит углы как rotationXYZ (сначала X, потом Y, потом Z)."""
    import math
    rx, ry, rz = (math.radians(a) for a in rot_deg)

    def rotate(v):
        x, y, z = v
        y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
        x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
        x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
        return x, y, z

    xs = [c for e in elements for c in (e["from"][0], e["to"][0])]
    ys = [c for e in elements for c in (e["from"][1], e["to"][1])]
    zs = [c for e in elements for c in (e["from"][2], e["to"][2])]
    px, py = [], []
    for cx in (min(xs), max(xs)):
        for cy in (min(ys), max(ys)):
            for cz in (min(zs), max(zs)):
                sx, sy, _ = rotate((cx - 8, cy - 8, cz - 8))
                px.append(sx); py.append(sy)
    return max(px) - min(px), max(py) - min(py)


def build_head(bbfile, cmd, name):
    d = json.load(open(os.path.join(ROOT, "..", bbfile), encoding="utf-8"))
    res = d.get("resolution", {"width": 16, "height": 16})
    rw, rh = res.get("width", 16), res.get("height", 16)

    src = d["textures"][0]["source"]
    png = base64.b64decode(re.sub(r"^data:image/png;base64,", "", src))
    open(os.path.join(MC, "textures", "item", name + ".png"), "wb").write(png)

    els_raw = [e for e in d.get("elements", []) if "from" in e and "to" in e]
    xs, ys, zs = [], [], []
    for e in els_raw:
        xs += [e["from"][0], e["to"][0]]; ys += [e["from"][1], e["to"][1]]; zs += [e["from"][2], e["to"][2]]
    cx, cy, cz = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2, (min(zs)+max(zs))/2
    maxdim = max(max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs)) or 16.0
    fit = TARGET / maxdim
    center = (cx, cy, cz)

    def nrm(p):
        return [round(8 + (p[i] - center[i]) * fit, 4) for i in range(3)]

    def cuv(uv):
        return [round(uv[0]*16.0/rw, 4), round(uv[1]*16.0/rh, 4), round(uv[2]*16.0/rw, 4), round(uv[3]*16.0/rh, 4)]

    els = []
    for e in els_raw:
        el = {"from": nrm(e["from"]), "to": nrm(e["to"])}
        rot = e.get("rotation")
        if rot and any(abs(a) > 0.001 for a in rot):
            axis = max(range(3), key=lambda i: abs(rot[i]))
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

    # свой gui-scale, чтобы ВСЕ головы смотрелись одинаково крупно в слоте
    disp = json.loads(json.dumps(DISPLAY))  # копия, иначе правки утекут в следующую модель
    gw, gh = gui_projected_size(els, disp["gui"]["rotation"])
    gs = round(GUI_TARGET / max(gw, gh, 0.001), 3)
    disp["gui"]["scale"] = [gs, gs, gs]

    model = {
        "credit": f"NationRise — голова меню ивентов ({bbfile}), нормализована в 16-куб",
        "textures": {"0": f"minecraft:item/{name}", "particle": f"minecraft:item/{name}"},
        "elements": els,
        "display": disp,
    }
    json.dump(model, open(os.path.join(MC, "models", "item", name + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"  {name}: elems={len(els)} maxdim={maxdim:.1f} fit={fit:.3f} "
          f"экран={gw:.1f}x{gh:.1f} gui-scale={gs} CMD={cmd}")


print("build_eventheads:")
for bb, cmd, name, _ in HEADS:
    build_head(bb, cmd, name)

# новый формат: один items/feather.json со всеми головами
item = {"model": {"type": "minecraft:range_dispatch", "property": "minecraft:custom_model_data", "index": 0,
                  "fallback": {"type": "minecraft:model", "model": f"minecraft:item/{BASE}"},
                  "entries": [{"threshold": cmd, "model": {"type": "minecraft:model", "model": f"minecraft:item/{name}"}}
                              for _, cmd, name, _ in HEADS]}}
json.dump(item, open(os.path.join(MC, "items", BASE + ".json"), "w", encoding="utf-8"), indent=1)

# старый формат (1.14–1.21.3): models/item/feather.json c overrides
old = {"parent": "minecraft:item/generated",
       "textures": {"layer0": f"minecraft:item/{BASE}"},
       "overrides": [{"predicate": {"custom_model_data": cmd}, "model": f"minecraft:item/{name}"}
                     for _, cmd, name, _ in HEADS]}
json.dump(old, open(os.path.join(MC, "models", "item", BASE + ".json"), "w", encoding="utf-8"), indent=1)
print("ok: items/feather.json + models/item/feather.json (dual format)")
