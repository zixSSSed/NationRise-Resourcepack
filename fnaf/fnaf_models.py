"""Модели FNAF для BetterModel (10.10.2026): аниматроники, генератор, ворота выхода.

Модели собираются кодом, а не руками: так у всех аниматроников один скелет и одни анимации,
а раскраски — просто другая палитра. Текстура каждой модели — атлас 128×128 из плиток 16×16:
материал (мех, металл, пластик…) в трёх оттенках — для боков, верха и низа куба, чтобы форма
читалась и без игрового освещения. Мелкие детали (глаза, зубы, нос, брови, бабочка) — отдельные
кубы, а не рисунок: так они видны издалека и в темноте.

Скелет (имена костей — метки BetterModel):
  root → body → h_head (голова смотрит за взглядом) → jaw, glow_eyes (зрачки светятся в темноте)
       → arm_l/arm_r → forearm_* → hand_*;  leg_l/leg_r → shin_*
Рост ~2,8 блока (45 px, 16 px = блок). Лицом к −Z (север), как модели игроков.

Анимации: idle, walk, run (зациклены), attack, jumpscare, stun (один раз).

Запуск: py -3.13 fnaf_models.py [папка вывода]  (по умолчанию bettermodel/models рядом со скриптом)
"""
import base64
import io
import json
import math
import os
import random
import sys
import uuid

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "bettermodel", "models")


def uid():
    return str(uuid.uuid4())


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


# ----------------------------------------------------------------- текстура-атлас

class Atlas:
    """128×128, плитки 16×16. Материал → три плитки (бок, верх, низ)."""

    def __init__(self, seed):
        self.img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        self.slots = {}
        self.next = 0
        self.rnd = random.Random(seed)

    def _slot(self):
        i = self.next
        self.next += 1
        if i >= 64:
            raise RuntimeError("атлас переполнен")
        return (i % 8) * 16, (i // 8) * 16

    def material(self, name, color, kind="fur"):
        if name in self.slots:
            return name
        base = hexrgb(color) if isinstance(color, str) else color
        tiles = {}
        for face, f in (("side", 1.0), ("up", 1.12), ("down", 0.72)):
            x0, y0 = self._slot()
            self._paint(x0, y0, shade(base, f), kind)
            tiles[face] = (x0, y0)
        self.slots[name] = tiles
        return name

    def _paint(self, x0, y0, c, kind):
        d = ImageDraw.Draw(self.img)
        r = self.rnd
        for y in range(16):
            for x in range(16):
                if kind == "fur":
                    n = r.uniform(0.9, 1.08)
                    if r.random() < 0.08:
                        n *= 0.84
                elif kind == "metal":
                    n = r.uniform(0.94, 1.04) * (1.06 if (x + y) % 7 == 0 else 1.0)
                elif kind == "plastic":
                    n = r.uniform(0.97, 1.02)
                elif kind == "glass":
                    n = 1.0 + 0.25 * max(0, 1 - ((x - 5) ** 2 + (y - 5) ** 2) / 18.0)
                elif kind == "worn":
                    n = r.uniform(0.8, 1.06)
                    if r.random() < 0.14:
                        n *= 0.55
                else:
                    n = 1.0
                edge = 0.86 if x in (0, 15) or y in (0, 15) else 1.0
                px = shade(c, n * edge)
                d.point((x0 + x, y0 + y), fill=px + (255,))
        if kind == "metal":   # заклёпки по углам
            for (x, y) in ((2, 2), (13, 2), (2, 13), (13, 13)):
                d.point((x0 + x, y0 + y), fill=shade(c, 1.35) + (255,))
                d.point((x0 + x + 1, y0 + y + 1), fill=shade(c, 0.6) + (255,))

    def special(self, name, painter):
        """Плитка с рисунком (зубы, надпись на нагруднике, решётка, панель…), одна на все грани."""
        if name in self.slots:
            return name
        x0, y0 = self._slot()
        tile = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        painter(ImageDraw.Draw(tile), tile)
        self.img.paste(tile, (x0, y0))
        self.slots[name] = {"side": (x0, y0), "up": (x0, y0), "down": (x0, y0)}
        return name

    def special_big(self, name, painter):
        """Плитка 32×32 (четыре слота квадратом) — для надписей."""
        if name in self.slots:
            return name
        # ищем свободный квадрат 2×2 в сетке 8×8, начиная с конца атласа
        for row in range(6, -1, -2):
            for col in range(6, -1, -2):
                idx = [row * 8 + col, row * 8 + col + 1, (row + 1) * 8 + col, (row + 1) * 8 + col + 1]
                if all(i >= self.next for i in idx) and not getattr(self, "_big_used", set()) & set(idx):
                    self._big_used = getattr(self, "_big_used", set()) | set(idx)
                    x0, y0 = col * 16, row * 16
                    tile = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
                    painter(ImageDraw.Draw(tile), tile)
                    self.img.paste(tile, (x0, y0))
                    self.slots[name] = {"side": (x0, y0), "up": (x0, y0), "down": (x0, y0), "big": True}
                    return name
        raise RuntimeError("нет места под большую плитку")

    def data_uri(self):
        buf = io.BytesIO()
        clean = Image.new("RGBA", self.img.size)
        clean.putdata(list(self.img.getdata()))
        clean.save(buf, "PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# ----------------------------------------------------------------- модель

class Model:
    def __init__(self, name, seed=1):
        self.name = name
        self.atlas = Atlas(seed)
        self.elements = []
        self.root = []
        self.groups = {}
        self.animations = []

    def group(self, name, origin, parent=None, rotation=None):
        g = {"name": name, "origin": [round(v, 4) for v in origin], "color": 0, "uuid": uid(), "export": True,
             "isOpen": True, "locked": False, "visibility": True, "autouv": 0, "children": []}
        if rotation:
            g["rotation"] = list(rotation)
        (self.groups[parent]["children"] if parent else self.root).append(g)
        self.groups[name] = g
        return name

    def cube(self, group, frm, to, mat, rotation=None, origin=None, name="cube"):
        tiles = self.atlas.slots[mat]
        span = 32 if tiles.get("big") else 16
        faces = {}
        for f in ("north", "south", "east", "west", "up", "down"):
            tx, ty = tiles["up" if f == "up" else "down" if f == "down" else "side"]
            if tiles.get("big") and f != "north":
                faces[f] = {"uv": [tx + 1, ty + 1, tx + 3, ty + 3], "texture": 0}
            else:
                faces[f] = {"uv": [tx + 0.5, ty + 0.5, tx + span - 0.5, ty + span - 0.5], "texture": 0}
        e = {"name": name, "box_uv": False, "rescale": False, "locked": False, "render_order": "default",
             "allow_mirror_modeling": True, "from": [round(v, 4) for v in frm], "to": [round(v, 4) for v in to],
             "autouv": 0, "color": 0, "origin": [round(v, 4) for v in (origin or frm)], "faces": faces,
             "type": "cube", "uuid": uid()}
        if rotation:
            e["rotation"] = list(rotation)
            e["origin"] = [round(v, 4) for v in (origin or [(a + b) / 2 for a, b in zip(frm, to)])]
        self.elements.append(e)
        self.groups[group]["children"].append(e["uuid"])
        return e

    def box(self, group, center, size, mat, **kw):
        cx, cy, cz = center
        sx, sy, sz = size
        return self.cube(group, (cx - sx / 2, cy - sy / 2, cz - sz / 2), (cx + sx / 2, cy + sy / 2, cz + sz / 2), mat, **kw)

    # ---- анимации ----

    def animation(self, name, length, loop, tracks):
        """tracks: {bone: {channel: [(time, (x,y,z), interp?)]}}"""
        animators = {}
        for bone, chans in tracks.items():
            if bone not in self.groups:
                continue
            kfs = []
            for ch, frames in chans.items():
                for fr in frames:
                    t, v = fr[0], fr[1]
                    interp = fr[2] if len(fr) > 2 else "catmullrom"
                    kfs.append({"channel": ch, "data_points": [{"x": str(round(v[0], 3)), "y": str(round(v[1], 3)),
                                                                "z": str(round(v[2], 3))}],
                                "uuid": uid(), "time": round(t, 4), "color": -1, "interpolation": interp})
            animators[self.groups[bone]["uuid"]] = {"name": bone, "type": "bone", "keyframes": kfs}
        # Имена с приставкой fn_: «idle» и «walk» BetterModel играет сам (встроенные анимации трекера)
        # со своим приоритетом — и они перебивали наши вызовы, модель вечно стояла в idle.
        self.animations.append({"uuid": uid(), "name": "fn_" + name, "loop": loop, "override": False, "length": length,
                                "snapping": 24, "selected": False, "saved": True, "path": "", "anim_time_update": "",
                                "blend_weight": "", "start_delay": "", "loop_delay": "", "animators": animators})

    def to_json(self):
        return {
            "meta": {"format_version": "4.10", "model_format": "free", "box_uv": False},
            "name": self.name, "model_identifier": "", "visible_box": [2, 3, 0], "variable_placeholders": "",
            "variable_placeholder_buttons": [], "timeline_setups": [], "unhandled_root_fields": {},
            "resolution": {"width": 128, "height": 128},
            "elements": self.elements, "outliner": self.root,
            "textures": [{"path": "", "name": self.name + ".png", "folder": "", "namespace": "", "id": "0",
                          "width": 128, "height": 128, "uv_width": 128, "uv_height": 128, "particle": False,
                          "layers_enabled": False, "sync_to_project": "", "render_mode": "default",
                          "render_sides": "auto", "frame_time": 1, "frame_order_type": "loop", "frame_order": "",
                          "frame_interpolate": False, "visible": True, "internal": True, "saved": False,
                          "uuid": uid(), "relative_path": "", "source": self.atlas.data_uri()}],
            "animations": self.animations,
        }

    def save(self, folder):
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, self.name + ".bbmodel")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_json(), f, ensure_ascii=False)
        return path


