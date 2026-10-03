"""Bible scenes for entries 030-071, in the same painted silhouette style as scenes.py.

Jesus never appears as more than a distant figure or silhouette.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

from scene import (Scene, W, H, rgb, col_of, smoothstep, bezier, draw_person, draw_sheep, draw_cross, draw_bird,
                   draw_dove, draw_church, draw_house, draw_open_book, draw_round_tree, draw_pine)
from scenes import flock


# ---------- extra drawing helpers ----------

def rainbow(s, cx, cy, r, width, alpha=0.32):
    d = np.sqrt((s.xx - cx * W) ** 2 + (s.yy - cy * H) ** 2)
    t = (d - (r - width / 2)) / width
    band = np.clip(1 - np.abs(t * 2 - 1), 0, 1) ** 0.7
    cols = np.array([rgb(c) for c in ('#7a5cff', '#3d8bff', '#3ec46d', '#ffe14d', '#ff9a3d', '#ff4d4d')])
    tt = np.clip(t, 0, 0.999) * (len(cols) - 1)
    i = tt.astype(int)
    f = (tt - i)[..., None]
    col = cols[i] * (1 - f) + cols[np.minimum(i + 1, len(cols) - 1)] * f
    fade = smoothstep(0, H * 0.06, cy * H - s.yy)
    s.img = s.img * (1 - (band * fade * alpha)[..., None]) + col * (band * fade * alpha)[..., None]


def draw_ark(dr, x, y, w, col, window=None):
    dr.polygon([(x - w / 2, y - w * 0.2), (x + w / 2, y - w * 0.2), (x + w * 0.42, y), (x - w * 0.42, y)], fill=col)
    dr.rectangle([x - w * 0.34, y - w * 0.32, x + w * 0.34, y - w * 0.19], fill=col)
    dr.polygon([(x - w * 0.38, y - w * 0.32), (x + w * 0.38, y - w * 0.32), (x + w * 0.3, y - w * 0.4), (x - w * 0.3, y - w * 0.4)], fill=col)
    if window:
        for i in range(6):
            wx = x - w * 0.28 + i * w * 0.1
            dr.rectangle([wx, y - w * 0.29, wx + w * 0.04, y - w * 0.25], fill=window)


def flame(s, cx, cy, h, inner='#fff2b0', outer='#ff7a2a', glow=True):
    cx, cy = cx * W, cy * H
    im, dr = s.layer()
    for k, (c, sc) in enumerate(((outer, 1.0), ('#ffb340', 0.72), (inner, 0.42))):
        hh = h * sc
        ww = hh * 0.42
        pts = bezier((cx, cy - hh), (cx + ww * 1.1, cy - hh * 0.45), (cx + ww, cy - hh * 0.05), (cx, cy)) + \
            bezier((cx, cy), (cx - ww, cy - hh * 0.05), (cx - ww * 1.1, cy - hh * 0.45), (cx, cy - hh))
        dr.polygon(pts, fill=col_of(c, 235))
    s.composite(im, 2.5)
    if glow:
        s.glow(cx / W, (cy - h * 0.4) / H, h * 2.4, '#ffb05a', 0.35, 1.4)


def draw_bush(dr, x, y, w, col, rng):
    for _ in range(26):
        cx = x + rng.uniform(-0.45, 0.45) * w
        cy = y - rng.uniform(0.05, 0.5) * w * (1 - abs(cx - x) / w)
        r = w * rng.uniform(0.08, 0.16)
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)


def draw_tablets(dr, x, y, s, col, line):
    for dx in (-0.52, 0.52):
        cx = x + dx * s
        dr.rectangle([cx - s * 0.45, y - s * 1.0, cx + s * 0.45, y], fill=col)
        dr.ellipse([cx - s * 0.45, y - s * 1.45, cx + s * 0.45, y - s * 0.55], fill=col)
        for i in range(5):
            ly = y - s * 0.9 + i * s * 0.17
            dr.line([cx - s * 0.3, ly, cx + s * 0.3, ly], fill=line, width=max(2, int(s * 0.04)))


def draw_harp(dr, x, y, h, col, width=4):
    dr.line(bezier((x, y), (x - h * 0.05, y - h * 0.5), (x + h * 0.1, y - h * 0.9), (x + h * 0.05, y - h)), fill=col, width=width + 2)
    dr.line(bezier((x + h * 0.05, y - h), (x + h * 0.35, y - h * 0.95), (x + h * 0.45, y - h * 0.6), (x + h * 0.55, y - h * 0.55)), fill=col, width=width + 2)
    dr.line([x, y, x + h * 0.55, y - h * 0.55], fill=col, width=width + 2)
    for i in range(1, 7):
        t = i / 7
        dr.line([x + t * h * 0.08, y - t * h * 0.95, x + t * h * 0.55, y - t * h * 0.55], fill=col, width=max(1, width // 2))


def draw_star(s, cx, cy, size, color='#fff8e0', glow_color='#cfd8ff'):
    s.glow(cx, cy, size * 2.2, glow_color, 0.5, 1.3)
    s.glow(cx, cy, size * 0.7, '#ffffff', 0.7, 1.6)
    x, y = cx * W, cy * H
    dx, dy = s.xx - x, s.yy - y
    for ang, ln in ((0, 1.0), (math.pi / 2, 1.5), (math.pi / 4, 0.45), (-math.pi / 4, 0.45)):
        c, si = math.cos(ang), math.sin(ang)
        along = dx * c + dy * si
        across = -dx * si + dy * c
        m = np.exp(-(across / 3.0) ** 2) * np.exp(-np.abs(along) / (size * ln))
        s.add(rgb(color) * (0.9 * m)[..., None])


def draw_camel(dr, x, y, h, col, rider=True):
    # body and hump
    dr.ellipse([x - h * 0.45, y - h * 0.85, x + h * 0.35, y - h * 0.5], fill=col)
    dr.ellipse([x - h * 0.25, y - h * 1.02, x + h * 0.12, y - h * 0.65], fill=col)
    # legs
    for lx in (-0.35, -0.25, 0.18, 0.28):
        dr.polygon([(x + lx * h, y - h * 0.6), (x + (lx + 0.06) * h, y - h * 0.6), (x + (lx + 0.04) * h, y), (x + (lx + 0.01) * h, y)], fill=col)
    # neck and head
    dr.polygon([(x + h * 0.25, y - h * 0.75), (x + h * 0.35, y - h * 0.68), (x + h * 0.55, y - h * 1.05), (x + h * 0.47, y - h * 1.1)], fill=col)
    dr.ellipse([x + h * 0.44, y - h * 1.16, x + h * 0.68, y - h * 1.04], fill=col)
    if rider:
        dr.ellipse([x - h * 0.12, y - h * 1.38, x + h * 0.02, y - h * 1.24], fill=col)
        dr.polygon([(x - h * 0.16, y - h * 1.25), (x + h * 0.06, y - h * 1.25), (x + h * 0.1, y - h * 0.95), (x - h * 0.2, y - h * 0.95)], fill=col)


def draw_boat(dr, x, y, w, col, sail=True, people=0):
    hull = [(x - w / 2, y - w * 0.12), (x + w / 2, y - w * 0.14), (x + w * 0.38, y), (x - w * 0.36, y)]
    dr.polygon(hull, fill=col)
    if sail:
        dr.line([x, y - w * 0.12, x, y - w * 0.95], fill=col, width=max(3, int(w * 0.02)))
        dr.polygon([(x + w * 0.02, y - w * 0.9), (x + w * 0.38, y - w * 0.2), (x + w * 0.02, y - w * 0.2)], fill=col)
    for i in range(people):
        px = x - w * 0.3 + i * w * 0.12
        draw_person(dr, px, y - w * 0.11, w * 0.22, col, robe=True)


def draw_olive_tree(dr, x, y, h, col, rng):
    trunk = bezier((x, y), (x - h * 0.12, y - h * 0.25), (x + h * 0.1, y - h * 0.4), (x - h * 0.02, y - h * 0.55), 20)
    for i in range(len(trunk) - 1):
        wdt = int(h * (0.09 - 0.05 * i / len(trunk)))
        dr.line([trunk[i], trunk[i + 1]], fill=col, width=max(3, wdt))
    for _ in range(40):
        cx = x + rng.uniform(-0.5, 0.5) * h
        cy = y - h * 0.65 + rng.uniform(-0.18, 0.15) * h
        r = h * rng.uniform(0.05, 0.11)
        dr.ellipse([cx - r * 1.6, cy - r, cx + r * 1.6, cy + r], fill=col)


def draw_basket(dr, x, y, w, basket, bread, fish):
    dr.ellipse([x - w * 0.5, y - w * 0.18, x + w * 0.5, y + w * 0.05], fill=basket)
    dr.polygon([(x - w * 0.5, y - w * 0.07), (x + w * 0.5, y - w * 0.07), (x + w * 0.38, y + w * 0.3), (x - w * 0.38, y + w * 0.3)], fill=basket)
    for i, dx in enumerate((-0.25, 0.0, 0.24)):
        dr.ellipse([x + (dx - 0.16) * w, y - w * 0.28, x + (dx + 0.16) * w, y - w * 0.04], fill=bread)
    for fy, flip in ((-0.32, 1), (-0.22, -1)):
        fx = x + 0.05 * w * flip
        body = bezier((fx - w * 0.28, y + fy * w), (fx - w * 0.1, y + (fy - 0.07) * w), (fx + w * 0.12, y + (fy - 0.07) * w), (fx + w * 0.22, y + fy * w)) + \
            bezier((fx + w * 0.22, y + fy * w), (fx + w * 0.12, y + (fy + 0.07) * w), (fx - w * 0.1, y + (fy + 0.07) * w), (fx - w * 0.28, y + fy * w))
        dr.polygon(body, fill=fish)
        dr.polygon([(fx + w * 0.2, y + fy * w), (fx + w * 0.32, y + (fy - 0.06) * w), (fx + w * 0.32, y + (fy + 0.06) * w)], fill=fish)


def draw_tomb(dr, x, y, h, rock, dark, stone):
    dr.ellipse([x - h * 1.2, y - h * 1.2, x + h * 1.4, y + h * 0.4], fill=rock)
    dr.rectangle([x - h * 1.6, y - h * 0.1, x + h * 1.8, y + h * 0.6], fill=rock)
    dr.ellipse([x - h * 0.32, y - h * 0.7, x + h * 0.32, y + h * 0.1], fill=dark)
    dr.rectangle([x - h * 0.32, y - h * 0.3, x + h * 0.32, y + h * 0.02], fill=dark)
    dr.ellipse([x + h * 0.45, y - h * 0.6, x + h * 1.1, y + h * 0.05], fill=stone)


def draw_chalice(dr, x, y, h, col):
    dr.polygon(bezier((x - h * 0.28, y - h), (x - h * 0.28, y - h * 0.62), (x - h * 0.1, y - h * 0.5), (x, y - h * 0.5)) +
               bezier((x, y - h * 0.5), (x + h * 0.1, y - h * 0.5), (x + h * 0.28, y - h * 0.62), (x + h * 0.28, y - h)), fill=col)
    dr.rectangle([x - h * 0.035, y - h * 0.52, x + h * 0.035, y - h * 0.12], fill=col)
    dr.ellipse([x - h * 0.2, y - h * 0.16, x + h * 0.2, y + h * 0.02], fill=col)


def draw_loaf(dr, x, y, w, col, score):
    dr.ellipse([x - w / 2, y - w * 0.42, x + w / 2, y + w * 0.05], fill=col)
    for i in range(3):
        sx = x - w * 0.22 + i * w * 0.2
        dr.line([sx, y - w * 0.3, sx + w * 0.08, y - w * 0.12], fill=score, width=max(2, int(w * 0.025)))


def draw_oil_lamp(dr, x, y, w, col):
    dr.polygon(bezier((x - w / 2, y - w * 0.1), (x - w * 0.3, y + w * 0.12), (x + w * 0.3, y + w * 0.12), (x + w * 0.6, y - w * 0.2)) +
               [(x + w * 0.6, y - w * 0.24), (x - w * 0.1, y - w * 0.2)], fill=col)
    dr.rectangle([x - w * 0.12, y + w * 0.05, x + w * 0.12, y + w * 0.6], fill=col)
    dr.rectangle([x - w * 0.3, y + w * 0.6, x + w * 0.3, y + w * 0.68], fill=col)


def draw_lily(dr, x, y, h, stem, petal):
    dr.line([x, y, x + h * 0.05, y - h], fill=stem, width=max(2, int(h * 0.03)))
    dr.polygon([(x, y - h * 0.4), (x - h * 0.25, y - h * 0.65), (x - h * 0.02, y - h * 0.55)], fill=stem)
    tx, ty = x + h * 0.05, y - h
    for ang in (-60, -20, 20, 60, 0):
        a = math.radians(ang - 90)
        ex, ey = tx + math.cos(a) * h * 0.22, ty + math.sin(a) * h * 0.22 - h * 0.05
        dr.polygon([(tx - h * 0.04, ty), (ex, ey), (tx + h * 0.04, ty)], fill=petal)
    dr.ellipse([tx - h * 0.06, ty - h * 0.06, tx + h * 0.06, ty + h * 0.03], fill=petal)


def draw_lighthouse(dr, x, y, h, col, lamp):
    dr.polygon([(x - h * 0.12, y), (x + h * 0.12, y), (x + h * 0.07, y - h * 0.82), (x - h * 0.07, y - h * 0.82)], fill=col)
    dr.rectangle([x - h * 0.1, y - h * 0.86, x + h * 0.1, y - h * 0.82], fill=col)
    dr.rectangle([x - h * 0.06, y - h * 0.97, x + h * 0.06, y - h * 0.86], fill=lamp)
    dr.polygon([(x - h * 0.09, y - h * 0.97), (x + h * 0.09, y - h * 0.97), (x, y - h * 1.06)], fill=col)


def draw_wall_gate(dr, x, y, h, wall, open_col):
    dr.rectangle([0, y - h * 0.55, W, y + h * 0.1], fill=wall)
    dr.rectangle([x - h * 0.35, y - h * 0.95, x + h * 0.35, y + h * 0.1], fill=wall)
    dr.ellipse([x - h * 0.22, y - h * 0.82, x + h * 0.22, y - h * 0.38], fill=open_col)
    dr.rectangle([x - h * 0.22, y - h * 0.6, x + h * 0.22, y + h * 0.1], fill=open_col)


def draw_city(dr, base_y, x0, x1, col, rng, window=None):
    x = x0
    while x < x1:
        w = rng.uniform(40, 110)
        h = rng.uniform(60, 190)
        dr.rectangle([x, base_y - h, x + w, base_y], fill=col)
        if rng.uniform() < 0.25:
            dr.ellipse([x + w * 0.1, base_y - h - w * 0.4, x + w * 0.9, base_y - h + w * 0.4], fill=col)
        if rng.uniform() < 0.2:
            dr.rectangle([x + w * 0.4, base_y - h - 90, x + w * 0.6, base_y - h], fill=col)
        if window and rng.uniform() < 0.5:
            wx = x + w * 0.4
            dr.rectangle([wx, base_y - h * 0.6, wx + 10, base_y - h * 0.6 + 14], fill=window)
        x += w * rng.uniform(0.7, 1.0)


def sky_dusk(s, warm='#ffb27a'):
    s.sky([(0, '#26304f'), (0.3, '#6b6a92'), (0.55, warm), (0.62, '#ffd7a0')])


def ground_silhouette(s, base, waves, c1='#1d1b28', c2='#121119'):
    return s.hills(base, waves, c1, c2)


# ---------- scenes ----------

def noah_rainbow(seed):
    s = Scene(seed)
    s.sky([(0, '#5e7fae'), (0.3, '#b6c7d8'), (0.5, '#f1e4cf')])
    s.clouds(0.02, 0.18, '#e8edf3', 0.55, scale=5, coverage=0.55)
    rainbow(s, 0.5, 0.52, 620, 120, 0.38)
    s.ridge(0.5, 0.1, '#7b8aa0', '#8a96a6', rough=4, peak=(0.5, 1.0, 0.16), haze='#efe4d4', haze_alpha=0.4)
    top = s.ridge(0.54, 0.05, '#3f4a5a', '#333d4b', rough=5, peak=(0.5, 1.2, 0.1))
    im, dr = s.layer()
    draw_ark(dr, 0.5 * W, top[int(0.5 * W)] + 14, 420, col_of('#2a2622'), col_of('#ffd27a'))
    s.composite(im, 0.9)
    s.water(0.56, tint='#4c607a', darken=0.85, ripple=1.5)
    s.vignette(0.25)
    return s


def burning_bush(seed):
    s = Scene(seed)
    s.sky([(0, '#2a2f55'), (0.35, '#8a6c86'), (0.6, '#f0a46e'), (0.66, '#f7c48e')])
    s.ridge(0.6, 0.12, '#6a4f5f', '#5a4452', rough=4, peak=(0.7, 1.2, 0.14), haze='#e8a17a', haze_alpha=0.3)
    top = s.hills(0.72, [(0.02, 0.6, 0.4)], '#3a2b2a', '#1f1716')
    im, dr = s.layer()
    bx = 0.5 * W
    draw_bush(dr, bx, top[int(bx)] + 20, 400, col_of('#24180f'), s.rng)
    draw_person(dr, 0.3 * W, top[int(0.3 * W)] + 30, 190, col_of('#181110'), robe=True, staff=True, hair=True)
    s.composite(im, 0.9)
    flame(s, 0.5, (top[int(bx)] - 50) / H, 170)
    s.vignette(0.3)
    return s


def red_sea(seed):
    s = Scene(seed)
    s.sky([(0, '#33496e'), (0.3, '#8fa3bd'), (0.5, '#f3dcc0')])
    s.glow(0.5, 0.5, 500, '#fff1d6', 0.4, 1.4)
    s.rays(0.5, 0.5, '#fff4dc', 0.16, n=10)
    im, dr = s.layer()
    # walls of water on either side of a path
    for side in (-1, 1):
        pts = [(0.5 * W + side * 30, 0.52 * H)]
        for i in range(40):
            t = i / 39
            x = 0.5 * W + side * (30 + t * 0.62 * W)
            y = 0.52 * H - (80 + 380 * t ** 0.8) + 30 * math.sin(t * 13)
            pts.append((x, y))
        pts += [(0.5 * W + side * W, H), (0.5 * W + side * (60), H)]
        dr.polygon(pts, fill=col_of('#2f5f80'))
    s.composite(im, 1.5)
    n = s.noise2d(6, 4, 0.6, aspect=0.4)
    side_mask = (np.abs(s.xx - 0.5 * W) > 60 + (s.yy - 0.52 * H).clip(0) * 0.6) & (s.yy > 0.3 * H)
    s.img = s.img * (1 + 0.25 * (n[..., None] - 0.5) * side_mask[..., None])
    im, dr = s.layer()
    dr.polygon([(0.48 * W, 0.52 * H), (0.52 * W, 0.52 * H), (0.62 * W, H), (0.38 * W, H)], fill=col_of('#c9b28c'))
    s.composite(im, 2)
    im, dr = s.layer()
    for i, (x, y, h) in enumerate([(0.5, 0.66, 70), (0.47, 0.7, 80), (0.53, 0.71, 82), (0.5, 0.76, 95)]):
        draw_person(dr, x * W, y * H, h, col_of('#3b2f26'), robe=True)
    s.composite(im, 0.8)
    s.vignette(0.3)
    return s


def sinai(seed):
    s = Scene(seed)
    s.sky([(0, '#1f2a4a'), (0.3, '#59618a'), (0.45, '#d9a785')])
    s.lit_clouds(0.05, 0.25, '#5c5a7e', '#ffdcae', 0.22, alpha=0.6, scale=4, coverage=0.55)
    s.glow(0.5, 0.2, 520, '#fff0cc', 0.5, 1.3)
    s.rays(0.5, 0.2, '#fff4d8', 0.2, n=13)
    top = s.ridge(0.5, 0.2, '#5a4a52', '#3b3038', rough=4, peak=(0.5, 1.3, 0.15))
    s.ridge(0.6, 0.05, '#2c2329', '#1d171c', rough=5)
    im, dr = s.layer()
    draw_tablets(dr, 0.5 * W, top[int(0.5 * W)] + 8, 46, col_of('#f2e2c0'), col_of('#9a7d5a'))
    s.composite(im, 0.8)
    s.vignette(0.3)
    return s


def jacobs_ladder(seed):
    s = Scene(seed)
    s.sky([(0, '#0b1230'), (0.4, '#1f2d55'), (0.6, '#3a4570')])
    s.stars(800, y_max=0.6)
    # stairway of light
    x = (s.xx / W - 0.5)
    y = s.yy / H
    width = 0.02 + (0.62 - y).clip(0) * 0.25
    beam = np.exp(-(x / width) ** 2) * (y < 0.6) * smoothstep(0.0, 0.25, y)
    steps = 0.75 + 0.25 * (np.sin(y * 260) > 0.6)
    s.add(rgb('#fff2cf') * (0.75 * beam * steps)[..., None])
    s.glow(0.5, 0.05, 400, '#fff4d8', 0.4, 1.4)
    top = s.hills(0.62, [(0.015, 0.8, 0.4)], '#1d2236', '#121522')
    im, dr = s.layer()
    # sleeper with a stone pillow
    sx, sy = 0.5 * W, top[int(0.5 * W)] + 26
    dr.ellipse([sx - 150, sy - 40, sx + 130, sy + 6], fill=col_of('#0c0e18'))
    dr.ellipse([sx + 110, sy - 50, sx + 175, sy + 2], fill=col_of('#0c0e18'))
    dr.ellipse([sx + 160, sy - 30, sx + 230, sy + 10], fill=col_of('#2a2c36'))
    s.composite(im, 1)
    s.glow(0.5, 0.6, 220, '#ffe6b0', 0.2, 1.5)
    s.vignette(0.3)
    return s


def david_harp(seed):
    s = Scene(seed)
    s.sky([(0, '#4f6c9c'), (0.3, '#c2a6a6'), (0.52, '#ffcf96'), (0.6, '#ffe2b0')])
    s.sun(0.72, 0.56, 40, halo='#ffcf8a', strength=1.0)
    s.lit_clouds(0.08, 0.4, '#8e8cac', '#ffd7aa', 0.5, alpha=0.5, scale=4, coverage=0.56)
    s.ridge(0.6, 0.04, '#8a7a88', '#8a7a88', rough=4, haze='#ffc796', haze_alpha=0.4)
    top = s.hills(0.68, [(0.02, 0.7, 0.4)], '#4f5a3c', '#2a3020')
    im, dr = s.layer()
    px = 0.42 * W
    py = top[int(px)] + 14
    draw_person(dr, px, py, 200, col_of('#1b1a14'), robe=True, hair=True)
    draw_harp(dr, px + 30, py - 70, 120, col_of('#1b1a14'), 5)
    flock(s, dr, [(0.6, 0.72, 1.0, -1), (0.68, 0.73, 1.05, -1), (0.75, 0.725, 0.9, 1), (0.57, 0.75, 1.15, -1)], 70, body='#e8d6b8', head='#1b1a14')
    s.composite(im, 0.9)
    s.grass(np.full(W, 0.8 * H), 1800, ['#2a3820', '#3a4a2a', '#1f2a18'], height=(40, 140))
    s.vignette(0.28)
    return s


def elijah_whisper(seed):
    s = Scene(seed)
    s.sky([(0, '#2f3a5c'), (0.35, '#7d86a6'), (0.55, '#d8c8c2')])
    s.mist(0.45, 0.06, '#e8e2dc', 0.4)
    top = s.ridge(0.62, 0.3, '#4a4a58', '#2c2c36', rough=4, peak=(0.4, 1.2, 0.2))
    im, dr = s.layer()
    cx, cy = 0.56 * W, 0.7 * H
    dr.ellipse([cx - 120, cy - 220, cx + 120, cy + 40], fill=col_of('#14131b'))
    s.composite(im, 3)
    s.glow(0.56, 0.68, 200, '#ffe6b8', 0.25, 1.5)
    im, dr = s.layer()
    draw_person(dr, cx, cy + 20, 170, col_of('#0d0c12'), robe=True, hair=True)
    s.composite(im, 0.8)
    s.mist(0.78, 0.04, '#cfc8c6', 0.3)
    s.hills(0.9, [(0.01, 1.0, 0.0)], '#1c1b24', '#121118')
    s.vignette(0.3)
    return s


def jerusalem(seed):
    s = Scene(seed)
    s.sky([(0, '#3a4c7a'), (0.3, '#b48e9a'), (0.52, '#ffbe86'), (0.58, '#ffd8a0')])
    s.sun(0.32, 0.55, 40, halo='#ffbe7a', strength=1.0)
    s.lit_clouds(0.08, 0.4, '#8a6e8e', '#ffc39a', 0.5, alpha=0.5, scale=4, coverage=0.57)
    s.ridge(0.6, 0.1, '#7e6a7e', '#7e6a7e', rough=4, peak=(0.15, 1.0, 0.12), haze='#ffb07a', haze_alpha=0.3)
    s.ridge(0.62, 0.1, '#6a5a6e', '#6a5a6e', rough=4, peak=(0.88, 1.0, 0.12), haze='#f2a07a', haze_alpha=0.25)
    top = s.hills(0.7, [(0.01, 1.0, 0.2)], '#3a2e3a', '#241c24')
    im, dr = s.layer()
    base = 0.7 * H
    dr.rectangle([0.18 * W, base - 70, 0.82 * W, base + 30], fill=col_of('#2b2230'))
    for i in range(9):
        tx = 0.18 * W + i * 0.08 * W
        dr.rectangle([tx, base - 120, tx + 50, base], fill=col_of('#2b2230'))
    draw_city(dr, base - 60, 0.25 * W, 0.75 * W, col_of('#2b2230'), s.rng, col_of('#ffcc78'))
    dr.ellipse([0.45 * W, base - 300, 0.55 * W, base - 210], fill=col_of('#2b2230'))
    dr.rectangle([0.44 * W, base - 260, 0.56 * W, base - 60], fill=col_of('#2b2230'))
    s.composite(im, 0.9)
    s.vignette(0.3)
    return s


def bethlehem_star(seed):
    s = Scene(seed)
    s.sky([(0, '#060a1e'), (0.5, '#16224a'), (0.75, '#2c3666')])
    s.stars(900, y_max=0.75)
    draw_star(s, 0.5, 0.18, 120)
    s.rays(0.5, 0.18, '#dfe4ff', 0.12, n=8, length=2400)
    top = s.hills(0.8, [(0.02, 0.7, 0.5), (0.008, 2.2, 0.2)], '#14182c', '#0b0d18')
    im, dr = s.layer()
    draw_city(dr, 0.795 * H, 0.3 * W, 0.7 * W, col_of('#0f1222'), s.rng, col_of('#ffcf7a'))
    s.composite(im, 0.9)
    s.vignette(0.3)
    return s


def shepherds_night(seed):
    s = Scene(seed)
    s.sky([(0, '#0a1028'), (0.5, '#1b2650'), (0.7, '#2f3a68')])
    s.stars(700, y_max=0.7)
    s.glow(0.5, 0.18, 620, '#fff2d0', 0.55, 1.3)
    s.rays(0.5, 0.18, '#fff6e0', 0.22, n=14, length=2000)
    top = s.hills(0.72, [(0.03, 0.6, 0.2), (0.01, 2.0, 1.0)], '#1c2234', '#0e1120')
    im, dr = s.layer()
    for x, h, st in ((0.36, 180, True), (0.44, 160, False), (0.62, 175, True)):
        draw_person(dr, x * W, top[int(x * W)] + 16, h, col_of('#090b14'), robe=True, staff=st)
    flock(s, dr, [(0.5, 0.75, 1.0, 1), (0.56, 0.76, 1.1, -1), (0.3, 0.77, 1.15, 1), (0.7, 0.765, 0.95, -1)], 70, body='#b9b6c8', head='#090b14')
    s.composite(im, 0.9)
    s.vignette(0.3)
    return s


def wise_men(seed):
    s = Scene(seed)
    s.sky([(0, '#0a0f2a'), (0.5, '#2a2f5c'), (0.72, '#7a5e78'), (0.78, '#c2867a')])
    s.stars(600, y_max=0.6)
    draw_star(s, 0.68, 0.16, 100)
    top = s.hills(0.76, [(0.025, 0.5, 0.3), (0.012, 1.3, 1.0)], '#2c2232', '#160f1a')
    im, dr = s.layer()
    for x, h in ((0.36, 180), (0.5, 200), (0.64, 175)):
        draw_camel(dr, x * W, top[int(x * W)] + 10, h, col_of('#0f0a12'))
    s.composite(im, 0.9)
    s.vignette(0.3)
    return s


def jordan_dove(seed):
    s = Scene(seed)
    s.sky([(0, '#3e5f92'), (0.3, '#86a2c4'), (0.5, '#f4e8d4')])
    s.glow(0.5, 0.06, 420, '#fff8e6', 0.3, 1.3)
    s.rays(0.5, 0.02, '#ffffff', 0.16, n=9, length=2600)
    s.ridge(0.5, 0.05, '#8aa0b4', '#9aacba', rough=4, haze='#efe6d6', haze_alpha=0.45)
    s.hills(0.53, [(0.01, 1.0, 0.2)], '#7a9a62', '#56784a')
    s.water(0.55, tint='#4f7088', darken=0.85, ripple=1.5)
    im, dr = s.layer()
    draw_dove(dr, 0.5 * W + 6, 0.25 * H + 8, 170, col_of('#2a3a5a', 70))
    draw_dove(dr, 0.5 * W, 0.25 * H, 170, col_of('#ffffff'))
    draw_person(dr, 0.5 * W, 0.6 * H, 120, col_of('#2a3038'), robe=True, hair=True)
    dr.polygon([(0, 0.53 * H), (0.2 * W, 0.535 * H), (0.12 * W, 0.6 * H), (0, 0.62 * H)], fill=col_of('#4e6c3e'))
    s.composite(im, 1)
    s.vignette(0.25)
    return s


def galilee_boat(seed):
    s = Scene(seed)
    s.sky([(0, '#5a7aa8'), (0.3, '#c5b3b0'), (0.45, '#ffd6a8')])
    s.sun(0.62, 0.44, 36, halo='#ffcf96', strength=0.9)
    s.clouds(0.05, 0.3, '#f4e6e0', 0.45, scale=4, coverage=0.56)
    s.ridge(0.46, 0.05, '#7a7c94', '#7a7c94', rough=4, haze='#f2c8a0', haze_alpha=0.35)
    s.water(0.47, tint='#3e5672', darken=0.85, ripple=2.0, glitter_x=0.62, glitter_color='#ffd8a8')
    im, dr = s.layer()
    draw_boat(dr, 0.46 * W, 0.53 * H, 360, col_of('#1c1a20'), sail=True, people=3)
    draw_person(dr, 0.7 * W, 0.535 * H, 110, col_of('#1c1a20'), robe=True, hair=True)
    dr.polygon([(0.6 * W, 0.535 * H), (W, 0.53 * H), (W, 0.55 * H), (0.62 * W, 0.545 * H)], fill=col_of('#2a2a26'))
    s.composite(im, 0.9)
    s.vignette(0.25)
    return s


def walk_on_water(seed):
    s = Scene(seed)
    s.sky([(0, '#1a2236'), (0.3, '#3a4660'), (0.5, '#8a96a8'), (0.56, '#c8ccd0')])
    s.clouds(0.02, 0.4, '#2a3348', 0.7, scale=4, coverage=0.45)
    s.glow(0.64, 0.5, 380, '#fff4dc', 0.35, 1.4)
    s.water(0.56, tint='#1e2a3c', darken=0.75, ripple=6.0, glitter_x=0.64, glitter_color='#e8ecf2')
    im, dr = s.layer()
    for i in range(70):
        x = s.rng.uniform(0, W)
        y = s.rng.uniform(0.57, 1.0) * H
        ln = s.rng.uniform(30, 120)
        dr.arc([x - ln, y - 20, x + ln, y + 20], 200, 340, fill=col_of('#c8d2e0', 90), width=3)
    draw_boat(dr, 0.34 * W, 0.62 * H, 300, col_of('#0e121a'), sail=True, people=3)
    draw_person(dr, 0.64 * W, 0.645 * H, 150, col_of('#0e121a'), robe=True, hair=True)
    s.composite(im, 0.9)
    s.glow(0.64, 0.62, 120, '#fff4dc', 0.2, 1.5)
    s.vignette(0.3)
    return s


def bread_of_life(seed):
    s = Scene(seed)
    s.sky([(0, '#4f6a96'), (0.35, '#cfb8a6'), (0.6, '#f2d6aa')])
    s.sun(0.3, 0.55, 34, halo='#ffd59a', strength=0.8)
    s.ridge(0.6, 0.04, '#8a8a8a', '#8a8a8a', rough=4, haze='#f0d4ac', haze_alpha=0.4)
    s.hills(0.66, [(0.015, 0.8, 0.2)], '#86955c', '#52603a')
    im, dr = s.layer()
    dr.rectangle([0, 0.8 * H, W, H], fill=col_of('#5a4030'))
    dr.rectangle([0, 0.8 * H, W, 0.808 * H], fill=col_of('#7a5a40'))
    s.composite(im, 2)
    s.glow(0.5, 0.76, 320, '#ffe0a6', 0.22, 1.5)
    im, dr = s.layer()
    draw_basket(dr, 0.5 * W, 0.775 * H, 420, col_of('#7a5430'), col_of('#e8b870'), col_of('#9aa8b0'))
    s.composite(im, 1)
    s.vignette(0.3)
    return s


def gethsemane(seed):
    s = Scene(seed)
    s.sky([(0, '#060b1e'), (0.4, '#17234a'), (0.6, '#2c3a64')])
    s.stars(500, y_max=0.5)
    s.sun(0.7, 0.2, 40, color='#f2f2ea', halo='#c8d4ff', strength=0.45)
    top = s.hills(0.66, [(0.015, 0.8, 0.3)], '#141a2c', '#0b0f1c')
    im, dr = s.layer()
    for x, h in ((0.15, 420), (0.86, 380), (0.65, 300)):
        draw_olive_tree(dr, x * W, top[int(x * W)] + 20, h, col_of('#0a0d18'), s.rng)
    dr.ellipse([0.36 * W, 0.7 * H, 0.58 * W, 0.76 * H], fill=col_of('#1a1e2c'))
    s.composite(im, 0.9)
    im, dr = s.layer()
    x, y, h = 0.5 * W, 0.71 * H, 200
    c = col_of('#05070e')
    dr.ellipse([x - h * 0.02, y - h * 0.95, x + h * 0.13, y - h * 0.8], fill=c)
    dr.polygon([(x - h * 0.09, y - h * 0.78), (x + h * 0.07, y - h * 0.8), (x + h * 0.1, y - h * 0.42), (x - h * 0.13, y - h * 0.4)], fill=c)
    dr.polygon([(x - h * 0.13, y - h * 0.44), (x + h * 0.1, y - h * 0.44), (x + h * 0.09, y), (x - h * 0.11, y)], fill=c)
    dr.polygon([(x - h * 0.11, y - h * 0.09), (x - h * 0.4, y - h * 0.05), (x - h * 0.42, y), (x - h * 0.11, y)], fill=c)
    dr.polygon([(x + h * 0.02, y - h * 0.74), (x + h * 0.08, y - h * 0.77), (x + h * 0.2, y - h * 0.62), (x + h * 0.15, y - h * 0.57)], fill=c)
    s.composite(im, 0.8)
    s.glow(0.53, 0.62, 160, '#cfd8ff', 0.12, 1.5)
    s.vignette(0.3)
    return s


def three_crosses(seed):
    s = Scene(seed)
    s.sky([(0, '#1c1c34'), (0.25, '#5a3e5a'), (0.42, '#c8705a'), (0.5, '#f0a46a')])
    s.lit_clouds(0.05, 0.4, '#3a2a40', '#e88a6a', 0.42, alpha=0.7, scale=4, coverage=0.5)
    s.glow(0.5, 0.42, 420, '#ffb47a', 0.3, 1.4)
    top = s.hills(0.5, [(0.035, 0.5, 1.5)], '#221820', '#140e14')
    im, dr = s.layer()
    for x, h in ((0.36, 260), (0.5, 340), (0.64, 260)):
        draw_cross(dr, x * W, top[int(x * W)] + 8, h, col_of('#0e090e'))
    s.composite(im, 0.8)
    s.vignette(0.32)
    return s


def empty_tomb(seed):
    s = Scene(seed)
    s.sky([(0, '#5a7cb0'), (0.3, '#c9b0b8'), (0.5, '#ffd8a8'), (0.56, '#ffe8c4')])
    s.sun(0.72, 0.5, 44, halo='#ffd896', strength=1.1)
    s.rays(0.72, 0.5, '#fff2d0', 0.2, n=12)
    s.clouds(0.05, 0.35, '#fbeee4', 0.45, scale=4, coverage=0.57)
    top = s.hills(0.62, [(0.015, 0.8, 0.2)], '#6a7a52', '#3e4c32')
    im, dr = s.layer()
    draw_tomb(dr, 0.42 * W, 0.72 * H, 300, col_of('#6a5e52'), col_of('#1a1410'), col_of('#7a6e60'))
    s.composite(im, 1)
    s.glow(0.42, 0.7, 160, '#fff4d8', 0.35, 1.5)
    s.flowers(np.full(W, 0.8 * H), 500, ['#ffffff', '#ffe68a', '#f4c6d8'])
    s.vignette(0.25)
    return s


def emmaus_road(seed):
    s = Scene(seed)
    sky_dusk(s)
    s.sun(0.5, 0.58, 46, halo='#ffbe7a', strength=1.0)
    s.lit_clouds(0.08, 0.45, '#7a6a90', '#ffc49a', 0.55, alpha=0.5, scale=4, coverage=0.57)
    s.ridge(0.6, 0.03, '#8a6c80', '#8a6c80', rough=4, haze='#ffb48a', haze_alpha=0.35)
    top = s.hills(0.64, [(0.01, 1.0, 0.3)], '#5a4a4c', '#2c2226')
    im, dr = s.layer()
    dr.polygon([(0.49 * W, 0.645 * H), (0.51 * W, 0.645 * H), (0.66 * W, H), (0.34 * W, H)], fill=col_of('#b4906e', 220))
    s.composite(im, 2)
    im, dr = s.layer()
    for x, h, hair in ((0.46, 160, False), (0.5, 170, True), (0.54, 158, False)):
        draw_person(dr, x * W, 0.72 * H, h, col_of('#1a1418'), robe=True, hair=hair, stride=0.4)
    s.composite(im, 0.8)
    s.grass(top, 1400, ['#3a2d33', '#4a3a3e', '#2b2226'], height=(30, 120))
    s.vignette(0.3)
    return s


def communion(seed):
    s = Scene(seed)
    s.sky([(0, '#0e0c12'), (0.6, '#1e1a20'), (1.0, '#2a2226')])
    s.glow(0.5, 0.62, 700, '#ffb860', 0.28, 1.3)
    im, dr = s.layer()
    dr.rectangle([0, 0.78 * H, W, H], fill=col_of('#3a2618'))
    s.composite(im, 1)
    im, dr = s.layer()
    draw_chalice(dr, 0.6 * W, 0.78 * H, 330, col_of('#c9a050'))
    draw_loaf(dr, 0.36 * W, 0.785 * H, 300, col_of('#c88a4a'), col_of('#7a4a24'))
    s.composite(im, 1)
    flame(s, 0.82, 0.62, 80, glow=True)
    im, dr = s.layer()
    dr.rectangle([0.8 * W, 0.62 * H, 0.84 * W, 0.78 * H], fill=col_of('#efe2c8'))
    s.composite(im, 1)
    s.glow(0.6, 0.66, 160, '#ffe2a0', 0.18, 1.5)
    s.vignette(0.35)
    return s


def true_vine(seed):
    s = Scene(seed)
    s.sky([(0, '#6a90c0'), (0.3, '#c6d4dc'), (0.5, '#f6e8cc')])
    s.sun(0.75, 0.48, 34, halo='#fff0c4', strength=0.8)
    s.ridge(0.52, 0.05, '#8aa0aa', '#9aaeb0', rough=4, haze='#f2e6cc', haze_alpha=0.45)
    top = s.hills(0.56, [(0.02, 0.7, 0.3)], '#8aa45a', '#4e6a32')
    im, dr = s.layer()
    for r in range(8):
        y = 0.58 * H + r * r * 9 + r * 40
        for k in range(18):
            x = (k / 17) * W * 1.1 - 0.05 * W + (r % 2) * 20
            sz = 6 + r * 4
            dr.ellipse([x - sz * 2, y - sz, x + sz * 2, y + sz * 0.6], fill=col_of('#3e5a26'))
    s.composite(im, 1)
    im, dr = s.layer()
    vine = bezier((-50, 0.82 * H), (0.3 * W, 0.74 * H), (0.6 * W, 0.92 * H), (W + 50, 0.8 * H), 60)
    dr.line(vine, fill=col_of('#3a2a1a'), width=18)
    for i in range(0, 60, 6):
        vx, vy = vine[i]
        for _ in range(3):
            lx = vx + s.rng.uniform(-60, 60)
            ly = vy + s.rng.uniform(-80, 20)
            dr.ellipse([lx - 40, ly - 26, lx + 40, ly + 26], fill=col_of('#4a6e2a'))
        if i % 12 == 0:
            for g in range(14):
                gx = vx + s.rng.uniform(-20, 20)
                gy = vy + 30 + g * 8 + s.rng.uniform(-6, 6)
                dr.ellipse([gx - 12, gy - 12, gx + 12, gy + 12], fill=col_of('#4a2a5a'))
    s.composite(im, 1)
    s.vignette(0.25)
    return s


def lilies(seed):
    s = Scene(seed)
    s.sky([(0, '#5e94cc'), (0.25, '#a6c8e4'), (0.4, '#eef2ea')])
    s.clouds(0.03, 0.3, '#ffffff', 0.65, scale=4, coverage=0.52)
    s.ridge(0.64, 0.03, '#9cbab4', '#a6c0b4', rough=4, haze='#f0f4ea', haze_alpha=0.5)
    top = s.hills(0.68, [(0.01, 1.0, 0.4)], '#94bc64', '#4e8436')
    s.grass(top, 2500, ['#4e8436', '#6aa04a', '#3e6e2a'], height=(30, 140))
    im, dr = s.layer()
    for _ in range(90):
        x = s.rng.uniform(0, W)
        y = s.rng.uniform(0.72, 1.02) * H
        k = (y - 0.7 * H) / (0.3 * H)
        draw_lily(dr, x, y, 60 + 200 * k, col_of('#3e6e2a'), col_of('#fbf8f0'))
    s.composite(im, 0.9)
    s.vignette(0.2)
    return s


def lamp_stand(seed):
    s = Scene(seed)
    s.sky([(0, '#0c0e16'), (1.0, '#1c1a20')])
    im, dr = s.layer()
    dr.rectangle([0.18 * W, 0.18 * H, 0.82 * W, 0.5 * H], fill=col_of('#24304a'))
    dr.line([0.5 * W, 0.18 * H, 0.5 * W, 0.5 * H], fill=col_of('#0c0e16'), width=14)
    dr.line([0.18 * W, 0.34 * H, 0.82 * W, 0.34 * H], fill=col_of('#0c0e16'), width=14)
    s.composite(im, 1)
    s.stars(80, y_max=0.45)
    s.glow(0.5, 0.66, 760, '#ffb060', 0.35, 1.3)
    im, dr = s.layer()
    draw_oil_lamp(dr, 0.46 * W, 0.7 * H, 340, col_of('#6a4426'))
    dr.rectangle([0, 0.86 * H, W, H], fill=col_of('#2a1c12'))
    s.composite(im, 1)
    flame(s, (0.46 * W + 340 * 0.56) / W, (0.7 * H - 340 * 0.22) / H, 120)
    s.vignette(0.3)
    return s


def lamb_of_god(seed):
    s = Scene(seed)
    s.sky([(0, '#6a8cbc'), (0.3, '#d2c4c0'), (0.52, '#ffe2b8')])
    s.sun(0.72, 0.48, 36, halo='#ffe0a8', strength=0.8)
    s.rays(0.72, 0.48, '#fff4dc', 0.12, n=12)
    s.ridge(0.54, 0.04, '#9aa6b4', '#9aa6b4', rough=4, haze='#ffe8c8', haze_alpha=0.45)
    top = s.hills(0.6, [(0.025, 0.5, 1.6)], '#a8c06c', '#5a8040', light=(0.5, '#fff0b8', 0.2))
    im, dr = s.layer()
    draw_sheep(dr, 0.5 * W, top[int(0.5 * W)] + 70, 200, col_of('#f6eee0'), col_of('#3a3228'), 1)
    s.composite(im, 1)
    s.grass(np.full(W, 0.8 * H), 1800, ['#4f7f33', '#6a9442', '#3a6527'], height=(40, 140))
    s.vignette(0.22)
    return s


def pentecost(seed):
    s = Scene(seed)
    s.sky([(0, '#2a1c3c'), (0.3, '#7a3e5a'), (0.55, '#ff8a4a'), (0.62, '#ffc874')])
    s.glow(0.5, 0.62, 900, '#ff9a4a', 0.4, 1.3)
    s.rays(0.5, 0.64, '#ffd090', 0.25, n=16)
    # curved horizon: "to the ends of the earth"
    d = np.sqrt((s.xx - 0.5 * W) ** 2 + (s.yy - (0.64 * H + 3000)) ** 2)
    s.blend(1 - smoothstep(2998, 3002, d), rgb('#140e1a'))
    s.blend(np.exp(-((d - 3000) / 6) ** 2), rgb('#ffcf8a'), 0.8)
    im, dr = s.layer()
    for x in (0.38, 0.46, 0.54, 0.62):
        draw_person(dr, x * W, 0.68 * H, 120, col_of('#0a0610'), robe=True)
    s.composite(im, 0.8)
    for x in (0.38, 0.46, 0.54, 0.62):
        flame(s, x + 0.002, 0.68 - 120 / H - 0.004, 40, glow=False)
    s.vignette(0.3)
    return s


def prodigal(seed):
    s = Scene(seed)
    sky_dusk(s, '#ffa878')
    s.sun(0.3, 0.6, 40, halo='#ffbe7a', strength=1.0)
    s.lit_clouds(0.1, 0.45, '#7a6a90', '#ffc49a', 0.55, alpha=0.5, scale=4, coverage=0.57)
    top = s.hills(0.66, [(0.025, 0.6, 2.0)], '#4a3c40', '#241c20')
    im, dr = s.layer()
    hx = int(0.76 * W)
    draw_house(dr, hx, top[hx] + 10, 150, col_of('#16121a'), col_of('#ffcc78'))
    dr.polygon([(0.72 * W, top[hx] + 14), (0.75 * W, top[hx] + 14), (0.5 * W, H), (0.3 * W, H)], fill=col_of('#9a7a62', 160))
    s.composite(im, 1.5)
    im, dr = s.layer()
    c = col_of('#120e14')
    draw_person(dr, 0.53 * W, 0.735 * H, 170, c, robe=True, hair=False)
    draw_person(dr, 0.575 * W, 0.735 * H, 175, c, robe=True, hair=True)
    s.composite(im, 0.8)
    s.vignette(0.3)
    return s


def darkest_valley(seed):
    s = Scene(seed)
    s.sky([(0, '#1a1e30'), (0.4, '#3a4058'), (0.55, '#c8a888')])
    s.glow(0.5, 0.52, 260, '#ffe6b8', 0.45, 1.4)
    im, dr = s.layer()
    left = [(0, 0)] + [(0.05 * W + 0.38 * W * (i / 30) ** 0.7 + s.rng.uniform(-15, 15), i / 30 * H) for i in range(31)] + [(0, H)]
    right = [(W, 0)] + [(0.95 * W - 0.38 * W * (i / 30) ** 0.7 + s.rng.uniform(-15, 15), i / 30 * H) for i in range(31)] + [(W, H)]
    dr.polygon(left, fill=col_of('#14161f'))
    dr.polygon(right, fill=col_of('#181a24'))
    s.composite(im, 1.2)
    im, dr = s.layer()
    dr.polygon([(0.48 * W, 0.56 * H), (0.52 * W, 0.56 * H), (0.6 * W, H), (0.4 * W, H)], fill=col_of('#5a4e44', 200))
    s.composite(im, 3)
    im, dr = s.layer()
    draw_person(dr, 0.52 * W, 0.74 * H, 190, col_of('#08090e'), robe=True, staff=True, hair=True)
    flock(s, dr, [(0.44, 0.77, 1.0, 1), (0.4, 0.8, 1.15, 1), (0.47, 0.81, 1.2, 1)], 70, body='#8c8a94', head='#08090e')
    s.composite(im, 0.8)
    s.vignette(0.3)
    return s


def house_of_lord(seed):
    s = Scene(seed)
    s.sky([(0, '#6a8cc0'), (0.25, '#c4cfdc'), (0.42, '#fbe8c8')])
    s.sun(0.68, 0.36, 34, halo='#fff0c4', strength=0.8)
    s.clouds(0.03, 0.22, '#ffffff', 0.5, scale=5, coverage=0.56)
    s.ridge(0.44, 0.05, '#9aaab8', '#a4b0ba', rough=4, haze='#f6e8d0', haze_alpha=0.45)
    top = s.hills(0.48, [(0.02, 0.6, 1.2)], '#a4c06a', '#5c8a40', light=(0.68, '#fff0b8', 0.2))
    im, dr = s.layer()
    cx = int(0.5 * W)
    draw_church(dr, cx - 60, top[cx] + 8, 230, col_of('#f4ece0'), window=col_of('#c89a5a'))
    pts = [(0.5 * W + math.sin(t * 6) * 80 * t, top[cx] + 20 + t * (H - top[cx])) for t in np.linspace(0, 1, 60)]
    for i, (x, y) in enumerate(pts):
        w = 4 + i * 2.2
        dr.ellipse([x - w, y - w * 0.25, x + w, y + w * 0.25], fill=col_of('#e4d2a8'))
    flock(s, dr, [(0.36, 0.53, 0.9, 1), (0.42, 0.535, 1.0, 1), (0.62, 0.53, 0.9, -1)], 60)
    s.composite(im, 1)
    s.vignette(0.22)
    return s


def under_wings(seed):
    s = Scene(seed)
    s.sky([(0, '#3a4c74'), (0.35, '#a08ca8'), (0.58, '#ffc898'), (0.64, '#ffe0b4')])
    s.sun(0.5, 0.62, 44, halo='#ffcc8a', strength=1.0)
    s.lit_clouds(0.08, 0.45, '#8a7aa0', '#ffd0a4', 0.55, alpha=0.5, scale=4, coverage=0.57)
    top = s.hills(0.7, [(0.01, 1.0, 0.2)], '#3a3040', '#1c1620')
    im, dr = s.layer()
    c = col_of('#120e16')
    # a branch with a large bird spreading its wings over small ones
    dr.line(bezier((-0.05 * W, 0.745 * H), (0.3 * W, 0.735 * H), (0.6 * W, 0.75 * H), (1.05 * W, 0.735 * H)), fill=c, width=34)
    bx, by, k = 0.5 * W, 0.735 * H, 1.7
    dr.ellipse([bx - 70 * k, by - 120 * k, bx + 70 * k, by + 10 * k], fill=c)
    dr.ellipse([bx - 34 * k, by - 175 * k, bx + 30 * k, by - 108 * k], fill=c)
    dr.polygon([(bx + 26 * k, by - 148 * k), (bx + 58 * k, by - 138 * k), (bx + 26 * k, by - 128 * k)], fill=c)
    for sgn in (-1, 1):
        wing = bezier((bx, by - 100 * k), (bx + sgn * 110 * k, by - 190 * k), (bx + sgn * 230 * k, by - 120 * k), (bx + sgn * 300 * k, by + 5 * k)) + \
            bezier((bx + sgn * 300 * k, by + 5 * k), (bx + sgn * 200 * k, by - 30 * k), (bx + sgn * 110 * k, by - 5 * k), (bx, by - 10 * k))
        dr.polygon(wing, fill=c)
    for dx in (-200, -130, 130, 200):
        dr.ellipse([bx + dx * k - 22 * k, by - 22 * k, bx + dx * k + 22 * k, by + 12 * k], fill=c)
        dr.ellipse([bx + dx * k - 12 * k, by - 42 * k, bx + dx * k + 12 * k, by - 18 * k], fill=c)
    s.composite(im, 0.9)
    s.vignette(0.3)
    return s


def perfect_peace(seed):
    s = Scene(seed)
    s.sky([(0, '#2a3460'), (0.25, '#8a86ae'), (0.42, '#f0c4b0'), (0.47, '#f8dcc0')])
    s.glow(0.5, 0.47, 500, '#ffd8b8', 0.3, 1.4)
    s.ridge(0.47, 0.03, '#6c6a8a', '#6c6a8a', rough=4, haze='#f0c8b8', haze_alpha=0.3)
    im, dr = s.layer()
    dr.ellipse([0.36 * W, 0.465 * H, 0.64 * W, 0.49 * H], fill=col_of('#2a2a3c'))
    draw_round_tree(dr, 0.5 * W, 0.475 * H, 300, col_of('#1e1e2e'), s.rng)
    s.composite(im, 1)
    s.water(0.48, tint='#3c4064', darken=0.88, ripple=1.0)
    s.vignette(0.25)
    return s


def prayer_by_sea(seed):
    s = Scene(seed)
    s.sky([(0, '#34477a'), (0.35, '#b29aaa'), (0.55, '#ffcca0'), (0.6, '#ffe2b8')])
    s.sun(0.5, 0.585, 44, halo='#ffcc8a', strength=1.0)
    s.lit_clouds(0.08, 0.45, '#8e7ea0', '#ffd0a8', 0.55, alpha=0.5, scale=4, coverage=0.57)
    s.water(0.6, tint='#3a4870', darken=0.85, ripple=2.0, glitter_x=0.5, glitter_color='#ffd8a8')
    im, dr = s.layer()
    dr.polygon([(0.15 * W, H), (0.3 * W, 0.76 * H), (0.55 * W, 0.74 * H), (0.75 * W, 0.8 * H), (0.85 * W, H)], fill=col_of('#18141e'))
    x, y, h = 0.48 * W, 0.745 * H, 190
    c = col_of('#0c0a10')
    dr.ellipse([x - h * 0.02, y - h * 0.95, x + h * 0.13, y - h * 0.8], fill=c)
    dr.polygon([(x - h * 0.09, y - h * 0.78), (x + h * 0.07, y - h * 0.8), (x + h * 0.1, y - h * 0.42), (x - h * 0.13, y - h * 0.4)], fill=c)
    dr.polygon([(x - h * 0.13, y - h * 0.44), (x + h * 0.1, y - h * 0.44), (x + h * 0.09, y), (x - h * 0.11, y)], fill=c)
    dr.polygon([(x - h * 0.11, y - h * 0.09), (x - h * 0.4, y - h * 0.05), (x - h * 0.42, y), (x - h * 0.11, y)], fill=c)
    dr.polygon([(x + h * 0.02, y - h * 0.74), (x + h * 0.08, y - h * 0.77), (x + h * 0.2, y - h * 0.62), (x + h * 0.15, y - h * 0.57)], fill=c)
    dr.polygon([(x + h * 0.14, y - h * 0.6), (x + h * 0.2, y - h * 0.61), (x + h * 0.22, y - h * 0.77), (x + h * 0.17, y - h * 0.78)], fill=c)
    s.composite(im, 0.9)
    s.vignette(0.3)
    return s


def winding_river(seed):
    s = Scene(seed)
    s.sky([(0, '#5a80b4'), (0.3, '#c8d4de'), (0.45, '#f6e6c8')])
    s.sun(0.4, 0.44, 30, halo='#fff0c4', strength=0.7)
    s.ridge(0.47, 0.08, '#7e94aa', '#8c9eae', rough=4, haze='#f0e2cc', haze_alpha=0.4)
    s.mist(0.48, 0.015, '#f6eee0', 0.5)
    top = s.hills(0.5, [(0.01, 1.0, 0.2)], '#86a660', '#3e6230', light=(0.4, '#fff0b8', 0.15))
    im, dr = s.layer()
    pts = []
    for t in np.linspace(0, 1, 120):
        y = 0.505 * H + t * 0.5 * H
        x = 0.5 * W + math.sin(t * 9) * W * 0.22 * t
        w = 4 + 150 * t ** 1.4
        dr.ellipse([x - w, y - w * 0.18, x + w, y + w * 0.18], fill=col_of('#a8c4d8'))
    s.composite(im, 1.5)
    s.pines(top, 40, '#2a4127', height=(60, 200), x_range=(0.0, 0.2), y_jitter=300)
    s.pines(top, 40, '#2a4127', height=(60, 200), x_range=(0.82, 1.0), y_jitter=300)
    s.vignette(0.22)
    return s


def spring_blossom(seed):
    s = Scene(seed)
    s.sky([(0, '#6c9ad0'), (0.3, '#c4d8ea'), (0.45, '#f6eee6')])
    s.clouds(0.03, 0.2, '#ffffff', 0.6, scale=5, coverage=0.55)
    s.ridge(0.5, 0.03, '#a4bcc0', '#a4bcc0', rough=4, haze='#f2f2ea', haze_alpha=0.5)
    top = s.hills(0.55, [(0.02, 0.7, 0.4)], '#a8cc74', '#5a9040')
    im, dr = s.layer()
    tx, ty = 0.5 * W, top[int(0.5 * W)] + 20
    dr.polygon([(tx - 26, ty), (tx + 26, ty), (tx + 10, ty - 250), (tx - 10, ty - 250)], fill=col_of('#4a3426'))
    for a in (-0.9, -0.4, 0.3, 0.8):
        dr.line([tx, ty - 220, tx + math.sin(a) * 260, ty - 220 - math.cos(a) * 200], fill=col_of('#4a3426'), width=16)
    for _ in range(900):
        r = abs(s.rng.normal(0, 1)) * 0.5 + s.rng.uniform(0, 0.5)
        ang = s.rng.uniform(math.pi, 2 * math.pi)
        x = tx + math.cos(ang) * 380 * r
        y = ty - 330 + math.sin(ang) * 260 * r * 0.9 + 60
        sz = s.rng.uniform(8, 22)
        c = ['#ffd6e4', '#ffc4d8', '#fff0f4', '#f4a8c4'][s.rng.integers(4)]
        dr.ellipse([x - sz, y - sz, x + sz, y + sz], fill=col_of(c, 230))
    s.composite(im, 1)
    s.grass(np.full(W, 0.72 * H), 2600, ['#5a9040', '#74a850', '#4a7a32'], height=(30, 130))
    s.flowers(np.full(W, 0.7 * H), 500, ['#ffd6e4', '#ffffff', '#f4a8c4'], size=(3, 8))
    s.vignette(0.2)
    return s


def grace_cross_meadow(seed):
    s = Scene(seed)
    s.sky([(0, '#5a7cb4'), (0.25, '#c8c4d0'), (0.42, '#ffdcb0'), (0.48, '#ffe8c8')])
    s.glow(0.5, 0.36, 600, '#fff0d0', 0.4, 1.3)
    s.rays(0.5, 0.36, '#fff4dc', 0.22, n=14)
    s.clouds(0.04, 0.25, '#ffffff', 0.4, scale=5, coverage=0.56)
    top = s.hills(0.48, [(0.03, 0.5, 1.6)], '#a8c46c', '#5e8a42', light=(0.5, '#fff0b8', 0.2))
    im, dr = s.layer()
    cx = int(0.5 * W)
    draw_cross(dr, cx, top[cx] + 6, 300, col_of('#3a2c22'))
    s.composite(im, 0.9)
    s.flowers(top, 1200, ['#ffffff', '#ffe68a', '#f4c6d8', '#d8c4ff'])
    s.vignette(0.22)
    return s


def lighthouse(seed):
    s = Scene(seed)
    s.sky([(0, '#141c34'), (0.28, '#3c4870'), (0.45, '#a07c88'), (0.5, '#e09a7a')])
    s.stars(300, y_max=0.35)
    s.water(0.5, tint='#1c2440', darken=0.8, ripple=3.0)
    im, dr = s.layer()
    dr.polygon([(0.48 * W, 0.53 * H), (0.6 * W, 0.47 * H), (0.84 * W, 0.455 * H), (W, 0.47 * H), (W, 0.55 * H), (0.44 * W, 0.55 * H)], fill=col_of('#14141e'))
    draw_lighthouse(dr, 0.74 * W, 0.462 * H, 340, col_of('#14141e'), col_of('#fff0c0'))
    s.composite(im, 0.9)
    lx, ly = 0.74, (0.462 * H - 0.92 * 340) / H
    ang = np.arctan2(s.yy - ly * H, s.xx - lx * W)
    d = np.sqrt((s.xx - lx * W) ** 2 + (s.yy - ly * H) ** 2)
    beam = np.exp(-((ang - math.pi * 0.97) / 0.07) ** 2) * np.exp(-d / 1400)
    s.add(rgb('#fff0c8') * (0.5 * beam)[..., None])
    s.glow(lx, ly, 60, '#fff4d0', 0.8, 1.6)
    s.vignette(0.3)
    return s


def delight_garden(seed):
    s = Scene(seed)
    s.sky([(0, '#5c96d0'), (0.25, '#a8cceb'), (0.42, '#f0f4ea')])
    s.sun(0.75, 0.14, 34, halo='#fff4d0', strength=0.7)
    s.clouds(0.04, 0.3, '#ffffff', 0.6, scale=4, coverage=0.53)
    s.ridge(0.66, 0.03, '#9cc0b4', '#a6c4b4', rough=4, haze='#f0f4ea', haze_alpha=0.5)
    top = s.hills(0.7, [(0.01, 1.0, 0.4)], '#9cc46a', '#5a9a3e')
    im, dr = s.layer()
    for x, h in ((0.12, 340), (0.88, 360), (0.28, 240), (0.74, 250)):
        draw_round_tree(dr, x * W, top[int(x * W)] + 30, h, col_of('#3e6a2c'), s.rng)
        for _ in range(14):
            fx = x * W + s.rng.uniform(-0.25, 0.25) * h
            fy = top[int(x * W)] + 30 - h * 0.62 + s.rng.uniform(-0.15, 0.15) * h
            dr.ellipse([fx - 10, fy - 10, fx + 10, fy + 10], fill=col_of('#ff9a4a'))
    dr.polygon([(0.49 * W, top[int(0.5 * W)] + 4), (0.51 * W, top[int(0.5 * W)] + 4), (0.62 * W, H), (0.38 * W, H)], fill=col_of('#e4d2a8'))
    s.composite(im, 1)
    s.flowers(top, 2200, ['#ffffff', '#ffe26a', '#ffb3c6', '#e889a8', '#c9a8ff'], size=(3, 10))
    s.vignette(0.2)
    return s


def two_trees(seed):
    s = Scene(seed)
    sky_dusk(s, '#ffb48a')
    s.sun(0.5, 0.6, 44, halo='#ffbe7a', strength=1.0)
    s.lit_clouds(0.08, 0.45, '#7a6a90', '#ffc49a', 0.55, alpha=0.5, scale=4, coverage=0.57)
    top = s.hills(0.68, [(0.03, 0.5, 1.6)], '#3a2c38', '#1c141c')
    im, dr = s.layer()
    c = col_of('#120c12')
    bx, by = 0.5 * W, top[int(0.5 * W)] + 10
    for sgn in (-1, 1):
        trunk = bezier((bx + sgn * 34, by + 10), (bx - sgn * 40, by - 140), (bx + sgn * 150, by - 250), (bx + sgn * 70, by - 380), 30)
        for i in range(len(trunk) - 1):
            dr.line([trunk[i], trunk[i + 1]], fill=c, width=int(54 - 30 * i / len(trunk)))
        dr.ellipse([bx + sgn * 34 - 46, by - 6, bx + sgn * 34 + 46, by + 26], fill=c)
    for _ in range(36):
        cx = bx + s.rng.uniform(-0.6, 0.6) * 460
        cy = by - 430 + s.rng.uniform(-0.3, 0.2) * 320
        r = s.rng.uniform(60, 110)
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    s.composite(im, 0.9)
    s.vignette(0.3)
    return s


def family_beach(seed):
    s = Scene(seed)
    s.sky([(0, '#3a4c80'), (0.35, '#c08ea0'), (0.55, '#ffc08a'), (0.6, '#ffdca8')])
    s.sun(0.62, 0.585, 46, halo='#ffbe7a', strength=1.0)
    s.lit_clouds(0.08, 0.45, '#8a6e9a', '#ffc8a0', 0.55, alpha=0.5, scale=4, coverage=0.57)
    s.water(0.6, tint='#3e4a78', darken=0.85, ripple=2.5, glitter_x=0.62, glitter_color='#ffd4a0')
    im, dr = s.layer()
    dr.polygon([(0, 0.74 * H), (W, 0.7 * H), (W, H), (0, H)], fill=col_of('#b88a74', 235))
    s.composite(im, 3)
    im, dr = s.layer()
    c = col_of('#1a1218')
    draw_person(dr, 0.38 * W, 0.8 * H, 210, c, robe=False)
    draw_person(dr, 0.47 * W, 0.8 * H, 195, c, robe=True, hair=True)
    draw_person(dr, 0.55 * W, 0.8 * H, 120, c, robe=False)
    draw_person(dr, 0.6 * W, 0.8 * H, 95, c, robe=True, hair=True, arms_up=True)
    s.composite(im, 0.8)
    s.vignette(0.3)
    return s


def garden_gate(seed):
    s = Scene(seed)
    s.sky([(0, '#5e84b8'), (0.3, '#c8cede'), (0.52, '#fbe6c4')])
    s.clouds(0.04, 0.3, '#ffffff', 0.5, scale=4, coverage=0.55)
    s.glow(0.5, 0.62, 300, '#fff4d8', 0.4, 1.4)
    im, dr = s.layer()
    draw_wall_gate(dr, 0.5 * W, 0.8 * H, 500, col_of('#8a7a68'), col_of('#fff0cc'))
    s.composite(im, 1)
    s.glow(0.5, 0.66, 200, '#fff6e0', 0.35, 1.5)
    im, dr = s.layer()
    for _ in range(300):
        x = s.rng.uniform(0, W)
        y = s.rng.uniform(0.52, 0.66) * H
        if abs(x - 0.5 * W) < 140:
            continue
        r = s.rng.uniform(10, 26)
        dr.ellipse([x - r, y - r, x + r, y + r], fill=col_of(['#4a6e2a', '#5a8236', '#3a5a22'][s.rng.integers(3)]))
    dr.rectangle([0, 0.84 * H, W, H], fill=col_of('#6a8a44'))
    s.composite(im, 1)
    s.flowers(np.full(W, 0.84 * H), 800, ['#ffffff', '#ffe26a', '#ffb3c6'])
    s.vignette(0.22)
    return s


def light_after_rain(seed):
    s = Scene(seed)
    s.sky([(0, '#3a4256'), (0.3, '#6a7488'), (0.5, '#c8c4c0'), (0.6, '#e8dcc8')])
    s.clouds(0.0, 0.35, '#4a5060', 0.8, scale=4, coverage=0.4)
    s.glow(0.62, 0.3, 300, '#fff4d8', 0.45, 1.4)
    s.rays(0.62, 0.28, '#fff4dc', 0.25, n=9, length=2400)
    im, dr = s.layer()
    for _ in range(500):
        x = s.rng.uniform(0, 0.45) * W
        y = s.rng.uniform(0.2, 0.7) * H
        dr.line([x, y, x - 10, y + 50], fill=col_of('#c8d0dc', 70), width=2)
    s.composite(im, 0.6)
    s.ridge(0.66, 0.05, '#6c7a80', '#78848a', rough=4, haze='#e8dcc8', haze_alpha=0.35)
    top = s.hills(0.72, [(0.02, 0.7, 0.5)], '#5e7a4a', '#34482a', light=(0.62, '#fff0c0', 0.2))
    s.grass(np.full(W, 0.86 * H), 1400, ['#34482a', '#46603a', '#283a20'], height=(40, 130))
    s.vignette(0.28)
    return s


def light_of_world(seed):
    s = Scene(seed)
    s.sky([(0, '#3a5070'), (0.4, '#9aa8a4'), (0.6, '#f0dcb4')])
    s.glow(0.5, 0.55, 500, '#fff0c8', 0.5, 1.3)
    s.rays(0.5, 0.5, '#fff4d8', 0.3, n=12, length=2600)
    top = s.hills(0.62, [(0.01, 1.0, 0.2)], '#5a6a4a', '#2c3a26')
    im, dr = s.layer()
    for _ in range(46):
        x = s.rng.choice([s.rng.uniform(-0.05, 0.36), s.rng.uniform(0.64, 1.05)]) * W
        w = s.rng.uniform(14, 44)
        lean = s.rng.uniform(-30, 30)
        dr.polygon([(x - w + lean, -20), (x + w * 0.7 + lean, -20), (x + w * 1.3, H), (x - w * 1.3, H)], fill=col_of('#18201a'))
    dr.polygon([(0.48 * W, 0.63 * H), (0.52 * W, 0.63 * H), (0.62 * W, H), (0.38 * W, H)], fill=col_of('#c8b08a', 200))
    s.composite(im, 1.4)
    s.mist(0.66, 0.05, '#f6ecd8', 0.35)
    im, dr = s.layer()
    draw_person(dr, 0.5 * W, 0.72 * H, 150, col_of('#1a1a18'), robe=True, hair=True)
    s.composite(im, 0.8)
    s.vignette(0.3)
    return s


def resting_boat(seed):
    s = Scene(seed)
    s.sky([(0, '#2a3460'), (0.35, '#9a8aaa'), (0.56, '#f4c4a8'), (0.6, '#fadcc4')])
    s.glow(0.5, 0.6, 500, '#ffd8b8', 0.3, 1.4)
    s.ridge(0.6, 0.025, '#7a7090', '#7a7090', rough=4, haze='#f0c4b0', haze_alpha=0.3)
    s.water(0.61, tint='#3c4064', darken=0.88, ripple=1.0)
    im, dr = s.layer()
    draw_boat(dr, 0.5 * W, 0.68 * H, 300, col_of('#16141e'), sail=False)
    s.composite(im, 0.9)
    s.vignette(0.25)
    return s


SCENES2 = {
    'wallpaper_030': (noah_rainbow, 130),
    'wallpaper_031': (burning_bush, 131),
    'wallpaper_032': (red_sea, 132),
    'wallpaper_033': (sinai, 133),
    'wallpaper_034': (jacobs_ladder, 134),
    'wallpaper_035': (david_harp, 135),
    'wallpaper_036': (elijah_whisper, 136),
    'wallpaper_037': (jerusalem, 137),
    'wallpaper_038': (bethlehem_star, 138),
    'wallpaper_039': (shepherds_night, 139),
    'wallpaper_040': (wise_men, 140),
    'wallpaper_041': (jordan_dove, 141),
    'wallpaper_042': (galilee_boat, 142),
    'wallpaper_043': (walk_on_water, 143),
    'wallpaper_044': (bread_of_life, 144),
    'wallpaper_045': (gethsemane, 145),
    'wallpaper_046': (three_crosses, 146),
    'wallpaper_047': (empty_tomb, 147),
    'wallpaper_048': (emmaus_road, 148),
    'wallpaper_049': (communion, 149),
    'wallpaper_050': (true_vine, 150),
    'wallpaper_051': (lilies, 151),
    'wallpaper_052': (lamp_stand, 152),
    'wallpaper_053': (lamb_of_god, 153),
    'wallpaper_054': (pentecost, 154),
    'wallpaper_055': (prodigal, 155),
    'wallpaper_056': (darkest_valley, 156),
    'wallpaper_057': (house_of_lord, 157),
    'wallpaper_058': (under_wings, 158),
    'wallpaper_059': (perfect_peace, 159),
    'wallpaper_060': (prayer_by_sea, 160),
    'wallpaper_061': (winding_river, 161),
    'wallpaper_062': (spring_blossom, 162),
    'wallpaper_063': (grace_cross_meadow, 163),
    'wallpaper_064': (lighthouse, 164),
    'wallpaper_065': (delight_garden, 165),
    'wallpaper_066': (two_trees, 166),
    'wallpaper_067': (family_beach, 167),
    'wallpaper_068': (garden_gate, 168),
    'wallpaper_069': (light_after_rain, 169),
    'wallpaper_070': (light_of_world, 170),
    'wallpaper_071': (resting_boat, 171),
}
