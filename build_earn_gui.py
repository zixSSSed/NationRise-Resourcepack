# -*- coding: utf-8 -*-
"""Generate the dedicated /earn marketplace background and its isolated font.

The glyph covers only the six server-controlled rows of a generic 54-slot menu.
It must never replace minecraft's global generic_54 texture: other plugins and the
player inventory keep their normal appearance.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
PACK = ROOT / "pack"
TEXTURE_DIR = PACK / "assets" / "nationrise" / "textures" / "font"
FONT_DIR = PACK / "assets" / "nationrise" / "font"
PREVIEW = ROOT / "logo" / "_earn_gui_preview.png"
TEXTURE = TEXTURE_DIR / "earn_bg.png"
FONT_JSON = FONT_DIR / "earn.json"

WIDTH, HEIGHT = 176, 125  # title/header (17 px) + six rows (6 * 18 px)
SUPERSAMPLE = 4
GLYPH = "\uf8c0"

PALETTE = {
    "shell": "#17121f",
    "shell_inner": "#282132",
    "outline": "#c9b8f2",
    "cream": "#f7fadb",
    "header": "#d9d9dc",
    "header_shadow": "#777783",
    "cyan": "#35c8d8",
    "cyan_dark": "#1d7788",
    "lime": "#7ed84b",
    "lime_dark": "#467b2a",
    "violet": "#9a5de0",
    "violet_dark": "#553180",
    "amber": "#f1a928",
    "amber_dark": "#915e11",
    "blue": "#4089bd",
    "blue_dark": "#234e70",
    "ink": "#241e2b",
}


def scale_box(box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    # PIL-боксы инклюзивны: масштабируем размах, а не координату конца,
    # иначе каждый прямоугольник рисуется на 0.75 px короче (right/bottom
    # уезжали ПОД иконку предмета вместо рамки вокруг неё).
    x0, y0, x1, y1 = box
    return (x0 * SUPERSAMPLE, y0 * SUPERSAMPLE,
            (x1 + 1) * SUPERSAMPLE - 1, (y1 + 1) * SUPERSAMPLE - 1)


def color(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = hex_color.removeprefix("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = ROOT / name
    if not path.exists():
        path = Path(r"C:\Windows\Fonts\segoeuib.ttf")
    return ImageFont.truetype(str(path), size * SUPERSAMPLE)


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int,
            fill: str, outline: str | None = None, width: int = 1) -> None:
    draw.rounded_rectangle(
        scale_box(box), radius=radius * SUPERSAMPLE, fill=color(fill),
        outline=color(outline) if outline else None, width=width * SUPERSAMPLE,
    )


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], main: str, dark: str) -> None:
    x0, y0, x1, y1 = box
    rounded(draw, (x0 + 1, y0 + 2, x1 + 1, y1 + 2), 3, PALETTE["shell"], None)
    rounded(draw, box, 3, dark, PALETTE["outline"], 1)
    rounded(draw, (x0 + 2, y0 + 2, x1 - 2, y1 - 2), 2, main, PALETTE["cream"], 1)

    # Quiet diagonal texture keeps large cards from looking like flat stained glass.
    span = y1 - y0
    for offset in range(x0 - span, x1 + 1, 10):
        start = max(0, x0 - offset)
        end = min(span, x1 - offset)
        if start > end:
            continue
        draw.line(
            [((offset + start) * SUPERSAMPLE, (y0 + start) * SUPERSAMPLE),
             ((offset + end) * SUPERSAMPLE, (y0 + end) * SUPERSAMPLE)],
            fill=color(PALETTE["cream"], 20), width=SUPERSAMPLE,
        )


def label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, dark: str) -> None:
    x, y = xy
    f = font("_mont800.ttf", 6)
    # One-pixel dark extrusion gives the same chunky shelf-label feel as the reference.
    draw.text((x * SUPERSAMPLE, (y + 1) * SUPERSAMPLE), text, font=f, fill=color(dark, 210))
    draw.text((x * SUPERSAMPLE, y * SUPERSAMPLE), text, font=f, fill=color(PALETTE["cream"]))


def slot_plaque(draw: ImageDraw.ImageDraw, slot: int, dark: str) -> None:
    col, row = slot % 9, slot // 9
    x, y = 7 + 18 * col, 17 + 18 * row
    rounded(draw, (x + 1, y + 2, x + 18, y + 19), 2, PALETTE["shell"], None)
    rounded(draw, (x, y, x + 17, y + 17), 2, dark, PALETTE["cream"], 1)
    draw.line(
        [(x + 3) * SUPERSAMPLE, (y + 3) * SUPERSAMPLE,
         (x + 14) * SUPERSAMPLE, (y + 3) * SUPERSAMPLE],
        fill=color(PALETTE["cream"], 105), width=SUPERSAMPLE,
    )


def draw_background() -> Image.Image:
    canvas = Image.new(
        "RGBA", (WIDTH * SUPERSAMPLE, HEIGHT * SUPERSAMPLE), color(PALETTE["shell"])
    )
    draw = ImageDraw.Draw(canvas, "RGBA")

    # Outer shell and a raised marketplace title plate.
    rounded(draw, (0, 0, WIDTH - 1, HEIGHT - 1), 5, PALETTE["shell"], PALETTE["outline"], 1)
    rounded(draw, (3, 3, WIDTH - 4, HEIGHT - 2), 4, PALETTE["shell_inner"], PALETTE["cream"], 1)
    rounded(draw, (9, 2, 167, 18), 2, PALETTE["header_shadow"], PALETTE["ink"], 1)
    rounded(draw, (11, 1, 165, 16), 2, PALETTE["header"], PALETTE["cream"], 1)
    draw.line(
        [(14 * SUPERSAMPLE, 3 * SUPERSAMPLE), (162 * SUPERSAMPLE, 3 * SUPERSAMPLE)],
        fill=color("#ffffff", 135), width=SUPERSAMPLE,
    )
    title = "КАК ЗАРАБОТАТЬ"
    title_font = font("_mont800.ttf", 7)
    title_box = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_box[2] - title_box[0]
    title_x = ((150 * SUPERSAMPLE) - title_width) // 2
    draw.text(
        (title_x + SUPERSAMPLE, 5 * SUPERSAMPLE), title, font=title_font,
        fill=color(PALETTE["header_shadow"]),
    )
    draw.text(
        (title_x, 4 * SUPERSAMPLE), title, font=title_font,
        fill=color(PALETTE["ink"]),
    )

    # Original NationRise composition inspired by the reference, not copied from it.
    panel(draw, (5, 20, 98, 106), PALETTE["cyan"], PALETTE["cyan_dark"])
    panel(draw, (5, 108, 98, 123), PALETTE["blue"], PALETTE["blue_dark"])
    panel(draw, (100, 20, 171, 56), PALETTE["lime"], PALETTE["lime_dark"])
    panel(draw, (100, 58, 171, 94), PALETTE["violet"], PALETTE["violet_dark"])
    panel(draw, (100, 96, 171, 123), PALETTE["amber"], PALETTE["amber_dark"])

    label(draw, (9, 22), "РАБОТЫ", PALETTE["cyan_dark"])
    label(draw, (7, 110), "ЕЩЁ", PALETTE["blue_dark"])
    label(draw, (104, 22), "ПРОДАЖА", PALETTE["lime_dark"])
    label(draw, (104, 60), "ТОРГОВЛЯ", PALETTE["violet_dark"])
    label(draw, (104, 98), "НАГРАДЫ", PALETTE["amber_dark"])

    # Actual Bukkit items are rendered on top; plaques visually join them into cards.
    for slot in (10, 12, 21, 28, 30, 40):
        slot_plaque(draw, slot, PALETTE["cyan_dark"])
    for slot in (46, 47, 48, 49):
        slot_plaque(draw, slot, PALETTE["blue_dark"])
    for slot in (15, 16):
        slot_plaque(draw, slot, PALETTE["lime_dark"])
    for slot in (33, 34):
        slot_plaque(draw, slot, PALETTE["violet_dark"])
    for slot in (50, 51, 52, 53):
        slot_plaque(draw, slot, PALETTE["amber_dark"])

    # Small brand crown in the title plate; the normal inventory title stays readable.
    crown = [
        (153, 11), (153, 6), (156, 9), (159, 5), (162, 9), (165, 6), (165, 11),
    ]
    draw.polygon([(x * SUPERSAMPLE, y * SUPERSAMPLE) for x, y in crown], fill=color(PALETTE["violet"]))
    draw.rectangle(scale_box((153, 11, 165, 13)), fill=color(PALETTE["violet_dark"]))

    return canvas.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def font_definition() -> dict:
    advances: dict[str, int] = {}
    for index, magnitude in enumerate((1, 2, 4, 8, 16, 32, 64, 128, 256)):
        advances[chr(0xF800 + index)] = -magnitude
        advances[chr(0xF810 + index)] = magnitude
    return {
        "providers": [
            {"type": "space", "advances": advances},
            {
                "type": "bitmap",
                "file": "nationrise:font/earn_bg.png",
                "ascent": 13,
                "height": HEIGHT,
                "chars": [GLYPH],
            },
        ]
    }


def main() -> None:
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    image = draw_background()
    image.save(TEXTURE)
    FONT_JSON.write_text(
        json.dumps(font_definition(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    image.resize((WIDTH * 4, HEIGHT * 4), Image.Resampling.NEAREST).save(PREVIEW)
    print(f"earn GUI: {TEXTURE} ({WIDTH}x{HEIGHT})")
    print(f"earn font: {FONT_JSON} (glyph U+{ord(GLYPH):04X})")
    print(f"preview: {PREVIEW}")


if __name__ == "__main__":
    main()