# ----------------------------------------------------------------- рисованные плитки

def teeth(d, img):
    d.rectangle((0, 0, 15, 15), fill=(232, 226, 205, 255))
    for x in range(0, 16, 3):
        d.line((x, 0, x, 15), fill=(120, 110, 90, 255))


def sharp_teeth(d, img):
    d.rectangle((0, 0, 15, 15), fill=(40, 20, 20, 255))
    for x in range(0, 16, 4):
        d.polygon([(x, 0), (x + 3, 0), (x + 1.5, 13)], fill=(238, 232, 214, 255))


def bib(text, ink):
    def paint(d, img):
        d.rectangle((0, 0, 15, 15), fill=(245, 242, 236, 255))
        d.rectangle((0, 0, 15, 15), outline=(200, 190, 175, 255))
        # 3 строки «пиксельных букв»: имитация надписи LET'S EAT!!! цветными штрихами
        colors = ink
        y = 3
        for row in text:
            x = 2
            for i, ch in enumerate(row):
                if ch == " ":
                    x += 2
                    continue
                c = colors[i % len(colors)]
                d.rectangle((x, y, x, y + 2), fill=c)
                if ch in "EATLSPRY!":
                    d.point((x + 1, y), fill=c)
                    d.point((x + 1, y + 2 if ch != "!" else y), fill=c)
                x += 2
            y += 5
    return paint


FONT3x5 = {
    "L": ["100", "100", "100", "100", "111"], "E": ["111", "100", "110", "100", "111"],
    "T": ["111", "010", "010", "010", "010"], "S": ["111", "100", "111", "001", "111"],
    "A": ["010", "101", "111", "101", "101"], "P": ["110", "101", "110", "100", "100"],
    "R": ["110", "101", "110", "101", "101"], "Y": ["101", "101", "010", "010", "010"],
    "!": ["1", "1", "1", "0", "1"], "'": ["1", "1", "0", "0", "0"],
}


def bib_big(lines):
    """Нагрудник 32×32: белый, кайма, надпись разноцветными буквами 3×5 в две строки."""
    ink = [(150, 60, 170), (232, 120, 34), (58, 150, 205), (210, 58, 58), (70, 160, 70)]

    def paint(d, img):
        d.rectangle((0, 0, 31, 31), fill=(246, 243, 236, 255))
        d.rectangle((0, 0, 31, 31), outline=(196, 186, 170, 255))
        d.rectangle((1, 1, 30, 30), outline=(230, 224, 212, 255))
        y = 7
        k = 0
        for line in lines:
            width = sum(len(FONT3x5.get(ch, ["000"])[0]) + 1 for ch in line) - 1
            x = (32 - width) // 2
            for ch in line:
                glyph = FONT3x5.get(ch)
                if glyph is None:
                    x += 2
                    continue
                c = ink[k % len(ink)] + (255,)
                k += 1
                for gy, row in enumerate(glyph):
                    for gx, bit in enumerate(row):
                        if bit == "1":
                            d.point((x + gx, y + gy), fill=c)
                x += len(glyph[0]) + 1
            y += 9
    return paint


