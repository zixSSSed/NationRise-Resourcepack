# NationRise Resourcepack

Ресурспак сервера NationRise (АнПрим). Генерируется Python-скриптами.

## Сборка
Нужен Python 3.13 (`py -3.13`) с Pillow (`py -3.13 -m pip install pillow`).

```bat
py -3.13 build_builditems.py   & rem иконки меню + миньоны (CMD в items/paper.json)
py -3.13 build_ahfont.py       & rem шрифт-оверлей аукциона
py -3.13 build_earn_gui.py     & rem отдельный marketplace-фон меню /earn
py -3.13 build_town_gui.py     & rem отдельные фоны /t и /t builds
py -3.13 build_market_gui.py   & rem отдельные фоны /shop и /buyer
py -3.13 build_effpick.py      & rem донат-кирка из ../model.bbmodel
py -3.13 pack_zip.py           & rem собрать NationRise-Resourcepack.zip
py -3.13 build_lite_zip.py     & rem lite ZIP без font/textures/font
```

Готовый zip кладётся игрокам в `.minecraft/resourcepacks/`.

ВАЖНО: `items/paper.json` целиком генерирует `build_builditems.py` (в нём же CMD миньонов 70xxx/71xxx) —
не редактировать руками. Углы поворотов моделей: только 0 / ±22.5 / ±45.

`pack_zip.py` сортирует пути, использует фиксированные timestamp/mode и нормализует
переводы строк JSON/mcmeta в LF: одинаковое дерево `pack/` на Windows/Linux даёт
одинаковый ZIP и SHA-1. Публиковать нужно ровно проверенный артефакт full +
собранный из него lite.
