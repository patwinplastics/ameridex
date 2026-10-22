#!/usr/bin/env python3
"""Render the DexerDry install help page from data/dexerdry-install.json.

Rebuilds two generated parts of dexerdry-install-help.html, so the page works
without JavaScript and search engines see every answer:
  * the FAQPage JSON-LD (<script type="application/ld+json" id="ih-faq-jsonld">)
  * the static answer list between <!-- INSTALL-HELP:START --> and <!-- INSTALL-HELP:END -->
js/install-help.js then fetches the same JSON and adds instant search.
Run after editing the JSON:  python3 tools/build-install-help.py
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'dexerdry-install-help.html'
DATA = ROOT / 'data/dexerdry-install.json'
START, END = '<!-- INSTALL-HELP:START -->', '<!-- INSTALL-HELP:END -->'
LD_RE = re.compile(r'(<script id="ih-faq-jsonld" type="application/ld\+json">).*?(</script>)', re.S)
ALLOWED = re.compile(r'</?(p|strong)>')
VIDEO_PREFIX = re.compile(r'^Video\s*\d+[:.\s-]*')
INTERNAL = ('source_notes', 'conflict_note', 'needs_review', 'mentions_screw_brand', 'also_source')

data = json.loads(DATA.read_text())
items = list(data['qa'])
for q in items:
    for k in INTERNAL:
        if k in q:
            sys.exit(f'internal-only field {k} found in {q["id"]}; strip it from the public JSON')
    q['video_title'] = VIDEO_PREFIX.sub('', q['video_title'])
    for k in ('question', 'short_answer', 'answer', 'answer_html'):
        if '\u2014' in q[k] or '\u2013' in q[k]:
            sys.exit(f'em or en dash found in {q["id"]}.{k}; replace it before building')
    leftover = ALLOWED.sub('', q['answer_html'])
    if '<' in leftover:
        sys.exit(f'unexpected HTML in {q["id"]}.answer_html; only p and strong are allowed')

def item_html(q):
    e = html.escape
    return (
        f'<details class="ih-item" id="{e(q["id"])}" data-cat="{e(q["category"])}">'
        f'<summary><span class="ih-q">{e(q["question"])}</span>'
        f'<span class="ih-short">{e(q["short_answer"])}</span>'
        f'<span class="ih-cat">{e(q["category"])}</span></summary>'
        f'<div class="ih-body">{q["answer_html"]}'
        f'<p><a class="ih-watch" href="{e(q["video_url"])}" rel="noopener" target="_blank">'
        f'&#9654; Watch this step <small>{e(q["video_title"])} at {e(q["timestamp_label"])} (opens in a new tab)</small></a></p>'
        f'</div></details>'
    )

listing = '\n'.join(item_html(q) for q in items)
ld = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    'mainEntity': [
        {'@type': 'Question', 'name': q['question'],
         'acceptedAnswer': {'@type': 'Answer', 'text': q['answer']}}
        for q in items
    ],
}
ld_text = json.dumps(ld, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

src = PAGE.read_text()
if START not in src or END not in src or not LD_RE.search(src):
    sys.exit('markers missing from dexerdry-install-help.html')
src = re.sub(re.escape(START) + '.*?' + re.escape(END), lambda m: f'{START}\n{listing}\n{END}', src, flags=re.S)
src = LD_RE.sub(lambda m: m.group(1) + ld_text + m.group(2), src)
PAGE.write_text(src)
print(f'Rendered {len(items)} install answers into {PAGE.name}.')
