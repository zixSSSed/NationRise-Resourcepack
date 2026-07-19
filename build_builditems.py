# -*- coding: utf-8 -*-
"""Phase 2: кастомные иконки-предметы для GUI (здания/категории /t builds + вкладки
редкостей в журнале рыб). Носитель — PAPER + CustomModelData (60101..60312),
переопределяется ТОЛЬКО items/paper.json (реальная бумага без CMD → ваниль).
Стиль: цветная плитка (цвет берётся из § кода зданий/категорий) + белый символ."""
import os, json, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from fontTools import ttLib

ROOT = os.path.dirname(os.path.abspath(__file__))
MC = os.path.join(ROOT, "pack", "assets", "minecraft")
TEX = os.path.join(MC, "textures", "item")
MODELS = os.path.join(MC, "models", "item")
ITEMS = os.path.join(MC, "items")
for d in (TEX, MODELS, ITEMS): os.makedirs(d, exist_ok=True)

SEGUISYM = r"C:\Windows\Fonts\seguisym.ttf"; SEGUIEMJ = r"C:\Windows\Fonts\seguiemj.ttf"
sym_cmap = set(ttLib.TTFont(SEGUISYM).getBestCmap())
emj_cmap = set(ttLib.TTFont(SEGUIEMJ).getBestCmap())

SECT = {  # § код -> RGB (насыщенные для плиток)
 '0':(45,45,52),'1':(50,70,170),'2':(50,160,70),'3':(50,165,175),'4':(190,55,55),
 '5':(150,75,195),'6':(255,180,60),'7':(150,150,162),'8':(95,95,108),'9':(80,130,240),
 'a':(110,210,95),'b':(95,205,238),'c':(236,90,90),'d':(222,120,236),'e':(245,216,92),'f':(225,225,232)}
SECT.update({
 'S':(59,130,196),   # steel blue
 'G':(224,169,60),   # warm gold
 'E':(60,167,106),   # emerald
 'R':(207,78,78),    # carmine
 'N':(95,105,119),   # neutral slate
})
APPROVED_CODE = {
 '0':'N','1':'S','2':'E','3':'S','4':'R','5':'S','6':'G','7':'N','8':'N',
 '9':'S','a':'E','b':'S','c':'R','d':'S','e':'G','f':'N',
}

