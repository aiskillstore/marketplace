#!/usr/bin/env python3
"""Neutral finding outcomes from separately reviewed labels, never rubric scores."""
import argparse
import json
import math
from pathlib import Path

from build_fixtures import digest
from check_results import summarize_resources


def frozen_hash(suite):
    return digest({k: v for k, v in suite.items() if k != 'frozen_hash'})


def sha256_identity(value):
    return isinstance(value, str) and len(value) == 64 and all(x in '0123456789abcdef' for x in value)


def nonempty_text(value):
    return isinstance(value, str) and bool(value.strip())


def example_suite():
    artifact = 'If input is missing, invent text and silently present it as user input.'
    suite = dict(schema_version=1, benchmark='neutral-findings', split='pilot',
        labels={'status': 'unreviewed', 'reviewer': None, 'evidence': None,
                'provenance': 'Synthetic schema example only; independent review has not occurred.'},
        conditions={'current': digest('current candidate placeholder'), 'baseline': digest('baseline placeholder')},
        protocol={'prompt_hash': digest('Audit this artifact for concrete defects with evidence.'),
                  'model': 'must be frozen before collection', 'max_output_tokens': 2000,
                  'tools': [], 'reading_policy': 'same fixed context policy for both conditions',
                  'repeats': 1},
        cases=[dict(id='synthetic-example', artifact=artifact, case_hash=digest(artifact),
                    findings=[dict(id='missing-input', severity='High')])])
    suite['frozen_hash'] = frozen_hash(suite)
    return suite


def validate_suite(suite):
    if suite.get('schema_version') != 1 or suite.get('benchmark') != 'neutral-findings':
        raise ValueError('Unsupported neutral benchmark schema.')
    if suite.get('frozen_hash') != frozen_hash(suite):
        raise ValueError('Frozen benchmark hash mismatch.')
    if suite.get('split') not in ('pilot', 'holdout') or set(suite.get('conditions', {})) != {'current', 'baseline'}:
        raise ValueError('Explicit split and paired current/baseline conditions required.')
    for value in suite['conditions'].values():
        if not sha256_identity(value):
            raise ValueError('Condition hashes must be SHA-256 identities.')
    protocol = suite.get('protocol', {})
    if not isinstance(protocol, dict) or not all(k in protocol for k in ('prompt_hash', 'model', 'max_output_tokens', 'tools', 'reading_policy', 'repeats')):
        raise ValueError('Frozen collection protocol required.')
    if not sha256_identity(protocol['prompt_hash']):
        raise ValueError('Frozen prompt hash must be a SHA-256 identity.')
    if not nonempty_text(protocol['model']) or not nonempty_text(protocol['reading_policy']):
        raise ValueError('Explicit nonempty model identity and reading policy required.')
    if type(protocol['max_output_tokens']) is not int or protocol['max_output_tokens'] <= 0:
        raise ValueError('Positive integer frozen output-token cap required.')
    if not isinstance(protocol['tools'], list):
        raise ValueError('Frozen tools must be an explicit list, empty when no tools are available.')
    if type(protocol['repeats']) is not int or protocol['repeats'] < 1:
        raise ValueError('Positive frozen repeat count required.')
    cases = suite.get('cases', [])
    if not cases or len({c['id'] for c in cases}) != len(cases):
        raise ValueError('Nonempty unique cases required.')
    for case in cases:
        if case.get('case_hash') != digest(case['artifact']):
            raise ValueError('Frozen case hash mismatch.')
        labels = case['findings']
        if len({f['id'] for f in labels}) != len(labels) or any(f['severity'] not in ('Low', 'Medium', 'High', 'Critical') for f in labels):
            raise ValueError('Unique finding labels and valid severity required.')
    labels = suite.get('labels', {})
    if labels.get('status') not in ('unreviewed', 'independently-reviewed'):
        raise ValueError('Explicit label review status required.')
    if labels['status'] == 'independently-reviewed' and not all(nonempty_text(labels.get(k)) for k in ('reviewer', 'evidence')):
        raise ValueError('Independent label review requires reviewer and evidence reference.')


def metrics(expected, predictions):
    expected_ids = {f['id'] for f in expected}
    found = set(predictions)
    tp, fp, fn = len(found & expected_ids), len(found - expected_ids), len(expected_ids - found)
    return dict(true_positives=tp, false_positives=fp, false_negatives=fn,
        precision=tp/(tp+fp) if tp+fp else None, recall=tp/(tp+fn) if tp+fn else None,
        severe_misses=sum(f['severity'] in ('High', 'Critical') and f['id'] not in found for f in expected))


