# -*- coding: utf-8 -*-
# Генератор мини-3D скинов миньонов: модель игрока БАЗА+ОВЕРЛЕЙ (12 кубов) из стандартной
# развёртки скина 64x64. Один геометрический шаблон, разные текстуры. uv модели = пиксель/4.
import json, os, shutil
from PIL import Image

PACK = r"C:\Users\bravl\OneDrive\Desktop\prilC++Claude\NationRise-Branding\pack\assets\minecraft"
LOGO = r"C:\Users\bravl\OneDrive\Desktop\prilC++Claude\NationRise-Branding\logo"
TEXDIR = os.path.join(PACK, "textures", "item")
MODDIR = os.path.join(PACK, "models", "item")

# фигура: ноги y=-1..11, тело/руки 11..23, голова 23..31 (овэрлей +0.5 укладывается в лимит [-16,32])
# части: (имя, from, to, base(ox,oy), ovl(ox,oy), w,h,d)
PARTS = [
    ("legR", [-4,-1,-2],[0,11,2],  (0,16),(0,32),   4,12,4),
    ("legL", [0,-1,-2],[4,11,2],   (16,48),(0,48),  4,12,4),
    ("body", [-4,11,-2],[4,23,2],  (16,16),(16,32),  8,12,4),
    ("armR", [4,11,-2],[8,23,2],   (40,16),(40,32),  4,12,4),
    ("armL", [-8,11,-2],[-4,23,2], (32,48),(48,48),  4,12,4),
    ("head", [-4,23,-4],[4,31,4],  (0,0),(32,0),     8,8,8),
]
INF = 0.5  # раздув овэрлея

def U(px4): return [round(v/4.0,3) for v in px4]
def box_faces(ox,oy,w,h,d):
    # стандартная развёртка куба скина -> грани модели
    up    = [ox+d,     oy,     ox+d+w,   oy+d]
    down  = [ox+d+w,   oy,     ox+d+2*w, oy+d]
    west  = [ox,       oy+d,   ox+d,     oy+d+h]   # правый бок
    north = [ox+d,     oy+d,   ox+d+w,   oy+d+h]   # лицо/перёд
    east  = [ox+d+w,   oy+d,   ox+2*d+w, oy+d+h]   # левый бок
    south = [ox+2*d+w, oy+d,   ox+2*d+2*w, oy+d+h] # спина
    return {"north":{"uv":U(north),"texture":"#s"},"south":{"uv":U(south),"texture":"#s"},
            "west":{"uv":U(west),"texture":"#s"},"east":{"uv":U(east),"texture":"#s"},
            "up":{"uv":U(up),"texture":"#s"},"down":{"uv":U(down),"texture":"#s"}}

def build_elements():
    els=[]
    for name,fr,to,base,ovl,w,h,d in PARTS:
        els.append({"name":name,"from":fr,"to":to,"faces":box_faces(base[0],base[1],w,h,d)})
        fo=[fr[0]-INF,fr[1]-INF,fr[2]-INF]; to2=[to[0]+INF,to[1]+INF,to[2]+INF]
        els.append({"name":name+"_o","from":fo,"to":to2,"faces":box_faces(ovl[0],ovl[1],w,h,d)})
    return els

def model_json(texid):
    return {
        "__comment":"Мини-3D скин миньона (фигура игрока, развёртка 64x64, база+овэрлей). Носитель PAPER+CMD на слоте головы НЕВИДИМОГО армор-стенда.",
        "textures":{"s":"minecraft:item/"+texid,"particle":"minecraft:item/"+texid},
        "elements":build_elements(),
        "display":{
            "head":{"translation":[0,-20.0,0],"scale":[0.95,0.95,0.95]},
            "gui":{"rotation":[12,-28,0],"translation":[0,-1,0],"scale":[0.9,0.9,0.9]},
            "ground":{"translation":[0,3,0],"scale":[0.4,0.4,0.4]},
            "fixed":{"scale":[0.7,0.7,0.7]}
        }
    }

