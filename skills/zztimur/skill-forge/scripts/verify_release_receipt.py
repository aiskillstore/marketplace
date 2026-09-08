#!/usr/bin/env python3
"""Check a reviewer-pinned receipt against candidate bytes and live GitHub facts.

The dispatch receipt hash is the reviewer assertion trust root. An evaluator
report is a pinned review artifact, not a measurement performed by this program.
"""
import argparse
import hashlib
import io
import json
import re
import subprocess
import zipfile
from pathlib import Path

ARTIFACT_NAME = 'release-review-receipt'
SELF_TESTS_PATH = '.github/workflows/self-tests.yml'
CAPTURE_PATH = '.github/workflows/capture-release-receipt.yml'
JOBS = {'Linux containment and bounded tests'} | {
    os + ' / Python ' + version for os in ('ubuntu-latest', 'macos-latest', 'windows-latest')
    for version in ('3.9', '3.x')}
# This is a Skill Forge dual-profile publication gate, not an arbitrary-skill
# audit. Bundled UI metadata, source/runtime suites, and canonical archive proof
# make G07/G11/G12/G23 applicable; the published description limit makes G06
# applicable. Only conditional host fields/validator/upload limits may be N/A.
# See audit-contract.json and release-gate-checklist.md for the full semantics.
OPTIONAL_GATES = {'G08', 'G10', 'G19'}
SEMANTIC_GATES = {'G05', 'G14', 'G17', 'G18', 'G20', 'G21'}
MAX_BYTES = 2_000_000


def need(ok, field):
    if not ok:
        raise ValueError('Release evidence rejected: ' + field)


def shape(value, fields, field):
    need(type(value) is dict and set(value) == set(fields.split()), field)


def text(value):
    return type(value) is str and bool(value.strip()) and len(value) <= 20000 and not re.search(r'[\x00-\x1f\x7f]', value)


def digest(value):
    return type(value) is str and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def positive(value):
    return type(value) is int and value > 0


def load_json(raw):
    need(len(raw) <= MAX_BYTES, 'JSON size')
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: need(False, 'nonfinite JSON number'))


def verify_independent(report, pins, archive_sha256):
    need(type(report) is dict and type(report.get('schema_version')) is int and report['schema_version'] == 2,
         'independent report version')
    need(report.get('status') == 'pass' and report.get('evidence_class') == 'independent_schema_match',
         'independent report status')
    transition = report.get('schema_transition', {})
    need(transition.get('requested') is False and transition.get('activated') is False, 'bootstrap evidence')
    for key in ('scratch_execution', 'credential_environment_removed', 'installed_integrity_verified', 'candidate_integrity_verified'):
        need(report.get(key) is True, 'independent report ' + key)
    need(report.get('installed_mutated') is False and report.get('candidate_mutated') is False and report.get('errors') == [],
         'independent mutation/errors')
    candidate = report.get('candidate', {})
    need(all(candidate.get(k) == archive_sha256 for k in ('sha256', 'sha256_after', 'copy_sha256', 'expected_sha256')),
         'independent candidate identity')
    provenance = report.get('evaluator_provenance', {})
    for kind in ('tree', 'inspector'):
        expected = pins[kind + '_sha256']
        need(digest(expected) and all(provenance.get(k) == expected for k in (
            kind+'_sha256', kind+'_sha256_after', kind+'_copy_sha256', 'expected_'+kind+'_sha256')),
            'reviewer-pinned evaluator ' + kind)
    integrity = provenance.get('tree_integrity_sha256')
    need(digest(integrity) and integrity == provenance.get('tree_integrity_sha256_after'), 'evaluator integrity')
    profiles = report.get('profiles', {})
    need(type(profiles) is dict and set(profiles) == {'portable', 'openai'}, 'independent profiles')
    for name, row in profiles.items():
        need(row.get('status') == 'pass' and type(row.get('schema_version')) is int and row['schema_version'] == 6
             and row.get('schema_compatibility') == 'exact', 'independent profile version/status')
        need(type(row.get('exit_code')) is int and row['exit_code'] == 0 and row.get('errors') == [], 'independent profile exit')
        for key in ('timed_out', 'output_limit_exceeded', 'target_alias_used', 'raw_frontmatter_propagated'):
            need(row.get(key) is False, 'independent profile ' + key)
        need(row.get('requested_target') == name and row.get('canonical_target') == name and row.get('input_type') == 'zip',
             'independent profile target')
        need(row.get('manifest_verification_complete') is True and row.get('coverage_complete') is True, 'independent coverage')
        summary = row.get('summary', {})
        need(summary.get('status') == 'pass' and summary.get('strict_pass') is True, 'independent strict pass')
        counts = [summary.get(k) for k in ('error_count', 'warning_count', 'finding_count')]
        need(all(type(n) is int and n >= 0 for n in counts) and counts[0] == 0 and counts[2] >= sum(counts[:2]),
             'independent summary counts')


