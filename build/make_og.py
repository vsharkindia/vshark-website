"""
Share images (Open Graph / Twitter, 1200x630) for every page — run when page images change:
    python build/make_og.py      (needs Pillow: pip install pillow)
then  python build/build.py      (picks up img/og/<page>.jpg; pages without their own image use img/og/default.jpg)

Each image is the page's hero photo, cropped to 1200x630, with a dark fade and the white VShark logo.
"""
import json, os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, 'data', 'site.json'), encoding='utf-8'))
OUT = os.path.join(ROOT, 'img', 'og')
W, H = 1200, 630
LOGO = Image.open(os.path.join(ROOT, 'img', 'vshark-logo-white.png')).convert('RGBA')
DEFAULT = 'img/about/vshark-engineer-3d-scanning-a-car-body-at-a-customer-workshop.webp'

def cover(img):
    img = img.convert('RGB')
    s = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    l, t = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((l, t, l + W, t + H))

def brand(img):
    # dark fade along the bottom so the logo reads on any photo, plus the red accent bar
    fade = Image.new('L', (1, H))
    for y in range(H):
        fade.putpixel((0, y), int(200 * max(0, (y - H * .45) / (H * .55)) ** 1.4))
    img.paste(Image.new('RGB', (W, H), (14, 17, 20)), (0, 0), fade.resize((W, H)))
    logo = LOGO.copy()
    logo.thumbnail((300, 80), Image.LANCZOS)
    img.paste(logo, (56, H - 56 - logo.height), logo)
    ImageDraw.Draw(img).rectangle((0, H - 10, W, H), fill=(153, 27, 46))  # --accent
    return img

def products_card():
    img = Image.new('RGB', (W, H), (245, 246, 248))
    prods = [Image.open(os.path.join(ROOT, p['image'])).convert('RGBA') for p in D['products']]
    slot = W // len(prods)
    for i, p in enumerate(prods):
        p.thumbnail((slot - 40, H - 170), Image.LANCZOS)
        img.paste(p, (i * slot + (slot - p.width) // 2, (H - 110 - p.height) // 2 + 10), p)
    return brand(img)

def save(name, img):
    img.save(os.path.join(OUT, name + '.jpg'), 'JPEG', quality=84, optimize=True, progressive=True)
    print('  img/og/' + name + '.jpg')

def photo(path):
    return brand(cover(Image.open(os.path.join(ROOT, path))))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    save('default', photo(DEFAULT))
    save('home', photo(D['services'][0]['image']))
    save('about', photo(DEFAULT))
    save('services', photo(D['services'][1]['image']))
    save('industries', photo(D['industries'][1]['image']))
    save('products', products_card())
    first = D['projects'][0]
    save('portfolio', photo(first['after'] if first['kind'] == 'pair' else first['images'][0]))
    for s in D['services']:
        save('services-' + s['slug'], photo(s['image']))
    for i in D['industries']:
        save('industries-' + i['slug'], photo(i['image']))
