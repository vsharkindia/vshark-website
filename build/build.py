"""
VShark site builder — no dependencies, run:  python build/build.py

Reads data/site.json and
  • writes every inner page (services/, products/, portfolio/, industries/, contact.html, thanks.html)
  • refreshes the marked regions of the hand-built homepage (index.html):
      <!-- @NAME --> … <!-- /@NAME -->   for header, products, services, industries, footer
  • fingerprints css/js links (?v=<hash>) so browsers always pick up changes.
Output is plain static HTML committed to the repo; Netlify needs no build step.
"""
import datetime, hashlib, html, json, os, re, sys
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, 'data', 'site.json'), encoding='utf-8'))
E = lambda t: html.escape(str(t), quote=True)
SVC = {s['slug']: s for s in D['services']}
IND = {i['slug']: i for i in D['industries'] + D.get('filterIndustries', [])}
C = D['contact']

def ver(path):
    # line endings are normalised so a Windows checkout (CRLF) gives the same hash as Linux/Netlify (LF)
    with open(os.path.join(ROOT, path), 'rb') as f:
        return hashlib.md5(f.read().replace(b'\r\n', b'\n')).hexdigest()[:8]

def asset(path, P):
    return f'{P}{path}?v={ver(path)}'

# ---------------------------------------------------------------- icons
ICON = {
 'phone': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
 'mail': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/></svg>',
 'wa': '<svg viewBox="0 0 32 32" class="fill" aria-hidden="true"><path d="M16 3a13 13 0 0 0-11.2 19.6L3 29l6.6-1.7A13 13 0 1 0 16 3zm0 23.7c-2 0-4-.6-5.7-1.6l-.4-.2-3.9 1 1-3.8-.3-.4A10.7 10.7 0 1 1 16 26.7zm5.9-8c-.3-.2-1.9-1-2.2-1-.3-.1-.5-.2-.7.2l-1 1.2c-.2.2-.4.2-.7.1a8.8 8.8 0 0 1-4.4-3.8c-.3-.6.3-.5.9-1.7.1-.2 0-.4 0-.5l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4-.3.3-1.2 1.1-1.2 2.8s1.2 3.3 1.4 3.5c.2.2 2.4 3.7 5.9 5.2 2.2.9 3 1 4.1.8.7-.1 1.9-.8 2.2-1.5.3-.8.3-1.4.2-1.5l-.6-.3z"/></svg>',
 'ig': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="2" width="20" height="20" rx="5"/><path d="M16 11.4A4 4 0 1 1 12.6 8a4 4 0 0 1 3.4 3.4z"/><path d="M17.5 6.5h.01"/></svg>',
 'fb': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>',
 'in': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg>',
 'yt': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22.5 6.4a2.8 2.8 0 0 0-2-2C18.8 4 12 4 12 4s-6.8 0-8.5.4a2.8 2.8 0 0 0-2 2A29 29 0 0 0 1 12a29 29 0 0 0 .5 5.6 2.8 2.8 0 0 0 2 2c1.7.4 8.5.4 8.5.4s6.8 0 8.5-.4a2.8 2.8 0 0 0 2-2A29 29 0 0 0 23 12a29 29 0 0 0-.5-5.6z"/><path d="m9.8 15.5 5.7-3.5-5.7-3.5z"/></svg>',
 'shop': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9 4.5 4h15L21 9"/><path d="M3 9a3 3 0 0 0 6 0 3 3 0 0 0 6 0 3 3 0 0 0 6 0"/><path d="M5 11.5V20h14v-8.5M10 20v-5h4v5"/></svg>',
 'web': '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20"/></svg>',
 'arrow': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
 'down': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
 'specs': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/></svg>',
 'play': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>',
 'pin': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>',
 'file': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M12 12v6M9 15l3 3 3-3"/></svg>',
}
A = ICON['arrow']
# default pre-filled WhatsApp message (from the Meta ads brief); context-specific links pass their own
WA_DEFAULT = 'Hi VShark, I need 3D scanning / reverse engineering for: '
wa_link = lambda msg=None: f'https://wa.me/{C["whatsapp"]}?text={quote(WA_DEFAULT if msg is None else msg, safe="")}'

# ---------------------------------------------------------------- meta (handoff part C)
META = {
    '': ('3D Scanning & Reverse Engineering Services | VShark Solutions',
         '3D scanning, reverse engineering, Scan to BIM, Class A surfacing and 3D inspection services in India and the UAE. India distributor of JINUOSH Vertex scanners.'),
    '3d-scanning-services-coimbatore.html': ('3D Scanning Services in Coimbatore | VShark Solutions',
         'On-site 3D scanning in Coimbatore for parts, moulds and castings. STL and editable CAD files, reverse engineering and CMM arm inspection. Get a quote.'),
    'products/index.html': ('Vertex 3D Scanners in India | JINUOSH Distributor | VShark',
         'Buy JINUOSH Vertex3D, Vertex3D Pro and Vertex Tracker 3D scanners in India from the India distributor. Compare specs, request a quote or book a demo.'),
    'services/index.html': ('3D Scanning & 3D Design Services | VShark Solutions',
         '3D scanning, reverse engineering, Scan to BIM, Class A surfacing, digital metrology, 3D printing and product rendering for India, the UAE and worldwide.'),
    'services/3d-scanning.html': ('3D Scanning Services in India & UAE | VShark Solutions',
         'Accurate 3D scanning of parts, castings, vehicles and large objects. Get mesh, point cloud or CAD-ready data from Coimbatore and the UAE. Free quote.'),
    'services/reverse-engineering.html': ('Reverse Engineering Services – Scan to CAD | VShark',
         'Turn worn, legacy or undocumented parts into editable, manufacturable CAD (STEP, IGES and other neutral formats). Reverse engineering for India and the UAE.'),
    # handoff wording said "your laser-scan point clouds" — corrected: VShark also does the site scanning
    'services/scan-to-bim.html': ('Scan to BIM Services – Point Cloud to Revit | VShark',
         'We laser-scan plant rooms, piping and buildings, or use your point cloud, and model them as accurate Autodesk Revit BIM for retrofit and facility management.'),
    'services/class-a-surfacing.html': ('Class A Surfacing Services | Automotive Surfaces | VShark',
         'Class A surfacing for automotive and consumer products: G2/G3-continuous surfaces checked with zebra and curvature analysis, ready for tooling.'),
    'services/digital-metrology.html': ('3D Inspection & Digital Metrology Services | VShark',
         'Scan-to-CAD deviation colour maps, GD&T checks and first-article inspection reports for castings, moulded and machined parts.'),
    'services/3d-printing.html': ('3D Printing Services – Prototypes & Parts | VShark',
         'FDM and SLA 3D printing of prototypes, functional parts, scale models and jewellery masters, from your CAD or a 3D scan of an existing part.'),
    'services/product-rendering.html': ('Product Rendering & 3D Visualisation | VShark Solutions',
         'Photorealistic product renders, exploded views and jewellery visuals created from CAD, so you can market a product before it is made.'),
    'industries/index.html': ('Industries We Serve – 3D Scanning & CAD | VShark',
         '3D scanning, reverse engineering and inspection for aerospace, automobile, construction, healthcare, education and jewellery.'),
    'industries/aerospace.html': ('3D Scanning for Aerospace Components | VShark Solutions',
         'Inspection and reverse engineering of turbine blades, impellers, ducts, fairings and UAV parts, from high-accuracy 3D scan data.'),
    'industries/automobile.html': ('3D Scanning & Reverse Engineering for Automotive | VShark',
         'Body surfacing, chassis and casting digitisation, fixture design and scan-based inspection for OEMs, tier suppliers and motorsport.'),
    'industries/construction.html': ('Scan to BIM for Construction & Facilities | VShark',
         'Revit BIM models from point cloud data of buildings, plant rooms and industrial structures, for renovation, retrofit and asset management.'),
    'industries/healthcare.html': ('3D Scanning for Healthcare & Medical Devices | VShark',
         '3D scanning and design for medical devices, orthotics, prosthetics and custom-fit parts, from scan to CAD to 3D print.'),
    'industries/education.html': ('3D Scanning for Universities & Labs | VShark Solutions',
         '3D scanners, training and scanning services for engineering colleges, research labs and design schools across India and the UAE.'),
    'industries/jewellery.html': ('3D Scanning & Printing for Jewellery | VShark Solutions',
         'Fine-detail 3D scanning, CAD and high-detail SLA resin masters for jewellers, plus 3D scanning of temple idols and heritage carvings.'),
    'portfolio/index.html': ('Portfolio – 3D Scanning & Reverse Engineering Projects',
         'Real scan, CAD and inspection projects: castings, vehicle bodies, frames, impellers, plant rooms and more. Filter by service or industry.'),
    'contact.html': ('Contact VShark Solutions – Get a Quote | India & UAE',
         'Send your part photos or drawings for a free quote. Call +91 95142 48525 (India) or +971 52 248 6238 (UAE), or WhatsApp us.'),
    'thanks.html': ('Thank you | VShark Solutions', 'Enquiry received.'),
    '404.html': ('Page not found | VShark Solutions', 'The page you are looking for has moved or does not exist.'),
    'about.html': ('About VShark Solutions – 3D Scanning & Engineering Since 2019',
         'VShark Solutions is a 3D scanning, reverse engineering and 3D design company based in Coimbatore and Dubai, serving clients across India, the UAE and worldwide since 2019.'),
    'privacy-policy.html': ('Privacy Policy | VShark Solutions',
         'How VShark Solutions collects, uses and protects personal data and files shared through our website, WhatsApp and email.'),
    'links.html': ('VShark Solutions – Links | WhatsApp, Quote, YouTube, Instagram',
         'All VShark Solutions links in one place: website, WhatsApp chat, quote form, YouTube, Instagram, Facebook and IndiaMART.'),
}
SITE_URL = 'https://www.vsharksolutions.com/'
# social profiles listed in the Organization schema `sameAs` (dev note 2026-10-27, item 2).
# LinkedIn is left out until VShark sends the company page URL (the current link is a personal profile).
SAME_AS = ('youtube', 'instagram', 'facebook', 'linkedin', 'indiamart')

def page_url(rel):
    '''Public URL of a page: the same form the sitemap uses (folder index pages end in /).'''
    if rel in ('', 'index.html'):
        return SITE_URL
    return SITE_URL + (rel[:-len('index.html')] if rel.endswith('/index.html') else rel)

def og_image(rel):
    '''1200×630 share image made by build/make_og.py: img/og/<page>.jpg, or the site default.'''
    name = 'home' if rel in ('', 'index.html') else rel[:-5].replace('/index', '').replace('/', '-')
    path = f'img/og/{name}.jpg'
    return path if os.path.exists(os.path.join(ROOT, path)) else 'img/og/default.jpg'

NOINDEX_PAGES = {'thanks.html', '404.html'}
OG_IMAGE = SITE_URL + 'img/og-default.jpg'

def canonical_url(rel):
    if rel in ('', 'index.html'):
        return SITE_URL
    return SITE_URL + (rel[:-len('index.html')] if rel.endswith('/index.html') else rel)

def head_meta(rel):
    title, desc = META[rel]
    url, img = page_url(rel), SITE_URL + og_image(rel)
    iw, ih, ialt = 1200, 630, title
    if rel in OG_POST:
        img, iw, ih, ialt = OG_POST[rel]
    tags = [f'<title>{E(title)}</title>',
            f'<meta name="description" content="{E(desc)}">']
    if rel not in ('404.html', 'thanks.html'):   # served at many URLs / not for search
        tags.append(f'<link rel="canonical" href="{url}">')
    tags += ['<meta property="og:type" content="website">',
             '<meta property="og:site_name" content="VShark Solutions">',
             '<meta property="og:locale" content="en_IN">',
             f'<meta property="og:url" content="{url}">',
             f'<meta property="og:title" content="{E(title)}">',
             f'<meta property="og:description" content="{E(desc)}">',
             f'<meta property="og:image" content="{img}">',
             f'<meta property="og:image:width" content="{iw}">',
             f'<meta property="og:image:height" content="{ih}">',
             f'<meta property="og:image:alt" content="{E(ialt)}">',
             '<meta name="twitter:card" content="summary_large_image">',
             f'<meta name="twitter:title" content="{E(title)}">',
             f'<meta name="twitter:description" content="{E(desc)}">',
             f'<meta name="twitter:image" content="{img}">']
    if rel in ('404.html', 'thanks.html'):
        tags.append('<meta name="robots" content="noindex">')
    return '\n  '.join(tags)

def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace('</', '<\\/') + '</script>'

def area_served(extra_cities=()):
    """One areaServed list for Organization/LocalBusiness and every Service node (S58). UAE = service area only, no address/registration claim."""
    return ([{'@type': 'City', 'name': 'Coimbatore'}] + [{'@type': 'City', 'name': c} for c in extra_cities if c and c != 'Coimbatore']
            + [{'@type': 'AdministrativeArea', 'name': 'Tamil Nadu'}, {'@type': 'Country', 'name': 'India'}, {'@type': 'Country', 'name': 'United Arab Emirates'}])

def schema_org():
    """Organization + LocalBusiness JSON-LD (handoff A7 / B8, dev note 2026-10-27 item 4) — same on every page."""
    S = C['social']
    country = {'IN': 'India', 'AE': 'United Arab Emirates'}
    org = {
        '@context': 'https://schema.org', '@type': ['Organization', 'LocalBusiness'], '@id': SITE_URL + '#business',
        'name': 'VShark Solutions Private Limited', 'legalName': 'VShark Solutions Private Limited',
        'alternateName': 'VShark Solutions', 'url': SITE_URL,
        'logo': SITE_URL + 'img/vshark-logo.png', 'image': SITE_URL + 'img/vshark-logo.png',
        'description': META[''][1],
        'email': C['email'], 'telephone': C['phones'][0]['tel'],
        'address': [dict({'@type': 'PostalAddress', 'addressLocality': o['city'], 'addressCountry': o['country']},
                         **({'streetAddress': o['street'], 'addressRegion': o['region'], 'postalCode': o['postcode']} if o.get('street') else {}))
                    for o in C['offices']],
        'contactPoint': [{'@type': 'ContactPoint', 'telephone': p['tel'], 'email': C['email'], 'contactType': 'sales',
                          'areaServed': 'IN' if p['label'] == 'India' else 'AE'} for p in C['phones']],
        'areaServed': area_served(), 'foundingDate': '2019',
        'sameAs': [S[k] for k in SAME_AS if S.get(k)],
    }
    return ld(org)

# ---------------------------------------------------------------- YouTube videos (VideoObject, dev note item 4)
def videos_for(key):
    return [v for v in D.get('videos', []) if key in v.get('pages', [])]

