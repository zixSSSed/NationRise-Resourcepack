# -*- coding: utf-8 -*-
"""
Временные текстуры предметов чудес света: осколок тотема и чертёж.

Рисуются пиксель-в-пиксель, а не режутся из ванильного тотема: ванильных ассетов
в репозитории нет, а тянуть их из клиентского jar — лишняя зависимость ради заглушки.
Владелец обещал прислать нормальную bbmodel — тогда эти файлы просто заменятся.

Запуск: py -3.13 build_wonder_items.py
"""
from PIL import Image
from pathlib import Path

PACK = Path(__file__).parent / "pack" / "assets" / "minecraft"
TEX = PACK / "textures" / "item"
MODELS = PACK / "models" / "item"

# Палитра ванильного тотема: тёплое золото + нефритовая вставка + тёмный контур.
OUTLINE = (44, 30, 12, 255)
GOLD_D = (150, 100, 26, 255)
GOLD = (214, 155, 44, 255)
GOLD_L = (245, 205, 106, 255)
JADE_D = (30, 110, 70, 255)
JADE = (58, 168, 104, 255)

# Чертёж: холодная бумага с сеткой и золотой печатью.
PAPER_D = (108, 128, 156, 255)
PAPER = (168, 190, 214, 255)
PAPER_L = (214, 230, 244, 255)
INK = (46, 66, 96, 255)


def draw(pixels):
    """pixels: список строк по 16 символов, символ — ключ палитры."""
    key = {
        ".": (0, 0, 0, 0),
        "#": OUTLINE,
        "d": GOLD_D, "g": GOLD, "l": GOLD_L,
        "j": JADE, "J": JADE_D,
        "p": PAPER, "P": PAPER_L, "q": PAPER_D, "i": INK,
    }
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(pixels):
        assert len(row) == 16, f"строка {y} длиной {len(row)}, нужно 16"
        for x, ch in enumerate(row):
            img.putpixel((x, y), key[ch])
    return img


# Осколок: отколотый клин верхушки тотема — золото с нефритовым глазом,
# слева ровный скол, справа зазубрина, чтобы читалось «часть чего-то целого».
SHARD = [
    "................",
    "........##......",
    ".......#ld#.....",
    "......#lggd#....",
    "......#lgjd#....",
    ".....#lgjjgd#...",
    ".....#lgjJgd#...",
    "....#lggjjggd#..",
    "....#lgggggd#...",
    "....#lggggd#....",
    ".....#lgggd#....",
    ".....#lggd#.....",
    "......#lgd#.....",
    "......#ld#......",
    ".......##.......",
    "................",
]

# Чертёж: свёрнутый лист с линиями плана и золотой печатью в углу.
BLUEPRINT = [
    "................",
    "..############..",
    "..#PPPPPPPPPP#..",
    "..#PiiiiPPPPP#..",
    "..#PiqqiPPPPP#..",
    "..#PiqqiiiiiP#..",
    "..#PiiiiqqqiP#..",
    "..#PPPPPqqqiP#..",
    "..#PiiiiiiiiP#..",
    "..#PiqqqqqqiP#..",
    "..#PiqqqqqqiP#..",
    "..#PiiiiiiiiP#..",
    "..#PPPPPP#ld#...",
    "..#PPPPP#lggd#..",
    "..#######lggd#..",
    "..........###...",
]

MODEL = """{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "minecraft:item/%s"
  }
}
"""

for name, art in (("nr_totem_shard", SHARD), ("nr_wonder_blueprint", BLUEPRINT)):
    draw(art).save(TEX / f"{name}.png", optimize=True)
    (MODELS / f"{name}.json").write_text(MODEL % name, encoding="utf-8")
    print("готово:", name)
