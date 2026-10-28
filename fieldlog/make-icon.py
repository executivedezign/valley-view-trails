"""NHW Field Log app icon: a ruled field-notebook page with a small mushroom
drawn on it, which is most of what goes into the log.

Drawn at 8x and downsampled; Pillow's primitives have no antialiasing of their
own. Warm amber, to sit apart from the blue Camera Weather and green Macro
Exposure icons.
"""
from PIL import Image, ImageDraw


def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def vgrad(size, top, bottom):
    img = Image.new('RGB', (1, size))
    px = img.load()
    for y in range(size):
        px[0, y] = lerp(top, bottom, y / max(size - 1, 1))
    return img.resize((size, size), Image.BILINEAR)


def render(px, maskable=False):
    SS = 8
    S = px * SS
    base = vgrad(S, (46, 34, 20), (20, 15, 10)).convert('RGBA')
    d = ImageDraw.Draw(base)

    k = 0.80 if maskable else 1.0          # shrink into the maskable safe zone
    c = S / 2
    w, h = S * .56 * k, S * .68 * k
    x0, y0 = c - w / 2, c - h / 2
    r = S * .045 * k

    # the page, with a darker spine strip on the left
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], r, fill=(240, 228, 200))
    d.rounded_rectangle([x0, y0, x0 + w * .13, y0 + h], r, fill=(178, 120, 52))
    d.rectangle([x0 + w * .08, y0, x0 + w * .13, y0 + h], fill=(178, 120, 52))

    # ruled lines
    lw = max(SS, int(S * .008))
    for i in range(6):
        y = y0 + h * (.20 + i * .13)
        d.line([(x0 + w * .22, y), (x0 + w * .90, y)], fill=(196, 182, 152), width=lw)

    # the mushroom: cap (half ellipse) on a short stem, sitting on the lower lines
    mx, base_y = x0 + w * .58, y0 + h * .80
    cw, ch = w * .52, h * .26
    stem_w, stem_h = cw * .22, h * .22
    d.rounded_rectangle([mx - stem_w / 2, base_y - stem_h, mx + stem_w / 2, base_y],
                        stem_w * .35, fill=(226, 206, 168), outline=(120, 80, 40), width=lw)
    cap_top = base_y - stem_h - ch * .82
    d.pieslice([mx - cw / 2, cap_top, mx + cw / 2, cap_top + ch * 2], 180, 360,
               fill=(196, 84, 40), outline=(120, 50, 24), width=lw)
    for sx, sy, sr in ((-.18, .38, .055), (.12, .26, .045), (.24, .55, .035)):
        cx_, cy_ = mx + cw * sx, cap_top + ch * sy
        rr = cw * sr
        d.ellipse([cx_ - rr, cy_ - rr, cx_ + rr, cy_ + rr], fill=(244, 222, 190))

    return base.resize((px, px), Image.LANCZOS).convert('RGB')


if __name__ == '__main__':
    render(180).save('icon-180.png')
    render(192).save('icon-192.png')
    render(512).save('icon-512.png')
    render(512, maskable=True).save('icon-512-maskable.png')
    render(32).save('favicon-32.png')
