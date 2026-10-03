"""One recipe per wallpaper. Each returns a finished Scene.

Layout notes (where the app draws the verse):
  bottom -> verse band ~58-80% height, subject lives in 18-52%
  center -> verse band ~38-62%, subject above (sky) and/or below (land)
  top    -> verse band ~16-40%, subject lives in 50-86%
"""
import numpy as np

from scene import (Scene, W, H, rgb, col_of, draw_person, draw_sheep, draw_cross, draw_bird,
                   draw_dove, draw_church, draw_house, draw_open_book, draw_round_tree, draw_pine)


def flock(s, dr, spots, size, body='#f4ead8', head='#2c2a26'):
    for (x, y, k, f) in spots:
        draw_sheep(dr, x * W, y * H, size * k, col_of(body), col_of(head), f)


def shepherd_pasture(seed):
    """Psalm 23:1 - green pasture, sheep, mountains, morning light. layout: bottom"""
    s = Scene(seed)
    s.sky([(0, '#7fa6c9'), (0.22, '#bcd3e0'), (0.36, '#f3e2c0'), (0.45, '#f8d9a4')])
    s.sun(0.68, 0.335, 34, halo='#ffd896', strength=0.9)
    s.rays(0.68, 0.335, '#fff1cc', 0.10, n=9)
    s.lit_clouds(0.04, 0.26, '#e9eef3', '#fff2d8', 0.3, alpha=0.55, scale=5, coverage=0.55)
    s.ridge(0.40, 0.09, '#9fb2c4', '#b6c2c6', rough=4, peak=(0.3, 1.1, 0.18), haze='#e9dcc4', haze_alpha=0.45)
    s.ridge(0.43, 0.05, '#7f9a8e', '#90a690', rough=6, haze='#e9dcc4', haze_alpha=0.3)
    s.mist(0.43, 0.02, '#fbe9c8', 0.45)
    top = s.hills(0.47, [(0.012, 1.3, 0.4), (0.006, 3.1, 1.2)], '#a7c46d', '#5f8a3c', light=(0.68, '#ffe7a8', 0.18))
    s.hills(0.53, [(0.02, 0.9, 2.0), (0.005, 2.6, 0.2)], '#86ad53', '#3f6a2c', light=(0.65, '#ffe0a0', 0.12))
    im, dr = s.layer()
    flock(s, dr, [(0.36, 0.505, 1.0, 1), (0.44, 0.512, 0.9, -1), (0.52, 0.508, 1.05, 1), (0.6, 0.5, 0.8, 1),
                  (0.29, 0.515, 0.85, 1), (0.48, 0.52, 1.1, -1), (0.66, 0.512, 0.75, -1)], 64)
    for x, h in ((0.12, 260), (0.18, 200), (0.86, 300)):
        draw_round_tree(dr, x * W, 0.49 * H, h, col_of('#3d5a2c'), s.rng)
    s.composite(im, 1.0)
    s.hills(0.88, [(0.01, 1.2, 0.5)], '#4d7a32', '#2e4d22')
    s.grass(np.full(W, 0.86 * H), 2200, ['#3a6527', '#4f7f33', '#2c4f1e', '#6a9442'], height=(30, 110), lean=14)
    s.vignette(0.28)
    return s


def still_lake(seed):
    """Psalm 46:10 - calm lake, mountains, soft sunrise. layout: center"""
    s = Scene(seed)
    s.sky([(0, '#3e5579'), (0.18, '#8a9dbb'), (0.3, '#e7c3b0'), (0.36, '#f6d5ad')])
    s.sun(0.5, 0.345, 30, halo='#ffcf9a', strength=0.8)
    s.clouds(0.06, 0.22, '#f0d2c4', 0.35, scale=4, coverage=0.58)
    s.ridge(0.355, 0.12, '#55678a', '#6c7896', rough=4, peak=(0.62, 1.2, 0.14), haze='#e8c9b6', haze_alpha=0.35)
    s.ridge(0.365, 0.05, '#3d4c66', '#3d4c66', rough=7, haze='#d8b9a8', haze_alpha=0.2)
    top = s.ridge(0.37, 0.008, '#26324a', '#26324a', rough=10)
    s.pines(top, 140, '#1d2638', height=(18, 46), y_jitter=6)
    s.water(0.37, tint='#2b3c58', darken=0.8, ripple=2.0, glitter_x=0.5, glitter_color='#ffd9ae')
    s.mist(0.372, 0.012, '#f6dcc4', 0.5)
    s.vignette(0.3)
    return s


def strong_sunrise_figure(seed):
    """Isaiah 41:10 - sunrise over mountains, a person standing confidently. layout: top"""
    s = Scene(seed)
    s.sky([(0, '#1f2f52'), (0.25, '#4c5f8c'), (0.48, '#e79a73'), (0.58, '#ffcf8a')])
    s.sun(0.5, 0.575, 46, halo='#ffbf70', strength=1.1)
    s.rays(0.5, 0.575, '#ffe1a6', 0.16, n=13, length=1900)
    s.lit_clouds(0.36, 0.5, '#8a6c86', '#ffc48c', 0.55, alpha=0.6, scale=5, coverage=0.56)
    s.ridge(0.62, 0.08, '#6a5a78', '#7a6a80', rough=4, haze='#f2b48a', haze_alpha=0.35)
    s.mist(0.62, 0.015, '#ffd4a2', 0.5)
    top = s.ridge(0.68, 0.05, '#2c2638', '#1c1826', rough=5, peak=(0.5, 1.3, 0.18))
    im, dr = s.layer()
    tx = int(0.5 * W)
    draw_person(dr, tx, top[tx] + 6, 230, col_of('#120f18'), robe=False)
    s.composite(im, 0.9)
    s.hills(0.9, [(0.015, 1.1, 0.2)], '#16121c', '#0e0b12')
    s.vignette(0.3)
    return s


