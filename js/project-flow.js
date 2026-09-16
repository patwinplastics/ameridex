/* Explicit, allowlisted URL handoffs. No account, storage, PII or network calls. */
(() => {
  'use strict';
  const colors = ['Driftwood','Khaki','Slate','Beachwood','Chestnut','Redwood','Hazelnut'];
  const types = {new:'New construction',redeck:'Full re-deck',other:'Other / need guidance'};
  const uses = {kitchen:'Outdoor kitchen & dining',lounge:'Lounge & gathering area',storage:'Storage & gear',other:'Another use'};
  const inspirations = {kitchen:'Outdoor kitchen inspiration',lounge:'Under-deck lounge inspiration',twolevel:'Two-level living inspiration'};
  const qs = new URLSearchParams(location.search);
  const number = value => Number.isFinite(Number(value)) && Number(value)>=1 && Number(value)<=1000 ? String(Number(value)) : '';
  const state = {
    color: (qs.get('color') || '').split(',').map(c=>colors.find(x=>x.toLowerCase()===c.trim().toLowerCase())).filter(Boolean).filter((c,i,a)=>a.indexOf(c)===i).join(','),
    width:number(qs.get('width')),depth:number(qs.get('depth')),
    project: Object.hasOwn(types,qs.get('project')) ? qs.get('project') : '',
    use: Object.hasOwn(uses,qs.get('use')) ? qs.get('use') : '',
    inspiration: Object.hasOwn(inspirations,qs.get('inspiration')) ? qs.get('inspiration') : ''
  };
  function url(page) {
    const params = new URLSearchParams();
    Object.entries(state).forEach(([k,v])=>{if(v)params.set(k,v)});
    return page + (params.size ? '?' + params.toString() : '');
  }
  function lines() {
    return [
      ['Project',types[state.project] || 'To be confirmed'],
      ['Dimensions',state.width && state.depth ? `${state.width} × ${state.depth} ft · ${Number((state.width*state.depth).toFixed(2)).toLocaleString()} sq ft` : state.width ? `${state.width} ft width · depth to be confirmed` : state.depth ? `${state.depth} ft depth · width to be confirmed` : 'To be confirmed'],
      ['Color',state.color.replaceAll(',',', ') || 'Still exploring'],
      ['Space below',uses[state.use] || 'Still deciding'],
      ...(state.inspiration ? [['Direction',inspirations[state.inspiration]]] : [])
    ];
  }
  const el = (tag,text) => { const n=document.createElement(tag); if(text)n.textContent=text;return n; };
  function renderSummary(target) {
    target.replaceChildren();
    const dl=el('dl'); lines().forEach(([k,v])=>{dl.append(el('dt',k),el('dd',v));}); target.append(dl);
  }
  const planner=document.getElementById('project-planner');
  if(planner) {
    const fields={project:'plan-type',width:'plan-width',depth:'plan-depth',color:'plan-color',use:'plan-use'};
    // Planner chooses one direction; the sample form supports multiple colors.
    state.color=state.color.split(',')[0];
    Object.entries(fields).forEach(([k,id])=>{
      const f=document.getElementById(id);
      if(!f.value && state[k])f.value=state[k];
    });
    function update(){
      let invalid=false;
      Object.entries(fields).forEach(([k,id])=>{
        const f=document.getElementById(id);
        if(k==='width'||k==='depth'){
          const bad=Boolean(f.value && !number(f.value)) || f.validity.badInput;
          f.setAttribute('aria-invalid',String(bad)); invalid=invalid||bad;
          state[k]=number(f.value);
        } else state[k]=f.value;
      });
      document.getElementById('planner-error').textContent=invalid ? 'Enter dimensions from 1 to 1,000 feet, or leave them blank.' : '';
      renderSummary(document.getElementById('plan-summary'));
      const preview=document.getElementById('plan-color-preview');
      preview.hidden=!state.color;
      if(state.color){
        document.getElementById('plan-color-image').src='assets/img/swatches/'+state.color.toLowerCase()+'.png';
        document.getElementById('plan-color-image').alt=state.color+' deck board';
        document.getElementById('plan-color-label').textContent=state.color;
      }
      [['plan-quote','get-a-free-quote.html'],['plan-samples','samples-request.html']].forEach(([id,path])=>{
        const a=document.getElementById(id);a.href=url(path);a.setAttribute('aria-disabled',String(invalid));
      });
    }
    planner.addEventListener('input',update);planner.addEventListener('change',update);
    planner.addEventListener('click',e=>{
      if(e.target.closest('a[aria-disabled=true]')){e.preventDefault();document.querySelector('[aria-invalid=true]').focus()}
    });
    update();
  }
  const sample=document.querySelector('input[name=selected_colors]');
  const quote=document.getElementById('deck_width');
  const dealerMode=qs.get('type')==='dealer';
  if((sample || quote) && !dealerMode) {
    const form=(sample||quote).closest('form');
    const banner=el('aside');banner.className='project-handoff';banner.setAttribute('aria-label','Connected project details');
    banner.append(el('h2','Your project, carried forward'));
    const summary=el('p');banner.append(summary);
    const links=el('div');links.className='handoff-links';
    const edit=el('a','Edit project plan');const other=el('a',sample?'Continue to a quote ↗':'Explore samples ↗');
    links.append(edit,other);banner.append(links);form.before(banner);
    function refresh(){
      summary.textContent=lines().filter(([k,v])=>!['To be confirmed','Still exploring','Still deciding'].includes(v)).map(([k,v])=>`${k}: ${v}`).join(' · ') || 'Choose a color or start a project plan to connect your next steps.';
      edit.href=url('plan-your-project.html');other.href=url(sample?'get-a-free-quote.html':'samples-request.html');
      if(sample){
        ['width','depth','project','use','inspiration'].forEach(k=>{
          let input=form.querySelector(`[name="planning_${k}"]`);
          if(!input){input=el('input');input.type='hidden';input.name='planning_'+k;form.append(input)}
          input.value=state[k];
        });
      }
    }
    if(sample){
      const chosen=state.color.split(',');
      document.querySelectorAll('.color-pick').forEach(button=>{
        if(chosen.includes(button.dataset.color) && !button.classList.contains('selected'))button.click();
      });
      const sync=()=>{state.color=[...document.querySelectorAll('.color-pick.selected')].map(b=>b.dataset.color).filter(c=>colors.includes(c)).join(',');refresh()};
      form.addEventListener('click',()=>queueMicrotask(sync));
      sync();
    } else {
      if(state.width)quote.value=state.width;
      if(state.depth)document.getElementById('deck_depth').value=state.depth;
      const status=document.getElementById('deck_status');
      const typeValues={new:'New construction',redeck:'Replacing an existing deck',other:'Other'};
      if(state.project)status.value=typeValues[state.project];
      const useValues={kitchen:'Outdoor Kitchen',lounge:'Lounge Area',storage:'Storage / Gear',other:'Other'};
      form.querySelectorAll('[name=use_below]').forEach(i=>{if(i.value===useValues[state.use])i.checked=true});
      const color=document.getElementById('quote-color');
      if(color){
        if(state.color.includes(',')){
          const selection=el('option',state.color.replaceAll(',',', '));
          selection.value=state.color;color.append(selection);
        }
        color.value=state.color||'';
      }
      const design=document.getElementById('project_inspiration');
      if(design)design.value=inspirations[state.inspiration]||'';
      const sync=()=>{
        state.width=number(quote.value);state.depth=number(document.getElementById('deck_depth').value);
        state.project=Object.keys(typeValues).find(k=>typeValues[k]===status.value)||'';
        if(color)state.color=color.value;
        state.use=Object.keys(useValues).find(k=>form.querySelector(`[name=use_below][value="${useValues[k]}"]`)?.checked)||'';
        refresh();
      };
      form.addEventListener('input',sync);form.addEventListener('change',sync);refresh();
    }
  }
  const calculator=document.getElementById('deck-calc');
  const handoff=document.getElementById('calc-to-quote');
  if(calculator&&handoff){
    const update=()=>{
      const w=number(document.getElementById('calc-width').value),d=number(document.getElementById('calc-length').value);
      handoff.hidden=!(w&&d);
      state.width=w;state.depth=d;handoff.href=url('get-a-free-quote.html');
    };
    calculator.addEventListener('submit',update);calculator.addEventListener('input',update);update();
  }
})();
