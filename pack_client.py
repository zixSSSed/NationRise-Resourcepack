# -*- coding: utf-8 -*-
"""Собирает пак для локального клиента одной командой.

    py -3.13 pack_client.py

Запускать ПОСЛЕ старта сервера. BetterModel пересобирает свой пак на каждом запуске и
подписывает кости своими именами; пак от прошлого запуска эти имена не знает, и клиент
рисует новые модели старыми кусками — не пусто, а мешанина из чужих деталей. Именно так
Цербер один раз собрался из обломков сундука и рыцаря.

Три шага подряд: наш пак (иконки, шрифт, звуки) -> пак моделей -> общий архив в папку
ресурспаков клиента.
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
STEPS = [
    ("наш пак: иконки, шрифт, звуки", "pack_zip.py", True),
    ("пак моделей BetterModel", "build_models_pack.py", False),
    ("общий пак для клиента", "build_all_pack.py", False),
]


def main():
    for i, (title, script, quiet) in enumerate(STEPS, 1):
        # flush обязателен: вывод дочерних скриптов идёт в тот же поток мимо нашего буфера,
        # и без него заголовки шагов всплывают после их же вывода.
        print(f"[{i}/{len(STEPS)}] {title}", flush=True)
        res = subprocess.run([sys.executable, str(HERE / script)],
                             capture_output=quiet, text=True, encoding="utf-8")
        if res.returncode != 0:
            if quiet and res.stdout:
                print(res.stdout)
            if quiet and res.stderr:
                print(res.stderr)
            print(f"\nОШИБКА на шаге «{title}».")
            return 1
    print("\nГотово. В игре: Настройки → Наборы ресурсов → NationRise-ALL.")
    print("Если пак уже был включён — переподключитесь к серверу, иначе клиент оставит старую копию.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
