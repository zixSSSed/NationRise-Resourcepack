# -*- coding: utf-8 -*-
"""Build simplified BlueMap POI icons from the owner-approved art direction."""

from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(
    ROOT, "artwork", "bluemap-icons-simplified-transparent.png"
)
OUT = os.path.join(ROOT, "bluemap")
PREVIEW = os.path.join(ROOT, "logo", "bluemap-town-icons-preview.png")

ALPHA_THRESHOLD = 96
OUTPUT_SIZE = 32
WHITE = "#F2F5F8"
MUTED = "#AEB8C5"

ICONS = [
    ("nationrise-town-level-1.png", "Уровень 1"),
    ("nationrise-town-level-2.png", "Уровень 2"),
    ("nationrise-town-level-3.png", "Уровень 3"),
    ("nationrise-town-level-4.png", "Уровень 4"),
    ("nationrise-town-level-5.png", "Уровень 5"),
    ("nationrise-town-capital.png", "Столица"),
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


def active_x_ranges(alpha: Image.Image) -> list[tuple[int, int]]:
    pixels = alpha.load()
    ranges = []
    start = end = None
    for x in range(alpha.width):
        active = any(
            pixels[x, y] > ALPHA_THRESHOLD for y in range(alpha.height)
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
    # Ignore isolated chroma-key residue at a sheet edge.
    return [(x0, x1) for x0, x1 in ranges if x1 - x0 >= 8]


def extract(source: Image.Image) -> list[Image.Image]:
    ranges = active_x_ranges(source.getchannel("A"))
    if len(ranges) != len(ICONS):
        raise RuntimeError(
            f"Expected {len(ICONS)} BlueMap icons, found {len(ranges)}"
        )
    result = []
    for x0, x1 in ranges:
        candidate = source.crop((x0, 0, x1 + 1, source.height))
        bbox = candidate.getbbox()
        if bbox is None:
            raise RuntimeError("Empty BlueMap source icon")
        result.append(candidate.crop(bbox))
    return result


def fit(source: Image.Image) -> Image.Image:
    # The dedicated simplified sheet already removes tiny decorations. Keep
    # its clean silhouette and use almost the full 32px marker footprint.
    inner = OUTPUT_SIZE - 2
    scale = min(inner / source.width, inner / source.height)
    width = max(1, round(source.width * scale))
    height = max(1, round(source.height * scale))
    resized = source.resize((width, height), Image.Resampling.LANCZOS)
    resized = ImageEnhance.Contrast(resized).enhance(1.12)
    resized = ImageEnhance.Color(resized).enhance(1.08)
    resized = resized.filter(
        ImageFilter.UnsharpMask(radius=0.65, percent=165, threshold=2)
    )
    output = Image.new(
        "RGBA", (OUTPUT_SIZE, OUTPUT_SIZE), (0, 0, 0, 0)
    )
    output.alpha_composite(
        resized, ((OUTPUT_SIZE - width) // 2, (OUTPUT_SIZE - height) // 2)
    )
    return output


def make_preview(rendered: list[tuple[str, str, Image.Image]]):
    width, height = 1220, 292
    sheet = Image.new("RGBA", (width, height), "#10151D")
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (24, 15),
        "NationRise BlueMap — утверждённый pixel-art",
        font=font(28, bold=True),
        fill=WHITE,
    )
    draw.text(
        (24, 54),
        "Каждый PNG реально 32×32; ниже показан nearest-neighbour zoom ×4.",
        font=font(16),
        fill=MUTED,
    )
    for index, (_, title, image) in enumerate(rendered):
        x = 16 + index * 200
        draw.rounded_rectangle(
            (x, 91, x + 188, 275),
            radius=11,
            fill="#202936",
            outline="#43546B",
        )
        sheet.alpha_composite(
            image.resize((128, 128), Image.Resampling.NEAREST), (x + 30, 101)
        )
        label = f"{index + 1}. {title}" if index < 5 else "Столица"
        draw.text((x + 42, 238), label, font=font(17), fill=WHITE)
    os.makedirs(os.path.dirname(PREVIEW), exist_ok=True)
    sheet.save(PREVIEW, optimize=True)


def main():
    if not os.path.exists(SOURCE):
        raise SystemExit(f"Missing approved transparent source: {SOURCE}")
    source = Image.open(SOURCE).convert("RGBA")
    source_icons = extract(source)
    os.makedirs(OUT, exist_ok=True)
    rendered = []
    for (name, title), source_icon in zip(ICONS, source_icons):
        image = fit(source_icon)
        if image.size != (32, 32) or not image.getbbox():
            raise RuntimeError(f"Invalid BlueMap icon: {name}")
        image.save(os.path.join(OUT, name), optimize=True)
        rendered.append((name, title, image))
    make_preview(rendered)
    print(f"Approved concept BlueMap icons: {len(rendered)} generated")
    print(f"Output: {OUT}")
    print(f"Preview: {PREVIEW}")


if __name__ == "__main__":
    main()
