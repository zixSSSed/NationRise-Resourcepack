# -*- coding: utf-8 -*-
import os, shutil
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
INC = os.path.join(ROOT, "incoming")
PACK = os.path.join(ROOT, "pack", "assets", "minecraft")
ITEMTEX = os.path.join(PACK, "textures", "item")
FONTTEX = os.path.join(PACK, "textures", "font")
os.makedirs(ITEMTEX, exist_ok=True)
os.makedirs(FONTTEX, exist_ok=True)

# --- удочки -> текстуры предметов ---
shutil.copyfile(os.path.join(INC, "fishing rod nether.png"), os.path.join(ITEMTEX, "nr_rod_nether.png"))
shutil.copyfile(os.path.join(INC, "fishing rod end.png"),    os.path.join(ITEMTEX, "nr_rod_end.png"))

# превью удочек (крупно)
rn = Image.open(os.path.join(INC, "fishing rod nether.png")).convert("RGBA")
re = Image.open(os.path.join(INC, "fishing rod end.png")).convert("RGBA")
sc = 14
prev = Image.new("RGBA", (16 * sc * 2 + 60, 16 * sc + 40), (21, 15, 31, 255))
prev.alpha_composite(rn.resize((16 * sc, 16 * sc), Image.NEAREST), (20, 20))
prev.alpha_composite(re.resize((16 * sc, 16 * sc), Image.NEAREST), (40 + 16 * sc, 20))
prev.save(os.path.join(ROOT, "logo", "_rods_preview.png"))

# --- логотип -> глиф заголовка скорборда ---
logo = Image.open(os.path.join(INC, "Logo.png")).convert("RGBA")
bb = logo.getbbox()
trim = logo.crop(bb)
trim.save(os.path.join(FONTTEX, "nr_logo.png"))
# превью на тёмном
lp = Image.new("RGBA", (trim.width + 40, trim.height + 40), (21, 15, 31, 255))
lp.alpha_composite(trim, (20, 20))
lp.save(os.path.join(ROOT, "logo", "_logo_title_preview.png"))

print("rods ->", os.listdir(ITEMTEX))
print("logo glyph:", trim.size, "-> textures/font/nr_logo.png")
