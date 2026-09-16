"""Переносит Королевскую Сокровищницу из BetterModel в наш ресурспак.

Зачем перенос. У BetterModel модель разъезжалась: крышка вставала не на своё место,
потому что движок трактует опорную точку кости по-своему, а проверить это можно только
в игре. Плюс обфускация имён — при каждой пересборке пака они меняются, и клиентская
копия молча протухает. Для сундука всё это лишнее: у него одна подвижная часть на одной
петле, а такое рисуется обычными дисплеями с нашими же моделями, как сделаны печки.

Что делает скрипт: делит модель по группам художника (`Niz` — низ, `Verh` — верх с
крышкой) на две модели предмета Minecraft, кладёт текстуру и прописывает обе в
`items/chest.json` через custom_model_data.

Тонкость с UV: Blockbench держит их в системе координат текстуры (здесь 128×128),
а ванильные модели — всегда в 0..16. Без пересчёта текстура легла бы крошечным
уголком в углу каждой грани.

Запуск: py -3.13 build_royal_chest_pack.py [путь к .bbmodel]
"""

import base64
import io
import json
import sys
from pathlib import Path

PACK = Path(__file__).parent / "pack" / "assets" / "minecraft"
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\bravl\Downloads\RoyalChest.bbmodel")

TEXTURE = "nr_royal_chest"
BASE_MODEL, LID_MODEL = "nr_royal_chest_base", "nr_royal_chest_lid"
CMD_BASE, CMD_LID = 60721, 60722
LID_GROUP = "Verh"

# Модель шире блока, поэтому её центр совмещаем с центром блока: в пространстве модели
# это (8, _, 8). По высоте низ кладём на пол блока.
CENTER = 8.0


def bounds(elements):
    lo = [float("inf")] * 3
    hi = [float("-inf")] * 3
    for e in elements:
        for i in range(3):
            lo[i] = min(lo[i], e["from"][i], e["to"][i])
            hi[i] = max(hi[i], e["from"][i], e["to"][i])
    return lo, hi


