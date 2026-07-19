# -*- coding: utf-8 -*-
"""Generate isolated branded backgrounds for auction and utility menus.

Only titles rendered with ``nationrise:utility_gui`` can display these
backgrounds. Vanilla, lite-pack and Bedrock clients therefore keep the
server-provided fallback inventory without global texture replacement.
"""
from __future__ import annotations

import json

from PIL import Image, ImageDraw

from build_town_gui import (
    CATEGORY_COLORS,
    FONT_DIR,
    PALETTE,
    SUPERSAMPLE,
    TEXTURE_DIR,
    WIDTH,
    band,
    base,
    clear_text,
    font,
    plaque,
    rgba,
    rounded,
)


FONT_JSON = FONT_DIR / "utility_gui.json"
PREVIEW = FONT_DIR.parents[3] / "logo" / "_utility_gui_preview.png"
RTP_PREVIEW = FONT_DIR.parents[3] / "logo" / "_rtp_map_preview.png"
RTP_OVERLAY_PREVIEW = FONT_DIR.parents[3] / "logo" / "_rtp_map_overlay_preview.png"
AUCTION_PREVIEW = FONT_DIR.parents[3] / "logo" / "_auction_market_preview.png"
AUCTION_OVERLAY_PREVIEW = FONT_DIR.parents[3] / "logo" / "_auction_market_overlay_preview.png"
AUCTION_CATEGORIES_PREVIEW = FONT_DIR.parents[3] / "logo" / "_auction_categories_preview.png"
AUCTION_CATEGORIES_OVERLAY_PREVIEW = FONT_DIR.parents[3] / "logo" / "_auction_categories_overlay_preview.png"
ITEM_TEXTURE_DIR = FONT_DIR.parents[3] / "pack" / "assets" / "minecraft" / "textures" / "item"
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
    "\uf8ea": ("rtp_bg.png", 125),
}

RTP_MARKERS = {
    10: "nr_rtp_namerica.png",
    29: "nr_rtp_samerica.png",
    13: "nr_rtp_europe.png",
    22: "nr_rtp_africa.png",
    15: "nr_rtp_asia.png",
    34: "nr_rtp_australia.png",
    49: "nr_rtp_random.png",
}


def _slot_well(draw: ImageDraw.ImageDraw, slot: int, accent: str = "slate") -> None:
    col, row = slot % 9, slot // 9
    x, y = 7 + 18 * col, 17 + 18 * row
    rounded(draw, (x + 1, y + 2, x + 18, y + 19), 2, "shell")
    rounded(draw, (x, y, x + 17, y + 17), 2, "slate_dark", accent)
    rounded(draw, (x + 2, y + 2, x + 15, y + 14), 1, "inner")
    draw.line(
        [((x + 4) * SUPERSAMPLE, (y + 3) * SUPERSAMPLE),
         ((x + 13) * SUPERSAMPLE, (y + 3) * SUPERSAMPLE)],
        fill=rgba(PALETTE[accent], 125),
        width=SUPERSAMPLE,
    )


def lots_background(heading: str, storage: bool = False) -> Image.Image:
    image, draw = base(125, heading)
    for slot in range(45):
        _slot_well(draw, slot, "blue" if storage else "slate")
    controls = {
        45: ("red", "red_dark") if storage else ("lime", "lime_dark"),
        46: ("blue", "blue_dark"),
        47: ("amber", "amber_dark"),
        48: ("slate", "slate_dark"),
        49: ("amber", "amber_dark"),
        50: ("slate", "slate_dark"),
        51: ("amber", "amber_dark"),
        52: ("blue", "blue_dark"),
        53: ("blue", "blue_dark"),
    }
    for slot, colorset in controls.items():
        plaque(draw, slot, *colorset)
    return image.resize((WIDTH, 125), Image.Resampling.LANCZOS)


def auction_categories() -> Image.Image:
    image, draw = base(107, "NATIONRISE · КАТЕГОРИИ")
    for index, slot in enumerate((12, 14, 21, 23, 30, 32, 39, 41)):
        _slot_well(draw, slot, ("blue", "amber", "lime", "slate")[index % 4])
    plaque(draw, 40, "red", "red_dark")
    return image.resize((WIDTH, 107), Image.Resampling.LANCZOS)


def donate() -> Image.Image:
    image, draw = base(125, "ПРИВИЛЕГИИ NATIONRISE")
    band(draw, (22, 33, 154, 72), "blue", "blue_dark")
    plaque(draw, 4, "amber", "amber_dark")
    for slot in (19, 20, 21, 22, 23, 24):
        plaque(draw, slot, "blue", "blue_dark")
    for slot in (9, 18, 27, 36, 17, 26, 35, 44):
        _slot_well(draw, slot, "slate")
    plaque(draw, 49, "amber", "amber_dark")
    return image.resize((WIDTH, 125), Image.Resampling.LANCZOS)


