#!/usr/bin/env python3
"""Render a visible breadcrumb trail on every page from its BreadcrumbList JSON-LD.

The trail sits right after the opening <main> tag between
<!-- BREADCRUMB:START --> and <!-- BREADCRUMB:END --> markers and is rebuilt
from the page's own JSON-LD each run, so a page copied as a template picks up
the right trail automatically. Runs in the Pages deploy workflow and can be run
locally:  python3 tools/sync-breadcrumbs.py
Pages without BreadcrumbList JSON-LD (home, thanks pages, 404) are skipped.
"""
import glob, html, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SITE = 'https://www.ameridex.com/'
DISPLAY = {'Blog': 'Learning Center'}
START, END = '<!-- BREADCRUMB:START -->', '<!-- BREADCRUMB:END -->'
BLOCK_RE = re.compile(r'\n?' + re.escape(START) + r'.*?' + re.escape(END), re.S)
LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
MAIN_RE = re.compile(r'<main\b[^>]*>')


def crumbs_for(src):
    for raw in LD_RE.findall(src):
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        nodes = data.get('@graph', [data]) if isinstance(data, dict) else data
        for n in nodes if isinstance(nodes, list) else [nodes]:
            if isinstance(n, dict) and n.get('@type') == 'BreadcrumbList':
                items = sorted(n.get('itemListElement', []), key=lambda x: x.get('position', 0))
                out = []
                for it in items:
                    url = it.get('item')
                    if isinstance(url, dict):
                        url = url.get('@id')
                    out.append((it.get('name', ''), url or ''))
                return out
    return None


def rel_href(url, depth):
    path = url[len(SITE):] if url.startswith(SITE) else url
    path = path or 'index.html'
    return '../' * depth + path


def render(crumbs, depth):
    parts = []
    for i, (name, url) in enumerate(crumbs):
        label = html.escape(DISPLAY.get(name, name), quote=False)
        if i == len(crumbs) - 1:
            parts.append('<li><span aria-current="page">%s</span></li>' % label)
        else:
            parts.append('<li><a href="%s">%s</a></li>' % (rel_href(url, depth), label))
    return '%s<nav aria-label="Breadcrumb" class="crumbs"><ol>%s</ol></nav>%s' % (START, ''.join(parts), END)


def main():
    changed = 0
    files = sorted(glob.glob(os.path.join(ROOT, '*.html')) + glob.glob(os.path.join(ROOT, 'blog', '*.html')))
    for path in files:
        rel = os.path.relpath(path, ROOT)
        src = open(path, encoding='utf-8').read()
        crumbs = crumbs_for(src)
        new = BLOCK_RE.sub('', src)
        if crumbs and len(crumbs) >= 2:
            m = MAIN_RE.search(new)
            if m:
                block = render(crumbs, rel.count('/'))
                new = new[:m.end()] + '\n' + block + new[m.end():]
        if new != src:
            open(path, 'w', encoding='utf-8').write(new)
            changed += 1
    print('breadcrumbs updated on %d page(s)' % changed)


if __name__ == '__main__':
    sys.exit(main())