def video_ld(v):
    '''VideoObject JSON-LD. Description falls back to the title, and uploadDate is left out,
    until they are copied from YouTube into data/site.json.'''
    obj = {'@context': 'https://schema.org', '@type': 'VideoObject', 'name': v['title'],
           'description': v.get('description') or v['title'],
           'thumbnailUrl': [f'https://i.ytimg.com/vi/{v["id"]}/maxresdefault.jpg', f'https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg'],
           'contentUrl': f'https://www.youtube.com/watch?v={v["id"]}',
           'embedUrl': f'https://www.youtube.com/embed/{v["id"]}',
           'publisher': {'@id': SITE_URL + '#business'}}
    if v.get('uploadDate'):
        obj['uploadDate'] = v['uploadDate']
    if v.get('duration'):
        obj['duration'] = v['duration']
    return ld(obj)

def video_section(vids, title_html='See it <em>in action.</em>', alt=False):
    if not vids:
        return ''
    cards = '\n'.join(f'''        <figure class="vcard" data-reveal>
          <div class="vcard__frame"><iframe src="https://www.youtube-nocookie.com/embed/{v['id']}" title="{E(v['title'])}" loading="lazy"
            allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>
          <figcaption>{E(v['title'])}</figcaption>
          {video_ld(v)}
        </figure>''' for v in vids)
    return f'''    <section class="section blk{' blk--alt' if alt else ''}">
      <div class="sec-head"><div><span class="tag mono">Video</span><h2 class="h2" data-reveal>{title_html}</h2></div>
        <a class="sec-head__link" href="{C['social']['youtube']}" target="_blank" rel="noopener" data-reveal>YouTube channel {A}</a></div>
      <div class="vgrid">
{cards}
      </div>
    </section>'''

# ---------------------------------------------------------------- shared chrome
def header(P, active=''):
    def link(key, href, label):
        cls = ' is-current' if key == active else ''
        return f'<a href="{href}" class="nav__link{cls}">{label}</a>'
    svc_items = ''.join(f'<a href="{P}services/{s["slug"]}.html"><i class="mono">{i+1:02d}</i>{E(s["name"])}</a>' for i, s in enumerate(D['services']))
    ind_items = ''.join(f'<a href="{P}industries/{s["slug"]}.html"><i class="mono">{i+1:02d}</i>{E(s["name"])}</a>' for i, s in enumerate(D['industries']))
    def drop(key, href, label, items, all_label):
        cls = ' is-current' if key == active else ''
        return (f'<div class="nav__item nav__item--drop"><a href="{href}" class="nav__link{cls}" aria-haspopup="true">{label}{ICON["down"]}</a>'
                f'<div class="nav__drop"><div class="nav__drop-inner">{items}<a class="nav__drop-all" href="{href}">{all_label} {A}</a></div></div></div>')
    m = lambda i, href, label: f'<a href="{href}"><i class="mono">{i:02d}</i>{label}</a>'
    phones = ''.join(f'<a href="tel:{p["tel"]}">{E(p["display"])} ({E(p["label"])})</a>' for p in C['phones'])
    return f'''<!-- @header -->
  <header class="header" id="header">
    <a href="{P}index.html" class="header__logo" aria-label="VShark Solutions home">
      <img src="{P}img/vshark-logo.png" alt="VShark Solutions">
    </a>
    <nav class="nav" aria-label="Primary">
      {link('products', f'{P}products/index.html', 'Products')}
      {drop('services', f'{P}services/index.html', 'Services', svc_items, 'All services')}
      {drop('industries', f'{P}industries/index.html', 'Industries', ind_items, 'All industries')}
      {link('portfolio', f'{P}portfolio/index.html', 'Portfolio')}
      {link('blog', f'{P}blog/', 'Blog')}
      {link('about', f'{P}about.html', 'About')}
      {link('contact', f'{P}contact.html', 'Contact')}
    </nav>
    <div class="header__actions">
      <a href="{wa_link()}" class="header__wa" target="_blank" rel="noopener" aria-label="Chat with VShark on WhatsApp" data-wa-location="header">{ICON['wa']}</a>
      <a href="{P}contact.html" class="btn btn--sm btn--accent header__cta magnetic"><span>Enquire Now</span></a>
      <button class="burger" id="burger" aria-label="Open menu" aria-expanded="false"><span></span><span></span></button>
    </div>
  </header>

  <!-- MOBILE MENU -->
  <div class="menu" id="menu" aria-hidden="true">
    <nav class="menu__nav">
      {m(1, f'{P}products/index.html', 'Products')}
      {m(2, f'{P}services/index.html', 'Services')}
      {m(3, f'{P}industries/index.html', 'Industries')}
      {m(4, f'{P}portfolio/index.html', 'Portfolio')}
      {m(5, f'{P}blog/', 'Blog')}
      {m(6, f'{P}about.html', 'About')}
      {m(7, f'{P}contact.html', 'Contact')}
    </nav>
    <div class="menu__cta">
      <a class="btn btn--accent" href="{P}contact.html"><span>Get a quote</span>{A}</a>
      <a class="btn btn--ghost" href="{wa_link(WA_DEFAULT)}" target="_blank" rel="noopener">{ICON['wa']}<span>WhatsApp</span></a>
    </div>
    <div class="menu__foot mono">
      <a href="mailto:{C['email']}">{C['email']}</a>
      {phones}
    </div>
  </div>
  <!-- /@header -->'''

def footer(P, msg=WA_DEFAULT):
    phones_f = ''.join(f'<a href="tel:{p["tel"]}">{ICON["phone"]}{E(p["display"])} <small class="mono">{E(p["label"])}</small></a>' for p in C['phones'])
    phones_r = ''.join(f'<a href="tel:{p["tel"]}"><small class="mono">{E(p["label"])}</small>{E(p["display"])}</a>' for p in C['phones'])
    S = C['social']
    svc_links = ''.join(f'<a href="{P}services/{s["slug"]}.html">{E(s["name"])}</a>' for s in D['services'])
    return f'''<!-- @footer -->
  <footer class="footer" id="contact">
    <div class="footer__top">
      <div class="footer__brand">
        <img class="footer__logo" src="{P}img/vshark-logo.png" alt="VShark Solutions">
        <p class="muted">Leading the way in advanced technology solutions — state-of-the-art 3D scanning and 3D design services for businesses and individuals.</p>
      </div>
      <div class="footer__col">
        <span class="mono muted">Services</span>
        {svc_links}
      </div>
      <div class="footer__contact">
        <span class="mono muted">Contact</span>
        <a href="mailto:{C['email']}">{ICON['mail']}{C['email']}</a>
        {phones_f}
        {''.join(f'<span class="footer__addr">{ICON["pin"]}<span><small class="mono">{E(o["label"])}</small> {", ".join(E(l) for l in o["lines"])}</span></span>' for o in C['offices'])}
        <div class="footer__social">
          <a href="{wa_link()}" target="_blank" rel="noopener" aria-label="WhatsApp">{ICON['wa']}</a>
          <a href="{S['youtube']}" target="_blank" rel="noopener" aria-label="YouTube">{ICON['yt']}</a>
          <a href="{S['instagram']}" target="_blank" rel="noopener" aria-label="Instagram">{ICON['ig']}</a>
          <a href="{S['facebook']}" target="_blank" rel="noopener" aria-label="Facebook">{ICON['fb']}</a>
          <a href="{S['indiamart']}" target="_blank" rel="noopener" aria-label="IndiaMART">{ICON['shop']}</a>
          <a href="{S['linkedin']}" target="_blank" rel="noopener" aria-label="LinkedIn">{ICON['in']}</a>
        </div>
      </div>
    </div>
    <div class="footer__big" aria-hidden="true">VSHARK</div>
    <div class="footer__bottom mono">
      <span>© <span id="year">2026</span> VShark Solutions Private Limited</span>
      <span><a href="{P}about.html">About</a> · <a href="{P}blog/">Blog</a> · <a href="{P}links.html">Links</a> · <a href="{P}privacy-policy.html">Privacy Policy</a> · <a href="{P}privacy-policy.html#cookies-and-analytics" data-cookie-settings>Cookie settings</a></span>
      <a href="#top">Back to top ↑</a>
    </div>
  </footer>

  <!-- CONTACT RAIL — fixed on the right edge -->
  <aside class="rail" aria-label="Contact VShark">
    <div class="rail__item rail__item--phone">
      <button type="button" class="rail__btn" aria-label="Call us" aria-expanded="false">{ICON['phone']}</button>
      <div class="rail__flyout">{phones_r}</div>
    </div>
    <a class="rail__item rail__btn" href="{wa_link()}" target="_blank" rel="noopener" aria-label="WhatsApp">{ICON['wa']}<span class="rail__label">WhatsApp</span></a>
    <a class="rail__item rail__btn" href="mailto:{C['email']}" aria-label="Email">{ICON['mail']}<span class="rail__label">{C['email']}</span></a>
    <a class="rail__item rail__btn" href="{S['youtube']}" target="_blank" rel="noopener" aria-label="YouTube">{ICON['yt']}<span class="rail__label">YouTube</span></a>
    <a class="rail__item rail__btn" href="{S['instagram']}" target="_blank" rel="noopener" aria-label="Instagram">{ICON['ig']}<span class="rail__label">Instagram</span></a>
    <a class="rail__item rail__btn" href="{S['facebook']}" target="_blank" rel="noopener" aria-label="Facebook">{ICON['fb']}<span class="rail__label">Facebook</span></a>
    <a class="rail__item rail__btn" href="{S['linkedin']}" target="_blank" rel="noopener" aria-label="LinkedIn">{ICON['in']}<span class="rail__label">LinkedIn</span></a>
  </aside>

  <!-- FLOATING WHATSAPP BUTTON — every page, bottom-right -->
  <a class="wa-float" href="{wa_link()}" target="_blank" rel="noopener" aria-label="Chat with VShark on WhatsApp" data-wa-location="floating_button">{ICON['wa']}</a>

  <!-- MOBILE ACTION BAR — phones only; replaces the rail -->
  <nav class="mbar" aria-label="Quick contact">
    <div class="mbar__call">
      <button type="button" class="mbar__btn" aria-expanded="false" aria-controls="mbarPhones">{ICON['phone']}<span>Call</span></button>
      <div class="mbar__sheet" id="mbarPhones">{phones_r}</div>
    </div>
    <a class="mbar__btn" href="{wa_link(msg)}" target="_blank" rel="noopener">{ICON['wa']}<span>WhatsApp</span></a>
    <a class="mbar__btn mbar__btn--accent" href="{P}contact.html"><span>Get a quote</span>{A}</a>
  </nav>
  <!-- /@footer -->'''

def page(P, rel, active, body, scripts=(), wa_msg=WA_DEFAULT, view=None):
    '''view = (content_name, content_category): js/consent.js sends Meta ViewContent + GA4 view_content for it.'''
    js = '\n'.join(f'  <script src="{asset(s, P)}"></script>' for s in ('vendor/gsap.min.js', 'vendor/ScrollTrigger.min.js', 'vendor/lenis.min.js', *scripts, 'js/main.js'))
    view_attr = f' data-view-content="{E(view[0])}" data-view-category="{E(view[1])}"' if view else ''
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {head_meta(rel)}
  {schema_org()}
  <meta name="theme-color" content="#f5f6f8">
  <link rel="icon" href="{P}favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="{P}img/favicon-32.png">
  <link rel="apple-touch-icon" href="{P}img/apple-touch-icon.png">
  <link rel="stylesheet" href="{asset('fonts/fonts.css', P)}">
  <link rel="stylesheet" href="{asset('css/style.css', P)}">
  <link rel="stylesheet" href="{asset('css/pages.css', P)}">
  <script src="{asset('js/consent.js', P)}" defer></script>
</head>
<body class="inner"{view_attr}>
  <div class="cursor" aria-hidden="true"><div class="cursor__dot"></div><div class="cursor__ring"><span class="cursor__text"></span></div></div>

  {header(P, active)}

  <main id="top">
{body}
  </main>

  {footer(P, wa_msg)}

