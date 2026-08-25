# -*- coding: utf-8 -*-
"""Build NationRise scoreboard glyphs from the owner-approved concept sheet.

The source sheet is an imagegen pixel-art sheet with its magenta chroma key
already removed. This script performs only deterministic technical work:
segmentation, proportional fitting, game-size resampling, font registration,
and preview generation. It does not redraw or reinterpret the artwork.
"""

from __future__ import annotations

import json
import os
import colorsys
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(
    ROOT, "artwork", "scoreboard-icons-source-transparent.png"
)
FONT_TEXTURES = os.path.join(
    ROOT, "pack", "assets", "minecraft", "textures", "font"
)
DEFAULT_FONT = os.path.join(
    ROOT, "pack", "assets", "minecraft", "font", "default.json"
)
PREVIEW = os.path.join(ROOT, "logo", "scoreboard-icons-preview.png")
GAME_PREVIEW = os.path.join(
    ROOT, "logo", "scoreboard-icons-game-scale-preview.png"
)

SOURCE_ROWS = ((141, 293), (362, 532), (627, 758))
EXPECTED_ROW_COUNTS = (11, 10, 13)
ALPHA_THRESHOLD = 96
OUTPUT_SIZE = 16
RENDER_HEIGHT = 10

WHITE = "#F2F5F8"
MUTED = "#AEB8C5"
CYAN = "#72C7F2"


@dataclass(frozen=True)
class Glyph:
    ident: str
    title: str
    codepoint: int


GLYPHS = [
    Glyph("balance", "Баланс", 0xE100),
    Glyph("crystals", "Кристаллы", 0xE101),
    Glyph("rank", "Донат-ранг", 0xE102),
    Glyph("town", "Город", 0xE103),
    Glyph("town_role", "Должность", 0xE104),
    Glyph("town_bank", "Банк города", 0xE105),
    Glyph("nation", "Нация", 0xE106),
    Glyph("ideology", "Идеология", 0xE107),
    Glyph("zone", "Территория", 0xE108),
    Glyph("kills", "Убийства", 0xE109),
    Glyph("deaths", "Смерти", 0xE10A),
    Glyph("kd", "К/Д", 0xE10B),
    Glyph("streak", "Серия", 0xE10C),
    Glyph("best_streak", "Лучшая серия", 0xE10D),
    Glyph("damage_dealt", "Урон нанесён", 0xE10E),
    Glyph("damage_taken", "Урон получен", 0xE10F),
    Glyph("wins", "Победы", 0xE110),
    Glyph("job", "Профессия", 0xE111),
    Glyph("fish_level", "Рыбалка", 0xE112),
    Glyph("anchors", "Якоря", 0xE113),
    Glyph("playtime", "Наиграно", 0xE114),
    Glyph("playtime_today", "Сегодня", 0xE115),
    Glyph("ping", "Пинг", 0xE116),
    Glyph("tps", "TPS", 0xE117),
    Glyph("online", "Онлайн", 0xE118),
    Glyph("time_msk", "Время МСК", 0xE119),
    Glyph("coords", "Координаты", 0xE11A),
    Glyph("biome", "Биом", 0xE11B),
    Glyph("ideology_communism", "Коммунизм", 0xE11C),
    Glyph("ideology_fascism", "Фашизм", 0xE11D),
    Glyph("ideology_monarchy", "Монархия", 0xE11E),
    Glyph("ideology_democracy", "Демократия", 0xE11F),
    Glyph("ideology_theocracy", "Теократия", 0xE120),
    Glyph("ping_bad", "Плохая связь", 0xE121),
]


