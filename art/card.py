"""A kid's card for the judge, in crayon (dev-time only; needs Pillow + numpy).

  python art/card.py OUT.png

A typed letter on top, a crayon drawing below: the judge, on its day off,
in a deck chair at the beach with sunglasses and an ice cream, and a dog
drawn by the little brother. Everything is drawn here: wax strokes are
polylines broken up by a paper-grain mask, fills are jittered hatching.
"""
import math
import random
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W = H = 1024
rng = random.Random(2026)
FONT_TYPE = "C:/Windows/Fonts/segoeuib.ttf"
FONT_HAND = "C:/Windows/Fonts/segoeprb.ttf"
INK = (52, 42, 36)

LETTER = [
    ("DEAR JUDGE,", 0),
    ("We heard you look at happy pictures all day,", 1),
    ("but nobody ever draws one of you.", 0),
    ("So this is you, on your day off.", 1),
    ("You have ice cream. The sun is warm.", 1),
    ("Nobody needs anything from you today.", 0),
    ("Love, June (6) and Ollie (4)", 1),
    ("P.S. Ollie drew the dog. The dog is yours now.", 1),
]


# ------------------------------------------------------------------ paper
def grain(seed, scale=1.0):
    """Paper tooth: values in 0..1, fixed by seed so every run is the same."""
    r = np.random.default_rng(seed)
    a = r.random((H, W)).astype(np.float32)
    img = Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7 * scale))
    b = np.asarray(img, dtype=np.float32) / 255.0
    b = (b - b.mean()) / (b.std() + 1e-6)
    return b


G1 = grain(1)
G2 = grain(2, 2.0)


