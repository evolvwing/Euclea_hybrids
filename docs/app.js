const $=id=>document.getElementById(id);
const requestedTrait=new URLSearchParams(location.search).get('trait');
const trait=['dorsal','scoli'].includes(requestedTrait)?'dorsal':'crimson';
const dorsalLines=trait==='dorsal';
const labels={crimson:'Larval dorsal crimson patches',dorsal:'Larval dorsal orange lines'};
const states={'0':'Absent','1':'Present','A':'Ambiguous'};
const key='euclea-larvae-reviewed-20261122-v1';let edits={};try{edits=JSON.parse(localStorage.getItem(key)||'{}')}catch{}
const initialEdits=JSON.parse(JSON.stringify(edits));
const dorsalReviewKey='euclea-dorsal-review-v1';
const crimsonReviewKey='euclea-crimson-exclusions-v1';
function readReviewDraft(storageKey){
 const draft=new Map();
 try{
  for(const [id,excluded] of Object.entries(JSON.parse(localStorage.getItem(storageKey)||'{}'))){
   if(/^euclea-\d{3}$/.test(id)&&typeof excluded==='boolean')draft.set(id,excluded);
  }
 }catch{}
 return draft;
}
const reviewDraft=readReviewDraft(dorsalReviewKey);
const crimsonReviewDraft=readReviewDraft(crimsonReviewKey);
let crimsonExclusionsOnLoad=new Set();
let data=[],selected=null,visibleRows=[];
const visibleCards=new Map();
const initialScore=r=>initialEdits[r.image_id]?.crimson??r.crimson;
const score=r=>edits[r.image_id]?.crimson??r.crimson;
const broodOrder=['E. incisa','F1 (line unresolved)','F2-1','F2-2','F2-3','F2-4','F2-5','BC-1','BC-2','BC-3'];
$(trait+'Tab').classList.add('active');$('traitTitle').textContent=labels[trait];
$('definition').textContent=trait==='crimson'?'Localized paired crimson patches at the repeated dorsal positions. Score faint patches as present, including those within orange-pink bands.':'Photos are ranked by orange-pink coverage within each brood. Open a ranked photo to see the scored pixels.';
for(const id of ['crimsonInfo','crimsonFilter','crimsonExcludedFilter','crimsonEditor','crimsonViewerNote','autosave']) $(id).hidden=dorsalLines;
document.querySelector('.saveNote').hidden=dorsalLines;
for(const id of ['dorsalSort','dorsalDetails','dorsalReviewNotice']) $(id).hidden=!dorsalLines;
function el(tag,cls,text){const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n}
function render(){const q=$('search').value.toLowerCase();const matching=data.filter(r=>(!$('brood').value||r.brood===$('brood').value)&&(dorsalLines||!$('state').value||initialScore(r)===$('state').value)&&(!q||(r.filename+' '+r.image_id).toLowerCase().includes(q)));
 const shown=dorsalLines||$('showCrimsonExcluded').checked
  ? matching : matching.filter(row=>!crimsonExclusionsOnLoad.has(row.image_id));
 visibleRows=shown;updateCounts();visibleCards.clear();
 $('gallery').replaceChildren();
 if(dorsalLines){renderDorsalLines(shown);return;}
 for(const brood of broodOrder){const members=shown.filter(r=>r.brood===brood);if(!members.length)continue;const section=el('section','group');section.append(el('h2','',brood));
 for(const state of ['0','1','A']){const group=members.filter(r=>initialScore(r)===state).sort((a,b)=>a.filename.localeCompare(b.filename));if(!group.length)continue;
 section.append(el('h3','stateheading',`${state} · ${states[state]} — ${group.length} image views`));const grid=el('div','grid');
 for(const r of group){const card=el('article','card'),b=el('button','photo');b.setAttribute('aria-label','Review '+r.filename);const im=el('img');im.src=`assets/${r.image_id}.jpg`;im.alt=r.filename;im.loading='lazy';b.append(im);b.onclick=()=>open(r);card.append(b);const meta=el('div','meta',r.filename);const badges=el('div','badges');const stateBadge=el('span','badge'),editedBadge=el('span','badge editedbadge','Edited');badges.append(stateBadge,editedBadge);meta.append(badges);if(r.reference_note)meta.append(el('div','refmark','User reference'));const buttons=el('div','statebuttons');buttons.setAttribute('role','group');buttons.setAttribute('aria-label',labels[trait]+' for '+r.filename);
 for(const value of ['0','1','A']){const button=el('button','statebutton',value==='A'?'Ambiguous':value);button.type='button';button.setAttribute('aria-label',`${states[value]}: ${r.filename}`);button.dataset.state=value;button.setAttribute('aria-pressed',String(score(r)===value));button.title=states[value];button.onclick=()=>{edits[r.image_id]={crimson:value};const ok=persist();updateCard(r);updateCounts();$('autosave').textContent=ok?`${r.filename}: ${states[value]} — saved in this browser.`:'Browser storage unavailable. Export the CSV now to retain your edits.';};buttons.append(button)}meta.append(buttons,reviewButton(r));card.append(meta);grid.append(card);visibleCards.set(r.image_id,{stateBadge,editedBadge,buttons});updateCard(r)}section.append(grid)}$('gallery').append(section)}
}
function updateCounts(){
 if(dorsalLines){
  const excluded=visibleRows.filter(r=>r.dorsal_exclusion_reason||reviewExcluded(r)).length;
  $('stats').textContent=`${visibleRows.length-excluded} ranked · ${excluded} excluded`;
  return;
 }
 const included=visibleRows.filter(row=>!crimsonExcluded(row));
 const counts=Object.fromEntries(['0','1','A'].map(s=>[s,included.filter(r=>score(r)===s).length]));
 const excluded=data.filter(crimsonExcluded).length;
 $('stats').textContent=`${included.length} image views · ${counts['0']} absent · ${counts['1']} present · ${counts.A} ambiguous · ${excluded} excluded overall`;
}
function updateCard(r){const c=visibleCards.get(r.image_id);if(!c)return;const state=score(r);c.stateBadge.className='badge s'+state;c.stateBadge.textContent=`${state} · ${states[state]}`;c.editedBadge.style.visibility=edits[r.image_id]?.crimson!==undefined?'visible':'hidden';for(const b of c.buttons.children)b.setAttribute('aria-pressed',String(b.dataset.state===state))}
const publishedExclusion=row=>row.dorsal_review_excluded==='yes';
const reviewExcluded=row=>reviewDraft.get(row.image_id)??publishedExclusion(row);
const excludedOnLoad=row=>Boolean(row.dorsal_exclusion_reason)||publishedExclusion(row);
const publishedCrimsonExclusion=row=>row.crimson_review_excluded==='yes';
const crimsonExcluded=row=>crimsonReviewDraft.get(row.image_id)??publishedCrimsonExclusion(row);

