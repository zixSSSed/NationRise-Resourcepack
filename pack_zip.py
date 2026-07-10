# -*- coding: utf-8 -*-
import os, zipfile, hashlib, json

ROOT = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(ROOT, "pack")
OUT = os.path.join(ROOT, "NationRise-Resourcepack.zip")

# валидация ВСЕХ json (pack.mcmeta + font + items + models) — кривой json ломает пак молча
_jsons = [os.path.join(PACK, "pack.mcmeta")]
for dp, _, files in os.walk(os.path.join(PACK, "assets")):
    for fn in files:
        if fn.endswith(".json"): _jsons.append(os.path.join(dp, fn))
_bad = 0
for p in _jsons:
    try:
        with open(p, encoding="utf-8") as f:
            json.load(f)
    except Exception as e:
        print("JSON BAD:", os.path.relpath(p, PACK), "->", e); _bad += 1
if _bad:
    raise SystemExit(f"{_bad} битых JSON — пак не собран")
print(f"JSON ok: {len(_jsons)} files validated")

entries = []
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for dp, _, files in os.walk(PACK):
        for fn in files:
            full = os.path.join(dp, fn)
            arc = os.path.relpath(full, PACK).replace(os.sep, "/")
            z.write(full, arc)
            entries.append(arc)

sha1 = hashlib.sha1(open(OUT, "rb").read()).hexdigest()
print("\nzip:", OUT)
print("size:", os.path.getsize(OUT), "bytes")
print("sha1:", sha1)
print("entries:", len(entries))
for e in sorted(entries):
    print("  ", e)
