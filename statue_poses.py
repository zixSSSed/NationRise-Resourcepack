# -*- coding: utf-8 -*-
"""Позы статуй «Аллеи славы» (04.10.2026): задание поз, предпросмотр и запись в модель BetterModel.

Модель — стандартный скелет игрока BetterModel (plugins/BetterModel/players/steve.bbmodel): бёдра,
талия, грудь, голова, плечо+предплечье, бедро+голень. Позы — анимации «statue_*» (держат кадр),
геометрию не трогаем, поэтому ресурспак моделей пересобирать не нужно.

Оси (проверено по встроенной анимации roll): перед модели — −Z (грань north = лицо);
правая рука — +X. Поворот кости X<0 наклоняет вперёд (к лицу); для свисающей руки/ноги X>0
выносит её вперёд. Z>0 у правой руки — в сторону (наружу), у левой наружу — Z<0.

  py -3.13 statue_poses.py preview <steve.bbmodel> <out.png> [skin.png]
  py -3.13 statue_poses.py write   <steve.bbmodel>          — дописать/обновить анимации statue_*
"""
import base64, io, json, math, sys, uuid
from PIL import Image, ImageDraw

# ---- позы: кость -> (x, y, z) градусы; "@root_pos" — смещение корня (пиксели модели) ----
POSES = {
    # Победитель: подбородок вверх, правая рука вскинута к небу, левая — кулак на поясе.
    "statue_victory": {
        "h_ph_head": (14, 12, 0),
        "pc_chest": (4, 6, 0),
        "pra_right_arm": (172, 0, 10), "prfa_right_forearm": (6, 0, 0),
        "pla_left_arm": (-18, 0, -38), "plfa_left_forearm": (82, 0, 0),
        "prl_right_leg": (-4, 0, 5), "pll_left_leg": (10, 0, -5), "plfl_left_foreleg": (-10, 0, 0),
    },
    # Отдание чести: прямая стойка, правая ладонь у виска, левая рука по шву.
    "statue_salute": {
        "h_ph_head": (2, 0, 0),
        "pra_right_arm": (55, -55, 55), "prfa_right_forearm": (125, 0, 0),
        "pla_left_arm": (0, 0, -3),
    },
    # Рыцарь на одном колене: правое колено в землю, левая нога согнута, голова склонена.
    "statue_knight": {
        "@root_pos": (0, -4.6, 0),
        "pc_chest": (-6, 0, 0),
        "h_ph_head": (-14, 0, 0),
        "prl_right_leg": (-8, 0, 0), "prfl_right_foreleg": (-84, 0, 0),
        "pll_left_leg": (84, 0, 0), "plfl_left_foreleg": (-86, 0, 0),
        "pra_right_arm": (40, 0, -28), "prfa_right_forearm": (105, 0, 0),
        "pla_left_arm": (55, 0, 6), "plfa_left_forearm": (35, 0, 0),
    },
    # Руки на груди: уверенная стойка, ноги на ширине плеч, взгляд чуть сверху вниз.
    "statue_crossed": {
        "h_ph_head": (-4, -8, 0),
        "pra_right_arm": (38, 0, -20), "prfa_right_forearm": (92, 0, -38),
        "pla_left_arm": (38, 0, 20), "plfa_left_forearm": (92, 0, 38),
        "prl_right_leg": (0, 0, 7), "pll_left_leg": (0, 0, -7),
    },
    # Полководец: обе руки на рукояти меча перед собой, остриё в землю.
    "statue_commander": {
        "h_ph_head": (6, 0, 0),
        "pra_right_arm": (30, 0, -14), "prfa_right_forearm": (28, 0, 0),
        "pla_left_arm": (30, 0, 14), "plfa_left_forearm": (28, 0, 0),
        "prl_right_leg": (0, 0, 7), "pll_left_leg": (0, 0, -7),
    },
    # Приветствие: правая рука поднята ладонью вперёд, левая на поясе.
    "statue_wave": {
        "h_ph_head": (6, -12, 0),
        "pc_chest": (0, -6, 0),
        "pra_right_arm": (150, 0, 42), "prfa_right_forearm": (25, 0, 0),
        "pla_left_arm": (-18, 0, -38), "plfa_left_forearm": (82, 0, 0),
        "pll_left_leg": (8, 0, -4), "plfl_left_foreleg": (-10, 0, 0),
    },
    # Знаменосец: правая рука с древком вверх, левая — ладонь на груди, шаг вперёд.
    "statue_banner": {
        "h_ph_head": (10, 0, 0),
        "pra_right_arm": (125, 0, 12), "prfa_right_forearm": (18, 0, 0),
        "pla_left_arm": (35, 0, 18), "plfa_left_forearm": (100, 0, 30),
        "prl_right_leg": (-14, 0, 0), "pll_left_leg": (18, 0, 0), "plfl_left_foreleg": (-14, 0, 0),
    },
    # Мыслитель: подбородок на кулаке, вторая рука поддерживает локоть.
    "statue_thinker": {
        "h_ph_head": (-10, 0, 0),
        "pc_chest": (-6, 0, 0),
        "pra_right_arm": (55, 0, -12), "prfa_right_forearm": (128, 0, 0),
        "pla_left_arm": (38, 0, 22), "plfa_left_forearm": (88, 0, 34),
        "prl_right_leg": (4, 0, 4), "pll_left_leg": (-8, 0, -8), "plfl_left_foreleg": (14, 0, 0),
    },
}

