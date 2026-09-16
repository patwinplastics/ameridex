"""Apply the approved shared header to every root, blog and dealer page.

Run after any static page build. Optional directory argument targets a preview.
"""
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
import sys
source = Path(__file__).resolve().parents[1]
root = Path(sys.argv[1]) if len(sys.argv)>1 else source
template = (source/'components/site-header.html').read_text()
count=0
for p in root.rglob('*.html'):
    if any(x in p.relative_to(root).parts for x in ('components','tools','.git')): continue
    s=BeautifulSoup(p.read_text(),'html.parser')
    if not s.body or not s.head: continue
    prefix='../'*(len(p.relative_to(root).parts)-1)
    for old in list(s.select('header.site-header, header.home-header, .trust-topbar, .mobile-menu')):
        old.decompose()
    header=BeautifulSoup(template,'html.parser').header
    for el in header.select('[href],[src]'):
        attr='href' if el.has_attr('href') else 'src'
        value=el[attr]; u=urlsplit(value)
        if not u.scheme and not u.netloc:
            el[attr]=prefix+value
            if attr=='href' and u.path==p.relative_to(root).as_posix() and not u.fragment and 'brand' not in el.get('class',[]):
                el['aria-current']='page'
    skip=s.select_one('a.skip-link')
    if skip: skip.insert_after(header)
    else: s.body.insert(0,header)
    for el in list(s.select('link[href$="css/header.css"],script[src$="js/header.js"]')): el.decompose()
    s.head.append(s.new_tag('link',rel='stylesheet',href=prefix+'css/header.css'))
    s.head.append(s.new_tag('script',src=prefix+'js/header.js',defer=True))
    p.write_text(str(s))
    count+=1
print(f'Synchronized shared navigation across {count} pages.')