{js}
</body>
</html>
'''

# ---------------------------------------------------------------- building blocks
def crumbs(P, items):
    parts = [f'<a href="{P}index.html">Home</a>'] + [f'<a href="{h}">{E(t)}</a>' if h else f'<span>{E(t)}</span>' for t, h in items]
    return '<nav class="crumbs mono" aria-label="Breadcrumb">' + ' <i>/</i> '.join(parts) + '</nav>'

def page_hero(P, crumb_items, tag, title_html, lead, image=None, side='', alt=''):
    img = f'<figure class="page-hero__media" data-in><img src="{P}{image}" alt="{E(alt)}" loading="eager"><i class="page-hero__slash" aria-hidden="true"></i></figure>' if image else side
    return f'''    <section class="page-hero{' page-hero--media' if (image or side) else ''}">
      <div class="page-hero__text">
        <div data-in>{crumbs(P, crumb_items)}</div>
        <span class="tag mono" data-in>{tag}</span>
        <h1 class="page-hero__title" data-in>{title_html}</h1>
        <p class="page-hero__lead" data-in>{lead}</p>
      </div>
      {img}
    </section>'''

def cta(P, title='Have a part, a building or an idea?', text='Tell us what you need — we usually reply within one working day.', msg=WA_DEFAULT):
    return f'''    <section class="cta-band">
      <div class="cta-band__inner">
        <h2 class="h2">{title}</h2>
        <p>{E(text)}</p>
        <div class="cta-band__actions">
          <a class="btn btn--light magnetic" href="{P}contact.html"><span>Send an enquiry</span>{A}</a>
          <a class="btn btn--outline-light magnetic" href="{wa_link(msg)}" target="_blank" rel="noopener">{ICON['wa']}<span>WhatsApp us</span></a>
        </div>
      </div>
    </section>'''

def a_an(t):
    return ('an ' if t[:1].lower() in 'aeiou' else 'a ') + t.lower()

def proj_card(P, p, show_tags=True):
    svc = ' '.join(p['services']); ind = ' '.join(p['industries'])
    if p['kind'] == 'pair':
        media = (f'<div class="proj__media proj__media--pair" data-cmp><img src="{P}{p["before"]}" alt="3D scan of {E(a_an(p.get("part", p["title"])))}" loading="lazy">'
                 f'<img class="proj__cad" src="{P}{p["after"]}" alt="CAD model of {E(a_an(p.get("part", p["title"])))}" loading="lazy"><i class="proj__divider"></i>'
                 f'<span class="proj__lab proj__lab--l mono">CAD</span><span class="proj__lab proj__lab--r mono">Scan</span></div>')
        nv = len(p.get('views', []))
        badge = 'Scan → CAD' + (f' · +{nv} view{"s" if nv > 1 else ""}' if nv else '')
        views = ';;'.join(f'{lab}|{P}{src}' for lab, src in p.get('views', []))
        data = f'data-kind="pair" data-before="{P}{p["before"]}" data-after="{P}{p["after"]}" data-views="{E(views)}"'
    else:
        fit = ' proj__media--contain' if p.get('fit') == 'contain' else ''
        media = f'<div class="proj__media{fit}"><img src="{P}{p["images"][0]}" alt="{E(p["title"])}" loading="lazy"></div>'
        n_img = len(p['images'])
        badge = p.get('badge') or (f'{n_img} images' if n_img > 1 else 'View')
        data = f'data-kind="gallery" data-images="{"|".join(P + i for i in p["images"])}"'
    tags = ''
    if show_tags:
        names = [SVC[s]['name'] for s in p['services']] + [IND[i]['name'] for i in p['industries']]
        tags = '<span class="proj__tags">' + ''.join(f'<i>{E(n)}</i>' for n in names) + '</span>'
    return f'''        <article class="proj" data-services="{svc}" data-industries="{ind}" {data} data-title="{E(p['title'])}" data-summary="{E(p['summary'])}">
          <button class="proj__open" type="button" aria-label="Open {E(p['title'])}">
            {media}
            <span class="proj__badge mono">{badge}</span>
            <span class="proj__body"><b>{E(p['title'])}</b><span>{E(p['summary'])}</span>{tags}</span>
          </button>
        </article>'''

def proj_section(P, projects, title_html, link_qs):
    if not projects:
        return f'''    <section class="section blk">
      <div class="sec-head"><div><span class="tag mono">Portfolio</span><h2 class="h2">{title_html}</h2>
      <p class="sec-head__sub muted">Project case studies for this area are being added. Ask us for examples relevant to your work.</p></div>
      <a class="sec-head__link" href="{P}portfolio/index.html">Full portfolio {A}</a></div>
    </section>'''
    cards = '\n'.join(proj_card(P, p, False) for p in projects[:8])
    n = len(projects)
    return f'''    <section class="section blk">
      <div class="sec-head"><div><span class="tag mono">Portfolio · {n} project{'s' if n != 1 else ''}</span><h2 class="h2" data-reveal>{title_html}</h2></div>
        <div class="pcar__head" data-reveal><a class="sec-head__link" href="{P}portfolio/index.html?{link_qs}">See all {A}</a></div></div>
      <div class="pcar">
        <div class="pcar__track">
{cards}
        </div>
        <div class="pcar__bar" aria-hidden="true"><b></b></div>
      </div>
    </section>'''

def faq_section(faqs, title_html='Common <em>questions.</em>'):
    """Accordion of questions with FAQPage JSON-LD (read by Google and AI search)."""
    if not faqs:
        return ''
    items = '\n'.join(f'''        <details class="faq__item" data-reveal>
          <summary><span>{E(q)}</span><i aria-hidden="true"></i></summary>
          <div class="faq__a"><p>{E(a)}</p></div>
        </details>''' for q, a in faqs)
    ld = json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage',
                     'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]},
                    ensure_ascii=False, indent=1).replace('</', '<\\/')
    return f'''    <section class="section blk faq" id="faq">
      <div class="sec-head"><div><span class="tag mono">FAQ</span><h2 class="h2" data-reveal>{title_html}</h2></div></div>
      <div class="faq__list">
{items}
      </div>
      <script type="application/ld+json">
{ld}
      </script>
    </section>'''

def xnav(P, items, current, folder, label):
    '''Row of every service / industry at the bottom of a detail page; the current one is highlighted.'''
    links = '\n'.join(
        f'''        <a class="xnav__item{' is-current' if o is current else ''}" href="{P}{folder}/{o['slug']}.html"{' aria-current="page"' if o is current else ''}>
          <img src="{P}{o.get('tile') or o.get('square') or o['image']}" alt="{E(o.get('alt') or o['name'])}" loading="lazy"><span><i class="mono">{k+1:02d}</i><b>{E(o['name'])}</b></span>
        </a>''' for k, o in enumerate(items))
    return f'''    <section class="section xnav" aria-label="{label}">
      <div class="xnav__head"><span class="tag mono">{label}</span><a class="xnav__all mono" href="{P}{folder}/index.html">Overview {A}</a></div>
      <nav class="xnav__row">
{links}
      </nav>
    </section>'''

LIGHTBOX = '''    <div class="lb" id="lb" aria-hidden="true" role="dialog" aria-modal="true" aria-label="Project viewer">
      <button class="lb__close" type="button" aria-label="Close">×</button>
      <div class="lb__stage"></div>
      <div class="lb__cap"><b class="lb__title"></b><span class="lb__sum"></span><span class="lb__views" role="group" aria-label="Views"></span><span class="lb__count mono"></span></div>
      <button class="lb__nav lb__prev" type="button" aria-label="Previous image">‹</button>
      <button class="lb__nav lb__next" type="button" aria-label="Next image">›</button>
    </div>'''

# TODO(handoff A8): add the JINUOSH logo here once their written letter is received
DIST_BADGE = '<p class="dist-badge" data-in><span class="mono">India distributor</span>JINUOSH Vertex 3D scanners in India</p>'

def prod_tile(P, p, i, href):
    return f'''    <article class="prod" data-reveal>
      <div class="prod__tile">
        <div class="prod__stage" aria-hidden="true">
          <span class="prod__num">{i+1:02d}</span>
          <i class="prod__slash prod__slash--grey"></i>
          <i class="prod__slash prod__slash--red"></i>
        </div>
        <div class="prod__body">
          <h3>{E(p['name'])}</h3>
          <p class="prod__type">{E(p['type'])}</p>
          <div class="prod__fig"><b>{E(p['figure'])}</b><span class="mono">{E(p['unit'])}</span></div>
          <span class="prod__more">View product {A}</span>
        </div>
      </div>
      <img class="prod__img" src="{P}{p['image']}" alt="{E(p['name'])} 3D scanner" loading="lazy" draggable="false">
      <span class="prod__scan" aria-hidden="true"></span>
      <a class="prod__link" href="{href}" aria-label="{E(p['name'])} — view product"></a>
    </article>'''

def svc_tile(P, s, i):
    return f'''        <a class="stile" href="{P}services/{s['slug']}.html" data-reveal>
          <span class="stile__media"><img src="{P}{s['tile']}" alt="{E(s['alt'])}" loading="lazy"></span>
          <span class="stile__body"><i class="mono">{i+1:02d}</i><b>{E(s['name'])}</b><span>{E(s['tagline'])}</span><em>Explore {A}</em></span>
        </a>'''

def ind_tile(P, s, i):
    return f'''        <a class="itile" href="{P}industries/{s['slug']}.html" data-reveal>
          <img src="{P}{s['square']}" alt="{E(s['alt'])}" loading="lazy">
          <span class="itile__body"><i class="mono">{i+1:02d}</i><b>{E(s['name'])}</b><span>{E(s['line'])}</span></span>
        </a>'''

# ---------------------------------------------------------------- pages
def service_page(s):
    P = '../'
    i = D['services'].index(s)
    pts = '\n'.join(f'''        <div class="feat" data-reveal><i class="mono">{k+1:02d}</i><h3>{E(t)}</h3><p>{E(d)}</p></div>''' for k, (t, d) in enumerate(s['points']))
    dels = ''.join(f'<li>{E(d)}</li>' for d in s['deliverables'])
    steps = [('Brief', f'Tell us about the part, product or space and what you need from {s["name"].lower()}.'),
             ('Capture & model', 'Our engineers scan, model or prepare your data with the right tools for the job.'),
             ('Review', 'You check the result against your requirements; we refine until it is right.'),
             ('Deliver', 'Final files, parts or reports delivered in the formats your team uses.')]
    step_html = '\n'.join(f'<li class="step2" data-reveal><i class="mono">{k+1:02d}</i><b>{t}</b><span>{E(d)}</span></li>' for k, (t, d) in enumerate(steps))
    inds = ''.join(f'<a class="chip" href="{P}industries/{x}.html">{E(IND[x]["name"])} {A}</a>' for x in s['industries'])
    projects = [p for p in D['projects'] if s['slug'] in p['services']]
    prods = ''
    if s.get('products'):
        prods = f'''    <section class="section blk blk--alt">
      <div class="sec-head"><div><span class="tag mono">Equipment</span><h2 class="h2" data-reveal>Scanners we <em>use &amp; sell.</em></h2></div>
        <a class="sec-head__link" href="{P}products/index.html" data-reveal>All products {A}</a></div>
      <div class="prod-grid">
{chr(10).join(prod_tile(P, p, k, f"{P}products/index.html#{p['slug']}") for k, p in enumerate(D['products']))}
      </div>
    </section>'''
    fig2 = f'          <figure class="svc-fig" data-reveal><img src="{P}{s["image2"]}" alt="{E(s["alt2"])}" loading="lazy"></figure>' if s.get('image2') else ''
    cur_attr = ' aria-current="page"'
    others = ''.join(f'<a href="{P}services/{o["slug"]}.html"{cur_attr if o is s else ""}>{E(o["name"])}</a>' for o in D['services'])
    body = f'''{page_hero(P, [("Services", P + "services/index.html"), (s["name"], None)], f"( {i+1:02d} ) — Service", E(s["name"]), E(s["tagline"]), s["image"], alt=s["alt"])}

    <section class="section blk">
      <div class="split">
        <div class="split__main">
          <span class="tag mono">What we do</span>
          <p class="lead-lg" data-reveal>{E(s['intro'])}</p>
          <div class="feat-grid">
{pts}
          </div>
{fig2}
        </div>
        <aside class="split__side" data-reveal>
          <div class="side-card">
            <span class="mono muted">Deliverables</span>
            <ul class="ticks">{dels}</ul>
            <a class="btn btn--accent btn--block magnetic" href="{P}contact.html?service={s['slug']}"><span>Get a quote</span>{A}</a>
          </div>
          <nav class="side-nav" aria-label="All services"><span class="mono muted">All services</span>{others}</nav>
        </aside>
      </div>
    </section>

    <section class="section blk blk--alt">
      <div class="sec-head"><div><span class="tag mono">How it works</span><h2 class="h2" data-reveal>Four steps, <em>no surprises.</em></h2></div></div>
      <ol class="steps2">
{step_html}
      </ol>
      <div class="ind-chips" data-reveal><span class="mono muted">Industries we do this for</span><div>{inds}</div></div>
    </section>

{proj_section(P, projects, f'{E(s["name"])} <em>projects.</em>', f'service={s["slug"]}')}
{video_section(videos_for(s['slug']), f'{E(s["name"])} <em>in action.</em>', alt=True)}
{prods}
{faq_section(s.get('faq', []), f'{E(s["name"])} <em>FAQ.</em>')}
{xnav(P, D['services'], s, 'services', 'All services')}
{cta(P, msg=f"Hi VShark, I'm interested in {s['name']}.")}
{LIGHTBOX}'''
    return page(P, f"services/{s['slug']}.html", 'services', body, ('js/portfolio.js',),
                wa_msg=f"Hi VShark, I'm interested in {s['name']}.", view=(s['name'], 'Service'))

def services_index():
    P = '../'
    tiles = '\n'.join(svc_tile(P, s, i) for i, s in enumerate(D['services']))
    body = f'''{page_hero(P, [("Services", None)], "( 02 ) — Services", "From physical to <em>digital</em> and back.", "Seven services, one connected workflow — from capturing reality to engineering, inspecting, printing and presenting it.")}
    <section class="section blk">
      <div class="stile-grid">
{tiles}
      </div>
    </section>
{cta(P)}'''
    return page(P, 'services/index.html', 'services', body)

def industries_index():
    P = '../'
    tiles = '\n'.join(ind_tile(P, s, i) for i, s in enumerate(D['industries']))
    body = f'''{page_hero(P, [("Industries", None)], "( 03 ) — Industries", "Industries <em>we serve.</em>", "Six sectors, one standard of precision.")}
    <section class="section blk">
      <div class="itile-grid">
{tiles}
      </div>
    </section>
{cta(P)}'''
    return page(P, 'industries/index.html', 'industries', body)

def industry_page(ind):
    P = '../'
    i = D['industries'].index(ind)
    svcs = [s for s in D['services'] if ind['slug'] in s['industries']]
    tiles = '\n'.join(svc_tile(P, s, D['services'].index(s)) for s in svcs)
    projects = [p for p in D['projects'] if ind['slug'] in p['industries']]
    body = f'''{page_hero(P, [("Industries", P + "industries/index.html"), (ind["name"], None)], f"( {i+1:02d} ) — Industry", E(ind["name"]), E(ind["line"]), ind["square"], alt=ind["alt"])}
    <section class="section blk">
      <p class="lead-lg" data-reveal>{E(ind['intro'])}</p>
    </section>
    <section class="section blk blk--alt">
      <div class="sec-head"><div><span class="tag mono">Services</span><h2 class="h2" data-reveal>What we do for <em>{E(ind['name'].lower())}.</em></h2></div></div>
      <div class="stile-grid">
{tiles}
      </div>
    </section>
{proj_section(P, projects, f'{E(ind["name"])} <em>projects.</em>', f'industry={ind["slug"]}')}
{video_section(videos_for(ind['slug']), alt=True)}
{xnav(P, D['industries'], ind, 'industries', 'All industries')}
{cta(P, msg=f"Hi VShark, I work in {ind['name']} and would like to discuss a project.")}
{LIGHTBOX}'''
    return page(P, f"industries/{ind['slug']}.html", 'industries', body, ('js/portfolio.js',))

def video_embed(P, url, title):
    '''YouTube link -> privacy-friendly embed; anything else is treated as a local/hosted video file.'''
    m = re.search(r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/))([\w-]{11})', url)
    if m:
        return (f'<iframe src="https://www.youtube-nocookie.com/embed/{m.group(1)}" title="{E(title)} video" loading="lazy" '
                'allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>')
    src = url if url.startswith('http') else P + url
    return f'<video src="{E(src)}" controls preload="metadata" playsinline></video>'

def spec_dialog(P, p, k):
    '''Popup with one scanner's specifications. Media blocks render only when the data has them.'''
    col = k + 1
    groups = ''.join(
        f'<div class="sd__group"><h3 class="mono">{E(name)}</h3><dl>'
        + ''.join(f'<div><dt>{E(D["productSpecs"][i][0])}</dt><dd>{E(D["productSpecs"][i][col])}</dd></div>' for i in idx)
        + '</dl></div>' for name, idx in D['productSpecGroups'])
    logo = f'<img class="sd__logo" src="{P}{p["logo"]}" alt="{E(p["name"])} logo">' if p.get('logo') else ''
    media = ''
    if p.get('video'):
        media += f'<div class="sd__video">{video_embed(P, p["video"], p["name"])}</div>'
    if p.get('gallery'):
        media += '<div class="sd__gallery">' + ''.join(f'<img src="{P}{g}" alt="{E(p["name"])}" loading="lazy">' for g in p['gallery']) + '</div>'
    if media:
        media = f'<div class="sd__media">{media}</div>'
    brochure = (f'<a class="btn btn--ghost" href="{P}{p["brochure"]}" target="_blank" rel="noopener" download>{ICON["file"]}<span>Datasheet (PDF)</span></a>'
                if p.get('brochure') else '')
    return f'''    <dialog class="sd" id="spec-{p['slug']}" aria-labelledby="spec-{p['slug']}-title" data-lenis-prevent>
      <button class="sd__close" type="button" aria-label="Close specifications" data-spec-close>×</button>
      <div class="sd__panel">
        <header class="sd__head">
          <div class="sd__shot"><i class="prod__slash prod__slash--red"></i><img src="{P}{p['image']}" alt="{E(p['name'])} 3D scanner" loading="lazy"></div>
          <div class="sd__title">
            {logo}<span class="tag mono">{E(p['type'])}</span>
            <h2 id="spec-{p['slug']}-title">{E(p['name'])}</h2>
            <p>{E(p['summary'])}</p>
            <div class="prod__fig"><b>{E(p['figure'])}</b><span class="mono">{E(p['unit'])}</span></div>
          </div>
        </header>
        {media}
        <div class="sd__specs">{groups}</div>
        <p class="sd__pc"><b>Recommended computer</b> {E(D['productPc'])}</p>
        <footer class="sd__foot">
          <a class="btn btn--accent" href="{P}contact.html?product={p['slug']}"><span>Request a quote</span>{A}</a>
          <a class="btn btn--ghost" href="{wa_link('Hi VShark, I would like a demo of the ' + p['name'] + ' scanner.')}" target="_blank" rel="noopener"><span>Book a demo</span></a>
          {brochure}
          <span class="sd__note muted">Manufacturer specifications, subject to change.</span>
        </footer>
      </div>
    </dialog>'''

