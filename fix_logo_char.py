# -*- coding: utf-8 -*-
import json, os
ROOT = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(ROOT, "pack", "assets", "minecraft", "font", "default.json")
LOGO_CP = 0xE010
data = json.load(open(p, encoding="utf-8"))
found = False
for prov in data["providers"]:
    if prov.get("file") == "minecraft:font/nr_logo.png":
        prov["chars"] = [chr(LOGO_CP)]
        found = True
json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
data2 = json.load(open(p, encoding="utf-8"))
for prov in data2["providers"]:
    if prov.get("file") == "minecraft:font/nr_logo.png":
        ch = prov["chars"][0]
        print("logo provider found:", found, "| chars[0] = U+%04X" % ord(ch), "| len =", len(ch))
