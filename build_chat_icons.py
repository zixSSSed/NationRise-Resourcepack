# -*- coding: utf-8 -*-
"""Иконки из купленного набора «2000+ иконок» (12×12, пиксель-арт) — в шрифт пака (13.10.2026).

Берём именные иконки из папки «.png» набора (anvil, book, coins, crown …) и кладём их глифами
в minecraft:default на коды U+E750 + номер (по алфавиту имён — коды не плывут). Высота 12 и
картинка 12×12: один тексель на пиксель интерфейса, иконка не «двоится» ни на каком масштабе.

    py -3.13 build_chat_icons.py <набор.zip> pack            — в исходник пака (папка pack/)
    py -3.13 build_chat_icons.py <набор.zip> <в.zip> <из.zip> — дописать в готовый пак-зип

Коды для плагина — dev.townlands.util.Icons (держать в согласии с ICONS ниже).
"""
import io
import json
import os
import sys
import zipfile

BASE_CP = 0xE750
ASCENT, HEIGHT = 10, 12
FONT = "assets/minecraft/font/default.json"


def icons_from(set_zip):
    z = zipfile.ZipFile(set_zip)
    out = {}
    for n in z.namelist():
        if "/.png/" in n and n.lower().endswith(".png"):
            out[n.rsplit("/", 1)[-1][:-4]] = z.read(n)
    return dict(sorted(out.items()))


def providers(icons):
    ps = []
    for i, name in enumerate(icons):
        ps.append({"type": "bitmap", "file": f"minecraft:font/nr_icon_{name}.png",
                   "ascent": ASCENT, "height": HEIGHT, "chars": [chr(BASE_CP + i)]})
    return ps


def merge_font(font_json, icons):
    d = json.loads(font_json) if font_json else {"providers": []}
    ps = [p for p in d.get("providers", []) if not str(p.get("file", "")).startswith("minecraft:font/nr_icon_")]
    # перед «include/default», чтобы наши коды точно были раньше ванильных шрифтов
    idx = next((i for i, p in enumerate(ps) if p.get("type") == "reference" and "default" in str(p.get("id"))), len(ps))
    d["providers"] = ps[:idx] + providers(icons) + ps[idx:]
    return json.dumps(d, ensure_ascii=False, indent=2).encode("utf-8")


def to_dir(icons, root):
    tex = os.path.join(root, "assets", "minecraft", "textures", "font")
    os.makedirs(tex, exist_ok=True)
    for name, data in icons.items():
        open(os.path.join(tex, f"nr_icon_{name}.png"), "wb").write(data)
    fp = os.path.join(root, *FONT.split("/"))
    old = open(fp, "rb").read().decode("utf-8") if os.path.exists(fp) else None
    open(fp, "wb").write(merge_font(old, icons))


def to_zip(icons, src, dst):
    zin = zipfile.ZipFile(src)
    entries = {n: zin.read(n) for n in zin.namelist() if not n.startswith("assets/minecraft/textures/font/nr_icon_")}
    for name, data in icons.items():
        entries[f"assets/minecraft/textures/font/nr_icon_{name}.png"] = data
    entries[FONT] = merge_font(entries.get(FONT, b"").decode("utf-8") or None, icons)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(entries):
            info = zipfile.ZipInfo(n, date_time=(2026, 10, 13, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, entries[n])


def main():
    icons = icons_from(sys.argv[1])
    if sys.argv[2] == "pack":
        to_dir(icons, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pack"))
    else:
        to_zip(icons, sys.argv[3], sys.argv[2])
    for i, name in enumerate(icons):
        print(f"U+{BASE_CP + i:04X} {name}")


if __name__ == "__main__":
    main()