def products_page():
    P = '../'
    rows, dialogs = [], []
    for k, p in enumerate(D['products']):
        rows.append(f'''      <article class="prow{' prow--flip' if k % 2 else ''}" id="{p['slug']}">
        <div class="prow__media" data-reveal>
          <i class="prod__slash prod__slash--grey"></i><i class="prod__slash prod__slash--red"></i>
          <img src="{P}{p['image']}" alt="{E(p['name'])} 3D scanner" loading="lazy">
          <span class="prow__num">{k+1:02d}</span>
        </div>
        <div class="prow__text" data-reveal>
          <span class="tag mono">{E(p['type'])}</span>
          <h2 class="h2">{E(p['name'])}</h2>
          <p class="lead">{E(p['summary'])}</p>
          <div class="prod__fig"><b>{E(p['figure'])}</b><span class="mono">{E(p['unit'])}</span></div>
          <div class="prow__actions">
            <a class="btn btn--accent magnetic" href="{P}contact.html?product={p['slug']}"><span>Request a quote</span>{A}</a>
            <a class="btn btn--ghost magnetic" href="{wa_link('Hi VShark, I would like a demo of the ' + p['name'] + ' scanner.')}" target="_blank" rel="noopener"><span>Book a demo</span></a>
            <button class="btn btn--link" type="button" data-spec-open="{p['slug']}" aria-haspopup="dialog"><span>Specifications</span>{ICON['specs']}</button>
          </div>
        </div>
      </article>''')
        dialogs.append(spec_dialog(P, p, k))
    head = ''.join(f'<th scope="col">{E(p["name"])}</th>' for p in D['products'])
    trs = '\n'.join(f'<tr><th scope="row">{E(r[0])}</th>' + ''.join(f'<td>{E(c)}</td>' for c in r[1:]) + '</tr>' for r in D['productSpecs'])
    body = f'''{page_hero(P, [("Products", None)], "( 01 ) — Products", "Professional <em>3D scanners.</em>", "Vertex blue-laser and optical-tracking scanners — sold, set up and supported by VShark's scanning engineers.", side=DIST_BADGE)}
    <section class="section blk prows">
{chr(10).join(rows)}
    </section>
    <section class="section blk blk--alt" id="compare">
      <div class="sec-head"><div><span class="tag mono">Specifications</span><h2 class="h2" data-reveal>Compare <em>side by side.</em></h2></div></div>
      <div class="spec-wrap" data-reveal>
        <table class="spec">
          <thead><tr><th scope="col">Specification</th>{head}</tr></thead>
          <tbody>
{trs}
          </tbody>
        </table>
      </div>
      <p class="spec-note muted"><b>Recommended computer:</b> {E(D['productPc'])}. Specifications from the manufacturer and subject to change.</p>
    </section>
    <section class="section blk blk--alt">
      <div class="sec-head"><div><span class="tag mono">Full details</span><h2 class="h2" data-reveal>Specifications, what's included <em>and FAQs.</em></h2></div></div>
      <nav class="bchips" aria-label="Scanner detail pages"><a class="chip" href="{P}jinuosh-vertex-3d-scanner-india.html">Vertex3D and Vertex3D Pro in India</a><a class="chip" href="{P}vertex-tracker.html">Vertex Tracker in India</a><a class="chip" href="{P}blog/choosing-a-handheld-3d-scanner-india/">Buying guide: which Vertex scanner?</a><a class="chip" href="{P}jinuosh-vertex-vs-creaform-shining-3d-gom.html">Vertex vs Creaform, Shining 3D, GOM</a></nav>
    </section>
{video_section(videos_for('products'), 'The scanners <em>in action.</em>')}
{faq_section(D.get('productFaq', []), 'Buying a scanner: <em>FAQ.</em>')}
{chr(10).join(dialogs)}
{cta(P, 'Not sure which scanner fits?', 'Send us your parts and use case — we will recommend a model and can arrange a live demo.', 'Hi VShark, please help me choose a 3D scanner.')}'''
    return page(P, 'products/index.html', 'products', body, ('js/products.js',),
                wa_msg='Hi VShark, I would like a quote or demo for a 3D scanner.',
                view=('Vertex 3D scanners', 'Product'))

def portfolio_page():
    P = '../'
    used_s = [s for s in D['services'] if any(s['slug'] in p['services'] for p in D['projects'])]
    used_i = [s for s in D['industries'] + D.get('filterIndustries', []) if any(s['slug'] in p['industries'] for p in D['projects'])]
    chips = lambda key, items: f'<button class="chip is-on" type="button" data-f="{key}" data-v="">All</button>' + ''.join(f'<button class="chip" type="button" data-f="{key}" data-v="{x["slug"]}">{E(x["name"])}</button>' for x in items)
    cards = '\n'.join(proj_card(P, p) for p in D['projects'])
    body = f'''{page_hero(P, [("Portfolio", None)], "( 04 ) — Portfolio", "Completed <em>projects.</em>", "A selection of scanning, engineering and visualisation work. Filter by service or industry. On a Scan → CAD project, hover or drag across the image to compare the scan with the finished model.")}
    <section class="section blk pf">
      <div class="pf__filters" data-reveal>
        <div class="pf__row"><span class="mono muted">Service</span><div class="pf__chips">{chips('service', used_s)}</div></div>
        <div class="pf__row"><span class="mono muted">Industry</span><div class="pf__chips">{chips('industry', used_i)}</div></div>
        <span class="pf__count mono" aria-live="polite"></span>
      </div>
      <div class="proj-grid proj-grid--pf" id="pfGrid">
{cards}
      </div>
      <div class="pf__more-wrap"><button class="btn btn--ghost pf__more" type="button" hidden><span>Show more projects</span></button></div>
      <p class="pf__empty muted" hidden>No projects match this combination yet — <a href="{P}contact.html">ask us for examples</a>.</p>
    </section>
{cta(P)}
{LIGHTBOX}'''
    return page(P, 'portfolio/index.html', 'portfolio', body, ('js/portfolio.js',))

def md(text):
    """Tiny Markdown subset for the policy text: ## headings, **bold**, - lists, paragraphs, line breaks.
    A bold-only line directly above a list becomes a sub-heading."""
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S).strip()
    inline = lambda t: re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', E(t))
    out = []
    for block in re.split(r'\n\s*\n', text):
        lines = block.strip().split('\n')
        i = 0
        while i < len(lines):
            l = lines[i]
            if l.startswith('## '):
                hid = re.sub(r'[^a-z0-9]+', '-', re.sub(r'^\d+\.\s*', '', l[3:]).lower()).strip('-')  # '6. Cookies and analytics' -> cookies-and-analytics
                out.append(f'<h2 id="{hid}">{inline(l[3:])}</h2>'); i += 1
            elif l.startswith('- '):
                items = []
                while i < len(lines) and lines[i].startswith('- '):
                    items.append(f'<li>{inline(lines[i][2:])}</li>'); i += 1
                out.append('<ul>' + ''.join(items) + '</ul>')
            elif re.fullmatch(r'\*\*[^*]+\*\*', l) and i + 1 < len(lines) and lines[i + 1].startswith('- '):
                out.append(f'<h3>{E(l[2:-2])}</h3>'); i += 1
            else:
                para = []
                while i < len(lines) and not lines[i].startswith(('- ', '## ')):
                    para.append(inline(lines[i])); i += 1
                out.append('<p>' + '<br>'.join(para) + '</p>')
    return '\n'.join(out)

def about_page():
    P = ''
    PH = 'img/about/'
    svc = ''.join(f'<li><a href="services/{s["slug"]}.html"><b>{E(s["name"])}</b><span>{E(t)}</span>{A}</a></li>' for s, t in zip(D['services'], [
        'High-accuracy blue-laser scanning of parts, castings, vehicles and large objects, at our facility or on site anywhere in India and the UAE.',
        'Worn, legacy and undocumented parts rebuilt as editable, manufacturable CAD, delivered as STEP and other neutral formats.',
        # handoff said "built from your point cloud data" — corrected: VShark also laser-scans the site
        'Buildings and plant rooms laser-scanned on site, or your own point cloud, modelled as accurate Autodesk Revit BIM.',
        'Smooth, curvature-continuous surfaces for visible automotive and product parts.',
        'Scan-to-CAD inspection with deviation colour maps and clear reports.',
        'FDM and SLA prototypes, functional parts, scale models and jewellery masters.',
        'Photorealistic visuals of products before they are made.',
    ]))
    steps = [('Understand the goal', 'A replacement part, an inspection report, a BIM model or a new product. We start with what you need the data for.'),
             ('Capture accurately', "The right scanner and setup for the part's size, surface and tolerance."),
             ('Engineer with care', 'Experienced engineers build CAD, surfaces and models with design intent, not just shape.'),
             ('Prove the result', 'Every model is checked against the scan, and you see the deviation.'),
             ('Deliver on time', 'In the formats your team and suppliers already use.')]
    step_html = '\n'.join(f'<li class="step2" data-reveal><i class="mono">{k+1:02d}</i><b>{t}</b><span>{E(d)}</span></li>' for k, (t, d) in enumerate(steps))
    why = [('One team, end to end', 'Scanning, CAD, inspection, printing and rendering under one roof.'),
           ('Accuracy you can verify', 'Scan-to-CAD comparisons and reports on every job.'),
           ('On-site service in India and the UAE', 'We come to your plant, workshop or site.'),
           ('Confidential by default', 'NDAs on request, with client data and designs kept secure.'),
           ('Fast response', 'We usually reply within one working day.')]
    why_html = '\n'.join(f'<div class="feat" data-reveal><i class="mono">{k+1:02d}</i><h3>{E(t)}</h3><p>{E(d)}</p></div>' for k, (t, d) in enumerate(why))
    offices = ''.join(f'<div class="ccard ccard--static">{ICON["pin"]}<span><small class="mono">{E(o["label"])}</small>{"<br>".join(E(l) for l in o["lines"])}</span></div>' for o in C['offices'])
    phones = ''.join(f'<a class="ccard" href="tel:{p["tel"]}">{ICON["phone"]}<span><small class="mono">{E(p["label"])}</small>{E(p["display"])}</span></a>' for p in C['phones'])
    stats = [('2019', 'In business since'), ('7', 'Countries served'), (str(len(D['services'])), 'Services under one roof'), ('IN · AE', 'On-site service')]
    stat_html = ''.join(f'<div class="astat" data-reveal><b>{E(a)}</b><span class="mono">{E(l)}</span></div>' for a, l in stats)
    body = f"""{page_hero(P, [("About", None)], "( 05 ) — About", "We capture reality. <em>Then we engineer it.</em>",
        "VShark Solutions Private Limited is a 3D scanning and engineering design company based in Coimbatore, India, with a presence in Dubai, UAE. Since 2019, we have helped manufacturers, engineers, designers and builders turn physical objects into accurate, usable digital data, and turn digital designs back into real parts.",
        PH + 'vshark-engineer-3d-scanning-a-car-boot-floor-with-a-jinuosh-vertex-handheld-scanner.webp', alt='VShark engineer 3D scanning a car boot floor with a JINUOSH Vertex handheld scanner')}

    <section class="section blk">
      <p class="lead-lg" data-reveal>Our clients range from automotive and aerospace suppliers to foundries, mining and process plants, construction teams, jewellers and research labs. We have delivered projects for clients in India, the UAE, Saudi Arabia, the USA, the UK, Germany and Canada.</p>
      <div class="astats">{stat_html}</div>
    </section>

    <section class="section blk blk--alt">
      <div class="about-split">
        <div>
          <div class="sec-head"><div><span class="tag mono">What we do</span><h2 class="h2" data-reveal>Seven services, <em>one team.</em></h2></div></div>
          <ul class="alist" data-reveal>{svc}</ul>
        </div>
        <figure class="about-fig" data-reveal><img src="{PH}vshark-engineer-laser-scanning-an-aluminium-housing-with-a-portable-measuring-arm.webp" alt="VShark engineer laser scanning an aluminium housing with a portable measuring arm" loading="lazy"></figure>
      </div>
    </section>

    <section class="section blk">
      <div class="dist-block" data-reveal>
        {DIST_BADGE.replace(' data-in', '')}
        <div>
          <h2 class="h2">Scanners we <em>use and sell.</em></h2>
          <p>We are the India distributor of JINUOSH Vertex 3D scanners in India: the Vertex3D, Vertex3D Pro and Vertex Tracker. We use these scanners every day in our own service work, so our advice comes from real projects, not brochures. Every scanner we supply is installed at the customer's site, with hands-on training for their team, and comes with a 12-month warranty.</p>
          <a class="btn btn--ghost" href="products/index.html"><span>See the scanners</span>{A}</a>
        </div>
      </div>
    </section>

    <section class="section blk blk--alt">
      <div class="sec-head"><div><span class="tag mono">How we work</span><h2 class="h2" data-reveal>Five steps, <em>proven results.</em></h2></div></div>
      <ol class="steps2 steps2--5">
{step_html}
      </ol>
    </section>

    <section class="section blk">
      <div class="about-split about-split--flip">
        <figure class="about-fig" data-reveal><img src="{PH}3d-scan-data-of-a-car-wheel-in-scan-software.webp" alt="3D scan data of a car wheel in scan software, captured with a handheld 3D scanner" loading="lazy"></figure>
        <div>
          <div class="sec-head"><div><span class="tag mono">Why VShark</span><h2 class="h2" data-reveal>Why clients <em>choose us.</em></h2></div></div>
          <div class="feat-grid feat-grid--1">
{why_html}
          </div>
        </div>
      </div>
    </section>

    <section class="section blk blk--alt">
      <div class="sec-head"><div><span class="tag mono">Our locations</span><h2 class="h2" data-reveal>Coimbatore <em>&amp; Dubai.</em></h2></div></div>
      <div class="aloc" data-reveal>{offices}{phones}<a class="ccard" href="mailto:{C['email']}">{ICON['mail']}<span><small class="mono">Email</small>{C['email']}</span></a></div>
    </section>
{cta(P, 'Have a part, a building or an idea?', 'Send us photos or drawings for a free quote — we usually reply within one working day.')}"""
    return page(P, 'about.html', 'about', body)

