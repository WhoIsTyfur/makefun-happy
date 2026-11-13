"""Final grade for a Blender render (dev-time only; needs Pillow).

  python art/post.py IN.png OUT.png [saturation] [warmth] [vignette]

Lifts saturation a little (AgX mutes strong colours), warms the mids and adds
a soft vignette that pulls the eye to the middle. Writes an optimized PNG.
"""
import sys

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter


def grade(src, dst, sat=1.18, warmth=0.04, vignette=0.22):
    img = Image.open(src).convert("RGB")
    img = ImageEnhance.Color(img).enhance(sat)
    img = ImageEnhance.Contrast(img).enhance(1.04)
    r, g, b = img.split()
    r = r.point(lambda v: min(255, int(v * (1 + warmth))))
    b = b.point(lambda v: int(v * (1 - warmth)))
    img = Image.merge("RGB", (r, g, b))
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse((-w * 0.25, -h * 0.2, w * 1.25, h * 1.2), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(w * 0.12))
    dark = ImageEnhance.Brightness(img).enhance(1 - vignette)
    img = Image.composite(img, dark, mask)
    if img.size != (1024, 1024):
        img = img.resize((1024, 1024), Image.LANCZOS)
    img.save(dst, optimize=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    grade(a[0], a[1], *(float(x) for x in a[2:]))