def summit_forward(seed):
    """Philippians 4:13 - dramatic sunrise, a person walking up toward the summit. layout: bottom"""
    s = Scene(seed)
    s.sky([(0, '#26375e'), (0.2, '#6f6f97'), (0.38, '#f0a36b'), (0.46, '#ffd590')])
    s.sun(0.62, 0.43, 40, halo='#ffbe6e', strength=1.1)
    s.rays(0.62, 0.43, '#ffe0a0', 0.2, n=12)
    s.lit_clouds(0.08, 0.32, '#5d5a80', '#ffb98a', 0.36, alpha=0.65, scale=4, coverage=0.54)
    s.ridge(0.44, 0.1, '#6f5f7d', '#7c6d84', rough=4, peak=(0.25, 1.2, 0.15), haze='#f2b48a', haze_alpha=0.3)
    s.mist(0.45, 0.02, '#ffd09a', 0.45)
    top = s.ridge(0.53, 0.15, '#3a3046', '#221c2c', rough=5, peak=(0.55, 1.25, 0.22))
    im, dr = s.layer()
    px = int(0.47 * W)
    draw_person(dr, px, top[px] + 4, 120, col_of('#15111b'), robe=False, stride=0.9)
    s.composite(im, 0.8)
    s.hills(0.9, [(0.01, 1.3, 0.8)], '#1d1825', '#120f17')
    s.vignette(0.32)
    return s


def rest_field(seed):
    """Matthew 11:28 - peaceful field, soft sunlight, distant robed figure. layout: center"""
    s = Scene(seed)
    s.sky([(0, '#8db3d6'), (0.2, '#c6dbe8'), (0.32, '#f8ecd2')])
    s.sun(0.75, 0.15, 30, halo='#fff0c8', strength=0.45)
    s.rays(0.75, 0.15, '#fff6dc', 0.08, n=10, length=2600)
    s.clouds(0.02, 0.2, '#ffffff', 0.5, scale=5, coverage=0.55)
    s.ridge(0.66, 0.035, '#9db7b2', '#a9c0b2', rough=4, haze='#f6ecd6', haze_alpha=0.5)
    top = s.hills(0.7, [(0.012, 1.0, 0.3), (0.006, 2.4, 1.0)], '#c8d684', '#87a856', light=(0.75, '#fff0b8', 0.2))
    s.hills(0.75, [(0.015, 0.8, 1.8)], '#a5c066', '#6c9145', light=(0.7, '#ffe9a6', 0.14))
    s.flowers(np.full(W, 0.76 * H), 900, ['#fff6e0', '#f6e27a', '#ffffff', '#e9c6e6'])
    im, dr = s.layer()
    draw_person(dr, 0.58 * W, 0.722 * H, 120, col_of('#3d3a2e'), robe=True, hair=True)
    for x, h in ((0.14, 300),):
        draw_round_tree(dr, x * W, 0.71 * H, h, col_of('#4a6a33'), s.rng)
    s.composite(im, 1.0)
    s.grass(np.full(W, 0.86 * H), 1800, ['#5b8a3a', '#7aa34b', '#46702c', '#93b55e'], height=(40, 130))
    s.vignette(0.22)
    return s


def cross_sunset(seed):
    """John 3:16 - a cross on a hill at sunset. layout: bottom"""
    s = Scene(seed)
    s.sky([(0, '#2a2547'), (0.22, '#7a4e72'), (0.4, '#ec8a5c'), (0.5, '#ffcc7e')])
    s.sun(0.5, 0.47, 52, halo='#ffb366', strength=1.2)
    s.rays(0.5, 0.47, '#ffd59c', 0.18, n=14)
    s.lit_clouds(0.12, 0.4, '#5a3d62', '#ffad78', 0.42, alpha=0.6, scale=4, coverage=0.55)
    s.ridge(0.5, 0.04, '#6b4a66', '#6b4a66', rough=5, haze='#f39a6a', haze_alpha=0.35)
    top = s.hills(0.53, [(0.03, 0.5, 1.4), (0.006, 2.2, 0.4)], '#2a1d2c', '#1a121c')
    im, dr = s.layer()
    cx = int(0.5 * W)
    draw_cross(dr, cx, top[cx] + 8, 420, col_of('#160f18'))
    s.composite(im, 0.9)
    s.glow(0.5, 0.42, 380, '#ffcf8f', 0.18, 1.5)
    s.vignette(0.32)
    return s


def starry_dawn(seed):
    """Jeremiah 29:11 - stars fading into dawn over quiet hills. layout: center"""
    s = Scene(seed)
    s.sky([(0, '#0b1230'), (0.3, '#1d2f5a'), (0.6, '#6b6f9c'), (0.72, '#f0b68e'), (0.76, '#ffd7a0')])
    s.milky_way(-0.4, 0.22, 0.1, 0.2)
    s.stars(500, y_max=0.6)
    s.glow(0.5, 0.76, 700, '#ffc58a', 0.35, 1.4)
    s.ridge(0.77, 0.04, '#3c3a5c', '#3c3a5c', rough=4, haze='#e0a882', haze_alpha=0.25)
    top = s.hills(0.8, [(0.02, 0.7, 0.9), (0.008, 2.0, 2.0)], '#1d1c33', '#11111f')
    im, dr = s.layer()
    tx = int(0.68 * W)
    draw_round_tree(dr, tx, top[tx] + 10, 240, col_of('#0f0f1c'), s.rng)
    s.composite(im, 0.9)
    s.vignette(0.3)
    return s


