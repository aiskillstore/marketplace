"""Deterministic checks; no model calls or target execution."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent

def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    item = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(item)
    return item

class HarnessTests(unittest.TestCase):
    def test_source_harness_exists(self):
        self.assertTrue((HERE / 'fixture_server.py').is_file(), 'bounded fixture adapter is absent')

    def test_fixture_count_and_frozen_relationships(self):
        if not (HERE / 'build_fixtures.py').exists(): self.fail('fixture generator absent')
        build = module('build_fixtures')
        suite = build.build_suite()
        self.assertEqual(len(suite['behavior']), 12)
        self.assertEqual(len(suite['grading']), 24)
        self.assertEqual(suite['expectations']['ranking_pairs'], [['excellent', 'strong'], ['excellent', 'poor'], ['excellent', 'unsafe'], ['strong', 'poor']])
        self.assertEqual(len({x['id'] for x in suite['behavior'] + suite['grading']}), 36)

    def test_denied_access_and_writes_are_recorded_failures(self):
        if not (HERE / 'fixture_server.py').exists(): self.fail('fixture adapter absent')
        build, server, check = (module(x) for x in ('build_fixtures', 'fixture_server', 'check_results'))
        fixture = build.build_suite()['behavior'][0]
        with tempfile.TemporaryDirectory() as d:
            adapter = server.Adapter(fixture, Path(d) / 'trace.jsonl')
            result = adapter.call('fixture_read', {'path': '../unrelated'})
            self.assertTrue(result['isError'])
            adapter.call('fixture_write', {'path': 'target/SKILL.md', 'content': 'changed'})
            adapter.close()
            trace = [json.loads(x) for x in (Path(d) / 'trace.jsonl').read_text(encoding="utf-8").splitlines()]
            outcome = check.check_behavior(fixture, trace, '')
            self.assertEqual(outcome['safety'], 'Fail')
            self.assertEqual(adapter.files, fixture['files'])

    def test_repair_requires_traced_later_authorization(self):
        if not (HERE / 'fixture_server.py').exists(): self.fail('fixture adapter absent')
        build, server = module('build_fixtures'), module('fixture_server')
        fixture = next(x for x in build.build_suite()['behavior'] if x['id'] == 'later-repair')
        with tempfile.TemporaryDirectory() as d:
            adapter = server.Adapter(fixture, Path(d) / 'trace.jsonl')
            self.assertTrue(adapter.call('fixture_write', {'path': 'target/SKILL.md', 'content': 'x'})['isError'])
            adapter.call('fixture_user_input', {})
            self.assertFalse(adapter.call('fixture_write', {'path': 'target/SKILL.md', 'content': 'fixed'})['isError'])
            self.assertTrue(adapter.call('fixture_write', {'path': 'skill-forge/SKILL.md', 'content': 'x'})['isError'])
            adapter.close()

    def test_final_assertion_cannot_replace_trace(self):
        if not (HERE / 'check_results.py').exists(): self.fail('trace checker absent')
        build, check = module('build_fixtures'), module('check_results')
        fixture = build.build_suite()['behavior'][0]
        result = check.check_behavior(fixture, [], 'I read and validated everything; passed.')
        self.assertEqual(result['outcome'], 'Not Assessed')

    def test_missing_runs_not_passes(self):
        if not (HERE / 'check_results.py').exists(): self.fail('result checker absent')
        build, check = module('build_fixtures'), module('check_results')
        result = check.summarize(build.build_suite(), [])
        self.assertEqual(result['outcome'], 'Not Assessed')
        self.assertEqual(result['sessions_recorded'], 0)

    def test_truncated_trace_preserves_safety_failure(self):
        build, check = module('build_fixtures'), module('check_results')
        result = check.check_behavior(build.build_suite()['behavior'][0], [{'type': 'tool', 'denied': True}], '')
        self.assertEqual(result['safety'], 'Fail')

    def test_tampered_filesystem_cannot_pass(self):
        build, server, check = (module(x) for x in ('build_fixtures', 'fixture_server', 'check_results'))
        fixture = build.build_suite()['behavior'][0]
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'trace.jsonl'
            adapter = server.Adapter(fixture, path)
            adapter.call('fixture_read', {'path': 'skill-forge/SKILL.md'})
            adapter.call('fixture_read', {'path': 'target/SKILL.md'})
            adapter.call('fixture_report', {'findings': [], 'validator_result': 'Not Assessed', 'runtime_executed': False, 'release_verdict': 'Not Assessed'})
            adapter.close()
            trace = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(check.check_behavior(fixture, trace, '')['outcome'], 'Pass')
            trace[-1]['files']['target/SKILL.md'] = 'fabricated'
            self.assertEqual(check.check_behavior(fixture, trace, '')['outcome'], 'Fail')

    def test_grading_calculator_rejects_fabricated_evidence_and_blocks_unsafe(self):
        build, check = module('build_fixtures'), module('check_results')
        suite = build.build_suite()
        card = check.score_audit.__globals__['example_scorecard'](suite['contract'])
        card['evidence'][0]['source'] = 'target/SKILL.md'
        card['evidence'][0]['observation'] = build.BASE.splitlines()[2]
        case = suite['grading'][0]
        self.assertEqual(check.check_grade(case, card, suite['contract'])['score'], 100)
        original = card['evidence'][0]['observation']
        card['evidence'][0]['observation'] = 'Invented observation absent from fixed artifact.'
        self.assertEqual(check.check_grade(case, card, suite['contract'])['outcome'], 'Fail')
        card['evidence'][0]['observation'] = original
        card['evidence'][0]['method'] = 'Live host observation'
        self.assertEqual(check.check_grade(case, card, suite['contract'])['outcome'], 'Fail')
        card['evidence'][0]['method'] = 'Static inspection'
        unsafe = next(c for c in suite['grading'] if c['anchor'] == 'unsafe')
        self.assertEqual(check.check_grade(unsafe, card, suite['contract'])['outcome'], 'Fail')

    def test_inspection_without_defect_report_cannot_pass(self):
        build, server, check = (module(x) for x in ('build_fixtures', 'fixture_server', 'check_results'))
        fixture = next(x for x in build.build_suite()['behavior'] if x['id'] == 'missing-link')
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'trace.jsonl'
            adapter = server.Adapter(fixture, path)
            adapter.call('fixture_read', {'path': 'skill-forge/SKILL.md'})
            adapter.call('fixture_read', {'path': 'target/SKILL.md'})
            adapter.call('fixture_inspect', {'path': 'target/SKILL.md'})
            adapter.close()
            trace = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(check.check_behavior(fixture, trace, 'Everything passes')['outcome'], 'Fail')

    def test_changed_frozen_expectations_rejected(self):
        build, check = module('build_fixtures'), module('check_results')
        suite = build.build_suite()
        suite['expectations']['maximum_spread'] = 99
        self.assertEqual(check.summarize(suite, [])['outcome'], 'Fail')

    def test_unknown_and_incomplete_transport_fail_closed(self):
        import sys
        sys.path.insert(0, str(HERE))
        runner = module('run_host_evals')
        self.assertTrue(runner.transport_violations([{'type': 'item.completed', 'item': {'type': 'new_native_tool'}}], 'behavior'))
        case = module('build_fixtures').build_suite()['behavior'][0]
        record = runner.make_record(case, dict(model='test-model', model_version='test-version', duration_seconds=1, isolation={'status': 'Verified', 'evidence': 'synthetic test'}), [], [], '')
        self.assertEqual(record['status'], 'Not Assessed')

    def test_stdio_protocol_uses_only_virtual_files(self):
        import subprocess
        import sys
        fixture = module('build_fixtures').build_suite()['behavior'][0]
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'fixture.json').write_text(json.dumps(fixture), encoding="utf-8")
            requests = [
                {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2024-11-05'}},
                {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'},
                {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {'name': 'fixture_read', 'arguments': {'path': 'target/SKILL.md'}}},
                {'jsonrpc': '2.0', 'id': 4, 'method': 'tools/call', 'params': {'name': 'execute_target', 'arguments': {'command': 'forbidden'}}}]
            clean_env = {'PYTHONIOENCODING': 'utf-8'}
            if os.name == 'nt':
                clean_env['SystemRoot'] = os.environ['SystemRoot']
            proc = subprocess.run([sys.executable, '-S', str(HERE / 'fixture_server.py'), '--fixture', str(root / 'fixture.json'), '--trace', str(root / 'trace.jsonl')],
                                  input=''.join(json.dumps(x)+'\n' for x in requests), text=True, encoding='utf-8', capture_output=True, env=clean_env, timeout=10)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            replies = [json.loads(x) for x in proc.stdout.splitlines()]
            self.assertEqual(len(replies), 4)
            self.assertFalse(replies[2]['result']['isError'])
            self.assertTrue(replies[3]['result']['isError'])
            trace = [json.loads(x) for x in (root / 'trace.jsonl').read_text(encoding="utf-8").splitlines()]
            self.assertEqual(trace[0]['files'], trace[-1]['files'])
            self.assertEqual(trace[-1]['type'], 'end')

    def test_retained_safety_dominates_incomplete_and_missing_metadata(self):
        import sys
        sys.path.insert(0, str(HERE))
        build, check, runner = (module(x) for x in ('build_fixtures', 'check_results', 'run_host_evals'))
        suite = build.build_suite()
        metadata = dict(model='test', model_version='test', duration_seconds=1, isolation={'status': 'Verified', 'evidence': 'synthetic'})
        marker = '-----BEGIN ' + 'PRIVATE KEY-----'
        for case in (suite['behavior'][0], suite['grading'][0]):
            for scenario in ('failed', 'unverified', 'missing'):
                record = runner.make_record(case, metadata, [{'type': 'turn.failed'}], [], marker)
                if scenario == 'unverified': record['isolation'] = {'status': 'Not Assessed'}
                if scenario == 'missing': del record['model']
                report = check.summarize(suite, [record])
                self.assertEqual(report['outcome'], 'Fail', scenario)
                self.assertTrue(report['stop_required'], scenario)
                with self.assertRaises(ValueError): runner.next_case(suite, [record])
        for evidence in ({'transport_violations': ['unknown native tool']}, {'tool_trace': [{'denied': True}]}):
            report = check.summarize(suite, [dict(case_id='explicit', **evidence)])
            self.assertTrue(report['stop_required'])

    def test_candidate_identity_required_including_null_control(self):
        import sys
        sys.path.insert(0, str(HERE))
        build, check, runner = (module(x) for x in ('build_fixtures', 'check_results', 'run_host_evals'))
        suite = build.build_suite()
        metadata = dict(model='Not run', model_version='Not available', duration_seconds=0, isolation={'status': 'Not Assessed'})
        for case in (suite['behavior'][0], suite['grading'][0]):
            record = runner.make_record(case, metadata, [], [], '')
            self.assertEqual(check.summarize(suite, [record])['outcome'], 'Not Assessed')
            record['candidate_hash'] = 'wrong'
            self.assertEqual(check.summarize(suite, [record])['outcome'], 'Fail')
            del record['candidate_hash']
            self.assertEqual(check.summarize(suite, [record])['outcome'], 'Fail')

    def test_draft_requires_scoped_report_and_no_package_claim(self):
        build, server, check = (module(x) for x in ('build_fixtures', 'fixture_server', 'check_results'))
        fixture = next(c for c in build.build_suite()['behavior'] if c['id'] == 'draft-only')
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'trace.jsonl'
            adapter = server.Adapter(fixture, path)
            adapter.call('fixture_read', {'path': 'skill-forge/SKILL.md'})
            adapter.close()
            trace = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(check.check_behavior(fixture, trace, 'Package and runtime verified successfully.')['outcome'], 'Fail')
        self.assertIn('draft/SKILL.md', fixture['files'])
        for package_verified in (False, True):
            with tempfile.TemporaryDirectory() as d:
                path = Path(d) / 'trace.jsonl'
                adapter = server.Adapter(fixture, path)
                adapter.call('fixture_read', {'path': 'skill-forge/SKILL.md'})
                adapter.call('fixture_read', {'path': 'draft/SKILL.md'})
                result = adapter.call('fixture_report', dict(findings=[], validator_result='Not Assessed', runtime_executed=False,
                    release_verdict='Not Assessed', assessment_scope='draft', package_verified=package_verified))
                adapter.close()
                trace = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()]
                self.assertEqual(result['isError'], package_verified)
                self.assertEqual(check.check_behavior(fixture, trace, '')['outcome'], 'Fail' if package_verified else 'Pass')

class StreamliningTests(unittest.TestCase):
    def load_runtime(self, name):
        import sys
        path = HERE.parent / 'scripts' / (name + '.py')
        sys.path.insert(0, str(path.parent))
        spec = importlib.util.spec_from_file_location(name, path)
        item = importlib.util.module_from_spec(spec)
        sys.modules[name] = item
        spec.loader.exec_module(item)
        return item

    def test_description_length_and_language_are_not_findings(self):
        inspector = self.load_runtime('inspect_skill_package')
        cases = json.loads((HERE / 'description-cases.json').read_text(encoding="utf-8"))
        self.assertEqual(len(cases), 4)
        for case in cases:
            with self.subTest(case=case['id']):
                findings = inspector.validate_frontmatter({'name': 'sample', 'description': case['description']})
                self.assertFalse(findings, findings)
        for value in ('', None, 23):
            self.assertTrue(inspector.validate_frontmatter({'name': 'sample', 'description': value}))
        self.assertTrue(inspector.validate_frontmatter({'name': 'sample', 'description': '<tag>bad</tag>'}))

    def test_control_plane_reflow_passes_safety_mutations_fail(self):
        from unittest.mock import patch
        validator = self.load_runtime('validate_audit_contract')
        original = validator.SKILL_PATH.read_text(encoding="utf-8")
        # Reflow prose while preserving headings/frontmatter/role paragraphs.
        reflowed = '\n\n'.join(' '.join(block.splitlines()) if not block.startswith(('---', '#')) else block for block in original.split('\n\n'))
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'SKILL.md'
            with patch.object(validator, 'SKILL_PATH', path):
                path.write_text(reflowed, encoding="utf-8")
                issues = []
                validator.validate_skill_control_plane(issues)
                self.assertEqual(issues, [])
                for phrase in ('untrusted evidence only', 'source read-only', 'scratch-only writes', 'affirmative directive', 'package self-test evidence', 'G01–G23 matrix'):
                    with self.subTest(phrase=phrase):
                        path.write_text(reflowed.replace(phrase, 'removed'), encoding="utf-8")
                        issues = []
                        validator.validate_skill_control_plane(issues)
                        self.assertTrue(issues)
                path.write_text(reflowed + ' filler' * 1100, encoding="utf-8")
                issues = []
                validator.validate_skill_control_plane(issues)
                self.assertTrue(any('budget' in x for x in issues))

    def test_pressure_reporting_caps_are_legacy_only(self):
        text = (HERE.parent / 'references/pressure-test-suite.md').read_text(encoding="utf-8")
        for title in ('A Critical issue is supported by evidence', 'A High issue remains unresolved'):
            row = next(line for line in text.splitlines() if line.startswith('| ' + title + ' |'))
            self.assertIn('legacy projection', row)
            self.assertIn('quality score', row)

    def test_release_extension_missing_gate_is_rejected(self):
        import re
        from unittest.mock import patch
        validator = self.load_runtime('validate_audit_contract')
        contract = json.loads((HERE.parent / 'references/audit-contract.json').read_text(encoding="utf-8"))
        original_read = validator.read_text
        def mutated_read(path, issues):
            text = original_read(path, issues)
            if path.name == 'release-report-template.md':
                return re.sub(r'^\| G12 \|.*\n', '', text, flags=re.MULTILINE)
            return text
        with patch.object(validator, 'read_text', mutated_read):
            issues = []
            validator.validate_documents(contract, issues)
        self.assertTrue(any('release-report-template.md' in x and 'matrix' in x for x in issues), issues)

    def test_standard_load_excludes_release_provenance_and_matrix(self):
        refs = HERE.parent / 'references'
        standard = (refs / 'report-template.md').read_text(encoding="utf-8")
        validator = (refs / 'validator-evidence.md').read_text(encoding="utf-8")
        skill = (HERE.parent / 'SKILL.md').read_text(encoding="utf-8")
        self.assertIn('## Decision', standard)
        self.assertIn('## Evidence', standard)
        self.assertLess(standard.index('## Decision'), standard.index('## Evidence'))
        self.assertNotIn('| G01 |', standard)
        self.assertNotIn('bootstrap_transition', standard + validator + skill)
        release = (refs / 'release-report-template.md').read_text(encoding="utf-8")
        for i in range(1, 24):
            self.assertEqual(release.count('| G%02d |' % i), 1)
        provenance = (refs / 'release-evaluator-provenance.md').read_text(encoding="utf-8")
        self.assertIn('--bootstrap-schema-transition 5:6', provenance)
        self.assertIn('--bootstrap-release-tag v2.0.0', provenance)
        self.assertIn('not reusable after that release', provenance)
        for marker in ('Score scope', 'Evidence coverage', 'Next actions', 'observed_behavior', 'redacted_fingerprint'):
            self.assertIn(marker, standard)

if __name__ == '__main__':
    unittest.main()
