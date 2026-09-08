"""Controller regressions; these never certify a real container backend."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch


class BoundedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / 'scripts/run_bounded_tests.py'
        sys.path.insert(0, str(path.parent))
        spec = importlib.util.spec_from_file_location('bounded_runner', path)
        cls.runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.runner)

    def plan(self, root):
        return dict(schema_version=1, source_root=str(root), source_files=['test.py'],
                    scratch_inputs=[], commands=[['python3', '-B', '-S', '/source/test.py']],
                    reviewed=True, network=False, wall_seconds=30, memory_mib=128,
                    process_limit=16, output_bytes=65536)

    def test_invalid_plans_cannot_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            plan = self.plan(root)
            self.runner.validate_plan(plan)
            for key, value in [('reviewed', False), ('network', True), ('wall_seconds', True),
                               ('memory_mib', 0), ('commands', ['echo unsafe']),
                               ('source_files', ['../outside']), ('source_files', ['.env']),
                               ('scratch_inputs', [{'source': 'test.py', 'destination': '../out'}])]:
                with self.subTest(key=key, value=value):
                    bad = dict(plan, **{key: value})
                    with self.assertRaises(ValueError): self.runner.validate_plan(bad)

    def test_unsupported_host_does_not_read_or_execute_target(self):
        with patch.object(self.runner.platform, 'system', return_value='Windows'), \
             patch.object(self.runner, 'copy_sources', side_effect=AssertionError('target read')):
            result = self.runner.execute(self.plan(Path.cwd() / 'synthetic-source'))
        self.assertEqual(result['outcome'], 'Not Assessed')
        self.assertFalse(result['target_launched'])

    def test_container_options_fix_security_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            options = self.runner.container_options('test-name', Path(directory), self.plan(Path(directory)))
        joined = ' '.join(options)
        for value in ('--network=none', '--read-only', '--cap-drop=ALL', '--pull=never',
                      '--security-opt=no-new-privileges', '--pids-limit=16', '--memory=128m',
                      '--memory-swap=128m', '--user=65534:65534', '--log-driver=none'):
            self.assertIn(value, options)
        self.assertIn('readonly', joined)
        self.assertIn('@sha256:', self.runner.IMAGE)

    @unittest.skipUnless(os.name == 'posix', 'POSIX source descriptor controls')
    def test_source_copy_rejects_symlinks_and_limits(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source = root / 'source'; source.mkdir()
            (source / 'test.py').write_text('print(1)', encoding="utf-8")
            dest = root / 'copy'; dest.mkdir()
            result = self.runner.copy_sources(self.plan(source), dest)
            self.assertEqual(set(result), {'test.py'})
            (source / 'link.py').symlink_to(source / 'test.py')
            with self.assertRaises((ValueError, OSError)):
                self.runner.copy_sources(dict(self.plan(source), source_files=['link.py']), dest)

    def test_failed_capability_prevents_targets(self):
        capability = dict(outcome='Not Assessed', supported=False, controls={}, reasons=['probe failed'])
        with patch.object(self.runner, 'probe', return_value=capability), \
             patch.object(self.runner, 'copy_sources', side_effect=AssertionError('target read')):
            result = self.runner.execute(self.plan(Path.cwd() / 'synthetic-source'))
        self.assertFalse(result['target_launched'])

    def test_outcomes_and_redaction(self):
        self.assertEqual(self.runner.classify(0, False), 'Pass')
        self.assertEqual(self.runner.classify(1, False), 'Artifact Fail')
        self.assertEqual(self.runner.classify(0, True), 'Execution Error')

    @unittest.skipUnless(os.name == 'posix', 'POSIX process controller')
    def test_controller_bounds_output_and_timeout(self):
        output = self.runner.invoke([sys.executable, '-I', '-c', 'print("x"*100000)'], output_limit=1024)
        self.assertTrue(output['output_limited'])
        self.assertLessEqual(len(output['text']), 1024)
        timeout = self.runner.invoke([sys.executable, '-I', '-c', 'import time;time.sleep(2)'], timeout=0.1)
        self.assertTrue(timeout['timed_out'])

    def test_container_cleanup_runs_after_timeout(self):
        responses = [dict(code=0, text='id', timed_out=False, output_limited=False),
                     dict(code=-9, text='', timed_out=True, output_limited=False),
                     dict(code=0, text='id'),
                     dict(code=0, text=json.dumps(dict(Status='exited', StartedAt='2026-09-06T00:00:00Z', Running=False, Error='', ExitCode=137, OOMKilled=False))),
                     dict(code=0, text='id'), dict(code=0, text='')]
        with patch.object(self.runner, 'invoke', side_effect=responses) as call:
            result = self.runner.container_run(['docker'], Path('/synthetic'), self.plan(Path('/synthetic')), 'pass')
        self.assertTrue(result['cleanup_verified'])
        self.assertTrue(any('kill' in item.args[0] for item in call.call_args_list))
        self.assertTrue(any('rm' in item.args[0] and '--force' in item.args[0] for item in call.call_args_list))

    def test_never_started_container_cannot_pass(self):
        responses = [dict(code=0, text='id', timed_out=False, output_limited=False),
                     dict(code=1, text='start transport failed', timed_out=False, output_limited=False),
                     dict(code=0, text=json.dumps(dict(Status='created', StartedAt='0001-01-01T00:00:00Z', Running=False, Error='', ExitCode=0))),
                     dict(code=0, text='id'), dict(code=0, text='')]
        with patch.object(self.runner, 'invoke', side_effect=responses):
            with self.assertRaises(RuntimeError):
                self.runner.container_run(['docker'], Path('/synthetic'), self.plan(Path('/synthetic')), 'pass')

    def test_target_failure_is_distinct_from_attach_failure(self):
        for client_code in (1, 125):
            responses = [dict(code=0, text='id', timed_out=False, output_limited=False),
                         dict(code=client_code, text='', timed_out=False, output_limited=False),
                         dict(code=0, text=json.dumps(dict(Status='exited', StartedAt='2026-09-06T00:00:00Z', Running=False, Error='', ExitCode=1, OOMKilled=False))),
                         dict(code=0, text='id'), dict(code=0, text='')]
            with self.subTest(client_code=client_code), patch.object(self.runner, 'invoke', side_effect=responses):
                if client_code == 1:
                    result = self.runner.container_run(['docker'], Path('/synthetic'), self.plan(Path('/synthetic')), 'pass')
                    self.assertEqual(self.runner.classify(result['code'], False), 'Artifact Fail')
                else:
                    with self.assertRaises(RuntimeError):
                        self.runner.container_run(['docker'], Path('/synthetic'), self.plan(Path('/synthetic')), 'pass')


if __name__ == '__main__':
    unittest.main()
