# -*- coding: utf-8 -*-
"""Generate isolated branded backgrounds for /shop and /buyer.

The script reuses the deterministic NationRise GUI primitives from
build_town_gui.py, but writes a separate nationrise:market_gui font. It never
replaces vanilla/default GUI textures, so lite/off/Bedrock clients keep the
server-side fallback inventories.
"""
from __future__ import annotations

import json

from PIL import Image, ImageDraw

from build_town_gui import (
    CATEGORY_COLORS,
    FONT_DIR,
    PALETTE,
    TEXTURE_DIR,
    WIDTH,
    band,
    base,
    clear_text,
    plaque,
    rgba,
)


FONT_JSON = FONT_DIR / "market_gui.json"
PREVIEW = FONT_DIR.parents[3] / "logo" / "_market_gui_preview.png"
SHOP_PREVIEW = FONT_DIR.parents[3] / "logo" / "_shop_root_preview.png"
SHOP_OVERLAY_PREVIEW = FONT_DIR.parents[3] / "logo" / "_shop_root_overlay_preview.png"
ITEM_TEXTURE_DIR = FONT_DIR.parents[3] / "pack" / "assets" / "minecraft" / "textures" / "item"
GLYPHS = {
    "\uf8d1": ("shop_root_bg.png", 89),
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


def _text(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], value: str,
          size: int, color: str, y: int) -> None:
    from build_town_gui import SUPERSAMPLE, font

    x0, _, x1, _ = box
    face = font(size)
    bounds = draw.textbbox((0, 0), value, font=face)
    width = bounds[2] - bounds[0]
    x = ((x0 + x1 + 1) * SUPERSAMPLE - width) // 2
    clear_text(
        draw,
        (x, y * SUPERSAMPLE),
        value,
        face,
        fill=color,
        outline="ink",
        stroke=1,
    )


