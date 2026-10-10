"""Базовый пак с FNAF (10.10.2026): лапы аниматроников от первого лица, картинки скримеров и,
по желанию, модели BetterModel из конкретной сборки.

py -3.13 fnaf_pack.py <базовый.zip> <выход.zip> [--bettermodel <build.zip>]

* Лапа: предмет `nationrise:fnaf_arm_<персонаж>` — предплечье и кисть правой руки модели, той же
  текстурой (атлас персонажа). Охотник держит её в руке: от первого лица видна лапа, а не своя рука.
* Скример: шрифт `nationrise:fnaf`, символ U+E000 + номер персонажа — морда крупным планом с открытой
  пастью (кадр jumpscare@0.5), отрисована тем же рендером, что и превью.
* --bettermodel: заменить в паке модели BetterModel на сборку сервера (build.zip). Имена ассетов
  BetterModel зависят от набора моделей — пак и сборка обязаны быть из одной пары.
"""
import io
import json
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import preview  # noqa: E402
from PIL import Image  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "..", "bettermodel", "models")
CHARS = ["fnaf_freddy", "fnaf_bonnie", "fnaf_chica", "fnaf_foxy", "fnaf_golden_freddy", "fnaf_springtrap",
         "fnaf_toy_freddy", "fnaf_toy_bonnie", "fnaf_toy_chica", "fnaf_mangle"]


def model_json(name):
    return json.load(open(os.path.join(MODELS, name + ".bbmodel"), encoding="utf-8"))


def texture_png(m):
    import base64
    return base64.b64decode(m["textures"][0]["source"].split(",", 1)[1])


def arm_model(m, name):
    """Предплечье+кисть правой руки → модель предмета (UV в шкале 0..16 при атласе 128)."""
    groups = {}

    def walk(node, chain):
        for ch in node.get("children", []):
            if isinstance(ch, dict):
                walk(ch, chain + [ch["name"]])
            else:
                groups[ch] = chain
    for n in m["outliner"]:
        walk(n, [n["name"]])
    els = [e for e in m["elements"] if any(g in ("forearm_r", "hand_r") for g in groups.get(e["uuid"], []))]
    xs = [v for e in els for v in (e["from"][0], e["to"][0])]
    ys = [v for e in els for v in (e["from"][1], e["to"][1])]
    zs = [v for e in els for v in (e["from"][2], e["to"][2])]
    # центрируем по X/Z в 8, низ кисти — на 0
    dx, dy, dz = 8 - (min(xs) + max(xs)) / 2, -min(ys), 8 - (min(zs) + max(zs)) / 2
    out = []
    for e in els:
        f = [e["from"][0] + dx, e["from"][1] + dy, e["from"][2] + dz]
        t = [e["to"][0] + dx, e["to"][1] + dy, e["to"][2] + dz]
        faces = {}
        for fn, fd in e["faces"].items():
            u0, v0, u1, v1 = fd["uv"]
            faces[fn] = {"uv": [round(u0 / 8, 3), round(v0 / 8, 3), round(u1 / 8, 3), round(v1 / 8, 3)], "texture": "#0"}
        out.append({"from": [round(v, 3) for v in f], "to": [round(v, 3) for v in t], "faces": faces})
    return {
        "textures": {"0": f"nationrise:item/fnaf/{name}", "particle": f"nationrise:item/fnaf/{name}"},
        "elements": out,
        "display": {
            # Лапа идёт снизу справа вперёд, кисть — дальше от камеры, пальцами вниз.
            "firstperson_righthand": {"rotation": [-62, -8, 4], "translation": [2.5, -1.5, -2.5], "scale": [0.95, 0.95, 0.95]},
            "firstperson_lefthand": {"rotation": [-62, 8, -4], "translation": [2.5, -1.5, -2.5], "scale": [0.95, 0.95, 0.95]},
            "thirdperson_righthand": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [0.01, 0.01, 0.01]},
            "gui": {"rotation": [20, -35, 0], "translation": [0, -1, 0], "scale": [0.8, 0.8, 0.8]},
            "ground": {"scale": [0.4, 0.4, 0.4]},
        },
    }


def jumpscare_png(m):
    """Морда крупным планом, пасть раскрыта; фон прозрачный, по краю — тёмная виньетка."""
    tex = Image.open(io.BytesIO(texture_png(m))).convert("RGBA")
    pose = preview.pose_of(m, "jumpscare@0.5")
    pose = {k: v for k, v in pose.items()}   # голова, челюсть, руки — берём как есть
    img = preview.render(m, tex, 0, 2, size=(256, 256), pose=pose, bg=(0, 0, 0, 0), only="h_head")
    return img


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    base, out = args[0], args[1]
    bm = None
    if "--bettermodel" in sys.argv:
        bm = sys.argv[sys.argv.index("--bettermodel") + 1]
    zin = zipfile.ZipFile(base)
    entries = {}
    for info in zin.infolist():
        n = info.filename
        if bm and (n.startswith("bettermodel_a/") or n.startswith("bettermodel_b/") or n.startswith("assets/bettermodel/")):
            continue
        if n.startswith("assets/nationrise/") and "/fnaf" in n:
            continue
        entries[n] = zin.read(n)
    if bm:
        zb = zipfile.ZipFile(bm)
        for n in zb.namelist():
            if n.startswith("assets/bettermodel/") and not n.endswith("/"):
                entries[n] = zb.read(n)
        meta = json.loads(entries["pack.mcmeta"])
        if "overlays" in meta:
            meta["overlays"]["entries"] = [e for e in meta["overlays"]["entries"]
                                           if not str(e.get("directory", "")).startswith("bettermodel_")]
            if not meta["overlays"]["entries"]:
                meta.pop("overlays")
        entries["pack.mcmeta"] = json.dumps(meta, ensure_ascii=False, indent=2).encode("utf-8")
    providers = []
    for i, name in enumerate(CHARS):
        m = model_json(name)
        short = name
        entries[f"assets/nationrise/textures/item/fnaf/{short}.png"] = texture_png(m)
        entries[f"assets/nationrise/models/item/fnaf_arm_{short[5:]}.json"] = json.dumps(arm_model(m, short)).encode()
        entries[f"assets/nationrise/items/fnaf_arm_{short[5:]}.json"] = json.dumps(
            {"model": {"type": "minecraft:model", "model": f"nationrise:item/fnaf_arm_{short[5:]}"}}).encode()
        buf = io.BytesIO()
        jumpscare_png(m).save(buf, "PNG")
        entries[f"assets/nationrise/textures/font/fnaf/{short}.png"] = buf.getvalue()
        providers.append({"type": "bitmap", "file": f"nationrise:font/fnaf/{short}.png", "ascent": 60, "height": 120,
                          "chars": [chr(0xE000 + i)]})
    entries["assets/nationrise/font/fnaf.json"] = json.dumps({"providers": providers}).encode()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(entries):
            info = zipfile.ZipInfo(n, date_time=(2026, 10, 10, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, entries[n])
    print(out, len(entries))


if __name__ == "__main__":
    main()