def privacy_page():
    P = ''
    text = open(os.path.join(ROOT, 'data', 'privacy-policy.md'), encoding='utf-8').read()
    updated = re.search(r'^Last updated: (.+)$', text, re.M).group(1)
    text = re.sub(r'^Last updated: .+$', '', text, flags=re.M)
    body = f"""{page_hero(P, [("Privacy Policy", None)], "Legal", "Privacy <em>Policy.</em>", f"Last updated: {E(updated)}")}
    <section class="section blk">
      <div class="prose">
{md(text)}
      </div>
    </section>"""
    return page(P, 'privacy-policy.html', '', body)

def contact_page():
    P = ''
    svc_opts = ''.join(f'<option value="{E(s["name"])}">{E(s["name"])}</option>' for s in D['services'])
    prod_opts = ''.join(f'<option value="{E("Product: " + p["name"])}">Buy a scanner — {E(p["name"])}</option>' for p in D['products'])
    phones = ''.join(f'<a class="ccard" href="tel:{p["tel"]}">{ICON["phone"]}<span><small class="mono">{E(p["label"])}</small>{E(p["display"])}</span></a>' for p in C['phones'])
    addr = ''.join(f'<div class="ccard ccard--static">{ICON["pin"]}<span><small class="mono">{E(o["label"])} office</small>{"<br>".join(E(l) for l in o["lines"])}</span></div>' for o in C['offices'])
    mapq = quote(C['map'])
    gmap = f'''    <section class="section blk cmap" data-reveal>
      <iframe title="Map: VShark Solutions, {E(C['map'])}" src="https://www.google.com/maps?q={mapq}&amp;output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
      <a class="sec-head__link" href="https://www.google.com/maps/search/?api=1&amp;query={mapq}" target="_blank" rel="noopener">Open in Google Maps {A}</a>
    </section>'''
    body = f'''{page_hero(P, [("Contact", None)], "( 06 ) — Contact", "Let's <em>scan it.</em>", "Tell us about your part, building or idea. We usually reply within one working day.")}
    <section class="section blk">
      <div class="contact">
        <form class="cform" id="enquiry" name="enquiry" method="POST" action="send-enquiry.php" data-netlify="true" netlify-honeypot="company_url" enctype="multipart/form-data" data-reveal>
          <input type="hidden" name="form-name" value="enquiry">
          <!-- ad attribution, filled in by js/consent.js from the landing URL -->
          {''.join(f'<input type="hidden" name="{k}" data-attr>' for k in ('utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'fbclid', 'gclid', 'landing_page', 'referrer'))}
          <p class="cform__hp" aria-hidden="true"><label>Leave empty <input name="company_url" tabindex="-1" autocomplete="off"></label></p>
          <div class="cform__grid">
            <label class="field"><span>Name *</span><input name="name" required autocomplete="name"></label>
            <label class="field"><span>Company</span><input name="company" autocomplete="organization"></label>
            <label class="field"><span>Email *</span><input type="email" name="email" required autocomplete="email"></label>
            <label class="field"><span>Phone / WhatsApp</span><input type="tel" name="phone" autocomplete="tel"></label>
            <label class="field field--full"><span>I'm interested in *</span>
              <select name="interest" id="cInterest" required><option value="">Choose a service or product…</option>{svc_opts}{prod_opts}<option value="Other">Something else</option></select></label>
            <label class="field field--full"><span>Project details *</span><textarea name="message" rows="5" required placeholder="Part size, material, quantity, deadline, file formats you need…"></textarea></label>
            <label class="field field--full field--file"><span>Attach a file (optional, max 8 MB)</span><input type="file" name="attachment" accept=".pdf,.jpg,.jpeg,.png,.stl,.step,.stp,.zip"></label>
          </div>
          <label class="consent"><input type="checkbox" name="consent" value="yes" required>
            <span>I agree to VShark Solutions using my details and any files I share to respond to my enquiry, as described in the <a href="privacy-policy.html" target="_blank" rel="noopener">Privacy Policy</a>.</span></label>
          <button class="btn btn--accent magnetic" type="submit"><span>Send enquiry</span>{A}</button>
        </form>
        <aside class="contact__side" data-reveal>
          <a class="ccard ccard--wa" href="{wa_link(WA_DEFAULT)}" target="_blank" rel="noopener">{ICON['wa']}<span><small class="mono">Fastest</small>Chat on WhatsApp</span></a>
          <a class="ccard" href="mailto:{C['email']}">{ICON['mail']}<span><small class="mono">Email</small>{C['email']}</span></a>
          {phones}
          {addr}
        </aside>
      </div>
    </section>
{gmap}'''
    return page(P, 'contact.html', 'contact', body, ('js/contact.js',))

def thanks_page():
    P = ''
    body = f'''{page_hero(P, [("Contact", "contact.html"), ("Thank you", None)], "Enquiry sent", "Thank <em>you.</em>", "We have received your message and will get back to you within one working day.")}
    <section class="section blk"><a class="btn btn--accent magnetic" href="index.html"><span>Back to home</span>{A}</a></section>'''
    return page(P, 'thanks.html', 'contact', body)

def coimbatore_page():
    """S07: local landing page '3D Scanning Services in Coimbatore' (answer-first, FAQ + Service schema)."""
    P = ''
    img = 'img/services/'
    scan_items = [
        ('Machined parts, castings and forgings', 'Capture the real geometry, including wear, shrinkage and casting variation.'),
        ('Moulds, dies and tooling', 'Rebuild tooling that has no drawing, or check it against its CAD.'),
        ('Worn or broken spares', 'Digitise out-of-production parts so they can be remade or repaired.'),
        ('Fixtures, jigs and assemblies', 'Record how an assembly really fits together.'),
        ('Vehicle parts and body panels', 'Scan panels, under-body and suspension areas for design or repair work.'),
        ('Large objects and plant areas', 'On-site scanning is easier than moving the part.'),
    ]
    scan_html = '\n'.join(f'          <div class="feat" data-reveal><i class="mono">{k+1:02d}</i><h3>{E(t)}</h3><p>{E(d)}</p></div>' for k, (t, d) in enumerate(scan_items))
    steps = [('Send the part details', 'A photo and a short description of the part, or the part itself.'),
             ('Confirm method and quote', 'We confirm the scanning method, the output you need and the price.'),
             ('Scan', 'At our Coimbatore facility, or at your plant anywhere in India.'),
             ('Process', 'We clean the scan data and build the mesh or CAD model.'),
             ('Deliver', 'You receive the files and we answer questions on them.')]
    step_html = '\n'.join(f'<li class="step2" data-reveal><i class="mono">{k+1:02d}</i><b>{E(t)}</b><span>{E(d)}</span></li>' for k, (t, d) in enumerate(steps))
    deliver = [('STL or PLY mesh', '3D printing, visual checks and reference.'),
               ('Editable CAD: STEP, IGES, Parasolid', 'Redesign, tooling and manufacturing.'),
               ('Deviation colour map and report', 'Compare a made part against its CAD or a master.'),
               ('Measured 2D drawing', 'Shop-floor use and repair.')]
    del_html = '\n'.join(f'          <div class="feat" data-reveal><i class="mono">{k+1:02d}</i><h3>{E(t)}</h3><p>{E(d)}</p></div>' for k, (t, d) in enumerate(deliver))
    rates = [('Scanner-based inspection and scanning', 'Rs 1,500 per hour'),
             ('Portable CMM arm scanning and inspection', 'Rs 2,500 per hour'),
             ('CAD design from scan data or sketches', 'Rs 1,000 per hour'),
             ('Building, facade and heritage structure scanning', 'Rs 3,000 per hour')]
    rate_html = '\n'.join(f'          <div class="feat" data-reveal><i class="mono">{k+1:02d}</i><h3>{E(t)}</h3><p>{E(r)}</p></div>' for k, (t, r) in enumerate(rates))
    faqs = [
        ('Do you offer 3D scanning in Coimbatore?', 'Yes. VShark Solutions offers 3D scanning in Coimbatore, at our facility or at your plant, and delivers STL meshes or editable CAD files.'),
        ('Can you scan at my factory?', 'Yes. We travel to your plant in Coimbatore and across India. This suits large parts, heavy castings and tooling that cannot be moved.'),
        ('Can you turn a scanned part into editable CAD?', 'Yes. We provide reverse engineering and scan-to-CAD, delivered as STEP files and other neutral formats such as IGES and Parasolid.'),
        ('How long does a 3D scanning job take?', 'Small parts can be scanned in under a day. Larger parts and bigger quantities take more time, and CAD modelling adds time depending on the part. We give a delivery date with the quote.'),
        ('How much does 3D scanning cost in Coimbatore?', 'The price depends on the part size, surface, accuracy and location, so we quote per job. As of November 2026 our listed rates are Rs 1,500 per hour for scanner-based inspection and scanning, Rs 2,500 per hour for portable CMM arm work, Rs 1,000 per hour for CAD design and Rs 3,000 per hour for building scans. On-site travel and accommodation are charged extra.'),
        ('What file formats do you deliver?', 'STL and PLY meshes, and STEP, IGES or Parasolid CAD files. Inspection results come as deviation colour maps and reports.'),
        ('Do you offer CMM inspection in Coimbatore?', 'Yes. We offer CMM arm inspection for dimensional checks against a drawing or CAD model.'),
    ]
    svc_ld = json.dumps({'@context': 'https://schema.org', '@type': 'Service', 'serviceType': '3D scanning',
                         'name': '3D scanning services in Coimbatore',
                         'description': 'On-site and in-house 3D scanning of parts, moulds, castings and tooling, delivered as STL meshes or editable STEP CAD files.',
                         'provider': {'@id': SITE_URL + '#business'},
                         'areaServed': area_served(),
                         'url': SITE_URL + '3d-scanning-services-coimbatore.html'}, ensure_ascii=False).replace('</', '<' + chr(92) + '/')
    body = f"""{page_hero(P, [("Services", "services/index.html"), ("3D scanning in Coimbatore", None)], "( 01 ) — Coimbatore", "3D Scanning Services <em>in Coimbatore.</em>",
        "VShark Solutions Pvt Ltd offers 3D scanning services in Coimbatore, Tamil Nadu. We scan parts, moulds, castings and tooling at our facility or at your plant, then deliver an STL mesh or an editable STEP CAD model.",
        img + '3d-scanning-services-coimbatore-vertex-hero.webp', alt='VShark engineer scanning a car boot floor with a JINUOSH Vertex handheld 3D scanner')}

    <section class="section blk">
      <div class="split">
        <div class="split__main">
          <span class="tag mono">What we scan</span>
          <p class="lead-lg" data-reveal>If a part has no drawing, is worn, or must be checked against its CAD, we can capture it in 3D and turn the scan into data your team can use.</p>
          <div class="feat-grid">
{scan_html}
          </div>
          <figure class="svc-fig" data-reveal><img src="{img}3d-scan-data-of-a-car-wheel-in-scan-software.webp" alt="3D scan data of a car wheel shown in scan software" loading="lazy"></figure>
        </div>
        <aside class="split__side" data-reveal>
          <div class="side-card">
            <span class="mono muted">Get a quote</span>
            <p>Send a photo of the part and what you need from it. We usually reply within one working day.</p>
            <a class="btn btn--accent btn--block magnetic" href="contact.html?service=3d-scanning"><span>Request a quote</span>{A}</a>
          </div>
        </aside>
      </div>
    </section>

    <section class="section blk blk--alt">
      <div class="sec-head"><div><span class="tag mono">How a job works</span><h2 class="h2" data-reveal>Five steps, <em>clear quote.</em></h2></div></div>
      <ol class="steps2">
{step_html}
      </ol>
    </section>

    <section class="section blk">
      <div class="sec-head"><div><span class="tag mono">What you receive</span><h2 class="h2" data-reveal>Files your team <em>can use.</em></h2></div></div>
      <div class="feat-grid">
{del_html}
      </div>
    </section>

    <section class="section blk blk--alt">
      <div class="split">
        <div class="split__main">
          <span class="tag mono">Reverse engineering, inspection and equipment</span>
          <h2 class="h2" data-reveal>Scan to CAD, <em>inspect, or buy the scanner.</em></h2>
          <p class="lead-lg" data-reveal>Many buyers need a CAD model of a part that has no drawing. We turn the scan into an editable model so a tool room or foundry can make, repair or improve the part. We also offer CMM arm inspection for dimensional checks against a drawing or CAD model, and we are the India distributor of JINUOSH Vertex 3D scanners.</p>
          <p data-reveal><a class="sec-head__link" href="services/reverse-engineering.html">Reverse engineering {A}</a> &nbsp; <a class="sec-head__link" href="services/digital-metrology.html">Digital metrology and inspection {A}</a> &nbsp; <a class="sec-head__link" href="products/index.html">JINUOSH Vertex scanners {A}</a></p>
          <figure class="svc-fig" data-reveal><img src="{img}cmm-arm-scanning-splined-shaft.webp" alt="CMM arm scanning a splined shaft on a granite table" loading="lazy"></figure>
        </div>
        <aside class="split__side" data-reveal>
          <div class="side-card">
            <span class="mono muted">Accuracy</span>
            <p>The JINUOSH Vertex3D handheld blue-laser scanner we distribute is specified at up to 0.020 mm (JINUOSH specification, November 2026). We tell you the expected accuracy for your part before we start.</p>
          </div>
        </aside>
      </div>
    </section>

    <section class="section blk">
      <div class="sec-head"><div><span class="tag mono">Pricing, as of November 2026</span><h2 class="h2" data-reveal>Quoted per job, <em>rates listed.</em></h2></div></div>
      <p class="lead-lg" data-reveal>Scanning cost depends on part size, surface, accuracy and location, so we quote per job after seeing the part. Our listed rates for related services in India are below. On-site travel and accommodation are charged extra, and rates can change, so confirm them when you ask for a quote.</p>
      <div class="feat-grid">
{rate_html}
      </div>
    </section>

{faq_section(faqs, '3D scanning in Coimbatore <em>FAQ.</em>')}

    <section class="section blk blk--alt">
      <div class="sec-head"><div><span class="tag mono">Contact</span><h2 class="h2" data-reveal>VShark Solutions <em>Pvt Ltd.</em></h2></div></div>
      <p class="lead-lg" data-reveal>Rajiv Gandhi Nagar, Neelambur, Coimbatore, Tamil Nadu 641062. WhatsApp or call {E(C['phones'][0]['display'])}, or email {E(C['email'])}.</p>
    </section>
    <script type="application/ld+json">{svc_ld}</script>
{cta(P, msg="Hi VShark, I need 3D scanning in Coimbatore for: ")}"""
    return page(P, '3d-scanning-services-coimbatore.html', 'services', body, wa_msg="Hi VShark, I need 3D scanning in Coimbatore for: ")


