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

# GUI/font contract: no global TTF, every bitmap exists, and both item-model
# formats expose the same CMD set (1.21.4+ items/ and <=1.21.3 overrides).
font_root = os.path.join(PACK, "assets")
missing_bitmaps = []
ttf_providers = []
default_has_vanilla = False
for p in _jsons:
    if os.path.basename(os.path.dirname(p)) != "font":
        continue
    with open(p, encoding="utf-8") as source:
        definition = json.load(source)
    for provider in definition.get("providers", []):
        if provider.get("type") == "ttf":
            ttf_providers.append(os.path.relpath(p, PACK))
        if (
            os.path.normcase(p)
            == os.path.normcase(os.path.join(PACK, "assets", "minecraft", "font", "default.json"))
            and provider.get("type") == "reference"
            and provider.get("id") == "minecraft:include/default"
        ):
            default_has_vanilla = True
        if provider.get("type") != "bitmap":
            continue
        ref = provider.get("file", "")
        namespace, sep, asset = ref.partition(":")
        if not sep:
            namespace, asset = "minecraft", ref
        bitmap = os.path.join(font_root, namespace, "textures", asset.replace("/", os.sep))
        if not os.path.isfile(bitmap):
            missing_bitmaps.append(f"{os.path.relpath(p, PACK)} -> {ref}")

if ttf_providers:
    raise SystemExit("TTF providers forbidden: " + ", ".join(sorted(set(ttf_providers))))
if not default_has_vanilla:
    raise SystemExit("assets/minecraft/font/default.json must reference minecraft:include/default")
if missing_bitmaps:
    raise SystemExit("Missing bitmap assets:\n  " + "\n  ".join(missing_bitmaps))

new_paper = json.load(open(
    os.path.join(PACK, "assets", "minecraft", "items", "paper.json"),
    encoding="utf-8",
))
old_paper = json.load(open(
    os.path.join(PACK, "assets", "minecraft", "models", "item", "paper.json"),
    encoding="utf-8",
))
new_cmds = {
    entry["threshold"]
    for entry in new_paper.get("model", {}).get("entries", [])
    if "threshold" in entry
}
old_cmds = {
    override.get("predicate", {}).get("custom_model_data")
    for override in old_paper.get("overrides", [])
}
old_cmds.discard(None)
if new_cmds != old_cmds:
    only_new = sorted(new_cmds - old_cmds)
    only_old = sorted(old_cmds - new_cmds)
    raise SystemExit(
        "paper CMD formats differ; run build_dualformat.py "
        f"(only items/: {only_new}, only models/: {only_old})"
    )
print(f"GUI contract ok: {len(new_cmds)} paper CMDs, bitmap refs complete, vanilla font")

entries = []
files = []
for dp, dirs, names in os.walk(PACK):
    dirs.sort()
    for fn in sorted(names):
        full = os.path.join(dp, fn)
        arc = os.path.relpath(full, PACK).replace(os.sep, "/")
        files.append((arc, full))

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for arc, full in sorted(files):
        # Stable filename order and timestamp make equal source trees byte-for-byte reproducible.
        info = zipfile.ZipInfo(arc, date_time=(1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        with open(full, "rb") as source:
            data = source.read()
        # Git may check text files out as CRLF on Windows. The pack semantics are
        # identical, but raw ZIP bytes and SHA-1 would otherwise differ by OS.
        if arc.endswith((".json", ".mcmeta")):
            data = data.replace(b"\r\n", b"\n")
        z.writestr(info, data)
        entries.append(arc)

sha1 = hashlib.sha1(open(OUT, "rb").read()).hexdigest()
print("\nzip:", OUT)
print("size:", os.path.getsize(OUT), "bytes")
print("sha1:", sha1)
print("entries:", len(entries))
for e in sorted(entries):
    print("  ", e)
