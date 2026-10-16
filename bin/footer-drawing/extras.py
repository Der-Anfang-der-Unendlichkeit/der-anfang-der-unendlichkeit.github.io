"""Signs of people: the night lights of the Americas on the Earth in the sky,
settlements on the Moon the man stands on, and a rocket climbing from it.

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
import america

FIGURE = (1640, 380)  # the man and his rock lie right of and below this
# Where the planet's light comes from: the right, and from behind it, so it
# shows a crescent. tone.fx shades it with the same vector.
LIGHT = (.88, .22, -.42)


def limb_y(x):
    cx, cy, r = LIMB
    return cy - math.sqrt(r * r - (x - cx) ** 2)


# --- Night lights -------------------------------------------------------------
# As in photos of the Earth at night: a web of faint lights along roads, with
# brighter cities at its nodes. The planet in the sky is the Earth, showing
# North America; the ground the man stands on is the Moon, settled too.

def moon_lights(rnd, w, h, seed, cities):
    """Settlements on the Moon as (u, v, brightness, core) on a w by h map:
    towns clustered in settled regions, mostly small, a few big, joined by roads.
    No seas, so no lit coasts."""
    octaves = [(Noise(seed + k, 300 / 2 ** k), .5 ** k) for k in range(3)]

    def settled(u, v):
        return max(0, min(1, sum(n(u, v) * a for n, a in octaves) * 1.4 + .35))

    towns = []
    while len(towns) < cities:
        u, v = rnd.uniform(0, w), rnd.uniform(0, h)
        if rnd.random() < settled(u, v) ** 2:
            towns.append((u, v, 1.5 + 12 * rnd.random() ** 5))
    out = []
    for u, v, size in towns:
        for k in range(int(3 + size * size * .3)):
            d = abs(rnd.gauss(0, size * .45))
            a = rnd.uniform(0, 2 * math.pi)
            out.append((u + math.cos(a) * d, v + math.sin(a) * d,
                        min(1, .3 + size / 16) * math.exp(-d / size), size > 7 and d < size * .25))
    for u, v, size in towns:
        near = sorted(towns, key=lambda t: (t[0] - u) ** 2 + (t[1] - v) ** 2)[1:3]
        for tu, tv, _ in near:
            L = math.hypot(tu - u, tv - v)
            if L > 70:
                continue
            bend = rnd.uniform(-.25, .25)
            for k in range(int(L / 4)):
                t = k / max(1, L / 4)
                if rnd.random() < .5:
                    w_ = bend * math.sin(t * math.pi)
                    out.append((u + (tu - u) * t - (tv - v) * w_ + rnd.gauss(0, 1.5),
                                v + (tv - v) * t + (tu - u) * w_ + rnd.gauss(0, 1.5), rnd.uniform(.14, .28), False))
    for _ in range(9000):
        u, v = rnd.uniform(0, w), rnd.uniform(0, h)
        if rnd.random() < settled(u, v) ** 3 * .6:
            out.append((u, v, rnd.uniform(.1, .22), False))
    return out


def draw_lights(f, glow, rnd, lights, project, size=1, halo=0):
    """`size` scales the lights; `halo` adds glow around the brighter ones too."""
    for u, v, b, core in lights:
        p = project(u, v)
        if p is None:
            continue
        x, y, fade = p
        b *= fade
        if b < .06:
            continue
        r = ((1.1 + .5 * b) if core else (.9 + .5 * b)) * size
        f.write(f'fill-opacity {min(1, .5 + .8 * b):.2f}\ncircle {x:.1f},{y:.1f} {x + r:.1f},{y:.1f}\n')
        if core or b > 1 - halo:
            glow.write(f'fill-opacity {(.03 + .05 * b) * (1 + 2 * halo):.2f}\ncircle {x:.1f},{y:.1f} {x + 6 * size:.1f},{y:.1f}\n')


GROUND_DEPTH = 700  # map units from the bottom of the picture to the horizon


def moon_project(u, v):
    """Map u runs along the picture, v from the bottom edge to the horizon,
    crowding together toward the horizon as the ground recedes."""
    x = u
    top = limb_y(x) + 6
    if top >= H:
        return None
    t = v / GROUND_DEPTH
    if not 0 <= t < 1:
        return None
    y = top + (H - top) * (1 - t) ** 1.7
    if x > FIGURE[0] and y > FIGURE[1]:
        return None
    return x, y, min(1, (y - top) / 25) * (1 - .4 * t)


# The planet is the Earth, seen from the Moon, turned so that the Americas are
# on its night side
VIEW_LAT, VIEW_LON = math.radians(12), math.radians(-72)


def inside(lat, lon, poly):
    hit = False
    for (a1, o1), (a2, o2) in zip(poly, poly[1:] + poly[:1]):
        if (a1 > lat) != (a2 > lat) and lon < o1 + (lat - a1) * (o2 - o1) / (a2 - a1):
            hit = not hit
    return hit


def on_land(lat, lon):
    return any(inside(lat, lon, p) for p in america.LAND) and not any(inside(lat, lon, p) for p in america.GREAT_LAKES)


def america_lights(rnd):
    """Night lights of the Americas as (lat, lon, brightness, core): cities by
    population, the roads between them, towns and coasts lit most where people
    are most."""
    cities = america.CITIES

    def crowding(lat, lon):
        return sum(pop / (1 + ((lat - a) ** 2 + ((lon - o) * math.cos(math.radians(lat))) ** 2) / 9)
                   for a, o, pop in cities) / 12

    out = []
    for lat, lon, pop in cities:
        size = .12 * math.sqrt(pop) + .05
        for k in range(int(5 + 8 * pop ** .8)):
            d = abs(rnd.gauss(0, size))
            a = rnd.uniform(0, 2 * math.pi)
            pa, po = lat + math.sin(a) * d, lon + math.cos(a) * d / math.cos(math.radians(lat))
            if on_land(pa, po):
                out.append((pa, po, min(1, .45 + pop / 12) * math.exp(-d / (size * 1.5)), d < size * .5))
    # Highways to the nearest cities
    for lat, lon, pop in cities:
        near = sorted(cities, key=lambda c: (c[0] - lat) ** 2 + (c[1] - lon) ** 2)[1:4]
        for a, o, _ in near:
            L = math.hypot(a - lat, o - lon)
            if L > 9:
                continue
            for k in range(int(L / .25)):
                t = k / (L / .25)
                pa = lat + (a - lat) * t + rnd.gauss(0, .05)
                po = lon + (o - lon) * t + rnd.gauss(0, .05)
                if on_land(pa, po) and rnd.random() < .3:
                    out.append((pa, po, rnd.uniform(.1, .22), False))
    # Towns everywhere, densest near the cities; lit coasts where people live
    for _ in range(30000):
        lat, lon = rnd.uniform(-56, 60), rnd.uniform(-130, -34)
        if not on_land(lat, lon):
            continue
        c = crowding(lat, lon)
        if rnd.random() < .015 + .35 * min(1, c):
            out.append((lat, lon, rnd.uniform(.12, .26) + min(.25, c * .3), False))
    for poly in america.LAND + america.GREAT_LAKES:
        for (a1, o1), (a2, o2) in zip(poly, poly[1:] + poly[:1]):
            n = int(math.hypot(a2 - a1, o2 - o1) / .2)
            for k in range(n):
                t = k / max(1, n)
                lat, lon = a1 + (a2 - a1) * t + rnd.gauss(0, .06), o1 + (o2 - o1) * t + rnd.gauss(0, .06)
                c = crowding(lat, lon)
                if lat < 58 and on_land(lat, lon) and rnd.random() < .05 + min(.6, c):
                    out.append((lat, lon, rnd.uniform(.18, .3) + min(.3, c * .4), False))
    return out


def earth_project(lat, lon):
    """Puts a place on the Earth (in degrees) onto the planet in the picture,
    keeping to its visible night side."""
    cx, cy, r = RING
    la, lo = math.radians(lat), math.radians(lon) - VIEW_LON
    x = math.cos(la) * math.sin(lo)
    y = -(math.cos(VIEW_LAT) * math.sin(la) - math.sin(VIEW_LAT) * math.cos(la) * math.cos(lo))
    z = math.sin(VIEW_LAT) * math.sin(la) + math.cos(VIEW_LAT) * math.cos(la) * math.cos(lo)
    if z <= .05:
        return None
    if x * LIGHT[0] + y * LIGHT[1] + z * LIGHT[2] > -.02:
        return None  # daylight
    px, py = cx + r * x, cy + r * y
    if math.hypot(px - cx, py - cy) > r - 5 or py > limb_y(px) - 4:
        return None
    return px, py, min(1, z * 2.5)  # dimmer toward the rim, through more air


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
        draw_lights(f, glow, rnd, moon_lights(rnd, 1650, GROUND_DEPTH, 300, 420), moon_project,
                    size=1.5, halo=.75)  # brighter than the Earth's: much closer, on paler ground
        draw_lights(f, glow, rnd, america_lights(rnd), earth_project)
    rocket(out, rnd)


if __name__ == '__main__':
    main(sys.argv[1])
