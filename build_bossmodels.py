# -*- coding: utf-8 -*-
"""Кладёт модели боссов в BetterModel, выбросив из них неиспользуемые текстуры.

Тот же приём, что и в build_cerberus.py: у моделей Littleroom в списке текстур лежат
рабочие черновики автора, а гранями заняты одна-две. Всё лишнее уехало бы игрокам в паке
просто так, поэтому чистим — и обязательно перебиваем номера, потому что грань ссылается
на текстуру НОМЕРОМ в списке, и после удаления они съезжают.

    py -3.13 build_bossmodels.py

Дальше как всегда: запустить сервер (BetterModel пересоберёт свой пак) и прогнать
pack_client.py. Модели Littleroom требуют указания авторства везде, где их видно.
"""

import json
import shutil
from pathlib import Path

BRAND = Path(__file__).parent
SCRATCH = Path(
    r"C:\Users\bravl\AppData\Local\Temp\claude\C--Users-bravl-OneDrive-Desktop-prilC--Claude"
    r"\6c24310f-32e3-4122-b78f-7a9292d66534\scratchpad\candidates"
)
MODELS_OUT = Path(r"C:\Users\bravl\PaperServer\plugins\BetterModel\models")
PACK = BRAND / "pack" / "assets" / "nationrise"

# имя в BetterModel -> путь к исходнику
SOURCES = {
    "lr_yeti": SCRATCH / "yeti" / "plugins" / "ModelEngine" / "blueprints" / "lr_yeti.bbmodel",
    "merloc": SCRATCH / "merloc" / "plugins" / "ModelEngine" / "blueprints" / "merloc.bbmodel",
    # Свита Аквамена: мина и ударная волна над головой в момент оглушения.
    "sea_mine": SCRATCH / "merloc" / "plugins" / "ModelEngine" / "blueprints" / "sea_mine.bbmodel",
    "concussion": SCRATCH / "merloc" / "plugins" / "ModelEngine" / "blueprints" / "concussion.bbmodel",
    # Свита йети: катящийся ком и ледяные шипы, вырастающие под игроками.
    "lr_yeti_snowball": SCRATCH / "yeti" / "plugins" / "ModelEngine" / "blueprints" / "lr_yeti_snowball.bbmodel",
    "lr_yeti_icespikes": SCRATCH / "yeti" / "plugins" / "ModelEngine" / "blueprints" / "lr_yeti_icespikes.bbmodel",
    # Минотавр: сам он и та же ударная волна (файл в его пакете свой, но модель одна и та же).
    "lr_minotaur": SCRATCH / "minotaur" / "plugins" / "ModelEngine" / "blueprints" / "LR_minotaur.bbmodel",
    # Медуза: она, змея с её головы (летит и кусает) и каменная фигура — ею накрывает
    # окаменевших игроков, из неё же собрано кольцо статуй вокруг арены.
    "medusa": SCRATCH / "medusa" / "plugins" / "ModelEngine" / "blueprints" / "medusa.bbmodel",
    "medusa_snakehead": SCRATCH / "medusa" / "plugins" / "ModelEngine" / "blueprints" / "medusa_snakehead.bbmodel",
    "stone_player": SCRATCH / "medusa" / "plugins" / "ModelEngine" / "blueprints" / "stone_player.bbmodel",
    # Гидра: сама она, отрубленная голова (падает рядом) и куски земли вдоль трещины.
    "lr_hydra": SCRATCH / "hydra" / "plugins" / "ModelEngine" / "blueprints" / "littleroom" / "hydra" / "lr_hydra.bbmodel",
    "lr_hydra_head": SCRATCH / "hydra" / "plugins" / "ModelEngine" / "blueprints" / "littleroom" / "hydra" / "lr_hydra_head.bbmodel",
    "lr_hydra_ground_break": SCRATCH / "hydra" / "plugins" / "ModelEngine" / "blueprints" / "littleroom" / "hydra" / "lr_hydra_ground_break.bbmodel",
}

