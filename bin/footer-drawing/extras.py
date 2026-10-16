"""Signs of people: night lights on the Earth and on the planet's night side,
and a rocket climbing from the Earth.

Writes, as MVG for ImageMagick:
  lights.mvg       night lights (eraser marks, white on black)
  lights-glow.mvg  the brighter lights' glow, to be blurred
  rocket.mvg       the rocket's lit body, flame, plume and trail (eraser marks)
  rocket-glow.mvg  their haze, to be blurred
  rocket-ink.mvg   the rocket's outline and shading (pencil, white on black = graphite)
"""
import math, random, sys
from erase import RING, LIMB
from strokes import W, H, Noise

FIGURE = (1640, 380)  # the man and his rock lie right of and below this
# Where the planet's light comes from: the right, and from behind it, so it
# shows a crescent. tone.fx shades it with the same vector.
LIGHT = (.88, .22, -.42)


def limb_y(x):
    cx, cy, r = LIMB
    return cy - math.sqrt(r * r - (x - cx) ** 2)


# --- Night lights -------------------------------------------------------------
# As in photos of the Earth at night: continents traced by lit coastlines, the
# land covered in a web of faint lights along roads, bright cities at its nodes.
# Generated on a flat map, then projected onto the Earth or the planet.

def lights_map(rnd, w, h, seed, cities, specks):
    """Returns lights as (u, v, brightness, core) on a w by h map."""
    octaves = [(Noise(seed + k, 300 / 2 ** k), .5 ** k) for k in range(4)]

    def height(u, v):
        return sum(n(u, v) * a for n, a in octaves)

    def land(u, v):
        return height(u, v) > -.05

    def coastal(u, v):
        return math.exp(-((height(u, v) + .05) / .07) ** 2)

    out = []
    # Cities, more of them along the coasts, mostly small, a few big
    towns = []
    while len(towns) < cities:
        u, v = rnd.uniform(0, w), rnd.uniform(0, h)
        if land(u, v) and rnd.random() < .2 + .8 * coastal(u, v):
            towns.append((u, v, 1.5 + 14 * rnd.random() ** 5))
    for u, v, size in towns:
        for k in range(int(2 + size * size * .3)):
            d = abs(rnd.gauss(0, size * .45))
            a = rnd.uniform(0, 2 * math.pi)
            pu, pv = u + math.cos(a) * d, v + math.sin(a) * d
            if land(pu, pv):
                out.append((pu, pv, min(1, .3 + size / 18) * math.exp(-d / size), size > 7 and d < size * .25))
    # Roads to the nearest towns, lit by the villages along them
    for i, (u, v, size) in enumerate(towns):
        near = sorted(towns, key=lambda t: (t[0] - u) ** 2 + (t[1] - v) ** 2)[1:4]
        for tu, tv, _ in near:
            L = math.hypot(tu - u, tv - v)
            if L > 95:
                continue
            bend = rnd.uniform(-.2, .2)
            for k in range(int(L / 4)):
                t = k / max(1, L / 4)
                pu = u + (tu - u) * t - (tv - v) * bend * math.sin(t * math.pi)
                pv = v + (tv - v) * t + (tu - u) * bend * math.sin(t * math.pi)
                pu += rnd.gauss(0, 1.5); pv += rnd.gauss(0, 1.5)
                if land(pu, pv) and rnd.random() < .6:
                    out.append((pu, pv, rnd.uniform(.18, .34), False))
    # Coasts, lit almost everywhere
    for _ in range(specks):
        u, v = rnd.uniform(0, w), rnd.uniform(0, h)
        if not land(u, v):
            continue
        c = coastal(u, v)
        if rnd.random() < .12 + .88 * c:
            out.append((u, v, rnd.uniform(.12, .26) + .4 * c, False))
    return out


