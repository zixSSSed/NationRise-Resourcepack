# -*- coding: utf-8 -*-
"""Два глифа, которые шрифт не вытянул на 16 px, — рисуем сами.

🧱 в Segoe UI Symbol нет вообще, силуэт из Emoji вышел сплошным белым пятном.
🗺 в Symbol есть, но это карта мира с континентами — на такой сетке каша.
Остальные 22 из build_guiglyphs2.py шрифт отдал нормально.
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTTEX = os.path.join(ROOT, "pack", "assets", "minecraft", "textures", "font")
W = (255, 255, 255, 255)
CLEAR = (0, 0, 0, 0)


def new():
    im = Image.new("RGBA", (16, 16), CLEAR)
    return im, ImageDraw.Draw(im)


def worldmap():
    """Сложенная гармошкой бумажная карта: три панели, средняя приподнята."""
    im, d = new()
    d.line([(1, 3), (5, 3)], fill=W)        # верх левой панели
    d.line([(5, 1), (10, 1)], fill=W)       # верх средней (выше — отсюда «сгиб»)
    d.line([(10, 3), (14, 3)], fill=W)      # верх правой
    d.line([(1, 12), (5, 12)], fill=W)      # низ левой
    d.line([(5, 10), (10, 10)], fill=W)     # низ средней
    d.line([(10, 12), (14, 12)], fill=W)    # низ правой
    d.line([(1, 3), (1, 12)], fill=W)       # левый край
    d.line([(14, 3), (14, 12)], fill=W)     # правый край
    d.line([(5, 1), (5, 12)], fill=W)       # линия сгиба
    d.line([(10, 1), (10, 12)], fill=W)     # линия сгиба
    return im


def brick():
    """Кладка в перевязку: три курса, швы — прозрачные, иначе снова выйдет пятно."""
    im, d = new()
    for y in (1, 6, 11):
        d.rectangle([1, y, 14, y + 3], fill=W)
    # средний курс сдвинут: половинка у края берётся в 2 px, иначе она читается
    # не как кирпич, а как случайная царапина
    for y, joints in ((1, (5, 10)), (6, (3, 8, 13)), (11, (5, 10))):
        for x in joints:
            d.line([(x, y), (x, y + 3)], fill=CLEAR)
    return im


for name, im in (("worldmap", worldmap()), ("brick", brick())):
    im.save(os.path.join(FONTTEX, f"nr_gui_{name}.png"))
    print("перерисован nr_gui_%s.png" % name)

# превью на фирменном тёмном, крем-тоном
sheet = Image.new("RGBA", (2 * 76 + 12, 88), (28, 22, 38, 255))
for i, (name, im) in enumerate((("worldmap", worldmap()), ("brick", brick()))):
    g = im.resize((64, 64), Image.NEAREST)
    tint = Image.new("RGBA", g.size, CLEAR)
    tint.paste((247, 250, 219, 255), (0, 0), g.split()[3])
    tint.putalpha(g.split()[3])
    sheet.alpha_composite(tint, (12 + i * 76, 12))
sheet.save(os.path.join(ROOT, "logo", "_guiglyphs2_fix_preview.png"))
