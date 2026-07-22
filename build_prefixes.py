# -*- coding: utf-8 -*-
"""Стафф-плашки + разнообразные значки рангов + текстурные глифы религий/идеологий."""
import os, json, math
from PIL import Image, ImageDraw, ImageFont
from fontTools import ttLib
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = os.path.dirname(os.path.abspath(__file__))
MC = os.path.join(ROOT, "pack", "assets", "minecraft")
FONTTEX = os.path.join(MC, "textures", "font")
DEFAULT = os.path.join(MC, "font", "default.json")
os.makedirs(FONTTEX, exist_ok=True)

TTF = os.path.join(ROOT, "_mont800.ttf")
if not os.path.exists(TTF):
    fv = ttLib.TTFont(os.path.join(ROOT, "_mont_var.ttf")); instantiateVariableFont(fv, {"wght": 800}, inplace=True); fv.save(TTF)
cmap = ttLib.TTFont(TTF).getBestCmap()
GREEK = {"α": ("α" if ord("α") in cmap else "A"), "β": ("β" if ord("β") in cmap else "B"), "Ω": ("Ω" if ord("Ω") in cmap else "O")}
def fixg(s):
    for g, r in GREEK.items(): s = s.replace(g, r)
    return s

def C(t, a=255): return (int(t[0]), int(t[1]), int(t[2]), a)
def supersample(fn, size=16, ss=8):
    S = size * ss; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); fn(ImageDraw.Draw(im), S); return im.resize((size, size), Image.LANCZOS)

# ===================== СТАФФ: ПЛАШКИ =====================
SCH = {
    "red": dict(top=(232,82,82), bot=(150,26,26), border=(92,14,14), text=(255,255,255), shadow=(54,8,8)),
    "blue": dict(top=(86,150,255), bot=(28,74,176), border=(14,42,100), text=(255,255,255), shadow=(10,26,68)),
    "green": dict(top=(142,224,92), bot=(58,150,30), border=(26,88,14), text=(255,255,255), shadow=(18,58,10)),
    "gold": dict(top=(255,212,80), bot=(198,142,44), border=(108,74,16), text=(255,255,255), shadow=(80,50,8)),
    "purple": dict(top=(157,107,234), bot=(77,34,178), border=(46,21,104), text=(247,250,219), shadow=(28,12,64)),
    "gray": dict(top=(178,178,186), bot=(108,108,118), border=(56,56,64), text=(255,255,255), shadow=(40,40,46)),
    "yt": dict(top=(255,86,74), bot=(198,18,18), border=(94,8,8), text=(255,255,255), shadow=(58,6,6)),
    "tt": dict(top=(70,74,88), bot=(20,22,28), border=(4,4,6), text=(37,244,238), shadow=(8,8,12)),
}
# медиа-роли: те же плашки, что у стаффа, но своя палитра (ниже стаффа по приоритету показа)
MEDIA = [("youtube","YOUTUBE","yt",0xE037), ("tiktok","TIKTOK","tt",0xE038)]
STAFF = [("admin","ADMIN","red",0xE020),("curator","КУРАТОР","red",0xE021),("ss_curator","SS-КУРАТОР","red",0xE022),
         ("teamlead","TEAM LEAD","gold",0xE023),("alpha","α-INSP","purple",0xE024),("moder","MODER","blue",0xE025),
         ("beta","β-INSP","purple",0xE026),("jrmoder","JR.MODER","blue",0xE027),("omega","Ω-INSP","purple",0xE028),
         ("helper","HELPER","green",0xE029),("jrhelper","JR.HELPER","green",0xE02A),("junior","JUNIOR","gray",0xE02B)]
SCALE = 4; PH = 9 * SCALE
def vgrad(w, h, top, bot):
    g = Image.new("RGB", (1, h))
    for j in range(h): g.putpixel((0, j), tuple(int(top[k]+(bot[k]-top[k])*(j/max(1,h-1))) for k in range(3)))
    return g.resize((w, h)).convert("RGBA")
