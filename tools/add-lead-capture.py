"""Insert AmeriDex lead-capture blocks. Idempotent: skips pages already patched.

- Planning guide download on blog/planning-a-new-deck-checklist.html
- "Send me this estimate" on above-joist-deck-drainage-cost.html
- Sample-request card mid-article and a samples-first final CTA on every blog post
- Role, project and timeline qualification fields on the sample and quote forms
"""
from pathlib import Path
from bs4 import BeautifulSoup
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]

ROLES = ['Homeowner', 'Builder or contractor', 'Architect or designer', 'Dealer or distributor']
TIMES = ['Within 3 months', '3 to 6 months', '6 to 12 months', 'Just researching']
SCOPES = ['New construction', 'Full re-deck', 'Not sure yet']


def options(items, placeholder):
    return f'<option value="">{placeholder}</option>' + ''.join(f'<option>{i}</option>' for i in items)


def common_fields(pid, contact_label):
    return f'''
<div><label for="{pid}-email">Email *</label><input autocomplete="email" id="{pid}-email" name="email" required type="email"/></div>
<div><label for="{pid}-zip">ZIP code *</label><input autocomplete="postal-code" id="{pid}-zip" inputmode="numeric" name="zip" required type="text" maxlength="10"/></div>
<div><label for="{pid}-role">I am a *</label><select id="{pid}-role" name="customer_role" required>{options(ROLES, 'Select one')}</select></div>
<div><label for="{pid}-time">When are you planning to build?</label><select id="{pid}-time" name="timeline">{options(TIMES, 'Select a window')}</select></div>
<div class="lc-full"><label class="lc-check"><input name="contact_ok" type="checkbox" value="Yes"/> <span>{contact_label}</span></label></div>
<div class="lc-hp" aria-hidden="true"><label for="{pid}-gotcha">Leave this field empty</label><input id="{pid}-gotcha" name="_gotcha" tabindex="-1" type="text" autocomplete="off"/></div>'''


def guide_block(prefix):
    return f'''<section class="lc-card" id="guide-download" aria-labelledby="guide-download-title">
<div class="lc-split">
<img class="lc-cover" src="{prefix}assets/img/planning-guide-cover.jpg" alt="Cover of the AmeriDex Project Planning Guide" width="510" height="660" loading="lazy"/>
<div>
<p class="lc-eyebrow">Free printable PDF</p>
<h2 id="guide-download-title">Get the AmeriDex Project Planning Guide</h2>
<p>This checklist plus builder questions and a project worksheet, in a 3-page PDF you can print and bring to your next builder conversation.</p>
<form data-lead-form="guide" data-lead-success="guide-success" novalidate>
<input type="hidden" name="_subject" value="Planning guide download"/>
<input type="hidden" name="lead_source" value="Project Planning Guide"/>
<div class="lc-grid">
<div class="lc-full"><label for="guide-name">First name</label><input autocomplete="given-name" id="guide-name" name="first_name" type="text"/></div>
{common_fields('guide', 'Have an authorized AmeriDex installer or dealer contact me about my project')}
</div>
<div class="lc-actions" style="margin-top:1rem"><button class="lc-btn" type="submit">Get My Free Guide</button></div>
<p class="lc-status" data-lead-status role="alert"></p>
<p class="lc-fine">No spam. We only call if you check the box above.</p>
</form>
<div class="lc-success" id="guide-success" hidden tabindex="-1">
<h3>Your Guide Is Ready</h3>
<p>Download it now, then request free samples so you can see the colors against your house.</p>
<div class="lc-actions"><a class="lc-btn" data-guide-file href="{prefix}pdfs/ameridex-project-planning-guide.pdf" download>Download the PDF</a><a class="lc-btn lc-btn-outline" href="{prefix}samples-request.html">Request Free Samples</a></div>
</div>
</div>
</div>
</section>'''


