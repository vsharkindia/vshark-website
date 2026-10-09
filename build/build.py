"""
VShark site builder — no dependencies, run:  python build/build.py

Reads data/site.json and
  • writes every inner page (services/, products/, portfolio/, industries/, contact.html, thanks.html)
  • refreshes the marked regions of the hand-built homepage (index.html):
      <!-- @NAME --> … <!-- /@NAME -->   for header, products, services, industries, footer
  • fingerprints css/js links (?v=<hash>) so browsers always pick up changes.
Output is plain static HTML committed to the repo; Netlify needs no build step.
"""
import hashlib, html, json, os, re, sys
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, 'data', 'site.json'), encoding='utf-8'))
E = lambda t: html.escape(str(t), quote=True)
SVC = {s['slug']: s for s in D['services']}
IND = {i['slug']: i for i in D['industries']}
C = D['contact']

def ver(path):
    with open(os.path.join(ROOT, path), 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:8]

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
 'arrow': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
 'down': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
}
A = ICON['arrow']
wa_link = lambda msg='': f'https://wa.me/{C["whatsapp"]}' + (f'?text={quote(msg)}' if msg else '')

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
      {link('blog', '#', 'Blog')}
      {link('contact', f'{P}contact.html', 'Contact')}
    </nav>
    <a href="{P}contact.html" class="btn btn--sm btn--accent header__cta magnetic"><span>Enquire Now</span></a>
    <button class="burger" id="burger" aria-label="Open menu" aria-expanded="false"><span></span><span></span></button>
  </header>

  <!-- MOBILE MENU -->
  <div class="menu" id="menu" aria-hidden="true">
    <nav class="menu__nav">
      {m(1, f'{P}products/index.html', 'Products')}
      {m(2, f'{P}services/index.html', 'Services')}
      {m(3, f'{P}industries/index.html', 'Industries')}
      {m(4, f'{P}portfolio/index.html', 'Portfolio')}
      {m(5, '#', 'Blog')}
      {m(6, f'{P}contact.html', 'Contact')}
    </nav>
    <div class="menu__foot mono">
      <a href="mailto:{C['email']}">{C['email']}</a>
      {phones}
    </div>
  </div>
  <!-- /@header -->'''

def footer(P):
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
        <div class="footer__social">
          <a href="{wa_link()}" target="_blank" rel="noopener" aria-label="WhatsApp">{ICON['wa']}</a>
          <a href="{S['instagram']}" target="_blank" rel="noopener" aria-label="Instagram">{ICON['ig']}</a>
          <a href="{S['facebook']}" target="_blank" rel="noopener" aria-label="Facebook">{ICON['fb']}</a>
          <a href="{S['linkedin']}" target="_blank" rel="noopener" aria-label="LinkedIn">{ICON['in']}</a>
        </div>
      </div>
    </div>
    <div class="footer__big" aria-hidden="true">VSHARK</div>
    <div class="footer__bottom mono">
      <span>© <span id="year">2026</span> VShark Solutions Private Limited</span>
      <span>All rights reserved</span>
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
    <a class="rail__item rail__btn" href="{S['instagram']}" target="_blank" rel="noopener" aria-label="Instagram">{ICON['ig']}<span class="rail__label">Instagram</span></a>
    <a class="rail__item rail__btn" href="{S['facebook']}" target="_blank" rel="noopener" aria-label="Facebook">{ICON['fb']}<span class="rail__label">Facebook</span></a>
    <a class="rail__item rail__btn" href="{S['linkedin']}" target="_blank" rel="noopener" aria-label="LinkedIn">{ICON['in']}<span class="rail__label">LinkedIn</span></a>
  </aside>
  <!-- /@footer -->'''

def page(P, title, desc, active, body, scripts=()):
    js = '\n'.join(f'  <script src="{asset(s, P)}"></script>' for s in ('vendor/gsap.min.js', 'vendor/ScrollTrigger.min.js', 'vendor/lenis.min.js', *scripts, 'js/main.js'))
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{E(title)} — VShark Solutions</title>
  <meta name="description" content="{E(desc)}">
  <meta name="theme-color" content="#f5f6f8">
  <link rel="icon" href="{P}favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="{P}img/favicon-32.png">
  <link rel="apple-touch-icon" href="{P}img/apple-touch-icon.png">
  <link rel="stylesheet" href="{asset('fonts/fonts.css', P)}">
  <link rel="stylesheet" href="{asset('css/style.css', P)}">
  <link rel="stylesheet" href="{asset('css/pages.css', P)}">