def notfound_page():
    P = '/'   # served at any missing URL, so every link is root-relative
    links = [('Services', 'services/index.html'), ('3D scanners', 'products/index.html'), ('Portfolio', 'portfolio/index.html'), ('Contact', 'contact.html')]
    chips = ''.join(f'<a class="chip" href="{P}{h}">{E(t)} {A}</a>' for t, h in links)
    body = f"""{page_hero(P, [("Page not found", None)], "Error 404", "Page not <em>found.</em>", "The page you are looking for has moved or no longer exists. These are good places to continue:")}
    <section class="section blk"><div class="ind-chips"><div>{chips}</div></div></section>"""
    return page(P, '404.html', '', body)

def links_page():
    '''/links — bio-link page for Instagram / YouTube / Facebook profiles (dev note 2026-10-27 item 2).'''
    P = ''
    S = C['social']
    ext = ' target="_blank" rel="noopener"'
    items = [
        ('wa', 'Chat on WhatsApp', C['phones'][0]['display'], wa_link(), ext + ' data-wa-location="links_page"', ' blink--wa'),
        ('arrow', 'Get a free quote', 'Send part photos or drawings', 'contact.html', '', ' blink--accent'),
        ('web', 'Website', 'vsharksolutions.com', 'index.html', '', ''),
        ('yt', 'YouTube', 'Scanning demos and projects', S['youtube'], ext, ''),
        ('ig', 'Instagram', '@vshark.solutions', S['instagram'], ext, ''),
        ('fb', 'Facebook', 'VShark Solutions', S['facebook'], ext, ''),
        ('shop', 'IndiaMART', 'Buy Vertex 3D scanners', S['indiamart'], ext, ''),
        ('phone', 'Call India', C['phones'][0]['display'], f'tel:{C["phones"][0]["tel"]}', '', ''),
        ('phone', 'Call UAE', C['phones'][1]['display'], f'tel:{C["phones"][1]["tel"]}', '', ''),
        ('mail', 'Email', C['email'], f'mailto:{C["email"]}', '', ''),
    ]
    rows = '\n'.join(f'        <a class="blink{cls}" href="{href}"{attrs}><span class="blink__ic">{ICON[ic]}</span><span class="blink__t"><b>{E(t)}</b><small>{E(sub)}</small></span>{A}</a>'
                     for ic, t, sub, href, attrs, cls in items)
    body = f'''    <section class="section blk blinks">
      <div class="blinks__head" data-in>
        <img class="blinks__logo" src="img/emblem-512.png" alt="VShark Solutions emblem">
        <h1 class="h2">VShark <em>Solutions</em></h1>
        <p class="muted">3D scanning, reverse engineering and Vertex 3D scanners · Coimbatore, India &amp; Dubai, UAE</p>
      </div>
      <nav class="blinks__list" aria-label="VShark links">
{rows}
      </nav>
    </section>'''
    return page(P, 'links.html', '', body)

def llms_txt():
    '''/llms.txt — plain-language summary of the site for AI search tools (llmstxt.org format).'''
    u = page_url
    S = C['social']
    svc = '\n'.join(f'- [{s["name"]}]({u("services/" + s["slug"] + ".html")}): {META["services/" + s["slug"] + ".html"][1]}' for s in D['services'])
    ind = '\n'.join(f'- [{i["name"]}]({u("industries/" + i["slug"] + ".html")}): {i["line"]}' for i in D['industries'])
    prod = '\n'.join(f'- [{p["name"]}]({u("products/index.html")}#{p["slug"]}): {p["type"]}. {p["summary"]}' for p in D['products'])
    phones = ' · '.join(f'{p["display"]} ({p["label"]})' for p in C['phones'])
    txt = f'''# VShark Solutions

> VShark Solutions Private Limited is a 3D scanning, reverse engineering and 3D design company based in Coimbatore, Tamil Nadu, India, with a presence in Dubai, United Arab Emirates. Since 2019 it has served manufacturers, engineers, builders, jewellers and research labs across India, the UAE and worldwide, and it is the India distributor of JINUOSH Vertex 3D scanners in India.

- Locations: Coimbatore, Tamil Nadu, India (head office: {C['offices'][0]['street']}, {C['offices'][0]['city']} {C['offices'][0]['postcode']}) and Dubai, UAE. On-site service across India and the UAE.
- Contact: {C['email']} · {phones} · WhatsApp +91 95142 48525
- Free quotes: send part photos, drawings or scan data through {u('contact.html')}

## Services

{svc}

## Products (JINUOSH Vertex 3D scanners, sold, installed and supported in India)

{prod}

## Industries

{ind}

## Key pages

- [Home]({u('')}): overview of services, scanners and industries
- [About]({u('about.html')}): company background, how we work, locations
- [Portfolio]({u('portfolio/index.html')}): completed scanning, CAD and inspection projects
- [Contact]({u('contact.html')}): enquiry form, phone, WhatsApp and office addresses
- [Vertex3D and Vertex3D Pro in India]({u('jinuosh-vertex-3d-scanner-india.html')}): specifications, what is included, FAQs
- [Vertex Tracker in India]({u('vertex-tracker.html')}): optical-tracking scanner specifications and FAQs
- [3D scanning services in Coimbatore]({u('3d-scanning-services-coimbatore.html')}): on-site scanning, reverse engineering and inspection
- [JINUOSH Vertex vs Creaform, Shining 3D, GOM: how to compare]({u('jinuosh-vertex-vs-creaform-shining-3d-gom.html')})
- [Best 3D scanning service in Coimbatore: how to choose]({u('best-3d-scanning-service-coimbatore.html')})
- [3D scanning services in India]({u('3d-scanning-services-india.html')})
- [3D scanning services in Pune]({u('3d-scanning-services-pune.html')})
- [3D scanning services in Chennai]({u('3d-scanning-services-chennai.html')})
- [3D scanning services in Hyderabad]({u('3d-scanning-services-hyderabad.html')})
- [3D scanning services in Bengaluru]({u('3d-scanning-services-bengaluru.html')})
- [3D scanning and reverse engineering for the UAE]({u('3d-scanning-services-uae.html')})
- [Reverse engineering services in India]({u('reverse-engineering-services-india.html')})
- [Reverse engineering services in Tamil Nadu]({u('reverse-engineering-services-tamil-nadu.html')})
- [Reverse engineering in Coimbatore]({u('reverse-engineering-coimbatore.html')})
- [Automotive 3D scanning and reverse engineering in India]({u('automotive-reverse-engineering-india.html')})
- [Mould and die 3D scanning and reverse engineering in India]({u('mould-die-3d-scanning-india.html')})
- [Casting and foundry 3D scanning and inspection in India]({u('casting-foundry-3d-scanning-india.html')})
- [Industrial machinery 3D scanning and spare parts in India]({u('industrial-machinery-spare-parts-3d-scanning-india.html')})
- [3D printing from your 3D scan in India]({u('3d-printing-from-scan-india.html')})
- [3D scanning cost in India: what decides the quote]({u('3d-scanning-cost-india.html')})
- [Spare part with no drawing: how we rebuild it]({u('spare-part-no-drawing-reverse-engineering.html')})
- [CMM inspection services in Coimbatore]({u('cmm-inspection-services.html')})

## Social

- YouTube: {S['youtube']}
- Instagram: {S['instagram']}
- Facebook: {S['facebook']}
- LinkedIn: {S['linkedin']}
- IndiaMART: {S['indiamart']}
'''
    if BLOG_POSTS:
        blog = '\n'.join(f'- [{q["title"]}]({u("blog/" + q["slug"] + "/")}): {q["description"]}' for q in reversed(BLOG_POSTS))
        txt = txt.replace('## Social', f'## Blog\n\n- [All articles]({u("blog/")})\n{blog}\n\n## Social', 1)
    open(os.path.join(ROOT, 'llms.txt'), 'w', encoding='utf-8', newline='\n').write(txt)

# ---------------------------------------------------------------- image width/height (prevents layout shift)
def image_size(path):
    '''(width, height) of a PNG, JPEG or WebP file, read from its header — no Pillow needed.'''
    with open(path, 'rb') as f:
        h = f.read(64)
        if h[:8] == b'\x89PNG\r\n\x1a\n':
            return int.from_bytes(h[16:20], 'big'), int.from_bytes(h[20:24], 'big')
        if h[:4] == b'RIFF' and h[8:12] == b'WEBP':
            kind = h[12:16]
            if kind == b'VP8 ':
                return int.from_bytes(h[26:28], 'little') & 0x3FFF, int.from_bytes(h[28:30], 'little') & 0x3FFF
            if kind == b'VP8L':
                b = int.from_bytes(h[21:25], 'little')
                return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
            if kind == b'VP8X':
                return int.from_bytes(h[24:27], 'little') + 1, int.from_bytes(h[27:30], 'little') + 1
        if h[:2] == b'\xff\xd8':
            f.seek(2)
            while True:
                m = f.read(4)
                if len(m) < 4 or m[0] != 0xFF:
                    return None
                seg = int.from_bytes(m[2:4], 'big')
                if 0xC0 <= m[1] <= 0xCF and m[1] not in (0xC4, 0xC8, 0xCC):
                    d = f.read(5)
                    return int.from_bytes(d[3:5], 'big'), int.from_bytes(d[1:3], 'big')
                f.seek(seg - 2, 1)
    return None

def add_image_sizes(rel):
    '''Give every local <img> in a built page its intrinsic width/height (CSS keeps height:auto).'''
    path = os.path.join(ROOT, rel)
    base = os.path.dirname(path)
    s = open(path, encoding='utf-8').read()
    def fix(m):
        tag = m.group(0)
        if re.search(r'\swidth=', tag):
            return tag
        src = re.search(r'\ssrc="([^"?#]+)', tag)
        if not src or src.group(1).startswith(('http:', 'https:', 'data:', '//')):
            return tag
        f = src.group(1)
        f = os.path.join(ROOT, f.lstrip('/')) if f.startswith('/') else os.path.normpath(os.path.join(base, f))
        size = image_size(f) if os.path.exists(f) else None
        if not size:
            print(f'  ! {rel}: no size for {src.group(1)}')
            return tag
        return tag[:4] + f' width="{size[0]}" height="{size[1]}"' + tag[4:]
    s2 = re.sub(r'<img\b[^>]*>', fix, s)
    if s2 != s:
        open(path, 'w', encoding='utf-8', newline='\n').write(s2)

def sitemap_and_robots(pages):
    """sitemap.xml (handoff B6) lists every public page; robots.txt points to it."""
    skip = {'thanks.html', '404.html'}
    urls = ['index.html'] + [r for r in pages if r not in skip]
    def loc(r):
        return SITE_URL + ('' if r == 'index.html' else r[:-len('index.html')] if r.endswith('/index.html') else r)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        f'  <url><loc>{loc(r)}</loc><lastmod>{LASTMOD[r]["date"]}</lastmod></url>\n' for r in urls) + '</urlset>\n'
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n').write(xml)
    robots = f'User-agent: *\nAllow: /\nDisallow: /build/\nDisallow: /data/\n\nSitemap: {SITE_URL}sitemap.xml\n'
    open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf-8', newline='\n').write(robots)

# ---------------------------------------------------------------- homepage regions
def home_products():
    P = ''
    return '<!-- @products -->\n      <div class="prod-grid" id="productGrid">\n' + '\n'.join(
        prod_tile(P, p, i, f'products/index.html#{p["slug"]}') for i, p in enumerate(D['products'])) + '\n      </div>\n      <!-- /@products -->'

def home_services():
    n = len(D['services'])
    items = '\n'.join(f'''          <li class="svx__row">
            <button class="svx__item{' is-active' if i == 0 else ''}" type="button" role="tab" id="svxTab{i}" aria-selected="{'true' if i == 0 else 'false'}" aria-controls="svxPanel"
              data-name="{E(s['name'])}" data-desc="{E(s['tagline'])}" data-href="services/{s['slug']}.html">
              <span class="svx__n mono">{i+1:02d}</span><b>{E(s['name'])}</b>{A}<i class="svx__bar"></i>
            </button>
            <div class="svx__drop">
              <img src="{s['tile']}" alt="{E(s['alt'])}" loading="lazy">
              <p>{E(s['tagline'])}</p>
              <a href="services/{s['slug']}.html" class="svx__link">Learn more {A}</a>
            </div>
          </li>''' for i, s in enumerate(D['services']))
    imgs = '\n'.join(f'          <img class="svx__img{" is-on" if i == 0 else ""}" src="{s["tile"]}" alt="{E(s["alt"])}" loading="lazy">' for i, s in enumerate(D['services']))
    f = D['services'][0]
    return f'''<!-- @services -->
      <div class="svx" id="svx">
        <ol class="svx__list" role="tablist" aria-label="Services">
{items}
        </ol>
        <div class="svx__stage" id="svxPanel" role="tabpanel" aria-labelledby="svxTab0">
          <div class="svx__media">
{imgs}
            <span class="svx__scan" aria-hidden="true"></span>
            <i class="svx__slash" aria-hidden="true"></i>
          </div>
          <div class="svx__info">
            <span class="svx__count mono"><b>01</b> / {n:02d}</span>
            <h3 class="svx__title">{E(f['name'])}</h3>
            <p class="svx__desc">{E(f['tagline'])}</p>
            <a class="svx__link svx__more" href="services/{f['slug']}.html">Learn more {A}</a>
          </div>
        </div>
      </div>
      <!-- /@services -->'''

