"""
Import portfolio images from the team's source folder into img/portfolio/.

  python build/import_portfolio.py "C:/Users/ADMIN/Desktop/TEMP/Vshark V2.0"

• Scan/CAD sets: every image in a set is cropped with ONE shared box (the union of
  the object outlines + margin, widened to 3:2) so scan, CAD and overlay stay
  pixel-aligned for the compare slider; output 1500×1000 WebP.
• Single images: longest side ≤ 1600 px, WebP. Optional 'crop' (fractions of
  width/height) or 'cover' (rectangle painted with the background colour) removes
  third-party reference insets.
Output names are <slug>-<role>.webp. Add new sets to PAIRS / SINGLES below.
"""
import os, sys
from PIL import Image, ImageDraw, ImageChops

SRC = sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\ADMIN\Desktop\TEMP\Vshark V2.0'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'img', 'portfolio')
BG = (242, 242, 242)
W, H = 1500, 1000

# slug: {role: relative path}; roles: scan, cad, overlay, overlay2 …
PAIRS = {
 'race-car-body':       {'scan': r'Automotive\Car Exterior\prototype-race-car-body-3d-scan-data.png', 'cad': r'Automotive\Car Exterior\prototype-race-car-body-reverse-engineering-cad-model.png', 'overlay': r'Automotive\Car Exterior\prototype-race-car-body-scan-to-cad-overlay-inspection.png'},
 'car-body-in-white':   {'scan': r'Automotive\Car chassis\car-body-in-white-chassis-3d-scan-data.png', 'cad': r'Automotive\Car chassis\car-body-in-white-chassis-reverse-engineering-cad-model.png'},
 'engine-crankcase':    {'scan': r'Automotive\Casting block\engine-crankcase-casting-3d-scan-data.png', 'cad': r'Automotive\Casting block\engine-crankcase-casting-reverse-engineering-cad-model.png', 'overlay': r'Automotive\Casting block\engine-crankcase-casting-scan-to-cad-overlay-inspection.png'},
 'e-bike-frame':        {'scan': r'Automotive\bike frame cover\electric-dirt-bike-3d-scan-data.png', 'cad': r'Automotive\bike frame cover\electric-dirt-bike-frame-reverse-engineering-cad-model.png', 'overlay': r'Automotive\bike frame cover\electric-dirt-bike-frame-scan-to-cad-overlay-angled-view.png', 'overlay2': r'Automotive\bike frame cover\electric-dirt-bike-frame-scan-to-cad-overlay-side-view.png'},
 'cylinder-head':       {'scan': r'Automotive\cylinder head\engine-cylinder-head-3d-scan-data.png', 'cad': r'Automotive\cylinder head\engine-cylinder-head-reverse-engineering-cad-model.png'},
 'roll-cage':           {'scan': r'Automotive\roll cage\tubular-roll-cage-chassis-3d-scan-data.png', 'cad': r'Automotive\roll cage\tubular-roll-cage-chassis-reverse-engineering-cad-model.png', 'overlay': r'Automotive\roll cage\tubular-roll-cage-chassis-scan-to-cad-overlay-inspection.png'},
 'tractor-underbody':   {'scan': r'Automotive\tracktor\tractor-underbody-3d-scan-data.png', 'cad': r'Automotive\tracktor\tractor-underbody-reverse-engineering-cad-model.png', 'overlay': r'Automotive\tracktor\tractor-underbody-scan-to-cad-overlay-inspection.png'},
 'truck-chassis':       {'scan': r'Automotive\truck frame\truck-chassis-frame-3d-scan-data.png', 'cad': r'Automotive\truck frame\truck-chassis-frame-reverse-engineering-cad-model.png', 'overlay': r'Automotive\truck frame\truck-chassis-frame-scan-to-cad-overlay-inspection.png'},
 'motorcycle-fairing':  {'scan': r'CLASS A\bike faring\motorcycle-front-fairing-3d-scan-data.png', 'cad': r'CLASS A\bike faring\motorcycle-front-fairing-class-a-surface-cad-model.png', 'overlay': r'CLASS A\bike faring\motorcycle-front-fairing-class-a-surface-scan-overlay.png'},
 'dashboard':           {'scan': r'CLASS A\dashboard\car-dashboard-instrument-panel-3d-scan-data.png', 'cad': r'CLASS A\dashboard\car-dashboard-instrument-panel-class-a-surface-cad-model.png', 'overlay': r'CLASS A\dashboard\car-dashboard-instrument-panel-class-a-surface-scan-overlay.png'},
 'key-fob':             {'scan': r'CLASS A\keyfob\car-key-fob-3d-scan-data.png', 'cad': r'CLASS A\keyfob\car-key-fob-class-a-surface-cad-model.png', 'overlay': r'CLASS A\keyfob\car-key-fob-class-a-surface-scan-overlay.png'},
 'uav-wing':            {'scan': r'CLASS A\wing\uav-drone-wing-3d-scan-data.png', 'cad': r'CLASS A\wing\uav-drone-wing-class-a-surface-cad-model.png', 'overlay': r'CLASS A\wing\uav-drone-wing-class-a-surface-scan-overlay.png'},
 'pump-volute':         {'scan': r'Oil and Gas\pump\centrifugal-pump-volute-casing-3d-scan-data.png', 'cad': r'Oil and Gas\pump\centrifugal-pump-volute-casing-reverse-engineering-cad-model.png'},
 'crusher-liner':       {'scan': r'crusher\cone-crusher-liner-3d-scan-data.png', 'cad': r'crusher\cone-crusher-liner-reverse-engineering-cad-model.png', 'overlay': r'crusher\cone-crusher-liner-scan-to-cad-overlay-inspection.png'},
 'smartphone-housing':  {'scan': r'mobile\smartphone-back-housing-3d-scan-data.png', 'cad': r'mobile\smartphone-back-housing-reverse-engineering-cad-model.png', 'overlay': r'mobile\smartphone-back-housing-scan-to-cad-overlay-inspection.png'},
 'mold-insert':         {'scan': r'mold assm\automotive-mold-insert-assembly-3d-scan-data.png', 'cad': r'mold assm\automotive-mold-insert-assembly-reverse-engineering-cad-model.png', 'overlay': r'mold assm\automotive-mold-insert-assembly-scan-to-cad-overlay-inspection.png'},
 'shopping-trolley':    {'scan': r'shopping kart\plastic-shopping-trolley-3d-scan-data.png', 'cad': r'shopping kart\plastic-shopping-trolley-reverse-engineering-cad-model.png', 'overlay': r'shopping kart\plastic-shopping-trolley-scan-to-cad-overlay-inspection.png'},
}

