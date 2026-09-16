"""Готовит модель Королевской Сокровищницы для BetterModel.

Художник отдаёт сундук в формате java_block: это формат для блоков ресурспака, в нём нет
ни костей с осью вращения, ни анимаций вообще. BetterModel принимает только `free` —
формат с произвольной геометрией и скелетом. Скрипт переводит одно в другое и добавляет
крышку, которая открывается.

Что именно делается:

1. `model_format` меняется на `free` — иначе BetterModel молча не подхватит файл.

2. Модель сдвигается так, чтобы стоять НА точке привязки и быть отцентрованной по ней.
   В исходнике сундук нарисован в углу координат (X от -1 до 25), и если этого не сделать,
   он вылезет на полтора блока в сторону от места, куда его поставили.

3. Группе `Verh` (весь верх сундука) выставляется ось вращения по задней нижней кромке —
   это и есть петля. В исходнике у обеих групп origin стоит в [8,8,8], то есть посреди
   сундука: крышка вращалась бы вокруг собственной середины и уезжала внутрь ящика.

4. Добавляются три анимации: `idle` (крышка закрыта), `open` (открывается и ОСТАЁТСЯ
   открытой — режим hold) и `close`.

Запуск: py -3.13 build_royal_chest.py [путь к исходному .bbmodel]
Результат кладётся в plugins/BetterModel/models/royal_chest.bbmodel.
"""

import io
import json
import sys
import uuid
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1
           else r"C:\Users\bravl\Downloads\RoyalChest.bbmodel")
OUT = Path(r"C:\Users\bravl\PaperServer\plugins\BetterModel\models\royal_chest.bbmodel")

# Группа, которая открывается. Художник уже разделил модель на верх и низ — используем это.
LID_GROUP = "Verh"

# Насколько распахивается крышка. Знак: положительный поворот по X поднимает переднюю
# кромку вверх (петля сзади). Если в игре крышка провалится вниз — поменять на -OPEN_ANGLE.
OPEN_ANGLE = 60.0


def bounds(elements):
    """Габариты всей модели по элементам."""
    lo = [float("inf")] * 3
    hi = [float("-inf")] * 3
    for e in elements:
        for i in range(3):
            lo[i] = min(lo[i], e["from"][i], e["to"][i])
            hi[i] = max(hi[i], e["from"][i], e["to"][i])
    return lo, hi


def main():
    model = json.load(io.open(SRC, encoding="utf-8"))
    elements = model["elements"]

    # ---- 1. формат ----
    model["meta"]["model_format"] = "free"
    model["meta"]["format_version"] = "4.10"   # версия, на которой работают модели из поставки
    model.pop("java_block_version", None)
    model.pop("parent", None)
    model["name"] = "royal_chest"

    # ---- 2. центрирование ----
    lo, hi = bounds(elements)
    shift = [-(lo[0] + hi[0]) / 2.0, -lo[1], -(lo[2] + hi[2]) / 2.0]
    for e in elements:
        for key in ("from", "to", "origin"):
            if key in e:
                e[key] = [round(e[key][i] + shift[i], 4) for i in range(3)]

    # ---- 3. петля крышки ----
    lid = next(g for g in model["groups"] if g["name"] == LID_GROUP)
    lid_uuids = set()
    for node in model["outliner"]:
        if node["uuid"] == lid["uuid"]:
            lid_uuids = set(node["children"])
    lid_elements = [e for e in elements if e["uuid"] in lid_uuids]
    base_elements = [e for e in elements if e["uuid"] not in lid_uuids]
    llo, lhi = bounds(lid_elements)
    blo, bhi = bounds(base_elements)
    # Ось — по шву между низом и верхом, у ЗАДНЕЙ кромки: по центру ширины, на высоте
    # верха основания, у его дальнего края. Замок нарисован спереди (минимальный Z),
    # значит петля висит на максимальном.
    #
    # Считать по габаритам самой крышки нельзя: в группу верха входят декоративные
    # петли, нарисованные ниже шва, и ось уезжала бы внутрь основания — верх при
    # открывании вспарывал бы ящик снизу.
    hinge = [round((blo[0] + bhi[0]) / 2.0, 4), round(bhi[1], 4), round(bhi[2], 4)]
    lid["origin"] = hinge
    lid["name"] = "lid"
    for g in model["groups"]:
        if g["name"] != "lid":
            g["name"] = "base"
            g["origin"] = [0, 0, 0]

    # ---- 4. анимации ----
    def key(time, angle):
        return {
            "channel": "rotation",
            "data_points": [{"x": str(angle), "y": "0", "z": "0"}],
            "uuid": str(uuid.uuid4()),
            "time": time,
            "color": -1,
            "interpolation": "linear",
            "bezier_linked": True,
            "bezier_left_time": [-0.1, -0.1, -0.1],
            "bezier_left_value": [0, 0, 0],
            "bezier_right_time": [0.1, 0.1, 0.1],
            "bezier_right_value": [0, 0, 0],
        }

    def anim(name, loop, length, frames):
        return {
            "uuid": str(uuid.uuid4()),
            "name": name,
            "loop": loop,
            "override": False,
            "length": length,
            "snapping": 24,
            "selected": False,
            "saved": True,
            "path": "",
            "anim_time_update": "",
            "blend_weight": "",
            "start_delay": "",
            "loop_delay": "",
            "animators": {
                lid["uuid"]: {
                    "name": "lid",
                    "type": "bone",
                    "keyframes": [key(t, a) for t, a in frames],
                }
            },
        }

    model["animations"] = [
        # Крышка закрыта. Нужна как состояние покоя: без неё сундук после close
        # остаётся в позе последнего кадра предыдущей анимации.
        anim("idle", "loop", 1.0, [(0.0, 0.0), (1.0, 0.0)]),
        # hold — крышка ОСТАЁТСЯ поднятой, пока её не закроют. С "once" она хлопнула бы
        # обратно сразу после проигрывания, и открытым сундук выглядел бы полсекунды.
        anim("open", "hold", 0.5, [(0.0, 0.0), (0.5, OPEN_ANGLE)]),
        anim("close", "once", 0.4, [(0.0, OPEN_ANGLE), (0.4, 0.0)]),
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(model, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False)

    print(f"готово: {OUT}")
    print(f"  габариты после сдвига: X {lo[0]+shift[0]:.1f}..{hi[0]+shift[0]:.1f}, "
          f"Y {lo[1]+shift[1]:.1f}..{hi[1]+shift[1]:.1f}, "
          f"Z {lo[2]+shift[2]:.1f}..{hi[2]+shift[2]:.1f} (в пикселях, 16 = блок)")
    print(f"  размер в блоках: {(hi[0]-lo[0])/16:.2f} x {(hi[1]-lo[1])/16:.2f} x {(hi[2]-lo[2])/16:.2f}")
    print(f"  петля крышки: {hinge}")
    print(f"  анимации: {[a['name'] for a in model['animations']]}")


if __name__ == "__main__":
    main()