</head>
<body class="inner">
  <div class="cursor" aria-hidden="true"><div class="cursor__dot"></div><div class="cursor__ring"><span class="cursor__text"></span></div></div>

  {header(P, active)}

  <main id="top">
{body}
  </main>

  {footer(P)}

{js}
</body>
</html>
'''

# ---------------------------------------------------------------- building blocks
def crumbs(P, items):
    parts = [f'<a href="{P}index.html">Home</a>'] + [f'<a href="{h}">{E(t)}</a>' if h else f'<span>{E(t)}</span>' for t, h in items]
    return '<nav class="crumbs mono" aria-label="Breadcrumb">' + ' <i>/</i> '.join(parts) + '</nav>'

def page_hero(P, crumb_items, tag, title_html, lead, image=None, side=''):
    img = f'<figure class="page-hero__media" data-in><img src="{P}{image}" alt="" loading="eager"><i class="page-hero__slash" aria-hidden="true"></i></figure>' if image else side
    return f'''    <section class="page-hero{' page-hero--media' if (image or side) else ''}">
      <div class="page-hero__text">
        <div data-in>{crumbs(P, crumb_items)}</div>
        <span class="tag mono" data-in>{tag}</span>
        <h1 class="page-hero__title" data-in>{title_html}</h1>
        <p class="page-hero__lead" data-in>{lead}</p>
      </div>
      {img}
    </section>'''

def cta(P, title='Have a part, a building or an idea?', text='Tell us what you need — we usually reply within one working day.', msg='Hi VShark, I would like to discuss a project.'):
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

def proj_card(P, p, show_tags=True):
    svc = ' '.join(p['services']); ind = ' '.join(p['industries'])
    if p['kind'] == 'pair':
        media = (f'<div class="proj__media proj__media--pair" data-cmp><img src="{P}{p["before"]}" alt="" loading="lazy">'
                 f'<img class="proj__cad" src="{P}{p["after"]}" alt="" loading="lazy"><i class="proj__divider"></i>'
                 f'<span class="proj__lab proj__lab--l mono">CAD</span><span class="proj__lab proj__lab--r mono">Scan</span></div>')
        badge = 'Scan → CAD'
        data = f'data-kind="pair" data-before="{P}{p["before"]}" data-after="{P}{p["after"]}"'
    else:
        media = f'<div class="proj__media"><img src="{P}{p["images"][0]}" alt="" loading="lazy"></div>'
        badge = f'{len(p["images"])} images'
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
    cards = '\n'.join(proj_card(P, p, False) for p in projects)
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

def xnav(P, items, current, folder, label):
    '''Row of every service / industry at the bottom of a detail page; the current one is highlighted.'''
    links = '\n'.join(
        f'''        <a class="xnav__item{' is-current' if o is current else ''}" href="{P}{folder}/{o['slug']}.html"{' aria-current="page"' if o is current else ''}>
          <img src="{P}{o['image']}" alt="" loading="lazy"><span><i class="mono">{k+1:02d}</i><b>{E(o['name'])}</b></span>
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
      <div class="lb__cap"><b class="lb__title"></b><span class="lb__sum"></span><span class="lb__count mono"></span></div>
      <button class="lb__nav lb__prev" type="button" aria-label="Previous image">‹</button>
      <button class="lb__nav lb__next" type="button" aria-label="Next image">›</button>
    </div>'''

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
          <span class="stile__media"><img src="{P}{s['image']}" alt="" loading="lazy"></span>
          <span class="stile__body"><i class="mono">{i+1:02d}</i><b>{E(s['name'])}</b><span>{E(s['tagline'])}</span><em>Explore {A}</em></span>
        </a>'''