def plaque(label, sch):
    label = fixg(label); font = ImageFont.truetype(TTF, int(PH*0.66))
    bb = ImageDraw.Draw(Image.new("RGBA",(4,4))).textbbox((0,0), label, font=font)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]; padx = int(PH*0.34); W = tw+padx*2
    img = Image.new("RGBA",(W,PH),(0,0,0,0)); rad = int(PH*0.26)
    mask = Image.new("L",(W,PH),0); ImageDraw.Draw(mask).rounded_rectangle([0,0,W-1,PH-1],radius=rad,fill=255)
    img.paste(vgrad(W,PH,sch["top"],sch["bot"]),(0,0),mask); d = ImageDraw.Draw(img)
    d.rounded_rectangle([0,0,W-1,PH-1],radius=rad,outline=C(sch["border"]),width=max(2,int(PH*0.06)))
    d.line([(rad,max(2,SCALE)),(W-rad,max(2,SCALE))],fill=tuple(min(255,c+46) for c in sch["top"])+(150,),width=max(1,SCALE))
    tx, ty = (W-tw)//2-bb[0], (PH-th)//2-bb[1]
    d.text((tx,ty+SCALE),label,font=font,fill=C(sch["shadow"])); d.text((tx,ty),label,font=font,fill=C(sch["text"]))
    return img

# ===================== РАНГИ: РАЗНЫЕ ЗНАЧКИ (full-color) =====================
def shades(base):
    def f(m): return tuple(min(255,max(0,int(base[i]*m))) for i in range(3))
    return f(0.42), f(0.74), base, f(1.26), f(1.7)  # dark, mid, base, light, hl

def i_gem_round(base):
    dk, md, bc, lt, hl = shades(base)
    def draw(d, S):
        def P(x,y): return (x*S,y*S)
        TL,TR=P(0.34,0.16),P(0.66,0.16); GL,GR=P(0.10,0.42),P(0.90,0.42); ML,MR=P(0.40,0.42),P(0.60,0.42); CU=P(0.5,0.92)
        d.polygon([TL,TR,MR,ML],fill=C(lt)); d.polygon([TL,ML,GL],fill=C(md)); d.polygon([TR,MR,GR],fill=C(md))
        d.polygon([GL,ML,CU],fill=C(dk)); d.polygon([ML,MR,CU],fill=C(bc)); d.polygon([MR,GR,CU],fill=C(dk))
        ow=max(2,int(S*0.02)); d.line([TL,TR,GR,CU,GL,TL],fill=C(shades(base)[0],255),width=ow,joint="curve")
        d.polygon([TL,(TL[0]+S*0.07,TL[1]),(ML[0]-S*0.04,ML[1]-S*0.03),(ML[0]-S*0.12,ML[1]-S*0.03)],fill=C(hl))
    return supersample(draw)

def i_gem_emerald(base):
    dk, md, bc, lt, hl = shades(base)
    def draw(d, S):
        x0,y0,x1,y1=S*0.18,S*0.14,S*0.82,S*0.86; c=S*0.12
        outer=[(x0+c,y0),(x1-c,y0),(x1,y0+c),(x1,y1-c),(x1-c,y1),(x0+c,y1),(x0,y1-c),(x0,y0+c)]
        d.polygon(outer,fill=C(md),outline=C(dk,255))
        ix0,iy0,ix1,iy1=S*0.30,S*0.28,S*0.70,S*0.72
        d.rectangle([ix0,iy0,ix1,iy1],fill=C(bc))
        d.rectangle([ix0,iy0,ix1,(iy0+iy1)/2],fill=C(lt))  # верхняя ступень светлее
        d.line([(ix0,iy0),(ix1,iy0)],fill=C(hl),width=max(1,int(S*0.02)))
    return supersample(draw)