function storeReviewDraft(storageKey=dorsalReviewKey,draft=reviewDraft){
 try{
  localStorage.setItem(storageKey,JSON.stringify(Object.fromEntries(draft)));
  return true;
 }catch{return false;}
}

function updateReviewStatus(message=''){
 const count=reviewDraft.size;
 $('dorsalReviewNotice').textContent=message||(count
  ? `${count} local ${count===1?'change':'changes'}. Export the CSV to share your edits.`
  : 'Photos stay in place while you review. Export the CSV to share your edits.');
}

function reviewButton(row){
 const draft=dorsalLines?reviewDraft:crimsonReviewDraft;
 const storageKey=dorsalLines?dorsalReviewKey:crimsonReviewKey;
 const savedExclusion=dorsalLines?publishedExclusion:publishedCrimsonExclusion;
 const currentExclusion=dorsalLines?reviewExcluded:crimsonExcluded;
 const control=el('button','dorsal-review-button');
 control.type='button';
 control.disabled=dorsalLines&&Boolean(row.dorsal_exclusion_reason);
 function refresh(){
  const excluded=control.disabled||currentExclusion(row);
  control.textContent=control.disabled?'Excluded':excluded?'Restore':'Exclude';
  control.setAttribute('aria-label',`${control.textContent} ${row.filename}`);
  control.dataset.excluded=String(excluded);
 }
 refresh();
 control.onclick=()=>{
  const next=!currentExclusion(row);
  if(next===savedExclusion(row))draft.delete(row.image_id);
  else draft.set(row.image_id,next);
  const saved=storeReviewDraft(storageKey,draft);
  refresh();
  updateCounts();
  const storageError='Browser storage is unavailable. Export the CSV before leaving this page.';
  if(dorsalLines)updateReviewStatus(saved?'':storageError);
  else $('autosave').textContent=saved
   ? `${row.filename}: ${next?'excluded':'restored'} in this browser.`
   : storageError;
 };
 return control;
}

