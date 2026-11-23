"""Build the photo review, automated color estimates, and crimson segregation tests."""
import csv, json
from pathlib import Path
from collections import Counter
from scipy.stats import chisquare
from quantify_tubercles import quantify
ROOT = Path(__file__).resolve().parents[1]
source = ROOT/'data/larval_color_scores_reviewed.csv'
with source.open(newline='') as f:
    rows = list(csv.DictReader(f))
assert len(rows) == len({r['image_id'] for r in rows}), 'Duplicate image IDs'
for r in rows:
    assert r['crimson'] in ('0','1','A') and r['scoli_previously_ambiguous'] in ('','yes')
    assert (ROOT/'docs/assets'/f"{r['image_id']}.jpg").is_file()
batches = quantify(rows, ROOT/'docs/assets')
for batch, overlay in batches.items():
    (ROOT/'docs'/f'tubercle-masks-{batch}.json').write_text(json.dumps(overlay, separators=(',', ':')))
(ROOT/'docs/data.json').write_text(json.dumps(rows, ensure_ascii=False))
with (ROOT/'docs/larval_color_scores.csv').open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

def write(name, records):
    with (ROOT/'analysis'/name).open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=records[0].keys()); w.writeheader(); w.writerows(records)

counts=[]
for brood in sorted({r['brood'] for r in rows}):
    c=Counter(r['crimson'] for r in rows if r['brood']==brood)
    counts.append(dict(brood=brood,present=c['1'],absent=c['0'],ambiguous=c['A'],scored_n=c['1']+c['0']))
write('crimson_counts_by_brood.csv',counts)
results=[]
for model, probabilities in [('Single locus, complete dominance',{'F2':.75,'BC':.5}),('Two loci, complementary dominance',{'F2':9/16,'BC':.25})]:
    for group,p in probabilities.items():
        c=Counter(r['crimson'] for r in rows if r['brood'].startswith(group+'-'))
        n=c['1']+c['0']; expected=[n*p,n*(1-p)]
        result=chisquare([c['1'],c['0']],expected)
        results.append(dict(model=model,cross=group,present=c['1'],absent=c['0'],ambiguous_excluded=c['A'],scored_n=n,expected_present=expected[0],expected_absent=expected[1],expected_ratio='3:1' if p==.75 else '1:1' if p==.5 else '9:7' if p==9/16 else '1:3',chi_square=float(result.statistic),df=1,p_value=float(result.pvalue)))
write('crimson_segregation_tests.csv',results)
print(f'Built {len(rows)} reviewed records; regenerated counts and four Pearson tests.')
