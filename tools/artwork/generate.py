"""Render the placeholder wallpapers into the app's assets.

Usage: python3 tools/artwork/generate.py [wallpaper_001 ...]

Writes app/src/main/assets/wallpapers/<id>.jpg (1440x3200) and
app/src/main/assets/wallpapers/thumbs/<id>.jpg (432x960).
"""
import os
import sys
import time

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from scenes import SCENES  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'app', 'src', 'main', 'assets', 'wallpapers')
THUMBS = os.path.join(OUT, 'thumbs')


def main(ids):
    os.makedirs(THUMBS, exist_ok=True)
    for wid in ids or sorted(SCENES):
        fn, seed = SCENES[wid]
        t = time.time()
        im = fn(seed).finish(os.path.join(OUT, wid + '.jpg'))
        im.resize((432, 960), Image.LANCZOS).save(os.path.join(THUMBS, wid + '.jpg'), 'JPEG', quality=82, optimize=True, progressive=True)
        print(f'{wid} {fn.__name__} {time.time() - t:.1f}s')


if __name__ == '__main__':
    main(sys.argv[1:])
