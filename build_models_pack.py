"""Брендирует ресурспак BetterModel перед раздачей игрокам.

BetterModel собирает свой пак сама и подписывает его «BetterModel's default pack» с
собственной иконкой. Игрок видит эту подпись в списке наборов ресурсов, а на сервере,
где всё остальное оформлено под NationRise, это выглядит как чужая вещь.

Переименовать через настройки плагина нельзя: опции для названия у него нет, а внутрь
собранного zip он пишет своё. Поэтому берём готовый архив и переписываем в нём две вещи:
подпись в pack.mcmeta и картинку pack.png. Сама геометрия и текстуры не трогаются.

Почему отдельным файлом, а не правкой на месте: BetterModel пересобирает свой build.zip
при каждом запуске сервера и затирает любые правки. Раздавать надо именно эту копию —
её же кладут на хостинг и в клиент для локальных проверок.

Запуск: py -3.13 build_models_pack.py
"""

import io
import json
import shutil
import zipfile
from pathlib import Path

import sys

# По умолчанию берём локальный сборочный архив, но путь можно передать аргументом:
# у боевого сервера свой набор моделей, и пак для раздачи собирается ИМЕННО из его файла.
# Имена внутри обфусцированы и у разных сборок разные — пак с чужой сборки не подойдёт.
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\Users\bravl\PaperServer\plugins\BetterModel\build.zip")
OUT = Path(r"C:\Users\bravl\OneDrive\Desktop\prilC++Claude\NationRise-Branding\NationRise-Models.zip")
# В папку клиента этот пак больше не кладём: там его собирает build_all_pack.py вместе с
# нашим, одним файлом. Два похожих архива рядом — приглашение включить не тот; один раз
# на этом уже потеряли вечер.
CLIENT = None
# Иконка пака: берём ту же, что у основного, чтобы в списке они смотрелись парой.
ICON = Path(r"C:\Users\bravl\OneDrive\Desktop\prilC++Claude\NationRise-Branding\pack\pack.png")

DESCRIPTION = "NationRise — модели существ и построек"


def check_fresh():
    """Проверить, что build.zip собран ПОСЛЕ последней правки моделей.

    Это ровно та ошибка, которая уже стоила одного вечера: модель добавили, пак собрали,
    а сервер между этим не запускали — и клиент рисовал новые кости по старой таблице
    имён. Выглядит это не как «модели нет», а как чужие куски вместо неё, и догадаться
    неоткуда. Поэтому проверяем по времени файлов и говорим прямо.
    """
    models = SRC.parent / "models"
    if not models.is_dir():
        return
    built = SRC.stat().st_mtime
    stale = [p.name for p in models.glob("*.bbmodel") if p.stat().st_mtime > built]
    if stale:
        raise SystemExit(
            "build.zip старее моделей: " + ", ".join(sorted(stale))
            + "\nЗапустите сервер — BetterModel пересоберёт пак, и только потом собирайте клиентский."
        )


def main():
    if not SRC.exists():
        raise SystemExit(f"нет исходника: {SRC}\nЗапустите сервер — BetterModel соберёт пак сама.")
    check_fresh()

    icon = ICON.read_bytes() if ICON.exists() else None
    patched = 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(SRC) as src, zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "pack.mcmeta":
                meta = json.loads(data.decode("utf-8"))
                meta.setdefault("pack", {})["description"] = DESCRIPTION
                data = json.dumps(meta, ensure_ascii=False).encode("utf-8")
                patched += 1
            elif item.filename == "pack.png" and icon is not None:
                data = icon
                patched += 1
            dst.writestr(item, data)

    if CLIENT is not None and CLIENT.parent.exists():
        shutil.copy2(OUT, CLIENT)

    print(f"готово: {OUT}  ({OUT.stat().st_size} б)")
    print(f"  переписано файлов: {patched} (pack.mcmeta{', pack.png' if icon else ' — иконка не найдена, оставлена родная'})")
    print(f"  подпись в клиенте: «{DESCRIPTION}»")
    if CLIENT is not None and CLIENT.parent.exists():
        print(f"  копия для клиента: {CLIENT}")


if __name__ == "__main__":
    main()