# Звуки: раздел в нашем неймспейсе -> папка исходника и список файлов.
# Из кода зовутся ключом nationrise:<раздел>.<имя>. Берём только то, что реально играем:
# chest_spawn у йети — от их сундука с лутом, его у нас нет, а весит он больше всех.
SOUNDS = {
    "yeti": (
        SCRATCH / "yeti" / "resourcepack_sounds_items" / "assets" / "minecraft" / "sounds",
        ["swing1", "swing2", "swing3", "swing4", "swing5",
         "impact1", "impact2", "impact3", "impact4",
         "ground_impact1", "ground_impact2",
         "grunt1", "grunt2", "grunt3",
         "rage1", "rage2", "rage3",
         "snow_grab1", "snow_grab2", "snowball_roll", "snowball_impact",
         "yeti_dig", "yeti_wind", "poof"],
    ),
    "merloc": (
        SCRATCH / "merloc" / "resourcepack" / "assets" / "minecraft" / "sounds",
        ["scream_1", "scream_2", "scream_3",
         "trident_impact_1", "trident_impact_2", "trident_impact_3", "trident_impact_4", "trident_impact_5",
         "bubbles_1", "bubbles_2", "bubbles_3",
         "pfish_pop_1", "pfish_pop_2", "pfish_pop_3"],
    ),
    "minotaur": (
        SCRATCH / "minotaur" / "custom_sounds_resourcepack" / "assets" / "minecraft" / "sounds",
        ["bull1", "wind1",
         "chain1", "chain2", "chain3", "chain4",
         "ground1", "ground2", "ground3",
         "grunt1", "grunt2", "grunt3", "grunt4",
         "impact1", "impact2", "impact3", "impact4",
         "leap1", "leap2",
         "swing1", "swing2", "swing3", "swing4"],
    ),
    "medusa": (
        SCRATCH / "medusa" / "resourcepack_custom_sounds_items" / "assets" / "minecraft" / "sounds",
        ["glare", "spin", "twinsnakes", "shoot",
         "rockbreak1", "rockbreak2", "rockbreak3",
         "death", "deathfall"],
    ),
    "hydra": (
        SCRATCH / "hydra" / "resourcepack" / "assets" / "littleroom_hydra" / "sounds",
        ["bite_1", "bite_2",
         "growl_1", "growl_2", "growl_3",
         "grunt_1", "grunt_2", "grunt_3", "grunt_4", "grunt_5", "grunt_6",
         "hit_1", "hit_2", "hit_3", "hit_4",
         "ground_crack_1", "ground_crack_2", "ground_crack_3",
         "flamethrower_40tick", "flamethrower_loop",
         "dismember_head", "land", "leap", "spotted_roar",
         "death", "death_poof"],
    ),
}


def used_texture_indices(model):
    used = set()
    for el in model.get("elements", []):
        for face in (el.get("faces") or {}).values():
            if isinstance(face, dict) and isinstance(face.get("texture"), int) and face["texture"] >= 0:
                used.add(face["texture"])
    return used


def strip_textures(model):
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


def find_ogg(root, name):
    """Файл может лежать в любой подпапке неймспейса автора — ищем по имени."""
    hits = list(root.rglob(name + ".ogg"))
    return hits[0] if hits else None


def put_sounds():
    """Звуки в наш неймспейс + события в общий sounds.json (существующие не трогаем)."""
    json_path = PACK / "sounds.json"
    events = {}
    if json_path.exists():
        events = json.loads(json_path.read_text(encoding="utf-8"))
    total = 0
    for section, (root, names) in SOUNDS.items():
        if not root.exists():
            raise SystemExit(f"нет звуков: {root}")
        dst_dir = PACK / "sounds" / section
        dst_dir.mkdir(parents=True, exist_ok=True)
        for n in names:
            src = find_ogg(root, n)
            if src is None:
                raise SystemExit(f"нет файла звука: {section}/{n}.ogg")
            dst = dst_dir / f"{n}.ogg"
            shutil.copy2(src, dst)
            total += dst.stat().st_size
            events[f"{section}.{n}"] = {"sounds": [f"{section}/{n}"]}
        print(f"звуки {section}: {len(names)} файлов")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"итого звуков добавлено: {total} б; событий в sounds.json: {len(events)}")


def main():
    MODELS_OUT.mkdir(parents=True, exist_ok=True)
    for name, src in SOURCES.items():
        if not src.exists():
            raise SystemExit(f"нет исходника: {src}")
        model = json.loads(src.read_text(encoding="utf-8"))
        fmt = model.get("meta", {}).get("model_format")
        if fmt != "free":
            raise SystemExit(f"{name}: формат «{fmt}», а BetterModel принимает только free")
        was, now = strip_textures(model)
        out = MODELS_OUT / f"{name}.bbmodel"
        out.write_text(json.dumps(model, ensure_ascii=False), encoding="utf-8")
        anims = [a["name"] for a in model.get("animations", [])]
        print(f"{name}: текстур {was} -> {now}, {out.stat().st_size} б, анимаций {len(anims)}")
        print("   " + ", ".join(anims))
    put_sounds()
    print("\nдальше: запустить сервер, затем py -3.13 pack_client.py")


if __name__ == "__main__":
    main()