def forest_path(seed):
    """Proverbs 3:5-6 - a straight path through a meadow toward the light. layout: top"""
    s = Scene(seed)
    s.sky([(0, '#94b8d4'), (0.3, '#d6e2e2'), (0.5, '#fbeccb')])
    s.sun(0.5, 0.5, 34, halo='#fff0c2', strength=0.9)
    s.rays(0.5, 0.5, '#fff5d8', 0.14, n=12)
    s.clouds(0.03, 0.3, '#ffffff', 0.45, scale=5, coverage=0.58)
    s.ridge(0.53, 0.06, '#8fa8b0', '#9fb2b0', rough=4, haze='#f6ead2', haze_alpha=0.5)
    top = s.hills(0.56, [(0.008, 1.1, 0.2)], '#a7c179', '#5b8a3a', light=(0.5, '#fff0b0', 0.2))
    im, dr = s.layer()
    # perspective path from the bottom centre to the horizon
    dr.polygon([(0.497 * W, 0.565 * H), (0.503 * W, 0.565 * H), (0.7 * W, H), (0.3 * W, H)], fill=col_of('#e3d3a8'))
    s.composite(im, 1.5)
    s.pines(top, 26, '#2f4a2c', height=(160, 420), x_range=(0.0, 0.3), y_jitter=120)
    s.pines(top, 26, '#2f4a2c', height=(160, 420), x_range=(0.7, 1.0), y_jitter=120)
    s.grass(np.full(W, 0.6 * H), 2600, ['#5b8a3a', '#7aa34b', '#46702c'], height=(30, 140))
    im, dr = s.layer()
    dr.polygon([(0.497 * W, 0.565 * H), (0.503 * W, 0.565 * H), (0.62 * W, H), (0.38 * W, H)], fill=col_of('#ead9ad', 200))
    s.composite(im, 3)
    s.vignette(0.25)
    return s


def mountain_valley(seed):
    """Psalm 121:8 - a road winding through a protected valley. layout: center"""
    s = Scene(seed)
    s.sky([(0, '#5e83ad'), (0.2, '#a9c3d8'), (0.33, '#f1e3cc')])
    s.clouds(0.03, 0.22, '#ffffff', 0.5, scale=5, coverage=0.55)
    s.ridge(0.33, 0.12, '#6c84a0', '#8a9cb0', rough=4, peak=(0.2, 1.1, 0.15), haze='#e9e0d0', haze_alpha=0.35)
    s.ridge(0.36, 0.12, '#56707f', '#6d8490', rough=4, peak=(0.85, 1.1, 0.15), haze='#e9e0d0', haze_alpha=0.25)
    s.mist(0.37, 0.02, '#f6efe2', 0.5)
    top = s.hills(0.66, [(0.02, 0.8, 0.5), (0.008, 2.2, 0.1)], '#7c9c5a', '#3f6532', light=(0.4, '#ffecb0', 0.15))
    im, dr = s.layer()
    pts = []
    for i in range(80):
        t = i / 79
        y = 0.66 * H + t * 0.34 * H
        x = 0.5 * W + np.sin(t * 5.0) * W * 0.12 * t
        pts.append((x, y, 3 + t * 90))
    for (x, y, w) in pts:
        dr.ellipse([x - w, y - w * 0.2, x + w, y + w * 0.2], fill=col_of('#d9c7a0'))
    draw_house(dr, 0.62 * W, 0.668 * H, 70, col_of('#3b3a33'), col_of('#ffd27a'))
    s.composite(im, 1.2)
    s.pines(top, 60, '#2a4127', height=(60, 200), x_range=(0.0, 0.25), y_jitter=200)
    s.pines(top, 50, '#2a4127', height=(60, 200), x_range=(0.8, 1.0), y_jitter=200)
    s.vignette(0.25)
    return s


def wheat_gratitude(seed):
    """1 Thessalonians 5:18 - golden wheat field at evening. layout: center"""
    s = Scene(seed)
    s.sky([(0, '#4d6a9a'), (0.25, '#d7a98a'), (0.42, '#ffd38c'), (0.5, '#ffe2a6')])
    s.sun(0.3, 0.62, 44, halo='#ffc874', strength=1.0)
    s.lit_clouds(0.06, 0.3, '#8e8cb0', '#ffd6a6', 0.35, alpha=0.5, scale=4, coverage=0.57)
    s.ridge(0.63, 0.02, '#b7926e', '#b7926e', rough=5, haze='#ffd59a', haze_alpha=0.4)
    top = s.hills(0.65, [(0.006, 1.0, 0.3)], '#e6b860', '#b5803a', light=(0.3, '#fff0b0', 0.3))
    s.grass(top, 7000, ['#d9a64e', '#e9c06a', '#c28a3c', '#f2d38a', '#a8762e'], height=(40, 180), lean=10)
    im, dr = s.layer()
    for i in range(500):
        x = s.rng.uniform(0, W)
        y = s.rng.uniform(0.66 * H, H)
        k = (y - 0.66 * H) / (0.34 * H)
        l = 14 + 40 * k
        dr.ellipse([x - l * 0.18, y - l, x + l * 0.18, y], fill=col_of('#f0c470', 230))
    s.composite(im, 0.9)
    s.vignette(0.3)
    return s


