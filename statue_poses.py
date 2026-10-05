# -*- coding: utf-8 -*-
"""Позы статуй «Аллеи славы» (04.10.2026): задание поз, предпросмотр и запись в модель BetterModel.

Модель — стандартный скелет игрока BetterModel (plugins/BetterModel/players/steve.bbmodel): бёдра,
талия, грудь, голова, плечо+предплечье, бедро+голень. Позы — анимации «statue_*» (держат кадр),
геометрию не трогаем, поэтому ресурспак моделей пересобирать не нужно.

Оси (проверено по встроенной анимации roll): перед модели — −Z (грань north = лицо);
правая рука — +X. Поворот кости X<0 наклоняет вперёд (к лицу); для свисающей руки/ноги X>0
выносит её вперёд. Z>0 у правой руки — в сторону (наружу), у левой наружу — Z<0; у ПОДНЯТОЙ
вверх руки знак обратный (Z поворачивает уже после X): правая наружу — Z<0.

Как это видит BetterModel 3.5 (снято javap'ом, 05.10.2026): для формата 5.0 повороты анимации
берутся как (−x, y, −z), координаты групп — invertXZ, кватернион — rotateZYX. То есть модель
целиком развёрнута на 180° вокруг вертикали (лицом на юг, как сущность с yaw 0), а сама поза
та же, что в этом предпросмотре: он рисует ровно то, что будет в игре.

Локти — чистые шарниры (05.10.2026): предплечье только сгибается по X (проворот по Y — не больше ±20°),
нужное направление кисти даёт поворот плеча. С проворотом предплечья его квадратное сечение вставало
наискось к плечу и углы коробки торчали на локте.

Пересечения (05.10.2026): там, где рука проходит сквозь голову или кисти друг сквозь друга,
в игре рябь — две текстуры спорят за один пиксель. Перед записью — check: ни одного «!!».

  py -3.13 statue_poses.py preview <steve.bbmodel> <out.png> [skin.png]
  py -3.13 statue_poses.py write   <steve.bbmodel>          — дописать/обновить анимации statue_*
  py -3.13 statue_poses.py check   <steve.bbmodel>          — не проходят ли руки/ноги сквозь тело
"""
import base64, io, json, math, sys, uuid
from PIL import Image, ImageDraw