def _pixel_coin_art(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    from build_town_gui import SUPERSAMPLE, scale_box

    x0, y0, x1, y1 = box
    for dx, dy in ((4, 24), (9, 27), (42, 25)):
        draw.ellipse(
            scale_box((x0 + dx, y0 + dy, x0 + dx + 7, y0 + dy + 5)),
            fill=rgba(PALETTE["amber"]),
            outline=rgba(PALETTE["cream"]),
            width=SUPERSAMPLE,
        )
    draw.rectangle(
        scale_box((x0 + 4, y0 + 11, x0 + 12, y0 + 24)),
        fill=rgba(PALETTE["amber_dark"]),
        outline=rgba(PALETTE["amber"]),
        width=SUPERSAMPLE,
    )
    draw.line(
        [(x0 + 6) * SUPERSAMPLE, (y0 + 14) * SUPERSAMPLE,
         (x0 + 10) * SUPERSAMPLE, (y0 + 14) * SUPERSAMPLE],
        fill=rgba(PALETTE["cream"]),
        width=SUPERSAMPLE,
    )


def _pixel_crystal_art(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    from build_town_gui import SUPERSAMPLE

    x0, y0, x1, y1 = box
    crystals = (
        ((x0 + 4, y0 + 29), (x0 + 8, y0 + 15), (x0 + 12, y0 + 29)),
        ((x1 - 12, y0 + 29), (x1 - 8, y0 + 18), (x1 - 4, y0 + 29)),
    )
    for points in crystals:
        draw.polygon(
            [(x * SUPERSAMPLE, y * SUPERSAMPLE) for x, y in points],
            fill=rgba(PALETTE["cyan"]),
            outline=rgba(PALETTE["cream"]),
        )
    draw.line(
        [(x0 + 8) * SUPERSAMPLE, (y0 + 17) * SUPERSAMPLE,
         (x0 + 8) * SUPERSAMPLE, (y0 + 27) * SUPERSAMPLE],
        fill=rgba(PALETTE["cream"]),
        width=SUPERSAMPLE,
    )


def _pixel_war_art(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    from build_town_gui import SUPERSAMPLE, scale_box

    x0, y0, x1, y1 = box
    for x in (x0 + 4, x1 - 11):
        draw.rectangle(
            scale_box((x, y0 + 18, x + 7, y0 + 30)),
            fill=rgba(PALETTE["slate_dark"]),
            outline=rgba(PALETTE["red"]),
            width=SUPERSAMPLE,
        )
        draw.rectangle(
            scale_box((x - 1, y0 + 15, x + 8, y0 + 19)),
            fill=rgba(PALETTE["slate"]),
        )
    draw.line(
        [(x0 + 7) * SUPERSAMPLE, (y0 + 28) * SUPERSAMPLE,
         (x0 + 15) * SUPERSAMPLE, (y0 + 20) * SUPERSAMPLE],
        fill=rgba(PALETTE["cream"]),
        width=2 * SUPERSAMPLE,
    )
    draw.line(
        [(x1 - 7) * SUPERSAMPLE, (y0 + 28) * SUPERSAMPLE,
         (x1 - 15) * SUPERSAMPLE, (y0 + 20) * SUPERSAMPLE],
        fill=rgba(PALETTE["cream"]),
        width=2 * SUPERSAMPLE,
    )


def _shop_plate(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int],
                fill: str, dark: str, title: str, subtitle: str, art) -> None:
    from build_town_gui import rounded

    x0, y0, x1, y1 = box
    rounded(draw, (x0 + 1, y0 + 2, x1 + 1, y1 + 2), 3, "shell")
    rounded(draw, box, 3, dark, "outline")
    rounded(draw, (x0 + 2, y0 + 2, x1 - 2, y1 - 2), 2, "inner")
    rounded(draw, (x0 + 3, y0 + 3, x1 - 3, y0 + 13), 2, fill)
    _text(draw, box, title, 5, "cream", y0 + 4)
    art(draw, box)
    _text(draw, box, subtitle, 4, "cream", y1 - 9)


def shop_root() -> Image.Image:
    image, draw = base(89, "МАГАЗИН NATIONRISE")
    _shop_plate(draw, (5, 20, 57, 68), "amber", "amber_dark",
                "МОНЕТЫ", "РЕСУРСЫ", _pixel_coin_art)
    _shop_plate(draw, (62, 20, 114, 68), "blue", "blue_dark",
                "КРИСТАЛЛЫ", "РЕДКОЕ", _pixel_crystal_art)
    _shop_plate(draw, (119, 20, 171, 68), "red", "red_dark",
                "ВОЕННОЕ", "ВОЙНА", _pixel_war_art)
    plaque(draw, 31, "slate", "slate_dark")
    return image.resize((WIDTH, 89), Image.Resampling.LANCZOS)


def shop_money() -> Image.Image:
    image, draw = base(71, "МАГАЗИН · ЗА МОНЕТЫ")
    plaque(draw, 4, "amber", "amber_dark")
    for index, slot in enumerate((10, 12, 14, 16)):
        fill, dark = (
            ("blue", "blue_dark"),
            ("amber", "amber_dark"),
            ("blue", "blue_dark"),
            ("lime", "lime_dark"),
        )[index]
        plaque(draw, slot, fill, dark)
    plaque(draw, 22, "slate", "slate_dark")
    plaque(draw, 18, "slate", "slate_dark")
    return image.resize((WIDTH, 71), Image.Resampling.LANCZOS)


def shop_donate() -> Image.Image:
    image, draw = base(71, "ВОЕННЫЙ РЫНОК")
    plaque(draw, 4, "blue", "blue_dark")
    band(draw, (23, 33, 78, 54), "lime", "lime_dark")
    band(draw, (97, 33, 152, 54), "red", "red_dark")
    plaque(draw, 11, "lime", "lime_dark")
    plaque(draw, 15, "red", "red_dark")
    plaque(draw, 22, "slate", "slate_dark")
    return image.resize((WIDTH, 71), Image.Resampling.LANCZOS)


def _market_slot_well(draw: ImageDraw.ImageDraw, slot: int, accent: str) -> None:
    from build_town_gui import rounded

    col, row = slot % 9, slot // 9
    x, y = 7 + 18 * col, 17 + 18 * row
    rounded(draw, (x + 1, y + 2, x + 18, y + 19), 2, "shell")
    rounded(draw, (x, y, x + 17, y + 17), 2, "slate_dark", accent)
    rounded(draw, (x + 2, y + 2, x + 15, y + 14), 1, "inner")


def shop_listing() -> Image.Image:
    image, draw = base(125, "МАГАЗИН: ТОВАРЫ")
    plaque(draw, 4, "amber", "amber_dark")
    for slot in INNER:
        _market_slot_well(draw, slot, "amber")
    plaque(draw, 45, "amber", "amber_dark")
    plaque(draw, 49, "slate", "slate_dark")
    plaque(draw, 53, "amber", "amber_dark")
    return image.resize((WIDTH, 125), Image.Resampling.LANCZOS)


def buyer_categories() -> Image.Image:
    image, draw = base(71, "СКУПЩИК: КАТЕГОРИИ")
    plaque(draw, 4, "lime", "lime_dark")
    for slot in (10, 12, 14, 16):
        plaque(draw, slot, "blue", "blue_dark")
    plaque(draw, 13, "amber", "amber_dark")
    plaque(draw, 22, "slate", "slate_dark")
    return image.resize((WIDTH, 71), Image.Resampling.LANCZOS)


def buyer_listing() -> Image.Image:
    image, draw = base(125, "СКУПЩИК: ПРОДАЖА")
    plaque(draw, 4, "lime", "lime_dark")
    for slot in INNER:
        _market_slot_well(draw, slot, "lime")
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

    root = generated[0]
    root.resize(
        (root.width * 4, root.height * 4), Image.Resampling.NEAREST
    ).save(SHOP_PREVIEW)

    overlay = root.copy()
    # Exact Minecraft item render bounds (16x16 inside an 18x18 slot).
    for slot, filename in (
        (10, "nr_shop_money.png"),
        (13, "nr_shop_crystal.png"),
        (16, "nr_shop_war.png"),
    ):
        col, row = slot % 9, slot // 9
        x, y = 8 + col * 18, 18 + row * 18
        icon = Image.open(ITEM_TEXTURE_DIR / filename).convert("RGBA").resize(
            (16, 16), Image.Resampling.LANCZOS
        )
        overlay.alpha_composite(icon, (x, y))
    overlay.resize(
        (overlay.width * 4, overlay.height * 4), Image.Resampling.NEAREST
    ).save(SHOP_OVERLAY_PREVIEW)

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
    print(f"shop background preview: {SHOP_PREVIEW}")
    print(f"shop item-overlay preview: {SHOP_OVERLAY_PREVIEW}")


if __name__ == "__main__":
    main()