def worship_sky(seed):
    """Psalm 150:6 - birds rising into a radiant morning sky. layout: bottom"""
    s = Scene(seed)
    s.sky([(0, '#5d86c1'), (0.25, '#a4c3e4'), (0.5, '#fde8c6'), (0.62, '#ffd59c')])
    s.sun(0.5, 0.62, 48, halo='#ffd38a', strength=1.0)
    s.rays(0.5, 0.62, '#fff2cc', 0.22, n=16, length=2600)
    s.lit_clouds(0.08, 0.4, '#e2e9f3', '#fff4dc', 0.45, alpha=0.6, scale=5, coverage=0.55)
    im, dr = s.layer()
    for (x, y, sz) in [(0.3, 0.28, 34), (0.38, 0.24, 28), (0.46, 0.3, 40), (0.55, 0.22, 30), (0.62, 0.27, 36),
                       (0.42, 0.18, 22), (0.68, 0.34, 26), (0.34, 0.36, 24), (0.58, 0.38, 20)]:
        draw_bird(dr, x * W, y * H, sz, col_of('#2b2f3d'), width=5)
    s.composite(im, 0.8)
    s.ridge(0.66, 0.05, '#7d8fa8', '#8b98a8', rough=4, haze='#fbe2c0', haze_alpha=0.4)
    s.mist(0.665, 0.015, '#fff0d6', 0.5)
    top = s.hills(0.72, [(0.015, 0.9, 0.4)], '#486a52', '#22362a')
    im, dr = s.layer()
    draw_person(dr, 0.5 * W, top[int(0.5 * W)] + 8, 150, col_of('#141c18'), robe=True, arms_up=True)
    s.composite(im, 0.8)
    s.vignette(0.25)
    return s


def dove_waters(seed):
    """John 14:27 - a dove over still, peaceful water. layout: bottom"""
    s = Scene(seed)
    s.sky([(0, '#3f5f8a'), (0.3, '#86a0bf'), (0.47, '#e9dccb')])
    s.glow(0.5, 0.3, 420, '#fff6e0', 0.18, 1.5)
    s.clouds(0.02, 0.2, '#e8eef5', 0.4, scale=5, coverage=0.56)
    s.ridge(0.47, 0.025, '#7d92ab', '#7d92ab', rough=4, haze='#e2d8cc', haze_alpha=0.45)
    s.water(0.48, tint='#4d6688', darken=0.85, ripple=1.5)
    s.glow(0.5, 0.3, 230, '#fffbe8', 0.22, 1.5)
    im, dr = s.layer()
    draw_dove(dr, 0.5 * W, 0.3 * H, 190, col_of('#fbfbf6'))
    s.composite(im, 1.0)
    s.vignette(0.25)
    return s


def ocean_sunrise(seed):
    """Romans 15:13 - sunrise over the ocean. layout: top"""
    s = Scene(seed)
    s.sky([(0, '#33497a'), (0.35, '#a08bb0'), (0.55, '#ffb98a'), (0.6, '#ffd7a0')])
    s.lit_clouds(0.2, 0.5, '#8a7aa0', '#ffc69a', 0.55, alpha=0.6, scale=4, coverage=0.56)
    s.sun(0.5, 0.585, 50, halo='#ffbe7a', strength=1.1)
    s.water(0.6, tint='#3a4a72', darken=0.82, ripple=3.0, glitter_x=0.5, glitter_color='#ffd09a')
    s.vignette(0.28)
    return s


def family_home(seed):
    """Joshua 24:15 - a warm home on a hill at dusk. layout: top"""
    s = Scene(seed)
    s.sky([(0, '#1e2a4a'), (0.35, '#5a5f8c'), (0.6, '#e4a07e'), (0.66, '#f6c592')])
    s.stars(260, y_max=0.4)
    s.glow(0.7, 0.66, 600, '#ffb47a', 0.3, 1.4)
    s.ridge(0.68, 0.04, '#5b5070', '#5b5070', rough=4, haze='#e8a582', haze_alpha=0.3)
    top = s.hills(0.74, [(0.03, 0.6, 1.0), (0.006, 2.3, 0.4)], '#2a2b3a', '#171822')
    im, dr = s.layer()
    hx = int(0.48 * W)
    s.glow(0.48, top[hx] / H - 0.02, 160, '#ffc070', 0.25, 1.4)
    draw_house(dr, hx, top[hx] + 10, 170, col_of('#14141c'), col_of('#ffcc78'))
    draw_round_tree(dr, 0.3 * W, top[int(0.3 * W)] + 14, 260, col_of('#12121a'), s.rng)
    draw_person(dr, 0.6 * W, top[int(0.6 * W)] + 18, 80, col_of('#101016'), robe=False)
    draw_person(dr, 0.63 * W, top[int(0.63 * W)] + 18, 70, col_of('#101016'), robe=True)
    draw_person(dr, 0.655 * W, top[int(0.655 * W)] + 18, 44, col_of('#101016'), robe=False)
    s.composite(im, 0.9)
    s.vignette(0.3)
    return s


