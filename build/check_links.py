"""Check that every internal href/src in the built pages resolves to a file (and #anchor).
Run:  python build/check_links.py"""
import glob, os, re, sys
from urllib.parse import urlsplit, unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pages = [p for p in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)
         if not any(x in p for x in ('node_modules', '.git', os.sep + 'build' + os.sep))]
ids = {}
for p in pages:
    ids[os.path.normpath(p)] = set(re.findall(r'\sid="([^"]+)"', open(p, encoding='utf-8').read()))

bad = []
for p in pages:
    s = open(p, encoding='utf-8').read()
    for attr, url in re.findall(r'\s(href|src)="([^"]+)"', s):
        if re.match(r'^(https?:|mailto:|tel:|data:|#$|javascript:)', url):
            continue
        u = urlsplit(url)
        base = ROOT if u.path.startswith('/') else os.path.dirname(p)   # root-relative links (used by 404.html)
        target = os.path.normpath(os.path.join(base, unquote(u.path).lstrip('/'))) if u.path else os.path.normpath(p)
        if u.path and not os.path.isfile(target):
            bad.append((os.path.relpath(p, ROOT), url, 'missing file'))
        elif u.fragment and target.endswith('.html') and u.fragment not in ids.get(target, set()) and u.fragment != 'top':
            bad.append((os.path.relpath(p, ROOT), url, 'missing anchor'))
print(f'{len(pages)} pages checked, {len(bad)} problems')
for b in bad:
    print('  ', *b)
sys.exit(1 if bad else 0)
