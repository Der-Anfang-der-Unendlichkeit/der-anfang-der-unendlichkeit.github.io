"""Cuts the pointing man and his rock out of the banner.

Reads two masks of the banner's bottom-right corner, at twice its size (840x920):
one thresholded on the blue channel (the figure stands dark against the warm
glow) and one on brightness (the only one that catches his raised arm and
finger). Writes the figure as a PBM, 1 = figure.

usage: figure.py blue.pgm gray.pgm out.pbm
"""
import math, sys
from collections import deque


def read(path):
    d = open(path).read().split()
    w, h, mx = int(d[1]), int(d[2]), int(d[3])
    return w, h, [1 if int(v) > mx // 2 else 0 for v in d[4:]]


W, H, blue = read(sys.argv[1])
_, _, gray = read(sys.argv[2])

# The cover's ring passes behind his shoulder; erase it so it doesn't join the figure
CX, CY, R, HW = -674.6, -582.4, 1381.8, 17
ring = [abs(math.hypot(x - CX, y - CY) - R) <= HW for y in range(H) for x in range(W)]
m = [p and not a for p, a in zip(blue, ring)]
# ...and the title lettering near his hand
for y in range(H):
    for x in range(W):
        if (x < 300 and y < 300) or (x < 340 and y < 64):
            m[y * W + x] = 0


def fill(mask, seeds, ymax=H, diagonal=True):
    out = [0] * (W * H)
    q = deque()
    for x, y in seeds:
        assert mask[y * W + x], (x, y)
        out[y * W + x] = 1
        q.append((x, y))
    steps = ((1, 0), (-1, 0), (0, 1), (0, -1)) + (((1, 1), (-1, -1), (1, -1), (-1, 1)) if diagonal else ())
    while q:
        x, y = q.popleft()
        for dx, dy in steps:
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < ymax and mask[ny * W + nx] and not out[ny * W + nx]:
                out[ny * W + nx] = 1
                q.append((nx, ny))
    return out


fig = fill(m, ((450, 500), (450, 125), (320, 150)))         # body, head, arm
arm = fill(gray, ((320, 150),), ymax=330, diagonal=False)   # arm and finger, by brightness
fig = [a or b for a, b in zip(fig, arm)]

# Close the notch the erased ring cut across him
def at(x, y):
    x, y = int(round(x)), int(round(y))
    return 0 <= x < W and 0 <= y < H and fig[y * W + x]

add = []
for y in range(H):
    for x in range(W):
        i = y * W + x
        if ring[i] and blue[i]:
            r = math.hypot(x - CX, y - CY)
            ux, uy = (x - CX) / r, (y - CY) / r
            if at(x + ux * (R - HW - 3 - r), y + uy * (R - HW - 3 - r)) and at(x + ux * (R + HW + 3 - r), y + uy * (R + HW + 3 - r)):
                add.append(i)
for i in add:
    fig[i] = 1

with open(sys.argv[3], 'w') as f:
    f.write('P1\n%d %d\n' % (W, H))
    f.write('\n'.join(' '.join(str(fig[y * W + x]) for x in range(W)) for y in range(H)))
