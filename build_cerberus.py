# -*- coding: utf-8 -*-
"""Готовит Цербера: модели для BetterModel и его голос для нашего ресурспака.

Что делает
----------
1. Кладёт `cerberus.bbmodel` и `hellhound.bbmodel` в `plugins/BetterModel/models`,
   выбросив из них неиспользуемые текстуры. В исходнике их шесть, а гранями заняты две:
   остальные — рабочие черновики автора и картинка-аватарка на 150 КБ. Они бы уехали
   игрокам в паке просто так.
2. Раскладывает звуки пса в `pack/assets/nationrise`: сами ogg и `sounds.json` с именами
   событий. Из кода они зовутся ключом `nationrise:cerberus.<имя>`.

Почему индексы текстур приходится перебивать
--------------------------------------------
В bbmodel грань ссылается на текстуру НОМЕРОМ в списке. Выкинуть лишние и оставить список
как есть нельзя — номера съедут, и модель раскрасится чужими картинками (а чаще станет
прозрачной). Поэтому строим карту «старый номер → новый» и проходим по всем граням.

Порядок работы
--------------
    py -3.13 build_cerberus.py          # модели + звуки
    <запустить сервер: BetterModel пересоберёт свой build.zip>
    py -3.13 pack_zip.py                # наш пак со звуками
    py -3.13 build_models_pack.py       # брендированный пак моделей
    py -3.13 build_all_pack.py          # общий пак для клиента

Отдельно: модели Littleroom требуют указания авторства везде, где их видно.
"""

import json
import shutil
from pathlib import Path

BRAND = Path(__file__).parent
SRC = Path(
    r"C:\Users\bravl\AppData\Local\Temp\claude\C--Users-bravl-OneDrive-Desktop-prilC--Claude"
    r"\6c24310f-32e3-4122-b78f-7a9292d66534\scratchpad\littleroom\cerberus\cerberus"
)
BLUEPRINTS = SRC / "plugins" / "ModelEngine" / "blueprints"
SOUNDS_SRC = SRC / "custom_sounds_resourcepack" / "assets" / "minecraft" / "sounds" / "littleroom" / "cerberus"

MODELS_OUT = Path(r"C:\Users\bravl\PaperServer\plugins\BetterModel\models")
PACK = BRAND / "pack"
SOUNDS_OUT = PACK / "assets" / "nationrise" / "sounds" / "cerberus"
SOUNDS_JSON = PACK / "assets" / "nationrise" / "sounds.json"

# Событие в паке -> файл в исходнике. Третий лай у автора лежит под именем bark4.
SOUND_MAP = {
    "growl1": "growl1", "growl2": "growl2", "growl3": "growl3",
    "bark1": "bark1", "bark2": "bark2", "bark3": "bark4",
    "chain1": "chain1", "chain2": "chain2", "chain3": "chain3",
    "chainswing": "chainswing",
    "impact_ground": "impact_ground", "impact_ground_big": "impact_ground_big",
    "styx_rumble": "styx_rumble",
    "wake": "wake", "whimper": "whimper", "poof": "poof",
}


def used_texture_indices(model):
    """Номера текстур, на которые реально ссылаются грани."""
    used = set()
    for el in model.get("elements", []):
        for face in (el.get("faces") or {}).values():
            if isinstance(face, dict) and isinstance(face.get("texture"), int) and face["texture"] >= 0:
                used.add(face["texture"])
    return used


def strip_textures(model):
    """Оставить только занятые текстуры и перебить номера граней. Возвращает (было, стало)."""
    textures = model.get("textures", [])
    used = used_texture_indices(model)
    if not used or len(used) == len(textures):
        return len(textures), len(textures)

    keep = [i for i in range(len(textures)) if i in used]
    remap = {old: new for new, old in enumerate(keep)}
    model["textures"] = [textures[i] for i in keep]
    for new, tex in enumerate(model["textures"]):
        if "id" in tex:
            tex["id"] = str(new)

    for el in model.get("elements", []):
        for face in (el.get("faces") or {}).values():
            if isinstance(face, dict) and isinstance(face.get("texture"), int):
                face["texture"] = remap.get(face["texture"], 0)
    return len(textures), len(keep)


def put_model(name):
    src = BLUEPRINTS / f"{name}.bbmodel"
    if not src.exists():
        raise SystemExit(f"нет исходника модели: {src}")
    model = json.loads(src.read_text(encoding="utf-8"))
    fmt = model.get("meta", {}).get("model_format")
    if fmt != "free":
        raise SystemExit(f"{name}: формат «{fmt}», а BetterModel принимает только free")
    was, now = strip_textures(model)
    MODELS_OUT.mkdir(parents=True, exist_ok=True)
    out = MODELS_OUT / f"{name}.bbmodel"
    out.write_text(json.dumps(model, ensure_ascii=False), encoding="utf-8")
    anims = [a["name"] for a in model.get("animations", [])]
    print(f"  {name}: текстур {was} -> {now}, анимаций {len(anims)}, {out.stat().st_size} б")
    print(f"    {', '.join(anims)}")


def put_sounds():
    if not SOUNDS_SRC.exists():
        raise SystemExit(f"нет звуков: {SOUNDS_SRC}")
    SOUNDS_OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for event, filename in SOUND_MAP.items():
        src = SOUNDS_SRC / f"{filename}.ogg"
        if not src.exists():
            raise SystemExit(f"нет файла звука: {src}")
        dst = SOUNDS_OUT / f"{event}.ogg"
        shutil.copy2(src, dst)
        total += dst.stat().st_size

    existing = {}
    if SOUNDS_JSON.exists():
        existing = json.loads(SOUNDS_JSON.read_text(encoding="utf-8"))
    for event in SOUND_MAP:
        existing[f"cerberus.{event}"] = {"sounds": [f"cerberus/{event}"]}
    SOUNDS_JSON.parent.mkdir(parents=True, exist_ok=True)
    SOUNDS_JSON.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  звуков: {len(SOUND_MAP)} ({total} б) -> {SOUNDS_OUT}")
    print(f"  события: {SOUNDS_JSON} (всего {len(existing)})")


def main():
    print("модели:")
    for name in ("cerberus", "hellhound"):
        put_model(name)
    print("звуки:")
    put_sounds()
    print()
    print("дальше: запустить сервер (BetterModel пересоберёт build.zip),")
    print("        затем pack_zip.py -> build_models_pack.py -> build_all_pack.py")


if __name__ == "__main__":
    main()
