# -*- coding: utf-8 -*-
"""Generate six deterministic 32x32 NationRise BlueMap POI icons."""

from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont


ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "bluemap")
PREVIEW = os.path.join(ROOT, "logo", "bluemap-town-icons-preview.png")

SIZE = 32
DARK = "#17202D"
WHITE = "#F2F5F8"
STEEL = "#3B82C4"
STEEL_LIGHT = "#72C7F2"
GOLD = "#E0A93C"
GOLD_LIGHT = "#FFE36A"
EMERALD = "#3CA76A"
EMERALD_LIGHT = "#72DD91"
CARMINE = "#CF4E4E"
PURPLE = "#8A58C7"
BROWN = "#7A4B2A"
BROWN_LIGHT = "#C78343"
STONE = "#8B95A3"
STONE_LIGHT = "#CBD3DD"


def canvas():
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    return image, ImageDraw.Draw(image)


def shield(draw, fill, highlight):
    points = [(3, 3), (29, 3), (29, 19), (25, 26), (16, 31),
              (7, 26), (3, 19)]
    draw.polygon(points, fill=fill)
    draw.line(points + [points[0]], fill=DARK, width=2, joint="curve")
    draw.line([(5, 5), (27, 5), (27, 18)], fill=highlight, width=2)
    draw.line([(7, 24), (16, 29), (25, 24)], fill=DARK, width=1)


def cottage(draw, x, y, wall=BROWN_LIGHT, roof=GOLD):
    draw.rectangle((x, y + 4, x + 8, y + 11), fill=wall, outline=DARK, width=1)
    draw.polygon([(x - 1, y + 4), (x + 4, y), (x + 9, y + 4)], fill=roof)
    draw.line([(x - 1, y + 4), (x + 4, y), (x + 9, y + 4)], fill=DARK, width=1)
    draw.rectangle((x + 3, y + 7, x + 5, y + 11), fill=DARK)
    draw.point((x + 1, y + 6), fill=WHITE)


def tower(draw, x, y, height=12, accent=STEEL):
    draw.rectangle((x, y, x + 6, y + height), fill=STONE, outline=DARK)
    draw.rectangle((x - 1, y - 2, x + 7, y + 1), fill=STONE_LIGHT, outline=DARK)
    draw.rectangle((x + 2, y + 3, x + 4, y + 6), fill=accent)
    draw.rectangle((x + 2, y + height - 3, x + 4, y + height), fill=DARK)