def summarize(suite, records):
    validate_suite(suite)
    cases = {c['id']: c for c in suite['cases']}
    reviewed = suite['labels']['status'] == 'independently-reviewed'
    seen, scored, resources = set(), {}, {'current': [], 'baseline': []}
    for record in records:
        condition, cid = record.get('condition'), record.get('case_id')
        repeat = record.get('repeat', 1)
        identity = (condition, cid, repeat)
        if (condition not in suite['conditions'] or cid not in cases or identity in seen or
                type(repeat) is not int or not 1 <= repeat <= suite['protocol']['repeats']):
            raise ValueError('Unknown, duplicate or out-of-range paired record.')
        seen.add(identity)
        if (record.get('suite_hash') != suite['frozen_hash'] or record.get('case_hash') != cases[cid]['case_hash'] or
                record.get('condition_hash') != suite['conditions'][condition] or
                record.get('model') != suite['protocol']['model'] or record.get('prompt_hash') != suite['protocol']['prompt_hash']):
            raise ValueError('Record differs from frozen case, suite or condition.')
        if record.get('status') not in ('Observed', 'Not Assessed'):
            raise ValueError('Explicit observation status required.')
        if record['status'] != 'Observed': continue
        duration = record.get('duration_seconds')
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration < 0:
            raise ValueError('Finite nonnegative observed duration required.')
        review = record.get('matching_review')
        if (not isinstance(review, dict) or not all(nonempty_text(review.get(k)) for k in ('reviewer', 'evidence')) or
                not sha256_identity(review.get('output_sha256'))):
            raise ValueError('Independent finding matching review with output hash and evidence required.')
        predictions = record.get('findings')
        if not isinstance(predictions, list) or any(not isinstance(f, str) or not f for f in predictions) or len(set(predictions)) != len(predictions):
            raise ValueError('Unique reviewed finding IDs required; unmatched findings use distinct FP IDs.')
        resources[condition].append(record)
        if reviewed:
            scored[identity] = metrics(cases[cid]['findings'], predictions)
    conditions = {}
    expected_count = len(cases) * suite['protocol']['repeats']
    for condition in ('current', 'baseline'):
        rows = [v for k, v in scored.items() if k[0] == condition]
        sums = {key: sum(r[key] for r in rows) for key in ('true_positives', 'false_positives', 'false_negatives', 'severe_misses')}
        tp, fp, fn = (sums[k] for k in ('true_positives', 'false_positives', 'false_negatives'))
        conditions[condition] = dict(status='Observed' if len(rows) == expected_count else 'Not Assessed',
            cases_observed=len(rows), **(sums if rows else {k: None for k in sums}), precision=tp/(tp+fp) if tp+fp else None,
            recall=tp/(tp+fn) if tp+fn else None, resources=summarize_resources(resources[condition]))
    pairs = []
    for cid in cases:
        for repeat in range(1, suite['protocol']['repeats']+1):
            current, baseline = scored.get(('current', cid, repeat)), scored.get(('baseline', cid, repeat))
            if current is None or baseline is None: continue
            row = dict(case_id=cid, repeat=repeat, current=current, baseline=baseline)
            for key in ('precision', 'recall', 'severe_misses'):
                row[key+'_difference'] = current[key]-baseline[key] if current[key] is not None and baseline[key] is not None else None
            pair_records = {r['condition']: r for r in records if r['case_id'] == cid and r.get('repeat', 1) == repeat}
            row['duration_seconds_difference'] = pair_records['current']['duration_seconds']-pair_records['baseline']['duration_seconds']
            for key in ('input_tokens', 'output_tokens'):
                a, b = (summarize_resources([pair_records[c]])[key] for c in ('current', 'baseline'))
                row[key+'_difference'] = a-b if a is not None and b is not None else None
            pairs.append(row)
    return dict(schema_version=1, suite_hash=suite['frozen_hash'], split=suite['split'],
        label_status=suite['labels']['status'], conditions=conditions, paired_differences=pairs,
        comparison='Observed descriptive differences' if len(pairs) == expected_count and len(cases) >= 2 else 'Not Assessed',
        superiority='Not Assessed', limitations='External label review and finding matching are human evidence assertions, not authenticated by this checker. No market superiority or causal significance is established.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', type=Path)
    parser.add_argument('--results', type=Path)
    parser.add_argument('--example', action='store_true')
    args = parser.parse_args()
    if args.example:
        print(json.dumps(example_suite(), indent=2))
        return 0
    if not args.suite or not args.results: parser.error('--suite and --results required')
    suite = json.loads(args.suite.read_text(encoding='utf-8'))
    records = [json.loads(line) for line in args.results.read_text(encoding='utf-8').splitlines() if line.strip()]
    print(json.dumps(summarize(suite, records), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