def i_star(base):
    dk, md, bc, lt, hl = shades(base)
    def draw(d, S):
        cx,cy=S/2,S*0.52; o,i=S*0.42,S*0.17; pts=[]
        for k in range(10):
            a=-math.pi/2+k*math.pi/5; r=o if k%2==0 else i; pts.append((cx+math.cos(a)*r,cy+math.sin(a)*r))
        d.polygon(pts,fill=C(bc),outline=C(dk,255))
        inn=[]
        for k in range(10):
            a=-math.pi/2+k*math.pi/5; r=(o if k%2==0 else i)*0.5; inn.append((cx+math.cos(a)*r,cy+math.sin(a)*r))
        d.polygon(inn,fill=C(lt))
        d.line([(cx,cy-o),(cx,cy)],fill=C(hl),width=max(2,int(S*0.03)))
    return supersample(draw)

def i_crown(gold=(255,200,80), gem=(214,46,72)):
    dk,md,bc,lt,hl=shades(gold); gd,gm,gb,gl,gh=shades(gem)
    def draw(d,S):
        def P(x,y): return (x*S,y*S)
        pts=[P(0.06,0.62),P(0.20,0.22),P(0.36,0.50),P(0.50,0.14),P(0.64,0.50),P(0.80,0.22),P(0.94,0.62),P(0.94,0.84),P(0.06,0.84)]
        d.polygon(pts,fill=C(bc),outline=C(dk,255))
        d.rectangle([S*0.06,S*0.66,S*0.94,S*0.84],fill=C(md))  # лента
        d.line([(S*0.06,S*0.66),(S*0.94,S*0.66)],fill=C(lt),width=max(1,int(S*0.02)))
        for fx,fy in [(0.20,0.22),(0.50,0.14),(0.80,0.22)]:  # камни на зубцах
            r=S*0.055; d.ellipse([P(fx,fy)[0]-r,P(fx,fy)[1]-r+S*0.02,P(fx,fy)[0]+r,P(fx,fy)[1]+r+S*0.02],fill=C(gb),outline=C(gd,255))
        for fx in (0.28,0.5,0.72):  # камни на ленте
            r=S*0.05; cyl=S*0.75; d.ellipse([P(fx,0)[0]-r,cyl-r,P(fx,0)[0]+r,cyl+r],fill=C(gb),outline=C(gd,255))
    return supersample(draw)

def i_shield(base):
    dk,md,bc,lt,hl=shades(base)
    def draw(d,S):
        def P(x,y): return (x*S,y*S)
        sh=[P(0.18,0.14),P(0.82,0.14),P(0.84,0.46),P(0.5,0.92),P(0.16,0.46)]
        d.polygon(sh,fill=C(bc),outline=C(dk,255))
        d.polygon([P(0.18,0.14),P(0.82,0.14),P(0.80,0.33),P(0.20,0.33)],fill=C(lt))   # верх светлее
        cx,cy=S*0.5,S*0.46; r=S*0.135
        d.polygon([(cx,cy-r),(cx+r,cy),(cx,cy+r),(cx-r,cy)],fill=C(hl),outline=C(dk,255))  # камень в центре
        d.line([P(0.19,0.16),P(0.18,0.44)],fill=C(lt),width=max(1,int(S*0.018)))
    return supersample(draw)

def i_sunburst(base):
    dk,md,bc,lt,hl=shades(base)
    def draw(d,S):
        cx,cy=S/2,S/2; R=S*0.21; RR=S*0.46; n=12
        for k in range(n):
            a=k*2*math.pi/n
            p1=(cx+math.cos(a)*RR,cy+math.sin(a)*RR)
            p2=(cx+math.cos(a+math.pi/n*0.55)*R*0.92,cy+math.sin(a+math.pi/n*0.55)*R*0.92)
            p3=(cx+math.cos(a-math.pi/n*0.55)*R*0.92,cy+math.sin(a-math.pi/n*0.55)*R*0.92)
            d.polygon([p1,p2,p3],fill=C(md))
        d.ellipse([cx-R,cy-R,cx+R,cy+R],fill=C(bc),outline=C(dk,255))
        d.ellipse([cx-R*0.62,cy-R*0.62,cx+R*0.62,cy+R*0.62],fill=C(lt))
        d.ellipse([cx-R*0.30,cy-R*0.38,cx+R*0.02,cy-R*0.06],fill=C(hl))   # блик
    return supersample(draw)