# ---- позы: кость -> (x, y, z) градусы; "@root_pos" — смещение корня (пиксели модели) ----
POSES = {
    # Победитель: подбородок вверх, правая рука вскинута к небу, левая — кулак на поясе.
    "statue_victory": {
        "h_ph_head": (14, 12, 0), "pc_chest": (4, 6, 0), "pra_right_arm": (175.5, 15.9, -8.8),
        "prfa_right_forearm": (0, 0, 0), "pla_left_arm": (-18, 0, -38), "plfa_left_forearm": (82, 0, 0),
        "prl_right_leg": (-4, 0, 5), "pll_left_leg": (10, 0, -5), "plfl_left_foreleg": (-10, 0, 0),
    },
    # Отдание чести: прямая стойка, правая ладонь у виска, левая рука по шву.
    "statue_salute": {
        "h_ph_head": (2, 0, 0), "pra_right_arm": (50.5, -68.5, 78.8), "prfa_right_forearm": (126.7, 6.1, 0),
        "pla_left_arm": (-0.5, -2.4, -3),
        "plfa_left_forearm": (0.3, -4.9, 0),
    },
    # Рыцарь на одном колене: правое колено в землю, левая нога согнута, голова склонена.
    "statue_knight": {
        "@root_pos": (0, -4.6, 0), "pc_chest": (-6, 0, 0), "h_ph_head": (-14, 0, 0),
        "prl_right_leg": (-8, 0, 0), "prfl_right_foreleg": (-84, 0, 0), "pll_left_leg": (84, 0, 0),
        "plfl_left_foreleg": (-86, 0, 0), "pra_right_arm": (68.6, 26.4, 73.9),
        "prfa_right_forearm": (57.7, 17.4, 0), "pla_left_arm": (27.1, -48.5, -54.1),
        "plfa_left_forearm": (51.5, -19.4, 0),
    },
    # Руки на груди: уверенная стойка, ноги на ширине плеч, взгляд чуть сверху вниз.
    "statue_crossed": {
        "h_ph_head": (-4, -8, 0), "pra_right_arm": (81.6, 30, 86.3),
        "prfa_right_forearm": (54.6, 19.9, 0), "pla_left_arm": (31.4, -46.9, -73.2),
        "plfa_left_forearm": (80.4, -19.1, 0), "prl_right_leg": (0, 0, 7), "pll_left_leg": (0, 0, -7),
    },
    # Полководец: обе руки на рукояти меча перед собой, остриё в землю.
    "statue_commander": {
        "h_ph_head": (6, 0, 0), "pra_right_arm": (125.5, 59.5, 148.7), "prfa_right_forearm": (22.6, -19.8, 0),
        "pla_left_arm": (67.2, -59.1, -81.2), "plfa_left_forearm": (21.8, -6.2, 0), "prl_right_leg": (0, 0, 7),
        "pll_left_leg": (0, 0, -7),
    },
    # Приветствие: правая рука поднята ладонью вперёд, левая на поясе.
    "statue_wave": {
        "h_ph_head": (6, -12, 0), "pc_chest": (0, -6, 0), "pra_right_arm": (150, 0, -25),
        "prfa_right_forearm": (25, 0, 0), "pla_left_arm": (-16.6, 0.1, -39.6), "plfa_left_forearm": (82, 0, 0),
        "pll_left_leg": (8, 0, -4), "plfl_left_foreleg": (-10, 0, 0),
    },
    # Знаменосец: правая рука с древком вверх, левая — ладонь на груди, шаг вперёд.
    "statue_banner": {
        "h_ph_head": (10, 0, 0), "pra_right_arm": (151.4, 1.3, 0.2), "prfa_right_forearm": (2.7, -6, 0),
        "pla_left_arm": (69, -31.7, -80.5), "plfa_left_forearm": (59.3, -16.2, 0),
        "prl_right_leg": (-14, 0, 0), "pll_left_leg": (18, 0, 0), "plfl_left_foreleg": (-14, 0, 0),
    },
    # Мыслитель: подбородок на кулаке, вторая рука поддерживает локоть.
    "statue_thinker": {
        "h_ph_head": (-10, 0, 0), "pc_chest": (-6, 0, 0), "pra_right_arm": (57.5, 49, 74.9),
        "prfa_right_forearm": (78.2, -19.5, 0), "pla_left_arm": (47.6, -43.5, -68.9),
        "plfa_left_forearm": (60, -4.8, 0), "prl_right_leg": (4, 0, 4), "pll_left_leg": (-8, 0, -8),
        "plfl_left_foreleg": (14, 0, 0),
    },
    # Герой: руки на поясе, грудь вперёд, подбородок вверх.
    "statue_hero": {
        "h_ph_head": (12, 0, 0), "pc_chest": (4, 0, 0), "pra_right_arm": (-14, 0, 42),
        "prfa_right_forearm": (88, 0, 0), "pla_left_arm": (-14, 0, -42), "plfa_left_forearm": (88, 0, 0),
        "prl_right_leg": (0, 0, 7), "pll_left_leg": (0, 0, -7),
    },
    # Триумф: обе руки вскинуты буквой V.
    "statue_triumph": {
        "h_ph_head": (22, 0, 0), "pc_chest": (6, 0, 0), "pra_right_arm": (165, 0, -32),
        "prfa_right_forearm": (8, 0, 0), "pla_left_arm": (165, 0, 32), "plfa_left_forearm": (8, 0, 0),
        "prl_right_leg": (0, 0, 6), "pll_left_leg": (0, 0, -6),
    },
    # Вперёд!: правая рука указывает вперёд, левая на поясе, шаг вперёд.
    "statue_point": {
        "h_ph_head": (4, 0, 0), "pra_right_arm": (90, 0, 0), "prfa_right_forearm": (0, 0, 0),
        "pla_left_arm": (-14, 0, -42), "plfa_left_forearm": (88, 0, 0), "prl_right_leg": (22, 0, 0),
        "prfl_right_foreleg": (-10, 0, 0), "pll_left_leg": (-14, 0, 0),
    },
    # Поклон: поклон в пояс, правая ладонь на груди, левая за спиной.
    "statue_bow": {
        "pw_waist": (-18, 0, 0), "pc_chest": (-14, 0, 0), "h_ph_head": (-12, 0, 0),
        "pra_right_arm": (70, 26.1, 70.4), "prfa_right_forearm": (55.2, 13, 0),
        "pla_left_arm": (-94, -6.7, 61.8), "plfa_left_forearm": (76.4, -0.4, 0),
    },
    # Дозорный: ладонь козырьком у лба — вглядывается вдаль; левая на поясе.
    "statue_lookout": {
        "h_ph_head": (10, -8, 0), "pra_right_arm": (80.7, -20.7, 73.8),
        "prfa_right_forearm": (57, 7.8, 0), "pla_left_arm": (-16.6, -27.4, -38.8),
        "plfa_left_forearm": (84.6, 15, 0), "prl_right_leg": (0, 0, 6), "pll_left_leg": (6, 0, -6),
    },
    # Отдых: руки за головой, локти в стороны.
    "statue_relax": {
        "h_ph_head": (14, 0, 0), "pra_right_arm": (205.9, -14.8, -15.2), "prfa_right_forearm": (122.8, -8.3, 0),
        "pla_left_arm": (199.4, 15.7, 34.1), "plfa_left_forearm": (120.1, 16.9, 0), "prl_right_leg": (0, 0, 6),
        "pll_left_leg": (8, 0, -4), "plfl_left_foreleg": (-8, 0, 0),
    },
    # Защитник: левая рука со щитом впереди, правая с мечом наготове, боевая стойка.
    "statue_guard": {
        "pc_chest": (-6, -14, 0), "h_ph_head": (0, 6, 0), "pla_left_arm": (72, 0, 8),
        "plfa_left_forearm": (38, 0, 0), "pra_right_arm": (-24, 0, 22), "prfa_right_forearm": (62, 0, 0),
        "pll_left_leg": (22, 0, -4), "plfl_left_foreleg": (-18, 0, 0), "prl_right_leg": (-16, 0, 4),
    },
    # Сидит на краю: попой на блоке, ноги свешиваются — ставьте у края; руки опущены, ладони у бёдер.
    "statue_sit": {
        "@root_pos": (0, -9.2, 0), "h_ph_head": (4, 0, 0), "prl_right_leg": (90, -4, 0),
        "prfl_right_foreleg": (-90, 0, 0), "pll_left_leg": (90, 4, 0), "plfl_left_foreleg": (-90, 0, 0),
        "pra_right_arm": (-14.6, 18.4, 7.9), "prfa_right_forearm": (77.7, -3.3, 0),
        "pla_left_arm": (-15.1, -5.3, -2.9), "plfa_left_forearm": (76.7, 0.7, 0),
    },
    # Сидит на земле: ноги вытянуты вперёд по блоку, ладони на коленях. В любом размере прижат к блоку.
    "statue_sit_ground": {
        "h_ph_head": (4, 0, 0), "pc_chest": (-4, 0, 0), "prl_right_leg": (90, -5, 0),
        "pll_left_leg": (90, 5, 0), "prfl_right_foreleg": (0, 0, 0), "plfl_left_foreleg": (0, 0, 0),
        "pra_right_arm": (26.1, 27.6, 46.4), "prfa_right_forearm": (55.2, 20, 0),
        "pla_left_arm": (-8.6, -26.5, -14.1), "plfa_left_forearm": (69.9, 3.6, 0),
        "@root_pos": (0, -9.2, 0),
    },
    # Меч на плече: правая рука держит меч, лежащий на плече; левая расслаблена.
    "statue_shoulder": {
        "h_ph_head": (6, 10, 0), "pra_right_arm": (44.3, 13.1, 10.6), "prfa_right_forearm": (122.1, -8.4, 0),
        "pla_left_arm": (5.4, -7.6, -8.3), "plfa_left_forearm": (12.3, 4.2, 0), "prl_right_leg": (0, 0, 6),
        "pll_left_leg": (10, 0, -4), "plfl_left_foreleg": (-10, 0, 0),
    },
    # Главный: руки сцеплены за спиной на пояснице, грудь вперёд, подбородок вверх — хозяин положения.
    # Предплечья лежат на пояснице на ~1 пиксель (см. CONTACT): иначе локти торчали бы высоко назад.
    "statue_chief": {
        "h_ph_head": (8, 0, 0), "pc_chest": (3, 0, 0), "prl_right_leg": (0, 0, 5), "pll_left_leg": (0, 0, -5),
        "pra_right_arm": (-62.9, 3.6, -24.7), "prfa_right_forearm": (37.7, 9.4, 0),
        "pla_left_arm": (-77.9, -22.8, 58.6), "plfa_left_forearm": (53.4, 1.1, 0),
    },
}

