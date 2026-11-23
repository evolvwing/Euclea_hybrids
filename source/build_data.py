"""Rebuild image-level review data. Color metrics are QC aids, not trait calls."""
import json, csv, re, hashlib
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
files=json.loads((ROOT/'source/inventory.json').read_text())
scores=json.loads((ROOT/'source/scores.json').read_text())
rows=[]
refs={'Backcross_1__DSC_6295__larva_01.jpg':'User reference: faint paired dots = 1',
      'Backcross_1__DSC_6399__larva_02.jpg':'User reference: clear absence = 0',
      'Backcross_1__DSC_6424__larva_03.jpg':'User reference: faint patches = 1',
      'F1__DSC_5345__larva_01.jpg':'User reference: crimson patches present'}
for i,f in enumerate(files):
    name=f['title'];s=scores[str(i)];m=re.match(r'(Backcross|Dihybrid)_(\d+)',name)
    brood=(('BC-' if m[1]=='Backcross' else 'F2-')+m[2]) if m else ('F1 (line unresolved)' if name.startswith('F1') else 'E. incisa')
    path=ROOT/'docs/assets'/f"{f['id']}.jpg"
    im=Image.open(path).convert('RGB').resize((180,300));a=np.array(im).astype(float)/255
    # Fixed central rectangle, deliberately not represented as an anatomical mask.
    r,g,b=a[30:270,36:144,:].transpose(2,0,1)
    red=(r>g*1.25)&(r>b*1.15)&(r>.25)
    orange=(r>g*1.1)&(g>b*1.2)&(r>.35)
    gray=np.array(im.convert('L'),dtype=float)
    sharp=float((np.diff(gray,axis=0)**2).mean()+(np.diff(gray,axis=1)**2).mean())
    row={'image_id':f['id'],'filename':name,'brood':brood,
         'crimson':s['crimson'],'scoli_previously_ambiguous':s['scoli_previously_ambiguous'],
         'crimson_state':s['crimson'] if s['crimson']!='A' else '',
         'crimson_status':'ambiguous' if s['crimson']=='A' else 'provisional_visual',
         'reference_note':refs.get(name,''),'partial_crop_flag':int('partial' in name),
         'individual_id':'','analysis_include':0,'instar':'unknown',
         'central_red_pixel_fraction':round(float(red.mean()),5),
         'central_orange_pixel_fraction':round(float(orange.mean()),5),
         'image_gradient_energy':round(sharp,2),'image_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    if name in refs:
        if name.startswith('Backcross'):
            row['crimson_status']='user_confirmed'
    rows.append(row)
(ROOT/'source/reconstructed_initial_data.json').write_text(json.dumps(rows))
with (ROOT/'source/reconstructed_initial_scores.csv').open('w',newline='') as h:
    w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('Built',len(rows),'rows; all observations excluded from segregation tests pending identity review.')
