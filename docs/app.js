const $=id=>document.getElementById(id);
const trait=new URLSearchParams(location.search).get('trait')==='scoli'?'scoli':'crimson';
const labels={crimson:'Crimson dorsal patches',scoli:'Orange-pink tubercles'};
const states={'0':'Absent','1':'Present','A':'Ambiguous'};
const key='euclea-larvae-reviewed-20261122-v1';let edits={};try{edits=JSON.parse(localStorage.getItem(key)||'{}')}catch{}
const initialEdits=JSON.parse(JSON.stringify(edits));
let data=[],selected=null,visibleRows=[];
const visibleCards=new Map();
const initialScore=(r,t)=>initialEdits[r.image_id]?.[t]??r[t];
const score=(r,t)=>edits[r.image_id]?.[t]??r[t];
const broodOrder=['E. incisa','F1 (line unresolved)','F2-1','F2-2','F2-3','F2-4','F2-5','BC-1','BC-2','BC-3'];
$(trait+'Tab').classList.add('active');$('traitTitle').textContent=labels[trait];
$('definition').textContent=trait==='crimson'?'Localized paired crimson patches at the repeated dorsal positions. Score faint patches as present, including those within orange-pink bands.':'Orange-pink pigmentation of the projecting tubercles (scoli), scored separately from crimson patches on the body.';
function el(tag,cls,text){const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n}
function render(){const q=$('search').value.toLowerCase();const shown=data.filter(r=>(!$('brood').value||r.brood===$('brood').value)&&(!$('state').value||initialScore(r,trait)===$('state').value)&&(!q||(r.filename+' '+r.image_id).toLowerCase().includes(q)));
 visibleRows=shown;updateCounts();visibleCards.clear();
 $('gallery').replaceChildren();
 for(const brood of broodOrder){const members=shown.filter(r=>r.brood===brood);if(!members.length)continue;const section=el('section','group');section.append(el('h2','',brood));
 for(const state of ['0','1','A']){const group=members.filter(r=>initialScore(r,trait)===state).sort((a,b)=>a.filename.localeCompare(b.filename));if(!group.length)continue;
 section.append(el('h3','stateheading',`${state} · ${states[state]} — ${group.length} image views`));const grid=el('div','grid');
 for(const r of group){const card=el('article','card'),b=el('button','photo');b.setAttribute('aria-label','Review '+r.filename);const im=el('img');im.src=`assets/${r.image_id}.jpg`;im.alt=r.filename;im.loading='lazy';b.append(im);b.onclick=()=>open(r);card.append(b);const meta=el('div','meta',r.filename);const badges=el('div','badges');const stateBadge=el('span','badge'),editedBadge=el('span','badge editedbadge','Edited');badges.append(stateBadge,editedBadge);meta.append(badges);if(r.reference_note)meta.append(el('div','refmark','User reference'));const buttons=el('div','statebuttons');buttons.setAttribute('role','group');buttons.setAttribute('aria-label',labels[trait]+' for '+r.filename);
 for(const value of ['0','1','A']){const button=el('button','statebutton',value==='A'?'Ambiguous':value);button.type='button';button.setAttribute('aria-label',`${states[value]}: ${r.filename}`);button.dataset.state=value;button.setAttribute('aria-pressed',String(score(r,trait)===value));button.title=states[value];button.onclick=()=>{edits[r.image_id]={...(edits[r.image_id]||{}),[trait]:value};const ok=persist();updateCard(r);updateCounts();$('autosave').textContent=ok?`${r.filename}: ${states[value]} — saved in this browser.`:'Browser storage unavailable. Export the CSV now to retain your edits.';};buttons.append(button)}meta.append(buttons);card.append(meta);grid.append(card);visibleCards.set(r.image_id,{stateBadge,editedBadge,buttons});updateCard(r)}section.append(grid)}$('gallery').append(section)}
}
function updateCounts(){const counts=Object.fromEntries(['0','1','A'].map(s=>[s,visibleRows.filter(r=>score(r,trait)===s).length]));$('stats').textContent=`${visibleRows.length} image views · ${counts['0']} absent · ${counts['1']} present · ${counts.A} ambiguous`}
function updateCard(r){const c=visibleCards.get(r.image_id);if(!c)return;const state=score(r,trait);c.stateBadge.className='badge s'+state;c.stateBadge.textContent=`${state} · ${states[state]}`;c.editedBadge.style.visibility=edits[r.image_id]?.[trait]!==undefined?'visible':'hidden';for(const b of c.buttons.children)b.setAttribute('aria-pressed',String(b.dataset.state===state))}
function open(r){selected=r;$('large').src=`assets/${r.image_id}.jpg`;$('viewName').textContent=r.filename;$('viewBrood').textContent=r.brood;$('ref').textContent=r.reference_note;$('editCrimson').value=score(r,'crimson');$('editScoli').value=score(r,'scoli');$('displayImage').href=$('large').getAttribute('src');$('saved').textContent='';$('viewer').showModal()}
$('close').onclick=()=>$('viewer').close();
function persist(){try{localStorage.setItem(key,JSON.stringify(edits));return true}catch{$('saved').textContent='Browser storage unavailable. Export the CSV now to retain these edits.';$('autosave').textContent=$('saved').textContent;return false}}
$('save').onclick=()=>{edits[selected.image_id]={crimson:$('editCrimson').value,scoli:$('editScoli').value};if(persist())$('saved').textContent='Saved in this browser. Export CSV to share.';updateCard(selected);updateCounts()};
$('restore').onclick=()=>{delete edits[selected.image_id];persist();$('editCrimson').value=selected.crimson;$('editScoli').value=selected.scoli;$('saved').textContent='Original draft scores restored.';updateCard(selected);updateCounts()};
for(const id of ['brood','state','search'])$(id).addEventListener('input',render);
$('export').onclick=()=>{const rows=data.map(r=>{const x={...r};for(const t of ['crimson','scoli']){x[t]=score(r,t);x[t+'_state']=x[t]==='A'?'':x[t];if(edits[r.image_id]?.[t]!==undefined)x[t+'_status']=x[t]==='A'?'ambiguous':'user_reviewed'}return x});const keys=Object.keys(rows[0]);const esc=v=>'"'+String(v??'').replaceAll('"','""')+'"';const csv=[keys.map(esc).join(','),...rows.map(r=>keys.map(k=>esc(r[k])).join(','))].join('\r\n');const u=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=el('a');a.href=u;a.download='larval_color_scores_reviewed.csv';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};
fetch('data.json').then(r=>{if(!r.ok)throw Error('Data could not be loaded');return r.json()}).then(rows=>{data=rows;for(const b of broodOrder){if(data.some(r=>r.brood===b)){const o=el('option','',b);o.value=b;$('brood').append(o)}}render()}).catch(e=>{$('stats').textContent=e.message});
