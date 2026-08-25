# -*- coding: utf-8 -*-
"""Донат-кирка «Эффективность X»: конвертирует ../model.bbmodel (java_block из Blockbench)
в модель пака nr_pick_ef10 + оверрайд items/netherite_pickaxe.json (CMD 60701)."""
import json, os, base64, re

ROOT = os.path.dirname(os.path.abspath(__file__))
BB = os.path.join(ROOT, "..", "model.bbmodel")
MC = os.path.join(ROOT, "pack", "assets", "minecraft")
CMD = 60701
NAME = "nr_pick_ef10"

d = json.load(open(BB, encoding="utf-8"))
res = d.get("resolution", {"width": 16, "height": 16})
rw, rh = res.get("width", 16), res.get("height", 16)

# --- текстура (base64 data-uri) ---
src = d["textures"][0]["source"]
png = base64.b64decode(re.sub(r"^data:image/png;base64,", "", src))
open(os.path.join(MC, "textures", "item", NAME + ".png"), "wb").write(png)

# --- элементы: bbmodel хранит uv в пикселях текстуры; vanilla-модель ждёт 0-16 ---
def cuv(uv): return [round(uv[0] * 16.0 / rw, 4), round(uv[1] * 16.0 / rh, 4),
                     round(uv[2] * 16.0 / rw, 4), round(uv[3] * 16.0 / rh, 4)]
els = []
for e in d.get("elements", []):
    el = {"from": e["from"], "to": e["to"]}
    rot = e.get("rotation")
    if rot and any(abs(a) > 0.001 for a in rot):
        axis = max(range(3), key=lambda i: abs(rot[i]))
        # ваниль разрешает только 0/±22.5/±45 — свободные углы Blockbench снапим к ближайшему,
        # иначе клиент бракует ВСЮ модель (missing texture)
        angle = min((-45.0, -22.5, 0.0, 22.5, 45.0), key=lambda a: abs(a - rot[axis]))
        if angle:
            el["rotation"] = {"origin": e.get("origin", [8, 8, 8]),
                              "axis": "xyz"[axis], "angle": angle}
    faces = {}
    for fn, f in e.get("faces", {}).items():
        if f.get("texture") is None: continue
        fo = {"uv": cuv(f["uv"]), "texture": "#0"}
        if f.get("rotation"): fo["rotation"] = f["rotation"]
        faces[fn] = fo
    el["faces"] = faces
    els.append(el)

model = {
    "credit": "NationRise — донат-кирка (из model.bbmodel юзера)",
    "textures": {"0": f"minecraft:item/{NAME}", "particle": f"minecraft:item/{NAME}"},
    "elements": els,
    "display": d.get("display") or {  # стандартные хват-трансформы ручного инструмента
        "thirdperson_righthand": {"rotation": [0, -90, 55], "translation": [0, 4, 0.5], "scale": [0.85, 0.85, 0.85]},
        "thirdperson_lefthand": {"rotation": [0, 90, -55], "translation": [0, 4, 0.5], "scale": [0.85, 0.85, 0.85]},
        "firstperson_righthand": {"rotation": [0, -90, 25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
        "firstperson_lefthand": {"rotation": [0, 90, -25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
        "gui": {"rotation": [30, 225, 0], "translation": [0, 0, 0], "scale": [0.8, 0.8, 0.8]},
        "ground": {"translation": [0, 3, 0], "scale": [0.45, 0.45, 0.45]},
        "fixed": {"rotation": [0, 180, 0], "scale": [1, 1, 1]},
    },
}
json.dump(model, open(os.path.join(MC, "models", "item", NAME + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- оверрайд предмета: netherite_pickaxe c CMD 60701 -> наша модель, иначе ваниль ---
item = {"model": {"type": "minecraft:range_dispatch", "property": "minecraft:custom_model_data", "index": 0,
                  "fallback": {"type": "minecraft:model", "model": "minecraft:item/netherite_pickaxe"},
                  "entries": [{"threshold": CMD, "model": {"type": "minecraft:model", "model": f"minecraft:item/{NAME}"}}]}}
json.dump(item, open(os.path.join(MC, "items", "netherite_pickaxe.json"), "w", encoding="utf-8"), indent=1)
print(f"effpick ok: elements={len(els)}, tex={rw}x{rh}, CMD={CMD}")