function renderDorsalLines(rows){
 const ranked=rows.filter(r=>!excludedOnLoad(r));
 const direction=$('sort').value==='asc'?1:-1;
 ranked.sort((a,b)=>direction*(Number(a.dorsal_orange_pink_percent)-Number(b.dorsal_orange_pink_percent))
  ||a.filename.localeCompare(b.filename));
 const groups=broodOrder.map(brood=>[brood,ranked.filter(row=>row.brood===brood)]);
 groups.push(['Excluded',rows.filter(excludedOnLoad)]);
 for(const [title,items] of groups){
  if(!items.length)continue;
  const section=el('section','group');
  section.append(el('h2','',title));
  const grid=el('div','grid');
  for(const row of items){
   const card=el('article','card');
   const button=el('button','photo');
   button.setAttribute('aria-label',`View ${row.filename}`);
   const img=el('img');
   img.src=`assets/${row.image_id}.jpg`;
   img.alt=row.filename;
   img.loading='lazy';
   button.append(img);
   button.onclick=()=>open(row);
   const meta=el('div','meta',row.filename);
   meta.append(el('div','brood-label',row.brood));
   if(row.dorsal_exclusion_reason){
    meta.append(el('p','note',row.dorsal_exclusion_reason));
   }
   meta.append(reviewButton(row));
   card.append(button,meta);
   grid.append(card);
  }
  section.append(grid);
  $('gallery').append(section);
 }
}

function decodeOverlay(encoded){
 return new DataView(Uint8Array.from(atob(encoded),char=>char.charCodeAt(0)).buffer);
}

const overlayRequests=new Map();
let overlayRequest=0;
function setOverlayVisible(visible){
 $('mask').hidden=!visible;
 $('maskLegend').hidden=!visible;
 $('toggleMask').setAttribute('aria-pressed',String(visible));
 $('toggleMask').textContent=visible?'Hide scored pixels':'Show scored pixels';
}
$('toggleMask').onclick=async()=>{
 const request=++overlayRequest;
 if(!$('mask').hidden){
  setOverlayVisible(false);
  return;
 }
 const row=selected;
 const batch=Math.floor((Number(row.image_id.split('-').at(-1))-1)/32);
 $('maskStatus').textContent='Loading overlay…';
 try{
  if(!overlayRequests.has(batch)) {
   overlayRequests.set(batch,fetch(`dorsal-line-masks-${batch}.json`).then(response=>{
    if(!response.ok)throw new Error('Overlay unavailable');
    return response.json();
   }));
  }
  const {width,height,masks,midlines}=await overlayRequests.get(batch);
  if(request!==overlayRequest)return;
  const canvas=$('mask');
  canvas.width=width;
  canvas.height=height;
  const context=canvas.getContext('2d');
  const overlay=context.createImageData(width,height);
  const runs=decodeOverlay(masks[row.image_id]);
  for(let i=0;i<runs.byteLength;i+=6){
   const start=runs.getUint32(i,true);
   const end=start+runs.getUint8(i+4);
   const rgba=runs.getUint8(i+5)===1?[255,38,116,170]:[174,238,45,160];
   for(let pixel=start;pixel<end;pixel++)overlay.data.set(rgba,4*pixel);
  }
  context.putImageData(overlay,0,0);
  const [top,encodedTrace]=midlines[row.image_id];
  const trace=decodeOverlay(encodedTrace);
  context.beginPath();
  context.moveTo(trace.getUint16(0,true),top);
  for(let i=2;i<trace.byteLength;i+=2)context.lineTo(trace.getUint16(i,true),top+i/2);
  context.strokeStyle='#19342b';
  context.lineWidth=3;
  context.stroke();
  context.strokeStyle='#fff170';
  context.lineWidth=1.25;
  context.stroke();
  $('maskStatus').textContent='';
  setOverlayVisible(true);
 }catch{
  overlayRequests.delete(batch);
  if(request===overlayRequest)$('maskStatus').textContent='Could not load scored pixels. Try again.';
 }
};

