"""Writes MVG files of pencil strokes for ImageMagick to draw.

Each stroke is a slightly curved quadratic path. Tapering is faked by drawing a
long faint pass and a shorter, darker pass over its middle.
"""
import math, random, sys

W, H = 2400, 1080


def head(f):
    f.write('viewbox 0 0 %d %d\nfill none\nstroke black\nstroke-linecap round\n' % (W, H))


def stroke(f, rnd, x0, y0, x1, y1, width, opacity, bow=0.04):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    b = rnd.uniform(-bow, bow)
    cx, cy = mx - dy * b, my + dx * b
    for frac, wmul, omul in ((1.0, .8, .55), (.7, 1.0, 1.0)):
        # shrink toward the middle for the darker pass
        s = (1 - frac) / 2
        ax, ay = x0 + dx * s, y0 + dy * s
        bx, by = x1 - dx * s, y1 - dy * s
        f.write('stroke-width %.2f\nstroke-opacity %.2f\npath \'M %.1f %.1f Q %.1f %.1f %.1f %.1f\'\n'
                % (width * wmul, min(1, opacity * omul), ax, ay, cx, cy, bx, by))


def arcs(path, cx, cy, r0, r1, gap, length, width, opacity, seed, a_range):
    """Strokes along concentric arcs (for the Earth, following its limb)."""
    rnd = random.Random(seed)
    with open(path, 'w') as f:
        head(f)
        r = r0
        while r > r1:
            a = a_range[0] + rnd.uniform(0, .01)
            while a < a_range[1]:
                L = rnd.uniform(*length)
                da = L / r
                rr = r + rnd.uniform(-gap * .3, gap * .3)
                p0 = (cx + rr * math.cos(a), cy + rr * math.sin(a))
                rr2 = rr + rnd.uniform(-1.5, 1.5)
                p1 = (cx + rr2 * math.cos(a + da), cy + rr2 * math.sin(a + da))
                if -20 < p0[0] < W + 20 and -20 < p0[1] < H + 20:
                    stroke(f, rnd, *p0, *p1, rnd.uniform(*width), rnd.uniform(*opacity), .02)
                a += da * rnd.uniform(1.0, 1.15)
            r -= gap * rnd.uniform(.85, 1.15)


class Noise:
    """Smooth 2D value noise in [-1, 1]."""
    def __init__(self, seed, cell):
        self.r = random.Random(seed); self.cell = cell; self.g = {}
    def v(self, ix, iy):
        if (ix, iy) not in self.g: self.g[ix, iy] = self.r.uniform(-1, 1)
        return self.g[ix, iy]
    def __call__(self, x, y):
        fx, fy = x / self.cell, y / self.cell
        ix, iy = math.floor(fx), math.floor(fy)
        tx, ty = fx - ix, fy - iy
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        a = self.v(ix, iy) + (self.v(ix + 1, iy) - self.v(ix, iy)) * tx
        b = self.v(ix, iy + 1) + (self.v(ix + 1, iy + 1) - self.v(ix, iy + 1)) * tx
        return a + (b - a) * ty


def patches(path, angle, gap, size, width, opacity, seed, box=(0, 0, W, H), swirl=14, accept=None):
    """Hand-style hatching: overlapping clusters of short parallel strokes whose
    direction drifts smoothly across the picture."""
    rnd = random.Random(seed)
    field = Noise(seed + 100, 380)
    x0, y0, x1, y1 = box
    step = size[0] * .78
    with open(path, 'w') as f:
        head(f)
        y = y0 - size[1] / 2
        row = 0
        while y < y1 + size[1] / 2:
            x = x0 - size[1] / 2 + (step / 2 if row % 2 else 0)
            while x < x1 + size[1] / 2:
                px, py = x + rnd.uniform(-step * .4, step * .4), y + rnd.uniform(-step * .4, step * .4)
                if accept is None or accept(px, py):
                    a = math.radians(angle + swirl * field(px, py) + rnd.uniform(-3, 3))
                    ux, uy = math.cos(a), math.sin(a)
                    nx, ny = -uy, ux
                    P = rnd.uniform(*size)
                    L = P * rnd.uniform(.8, 1.1)
                    n = max(2, int(P * rnd.uniform(.55, .9) / gap))
                    w0 = rnd.uniform(*width); o0 = (opacity[0] + opacity[1]) / 2 + rnd.uniform(-1, 1) * (opacity[1] - opacity[0]) / 4
                    for k in range(n):
                        off = (k - n / 2) * gap + rnd.uniform(-gap * .2, gap * .2)
                        lk = L * rnd.uniform(.85, 1.08)
                        st = rnd.uniform(-L * .08, L * .08) - lk / 2
                        sx, sy = px + nx * off + ux * st, py + ny * off + uy * st
                        stroke(f, rnd, sx, sy, sx + ux * lk, sy + uy * lk,
                               w0 * rnd.uniform(.85, 1.15), o0 * rnd.uniform(.8, 1.1), .05)
                x += step
            y += step
            row += 1


if __name__ == '__main__':
    out = sys.argv[1]
    sky = (0, 0, W, H)
    patches(f'{out}/sky1.mvg', -50, 6.5, (70, 120), (.8, 1.2), (.3, .55), 1, sky)
    patches(f'{out}/sky2.mvg', -38, 6.5, (60, 110), (.8, 1.2), (.3, .55), 2, sky)
    patches(f'{out}/sky3.mvg', 18, 6.2, (55, 100), (.7, 1.1), (.3, .55), 3, sky)
    patches(f'{out}/sky4.mvg', -4, 5.8, (50, 90), (.7, 1.1), (.3, .55), 4, sky)
    arcs(f'{out}/earth1.mvg', 1150, 3680, 2850, 2550, 6.5, (40, 120), (.7, 1.1), (.3, .6), 5, (math.radians(220), math.radians(320)))
    arcs(f'{out}/earth2.mvg', 1150, 3680, 2848, 2550, 6.5, (30, 90), (.7, 1.0), (.3, .6), 6, (math.radians(220), math.radians(320)))
    patches(f'{out}/earth3.mvg', -40, 6, (40, 80), (.7, 1.0), (.3, .55), 7, (0, 680, 2400, 1080))
    fb = (1600, 360, 2320, 1080)
    patches(f'{out}/fig1.mvg', 70, 3.4, (22, 40), (.6, .9), (.4, .7), 8, fb, 25)
    patches(f'{out}/fig2.mvg', -35, 3.4, (22, 40), (.6, .9), (.4, .7), 9, fb, 25)
    patches(f'{out}/fig3.mvg', 15, 3.2, (20, 36), (.6, .9), (.4, .7), 10, fb, 25)
    patches(f'{out}/fig4.mvg', -75, 3.2, (18, 32), (.6, .9), (.4, .7), 11, fb, 25)