def vents(d, img):
    d.rectangle((0, 0, 15, 15), fill=(70, 72, 70, 255))
    for y in range(2, 15, 3):
        d.rectangle((2, y, 13, y + 1), fill=(22, 22, 22, 255))


def panel(d, img):
    d.rectangle((0, 0, 15, 15), fill=(54, 58, 56, 255))
    d.ellipse((1, 2, 7, 8), fill=(225, 220, 200, 255), outline=(20, 20, 20, 255))
    d.line((4, 5, 6, 3), fill=(190, 30, 30, 255))
    d.ellipse((9, 2, 15, 8), fill=(225, 220, 200, 255), outline=(20, 20, 20, 255))
    d.line((12, 5, 10, 3), fill=(190, 30, 30, 255))
    for x in (2, 6, 10):
        d.rectangle((x, 11, x + 2, 13), fill=(30, 30, 30, 255))
        d.point((x + 1, 12), fill=(200, 60, 40, 255))


def hazard(d, img):
    for x in range(-16, 16):
        for y in range(16):
            c = (230, 180, 30, 255) if ((x + y) // 4) % 2 == 0 else (25, 25, 25, 255)
            if 0 <= x < 16:
                d.point((x, y), fill=c)


def lamp_on(d, img):
    d.rectangle((0, 0, 15, 15), fill=(255, 214, 90, 255))
    d.ellipse((3, 3, 10, 10), fill=(255, 250, 215, 255))


def lamp_off(d, img):
    d.rectangle((0, 0, 15, 15), fill=(70, 58, 30, 255))
    d.ellipse((3, 3, 9, 9), fill=(105, 92, 55, 255))


def wires(d, img):
    d.rectangle((0, 0, 15, 15), fill=(35, 33, 30, 255))
    for i, c in enumerate(((170, 30, 30), (40, 60, 160), (190, 160, 40))):
        x = 3 + i * 4
        for y in range(16):
            d.point((x + (1 if (y // 3) % 2 else 0), y), fill=c + (255,))


def tear(base):
    def paint(d, img):
        c = hexrgb(base)
        d.rectangle((0, 0, 15, 15), fill=c + (255,))
        d.polygon([(4, 2), (12, 5), (10, 12), (3, 10)], fill=(25, 22, 20, 255))
        d.line((5, 6, 9, 9), fill=(150, 150, 150, 255))
    return paint


# ----------------------------------------------------------------- аниматроник

def animatronic(spec):
    """Аниматроник v2: грушевидный корпус с животом, крупная покатая голова, веки, объёмная морда,
    сегментированные конечности с металлическими суставами, ладонь с пальцами."""
    m = Model(spec["id"], seed=sum(map(ord, spec["id"])))
    a = m.atlas
    P = spec["palette"]
    kind = spec.get("kind", "fur")
    a.material("main", P["main"], kind)
    a.material("light", P["light"], kind)
    a.material("dark", P.get("dark", shade(hexrgb(P["main"]), 0.62)), kind)
    a.material("lid", shade(hexrgb(P["main"]), 0.85), kind)
    a.material("metal", "#5d6266", "metal")
    a.material("metal_dark", "#34383b", "metal")
    a.material("black", "#151515", "plastic")
    a.material("eye", P.get("eye_white", "#ece8de"), "plastic")
    a.material("pupil", P["pupil"], "glass")
    a.material("nose", P.get("nose", "#1c1210"), "plastic")
    a.material("cheek", P.get("cheek", "#e48a9a"), "plastic")
    a.material("pants", P.get("pants", "#a87d55"), "fur")
    a.material("beak", P.get("beak", "#e98a1c"), "plastic")
    a.material("prop", P.get("prop", "#2a2a2a"), "plastic")
    a.material("prop2", P.get("prop2", "#9a9a9a"), "metal")
    a.special("teeth", sharp_teeth if spec.get("sharp") else teeth)
    if spec.get("bib"):
        a.special_big("bib", bib_big(spec["bib"]))
    if spec.get("worn"):
        a.special("tear", tear(P["main"]))
        a.special("wires", wires)

    W = spec.get("width", 1.0)
    T = spec.get("thin", 1.0)          # худоба конечностей (Спрингтрап, Фокси)
    m.group("root", (0, 0, 0))
    m.group("body", (0, 18, 0), "root")

    # ---------------- ноги ----------------
    for side, sx in (("l", 1), ("r", -1)):
        x = 3.9 * sx
        leg = m.group(f"leg_{side}", (x, 18.5, 0), "root")
        lm = "pants" if spec.get("shorts") else "main"
        m.box(leg, (x, 15.0, 0), (6.4 * T, 6.0, 6.4 * T), lm)                 # бедро (верх толще)
        m.box(leg, (x, 12.2, 0), (5.8 * T, 2.6, 5.8 * T), lm)
        m.box(leg, (x, 10.6, 0), (3.0, 1.4, 3.0), "metal")                   # колено
        shin = m.group(f"shin_{side}", (x, 10.6, 0), leg)
        endo = spec.get("endo_shin") == side
        sm = "metal" if endo else ("pants" if spec.get("shorts_long") else "main")
        if endo:
            m.box(shin, (x, 6.8, 0), (1.8, 6.6, 1.8), "metal")
            m.box(shin, (x + 0.9 * sx, 7.5, 0.6), (0.5, 4.0, 0.5), "wires" if spec.get("worn") else "metal_dark")
        else:
            m.box(shin, (x, 7.2, 0), (5.4 * T, 6.0, 5.4 * T), sm)
            m.box(shin, (x, 4.6, 0), (5.0 * T, 1.4, 5.0 * T), sm)
        fm = "beak" if spec.get("bird_feet") else "dark"
        m.cube(shin, (x - 3.4, 0, -6.4), (x + 3.4, 3.4, 3.0), fm)               # ступня
        m.cube(shin, (x - 3.0, 3.4, -4.5), (x + 3.0, 4.2, 2.4), fm)
        if spec.get("bird_feet"):
            for t in (-2.2, 0, 2.2):
                m.cube(shin, (x + t - 0.7, 0, -8.6), (x + t + 0.7, 1.4, -6.4), fm)
        else:
            for t in (-2.0, 0, 2.0):
                m.cube(shin, (x + t - 0.8, 0.2, -7.2), (x + t + 0.8, 2.0, -6.4), fm)

    # ---------------- корпус ----------------
    b = "body"
    m.cube(b, (-6.6 * W, 16.6, -4.9 * W), (6.6 * W, 21.2, 4.9 * W), "pants" if spec.get("shorts") else "dark")   # таз
    m.cube(b, (-8.0 * W, 21.0, -5.9 * W), (8.0 * W, 27.6, 5.9 * W), "main")                                      # живот
    m.cube(b, (-7.4 * W, 27.4, -5.4 * W), (7.4 * W, 32.8, 5.4 * W), "main")                                      # грудь
    m.cube(b, (-6.0 * W, 32.6, -4.4 * W), (6.0 * W, 33.6, 4.4 * W), "main")
    if spec.get("bib"):
        m.cube(b, (-5.4 * W, 22.0, -6.45 * W), (5.4 * W, 31.4, -5.85 * W), "bib")
    elif spec.get("belly", True):
        m.cube(b, (-5.8 * W, 21.6, -6.5 * W), (5.8 * W, 28.8, -5.85 * W), "light")
        m.cube(b, (-4.4 * W, 22.6, -7.0 * W), (4.4 * W, 27.6, -6.45 * W), "light")
    if spec.get("worn"):
        m.cube(b, (1.6, 23.5, -6.05 * W), (6.4, 28.8, -5.75 * W), "tear")
        m.cube(b, (-7.2, 25.5, 5.85 * W), (-2.0, 30.2, 6.2 * W), "wires")
        m.box(b, (4.0, 26.0, -5.4 * W), (2.2, 4.0, 1.0), "metal")
    if spec.get("bowtie"):
        a.material("bowtie", spec["bowtie"], "plastic")
        m.cube(b, (-3.2, 31.0, -6.0 * W), (-0.6, 33.2, -5.2 * W), "bowtie")
        m.cube(b, (0.6, 31.0, -6.0 * W), (3.2, 33.2, -5.2 * W), "bowtie")
        m.cube(b, (-0.7, 31.5, -6.2 * W), (0.7, 32.7, -5.2 * W), "bowtie")

    # ---------------- руки ----------------
    for side, sx in (("l", 1), ("r", -1)):
        x = 9.4 * sx * W
        arm = m.group(f"arm_{side}", (x, 31.4, 0), b)
        m.box(arm, (x, 31.4, 0), (4.6, 4.0, 5.0), "main")                    # плечо
        m.box(arm, (x + 0.3 * sx, 27.6, 0), (4.8 * T, 5.4, 4.8 * T), "main")
        m.box(arm, (x + 0.3 * sx, 24.6, 0), (2.8, 1.4, 2.8), "metal")         # локоть
        fore = m.group(f"forearm_{side}", (x + 0.3 * sx, 24.6, 0), arm)
        endo = spec.get("endo_arm") == side
        if endo:
            m.box(fore, (x + 0.3 * sx, 20.8, 0), (1.8, 6.2, 1.8), "metal")
            m.box(fore, (x + 1.0 * sx, 21.0, 0.6), (0.5, 4.0, 0.5), "wires" if spec.get("worn") else "metal_dark")
        else:
            m.box(fore, (x + 0.3 * sx, 21.2, 0), (4.6 * T, 5.6, 4.6 * T), "main")
            m.box(fore, (x + 0.3 * sx, 18.3, 0), (4.0 * T, 1.0, 4.0 * T), "main")
        hand = m.group(f"hand_{side}", (x + 0.3 * sx, 17.6, 0), fore)
        hx = x + 0.3 * sx
        if spec.get("hook") == side:
            m.box(hand, (hx, 16.4, 0), (1.4, 2.6, 1.4), "prop2")
            m.box(hand, (hx, 14.6, -1.2), (1.3, 1.3, 3.6), "prop2")
            m.box(hand, (hx, 15.6, -2.8), (1.3, 2.2, 1.3), "prop2")
            m.box(hand, (hx, 16.6, -2.2), (1.2, 0.6, 1.2), "prop2")
        else:
            hm = "light" if spec.get("light_hands") else "main"
            m.box(hand, (hx, 15.4, 0), (5.0 * T, 4.2, 5.0 * T), hm)          # ладонь
            for f in (-1.6, 0, 1.6):
                m.box(hand, (hx + f * T, 12.6, -0.9), (1.4, 2.4, 2.0), "dark")  # пальцы
            m.box(hand, (hx - 2.6 * sx, 14.6, -1.4), (1.2, 2.2, 1.6), "dark")   # большой
    if spec.get("mic"):
        hx = -9.4 * W - 0.3
        m.box("hand_r", (hx, 13.2, -3.0), (1.0, 5.0, 1.0), "prop")
        m.box("hand_r", (hx, 16.2, -3.0), (2.0, 2.0, 2.0), "prop2")
    if spec.get("cupcake"):
        hx = 9.4 * W + 0.3
        a.material("cake", "#e47fb0", "plastic")
        a.material("cup", "#b04080", "plastic")
        m.box("hand_l", (hx, 12.6, -3.6), (5.0, 0.6, 5.0), "prop2")
        m.box("hand_l", (hx, 14.0, -3.6), (3.2, 2.2, 3.2), "cup")
        m.box("hand_l", (hx, 15.8, -3.6), (3.8, 1.6, 3.8), "cake")
        m.box("hand_l", (hx, 17.2, -3.6), (0.5, 1.4, 0.5), "light")
        m.box("hand_l", (hx - 0.8, 16.0, -5.55), (0.6, 0.6, 0.2), "black")
        m.box("hand_l", (hx + 0.8, 16.0, -5.55), (0.6, 0.6, 0.2), "black")

    # ---------------- голова ----------------
    head = m.group("h_head", (0, 33.6, 0), b)
    m.box(head, (0, 34.2, 0), (3.6, 1.4, 3.6), "metal")
    hw, hh, hd = spec.get("head", (14.0, 10.0, 12.6))
    y0 = 34.8
    fz = -hd / 2
    m.cube(head, (-hw / 2, y0, fz), (hw / 2, y0 + hh, -fz), "main")
    m.cube(head, (-hw / 2 + 1.2, y0 + hh, fz + 1.2), (hw / 2 - 1.2, y0 + hh + 1.0, -fz - 1.2), "main")     # покатая макушка
    m.cube(head, (-hw / 2 - 0.6, y0 + 1.2, fz + 1.4), (hw / 2 + 0.6, y0 + hh - 2.4, -fz - 1.4), "main")   # щёки
    m.cube(head, (-hw / 2 + 1.0, y0 - 0.8, fz + 1.0), (hw / 2 - 1.0, y0, -fz - 1.0), "dark")               # низ головы
    snout = spec.get("snout", "bear")
    jaw = m.group("jaw", (0, y0 + 1.6, fz + 2.0), head)
    if snout == "beak":
        m.cube(head, (-4.2, y0 + 2.0, fz - 3.8), (4.2, y0 + 4.8, fz + 0.4), "beak")
        m.cube(head, (-3.2, y0 + 4.8, fz - 2.6), (3.2, y0 + 5.4, fz + 0.4), "beak")
        m.cube(jaw, (-3.8, y0 + 0.2, fz - 3.2), (3.8, y0 + 1.8, fz + 0.6), "beak")
        m.cube(jaw, (-3.2, y0 + 1.75, fz - 2.8), (3.2, y0 + 2.05, fz - 0.4), "teeth")
    elif snout == "fox":
        m.cube(head, (-3.2, y0 + 1.8, fz - 5.4), (3.2, y0 + 5.0, fz + 0.3), "light")
        m.cube(head, (-2.6, y0 + 5.0, fz - 4.2), (2.6, y0 + 5.6, fz + 0.3), "main")
        m.cube(head, (-1.4, y0 + 4.2, fz - 6.0), (1.4, y0 + 5.4, fz - 5.2), "nose")
        m.cube(head, (-3.0, y0 + 1.55, fz - 5.2), (3.0, y0 + 1.95, fz - 0.4), "teeth")
        m.cube(jaw, (-2.9, y0 + 0.2, fz - 5.0), (2.9, y0 + 1.6, fz + 0.6), "light")
        m.cube(jaw, (-2.7, y0 + 1.55, fz - 4.8), (2.7, y0 + 1.95, fz - 0.4), "teeth")
    else:
        m.cube(head, (-4.4, y0 + 1.8, fz - 2.4), (4.4, y0 + 5.2, fz + 0.3), "light")
        m.cube(head, (-3.4, y0 + 5.2, fz - 1.6), (3.4, y0 + 5.8, fz + 0.3), "light")
        m.cube(head, (-1.8, y0 + 4.2, fz - 3.2), (1.8, y0 + 5.8, fz - 2.3), "nose")
        m.cube(head, (-3.8, y0 + 1.55, fz - 2.2), (3.8, y0 + 1.95, fz - 0.2), "teeth")
        m.cube(jaw, (-4.0, y0 + 0.1, fz - 2.2), (4.0, y0 + 1.6, fz + 0.8), "light")
        m.cube(jaw, (-3.6, y0 + 1.55, fz - 2.0), (3.6, y0 + 1.95, fz - 0.2), "teeth")
    if spec.get("cheeks"):
        m.cube(head, (-6.4, y0 + 2.8, fz - 0.3), (-4.6, y0 + 4.2, fz + 0.1), "cheek")
        m.cube(head, (4.6, y0 + 2.8, fz - 0.3), (6.4, y0 + 4.2, fz + 0.1), "cheek")
    # глаза с веками (верхнее веко прикрывает треть глаза — фирменный взгляд FNAF)
    ey = y0 + 6.4
    eyes = m.group("glow_eyes", (0, ey, fz), head)
    for sx in (1, -1):
        cx = 3.1 * sx
        if spec.get("eyepatch") and sx == -1:
            m.cube(head, (cx - 2.0, ey - 1.5, fz - 0.45), (cx + 2.0, ey + 1.7, fz + 0.1), "black")
            m.cube(head, (cx - 2.6, ey + 1.5, fz - 0.42), (cx + 3.4, ey + 1.9, fz + 0.2), "black",
                   rotation=[0, 0, -22.5], origin=[cx, ey + 1.7, fz])
            continue
        if spec.get("hollow_eyes"):
            m.cube(head, (cx - 1.6, ey - 1.3, fz - 0.25), (cx + 1.6, ey + 1.4, fz + 0.1), "black")
            m.cube(eyes, (cx - 0.35, ey - 0.4, fz - 0.4), (cx + 0.35, ey + 0.3, fz - 0.2), "pupil")
        else:
            m.cube(head, (cx - 1.6, ey - 1.3, fz - 0.3), (cx + 1.6, ey + 1.5, fz + 0.1), "eye")
            m.cube(eyes, (cx - 0.65, ey - 0.75, fz - 0.5), (cx + 0.65, ey + 0.45, fz - 0.25), "pupil")
            m.cube(head, (cx - 1.75, ey + 0.55, fz - 0.55), (cx + 1.75, ey + 1.6, fz + 0.1), "lid")
        if spec.get("brows", True):
            m.cube(head, (cx - 2.0, ey + 1.9, fz - 0.5), (cx + 2.0, ey + 2.7, fz + 0.1), "dark",
                   rotation=[0, 0, -22.5 * sx], origin=[cx, ey + 2.3, fz])
        if spec.get("lashes"):
            for lx in (-1.2, 0, 1.2):
                m.cube(head, (cx + lx - 0.2, ey + 1.6, fz - 0.6), (cx + lx + 0.2, ey + 2.4, fz - 0.3), "black")
    # уши
    ears = spec.get("ears", "bear")
    top = y0 + hh
    for sx in (1, -1):
        sd = "l" if sx == 1 else "r"
        if ears == "bear":
            m.cube(head, (4.6 * sx - 2.0, top - 0.8, -1.0), (4.6 * sx + 2.0, top + 3.0, 1.0), "main")
            m.cube(head, (4.6 * sx - 1.1, top - 0.1, -1.15), (4.6 * sx + 1.1, top + 2.3, -0.9), "light")
        elif ears == "bunny":
            broken = spec.get("broken_ear") and sx == 1
            ear = m.group(f"ear_{sd}", (2.8 * sx, top, 0), head, rotation=[0, 0, (-50 if broken else -10) * sx])
            ln = 6.0 if broken else 13.0
            m.cube(ear, (2.8 * sx - 1.6, top - 0.4, -1.0), (2.8 * sx + 1.6, top + ln * 0.55, 1.0), "main")
            m.cube(ear, (2.8 * sx - 1.3, top + ln * 0.55, -0.9), (2.8 * sx + 1.3, top + ln, 0.9), "main")
            m.cube(ear, (2.8 * sx - 0.8, top + 0.6, -1.15), (2.8 * sx + 0.8, top + ln - 1.4, -0.9), "light")
            if broken:
                m.cube(ear, (2.8 * sx - 0.5, top + ln, -0.5), (2.8 * sx + 0.5, top + ln + 1.6, 0.5), "wires")
        elif ears == "fox":
            ear = m.group(f"ear_{sd}", (4.4 * sx, top, 0), head, rotation=[0, 0, -15 * sx])
            m.cube(ear, (4.4 * sx - 2.0, top - 0.6, -1.0), (4.4 * sx + 2.0, top + 2.8, 1.0), "main")
            m.cube(ear, (4.4 * sx - 1.3, top + 2.8, -0.8), (4.4 * sx + 1.3, top + 4.8, 0.8), "main")
            m.cube(ear, (4.4 * sx - 0.6, top + 4.8, -0.5), (4.4 * sx + 0.6, top + 5.8, 0.5), "main")
            m.cube(ear, (4.4 * sx - 0.8, top + 0.2, -1.15), (4.4 * sx + 0.8, top + 3.8, -0.9), "dark")
    if spec.get("tuft"):
        for i, (dx, rz) in enumerate(((-1.1, 22.5), (0, 0), (1.1, -22.5))):
            m.cube(head, (dx - 0.6, top + 0.6, -1.6 + i * 0.4), (dx + 0.6, top + 3.2, -0.4 + i * 0.4), "main",
                   rotation=[0, 0, rz], origin=[dx, top + 0.6, -1.0])
    if spec.get("hat"):
        a.material("hat", spec["hat"], "plastic")
        a.material("band", spec.get("hat_band", "#3b2b20"), "plastic")
        m.cube(head, (-3.6, top + 0.9, -3.4), (3.6, top + 1.5, 3.8), "hat")
        m.cube(head, (-2.6, top + 1.5, -2.4), (2.6, top + 5.4, 2.8), "hat")
        m.cube(head, (-2.7, top + 1.5, -2.5), (2.7, top + 2.2, 2.9), "band")
    if spec.get("worn"):
        m.cube(head, (-hw / 2 - 0.08, y0 + 2.4, -1.2), (-hw / 2 + 0.3, y0 + 6.0, 2.8), "tear")

    add_animations(m, spec)
    return m


def add_animations(m, spec):
    L = "linear"
    S = "step"
    m.animation("idle", 2.4, "loop", {
        "body": {"position": [(0, (0, 0, 0)), (1.2, (0, -0.35, 0)), (2.4, (0, 0, 0))]},
        "h_head": {"rotation": [(0, (0, 0, 0), S), (0.7, (4, 9, -3), S), (1.3, (0, 0, 0), S),
                                (1.9, (-3, -7, 2), S), (2.4, (0, 0, 0), S)]},
        "jaw": {"rotation": [(0, (0, 0, 0)), (1.2, (6, 0, 0)), (2.4, (0, 0, 0))]},
        "arm_l": {"rotation": [(0, (0, 0, -3)), (1.2, (0, 0, -5)), (2.4, (0, 0, -3))]},
        "arm_r": {"rotation": [(0, (0, 0, 3)), (1.2, (0, 0, 5)), (2.4, (0, 0, 3))]},
    })

    def gait(len_, legs, shins, arms, bob, lean):
        q = len_ / 4
        return {
            "leg_l": {"rotation": [(0, (legs, 0, 0)), (2 * q, (-legs, 0, 0)), (len_, (legs, 0, 0))]},
            "leg_r": {"rotation": [(0, (-legs, 0, 0)), (2 * q, (legs, 0, 0)), (len_, (-legs, 0, 0))]},
            "shin_l": {"rotation": [(0, (0, 0, 0)), (q, (shins, 0, 0)), (2 * q, (0, 0, 0)), (len_, (0, 0, 0))]},
            "shin_r": {"rotation": [(0, (0, 0, 0)), (2 * q, (0, 0, 0)), (3 * q, (shins, 0, 0)), (len_, (0, 0, 0))]},
            "arm_l": {"rotation": [(0, (-arms, 0, -4)), (2 * q, (arms, 0, -4)), (len_, (-arms, 0, -4))]},
            "arm_r": {"rotation": [(0, (arms, 0, 4)), (2 * q, (-arms, 0, 4)), (len_, (arms, 0, 4))]},
            "forearm_l": {"rotation": [(0, (-12, 0, 0)), (len_, (-12, 0, 0))]},
            "forearm_r": {"rotation": [(0, (-12, 0, 0)), (len_, (-12, 0, 0))]},
            "body": {"position": [(0, (0, 0, 0)), (q, (0, -bob, 0)), (2 * q, (0, 0, 0)), (3 * q, (0, -bob, 0)), (len_, (0, 0, 0))],
                     "rotation": [(0, (lean, 2, 0)), (2 * q, (lean, -2, 0)), (len_, (lean, 2, 0))]},
            "h_head": {"rotation": [(0, (0, 0, 2), S), (q, (3, 6, 0), S), (2 * q, (0, 0, -2), S), (3 * q, (2, -5, 0), S), (len_, (0, 0, 2), S)]},
        }

    m.animation("walk", 1.1, "loop", gait(1.1, 24, 22, 18, 0.7, 2))
    m.animation("run", 0.62, "loop", gait(0.62, 42, 46, 38, 1.2, 12))
    m.animation("attack", 0.65, "once", {
        "arm_r": {"rotation": [(0, (0, 0, 4)), (0.18, (-150, -10, 10)), (0.34, (35, 0, 4)), (0.65, (0, 0, 4))]},
        "forearm_r": {"rotation": [(0, (0, 0, 0)), (0.18, (-30, 0, 0)), (0.34, (-5, 0, 0)), (0.65, (0, 0, 0))]},
        "body": {"rotation": [(0, (0, 0, 0)), (0.18, (-6, -12, 0)), (0.34, (16, 10, 0)), (0.65, (0, 0, 0))]},
        "jaw": {"rotation": [(0, (0, 0, 0)), (0.25, (28, 0, 0)), (0.5, (0, 0, 0))]},
        "h_head": {"rotation": [(0, (0, 0, 0)), (0.3, (12, 0, 0)), (0.65, (0, 0, 0))]},
    })
    shake = []
    t = 0.0
    while t < 1.2:
        shake.append((round(t, 3), (-14, random.uniform(-9, 9), random.uniform(-6, 6)), S))
        t += 0.06
    m.animation("jumpscare", 1.2, "once", {
        "h_head": {"position": [(0, (0, 0, 0)), (0.12, (0, -1, -5)), (1.2, (0, -1, -5))], "rotation": shake},
        "jaw": {"rotation": [(0, (0, 0, 0)), (0.1, (42, 0, 0)), (1.2, (42, 0, 0))]},
        "arm_l": {"rotation": [(0, (0, 0, 0)), (0.15, (-115, 0, -28)), (1.2, (-115, 0, -28))]},
        "arm_r": {"rotation": [(0, (0, 0, 0)), (0.15, (-115, 0, 28)), (1.2, (-115, 0, 28))]},
        "body": {"rotation": [(0, (0, 0, 0)), (0.15, (14, 0, 0)), (1.2, (14, 0, 0))]},
    })
    tw = []
    t = 0.0
    while t < 1.5:
        tw.append((round(t, 3), (random.uniform(-20, 25), random.uniform(-30, 30), random.uniform(-15, 15)), S))
        t += 0.12
    m.animation("stun", 1.5, "once", {
        "h_head": {"rotation": tw},
        "arm_l": {"rotation": [(0, (0, 0, 0)), (0.2, (20, 0, -10)), (1.5, (0, 0, 0))]},
        "arm_r": {"rotation": [(0, (0, 0, 0)), (0.2, (20, 0, 10)), (1.5, (0, 0, 0))]},
        "body": {"rotation": [(0, (0, 0, 0)), (0.2, (10, 0, 4)), (1.5, (0, 0, 0))]},
    })


# ----------------------------------------------------------------- персонажи

CHARACTERS = [
    {"id": "fnaf_freddy", "palette": {"main": "#7a4a2b", "light": "#b98a5e", "dark": "#4e2e1a", "pupil": "#3d7fd6"},
     "ears": "bear", "snout": "bear", "hat": "#151515", "bowtie": "#151515", "mic": True},
    {"id": "fnaf_bonnie", "palette": {"main": "#5b56b0", "light": "#8f8bd8", "dark": "#3a3678", "pupil": "#e0405c"},
     "ears": "bunny", "snout": "bear", "bowtie": "#c22b2b", "tuft": True},
    {"id": "fnaf_chica", "palette": {"main": "#e3b520", "light": "#f2d867", "dark": "#a17c10", "pupil": "#9a3fc4",
                                     "beak": "#ea8a1a"},
     "ears": "none", "snout": "beak", "bib": ["LET'S", "EAT!!!"], "cupcake": True, "bird_feet": True, "belly": False,
     "round_head": True, "tuft": True},
    {"id": "fnaf_foxy", "palette": {"main": "#a8322a", "light": "#d9b48a", "dark": "#6e1f1a", "pupil": "#f2c22e",
                                    "pants": "#8b6a45"},
     "ears": "fox", "snout": "fox", "sharp": True, "eyepatch": True, "hook": "r", "shorts": True, "endo_shin": "l",
     "endo_arm": "l", "worn": True},
    {"id": "fnaf_golden_freddy", "palette": {"main": "#c39a32", "light": "#dcbd6a", "dark": "#7c5f1a", "pupil": "#f4f4f4"},
     "ears": "bear", "snout": "bear", "hat": "#151515", "bowtie": "#151515", "hollow_eyes": True, "worn": True},
    {"id": "fnaf_springtrap", "palette": {"main": "#7d8248", "light": "#a8a66b", "dark": "#4b4f28", "pupil": "#7cff4a"},
     "ears": "bunny", "snout": "bear", "sharp": True, "broken_ear": True, "worn": True, "endo_arm": "r",
     "endo_shin": "r", "kind": "worn", "brows": False},
    {"id": "fnaf_toy_freddy", "palette": {"main": "#9a6034", "light": "#e0b98c", "dark": "#6a3f20", "pupil": "#4aa3ff",
                                          "cheek": "#ee8aa4"},
     "ears": "bear", "snout": "bear", "hat": "#151515", "bowtie": "#151515", "mic": True, "cheeks": True, "kind": "plastic",
     "light_hands": True},
    {"id": "fnaf_toy_bonnie", "palette": {"main": "#5d9be3", "light": "#eef2f7", "dark": "#3a6aa8", "pupil": "#35c26a",
                                          "cheek": "#ee8aa4"},
     "ears": "bunny", "snout": "bear", "bowtie": "#c22b2b", "cheeks": True, "lashes": True, "kind": "plastic",
     "light_hands": True},
    {"id": "fnaf_toy_chica", "palette": {"main": "#f5d23c", "light": "#fbe98e", "dark": "#c49f1a", "pupil": "#3d8ee8",
                                         "beak": "#f08c23", "cheek": "#ee8aa4"},
     "ears": "none", "snout": "beak", "bib": ["LET'S", "PARTY!"], "cupcake": True, "bird_feet": True, "belly": False,
     "round_head": True, "cheeks": True, "lashes": True, "kind": "plastic", "tuft": True},
    {"id": "fnaf_mangle", "palette": {"main": "#ece6e2", "light": "#f4b3cc", "dark": "#b8aaa6", "pupil": "#f2c22e",
                                      "pants": "#e58fb3", "cheek": "#ef6f9a"},
     "ears": "fox", "snout": "fox", "sharp": True, "cheeks": True, "endo_arm": "l", "endo_shin": "r", "worn": True,
     "kind": "plastic", "bowtie": "#c22b2b"},
]


# ----------------------------------------------------------------- генератор

def generator():
    m = Model("fnaf_generator", seed=77)
    a = m.atlas
    a.material("housing", "#c49a2c", "metal")
    a.material("dark", "#2e3133", "metal")
    a.material("steel", "#7b8186", "metal")
    a.material("tank", "#a3261e", "metal")
    a.material("black", "#141414", "plastic")
    a.special("vents", vents)
    a.special("panel", panel)
    a.special("hazard", hazard)
    a.special("lamp_on", lamp_on)
    a.special("lamp_off", lamp_off)
    m.group("base", (0, 0, 0))
    m.group("body", (0, 1.5, 0), "base")
    g = "body"
    # салазки
    m.cube("base", (-9.2, 0, -7.0), (9.2, 1.0, -5.0), "dark")
    m.cube("base", (-9.2, 0, 5.0), (9.2, 1.0, 7.0), "dark")
    m.cube("base", (-8.6, 1.0, -6.6), (8.6, 1.6, 6.6), "steel")
    # корпус
    m.cube(g, (-8.0, 1.6, -6.0), (8.0, 12.4, 6.0), "housing")
    m.cube(g, (-8.3, 1.6, -6.3), (8.3, 2.6, 6.3), "hazard")
    m.cube(g, (-8.05, 4.0, -4.5), (-7.6, 10.5, 4.5), "vents")
    m.cube(g, (7.6, 4.0, -4.5), (8.05, 10.5, 4.5), "vents")
    m.cube(g, (-5.2, 4.2, -6.35), (5.2, 10.6, -5.9), "panel")
    m.cube(g, (-8.4, 12.2, -6.4), (8.4, 13.0, 6.4), "dark")
    # бак и выхлоп
    m.cube(g, (-6.2, 13.0, -3.6), (3.8, 17.0, 3.6), "tank")
    m.cube(g, (-6.6, 14.6, -3.9), (4.2, 15.4, 3.9), "dark")
    m.cube(g, (-2.4, 17.0, -1.0), (-0.4, 18.0, 1.0), "black")
    m.cube(g, (5.2, 13.0, 2.0), (7.0, 19.6, 3.8), "steel")
    m.cube(g, (4.8, 19.6, 1.6), (7.4, 20.4, 4.2), "dark")
    # провода к панели
    m.cube(g, (-7.4, 9.0, -6.6), (-6.6, 12.2, -6.1), "black")
    m.cube(g, (6.6, 7.0, -6.6), (7.4, 12.2, -6.1), "tank")
    # лампы: погашенные — всегда; горящие (светятся) — растут в анимации fixed
    m.group("lamps", (0, 13.0, -6.0), g)
    m.group("glow_lamps", (0, 13.0, -6.0), "lamps")
    for x in (-3.5, 0, 3.5):
        m.cube("lamps", (x - 1.0, 13.0, -6.6), (x + 1.0, 14.6, -4.6), "lamp_off")
        m.cube("glow_lamps", (x - 1.15, 12.9, -6.75), (x + 1.15, 14.75, -4.45), "lamp_on")
    L = "linear"
    off = {"glow_lamps": {"scale": [(0, (0.01, 0.01, 0.01), "step")]}}
    m.animation("idle", 1.0, "loop", dict(off))
    vib = []
    t = 0.0
    while t <= 0.4:
        vib.append((round(t, 3), (random.uniform(-0.12, 0.12), random.uniform(-0.05, 0.08), random.uniform(-0.12, 0.12)), L))
        t += 0.05
    m.animation("repair", 0.4, "loop", {"body": {"position": vib}, **off})
    jolt = [(0, (0, 0, 0), L), (0.06, (0.8, 0.3, -0.5), L), (0.12, (-0.8, 0, 0.6), L), (0.2, (0.6, 0.2, -0.3), L),
            (0.3, (-0.4, 0, 0.3), L), (0.45, (0, 0, 0), L)]
    m.animation("fail", 0.5, "once", {"body": {"position": jolt,
                                                  "rotation": [(0, (0, 0, 0)), (0.1, (0, 0, 4)), (0.2, (0, 0, -4)), (0.5, (0, 0, 0))]},
                                         **off})
    shake = [(0, (0, 0, 0), L)]
    t = 0.05
    while t < 1.0:
        k = 1 - t
        shake.append((round(t, 3), (random.uniform(-0.6, 0.6) * k, random.uniform(0, 0.4) * k, random.uniform(-0.6, 0.6) * k), L))
        t += 0.05
    shake.append((1.0, (0, 0, 0), L))
    m.animation("fixed", 1.0, "hold", {
        "body": {"position": shake},
        "glow_lamps": {"scale": [(0, (0.01, 0.01, 0.01), "step"), (0.35, (0.01, 0.01, 0.01), "step"),
                                 (0.4, (1.2, 1.2, 1.2), L), (0.55, (1, 1, 1), L), (1.0, (1, 1, 1), L)]},
    })
    return m


# ----------------------------------------------------------------- ворота выхода

def gate():
    m = Model("fnaf_gate", seed=91)
    a = m.atlas
    a.material("frame", "#3a3d40", "metal")
    a.material("door", "#6e7377", "metal")
    a.special("hazard", hazard)
    a.material("light", "#c22b2b", "glass")
    a.special("lamp_on", lamp_on)
    m.group("frame", (0, 0, 0))
    m.cube("frame", (-25, 0, -1.5), (-23, 48, 1.5), "frame")
    m.cube("frame", (23, 0, -1.5), (25, 48, 1.5), "frame")
    m.cube("frame", (-25, 48, -1.5), (25, 51, 1.5), "frame")
    m.cube("frame", (-23, 48.2, -1.7), (23, 49.2, 1.7), "hazard")
    m.group("glow_sign", (0, 50, -1.7), "frame")
    m.cube("glow_sign", (-6, 49.5, -2.2), (6, 51.5, -1.6), "light")
    for side, sx in (("door_l", -1), ("door_r", 1)):
        m.group(side, (12 * sx, 0, 0), "frame")
        x0, x1 = (-23, 0) if sx < 0 else (0, 23)
        m.cube(side, (x0, 0, -1), (x1, 48, 1), "door")
        for y in range(6, 48, 8):
            m.cube(side, (x0 + 1, y, -1.2), (x1 - 1, y + 0.8, 1.2), "frame")
        m.cube(side, (x0 + (20 if sx < 0 else 1), 2, -1.25), (x1 - (1 if sx < 0 else 20), 6, 1.25), "hazard")
    L = "linear"
    m.animation("idle", 1.0, "loop", {"door_l": {"position": [(0, (0, 0, 0), "step")]},
                                       "door_r": {"position": [(0, (0, 0, 0), "step")]}})
    m.animation("open", 2.0, "hold", {
        "door_l": {"position": [(0, (0, 0, 0), L), (0.2, (0.6, 0, 0), L), (2.0, (-22, 0, 0), L)]},
        "door_r": {"position": [(0, (0, 0, 0), L), (0.2, (-0.6, 0, 0), L), (2.0, (22, 0, 0), L)]},
    })
    return m


def main():
    random.seed(10102026)
    os.makedirs(OUT, exist_ok=True)
    built = []
    for spec in CHARACTERS:
        built.append(animatronic(spec).save(OUT))
    built.append(generator().save(OUT))
    built.append(gate().save(OUT))
    for p in built:
        print(os.path.relpath(p, os.path.join(HERE, "..")))


if __name__ == "__main__":
    main()
