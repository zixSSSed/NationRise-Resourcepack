# -*- coding: utf-8 -*-
"""Догоняющая партия GUI-глифов.

Первый build_guiglyphs.py закрыл 57 символов, но плагин с тех пор оброс новыми.
Эти 24 сейчас рисует ванильный unifont: клиент 1.21.x везёт unifont_all_no_pua,
он покрывает планы 0-15, так что квадратов нет — но чёрно-белые контуры юнифонта
стоят рядом с иконками пака и стилистически выпадают.

Отличия от первого скрипта:
  * якорь вставки — не ttf-провайдер (его в default.json давно нет, старый скрипт
    на нём падал бы), а завершающая ссылка minecraft:include/default;
  * удаляются только записи ЭТИХ символов, чужие nr_gui_ не трогаются.

Порядок провайдеров = порядок приоритета, первый выигрывает: поэтому вставляем
перед include/default, иначе юнифонт перебил бы наши картинки.
"""
import os, json
from PIL import Image, ImageDraw, ImageFont
from fontTools import ttLib

ROOT = os.path.dirname(os.path.abspath(__file__))
MC = os.path.join(ROOT, "pack", "assets", "minecraft")
FONTTEX = os.path.join(MC, "textures", "font")
DEFAULT = os.path.join(MC, "font", "default.json")

SEGUISYM = r"C:\Windows\Fonts\seguisym.ttf"
SEGUIEMJ = r"C:\Windows\Fonts\seguiemj.ttf"
sym_cmap = set(ttLib.TTFont(SEGUISYM).getBestCmap().keys())
emj_cmap = set(ttLib.TTFont(SEGUIEMJ).getBestCmap().keys())

# Имена не должны сталкиваться с уже занятыми: ⚒ это hammerpick, а 🔨 — hammer;
# ☠ это skull, а 💀 — skullbone; ♛ это nr_crown, а 👑 — crownfull.
GUI = [
    ("temple",     0x1F3DB),  # чудеса света, ратуша, война
    ("bomb",       0x1F4A3),  # TNT Run
    ("globe",      0x1F310),  # /menu — карта мира
    ("clipboard",  0x1F4CB),  # скупщик
    ("trident",    0x1F531),  # боссы
    ("ballot",     0x1F5F3),  # голосование
    ("honey",      0x1F36F),  # пасека
    ("shield",     0x1F6E1),  # магазин, Discord
    ("worldmap",   0x1F5FA),  # Королевская битва, /menu
    ("waterwave",  0x1F30A),  # босс-волна
    ("turtle",     0x1F422),  # квест черепашки
    ("skullbone",  0x1F480),  # руины города
    ("beer",       0x1F37A),  # пивоварня
    ("eye",        0x1F441),  # BuildBattle — режим зрителя
    ("hammer",     0x1F528),  # BuildBattle — стройка
    ("calendar",   0x1F4C5),  # расписание ивентов
    ("dove",       0x1F54A),  # час PvP выключен
    ("crownfull",  0x1F451),  # столица на карте
    ("picture",    0x1F5BC),  # картины
    ("spider",     0x1F577),  # квест
    ("brick",      0x1F9F1),  # магазин — стройматериалы
    ("meat",       0x1F356),  # магазин — еда
    ("heartbreak", 0x1F494),  # развод
    ("link",       0x1F517),  # привязка аккаунта
]

CANVAS = 144


def render_mono(cp):
    """Чёткий белый монохром из Segoe UI Symbol."""
    f = ImageFont.truetype(SEGUISYM, 116)
    im = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ch = chr(cp)
    bb = d.textbbox((0, 0), ch, font=f)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    d.text(((CANVAS - w) // 2 - bb[0], (CANVAS - h) // 2 - bb[1]), ch, font=f, fill=(255, 255, 255, 255))
    return im


def render_silhouette(cp):
    """Белый силуэт из цветного Segoe UI Emoji (альфа→белый)."""
    f = ImageFont.truetype(SEGUIEMJ, 109)
    im = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ch = chr(cp)
    bb = d.textbbox((0, 0), ch, font=f, embedded_color=True)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    d.text(((CANVAS - w) // 2 - bb[0], (CANVAS - h) // 2 - bb[1]), ch, font=f, embedded_color=True)
    alpha = im.split()[3].point(lambda a: 255 if a > 64 else 0)
    out = Image.new("RGBA", im.size, (255, 255, 255, 0))
    out.putalpha(alpha)
    return out


def finalize(im, size=16):
    bbx = im.getbbox()
    if bbx:
        im = im.crop(bbx)
    side = max(max(im.size), 1)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.alpha_composite(im, ((side - im.width) // 2, (side - im.height) // 2))
    return sq.resize((size, size), Image.LANCZOS)


done, previews = [], []
for name, cp in GUI:
    src = "sym" if cp in sym_cmap else ("emj" if cp in emj_cmap else None)
    if src is None:
        print("нет глифа ни в одном шрифте:", name, hex(cp))
        continue
    im = finalize(render_mono(cp) if src == "sym" else render_silhouette(cp))
    if not im.getbbox():
        print("пустой рендер:", name, hex(cp))
        continue
    im.save(os.path.join(FONTTEX, f"nr_gui_{name}.png"))
    done.append((name, cp))
    previews.append((name, cp, src, im))

# ---- default.json ----
data = json.load(open(DEFAULT, encoding="utf-8"))
mine = {chr(cp) for _, cp in done}
provs = [p for p in data["providers"]
         if not (p.get("type") == "bitmap" and mine.intersection("".join(p.get("chars") or [])))]
anchor = next(i for i, p in enumerate(provs)
              if p.get("type") == "reference" and p.get("id") == "minecraft:include/default")
provs[anchor:anchor] = [{"type": "bitmap", "file": f"minecraft:font/nr_gui_{name}.png",
                         "ascent": 8, "height": 10, "chars": [chr(cp)]} for name, cp in done]
data["providers"] = provs
json.dump(data, open(DEFAULT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---- превью: крем на фирменном тёмном, как это увидят в игре ----
pad, cell = 12, 64
cols = 8
rows = (len(previews) + cols - 1) // cols
sheet = Image.new("RGBA", (cols * (cell + pad) + pad, rows * (cell + pad + 12) + pad), (28, 22, 38, 255))
for i, (name, cp, src, im) in enumerate(previews):
    g = im.resize((cell, cell), Image.NEAREST)
    tint = Image.new("RGBA", g.size, (0, 0, 0, 0))
    tint.paste((247, 250, 219, 255), (0, 0), g.split()[3])
    tint.putalpha(g.split()[3])
    r, c = divmod(i, cols)
    sheet.alpha_composite(tint, (pad + c * (cell + pad), pad + r * (cell + pad + 12)))
sheet.save(os.path.join(ROOT, "logo", "_guiglyphs2_preview.png"))

print(f"готово: {len(done)}/{len(GUI)}")
print("из Segoe UI Symbol:", [n for n, cp, s, _ in previews if s == "sym"])
print("силуэт из Segoe UI Emoji:", [n for n, cp, s, _ in previews if s == "emj"])
print("провайдеров в default.json:", len(provs))