ESTIMATE = f'''<div class="lc-card" id="estimate-capture" style="margin-bottom:0">
<p class="lc-eyebrow">Save your numbers</p>
<h3>Send Me This Estimate</h3>
<p>We will email your material estimate with a written-quote checklist, usually within 1 to 2 business days.</p>
<form data-lead-form="estimate" data-lead-success="estimate-success" novalidate>
<input type="hidden" name="_subject" value="Calculator estimate request"/>
<input type="hidden" name="lead_source" value="Cost calculator"/>
<div class="lc-grid">
<div><label for="estimate-name">First name</label><input autocomplete="given-name" id="estimate-name" name="first_name" type="text"/></div>
<div><label for="estimate-scope">Project</label><select id="estimate-scope" name="project_scope">{options(SCOPES, 'Select one')}</select></div>
{common_fields('estimate', 'Connect me with an authorized AmeriDex installer or dealer')}
</div>
<div class="lc-actions" style="margin-top:1rem"><button class="lc-btn" type="submit">Email My Estimate</button></div>
<p class="lc-status" data-lead-status role="alert"></p>
</form>
<div class="lc-success" id="estimate-success" hidden tabindex="-1">
<h3>Estimate Received</h3>
<p>Thanks. Your dimensions are on their way to the AmeriDex team. While you wait, see the colors in person.</p>
<div class="lc-actions"><a class="lc-btn" href="samples-request.html">Request Free Samples</a><a class="lc-btn lc-btn-outline" href="get-a-free-quote.html">Get a Written Quote</a></div>
</div>
</div>'''

ESTIMATE_JS = '''<script>
(function () {
  var f = document.querySelector('form[data-lead-form="estimate"]');
  if (!f) return;
  f.leadBeforeSubmit = function () {
    var w = parseFloat(document.getElementById('calc-width').value);
    var l = parseFloat(document.getElementById('calc-length').value);
    if (!(w > 0 && l > 0)) { document.getElementById('calc-width').focus(); return false; }
    var put = function (n, v) {
      var el = f.querySelector('input[name="' + n + '"]');
      if (!el) { el = document.createElement('input'); el.type = 'hidden'; el.name = n; f.appendChild(el); }
      el.value = v;
    };
    put('deck_width_ft', w); put('deck_length_ft', l);
    put('deck_area_sqft', document.getElementById('calc-sqft').textContent);
    put('board_linear_ft', document.getElementById('calc-lf').textContent);
    put('material_estimate', document.getElementById('calc-cost').textContent);
    return true;
  };
})();
</script>'''


def sample_card(prefix, swatch):
    return f'''<aside class="lc-card lc-sample" aria-label="Free AmeriDex samples">
<img src="{prefix}assets/img/swatches-flat/{swatch}.jpg" alt="AmeriDex {swatch.title()} deck board sample" width="1000" height="750" loading="lazy"/>
<div>
<p class="lc-eyebrow">Free samples</p>
<h3>Hold It Before You Build</h3>
<p>Get a real cut of AmeriDex board and Dexerdry seal shipped free. Pour water on it, bend the seal and show it to your builder.</p>
<a class="lc-btn" href="{prefix}samples-request.html">Ship My Free Samples</a>
</div>
</aside>'''


def frag(html):
    return BeautifulSoup(html, 'html.parser')


def ensure_assets(s, prefix, js=True):
    if not s.head.select_one('link[href$="css/lead-capture.css"]'):
        s.head.append(s.new_tag('link', rel='stylesheet', href=prefix + 'css/lead-capture.css'))
    if js and not s.head.select_one('script[src$="js/lead-capture.js"]'):
        s.head.append(s.new_tag('script', src=prefix + 'js/lead-capture.js', defer=True))


def save(p, s):
    p.write_text(str(s))
    print('patched', p.relative_to(root))


# 1. Planning guide on the checklist post
p = root / 'blog/planning-a-new-deck-checklist.html'
s = BeautifulSoup(p.read_text(), 'html.parser')
if not s.select_one('#guide-download'):
    sections = s.find('main').find_all('section', recursive=False) if s.find('main') else []
    final = [x for x in s.select('section.bg-navy') if x.find('h2')][-1]
    final.insert_before(frag(f'<section class="section-pad"><div class="container" style="max-width:880px">{guide_block("../")}</div></section>'))
    hero_p = s.select('section.bg-navy')[0].find_all('p')[-1]
    hero_p.insert_after(frag('<p style="margin-top:1rem"><a href="#guide-download" style="color:#cdb795;font-weight:700">Get the printable PDF version, free &darr;</a></p>'))
    ensure_assets(s, '../')
    save(p, s)