def main():
    model = json.load(io.open(SRC, encoding="utf-8"))
    res = model.get("resolution", {"width": 16, "height": 16})
    uv_scale = (16.0 / res.get("width", 16), 16.0 / res.get("height", 16))

    # текстура
    tex = model["textures"][0]
    (PACK / "textures" / "item").mkdir(parents=True, exist_ok=True)
    tex_path = PACK / "textures" / "item" / f"{TEXTURE}.png"
    tex_path.write_bytes(base64.b64decode(tex["source"].split(",", 1)[1]))

    # какие элементы в крышке
    lid_group = next(g for g in model["groups"] if g["name"] == LID_GROUP)
    lid_uuids = set()
    for node in model["outliner"]:
        if node.get("uuid") == lid_group["uuid"]:
            lid_uuids = set(node.get("children", []))

    elements = model["elements"]
    lo, hi = bounds(elements)
    # сдвиг: по X и Z в центр блока, по Y — низом на пол
    shift = [CENTER - (lo[0] + hi[0]) / 2.0, -lo[1], CENTER - (lo[2] + hi[2]) / 2.0]

    def convert(el):
        out = {
            "from": [round(el["from"][i] + shift[i], 4) for i in range(3)],
            "to": [round(el["to"][i] + shift[i], 4) for i in range(3)],
            "faces": {},
        }
        for name, f in (el.get("faces") or {}).items():
            if f.get("texture") is None:
                continue
            u1, v1, u2, v2 = f["uv"]
            out["faces"][name] = {
                "uv": [round(u1 * uv_scale[0], 4), round(v1 * uv_scale[1], 4),
                       round(u2 * uv_scale[0], 4), round(v2 * uv_scale[1], 4)],
                "texture": "#0",
            }
        return out

    base_el = [convert(e) for e in elements if e["uuid"] not in lid_uuids]
    lid_el = [convert(e) for e in elements if e["uuid"] in lid_uuids]

    # Петля: шов между низом и верхом, у задней кромки. Замок нарисован спереди
    # (минимальный Z), значит петля висит на максимальном.
    blo, bhi = bounds([e for e in elements if e["uuid"] not in lid_uuids])
    hinge = [round(CENTER, 4),
             round(bhi[1] + shift[1], 4),
             round(bhi[2] + shift[2], 4)]

    def write_model(name, els):
        body = {
            "credit": "NationRise",
            "texture_size": [res.get("width", 16), res.get("height", 16)],
            "textures": {"0": f"minecraft:item/{TEXTURE}", "particle": f"minecraft:item/{TEXTURE}"},
            "elements": els,
            # Дисплей рисует предмет как есть, без ванильных доворотов для руки и головы:
            # модель ставится в мир, а не держится в руке.
            "display": {"fixed": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]}},
        }
        (PACK / "models" / "item").mkdir(parents=True, exist_ok=True)
        p = PACK / "models" / "item" / f"{name}.json"
        json.dump(body, io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return p

    write_model(BASE_MODEL, base_el)
    write_model(LID_MODEL, lid_el)

    # прописываем в range_dispatch базового предмета
    items = PACK / "items"
    items.mkdir(parents=True, exist_ok=True)
    chest_json = items / "chest.json"
    # Запасная ветка — ВАНИЛЬНОЕ определение сундука целиком, вплоть до рождественской
    # текстуры. Обычной моделью его заменить нельзя: сундук рисуется особым рендером, а
    # `minecraft:item/chest` — только подложка для него, не самостоятельная модель. Стоило
    # подставить её напрямую, и все сундуки в руках и в инвентаре стали невидимыми.
    VANILLA_CHEST = {
        "type": "minecraft:select",
        "property": "minecraft:local_time",
        "pattern": "MM-dd",
        "cases": [{
            "when": ["12-24", "12-25", "12-26"],
            "model": {"type": "minecraft:special", "base": "minecraft:item/chest",
                      "model": {"type": "minecraft:chest", "texture": "minecraft:christmas"}},
        }],
        "fallback": {"type": "minecraft:special", "base": "minecraft:item/chest",
                     "model": {"type": "minecraft:chest", "texture": "minecraft:normal"}},
    }
    if chest_json.exists():
        disp = json.load(io.open(chest_json, encoding="utf-8"))
        disp["model"]["fallback"] = VANILLA_CHEST
    else:
        disp = {"model": {"type": "minecraft:range_dispatch",
                          "property": "minecraft:custom_model_data", "index": 0,
                          "fallback": VANILLA_CHEST,
                          "entries": []}}
    entries = [e for e in disp["model"]["entries"] if e["threshold"] not in (CMD_BASE, CMD_LID)]
    entries.append({"threshold": CMD_BASE,
                    "model": {"type": "minecraft:model", "model": f"minecraft:item/{BASE_MODEL}"}})
    entries.append({"threshold": CMD_LID,
                    "model": {"type": "minecraft:model", "model": f"minecraft:item/{LID_MODEL}"}})
    disp["model"]["entries"] = sorted(entries, key=lambda e: e["threshold"])
    json.dump(disp, io.open(chest_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("модели записаны в пак:")
    print(f"  низ:     item/{BASE_MODEL}.json   ({len(base_el)} кубов, CMD {CMD_BASE})")
    print(f"  крышка:  item/{LID_MODEL}.json    ({len(lid_el)} кубов, CMD {CMD_LID})")
    print(f"  текстура: {tex_path.name} ({tex_path.stat().st_size} б)")
    print(f"  предмет-носитель: minecraft:chest")
    print()
    print(f"  габариты: X {lo[0]+shift[0]:.1f}..{hi[0]+shift[0]:.1f}, "
          f"Y {lo[1]+shift[1]:.1f}..{hi[1]+shift[1]:.1f}, "
          f"Z {lo[2]+shift[2]:.1f}..{hi[2]+shift[2]:.1f}")
    print(f"  ПЕТЛЯ (вписать в конфиг royal.hinge): {hinge[0]}, {hinge[1]}, {hinge[2]}")


if __name__ == "__main__":
    main()