def _verify_receipt(receipt, report_bytes, facts, *, repository, release_tag, commit, archive_sha256, receipt_run_id):
    shape(receipt, 'schema_version repository release_tag commit archive_sha256 reviewer independent_evaluator self_tests_run_id gates', 'receipt fields')
    need(type(receipt['schema_version']) is int and receipt['schema_version'] == 1, 'receipt version')
    need(re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository) is not None, 'repository')
    need(re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+', release_tag) is not None, 'release tag')
    need(re.fullmatch(r'[0-9a-f]{40}', commit) is not None and digest(archive_sha256), 'candidate identity format')
    for key, expected in (('repository',repository), ('release_tag',release_tag), ('commit',commit), ('archive_sha256',archive_sha256)):
        need(receipt[key] == expected, 'receipt ' + key)
    reviewer = receipt['reviewer']
    shape(reviewer, 'github_login evidence_class', 'reviewer fields')
    need(text(reviewer['github_login']) and reviewer['evidence_class'] == 'reviewer_assertion', 'reviewer trust root')
    gates = receipt['gates']
    need(type(gates) is list and len(gates) == 23, '23 gates required')
    ids = []
    for gate in gates:
        shape(gate, 'id result evidence_label evidence_class rationale evidence_refs', 'gate fields')
        need(type(gate['id']) is str, 'gate ID')
        ids.append(gate['id'])
        need(gate['result'] in ('Pass', 'Not Applicable'), 'gate outcome')
        need(gate['result'] == 'Pass' or gate['id'] in OPTIONAL_GATES, 'mandatory Skill Forge gate')
        allowed_labels = ('Verified', 'Inferred') if gate['id'] in SEMANTIC_GATES else ('Verified',)
        need(gate['evidence_label'] in allowed_labels and gate['evidence_class'] == 'reviewer_assertion', 'gate evidence class')
        need(text(gate['rationale']) and type(gate['evidence_refs']) is list and gate['evidence_refs']
             and all(text(ref) for ref in gate['evidence_refs']), 'gate evidence references')
    need(set(ids) == {'G%02d' % n for n in range(1,24)}, 'gate IDs')
    need(any(g['result'] == 'Pass' for g in gates), 'all gates excluded')
    pins = receipt['independent_evaluator']
    shape(pins, 'report_sha256 tree_sha256 inspector_sha256', 'evaluator pins')
    need(digest(pins['report_sha256']) and hashlib.sha256(report_bytes).hexdigest() == pins['report_sha256'], 'evaluator report digest')
    verify_independent(load_json(report_bytes), pins, archive_sha256)
    artifact, capture, capture_workflow = facts['artifact'], facts['receipt_run'], facts['receipt_workflow']
    need(positive(receipt_run_id) and capture['id'] == receipt_run_id and artifact['workflow_run']['id'] == receipt_run_id,
         'receipt artifact run identity')
    need(artifact['name'] == ARTIFACT_NAME and artifact['expired'] is False, 'receipt artifact')
    need(capture_workflow['path'] == CAPTURE_PATH and capture['workflow_id'] == capture_workflow['id'], 'receipt capture workflow')
    need(capture['actor']['login'] == reviewer['github_login'], 'receipt uploading reviewer')
    for run in (capture, facts['ci_run']):
        need(run['repository']['full_name'] == repository and run['head_repository']['full_name'] == repository, 'run repository')
        need(run['status'] == 'completed' and run['conclusion'] == 'success', 'completed successful run')
    ci, workflow = facts['ci_run'], facts['ci_workflow']
    need(positive(receipt['self_tests_run_id']) and ci['id'] == receipt['self_tests_run_id'], 'self tests run identity')
    need(ci['head_sha'] == commit and ci['event'] in ('push','workflow_dispatch'), 'self tests exact source commit')
    need(workflow['path'] == SELF_TESTS_PATH and workflow['name'] == 'Self Tests'
         and ci['workflow_id'] == workflow['id'] and ci['name'] == 'Self Tests', 'self tests workflow identity')
    need(positive(ci['run_attempt']) and facts['jobs_run_attempt'] == ci['run_attempt'], 'CI attempt')
    jobs = facts['jobs']
    need(type(jobs) is list and len(jobs) == 7 and {j['name'] for j in jobs} == JOBS, 'seven required jobs')
    need(len({j['id'] for j in jobs}) == 7, 'unique CI jobs')
    for job in jobs:
        need(job['run_id'] == ci['id'] and job['head_sha'] == commit, 'CI job source identity')
        need(job['status'] == 'completed' and job['conclusion'] == 'success', 'CI job success')
    return dict(publication_allowed=True, commit=commit, archive_sha256=archive_sha256,
                review_evidence_class='reviewer_assertion', evaluator_evidence_class='reviewer_pinned_report',
                gate_evidence_labels={gate['id']: gate['evidence_label'] for gate in gates},
                ci_evidence_class='github_api_observation', self_tests_run_id=ci['id'], self_tests_run_attempt=ci['run_attempt'])


def verify_receipt(*args, **kwargs):
    """Validate injected API observations; only the CLI fetch establishes their origin."""
    try:
        return _verify_receipt(*args, **kwargs)
    except (KeyError, TypeError, AttributeError, RecursionError):
        raise ValueError('Release evidence rejected: missing or malformed field') from None


def github(path, binary=False):
    """Fetch authenticated observations from github.com, never a receipt-supplied URL."""
    result = subprocess.run(['gh','api','--hostname','github.com', '-H', 'Accept: application/vnd.github+json',
                             '-H', 'X-GitHub-Api-Version: 2022-11-28', path],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    need(result.returncode == 0 and len(result.stdout) <= MAX_BYTES, 'GitHub API request')
    return result.stdout if binary else load_json(result.stdout)


def fetch_and_verify(*, repository, release_tag, commit, archive, receipt_run_id, receipt_sha256, api=github):
    need(re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository) is not None
         and positive(receipt_run_id) and digest(receipt_sha256), 'fetch inputs')
    prefix = 'repos/' + repository + '/actions/'
    capture = api(prefix+'runs/'+str(receipt_run_id))
    listing = api(prefix+'runs/'+str(receipt_run_id)+'/artifacts?per_page=100')
    need(type(listing.get('total_count')) is int and listing['total_count'] <= 100
         and len(listing['artifacts']) == listing['total_count'], 'complete artifact listing')
    matches = [a for a in listing['artifacts'] if a.get('name') == ARTIFACT_NAME]
    need(len(matches) == 1, 'unique receipt artifact')
    artifact = matches[0]
    need(positive(artifact['id']) and type(artifact['size_in_bytes']) is int and 0 < artifact['size_in_bytes'] <= MAX_BYTES
         and artifact['expired'] is False, 'artifact download bound')
    bundle = api(prefix+'artifacts/'+str(artifact['id'])+'/zip', binary=True)
    need(len(bundle) <= MAX_BYTES and artifact.get('digest') == 'sha256:'+hashlib.sha256(bundle).hexdigest(), 'GitHub artifact digest')
    with zipfile.ZipFile(io.BytesIO(bundle)) as zipped:
        members = zipped.infolist()
        need(len(members) == 2 and {m.filename for m in members} == {'receipt.json','independent-evaluator.json'}
             and all(m.file_size <= MAX_BYTES for m in members), 'receipt bundle members')
        receipt_bytes = zipped.read('receipt.json')
        report_bytes = zipped.read('independent-evaluator.json')
    need(hashlib.sha256(receipt_bytes).hexdigest() == receipt_sha256, 'reviewer dispatch receipt pin')
    receipt = load_json(receipt_bytes)
    ci_id = receipt.get('self_tests_run_id')
    need(positive(ci_id), 'self tests run ID')
    ci = api(prefix+'runs/'+str(ci_id))
    need(positive(ci['run_attempt']), 'self tests run attempt')
    jobs = api(prefix+'runs/'+str(ci_id)+'/attempts/'+str(ci['run_attempt'])+'/jobs?per_page=100')
    need(jobs['total_count'] == len(jobs['jobs']) == 7, 'complete CI jobs listing')
    facts = dict(ci_run=ci, jobs=jobs['jobs'], jobs_run_attempt=ci['run_attempt'], ci_workflow=api(prefix+'workflows/self-tests.yml'),
                 receipt_run=capture, receipt_workflow=api(prefix+'workflows/capture-release-receipt.yml'), artifact=artifact)
    with Path(archive).open('rb') as stream:
        archive_hash = hashlib.sha256()
        for block in iter(lambda: stream.read(1024*1024), b''):
            archive_hash.update(block)
    result = verify_receipt(receipt, report_bytes, facts, repository=repository, release_tag=release_tag,
                            commit=commit, archive_sha256=archive_hash.hexdigest(), receipt_run_id=receipt_run_id)
    # Detect a rerun started while these observations were being fetched.
    latest = api(prefix+'runs/'+str(ci_id))
    need(latest['run_attempt'] == ci['run_attempt'] and latest['status'] == 'completed'
         and latest['conclusion'] == 'success' and latest['head_sha'] == commit, 'CI changed during verification')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repository','release-tag','commit','archive','receipt-run-id','receipt-sha256'):
        parser.add_argument('--'+name, required=True, type=int if name=='receipt-run-id' else str)
    args = parser.parse_args()
    try:
        result = fetch_and_verify(**vars(args))
    except (ValueError, KeyError, TypeError, AttributeError, OSError, RecursionError, zipfile.BadZipFile, subprocess.SubprocessError):
        print(json.dumps(dict(publication_allowed=False, error='Missing, untrusted, stale, or incomplete release evidence.')))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