# id -> исходная текстура. Готовые персонажи:
SKINS = {
    "homeboby": os.path.join(TEXDIR,"nr_minion_homeboby.png"),
    "lelouch":  os.path.join(LOGO,"Lelouch.png"),
    "cc":       os.path.join(LOGO,"CC.png"),
    "nekmeng":  os.path.join(LOGO,"NekMeng.png"),
    "minion":   os.path.join(LOGO,"minion.png"),
    "pudge":    os.path.join(LOGO,"Pudge.png"),
}

# ---- БАЗОВЫЕ миньоны (стиль Hypixel): голова цвета ресурса + лицо, светлый корпус с акцентом, тёмные ноги ----
BASE = os.path.join(LOGO,"_base"); os.makedirs(BASE, exist_ok=True)
def _T(c): return (c[0],c[1],c[2],255)
def _fill(px,x0,y0,w,h,c):
    for y in range(y0,y0+h):
        for x in range(x0,x0+w): px[x,y]=_T(c)
def base_minion(th):
    im=Image.new("RGBA",(64,64),(0,0,0,0)); px=im.load()
    # голова
    _fill(px,0,8,32,8,th["head"]); _fill(px,8,0,16,8,th["head"]); _fill(px,8,0,8,8,th["headTop"])
    for (x,y) in [(9,1),(12,2),(14,4),(10,5),(13,6)]: px[x,y]=_T(th["accent"])
    for ex in (9,13):
        _fill(px,ex,10,2,2,th["eye"])
        px[ex,10]=_T((min(255,th["eye"][0]+60),min(255,th["eye"][1]+30),min(255,th["eye"][2]+15)))
        px[ex+1,11]=_T(th["pupil"])
    for x in range(10,14): px[x,13]=_T(th["accent"])
    px[10,14]=_T(th["accent"]); px[13,14]=_T(th["accent"])
    # тело
    _fill(px,16,20,24,12,th["body"]); _fill(px,20,16,16,4,th["body"])
    for x in range(20,28): px[x,20]=_T(th["accent"]); px[x,29]=_T(th["accent"]); px[x,30]=_T(th["accent"])
    px[23,22]=_T(th["accent"]); px[24,22]=_T(th["accent"])
    # руки
    _fill(px,40,20,16,12,th["arm"]); _fill(px,44,16,8,4,th["arm"]); _fill(px,40,29,16,3,th["accent"]); _fill(px,44,16,4,4,th["accent"])
    _fill(px,32,52,16,12,th["arm"]); _fill(px,36,48,8,4,th["arm"]); _fill(px,32,61,16,3,th["accent"]); _fill(px,36,48,4,4,th["accent"])
    # ноги
    _fill(px,0,20,16,12,th["leg"]); _fill(px,4,16,8,4,th["leg"]); _fill(px,0,29,16,3,th["boot"])
    _fill(px,16,52,16,12,th["leg"]); _fill(px,20,48,8,4,th["leg"]); _fill(px,16,61,16,3,th["boot"])
    return im
# базовый вид миньонов теперь — видимый армор-стенд + броня + 3D-голова по профессии
# (см. gen_minion_heads.py), а НЕ цельный скин. Здесь только кастомные/платные скины (SKINS).
for sid, src in SKINS.items():
    texid="nr_minion_"+sid
    # текстура
    Image.open(src).convert("RGBA").save(os.path.join(TEXDIR,texid+".png"))
    # модель
    with open(os.path.join(MODDIR,texid+".json"),"w",encoding="utf-8") as f:
        json.dump(model_json(texid),f,ensure_ascii=False,indent=2)
    print("skin:",sid,"->",texid)

# удалить старые homelander-файлы
for p in [os.path.join(TEXDIR,"nr_minion_homelander.png"), os.path.join(MODDIR,"nr_minion_homelander.json")]:
    if os.path.exists(p): os.remove(p); print("removed",os.path.basename(p))
print("DONE")