def font(size: int, bold: bool = False):
    candidates = [
        (
            r"C:\Windows\Fonts\arialbd.ttf"
            if bold
            else r"C:\Windows\Fonts\arial.ttf"
        ),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def active_x_ranges(
    alpha: Image.Image, y0: int, y1: int
) -> list[tuple[int, int]]:
    width = alpha.width
    ranges = []
    start = end = None
    pixels = alpha.load()
    for x in range(width):
        active = any(
            pixels[x, y] > ALPHA_THRESHOLD for y in range(y0, y1 + 1)
        )
        if active and start is None:
            start = x
        if active:
            end = x
        if start is not None and not active:
            ranges.append((start, end))
            start = end = None
    if start is not None:
        ranges.append((start, end))
    return ranges


def extract_source_icons(source: Image.Image) -> list[Image.Image]:
    alpha = source.getchannel("A")
    rows = []
    for (y0, y1), expected in zip(SOURCE_ROWS, EXPECTED_ROW_COUNTS):
        ranges = active_x_ranges(alpha, y0, y1)
        if len(ranges) != expected:
            raise RuntimeError(
                f"Concept segmentation changed at y={y0}..{y1}: "
                f"expected {expected}, got {len(ranges)}"
            )
        row = []
        for x0, x1 in ranges:
            candidate = source.crop((x0, y0, x1 + 1, y1 + 1))
            bbox = candidate.getbbox()
            if bbox is None:
                raise RuntimeError("Empty concept icon")
            row.append(candidate.crop(bbox))
        rows.append(row)

    # The model produced one extra dark-purple clock at row 3, index 0.
    # The approved lilac "today" clock is index 1. All other requested icons
    # remain in their prompt order.
    ordered = rows[0] + rows[1] + rows[2][1:]
    if len(ordered) != len(GLYPHS) - 1:
        raise RuntimeError(
            f"Expected {len(GLYPHS) - 1} source icons after removing the duplicate, "
            f"got {len(ordered)}"
        )
    return ordered


def fit_game_icon(source: Image.Image) -> Image.Image:
    """Fit approved art into a crisp 16x16 RGBA glyph without distortion."""
    target_inner = OUTPUT_SIZE - 2
    scale = min(target_inner / source.width, target_inner / source.height)
    width = max(1, round(source.width * scale))
    height = max(1, round(source.height * scale))
    resized = source.resize((width, height), Image.Resampling.LANCZOS)
    resized = ImageEnhance.Contrast(resized).enhance(1.08)
    resized = ImageEnhance.Color(resized).enhance(1.06)
    resized = resized.filter(
        ImageFilter.UnsharpMask(radius=0.7, percent=145, threshold=2)
    )
    output = Image.new("RGBA", (OUTPUT_SIZE, OUTPUT_SIZE), (0, 0, 0, 0))
    x = (OUTPUT_SIZE - width) // 2
    y = (OUTPUT_SIZE - height) // 2
    output.alpha_composite(resized, (x, y))
    return output


def red_connection_variant(source: Image.Image) -> Image.Image:
    """Preserve the approved bars artwork and change only its signal colour."""
    output = source.copy()
    pixels = output.load()
    for y in range(output.height):
        for x in range(output.width):
            red, green, blue, alpha = pixels[x, y]
            if alpha == 0:
                continue
            hue, saturation, value = colorsys.rgb_to_hsv(
                red / 255.0, green / 255.0, blue / 255.0
            )
            if value < 0.28:
                continue
            saturation = max(saturation, 0.78)
            new_red, new_green, new_blue = colorsys.hsv_to_rgb(
                0.0, saturation, value
            )
            pixels[x, y] = (
                round(new_red * 255),
                round(new_green * 255),
                round(new_blue * 255),
                alpha,
            )
    return output


def bright_crystal_variant(source: Image.Image) -> Image.Image:
    """Lift the approved purple crystal facets without changing its silhouette."""
    output = source.copy()
    pixels = output.load()
    for y in range(output.height):
        for x in range(output.width):
            red, green, blue, alpha = pixels[x, y]
            if alpha == 0:
                continue
            hue, saturation, value = colorsys.rgb_to_hsv(
                red / 255.0, green / 255.0, blue / 255.0
            )
            # Preserve the near-black pixel outline.
            if value < 0.14:
                continue
            if saturation < 0.18:
                # Neutral facet pixels become pale lavender highlights.
                hue = 0.75
                saturation = 0.22
                value = min(1.0, max(0.86, value * 1.30))
            else:
                # Keep the original purple family while restoring game-scale
                # readability lost during the 16 px downsample.
                hue = 0.75 + (hue - 0.75) * 0.35
                saturation = min(0.94, max(0.70, saturation * 1.08))
                value = min(1.0, max(0.60, 0.24 + value * 1.28))
            new_red, new_green, new_blue = colorsys.hsv_to_rgb(
                hue, saturation, value
            )
            pixels[x, y] = (
                round(new_red * 255),
                round(new_green * 255),
                round(new_blue * 255),
                alpha,
            )
    return output


def provider(glyph: Glyph) -> dict:
    return {
        "type": "bitmap",
        "file": f"minecraft:font/nr_sb_{glyph.ident}.png",
        "ascent": 8,
        "height": RENDER_HEIGHT,
        "chars": [chr(glyph.codepoint)],
    }


def update_default_font():
    with open(DEFAULT_FONT, encoding="utf-8") as handle:
        data = json.load(handle)
    providers = [
        entry
        for entry in data["providers"]
        if not entry.get("file", "").startswith("minecraft:font/nr_sb_")
        and entry.get("file") != "minecraft:nationrise.ttf"
    ]
    insert_at = next(
        (
            index
            for index, entry in enumerate(providers)
            if entry.get("type") == "reference"
            and entry.get("id") == "minecraft:include/default"
        ),
        len(providers),
    )
    providers[insert_at:insert_at] = [provider(glyph) for glyph in GLYPHS]
    data["providers"] = providers
    with open(DEFAULT_FONT, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=1)
        handle.write("\n")


def make_contact_preview(rendered: list[tuple[Glyph, Image.Image]]):
    columns = 4
    cell_w, cell_h = 310, 92
    rows = (len(rendered) + columns - 1) // columns
    sheet = Image.new(
        "RGBA", (columns * cell_w, rows * cell_h + 82), "#10151D"
    )
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (24, 14),
        "NationRise — утверждённые pixel-emoji",
        font=font(27, bold=True),
        fill=WHITE,
    )
    draw.text(
        (24, 50),
        "Слева арт 16×16 увеличен ×4; маленький значок справа — игровой render 10 px.",
        font=font(15),
        fill=MUTED,
    )
    for index, (glyph, icon) in enumerate(rendered):
        row, column = divmod(index, columns)
        x, y = column * cell_w, 82 + row * cell_h
        draw.rounded_rectangle(
            (x + 8, y + 6, x + cell_w - 8, y + cell_h - 6),
            radius=9,
            fill="#202936",
            outline="#43546B",
        )
        sheet.alpha_composite(
            icon.resize((64, 64), Image.Resampling.NEAREST), (x + 18, y + 14)
        )
        game = icon.resize(
            (RENDER_HEIGHT, RENDER_HEIGHT), Image.Resampling.LANCZOS
        )
        sheet.alpha_composite(game, (x + 92, y + 18))
        draw.text((x + 118, y + 15), glyph.title, font=font(18), fill=WHITE)
        draw.text(
            (x + 118, y + 44),
            f"{glyph.ident} · U+{glyph.codepoint:04X}",
            font=font(14),
            fill=CYAN,
        )
        draw.text(
            (x + 118, y + 65),
            "full pack",
            font=font(12),
            fill=MUTED,
        )
    os.makedirs(os.path.dirname(PREVIEW), exist_ok=True)
    sheet.save(PREVIEW, optimize=True)