def home_industries():
    panels = '\n'.join(f'''        <div class="ip{' is-active' if i == 0 else ''}" role="button" tabindex="0" aria-pressed="{'true' if i == 0 else 'false'}" aria-label="{E(s['name'])}">
          <picture><source media="(max-width: 760px)" srcset="{s['square']}"><img src="{s['image']}" alt="{E(s['alt'])}" loading="lazy" draggable="false"></picture>
          <span class="ip__num mono">{i+1:02d}</span>
          <span class="ip__label">{E(s['name'])}</span>
          <span class="ip__body"><b>{E(s['name'])}</b><span>{E(s['line'])}</span><a class="ip__go" href="industries/{s['slug']}.html">Explore {E(s['name'].lower())} {A}</a></span>
          <i class="ip__scan" aria-hidden="true"></i>
          <i class="ip__bar" aria-hidden="true"></i>
        </div>''' for i, s in enumerate(D['industries']))
    return f'''<!-- @industries -->
      <div class="ind-acc" id="indAcc" role="group" aria-label="Industries">
{panels}
      </div>
      <!-- /@industries -->'''

def build_home():
    p = os.path.join(ROOT, 'index.html')
    s = open(p, encoding='utf-8').read()
    regions = {'header': header('', ''), 'footer': footer(''), 'products': home_products(),
               'services': home_services(), 'industries': home_industries(),
               'meta': '<!-- @meta -->\n  ' + head_meta('') + '\n  ' + schema_org() + '\n  <!-- /@meta -->'}
    for name, content in regions.items():
        pat = re.compile(r'<!-- @%s -->.*?<!-- /@%s -->' % (name, name), re.S)
        if not pat.search(s):
            sys.exit(f'index.html: missing region @{name}')
        s = pat.sub(lambda m: content, s)
    # fingerprint local css/js
    s = re.sub(r'(href|src)="((?:css|js|fonts)/[\w.-]+\.(?:css|js))(?:\?v=[\w]+)?"', lambda m: f'{m.group(1)}="{asset(m.group(2), "")}"', s)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)

# ---------------------------------------------------------------- blog (S10 / audit F3, handoff Part F)
BLOG_DIR = os.path.join(ROOT, 'data', 'blog')
BLOG_CATS = [('Reverse Engineering', 'reverse-engineering'), ('3D Scanning', '3d-scanning'), ('Inspection & Metrology', 'inspection-metrology'),
             ('Scan to BIM', 'scan-to-bim'), ('Class A Surfacing', 'class-a-surfacing'), ('3D Printing', '3d-printing'), ('3D Scanners', '3d-scanners')]
CAT_SLUG = dict(BLOG_CATS)
BLOG_PER_PAGE = 9
OG_POST = {}      # rel -> (image url, width, height, alt) for per-post og:image

def blog_href(u, P):
    """Site-relative paths used in the post text (/services/x, /contact?service=x ...) -> real file paths."""
    if u.startswith(('http', 'mailto:', 'tel:', '#')):
        return u
    path, _, q = u.partition('?')
    q = '?' + q if q else ''
    path = path.strip('/')
    if path == '':
        return P + 'index.html'
    if path.startswith(('services/', 'industries/')) and not path.endswith('.html'):
        return P + path + '.html' + q
    if path in ('contact', 'about', 'privacy-policy', '3d-scanning-services-coimbatore', 'vertex-tracker', 'jinuosh-vertex-3d-scanner-india', 'best-3d-scanning-service-coimbatore', 'jinuosh-vertex-vs-creaform-shining-3d-gom', 'reverse-engineering-services-india', '3d-scanning-services-india', 'spare-part-no-drawing-reverse-engineering', 'cmm-inspection-services', 'reverse-engineering-services-tamil-nadu', 'automotive-reverse-engineering-india', 'mould-die-3d-scanning-india', 'casting-foundry-3d-scanning-india', 'industrial-machinery-spare-parts-3d-scanning-india', '3d-printing-from-scan-india', '3d-scanning-cost-india', 'reverse-engineering-coimbatore', '3d-scanning-services-pune', '3d-scanning-services-chennai', '3d-scanning-services-hyderabad', '3d-scanning-services-bengaluru', '3d-scanning-services-uae'):
        return P + path + '.html' + q
    if path in ('products', 'portfolio', 'services', 'industries', 'blog') or path.startswith('blog/'):
        return P + path + '/' + q
    print('  WARNING blog link not mapped:', u)
    return P + path + q

def blog_inline(t, P):
    t = E(t)
    t = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', lambda m: f'<a href="{blog_href(html.unescape(m.group(2)), P)}">{m.group(1)}</a>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*([^*\n]+?)\*(?![\w*])', r'<em>\1</em>', t)
    return t

