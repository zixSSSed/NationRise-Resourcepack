# -*- coding: utf-8 -*-
import os, urllib.request, ssl, shutil
from fontTools import ttLib
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.path.join(ROOT, "pack", "assets", "minecraft", "font")
LOGODIR = os.path.join(ROOT, "logo")

SRC = {
    "Inter":      "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
    "Montserrat": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf",
}

def dl(url, path):
    if os.path.exists(path):
        return
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=90) as r, open(path, "wb") as f:
        f.write(r.read())

def instance(src, axes, out):
    f = ttLib.TTFont(src)
    instantiateVariableFont(f, axes, inplace=True)
    f.save(out)

raw_inter = os.path.join(ROOT, "_inter_var.ttf")
raw_mont = os.path.join(ROOT, "_mont_var.ttf")
dl(SRC["Inter"], raw_inter)
dl(SRC["Montserrat"], raw_mont)

inter500 = os.path.join(ROOT, "_inter500.ttf")
mont500 = os.path.join(ROOT, "_mont500.ttf")
instance(raw_inter, {"wght": 500, "opsz": 14}, inter500)
instance(raw_mont, {"wght": 500}, mont500)
print("instanced Inter + Montserrat (wght 500)")

# текущий шрифт пака (Rubik) — для сравнения
rubik = os.path.join(FONTDIR, "nationrise.ttf")

# ---- сравнительный рендер (приближённо «как в скорборде») ----
PUR = (140, 91, 232); CRE = (247, 250, 219); LIL = (201, 184, 242); BG = (15, 10, 24)
lines = [("NATIONRISE", CRE), ("Игрок: Steve", PUR), ("Баланс: 12 540", PUR),
         ("Кристаллы: 30", PUR), ("Город: Империум (ур.4)", PUR)]
cands = [("Rubik (сейчас)", rubik), ("Inter", inter500), ("Montserrat", mont500)]

colw, rowh, pad = 360, 34, 22
size_small = 17
img = Image.new("RGB", (colw * 3, rowh * (len(lines) + 1) + pad * 2), BG)
d = ImageDraw.Draw(img)
for ci, (label, path) in enumerate(cands):
    x0 = ci * colw + pad
    fhead = ImageFont.truetype(path, 22)
    d.text((x0, pad), label, font=fhead, fill=(150, 130, 200))
    fbody = ImageFont.truetype(path, size_small)
    for li, (txt, col) in enumerate(lines):
        d.text((x0, pad + rowh + li * rowh), txt, font=fbody, fill=col)
    if ci:
        d.line([(ci * colw, 0), (ci * colw, img.height)], fill=(40, 30, 55), width=1)
out = os.path.join(LOGODIR, "_font_compare.png")
# 2x для чёткости показа
img.resize((img.width * 2, img.height * 2), Image.NEAREST).save(out)
print("comparison ->", out)

# по умолчанию ставим Inter в пак (легко поменять)
shutil.copyfile(inter500, os.path.join(FONTDIR, "nationrise.ttf"))
print("pack font set to Inter (provisional)")
