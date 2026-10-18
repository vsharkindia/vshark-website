"""
VShark customer collateral — no dependencies, run:  python collateral/build_collateral.py

Reads data/site.json (same content as the website) and writes
  • collateral/presentation.html  — 16:9 slide deck (arrow keys / click to present)
  • collateral/brochure-services.html  — two-page A4 brochure, services first
  • collateral/brochure-scanners.html  — two-page A4 brochure, 3D scanners for sale
then, if Microsoft Edge or Chrome is installed, exports each to a matching VShark-*.pdf,
and, if Node.js and pptxgenjs are available, writes the PowerPoint version
  • collateral/VShark-Presentation.pptx   (via collateral/build_pptx.js)
Pass --no-pdf / --no-pptx to skip those exports.
Photos are copied to collateral/assets/ as JPEG (needs Pillow: pip install pillow) to keep the PDFs small.
"""
import html, json, os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
D = json.load(open(ROOT / 'data' / 'site.json', encoding='utf-8'))
E = lambda t: html.escape(str(t), quote=True)
IND = {i['slug']: i for i in D['industries']}
PRJ = {p['slug']: p for p in D['projects']}
C = D['contact']
P = '../'          # pages live in collateral/, assets in the site root
SITE = 'vsharksolutions.com'

# Not in site.json — copied from the homepage testimonial strip (index.html).
QUOTES = [
    ("VShark Solutions was able to take a relatively poorly scanned object and convert it to a solid model with very accurate dimensions. Their surfacing skills are amazing, and the accuracy is perfect for our needs.", "Rachel Labonte", "Canada"),
    ("VSHARK provided the best engineering service we've ever experienced. Their attention to detail and quick responsiveness made working with them a pleasure. We've collaborated with them many times and will continue to do so.", "Mace Roper", "United States"),
    ("Working with VSHARK on a reverse engineering and 3D modelling project was impressive; their professionalism, clear communication, and dedication to quality made the entire process smooth and efficient.", "Benedikt Klein", "Germany"),
    ("Exceptional work and accuracy! I will be using VSHARK skills again; I highly recommend them if you need something converted accurately. No need to look further.", "Xander Elon", "United Kingdom"),
    ("VShark Solutions delivered exceptional work beyond my expectations! Their attention to detail and professionalism made the entire process seamless. I highly recommend them for any project.", "Ahtisham Muhammad", "Saudi Arabia"),
    ("Working with VSHARK Engineers was a fantastic experience. Their creative approach and attention to detail perfectly aligned with our brand, and they were always polite and cooperative throughout the project.", "Mariam Al-Ghayousi", "Dubai"),
]
COUNTRIES = 'India · UAE · Saudi Arabia · USA · UK · Germany · Canada'

PROCESS_IMG = [next(s['tile'] for s in D['services'] if s['slug'] == '3d-scanning'), 'img/portfolio/scan-impeller.webp',
               'img/portfolio/cad-impeller.webp', next(s['tile'] for s in D['services'] if s['slug'] == '3d-printing')]
PROCESS = [
    ('Capture', 'We scan the part, product or site — in our lab or on location.'),
    ('Process', 'Scans are aligned, cleaned and merged into usable, watertight data.'),
    ('Engineer', 'CAD, Class A surfaces, BIM or inspection built from that data.'),
    ('Deliver', 'CAD files, drawings and reports in the formats your team uses.'),
]

ABOUT = [
    "VShark Solutions provides state-of-the-art 3D scanning and 3D design services for businesses and individuals.",
    "We capture parts, products and spaces as accurate digital data — then engineer that data into editable CAD, "
    "flawless surfaces, BIM models, inspection reports, prototypes and photoreal visuals. One partner, from the physical "
    "object to the finished digital deliverable and back again.",
]

PAIRS = ['cylinder-head', 'impeller', 'motorcycle-tubular-frame', 'bumper']
VISUALS = [  # (project slug, image file, caption) — picks avoid third-party logos and photos of real people
    ('product-renders', 'rendeing2.webp', 'Product rendering'),
    ('eyewear-frame', 'eye-wear1.webp', 'Eyewear surfacing'),
    ('jewellery-renders', 'render-ram-ring.webp', 'Jewellery rendering'),
    ('character-sculpts', 'rendeing5.webp', 'Character sculpts'),
    ('spaces-exhibitions', 'render-exhibition.webp', 'Exhibition stands'),
]
VIMG = lambda k, f: next(i for i in PRJ[k]['images'] if i.endswith('/' + f))

