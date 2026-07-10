# -*- coding: utf-8 -*-
"""GUI-оверлей аукциона: negative-space шрифт + бесшовная панель + цифры,
чтобы рисовать «X/Y» ПРЯМО поверх нижнего ряда (слоты 48-50) через ЗАГОЛОВОК окна.
Вертикаль задаётся ascent'ом (ниже) — калибруется по скрину из игры."""
import os, json
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
MC = os.path.join(ROOT, "pack", "assets", "minecraft")
FONT = os.path.join(MC, "font"); FTEX = os.path.join(MC, "textures", "font")
os.makedirs(FTEX, exist_ok=True)

# --- КАЛИБРОВКА вертикали (13 - ascent = верх глифа по Y в окне) ---
BAR_ASCENT = -94   # панель: верх на ~107 (полностью накрыть нижний ряд слотов)
DIG_ASCENT = -97   # цифры: по центру панели
BAR_H = 18         # выше слота (18px), чтобы закрыть его целиком
DIG_H = 12

# --- 1) панель ПОЛНОСТЬЮ накрывает 3 слота (56x18), почти квадратные углы ---
PW, PH, SS = 56, BAR_H, 8
img = Image.new("RGBA", (PW*SS, PH*SS), (0,0,0,0)); d = ImageDraw.Draw(img)
rad = int(PH*SS*0.16)
# сплошная тёмная подложка на все углы (полное перекрытие слотов) + рамка сверху
d.rectangle([0, int(SS*0.4), PW*SS, PH*SS-int(SS*0.4)], fill=(26,21,36,255))
d.rounded_rectangle([SS, SS, PW*SS-SS, PH*SS-SS], radius=rad, fill=(36,30,49,255), outline=(160,136,200,255), width=int(SS*1.5))
ins = int(PH*SS*0.18)
d.rounded_rectangle([SS+ins, SS+ins, PW*SS-SS-ins, PH*SS-SS-ins], radius=int(rad*0.6), fill=(14,11,20,255), outline=(74,61,98,255), width=max(1, int(SS*0.7)))
img.resize((PW, PH), Image.LANCZOS).save(os.path.join(FTEX, "nr_ahbar.png"))
BAR_ADV = PW  # ширина панели (для сдвигов в Java)

# --- 2) цифры 0-9 и «/» — крупные, БЕЗ обрезки (авто-фит в ячейку) ---
try: FPATH = os.path.join(ROOT, "_mont800.ttf"); ImageFont.truetype(FPATH, 10)
except Exception: FPATH = r"C:\Windows\Fonts\segoeuib.ttf"
CELL = 32
chars = "0123456789/"
# подобрать размер так, чтобы самый высокий глиф занимал ~78% ячейки
fsz = CELL
while fsz > 6:
    f = ImageFont.truetype(FPATH, fsz)
    hmax = max((ImageDraw.Draw(Image.new("RGBA",(1,1))).textbbox((0,0),c,font=f)[3]
                - ImageDraw.Draw(Image.new("RGBA",(1,1))).textbbox((0,0),c,font=f)[1]) for c in chars)
    if hmax <= CELL*0.80: break
    fsz -= 1
strip = Image.new("RGBA", (CELL*len(chars), CELL), (0,0,0,0)); sd = ImageDraw.Draw(strip)
for i, ch in enumerate(chars):
    bb = sd.textbbox((0,0), ch, font=f); w, h = bb[2]-bb[0], bb[3]-bb[1]
    sd.text((i*CELL + (CELL-w)//2 - bb[0], (CELL-h)//2 - bb[1]), ch, font=f, fill=(255,255,255,255))
strip.save(os.path.join(FTEX, "nr_ahdig.png"))
print("digit font size:", fsz)

# --- 3) negative-space провайдер: PUA-символы -> сдвиг в пикселях ---
MAG = [1,2,4,8,16,32,64,128,256]
adv = {}
for i, m in enumerate(MAG):
    adv[chr(0xF810+i)] = m       # +m
    adv[chr(0xF800+i)] = -m      # -m
space_prov = {"type": "space", "advances": adv}
bar_prov = {"type": "bitmap", "file": "minecraft:font/nr_ahbar.png", "ascent": BAR_ASCENT, "height": BAR_H, "chars": [chr(0xF8A0)]}
dig_chars = "".join(chr(0xF8B0+i) for i in range(len(chars)))  # F8B0=0 … F8B9=9, F8BA=/
dig_prov = {"type": "bitmap", "file": "minecraft:font/nr_ahdig.png", "ascent": DIG_ASCENT, "height": DIG_H, "chars": [dig_chars]}

DEFAULT = os.path.join(FONT, "default.json")
data = json.load(open(DEFAULT, encoding="utf-8"))
provs = [p for p in data["providers"] if p.get("file","") not in ("minecraft:font/nr_ahbar.png","minecraft:font/nr_ahdig.png") and not (p.get("type")=="space" and any(c in p.get("advances",{}) for c in (chr(0xF810),)))]
# вставить перед первым ttf
ti = next((i for i,p in enumerate(provs) if p.get("type")=="ttf"), len(provs))
provs[ti:ti] = [space_prov, bar_prov, dig_prov]
data["providers"] = provs
json.dump(data, open(DEFAULT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("ahfont ok. BAR_ADV(px)=", BAR_ADV, "BAR_ASCENT=", BAR_ASCENT, "DIG_ASCENT=", DIG_ASCENT)
print("space chars: +m F810.., -m F800.. ; bar=U+F8A0 ; digits F8B0-F8BA(0..9,/)")
