# -*- coding: utf-8 -*-
"""Generate isolated branded backgrounds for /shop and /buyer.

The script reuses the deterministic NationRise GUI primitives from
build_town_gui.py, but writes a separate nationrise:market_gui font. It never
replaces vanilla/default GUI textures, so lite/off/Bedrock clients keep the
server-side fallback inventories.
"""
from __future__ import annotations

import json

from PIL import Image

from build_town_gui import (
    CATEGORY_COLORS,
    FONT_DIR,
    PALETTE,
    TEXTURE_DIR,
    WIDTH,
    band,
    base,
    plaque,
    rgba,
)


FONT_JSON = FONT_DIR / "market_gui.json"
PREVIEW = FONT_DIR.parents[3] / "logo" / "_market_gui_preview.png"
GLYPHS = {
    "\uf8d1": ("shop_root_bg.png", 71),
    "\uf8d2": ("shop_money_bg.png", 71),
    "\uf8d3": ("shop_donate_bg.png", 71),
    "\uf8d4": ("shop_listing_bg.png", 125),
    "\uf8d5": ("buyer_categories_bg.png", 71),
    "\uf8d6": ("buyer_listing_bg.png", 125),
}
INNER = (
    *range(10, 17),
    *range(19, 26),
    *range(28, 35),
    *range(37, 44),
)


def shop_root() -> Image.Image:
    image, draw = base(71, "MARKETPLACE")
    plaque(draw, 11, "amber", "amber_dark")
    plaque(draw, 15, "cyan", "cyan_dark")
    plaque(draw, 22, "slate", "slate_dark")
    return image.resize((WIDTH, 71), Image.Resampling.LANCZOS)


def shop_money() -> Image.Image:
    image, draw = base(71, "МАГАЗИН ЗА МОНЕТЫ")
    plaque(draw, 4, "amber", "amber_dark")
    for index, slot in enumerate((10, 12, 14, 16)):
        fill, dark = CATEGORY_COLORS[index]
        plaque(draw, slot, fill, dark)
    plaque(draw, 22, "violet", "violet_dark")
    plaque(draw, 18, "slate", "slate_dark")
    return image.resize((WIDTH, 71), Image.Resampling.LANCZOS)


def shop_donate() -> Image.Image:
    image, draw = base(71, "МАГАЗИН ЗА КРИСТАЛЛЫ")
    plaque(draw, 4, "cyan", "cyan_dark")
    plaque(draw, 10, "violet", "violet_dark")
    plaque(draw, 13, "lime", "lime_dark")
    plaque(draw, 16, "red", "red_dark")
    plaque(draw, 22, "slate", "slate_dark")
    return image.resize((WIDTH, 71), Image.Resampling.LANCZOS)


def shop_listing() -> Image.Image:
    image, draw = base(125, "МАГАЗИН: ТОВАРЫ")
    band(draw, (23, 34, 153, 107), "violet", "violet_dark")
    plaque(draw, 4, "amber", "amber_dark")
    for index, slot in enumerate(INNER):
        fill, dark = CATEGORY_COLORS[index % len(CATEGORY_COLORS)]
        plaque(draw, slot, fill, dark)
    plaque(draw, 45, "blue", "blue_dark")
    plaque(draw, 49, "slate", "slate_dark")
    plaque(draw, 53, "blue", "blue_dark")
    return image.resize((WIDTH, 125), Image.Resampling.LANCZOS)


def buyer_categories() -> Image.Image:
    image, draw = base(71, "СКУПЩИК: КАТЕГОРИИ")
    plaque(draw, 4, "lime", "lime_dark")
    for index, slot in enumerate((10, 12, 14, 16)):
        fill, dark = CATEGORY_COLORS[(index + 1) % len(CATEGORY_COLORS)]
        plaque(draw, slot, fill, dark)
    plaque(draw, 13, "amber", "amber_dark")
    plaque(draw, 22, "slate", "slate_dark")
    return image.resize((WIDTH, 71), Image.Resampling.LANCZOS)


def buyer_listing() -> Image.Image:
    image, draw = base(125, "СКУПЩИК: ПРОДАЖА")
    band(draw, (23, 34, 153, 107), "lime", "lime_dark")
    plaque(draw, 4, "lime", "lime_dark")
    for index, slot in enumerate(INNER):
        fill, dark = (("lime", "lime_dark"), ("cyan", "cyan_dark"))[index % 2]
        plaque(draw, slot, fill, dark)
    plaque(draw, 48, "blue", "blue_dark")
    plaque(draw, 50, "slate", "slate_dark")
    return image.resize((WIDTH, 125), Image.Resampling.LANCZOS)


def font_definition() -> dict:
    advances: dict[str, int] = {}
    for index, magnitude in enumerate((1, 2, 4, 8, 16, 32, 64, 128, 256)):
        advances[chr(0xF800 + index)] = -magnitude
        advances[chr(0xF810 + index)] = magnitude

    providers: list[dict] = [{"type": "space", "advances": advances}]
    for glyph, (filename, height) in GLYPHS.items():
        providers.append({
            "type": "bitmap",
            "file": f"nationrise:font/{filename}",
            "ascent": 13,
            "height": height,
            "chars": [glyph],
        })
    return {"providers": providers}


def main() -> None:
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    generated = (
        shop_root(),
        shop_money(),
        shop_donate(),
        shop_listing(),
        buyer_categories(),
        buyer_listing(),
    )
    for image, (_, (filename, expected_height)) in zip(generated, GLYPHS.items()):
        if image.size != (WIDTH, expected_height):
            raise ValueError(
                f"{filename}: expected {WIDTH}x{expected_height}, got {image.size}"
            )
        image.save(TEXTURE_DIR / filename)

    FONT_JSON.write_text(
        json.dumps(font_definition(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    scale = 3
    padding = 12
    preview_height = (
        sum(image.height * scale for image in generated)
        + padding * (len(generated) + 1)
    )
    preview = Image.new(
        "RGBA",
        (WIDTH * scale + padding * 2, preview_height),
        rgba(PALETTE["shell"]),
    )
    y = padding
    for image in generated:
        enlarged = image.resize(
            (image.width * scale, image.height * scale),
            Image.Resampling.NEAREST,
        )
        preview.alpha_composite(enlarged, (padding, y))
        y += enlarged.height + padding
    preview.save(PREVIEW)

    print(f"market GUI font: {FONT_JSON}")
    for glyph, (filename, height) in GLYPHS.items():
        print(f"  U+{ord(glyph):04X}: {filename} ({WIDTH}x{height})")
    print(f"preview: {PREVIEW}")


if __name__ == "__main__":
    main()
