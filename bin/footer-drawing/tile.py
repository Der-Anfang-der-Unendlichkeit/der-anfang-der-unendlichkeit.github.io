"""Stroke and star files for a horizontally seamless strip of sky, T wide.

Everything is drawn three times, shifted by -T, 0 and +T, so whatever crosses
one edge comes back in at the other.
"""
import math, random, sys
import strokes

T, H = 1200, 1080


def wrap(src, dst):
    body = [l for l in open(src) if not l.startswith('viewbox')]
    with open(dst, 'w') as f:
        f.write(f'viewbox 0 0 {T} {H}\n')
        for dx in (-T, 0, T):
            f.write(f'push graphic-context\ntranslate {dx},0\n')
            f.writelines(body)
            f.write('pop graphic-context\n')


def stars(out):
    rnd = random.Random(99)
    with open(f'{out}/t_stars_raw.mvg', 'w') as f, open(f'{out}/t_glints_raw.mvg', 'w') as g:
        f.write('stroke none\n'); g.write('fill none\nstroke white\nstroke-linecap round\n')
        n = 0
        while n < 560:
            x, y = rnd.uniform(0, T), rnd.uniform(0, H)
            if rnd.random() > .3 * min(1, 1.6 - (y - 80) / 700) or y > 1000:
                continue
            n += 1
            m = rnd.random() ** 3.2
            r = .55 + 2.2 * m
            f.write(f'fill-opacity {.45 + .55 * min(1, m * 3):.2f}\nfill white\ncircle {x:.1f},{y:.1f} {x + r:.1f},{y:.1f}\n')
            if m > .86:
                for ang, ln, w in ((0, 5, .8), (90, 5, .8), (45, 2, .5), (135, 2, .5)):
                    a = math.radians(ang + rnd.uniform(-5, 5)); L = ln * r * rnd.uniform(.8, 1.2)
                    g.write(f'stroke-width {w}\nstroke-opacity .8\nline {x - math.cos(a) * L:.1f},{y - math.sin(a) * L:.1f} '
                            f'{x + math.cos(a) * L:.1f},{y + math.sin(a) * L:.1f}\n')
    wrap(f'{out}/t_stars_raw.mvg', f'{out}/t_stars.mvg')
    wrap(f'{out}/t_glints_raw.mvg', f'{out}/t_glints.mvg')


if __name__ == '__main__':
    out = sys.argv[1]
    strokes.W, strokes.H = T, H
    box = (0, 0, T, H)
    for name, args in (('sky1', (-50, 6.5, (70, 120), (.8, 1.2), (.3, .55), 21)),
                       ('sky2', (-38, 6.5, (60, 110), (.8, 1.2), (.3, .55), 22)),
                       ('sky3', (18, 6.2, (55, 100), (.7, 1.1), (.3, .55), 23)),
                       ('sky4', (-4, 5.8, (50, 90), (.7, 1.1), (.3, .55), 24))):
        a, gap, size, width, op, seed = args
        strokes.patches(f'{out}/t_{name}_raw.mvg', a, gap, size, width, op, seed, box, accept=lambda px, py: 0 <= px < T)
        wrap(f'{out}/t_{name}_raw.mvg', f'{out}/t_{name}.mvg')
    stars(out)
