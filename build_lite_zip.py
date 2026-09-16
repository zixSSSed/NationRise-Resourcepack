# -*- coding: utf-8 -*-
"""
Lite-вариант пака: полный ZIP минус тяжёлые кастомные глифы.

Читает готовый NationRise-Resourcepack.zip и копирует записи байт-в-байт, поэтому
lite детерминирован относительно full. Модели предметов (CMD: скины, миньоны,
инструменты, головы) остаются.

Что изменилось
--------------
Раньше отсюда вылетали ВСЕ шрифты вместе с default.json. Пока плашки были обычным
текстом, это ничего не ломало. Теперь плашка — это фон, значок и собственный шрифт из
пака, и на lite вместо неё игрок видел бы сплошную стену квадратиков: и рамку, и
корону, и каждую букву подписи.

Поэтому lite оставляет ровно плашечную группу: боковинки, полосы фона, значки, атлас
шрифта 5×5 и пробелы. Это около трёх килобайт — против почти четырёхсот, которые
занимают остальные глифы. Сам default.json пересобирается: в нём остаются только эти
провайдеры и ссылка на ванильный шрифт. Провайдер с отсутствующей текстурой клиент
ругает в лог, поэтому просто «оставить json как есть» было нельзя.
"""
import os, zipfile, hashlib, json

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "NationRise-Resourcepack.zip")
OUT = os.path.join(ROOT, "NationRise-Resourcepack-lite.zip")

FONT_DIRS = (
    "assets/minecraft/font/",
    "assets/minecraft/textures/font/",
    "assets/nationrise/font/",
    "assets/nationrise/textures/font/",
)
KEEP_PREFIX = ("nr_pill_", "nr_plq_")          # что из шрифтов остаётся в lite
DEFAULT_JSON = "assets/minecraft/font/default.json"


def keep_texture(name):
    base = name.rsplit("/", 1)[-1]
    return any(base.startswith(p) for p in KEEP_PREFIX)


def keep_provider(p):
    """Пробелы и ссылка на ванильный шрифт нужны всегда; из картинок — только плашечные."""
    t = p.get("type")
    if t in ("space", "reference"):
        return True
    if t == "bitmap":
        return keep_texture(str(p.get("file", "")))
    return False


kept = dropped = 0
with zipfile.ZipFile(SRC) as src, zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as out:
    for info in src.infolist():
        name = info.filename
        if name == DEFAULT_JSON:
            data = json.loads(src.read(name).decode("utf-8"))
            data["providers"] = [p for p in data["providers"] if keep_provider(p)]
            out.writestr(info, json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
            kept += 1
            print("default.json: провайдеров оставлено", len(data["providers"]))
            continue
        if any(name.startswith(d) for d in FONT_DIRS):
            if keep_texture(name):
                out.writestr(info, src.read(name))
                kept += 1
            else:
                dropped += 1
            continue
        out.writestr(info, src.read(name))
        kept += 1

sha1 = hashlib.sha1(open(OUT, "rb").read()).hexdigest()
print("lite zip:", OUT)
print("size:", os.path.getsize(OUT), "bytes")
print("kept:", kept, "dropped(fonts):", dropped)
print("sha1:", sha1)