def make_game_preview(rendered: list[tuple[Glyph, Image.Image]]):
    examples = [
        ("balance", "Баланс: $481"),
        ("crystals", "Кристаллы: 2"),
        ("town", "Город: 2xс"),
        ("town_role", "Должность: Житель"),
        ("nation", "Нация: нет"),
        ("ideology", "Идеология: Фашизм"),
        ("kills", "Убийств: 19"),
        ("deaths", "Смертей: 7"),
        ("job", "Профессия: Шахтёр"),
        ("ping", "Пинг: 42 мс"),
        ("ping_bad", "Пинг: 240 мс"),
        ("online", "Онлайн: 14/100"),
        ("coords", "125 72 -380"),
    ]
    by_id = {glyph.ident: icon for glyph, icon in rendered}
    scale = 3
    logical_w, logical_h = 180, 12 + len(examples) * 12
    panel = Image.new("RGBA", (logical_w, logical_h), (20, 25, 34, 238))
    draw = ImageDraw.Draw(panel)
    text_font = font(9)
    for index, (ident, text) in enumerate(examples):
        y = 8 + index * 12
        game = by_id[ident].resize(
            (RENDER_HEIGHT, RENDER_HEIGHT), Image.Resampling.LANCZOS
        )
        panel.alpha_composite(game, (8, y))
        draw.text((22, y), text, font=text_font, fill=WHITE)
    panel = panel.resize(
        (logical_w * scale, logical_h * scale), Image.Resampling.NEAREST
    )
    panel.save(GAME_PREVIEW, optimize=True)


def main():
    if not os.path.exists(SOURCE):
        raise SystemExit(f"Missing approved transparent source: {SOURCE}")
    source = Image.open(SOURCE).convert("RGBA")
    source_icons = extract_source_icons(source)
    rendered = []
    os.makedirs(FONT_TEXTURES, exist_ok=True)
    for glyph, source_icon in zip(GLYPHS[:-1], source_icons):
        icon = fit_game_icon(source_icon)
        if glyph.ident == "crystals":
            icon = bright_crystal_variant(icon)
        if icon.size != (16, 16) or not icon.getbbox():
            raise RuntimeError(f"Invalid generated glyph: {glyph.ident}")
        icon.save(
            os.path.join(FONT_TEXTURES, f"nr_sb_{glyph.ident}.png"),
            optimize=True,
        )
        rendered.append((glyph, icon))
    bad_ping = red_connection_variant(
        next(icon for glyph, icon in rendered if glyph.ident == "ping")
    )
    bad_ping.save(
        os.path.join(FONT_TEXTURES, "nr_sb_ping_bad.png"), optimize=True
    )
    rendered.append((GLYPHS[-1], bad_ping))
    update_default_font()
    make_contact_preview(rendered)
    make_game_preview(rendered)
    print(f"Approved concept glyphs: {len(rendered)} generated")
    print(f"Codepoints: U+{GLYPHS[0].codepoint:04X}..U+{GLYPHS[-1].codepoint:04X}")
    print(f"Preview: {PREVIEW}")
    print(f"Game-scale preview: {GAME_PREVIEW}")


if __name__ == "__main__":
    main()
