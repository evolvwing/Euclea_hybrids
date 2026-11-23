"""Apply an authenticated repository owner's dorsal review request."""
import csv
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/larval_color_scores_reviewed.csv'
PUBLISHED = ROOT / 'docs/data.json'
EXPORT = ROOT / 'docs/larval_color_scores.csv'
FIELD = 'dorsal_review_excluded'
TITLE = 'Save dorsal orange line exclusions'


def read_request(event):
    owner = event['repository']['owner']['id']
    issue = event['issue']
    if (event['action'] != 'opened' or issue['title'] != TITLE
            or issue['user']['id'] != owner or event['sender']['id'] != owner):
        raise ValueError('Dorsal review requests require the repository owner')
    body = issue['body'] or ''
    if len(body) > 5000:
        raise ValueError('Dorsal review request is too large')
    payload = json.loads(body)
    if not isinstance(payload, dict) or set(payload) != {'exclude', 'restore'}:
        raise ValueError('Expected exclude and restore lists')
    changes = {}
    for action, values in payload.items():
        if not isinstance(values, list):
            raise ValueError('Expected an image number list')
        for value in values:
            if type(value) is not int or not 1 <= value <= 999:
                raise ValueError('Invalid image number')
            image_id = f'euclea-{value:03}'
            if image_id in changes:
                raise ValueError('Duplicate image number')
            changes[image_id] = 'yes' if action == 'exclude' else ''
    if not changes:
        raise ValueError('No changes to save')
    return changes


def write_csv(path, rows, fields, newline):
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator=newline)
        writer.writeheader()
        writer.writerows(rows)


def apply(changes):
    with SOURCE.open(newline='') as handle:
        reader = csv.DictReader(handle)
        baseline = list(reader)
        source_fields = list(reader.fieldnames)
    published = json.loads(PUBLISHED.read_text())
    source_rows = {row['image_id']: row for row in baseline}
    published_rows = {row['image_id']: row for row in published}
    for image_id in changes:
        if image_id not in source_rows or image_id not in published_rows:
            raise ValueError(f'Unknown image {image_id}')
        if published_rows[image_id]['dorsal_exclusion_reason']:
            raise ValueError(f'{image_id} has no automated score to review')
    if all(source_rows[image_id].get(FIELD, '') == value for image_id, value in changes.items()):
        return
    if FIELD not in source_fields:
        source_fields.append(FIELD)
    for row in baseline:
        row[FIELD] = changes.get(row['image_id'], row.get(FIELD, ''))
    for row in published:
        row[FIELD] = source_rows[row['image_id']][FIELD]
    write_csv(SOURCE, baseline, source_fields, '\r\n')
    PUBLISHED.write_text(json.dumps(published, ensure_ascii=False))
    write_csv(EXPORT, published, published[0].keys(), '\n')


if __name__ == '__main__':
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    apply(read_request(event))