def draw_lights(f, glow, rnd, lights, project):
    for u, v, b, core in lights:
        p = project(u, v)
        if p is None:
            continue
        x, y, fade = p
        b *= fade
        if b < .06:
            continue
        r = (1.1 + .5 * b) if core else (.9 + .5 * b)
        f.write(f'fill-opacity {min(1, .5 + .8 * b):.2f}\ncircle {x:.1f},{y:.1f} {x + r:.1f},{y:.1f}\n')
        if core:
            glow.write(f'fill-opacity {.03 + .05 * b:.2f}\ncircle {x:.1f},{y:.1f} {x + 6:.1f},{y:.1f}\n')


EARTH_DEPTH = 700  # map units from the bottom of the picture to the horizon


def earth_project(u, v):
    """Map u runs along the picture, v from the bottom edge to the horizon,
    crowding together toward the horizon as the ground recedes."""
    x = u
    top = limb_y(x) + 6
    if top >= H:
        return None
    t = v / EARTH_DEPTH
    if not 0 <= t < 1:
        return None
    y = top + (H - top) * (1 - t) ** 1.7
    if x > FIGURE[0] and y > FIGURE[1]:
        return None
    return x, y, min(1, (y - top) / 25) * (1 - .4 * t)


def planet_normal(lat, lon):
    return math.cos(lat) * math.sin(lon), -math.sin(lat), math.cos(lat) * math.cos(lon)


def planet_project(u, v):
    """Map units are the planet's radius times longitude and latitude."""
    cx, cy, r = RING
    lat, lon = v / r - 1.5, u / r - 1.6
    n = planet_normal(lat, lon)
    if n[2] <= .05:
        return None
    d = sum(a * b for a, b in zip(n, LIGHT))
    if d > -.02:
        return None  # daylight
    x, y = cx + r * n[0], cy + r * n[1]
    if math.hypot(x - cx, y - cy) > r - 5 or y > limb_y(x) - 4:
        return None
    return x, y, min(1, n[2] * 2.5)  # dimmer toward the rim, through more air


# --- Rocket -------------------------------------------------------------------

def bezier(p0, p1, p2, t):
    return tuple((1 - t) ** 2 * a + 2 * (1 - t) * t * b + t * t * c for a, b, c in zip(p0, p1, p2))


# The vehicle, nose along +x, engine exit at the origin: a slender two-stage
# rocket with a pointed fairing, small fins and an engine bell
BODY = "M 4 -3.6 L 58 -3.6 C 66 -3.4, 72 -1.6, 77 0 C 72 1.6, 66 3.4, 58 3.6 L 4 3.6 Z"
BELL = "M 0 -3 L 4 -2.3 L 4 2.3 L 0 3 Z"
FINS = ("M 4 -3.6 L 13 -3.6 L 6 -7.5 L 3 -7.5 Z", "M 4 3.6 L 13 3.6 L 6 7.5 L 3 7.5 Z")


