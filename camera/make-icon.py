"""Camera Weather app icon: a lens with condensation beading on the glass.

Drawn at 8x and downsampled, because Pillow's shape primitives have no
antialiasing of their own. Geometry is expressed in fractions of the canvas so
the same code renders every size the manifest asks for.
"""
from PIL import Image, ImageDraw, ImageFilter
import math

SS = 8  # supersample factor


def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def vgrad(size, top, bottom):
    img = Image.new('RGB', (1, size))
    px = img.load()
    for y in range(size):
        px[0, y] = lerp(top, bottom, y / max(size - 1, 1))
    return img.resize((size, size), Image.BILINEAR)


def radial(size, inner, outer, cx, cy, r, n=320):
    """Radial fill as an RGBA layer, used for the glass. Rendered small and
    upscaled — it is a smooth gradient, so nothing is lost and it is 150x faster."""
    k = n / size
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    px = img.load()
    for y in range(n):
        for x in range(n):
            d = math.hypot(x - cx * k, y - cy * k) / (r * k)
            px[x, y] = lerp(inner, outer, min(d, 1.0)) + (255,)
    return img.resize((size, size), Image.BILINEAR)


def droplet(draw, cx, cy, r, body, hi):
    """A bead of water: a disc, with a small specular dot up and to the left."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=body)
    hr = r * 0.34
    draw.ellipse([cx - r * .38 - hr, cy - r * .38 - hr,
                  cx - r * .38 + hr, cy - r * .38 + hr], fill=hi)


def render(px, maskable=False):
    S = px * SS
    # iOS applies its own squircle mask, so the art is full-bleed and the
    # content is kept inside a safe circle that survives Android's mask too.
    base = vgrad(S, (26, 33, 45), (13, 16, 21)).convert('RGBA')
    d = ImageDraw.Draw(base)

    c = S / 2
    R = S * (0.30 if maskable else 0.375)   # lens outer radius

    # barrel: a dark ring with a bright edge, so the lens reads as a cylinder
    d.ellipse([c - R, c - R, c + R, c + R], fill=(24, 30, 39))
    d.ellipse([c - R, c - R, c + R, c + R], outline=(78, 92, 110), width=int(R * .075))
    r2 = R * 0.845
    d.ellipse([c - r2, c - r2, c + r2, c + r2], outline=(52, 63, 78), width=int(R * .045))

    # glass: deep blue, brightest off-centre so it looks lit rather than flat
    gr = R * 0.735
    glass = radial(S, (58, 122, 208), (13, 40, 80), c - gr * .17, c - gr * .19, gr * 1.15)
    mask = Image.new('L', (S, S), 0)
    ImageDraw.Draw(mask).ellipse([c - gr, c - gr, c + gr, c + gr], fill=255)
    base.paste(glass, (0, 0), mask)

    # specular sweep across the upper left of the element
    sheen = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sheen)
    sd.ellipse([c - gr * .92, c - gr * .95, c + gr * .25, c + gr * .1],
               fill=(255, 255, 255, 34))
    sheen = sheen.filter(ImageFilter.GaussianBlur(S * .022))
    sheen.putalpha(sheen.getchannel('A').point(lambda v: v))
    base = Image.alpha_composite(base, Image.composite(
        sheen, Image.new('RGBA', (S, S), (0, 0, 0, 0)), mask))

    # rim of the front element: a bright coating reflection, brightest where the
    # sheen falls, which is what separates a lens from a painted circle
    d = ImageDraw.Draw(base)
    d.ellipse([c - gr, c - gr, c + gr, c + gr], outline=(120, 168, 232), width=int(R * .028))

    # condensation: the thing the app exists to warn about
    d = ImageDraw.Draw(base)
    beads = [(0.28, 0.32, 0.205), (-0.36, 0.06, 0.140), (0.03, -0.34, 0.108),
             (0.47, -0.16, 0.082)]
    for dx, dy, br in beads:
        droplet(d, c + gr * dx, c + gr * dy, gr * br,
                (214, 233, 255, 235), (255, 255, 255, 245))

    return base.resize((px, px), Image.LANCZOS).convert('RGB')


for size, name, mk in [(180, 'icon-180.png', False), (192, 'icon-192.png', False),
                       (512, 'icon-512.png', False), (512, 'icon-512-maskable.png', True),
                       (32, 'favicon-32.png', False)]:
    render(size, mk).save('/home/user/valley-view-trails/camera/' + name)
    print('wrote', name, size)