def wall(draw, x1, y1, x2, y2, accent):
    draw.rectangle((x1, y1, x2, y2), fill=STONE, outline=DARK)
    for x in range(x1, x2 + 1, 4):
        draw.rectangle((x, y1 - 2, min(x + 2, x2), y1), fill=STONE_LIGHT, outline=DARK)
    draw.rectangle(((x1 + x2) // 2 - 1, y2 - 4, (x1 + x2) // 2 + 1, y2), fill=accent)


def level_one():
    im, d = canvas()
    shield(d, BROWN, BROWN_LIGHT)
    cottage(d, 11, 10, BROWN_LIGHT, GOLD)
    d.rectangle((8, 23, 24, 25), fill=EMERALD, outline=DARK)
    return im


def level_two():
    im, d = canvas()
    shield(d, EMERALD, EMERALD_LIGHT)
    cottage(d, 5, 14, BROWN_LIGHT, GOLD)
    tower(d, 18, 10, 14, EMERALD)
    d.point((21, 12), fill=WHITE)
    return im


def level_three():
    im, d = canvas()
    shield(d, STEEL, STEEL_LIGHT)
    wall(d, 6, 17, 26, 25, STEEL)
    tower(d, 13, 8, 17, STEEL_LIGHT)
    d.line((16, 6, 16, 10), fill=DARK, width=1)
    d.polygon([(17, 6), (23, 8), (17, 10)], fill=CARMINE, outline=DARK)
    return im


def level_four():
    im, d = canvas()
    shield(d, PURPLE, "#C28CFF")
    wall(d, 5, 17, 27, 25, PURPLE)
    tower(d, 6, 10, 15, PURPLE)
    tower(d, 19, 10, 15, PURPLE)
    tower(d, 12, 6, 19, PURPLE)
    d.polygon([(13, 6), (16, 2), (19, 6)], fill=GOLD, outline=DARK)
    return im


def level_five():
    im, d = canvas()
    shield(d, GOLD, GOLD_LIGHT)
    wall(d, 4, 17, 28, 25, STEEL)
    tower(d, 5, 9, 16, GOLD)
    tower(d, 21, 9, 16, GOLD)
    tower(d, 12, 5, 20, GOLD)
    d.polygon([(13, 5), (16, 1), (19, 5)], fill=WHITE, outline=DARK)
    d.rectangle((15, 0, 17, 3), fill=GOLD_LIGHT, outline=DARK)
    d.point((16, 10), fill=STEEL_LIGHT)
    return im


def capital_crown():
    im, d = canvas()
    points = [(2, 10), (7, 18), (12, 7), (16, 18), (21, 7),
              (25, 18), (30, 10), (27, 26), (5, 26)]
    d.polygon(points, fill=GOLD)
    d.line(points + [points[0]], fill=DARK, width=2, joint="curve")
    d.rectangle((5, 23, 27, 28), fill=GOLD, outline=DARK, width=2)
    for x, color in ((8, CARMINE), (16, STEEL), (24, CARMINE)):
        d.polygon([(x, 20), (x + 2, 22), (x, 24), (x - 2, 22)], fill=color, outline=DARK)
    d.line((4, 11, 8, 17), fill=GOLD_LIGHT, width=2)
    d.point((12, 9), fill=WHITE)
    return im


ICONS = [
    ("nationrise-town-level-1.png", "Уровень 1", level_one),
    ("nationrise-town-level-2.png", "Уровень 2", level_two),
    ("nationrise-town-level-3.png", "Уровень 3", level_three),
    ("nationrise-town-level-4.png", "Уровень 4", level_four),
    ("nationrise-town-level-5.png", "Уровень 5", level_five),
    ("nationrise-town-capital.png", "Столица", capital_crown),
]


def preview_font(size):
    for path in (
        r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_preview(rendered):
    width, height = 1170, 250
    sheet = Image.new("RGBA", (width, height), "#10151D")
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (24, 16),
        "NationRise BlueMap — уровни городов и столица",
        font=preview_font(26),
        fill=WHITE,
    )
    draw.text(
        (24, 51),
        "PNG 32×32 · рекомендуемый anchor (16, 31) · корона заменяет уровень",
        font=preview_font(16),
        fill=STONE_LIGHT,
    )
    for index, (name, title, image) in enumerate(rendered):
        x = 18 + index * 190
        draw.rounded_rectangle(
            (x, 86, x + 176, 232),
            radius=10,
            fill="#202936",
            outline="#39485C",
        )
        sheet.alpha_composite(
            image.resize((96, 96), Image.Resampling.NEAREST), (x + 40, 96)
        )
        label = f"{index + 1}. {title}" if index < 5 else "★ Столица"
        draw.text((x + 38, 198), label, font=preview_font(16), fill=WHITE)
    os.makedirs(os.path.dirname(PREVIEW), exist_ok=True)
    sheet.save(PREVIEW)


def main():
    os.makedirs(OUT, exist_ok=True)
    rendered = []
    for name, title, factory in ICONS:
        image = factory()
        if image.size != (32, 32) or image.mode != "RGBA" or not image.getbbox():
            raise RuntimeError(f"Invalid BlueMap icon: {name}")
        image.save(os.path.join(OUT, name), optimize=True)
        rendered.append((name, title, image))
    make_preview(rendered)
    print(f"BlueMap icons: {len(rendered)} generated")
    print(f"Output: {OUT}")
    print(f"Preview: {PREVIEW}")


if __name__ == "__main__":
    main()
