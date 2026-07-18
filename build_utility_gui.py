# -*- coding: utf-8 -*-
"""Generate isolated branded backgrounds for auction and utility menus.

Only titles rendered with ``nationrise:utility_gui`` can display these
backgrounds. Vanilla, lite-pack and Bedrock clients therefore keep the
server-provided fallback inventory without global texture replacement.
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


FONT_JSON = FONT_DIR / "utility_gui.json"
PREVIEW = FONT_DIR.parents[3] / "logo" / "_utility_gui_preview.png"
GLYPHS = {
    "\uf8e1": ("auction_market_bg.png", 125),
    "\uf8e2": ("auction_storage_bg.png", 125),
    "\uf8e3": ("auction_categories_bg.png", 107),
    "\uf8e4": ("donate_bg.png", 125),
    "\uf8e5": ("events_bg.png", 71),
    "\uf8e6": ("casino_bg.png", 125),
    "\uf8e7": ("jobs_bg.png", 71),
    "\uf8e8": ("job_targets_bg.png", 125),
    "\uf8e9": ("town_storage_bg.png", 125),
}


def lots_background(heading: str, storage: bool = False) -> Image.Image:
    image, draw = base(125, heading)
    colors = (
        ("blue", "blue_dark"),
        ("cyan", "cyan_dark"),
    ) if storage else (
        ("violet", "violet_dark"),
        ("amber", "amber_dark"),
        ("cyan", "cyan_dark"),
    )
    for slot in range(45):
        plaque(draw, slot, *colors[(slot // 9 + slot) % len(colors)])
    controls = {
        45: ("red", "red_dark") if storage else ("lime", "lime_dark"),
        46: ("violet", "violet_dark"),
        47: ("blue", "blue_dark"),
        48: ("slate", "slate_dark"),
        49: ("amber", "amber_dark"),
        50: ("slate", "slate_dark"),
        51: ("blue", "blue_dark"),
        52: ("cyan", "cyan_dark"),
        53: ("violet", "violet_dark"),
    }
    for slot, colorset in controls.items():
        plaque(draw, slot, *colorset)
    return image.resize((WIDTH, 125), Image.Resampling.LANCZOS)


def auction_categories() -> Image.Image:
    image, draw = base(107, "АУКЦИОН: КАТЕГОРИИ")
    for index, slot in enumerate((12, 14, 21, 23, 30, 32, 39, 41)):
        plaque(draw, slot, *CATEGORY_COLORS[index % len(CATEGORY_COLORS)])
    plaque(draw, 40, "red", "red_dark")
    return image.resize((WIDTH, 107), Image.Resampling.LANCZOS)


def donate() -> Image.Image:
    image, draw = base(125, "ПРИВИЛЕГИИ NATIONRISE")
    band(draw, (22, 33, 154, 72), "violet", "violet_dark")
    plaque(draw, 4, "violet", "violet_dark")
    for index, slot in enumerate((19, 20, 21, 22, 23, 24)):
        plaque(draw, slot, *CATEGORY_COLORS[index % len(CATEGORY_COLORS)])
    for slot in (9, 18, 27, 36, 17, 26, 35, 44):
        plaque(draw, slot, "cyan", "cyan_dark")
    plaque(draw, 49, "amber", "amber_dark")
    return image.resize((WIDTH, 125), Image.Resampling.LANCZOS)


def events() -> Image.Image:
    image, draw = base(71, "РАСПИСАНИЕ ИВЕНТОВ")
    plaque(draw, 4, "violet", "violet_dark")
    for index, slot in enumerate((10, 11, 12, 13, 14, 15, 16, 22)):
        plaque(draw, slot, *CATEGORY_COLORS[index % len(CATEGORY_COLORS)])
    plaque(draw, 24, "lime", "lime_dark")
    plaque(draw, 26, "red", "red_dark")
    return image.resize((WIDTH, 71), Image.Resampling.LANCZOS)


def casino() -> Image.Image:
    image, draw = base(125, "КАЗИНО NATIONRISE")
    band(draw, (22, 34, 154, 71), "amber", "amber_dark")
    plaque(draw, 4, "violet", "violet_dark")
    for slot in range(19, 26):
        plaque(draw, slot, "amber", "amber_dark")
    plaque(draw, 13, "lime", "lime_dark")
    plaque(draw, 31, "lime", "lime_dark")
    for slot in (38, 39):
        plaque(draw, slot, "red", "red_dark")
    plaque(draw, 40, "amber", "amber_dark")
    for slot in (41, 42):
        plaque(draw, slot, "lime", "lime_dark")
    plaque(draw, 45, "slate", "slate_dark")
    plaque(draw, 49, "violet", "violet_dark")
    plaque(draw, 53, "red", "red_dark")
    return image.resize((WIDTH, 125), Image.Resampling.LANCZOS)


def jobs() -> Image.Image:
    image, draw = base(71, "РАБОТЫ: ПРОФЕССИИ")
    for index, slot in enumerate((10, 11, 12, 13)):
        plaque(draw, slot, *CATEGORY_COLORS[index % len(CATEGORY_COLORS)])
    plaque(draw, 22, "red", "red_dark")
    return image.resize((WIDTH, 71), Image.Resampling.LANCZOS)


def job_targets() -> Image.Image:
    image, draw = base(125, "РАБОТЫ: ВЫБОР ЦЕЛИ")
    for slot in range(45):
        fill, dark = (
            ("blue", "blue_dark"),
            ("lime", "lime_dark"),
            ("amber", "amber_dark"),
        )[slot % 3]
        plaque(draw, slot, fill, dark)
    plaque(draw, 49, "slate", "slate_dark")
    return image.resize((WIDTH, 125), Image.Resampling.LANCZOS)


def town_storage() -> Image.Image:
    image, draw = base(125, "СКЛАД ГОРОДА")
    for slot in range(45):
        fill, dark = (
            ("slate", "slate_dark"),
            ("blue", "blue_dark"),
        )[(slot // 9 + slot) % 2]
        plaque(draw, slot, fill, dark)
    plaque(draw, 45, "blue", "blue_dark")
    plaque(draw, 49, "violet", "violet_dark")
    plaque(draw, 53, "blue", "blue_dark")
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
        lots_background("АУКЦИОН: ЖИВОЙ РЫНОК"),
        lots_background("АУКЦИОН: МОИ ЛОТЫ", storage=True),
        auction_categories(),
        donate(),
        events(),
        casino(),
        jobs(),
        job_targets(),
        town_storage(),
    )
    for image, (_, (filename, expected_height)) in zip(generated, GLYPHS.items()):
        expected = (WIDTH, expected_height)
        if image.size != expected:
            raise ValueError(f"{filename}: expected {expected}, got {image.size}")
        image.save(TEXTURE_DIR / filename)

    FONT_JSON.write_text(
        json.dumps(font_definition(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    scale = 3
    padding = 12
    preview_height = sum(i.height * scale for i in generated) + padding * (len(generated) + 1)
    preview = Image.new(
        "RGBA", (WIDTH * scale + padding * 2, preview_height), rgba(PALETTE["shell"])
    )
    y = padding
    for image in generated:
        enlarged = image.resize(
            (image.width * scale, image.height * scale), Image.Resampling.NEAREST
        )
        preview.alpha_composite(enlarged, (padding, y))
        y += enlarged.height + padding
    preview.save(PREVIEW)

    print(f"utility GUI font: {FONT_JSON}")
    for glyph, (filename, height) in GLYPHS.items():
        print(f"  U+{ord(glyph):04X}: {filename} ({WIDTH}x{height})")
    print(f"preview: {PREVIEW}")


if __name__ == "__main__":
    main()