def events() -> Image.Image:
    image, draw = base(71, "РАСПИСАНИЕ ИВЕНТОВ")
    plaque(draw, 4, "blue", "blue_dark")
    for slot in (10, 11, 12, 13, 14, 15, 16, 22):
        plaque(draw, slot, "blue", "blue_dark")
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
        _slot_well(draw, slot, "blue")
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


def _map_poly(
    draw: ImageDraw.ImageDraw,
    points: tuple[tuple[int, int], ...],
    fill: tuple[int, int, int, int],
) -> None:
    scaled = [(x * SUPERSAMPLE, y * SUPERSAMPLE) for x, y in points]
    draw.polygon(scaled, fill=fill)
    draw.line(
        scaled + [scaled[0]],
        fill=(17, 24, 32, 255),
        width=2 * SUPERSAMPLE,
        joint="curve",
    )


def rtp_map() -> Image.Image:
    image, draw = base(125, "ТЕЛЕПОРТАЦИЯ")

    # Bright coherent world map, intentionally close in composition to the
    # approved reference: cyan ocean, coloured terrain and heavy pixel outline.
    rounded(draw, (4, 19, 171, 108), 3, "shell")
    draw.rounded_rectangle(
        (6 * SUPERSAMPLE, 21 * SUPERSAMPLE,
         169 * SUPERSAMPLE, 106 * SUPERSAMPLE),
        radius=2 * SUPERSAMPLE,
        fill=(74, 190, 216, 255),
        outline=(203, 211, 221, 255),
        width=2 * SUPERSAMPLE,
    )

    ice = (226, 239, 235, 255)
    grass = (71, 177, 105, 255)
    forest = (42, 128, 76, 255)
    desert = (208, 170, 67, 255)
    tundra = (130, 183, 128, 255)

    # North America + Greenland.
    _map_poly(draw, ((11, 38), (19, 30), (34, 27), (48, 31), (58, 39),
                     (55, 49), (46, 52), (40, 61), (29, 57), (24, 49),
                     (15, 50)), grass)
    _map_poly(draw, ((42, 33), (49, 29), (58, 36), (54, 42), (47, 40)), ice)
    _map_poly(draw, ((61, 27), (70, 23), (78, 27), (74, 35), (66, 36)), ice)
    _map_poly(draw, ((17, 42), (30, 34), (44, 37), (38, 48), (24, 51)), tundra)
    _map_poly(draw, ((31, 50), (43, 49), (48, 58), (40, 61)), desert)

    # South America.
    _map_poly(draw, ((43, 60), (55, 58), (65, 65), (63, 76), (57, 84),
                     (54, 96), (49, 102), (45, 91), (47, 78), (40, 69)), grass)
    _map_poly(draw, ((47, 64), (57, 63), (61, 73), (56, 82), (51, 76)), forest)
    _map_poly(draw, ((47, 82), (55, 86), (53, 97), (49, 99)), desert)

    # Europe and Africa.
    _map_poly(draw, ((74, 35), (79, 29), (87, 31), (91, 28), (98, 33),
                     (103, 39), (98, 46), (89, 45), (84, 49), (77, 45)), tundra)
    _map_poly(draw, ((78, 49), (91, 47), (101, 54), (99, 67), (93, 78),
                     (87, 88), (82, 78), (83, 67), (76, 58)), grass)
    _map_poly(draw, ((79, 53), (98, 54), (99, 64), (83, 63)), desert)
    _map_poly(draw, ((86, 67), (97, 65), (93, 79), (87, 85)), forest)

    # Asia.
    _map_poly(draw, ((98, 32), (109, 25), (124, 27), (134, 24), (151, 30),
                     (164, 38), (161, 49), (150, 52), (143, 61), (132, 59),
                     (124, 65), (115, 57), (105, 53), (99, 43)), forest)
    _map_poly(draw, ((101, 34), (113, 28), (128, 30), (123, 42), (111, 46)), tundra)
    _map_poly(draw, ((116, 45), (132, 38), (148, 42), (143, 54), (129, 58)), grass)
    _map_poly(draw, ((106, 49), (121, 47), (126, 57), (115, 57)), desert)
    _map_poly(draw, ((151, 53), (158, 57), (153, 64), (147, 60)), grass)

    # Australia and small islands.
    _map_poly(draw, ((132, 75), (140, 69), (152, 72), (160, 80),
                     (157, 91), (146, 96), (136, 92), (129, 84)), desert)
    _map_poly(draw, ((141, 73), (154, 76), (156, 86), (148, 92), (139, 87)), grass)
    _map_poly(draw, ((162, 90), (166, 93), (163, 98), (159, 95)), forest)

    # Antarctica mirrors the reference and visually anchors random teleport.
    _map_poly(draw, ((21, 101), (39, 100), (52, 103), (70, 101),
                     (88, 104), (106, 101), (126, 103), (145, 100),
                     (158, 102), (150, 106), (31, 106)), ice)

    # Random teleport has its own lower-row control; there is no text under it
    # that an item sprite could cover.
    band(draw, (71, 109, 105, 124), "lime", "lime_dark")
    return image.resize((WIDTH, 125), Image.Resampling.NEAREST)


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
        lots_background("NATIONRISE · АУКЦИОН"),
        lots_background("NATIONRISE · МОИ ЛОТЫ", storage=True),
        auction_categories(),
        donate(),
        events(),
        casino(),
        jobs(),
        job_targets(),
        town_storage(),
        rtp_map(),
    )
    for image, (_, (filename, expected_height)) in zip(generated, GLYPHS.items()):
        expected = (WIDTH, expected_height)
        if image.size != expected:
            raise ValueError(f"{filename}: expected {expected}, got {image.size}")
        image.save(TEXTURE_DIR / filename)

    auction = generated[0]
    auction.resize(
        (auction.width * 4, auction.height * 4), Image.Resampling.NEAREST
    ).save(AUCTION_PREVIEW)
    overlay = auction.copy()
    samples = {
        0: "nr_shop_crystal.png",
        1: "nr_shop_money.png",
        2: "nr_b_bank.png",
        3: "nr_b_barracks.png",
        4: "nr_b_mall.png",
        9: "nr_tm_buildings.png",
        10: "nr_ah_cat_food.png",
        11: "nr_shop_war.png",
        45: "nr_ah_refresh.png",
        46: "nr_ah_storage.png",
        47: "nr_ah_prev.png",
        49: "nr_ah_page.png",
        51: "nr_ah_next.png",
        52: "nr_ah_categories.png",
        53: "nr_ah_emblem.png",
    }
    for slot, filename in samples.items():
        col, row = slot % 9, slot // 9
        x, y = 8 + col * 18, 18 + row * 18
        icon = Image.open(ITEM_TEXTURE_DIR / filename).convert("RGBA").resize(
            (16, 16), Image.Resampling.LANCZOS
        )
        overlay.alpha_composite(icon, (x, y))
    overlay.resize(
        (overlay.width * 4, overlay.height * 4), Image.Resampling.NEAREST
    ).save(AUCTION_OVERLAY_PREVIEW)

    categories = generated[2]
    categories.resize(
        (categories.width * 4, categories.height * 4), Image.Resampling.NEAREST
    ).save(AUCTION_CATEGORIES_PREVIEW)
    categories_overlay = categories.copy()
    for slot, filename in {
        12: "nr_ah_cat_all.png",
        14: "nr_ah_cat_gear.png",
        21: "nr_ah_cat_tools.png",
        23: "nr_ah_cat_food.png",
        30: "nr_ah_cat_blocks.png",
        32: "nr_ah_cat_brew.png",
        39: "nr_ah_cat_res.png",
        41: "nr_ah_cat_misc.png",
        40: "nr_ah_exit.png",
    }.items():
        col, row = slot % 9, slot // 9
        x, y = 8 + col * 18, 18 + row * 18
        icon = Image.open(ITEM_TEXTURE_DIR / filename).convert("RGBA").resize(
            (16, 16), Image.Resampling.LANCZOS
        )
        categories_overlay.alpha_composite(icon, (x, y))
    categories_overlay.resize(
        (categories_overlay.width * 4, categories_overlay.height * 4),
        Image.Resampling.NEAREST,
    ).save(AUCTION_CATEGORIES_OVERLAY_PREVIEW)

    rtp = generated[-1]
    rtp.resize(
        (rtp.width * 4, rtp.height * 4), Image.Resampling.NEAREST
    ).save(RTP_PREVIEW)
    overlay = rtp.copy()
    for slot, filename in RTP_MARKERS.items():
        col, row = slot % 9, slot // 9
        x, y = 8 + col * 18, 18 + row * 18
        icon = Image.open(ITEM_TEXTURE_DIR / filename).convert("RGBA").resize(
            (16, 16), Image.Resampling.LANCZOS
        )
        overlay.alpha_composite(icon, (x, y))
    overlay.resize(
        (overlay.width * 4, overlay.height * 4), Image.Resampling.NEAREST
    ).save(RTP_OVERLAY_PREVIEW)

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
    print(f"rtp map preview: {RTP_PREVIEW}")
    print(f"rtp marker-overlay preview: {RTP_OVERLAY_PREVIEW}")
    print(f"auction background preview: {AUCTION_PREVIEW}")
    print(f"auction item-overlay preview: {AUCTION_OVERLAY_PREVIEW}")
    print(f"auction categories preview: {AUCTION_CATEGORIES_PREVIEW}")
    print(f"auction categories overlay preview: {AUCTION_CATEGORIES_OVERLAY_PREVIEW}")


if __name__ == "__main__":
    main()