def two_walk(seed):
    """Mark 10:9 - two people walking together toward the sunset. layout: top"""
    s = Scene(seed)
    s.sky([(0, '#3c4d7c'), (0.3, '#c58a8e'), (0.52, '#ffbf86'), (0.58, '#ffdca8')])
    s.sun(0.5, 0.57, 46, halo='#ffbd7a', strength=1.0)
    s.lit_clouds(0.1, 0.45, '#8c6e8e', '#ffc596', 0.5, alpha=0.5, scale=4, coverage=0.57)
    s.ridge(0.6, 0.03, '#8a6a7c', '#8a6a7c', rough=4, haze='#ffb68a', haze_alpha=0.35)
    top = s.hills(0.64, [(0.004, 1.0, 0.3)], '#5c4a50', '#2b2228')
    im, dr = s.layer()
    dr.polygon([(0.49 * W, 0.645 * H), (0.51 * W, 0.645 * H), (0.62 * W, H), (0.38 * W, H)], fill=col_of('#c99a78', 200))
    s.composite(im, 2)
    s.grass(top, 2400, ['#3a2d33', '#4a3a3e', '#2b2226'], height=(30, 140))
    im, dr = s.layer()
    draw_person(dr, 0.475 * W, 0.71 * H, 170, col_of('#1a1418'), robe=False, stride=0.5)
    draw_person(dr, 0.525 * W, 0.71 * H, 150, col_of('#1a1418'), robe=True, hair=True, stride=0.5)
    dr.line([0.475 * W + 26, 0.71 * H - 82, 0.525 * W - 23, 0.71 * H - 72], fill=col_of('#1a1418'), width=8)
    s.composite(im, 0.8)
    s.vignette(0.3)
    return s


def lamp_word(seed):
    """Psalm 119:105 - an open Bible glowing on a stone at night, path of light. layout: top"""
    s = Scene(seed)
    s.sky([(0, '#0d1428'), (0.45, '#1f2c4c'), (0.62, '#3a3f5c')])
    s.stars(600, y_max=0.6)
    s.ridge(0.6, 0.05, '#252c44', '#1e2438', rough=4)
    top = s.hills(0.66, [(0.01, 0.8, 0.2)], '#1d2233', '#121520')
    im, dr = s.layer()
    dr.ellipse([0.33 * W, 0.735 * H, 0.67 * W, 0.79 * H], fill=col_of('#2a2a33'))
    s.composite(im, 2)
    s.glow(0.5, 0.7, 520, '#ffcf7a', 0.22, 1.4)
    im, dr = s.layer()
    draw_open_book(dr, 0.5 * W, 0.755 * H, 280, col_of('#efdcb4'), col_of('#8a6c40'))
    s.composite(im, 1.0)
    s.glow(0.5, 0.69, 200, '#fff1c8', 0.12, 1.6)
    s.vignette(0.35)
    return s


def cross_mountain(seed):
    """1 Corinthians 1:18 - a cross on a mountaintop with rays of light. layout: bottom"""
    s = Scene(seed)
    s.sky([(0, '#26385e'), (0.25, '#7287ad'), (0.45, '#e9c9a6')])
    s.glow(0.5, 0.24, 700, '#fff0cf', 0.45, 1.3)
    s.rays(0.5, 0.24, '#fff4da', 0.26, n=15, length=2600)
    s.lit_clouds(0.03, 0.2, '#8f9cc0', '#fff0d8', 0.2, alpha=0.5, scale=5, coverage=0.58)
    s.ridge(0.48, 0.08, '#6f7b9a', '#7c869e', rough=4, haze='#ecd7bf', haze_alpha=0.35)
    s.mist(0.48, 0.02, '#f6e2c8', 0.45)
    top = s.ridge(0.55, 0.16, '#38405a', '#262b3e', rough=5, peak=(0.5, 1.3, 0.16))
    im, dr = s.layer()
    cx = int(0.5 * W)
    draw_cross(dr, cx, top[cx] + 6, 260, col_of('#151927'))
    s.composite(im, 0.8)
    s.vignette(0.3)
    return s


def heavens_declare(seed):
    """Psalm 19:1 - the Milky Way over mountains. layout: bottom"""
    s = Scene(seed)
    s.sky([(0, '#05081a'), (0.4, '#121b3d'), (0.58, '#2e3a66'), (0.64, '#5a5684')])
    s.milky_way(-0.6, 0.28, 0.13, 0.3)
    s.stars(900, y_max=0.62)
    s.glow(0.5, 0.64, 600, '#8f7cb8', 0.25, 1.5)
    s.ridge(0.6, 0.1, '#1f2544', '#181d36', rough=4, peak=(0.62, 1.1, 0.16))
    top = s.ridge(0.66, 0.05, '#0f1326', '#0a0d1a', rough=6)
    s.pines(top, 70, '#070a14', height=(40, 140), y_jitter=20)
    s.hills(0.92, [(0.01, 1.0, 0.0)], '#070a14', '#05070f')
    s.vignette(0.3)
    return s


def good_shepherd(seed):
    """John 10:11 - a distant shepherd seen from behind, leading sheep. layout: top"""
    s = Scene(seed)
    s.sky([(0, '#6c8fbf'), (0.3, '#c2d4e0'), (0.5, '#fbe5c0'), (0.56, '#ffd8a0')])
    s.sun(0.62, 0.53, 38, halo='#ffd590', strength=1.0)
    s.rays(0.62, 0.53, '#fff0c8', 0.14, n=11)
    s.clouds(0.03, 0.3, '#ffffff', 0.45, scale=5, coverage=0.56)
    s.ridge(0.56, 0.05, '#8ba2b6', '#9cadb8', rough=4, haze='#f8e2c0', haze_alpha=0.45)
    top = s.hills(0.6, [(0.015, 0.8, 0.5), (0.005, 2.2, 1.2)], '#9cbb63', '#577f36', light=(0.62, '#ffe7a6', 0.22))
    s.hills(0.7, [(0.018, 0.7, 2.2)], '#7ea24e', '#3d632a', light=(0.6, '#ffe2a0', 0.12))
    im, dr = s.layer()
    sx = 0.56
    draw_person(dr, sx * W, 0.685 * H, 190, col_of('#3a2f26'), robe=True, staff=True, hair=True)
    flock(s, dr, [(0.4, 0.71, 1.0, 1), (0.47, 0.72, 1.1, 1), (0.34, 0.725, 0.95, 1), (0.42, 0.735, 1.15, 1),
                  (0.5, 0.74, 1.2, 1), (0.37, 0.75, 1.25, 1), (0.28, 0.74, 1.1, 1), (0.45, 0.76, 1.3, 1)], 70)
    s.composite(im, 1.0)
    s.grass(np.full(W, 0.8 * H), 2400, ['#3a6527', '#4f7f33', '#2c4f1e', '#6a9442'], height=(40, 140))
    s.vignette(0.25)
    return s


