"""Layered version of wallpaper_001 (Psalm 23:1) for the animated Today screen.

Usage: python3 tools/artwork/pasture.py

Writes app/src/main/assets/animated/pasture/ (background, a horizontally seamless cloud
strip, one sprite per sheep, a grass band, a vignette and manifest.json) and regenerates
wallpaper_001.jpg as the composite of the same layers at rest, so the static wallpaper
and the animated scene always match.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
from scene import Scene, W, H, rgb, col_of, smoothstep, draw_sheep, draw_round_tree  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ASSETS = os.path.join(ROOT, 'app', 'src', 'main', 'assets')
OUT = os.path.join(ASSETS, 'animated', 'pasture')
WALL = os.path.join(ASSETS, 'wallpapers')

SHEEP = [(0.36, 0.505, 1.0, 1), (0.44, 0.512, 0.9, -1), (0.52, 0.508, 1.05, 1), (0.6, 0.5, 0.8, 1),
         (0.29, 0.515, 0.85, 1), (0.48, 0.52, 1.1, -1), (0.66, 0.512, 0.75, -1)]
SHEEP_SIZE = 64
CLOUD_Y1 = 0.25
VIGNETTE = 0.28


def rgba(arr_rgb, alpha):
    a = np.concatenate([np.clip(arr_rgb, 0, 1), np.clip(alpha, 0, 1)[..., None]], -1)
    return Image.fromarray((a * 255 + 0.5).astype(np.uint8), 'RGBA')


def capture(s, fn):
    """Runs a Scene drawing call but returns its RGBA layer instead of compositing it."""
    got = {}
    orig = s.composite

    def grab(im, blur=0.9):
        got['im'] = im.filter(ImageFilter.GaussianBlur(blur)) if blur else im
    s.composite = grab
    try:
        fn()
    finally:
        s.composite = orig
    return got['im']


def build():
    s = Scene(101)
    s.sky([(0, '#7fa6c9'), (0.22, '#bcd3e0'), (0.36, '#f3e2c0'), (0.45, '#f8d9a4')])
    s.sun(0.68, 0.335, 34, halo='#ffd896', strength=0.9)
    s.rays(0.68, 0.335, '#fff1cc', 0.10, n=9)

    # Clouds as their own layer: colour + alpha, exactly what lit_clouds would blend.
    m = s._cloud_mask(0.04, CLOUD_Y1, 5, 1 - 0.55)
    t = np.clip(1 - np.abs(s.yy - 0.3 * H) / (H * 0.35), 0, 1)[..., None]
    ccol = rgb('#e9eef3') * (1 - t) + rgb('#fff2d8') * t
    ca = m * 0.55
    cy1 = int((CLOUD_Y1 + 0.05) * H)
    cloud = rgba(np.broadcast_to(ccol, (H, W, 3))[:cy1], ca[:cy1])
    # Mirror-tile so the strip wraps seamlessly as it drifts.
    strip = Image.new('RGBA', (W * 2, cy1))
    strip.paste(cloud, (0, 0))
    strip.paste(cloud.transpose(Image.FLIP_LEFT_RIGHT), (W, 0))

    s.ridge(0.40, 0.09, '#9fb2c4', '#b6c2c6', rough=4, peak=(0.3, 1.1, 0.18), haze='#e9dcc4', haze_alpha=0.45)
    s.ridge(0.43, 0.05, '#7f9a8e', '#90a690', rough=6, haze='#e9dcc4', haze_alpha=0.3)
    s.mist(0.43, 0.02, '#fbe9c8', 0.45)
    s.hills(0.47, [(0.012, 1.3, 0.4), (0.006, 3.1, 1.2)], '#a7c46d', '#5f8a3c', light=(0.68, '#ffe7a8', 0.18))
    s.hills(0.53, [(0.02, 0.9, 2.0), (0.005, 2.6, 0.2)], '#86ad53', '#3f6a2c', light=(0.65, '#ffe0a0', 0.12))
    im, dr = s.layer()
    for x, h in ((0.12, 260), (0.18, 200), (0.86, 300)):
        draw_round_tree(dr, x * W, 0.49 * H, h, col_of('#3d5a2c'), s.rng)
    s.composite(im, 1.0)
    s.hills(0.88, [(0.01, 1.2, 0.5)], '#4d7a32', '#2e4d22')

    sprites = []
    for i, (x, y, k, f) in enumerate(SHEEP):
        im, dr = s.layer()
        draw_sheep(dr, x * W, y * H, SHEEP_SIZE * k, col_of('#f4ead8'), col_of('#2c2a26'), f)
        im = im.filter(ImageFilter.GaussianBlur(1.0))
        box = im.getbbox()
        box = (box[0] - 4, box[1] - 4, box[2] + 4, box[3] + 4)
        sprites.append((im.crop(box), box))

    grass_full = capture(s, lambda: s.grass(np.full(W, 0.86 * H), 2200, ['#3a6527', '#4f7f33', '#2c4f1e', '#6a9442'],
                                            height=(30, 110), lean=14))
    gy0 = int(0.86 * H - 220)
    grass = grass_full.crop((0, gy0, W, H))

    d = np.sqrt(((s.xx / W - 0.5) * 1.3) ** 2 + ((s.yy / H - 0.5) * 1.0) ** 2)
    vig = VIGNETTE * smoothstep(0.35, 0.95, d)
    vignette = rgba(np.zeros((H, W, 3), np.float32), vig).resize((W // 4, H // 4), Image.BILINEAR)

    bg = (np.clip(s.img, 0, 1) * 255 + 0.5).astype(np.uint8)
    return Image.fromarray(bg, 'RGB'), strip, sprites, grass, gy0, vignette, s.rng


def main():
    os.makedirs(OUT, exist_ok=True)
    bg, strip, sprites, grass, gy0, vignette, rng = build()
    bg.save(os.path.join(OUT, 'background.jpg'), 'JPEG', quality=86, optimize=True, progressive=True, subsampling=0)
    strip.save(os.path.join(OUT, 'clouds.webp'), 'WEBP', quality=82, method=6)
    grass.save(os.path.join(OUT, 'grass.webp'), 'WEBP', quality=85, method=6)
    vignette.save(os.path.join(OUT, 'vignette.webp'), 'WEBP', quality=90, method=6)
    manifest_sprites = []
    for i, (im, box) in enumerate(sprites):
        name = f'sheep_{i}.webp'
        im.save(os.path.join(OUT, name), 'WEBP', quality=90, method=6)
        manifest_sprites.append({
            'image': name, 'x': box[0], 'y': box[1],
            'wander': round(float(rng.uniform(10, 26)), 1),
            'period': round(float(rng.uniform(16, 30)), 1),
            'phase': round(float(rng.uniform(0, 1)), 3),
        })
    manifest = {
        'width': W, 'height': H,
        'background': 'background.jpg',
        'clouds': {'image': 'clouds.webp', 'y': 0, 'secondsPerLoop': 420},
        'sprites': manifest_sprites,
        'grass': {'image': 'grass.webp', 'y': gy0, 'sway': 7},
        'vignette': 'vignette.webp',
        'birds': True,
    }
    with open(os.path.join(OUT, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)

    # Static wallpaper = the same layers at rest.
    comp = bg.convert('RGBA')
    comp.alpha_composite(strip.crop((0, 0, W, strip.height)), (0, 0))
    for im, box in sprites:
        comp.alpha_composite(im, (box[0], box[1]))
    comp.alpha_composite(grass, (0, gy0))
    comp.alpha_composite(vignette.resize((W, H), Image.BILINEAR), (0, 0))
    arr = np.asarray(comp.convert('RGB'), np.float32) / 255.0
    arr += rng.normal(0, 0.008, (H, W, 1)).astype(np.float32)
    out = Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGB')
    out.save(os.path.join(WALL, 'wallpaper_001.jpg'), 'JPEG', quality=85, optimize=True, progressive=True, subsampling=0)
    out.resize((432, 960), Image.LANCZOS).save(os.path.join(WALL, 'thumbs', 'wallpaper_001.jpg'), 'JPEG', quality=82,
                                                optimize=True, progressive=True)
    print('pasture layers written to', OUT)


if __name__ == '__main__':
    main()
