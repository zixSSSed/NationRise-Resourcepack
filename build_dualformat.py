# -*- coding: utf-8 -*-
"""Двойной формат ресурспака: читает НОВЫЙ формат items/<base>.json (range_dispatch, 1.21.4+)
и генерит СТАРЫЙ формат models/item/<base>.json с overrides (custom_model_data predicate),
который понимают клиенты 1.14–1.21.3 (в т.ч. 1.16.5). Оба формата сосуществуют:
на 1.21.4+ читается items/ (overrides игнорируются), на ≤1.21.3 — наоборот.

Запускать ПОСЛЕ build_builditems.py и build_efftools.py (когда все items/*.json готовы)."""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
MC = os.path.join(ROOT, "pack", "assets", "minecraft")
ITEMS = os.path.join(MC, "items")
MODELS = os.path.join(MC, "models", "item")

# базовый предмет -> (parent старой модели, текстура layer0)
BASE = {
    "paper":             ("minecraft:item/generated", "minecraft:item/paper"),
    "cod":               ("minecraft:item/generated", "minecraft:item/cod"),
    "fishing_rod":       ("minecraft:item/handheld",  "minecraft:item/fishing_rod"),
    "netherite_pickaxe": ("minecraft:item/handheld",  "minecraft:item/netherite_pickaxe"),
    "netherite_axe":     ("minecraft:item/handheld",  "minecraft:item/netherite_axe"),
    "netherite_shovel":  ("minecraft:item/handheld",  "minecraft:item/netherite_shovel"),
}

print("build_dualformat:")
total = 0
for fn in sorted(os.listdir(ITEMS)):
    if not fn.endswith(".json"): continue
    base = fn[:-5]
    if base not in BASE:
        print(f"  ! пропуск {base}: нет базового parent/текстуры в BASE — добавь вручную"); continue
    d = json.load(open(os.path.join(ITEMS, fn), encoding="utf-8"))
    m = d.get("model", {})
    entries = m.get("entries", [])
    parent, tex = BASE[base]
    overrides = []
    for e in sorted(entries, key=lambda x: x.get("threshold", 0)):  # по возрастанию CMD (важно для old predicate)
        cmd = e.get("threshold")
        model = e.get("model", {}).get("model")
        if cmd is None or not model: continue
        overrides.append({"predicate": {"custom_model_data": cmd}, "model": model})
    old = {"parent": parent, "textures": {"layer0": tex}, "overrides": overrides}
    json.dump(old, open(os.path.join(MODELS, base + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    total += len(overrides)
    print(f"  {base}: {len(overrides)} overrides (старый формат)")
print(f"ok: {total} overrides всего")