# output name: (relative path, options)
SINGLES = {
 'heritage-gajalakshmi':   (r'3D Scaning\Idols  statue\gajalakshmi-carved-relief-3d-scan.jpg', {}),
 'heritage-ganesha':       (r'3D Scaning\Idols  statue\ganesha-idol-statue-3d-scan.jpg', {}),
 'heritage-lakshmi':       (r'3D Scaning\Idols  statue\goddess-lakshmi-relief-panel-3d-scan.jpg', {}),
 'heritage-leaf':          (r'3D Scaning\Idols  statue\leaf-vein-surface-detail-3d-scan.jpeg', {}),
 'pendant-casting':        (r'3D printing\Pendant\vajra-phurba-pendant-3d-jewelry-model-for-casting.jpeg', {}),
 'pendant-sculpt':         (r'3D printing\Pendant\vajra-phurba-pendant-3d-sculpt-stl-for-3d-printing.jpeg', {}),
 'model-utility-truck':    (r'3D printing\car models\4x4-utility-box-truck-scale-model-3d-printable-stl.jpeg', {}),
 'model-hot-rod':          (r'3D printing\car models\hot-rod-dragster-scale-model-3d-printable-stl.jpeg', {}),
 'model-race-car':         (r'3D printing\car models\retro-race-car-scale-model-3d-printable-stl.jpeg', {}),
 'model-tow-truck':        (r'3D printing\car models\vintage-winch-tow-truck-scale-model-3d-printable-stl.jpeg', {}),
 'model-bush-plane':       (r'3D printing\plane\bush-plane-aircraft-scale-model-3d-printable-stl.png', {'trim': True}),
 'sculpt-triceratops':     (r'3D printing\characters\baby-triceratops-figurine-3d-sculpt-for-3d-printing.jpeg', {}),
 # reference artwork of a third-party character (bottom-right inset) painted out
 'sculpt-cartoon':         (r'3D printing\characters\cartoon-character-figurine-3d-model-for-3d-printing.jpg', {'cover': (0.655, 0.595, 1.0, 1.0)}),
 'sculpt-cherubs':         (r'3D printing\characters\cherub-angels-relief-plaque-3d-model-for-3d-printing.jpg', {}),
 # right half is third-party game artwork used as reference: keep the sculpt only
 'sculpt-game-character':  (r'3D printing\characters\game-character-figurine-3d-sculpt-for-3d-printing.jpg', {'crop': (0.0, 0.0, 0.52, 1.0)}),
 'sculpt-kangaroo':        (r'3D printing\characters\kangaroo-boxer-character-3d-sculpt-turnaround.jpg', {}),
 'render-camera':          (r'Rendering\360-action-camera-3d-product-modelling-rendering.jpeg', {}),
 'render-exhibition':      (r'Rendering\exhibition-stall-design-3d-rendering.jpg', {}),
 'render-ram-ring':        (r'Rendering\gold-ram-head-ring-3d-jewelry-cad-rendering.jpg', {}),
 'render-laptop':          (r'Rendering\laptop-3d-product-rendering.png', {}),
 'render-sapphire-ring':   (r'Rendering\sapphire-diamond-engagement-ring-3d-jewelry-rendering.jpg', {}),
 'render-shoe':            (r'Rendering\sports-shoe-concept-3d-product-modelling-rendering.png', {}),
 'bim-vibrating-screen':   (r'Scan to BIM\crusher-plant-vibrating-screen-point-cloud-to-3d-model.png', {}),
 'bim-hopper-pump-skid':   (r'Scan to BIM\hopper-pump-skid-point-cloud-to-bim-model.jpg', {}),
 'bim-storage-tank':       (r'Scan to BIM\industrial-storage-tank-point-cloud-to-bim-model.jpg', {}),
 'bim-pump-room':          (r'Scan to BIM\pump-room-piping-laser-scan-to-bim-model.png', {}),
 'bim-steel-platform':     (r'Scan to BIM\steel-structure-platform-point-cloud-to-bim-model.jpg', {}),
}

