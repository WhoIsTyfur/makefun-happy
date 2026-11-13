"""Draw the 2D version of the entry (dev-time only; needs Pillow).

A small robot on tiptoe holds a handmade card up to the viewer, the judge.
Drawn at 2048 px and downsampled to 1024 for clean edges.
Usage: python art/gen2d.py out/2d.png
"""
import math
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2048
INK = (74, 46, 38)
FONT_HAND = "C:/Windows/Fonts/segoeprb.ttf"


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def background():
    img = Image.new("RGB", (S, S))
    top, bot = (255, 226, 170), (255, 176, 140)
    px = img.load()
    cx, cy = S * 0.5, S * 0.42
    for y in range(S):
        base = lerp(top, bot, y / S)
        for x in range(0, S):
            d = math.hypot(x - cx, y - cy) / (S * 0.6)
            g = max(0.0, 1.0 - d) ** 2 * 0.55
            px[x, y] = lerp(base, (255, 250, 225), g)
    return img


def rrect(d, box, r, fill, w=14):
    d.rounded_rectangle(box, r, fill=fill, outline=INK, width=w)


def sparkle(d, x, y, r, col):
    pts = []
    for i in range(8):
        a = i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.28
        pts.append((x + rr * math.sin(a), y - rr * math.cos(a)))
    d.polygon(pts, fill=col)


def heart(d, cx, cy, s, fill, outline=None, w=0):
    pts = []
    for i in range(200):
        t = i / 200 * 2 * math.pi
        hx = 16 * math.sin(t) ** 3
        hy = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + hx * s, cy - hy * s))
    d.polygon(pts, fill=fill, outline=outline, width=w)


def card():
    w, h = 1000, 640
    layer = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((40, 40, 40 + w, 40 + h), 30, fill=(255, 252, 244), outline=INK, width=14)
    f = ImageFont.truetype(FONT_HAND, 150)
    for text, y, col in (("for you,", 90, (226, 72, 86)), ("judge!", 300, (56, 108, 196))):
        tw = d.textlength(text, font=f)
        d.text((40 + (w - tw) / 2, 40 + y - 40), text, font=f, fill=col)
    heart(d, 40 + w - 150, 40 + h - 120, 5.2, (240, 80, 100))
    sparkle(d, 140, 110, 46, (255, 196, 60))
    sparkle(d, 150, h - 30, 34, (255, 196, 60))
    return layer.rotate(5, resample=Image.BICUBIC, expand=True)


def robot(img):
    d = ImageDraw.Draw(img)
    cx = S // 2
    # ground shadow
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((cx - 330, 1830, cx + 330, 1930), fill=(150, 70, 50, 90))
    img.paste(sh.filter(ImageFilter.GaussianBlur(18)), (0, 0), sh.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(img)
    body = (210, 236, 232)
    # legs on tiptoe
    for lx in (cx - 110, cx + 110):
        d.rounded_rectangle((lx - 48, 1640, lx + 48, 1840), 40, fill=(160, 196, 196), outline=INK, width=14)
    # arms reaching up to the card
    for sx, hx in ((cx - 230, cx - 420), (cx + 230, cx + 440)):
        d.line((sx, 1460, hx, 960), fill=INK, width=96, joint="curve")
        d.line((sx, 1460, hx, 960), fill=body, width=68, joint="curve")
    # torso
    rrect(d, (cx - 250, 1380, cx + 250, 1700), 90, body)
    heart(d, cx, 1540, 5.0, (240, 90, 110), outline=INK, w=10)
    # head
    rrect(d, (cx - 290, 1000, cx + 290, 1380), 140, body)
    d.rounded_rectangle((cx - 230, 1060, cx + 230, 1320), 100, fill=(44, 58, 86), outline=INK, width=10)
    # happy closed eyes, smile, blush
    glow = (140, 250, 220)
    for ex in (cx - 105, cx + 105):
        d.arc((ex - 60, 1120, ex + 60, 1220), 200, 340, fill=glow, width=26)
    d.arc((cx - 70, 1170, cx + 70, 1280), 20, 160, fill=glow, width=24)
    for bx in (cx - 170, cx + 170):
        d.ellipse((bx - 40, 1225, bx + 40, 1260), fill=(255, 130, 150))
    return img


def main(out):
    img = background()
    d = ImageDraw.Draw(img)
    for x, y, r in ((300, 380, 60), (1760, 300, 48), (1820, 1250, 70), (230, 1330, 52), (1650, 1700, 40)):
        sparkle(d, x, y, r, (255, 255, 240))
    robot(img)
    c = card()
    img.paste(c, ((S - c.width) // 2, 230), c)
    # hands over the card edge
    d = ImageDraw.Draw(img)
    for hx, hy in ((S // 2 - 420, 960), (S // 2 + 440, 920)):
        d.ellipse((hx - 70, hy - 70, hx + 70, hy + 70), fill=(210, 236, 232), outline=INK, width=14)
    img = img.resize((1024, 1024), Image.LANCZOS)
    img.save(out, optimize=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out/2d.png")