USED = set()

def jpeg(path, size=1100):
    """WebP photos are stored uncompressed when printed to PDF, so use JPEG copies in collateral/assets/."""
    if not path.endswith('.webp'):
        return P + path
    from PIL import Image
    src, out = ROOT / path, HERE / 'assets' / (Path(path).stem + '.jpg')
    USED.add(out.name)
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        out.parent.mkdir(exist_ok=True)
        im = Image.open(src).convert('RGB')
        im.thumbnail((size, size), Image.LANCZOS)
        im.save(out, 'JPEG', quality=82, optimize=True, progressive=True)
    return 'assets/' + out.name

def img(path, alt='', cls=''):
    c = f' class="{cls}"' if cls else ''
    return f'<img src="{E(jpeg(path))}" alt="{E(alt)}"{c}>'

def stats():
    # 0.02 mm is the scanner specification, not a guaranteed service tolerance (handoff A13)
    return [('0.02', 'mm', 'Scanner precision (up to)'), (str(len(D['services'])), '', 'Core services'),
            (str(len(D['industries'])), '', 'Industries served'), ('7', '', 'Countries served')]

def phones(sep=' · '):
    return sep.join(f'{E(p["display"])} ({E(p["label"])})' for p in C['phones'])

# ================================================================ presentation
def chrome(n, label, dark=False):
    logo = 'img/vshark-logo-white.png' if dark else 'img/vshark-logo.png'
    return (f'<div class="chrome">{img(logo, "VShark Solutions Pvt Ltd")}'
            f'<span class="mono">{E(label)} · {SITE}</span><span class="mono">{n:02d}</span></div>')