def content_box(im):
    diff = ImageChops.difference(im.convert('RGB'), Image.new('RGB', im.size, BG)).convert('L').point(lambda v: 255 if v > 12 else 0)
    return diff.getbbox() or (0, 0) + im.size

def frame(box, size, ratio=W / H, margin=0.07):
    l, t, r, b = box
    w, h = r - l, b - t
    l, t, r, b = l - w * margin, t - h * margin, r + w * margin, b + h * margin
    w, h = r - l, b - t
    cx, cy = (l + r) / 2, (t + b) / 2
    if w / h < ratio: w = h * ratio
    else: h = w / ratio
    return tuple(round(v) for v in (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))

def crop_padded(im, box):
    l, t, r, b = box
    canvas = Image.new('RGB', (r - l, b - t), BG)
    src = im.convert('RGB')
    canvas.paste(src, (-l, -t))
    return canvas

def save(im, name, q=80):
    path = os.path.join(OUT, name + '.webp')
    im.save(path, 'WEBP', quality=q, method=6)
    return os.path.getsize(path)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    total = 0
    for slug, roles in PAIRS.items():
        ims = {r: Image.open(os.path.join(SRC, p)) for r, p in roles.items()}
        sizes = {im.size for im in ims.values()}
        assert len(sizes) == 1, f'{slug}: images differ in size {sizes}'
        boxes = [content_box(im) for im in ims.values()]
        union = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
        box = frame(union, next(iter(sizes)))
        for role, im in ims.items():
            total += save(crop_padded(im, box).resize((W, H), Image.LANCZOS), f'{slug}-{role}')
    for name, (p, opt) in SINGLES.items():
        im = Image.open(os.path.join(SRC, p)).convert('RGB')
        w, h = im.size
        if 'cover' in opt:
            x0, y0, x1, y1 = opt['cover']
            bg = im.getpixel((w - 3, 3))
            ImageDraw.Draw(im).rectangle((int(x0 * w), int(y0 * h), w, h), fill=bg)
        if 'crop' in opt:
            x0, y0, x1, y1 = opt['crop']
            im = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
        if opt.get('trim'):
            im = crop_padded(im, frame(content_box(im), im.size, ratio=im.width / im.height, margin=0.12))
        im.thumbnail((1600, 1600), Image.LANCZOS)
        total += save(im, name, 82)
    print(f'{len(PAIRS)} sets + {len(SINGLES)} singles written to img/portfolio — {total / 1e6:.1f} MB')
