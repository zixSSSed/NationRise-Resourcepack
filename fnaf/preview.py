"""Превью .bbmodel без Blockbench: простой программный рендер кубов с текстурой (рисование
по алгоритму художника, грани разбиты на сетку и окрашены по своему участку атласа).

py -3.13 preview.py out.png model1.bbmodel [model2 ...] [--pose=anim@time]
"""
import base64
import io
import json
import math
import sys

from PIL import Image, ImageDraw


def rot(v, ang, origin):
    """Поворот точки v вокруг origin на углы (x, y, z) в градусах — порядок как в Blockbench (Z, Y, X)."""
    x, y, z = (v[i] - origin[i] for i in range(3))
    ax, ay, az = (math.radians(a) for a in ang)
    # Z
    x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
    # Y
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    # X
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    return (x + origin[0], y + origin[1], z + origin[2])


def load(path):
    m = json.load(open(path, encoding="utf-8"))
    src = m["textures"][0]["source"].split(",", 1)[1]
    tex = Image.open(io.BytesIO(base64.b64decode(src))).convert("RGBA")
    return m, tex


def pose_of(m, spec):
    """{uuid группы: (rotation, position)} из кадра анимации name@time (линейно между ключами)."""
    if not spec:
        return {}
    name, t = spec.split("@")
    t = float(t)
    an = next((a for a in m.get("animations", []) if a["name"] == name), None)
    out = {}
    if not an:
        return out
    for gid, anim in an["animators"].items():
        res = {}
        for ch in ("rotation", "position"):
            ks = sorted([k for k in anim["keyframes"] if k["channel"] == ch], key=lambda k: k["time"])
            if not ks:
                continue
            prev = ks[0]
            nxt = ks[-1]
            for k in ks:
                if k["time"] <= t:
                    prev = k
                if k["time"] >= t:
                    nxt = k
                    break
            def val(k):
                d = k["data_points"][0]
                return tuple(float(d[a]) for a in "xyz")
            if nxt["time"] == prev["time"]:
                v = val(prev)
            else:
                f = (t - prev["time"]) / (nxt["time"] - prev["time"])
                a, b = val(prev), val(nxt)
                v = tuple(a[i] + (b[i] - a[i]) * f for i in range(3))
            res[ch] = v
        out[gid] = res
    return out


def collect(m, pose):
    """Список (уголки куба в мире, грани, элемент)."""
    elems = {e["uuid"]: e for e in m["elements"]}
    cubes = []

    def walk(node, chain):
        g = node
        chain = chain + [g]
        for ch in g.get("children", []):
            if isinstance(ch, dict):
                walk(ch, chain)
            elif ch in elems:
                cubes.append((elems[ch], chain))

    for n in m["outliner"]:
        if isinstance(n, dict):
            walk(n, [])
    return cubes


FACE_IDX = {  # углы граней (индексы в списке 8 углов) по кругу; corners: x(0/1) y(0/1) z(0/1)
    "north": [(1, 1, 0), (0, 1, 0), (0, 0, 0), (1, 0, 0)],
    "south": [(0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)],
    "east": [(1, 1, 1), (1, 1, 0), (1, 0, 0), (1, 0, 1)],
    "west": [(0, 1, 0), (0, 1, 1), (0, 0, 1), (0, 0, 0)],
    "up": [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)],
    "down": [(0, 0, 1), (1, 0, 1), (1, 0, 0), (0, 0, 0)],
}
LIGHT = {"north": 0.9, "south": 0.7, "east": 0.8, "west": 0.75, "up": 1.0, "down": 0.5}