function open(r){
 selected=r;
 overlayRequest++;
 setOverlayVisible(false);
 $('maskStatus').textContent='';
 $('large').src=`assets/${r.image_id}.jpg`;
 $('displayImage').href=$('large').getAttribute('src');
 $('viewName').textContent=r.filename;
 $('viewBrood').textContent=r.brood;
 $('ref').textContent=r.reference_note;
 $('saved').textContent='';
 if(dorsalLines){
  $('toggleMask').hidden=Boolean(r.dorsal_exclusion_reason);
  const reason=r.dorsal_exclusion_reason||(reviewExcluded(r)?'Marked in review':'');
  $('dorsalExclusion').hidden=!reason;
  $('dorsalExclusion').textContent=reason?`Excluded · ${reason}`:'';
 }else{
  $('editCrimson').value=score(r);
 }
 $('viewer').showModal();
}
$('close').onclick=()=>$('viewer').close();
function persist(){try{localStorage.setItem(key,JSON.stringify(edits));return true}catch{$('saved').textContent='Browser storage unavailable. Export the CSV now to retain these edits.';$('autosave').textContent=$('saved').textContent;return false}}
$('save').onclick=()=>{edits[selected.image_id]={crimson:$('editCrimson').value};if(persist())$('saved').textContent='Saved in this browser. Export CSV to share.';updateCard(selected);updateCounts()};
$('restore').onclick=()=>{delete edits[selected.image_id];persist();$('editCrimson').value=selected.crimson;$('saved').textContent='Original draft scores restored.';updateCard(selected);updateCounts()};
for(const id of ['brood','state','sort','search','showCrimsonExcluded'])$(id).addEventListener('input',render);
$('export').onclick=()=>{const rows=data.map(r=>{const x={...r,dorsal_review_excluded:reviewExcluded(r)?'yes':'',crimson_review_excluded:crimsonExcluded(r)?'yes':''};x.crimson=score(r);x.crimson_state=x.crimson==='A'?'':x.crimson;if(edits[r.image_id]?.crimson!==undefined)x.crimson_status=x.crimson==='A'?'ambiguous':'user_reviewed';return x});const keys=Object.keys(rows[0]);const esc=v=>'"'+String(v??'').replaceAll('"','""')+'"';const csv=[keys.map(esc).join(','),...rows.map(r=>keys.map(k=>esc(r[k])).join(','))].join('\r\n');const u=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=el('a');a.href=u;a.download='larval_color_scores_reviewed.csv';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};
const dataUrl=reviewDraft.size||crimsonReviewDraft.size?`data.json?review=${Date.now()}`:'data.json?v=5c718f7654a0';
fetch(dataUrl,{cache:'no-cache'}).then(response=>{
 if(!response.ok)throw Error('Data could not be loaded');
 return response.json();
}).then(rows=>{
 data=rows;
 const reviewable=new Map(rows.filter(row=>!row.dorsal_exclusion_reason).map(row=>[row.image_id,row]));
 for(const [id,excluded] of reviewDraft){
  const row=reviewable.get(id);
  if(!row||excluded===publishedExclusion(row))reviewDraft.delete(id);
 }
 storeReviewDraft();
 for(const row of rows){
  if(crimsonReviewDraft.get(row.image_id)===publishedCrimsonExclusion(row))crimsonReviewDraft.delete(row.image_id);
  if(crimsonExcluded(row))crimsonExclusionsOnLoad.add(row.image_id);
 }
 storeReviewDraft(crimsonReviewKey,crimsonReviewDraft);
 updateReviewStatus();
 for(const brood of broodOrder){
  if(data.some(row=>row.brood===brood)){
   const option=el('option','',brood);
   option.value=brood;
   $('brood').append(option);
  }
 }
 render();
}).catch(error=>{$('stats').textContent=error.message});