def deck():
    S = []
    total_svc = len(D['services'])
    pc = PRJ['cylinder-head']

    S.append(f'''
<section class="slide slide--dark">
  <div class="cover">
    <div>
      {img('img/vshark-logo-white.png', 'VShark Solutions Pvt Ltd', 'cover__logo')}
      <p class="mono kicker">3D Scanning &amp; 3D Design Services</p>
      <h1 class="h1">We capture reality.<br><em>Then we engineer it.</em></h1>
      <p class="lead">Precise 3D scanning and innovative 3D design that transform physical parts, products and spaces into digital models — and back into physical prototypes.</p>
      <div class="cover__meta mono">
        <span>Email<b>{E(C['email'])}</b></span>
        {''.join(f'<span>{E(p["label"])}<b>{E(p["display"])}</b></span>' for p in C['phones'])}
      </div>
    </div>
    <div class="cover__pair">
      <figure>{img(pc['before'], 'Cylinder head 3D scan')}<figcaption class="mono">01 · Scan</figcaption></figure>
      <figure>{img(pc['after'], 'Cylinder head CAD model')}<figcaption class="mono">02 · CAD</figcaption></figure>
    </div>
  </div>
</section>''')

    st = ''.join(f'<div class="stat"><b>{a}<small>{u}</small></b><span class="mono">{E(l)}</span></div>' for a, u, l in stats())
    S.append(f'''
<section class="slide">
  <div class="about">
    <div>
      <p class="mono kicker">( 01 ) — Who we are</p>
      <h2 class="h2">From physical<br>to digital <em>and back.</em></h2>
      {''.join(f'<p class="lead">{E(t)}</p>' for t in ABOUT)}
    </div>
    <div class="stats">{st}</div>
  </div>
  {chrome(2, 'About VShark')}
</section>''')

    cards = ''.join(f'''
    <article class="svc">{img(s['tile'], s['alt'])}<div>
      <span class="mono">{i:02d}</span><h3 class="h3">{E(s['name'])}</h3><p>{E(s['tagline'])}</p></div></article>'''
        for i, s in enumerate(D['services'], 1))
    S.append(f'''
<section class="slide">
  <div class="head">
    <div><p class="mono kicker">( 02 ) — Services</p><h2 class="h2">Seven services, <em>one partner.</em></h2></div>
    <p class="lead">Use one service on its own, or hand us the whole job — from first scan to final file.</p>
  </div>
  <div class="svc-grid">{cards}
    <article class="svc svc--cta"><h3 class="h3">End-to-end delivery</h3><p>Scan, engineer, inspect, print and render — under one roof, with one point of contact.</p></article>
  </div>
  {chrome(3, 'Services')}
</section>''')

    steps = ''.join(f'<div class="step">{img(PROCESS_IMG[i - 1], t)}<div class="num">{i:02d}</div><h3 class="h3">{E(t)}</h3><p class="small">{E(d)}</p></div>'
                    for i, (t, d) in enumerate(PROCESS, 1))
    S.append(f'''
<section class="slide">
  <p class="mono kicker">( 03 ) — How we work</p>
  <h2 class="h2">A simple, four-step<br>process — <em>scan to solution.</em></h2>
  <div class="process">{steps}</div>
  {chrome(4, 'Process')}
</section>''')

    n = 5
    for i, s in enumerate(D['services'], 1):
        pts = ''.join(f'<li><b>{E(a)}</b><span>{E(b)}</span></li>' for a, b in s['points'])
        dl = ''.join(f'<span class="chip">{E(x)}</span>' for x in s['deliverables'])
        ind = ''.join(f'<span class="chip chip--ind">{E(IND[x]["name"])}</span>' for x in s['industries'] if x in IND)
        S.append(f'''
<section class="slide">
  <div class="detail">
    <div class="detail__left">
      <div class="detail__img">{img(s['image'], s['alt'])}<span class="mono">Service {i:02d} / {total_svc:02d}</span></div>
      <p class="mono label">Deliverables</p><div class="chips">{dl}</div>
      <p class="mono label">Industries</p><div class="chips">{ind}</div>
    </div>
    <div class="detail__body">
      <p class="mono kicker">( 02.{i} ) — Services</p>
      <h2 class="h2">{E(s['name'])}</h2>
      <p class="tagline">{E(s['tagline'])}</p>
      <p class="lead">{E(s['intro'])}</p>
      <ul class="points">{pts}</ul>
    </div>
  </div>
  {chrome(n, s['name'])}
</section>''')
        n += 1

    pairs = ''.join(f'''
    <div class="pair">
      <figure>{img(PRJ[k]['before'], PRJ[k]['title'] + ' scan')}<figcaption>Scan</figcaption></figure>
      <figure>{img(PRJ[k]['after'], PRJ[k]['title'] + ' CAD')}<figcaption>CAD</figcaption></figure>
      <p><b>{E(PRJ[k]['title'])}</b>{E(PRJ[k]['summary'])}</p>
    </div>''' for k in PAIRS)
    S.append(f'''
<section class="slide">
  <div class="head">
    <div><p class="mono kicker">( 04 ) — Portfolio</p><h2 class="h2">Scan in. <em>CAD out.</em></h2></div>
    <p class="lead">Real parts we have captured and rebuilt as editable, manufacturable CAD.</p>
  </div>
  <div class="pairs">{pairs}</div>
  {chrome(n, 'Portfolio — reverse engineering')}
</section>''')
    n += 1

    mos = ''.join(f'<figure>{img(VIMG(k, ix), cap)}<figcaption>{E(cap)}<span>{E(PRJ[k]["summary"])}</span></figcaption></figure>'
                  for k, ix, cap in VISUALS)
    S.append(f'''
<section class="slide">
  <div class="head">
    <div><p class="mono kicker">( 04 ) — Portfolio</p><h2 class="h2">Design &amp; <em>visualisation.</em></h2></div>
    <p class="lead">Surfacing, sculpting and photoreal rendering — visuals that sell a product before it is made.</p>
  </div>
  <div class="mosaic">{mos}</div>
  {chrome(n, 'Portfolio — design & visualisation')}
</section>''')
    n += 1

    inds = ''.join(f'<article class="ind">{img(d["portrait"], d["alt"])}<div><span class="mono">{i:02d}</span><h3 class="h3">{E(d["name"])}</h3><p>{E(d["line"])}</p></div></article>'
                   for i, d in enumerate(D['industries'], 1))
    S.append(f'''
<section class="slide">
  <div class="head">
    <div><p class="mono kicker">( 05 ) — Industries</p><h2 class="h2">Industries <em>we serve.</em></h2></div>
    <p class="lead">Six sectors, one standard of precision.</p>
  </div>
  <div class="ind-grid">{inds}</div>
  {chrome(n, 'Industries')}
</section>''')
    n += 1

    prods = ''.join(f'''<article>{img(p['image'], p['name'])}<div><h3 class="h3">{E(p['name'])}</h3><p class="type">{E(p['type'])}</p>
      <p class="fig">{E(p['figure'])}<small>{E(p['unit'])}</small></p></div></article>''' for p in D['products'])
    keep = ['High-speed scanning', 'Max. scanning speed', 'Max. scanning field', 'Max. resolution', 'Volume accuracy', 'Recommended sample size', 'Output formats']
    rows = ''.join(f'<tr><th>{E(r[0])}</th>' + ''.join(f'<td>{E(c)}</td>' for c in r[1:]) + '</tr>'
                   for r in D['productSpecs'] if r[0] in keep)
    S.append(f'''
<section class="slide">
  <div class="head">
    <div><p class="mono kicker">( 06 ) — Products</p><h2 class="h2">Professional <em>3D scanners.</em></h2></div>
    <p class="lead">Vertex blue-laser and optical-tracking scanners — now available from VShark, with training and support.</p>
  </div>
  <div class="prod">{prods}</div>
  <table class="specs"><thead><tr><th>Specification</th>{''.join(f'<th>{E(p["name"])}</th>' for p in D['products'])}</tr></thead><tbody>{rows}</tbody></table>
  <p class="pc"><span class="mono">Recommended PC</span>{E(D['productPc'])}</p>
  {chrome(n, 'Products')}
</section>''')
    n += 1

    qs = ''.join(f'<blockquote class="quote"><p>{E(q)}</p><footer>{E(w)}<span>{E(c)}</span></footer></blockquote>' for q, w, c in QUOTES)
    S.append(f'''
<section class="slide">
  <div class="head">
    <div><p class="mono kicker">( 07 ) — What clients say</p><h2 class="h2">Trusted <em>worldwide.</em></h2></div>
    <p class="lead mono nowrap">{COUNTRIES}</p>
  </div>
  <div class="quotes">{qs}</div>
  {chrome(n, 'Testimonials')}
</section>''')
    n += 1

    ph = ''.join(f'<li><span class="mono">{E(p["label"])}</span><a href="tel:{E(p["tel"])}">{E(p["display"])}</a></li>' for p in C['phones'])
    S.append(f'''
<section class="slide slide--dark">
  <div class="contact">
    <div>
      {img('img/vshark-logo-white.png', 'VShark Solutions Pvt Ltd', 'cover__logo')}
      <p class="mono kicker">( 08 ) — Get in touch</p>
      <h2 class="h1">Let&rsquo;s start<br><em>your project.</em></h2>
      <p class="lead">Send us a photo, drawing or the part itself — we&rsquo;ll come back with the right approach, timeline and quote.</p>
    </div>
    <ul class="contact__list">
      <li><span class="mono">Email</span><a href="mailto:{E(C['email'])}">{E(C['email'])}</a></li>
      {ph}
      <li><span class="mono">WhatsApp</span><a href="https://wa.me/{E(C['whatsapp'])}">+{E(C['whatsapp'][:2])} {E(C['whatsapp'][2:7])} {E(C['whatsapp'][7:])}</a></li>
      <li><span class="mono">Web</span><a href="https://{SITE}">{SITE}</a></li>
    </ul>
  </div>
  {chrome(n, 'Contact', dark=True)}
</section>''')

    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>VShark Solutions — Company Presentation</title>
