# -*- coding: utf-8 -*-
"""Перетекстуривание фона GUI-сундука (generic_54.png) в единое объёмное бренд-полотно.
Берём ВАНИЛЬНУЮ текстуру и перекрашиваем по яркости через бренд-рамп (фиолет NationRise) —
структура (слоты, бевелы, объём) сохраняется 1:1, слоты НЕ съезжают. + лёгкий градиент глубины.
Затем рендерим точный мокап /t menu (фон + кнопки-иконки в позициях слотов)."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
MC = os.path.join(ROOT, "pack", "assets", "minecraft")
GUIDIR = os.path.join(MC, "textures", "gui", "container")
ITEMTEX = os.path.join(MC, "textures", "item")
os.makedirs(GUIDIR, exist_ok=True)
VAN = os.path.join(ROOT, "vanilla_gui", "generic_54.png")

# --- бренд-рамп по яркости (тёмные тона → глубокий фиолет, светлые → лавандовый хайлайт) ---
STOPS = [(0,(18,13,28)), (55,(34,24,54)), (110,(58,42,96)), (170,(104,82,156)),
         (215,(150,126,196)), (245,(190,170,224)), (255,(214,200,240))]
def ramp(l):
    for i in range(len(STOPS)-1):
        l0,c0 = STOPS[i]; l1,c1 = STOPS[i+1]
        if l0 <= l <= l1:
            t = (l-l0)/max(1,(l1-l0))
            return tuple(int(c0[k]+(c1[k]-c0[k])*t) for k in range(3))
    return STOPS[-1][1]
LUT = [ramp(l) for l in range(256)]

van = Image.open(VAN).convert("RGBA")
W, H = van.size
vp = van.load()
out = Image.new("RGBA", (W, H), (0,0,0,0)); op = out.load()
PANEL_W, PANEL_H = 176, 222   # рабочая область панели (для градиента глубины)
for y in range(H):
    gy = max(0.0, min(1.0, y/PANEL_H))           # 0 верх → 1 низ
    depth = 1.0 - 0.14*gy                          # лёгкое затемнение книзу для объёма
    for x in range(W):
        r,g,b,a = vp[x,y]
        if a == 0: continue
        l = int(0.299*r + 0.587*g + 0.114*b)
        nr,ng,nb = LUT[l]
        op[x,y] = (int(nr*depth), int(ng*depth), int(nb*depth), a)

# тонкая тёплая кремовая «рим-линия» по верхней кромке панели (премиум-акцент)
od = ImageDraw.Draw(out)
od.line([(7,4),(PANEL_W-8,4)], fill=(247,250,219,90), width=1)
out.save(os.path.join(GUIDIR, "generic_54.png"))
print("themed generic_54.png saved")

# ================== МОКАП /t menu (45 слотов, 5 рядов) ==================
# позиции контента слота 16x16: x=8+18*col, y=18+18*row
def slot_xy(idx):
    return 8 + 18*(idx % 9), 18 + 18*(idx // 9)

# верхняя часть окна для 5-рядного меню: header(17) + 5*18 = 107px, ширина 176
menu_h = 17 + 5*18
panel = out.crop((0, 0, PANEL_W, menu_h)).copy()

# иконки openMain: slot -> файл
ICONS = {4:"nr_tm_info",10:"nr_tm_spawn",11:"nr_tm_bank",12:"nr_tm_storage",13:"nr_tm_residents",
         14:"nr_tm_jobs",15:"nr_tm_map",16:"nr_tm_switches",20:"nr_tm_level",21:"nr_tm_buildings",
         22:"nr_tm_ideology",23:"nr_tm_outposts",24:"nr_tm_sanctions",25:"nr_tm_religion",40:"nr_tm_close"}
for idx, fn in ICONS.items():
    p = os.path.join(ITEMTEX, fn+".png")
    if not os.path.exists(p): continue
    ic = Image.open(p).convert("RGBA").resize((16,16), Image.LANCZOS)
    x,y = slot_xy(idx)
    if y+16 <= menu_h:
        panel.alpha_composite(ic, (x,y))

# подпись-заголовок (как в игре) + увеличить ×4 для просмотра
try: f = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 8)
except: f = ImageFont.load_default()
ImageDraw.Draw(panel).text((8,5), "Город: zov", font=f, fill=(230,222,240,255))
mock = panel.resize((PANEL_W*4, menu_h*4), Image.NEAREST)
bg = Image.new("RGBA", (mock.width+40, mock.height+40), (24,18,32,255))
bg.alpha_composite(mock, (20,20))
bg.save(os.path.join(ROOT, "logo", "_gui_mockup.png"))
print("mockup saved:", menu_h, "px tall (×4)")