def rocket(out, rnd):
    """A rocket climbing from the far left of the horizon, pitching over toward
    the planet: its trail, the plume fanning out behind it in thin air, and the
    vehicle, lit from the right."""
    p0 = (40, limb_y(40) - 2)
    p1 = (60, 660)
    p2 = (240, 440)
    ux, uy = p2[0] - p1[0], p2[1] - p1[1]
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    ang = math.degrees(math.atan2(uy, ux))
    pts = [bezier(p0, p1, p2, k / 160) for k in range(161)]
    head = p2  # the engine
    local = f'push graphic-context\ntranslate {head[0]:.1f},{head[1]:.1f}\nrotate {ang:.1f}\nscale 1.6,1.6\n'

    def fan(f, length, half, rays, width, opacity, edge):
        """Lines from the engine, fanning backwards; brighter along the edges."""
        for k in range(rays):
            t = k / (rays - 1)
            a = math.radians(ang + 180 + (t * 2 - 1) * half)
            L = length * rnd.uniform(.85, 1) * (1 - .25 * abs(t * 2 - 1))
            o = opacity * (edge if t in (0, 1) else 1)
            f.write(f'stroke-width {width}\nstroke-opacity {o:.2f}\n'
                    f'line {head[0]:.1f},{head[1]:.1f} {head[0] + math.cos(a) * L:.1f},{head[1] + math.sin(a) * L:.1f}\n')

    with open(f'{out}/rocket.mvg', 'w') as f:
        f.write(f'viewbox 0 0 {W} {H}\nfill none\nstroke white\nstroke-linecap round\n')
        # the trail: barely there near the ground, firmer as it climbs
        for k in range(0, 150, 2):
            t = k / 150
            seg = pts[k:k + 3]
            f.write(f'stroke-width {1 + 2.4 * t:.2f}\nstroke-opacity {.2 + .7 * t:.2f}\n'
                    'path \'M ' + ' L '.join(f'{x:.1f} {y:.1f}' for x, y in seg) + "'\n")
        fan(f, 130, 20, 19, 1, .3, 2.6)
        f.write(local + 'stroke none\nfill white\n')
        # flame
        f.write('fill-opacity 1\nellipse -7,0 8,2.4 0,360\nfill-opacity .6\nellipse -14,0 14,4 0,360\n')
        # the body, pale, and brighter on its sunlit side (local +y faces right)
        f.write(f'fill-opacity .55\npath \'{BODY}\'\npath \'{BELL}\'\n')
        for fin in FINS:
            f.write(f'path \'{fin}\'\n')
        f.write('fill-opacity .9\npath \'M 6 .6 L 58 .6 L 58 3.4 L 6 3.4 Z\'\npath \'M 58 .6 L 58 3.4 C 66 3.2, 72 1.5, 77 0 Z\'\n')
        f.write('pop graphic-context\n')

    with open(f'{out}/rocket-glow.mvg', 'w') as f:
        f.write(f'viewbox 0 0 {W} {H}\nfill none\nstroke white\nstroke-linecap round\n')
        for k in range(0, 150, 4):
            t = k / 150
            seg = pts[k:k + 5]
            f.write(f'stroke-width {5 + 12 * t:.1f}\nstroke-opacity {.08 + .22 * t:.2f}\n'
                    'path \'M ' + ' L '.join(f'{x:.1f} {y:.1f}' for x, y in seg) + "'\n")
        fan(f, 140, 22, 30, 6, .32, 1)
        f.write(f'stroke none\nfill white\nfill-opacity .9\ncircle {head[0]:.1f},{head[1]:.1f} {head[0] + 14:.1f},{head[1]:.1f}\n')

    with open(f'{out}/rocket-ink.mvg', 'w') as f:
        f.write(f'viewbox 0 0 {W} {H}\nfill none\nstroke white\nstroke-linecap round\nstroke-linejoin round\n' + local)
        f.write(f'stroke-width 1\nstroke-opacity .85\npath \'{BODY}\'\npath \'{BELL}\'\n')
        for fin in FINS:
            f.write(f'path \'{fin}\'\n')
        # interstage and fairing joints
        f.write('stroke-width .8\nstroke-opacity .6\nline 30,-3.6 30,3.6\nline 46,-3.6 46,3.6\nline 58,-3.6 58,3.6\n')
        # shading along the side away from the light
        f.write('stroke-width .7\nstroke-opacity .55\nline 6,-2.6 57,-2.6\nline 6,-1.6 56,-1.6\nline 59,-2.3 70,-1.1\n')
        f.write('pop graphic-context\n')


def main(out):
    rnd = random.Random(2021)
    with open(f'{out}/lights.mvg', 'w') as f, open(f'{out}/lights-glow.mvg', 'w') as glow:
        for g in (f, glow):
            g.write(f'viewbox 0 0 {W} {H}\nstroke none\nfill white\n')
        draw_lights(f, glow, rnd, lights_map(rnd, 1650, EARTH_DEPTH, 300, 650, 40000), earth_project)
        draw_lights(f, glow, rnd, lights_map(rnd, 1090, 1020, 400, 420, 26000), planet_project)
    rocket(out, rnd)


if __name__ == '__main__':
    main(sys.argv[1])
