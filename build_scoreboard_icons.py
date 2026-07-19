# -*- coding: utf-8 -*-
"""NationRise scoreboard pixel-emoji glyphs.

Generates 33 deterministic 16x16 RGBA sprites and registers them in the
default Minecraft font at U+E100..U+E120. The sprites are intentionally
simple: Minecraft renders them at nine pixels high on the scoreboard.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Callable

from PIL import Image, ImageDraw, ImageFont


ROOT = os.path.dirname(os.path.abspath(__file__))
FONT_TEXTURES = os.path.join(
    ROOT, "pack", "assets", "minecraft", "textures", "font"
)
DEFAULT_FONT = os.path.join(
    ROOT, "pack", "assets", "minecraft", "font", "default.json"
)
PREVIEW = os.path.join(ROOT, "logo", "scoreboard-icons-preview.png")

SIZE = 16
DARK = "#17202D"
WHITE = "#F2F5F8"
STEEL = "#3B82C4"
STEEL_LIGHT = "#72C7F2"
GOLD = "#E0A93C"
GOLD_LIGHT = "#FFE36A"
EMERALD = "#3CA76A"
EMERALD_LIGHT = "#72DD91"
CARMINE = "#CF4E4E"
CARMINE_LIGHT = "#FF7878"
PURPLE = "#8A58C7"
PURPLE_LIGHT = "#C28CFF"
BROWN = "#7A4B2A"
BROWN_LIGHT = "#C78343"
GRAY = "#8B95A3"
GRAY_LIGHT = "#CBD3DD"
BLACK = "#20252E"


@dataclass(frozen=True)
class Glyph:
    ident: str
    title: str
    codepoint: int
    draw: Callable[[], Image.Image]


def canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    return image, ImageDraw.Draw(image)


def outlined_polygon(draw: ImageDraw.ImageDraw, points, fill, width=1):
    draw.polygon(points, fill=fill)
    draw.line(points + [points[0]], fill=DARK, width=width, joint="curve")


def outlined_rect(draw: ImageDraw.ImageDraw, box, fill, width=1):
    draw.rectangle(box, fill=fill, outline=DARK, width=width)


def outlined_ellipse(draw: ImageDraw.ImageDraw, box, fill, width=1):
    draw.ellipse(box, fill=fill, outline=DARK, width=width)


def money_bag():
    im, d = canvas()
    outlined_polygon(
        d,
        [(5, 4), (4, 6), (3, 9), (3, 13), (5, 15), (11, 15),
         (13, 13), (13, 9), (12, 6), (11, 4)],
        BROWN,
    )
    d.rectangle((5, 3, 11, 5), fill=GOLD, outline=DARK)
    d.rectangle((6, 1, 8, 3), fill=GOLD_LIGHT, outline=DARK)
    d.rectangle((9, 1, 11, 3), fill=GOLD_LIGHT, outline=DARK)
    outlined_ellipse(d, (6, 8, 10, 12), GOLD)
    d.point((8, 9), fill=GOLD_LIGHT)
    return im


def crystal():
    im, d = canvas()
    outlined_polygon(d, [(8, 1), (13, 6), (11, 14), (8, 15), (4, 13), (3, 6)], PURPLE)
    d.line([(8, 2), (8, 14)], fill=PURPLE_LIGHT)
    d.line([(4, 6), (8, 8), (12, 6)], fill=PURPLE_LIGHT)
    d.line([(5, 5), (8, 2), (11, 5)], fill=WHITE)
    return im


def star():
    im, d = canvas()
    points = [(8, 1), (10, 5), (15, 6), (11, 9), (12, 14),
              (8, 12), (4, 14), (5, 9), (1, 6), (6, 5)]
    outlined_polygon(d, points, GOLD)
    d.line([(8, 3), (8, 10)], fill=GOLD_LIGHT)
    d.point((6, 6), fill=WHITE)
    return im


def town_hall():
    im, d = canvas()
    outlined_polygon(d, [(2, 6), (8, 2), (14, 6)], STEEL)
    outlined_rect(d, (3, 6, 13, 14), STEEL)
    for x in (5, 8, 11):
        d.rectangle((x, 7, x + 1, 12), fill=STEEL_LIGHT)
    d.rectangle((7, 10, 9, 14), fill=BROWN, outline=DARK)
    d.line((2, 14, 14, 14), fill=DARK, width=2)
    d.point((8, 3), fill=WHITE)
    return im


def role_badge():
    im, d = canvas()
    outlined_polygon(d, [(3, 2), (13, 2), (13, 10), (8, 15), (3, 10)], PURPLE)
    outlined_polygon(d, [(8, 4), (9, 7), (12, 7), (10, 9), (11, 12),
                         (8, 10), (5, 12), (6, 9), (4, 7), (7, 7)], GOLD)
    d.point((7, 4), fill=WHITE)
    return im


def bank_chest():
    im, d = canvas()
    outlined_rect(d, (2, 6, 14, 14), BROWN)
    outlined_polygon(d, [(2, 6), (4, 3), (12, 3), (14, 6)], GOLD)
    d.line((3, 8, 13, 8), fill=GOLD_LIGHT)
    outlined_rect(d, (7, 8, 9, 12), GOLD)
    d.point((8, 9), fill=WHITE)
    return im


def nation_flag():
    im, d = canvas()
    d.line((3, 1, 3, 15), fill=DARK, width=2)
    outlined_polygon(d, [(4, 2), (13, 3), (11, 8), (4, 7)], STEEL)
    d.line((5, 3, 11, 4), fill=STEEL_LIGHT)
    d.rectangle((1, 14, 5, 15), fill=GOLD, outline=DARK)
    return im


def ideology_podium():
    im, d = canvas()
    outlined_rect(d, (4, 7, 12, 14), BROWN)
    outlined_rect(d, (3, 6, 13, 8), GOLD)
    d.rectangle((7, 9, 9, 14), fill=BROWN_LIGHT)
    d.line((11, 1, 11, 6), fill=DARK, width=1)
    outlined_polygon(d, [(12, 1), (15, 2), (12, 4)], STEEL)
    d.point((5, 7), fill=GOLD_LIGHT)
    return im


def map_pin():
    im, d = canvas()
    outlined_ellipse(d, (3, 1, 13, 11), EMERALD)
    outlined_polygon(d, [(5, 9), (11, 9), (8, 15)], EMERALD)
    outlined_ellipse(d, (6, 4, 10, 8), STEEL_LIGHT)
    d.point((8, 5), fill=WHITE)
    return im


def crossed_swords():
    im, d = canvas()
    d.line((3, 3, 13, 13), fill=DARK, width=4)
    d.line((13, 3, 3, 13), fill=DARK, width=4)
    d.line((4, 3, 13, 12), fill=GRAY_LIGHT, width=2)
    d.line((12, 3, 3, 12), fill=WHITE, width=2)
    d.line((2, 11, 5, 14), fill=GOLD, width=2)
    d.line((11, 14, 14, 11), fill=GOLD, width=2)
    return im


def skull():
    im, d = canvas()
    outlined_ellipse(d, (3, 1, 13, 11), GRAY_LIGHT)
    outlined_rect(d, (5, 9, 11, 14), GRAY_LIGHT)
    d.rectangle((5, 6, 7, 8), fill=BLACK)
    d.rectangle((9, 6, 11, 8), fill=BLACK)
    d.point((8, 9), fill=BLACK)
    for x in (6, 8, 10):
        d.line((x, 12, x, 14), fill=DARK)
    d.point((5, 3), fill=WHITE)
    return im


def scales():
    im, d = canvas()
    d.line((8, 2, 8, 14), fill=DARK, width=2)
    d.line((3, 5, 13, 5), fill=GOLD, width=2)
    d.line((3, 5, 1, 10), fill=DARK)
    d.line((13, 5, 15, 10), fill=DARK)
    outlined_polygon(d, [(0, 10), (5, 10), (4, 13), (1, 13)], CARMINE)
    outlined_polygon(d, [(11, 10), (16, 10), (15, 13), (12, 13)], STEEL)
    d.rectangle((5, 14, 11, 15), fill=GOLD, outline=DARK)
    return im


def flame():
    im, d = canvas()
    outlined_polygon(
        d,
        [(8, 1), (10, 5), (12, 3), (13, 8), (12, 13), (9, 15),
         (5, 14), (3, 11), (4, 6), (6, 8)],
        CARMINE,
    )
    outlined_polygon(d, [(8, 6), (10, 9), (9, 13), (6, 13), (6, 10)], GOLD)
    d.point((8, 9), fill=GOLD_LIGHT)
    return im


def trophy_flame():
    im, d = canvas()
    outlined_rect(d, (5, 6, 11, 11), GOLD)
    d.line((5, 7, 2, 6), fill=GOLD, width=2)
    d.line((11, 7, 14, 6), fill=GOLD, width=2)
    d.line((8, 11, 8, 14), fill=DARK, width=2)
    d.rectangle((5, 14, 11, 15), fill=GOLD, outline=DARK)
    outlined_polygon(d, [(8, 1), (10, 4), (9, 7), (6, 7), (6, 4)], CARMINE)
    d.point((8, 4), fill=GOLD_LIGHT)
    return im


def damage_dealt():
    im, d = canvas()
    d.line((4, 13, 12, 3), fill=DARK, width=4)
    d.line((5, 12, 12, 4), fill=WHITE, width=2)
    d.line((2, 11, 6, 15), fill=GOLD, width=2)
    outlined_polygon(d, [(9, 1), (15, 1), (12, 6), (15, 6), (8, 14), (10, 8), (7, 8)], CARMINE)
    return im


def damage_taken():
    im, d = canvas()
    outlined_polygon(d, [(2, 2), (14, 2), (13, 10), (8, 15), (3, 10)], BROWN)
    outlined_polygon(d, [(4, 4), (12, 4), (11, 9), (8, 12), (5, 9)], CARMINE)
    d.line((5, 5, 11, 10), fill=CARMINE_LIGHT)
    d.point((6, 4), fill=WHITE)
    return im


def victory_medal():
    im, d = canvas()
    outlined_polygon(d, [(4, 1), (7, 1), (9, 7), (6, 8)], STEEL)
    outlined_polygon(d, [(9, 1), (12, 1), (10, 8), (7, 7)], CARMINE)
    outlined_ellipse(d, (3, 6, 13, 15), GOLD)
    d.point((8, 8), fill=GOLD_LIGHT)
    d.line((6, 11, 10, 11), fill=BROWN)
    return im


def pickaxe():
    im, d = canvas()
    d.line((5, 14, 11, 3), fill=DARK, width=4)
    d.line((6, 14, 11, 4), fill=BROWN_LIGHT, width=2)
    d.line((3, 5, 7, 2), fill=DARK, width=3)
    d.line((7, 2, 14, 4), fill=DARK, width=3)
    d.line((4, 5, 7, 3), fill=STEEL_LIGHT, width=1)
    d.line((7, 3, 13, 4), fill=STEEL_LIGHT, width=1)
    return im


def fishing():
    im, d = canvas()
    d.arc((1, 0, 13, 12), 205, 335, fill=PURPLE_LIGHT, width=2)
    d.line((11, 4, 13, 10), fill=GRAY_LIGHT)
    outlined_polygon(d, [(8, 10), (12, 8), (15, 10), (12, 13), (8, 12), (6, 14), (7, 11)], STEEL)
    d.point((12, 10), fill=WHITE)
    d.line((2, 13, 7, 5), fill=BROWN_LIGHT, width=2)
    return im


def anchor():
    im, d = canvas()
    outlined_ellipse(d, (6, 1, 10, 5), STEEL_LIGHT)
    d.line((8, 5, 8, 13), fill=DARK, width=3)
    d.line((8, 5, 8, 13), fill=STEEL_LIGHT)
    d.line((3, 9, 13, 9), fill=STEEL_LIGHT, width=2)
    d.arc((2, 7, 14, 15), 0, 180, fill=DARK, width=3)
    d.arc((3, 8, 13, 14), 0, 180, fill=STEEL_LIGHT, width=1)
    return im


def hourglass():
    im, d = canvas()
    outlined_rect(d, (3, 1, 13, 3), GOLD)
    outlined_rect(d, (3, 13, 13, 15), GOLD)
    d.line((5, 3, 11, 13), fill=DARK, width=2)
    d.line((11, 3, 5, 13), fill=DARK, width=2)
    outlined_polygon(d, [(5, 4), (11, 4), (8, 8)], PURPLE_LIGHT)
    outlined_polygon(d, [(8, 8), (11, 12), (5, 12)], PURPLE)
    return im


def today_clock():
    im, d = canvas()
    outlined_ellipse(d, (2, 2, 14, 14), PURPLE_LIGHT)
    outlined_ellipse(d, (4, 4, 12, 12), WHITE)
    d.line((8, 5, 8, 9), fill=PURPLE, width=1)
    d.line((8, 9, 11, 9), fill=PURPLE, width=1)
    d.rectangle((1, 1, 4, 4), fill=GOLD, outline=DARK)
    d.point((2, 2), fill=GOLD_LIGHT)
    return im


def ping_bars():
    im, d = canvas()
    heights = (4, 7, 10, 13)
    colors = (EMERALD, EMERALD, EMERALD_LIGHT, GOLD_LIGHT)
    for i, (height, color) in enumerate(zip(heights, colors)):
        x = 1 + i * 4
        outlined_rect(d, (x, 15 - height, x + 2, 14), color)
    return im


def gear():
    im, d = canvas()
    for box in ((7, 0, 9, 4), (7, 12, 9, 15), (0, 7, 4, 9), (12, 7, 15, 9),
                (2, 2, 5, 5), (11, 2, 14, 5), (2, 11, 5, 14), (11, 11, 14, 14)):
        d.rectangle(box, fill=EMERALD, outline=DARK)
    outlined_ellipse(d, (3, 3, 13, 13), EMERALD)
    outlined_ellipse(d, (6, 6, 10, 10), BLACK)
    d.point((5, 4), fill=EMERALD_LIGHT)
    return im


def online_players():
    im, d = canvas()
    outlined_ellipse(d, (5, 1, 11, 7), STEEL_LIGHT)
    outlined_ellipse(d, (0, 4, 6, 10), STEEL)
    outlined_ellipse(d, (10, 4, 16, 10), STEEL)
    outlined_ellipse(d, (3, 7, 13, 15), STEEL)
    d.rectangle((1, 10, 5, 14), fill=STEEL, outline=DARK)
    d.rectangle((11, 10, 15, 14), fill=STEEL, outline=DARK)
    d.point((7, 2), fill=WHITE)
    return im


def clock():
    im, d = canvas()
    outlined_ellipse(d, (1, 1, 15, 15), STEEL)
    outlined_ellipse(d, (3, 3, 13, 13), WHITE)
    d.line((8, 4, 8, 9), fill=STEEL, width=2)
    d.line((8, 9, 11, 11), fill=CARMINE, width=2)
    d.point((5, 4), fill=STEEL_LIGHT)
    return im


def compass():
    im, d = canvas()
    outlined_ellipse(d, (1, 1, 15, 15), GOLD)
    outlined_ellipse(d, (3, 3, 13, 13), BLACK)
    outlined_polygon(d, [(9, 4), (10, 9), (7, 12), (6, 7)], CARMINE)
    d.point((8, 8), fill=WHITE)
    return im


def leaf():
    im, d = canvas()
    outlined_polygon(d, [(2, 12), (3, 6), (8, 2), (14, 1), (13, 8), (8, 13)], EMERALD)
    d.line((3, 13, 12, 4), fill=EMERALD_LIGHT, width=1)
    d.line((7, 9, 4, 8), fill=EMERALD_LIGHT)
    d.line((9, 7, 11, 8), fill=EMERALD_LIGHT)
    return im


def communism():
    im, d = canvas()
    d.arc((1, 3, 12, 14), 35, 300, fill=DARK, width=4)
    d.arc((2, 4, 11, 13), 35, 300, fill=CARMINE_LIGHT, width=2)
    d.line((4, 3, 13, 12), fill=DARK, width=4)
    d.line((5, 3, 13, 11), fill=CARMINE, width=2)
    d.line((9, 2, 14, 5), fill=DARK, width=3)
    d.line((10, 2, 14, 4), fill=GOLD_LIGHT, width=1)
    return im


def authoritarian_eagle():
    im, d = canvas()
    outlined_polygon(d, [(8, 3), (6, 5), (3, 3), (1, 5), (5, 9),
                         (2, 10), (5, 13), (8, 10)], GRAY)
    outlined_polygon(d, [(8, 3), (10, 5), (13, 3), (15, 5), (11, 9),
                         (14, 10), (11, 13), (8, 10)], GRAY)
    d.line((2, 5, 6, 8), fill=GRAY_LIGHT)
    d.line((14, 5, 10, 8), fill=GRAY_LIGHT)
    outlined_polygon(d, [(6, 7), (10, 7), (10, 13), (8, 15), (6, 13)], CARMINE)
    d.point((8, 8), fill=GOLD_LIGHT)
    d.point((9, 4), fill=WHITE)
    return im


def crown():
    im, d = canvas()
    outlined_polygon(d, [(2, 5), (5, 9), (8, 3), (11, 9), (14, 5),
                         (13, 13), (3, 13)], GOLD)
    d.rectangle((3, 11, 13, 14), fill=GOLD, outline=DARK)
    d.point((5, 10), fill=CARMINE)
    d.point((8, 10), fill=STEEL)
    d.point((11, 10), fill=CARMINE)
    d.point((8, 5), fill=GOLD_LIGHT)
    return im


def democracy():
    im, d = canvas()
    d.line((8, 2, 8, 14), fill=GOLD, width=2)
    d.line((3, 5, 13, 5), fill=STEEL_LIGHT, width=2)
    d.line((3, 5, 1, 10), fill=DARK)
    d.line((13, 5, 15, 10), fill=DARK)
    outlined_polygon(d, [(0, 10), (5, 10), (4, 13), (1, 13)], STEEL)
    outlined_polygon(d, [(11, 10), (16, 10), (15, 13), (12, 13)], STEEL)
    d.rectangle((5, 14, 11, 15), fill=GOLD, outline=DARK)
    d.point((8, 2), fill=GOLD_LIGHT)
    return im


def theocracy():
    im, d = canvas()
    outlined_polygon(d, [(2, 6), (8, 2), (14, 6)], GOLD)
    outlined_rect(d, (3, 6, 13, 14), WHITE)
    for x in (5, 8, 11):
        d.rectangle((x, 7, x + 1, 13), fill=GOLD)
    d.line((8, 0, 8, 5), fill=GOLD_LIGHT, width=1)
    d.line((6, 2, 10, 2), fill=GOLD_LIGHT, width=1)
    d.line((2, 14, 14, 14), fill=DARK, width=2)
    return im


GLYPHS = [
    Glyph("balance", "Баланс", 0xE100, money_bag),
    Glyph("crystals", "Кристаллы", 0xE101, crystal),
    Glyph("rank", "Донат-ранг", 0xE102, star),
    Glyph("town", "Город", 0xE103, town_hall),
    Glyph("town_role", "Должность", 0xE104, role_badge),
    Glyph("town_bank", "Банк города", 0xE105, bank_chest),
    Glyph("nation", "Нация", 0xE106, nation_flag),
    Glyph("ideology", "Идеология", 0xE107, ideology_podium),
    Glyph("zone", "Территория", 0xE108, map_pin),
    Glyph("kills", "Убийства", 0xE109, crossed_swords),
    Glyph("deaths", "Смерти", 0xE10A, skull),
    Glyph("kd", "К/Д", 0xE10B, scales),
    Glyph("streak", "Серия", 0xE10C, flame),
    Glyph("best_streak", "Лучшая серия", 0xE10D, trophy_flame),
    Glyph("damage_dealt", "Урон нанесён", 0xE10E, damage_dealt),
    Glyph("damage_taken", "Урон получен", 0xE10F, damage_taken),
    Glyph("wins", "Победы", 0xE110, victory_medal),
    Glyph("job", "Профессия", 0xE111, pickaxe),
    Glyph("fish_level", "Рыбалка", 0xE112, fishing),
    Glyph("anchors", "Якоря", 0xE113, anchor),
    Glyph("playtime", "Наиграно", 0xE114, hourglass),
    Glyph("playtime_today", "Сегодня", 0xE115, today_clock),
    Glyph("ping", "Пинг", 0xE116, ping_bars),
    Glyph("tps", "TPS", 0xE117, gear),
    Glyph("online", "Онлайн", 0xE118, online_players),
    Glyph("time_msk", "Время МСК", 0xE119, clock),
    Glyph("coords", "Координаты", 0xE11A, compass),
    Glyph("biome", "Биом", 0xE11B, leaf),
    Glyph("ideology_communism", "Коммунизм", 0xE11C, communism),
    Glyph("ideology_fascism", "Фашизм", 0xE11D, authoritarian_eagle),
    Glyph("ideology_monarchy", "Монархия", 0xE11E, crown),
    Glyph("ideology_democracy", "Демократия", 0xE11F, democracy),
    Glyph("ideology_theocracy", "Теократия", 0xE120, theocracy),
]


def provider_for(glyph: Glyph) -> dict:
    return {
        "type": "bitmap",
        "file": f"minecraft:font/nr_sb_{glyph.ident}.png",
        "ascent": 8,
        "height": 9,
        "chars": [chr(glyph.codepoint)],
    }


def update_default_font():
    with open(DEFAULT_FONT, encoding="utf-8") as handle:
        data = json.load(handle)
    providers = [
        provider
        for provider in data["providers"]
        if not provider.get("file", "").startswith("minecraft:font/nr_sb_")
        and provider.get("file") != "minecraft:nationrise.ttf"
    ]
    insert_at = next(
        (
            index
            for index, provider in enumerate(providers)
            if provider.get("type") == "reference"
            and provider.get("id") == "minecraft:include/default"
        ),
        len(providers),
    )
    providers[insert_at:insert_at] = [provider_for(glyph) for glyph in GLYPHS]
    data["providers"] = providers
    with open(DEFAULT_FONT, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=1)
        handle.write("\n")


def preview_font(size: int):
    candidates = [
        r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def make_preview(rendered: list[tuple[Glyph, Image.Image]]):
    columns = 4
    cell_w, cell_h = 300, 78
    rows = (len(rendered) + columns - 1) // columns
    sheet = Image.new("RGBA", (columns * cell_w, rows * cell_h + 72), "#10151D")
    draw = ImageDraw.Draw(sheet)
    title_font = preview_font(26)
    label_font = preview_font(18)
    small_font = preview_font(14)
    draw.text((24, 14), "NationRise — пиксель-эмодзи скорборда", font=title_font, fill=WHITE)
    draw.text(
        (24, 46),
        "Слева: увеличение ×3. В игре каждый глиф отображается высотой 9 px.",
        font=small_font,
        fill=GRAY_LIGHT,
    )
    for index, (glyph, icon) in enumerate(rendered):
        row, column = divmod(index, columns)
        x, y = column * cell_w, 72 + row * cell_h
        draw.rounded_rectangle(
            (x + 8, y + 6, x + cell_w - 8, y + cell_h - 6),
            radius=8,
            fill="#202936",
            outline="#39485C",
            width=1,
        )
        zoom = icon.resize((48, 48), Image.Resampling.NEAREST)
        sheet.alpha_composite(zoom, (x + 20, y + 15))
        draw.text((x + 80, y + 15), glyph.title, font=label_font, fill=WHITE)
        draw.text(
            (x + 80, y + 42),
            f"{glyph.ident}  U+{glyph.codepoint:04X}",
            font=small_font,
            fill="#72C7F2",
        )
    os.makedirs(os.path.dirname(PREVIEW), exist_ok=True)
    sheet.save(PREVIEW)


def main():
    os.makedirs(FONT_TEXTURES, exist_ok=True)
    rendered = []
    for glyph in GLYPHS:
        image = glyph.draw()
        if image.size != (SIZE, SIZE) or image.mode != "RGBA" or not image.getbbox():
            raise RuntimeError(f"Invalid glyph: {glyph.ident}")
        path = os.path.join(FONT_TEXTURES, f"nr_sb_{glyph.ident}.png")
        image.save(path, optimize=True)
        rendered.append((glyph, image))
    update_default_font()
    make_preview(rendered)
    print(f"Scoreboard glyphs: {len(rendered)} generated")
    print(f"Codepoints: U+{GLYPHS[0].codepoint:04X}..U+{GLYPHS[-1].codepoint:04X}")
    print(f"Preview: {PREVIEW}")


if __name__ == "__main__":
    main()
