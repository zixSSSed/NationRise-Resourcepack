# -*- coding: utf-8 -*-
"""
Головы миньонов v2 — из ГОТОВЫХ файлов юзера (64×16, стандартная развёртка головы:
top(8,0) bottom(16,0) / right(0,8) front(8,8) left(16,8) back(24,8), hat-слой +32 по x).
Кладёт текстуры в пак и пишет модели (куб головы [4,0,4]-[12,8,12] + hat-оверлей),
display.head = scale 1.0 / translation 0 (проверенная посадка на стенде).
paper.json уже мапит CMD 71001-71004 на эти модели — его не трогаем.
Запуск: py -3.13 gen_minion_heads_v2.py
"""
import json, os, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "..")  # prilC++Claude — юзерские PNG
PACK = os.path.join(ROOT, "pack", "assets", "minecraft")

# файл юзера -> имя модели/текстуры в паке (CMD уже прописаны в items/paper.json)
HEADS = {
    "miner.png": "nr_minhead_miner",         # 71001 — шахтёр (кирка)
    "fermer.png": "nr_minhead_farmer",       # 71002 — фермер (мотыга)
    "drovosek.png": "nr_minhead_lumberjack", # 71003 — лесоруб (топор)
    "zemlekop.png": "nr_minhead_digger",     # 71004 — землекоп (лопата)
}

# UV: текстура 64×16 → x-фактор 16/64=0.25, y-фактор 16/16=1. Значения в юнитах модели (0-16).
def faces(off):  # off=0 — база, off=8 — hat-слой (+32px по x)
    return {
        "north": {"uv": [2 + off, 8, 4 + off, 16], "texture": "#s"},   # лицо (8,8)-(16,16)
        "south": {"uv": [6 + off, 8, 8 + off, 16], "texture": "#s"},   # затылок (24,8)-(32,16)
        "west":  {"uv": [0 + off, 8, 2 + off, 16], "texture": "#s"},   # правая щека (0,8)-(8,16)
        "east":  {"uv": [4 + off, 8, 6 + off, 16], "texture": "#s"},   # левая щека (16,8)-(24,16)
        "up":    {"uv": [2 + off, 0, 4 + off, 8], "texture": "#s"},    # макушка (8,0)-(16,8)
        "down":  {"uv": [4 + off, 0, 6 + off, 8], "texture": "#s"},    # низ (16,0)-(24,8)
    }

def model(tex):
    return {
        "__comment": "Голова миньона из файла юзера (64×16 head-развёртка).",
        "textures": {"s": f"minecraft:item/{tex}", "particle": f"minecraft:item/{tex}"},
        "elements": [
            {"name": "head", "from": [4, 5, 4], "to": [12, 13, 12], "faces": faces(0)},
            {"name": "hat", "from": [3.75, 4.75, 3.75], "to": [12.25, 13.25, 12.25], "faces": faces(8)},
        ],
        "display": {
            "head": {"translation": [0, 0, 0], "scale": [1.15, 1.15, 1.15]},  # чуть ниже + на 15% крупнее
            "gui": {"rotation": [26, 222, 0], "scale": [1.0, 1.0, 1.0]},
            "fixed": {"scale": [1.0, 1.0, 1.0]},
        },
    }

def main():
    tex_dir = os.path.join(PACK, "textures", "item")
    mdl_dir = os.path.join(PACK, "models", "item")
    for src_name, tex in HEADS.items():
        src = os.path.join(SRC, src_name)
        if not os.path.isfile(src):
            print(f"!! нет файла {src} — пропуск")
            continue
        shutil.copyfile(src, os.path.join(tex_dir, tex + ".png"))
        with open(os.path.join(mdl_dir, tex + ".json"), "w", encoding="utf-8") as f:
            json.dump(model(tex), f, ensure_ascii=False, indent=1)
        print(f"OK {src_name} -> {tex} (текстура + модель)")

if __name__ == "__main__":
    main()