NAMES = {
    "statue_victory": "Победитель", "statue_salute": "Честь", "statue_knight": "Рыцарь",
    "statue_crossed": "Руки на груди", "statue_commander": "Полководец", "statue_wave": "Приветствие",
    "statue_banner": "Знаменосец", "statue_thinker": "Мыслитель",
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


def collect(d, pose):
    groups = {g["uuid"]: g for g in d["groups"]}
    elems = {e["uuid"]: e for e in d["elements"]}
    out = []
    def walk(node, xf):
        g = groups[node["uuid"]]
        name = g["name"]
        if name in ("shadow", "tag_name"): return
        rot = [float(v) for v in (g.get("rotation") or [0, 0, 0])]
        add = pose.get(name, (0, 0, 0))
        off = pose.get("@root_pos", (0, 0, 0)) if name == "player_root" else (0, 0, 0)
        R = euler([rot[i] + add[i] for i in range(3)])
        x2 = xf.then_local(R, g["origin"], off)
        for ch in node.get("children", []):
            if isinstance(ch, str):
                if ch in elems: out.append((elems[ch], x2))
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


def render(d, pose, skin, yaw_deg=-28, scale=9, size=(300, 420)):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    view = ry(math.radians(yaw_deg))
    tris = []
    for e, xf in collect(d, pose):
        for fname, quad in face_quads(e).items():
            fc = e["faces"].get(fname)
            if not fc or fc.get("texture") is None: continue
            pts3 = [mv(view, xf.apply(list(p))) for p in quad]
            # нормаль после поворотов; зритель смотрит из −Z
            a, b, c = pts3[0], pts3[1], pts3[3]
            u = [b[i] - a[i] for i in range(3)]; v = [c[i] - a[i] for i in range(3)]
            n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
            if n[2] <= 0: continue          # грань от зрителя (у лицевой при таком обходе n.z > 0)
            depth = sum(p[2] for p in pts3) / 4
            pts2 = [(size[0] / 2 + p[0] * scale * -1, size[1] - 30 - p[1] * scale) for p in pts3]
            tris.append((depth, pts2, fc["uv"], e["name"]))
    tris.sort(key=lambda t: -t[0])          # дальние первыми
    for depth, pts, uv, nm in tris:
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
        ImageDraw.Draw(mask).polygon(pts, fill=255)
        alpha = tex.getchannel("A").point(lambda v: 255 if v > 0 else 0)
        from PIL import ImageChops
        img.paste(tex, (0, 0), ImageChops.multiply(mask, alpha))
    return img


def preview(model, out, skinpath=None):
    d = load(model)
    skin = Image.open(skinpath).convert("RGBA") if skinpath else skin_from_model(d)
    poses = list(POSES.items())
    cell_w, cell_h = 300, 440
    sheet = Image.new("RGBA", (cell_w * 4, cell_h * 2 * ((len(poses) + 3) // 4)), (238, 232, 246, 255))
    dr = ImageDraw.Draw(sheet)
    from PIL import ImageFont
    try: font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
    except Exception: font = None
    for i, (name, pose) in enumerate(poses):
        col, row = i % 4, i // 4
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
        if "@root_pos" in pose:
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


if __name__ == "__main__":
    if sys.argv[1] == "preview": preview(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    elif sys.argv[1] == "write": write(sys.argv[2])
