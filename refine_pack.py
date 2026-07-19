# -*- coding: utf-8 -*-
import os, json
from fontTools import ttLib
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.path.join(ROOT, "pack", "assets", "minecraft", "font")
DEFAULT = os.path.join(FONTDIR, "default.json")
MONT_VAR = os.path.join(ROOT, "_mont_var.ttf")

# --- 1. Montserrat Bold (700) как игровой шрифт ---
f = ttLib.TTFont(MONT_VAR)
instantiateVariableFont(f, {"wght": 700}, inplace=True)
out = os.path.join(FONTDIR, "nationrise.ttf")
f.save(out)
cmap = f.getBestCmap()
need = "Привет Москва NationRise 123"
print("Montserrat 700 saved | cyrillic_ok =", all(ord(c) in cmap for c in need if c != " "),
      "| is_variable =", "fvar" in f)

# --- 2. default.json детерминированно ---
LOGO_CP = 0xE010
# (file, codepoint, ascent, height)
icons = [
    ("nr_crown",          0x265B, 7, 11),
    ("nr_crystal",        0x2756, 7, 10),
    ("nr_sun",            0x2600, 7, 10),
    ("nr_house",          0x2302, 9, 10),  # подняли: «уехал вниз» в чате
    ("nr_star4",          0x2726, 7, 10),
    ("nr_bank",           0x26C1, 7, 10),
    ("nr_flag",           0x2691, 9, 10),  # подняли вместе с домом
    ("nr_bolt",           0x26A1, 7, 11),
    ("nr_diamond",        0x25C6, 6, 9),
    ("nr_diamond_hollow", 0x25C7, 6, 9),
    ("nr_star_circle",    0x272A, 7, 10),
    ("nr_star5",          0x2605, 7, 10),
    ("nr_flower",         0x273F, 7, 10),
    ("nr_florette",       0x2740, 7, 10),
    ("nr_skull",          0x2620, 7, 10),
    ("nr_snowflake",      0x2744, 7, 10),
    ("nr_fire",           0x1F525, 7, 11),
    ("nr_biohazard",      0x2623, 7, 10),
    ("nr_yinyang",        0x262F, 7, 10),
]
providers = [
    {"type": "reference", "id": "minecraft:include/space"},
    {"type": "bitmap", "file": "minecraft:font/nr_logo.png", "ascent": 15, "height": 18, "chars": [chr(LOGO_CP)]},
]
for name, cp, asc, h in icons:
    providers.append({"type": "bitmap", "file": f"minecraft:font/{name}.png",
                      "ascent": asc, "height": h, "chars": [chr(cp)]})
# Deliberately no global TTF provider: players keep the vanilla text face while
# bitmap wordmarks, symbols and GUI backgrounds remain available.
providers.append({"type": "reference", "id": "minecraft:include/default"})
json.dump({"providers": providers}, open(DEFAULT, "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

chk = json.load(open(DEFAULT, encoding="utf-8"))
logo = [p for p in chk["providers"] if p.get("file") == "minecraft:font/nr_logo.png"][0]
print("default.json rebuilt | logo U+%04X h=%d asc=%d | icon ascent=7" % (
    ord(logo["chars"][0]), logo["height"], logo["ascent"]))
