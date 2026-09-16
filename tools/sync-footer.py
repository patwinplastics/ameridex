"""Apply the approved footer to source or an isolated preview. Idempotent."""
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
import sys
source = Path(__file__).resolve().parents[1]
root = Path(sys.argv[1]) if len(sys.argv)>1 else source
template = (source/'components/site-footer.html').read_text()
count = 0
for p in root.rglob('*.html'):
    if any(x in p.relative_to(root).parts for x in ('components','tools','.git')): continue
    s = BeautifulSoup(p.read_text(), 'html.parser')
    if not s.body or not s.head: continue
    prefix = '../' * (len(p.relative_to(root).parts)-1)
    for old in list(s.select('footer.site-footer, footer.home-footer, .dealer-pill')):
        old.decompose()
    footer = BeautifulSoup(template,'html.parser').footer
    for el in footer.select('[href],[src]'):
        attr = 'href' if el.has_attr('href') else 'src'
        u = urlsplit(el[attr])
        if not u.scheme and not u.netloc: el[attr] = prefix+el[attr]
    main = s.find('main')
    if main: main.insert_after(footer)
    else: s.body.append(footer)
    for el in list(s.select('link[href$="css/footer.css"]')): el.decompose()
    s.head.append(s.new_tag('link',rel='stylesheet',href=prefix+'css/footer.css'))
    p.write_text(str(s))
    count += 1
print(f'Synchronized shared footer across {count} pages.')
