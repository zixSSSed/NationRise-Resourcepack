# -*- coding: utf-8 -*-
"""Build Donatello's PLAYER_HEAD reward (CustomModelData 72001).

The source concept is kept in incoming/nr_turtlehead_concept.png. This builder
samples its green/purple/olive palette, writes a deterministic 64x16 Minecraft
head atlas, a 3D head model, and dual item definitions:

* assets/minecraft/items/player_head.json for current clients;
* assets/minecraft/models/item/player_head.json for legacy override clients.

CMD 72001 deliberately belongs to PLAYER_HEAD, not PAPER. An upper guard at
72002 restores the vanilla player-head model so unrelated future CMD values do
not inherit the turtle model through range/predicate threshold semantics.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from statistics import median

from PIL import Image


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "incoming" / "nr_turtlehead_concept.png"
MC = ROOT / "pack" / "assets" / "minecraft"
TEXTURE = MC / "textures" / "item" / "nr_turtlehead.png"
MODEL = MC / "models" / "item" / "nr_turtlehead.json"
VANILLA_MODEL = MC / "models" / "item" / "nr_player_head_vanilla.json"
MODERN_ITEM = MC / "items" / "player_head.json"
LEGACY_ITEM = MC / "models" / "item" / "player_head.json"
PREVIEW = ROOT / "logo" / "_turtlehead_preview.png"

CMD = 72001
UPPER_GUARD = CMD + 1


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def is_background(pixel: tuple[int, int, int, int]) -> bool:
    red, green, blue, alpha = pixel
    return alpha < 32 or (red > 225 and green < 70 and blue > 200)


def subject_bounds(image: Image.Image) -> tuple[int, int, int, int]:
    pixels = image.load()
    xs: list[int] = []
    ys: list[int] = []
    for y in range(image.height):
        for x in range(image.width):
            if not is_background(pixels[x, y]):
                xs.append(x)
                ys.append(y)
    if not xs:
        raise ValueError("concept image contains no foreground pixels")
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def sample(
    image: Image.Image,
    bounds: tuple[int, int, int, int],
    relative_x: float,
    relative_y: float,
    fallback: tuple[int, int, int],
) -> tuple[int, int, int]:
    left, top, right, bottom = bounds
    center_x = round(left + (right - left - 1) * relative_x)
    center_y = round(top + (bottom - top - 1) * relative_y)
    radius = max(2, round(min(right - left, bottom - top) * 0.018))
    colors: list[tuple[int, int, int]] = []
    pixels = image.load()
    for y in range(max(top, center_y - radius), min(bottom, center_y + radius + 1)):
        for x in range(max(left, center_x - radius), min(right, center_x + radius + 1)):
            pixel = pixels[x, y]
            if not is_background(pixel):
                colors.append(pixel[:3])
    if not colors:
        return fallback
    return tuple(round(median(channel)) for channel in zip(*colors))


def darken(color: tuple[int, int, int], amount: float) -> tuple[int, int, int, int]:
    return tuple(round(channel * amount) for channel in color) + (255,)


def lighten(color: tuple[int, int, int], amount: float) -> tuple[int, int, int, int]:
    return tuple(round(channel + (255 - channel) * amount) for channel in color) + (255,)


def palette_from_concept(image: Image.Image) -> dict[str, tuple[int, int, int, int]]:
    bounds = subject_bounds(image)
    green = sample(image, bounds, 0.50, 0.22, (72, 125, 45))
    purple = sample(image, bounds, 0.50, 0.50, (121, 65, 170))
    muzzle = sample(image, bounds, 0.50, 0.74, (166, 166, 75))
    return {
        "D": darken(green, 0.42),
        "A": darken(green, 0.72),
        "G": (*green, 255),
        "H": lighten(green, 0.16),
        "Q": darken(purple, 0.64),
        "P": (*purple, 255),
        "W": (244, 244, 236, 255),
        "K": (16, 18, 15, 255),
        "M": (*muzzle, 255),
        "N": darken(muzzle, 0.42),
        ".": (0, 0, 0, 0),
    }


def paint_face(
    atlas: Image.Image,
    origin: tuple[int, int],
    rows: tuple[str, ...],
    palette: dict[str, tuple[int, int, int, int]],
) -> None:
    if len(rows) != 8 or any(len(row) != 8 for row in rows):
        raise ValueError(f"face at {origin} must be exactly 8x8")
    pixels = atlas.load()
    ox, oy = origin
    for y, row in enumerate(rows):
        for x, key in enumerate(row):
            pixels[ox + x, oy + y] = palette[key]


def build_texture(concept: Image.Image) -> Image.Image:
    palette = palette_from_concept(concept)
    atlas = Image.new("RGBA", (64, 16), palette["."])

    # Unused base-atlas corner doubles as an opaque purple swatch for 3D mask tails.
    paint_face(atlas, (0, 0), (
        "PPPPPPPP",
        "PPPPPPPP",
        "PPQQPPQQ",
        "PPPPPPPP",
        "QQPPQQPP",
        "PPPPPPPP",
        "PPPPPPPP",
        "QQQQQQQQ",
    ), palette)

    paint_face(atlas, (8, 0), (
        "DDDDDDDD",
        "DGGGGGGD",
        "DGGHGGGD",
        "DGGGGGGD",
        "DAGGGGAD",
        "DAAAAAGD",
        "DGGGGGGD",
        "DDDDDDDD",
    ), palette)
    paint_face(atlas, (16, 0), (
        "DDDDDDDD",
        "DNNNNNND",
        "DNMMMMND",
        "DNMMMMND",
        "DNMMMMND",
        "DNMMMMND",
        "DNNNNNND",
        "DDDDDDDD",
    ), palette)

    right = (
        "DGGGGGGD",
        "GGGGGGGG",
        "PPPPPPPP",
        "QPPPPPPQ",
        "QQPPPPQQ",
        "GMMMMMAG",
        "GAAAAAAG",
        "DGGGGGGD",
    )
    left = tuple(row[::-1] for row in right)
    front = (
        "DGGGGGGD",
        "GGHGGHGG",
        "PPPPPPPP",
        "PWWPPWWP",
        "PWKPPKWP",
        "GMMMMMMG",
        "GMNMMNMG",
        "DMMNNMMD",
    )
    back = (
        "DGGGGGGD",
        "GGGGGGGG",
        "PPPPPPPP",
        "QPPPPPPQ",
        "QQPPPPQQ",
        "GGAAAAGG",
        "GAAAAAAG",
        "DGGGGGGD",
    )
    paint_face(atlas, (0, 8), right, palette)
    paint_face(atlas, (8, 8), front, palette)
    paint_face(atlas, (16, 8), left, palette)
    paint_face(atlas, (24, 8), back, palette)

    transparent = ("........",) * 8
    paint_face(atlas, (40, 0), transparent, palette)
    paint_face(atlas, (48, 0), transparent, palette)
    paint_face(atlas, (32, 8), (
        "........",
        "........",
        "PPPPPPPP",
        "PPPPPPPP",
        "QQQQQQQQ",
        "........",
        "........",
        "........",
    ), palette)
    paint_face(atlas, (40, 8), (
        "........",
        "........",
        "QPPPPPPQ",
        "P......P",
        "Q......Q",
        "........",
        "........",
        "........",
    ), palette)
    paint_face(atlas, (48, 8), (
        "........",
        "........",
        "PPPPPPPP",
        "PPPPPPPP",
        "QQQQQQQQ",
        "........",
        "........",
        "........",
    ), palette)
    paint_face(atlas, (56, 8), (
        "........",
        "........",
        "QPPPPPPQ",
        "PPPPPPPP",
        "QQQQQQQQ",
        "........",
        "........",
        "........",
    ), palette)
    return atlas


def head_faces(offset: int) -> dict[str, dict]:
    return {
        "north": {"uv": [2 + offset, 8, 4 + offset, 16], "texture": "#skin"},
        "south": {"uv": [6 + offset, 8, 8 + offset, 16], "texture": "#skin"},
        "west": {"uv": [0 + offset, 8, 2 + offset, 16], "texture": "#skin"},
        "east": {"uv": [4 + offset, 8, 6 + offset, 16], "texture": "#skin"},
        "up": {"uv": [2 + offset, 0, 4 + offset, 8], "texture": "#skin"},
        "down": {"uv": [4 + offset, 0, 6 + offset, 8], "texture": "#skin"},
    }


def ribbon_faces() -> dict[str, dict]:
    return {
        face: {"uv": [0, 0, 2, 8], "texture": "#skin"}
        for face in ("north", "south", "west", "east", "up", "down")
    }


def model_definition() -> dict:
    return {
        "credit": "NationRise — награда Донателло, CMD 72001",
        "textures": {
            "skin": "minecraft:item/nr_turtlehead",
            "particle": "minecraft:item/nr_turtlehead",
        },
        "elements": [
            {
                "name": "head",
                "from": [4, 5, 4],
                "to": [12, 13, 12],
                "faces": head_faces(0),
            },
            {
                "name": "raised_mask",
                "from": [3.75, 4.75, 3.75],
                "to": [12.25, 13.25, 12.25],
                "faces": head_faces(8),
            },
            {
                "name": "mask_knot",
                "from": [6.75, 8, 11.75],
                "to": [9.25, 10.5, 14],
                "faces": ribbon_faces(),
            },
            {
                "name": "mask_tail_left",
                "from": [5.25, 6.5, 12.5],
                "to": [7.25, 8, 16],
                "rotation": {
                    "origin": [7, 8, 13],
                    "axis": "z",
                    "angle": -22.5,
                },
                "faces": ribbon_faces(),
            },
            {
                "name": "mask_tail_right",
                "from": [8.75, 6, 12.5],
                "to": [10.75, 7.5, 16],
                "rotation": {
                    "origin": [9, 8, 13],
                    "axis": "z",
                    "angle": 22.5,
                },
                "faces": ribbon_faces(),
            },
        ],
        "display": {
            "head": {
                "translation": [0, 0, 0],
                "scale": [1.15, 1.15, 1.15],
            },
            "gui": {
                "rotation": [26, 222, 0],
                "scale": [1.0, 1.0, 1.0],
            },
            "ground": {
                "translation": [0, 3, 0],
                "scale": [0.45, 0.45, 0.45],
            },
            "fixed": {
                "rotation": [0, 180, 0],
                "scale": [1.0, 1.0, 1.0],
            },
            "thirdperson_righthand": {
                "rotation": [45, 45, 0],
                "translation": [0, 3, 0],
                "scale": [0.5, 0.5, 0.5],
            },
        },
    }


def vanilla_special_model() -> dict:
    return {
        "type": "minecraft:special",
        "base": "minecraft:item/template_skull",
        "model": {"type": "minecraft:player_head"},
    }


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(f"missing source concept: {SOURCE}")

    concept = Image.open(SOURCE).convert("RGBA")
    atlas = build_texture(concept)
    TEXTURE.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(TEXTURE, optimize=True)

    write_json(MODEL, model_definition())
    write_json(VANILLA_MODEL, {"parent": "minecraft:item/template_skull"})
    write_json(MODERN_ITEM, {
        "model": {
            "type": "minecraft:range_dispatch",
            "property": "minecraft:custom_model_data",
            "index": 0,
            "fallback": vanilla_special_model(),
            "entries": [
                {
                    "threshold": CMD,
                    "model": {
                        "type": "minecraft:model",
                        "model": "minecraft:item/nr_turtlehead",
                    },
                },
                {
                    "threshold": UPPER_GUARD,
                    "model": vanilla_special_model(),
                },
            ],
        },
    })
    write_json(LEGACY_ITEM, {
        "parent": "minecraft:item/template_skull",
        "overrides": [
            {
                "predicate": {"custom_model_data": CMD},
                "model": "minecraft:item/nr_turtlehead",
            },
            {
                "predicate": {"custom_model_data": UPPER_GUARD},
                "model": "minecraft:item/nr_player_head_vanilla",
            },
        ],
    })

    preview = Image.new("RGBA", (512, 256), (23, 18, 31, 255))
    concept.thumbnail((240, 240), Image.Resampling.LANCZOS)
    preview.alpha_composite(concept, (8, (256 - concept.height) // 2))
    enlarged = atlas.resize((256, 64), Image.Resampling.NEAREST)
    preview.alpha_composite(enlarged, (256, 96))
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    preview.save(PREVIEW)

    for path in (MODEL, VANILLA_MODEL, MODERN_ITEM, LEGACY_ITEM):
        json.loads(path.read_text(encoding="utf-8"))
    source_sha = hashlib.sha1(SOURCE.read_bytes()).hexdigest()
    texture_sha = hashlib.sha1(TEXTURE.read_bytes()).hexdigest()
    print(f"source: {SOURCE.name} sha1={source_sha}")
    print(f"texture: {TEXTURE} {atlas.width}x{atlas.height} sha1={texture_sha}")
    print(f"model: {MODEL.name}, elements={len(model_definition()['elements'])}")
    print(f"CMD {CMD}: PLAYER_HEAD dual-format; upper guard={UPPER_GUARD}")
    print(f"preview: {PREVIEW}")


if __name__ == "__main__":
    main()
