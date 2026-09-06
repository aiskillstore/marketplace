#!/usr/bin/env python3
"""Validate declared scorecard evidence and compute rubric 2.0 scores (stdlib)."""
import json
import re
from fractions import Fraction
from pathlib import Path
from inspect_skill_package import contains_sensitive_public_value, PublicArgumentParser


class ScorecardError(ValueError):
    """A public, field-specific validation error without input-value echoing."""


def require(condition, field):
    if not condition:
        raise ScorecardError(field + ': invalid or inconsistent value')


def shape(value, keys, field):
    require(type(value) is dict and set(value) == set(keys.split()), field)


def safe(value, field, depth=0):
    require(depth <= 32, field + '.depth')
    if isinstance(value, str):
        require(bool(value.strip()) and len(value) <= 20000 and
                not re.search(r'[\x00-\x1f\x7f]', value) and
                not contains_sensitive_public_value(value), field)
    elif isinstance(value, dict):
        for item in value.values():
            safe(item, field, depth + 1)
    elif isinstance(value, list):
        require(len(value) <= 1000, field)
        for item in value:
            safe(item, field, depth + 1)
    elif isinstance(value, float):
        require(value == value and abs(value) != float('inf'), field)


def string(value, field):
    require(type(value) is str and bool(value.strip()), field)


def records(value, keys, field, id_key='id'):
    require(type(value) is list, field)
    result = {}
    for row in value:
        shape(row, keys, field)
        string(row[id_key], field + '.' + id_key)
        require(row[id_key] not in result, field + '.duplicate_id')
        result[row[id_key]] = row
    return result


def refs(value, authority, field, nonempty=False):
    require(type(value) is list and all(type(x) is str for x in value), field)
    require(len(value) == len(set(value)) and set(value) <= set(authority) and (value or not nonempty), field)


