# Gumagawa ng lahat ng launcher icon (lahat ng density) mula sa logo_src.png
import os
from PIL import Image, ImageDraw

src = Image.open('logo_src.png').convert('RGBA')
res = 'android/app/src/main/res'
dens = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}

def mask(px, kind):
    big = px * 4
    m = Image.new('L', (big, big), 0)
    d = ImageDraw.Draw(m)
    if kind == 'round':
        d.ellipse((0, 0, big - 1, big - 1), fill=255)
    else:
        d.rounded_rectangle((0, 0, big - 1, big - 1), radius=int(big * 0.18), fill=255)
    return m.resize((px, px), Image.LANCZOS)

for name, px in dens.items():
    d = f'{res}/mipmap-{name}'
    os.makedirs(d, exist_ok=True)
    for kind, fn in (('square', 'ic_launcher.png'), ('round', 'ic_launcher_round.png')):
        im = src.resize((px, px), Image.LANCZOS)
        im.putalpha(mask(px, kind))
        im.save(f'{d}/{fn}')
    fg = px * 108 // 48
    canvas = Image.new('RGBA', (fg, fg), (0, 0, 0, 0))
    inner = int(fg * 0.62)
    logo = src.resize((inner, inner), Image.LANCZOS)
    canvas.paste(logo, ((fg - inner) // 2, (fg - inner) // 2))
    canvas.save(f'{d}/ic_launcher_foreground.png')

os.makedirs(f'{res}/values', exist_ok=True)
with open(f'{res}/values/ic_launcher_background.xml', 'w') as f:
    f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#000000</color>\n</resources>\n')
print('icons generated')