def paper():
    base = np.zeros((H, W, 3), np.float32)
    base[:] = (247, 241, 228)
    fib = Image.fromarray((np.random.default_rng(9).random((H // 4, W // 4)) * 255).astype(np.uint8))
    fib = np.asarray(fib.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3)), np.float32) / 255.0
    base += (fib[..., None] - 0.5) * 10 + G1[..., None] * 2.0
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot((xx - W / 2) / W, (yy - H / 2) / H)
    base *= (1 - 0.08 * d[..., None] ** 2)
    return np.clip(base, 0, 255)


# ------------------------------------------------------------------ crayon
class Crayon:
    """Collects strokes per colour into a mask, then lays wax with grain."""

    def __init__(self):
        self.layers = []

    def mask(self):
        return Image.new("L", (W, H), 0)

    def stroke(self, m, pts, width, passes=3, wobble=1.6):
        d = ImageDraw.Draw(m)
        for p in range(passes):
            jit = [(x + rng.uniform(-wobble, wobble), y + rng.uniform(-wobble, wobble)) for x, y in pts]
            d.line(jit, fill=255, width=max(1, int(width + rng.uniform(-1, 1))), joint="curve")

    def hatch(self, m, poly, spacing=6, width=4, angle=None):
        """Fill a polygon with jittered parallel strokes, clipped to it."""
        clip = Image.new("L", (W, H), 0)
        ImageDraw.Draw(clip).polygon(poly, fill=255)
        clip = clip.filter(ImageFilter.MaxFilter(5))
        lines = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(lines)
        a = math.radians(angle if angle is not None else rng.uniform(30, 60))
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        rad = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) / 2 + 10
        k = -rad
        while k < rad:
            ox, oy = -math.sin(a) * k, math.cos(a) * k
            p0 = (cx + ox - math.cos(a) * rad, cy + oy - math.sin(a) * rad)
            p1 = (cx + ox + math.cos(a) * rad, cy + oy + math.sin(a) * rad)
            d.line([p0, p1], fill=255, width=width)
            k += spacing + rng.uniform(-1.5, 1.5)
        m.paste(ImageChops.multiply(lines, clip), (0, 0), ImageChops.multiply(lines, clip))

    def lay(self, m, color, strength=0.9):
        self.layers.append((m, color, strength))

    def apply(self, canvas):
        out = canvas
        for m, color, strength in self.layers:
            a = np.asarray(m.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255.0
            tooth = np.clip(0.75 + 0.45 * G2 - 0.25 * G1, 0, 1)  # wax skips the paper's pits
            a = np.clip(a * tooth * strength, 0, 1)[..., None]
            out = out * (1 - a) + np.array(color, np.float32) * a
        return out


def ellipse_pts(cx, cy, rx, ry, n=48, wob=0.04, start=0.0):
    return [(cx + rx * (1 + rng.uniform(-wob, wob)) * math.cos(start + 2 * math.pi * i / n),
             cy + ry * (1 + rng.uniform(-wob, wob)) * math.sin(start + 2 * math.pi * i / n)) for i in range(n + 3)]


def poly_wobble(pts, amt=2.0):
    return [(x + rng.uniform(-amt, amt), y + rng.uniform(-amt, amt)) for x, y in pts]


# ------------------------------------------------------------------ the drawing
def drawing(cr):
    top = 620  # the drawing area starts here
    # sea and sand
    sea = cr.mask()
    cr.hatch(sea, [(40, top + 120), (984, top + 105), (984, top + 215), (40, top + 225)], spacing=7, width=4, angle=8)
    cr.lay(sea, (70, 140, 215), 0.75)
    waves = cr.mask()
    for row in range(2):
        y0 = top + 112 + row * 46
        pts = [(x, y0 + 7 * math.sin(x / 26.0 + row)) for x in range(44, 984, 8)]
        cr.stroke(waves, pts, 4)
    cr.lay(waves, (30, 90, 180))
    sand = cr.mask()
    cr.hatch(sand, [(40, top + 215), (984, top + 205), (984, 990), (40, 990)], spacing=6, width=5, angle=-20)
    cr.lay(sand, (245, 196, 70), 0.85)

    # deck chair: red and white stripes, legs
    chair = cr.mask()
    cx, cy = 430, top + 255
    back = [(cx - 120, cy - 150), (cx - 20, cy - 175), (cx + 60, cy + 40), (cx - 50, cy + 60)]
    stripes_red = cr.mask()
    for i in range(4):
        t0, t1 = i / 4, (i + 0.5) / 4
        q = [(back[0][0] + (back[1][0] - back[0][0]) * t0, back[0][1] + (back[1][1] - back[0][1]) * t0),
             (back[0][0] + (back[1][0] - back[0][0]) * t1, back[0][1] + (back[1][1] - back[0][1]) * t1),
             (back[3][0] + (back[2][0] - back[3][0]) * t1, back[3][1] + (back[2][1] - back[3][1]) * t1),
             (back[3][0] + (back[2][0] - back[3][0]) * t0, back[3][1] + (back[2][1] - back[3][1]) * t0)]
        cr.hatch(stripes_red, q, spacing=5, width=4)
    cr.lay(stripes_red, (226, 60, 60), 0.9)
    cr.stroke(chair, back + [back[0]], 4)
    for a, b in (((cx - 50, cy + 60), (cx - 95, cy + 125)), ((cx + 60, cy + 40), (cx + 110, cy + 120)),
                 ((cx - 20, cy - 175), (cx + 110, cy + 120))):
        cr.stroke(chair, [a, b], 6)
    cr.lay(chair, (120, 70, 40))

    # the judge: a little robot with a screen face and sunglasses, lounging
    rx, ry = cx - 10, cy - 70
    body = cr.mask()
    cr.hatch(body, poly_wobble([(rx - 60, ry - 5), (rx + 55, ry - 15), (rx + 70, ry + 85), (rx - 45, ry + 95)]),
             spacing=6, width=4)
    cr.lay(body, (120, 200, 190), 0.85)
    head = cr.mask()
    hx, hy = rx - 40, ry - 95
    hq = poly_wobble([(hx - 95, hy - 70), (hx + 88, hy - 80), (hx + 96, hy + 62), (hx - 90, hy + 70)])
    cr.hatch(head, hq, spacing=6, width=4)
    cr.lay(head, (150, 205, 235), 0.85)
    scr = cr.mask()
    cr.hatch(scr, poly_wobble([(hx - 66, hy - 46), (hx + 60, hy - 54), (hx + 66, hy + 42), (hx - 62, hy + 48)]),
             spacing=5, width=4)
    cr.lay(scr, (245, 250, 240), 0.9)
    outline = cr.mask()
    cr.stroke(outline, hq + [hq[0]], 4)
    cr.stroke(outline, [(rx - 60, ry - 5), (rx + 55, ry - 15), (rx + 70, ry + 85), (rx - 45, ry + 95), (rx - 60, ry - 5)], 4)
    cr.stroke(outline, [(hx + 5, hy - 78), (hx + 12, hy - 118)], 5)  # antenna
    cr.stroke(outline, ellipse_pts(hx + 13, hy - 128, 11, 11), 5)
    # legs stretched out, relaxed, crossed at the ankle
    cr.stroke(outline, [(rx + 50, ry + 80), (rx + 150, ry + 105), (rx + 205, ry + 100)], 6)
    cr.stroke(outline, [(rx + 40, ry + 92), (rx + 150, ry + 95), (rx + 200, ry + 118)], 6)
    cr.lay(outline, (45, 45, 55))
    shades = cr.mask()  # sunglasses
    for ex in (-28, 28):
        cr.hatch(shades, poly_wobble([(hx + ex - 26, hy - 22), (hx + ex + 24, hy - 24), (hx + ex + 20, hy + 6),
                                      (hx + ex - 22, hy + 8)], 1.0), spacing=3, width=4)
    cr.stroke(shades, [(hx - 56, hy - 20), (hx + 56, hy - 22)], 5)
    cr.lay(shades, (25, 25, 30))
    smile = cr.mask()
    cr.stroke(smile, [(hx - 30, hy + 20), (hx - 12, hy + 36), (hx + 12, hy + 37), (hx + 30, hy + 20)], 7)
    cr.lay(smile, (200, 40, 60))
    # arm up holding an ice cream cone, one drip
    arm = cr.mask()
    cr.stroke(arm, [(rx + 40, ry + 10), (rx + 95, ry - 25), (rx + 110, ry - 70)], 6)
    cr.lay(arm, (45, 45, 55))
    cone = cr.mask()
    icx, icy = rx + 115, ry - 95
    cr.hatch(cone, [(icx - 22, icy), (icx + 22, icy), (icx, icy + 55)], spacing=5, width=4, angle=45)
    cr.lay(cone, (205, 140, 70), 0.9)
    scoop = cr.mask()
    cr.hatch(scoop, ellipse_pts(icx, icy - 18, 30, 26, 32, 0.08), spacing=4, width=4)
    cr.lay(scoop, (250, 130, 170), 0.95)
    drip = cr.mask()
    cr.stroke(drip, [(icx + 18, icy - 2), (icx + 21, icy + 22)], 6)
    cr.lay(drip, (250, 130, 170))

    # the label the kids wrote
    lab = cr.mask()
    cr.stroke(lab, [(hx - 150, hy - 120), (hx - 120, hy - 95), (hx - 95, hy - 75)], 4)
    cr.stroke(lab, [(hx - 95, hy - 75), (hx - 112, hy - 78)], 4)
    cr.stroke(lab, [(hx - 95, hy - 75), (hx - 99, hy - 92)], 4)
    cr.lay(lab, (230, 90, 40))

    # Ollie's dog: wobblier, bigger, wonderful
    dx, dy = 760, top + 255
    dog = cr.mask()
    cr.hatch(dog, ellipse_pts(dx, dy, 95, 52, 40, 0.12), spacing=5, width=5)
    cr.hatch(dog, ellipse_pts(dx + 95, dy - 55, 48, 42, 32, 0.12), spacing=5, width=5)
    cr.lay(dog, (160, 100, 50), 0.85)
    dline = cr.mask()
    cr.stroke(dline, ellipse_pts(dx, dy, 95, 52, 40, 0.12), 5, wobble=2.5)
    cr.stroke(dline, ellipse_pts(dx + 95, dy - 55, 48, 42, 32, 0.12), 5, wobble=2.5)
    for lx in (-60, -25, 25, 60):
        cr.stroke(dline, [(dx + lx, dy + 40), (dx + lx + rng.uniform(-8, 8), dy + 105)], 6, wobble=2.5)
    cr.stroke(dline, [(dx - 92, dy - 10), (dx - 135, dy - 60), (dx - 128, dy - 75)], 6, wobble=2.5)  # wagging tail
    for k in range(3):  # wag lines
        cr.stroke(dline, [(dx - 160 - k * 4, dy - 85 + k * 22), (dx - 178 - k * 4, dy - 92 + k * 22)], 3)
    cr.stroke(dline, [(dx + 120, dy - 108), (dx + 132, dy - 140), (dx + 142, dy - 104)], 5)  # ears
    cr.stroke(dline, [(dx + 70, dy - 104), (dx + 66, dy - 138), (dx + 88, dy - 100)], 5)
    cr.lay(dline, (70, 45, 30))
    face = cr.mask()
    cr.stroke(face, ellipse_pts(dx + 82, dy - 66, 6, 6, 12), 6)
    cr.stroke(face, ellipse_pts(dx + 112, dy - 66, 6, 6, 12), 6)
    cr.stroke(face, [(dx + 84, dy - 38), (dx + 96, dy - 30), (dx + 110, dy - 38)], 5)
    cr.lay(face, (30, 25, 20))
    tongue = cr.mask()
    cr.hatch(tongue, ellipse_pts(dx + 97, dy - 22, 10, 13, 20, 0.1), spacing=3, width=4)
    cr.lay(tongue, (240, 90, 110))
    heart = cr.mask()
    hpts = []
    for i in range(41):
        t = i / 40 * 2 * math.pi
        hpts.append((dx + 170 + 16 * math.sin(t) ** 3 * 1.7,
                     dy - 130 - (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) * 1.7))
    cr.hatch(heart, hpts, spacing=4, width=4)
    cr.lay(heart, (235, 60, 90), 0.95)

    # big crayon sun in the corner, as kids draw it, smiling
    sx, sy = 905, 118
    sun = cr.mask()
    cr.hatch(sun, ellipse_pts(sx, sy, 62, 62, 40, 0.05), spacing=5, width=5)
    cr.lay(sun, (255, 205, 40), 0.95)
    rays = cr.mask()
    for k in range(12):
        a = k * math.pi / 6 + 0.2
        cr.stroke(rays, [(sx + 78 * math.cos(a), sy + 78 * math.sin(a)), (sx + 112 * math.cos(a), sy + 112 * math.sin(a))], 6)
    cr.stroke(rays, ellipse_pts(sx, sy, 62, 62, 40, 0.05), 4)
    cr.lay(rays, (245, 150, 30))
    sface = cr.mask()
    cr.stroke(sface, [(sx - 24, sy - 8), (sx - 18, sy - 16), (sx - 12, sy - 8)], 4)
    cr.stroke(sface, [(sx + 12, sy - 8), (sx + 18, sy - 16), (sx + 24, sy - 8)], 4)
    cr.stroke(sface, [(sx - 22, sy + 14), (sx, sy + 28), (sx + 22, sy + 14)], 5)
    cr.lay(sface, (150, 80, 20))
    return (hx, hy)


def text_layer(canvas, judge_at):
    img = Image.fromarray(canvas.astype(np.uint8))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_TYPE, 37)
    fb = ImageFont.truetype(FONT_TYPE, 44)
    y = 52
    for i, (line, gap) in enumerate(LETTER):
        y += gap * 16
        font = fb if i == 0 else f
        d.text((62, y), line, font=font, fill=INK)
        y += 47 if i else 58
    # crayon-written labels
    fh = ImageFont.truetype(FONT_HAND, 34)
    hx, hy = judge_at
    d.text((hx - 235, hy - 178), "you!", font=fh, fill=(225, 85, 35))
    d.text((800, 610 + 330), "yours", font=ImageFont.truetype(FONT_HAND, 28), fill=(110, 70, 40))
    return img


def main(out):
    canvas = paper()
    cr = Crayon()
    judge_at = drawing(cr)
    canvas = cr.apply(canvas)
    img = text_layer(canvas, judge_at)
    img.save(out, optimize=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out/card.png")
