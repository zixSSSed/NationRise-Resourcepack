# -*- coding: utf-8 -*-
import os, urllib.request, ssl
from fontTools import ttLib
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.path.join(ROOT, "pack", "assets", "minecraft", "font")
LOGODIR = os.path.join(ROOT, "logo")
os.makedirs(FONTDIR, exist_ok=True)

# Rubik — OFL, полное покрытие кириллицы/латиницы/цифр
URL = "https://github.com/google/fonts/raw/main/ofl/rubik/Rubik%5Bwght%5D.ttf"
raw = os.path.join(ROOT, "_rubik_var.ttf")

if not os.path.exists(raw):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=60) as r, open(raw, "wb") as f:
        f.write(r.read())
print("downloaded", os.path.getsize(raw), "bytes")

def make(weight, out):
    f = ttLib.TTFont(raw)
    instantiateVariableFont(f, {"wght": weight}, inplace=True)
    # переименуем семейство для аккуратности
    f.save(out)
    cmap = f.getBestCmap()
    sample = "Привет Москва — NationRise 123 ёЁ№"
    missing = [c for c in sample if ord(c) not in cmap and c != " "]
    print(f"  {os.path.basename(out)} wght={weight}: cyrillic_ok={not missing} missing={missing}")
    return cmap

print("instancing...")
cmap = make(500, os.path.join(FONTDIR, "nationrise.ttf"))          # тело (чат/скорборд)
make(800, os.path.join(LOGODIR, "nationrise-logo.ttf"))            # логотип (вордмарк)
# контрольные кириллические буквы
need = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
print("full cyrillic coverage:", all(ord(c) in cmap for c in need))
print("DONE")