# 2. Homepage guide card points at the download
p = root / 'index.html'
t = p.read_text()
old = '<a class="learning-feature-card learning-feature-guide" href="blog/planning-a-new-deck-checklist.html">'
if old in t:
    t = t.replace(old, '<a class="learning-feature-card learning-feature-guide" href="blog/planning-a-new-deck-checklist.html#guide-download">')
    t = t.replace('Open the planning checklist <span aria-hidden="true">↗</span>', 'Get the free planning guide <span aria-hidden="true">↗</span>')
    p.write_text(t); print('patched index.html')

# 3. Calculator estimate capture
p = root / 'above-joist-deck-drainage-cost.html'
s = BeautifulSoup(p.read_text(), 'html.parser')
if not s.select_one('#estimate-capture'):
    s.select_one('#calc-output').append(frag(ESTIMATE))
    s.body.append(frag(ESTIMATE_JS))
    ensure_assets(s, '')
    save(p, s)

# 4. Blog sample cards and samples-first closing CTA
swatches = ['driftwood', 'khaki', 'slate', 'beachwood', 'chestnut', 'redwood', 'hazelnut']
for i, p in enumerate(sorted((root / 'blog').glob('*.html'))):
    s = BeautifulSoup(p.read_text(), 'html.parser')
    if s.select_one('.lc-sample') or s.select_one('#guide-download'):
        continue
    navy = [x for x in s.select('section.bg-navy') if x.find('h2')]
    if not navy:
        print('skip (no final CTA)', p.name); continue
    final = navy[-1]
    body_h2 = [h for h in s.find('main').find_all('h2') if not h.find_parent('section', class_='bg-navy') and not h.find_parent(class_='lc-card') and not h.find_parent('footer')]
    if len(body_h2) >= 3:
        body_h2[len(body_h2) // 2].insert_before(frag(sample_card('../', swatches[i % 7])))
    else:
        final.insert_before(frag(f'<section class="section-pad"><div class="container" style="max-width:880px">{sample_card("../", swatches[i % 7])}</div></section>'))
    btns = final.find_all('a', class_='btn')
    for a in btns:
        if a.get('href', '').endswith('blog.html'):
            a['href'] = '../samples-request.html'
            a.string = 'Request free samples'
    ensure_assets(s, '../', js=False)
    save(p, s)

# 5. Sample form: role, project, timeline, contact opt-in
p = root / 'samples-request.html'
s = BeautifulSoup(p.read_text(), 'html.parser')
sel = s.select_one('#project_type')
if sel and not s.select_one('#timeline'):
    lab = s.select_one('label[for="project_type"]')
    lab.string = 'I am a *'
    sel['name'] = 'customer_role'; sel['required'] = ''
    sel.clear(); sel.append(frag(options(ROLES, 'Select one')))
    grid = sel.find_parent(class_='form-row')
    grid.insert_after(frag(f'''<div class="form-row form-row-2">
<div><label for="project_scope">Project</label><select id="project_scope" name="project_scope">{options(SCOPES, 'Select one')}</select></div>
<div><label for="timeline">When are you planning to build?</label><select id="timeline" name="timeline">{options(TIMES, 'Select a window')}</select></div>
</div>
<div style="margin-top:.6rem"><label class="agree-line" style="display:flex;gap:.6rem;align-items:flex-start;text-transform:none;letter-spacing:0;font-weight:500"><input name="contact_ok" style="width:18px;height:18px;margin-top:.15rem" type="checkbox" value="Yes"/> <span>Have an authorized AmeriDex installer or dealer contact me about my project (optional)</span></label></div>'''))
    save(p, s)

# 6. Quote form: timeline and role
p = root / 'get-a-free-quote.html'
s = BeautifulSoup(p.read_text(), 'html.parser')
if not s.select_one('#timeline'):
    h = s.select_one('#deck_height').find_parent(class_='form-row')
    h.insert_after(frag(f'<div><label for="timeline">When are you planning to build?</label><select id="timeline" name="timeline">{options(TIMES, "Select a window")}</select></div>'))
    bt = s.select_one('#best_time').parent
    bt.insert_before(frag(f'<div><label for="customer_role">I am a *</label><select id="customer_role" name="customer_role" required>{options(ROLES, "Select one")}</select></div>'))
    save(p, s)
