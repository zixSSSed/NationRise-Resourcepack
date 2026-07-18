# -*- coding: utf-8 -*-
"""Generate isolated branded backgrounds for /t and /t builds.

The backgrounds are title-font glyphs, not a replacement for generic_54.png.
Only server-owned menus that deliberately use nationrise:town_gui can show them;
vanilla, lite-pack and Bedrock users keep the normal inventory.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
PACK = ROOT / "pack"
TEXTURE_DIR = PACK / "assets" / "nationrise" / "textures" / "font"
FONT_DIR = PACK / "assets" / "nationrise" / "font"
PREVIEW = ROOT / "logo" / "_town_gui_preview.png"
FONT_JSON = FONT_DIR / "town_gui.json"

WIDTH = 176
SUPERSAMPLE = 4
GLYPHS = {
    "\uf8c1": ("town_main_bg.png", 107),
    "\uf8c2": ("town_builds_bg.png", 89),
    "\uf8c3": ("town_build_category_bg.png", 89),
}

PALETTE = {
    "shell": "#17121f",
    "inner": "#282132",
    "outline": "#c9b8f2",
    "cream": "#f7fadb",
    "ink": "#241e2b",
    "header": "#dedce3",
    "header_shadow": "#777383",
    "violet": "#985be0",
    "violet_dark": "#54317d",
    "cyan": "#35c8d8",
    "cyan_dark": "#1d7788",
    "lime": "#7ed84b",
    "lime_dark": "#467b2a",
    "amber": "#f1a928",
    "amber_dark": "#915e11",
    "red": "#db5a6b",
    "red_dark": "#7f2d3a",
    "blue": "#478ec6",
    "blue_dark": "#265273",
    "slate": "#736b80",
    "slate_dark": "#3c3746",
}

CATEGORY_COLORS = (
    ("violet", "violet_dark"),
    ("amber", "amber_dark"),
    ("red", "red_dark"),
    ("cyan", "cyan_dark"),
    ("blue", "blue_dark"),
    ("lime", "lime_dark"),
    ("slate", "slate_dark"),
)


def rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.removeprefix("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def scale_box(box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = box
    return (
        x0 * SUPERSAMPLE,
        y0 * SUPERSAMPLE,
        (x1 + 1) * SUPERSAMPLE - 1,
        (y1 + 1) * SUPERSAMPLE - 1,
    )


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(ROOT / "_mont800.ttf"), size * SUPERSAMPLE)


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int,
            fill: str, outline: str | None = None, width: int = 1) -> None:
    draw.rounded_rectangle(
        scale_box(box),
        radius=radius * SUPERSAMPLE,
        fill=rgba(PALETTE[fill]),
        outline=rgba(PALETTE[outline]) if outline else None,
        width=width * SUPERSAMPLE,
    )


def base(height: int, heading: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new(
        "RGBA", (WIDTH * SUPERSAMPLE, height * SUPERSAMPLE), rgba(PALETTE["shell"])
    )
    draw = ImageDraw.Draw(image, "RGBA")
    rounded(draw, (0, 0, WIDTH - 1, height - 1), 5, "shell", "outline")
    rounded(draw, (3, 3, WIDTH - 4, height - 2), 4, "inner", "cream")

    rounded(draw, (9, 2, 167, 18), 2, "header_shadow", "ink")
    rounded(draw, (11, 1, 165, 16), 2, "header", "cream")
    draw.line(
        [(14 * SUPERSAMPLE, 3 * SUPERSAMPLE), (162 * SUPERSAMPLE, 3 * SUPERSAMPLE)],
        fill=rgba("#ffffff", 135),
        width=SUPERSAMPLE,
    )
    heading_font = font(7)
    bounds = draw.textbbox((0, 0), heading, font=heading_font)
    text_width = bounds[2] - bounds[0]
    x = (WIDTH * SUPERSAMPLE - text_width) // 2
    draw.text(
        (x + SUPERSAMPLE, 5 * SUPERSAMPLE),
        heading,
        font=heading_font,
        fill=rgba(PALETTE["header_shadow"]),
    )
    draw.text(
        (x, 4 * SUPERSAMPLE),
        heading,
        font=heading_font,
        fill=rgba(PALETTE["ink"]),
    )
    return image, draw


def band(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int],
         fill: str, dark: str) -> None:
    x0, y0, x1, y1 = box
    rounded(draw, (x0 + 1, y0 + 2, x1 + 1, y1 + 2), 3, "shell")
    rounded(draw, box, 3, dark, "outline")
    rounded(draw, (x0 + 2, y0 + 2, x1 - 2, y1 - 2), 2, fill, "cream")
    draw.line(
        [
            ((x0 + 5) * SUPERSAMPLE, (y0 + 4) * SUPERSAMPLE),
            ((x1 - 5) * SUPERSAMPLE, (y0 + 4) * SUPERSAMPLE),
        ],
        fill=rgba(PALETTE["cream"], 80),
        width=SUPERSAMPLE,
    )


def plaque(draw: ImageDraw.ImageDraw, slot: int, fill: str, dark: str) -> None:
    col, row = slot % 9, slot // 9
    x, y = 7 + 18 * col, 17 + 18 * row
    rounded(draw, (x + 1, y + 2, x + 18, y + 19), 2, "shell")
    rounded(draw, (x, y, x + 17, y + 17), 2, dark, "cream")
    rounded(draw, (x + 2, y + 2, x + 15, y + 14), 2, fill)
    draw.line(
        [
            ((x + 4) * SUPERSAMPLE, (y + 3) * SUPERSAMPLE),
            ((x + 13) * SUPERSAMPLE, (y + 3) * SUPERSAMPLE),
        ],
        fill=rgba(PALETTE["cream"], 100),
        width=SUPERSAMPLE,
    )


def main_background() -> Image.Image:
    image, draw = base(107, "УПРАВЛЕНИЕ ГОРОДОМ")
    band(draw, (23, 34, 153, 53), "cyan", "cyan_dark")
    band(draw, (41, 52, 153, 71), "violet", "violet_dark")

    plaque(draw, 4, "amber", "amber_dark")
    for slot in range(10, 17):
        plaque(draw, slot, "cyan", "cyan_dark")
    for slot in range(20, 26):
        plaque(draw, slot, "violet", "violet_dark")
    plaque(draw, 40, "slate", "slate_dark")
    return image.resize((WIDTH, 107), Image.Resampling.LANCZOS)


def buildings_background() -> Image.Image:
    image, draw = base(89, "ЗДАНИЯ: НАПРАВЛЕНИЯ")
    band(draw, (23, 34, 153, 53), "blue", "blue_dark")
    plaque(draw, 4, "amber", "amber_dark")
    for index, slot in enumerate(range(10, 17)):
        fill, dark = CATEGORY_COLORS[index]
        plaque(draw, slot, fill, dark)
    plaque(draw, 31, "slate", "slate_dark")

    hint_font = font(5)
    hint = "ВЫБЕРИТЕ НАПРАВЛЕНИЕ РАЗВИТИЯ"
    bounds = draw.textbbox((0, 0), hint, font=hint_font)
    x = (WIDTH * SUPERSAMPLE - (bounds[2] - bounds[0])) // 2
    draw.text(
        (x, 57 * SUPERSAMPLE),
        hint,
        font=hint_font,
        fill=rgba(PALETTE["cream"], 190),
    )
    return image.resize((WIDTH, 89), Image.Resampling.LANCZOS)


def building_category_background() -> Image.Image:
    image, draw = base(89, "РАЗВИТИЕ ЗДАНИЙ")
    band(draw, (23, 34, 153, 71), "violet", "violet_dark")
    plaque(draw, 4, "amber", "amber_dark")
    for index, slot in enumerate((*range(10, 17), *range(19, 26))):
        fill, dark = CATEGORY_COLORS[index % len(CATEGORY_COLORS)]
        plaque(draw, slot, fill, dark)
    plaque(draw, 31, "slate", "slate_dark")
    return image.resize((WIDTH, 89), Image.Resampling.LANCZOS)


def font_definition() -> dict:
    advances: dict[str, int] = {}
    for index, magnitude in enumerate((1, 2, 4, 8, 16, 32, 64, 128, 256)):
        advances[chr(0xF800 + index)] = -magnitude
        advances[chr(0xF810 + index)] = magnitude

    providers: list[dict] = [{"type": "space", "advances": advances}]
    for glyph, (filename, height) in GLYPHS.items():
        providers.append(
            {
                "type": "bitmap",
                "file": f"nationrise:font/{filename}",
                "ascent": 13,
                "height": height,
                "chars": [glyph],
            }
        )
    return {"providers": providers}


def main() -> None:
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    generated = (
        main_background(),
        buildings_background(),
        building_category_background(),
    )
    for image, (_, (filename, expected_height)) in zip(generated, GLYPHS.items()):
        if image.size != (WIDTH, expected_height):
            raise ValueError(f"{filename}: expected {WIDTH}x{expected_height}, got {image.size}")
        image.save(TEXTURE_DIR / filename)

    FONT_JSON.write_text(
        json.dumps(font_definition(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    scale = 4
    padding = 12
    preview_height = sum(image.height * scale for image in generated) + padding * (len(generated) + 1)
    preview = Image.new("RGBA", (WIDTH * scale + padding * 2, preview_height), rgba(PALETTE["shell"]))
    y = padding
    for image in generated:
        enlarged = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
        preview.alpha_composite(enlarged, (padding, y))
        y += enlarged.height + padding
    preview.save(PREVIEW)

    print(f"town GUI font: {FONT_JSON}")
    for glyph, (filename, height) in GLYPHS.items():
        print(f"  U+{ord(glyph):04X}: {filename} ({WIDTH}x{height})")
    print(f"preview: {PREVIEW}")


if __name__ == "__main__":
    main()