<link rel="icon" href="{P}img/favicon-32.png">
<link rel="stylesheet" href="deck.css">
</head><body>
<!-- GENERATED by collateral/build_collateral.py from data/site.json — edit those, not this file. -->
<main class="deck">{''.join(S)}
</main>
<div class="nav"><button type="button" data-go="-1" aria-label="Previous slide">&larr;</button><span id="count"></span><button type="button" data-go="1" aria-label="Next slide">&rarr;</button></div>
<script>
(function () {{
  var slides = [].slice.call(document.querySelectorAll('.slide')), i = 0, count = document.getElementById('count');
  function fit() {{
    var s = Math.min(innerWidth / 1280, innerHeight / 720) * 0.94;
    slides.forEach(function (el) {{ el.style.transform = 'translate(-50%,-50%) scale(' + s + ')'; }});
  }}
  function show(n) {{
    i = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach(function (el, k) {{ el.classList.toggle('is-current', k === i); }});
    count.textContent = (i + 1) + ' / ' + slides.length;
    history.replaceState(null, '', '#' + (i + 1));
  }}
  addEventListener('resize', fit);
  addEventListener('keydown', function (e) {{
    if (['ArrowRight', 'ArrowDown', 'PageDown', ' '].indexOf(e.key) > -1) {{ e.preventDefault(); show(i + 1); }}
    else if (['ArrowLeft', 'ArrowUp', 'PageUp'].indexOf(e.key) > -1) {{ e.preventDefault(); show(i - 1); }}
    else if (e.key === 'Home') show(0); else if (e.key === 'End') show(slides.length - 1);
    else if (e.key === 'f') document.documentElement.requestFullscreen && document.documentElement.requestFullscreen();
  }});
  document.querySelector('.nav').addEventListener('click', function (e) {{
    var b = e.target.closest('button'); if (b) show(i + +b.dataset.go);
  }});
  document.querySelector('.deck').addEventListener('click', function (e) {{
    if (!e.target.closest('a')) show(i + (e.clientX < innerWidth / 3 ? -1 : 1));
  }});
  fit(); show((parseInt(location.hash.slice(1), 10) || 1) - 1);
}})();
</script>
</body></html>
'''

# ================================================================ brochures
def b_head(title):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>VShark Solutions — {E(title)}</title>
<link rel="icon" href="{P}img/favicon-32.png">
<link rel="stylesheet" href="brochure.css">
</head><body>
<!-- GENERATED by collateral/build_collateral.py from data/site.json — edit those, not this file. -->
'''