def i_mic(on=True):
    """Значок голосового чата: микрофон (зелёный — подключён, серый с перечёркиванием — нет)."""
    base = (108,226,120) if on else (128,132,140)
    dk, md, bc, lt, hl = shades(base)
    def draw(d, S):
        cx = S*0.5
        # капсула микрофона
        d.rounded_rectangle([cx-S*0.17, S*0.10, cx+S*0.17, S*0.56], radius=S*0.17, fill=C(bc), outline=C(dk,255), width=max(2,int(S*0.03)))
        d.rounded_rectangle([cx-S*0.10, S*0.16, cx-S*0.02, S*0.44], radius=S*0.05, fill=C(hl))  # блик
        # дуга-держатель
        d.arc([cx-S*0.32, S*0.30, cx+S*0.32, S*0.76], start=0, end=180, fill=C(md), width=max(3,int(S*0.055)))
        # ножка + подставка
        d.line([(cx, S*0.72), (cx, S*0.86)], fill=C(md), width=max(3,int(S*0.055)))
        d.line([(cx-S*0.20, S*0.88), (cx+S*0.20, S*0.88)], fill=C(md), width=max(3,int(S*0.055)))
        if not on:  # перечёркивание
            d.line([(S*0.12,S*0.88),(S*0.88,S*0.10)], fill=C((228,66,66),255), width=max(3,int(S*0.075)))
    return supersample(draw)

VOICE = [("mic_on", lambda: i_mic(True), 0xE039), ("mic_off", lambda: i_mic(False), 0xE03A)]

RANK = [("custom",  lambda: i_star((196,132,255)),0xE036),
        ("octavian",lambda: i_crown((255,205,90),(214,46,72)),0xE030),
        ("archon",  lambda: i_shield((236,72,72)),0xE031),
        ("king",    lambda: i_sunburst((255,198,72)),0xE032),
        ("elite",   lambda: i_star((255,228,96)),0xE033),
        ("prince",  lambda: i_gem_round((96,220,234)),0xE034),
        ("noble",   lambda: i_gem_emerald((112,208,92)),0xE035)]

