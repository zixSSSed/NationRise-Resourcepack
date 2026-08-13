# -*- coding: utf-8 -*-
"""Подъём глифов первой партии: приводим к общему правилу ascent = height - 2.

Как это работает у Minecraft: у bitmap-провайдера картинка масштабируется до `height`
пикселей, а её ВЕРХНИЙ край ставится на `ascent` пикселей выше базовой линии строки.
Значит нижний край оказывается на (height - ascent) ниже базовой линии.

У ванильного ascii.png height 8 при ascent 7 — буква свисает под базовую линию ровно
на 1 пиксель. Чтобы значок стоял вровень с буквами, ему нужно то же самое:
    height - ascent = 1  →  ascent = height - 1
...но в паке 137 глифов живут на ascent = height - 2 и выглядят правильно: значок
чуть выше буквы читается лучше, он выравнивается по «шапке» строки, а не по хвостам.
Это и берём за правило.

Самая первая партия (короны, звёзды, кристалл, череп…) делалась до этого правила:
там ascent 7 проставлен всем подряд, независимо от высоты. Корона при height 11
уезжала вниз на 2 пикселя, ✦ при height 10 — на 1.

Не трогаем:
  nr_logo   — логотип в шапке таба, стоит сам по себе, рядом нет строки для выравнивания;
  nr_ahbar,
  nr_ahdig  — полоса аукциона, отрицательный ascent там сознательный: элемент
              выносится в верх экрана, а не в строку.
"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(ROOT, "pack", "assets", "minecraft", "font", "default.json")
KEEP = {"nr_logo.png", "nr_ahbar.png", "nr_ahdig.png"}

data = json.load(open(DEFAULT, encoding="utf-8"))
fixed = []
for p in data["providers"]:
    if p.get("type") != "bitmap":
        continue
    name = p["file"].split("/")[-1]
    if name in KEEP:
        continue
    want = p["height"] - 2
    if p["ascent"] != want:
        fixed.append((name, p["ascent"], want, "".join(p.get("chars") or [])))
        p["ascent"] = want

json.dump(data, open(DEFAULT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
for name, old, new, ch in fixed:
    print(f"  {name:<26} ascent {old} → {new}  (вверх на {new - old}px)  {ch}")
print(f"поправлено: {len(fixed)}")