def b_cta(heading, text):
    ph = ''.join(f'<li><span class="mono">{E(p["label"])}</span><a href="tel:{E(p["tel"])}">{E(p["display"])}</a></li>' for p in C['phones'])
    return f'''<footer class="cta">
    <div>
      {img('img/vshark-logo-white.png', 'VShark Solutions Pvt Ltd')}
      <h2>{heading}</h2>
      <p>{text}</p>
    </div>
    <ul>
      <li><span class="mono">Email</span><a href="mailto:{E(C['email'])}">{E(C['email'])}</a></li>
      <li><span class="mono">Web</span><a href="https://{SITE}">{SITE}</a></li>
      {ph}
    </ul>
  </footer>'''

def b_foot():
    return f'<div class="foot">{img("img/vshark-logo.png", "VShark")}<span class="mono">{E(C["email"])} · {phones()}</span></div>'

def services_brochure():
    pc = PRJ['cylinder-head']
    st = ''.join(f'<div><b>{a}<small>{u}</small></b><span class="mono">{E(l)}</span></div>' for a, u, l in stats())
    svcs = ''.join(f'''
      <article class="svc">{img(s['image'], s['alt'])}<div>
        <h3><span>{i:02d}</span>{E(s['name'])}</h3><p>{E(s['tagline'])}</p>
        <small>{E(' · '.join(s['deliverables'][:3]))}</small></div></article>'''
        for i, s in enumerate(D['services'], 1))
    steps = ''.join(f'<div class="step">{img(PROCESS_IMG[i - 1], t)}<span class="mono">Step {i:02d}</span><b>{E(t)}</b><p>{E(d)}</p></div>'
                    for i, (t, d) in enumerate(PROCESS, 1))
    pairs = ''.join(f'''
      <div class="pair">
        <figure>{img(PRJ[k]['before'], PRJ[k]['title'] + ' scan')}<figcaption>Scan</figcaption></figure>
        <figure>{img(PRJ[k]['after'], PRJ[k]['title'] + ' CAD')}<figcaption>CAD</figcaption></figure>
        <p><b>{E(PRJ[k]['title'])}</b>{E(PRJ[k]['summary'])}</p>
      </div>''' for k in PAIRS)
    strip = ''.join(f'<figure>{img(VIMG(k, ix), cap)}<figcaption>{E(cap)}</figcaption></figure>' for k, ix, cap in VISUALS[:4])
    inds = ''.join(f'<article>{img(d["square"], d["alt"])}<div><h3>{E(d["name"])}</h3><p>{E(d["line"])}</p></div></article>' for d in D['industries'])
    prods = ''.join(f'<article>{img(p["image"], p["name"])}<div><h3>{E(p["name"])}</h3><p>{E(p["type"])}</p></div><b>{E(p["figure"])}<small>{E(p["unit"])}</small></b></article>' for p in D['products'])
    qs = ''.join(f'<blockquote class="quote"><p>&ldquo;{E(q)}&rdquo;</p><footer>{E(w)}<span>{E(c)}</span></footer></blockquote>' for q, w, c in (QUOTES[0], QUOTES[2]))
    return f'''{b_head('Services Brochure')}
<section class="page">
  <header class="hero">
    <div>
      {img('img/vshark-logo-white.png', 'VShark Solutions Pvt Ltd', 'hero__logo')}
      <h1>We capture reality.<br><em>Then we engineer it.</em></h1>
      <p>{E(ABOUT[0])} {E(ABOUT[1])}</p>
    </div>
    <div class="hero__pair">
      <figure>{img(pc['before'], 'Cylinder head 3D scan')}<figcaption>Scan</figcaption></figure>
      <figure>{img(pc['after'], 'Cylinder head CAD model')}<figcaption>CAD</figcaption></figure>
    </div>
  </header>
  <div class="stats">{st}</div>
  <div class="pad">
    <div class="sec"><span class="mono">01</span><h2>Our services</h2><p>Use one on its own, or hand us the whole job.</p></div>
    <div class="svc-list">{svcs}
      <article class="svc--cta"><h3>End-to-end, one partner</h3><p>Scan, engineer, inspect, print and render under one roof — with one point of contact.</p></article>
    </div>
    <div class="sec"><span class="mono">02</span><h2>How we work</h2><p>Scan to solution in four steps.</p></div>
    <div class="process">{steps}</div>
  </div>
  {b_foot()}
</section>

<section class="page">
  <div class="pad back-top">
    <div class="sec"><span class="mono">03</span><h2>Scan in. <em>CAD out.</em></h2><p>Real parts captured and rebuilt as editable CAD.</p></div>
    <div class="pairs">{pairs}</div>
    <div class="sec"><span class="mono">04</span><h2>Design &amp; visualisation</h2><p>Surfacing, sculpting and photoreal rendering.</p></div>
    <div class="strip">{strip}</div>
    <div class="sec"><span class="mono">05</span><h2>Industries we serve</h2><p>Six sectors, one standard of precision.</p></div>
    <div class="ind">{inds}</div>
    <div class="lower">
      <div>
        <div class="sec"><span class="mono">06</span><h2>3D scanners</h2></div>
        <div class="prod">{prods}</div>
      </div>
      <div>
        <div class="sec"><span class="mono">07</span><h2>What clients say</h2></div>
        <div class="quotes">{qs}</div>
        <p class="reach mono">Clients in {COUNTRIES}</p>
      </div>
    </div>
  </div>
  {b_cta('Let&rsquo;s start <em>your project.</em>', 'Send us a photo, drawing or the part itself — we&rsquo;ll reply with the right approach, timeline and quote.')}
</section>
</body></html>
'''