def ind_tile(P, s, i):
    return f'''        <a class="itile" href="{P}industries/{s['slug']}.html" data-reveal>
          <img src="{P}{s['image']}" alt="" loading="lazy">
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
    cur_attr = ' aria-current="page"'
    others = ''.join(f'<a href="{P}services/{o["slug"]}.html"{cur_attr if o is s else ""}>{E(o["name"])}</a>' for o in D['services'])
    body = f'''{page_hero(P, [("Services", P + "services/index.html"), (s["name"], None)], f"( {i+1:02d} ) — Service", E(s["name"]), E(s["tagline"]), s["image"])}

    <section class="section blk">
      <div class="split">
        <div class="split__main">
          <span class="tag mono">What we do</span>
          <p class="lead-lg" data-reveal>{E(s['intro'])}</p>
          <div class="feat-grid">
{pts}
          </div>
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
{prods}
{xnav(P, D['services'], s, 'services', 'All services')}
{cta(P, msg=f"Hi VShark, I'm interested in {s['name']}.")}
{LIGHTBOX}'''
    return page(P, s['name'], f"{s['name']} — {s['tagline']} VShark Solutions.", 'services', body, ('js/portfolio.js',))

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
    return page(P, 'Services', 'VShark Solutions services: 3D scanning, reverse engineering, Scan to BIM, Class A surfacing, digital metrology, 3D printing and product rendering.', 'services', body)

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
    return page(P, 'Industries', 'Industries served by VShark Solutions: aerospace, automobile, construction, healthcare, education and jewellery.', 'industries', body)

def industry_page(ind):
    P = '../'
    i = D['industries'].index(ind)
    svcs = [s for s in D['services'] if ind['slug'] in s['industries']]
    tiles = '\n'.join(svc_tile(P, s, D['services'].index(s)) for s in svcs)
    projects = [p for p in D['projects'] if ind['slug'] in p['industries']]
    body = f'''{page_hero(P, [("Industries", P + "industries/index.html"), (ind["name"], None)], f"( {i+1:02d} ) — Industry", E(ind["name"]), E(ind["line"]), ind["image"])}
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
{xnav(P, D['industries'], ind, 'industries', 'All industries')}
{cta(P, msg=f"Hi VShark, I work in {ind['name']} and would like to discuss a project.")}
{LIGHTBOX}'''
    return page(P, ind['name'], f"3D scanning and design for {ind['name'].lower()} — {ind['line']}", 'industries', body, ('js/portfolio.js',))

def products_page():
    P = '../'
    rows = []
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
          </div>
        </div>
      </article>''')
    head = ''.join(f'<th scope="col">{E(p["name"])}</th>' for p in D['products'])
    trs = '\n'.join(f'<tr><th scope="row">{E(r[0])}</th>' + ''.join(f'<td>{E(c)}</td>' for c in r[1:]) + '</tr>' for r in D['productSpecs'])
    body = f'''{page_hero(P, [("Products", None)], "( 01 ) — Products", "Professional <em>3D scanners.</em>", "Vertex blue-laser and optical-tracking scanners — sold, set up and supported by VShark's scanning engineers.")}
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
{cta(P, 'Not sure which scanner fits?', 'Send us your parts and use case — we will recommend a model and can arrange a live demo.', 'Hi VShark, please help me choose a 3D scanner.')}'''
    return page(P, 'Products — 3D Scanners', 'Vertex3D, Vertex3D Pro and Vertex Tracker 3D scanners from VShark Solutions — specifications, comparison and quotes.', 'products', body)

def portfolio_page():
    P = '../'
    used_s = [s for s in D['services'] if any(s['slug'] in p['services'] for p in D['projects'])]
    used_i = [s for s in D['industries'] if any(s['slug'] in p['industries'] for p in D['projects'])]
    chips = lambda key, items: f'<button class="chip is-on" type="button" data-f="{key}" data-v="">All</button>' + ''.join(f'<button class="chip" type="button" data-f="{key}" data-v="{x["slug"]}">{E(x["name"])}</button>' for x in items)
    cards = '\n'.join(proj_card(P, p) for p in D['projects'])
    body = f'''{page_hero(P, [("Portfolio", None)], "( 04 ) — Portfolio", "Completed <em>projects.</em>", "A selection of scanning, engineering and visualisation work. Filter by service or industry — drag the slider on Scan → CAD projects to compare.")}
    <section class="section blk pf">
      <div class="pf__filters" data-reveal>
        <div class="pf__row"><span class="mono muted">Service</span><div class="pf__chips">{chips('service', used_s)}</div></div>
        <div class="pf__row"><span class="mono muted">Industry</span><div class="pf__chips">{chips('industry', used_i)}</div></div>
        <span class="pf__count mono" aria-live="polite"></span>
      </div>
      <div class="proj-grid proj-grid--pf" id="pfGrid">
{cards}
      </div>
      <p class="pf__empty muted" hidden>No projects match this combination yet — <a href="{P}contact.html">ask us for examples</a>.</p>
    </section>
{cta(P)}
{LIGHTBOX}'''
    return page(P, 'Portfolio', 'Completed 3D scanning, reverse engineering, rendering and modelling projects by VShark Solutions.', 'portfolio', body, ('js/portfolio.js',))

