"""Genera los iconos de la PWA (cabeza azul de Jessito).  Uso: python make_icons.py"""
import os
from PIL import Image, ImageDraw, ImageFilter

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'icons')
os.makedirs(out, exist_ok=True)

def draw(size, pad):
    S = size * 2                                   # sobremuestreo para bordes suaves
    img = Image.new('RGB', (S, S), (8, 14, 36))
    g = ImageDraw.Draw(img)
    for r in range(S // 2, 0, -4):                 # fondo con degradado radial
        c = int(14 + 30 * (1 - r / (S / 2)))
        g.ellipse([S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r], fill=(c // 2, c, c * 2))
    m = S * pad
    box = [m, m * 1.15, S - m, S - m * 1.15]
    w, h = box[2] - box[0], box[3] - box[1]
    g.rounded_rectangle([box[0] - S * .05, box[1] + h * .3, box[0] + S * .03, box[1] + h * .62], S * .03, fill=(120, 190, 255))
    g.rounded_rectangle([box[2] - S * .03, box[1] + h * .3, box[2] + S * .05, box[1] + h * .62], S * .03, fill=(120, 190, 255))
    g.ellipse(box, fill=(47, 134, 255), outline=(28, 86, 194), width=int(S * .012))
    g.line([S / 2, box[1], S / 2, box[1] - S * .07], fill=(120, 190, 255), width=int(S * .015))
    g.ellipse([S / 2 - S * .03, box[1] - S * .1, S / 2 + S * .03, box[1] - S * .04], fill=(255, 224, 138))
    sc = [box[0] + w * .12, box[1] + h * .24, box[2] - w * .12, box[1] + h * .8]   # pantalla
    g.rounded_rectangle(sc, S * .09, fill=(5, 12, 32))
    sw, sh = sc[2] - sc[0], sc[3] - sc[1]
    for ex in (.3, .7):                                                          # ojos
        cx, cy = sc[0] + sw * ex, sc[1] + sh * .36
        g.ellipse([cx - S * .055, cy - S * .06, cx + S * .055, cy + S * .06], fill=(255, 255, 255))
        g.ellipse([cx - S * .035, cy - S * .04, cx + S * .035, cy + S * .04], fill=(60, 150, 255))
        g.ellipse([cx - S * .015, cy - S * .016, cx + S * .015, cy + S * .016], fill=(5, 12, 32))
    for i in range(11):                                                          # boca de luces (sonrisa)
        u = i / 10 * 2 - 1
        x = sc[0] + sw * (.5 + u * .26); y = sc[1] + sh * (.78 - .1 * u * u)
        g.ellipse([x - S * .012, y - S * .012, x + S * .012, y + S * .012], fill=(143, 224, 255))
    return img.resize((size, size), Image.LANCZOS)

draw(192, .13).save(os.path.join(out, 'icon-192.png'))
draw(512, .13).save(os.path.join(out, 'icon-512.png'))
draw(512, .24).save(os.path.join(out, 'maskable-512.png'))     # zona segura para iconos adaptables
draw(180, .13).save(os.path.join(out, 'apple-touch-icon.png'))
print('iconos listos en', os.path.abspath(out))