# ---------------------------------------------------------------- scanners brochure
# Copy that is not in site.json. Claims mirror the website's products page
# ("sold, set up and supported by VShark's scanning engineers", "we can arrange a live demo").
SCAN_MODES = [  # (name, laser lines — see productSpecs, what it is for)
    ('High-speed', '26 or 50 crossed blue laser lines', 'Captures large surfaces fast.'),
    ('Precision', '7 parallel blue laser lines', 'For fine features and sharp edges.'),
    ('Deep-hole', '1 single blue laser line', 'Reaches into holes and deep cavities.'),
]
WHY_US = [
    ('Sold by scanning engineers', 'We scan and model parts for clients every day — we know the whole workflow, not just the hardware.'),
    ('Live demo on your parts', 'Send us your parts and use case; we recommend the right model and show it working.'),
    ('Set-up, training & warranty', 'We install the scanner at your site, train your team at delivery, and every scanner has a 12-month warranty.'),
    ('Support in India & UAE', 'Local help by phone and WhatsApp — plus our service team for overflow work.'),
]
APPLICATIONS = [
    ('Reverse engineering', 'Scan legacy parts and rebuild them as CAD.'),
    ('Quality inspection', 'Compare production parts with CAD in colour maps.'),
    ('Product design', 'Capture prototypes, clay models and existing parts.'),
    ('Digital archiving', 'Record moulds, tools and heritage objects.'),
]
SCAN_SAMPLES = ['cylinder-head', 'impeller', 'motorcycle-tubular-frame', 'bumper']   # each project's scan image

def spec(label, i):
    return next(r[i + 1] for r in D['productSpecs'] if r[0] == label)

