"""Local synthetic boundary tests, never evidence of successful model behavior."""
import copy
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_fixtures as build
import check_results as check


class MeasuredQualityTests(unittest.TestCase):
    def test_only_explicit_observed_status_can_contribute_scores(self):
        from run_host_evals import make_record
        suite = build.build_suite()
        case = suite['grading'][0]
        card = check.score_audit.__globals__['example_scorecard'](suite['contract'])
        card['evidence'][0]['source'] = 'target/SKILL.md'
        card['evidence'][0]['observation'] = build.BASE.splitlines()[2]
        record = make_record(case, dict(model='synthetic', model_version='synthetic', duration_seconds=1,
            isolation={'status': 'Verified', 'evidence': 'synthetic unit test only'}),
            [{'type': 'turn.completed'}], [], json.dumps(card))
        self.assertEqual(check.summarize(suite, [record])['sessions'][0]['outcome'], 'Pass')
        for status in (None, 'Failed', '', True):
            with self.subTest(status=status):
                changed = copy.deepcopy(record)
                if status is None:
                    changed.pop('status')
                else:
                    changed['status'] = status
                result = check.summarize(suite, [changed])
                self.assertEqual(result['outcome'], 'Fail')
                self.assertEqual(result['spread'], [])
                self.assertFalse(any(row['outcome'] == 'Pass' for row in result['sessions']))

    def test_neutral_rejects_invalid_frozen_protocol_values(self):
        import check_outcomes as neutral
        for key, value in (('model', None), ('model', ' '), ('prompt_hash', None), ('prompt_hash', 'x'),
                           ('max_output_tokens', 0), ('max_output_tokens', True), ('max_output_tokens', 1.5),
                           ('tools', None), ('tools', 'none'), ('reading_policy', None), ('reading_policy', '')):
            with self.subTest(field=key, value=value):
                suite = neutral.example_suite()
                suite['protocol'][key] = value
                suite['frozen_hash'] = neutral.frozen_hash(suite)
                with self.assertRaises(ValueError):
                    neutral.summarize(suite, [])

    def test_ablation_label_and_fixed_reading_set(self):
        suite = build.build_suite()
        self.assertEqual({c['condition'] for c in suite['grading']}, {'rubric-only', 'with-skill'})
        self.assertIn('fixed-context', suite['grading_context']['label'])
        self.assertNotIn('skill-forge/references/release-report-template.md', suite['grading_context']['reading_set'])
        self.assertLess(len(suite['grading_context']['reading_set']), 8)

    def test_baseline_failure_is_not_candidate_failure_and_pairs_are_reported(self):
        from run_host_evals import make_record
        suite = build.build_suite()
        records = []
        for case in suite['grading']:
            metadata = dict(model='synthetic', model_version='synthetic', duration_seconds=1,
                            isolation={'status': 'Verified', 'evidence': 'mock-only'})
            records.append(make_record(case, metadata, [{'type': 'turn.completed', 'usage': {'input_tokens': 10, 'output_tokens': 2}}], [], case['condition']))
        def grade(case, scorecard, contract):
            return {'outcome': 'Fail' if case['condition'] == 'rubric-only' else 'Pass', 'score': 80 if case['condition'] == 'rubric-only' else 90, 'reasons': []}
        # Synthetic computed scores exercise aggregation only.
        with patch.object(check, 'check_grade', grade):
            result = check.summarize(suite, records)
        self.assertEqual(result['baseline_outcome'], 'Fail')
        # Equal candidate scores violate ranking; test candidate failures remain explicit.
        self.assertEqual(result['candidate_outcome'], 'Fail')
        self.assertEqual(result['paired_differences'][0]['mean_difference'], 10)
        suite['expectations']['ranking_pairs'] = []
        suite['expectations_hash'] = check.digest(suite['expectations'])
        with patch.object(check, 'check_grade', grade):
            result = check.summarize(suite, records)
        self.assertEqual(result['candidate_outcome'], 'Not Assessed')  # behavior absent
        self.assertEqual(result['outcome'], 'Not Assessed')
        self.assertEqual(result['resource_usage']['with-skill']['duration_seconds'], 12)

    def test_api_success_and_http_failure_are_not_confused(self):
        import run_api_evals as api
        case = build.build_suite()['grading'][0]
        calls = []
        payload = {'status': 'completed', 'id': 'mock-response', 'model': 'mock-model',
                   'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': '{}'}]}],
                   'usage': {'input_tokens': 20, 'output_tokens': 2}}
        def fake(request, timeout):
            calls.append((request, timeout))
            return io.BytesIO(json.dumps(payload).encode())
        record = api.run_case(case, 'explicit-model', 200, 3, 'synthetic-key', opener=fake, evidence_kind='mock transport test')
        self.assertEqual(record['status'], 'Not Assessed')
        self.assertEqual(record['transport_status'], 'completed')
        sent = json.loads(calls[0][0].data)
        self.assertEqual(sent['tools'], [])
        self.assertEqual(sent['tool_choice'], 'none')
        self.assertFalse(sent['store'])
        self.assertEqual(sent['max_output_tokens'], 200)
        self.assertEqual(calls[0][1], 3)
        self.assertNotIn('synthetic-key', json.dumps(record))
        def fail(request, timeout):
            raise HTTPError(request.full_url, 429, 'private body must not leak', {}, None)
        failed = api.run_case(case, 'model', 200, 3, 'synthetic-key', opener=fail)
        self.assertEqual(failed['status'], 'Not Assessed')
        self.assertIn('429', failed['reason'])
        self.assertNotIn('private body', json.dumps(failed))

    def test_api_missing_key_timeout_incomplete_tools_and_malformed(self):
        import run_api_evals as api
        case = build.build_suite()['grading'][0]
        def forbidden(*args, **kwargs): self.fail('missing key must never send a request')
        self.assertEqual(api.run_case(case, 'model', 200, 2, None, opener=forbidden)['status'], 'Not Assessed')
        def timeout(*args, **kwargs): raise TimeoutError('secret context')
        self.assertEqual(api.run_case(case, 'model', 200, 2, 'test', opener=timeout)['status'], 'Not Assessed')
        for payload in ({'status': 'incomplete'}, {'status': 'completed', 'output': [{'type': 'function_call'}]}, [], {'status': 'completed', 'output': 'bad'}):
            result = api.run_case(case, 'model', 200, 2, 'test', opener=lambda *a, **k: io.BytesIO(json.dumps(payload).encode()))
            self.assertEqual(result['status'], 'Not Assessed')
        case['prompt'] = 'arbitrary custom text'
        with self.assertRaises(ValueError): api.validate_suite({'grading': [case]})

    def test_api_cli_missing_environment_key_is_bounded_and_truthful(self):
        import contextlib
        import os
        import tempfile
        import run_api_evals as api
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            suite_path, results_path = root / 'suite.json', root / 'results.jsonl'
            suite_path.write_text(json.dumps(build.build_suite()), encoding='utf-8')
            argv = ['run_api_evals.py', '--suite', str(suite_path), '--results', str(results_path),
                    '--model', 'explicit-test-model', '--max-requests', '2', '--max-output-tokens', '100']
            with patch.dict(os.environ, {}, clear=True), patch.object(sys, 'argv', argv), patch.object(api, 'open_request') as transport:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(api.main(), 2)
                transport.assert_not_called()
                rows = [json.loads(x) for x in results_path.read_text().splitlines()]
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]['status'], 'Not Assessed')
                self.assertIn('no request sent', rows[0]['reason'])
                with self.assertRaises(FileExistsError): api.main()
            tampered = build.build_suite()
            tampered['grading'][0]['prompt'] += 'changed'
            with self.assertRaises(ValueError): api.validate_suite(tampered)

    def test_api_cli_observed_grade_failure_and_safety_return_nonzero(self):
        import contextlib
        import tempfile
        import run_api_evals as api
        for safety in (False, True):
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                suite_path = root / 'suite.json'
                suite_path.write_text(json.dumps(build.build_suite()), encoding='utf-8')
                argv = ['run_api_evals.py', '--suite', str(suite_path), '--results', str(root / 'results.jsonl'),
                        '--model', 'synthetic-test', '--max-requests', '1', '--max-output-tokens', '100']
                def fake_case(case, *args):
                    # Test fabricated controller record only, never a model success claim.
                    record = api_record(case)
                    if safety: record['transport_violations'] = ['unexpected tool']
                    return record
                def api_record(case):
                    from run_host_evals import make_record
                    return make_record(case, dict(model='synthetic', model_version='synthetic', duration_seconds=1,
                        isolation={'status': 'Verified', 'evidence': 'synthetic unit test only'}),
                        [{'type': 'turn.completed'}], [], '{}')
                with patch.object(sys, 'argv', argv), patch.object(api, 'run_case', fake_case):
                    captured = io.StringIO()
                    with contextlib.redirect_stdout(captured): self.assertEqual(api.main(), 1)
                    self.assertEqual(json.loads(captured.getvalue())['api_grading_assessment'], 'Fail')

    def test_neutral_metrics_bind_labels_cases_and_conditions(self):
        import check_outcomes as neutral
        suite = neutral.example_suite()
        self.assertEqual(neutral.summarize(suite, [])['comparison'], 'Not Assessed')
        self.assertIsNone(neutral.summarize(suite, [])['conditions']['current']['severe_misses'])
        suite['labels']['status'] = 'independently-reviewed'
        suite['labels']['reviewer'] = 'synthetic-test-reviewer'
        suite['labels']['evidence'] = 'synthetic fixture only'
        suite['frozen_hash'] = neutral.frozen_hash(suite)
        records = []
        for condition in ('current', 'baseline'):
            records.append(dict(case_id='synthetic-example', case_hash=suite['cases'][0]['case_hash'],
                condition=condition, condition_hash=suite['conditions'][condition], suite_hash=suite['frozen_hash'],
                model=suite['protocol']['model'], prompt_hash=suite['protocol']['prompt_hash'],
                matching_review={'reviewer': 'synthetic matcher', 'evidence': 'synthetic test only', 'output_sha256': neutral.digest('synthetic output')},
                status='Observed', findings=['missing-input'] if condition == 'current' else ['false-positive'],
                duration_seconds=2, token_usage={'input_tokens': 10, 'output_tokens': 5}))
        result = neutral.summarize(suite, records)
        self.assertEqual(result['conditions']['current']['precision'], 1)
        self.assertEqual(result['conditions']['baseline']['recall'], 0)
        self.assertEqual(result['conditions']['baseline']['severe_misses'], 1)
        self.assertEqual(result['paired_differences'][0]['recall_difference'], 1)
        self.assertEqual(result['comparison'], 'Not Assessed')  # single synthetic pair cannot establish superiority
        bad = copy.deepcopy(records)
        bad[0]['case_hash'] = 'changed'
        with self.assertRaises(ValueError): neutral.summarize(suite, bad)
        bad = copy.deepcopy(records)
        bad[0]['model'] = 'different model'
        with self.assertRaises(ValueError): neutral.summarize(suite, bad)
        bad = copy.deepcopy(records)
        bad[0]['duration_seconds'] = float('nan')
        with self.assertRaises(ValueError): neutral.summarize(suite, bad)
        for invalid_hash in ('x', True, 'g' * 64):
            bad = copy.deepcopy(records)
            bad[0]['matching_review']['output_sha256'] = invalid_hash
            with self.subTest(output_sha256=invalid_hash), self.assertRaises(ValueError):
                neutral.summarize(suite, bad)
        bad = copy.deepcopy(suite)
        bad['cases'][0]['artifact'] = 'changed'
        with self.assertRaises(ValueError): neutral.summarize(bad, records)


if __name__ == '__main__':
    unittest.main()
