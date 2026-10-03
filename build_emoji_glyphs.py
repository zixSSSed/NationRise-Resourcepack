# -*- coding: utf-8 -*-
"""Иконки-эмодзи пака (nr_gui_*, 82 шт.) из листов imagegen — как иконки скорборда.

02.10.2026. Листы artwork/emoji-sheet-1..4.png сгенерированы Codex ($imagegen) по образцу
scoreboard-icons-source.png на фоне #FF00FF, сетка 7×3, порядок — artwork/emoji-brief.md.
Скрипт делает только техническую работу: убирает пурпурный фон, находит иконки (связные
области), раскладывает их по порядку (строки сверху вниз, слева направо) и вписывает каждую
в 16×16 так же, как build_scoreboard_icons.fit_game_icon. Перерисовки нет.

python build_emoji_glyphs.py <выходная_папка> [preview.png]
Имена файлов — те же nr_gui_<имя>.png, что уже есть в паке (сопоставление по символу).
"""
import json, os, sys
from collections import deque
from PIL import Image, ImageEnhance, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(ROOT, "artwork")

# порядок = порядок в emoji-brief.md (лист → символы)
SHEETS = [
    "ℹ⌛⏸☄☮⚒⚓⚔⚙⚠⛏⛓⛔✅✉❤🌊🌌🌍🌐🍖",
    "🍞🍯🍺🎁🎒🎣🎭🎰🎲🏆🏗🏙🏛🏪🏰🐟🐢👁👋👑👤",
    "👥💀💎💔💣💤💥💰📅📊📋📖📢📦🔇🔍🔐🔑🔒🔗",
    "🔨🔮🔱🕊🕷🕸🖼🗑🗳🗺🛡🤝🥇🥈🥉🦑🧭🧱🩸🪱",
]
OUTPUT_SIZE = 20   # 03.10.2026: было 16 — при высоте 10 в строке это 1,6 текселя на точку, пиксели дублировались («двоятся»); 20 = ровно 2 на точку


def chroma(im):
    """#FF00FF → прозрачность; края без розовой каймы."""
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            mag = min(r, b) - g                    # «пурпурность»: красный и синий без зелёного
            if mag > 150 and r > 170 and b > 170:
                px[x, y] = (0, 0, 0, 0)
            elif mag > 60 and r > 120 and b > 120:
                k = (mag - 60) / 90                # полупрозрачная кайма
                na = int(255 * (1 - k))
                m = min(r, b)                       # снимаем розовый оттенок
                px[x, y] = (min(r, max(g, m - mag)), g, min(b, max(g, m - mag)), na)
    return im


def components(alpha, thr=96, grow=10, step=2):
    """Связные области (с запасом grow пикселей, чтобы детали одной иконки слиплись)."""
    w, h = alpha.size
    sw, sh = w // step, h // step
    small = alpha.resize((sw, sh), Image.NEAREST).point(lambda v: 255 if v > thr else 0)
    grown = small.filter(ImageFilter.MaxFilter(2 * (grow // step) + 1))
    m = grown.load()
    seen = [[False] * sw for _ in range(sh)]
    boxes = []
    for y in range(sh):
        for x in range(sw):
            if m[x, y] and not seen[y][x]:
                q = deque([(x, y)]); seen[y][x] = True
                x0 = x1 = x; y0 = y1 = y; n = 0
                while q:
                    cx, cy = q.popleft(); n += 1
                    x0, x1, y0, y1 = min(x0, cx), max(x1, cx), min(y0, cy), max(y1, cy)
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < sw and 0 <= ny < sh and m[nx, ny] and not seen[ny][nx]:
                            seen[ny][nx] = True; q.append((nx, ny))
                if n > 60:
                    boxes.append((x0 * step, y0 * step, (x1 + 1) * step, (y1 + 1) * step))
    return boxes


def order(boxes, rows=3):
    """Строки по центрам Y (k-средних не нужно: разрыв между строками большой), внутри — по X."""
    boxes = sorted(boxes, key=lambda b: (b[1] + b[3]) / 2)
    cy = [(b[1] + b[3]) / 2 for b in boxes]
    gaps = sorted(range(1, len(boxes)), key=lambda i: cy[i] - cy[i - 1], reverse=True)[:rows - 1]
    cuts = sorted(gaps)
    out, prev = [], 0
    for c in cuts + [len(boxes)]:
        out += sorted(boxes[prev:c], key=lambda b: b[0]); prev = c
    return out


def fit_game_icon(source):
    """Как build_scoreboard_icons.fit_game_icon: вписать без искажений, чуть резкости."""
    target_inner = OUTPUT_SIZE - 2
    scale = min(target_inner / source.width, target_inner / source.height)
    width = max(1, round(source.width * scale)); height = max(1, round(source.height * scale))
    resized = source.resize((width, height), Image.Resampling.BOX)   # BOX без ореолов LANCZOS
    resized = ImageEnhance.Contrast(resized).enhance(1.08)
    resized = ImageEnhance.Color(resized).enhance(1.06)
    resized = resized.filter(ImageFilter.UnsharpMask(radius=0.6, percent=120, threshold=2))
    out = Image.new("RGBA", (OUTPUT_SIZE, OUTPUT_SIZE), (0, 0, 0, 0))
    out.alpha_composite(resized, ((OUTPUT_SIZE - width) // 2, (OUTPUT_SIZE - height) // 2))
    return out


def main(outdir, preview=None, font_json=None):
    os.makedirs(outdir, exist_ok=True)
    names = {}
    if font_json:
        d = json.load(open(font_json, encoding="utf-8"))
        for p in d["providers"]:
            n = p.get("file", "").split("/")[-1]
            if n.startswith("nr_gui_"):
                for ch in p.get("chars", []):
                    names[ch.replace("️", "")] = n
    tiles, problems = [], []
    for i, chars in enumerate(SHEETS, 1):
        path = os.path.join(ART, f"emoji-sheet-{i}.png")
        if not os.path.exists(path):
            problems.append(f"нет {path}"); continue
        im = chroma(Image.open(path))
        boxes = order(components(im.getchannel("A")))
        if len(boxes) != len(chars):
            problems.append(f"лист {i}: найдено {len(boxes)} иконок, ждали {len(chars)}")
        for ch, b in zip(chars, boxes):
            crop = im.crop(b)
            bb = crop.getbbox()
            icon = fit_game_icon(crop.crop(bb) if bb else crop)
            fn = names.get(ch, "nr_gui_%x.png" % ord(ch))
            icon.save(os.path.join(outdir, fn))
            tiles.append((ch, crop, icon))
    print("иконок:", len(tiles))
    for p in problems: print("ВНИМАНИЕ:", p)
    if preview and tiles:
        cols, s = 14, 4; cell = OUTPUT_SIZE * s + 8
        rows = (len(tiles) + cols - 1) // cols
        bg = Image.new("RGBA", (cols * cell + 8, rows * cell + 8), (16, 0, 16, 255))
        for k, (_, _, icon) in enumerate(tiles):
            bg.alpha_composite(icon.resize((OUTPUT_SIZE * s, OUTPUT_SIZE * s), Image.NEAREST), (8 + (k % cols) * cell, 8 + (k // cols) * cell))
        bg.save(preview)


if __name__ == "__main__":
    main(*sys.argv[1:])