def scanners_brochure():
    hero = D['products'][1]
    st = [('0.020', 'mm', 'Highest precision'), ('7.1', 'M', 'Measurements per second'),
          ('0.01', 'mm', 'Max. resolution'), ('8', 'm', 'Largest object (Tracker)')]
    st = ''.join(f'<div><b>{a}<small>{u}</small></b><span class="mono">{E(l)}</span></div>' for a, u, l in st)
    keys = [('Laser lines', 'High-speed scanning'), ('Speed', 'Max. scanning speed'),
            ('Scan field', 'Max. scanning field'), ('Sample size', 'Recommended sample size')]
    cards = ''.join(f'''
      <article class="pcard">
        <div class="pcard__img">{img(p['image'], p['name'])}<span class="mono">{i + 1:02d}</span></div>
        <h3>{E(p['name'])}</h3><p class="pcard__type">{E(p['type'])}</p>
        <p class="pcard__sum">{E(p['summary'])}</p>
        <p class="pcard__fig">{E(p['figure'])}<small>{E(p['unit'])}</small></p>
        <dl>{''.join(f'<dt>{E(k)}</dt><dd>{E(spec(lab, i))}</dd>' for k, lab in keys)}</dl>
      </article>''' for i, p in enumerate(D['products']))
    modes = ''.join(f'''<div class="mode"><span class="mono">Mode {i:02d}</span><b>{E(t)}</b>
        <em>{E(lines)}</em><p>{E(d)}</p></div>'''
        for i, (t, lines, d) in enumerate(SCAN_MODES, 1))
    why = ''.join(f'<div class="why"><span class="mono">{i:02d}</span><b>{E(t)}</b><p>{E(d)}</p></div>' for i, (t, d) in enumerate(WHY_US, 1))
    samples = ''.join(f'<figure>{img(PRJ[k]["before"], PRJ[k]["title"])}<figcaption>{E(PRJ[k]["title"])}</figcaption></figure>' for k in SCAN_SAMPLES)
    apps = ''.join(f'<div class="app"><b>{E(t)}</b><p>{E(d)}</p></div>' for t, d in APPLICATIONS)
    head = ''.join(f'<th>{E(p["name"])}</th>' for p in D['products'])
    rows = ''.join(f'<tr><th>{E(r[0])}</th>' + ''.join(f'<td>{E(c)}</td>' for c in r[1:]) + '</tr>' for r in D['productSpecs'])
    svcs = ''.join(f'<li><span class="mono">{i:02d}</span>{E(s["name"])}</li>' for i, s in enumerate(D['services'], 1))
    flow = ' <i>&rarr;</i> '.join(f'<b>{E(t)}</b>' for t, _ in PROCESS)

    return f'''{b_head('3D Scanners Brochure')}
<section class="page">
  <header class="hero hero--prod">
    <div>
      {img('img/vshark-logo-white.png', 'VShark Solutions Pvt Ltd', 'hero__logo')}
      <p class="mono hero__kick">Vertex 3D scanners · now from VShark</p>
      <h1>Professional 3D scanners.<br><em>Backed by scanning engineers.</em></h1>
      <p>Vertex blue-laser and optical-tracking scanners — sold, set up and supported by the VShark team that scans and models parts for clients every day.</p>
    </div>
    <div class="hero__prod">{img(hero['image'], hero['name'])}<span class="mono">{E(hero['name'])}</span></div>
  </header>
  <div class="stats">{st}</div>
  <div class="pad">
    <div class="sec"><span class="mono">01</span><h2>Choose your scanner</h2><p>Three models, one family — all Class II eye-safe blue laser.</p></div>
    <div class="pcards">{cards}</div>
    <div class="sec"><span class="mono">02</span><h2>Three scan modes in every model</h2></div>
    <div class="modes">{modes}</div>
    <div class="sec"><span class="mono">03</span><h2>Why buy from VShark</h2></div>
    <div class="whys">{why}</div>
  </div>
  {b_foot()}
</section>

<section class="page">
  <div class="pad back-top">
    <div class="sec"><span class="mono">04</span><h2>What you can capture</h2><p>Scan data from parts captured by the VShark team.</p></div>
    <div class="strip strip--scan">{samples}</div>
    <div class="apps">{apps}</div>
    <div class="sec"><span class="mono">05</span><h2>Specifications</h2><p>Compare side by side.</p></div>
    <table class="specs"><thead><tr><th>Specification</th>{head}</tr></thead><tbody>{rows}</tbody></table>
    <p class="note"><b>Recommended computer:</b> {E(D['productPc'])}. Specifications from the manufacturer and subject to change.</p>
    <div class="also">
      <div>
        <div class="sec"><span class="mono">06</span><h2>Need it scanned instead?</h2></div>
        <p>Our service team handles one-off jobs and overflow work — from a single scan to finished CAD, inspection reports and prints.</p>
        <p class="flow">{flow}</p>
      </div>
      <ul class="svc-names">{svcs}</ul>
    </div>
  </div>
  {b_cta('Book a <em>live demo.</em>', 'Send us your parts and use case — we&rsquo;ll recommend a model, show it scanning and send a quote.')}
</section>
</body></html>
'''

