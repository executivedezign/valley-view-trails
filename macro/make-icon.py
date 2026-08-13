"""Macro Exposure app icon: a hexagonal aperture with the plane of focus
cutting through it as a bright slice — which is the whole subject of the app,
since at these magnifications that slice is microns thick.

Drawn at 8x and downsampled; Pillow's primitives have no antialiasing of their
own. Deliberately green, to sit apart from the blue lens of Camera Weather.
"""
from PIL import Image, ImageDraw, ImageFilter
import math


def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def vgrad(size, top, bottom):
    img = Image.new('RGB', (1, size))
    px = img.load()
    for y in range(size):
        px[0, y] = lerp(top, bottom, y / max(size - 1, 1))
    return img.resize((size, size), Image.BILINEAR)


def hexagon(cx, cy, r, rot=-90):
    return [(cx + r * math.cos(math.radians(rot + 60 * i)),
             cy + r * math.sin(math.radians(rot + 60 * i))) for i in range(6)]


def render(px, maskable=False):
    SS = 8
    S = px * SS
    base = vgrad(S, (24, 34, 32), (12, 17, 16)).convert('RGBA')

    c = S / 2
    R = S * (0.30 if maskable else 0.375)
    pts = hexagon(c, c, R)

    # the aperture opening, lit from the upper left
    mask = Image.new('L', (S, S), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    fill = vgrad(S, (34, 96, 78), (10, 32, 30)).convert('RGBA')
    base.paste(fill, (0, 0), mask)

    # blade edges
    d = ImageDraw.Draw(base)
    d.line(pts + [pts[0]], fill=(126, 200, 168), width=int(R * .055), joint='curve')

    # the plane of focus: a narrow bright band, glowing, clipped to the opening
    band = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    h = R * 0.075
    bd.rectangle([c - R, c - h, c + R, c + h], fill=(214, 255, 232, 255))
    glow = band.filter(ImageFilter.GaussianBlur(S * .028))
    for layer in (glow, band):
        base = Image.alpha_composite(
            base, Image.composite(layer, Image.new('RGBA', (S, S), (0, 0, 0, 0)), mask))

    # everything off the plane is out of focus — soft wedges above and below
    soft = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(soft)
    for dy in (-1, 1):
        y0, y1 = sorted((c + dy * R * .95, c + dy * h * 3.2))
        sd.rectangle([c - R, y0, c + R, y1], fill=(0, 0, 0, 70))
    soft = soft.filter(ImageFilter.GaussianBlur(S * .035))
    base = Image.alpha_composite(
        base, Image.composite(soft, Image.new('RGBA', (S, S), (0, 0, 0, 0)), mask))

    return base.resize((px, px), Image.LANCZOS).convert('RGB')


for size, name, mk in [(180, 'icon-180.png', False), (192, 'icon-192.png', False),
                       (512, 'icon-512.png', False), (512, 'icon-512-maskable.png', True),
                       (32, 'favicon-32.png', False)]:
    render(size, mk).save('/home/user/valley-view-trails/macro/' + name)
    print('wrote', name, size)