def misty_faith(seed):
    """Hebrews 11:1 - layered misty mountains, a path toward unseen light. layout: center"""
    s = Scene(seed)
    s.sky([(0, '#4a5f80'), (0.2, '#9fb0c4'), (0.3, '#e8dcc8')])
    s.glow(0.5, 0.28, 500, '#fff0d4', 0.4, 1.4)
    s.ridge(0.3, 0.06, '#8a9ab0', '#9aa6b6', rough=4, haze='#e8dcc8', haze_alpha=0.5)
    s.mist(0.3, 0.02, '#f2e8d8', 0.6)
    for i, (b, c1) in enumerate([(0.66, '#6f8098'), (0.72, '#56667e'), (0.79, '#3e4c62'), (0.87, '#2a3546')]):
        s.ridge(b, 0.05, c1, c1, rough=4 + i)
        s.mist(b + 0.005, 0.015, '#e9e2d8', 0.45 - i * 0.08)
    im, dr = s.layer()
    draw_person(dr, 0.52 * W, 0.70 * H, 90, col_of('#323d4f'), robe=True)
    s.composite(im, 0.8)
    s.hills(0.95, [(0.01, 1.0, 0.0)], '#1d2532', '#141a24')
    s.vignette(0.25)
    return s


def new_morning(seed):
    """Lamentations 3:22-23 - mist rising off a river at first light. layout: top"""
    s = Scene(seed)
    s.sky([(0, '#7c98c0'), (0.3, '#e6d6d6'), (0.5, '#ffe2bc'), (0.55, '#ffeacc')])
    s.sun(0.4, 0.52, 40, halo='#ffdba0', strength=0.9)
    s.clouds(0.05, 0.3, '#ffffff', 0.35, scale=4, coverage=0.58)
    s.ridge(0.55, 0.05, '#9aa9bc', '#a4b0bd', rough=4, haze='#fbe6cc', haze_alpha=0.5)
    top = s.hills(0.6, [(0.01, 1.0, 0.4)], '#7e9c74', '#56755a', light=(0.4, '#ffe0a8', 0.2))
    s.pines(top, 60, '#4f6a55', height=(50, 140), y_jitter=20)
    s.water(0.63, tint='#7d8ea8', darken=0.88, ripple=2.0, glitter_x=0.4, glitter_color='#ffe6b8')
    s.mist(0.63, 0.03, '#fff4e4', 0.6)
    s.hills(0.86, [(0.02, 0.8, 1.5)], '#3d5440', '#26362a')
    s.grass(np.full(W, 0.86 * H), 1600, ['#3d5a35', '#4f6e44', '#2c4227'], height=(40, 150))
    s.vignette(0.22)
    return s


def courage_peak(seed):
    """Joshua 1:9 - a hiker standing on a high ridge above the clouds. layout: top"""
    s = Scene(seed)
    s.sky([(0, '#2a4a7c'), (0.3, '#7ea2cc'), (0.5, '#f0dcc0')])
    s.sun(0.75, 0.42, 36, halo='#ffe2a6', strength=0.9)
    s.rays(0.75, 0.42, '#fff2d0', 0.12, n=10)
    s.clouds(0.5, 0.62, '#ffffff', 0.85, scale=5, coverage=0.45, soft=0.25)
    s.ridge(0.58, 0.06, '#7c8ca8', '#8d9ab0', rough=4, peak=(0.2, 1.2, 0.12), haze='#f0e2d0', haze_alpha=0.3)
    s.clouds(0.56, 0.68, '#fbf6f0', 0.8, scale=5, coverage=0.48, soft=0.25)
    top = s.ridge(0.82, 0.2, '#3d4658', '#262c38', rough=5, peak=(0.48, 1.3, 0.2))
    im, dr = s.layer()
    px = int(0.48 * W)
    draw_person(dr, px, top[px] + 5, 160, col_of('#151820'), robe=False)
    s.composite(im, 0.8)
    s.vignette(0.28)
    return s


def eagles_wings(seed):
    """Isaiah 40:31 - eagles soaring over mountain peaks. layout: bottom"""
    s = Scene(seed)
    s.sky([(0, '#3a6aa8'), (0.3, '#8cb4dc'), (0.52, '#f2e4cc')])
    s.sun(0.3, 0.2, 34, halo='#fff2cf', strength=0.8)
    s.clouds(0.05, 0.4, '#ffffff', 0.5, scale=5, coverage=0.57)
    im, dr = s.layer()
    for (x, y, sz) in [(0.45, 0.25, 90), (0.62, 0.32, 70), (0.36, 0.36, 55)]:
        c = col_of('#1e2533')
        cx, cy = x * W, y * H
        wing = [(cx - sz * 2.0, cy - sz * 0.15), (cx - sz * 1.0, cy - sz * 0.45), (cx - sz * 0.25, cy - sz * 0.1), (cx, cy),
                (cx + sz * 0.25, cy - sz * 0.1), (cx + sz * 1.0, cy - sz * 0.45), (cx + sz * 2.0, cy - sz * 0.15),
                (cx + sz * 1.0, cy - sz * 0.2), (cx + sz * 0.2, cy + sz * 0.15), (cx, cy + sz * 0.45), (cx - sz * 0.2, cy + sz * 0.15), (cx - sz * 1.0, cy - sz * 0.2)]
        dr.polygon(wing, fill=c)
    s.composite(im, 0.8)
    s.ridge(0.52, 0.16, '#5c6f8c', '#7a8aa2', rough=4, peak=(0.62, 1.2, 0.14), haze='#ebe2d4', haze_alpha=0.3)
    s.mist(0.53, 0.02, '#f4ede2', 0.5)
    top = s.ridge(0.6, 0.08, '#3a4a5e', '#2c394a', rough=5)
    s.pines(top, 120, '#1f2a36', height=(40, 160), y_jitter=60)
    s.hills(0.92, [(0.01, 1.0, 0.0)], '#1a232e', '#121921')
    s.vignette(0.25)
    return s