# ===================== РЕЛИГИИ/ИДЕОЛОГИИ: белые глифы из системных шрифтов =====================
SEGUI = r"C:\Windows\Fonts\seguisym.ttf"; NIRM = r"C:\Windows\Fonts\Nirmala.ttc"
def render_symbol(ch, fontpath, size=16):
    f = ImageFont.truetype(fontpath, 110); im = Image.new("RGBA",(128,128),(0,0,0,0)); d = ImageDraw.Draw(im)
    bb = d.textbbox((0,0), ch, font=f); w,h = bb[2]-bb[0], bb[3]-bb[1]
    d.text(((128-w)//2-bb[0],(128-h)//2-bb[1]), ch, font=f, fill=(255,255,255,255))
    bbx = im.getbbox()
    if bbx: im = im.crop(bbx)
    side = max(im.size, default=1); sq = Image.new("RGBA",(side,side),(0,0,0,0)); sq.alpha_composite(im,((side-im.width)//2,(side-im.height)//2))
    return sq.resize((size,size), Image.LANCZOS)
# (file, codepoint, fontpath)
SYMS = [("cross",0x271D,SEGUI),("maltese",0x2720,SEGUI),("crown_m",0x2655,SEGUI),("scales",0x2696,SEGUI),
        ("hammer",0x262D,SEGUI),("crescent",0x262A,SEGUI),("wheel",0x2638,SEGUI),("hexagram",0x2721,SEGUI),
        ("torii",0x26E9,SEGUI),("om",0x0950,NIRM)]

# ---- генерация ----
prev_plaques, prev_icons = [], []
for fid,label,sch,cp in STAFF:
    im=plaque(label,SCH[sch]); im.save(os.path.join(FONTTEX,f"nr_role_{fid}.png")); prev_plaques.append(im)
for fid,label,sch,cp in MEDIA:
    im=plaque(label,SCH[sch]); im.save(os.path.join(FONTTEX,f"nr_media_{fid}.png")); prev_plaques.append(im)
for fid,maker,cp in RANK:
    im=maker(); im.save(os.path.join(FONTTEX,f"nr_rank_{fid}.png")); prev_icons.append(im)
for fid,maker,cp in VOICE:
    im=maker(); im.save(os.path.join(FONTTEX,f"nr_voice_{fid}.png")); prev_icons.append(im)
done_syms=[]
for fid,cp,fp in SYMS:
    try:
        im=render_symbol(chr(cp),fp); im.save(os.path.join(FONTTEX,f"nr_sym_{fid}.png")); prev_icons.append(im); done_syms.append((fid,cp))
    except Exception as e:
        print("skip symbol",fid,repr(e))

# ---- default.json (идемпотентно) ----
data=json.load(open(DEFAULT,encoding="utf-8"))
provs=[p for p in data["providers"] if not any(p.get("file","").startswith(x) for x in ("minecraft:font/nr_role_","minecraft:font/nr_media_","minecraft:font/nr_rank_","minecraft:font/nr_voice_","minecraft:font/nr_sym_"))]
# куда вставлять: перед ttf-провайдером, иначе перед подключением ванильного шрифта
# (в паке после правок ChatGPT ttf больше нет — только reference include/space и include/default)
ti=next((i for i,p in enumerate(provs) if p.get("type")=="ttf"), None)
if ti is None:
    ti=next((i for i,p in enumerate(provs)
             if p.get("type")=="reference" and "space" not in str(p.get("id",""))), len(provs))
ins=[{"type":"bitmap","file":f"minecraft:font/nr_role_{fid}.png","ascent":7,"height":9,"chars":[chr(cp)]} for fid,_,_,cp in STAFF]
ins+=[{"type":"bitmap","file":f"minecraft:font/nr_media_{fid}.png","ascent":7,"height":9,"chars":[chr(cp)]} for fid,_,_,cp in MEDIA]
ins+=[{"type":"bitmap","file":f"minecraft:font/nr_rank_{fid}.png","ascent":8,"height":10,"chars":[chr(cp)]} for fid,_,cp in RANK]
ins+=[{"type":"bitmap","file":f"minecraft:font/nr_voice_{fid}.png","ascent":8,"height":10,"chars":[chr(cp)]} for fid,_,cp in VOICE]
ins+=[{"type":"bitmap","file":f"minecraft:font/nr_sym_{fid}.png","ascent":8,"height":10,"chars":[chr(cp)]} for fid,cp in done_syms]
provs[ti:ti]=ins; data["providers"]=provs
json.dump(data,open(DEFAULT,"w",encoding="utf-8"),ensure_ascii=False,indent=2)

# ---- превью ----
pad=12; icons=[g.resize((44,44),Image.NEAREST) for g in prev_icons]
W=max(max(im.width for im in prev_plaques), 6*(44+pad)+pad)
sheet=Image.new("RGBA",(W+pad*2, sum(im.height for im in prev_plaques)+pad*(len(prev_plaques)+1)+2*(44+pad)+pad),(28,22,38,255))
y=pad
for im in prev_plaques: sheet.alpha_composite(im,(pad,y)); y+=im.height+pad
# tint preview: показать значки в крем-цвете чтобы белые символы было видно
x=pad
for idx,g in enumerate(icons):
    tint=Image.new("RGBA",g.size,(0,0,0,0)); tint.paste((247,250,219,255),(0,0),g.split()[3]); tint.putalpha(g.split()[3])
    src=g if idx<len(RANK)+len(VOICE) else tint  # ранги/микрофоны цветные, символы — белые→крем
    sheet.alpha_composite(src,(x,y)); x+=44+pad
    if x>W: x=pad; y+=44+pad
sheet.save(os.path.join(ROOT,"logo","_symbols_preview.png"))
print("staff:",len(STAFF),"| media:",len(MEDIA),"| rank icons:",len(RANK),"| voice:",len(VOICE),"| symbols:",len(SYMS))
