# -*- coding: utf-8 -*-
# 3D-головы миньонов (стиль Hypixel): чистая голова-куб 8x8x8 с милым лицом + ПЛОСКАЯ широкая шляпа СВЕРХУ.
# Позиция display.head = scale 1.0, translation 0 (проверено — садится ровно на голову стенда).
import json, os
from PIL import Image

PACK = r"C:\Users\bravl\OneDrive\Desktop\prilC++Claude\NationRise-Branding\pack\assets\minecraft"
TEXDIR = os.path.join(PACK,"textures","item"); MODDIR = os.path.join(PACK,"models","item")
PREV = r"C:\Users\bravl\OneDrive\Desktop\prilC++Claude\NationRise-Branding\minion_skin_example"

SKIN=(236,202,168); SKIN_SH=(210,176,142); WHITE=(248,251,255); PUP=(46,52,70); MOUTH=(180,124,100)
def Tc(c): return (c[0],c[1],c[2],255)
def fill(px,x0,y0,w,h,c):
    for y in range(y0,y0+h):
        for x in range(x0,x0+w): px[x,y]=Tc(c)
SW = {"m":(0,17),"d":(6,17),"l":(12,17),"a":(18,17)}
def U(px2): return [round(v/2.0,3) for v in px2]

def make_tex(name, hatcols):
    im=Image.new("RGBA",(32,32),(0,0,0,0)); px=im.load()
    fill(px,0,8,32,8,SKIN); fill(px,8,0,16,8,SKIN)   # голова — кожа (все грани)
    # милое лицо на front [8,8]-[16,16]: два больших дружелюбных глаза + улыбка + румянец
    for ex in (10,13):
        fill(px,ex,11,2,2,WHITE); px[ex,12]=Tc(PUP); px[ex+1,12]=Tc(PUP)
    px[11,14]=Tc(MOUTH); px[12,14]=Tc(MOUTH); px[10,13]=Tc(MOUTH); px[13,13]=Tc(MOUTH)
    px[9,13]=Tc((240,180,162)); px[14,13]=Tc((240,180,162))
    fill(px,8,15,8,1,SKIN_SH)
    for nm,c in hatcols.items():
        x,y=SW[nm]; fill(px,x,y,4,4,c)
    im.save(os.path.join(TEXDIR,"nr_minhead_"+name+".png"))

def box(ox,oy,w,h,d):
    up=[ox+d,oy,ox+d+w,oy+d]; down=[ox+d+w,oy,ox+d+2*w,oy+d]
    west=[ox,oy+d,ox+d,oy+d+h]; north=[ox+d,oy+d,ox+d+w,oy+d+h]
    east=[ox+d+w,oy+d,ox+2*d+w,oy+d+h]; south=[ox+2*d+w,oy+d,ox+2*d+2*w,oy+d+h]
    return {"north":{"uv":U(north),"texture":"#s"},"south":{"uv":U(south),"texture":"#s"},
            "west":{"uv":U(west),"texture":"#s"},"east":{"uv":U(east),"texture":"#s"},
            "up":{"uv":U(up),"texture":"#s"},"down":{"uv":U(down),"texture":"#s"}}
def swf(nm):
    x,y=SW[nm]; u=U([x+1,y+1,x+3,y+3])
    return {d:{"uv":u,"texture":"#s"} for d in ("north","south","west","east","up","down")}
def head_cube(): return {"name":"head","from":[4,0,4],"to":[12,8,12],"faces":box(0,0,8,8,8)}
def el(name,frm,to,sw): return {"name":name,"from":frm,"to":to,"faces":swf(sw)}

def build(name, cmd, hatcols, extras):
    make_tex(name, hatcols)
    model={"__comment":"Голова миньона ("+name+"). PAPER+CMD "+str(cmd)+". Шляпа сверху головы.",
        "textures":{"s":"minecraft:item/nr_minhead_"+name,"particle":"minecraft:item/nr_minhead_"+name},
        "elements":[head_cube()]+extras,
        "display":{"head":{"translation":[0,0,0],"scale":[1.0,1.0,1.0]},
                   "gui":{"rotation":[26,222,0],"scale":[1.0,1.0,1.0]},"fixed":{"scale":[1.0,1.0,1.0]}}}
    json.dump(model,open(os.path.join(MODDIR,"nr_minhead_"+name+".json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)

# все шляпы — ПЛОСКИЕ и ШИРОКИЕ, стоят СВЕРХУ головы (y>=8), голова не тонет
# MINER: жёлтая каска (широкий плоский брим + низкий купол + лампа)
build("miner",71001,{"m":(244,200,44),"d":(200,160,28),"l":(255,250,215)},[
    el("brim",[1,8.0,1],[15,8.6,15],"m"),
    el("dome",[4,8.6,4],[12,10.0,12],"m"),
    el("band",[4,8.6,4],[12,9.0,12],"d"),
    el("lamp",[7,9.0,3.2],[9,10.0,4.2],"l"),
])
# FARMER: соломенная шляпа (ОГРОМНЫЙ плоский брим + низкий конус)
build("farmer",71002,{"m":(226,194,122),"d":(192,158,92)},[
    el("brim",[-1,8.0,-1],[17,8.5,17],"m"),
    el("brim2",[0,8.5,0],[16,8.8,16],"d"),
    el("cone",[4.5,8.8,4.5],[11.5,10.0,11.5],"m"),
])
# LUMBERJACK: зелёная шапка (широкий низкий купол + светлый отворот)
build("lumberjack",71003,{"m":(78,120,72),"d":(56,90,52),"a":(224,228,220)},[
    el("fold",[3.2,8.0,3.2],[12.8,8.7,12.8],"a"),
    el("cap",[3.6,8.7,3.6],[12.4,10.4,12.4],"m"),
    el("pom",[7.3,10.4,7.3],[8.7,11.2,8.7],"a"),
])
# DIGGER: хаки шлем (широкий брим + купол + шишечка)
build("digger",71004,{"m":(204,184,144),"d":(170,152,114)},[
    el("brim",[1.5,8.0,1.5],[14.5,8.5,14.5],"d"),
    el("dome",[3.6,8.5,3.6],[12.4,10.2,12.4],"m"),
    el("knob",[7.3,10.2,7.3],[8.7,10.9,8.7],"d"),
])

sheet=Image.new("RGBA",(4*36+8,44),(120,150,200,255))
for i,n in enumerate(["miner","farmer","lumberjack","digger"]):
    sheet.alpha_composite(Image.open(os.path.join(TEXDIR,"nr_minhead_"+n+".png")).resize((32,32),Image.NEAREST),(8+i*36,6))
sheet.save(os.path.join(PREV,"_minheads.png"))
print("OK heads clean: miner farmer lumberjack digger (scale 1.0, hat on top)")
