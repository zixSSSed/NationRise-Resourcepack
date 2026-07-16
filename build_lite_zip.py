# -*- coding: utf-8 -*-
"""Lite-вариант пака: полный ZIP минус ВСЕ шрифты (для клиентов, которым тяжело/конфликтно
с кастомными глифами). Модели предметов (CMD: скины, миньоны, инструменты, головы) остаются.
Читает готовый NationRise-Resourcepack.zip и копирует записи как есть (байт-в-байт),
кроме шрифтовых путей — поэтому lite детерминирован относительно full."""
import os, zipfile, hashlib

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "NationRise-Resourcepack.zip")
OUT = os.path.join(ROOT, "NationRise-Resourcepack-lite.zip")

STRIP = (
    "assets/minecraft/font/",
    "assets/minecraft/textures/font/",
    "assets/nationrise/font/",
    "assets/nationrise/textures/font/",
)

kept, dropped = 0, 0
with zipfile.ZipFile(SRC) as src, zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as out:
    for info in src.infolist():
        if any(info.filename.startswith(p) for p in STRIP):
            dropped += 1
            continue
        out.writestr(info, src.read(info.filename))
        kept += 1

sha1 = hashlib.sha1(open(OUT, "rb").read()).hexdigest()
print("lite zip:", OUT)
print("size:", os.path.getsize(OUT), "bytes")
print("kept:", kept, "dropped(fonts):", dropped)
print("sha1:", sha1)