def sym_white(cp, S):
    big = max(48, S*7)
    if cp in sym_cmap:
        f = ImageFont.truetype(SEGUISYM, int(big*0.82)); im = Image.new("RGBA",(big,big),(0,0,0,0)); d = ImageDraw.Draw(im)
        bb = d.textbbox((0,0),chr(cp),font=f); w,h = bb[2]-bb[0],bb[3]-bb[1]
        d.text(((big-w)//2-bb[0],(big-h)//2-bb[1]),chr(cp),font=f,fill=(255,255,255,255))
    elif cp in emj_cmap:
        f = ImageFont.truetype(SEGUIEMJ, int(big*0.78)); im = Image.new("RGBA",(big,big),(0,0,0,0)); d = ImageDraw.Draw(im)
        bb = d.textbbox((0,0),chr(cp),font=f,embedded_color=True); w,h = bb[2]-bb[0],bb[3]-bb[1]
        d.text(((big-w)//2-bb[0],(big-h)//2-bb[1]),chr(cp),font=f,embedded_color=True)
        a = im.split()[3].point(lambda v:255 if v>72 else 0); im = Image.new("RGBA",(big,big),(255,255,255,0)); im.putalpha(a)
    else:
        return None
    bx = im.getbbox()
    if not bx: return None
    im = im.crop(bx); side = max(im.size)
    sq = Image.new("RGBA",(side,side),(0,0,0,0)); sq.alpha_composite(im,((side-im.width)//2,(side-im.height)//2))
    return sq.resize((S,S),Image.LANCZOS)

def _odd(n): n=int(n); return n if n%2 else n+1
def _mul(c,f): return tuple(min(255,max(0,int(x*f))) for x in c)
def _vgrad(top,bot,w,h):
    g=Image.new("RGB",(1,max(1,h)))
    for j in range(max(1,h)):
        t=j/max(1,h-1); g.putpixel((0,j),tuple(int(top[k]+(bot[k]-top[k])*t) for k in range(3)))
    return g.resize((max(1,w),max(1,h))).convert("RGBA")
def _rmask(w,h,rad):
    mk=Image.new("L",(w,h),0); ImageDraw.Draw(mk).rounded_rectangle([0,0,w-1,h-1],radius=max(1,rad),fill=255); return mk

def tile(code, cp, size=64, ss=3):
    """Кнопка: тёмная база + приподнятое глянцевое лицо (3D-борт снизу) + белый символ с контуром."""
    c=SECT[code]; S=size*ss
    img=Image.new("RGBA",(S,S),(0,0,0,0)); d=ImageDraw.Draw(img)
    rad=int(S*0.24); m=int(S*0.055); lip=int(S*0.10)
    # 1) тёмная база на всю высоту — нижний «борт» кнопки (объём)
    d.rounded_rectangle([m,m,S-m,S-m],radius=rad,fill=_mul(c,0.30)+(255,))
    # 2) лицо кнопки, приподнято на lip (внизу остаётся тёмный борт)
    fx,fy,fw,fh=m,m,S-2*m,S-2*m-lip
    d.rounded_rectangle([fx,fy,fx+fw,fy+fh],radius=rad,fill=_mul(c,1.62)+(255,))      # глянцевый светлый кант
    ins=max(2,int(S*0.024)); gw,gh=fw-2*ins,fh-2*ins
    img.paste(_vgrad(_mul(c,1.30),_mul(c,0.92),gw,gh),(fx+ins,fy+ins),_rmask(gw,gh,rad-ins))
    # 3) внешний тёмный кант — отделяет кнопку от фона
    d.rounded_rectangle([m,m,S-m,S-m],radius=rad,outline=_mul(c,0.16)+(255,),width=max(2,int(S*0.03)))
    # 4) символ + тёмный контур по центру ЛИЦА (а не всей плитки)
    g=sym_white(cp,int(S*0.52))
    if g is None: raise ValueError("no glyph "+hex(cp))
    gx=(S-g.width)//2; gy=fy+(fh-g.height)//2
    ga=g.split()[3]
    out_a=ga.filter(ImageFilter.MaxFilter(_odd(g.width*0.07)))
    outline=Image.new("RGBA",g.size,(0,0,0,0)); outline.paste((20,15,30,255),(0,0),out_a); outline.putalpha(out_a)
    img.alpha_composite(outline,(gx,gy)); img.alpha_composite(g,(gx,gy))
    out=img.resize((size,size),Image.LANCZOS)
    return out.filter(ImageFilter.UnsharpMask(radius=1.0,percent=85,threshold=0))

def filler(size=64, ss=3):
    """Фон-панель меню (замена чёрному стеклу): тёмный бренд-слейт, ненавязчиво."""
    S=size*ss; img=Image.new("RGBA",(S,S),(0,0,0,0)); d=ImageDraw.Draw(img)
    rad=int(S*0.15); m=int(S*0.035)
    d.rounded_rectangle([m,m,S-m,S-m],radius=rad,fill=(32,37,46,255))
    d.rounded_rectangle([m,m,S-m,S-m],radius=rad,outline=(95,105,119,255),width=max(2,int(S*0.025)))
    d.line([(m+rad,m+int(S*0.07)),(S-m-rad,m+int(S*0.07))],fill=(139,149,163,150),width=max(1,int(S*0.02)))
    return img.resize((size,size),Image.LANCZOS)

def shop_token(kind, size=64, ss=4):
    """Approved-palette floating icons for the three large /shop plates."""
    S=size*ss
    img=Image.new("RGBA",(S,S),(0,0,0,0))
    d=ImageDraw.Draw(img)
    graphite=(32,37,46,255)
    steel=(59,130,196,255)
    gold=(224,169,60,255)
    emerald=(60,167,106,255)
    carmine=(207,78,78,255)
    white=(242,245,248,255)
    outline=max(3,int(S*0.035))

    if kind == "money":
        # Three offset coins and a compact ingot: legible at the 16px GUI size.
        for x,y in ((0.19,0.50),(0.34,0.57),(0.49,0.48)):
            box=[int(S*x),int(S*y),int(S*(x+0.31)),int(S*(y+0.19))]
            d.ellipse(box,fill=graphite)
            inset=outline
            d.ellipse([box[0]+inset,box[1]+inset,box[2]-inset,box[3]-inset],
                      fill=gold,outline=white,width=max(2,outline//2))
        d.polygon(
            [(int(S*.30),int(S*.31)),(int(S*.66),int(S*.31)),
             (int(S*.77),int(S*.48)),(int(S*.19),int(S*.48))],
            fill=graphite,
        )
        d.polygon(
            [(int(S*.33),int(S*.34)),(int(S*.64),int(S*.34)),
             (int(S*.70),int(S*.44)),(int(S*.27),int(S*.44))],
            fill=gold,
        )
        d.line([(int(S*.38),int(S*.37)),(int(S*.59),int(S*.37))],
               fill=white,width=max(2,outline//2))
    elif kind == "crystal":
        pts=[(int(S*.50),int(S*.12)),(int(S*.78),int(S*.39)),
             (int(S*.62),int(S*.83)),(int(S*.38),int(S*.83)),
             (int(S*.22),int(S*.39))]
        d.polygon(pts,fill=graphite)
        inner=[(int(S*.50),int(S*.18)),(int(S*.72),int(S*.41)),
               (int(S*.58),int(S*.77)),(int(S*.42),int(S*.77)),
               (int(S*.28),int(S*.41))]
        d.polygon(inner,fill=steel,outline=white,width=outline)
        d.polygon([(int(S*.50),int(S*.20)),(int(S*.50),int(S*.74)),
                   (int(S*.30),int(S*.41))],fill=(90,168,214,255))
        d.line([(int(S*.31),int(S*.41)),(int(S*.69),int(S*.41))],
               fill=white,width=max(2,outline//2))
        d.ellipse([int(S*.43),int(S*.34),int(S*.55),int(S*.46)],fill=white)
    elif kind == "war":
        # Steel shield with carmine field and two bright crossed blades.
        shield=[(int(S*.23),int(S*.18)),(int(S*.77),int(S*.18)),
                (int(S*.72),int(S*.62)),(int(S*.50),int(S*.86)),
                (int(S*.28),int(S*.62))]
        d.polygon(shield,fill=graphite)
        inset=[(int(S*.29),int(S*.24)),(int(S*.71),int(S*.24)),
               (int(S*.66),int(S*.58)),(int(S*.50),int(S*.77)),
               (int(S*.34),int(S*.58))]
        d.polygon(inset,fill=carmine,outline=white,width=outline)
        for flip in (-1,1):
            x0=int(S*(.34 if flip<0 else .66))
            x1=int(S*(.66 if flip<0 else .34))
            d.line([(x0,int(S*.65)),(x1,int(S*.31))],
                   fill=graphite,width=outline*3)
            d.line([(x0,int(S*.65)),(x1,int(S*.31))],
                   fill=white,width=outline)
        d.rectangle([int(S*.28),int(S*.62),int(S*.42),int(S*.69)],fill=gold)
        d.rectangle([int(S*.58),int(S*.62),int(S*.72),int(S*.69)],fill=gold)
    else:
        raise ValueError("unknown shop token: "+kind)

    return img.resize((size,size),Image.LANCZOS).filter(
        ImageFilter.UnsharpMask(radius=1.0,percent=95,threshold=0)
    )

def rtp_pin(name, size=64, ss=4):
    """Large gold teleport badges inspired by the approved pixel-map reference."""
    S=size*ss
    img=Image.new("RGBA",(S,S),(0,0,0,0))
    d=ImageDraw.Draw(img)
    graphite=(32,37,46,255)
    steel=(59,130,196,255)
    gold=(224,169,60,255)
    emerald=(60,167,106,255)
    carmine=(207,78,78,255)
    white=(242,245,248,255)
    outline=max(3,int(S*.035))

    if name == "random":
        d.ellipse([int(S*.13),int(S*.13),int(S*.87),int(S*.87)],
                  fill=graphite,outline=emerald,width=outline*2)
        d.ellipse([int(S*.24),int(S*.24),int(S*.76),int(S*.76)],
                  fill=(18,23,32,255),outline=white,width=outline)
        d.polygon([(int(S*.50),int(S*.19)),(int(S*.60),int(S*.50)),
                   (int(S*.50),int(S*.81)),(int(S*.40),int(S*.50))],
                  fill=gold)
        d.polygon([(int(S*.19),int(S*.50)),(int(S*.50),int(S*.40)),
                   (int(S*.81),int(S*.50)),(int(S*.50),int(S*.60))],
                  fill=steel)
        d.ellipse([int(S*.43),int(S*.43),int(S*.57),int(S*.57)],fill=white)
    else:
        accent = {
            "europe": steel,
            "asia": gold,
            "namerica": steel,
            "samerica": emerald,
            "africa": gold,
            "australia": carmine,
        }[name]
        # Framed ticket with a small location point, sized to remain bold when
        # Minecraft renders the 64px source into a 16px inventory slot.
        d.rounded_rectangle(
            [int(S*.10),int(S*.08),int(S*.90),int(S*.78)],
            radius=int(S*.11),fill=graphite,outline=white,width=outline)
        d.rounded_rectangle(
            [int(S*.15),int(S*.12),int(S*.85),int(S*.73)],
            radius=int(S*.08),fill=gold,outline=(139,100,32,255),width=outline)
        d.rounded_rectangle(
            [int(S*.23),int(S*.21),int(S*.77),int(S*.62)],
            radius=int(S*.06),fill=emerald,outline=white,width=outline)

        # White gamepad symbol.
        pad=[(int(S*.31),int(S*.36)),(int(S*.37),int(S*.28)),
             (int(S*.63),int(S*.28)),(int(S*.69),int(S*.36)),
             (int(S*.74),int(S*.53)),(int(S*.66),int(S*.58)),
             (int(S*.58),int(S*.50)),(int(S*.42),int(S*.50)),
             (int(S*.34),int(S*.58)),(int(S*.26),int(S*.53))]
        d.polygon(pad,fill=white)
        d.rectangle(
            [int(S*.34),int(S*.38),int(S*.47),int(S*.43)],fill=graphite)
        d.rectangle(
            [int(S*.38),int(S*.34),int(S*.43),int(S*.47)],fill=graphite)
        d.ellipse(
            [int(S*.58),int(S*.35),int(S*.65),int(S*.42)],fill=carmine)
        d.ellipse(
            [int(S*.65),int(S*.42),int(S*.72),int(S*.49)],fill=steel)

        # Point and continent colour key.
        d.polygon([(int(S*.38),int(S*.76)),(int(S*.62),int(S*.76)),
                   (int(S*.50),int(S*.94))],
                  fill=graphite,outline=white)
        d.ellipse([int(S*.44),int(S*.71),int(S*.56),int(S*.83)],
                  fill=accent,outline=white,width=max(2,outline//2))
    return img.resize((size,size),Image.LANCZOS).filter(
        ImageFilter.UnsharpMask(radius=1.0,percent=95,threshold=0)
    )

# ---- данные: (file, code, cp, cmd) ----
CATS = [  # порядок и cmd должны совпадать с MenuService
 ("state","d",0x1F451,60101),("economic","6",0x1F4B0,60102),("military","c",0x2694,60103),
 ("tech","b",0x2699,60104),("production","e",0x1F3ED,60105),("civil","a",0x1F3E0,60106),
 ("bonus","5",0x2B50,60107)]
BUILDS = [
 ("ratusha","d",0x1F3DB,60201),("meriya","e",0x1F514,60202),("bank","6",0x1F3E6,60203),
 ("cadastre","a",0x1F5FA,60204),("garrison","b",0x1F6E1,60205),("auction","2",0x1F528,60206),
 ("nation_hall","d",0x1F3F0,60207),("ptu","e",0x1F393,60208),("barracks","c",0x2694,60209),
 ("wall","7",0x1F9F1,60210),("sklad","5",0x1F4E6,60211),("depository","3",0x1F392,60212),
 ("konzlager","8",0x26D3,60213),("nether_gate","c",0x1F525,60214),("end_gate","5",0x1F441,60215),
 ("doska","6",0x1F3C6,60216),("monument","b",0x1F5FF,60217),("workshop","e",0x2692,60218),
 ("trade_empire","b",0x1F48E,60219),("mall","a",0x1F3EA,60220),("casino","6",0x1F3B0,60221),
 ("embassy","b",0x1F91D,60222),("temple","d",0x26EA,60223),("peace_council","a",0x262E,60224)]
RARS = [  # вкладки редкостей журнала: cmd 603xx, цвет = цвет редкости
 ("common","f",0x1F41F,60301),("uncommon","a",0x1F420,60302),("rare","b",0x1F421,60303),
 ("epic","d",0x1F991,60304),("legendary","6",0x1F988,60305),("relic","c",0x1F41A,60306),
 ("mythic","4",0x1F409,60307)]
ENVS = [("nether","c",0x1F525,60311),("end","5",0x1F30C,60312)]
# /t menu — кнопки главного меню города (цвет = цвет надписи кнопки). CMD 604xx.
TMENU = [
 ("info","6",0x2139,60401),("spawn","d",0x1F3E0,60402),("bank","6",0x1F4B0,60403),
 ("storage","5",0x1F4E6,60404),("residents","b",0x1F465,60405),("jobs","a",0x26CF,60406),
 ("map","e",0x1F5FA,60407),("switches","c",0x2699,60408),("level","b",0x2B50,60409),
 ("buildings","e",0x1F3D7,60410),("ideology","d",0x1F4DC,60411),("outposts","b",0x1F9ED,60412),
 ("sanctions","b",0x2696,60413),("religion","d",0x2638,60414),("notown","e",0x26A0,60415),
 ("close","7",0x1F6AA,60416)]
# /rtp — континенты (глобусы по полушариям) + случайно. CMD 605xx. Порядок = CONTINENTS в RtpService.
RTP = [
 ("europe","9",0x1F30D,60501),("asia","c",0x1F30F,60502),("namerica","b",0x1F30E,60503),
 ("samerica","a",0x1F30E,60504),("africa","6",0x1F30D,60505),("australia","e",0x1F30F,60506),
 ("random","5",0x1F3B2,60507)]
# /ah — аукцион: кнопки управления + иконки категорий. CMD 606xx. Порядок = AuctionService.
AH = [
 ("refresh","a",0x1F504,60601),("storage","d",0x1F4E6,60602),("prev","e",0x25C0,60603),
 ("page","b",0x1F4C4,60604),("next","e",0x25B6,60605),("categories","b",0x1F4DA,60606),
 ("emblem","5",0x1F451,60607),("exit","c",0x1F6AA,60608),
 ("prev_off","8",0x25C0,60609),("next_off","8",0x25B6,60610),
 ("cat_all","f",0x1F4CB,60611),("cat_gear","c",0x2694,60612),("cat_tools","e",0x26CF,60613),
 ("cat_food","6",0x1F356,60614),("cat_blocks","a",0x1F9F1,60615),("cat_brew","d",0x2697,60616),
 ("cat_res","b",0x1F48E,60617),("cat_misc","7",0x1F381,60618)]
SHOP = [
 ("money",60701),("crystal",60702),("war",60703)]

def panel3(size=64, ss=4):
    """Утопленная рамка-индикатор страниц на 3 слота (как «1/3172» в референсе). Возвращает (left,center,right)."""
    W=3*size*ss; H=size*ss; img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    m=int(H*0.09); rad=int(H*0.20)
    d.rounded_rectangle([m,m,W-m,H-m],radius=rad,fill=(32,37,46,255),outline=(139,149,163,255),width=max(2,int(H*0.055)))
    ins=int(H*0.22)
    d.rounded_rectangle([m+ins,m+ins,W-m-ins,H-m-ins],radius=int(rad*0.55),fill=(18,23,32,255),outline=(59,130,196,255),width=max(1,int(H*0.03)))
    d.line([(m+ins+rad,m+ins+int(H*0.06)),(W-m-ins-rad,m+ins+int(H*0.06))],fill=(224,169,60,120),width=max(1,int(H*0.02)))
    img=img.resize((3*size,size),Image.LANCZOS)
    return [img.crop((i*size,0,(i+1)*size,size)) for i in range(3)]

def emit(prefix, rows):
    out = []
    for name, code, cp, cmd in rows:
        fn = f"nr_{prefix}_{name}"
        try:
            im = tile(code, cp)
        except ValueError as e:
            print("  !! skip", fn, e); continue
        im.save(os.path.join(TEX, fn+".png"))
        json.dump({"parent":"minecraft:item/generated","textures":{"layer0":f"minecraft:item/{fn}"}},
                  open(os.path.join(MODELS, fn+".json"),"w",encoding="utf-8"), indent=2)
        out.append((cmd, fn, im))
    return out

def emit_approved(prefix, rows):
    recolored = [(name, APPROVED_CODE[code], cp, cmd) for name, code, cp, cmd in rows]
    return emit(prefix, recolored)

made = []
made += emit_approved("cat", CATS)
made += emit_approved("b", BUILDS)
made += emit("rar", RARS)
made += emit("renv", ENVS)
made += emit_approved("tm", TMENU)
for name, code, cp, cmd in RTP:
    fn = f"nr_rtp_{name}"
    im = rtp_pin(name)
    im.save(os.path.join(TEX, fn+".png"))
    json.dump({"parent":"minecraft:item/generated","textures":{"layer0":f"minecraft:item/{fn}"}},
              open(os.path.join(MODELS, fn+".json"),"w",encoding="utf-8"), indent=2)
    made.append((cmd, fn, im))
made += emit_approved("ah", AH)
for name, cmd in SHOP:
    fn = f"nr_shop_{name}"
    im = shop_token(name)
    im.save(os.path.join(TEX, fn+".png"))
    json.dump({"parent":"minecraft:item/generated","textures":{"layer0":f"minecraft:item/{fn}"}},
              open(os.path.join(MODELS, fn+".json"),"w",encoding="utf-8"), indent=2)
    made.append((cmd, fn, im))
# индикатор страниц на 3 слота (рамка): nr_ah_page_l/c/r, CMD 60621-60623
for fn, imn, cmd in zip(("nr_ah_page_l","nr_ah_page_c","nr_ah_page_r"), panel3(), (60621,60622,60623)):
    imn.save(os.path.join(TEX, fn+".png"))
    json.dump({"parent":"minecraft:item/generated","textures":{"layer0":f"minecraft:item/{fn}"}},
              open(os.path.join(MODELS, fn+".json"),"w",encoding="utf-8"), indent=2)
    made.append((cmd, fn, imn))
# фон-панель меню (замена чёрному стеклу) — CMD 60001
_f = filler(); _f.save(os.path.join(TEX, "nr_filler.png"))
json.dump({"parent":"minecraft:item/generated","textures":{"layer0":"minecraft:item/nr_filler"}},
          open(os.path.join(MODELS, "nr_filler.json"),"w",encoding="utf-8"), indent=2)
made.append((60001, "nr_filler", _f))
# прозрачная плитка: невидимый, но наводимый слот (для оверлей-панели) — CMD 60000
_blank = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
_blank.save(os.path.join(TEX, "nr_blank.png"))
json.dump({"parent":"minecraft:item/generated","textures":{"layer0":"minecraft:item/nr_blank"}},
          open(os.path.join(MODELS, "nr_blank.json"),"w",encoding="utf-8"), indent=2)
made.append((60000, "nr_blank", _blank))

# ---- items/paper.json (range_dispatch, fallback = ваниль paper) ----
# ВАЖНО: модели миньонов (головы 71xxx + скины 70xxx) генерят отдельные скрипты
# (gen_minion_heads_v2.py / gen_minion_skins.py), но их CMD должны быть ЗДЕСЬ —
# иначе пересборка paper.json стирает их и миньоны теряют головы/скины.
EXTRA = [
    (70001, "nr_minion_homeboby"), (70002, "nr_minion_lelouch"), (70003, "nr_minion_cc"),
    (70004, "nr_minion_nekmeng"), (70005, "nr_minion_minion"), (70006, "nr_minion_pudge"),
    (71001, "nr_minhead_miner"), (71002, "nr_minhead_farmer"),
    (71003, "nr_minhead_lumberjack"), (71004, "nr_minhead_digger"),
]
allcmds = [(cmd, fn) for cmd, fn, _ in made] + EXTRA
entries = [{"threshold": cmd, "model":{"type":"minecraft:model","model":f"minecraft:item/{fn}"}}
           for cmd, fn in sorted(allcmds)]
paper = {"model":{"type":"minecraft:range_dispatch","property":"minecraft:custom_model_data","index":0,
                  "fallback":{"type":"minecraft:model","model":"minecraft:item/paper"},"entries":entries}}
json.dump(paper, open(os.path.join(ITEMS,"paper.json"),"w",encoding="utf-8"), indent=2)

# ---- превью ----
cols=8; cell=72; pad=8
rows_n=(len(made)+cols-1)//cols
sheet=Image.new("RGBA",(cols*(cell+pad)+pad, rows_n*(cell+pad)+pad),(30,24,42,255))
for i,(cmd,fn,im) in enumerate(made):
    r,c=divmod(i,cols); sheet.alpha_composite(im.resize((cell,cell),Image.NEAREST),(pad+c*(cell+pad),pad+r*(cell+pad)))
sheet.save(os.path.join(ROOT,"logo","_builditems_preview.png"))
print(f"tiles: {len(made)} (cats {len(CATS)}, builds {len(BUILDS)}, rarities {len(RARS)}, envs {len(ENVS)})")
print("CMD band:", min(c for c,_,_ in made), "-", max(c for c,_,_ in made))