# ================================================================ PowerPoint export
def deck_data():
    """Everything build_pptx.js needs, with image paths relative to collateral/."""
    pj = lambda k: PRJ[k]
    return {
        'site': SITE, 'contact': C, 'about': ABOUT, 'countries': COUNTRIES,
        'stats': stats(),
        'process': [{'title': t, 'text': d, 'image': jpeg(PROCESS_IMG[i])} for i, (t, d) in enumerate(PROCESS)],
        'services': [dict(s, image=jpeg(s['image']), tile=jpeg(s['tile']), industries=[IND[x]['name'] for x in s['industries'] if x in IND])
                     for s in D['services']],
        'industries': [dict(i, image=jpeg(i['portrait'])) for i in D['industries']],
        'products': [dict(p, image=jpeg(p['image'])) for p in D['products']],
        'specs': [r for r in D['productSpecs'] if r[0] in ('High-speed scanning', 'Max. scanning speed', 'Max. scanning field',
                  'Max. resolution', 'Volume accuracy', 'Recommended sample size', 'Output formats')],
        'pc': D['productPc'],
        'cover': {'scan': jpeg(pj('cylinder-head')['before']), 'cad': jpeg(pj('cylinder-head')['after'])},
        'pairs': [{'title': pj(k)['title'], 'summary': pj(k)['summary'], 'scan': jpeg(pj(k)['before']), 'cad': jpeg(pj(k)['after'])}
                  for k in PAIRS],
        'visuals': [{'caption': cap, 'summary': pj(k)['summary'], 'image': jpeg(VIMG(k, ix))} for k, ix, cap in VISUALS],
        'quotes': [{'text': q, 'name': w, 'place': c} for q, w, c in QUOTES],
        'logo': jpeg('img/vshark-logo.png'), 'logoWhite': jpeg('img/vshark-logo-white.png'),
    }

def to_pptx(out):
    """Returns False when Node or pptxgenjs is missing (set NODE_PATH to the node_modules holding pptxgenjs)."""
    node = shutil.which('node')
    if not node:
        return False
    from PIL import Image
    data, dims = deck_data(), {}
    def walk(v):  # pixel size of every image, so pptxgenjs can crop to fill without distorting
        if isinstance(v, dict): [walk(x) for x in v.values()]
        elif isinstance(v, list): [walk(x) for x in v]
        elif isinstance(v, str) and v.endswith(('.jpg', '.png')) and v not in dims:
            dims[v] = Image.open(HERE / v).size
    walk(data)
    data['dims'] = dims
    r = subprocess.run([node, str(HERE / 'build_pptx.js'), str(out)], input=json.dumps(data),
                       text=True, encoding='utf-8', cwd=HERE, capture_output=True)
    if r.returncode == 3:
        return False
    if r.returncode:
        sys.exit(r.stderr)
    return True

# ================================================================ PDF export
def find_browser():
    cands = [shutil.which(n) for n in ('msedge', 'chrome', 'google-chrome', 'chromium')] + [
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge']
    return next((c for c in cands if c and os.path.isfile(c)), None)

def to_pdf(browser, src, out):
    subprocess.run([browser, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                    '--virtual-time-budget=8000', '--run-all-compositor-stages-before-draw',
                    f'--print-to-pdf={out}', src.as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)

if __name__ == '__main__':
    OUT = [('presentation.html', deck, 'VShark-Presentation.pdf'),
           ('brochure-services.html', services_brochure, 'VShark-Brochure-Services.pdf'),
           ('brochure-scanners.html', scanners_brochure, 'VShark-Brochure-Scanners.pdf')]
    for name, build, _ in OUT:
        body = build()
        (HERE / name).write_text(body, encoding='utf-8', newline='\n')
        print('wrote', f'collateral/{name}')
    for f in (HERE / 'assets').glob('*.jpg'):  # drop photos no longer used
        if f.name not in USED:
            f.unlink()
    if '--no-pptx' not in sys.argv:
        if to_pptx(HERE / 'VShark-Presentation.pptx'):
            print('wrote collateral/VShark-Presentation.pptx')
        else:
            print('Skipped PowerPoint: needs Node.js and pptxgenjs (npm install pptxgenjs, or set NODE_PATH).')
    if '--no-pdf' in sys.argv:
        sys.exit(0)
    b = find_browser()
    if not b:
        print('No Edge/Chrome found — open the HTML files and use Print > Save as PDF instead.')
        sys.exit(0)
    for name, _, pdf in OUT:
        to_pdf(b, HERE / name, HERE / pdf)
        print('wrote', f'collateral/{pdf}')
