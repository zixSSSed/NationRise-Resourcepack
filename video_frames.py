# -*- coding: utf-8 -*-
"""Режет видео боссфайта на кадры, чтобы их можно было разобрать глазами.

    py -3.13 video_frames.py <файл.mp4> [кадров-в-секунду]

Видео целиком мне не посмотреть, а вот кадры — обычные картинки. Раскладывает их в папку
рядом с видео и печатает пути. По умолчанию два кадра в секунду: анимации длятся от одной
до пяти секунд, и на такой частоте видно и начало движения, и обрыв, если он есть.

ffmpeg отдельно ставить не надо — он приезжает внутри imageio-ffmpeg, который уже стоит.
"""

import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg


def main():
    if len(sys.argv) < 2:
        raise SystemExit("как: py -3.13 video_frames.py <файл.mp4> [кадров-в-секунду]")
    src = Path(sys.argv[1])
    if not src.exists():
        raise SystemExit(f"нет файла: {src}")
    fps = sys.argv[2] if len(sys.argv) > 2 else "2"

    out = src.parent / (src.stem + "_frames")
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.jpg"):
        old.unlink()

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    # Ширина 960: больше не нужно — важны силуэт и фаза движения, а не текстуры,
    # а мелкие кадры читаются заметно хуже.
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(src),
           "-vf", f"fps={fps},scale=960:-2", "-q:v", "3", str(out / "f%04d.jpg")]
    subprocess.run(cmd, check=True)

    frames = sorted(out.glob("*.jpg"))
    total = sum(f.stat().st_size for f in frames)
    print(f"кадров: {len(frames)}  ({total // 1024} КБ)  -> {out}")
    for f in frames:
        print(" ", f)


if __name__ == "__main__":
    main()
