"""Eraser marks (white on black): background stars, the ring.

Writes stars.mvg (dots), glints.mvg (rays of the brighter stars) and ring.mvg.
"""
import math, random, sys
from strokes import W, H, Noise

RING = (680, 540, 340)
LIMB = (1150, 3680, 2850)


def sky_ok(x, y):
    cx, cy, r = LIMB
    if math.hypot(x - cx, y - cy) - r < 12:
        return False
    if 1640 < x < 2300 and y > 380:  # figure and rock
        return False
    return True


def main(out):
    rnd = random.Random(42)
    dots, glints = [], []
    n = 0
    while n < 1400:
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        md = abs(350 * (x - 300) + 1800 * (y - 360)) / 1833.7
        # denser along the Milky Way, sparser near the bright horizon
        p = .25 + .75 * math.exp(-(md / 210) ** 2)
        p *= min(1, 1.6 - (y - 80) / 700)
        if rnd.random() > p or not sky_ok(x, y):
            continue
        n += 1
        m = rnd.random() ** 3.2
        r = .55 + 2.2 * m
        dots.append((x, y, r, .45 + .55 * min(1, m * 3)))
        if m > .86:
            glints.append((x, y, r))
    with open(f'{out}/stars.mvg', 'w') as f:
        f.write(f'viewbox 0 0 {W} {H}\nstroke none\n')
        for x, y, r, o in dots:
            f.write(f'fill-opacity {o:.2f}\nfill white\ncircle {x:.1f},{y:.1f} {x + r:.1f},{y:.1f}\n')
    with open(f'{out}/glints.mvg', 'w') as f:
        f.write(f'viewbox 0 0 {W} {H}\nfill none\nstroke white\nstroke-linecap round\n')
        for x, y, r in glints:
            for ang, ln, w in ((0, 5, .8), (90, 5, .8), (45, 2, .5), (135, 2, .5)):
                a = math.radians(ang + rnd.uniform(-5, 5))
                L = ln * r * rnd.uniform(.8, 1.2)
                f.write(f'stroke-width {w:.2f}\nstroke-opacity .8\nline {x - math.cos(a) * L:.1f},{y - math.sin(a) * L:.1f} '
                        f'{x + math.cos(a) * L:.1f},{y + math.sin(a) * L:.1f}\n')
        # The bright star on the ring's upper left, as on the cover, is not drawn
        # here: the footer's SVG draws it at 427,312.5 so it can twinkle.
    # the ring: a firm pass and a fainter one beside it, both wobbling a little
    wob = Noise(5, 160)
    cx, cy, r = RING
    with open(f'{out}/ring.mvg', 'w') as f:
        f.write(f'viewbox 0 0 {W} {H}\nfill none\nstroke white\nstroke-linecap round\nstroke-linejoin round\n')
        shade = Noise(9, 90)
        for dr, w, o, a0, sweep in ((0, 2.6, .95, 200, 362), (3.5, 1.1, .5, 230, 330), (-2.5, .8, .35, 120, 200)):
            pts = []
            for k in range(0, 721):
                a = math.radians(a0 + sweep * k / 720)
                rr = r + dr + 1.6 * wob(math.cos(a) * 300 + 1000, math.sin(a) * 300 + 1000)
                pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
            # pressure varies along the line, so draw it in short overlapping pieces
            for k in range(0, 720, 6):
                seg = pts[k:k + 8]
                if len(seg) < 2:
                    break
                oo = o * max(.25, min(1, .8 + .5 * shade(k * 4, dr * 50)))
                f.write(f'stroke-width {w}\nstroke-opacity {oo:.2f}\npath \'M ' + ' L '.join(f'{x:.1f} {y:.1f}' for x, y in seg) + "'\n")


if __name__ == '__main__':
    main(sys.argv[1])
