"""Build the photo review, automated color estimates, and crimson segregation tests."""
import argparse, csv, json
from base64 import b64decode
from struct import iter_unpack
from pathlib import Path
from collections import Counter
from scipy.stats import chisquare
from quantify_tubercles import quantify
ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true', help='Verify the published measurements without rerunning image analysis.')
args = parser.parse_args()
source = ROOT/'data/larval_color_scores_reviewed.csv'
with source.open(newline='') as f:
    rows = list(csv.DictReader(f))
assert len(rows) == len({r['image_id'] for r in rows}), 'Duplicate image IDs'
for r in rows:
    assert r['crimson'] in ('0','1','A') and r['scoli_previously_ambiguous'] in ('','yes')
    assert (ROOT/'docs/assets'/f"{r['image_id']}.jpg").is_file()
docs = ROOT/'docs'
if args.check:
    published = json.loads((docs/'data.json').read_text())
    with (docs/'larval_color_scores.csv').open(newline='') as f:
        assert list(csv.DictReader(f)) == published, 'Published CSV and JSON differ'
    assert len(rows) == len(published)
    masks = {}
    for path in docs.glob('tubercle-masks-*.json'):
        overlay = json.loads(path.read_text())
        assert overlay['width'] * overlay['height'] == 168 * 280
        masks.update(overlay['masks'])
    for baseline, record in zip(rows, published):
        assert all(record[k] == v for k, v in baseline.items() if k not in (
            'scoli_orange_pink_percent', 'scoli_orange_pink_pixels',
            'scoli_yellow_green_pixels', 'scoli_exclusion_reason'
        )), f'Published baseline differs for {baseline["image_id"]}'
        if record['scoli_exclusion_reason']:
            assert record['image_id'] not in masks
            assert record['scoli_orange_pink_percent'] == ''
            continue
        counts = Counter()
        last = 0
        for start, length, color in iter_unpack('<HBB', b64decode(masks.pop(record['image_id']))):
            assert start >= last and length > 0 and color in (1, 2)
            counts[color] += length
            last = start + length
        assert last <= 168 * 280
        assert counts[1] == int(record['scoli_orange_pink_pixels'])
        assert counts[2] == int(record['scoli_yellow_green_pixels'])
        assert record['scoli_orange_pink_percent'] == f'{100 * counts[1] / counts.total():.2f}'
    assert not masks, 'Overlay contains unused images'
else:
    batches = quantify(rows, docs/'assets')
    for batch, overlay in batches.items():
        (docs/f'tubercle-masks-{batch}.json').write_text(json.dumps(overlay, separators=(',', ':')))
    (docs/'data.json').write_text(json.dumps(rows, ensure_ascii=False))
    with (docs/'larval_color_scores.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def write(name, records):
    if args.check:
        with (ROOT/'analysis'/name).open(newline='') as f:
            saved = list(csv.DictReader(f))
        assert len(saved) == len(records)
        for actual, expected in zip(saved, records):
            for field, value in expected.items():
                if isinstance(value, float):
                    assert abs(float(actual[field]) - value) <= abs(value) * 1e-12
                else:
                    assert actual[field] == str(value)
        return
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
print(f'{len(rows)} records and the crimson segregation results verified.' if args.check
      else f'Built {len(rows)} reviewed records; regenerated counts and four Pearson tests.')