def chapel_dawn(seed):
    """Psalm 95:6 - a small chapel on a hill at dawn. layout: top"""
    s = Scene(seed)
    s.sky([(0, '#2d3b66'), (0.3, '#8a86ad'), (0.55, '#f3b98f'), (0.62, '#ffd9a6')])
    s.glow(0.6, 0.62, 560, '#ffc88a', 0.35, 1.4)
    s.lit_clouds(0.08, 0.42, '#7a7aa0', '#ffc9a0', 0.5, alpha=0.5, scale=4, coverage=0.57)
    s.ridge(0.62, 0.04, '#6d6585', '#6d6585', rough=4, haze='#efb894', haze_alpha=0.35)
    top = s.hills(0.7, [(0.03, 0.55, 2.2), (0.006, 2.1, 0.5)], '#2d2c40', '#1a1a27')
    im, dr = s.layer()
    cx = int(0.44 * W)
    draw_church(dr, cx, top[cx] + 10, 330, col_of('#151520'), window=col_of('#ffcf7e'))
    draw_round_tree(dr, 0.74 * W, top[int(0.74 * W)] + 14, 220, col_of('#141420'), s.rng)
    s.composite(im, 0.9)
    s.vignette(0.3)
    return s


def flower_meadow(seed):
    """Psalm 118:24 - a meadow of flowers on a bright new day. layout: center"""
    s = Scene(seed)
    s.sky([(0, '#5e9ad6'), (0.25, '#a8cdeb'), (0.4, '#eef3ec')])
    s.sun(0.72, 0.12, 36, halo='#fff4d0', strength=0.9)
    s.clouds(0.04, 0.3, '#ffffff', 0.7, scale=5, coverage=0.52)
    s.ridge(0.66, 0.03, '#9cc0b8', '#a6c4b6', rough=4, haze='#f0f4ea', haze_alpha=0.5)
    top = s.hills(0.7, [(0.01, 1.0, 0.4), (0.005, 2.4, 2.0)], '#a3cc6a', '#5c9a3e', light=(0.72, '#fff4c0', 0.18))
    s.grass(top, 3500, ['#5b9a3a', '#74b04b', '#46802c', '#8cc25e'], height=(30, 140))
    s.flowers(top, 2400, ['#ffffff', '#ffe26a', '#ffb3c6', '#e889a8', '#c9a8ff', '#ffd08a'], size=(3, 10))
    s.vignette(0.2)
    return s


def first_love(seed):
    """1 John 4:19 - warm light spilling across a lake at golden hour. layout: top"""
    s = Scene(seed)
    s.sky([(0, '#4a5a8c'), (0.3, '#c38da0'), (0.52, '#ffbe8e'), (0.58, '#ffd6a2')])
    s.sun(0.5, 0.575, 42, halo='#ffbd80', strength=1.1)
    s.lit_clouds(0.08, 0.42, '#9a7ca0', '#ffc8a0', 0.5, alpha=0.5, scale=4, coverage=0.57)
    s.ridge(0.59, 0.04, '#7d6a88', '#7d6a88', rough=4, haze='#ffb48a', haze_alpha=0.3)
    s.water(0.6, tint='#4a4a72', darken=0.85, ripple=2.0, glitter_x=0.5, glitter_color='#ffd0a0')
    im, dr = s.layer()
    dr.polygon([(0, 0.84 * H), (0.22 * W, 0.86 * H), (0.4 * W, 0.92 * H), (0.45 * W, H), (0, H)], fill=col_of('#211a26'))
    draw_round_tree(dr, 0.1 * W, 0.86 * H, 480, col_of('#1c1620'), s.rng)
    s.composite(im, 1.2)
    s.vignette(0.3)
    return s


def moon_rest(seed):
    """Psalm 4:8 - moonlight over a still lake at night. layout: bottom"""
    s = Scene(seed)
    s.sky([(0, '#060b1e'), (0.35, '#14204a'), (0.5, '#2a3a6a')])
    s.stars(700, y_max=0.5)
    s.glow(0.62, 0.22, 380, '#cfd8ff', 0.25, 1.4)
    s.sun(0.62, 0.22, 46, color='#f2f2ea', halo='#c8d4ff', strength=0.5)
    s.ridge(0.5, 0.06, '#1d2850', '#1d2850', rough=4)
    top = s.ridge(0.515, 0.01, '#121a36', '#121a36', rough=8)
    s.pines(top, 150, '#0b1128', height=(20, 60), y_jitter=6)
    s.water(0.52, tint='#0e1734', darken=0.8, ripple=2.0, glitter_x=0.62, glitter_color='#dfe6ff')
    s.vignette(0.3)
    return s