def contact_page():
    P = ''
    svc_opts = ''.join(f'<option value="{E(s["name"])}">{E(s["name"])}</option>' for s in D['services'])
    prod_opts = ''.join(f'<option value="{E("Product: " + p["name"])}">Buy a scanner — {E(p["name"])}</option>' for p in D['products'])
    phones = ''.join(f'<a class="ccard" href="tel:{p["tel"]}">{ICON["phone"]}<span><small class="mono">{E(p["label"])}</small>{E(p["display"])}</span></a>' for p in C['phones'])
    addr = f'<div class="ccard ccard--static"><span><small class="mono">Office</span>{E(C["address"])}</span></div>' if C['address'] else ''
    body = f'''{page_hero(P, [("Contact", None)], "( 06 ) — Contact", "Let's <em>scan it.</em>", "Tell us about your part, building or idea. We usually reply within one working day.")}
    <section class="section blk">
      <div class="contact">
        <form class="cform" name="enquiry" method="POST" action="thanks.html" data-netlify="true" netlify-honeypot="company_url" enctype="multipart/form-data" data-reveal>
          <input type="hidden" name="form-name" value="enquiry">
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
          <button class="btn btn--accent magnetic" type="submit"><span>Send enquiry</span>{A}</button>
        </form>
        <aside class="contact__side" data-reveal>
          <a class="ccard ccard--wa" href="{wa_link('Hi VShark, I would like to discuss a project.')}" target="_blank" rel="noopener">{ICON['wa']}<span><small class="mono">Fastest</small>Chat on WhatsApp</span></a>
          <a class="ccard" href="mailto:{C['email']}">{ICON['mail']}<span><small class="mono">Email</small>{C['email']}</span></a>
          {phones}
          {addr}
        </aside>
      </div>
    </section>'''
    return page(P, 'Contact', 'Contact VShark Solutions for 3D scanning, reverse engineering, BIM, surfacing, metrology, printing, rendering and 3D scanner sales.', 'contact', body, ('js/contact.js',))

def thanks_page():
    P = ''
    body = f'''{page_hero(P, [("Contact", "contact.html"), ("Thank you", None)], "Enquiry sent", "Thank <em>you.</em>", "We have received your message and will get back to you within one working day.")}
    <section class="section blk"><a class="btn btn--accent magnetic" href="index.html"><span>Back to home</span>{A}</a></section>'''
    return page(P, 'Thank you', 'Enquiry received.', 'contact', body)

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
              <img src="{s['image']}" alt="" loading="lazy">
              <p>{E(s['tagline'])}</p>
              <a href="services/{s['slug']}.html" class="svx__link">Learn more {A}</a>
            </div>
          </li>''' for i, s in enumerate(D['services']))
    imgs = '\n'.join(f'          <img class="svx__img{" is-on" if i == 0 else ""}" src="{s["image"]}" alt="{E(s["name"])}" loading="lazy">' for i, s in enumerate(D['services']))
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
          <img src="{s['image']}" alt="" loading="lazy" draggable="false">
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
               'services': home_services(), 'industries': home_industries()}
    for name, content in regions.items():
        pat = re.compile(r'<!-- @%s -->.*?<!-- /@%s -->' % (name, name), re.S)
        if not pat.search(s):
            sys.exit(f'index.html: missing region @{name}')
        s = pat.sub(lambda m: content, s)
    # fingerprint local css/js
    s = re.sub(r'(href|src)="((?:css|js|fonts)/[\w.-]+\.(?:css|js))(?:\?v=[\w]+)?"', lambda m: f'{m.group(1)}="{asset(m.group(2), "")}"', s)
    open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- write everything
def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(content)
    return rel

if __name__ == '__main__':
    out = [write('services/index.html', services_index()),
           write('industries/index.html', industries_index()),
           write('products/index.html', products_page()),
           write('portfolio/index.html', portfolio_page()),
           write('contact.html', contact_page()),
           write('thanks.html', thanks_page())]
    out += [write(f'services/{s["slug"]}.html', service_page(s)) for s in D['services']]
    out += [write(f'industries/{s["slug"]}.html', industry_page(s)) for s in D['industries']]
    build_home()
    print(f'built {len(out)} pages + index.html')