def presented(value):
    if value is None:
        return None
    value = Fraction(value) * 10
    return ((value.numerator * 2 + value.denominator) // (2 * value.denominator)) / 10


def totals(a, e, p):
    return dict(applicable_weight=a, assessed_weight=e, earned_points=presented(p),
                coverage=float(Fraction(e, a)) if a else None,
                assessed_only_score=presented(100*p/e) if e else None,
                quality_score=presented(100*p/a) if e == a and a else None)


def _score_audit(scorecard, contract):
    """Return computed values; no caller totals or release verdict are authoritative."""
    from validate_audit_contract import validate_scoring_contract
    issues = []
    validate_scoring_contract(contract, issues)
    require(not issues, 'contract')
    fields = 'schema_version scorecard_version rubric_version assessment_profile target evidence findings criteria release legacy_projection'
    shape(scorecard, fields, 'scorecard')
    safe(scorecard, 'scorecard.public_text')
    require(type(scorecard['schema_version']) is int and scorecard['schema_version'] == 1, 'schema_version')
    for key in ('scorecard_version', 'rubric_version'):
        require(scorecard[key] == contract[key], key)
    profile = scorecard['assessment_profile']
    require(profile in contract['assessment_profiles'], 'assessment_profile')
    target = scorecard['target']
    shape(target, 'artifact host host_version', 'target')
    string(target['artifact'], 'target.artifact')
    for key in ('host', 'host_version'):
        require(target[key] is None or type(target[key]) is str and bool(target[key].strip()), 'target.' + key)
        require(profile != 'host' or bool(target[key]), 'target.' + key)
    defs = {row['id']: row for row in contract['criteria']}
    evidence = records(scorecard['evidence'], 'id method status source observation', 'evidence')
    for row in evidence.values():
        require(row['method'] in contract['evidence_methods'] and row['status'] in contract['evidence_labels'], 'evidence.method_status')
        require(row['method'] != 'Static simulation' or row['status'] == 'Inferred', 'evidence.simulation_status')
        string(row['source'], 'evidence.source'); string(row['observation'], 'evidence.observation')
    findings = records(scorecard['findings'], 'id defect_id primary_criterion_id evidence_ids impact severity resolved', 'findings')
    primary = {}
    impacts = {}
    for row in findings.values():
        string(row['defect_id'], 'findings.defect_id'); string(row['impact'], 'findings.impact')
        require(row['primary_criterion_id'] in defs, 'findings.primary_criterion_id')
        require(row['severity'] in ('Critical', 'High', 'Medium', 'Low', 'Nit') and type(row['resolved']) is bool, 'findings.severity_resolved')
        refs(row['evidence_ids'], evidence, 'findings.evidence_ids', True)
        defect = row['defect_id']
        require(primary.setdefault(defect, row['primary_criterion_id']) == row['primary_criterion_id'], 'findings.defect_primary')
        impacts.setdefault(defect, set()).add(' '.join(row['impact'].lower().split()))
    rows = records(scorecard['criteria'], 'criterion_id outcome evidence_ids finding_ids rationale na_reason additional_impacts', 'criteria', 'criterion_id')
    require(set(rows) == set(defs), 'criteria.ids')
    buckets = {row['id']: [0, 0, Fraction(0)] for row in contract['categories']}
    for cid, row in rows.items():
        definition = defs[cid]; outcome = row['outcome']
        require(outcome in contract['result_enums'], 'criteria.outcome')
        string(row['rationale'], 'criteria.rationale')
        refs(row['evidence_ids'], evidence, 'criteria.evidence_ids')
        refs(row['finding_ids'], findings, 'criteria.finding_ids')
        require(type(row['additional_impacts']) is list, 'criteria.additional_impacts')
        if outcome == 'Not Applicable':
            require(row['na_reason'] in definition['not_applicable_reasons'], 'criteria.na_reason')
        else:
            require(row['na_reason'] is None, 'criteria.na_reason')
        assessed = outcome in contract['earned_fractions']
        if assessed:
            require(any(evidence[eid]['method'] in definition['required_methods'][profile] and
                        (evidence[eid]['status'] == 'Verified' or profile == 'design' and evidence[eid]['status'] == 'Inferred')
                        for eid in row['evidence_ids']), 'criteria.sufficient_evidence')
        else:
            require(not row['evidence_ids'], 'criteria.unassessed_evidence')
        if outcome in ('Partial', 'Fail'):
            require(bool(row['finding_ids']), 'criteria.deduction_findings')
            extra = records(row['additional_impacts'], 'finding_id impact evidence_ids', 'criteria.additional_impacts', 'finding_id')
            needed = {fid for fid in row['finding_ids'] if findings[fid]['primary_criterion_id'] != cid}
            require(set(extra) == needed, 'criteria.additional_impacts')
            for fid, impact in extra.items():
                string(impact['impact'], 'criteria.additional_impact')
                refs(impact['evidence_ids'], evidence, 'criteria.additional_evidence', True)
                normalized = ' '.join(impact['impact'].lower().split())
                known = impacts[findings[fid]['defect_id']]
                require(normalized not in known, 'criteria.distinct_impact'); known.add(normalized)
        else:
            require(not row['finding_ids'] and not row['additional_impacts'], 'criteria.non_deduction')
        bucket = buckets[definition['category']]
        if outcome != 'Not Applicable': bucket[0] += definition['weight']
        if assessed:
            bucket[1] += definition['weight']
            bucket[2] += definition['weight'] * Fraction(str(contract['earned_fractions'][outcome]))
    release = scorecard['release']
    shape(release, 'artifact_eligible required_gates', 'release')
    require(type(release['artifact_eligible']) is bool and not (profile == 'design' and release['artifact_eligible']), 'release.artifact_eligible')
    gates = records(release['required_gates'], 'id result rationale', 'release.required_gates')
    require(not gates or set(gates) == {'G%02d' % n for n in range(1,24)}, 'release.gate_ids')
    require(not release['artifact_eligible'] or bool(gates), 'release.required_gates')
    for gate in gates.values():
        require(gate['result'] in contract['result_enums'], 'release.gate_result'); string(gate['rationale'], 'release.gate_rationale')
    results = {g['result'] for g in gates.values()}
    unresolved = {f['severity'] for f in findings.values() if not f['resolved']}
    verdict = ('Fail' if 'Fail' in results or unresolved & {'Critical', 'High'} else
               'Not Assessed' if not release['artifact_eligible'] or not gates or 'Not Assessed' in results or results == {'Not Applicable'} else
               'Partial' if 'Partial' in results else 'Pass')
    legacy = scorecard['legacy_projection']
    shape(legacy, 'enabled cap_reasons', 'legacy_projection')
    require(type(legacy['enabled']) is bool, 'legacy_projection.enabled')
    caps = contract['legacy_policy']['caps']
    refs(legacy['cap_reasons'], caps, 'legacy_projection.cap_reasons')
    reasons = set()
    if 'Critical' in unresolved: reasons.add('unresolved_critical')
    if 'High' in unresolved: reasons.add('unresolved_high')
    if not gates or gates['G20']['result'] in ('Fail', 'Not Assessed'):
        reasons.add('missing_or_failed_required_pressure_evidence')
    require(set(legacy['cap_reasons']) == reasons, 'legacy_projection.cap_reasons')
    output = totals(sum(b[0] for b in buckets.values()), sum(b[1] for b in buckets.values()), sum((b[2] for b in buckets.values()), Fraction(0)))
    quality = output['quality_score']
    output.update(scorecard_version=contract['scorecard_version'], rubric_version=contract['rubric_version'], assessment_profile=profile,
                  target=dict(target), categories={key: totals(*value) for key, value in buckets.items()}, release_verdict=verdict,
                  legacy_cap_reasons=sorted(reasons), legacy_policy_score=min([quality] + [caps[r] for r in reasons]) if legacy['enabled'] and quality is not None else None)
    return output


def score_audit(scorecard, contract):
    """Validate a JSON-shaped scorecard and return independently computed scores."""
    try:
        return _score_audit(scorecard, contract)
    except ScorecardError:
        raise
    except (TypeError, KeyError, AttributeError, RecursionError):
        raise ScorecardError('scorecard.structure: invalid field type') from None


def example_scorecard(contract):
    """Synthetic prose-only design with complete, declared static evidence."""
    return dict(schema_version=1, scorecard_version='1.0', rubric_version='2.0', assessment_profile='design',
                target=dict(artifact='synthetic-prose-skill', host=None, host_version=None),
                evidence=[dict(id='E1', method='Static inspection', status='Verified', source='SKILL.md', observation='Synthetic complete instructions and boundaries inspected.')], findings=[],
                criteria=[dict(criterion_id=c['id'], outcome='Pass', evidence_ids=['E1'], finding_ids=[], rationale='Synthetic instructions satisfy the documented design anchor.', na_reason=None, additional_impacts=[]) for c in contract['criteria']],
                release=dict(artifact_eligible=False, required_gates=[]), legacy_projection=dict(enabled=False, cap_reasons=['missing_or_failed_required_pressure_evidence']))


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'json.duplicate_key'); result[key] = value
        return result
    with path.open('rb') as stream:
        data = stream.read(1_000_001)
    require(len(data) <= 1_000_000, 'json.size')
    return json.loads(data, object_pairs_hook=pairs, parse_constant=lambda _: require(False, 'json.number'))


def main():
    parser = PublicArgumentParser(description=__doc__)
    parser.add_argument('scorecard', type=Path)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        result = score_audit(read_json(args.scorecard), read_json(Path(__file__).resolve().parent.parent / 'references/scoring-contract.json'))
    except ScorecardError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    except (ValueError, TypeError, KeyError, OSError, RecursionError):
        print(json.dumps({'error': 'Invalid scorecard or unavailable input; validate fields against scorecard-schema.md.'}))
        return 2
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
