"""Procedural painting primitives for Daily Grace placeholder artwork.

Every wallpaper is composed at 1440 x 3200 (20:9) with a safe-zone approach:
important subjects stay inside x 15-85% and y 12-88%, the text band for the
entry's layout is left calm (sky, water or soft land), and only scenery reaches
the edges.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1440, 3200


def rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


class Scene:
    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)
        self.img = np.zeros((H, W, 3), np.float32)
        yy, xx = np.mgrid[0:H, 0:W]
        self.yy = yy.astype(np.float32)
        self.xx = xx.astype(np.float32)

    # ---------- noise ----------
    def noise1d(self, n, octaves=5, base=6, persistence=0.5):
        out = np.zeros(n, np.float32)
        amp, total = 1.0, 0.0
        x = np.linspace(0, 1, n)
        for o in range(octaves):
            k = base * (2 ** o) + 1
            pts = self.rng.uniform(-1, 1, k)
            px = np.linspace(0, 1, k)
            # cosine-smoothed interpolation
            idx = np.clip((x * (k - 1)).astype(int), 0, k - 2)
            t = x * (k - 1) - idx
            t = (1 - np.cos(t * math.pi)) / 2
            out += amp * (pts[idx] * (1 - t) + pts[idx + 1] * t)
            total += amp
            amp *= persistence
        return out / total

    def noise2d(self, scale=8, octaves=4, persistence=0.5, aspect=1.0):
        """Smooth fractal value noise. aspect > 1 stretches features horizontally."""
        out = np.zeros((H, W), np.float32)
        amp, total = 1.0, 0.0
        sw, sh = W // 4, H // 4
        for o in range(octaves):
            gw = max(3, int(scale * (2 ** o)))
            gh = max(3, int(gw * H / W / aspect))
            small = self.rng.uniform(0, 1, (gh, gw)).astype(np.float32)
            im = Image.fromarray((small * 255).astype(np.uint8), 'L').resize((sw, sh), Image.BILINEAR)
            im = im.filter(ImageFilter.GaussianBlur(max(1.0, 0.45 * min(sw / gw, sh / gh))))
            im = im.resize((W, H), Image.BICUBIC)
            out += amp * (np.asarray(im, np.float32) / 255.0)
            total += amp
            amp *= persistence
        out /= total
        # re-normalise contrast lost to blurring
        lo, hi = np.percentile(out[::8, ::8], [2, 98])
        return np.clip((out - lo) / max(1e-4, hi - lo), 0, 1)

    # ---------- compositing ----------
    def blend(self, mask, color, alpha=1.0):
        m = (np.clip(mask, 0, 1) * alpha)[..., None]
        c = color if isinstance(color, np.ndarray) and color.ndim == 3 else np.asarray(color, np.float32)
        self.img = self.img * (1 - m) + c * m

    def add(self, light):
        self.img = self.img + light

    def layer(self):
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        return im, ImageDraw.Draw(im)

    def composite(self, im, blur=0.9):
        if blur:
            im = im.filter(ImageFilter.GaussianBlur(blur))
        a = np.asarray(im, np.float32) / 255.0
        alpha = a[..., 3:4]
        self.img = self.img * (1 - alpha) + a[..., :3] * alpha

    def mask_from(self, draw_fn, blur=0.9):
        im = Image.new('L', (W, H), 0)
        draw_fn(ImageDraw.Draw(im))
        if blur:
            im = im.filter(ImageFilter.GaussianBlur(blur))
        return np.asarray(im, np.float32) / 255.0

    # ---------- sky & light ----------
    def sky(self, stops):
        ys = np.array([p for p, _ in stops], np.float32) * H
        cols = np.array([rgb(c) for _, c in stops])
        y = np.arange(H, dtype=np.float32)
        col = np.stack([np.interp(y, ys, cols[:, i]) for i in range(3)], -1)
        self.img = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()

    def glow(self, cx, cy, radius, color, strength=1.0, power=2.0):
        d = np.sqrt((self.xx - cx * W) ** 2 + (self.yy - cy * H) ** 2) / radius
        self.add(rgb(color) * (strength * np.exp(-d ** power))[..., None])

    def sun(self, cx, cy, r, color='#fff6dc', halo='#ffcf7a', strength=1.0):
        self.glow(cx, cy, r * 9, halo, 0.35 * strength, 1.2)
        self.glow(cx, cy, r * 3.2, halo, 0.55 * strength, 1.6)
        d = np.sqrt((self.xx - cx * W) ** 2 + (self.yy - cy * H) ** 2)
        self.blend(1 - smoothstep(r - 2, r + 2, d), rgb(color), 0.97)

    def rays(self, cx, cy, color, strength=0.18, n=11, length=2200, seed_shift=0.0):
        dx, dy = self.xx - cx * W, self.yy - cy * H
        ang = np.arctan2(dy, dx)
        d = np.sqrt(dx ** 2 + dy ** 2)
        phase = self.rng.uniform(0, 6.28)
        pattern = 0.5 + 0.5 * np.cos(ang * n + phase + seed_shift + 0.6 * np.sin(ang * 3.0))
        pattern = pattern ** 4
        fall = np.exp(-d / length) * smoothstep(0, 140, d)
        self.add(rgb(color) * (0.42 * strength * pattern * fall)[..., None])

    def stars(self, count, y_max=0.6, size=(0.6, 2.2), bright=(0.4, 1.0)):
        im, dr = self.layer()
        for _ in range(count):
            x = self.rng.uniform(0, W)
            y = self.rng.uniform(0, H * y_max) * self.rng.uniform(0.3, 1.0) ** 0.5
            r = self.rng.uniform(*size)
            b = int(255 * self.rng.uniform(*bright))
            dr.ellipse([x - r, y - r, x + r, y + r], fill=(255, 250, 235, b))
        self.composite(im, blur=0.6)

    def milky_way(self, angle=-0.35, cy=0.25, width=0.12, strength=0.22):
        n = self.noise2d(10, 5, 0.6)
        c, s = math.cos(angle), math.sin(angle)
        x = (self.xx / W - 0.5)
        y = (self.yy / H - cy) * (H / W)
        dist = (-s * x + c * y)
        band = np.exp(-(dist / width) ** 2)
        self.add(rgb('#c9c3ff') * (strength * band * smoothstep(0.35, 0.85, n))[..., None])
        self.stars(int(900 * strength / 0.22), y_max=0.55, size=(0.4, 1.1), bright=(0.25, 0.8))

    def _cloud_mask(self, y0, y1, scale, coverage):
        """Soft cumulus/stratus shapes built from clusters of blurred ellipses."""
        im = Image.new('L', (W // 2, H // 2), 0)
        dr = ImageDraw.Draw(im)
        size = 6.0 / max(1.0, scale)  # larger scale -> smaller clouds
        clusters = int(4 + coverage * 10)
        for _ in range(clusters):
            cx = self.rng.uniform(-0.15, 1.15) * W / 2
            cy = self.rng.uniform(y0, y1) * H / 2
            span = self.rng.uniform(140, 320) * size
            for _ in range(int(self.rng.integers(8, 18))):
                ex = cx + self.rng.normal(0, span * 0.45)
                ey = cy + self.rng.normal(0, span * 0.08)
                rw = self.rng.uniform(0.18, 0.42) * span
                rh = rw * self.rng.uniform(0.32, 0.55)
                dr.ellipse([ex - rw, ey - rh, ex + rw, ey + rh * 0.7], fill=int(self.rng.uniform(150, 255)))
        im = im.filter(ImageFilter.GaussianBlur(10 * size)).resize((W, H), Image.BICUBIC)
        m = np.asarray(im, np.float32) / 255.0
        tex = self.noise2d(10, 3, 0.5, aspect=2.5)
        m = smoothstep(0.15, 0.75, m * (0.75 + 0.45 * tex))
        band = smoothstep((y0 - 0.04) * H, y0 * H, self.yy) * (1 - smoothstep(y1 * H, (y1 + 0.04) * H, self.yy))
        return m * band

    def clouds(self, y0, y1, color, alpha=0.6, scale=3, coverage=0.5, seed_aspect=3.5, soft=0.18):
        self.blend(self._cloud_mask(y0, y1, scale, 1 - coverage), rgb(color), alpha)

    def lit_clouds(self, y0, y1, base, lit, light_y, alpha=0.7, scale=3, coverage=0.52):
        """Clouds that pick up the colour of a low sun near light_y."""
        m = self._cloud_mask(y0, y1, scale, 1 - coverage)
        t = np.clip(1 - np.abs(self.yy - light_y * H) / (H * 0.35), 0, 1)[..., None]
        col = rgb(base) * (1 - t) + rgb(lit) * t
        self.blend(m, col, alpha)

    def mist(self, y, height, color, alpha=0.35):
        m = np.exp(-((self.yy - y * H) / (height * H)) ** 2)
        n = self.noise2d(4, 3, 0.5, aspect=5)
        self.blend(m * (0.6 + 0.6 * n), rgb(color), alpha)

    # ---------- land ----------
    def ridge(self, base_y, amp, color_top, color_bottom, rough=5, octaves=6, peak=None, haze=None, haze_alpha=0.0):
        """A mountain/hill silhouette whose top edge is fractal noise.

        peak=(x, height): adds a smooth summit bump centred on x (0..1).
        """
        x = np.linspace(0, 1, W)
        h = self.noise1d(W, octaves, rough, 0.52)
        if peak:
            px, ph, pw = peak
            h = h * 0.65 + ph * np.exp(-((x - px) / pw) ** 2) * (0.85 + 0.3 * self.noise1d(W, 4, 12, 0.5))
        top = (base_y - amp * h) * H
        mask = smoothstep(-1.2, 1.2, self.yy - top[None, :])
        span = np.clip((self.yy - top[None, :]) / (H * 0.25), 0, 1)[..., None]
        col = rgb(color_top) * (1 - span) + rgb(color_bottom) * span
        if haze:
            col = col * (1 - haze_alpha) + rgb(haze) * haze_alpha
        self.blend(mask, col)
        return top

    def hills(self, base_y, waves, color_top, color_bottom, light=None):
        """Smooth rolling hills. waves: list of (amp, freq, phase)."""
        x = np.linspace(0, 1, W)
        h = np.zeros(W, np.float32)
        for a, f, p in waves:
            h += a * np.sin(x * f * 2 * math.pi + p)
        top = (base_y - h) * H
        mask = smoothstep(-1.5, 1.5, self.yy - top[None, :])
        span = np.clip((self.yy - top[None, :]) / (H * 0.3), 0, 1)[..., None]
        col = rgb(color_top) * (1 - span) + rgb(color_bottom) * span
        if light is not None:
            lx, lc, ls = light
            k = np.exp(-((self.xx - lx * W) / (W * 0.45)) ** 2) * np.exp(-span[..., 0] * 4)
            col = col + rgb(lc) * (ls * k)[..., None]
        self.blend(mask, col)
        return top

    def water(self, horizon, tint='#203040', darken=0.72, ripple=4.0, glitter_x=None, glitter_color='#ffe2a8'):
        hy = int(horizon * H)
        src = self.img.copy()
        rows = np.arange(hy, H)
        mirror = np.clip(2 * hy - rows, 0, H - 1)
        refl = src[mirror]
        # gentle horizontal ripple shift
        shift = (np.sin(rows * 0.09) * ripple + np.sin(rows * 0.031 + 1.3) * ripple * 0.6).astype(int)
        for i in range(0, len(rows)):
            if shift[i]:
                refl[i] = np.roll(refl[i], shift[i], axis=0)
        # water smears reflections vertically and never mirrors a crisp sun disk
        rim = Image.fromarray((np.clip(refl, 0, 1) * 255).astype(np.uint8), 'RGB')
        rim = rim.resize((W // 4, max(1, len(rows) // 24)), Image.BILINEAR).resize((W, len(rows)), Image.BICUBIC)
        soft = np.asarray(rim, np.float32) / 255.0
        refl = np.minimum(refl * 0.35 + soft * 0.65, 0.92)
        depth = ((rows - hy) / (H - hy))[:, None, None]
        refl = refl * darken * (1 - 0.25 * depth) + rgb(tint) * (0.18 + 0.35 * depth)
        streak = self.noise2d(6, 3, 0.5, aspect=14)[hy:]
        refl = refl * (0.92 + 0.12 * streak[..., None])
        self.img[hy:] = refl
        # soft horizon line
        self.blend(np.exp(-((self.yy - hy) / 3.0) ** 2), rgb('#ffffff'), 0.12)
        if glitter_x is not None:
            im, dr = self.layer()
            for _ in range(1400):
                t = self.rng.uniform(0, 1) ** 1.6
                y = hy + 6 + t * (H - hy) * 0.9
                spread = 30 + t * 520
                x = glitter_x * W + self.rng.normal(0, spread * 0.45)
                ln = self.rng.uniform(6, 26) * (1 + t * 2)
                a = int(220 * (1 - t) ** 1.2 * self.rng.uniform(0.3, 1))
                c = tuple(int(v * 255) for v in rgb(glitter_color)) + (a,)
                dr.line([x - ln, y, x + ln, y], fill=c, width=2)
            self.composite(im, blur=1.0)

    def grass(self, base_top, count, colors, height=(40, 120), lean=18, y_spread=None):
        """Grass blades rising from base_top (array or scalar, in px) toward the bottom."""
        im, dr = self.layer()
        for _ in range(count):
            x = self.rng.uniform(-10, W + 10)
            bt = base_top[int(np.clip(x, 0, W - 1))] if isinstance(base_top, np.ndarray) else base_top
            y = self.rng.uniform(bt + 10, H + 40) if y_spread is None else self.rng.uniform(bt + 10, bt + y_spread)
            depth = (y - bt) / max(1, H - bt)
            hgt = self.rng.uniform(*height) * (0.5 + depth)
            lx = self.rng.uniform(-lean, lean) * (0.5 + depth)
            c = colors[self.rng.integers(len(colors))]
            col = tuple(int(v * 255) for v in rgb(c)) + (int(255 * self.rng.uniform(0.55, 0.95)),)
            dr.line([x, y, x + lx * 0.5, y - hgt * 0.55, x + lx, y - hgt], fill=col, width=max(1, int(1 + depth * 3)))
        self.composite(im, blur=0.7)

    def flowers(self, base_top, count, colors, size=(3, 9)):
        im, dr = self.layer()
        for _ in range(count):
            x = self.rng.uniform(0, W)
            bt = base_top[int(np.clip(x, 0, W - 1))] if isinstance(base_top, np.ndarray) else base_top
            y = self.rng.uniform(bt + 20, H)
            depth = (y - bt) / max(1, H - bt)
            r = self.rng.uniform(*size) * (0.4 + depth * 1.4)
            c = colors[self.rng.integers(len(colors))]
            col = tuple(int(v * 255) for v in rgb(c)) + (int(255 * self.rng.uniform(0.7, 1)),)
            dr.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=col)
        self.composite(im, blur=0.8)

    def pines(self, base_top, count, color, height=(80, 220), x_range=(0, 1), y_jitter=30):
        im, dr = self.layer()
        col = tuple(int(v * 255) for v in rgb(color)) + (255,)
        for _ in range(count):
            x = self.rng.uniform(*x_range) * W
            bt = base_top[int(np.clip(x, 0, W - 1))] if isinstance(base_top, np.ndarray) else base_top
            y = bt + self.rng.uniform(4, y_jitter)
            h = self.rng.uniform(*height)
            draw_pine(dr, x, y, h, col)
        self.composite(im, blur=0.8)

    def vignette(self, strength=0.35):
        d = np.sqrt(((self.xx / W - 0.5) * 1.3) ** 2 + ((self.yy / H - 0.5) * 1.0) ** 2)
        self.img *= (1 - strength * smoothstep(0.35, 0.95, d))[..., None]

    def finish(self, path, grain=0.008, quality=85):
        self.img += self.rng.normal(0, grain, (H, W, 1)).astype(np.float32)
        out = (np.clip(self.img, 0, 1) * 255 + 0.5).astype(np.uint8)
        im = Image.fromarray(out, 'RGB')
        im.save(path, 'JPEG', quality=quality, optimize=True, progressive=True, subsampling=0)
        return im


# ---------- silhouette drawing helpers (operate on ImageDraw) ----------

def col_of(hexc, a=255):
    return tuple(int(v * 255) for v in rgb(hexc)) + (a,)


def draw_pine(dr, x, y, h, col):
    tiers = 4
    dr.rectangle([x - h * 0.03, y - h * 0.15, x + h * 0.03, y], fill=col)
    for i in range(tiers):
        tb = y - h * 0.12 - i * h * 0.2
        tw = h * (0.32 - i * 0.06)
        dr.polygon([(x - tw, tb), (x + tw, tb), (x, tb - h * 0.38)], fill=col)


def draw_round_tree(dr, x, y, h, col, rng):
    dr.polygon([(x - h * 0.04, y), (x + h * 0.04, y), (x + h * 0.02, y - h * 0.5), (x - h * 0.02, y - h * 0.5)], fill=col)
    for _ in range(14):
        cx = x + rng.uniform(-0.28, 0.28) * h
        cy = y - h * 0.62 + rng.uniform(-0.22, 0.2) * h
        r = h * rng.uniform(0.14, 0.24)
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)


def draw_person(dr, x, y, h, col, robe=True, staff=False, hair=False, arms_up=False, stride=0.0):
    """A figure seen from behind / in silhouette, feet at (x, y), height h."""
    head_r = h * 0.068
    hy = y - h + head_r
    dr.ellipse([x - head_r, hy - head_r, x + head_r, hy + head_r * 1.05], fill=col)
    if hair:
        dr.polygon([(x - head_r * 1.05, hy), (x + head_r * 1.05, hy), (x + head_r * 1.2, hy + head_r * 2.4), (x - head_r * 1.2, hy + head_r * 2.4)], fill=col)
    sh_y = hy + head_r * 1.9
    sh_w = h * 0.125
    dr.polygon([(x - head_r * 0.45, hy + head_r), (x + head_r * 0.45, hy + head_r), (x + head_r * 0.5, sh_y), (x - head_r * 0.5, sh_y)], fill=col)
    if robe:
        hem_w = h * 0.17
        dr.polygon([(x - sh_w, sh_y + h * 0.02), (x - sh_w * 0.8, sh_y - h * 0.015), (x + sh_w * 0.8, sh_y - h * 0.015), (x + sh_w, sh_y + h * 0.02),
                    (x + hem_w + stride * h * 0.05, y - h * 0.03), (x - hem_w + stride * h * 0.05, y - h * 0.03)], fill=col)
        dr.polygon([(x - h * 0.07, y - h * 0.05), (x - h * 0.03 - stride * h * 0.06, y), (x - h * 0.08 - stride * h * 0.06, y)], fill=col)
        dr.polygon([(x + h * 0.03, y - h * 0.05), (x + h * 0.08 + stride * h * 0.06, y), (x + h * 0.03 + stride * h * 0.06, y)], fill=col)
    else:
        dr.polygon([(x - sh_w, sh_y), (x + sh_w, sh_y), (x + sh_w * 0.75, y - h * 0.47), (x - sh_w * 0.75, y - h * 0.47)], fill=col)
        lw = h * 0.045
        dr.polygon([(x - sh_w * 0.72, y - h * 0.48), (x - sh_w * 0.05, y - h * 0.48), (x - lw * 0.4 - stride * h * 0.1, y), (x - lw * 1.6 - stride * h * 0.1, y)], fill=col)
        dr.polygon([(x + sh_w * 0.05, y - h * 0.48), (x + sh_w * 0.72, y - h * 0.48), (x + lw * 1.6 + stride * h * 0.12, y), (x + lw * 0.4 + stride * h * 0.12, y)], fill=col)
    aw = h * 0.035
    if arms_up:
        for s in (-1, 1):
            dr.polygon([(x + s * sh_w * 0.7, sh_y + aw), (x + s * sh_w * 0.95, sh_y - aw * 0.2), (x + s * h * 0.26, sh_y - h * 0.3), (x + s * h * 0.21, sh_y - h * 0.32)], fill=col)
    else:
        for s in (-1, 1):
            dr.polygon([(x + s * sh_w * 0.75, sh_y), (x + s * (sh_w + aw * 0.6), sh_y + aw), (x + s * (sh_w + aw * 0.2), y - h * 0.5), (x + s * (sh_w - aw * 0.9), y - h * 0.5)], fill=col)
    if staff:
        sx = x + sh_w + aw * 0.6
        top = y - h * 1.12
        dr.line([sx, y + h * 0.01, sx, top], fill=col, width=max(2, int(h * 0.018)))
        r = h * 0.07
        dr.arc([sx - 2 * r, top - r, sx, top + r], 180, 360, fill=col, width=max(2, int(h * 0.018)))


def draw_sheep(dr, x, y, s, body, head, facing=1):
    """Sheep standing at feet (x, y), body length s."""
    leg_h = s * 0.32
    for lx in (-0.3, -0.18, 0.18, 0.3):
        dr.rectangle([x + lx * s - s * 0.025, y - leg_h, x + lx * s + s * 0.025, y], fill=head)
    by = y - leg_h - s * 0.2
    dr.ellipse([x - s * 0.5, by - s * 0.27, x + s * 0.5, by + s * 0.25], fill=body)
    for i in range(7):
        cx = x - s * 0.4 + i * s * 0.13
        dr.ellipse([cx - s * 0.12, by - s * 0.33, cx + s * 0.12, by - s * 0.1], fill=body)
    hx = x + facing * s * 0.56
    dr.ellipse([hx - s * 0.13, by - s * 0.3, hx + s * 0.13, by + s * 0.02], fill=head)
    dr.ellipse([hx - s * 0.06 - facing * s * 0.1, by - s * 0.3, hx + s * 0.06 - facing * s * 0.1, by - s * 0.22], fill=head)


def draw_cross(dr, x, y, h, col):
    """Cross standing with its foot at (x, y)."""
    w = h * 0.07
    dr.rectangle([x - w / 2, y - h, x + w / 2, y], fill=col)
    bar_y = y - h * 0.72
    dr.rectangle([x - h * 0.3, bar_y - w / 2, x + h * 0.3, bar_y + w / 2], fill=col)


def draw_bird(dr, x, y, s, col, width=3):
    dr.arc([x - s, y - s * 0.5, x, y + s * 0.5], 200, 330, fill=col, width=width)
    dr.arc([x, y - s * 0.5, x + s, y + s * 0.5], 210, 340, fill=col, width=width)


def bezier(p0, p1, p2, p3, n=40):
    pts = []
    for i in range(n + 1):
        t = i / n
        a = (1 - t) ** 3
        b = 3 * (1 - t) ** 2 * t
        c = 3 * (1 - t) * t ** 2
        d = t ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return pts


def draw_dove(dr, x, y, s, col):
    """A dove in flight, wings raised, centred on (x, y), wingspan ~2s."""
    body = bezier((x - s * 0.55, y + s * 0.05), (x - s * 0.2, y - s * 0.12), (x + s * 0.3, y - s * 0.1), (x + s * 0.62, y - s * 0.02)) + \
        bezier((x + s * 0.62, y - s * 0.02), (x + s * 0.3, y + s * 0.18), (x - s * 0.2, y + s * 0.2), (x - s * 0.55, y + s * 0.05))
    dr.polygon(body, fill=col)
    dr.ellipse([x + s * 0.5, y - s * 0.13, x + s * 0.72, y + s * 0.06], fill=col)
    dr.polygon([(x + s * 0.72, y - s * 0.05), (x + s * 0.82, y - s * 0.02), (x + s * 0.71, y + s * 0.01)], fill=col)
    tail = [(x - s * 0.5, y + s * 0.02), (x - s * 0.95, y - s * 0.08), (x - s * 0.98, y + s * 0.12), (x - s * 0.5, y + s * 0.12)]
    dr.polygon(tail, fill=col)
    for sgn, lift in ((1, 1.0), (-1, 0.75)):
        wing = bezier((x - s * 0.15, y - s * 0.05), (x - s * 0.35, y - s * 0.6 * lift), (x - s * 0.6 * sgn * 0 - s * 0.1, y - s * 1.0 * lift), (x - s * 0.55, y - s * 1.15 * lift)) + \
            bezier((x - s * 0.55, y - s * 1.15 * lift), (x - s * 0.1, y - s * 0.95 * lift), (x + s * 0.25, y - s * 0.55 * lift), (x + s * 0.2, y - s * 0.05))
        dr.polygon(wing, fill=col)


def draw_church(dr, x, y, h, col, window=None):
    """Small church with steeple, foot of the nave at (x, y), overall height h."""
    nave_w, nave_h = h * 0.55, h * 0.3
    dr.rectangle([x - nave_w * 0.1, y - nave_h, x + nave_w, y], fill=col)
    dr.polygon([(x - nave_w * 0.14, y - nave_h), (x + nave_w * 1.04, y - nave_h), (x + nave_w * 0.45, y - nave_h - h * 0.17)], fill=col)
    tw = h * 0.16
    tx = x - nave_w * 0.1 - tw
    dr.rectangle([tx, y - h * 0.55, tx + tw, y], fill=col)
    dr.polygon([(tx - tw * 0.08, y - h * 0.55), (tx + tw * 1.08, y - h * 0.55), (tx + tw / 2, y - h * 0.86)], fill=col)
    cxm = tx + tw / 2
    dr.rectangle([cxm - h * 0.008, y - h, cxm + h * 0.008, y - h * 0.85], fill=col)
    dr.rectangle([cxm - h * 0.04, y - h * 0.955, cxm + h * 0.04, y - h * 0.94], fill=col)
    if window:
        for i in range(3):
            wx = x + nave_w * (0.15 + i * 0.28)
            dr.rounded_rectangle([wx, y - nave_h * 0.75, wx + nave_w * 0.1, y - nave_h * 0.35], radius=h * 0.02, fill=window)
        dr.rounded_rectangle([tx + tw * 0.3, y - h * 0.42, tx + tw * 0.7, y - h * 0.3], radius=h * 0.02, fill=window)


def draw_house(dr, x, y, h, col, window):
    w = h * 1.1
    dr.rectangle([x - w / 2, y - h * 0.55, x + w / 2, y], fill=col)
    dr.polygon([(x - w * 0.6, y - h * 0.55), (x + w * 0.6, y - h * 0.55), (x, y - h)], fill=col)
    dr.rectangle([x + w * 0.22, y - h * 0.95, x + w * 0.34, y - h * 0.7], fill=col)
    for wx in (-0.3, 0.12):
        dr.rectangle([x + wx * w, y - h * 0.4, x + (wx + 0.16) * w, y - h * 0.2], fill=window)


def draw_open_book(dr, x, y, s, page, edge):
    """Open Bible seen from the front, spine bottom at (x, y), width 2s."""
    for sgn in (-1, 1):
        top = bezier((x, y - s * 0.62), (x + sgn * s * 0.3, y - s * 0.78), (x + sgn * s * 0.7, y - s * 0.72), (x + sgn * s, y - s * 0.66))
        bottom = bezier((x + sgn * s, y - s * 0.04), (x + sgn * s * 0.7, y - s * 0.1), (x + sgn * s * 0.3, y - s * 0.12), (x, y))
        dr.polygon(top + bottom, fill=page)
        for i in range(1, 9):
            f = i / 9
            ln = bezier((x + sgn * s * 0.12, y - s * 0.62 * (1 - f) - s * 0.06 * f - s * 0.06),
                        (x + sgn * s * 0.4, y - s * 0.72 * (1 - f) - s * 0.1 * f - s * 0.06),
                        (x + sgn * s * 0.7, y - s * 0.68 * (1 - f) - s * 0.08 * f - s * 0.06),
                        (x + sgn * s * 0.88, y - s * 0.62 * (1 - f) - s * 0.04 * f - s * 0.06), 20)
            dr.line(ln, fill=edge, width=max(1, int(s * 0.006)))
    dr.polygon([(x - s * 1.03, y - s * 0.02), (x + s * 1.03, y - s * 0.02), (x + s * 1.0, y + s * 0.05), (x, y + s * 0.07), (x - s * 1.0, y + s * 0.05)], fill=edge)