NAMES = {
    "statue_victory": "Победитель", "statue_salute": "Честь", "statue_knight": "Рыцарь",
    "statue_crossed": "Руки на груди", "statue_commander": "Полководец", "statue_wave": "Приветствие",
    "statue_banner": "Знаменосец", "statue_thinker": "Мыслитель",
    "statue_hero": "Герой", "statue_triumph": "Триумф", "statue_point": "Вперёд!", "statue_bow": "Поклон",
    "statue_lookout": "Дозорный", "statue_relax": "Отдых", "statue_guard": "Защитник", "statue_sit": "Сидит на краю",
    "statue_shoulder": "Меч на плече", "statue_chief": "Главный", "statue_sit_ground": "Сидит на земле",
}


# ---------------- математика ----------------
def rx(a):
    c, s = math.cos(a), math.sin(a)
    return [[1, 0, 0], [0, c, -s], [0, s, c]]
def ry(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]
def rz(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]
def mm(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def mv(a, v):
    return [sum(a[i][k] * v[k] for k in range(3)) for i in range(3)]

class Xf:
    """Аффинное преобразование: x' = R·x + t."""
    def __init__(self, R=None, t=None):
        self.R = R or [[1, 0, 0], [0, 1, 0], [0, 0, 1]]; self.t = t or [0, 0, 0]
    def apply(self, v):
        r = mv(self.R, v); return [r[i] + self.t[i] for i in range(3)]
    def then_local(self, R, origin, offset):
        # self ∘ T(offset) ∘ T(o) ∘ R ∘ T(−o)
        o = origin
        tl = [offset[i] + o[i] - mv(R, o)[i] for i in range(3)]
        R2 = mm(self.R, R)
        t2 = [self.apply(tl)[i] for i in range(3)]
        return Xf(R2, t2)


def euler(deg):
    x, y, z = (math.radians(v) for v in deg)
    return mm(rz(z), mm(ry(y), rx(x)))   # порядок ZYX, как у Blockbench


def load(path):
    return json.load(open(path, encoding="utf-8"))


def skin_from_model(d):
    src = d["textures"][0]["source"].split(",", 1)[1]
    return Image.open(io.BytesIO(base64.b64decode(src))).convert("RGBA")


# ---------------- суставы: локоть, колено, бедро без «выломанного» угла ----------------
# Кость сгибается вокруг оси посреди своей толщины. На 90° у такого сустава внешний угол
# пустеет: верхняя коробка кончается, нижняя ушла вперёд — в игре локоть выглядит
# «вывернутым», с вырезом (жалоба 05.10.2026). Лечится сдвигом нижней кости НАРУЖУ сгиба
# ровно настолько, чтобы её торец дошёл до внешней грани верхней: угол становится сплошным,
# а лишнее уходит внутрь верхней коробки (его не видно). 0.1 пикселя не доводим — иначе
# торец лёг бы в одну плоскость с гранью верхней коробки и рябил бы.
JOINT_BONES = ("prfa_right_forearm", "plfa_left_forearm", "prfl_right_foreleg", "plfl_left_foreleg",
               "prl_right_leg", "pll_left_leg")


# Вторая беда сустава — рябь: при сгибе по X боковые грани предплечья лежат в ОДНОЙ плоскости
# с гранями плеча (то же голень/бедро, бедро/таз), и там, где коробки перекрываются, две текстуры
# мерцают тонкими полосками вдоль локтя. Нижние кости чуть уже — на 3% по толщине (≈0.05 пикселя):
# их грани уходят внутрь верхних, совпадающих плоскостей нет. На глаз разницы в толщине не видно.
JOINT_SCALE = {b: (0.97, 1.0, 0.97) for b in JOINT_BONES}


def diag(v):
    return [[v[0], 0, 0], [0, v[1], 0], [0, 0, v[2]]]


HINGE_PARENT = {"prfa_right_forearm": "pra_right_arm", "plfa_left_forearm": "pla_left_arm",
                "prfl_right_foreleg": "prl_right_leg", "plfl_left_foreleg": "pll_left_leg"}
HINGE_INSET = 0.06


def joint_offsets(d, pose, margin=0.1):
    groups = {g["name"]: g for g in d["groups"]}
    elems = {e["uuid"]: e for e in d["elements"]}
    def skin_box(gname):
        def find(node):
            if isinstance(node, dict):
                if node["uuid"] == groups[gname]["uuid"]:
                    for ch in node.get("children", []):
                        if isinstance(ch, str) and elems.get(ch, {}).get("name") == "skin": return elems[ch]
                for ch in node.get("children", []):
                    r = find(ch)
                    if r: return r
            return None
        for r in d["outliner"]:
            got = find(r)
            if got: return got
    out = {}
    for bone in JOINT_BONES:
        rot = pose.get(bone)
        if not rot: continue
        e = skin_box(bone)
        if e is None: continue
        R = euler(rot)
        dv = mv(R, [0, -1, 0])
        n = math.hypot(dv[0], dv[2])
        if n < 0.02: continue
        u = [-dv[0] / n, 0, -dv[2] / n]                     # наружу от сгиба
        if "leg" in bone:                                   # ноги стоят вплотную: вбок не двигаем, только вперёд/назад
            if abs(dv[2]) < 0.02: continue
            u = [0, 0, -1 if dv[2] > 0 else 1]
        P = groups[bone]["origin"]
        if bone in HINGE_PARENT:
            # Локоть и колено: сгиб вокруг нижнего ВНЕШНЕГО ребра верхней кости (Q). Тогда открытый торец
            # нижней кости уходит внутрь верхней, а открытый низ верхней закрывает тело нижней — дыр нет.
            pe = skin_box(HINGE_PARENT[bone])
            if pe is None: continue
            pf, pt = pe["from"], pe["to"]
            cx, cz = (pf[0] + pt[0]) / 2, (pf[2] + pt[2]) / 2
            hu = max((x - cx) * u[0] + (z - cz) * u[2] for x in (pf[0], pt[0]) for z in (pf[2], pt[2]))
            hu -= HINGE_INSET                                   # чуть внутрь — без общих плоскостей
            Q = [cx + u[0] * hu, pf[1] + HINGE_INSET, cz + u[2] * hu]
            qp = [Q[i] - P[i] for i in range(3)]
            rq = mv(R, qp)
            out[bone] = tuple(qp[i] - rq[i] for i in range(3))
            continue
        f, t = e["from"], e["to"]
        A = [(f[0] + t[0]) / 2, t[1], (f[2] + t[2]) / 2]     # ось кости на уровне торца
        cap = [(x, t[1], z) for x in (f[0], t[0]) for z in (f[2], t[2])]
        def sup(pts): return max((p[0] - A[0]) * u[0] + (p[2] - A[2]) * u[2] for p in pts)
        moved = [[mv(R, [c[i] - P[i] for i in range(3)])[i] + P[i] for i in range(3)] for c in cap]
        delta = sup(cap) - sup(moved) - margin
        if delta > 0: out[bone] = (u[0] * delta, 0.0, u[2] * delta)
    out.update(up_joint_offsets(d, pose, skin_box))
    return out


# Суставы «вверх»: шея (голова на груди), грудь на талии, талия на тазу. Кость стоит на соседе снизу
# и при наклоне приподнимает один край низа — в щель под подбородком/на пояснице видно фон
# (на скрине 05.10.2026 — светлая полоска под головой у «Триумфа»). Опускаем кость ровно на этот
# подъём (+0.05): низ ложится на соседа, противоположный край уходит внутрь — его не видно.
UP_JOINTS = {"h_ph_head": "pc_chest", "pc_chest": "pw_waist", "pw_waist": "phip_hip"}
UP_SCALE = (0.98, 1.0, 0.98)     # и чуть уже: иначе боковые грани легли бы в плоскость соседа и рябили


def up_joint_offsets(d, pose, skin_box):
    groups = {g["name"]: g for g in d["groups"]}
    out = {}
    for bone, below in UP_JOINTS.items():
        rot = pose.get(bone)
        if not rot or (abs(rot[0]) < 1 and abs(rot[2]) < 1): continue
        e, pe = skin_box(bone), skin_box(below)
        if e is None or pe is None: continue
        R = euler(rot)
        P = groups[bone]["origin"]
        f, t = e["from"], e["to"]
        top = pe["to"][1]
        x0, x1 = max(f[0], pe["from"][0]), min(t[0], pe["to"][0])
        z0, z1 = max(f[2], pe["from"][2]), min(t[2], pe["to"][2])
        if x0 >= x1 or z0 >= z1: continue
        nrm = mv(R, [0, -1, 0])
        if abs(nrm[1]) < 0.2: continue
        q = [mv(R, [f[0] - P[0], f[1] - P[1], f[2] - P[2]])[i] + P[i] for i in range(3)]
        def height(x, z): return q[1] - (nrm[0] * (x - q[0]) + nrm[2] * (z - q[2])) / nrm[1]
        lift = max(height(x, z) for x in (x0, x1) for z in (z0, z1)) - top
        if lift > 0.02: out[bone] = (0.0, -(lift + 0.05), 0.0)
    return out


def joint_scale(d, pose):
    """Сужение костей: нижние в сгибах — всегда, «верхние» суставы — когда их пришлось опустить."""
    sc = dict(JOINT_SCALE)
    for bone, off in joint_offsets(d, pose).items():
        if bone in UP_JOINTS and off[1] < 0: sc[bone] = UP_SCALE
    return sc


def collect(d, pose):
    groups = {g["uuid"]: g for g in d["groups"]}
    elems = {e["uuid"]: e for e in d["elements"]}
    jo = joint_offsets(d, pose)
    js = joint_scale(d, pose)
    out = []
    def walk(node, xf):
        g = groups[node["uuid"]]
        name = g["name"]
        if name in ("shadow", "tag_name"): return
        rot = [float(v) for v in (g.get("rotation") or [0, 0, 0])]
        add = pose.get(name, (0, 0, 0))
        off = pose.get("@root_pos", (0, 0, 0)) if name == "player_root" else jo.get(name, (0, 0, 0))
        R = euler([rot[i] + add[i] for i in range(3)])
        if name in js: R = mm(R, diag(js[name]))
        x2 = xf.then_local(R, g["origin"], off)
        for ch in node.get("children", []):
            if isinstance(ch, str):
                if ch in elems: out.append((elems[ch], x2, name))
            else:
                walk(ch, x2)
    for root in d["outliner"]:
        if isinstance(root, dict): walk(root, Xf())
    return out


# Порядок углов грани: левый-верх, правый-верх, правый-низ, левый-низ (как видит смотрящий на грань)
def face_quads(e):
    f, t = e["from"], e["to"]; inf = e.get("inflate", 0) or 0
    x0, y0, z0 = f[0] - inf, f[1] - inf, f[2] - inf
    x1, y1, z1 = t[0] + inf, t[1] + inf, t[2] + inf
    return {
        "north": [(x1, y1, z0), (x0, y1, z0), (x0, y0, z0), (x1, y0, z0)],
        "south": [(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)],
        "east":  [(x1, y1, z1), (x1, y1, z0), (x1, y0, z0), (x1, y0, z1)],
        "west":  [(x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x0, y0, z0)],
        "up":    [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
        "down":  [(x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)],
    }


# В паке BetterModel части тела — «трубки» из пиксельных граней, и у кусков в суставах торцов НЕТ
# (снято с build.zip 05.10.2026): плечо и бедро открыты снизу, предплечье и голень — сверху, таз
# открыт сверху, талия — с обоих концов, грудь — снизу. Голова закрыта. Открытый конец, вышедший
# наружу в сгибе, видно насквозь — это и есть «пустоты на сгибах». Предпросмотр рисует так же.
OPEN_ENDS = {
    "pra_right_arm": ("down",), "pla_left_arm": ("down",), "prl_right_leg": ("down",), "pll_left_leg": ("down",),
    "prfa_right_forearm": ("up",), "plfa_left_forearm": ("up",), "prfl_right_foreleg": ("up",), "plfl_left_foreleg": ("up",),
    "phip_hip": ("up",), "pw_waist": ("up", "down"), "pc_chest": ("down",),
}


def clip_floor(poly, y0):
    """Сазерленд–Ходжмен: часть многоугольника (мировые координаты) не ниже пола y0."""
    out = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        ina, inb = a[1] >= y0, b[1] >= y0
        if ina: out.append(a)
        if ina != inb:
            t = (y0 - a[1]) / (b[1] - a[1])
            out.append([a[k] + (b[k] - a[k]) * t for k in range(3)])
    return out


def render(d, pose, skin, yaw_deg=-28, scale=9, size=(300, 420), pitch_deg=0, floor=None):
    """floor — высота пола в пикселях модели: всё ниже не рисуется (как блок в игре), сам пол — светлым."""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    view = mm(rx(math.radians(-pitch_deg)), ry(math.radians(yaw_deg)))   # pitch > 0 — взгляд сверху
    def proj(p3): return (size[0] / 2 + p3[0] * scale * -1, size[1] - 30 - p3[1] * scale)
    if floor is not None:
        fq = [[-40, floor, -40], [40, floor, -40], [40, floor, 40], [-40, floor, 40]]
        ImageDraw.Draw(img).polygon([proj(mv(view, p)) for p in fq], fill=(214, 236, 236, 255))
    tris = []
    for e, xf, bone in collect(d, pose):
        for fname, quad in face_quads(e).items():
            fc = e["faces"].get(fname)
            if not fc or fc.get("texture") is None: continue
            if fname in OPEN_ENDS.get(bone, ()): continue      # как в паке BetterModel: торца нет
            world = [xf.apply(list(p)) for p in quad]
            clipped = None
            if floor is not None:
                cl = clip_floor(world, floor)
                if len(cl) < 3: continue
                clipped = [proj(mv(view, p)) for p in cl]
            pts3 = [mv(view, p) for p in world]
            # нормаль после поворотов; зритель смотрит из −Z
            a, b, c = pts3[0], pts3[1], pts3[3]
            u = [b[i] - a[i] for i in range(3)]; v = [c[i] - a[i] for i in range(3)]
            n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
            if n[2] <= 0: continue          # грань от зрителя (у лицевой при таком обходе n.z > 0)
            depth = sum(p[2] for p in pts3) / 4
            pts2 = [proj(p) for p in pts3]
            tris.append((depth, pts2, fc["uv"], e["name"], clipped))
    tris.sort(key=lambda t: -t[0])          # дальние первыми
    for depth, pts, uv, nm, clipped in tris:
        u0, v0, u1, v1 = uv
        su, sv = 64 / 64, 64 / 64
        # аффинное: экран → текстура по трём углам (лв, пв, лн)
        (X0, Y0), (X1, Y1), _, (X3, Y3) = pts
        A = [[X1 - X0, X3 - X0], [Y1 - Y0, Y3 - Y0]]
        det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
        if abs(det) < 1e-6: continue
        inv = [[A[1][1] / det, -A[0][1] / det], [-A[1][0] / det, A[0][0] / det]]
        # (s,t) = inv·(X−X0, Y−Y0); U = u0 + s·(u1−u0); V = v0 + t·(v1−v0)
        du, dv = (u1 - u0) * su, (v1 - v0) * sv
        a_ = inv[0][0] * du; b_ = inv[0][1] * du; c_ = u0 * su - a_ * X0 - b_ * Y0
        d_ = inv[1][0] * dv; e_ = inv[1][1] * dv; f_ = v0 * sv - d_ * X0 - e_ * Y0
        tex = skin.transform(size, Image.AFFINE, (a_, b_, c_, d_, e_, f_), resample=Image.NEAREST)
        mask = Image.new("L", size, 0)
        ImageDraw.Draw(mask).polygon(clipped or pts, fill=255)
        alpha = tex.getchannel("A").point(lambda v: 255 if v > 0 else 0)
        from PIL import ImageChops
        img.paste(tex, (0, 0), ImageChops.multiply(mask, alpha))
    return img


def preview(model, out, skinpath=None):
    d = load(model)
    skin = Image.open(skinpath).convert("RGBA") if skinpath else skin_from_model(d)
    poses = list(POSES.items())
    cell_w, cell_h = 300, 440
    sheet = Image.new("RGBA", (cell_w * 6, cell_h * 2 * ((len(poses) + 5) // 6)), (238, 232, 246, 255))
    dr = ImageDraw.Draw(sheet)
    from PIL import ImageFont
    try: font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
    except Exception: font = None
    for i, (name, pose) in enumerate(poses):
        col, row = i % 6, i // 6
        for k, yaw in enumerate((-28, 62)):
            im = render(d, pose, skin, yaw_deg=yaw)
            sheet.alpha_composite(im, (col * cell_w, (row * 2 + k) * cell_h))
        dr.text((col * cell_w + 12, row * 2 * cell_h + 10), NAMES.get(name, name), fill=(60, 30, 90, 255), font=font)
    sheet.save(out)
    print("сохранено:", out)


def write(model):
    d = load(model)
    groups = {g["name"]: g["uuid"] for g in d["groups"]}
    d["animations"] = [a for a in d.get("animations", []) if not a["name"].startswith("statue_")]
    for name, pose in POSES.items():
        animators = {}
        for bone, rot in pose.items():
            if bone.startswith("@"): continue
            gid = groups[bone]
            kfs = []
            for t in (0, 1):
                kfs.append({"channel": "rotation", "data_points": [{"x": str(rot[0]), "y": str(rot[1]), "z": str(rot[2])}],
                            "uuid": str(uuid.uuid4()), "time": t, "color": -1, "interpolation": "linear"})
            animators[gid] = {"name": bone, "type": "bone", "rotation_global": False,
                              "quaternion_interpolation": False, "keyframes": kfs}
        for bone, sc in joint_scale(d, pose).items():
            if bone not in groups: continue
            gid = groups[bone]
            kfs = [{"channel": "scale", "data_points": [{"x": str(sc[0]), "y": str(sc[1]), "z": str(sc[2])}],
                    "uuid": str(uuid.uuid4()), "time": t, "color": -1, "interpolation": "linear"} for t in (0, 1)]
            animators.setdefault(gid, {"name": bone, "type": "bone", "rotation_global": False,
                                       "quaternion_interpolation": False, "keyframes": []})["keyframes"] += kfs
        for bone, off in joint_offsets(d, pose).items():
            gid = groups[bone]
            kfs = [{"channel": "position", "data_points": [{"x": str(round(off[0], 4)), "y": str(round(off[1], 4)), "z": str(round(off[2], 4))}],
                    "uuid": str(uuid.uuid4()), "time": t, "color": -1, "interpolation": "linear"} for t in (0, 1)]
            animators.setdefault(gid, {"name": bone, "type": "bone", "rotation_global": False,
                                       "quaternion_interpolation": False, "keyframes": []})["keyframes"] += kfs
        if "@root_pos" in pose and False:
            # Опускание всей модели (сидит, рыцарь) больше НЕ пишется в анимацию: на статуе-манекене
            # BetterModel ключ позиции корня не применял (05.10.2026) — сидящие висели в воздухе.
            # Плагин сам ставит модель ниже: FameService.poseDrop() = −@root_pos / 16 блока.
            p = pose["@root_pos"]
            gid = groups["player_root"]
            kfs = [{"channel": "position", "data_points": [{"x": str(p[0]), "y": str(p[1]), "z": str(p[2])}],
                    "uuid": str(uuid.uuid4()), "time": t, "color": -1, "interpolation": "linear"} for t in (0, 1)]
            animators.setdefault(gid, {"name": "player_root", "type": "bone", "rotation_global": False,
                                       "quaternion_interpolation": False, "keyframes": []})["keyframes"] += kfs
        d["animations"].append({"uuid": str(uuid.uuid4()), "name": name, "loop": "loop", "override": False,
                                "length": 1, "snapping": 24, "selected": False, "group_name": "",
                                "anim_time_update": "", "blend_weight": "", "start_delay": "", "loop_delay": "",
                                "animators": animators})
    json.dump(d, open(model, "w", encoding="utf-8"), ensure_ascii=False)
    print("позы записаны:", ", ".join(POSES))
    drops = {n: -p["@root_pos"][1] for n, p in POSES.items() if "@root_pos" in p}
    if drops: print("опускание (впиши в FameService.poseDrop, пикселей):", drops)


# ---------------- проверка: не проходят ли части тела друг сквозь друга ----------------
# В игре пересечение видно рябью: две текстуры спорят за один пиксель (кулак «в лице», кисти друг в друге).
# Поэтому позы проверяются боксами: внутренний слой скина разных костей не должен пересекаться
# (соседние по суставу пары — плечо и предплечье, грудь и плечо и т. п. — не считаются).
ADJACENT = {
    frozenset(p) for p in [
        ("phip_hip", "pw_waist"), ("pw_waist", "pc_chest"), ("phip_hip", "pc_chest"), ("pc_chest", "h_ph_head"),
        ("pc_chest", "pra_right_arm"), ("pc_chest", "pla_left_arm"),
        ("pra_right_arm", "prfa_right_forearm"), ("pla_left_arm", "plfa_left_forearm"),
        ("phip_hip", "prl_right_leg"), ("phip_hip", "pll_left_leg"), ("prl_right_leg", "pll_left_leg"),
        ("prl_right_leg", "prfl_right_foreleg"), ("pll_left_leg", "plfl_left_foreleg"),
    ]
}


def boxes(d, pose, layer="skin"):
    """[(кость, центр, оси, полуразмеры)] — ориентированные боксы элементов слоя в позе."""
    groups = {g["uuid"]: g for g in d["groups"]}
    elems = {e["uuid"]: e for e in d["elements"]}
    jo = joint_offsets(d, pose)
    js = joint_scale(d, pose)
    out = []
    def walk(node, xf):
        g = groups[node["uuid"]]
        name = g["name"]
        if name in ("shadow", "tag_name"): return
        rot = [float(v) for v in (g.get("rotation") or [0, 0, 0])]
        add = pose.get(name, (0, 0, 0))
        off = pose.get("@root_pos", (0, 0, 0)) if name == "player_root" else jo.get(name, (0, 0, 0))
        M = euler([rot[i] + add[i] for i in range(3)])
        if name in js: M = mm(M, diag(js[name]))
        x2 = xf.then_local(M, g["origin"], off)
        for ch in node.get("children", []):
            if isinstance(ch, str):
                e = elems.get(ch)
                if e is None or e["name"] != layer: continue
                inf = e.get("inflate", 0) or 0
                f, t = e["from"], e["to"]
                mid = [(f[i] + t[i]) / 2 for i in range(3)]
                half = [(t[i] - f[i]) / 2 + inf for i in range(3)]
                axes = []
                for j in range(3):
                    col = [x2.R[0][j], x2.R[1][j], x2.R[2][j]]
                    n = math.sqrt(sum(c * c for c in col))
                    axes.append([c / n for c in col]); half[j] *= n
                out.append((name, x2.apply(mid), axes, half))
            else:
                walk(ch, x2)
    for root in d["outliner"]:
        if isinstance(root, dict): walk(root, Xf())
    return out


def overlap(a, b):
    """Глубина взаимного проникновения двух боксов (>0 — пересекаются), по теореме о разделяющей оси."""
    _, ca, A, ha = a
    _, cb, B, hb = b
    def dot(u, v): return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]
    def cross(u, v): return [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
    t = [cb[i] - ca[i] for i in range(3)]
    best = 1e9
    for L in A + B + [cross(x, y) for x in A for y in B]:
        n = math.sqrt(dot(L, L))
        if n < 1e-6: continue
        L = [v / n for v in L]
        ra = sum(abs(dot(A[i], L)) * ha[i] for i in range(3))
        rb = sum(abs(dot(B[i], L)) * hb[i] for i in range(3))
        best = min(best, ra + rb - abs(dot(t, L)))
        if best < 0: return best
    return best


# Задуманные касания: часть тела «лежит» на другой. Глубина — ровно около 1 пикселя: при 0–0.5 грань
# предплечья совпала бы по плоскости с гранью тела или его второго слоя (+0.25) и рябила бы.
CONTACT = {
    "statue_chief": {frozenset(p) for p in [("prfa_right_forearm", "phip_hip"), ("prfa_right_forearm", "pw_waist"),
                                           ("plfa_left_forearm", "phip_hip"), ("plfa_left_forearm", "pw_waist")]},
}
CONTACT_BAND = (0.75, 1.25)
# Касания, которых не видно вовсе: голень, поднятая шарниром колена, уходит внутрь таза (у таза есть дно).
HIDDEN_OK = {frozenset(p) for p in [("prfl_right_foreleg", "phip_hip"), ("plfl_left_foreleg", "phip_hip")]}


def collisions(d, pose, layer="skin", tol=0.05, allow=()):
    bx = boxes(d, pose, layer)
    hits = []
    for i in range(len(bx)):
        for j in range(i + 1, len(bx)):
            a, b = bx[i], bx[j]
            if a[0] == b[0] or frozenset((a[0], b[0])) in ADJACENT: continue
            o = overlap(a, b)
            # верх плеча у самой головы задевает её и в ванили — это не брак, если неглубоко
            lim = 0.65 if {a[0], b[0]} & {"h_ph_head"} and {a[0], b[0]} & {"pra_right_arm", "pla_left_arm"} else tol
            if frozenset((a[0], b[0])) in HIDDEN_OK: continue
            if frozenset((a[0], b[0])) in allow:
                if o > tol and not (CONTACT_BAND[0] <= o <= CONTACT_BAND[1]): hits.append((a[0], b[0], o))
            elif o > lim: hits.append((a[0], b[0], o))
    return hits


def check(model):
    d = load(model)
    bad = 0
    for name, pose in POSES.items():
        hits = collisions(d, pose, allow=CONTACT.get(name, ()))
        mark = "OK " if not hits else "!! "
        bad += bool(hits)
        print(mark + NAMES.get(name, name).ljust(14) + "  ".join(f"{a}×{b} {o:.2f}px" for a, b, o in hits))
    print("с пересечениями:", bad, "из", len(POSES))


if __name__ == "__main__":
    if sys.argv[1] == "preview": preview(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    elif sys.argv[1] == "write": write(sys.argv[2])
    elif sys.argv[1] == "check": check(sys.argv[2])
