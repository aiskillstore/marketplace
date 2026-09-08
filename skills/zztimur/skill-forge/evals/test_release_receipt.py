"""Publication receipt tests: fetched facts must override receipt assertions."""
import copy
import hashlib
import io
import json
import sys
import unittest
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
COMMIT = 'a' * 40
ARCHIVE = 'b' * 64
TREE = 'c' * 64
INSPECTOR = 'd' * 64


def fixture():
    report = dict(schema_version=2, status='pass', evidence_class='independent_schema_match',
                  schema_transition=dict(requested=False, activated=False),
                  evaluator_provenance=dict(tree_sha256=TREE, tree_sha256_after=TREE, tree_copy_sha256=TREE,
                    expected_tree_sha256=TREE, inspector_sha256=INSPECTOR, inspector_sha256_after=INSPECTOR,
                    inspector_copy_sha256=INSPECTOR, expected_inspector_sha256=INSPECTOR,
                    tree_integrity_sha256=TREE, tree_integrity_sha256_after=TREE),
                  candidate=dict(sha256=ARCHIVE, sha256_after=ARCHIVE, copy_sha256=ARCHIVE, expected_sha256=ARCHIVE),
                  profiles={}, scratch_execution=True, credential_environment_removed=True,
                  installed_mutated=False, candidate_mutated=False, installed_integrity_verified=True,
                  candidate_integrity_verified=True, errors=[])
    for profile in ('portable', 'openai'):
        report['profiles'][profile] = dict(status='pass', schema_version=6, schema_compatibility='exact',
            exit_code=0, timed_out=False, output_limit_exceeded=False, raw_frontmatter_propagated=False,
            requested_target=profile, canonical_target=profile, target_alias_used=False,
            input_type='zip', manifest_verification_complete=True, coverage_complete=True,
            summary=dict(status='pass', strict_pass=True, error_count=0, warning_count=0, finding_count=0), errors=[])
    report_bytes = json.dumps(report).encode()
    receipt = dict(schema_version=1, repository='example/skill', release_tag='v3.0.0', commit=COMMIT,
        archive_sha256=ARCHIVE, reviewer=dict(github_login='reviewer', evidence_class='reviewer_assertion'),
        independent_evaluator=dict(report_sha256=hashlib.sha256(report_bytes).hexdigest(), tree_sha256=TREE,
                                   inspector_sha256=INSPECTOR), self_tests_run_id=101,
        gates=[dict(id='G%02d' % n, result='Pass', evidence_label='Verified',
                    evidence_class='reviewer_assertion', rationale='Reviewed exact candidate',
                    evidence_refs=['review:synthetic-record']) for n in range(1,24)])
    ci = dict(id=101, workflow_id=11, name='Self Tests', head_sha=COMMIT, status='completed', conclusion='success',
              run_attempt=2, event='push', repository=dict(full_name='example/skill'),
              head_repository=dict(full_name='example/skill'))
    names = ['Linux containment and bounded tests'] + [os+' / Python '+v for os in
             ('ubuntu-latest','macos-latest','windows-latest') for v in ('3.9','3.x')]
    jobs = [dict(id=idx+1, run_id=101, run_attempt=2, head_sha=COMMIT, name=name,
                 status='completed', conclusion='success') for idx,name in enumerate(names)]
    facts = dict(ci_run=ci, jobs=jobs, jobs_run_attempt=2, ci_workflow=dict(id=11,path='.github/workflows/self-tests.yml',name='Self Tests'),
                 receipt_run=dict(id=202, workflow_id=22,status='completed',conclusion='success',
                    repository=dict(full_name='example/skill'),head_repository=dict(full_name='example/skill'),
                    actor=dict(login='reviewer')),
                 receipt_workflow=dict(id=22,path='.github/workflows/capture-release-receipt.yml'),
                 artifact=dict(name='release-review-receipt',expired=False,workflow_run=dict(id=202)))
    return receipt, report_bytes, facts


class ReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exists = (ROOT/'scripts/verify_release_receipt.py').is_file()
        if cls.exists:
            import verify_release_receipt
            cls.module = verify_release_receipt

    def verify(self, receipt=None, report=None, facts=None):
        self.assertTrue(self.exists, 'publication receipt verifier is missing')
        default_receipt, default_report, default_facts = fixture()
        return self.module.verify_receipt(receipt if receipt is not None else default_receipt,
            report if report is not None else default_report, facts if facts is not None else default_facts,
            repository='example/skill', release_tag='v3.0.0', commit=COMMIT,
            archive_sha256=ARCHIVE, receipt_run_id=202)

    def test_complete_review_and_fetched_facts_allow_publication(self):
        result = self.verify()
        self.assertTrue(result['publication_allowed'])
        self.assertEqual(result['review_evidence_class'], 'reviewer_assertion')
        self.assertEqual(result['ci_evidence_class'], 'github_api_observation')

    def test_semantic_inferences_are_retained_without_relabeling_as_verified(self):
        receipt, report, facts = fixture()
        for index in (4,13,16,17,19,20):
            receipt['gates'][index]['evidence_label'] = 'Inferred'
        result = self.verify(receipt, report, facts)
        self.assertTrue(result['publication_allowed'])
        self.assertEqual(result['gate_evidence_labels']['G05'], 'Inferred')
        self.assertEqual(result['gate_evidence_labels']['G09'], 'Verified')

    def test_mandatory_skill_forge_gates_cannot_be_excluded(self):
        # Literal expectations follow the source+ZIP Skill Forge release scope,
        # independently of the implementation's applicability constants.
        for number in (1,2,3,4,5,6,7,9,11,12,13,14,15,16,17,18,20,21,22,23):
            receipt,report,facts=fixture()
            receipt['gates'][number-1]['result']='Not Applicable'
            with self.subTest(gate=number), self.assertRaises(ValueError):
                self.verify(receipt,report,facts)

    def test_optional_host_requirements_can_be_excluded_with_evidence(self):
        receipt,report,facts=fixture()
        for index in (7,9,18):
            receipt['gates'][index].update(result='Not Applicable',
                rationale='No applicable host-specific requirement or optional validator is available.',
                evidence_refs=['review:target-scope'])
        self.assertTrue(self.verify(receipt,report,facts)['publication_allowed'])
        receipt['gates'][9]['rationale']=''
        with self.assertRaises(ValueError): self.verify(receipt,report,facts)

    def test_measured_integrity_and_arithmetic_gates_cannot_use_inference(self):
        for number in (1,2,3,4,6,7,8,9,10,11,12,13,15,16,19,22,23):
            receipt,report,facts=fixture()
            receipt['gates'][number-1]['evidence_label']='Inferred'
            with self.subTest(gate=number), self.assertRaises(ValueError):
                self.verify(receipt,report,facts)

    def test_missing_stale_or_failed_gate_receipt_blocks(self):
        for change in ('missing','stale','fail','partial','unassessed','duplicate','unverified'):
            receipt, report, facts = fixture()
            if change=='missing': receipt['gates'].pop()
            if change=='stale': receipt['commit']='e'*40
            if change=='fail': receipt['gates'][0]['result']='Fail'
            if change=='partial': receipt['gates'][0]['result']='Partial'
            if change=='unassessed': receipt['gates'][0]['result']='Not Assessed'
            if change=='duplicate': receipt['gates'][1]=copy.deepcopy(receipt['gates'][0])
            if change=='unverified': receipt['gates'][0]['evidence_label']='Unverified'
            with self.subTest(change=change), self.assertRaises(ValueError): self.verify(receipt,report,facts)

    def test_fetched_ci_wrong_commit_failure_missing_and_rerun_block(self):
        for change in ('commit','failed','missing','attempt','workflow','fork','job_commit'):
            receipt,report,facts=fixture()
            if change=='commit': facts['ci_run']['head_sha']='e'*40
            if change=='failed': facts['jobs'][0]['conclusion']='failure'
            if change=='missing': facts['jobs'].pop()
            if change=='attempt': facts['jobs_run_attempt']=1
            if change=='workflow': facts['ci_run']['workflow_id']=33
            if change=='fork': facts['ci_run']['head_repository']['full_name']='other/skill'
            if change=='job_commit': facts['jobs'][0]['head_sha']='e'*40
            with self.subTest(change=change), self.assertRaises(ValueError): self.verify(receipt,report,facts)

    def test_independent_incomplete_bootstrap_or_mismatched_pin_blocks(self):
        for change in ('coverage','bootstrap','tree','candidate','profile','integrity','status'):
            receipt,report_bytes,facts=fixture(); report=json.loads(report_bytes)
            if change=='coverage': report['profiles']['portable']['coverage_complete']=False
            if change=='bootstrap': report['evidence_class']='bootstrap_transition'
            if change=='tree': report['evaluator_provenance']['tree_sha256']='e'*64
            if change=='candidate': report['candidate']['sha256']='e'*64
            if change=='profile': del report['profiles']['openai']
            if change=='integrity': report['installed_integrity_verified']=False
            if change=='status': report['status']='not_assessed'
            report_bytes=json.dumps(report).encode()
            receipt['independent_evaluator']['report_sha256']=hashlib.sha256(report_bytes).hexdigest()
            with self.subTest(change=change), self.assertRaises(ValueError): self.verify(receipt,report_bytes,facts)

    def test_receipt_artifact_wrong_workflow_run_reviewer_or_digest_blocks(self):
        for change in ('workflow','run','reviewer','expired','digest'):
            receipt,report,facts=fixture()
            if change=='workflow': facts['receipt_run']['workflow_id']=33
            if change=='run': facts['artifact']['workflow_run']['id']=404
            if change=='reviewer': facts['receipt_run']['actor']['login']='other'
            if change=='expired': facts['artifact']['expired']=True
            if change=='digest': report+=b' '
            with self.subTest(change=change), self.assertRaises(ValueError): self.verify(receipt,report,facts)

    def test_live_boundary_binds_bytes_and_rejects_race_or_wrong_digest(self):
        self.assertTrue(self.exists, 'publication receipt verifier is missing')
        for mode in ('valid','receipt_pin','bundle_digest','archive_bytes','rerun','missing_artifact'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temp:
                archive = Path(temp)/'candidate.zip'
                archive.write_bytes(b'synthetic candidate bytes')
                archive_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
                receipt, report_raw, facts = fixture()
                receipt['archive_sha256'] = archive_hash
                report = json.loads(report_raw)
                report['candidate'] = dict.fromkeys(report['candidate'], archive_hash)
                report_raw = json.dumps(report).encode()
                receipt['independent_evaluator']['report_sha256'] = hashlib.sha256(report_raw).hexdigest()
                raw = json.dumps(receipt).encode()
                pinned = hashlib.sha256(raw).hexdigest()
                buffer = io.BytesIO()
                with zipfile.ZipFile(buffer,'w') as zipped:
                    zipped.writestr('receipt.json',raw)
                    zipped.writestr('independent-evaluator.json',report_raw)
                bundle = buffer.getvalue()
                artifact = facts['artifact']
                artifact.update(id=303,size_in_bytes=len(bundle),digest='sha256:'+hashlib.sha256(bundle).hexdigest())
                if mode=='receipt_pin': pinned='e'*64
                if mode=='bundle_digest': artifact['digest']='sha256:'+'e'*64
                if mode=='archive_bytes': archive.write_bytes(b'tampered')
                # GitHub jobs do not guarantee run_attempt per job. The attempt
                # is bound by the requested /attempts/2/jobs API route itself.
                for job in facts['jobs']: job.pop('run_attempt')
                routes = {
                    'runs/202':facts['receipt_run'],
                    'runs/202/artifacts?per_page=100':dict(total_count=0 if mode=='missing_artifact' else 1,
                                                        artifacts=[] if mode=='missing_artifact' else [artifact]),
                    'artifacts/303/zip':bundle,
                    'runs/101':facts['ci_run'],
                    'runs/101/attempts/2/jobs?per_page=100':dict(total_count=7,jobs=facts['jobs']),
                    'workflows/self-tests.yml':facts['ci_workflow'],
                    'workflows/capture-release-receipt.yml':facts['receipt_workflow']}
                ci_requests = []
                def api(path,binary=False):
                    prefix='repos/example/skill/actions/'
                    if not path.startswith(prefix): raise AssertionError('unexpected API origin')
                    key=path[len(prefix):]
                    if key not in routes: raise AssertionError('unexpected API route')
                    if key=='runs/101':
                        ci_requests.append(key)
                        if mode=='rerun' and len(ci_requests)==2:
                            return dict(facts['ci_run'],run_attempt=3,status='in_progress',conclusion=None)
                    return routes[key]
                kwargs=dict(repository='example/skill',release_tag='v3.0.0',commit=COMMIT,
                            archive=archive,receipt_run_id=202,receipt_sha256=pinned,api=api)
                if mode=='valid':
                    self.assertTrue(self.module.fetch_and_verify(**kwargs)['publication_allowed'])
                else:
                    with self.assertRaises(ValueError): self.module.fetch_and_verify(**kwargs)


if __name__ == '__main__':
    unittest.main()
