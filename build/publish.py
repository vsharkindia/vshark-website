"""
Copy only the public website into dist/ (what Netlify publishes).

  python build/publish.py

Everything internal stays out: source data, build scripts, notes (*.md), server-only PHP and
config, editor/tooling files. The rules mirror the exclude list in .github/workflows/deploy.yml
and the deny rules in .htaccess, so the site looks the same on Netlify and on Apache/LiteSpeed.

Search engines: dist/_headers marks every page "noindex" unless the environment variable
ALLOW_INDEXING=1 is set (set it only on the Netlify site that serves www.vsharksolutions.com).
"""
import fnmatch, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist')

SKIP_DIRS = {'.git', '.github', '.claude', '.netlify', 'build', 'data', 'collateral', 'dist', 'netlify', 'node_modules', 'marketing'}
SKIP_FILES = ['*.md', '*.py', '*.toml', '*.yml', '*.yaml', '*.csv', '*.code-workspace', '*.zip', '*.php',
              '.gitignore', '.htaccess', '.user.ini', 'Changes.txt', 'README.txt', 'package.json', 'package-lock.json',
              'Thumbs.db', '.DS_Store']

def skipped(name):
    return any(fnmatch.fnmatch(name, pat) for pat in SKIP_FILES)

def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    n = size = 0
    for d, dirs, files in os.walk(ROOT):
        rel = os.path.relpath(d, ROOT)
        dirs[:] = [x for x in dirs if not (rel == '.' and x in SKIP_DIRS) and not x.startswith('.')]
        for f in files:
            if skipped(f):
                continue
            src = os.path.join(d, f)
            dst = os.path.join(DIST, rel, f)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            n += 1
            size += os.path.getsize(src)
    if os.environ.get('ALLOW_INDEXING') != '1':
        with open(os.path.join(DIST, '_headers'), 'w', encoding='utf-8') as fh:
            fh.write('/*\n  X-Robots-Tag: noindex, nofollow\n')
    print(f'published {n} files ({size / 1e6:.1f} MB) to dist/'
          + ('' if os.environ.get('ALLOW_INDEXING') == '1' else ' — noindex (staging/preview)'))
    leaked = [p for p in ('DEPLOY.md', 'build', 'data', 'netlify.toml', 'send-enquiry.php') if os.path.exists(os.path.join(DIST, p))]
    if leaked:
        sys.exit(f'internal files leaked into dist/: {leaked}')

if __name__ == '__main__':
    main()