def still_waters(seed):
    """Psalm 23:2 - green pastures beside still waters, sheep resting. layout: top"""
    s = Scene(seed)
    s.sky([(0, '#7fa8cf'), (0.25, '#c9dbe6'), (0.48, '#f6ead0')])
    s.sun(0.3, 0.42, 30, halo='#fff0c8', strength=0.7)
    s.clouds(0.03, 0.3, '#ffffff', 0.5, scale=5, coverage=0.56)
    s.ridge(0.5, 0.06, '#8aa3b4', '#9db0b8', rough=4, haze='#f2e6d0', haze_alpha=0.45)
    s.hills(0.54, [(0.01, 1.0, 0.2)], '#8fb069', '#5f8a45', light=(0.3, '#fff0b8', 0.15))
    s.water(0.56, tint='#56748e', darken=0.86, ripple=1.5)
    top = s.hills(0.68, [(0.03, 0.6, 0.3), (0.008, 2.0, 1.0)], '#9cc06a', '#4f7d35', light=(0.3, '#ffefb0', 0.15))
    im, dr = s.layer()
    flock(s, dr, [(0.32, 0.7, 1.0, 1), (0.42, 0.71, 1.1, -1), (0.55, 0.705, 0.95, 1), (0.63, 0.72, 1.2, -1), (0.48, 0.73, 1.25, 1)], 90)
    draw_round_tree(dr, 0.82 * W, 0.7 * H, 420, col_of('#3b5a2c'), s.rng)
    s.composite(im, 1.0)
    s.grass(np.full(W, 0.78 * H), 2400, ['#3a6527', '#4f7f33', '#2c4f1e', '#6a9442'], height=(40, 150))
    s.vignette(0.22)
    return s


def praying_dawn(seed):
    """Psalm 5:3 - a person kneeling in prayer on a hill at first light. layout: top"""
    s = Scene(seed)
    s.sky([(0, '#2c3e6c'), (0.35, '#9a97bb'), (0.58, '#f8c79a'), (0.64, '#ffe0b0')])
    s.sun(0.5, 0.64, 40, halo='#ffd09a', strength=0.9)
    s.rays(0.5, 0.64, '#ffe8c0', 0.12, n=12)
    s.lit_clouds(0.1, 0.45, '#8c8aac', '#ffd4ac', 0.55, alpha=0.5, scale=4, coverage=0.57)
    s.ridge(0.65, 0.04, '#7a7290', '#7a7290', rough=4, haze='#f8c49c', haze_alpha=0.35)
    top = s.hills(0.72, [(0.02, 0.5, 1.4)], '#2a2a3c', '#191926')
    im, dr = s.layer()
    x, y, h = 0.52 * W, top[int(0.52 * W)] + 6, 210
    c = col_of('#121220')
    # kneeling in profile facing right, head slightly bowed, hands folded
    dr.ellipse([x - h * 0.02, y - h * 0.95, x + h * 0.13, y - h * 0.8], fill=c)
    dr.polygon([(x - h * 0.09, y - h * 0.78), (x + h * 0.07, y - h * 0.8), (x + h * 0.1, y - h * 0.42), (x - h * 0.13, y - h * 0.4)], fill=c)
    dr.polygon([(x - h * 0.13, y - h * 0.44), (x + h * 0.1, y - h * 0.44), (x + h * 0.09, y), (x - h * 0.11, y)], fill=c)
    dr.polygon([(x - h * 0.11, y - h * 0.09), (x - h * 0.4, y - h * 0.05), (x - h * 0.42, y), (x - h * 0.11, y)], fill=c)
    dr.polygon([(x + h * 0.02, y - h * 0.74), (x + h * 0.08, y - h * 0.77), (x + h * 0.2, y - h * 0.62), (x + h * 0.15, y - h * 0.57)], fill=c)
    dr.polygon([(x + h * 0.14, y - h * 0.6), (x + h * 0.2, y - h * 0.61), (x + h * 0.22, y - h * 0.77), (x + h * 0.17, y - h * 0.78)], fill=c)
    s.composite(im, 0.8)
    s.vignette(0.3)
    return s


SCENES = {
    'wallpaper_001': (shepherd_pasture, 101),
    'wallpaper_002': (still_lake, 102),
    'wallpaper_003': (strong_sunrise_figure, 103),
    'wallpaper_004': (summit_forward, 104),
    'wallpaper_005': (rest_field, 105),
    'wallpaper_006': (cross_sunset, 106),
    'wallpaper_007': (starry_dawn, 107),
    'wallpaper_008': (forest_path, 108),
    'wallpaper_009': (mountain_valley, 109),
    'wallpaper_010': (wheat_gratitude, 110),
    'wallpaper_011': (worship_sky, 111),
    'wallpaper_012': (dove_waters, 112),
    'wallpaper_013': (ocean_sunrise, 113),
    'wallpaper_014': (family_home, 114),
    'wallpaper_015': (two_walk, 115),
    'wallpaper_016': (lamp_word, 116),
    'wallpaper_017': (cross_mountain, 117),
    'wallpaper_018': (heavens_declare, 118),
    'wallpaper_019': (good_shepherd, 119),
    'wallpaper_020': (misty_faith, 120),
    'wallpaper_021': (new_morning, 121),
    'wallpaper_022': (courage_peak, 122),
    'wallpaper_023': (eagles_wings, 123),
    'wallpaper_024': (chapel_dawn, 124),
    'wallpaper_025': (flower_meadow, 125),
    'wallpaper_026': (first_love, 126),
    'wallpaper_027': (moon_rest, 127),
    'wallpaper_028': (still_waters, 128),
    'wallpaper_029': (praying_dawn, 129),
}
