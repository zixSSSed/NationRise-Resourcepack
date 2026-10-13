# -*- coding: utf-8 -*-
"""Иконки из купленного набора «2000+ иконок» — в шрифт пака (13.10.2026, переделано в тот же день).

Первый заход брал 12×12 «именные» иконки: в строке чата (8 px) они торчали и налезали на соседние
строки подсказки. Теперь — подобранные мелкие иконки набора (7–10 px, нарисованы в этом размере):
высота глифа = высоте картинки (один тексель на пиксель — чётко на любом масштабе интерфейса),
по вертикали — по центру строчных букв. Крупнее 10 px обрезаем до 10 (там только тень).

    py -3.13 build_chat_icons.py <набор.zip> pack            — в исходник пака (папка pack/)
    py -3.13 build_chat_icons.py <набор.zip> <в.zip> <из.zip> — дописать в готовый пак-зип

Коды для плагина — dev.townlands.util.Icons (держать в согласии с ICONS ниже: порядок = код).
"""
import io
import json
import os
import sys
import zipfile

from PIL import Image

BASE_CP = 0xE750
FONT = "assets/minecraft/font/default.json"
TEX = "assets/minecraft/textures/font/nr_icon_"

# порядок задаёт код U+E750 + i; какой файл набора — в artwork/chat-icons-pick.json
ICONS = ["clock", "person", "sword", "skull", "coin", "gem", "hourglass", "rook", "earth", "chat",
         "star", "heart", "key", "trophy", "crown", "money"]
PICK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artwork", "chat-icons-pick.json")


def load_icons(set_zip):
    z = zipfile.ZipFile(set_zip)
    pick = json.load(open(PICK, encoding="utf-8"))
    out = []
    for name in ICONS:
        member = pick[name]["member"]
        im = Image.open(io.BytesIO(z.read(member))).convert("RGBA")
        k = pick[name].get("k", 1)
        if k > 1:
            im = im.resize((im.width // k, im.height // k), Image.NEAREST)
        bb = im.split()[-1].getbbox()
        if bb:
            im = im.crop(bb)
        if im.width > 10 or im.height > 10:            # только тень — обрезаем до 10×10
            im = im.crop((0, 0, min(10, im.width), min(10, im.height)))
        if im.width < 10:                              # одна ширина у всех: текст после иконок — ровной колонкой
            pad = Image.new("RGBA", (10, im.height), (0, 0, 0, 0))
            pad.paste(im, ((10 - im.width) // 2, 0))
            im = pad
        buf = io.BytesIO()
        im.save(buf, "PNG")
        out.append((name, buf.getvalue(), im.height))
    return out


def providers(icons):
    ps = []
    for i, (name, _, h) in enumerate(icons):
        ascent = (h + 7) // 2                          # центр иконки — на середине строчных букв
        ps.append({"type": "bitmap", "file": f"minecraft:font/nr_icon_{name}.png",
                   "ascent": ascent, "height": h, "chars": [chr(BASE_CP + i)]})
    return ps


def merge_font(font_json, icons):
    d = json.loads(font_json) if font_json else {"providers": []}
    ps = [p for p in d.get("providers", []) if not str(p.get("file", "")).startswith("minecraft:font/nr_icon_")]
    idx = next((i for i, p in enumerate(ps) if p.get("type") == "reference" and "default" in str(p.get("id"))), len(ps))
    d["providers"] = ps[:idx] + providers(icons) + ps[idx:]
    return json.dumps(d, ensure_ascii=False, indent=2).encode("utf-8")


def to_dir(icons, root):
    tex = os.path.join(root, "assets", "minecraft", "textures", "font")
    os.makedirs(tex, exist_ok=True)
    for f in os.listdir(tex):
        if f.startswith("nr_icon_"):
            os.remove(os.path.join(tex, f))
    for name, data, _ in icons:
        open(os.path.join(tex, f"nr_icon_{name}.png"), "wb").write(data)
    fp = os.path.join(root, *FONT.split("/"))
    old = open(fp, "rb").read().decode("utf-8") if os.path.exists(fp) else None
    open(fp, "wb").write(merge_font(old, icons))


def to_zip(icons, src, dst):
    zin = zipfile.ZipFile(src)
    entries = {n: zin.read(n) for n in zin.namelist() if not n.startswith(TEX)}
    for name, data, _ in icons:
        entries[f"{TEX}{name}.png"] = data
    entries[FONT] = merge_font(entries.get(FONT, b"").decode("utf-8") or None, icons)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(entries):
            info = zipfile.ZipInfo(n, date_time=(2026, 10, 13, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, entries[n])


def main():
    icons = load_icons(sys.argv[1])
    if sys.argv[2] == "pack":
        to_dir(icons, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pack"))
    else:
        to_zip(icons, sys.argv[3], sys.argv[2])
    for i, (name, _, h) in enumerate(icons):
        print(f"U+{BASE_CP + i:04X} {name} h={h}")


if __name__ == "__main__":
    main()