def blog_md(text, P, skip_img=None):
    """Markdown subset used by the posts: ### / #### headings, paragraphs, lists, tables, images, blockquotes."""
    out, lines, i = [], text.strip().split('\n'), 0
    while i < len(lines):
        l = lines[i]
        if not l.strip():
            i += 1
        elif l.startswith('### '):
            h = l[4:].strip()
            out.append(f'<h2 id="{re.sub(r"[^a-z0-9]+", "-", h.lower()).strip("-")}">{blog_inline(h, P)}</h2>'); i += 1
        elif l.startswith('#### '):
            out.append(f'<h3>{blog_inline(l[5:].strip(), P)}</h3>'); i += 1
        elif l.strip() == '---':
            i += 1
        elif re.match(r'!\[[^\]]*\]\([^)]+\)\s*$', l.strip()):
            alt, src = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', l.strip()).groups()
            if src != skip_img:
                out.append(f'<figure class="post-fig"><img src="{P}{src}" alt="{E(alt)}" loading="lazy"><figcaption>{E(alt)}</figcaption></figure>')
            i += 1
        elif l.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split(' | ')] if ' | ' in lines[i] else [c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            head, body = rows[0], [r for r in rows[1:] if not all(re.fullmatch(r':?-+:?', c) for c in r)]
            th = ''.join(f'<th>{blog_inline(c, P)}</th>' for c in head)
            tb = ''.join('<tr>' + ''.join(f'<td>{blog_inline(c, P)}</td>' for c in r) + '</tr>' for r in body)
            out.append(f'<div class="post-table"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>')
        elif re.match(r'(- |\* )', l):
            items = []
            while i < len(lines) and re.match(r'(- |\* )', lines[i]):
                items.append(f'<li>{blog_inline(lines[i][2:], P)}</li>'); i += 1
            out.append('<ul>' + ''.join(items) + '</ul>')
        elif re.match(r'\d+\. ', l):
            items = []
            while i < len(lines) and re.match(r'\d+\. ', lines[i]):
                li = re.sub(r'^\d+\. ', '', lines[i])
                items.append(f'<li>{blog_inline(li, P)}</li>'); i += 1
            out.append('<ol>' + ''.join(items) + '</ol>')
        elif l.startswith('@video '):
            url, _, vt = l[7:].partition(' | ')
            out.append(f'<div class="post-video">{video_embed(P, url.strip(), vt.strip())}</div>'); i += 1
        elif l.startswith('> '):
            q = []
            while i < len(lines) and lines[i].startswith('>'):
                q.append(lines[i][1:].strip()); i += 1
            out.append('<blockquote><p>' + blog_inline(' '.join(q), P) + '</p></blockquote>')
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(r'(#|\||- |\* |\d+\. |> |!\[|---|@video)', lines[i]):
                para.append(blog_inline(lines[i].strip(), P)); i += 1
            out.append('<p>' + ' '.join(para) + '</p>')
    return '\n'.join(out)

def load_posts():
    import datetime
    dates = json.load(open(os.path.join(BLOG_DIR, 'dates.json'), encoding='utf-8'))
    today = datetime.date.today().isoformat()
    posts = []
    for fn in sorted(os.listdir(BLOG_DIR)):
        if not fn.endswith('.md'):
            continue
        raw = open(os.path.join(BLOG_DIR, fn), encoding='utf-8').read()
        _, fm, body = raw.split('---\n', 2)
        p = dict(re.findall(r'(?m)^(\w+): (.*)$', fm))
        p['date'] = dates.get(p['slug'], today)
        if p['date'] > today:
            continue          # scheduled for later: not built, not in the sitemap
        faq_at = body.find('### FAQ')
        faq_txt = body[faq_at + 7:] if faq_at >= 0 else ''
        body = body[:faq_at] if faq_at >= 0 else body
        p['faqs'] = [(q.strip(), re.sub(r'\s+', ' ', a.strip())) for q, a in re.findall(r'\*\*(.+?)\*\*\n(.+?)(?=\n\n\*\*|\Z)', faq_txt.strip(), re.S)]
        p['body'] = body.strip()
        p['mins'] = max(2, round(len(re.sub(r'[#*|!\[\]()-]', ' ', body).split()) / 200))
        p['cat_slug'] = CAT_SLUG[p['category']]
        p['rel'] = f'blog/{p["slug"]}/index.html'
        p['order'] = int(p['order'])
        posts.append(p)
    return sorted(posts, key=lambda p: (p['date'], p['order']))

def _date_nice(d):
    import datetime
    return datetime.date.fromisoformat(d).strftime('%d %b %Y').lstrip('0')

def post_card(P, p):
    img = p['featured']
    return f'''        <article class="bcard" data-reveal>
          <a class="bcard__media" href="{P}blog/{p['slug']}/" tabindex="-1" aria-hidden="true"><img src="{P}{img}" alt="" loading="lazy"></a>
          <div class="bcard__body">
            <span class="mono bcard__meta">{E(p['category'])} · {p['mins']} min read</span>
            <h3 class="bcard__title"><a href="{P}blog/{p['slug']}/">{E(p['title'])}</a></h3>
            <p>{E(p['description'])}</p>
            <a class="bcard__more mono" href="{P}blog/{p['slug']}/">Read article &rarr;</a>
          </div>
        </article>'''

def blog_chips(P, current=None):
    chips = [f'<a class="chip{" is-current" if current is None else ""}" href="{P}blog/">All</a>'] + [
        f'<a class="chip{" is-current" if current == s else ""}" href="{P}blog/category/{s}/">{E(n)}</a>' for n, s in BLOG_CATS]
    return '<nav class="bchips" aria-label="Blog categories">' + ''.join(chips) + '</nav>'

def blog_listing(posts_all, cat=None, pg=1):
    """One listing page: /blog/, /blog/page/N/, /blog/category/<slug>/ (9 per page)."""
    sel = [p for p in reversed(posts_all) if cat is None or p['cat_slug'] == cat]
    pages = max(1, -(-len(sel) // BLOG_PER_PAGE))
    chunk = sel[(pg - 1) * BLOG_PER_PAGE: pg * BLOG_PER_PAGE]
    if cat:
        name = next(n for n, s in BLOG_CATS if s == cat)
        rel = f'blog/category/{cat}/index.html' if pg == 1 else f'blog/category/{cat}/page/{pg}/index.html'
        P = '../' * rel.count('/')
        crumbs_ = [("Blog", P + 'blog/'), (name, None)]
        title, lead = f'{E(name)} <em>articles.</em>', f'Guides and answers on {E(name.lower())} from the VShark engineering team.'
        META[rel] = (f'{name} Articles | VShark Solutions Blog', f'Articles on {name.lower()} from VShark Solutions: practical guides for manufacturers in India and the UAE.')
    else:
        rel = 'blog/index.html' if pg == 1 else f'blog/page/{pg}/index.html'
        P = '../' * rel.count('/')
        crumbs_ = [("Blog", None)]
        title, lead = 'Notes from the <em>scanning bench.</em>', 'Practical guides on 3D scanning, reverse engineering, inspection and scan-to-CAD, written by the VShark engineering team.'
        META[rel] = ('3D Scanning & Reverse Engineering Blog | VShark Solutions', 'Practical guides on 3D scanning, reverse engineering, scan to CAD, Scan to BIM, Class A surfacing and 3D inspection from VShark Solutions, India and the UAE.')
    if pg > 1:
        title_t, desc_t = META[rel]
        META[rel] = (f'{title_t.split(" | ")[0]} - Page {pg} | VShark Solutions', desc_t)
    cards = '\n'.join(post_card(P, p) for p in chunk) or '        <p>No articles in this category yet.</p>'
    base = f'blog/category/{cat}/' if cat else 'blog/'
    nav = ''
    if pages > 1:
        links = [f'<a class="chip{" is-current" if n == pg else ""}" href="{P}{base}{"" if n == 1 else f"page/{n}/"}">{n}</a>' for n in range(1, pages + 1)]
        nav = '<nav class="bchips bchips--pages" aria-label="Pages">' + ''.join(links) + '</nav>'
    body = f'''{page_hero(P, crumbs_, 'Blog', title, lead)}
    <section class="section blk">
      {blog_chips(P, cat)}
      <div class="bgrid">
{cards}
      </div>
      {nav}
    </section>
{cta(P)}'''
    return rel, page(P, rel, 'blog', body)

def blog_post(p, posts_all):
    rel, P = p['rel'], '../../'
    META[rel] = (p['title_tag'], p['description'])
    m = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', p['body'])
    f_alt = m.group(1) if m and m.group(2) == p['featured'] else p['title']
    d = _dims(os.path.join(ROOT, p['featured']))
    OG_POST[rel] = (SITE_URL + p['featured'], d[0], d[1], f_alt)
    body_html = blog_md(p['body'], P, skip_img=p['featured'])
    url = SITE_URL + f'blog/{p["slug"]}/'
    share = ''.join(f'<a class="chip" href="{h}" target="_blank" rel="noopener">{n}</a>' for n, h in [
        ('LinkedIn', 'https://www.linkedin.com/sharing/share-offsite/?url=' + quote(url, safe='')),
        ('WhatsApp', 'https://wa.me/?text=' + quote(p['title'] + ' ' + url, safe='')),
        ('Facebook', 'https://www.facebook.com/sharer/sharer.php?u=' + quote(url, safe='')),
        ('X', 'https://twitter.com/intent/tweet?url=' + quote(url, safe='') + '&text=' + quote(p['title'], safe=''))])
    svc = p['service'].strip('/')
    qs = svc.split('/')[-1] if svc.startswith('services/') else ('' if svc.startswith('products') else svc.split('/')[-1])
    quote_href = f'{P}contact.html' + (f'?service={qs}' if svc.startswith('services/') else '')
    related = [q for q in reversed(posts_all) if q['slug'] != p['slug']]
    related.sort(key=lambda q: q['cat_slug'] != p['cat_slug'])
    rel_cards = '\n'.join(post_card(P, q) for q in related[:3])
    body = f'''{page_hero(P, [("Blog", P + 'blog/'), (p['category'], P + f"blog/category/{p['cat_slug']}/"), (p['title'], None)],
        f"{E(p['category'])} · {_date_nice(p['date'])} · {p['mins']} min read", E(p['title']), E(p['description']), p['featured'], alt=f_alt)}
    <article class="section blk">
      <div class="prose prose--post">
{body_html}
      </div>
      <p class="post-byline mono">By VShark Engineering Team · Published {_date_nice(p['date'])}</p>
      <div class="post-share"><span class="mono">Share</span>{share}</div>
    </article>
{faq_section(p['faqs'], 'Common <em>questions.</em>')}
    <section class="cta-band">
      <div class="cta-band__inner">
        <h2 class="h2">Have a part to scan, model or inspect?</h2>
        <p>Send photos or drawings for a free quote.</p>
        <div class="cta-band__actions">
          <a class="btn btn--light magnetic" href="{quote_href}"><span>Get a quote</span>{A}</a>
          <a class="btn btn--outline-light magnetic" href="{wa_link(WA_DEFAULT)}" target="_blank" rel="noopener">{ICON['wa']}<span>WhatsApp us</span></a>
        </div>
        <p class="mono">India {E(C['phones'][0]['display'])} · UAE {E(C['phones'][1]['display'])}</p>
      </div>
    </section>
    <section class="section blk blk--alt">
      <div class="sec-head"><div><span class="tag mono">Keep reading</span><h2 class="h2" data-reveal>Related <em>articles.</em></h2></div></div>
      <div class="bgrid">
{rel_cards}
      </div>
    </section>'''
    return rel, page(P, rel, 'blog', body)

def build_blog():
    posts = load_posts()
    out = []
    for p in posts:
        rel, h = blog_post(p, posts)
        out.append(write(rel, h))
    pages = max(1, -(-len(posts) // BLOG_PER_PAGE))
    for pg in range(1, pages + 1):
        rel, h = blog_listing(posts, None, pg); out.append(write(rel, h))
    for _, s in BLOG_CATS:
        n = len([p for p in posts if p['cat_slug'] == s])
        if n:
            for pg in range(1, max(1, -(-n // BLOG_PER_PAGE)) + 1):
                rel, h = blog_listing(posts, s, pg); out.append(write(rel, h))
    BLOG_POSTS[:] = posts
    return out

BLOG_POSTS = []


# ---------------------------------------------------------------- Vertex product pages (S16)
PRODUCT_PAGES = {}   # rel -> front matter, for schema
PAGES_DIR = os.path.join(ROOT, 'data', 'pages')
PRODUCT_LD = {
    'jinuosh-vertex-3d-scanner-india.html': [
        ('Vertex3D', 'Handheld blue-laser 3D scanner with 26 crossed blue laser lines, up to 0.020 mm accuracy and a 650 x 550 mm scanning field.',
         'img/products/jinuosh-vertex3d-handheld-blue-laser-3d-scanner-front.webp', '1.07 kg'),
        ('Vertex3D Pro', 'Handheld blue-laser 3D scanner with 50 crossed blue laser lines, up to 0.020 mm accuracy and a 650 x 550 mm scanning field.',
         'img/products/vertex3d-pro.png', '1.15 kg')],
    'vertex-tracker.html': [
        ('Vertex Tracker', 'Optical-tracking 3D scanning system with up to 0.025 mm accuracy and a 1100 x 800 mm scanning field, for large parts.',
         'img/products/vertex-tracker.png', None)],
}

def reviewed_p(m):
    """Optional front-matter key reviewed: YYYY-MM-DD -> visible 'Last reviewed' line."""
    if not m.get('reviewed'):
        return ''
    d = datetime.date.fromisoformat(m['reviewed'].strip())
    return f'\n        <p class="muted"><small>Last reviewed: <time datetime="{d.isoformat()}">{d.strftime("%B %Y")}</time></small></p>'

def build_product_pages():
    out = []
    for fn in sorted(os.listdir(PAGES_DIR)):
        raw = open(os.path.join(PAGES_DIR, fn), encoding='utf-8').read()
        _, fm, body = raw.split('---\n', 2)
        m = dict(re.findall(r'(?m)^(\w+): (.*)$', fm))
        rel, P = m['rel'], ''
        META[rel] = (m['title_tag'], m['description'])
        PRODUCT_PAGES[rel] = m
        faq_at = body.find('### FAQ')
        faq_txt, body = body[faq_at + 7:], body[:faq_at]
        faqs = [(q.strip(), re.sub(r'\s+', ' ', a.strip())) for q, a in re.findall(r'\*\*(.+?)\*\*\n(.+?)(?=\n\n\*\*|\Z)', faq_txt.strip(), re.S)]
        hero = page_hero(P, [(m.get('crumb_label', 'Products'), P + m.get('crumb_href', 'products/index.html')), (re.sub('<[^>]+>', '', m['h1']), None)], m['tag'], m['h1'], E(m['lead']), m['image'], alt=m['image_alt'])
        html_page = f'''{hero}
    <article class="section blk">
      <div class="prose prose--post">
{blog_md(body, P)}{reviewed_p(m)}
      </div>
    </article>
{faq_section(faqs, 'Common <em>questions.</em>')}
    <section class="cta-band">
      <div class="cta-band__inner">
        <h2 class="h2">{m.get('cta_title', 'See it scan your part.')}</h2>
        <p>{E(m['cta_text']) if 'cta_text' in m else 'Request a quote, a free demo or a free sample scan. Send a photo of your part on WhatsApp.'}</p>
        <div class="cta-band__actions">
          <a class="btn btn--light magnetic" href="{P}{html.escape(m['cta_href']) if 'cta_href' in m else 'contact.html?product=' + m['product']}"><span>Request a quote</span>{A}</a>
          <a class="btn btn--outline-light magnetic" href="{wa_link(m['wa_msg'] if 'wa_msg' in m else WA_DEFAULT)}" target="_blank" rel="noopener">{ICON['wa']}<span>WhatsApp us</span></a>
        </div>
        <p class="mono">India {E(C['phones'][0]['display'])} · UAE {E(C['phones'][1]['display'])}</p>
      </div>
    </section>'''
        out.append(write(rel, page(P, rel, m.get('active', 'products'), html_page, wa_msg=m['wa_msg'] if 'wa_msg' in m else WA_DEFAULT)))
    return out

# ---------------------------------------------------------------- final pass (S05/S07 technical SEO)
LASTMOD_FILE = os.path.join(ROOT, 'data', 'lastmod.json')
LASTMOD = json.load(open(LASTMOD_FILE, encoding='utf-8')) if os.path.exists(LASTMOD_FILE) else {}
_DIMS = {}
IMG_RE = re.compile(r'<img\b[^>]*>')

def _dims(path):
    if path not in _DIMS:
        try:
            from PIL import Image
            with Image.open(path) as im:
                _DIMS[path] = im.size
        except Exception:
            _DIMS[path] = None
    return _DIMS[path]

def add_dims(html_text, rel):
    """Intrinsic width/height on every local <img> (audit F9, layout shift). CSS keeps height:auto, see css/style.css."""
    base = os.path.dirname(os.path.join(ROOT, rel))
    def fix(m):
        tag = m.group(0)
        if re.search(r'\swidth=', tag):
            return tag
        src = re.search(r'\ssrc="([^"]+)"', tag)
        if not src or src.group(1).startswith(('http', 'data:')):
            return tag
        u = src.group(1).split('?')[0]
        d = _dims(os.path.normpath(os.path.join(ROOT, u.lstrip('/')) if u.startswith('/') else os.path.join(base, u)))
        if not d:
            return tag
        return tag.replace('<img', f'<img width="{d[0]}" height="{d[1]}"', 1)
    return IMG_RE.sub(fix, html_text)

def extra_ld(rel):
    """BreadcrumbList on inner pages, Service on service pages, Organization + WebSite on the home page."""
    blocks = []
    url = canonical_url(rel)
    if rel in ('', 'index.html'):
        S = C['social']
        blocks.append({'@context': 'https://schema.org', '@type': 'Organization', '@id': SITE_URL + '#organization',
                       'name': 'VShark Solutions Private Limited', 'alternateName': 'VShark Solutions', 'url': SITE_URL,
                       'logo': SITE_URL + 'img/vshark-logo.png', 'email': C['email'],
                       'sameAs': [S['facebook'], S['instagram'], S['linkedin']] + ([S['youtube']] if S.get('youtube') else [])})
        blocks.append({'@context': 'https://schema.org', '@type': 'WebSite', '@id': SITE_URL + '#website', 'url': SITE_URL,
                       'name': 'VShark Solutions', 'publisher': {'@id': SITE_URL + '#organization'}, 'inLanguage': 'en'})
    elif rel in PRODUCT_LD:
        trail = [('Home', SITE_URL), ('Products', SITE_URL + 'products/'), (META[rel][0].split(' | ')[0], url)]
        for name, desc, img, wt in PRODUCT_LD[rel]:
            node = {'@context': 'https://schema.org', '@type': 'Product', 'name': name, 'description': desc, 'image': SITE_URL + img,
                    'brand': {'@type': 'Brand', 'name': 'JINUOSH'}, 'category': '3D scanner', 'url': url}
            if wt:
                node['weight'] = {'@type': 'QuantitativeValue', 'value': float(wt.split()[0]), 'unitCode': 'KGM'}
            blocks.append(node)
        blocks.append({'@context': 'https://schema.org', '@type': 'BreadcrumbList',
                       'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(trail)]})
    elif rel in PRODUCT_PAGES and PRODUCT_PAGES[rel].get('service_ld'):
        pm = PRODUCT_PAGES[rel]
        trail = [('Home', SITE_URL), (pm['crumb_label'], SITE_URL + pm['crumb_href']), (META[rel][0].split(' | ')[0], url)]
        blocks.append({'@context': 'https://schema.org', '@type': 'Service', 'serviceType': pm.get('service_type', '3D scanning'), 'name': META[rel][0], 'description': META[rel][1],
                       'url': url, 'provider': {'@id': SITE_URL + '#business'},
                       'areaServed': area_served(pm.get('area_cities', '').split('|'))})
        blocks.append({'@context': 'https://schema.org', '@type': 'BreadcrumbList',
                       'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(trail)]})
    elif rel.startswith('blog/'):
        post = next((q for q in BLOG_POSTS if q['rel'] == rel), None)
        trail = [('Home', SITE_URL), ('Blog', SITE_URL + 'blog/')]
        if post:
            trail += [(post['category'], SITE_URL + f"blog/category/{post['cat_slug']}/"), (post['title'], url)]
            blocks.append({'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': post['title'], 'description': post['description'],
                           'image': OG_POST[rel][0], 'author': {'@type': 'Organization', 'name': 'VShark Solutions'},
                           'publisher': {'@id': SITE_URL + '#business'}, 'datePublished': post['date'], 'dateModified': post['date'],
                           'mainEntityOfPage': url, 'inLanguage': 'en'})
        elif '/category/' in rel:
            cs = rel.split('/')[2]
            trail.append((next(n for n, c in BLOG_CATS if c == cs), url))
        blocks.append({'@context': 'https://schema.org', '@type': 'BreadcrumbList',
                       'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(trail)]})
    else:
        trail = [('Home', SITE_URL)]
        folder, _, leaf = rel.rpartition('/')
        title = META[rel][0].split(' | ')[0].split(' – ')[0]
        item = (SVC if folder == 'services' else IND if folder == 'industries' else {}).get(leaf[:-5])
        if folder in ('services', 'industries') and leaf != 'index.html':
            trail.append((folder.capitalize(), SITE_URL + folder + '/'))
            trail.append((item['name'] if item else title, url))
        else:
            trail.append((title, url))
        blocks.append({'@context': 'https://schema.org', '@type': 'BreadcrumbList',
                       'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(trail)]})
        if folder == 'services' and item:
            blocks.append({'@context': 'https://schema.org', '@type': 'Service', 'name': item['name'], 'serviceType': item['name'],
                           'description': META[rel][1], 'url': url, 'provider': {'@id': SITE_URL + '#business'},
                           'areaServed': area_served()})
    pmx = PRODUCT_PAGES.get(rel)
    if pmx and pmx.get('reviewed'):
        wp = {'@context': 'https://schema.org', '@type': 'WebPage', 'url': url, 'name': META[rel][0], 'dateModified': pmx['reviewed'].strip()}
        if pmx.get('published'):
            wp['datePublished'] = pmx['published'].strip()
        blocks.append(wp)
    return '<!-- @ld -->' + ''.join('<script type="application/ld+json">' + json.dumps(b, ensure_ascii=False).replace('</', '<\/') + '</script>' for b in blocks) + '<!-- /@ld -->'

def finalize(rels):
    import datetime
    today = datetime.date.today().isoformat()
    for rel in rels:
        path = os.path.join(ROOT, rel)
        t = open(path, encoding='utf-8').read()
        t = re.sub(r'\s*<!-- @ld -->.*?<!-- /@ld -->', '', t, flags=re.S)
        if rel not in NOINDEX_PAGES:
            t = t.replace('  <meta name="theme-color"', '  ' + extra_ld(rel) + '\n  <meta name="theme-color"', 1)
        open(path, 'w', encoding='utf-8', newline='\n').write(t)
        h = hashlib.sha1(t.encode('utf-8')).hexdigest()
        if LASTMOD.get(rel, {}).get('hash') != h:
            LASTMOD[rel] = {'hash': h, 'date': today}
    json.dump(LASTMOD, open(LASTMOD_FILE, 'w', encoding='utf-8', newline='\n'), indent=1, sort_keys=True)

# ---------------------------------------------------------------- write everything
def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8', newline='\n').write(content)
    return rel

if __name__ == '__main__':
    for v in D.get('videos', []):
        if not v.get('uploadDate'):
            print(f'  ! video {v["id"]}: no uploadDate in data/site.json (VideoObject is not eligible for Google video results yet)')
    out = [write('services/index.html', services_index()),
           write('industries/index.html', industries_index()),
           write('products/index.html', products_page()),
           write('portfolio/index.html', portfolio_page()),
           write('contact.html', contact_page()),
           write('thanks.html', thanks_page()),
           write('about.html', about_page()),
           write('privacy-policy.html', privacy_page()),
           write('3d-scanning-services-coimbatore.html', coimbatore_page()),
           write('links.html', links_page()),
           write('404.html', notfound_page())]
    out += [write(f'services/{s["slug"]}.html', service_page(s)) for s in D['services']]
    out += [write(f'industries/{s["slug"]}.html', industry_page(s)) for s in D['industries']]
    build_home()
    out += build_product_pages()
    out += build_blog()
    for rel in out + ['index.html']:
        add_image_sizes(rel)
    finalize(out + ['index.html'])
    sitemap_and_robots(out)
    llms_txt()
    print(f'built {len(out)} pages + index.html, sitemap.xml, robots.txt, llms.txt')
