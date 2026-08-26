"""Собирает ОДИН пак из нашего и моделей BetterModel — для локальных проверок.

Два пака в списке наборов ресурсов — это два места, где можно ошибиться: забыть включить
один, включить старую копию, перепутать порядок. На тесте это уже стоило нам часа: рыцарь
был виден, а сундук нет, потому что включённый пак собрали раньше, чем появилась модель
сундука. Одним файлом ошибиться негде.

Пересечений между паками нет: наш живёт в `assets/minecraft`, BetterModel — в своих
`assets/bettermodel` и папках-оверлеях. Совпадают только `pack.mcmeta` и `pack.png`, и
их мы собираем заново.

Отдельно про `pack.mcmeta`: у пака BetterModel есть оверлеи — версии моделей под разные
поколения формата. Просто взять наш файл нельзя, оверлеи потерялись бы и модели пропали
на части клиентов. Поэтому описание берём наше, а список оверлеев — от BetterModel.

На боевом сервере паки остаются раздельными: там их отдаёт сам плагин стопкой, и
пересобирать общий архив при каждом обновлении незачем.

Запуск: py -3.13 build_all_pack.py
"""

import io
import json
import zipfile
from pathlib import Path

BRAND = Path(__file__).parent
# Берём тот же архив, что собирает pack_zip.py. Раньше здесь стояла копия в папке клиента,
# и это стоило одной путаницы: копию забыли обновить, а собранный «общий» пак молча приехал
# со старым содержимым. Один источник — одна версия.
OURS = BRAND / "NationRise-Resourcepack.zip"
MODELS = BRAND / "NationRise-Models.zip"
OUT = Path(r"C:\Rockstar\game\resourcepacks\NationRise-ALL.zip")

DESCRIPTION = "\u00a7x\u00a78\u00a7C\u00a75\u00a7B\u00a7E\u00a78\u00a7l\u265b NationRise\u00a7r  \u00a7x\u00a7C\u00a79\u00a7B\u00a78\u00a7F\u00a72\u0438\u043a\u043e\u043d\u043a\u0438, \u0448\u0440\u0438\u0444\u0442 \u0438 \u043c\u043e\u0434\u0435\u043b\u0438"


def read_meta(zf):
    try:
        return json.loads(zf.read("pack.mcmeta").decode("utf-8"))
    except Exception:
        return {}


def main():
    for src in (OURS, MODELS):
        if not src.exists():
            raise SystemExit(f"нет файла: {src}")

    with zipfile.ZipFile(OURS) as a, zipfile.ZipFile(MODELS) as b:
        meta_a, meta_b = read_meta(a), read_meta(b)

        # Описание наше, оверлеи и диапазон форматов — от моделей: они строже.
        meta = {
            "pack": {
                "description": DESCRIPTION,
                "pack_format": meta_b.get("pack", {}).get("pack_format", 75),
                "supported_formats": meta_b.get("pack", {}).get("supported_formats", [46, 88]),
                "min_format": meta_b.get("pack", {}).get("min_format", 46),
                "max_format": meta_b.get("pack", {}).get("max_format", 88),
            }
        }
        if "overlays" in meta_b:
            meta["overlays"] = meta_b["overlays"]

        icon = None
        for zf in (a, b):
            try:
                icon = zf.read("pack.png")
                break
            except KeyError:
                continue

        seen = set()
        clash = []
        OUT.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as out:
            out.writestr("pack.mcmeta", json.dumps(meta, ensure_ascii=False))
            if icon:
                out.writestr("pack.png", icon)
            seen.update({"pack.mcmeta", "pack.png"})

            for zf, label in ((a, "наш"), (b, "модели")):
                for item in zf.infolist():
                    if item.is_dir() or item.filename in ("pack.mcmeta", "pack.png"):
                        continue
                    if item.filename in seen:
                        clash.append(f"{item.filename} ({label} пропущен)")
                        continue
                    seen.add(item.filename)
                    out.writestr(item, zf.read(item.filename))

    print(f"готово: {OUT}  ({OUT.stat().st_size} б, файлов {len(seen)})")
    if clash:
        print(f"  пересечений: {len(clash)}")
        for c in clash[:10]:
            print("   ", c)
    else:
        print("  пересечений нет — паки легли рядом без конфликтов")


if __name__ == "__main__":
    main()