def render(m, tex, yaw, pitch, size=(300, 380), pose=None, center=None, scale=None):
    pose = pose or {}
    cubes = collect(m, pose)
    polys = []
    W, H = size
    cy = math.radians(yaw)
    cp = math.radians(pitch)
    pts_all = []
    prepared = []
    for e, chain in cubes:
        f, t = e["from"], e["to"]
        corners = {}
        for ix in (0, 1):
            for iy in (0, 1):
                for iz in (0, 1):
                    p = (t[0] if ix else f[0], t[1] if iy else f[1], t[2] if iz else f[2])
                    if e.get("rotation"):
                        p = rot(p, e["rotation"], e.get("origin", (0, 0, 0)))
                    for g in reversed(chain):
                        pr = pose.get(g["uuid"], {})
                        r = list(g.get("rotation", (0, 0, 0)))
                        if "rotation" in pr:
                            r = [r[i] + pr["rotation"][i] for i in range(3)]
                        if any(r):
                            p = rot(p, r, g["origin"])
                        if "position" in pr:
                            p = tuple(p[i] + pr["position"][i] for i in range(3))
                    corners[(ix, iy, iz)] = p
        prepared.append((e, corners))
        pts_all.extend(corners.values())
    # камера: поворот вокруг Y (yaw), затем наклон (pitch); смотрим вдоль +Z
    def cam(p):
        x, y, z = p
        x, z = x * math.cos(cy) - z * math.sin(cy), x * math.sin(cy) + z * math.cos(cy)
        y, z = y * math.cos(cp) - z * math.sin(cp), y * math.sin(cp) + z * math.cos(cp)
        return x, y, z
    cams = [cam(p) for p in pts_all]
    xs = [c[0] for c in cams]
    ys = [c[1] for c in cams]
    if scale is None:
        scale = min((W - 30) / max(1e-3, max(xs) - min(xs)), (H - 30) / max(1e-3, max(ys) - min(ys)))
    ox = (max(xs) + min(xs)) / 2
    oy = (max(ys) + min(ys)) / 2
    for e, corners in prepared:
        for face, idx in FACE_IDX.items():
            fd = e["faces"].get(face)
            if not fd:
                continue
            quad = [cam(corners[i]) for i in idx]
            # отсечение задних граней (по нормали в камерных координатах)
            ax, ay = quad[1][0] - quad[0][0], quad[1][1] - quad[0][1]
            bx, by = quad[3][0] - quad[0][0], quad[3][1] - quad[0][1]
            if ax * by - ay * bx > 0:
                continue
            u0, v0, u1, v1 = fd["uv"]
            depth = sum(q[2] for q in quad) / 4
            polys.append((depth, quad, (u0, v0, u1, v1), LIGHT[face]))
    polys.sort(key=lambda p: -p[0])
    img = Image.new("RGBA", size, (34, 34, 40, 255))
    d = ImageDraw.Draw(img)
    N = 4
    for depth, quad, uv, light in polys:
        def lerp(a, b, f):
            return tuple(a[i] + (b[i] - a[i]) * f for i in range(3))
        for i in range(N):
            for j in range(N):
                fi0, fi1, fj0, fj1 = i / N, (i + 1) / N, j / N, (j + 1) / N
                def pt(fu, fv):
                    top = lerp(quad[0], quad[1], fu)
                    bot = lerp(quad[3], quad[2], fu)
                    p = lerp(top, bot, fv)
                    return ((p[0] - ox) * scale + W / 2, H / 2 - (p[1] - oy) * scale)
                poly = [pt(fi0, fj0), pt(fi1, fj0), pt(fi1, fj1), pt(fi0, fj1)]
                tu = uv[0] + (uv[2] - uv[0]) * (i + 0.5) / N
                tv = uv[1] + (uv[3] - uv[1]) * (j + 0.5) / N
                c = tex.getpixel((min(tex.width - 1, int(tu)), min(tex.height - 1, int(tv))))
                if c[3] < 10:
                    continue
                col = tuple(int(c[k] * light) for k in range(3)) + (255,)
                d.polygon(poly, fill=col)
    return img


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pose_spec = next((a[7:] for a in sys.argv[1:] if a.startswith("--pose=")), None)
    out, paths = args[0], args[1:]
    rows = []
    for p in paths:
        m, tex = load(p)
        pose = pose_of(m, pose_spec)
        views = [render(m, tex, yaw, pitch, pose=pose) for yaw, pitch in ((25, 12), (0, 4), (-80, 8))]
        rows.append((p.replace("\\", "/").split("/")[-1], views))
    sheet = Image.new("RGB", (300 * 3, 395 * len(rows)), (24, 24, 28))
    d = ImageDraw.Draw(sheet)
    for i, (name, views) in enumerate(rows):
        for j, v in enumerate(views):
            sheet.paste(v.convert("RGB"), (j * 300, i * 395 + 15))
        d.text((4, i * 395 + 2), name + ("  [" + pose_spec + "]" if pose_spec else ""), fill=(255, 255, 255))
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    main()


def grid(out, paths, yaw=25, pitch=10, cols=5, pose_spec=None):
    """Один ракурс на модель, сеткой — обзор всех сразу."""
    cells = []
    for p in paths:
        m, tex = load(p)
        cells.append((p.replace("\\", "/").split("/")[-1][:-8], render(m, tex, yaw, pitch, size=(220, 300), pose=pose_of(m, pose_spec))))
    rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGB", (220 * cols, 312 * rows), (24, 24, 28))
    d = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(cells):
        x, y = (i % cols) * 220, (i // cols) * 312
        sheet.paste(im.convert("RGB"), (x, y + 12))
        d.text((x + 3, y), name, fill=(255, 255, 255))
    sheet.save(out)
    print(out)
