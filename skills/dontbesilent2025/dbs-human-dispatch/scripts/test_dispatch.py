#!/usr/bin/env python3
"""Offline tests: no employee data, network calls or actual Agent invocation."""
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('dispatch', Path(__file__).with_name('dispatch.py'))
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)

class QueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db = runtime.connect(self.root)
        self.cfg = dict(runtime.DEFAULT_CONFIG, debounce_seconds=0)
        self.record = {'id': 'test-1', 'owner': 'Test owner', 'assignee': 'Test worker',
                       'goal': 'Produce a draft', 'deliverables': ['draft'], 'acceptance': ['has evidence'],
                       'due': '待协商', 'timezone': 'Asia/Shanghai', 'feedback': 'document',
                       'authorization': 'offline testing only', 'materials': [],
                       'mode': 'automatic', 'doc_token': 'docTest', 'state': 'assigned'}
        self.db.execute('INSERT INTO tasks VALUES(?,?,?)', ('test-1', 'docTest', json.dumps(self.record)))
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def event(self, ident='e1', doc='docTest', operator='employee'):
        return {'header': {'event_id': ident, 'event_type': 'drive.file.edit_v1', 'token': 'DO_NOT_STORE'},
                'event': {'file_token': doc, 'operator_id_list': [{'open_id': operator}]}}

    def test_dedup_and_coalesce_without_secret(self):
        first = runtime.ingest(self.db, self.cfg, self.event())
        self.assertEqual(runtime.ingest(self.db, self.cfg, self.event()), {'duplicate': 'e1'})
        self.assertEqual(runtime.ingest(self.db, self.cfg, self.event('e2'))['queued'], first['queued'])
        self.assertEqual(self.db.execute('SELECT count(*) FROM jobs').fetchone()[0], 1)
        self.assertNotIn('DO_NOT_STORE', self.db.execute('SELECT data FROM events').fetchone()[0])

    def test_unknown_self_and_inactive_are_ignored(self):
        self.assertEqual(runtime.ingest(self.db, self.cfg, self.event(doc='unknown'))['ignored'], 'unregistered_document')
        self.cfg['self_open_ids'] = ['bot']
        self.assertEqual(runtime.ingest(self.db, self.cfg, self.event(operator='bot'))['ignored'], 'self_edit')
        self.record['state'] = 'passed'
        self.db.execute('UPDATE tasks SET data=?', (json.dumps(self.record),))
        self.db.commit()
        self.assertEqual(runtime.ingest(self.db, self.cfg, self.event())['ignored'], 'inactive_task')

    def test_mixed_edit_is_not_dropped(self):
        self.cfg['self_open_ids'] = ['bot']
        event = self.event(operator='bot')
        event['event']['operator_id_list'].append({'open_id': 'employee'})
        self.assertIn('queued', runtime.ingest(self.db, self.cfg, event))

    def test_worker_missing_preserves_queue(self):
        runtime.ingest(self.db, self.cfg, self.event())
        with self.assertRaises(ValueError):
            runtime.dispatch(self.db, self.cfg, True, self.root)
        self.assertEqual(self.db.execute('SELECT state FROM jobs').fetchone()[0], 'pending')

    def test_real_subprocess_bridge_and_task_state_remains(self):
        runtime.ingest(self.db, self.cfg, self.event())
        self.cfg['agent_command'] = [sys.executable, '-c',
            'import sys,json; job=json.load(sys.stdin); assert job["task"]["id"]=="test-1"; print(json.dumps({"status":"processed","summary":"Offline job handled","receipts":[]}))']
        out = runtime.dispatch(self.db, self.cfg, True, self.root)
        self.assertEqual(out['state'], 'processed')
        self.assertEqual(runtime.task(self.db, 'test-1')['state'], 'assigned')

    def test_async_ack_is_uncertain_and_blocks_later_work(self):
        runtime.ingest(self.db, self.cfg, self.event())
        self.cfg['agent_command'] = [sys.executable, '-c', 'print("{\\"status\\":\\"accepted\\"}")']
        self.assertEqual(runtime.dispatch(self.db, self.cfg, True, self.root)['state'], 'uncertain')
        runtime.ingest(self.db, self.cfg, self.event('e2'))
        self.assertEqual(runtime.dispatch(self.db, self.cfg, True, self.root)['waiting'], 'no_ready_job')

    def test_failed_worker_never_retries_automatically(self):
        runtime.ingest(self.db, self.cfg, self.event())
        self.cfg['agent_command'] = [sys.executable, '-c', 'import sys; sys.exit(1)']
        self.assertEqual(runtime.dispatch(self.db, self.cfg, True, self.root)['state'], 'uncertain')
        self.assertEqual(runtime.dispatch(self.db, self.cfg, True, self.root)['waiting'], 'no_ready_job')

    def test_second_connection_observes_worker_lock(self):
        runtime.ingest(self.db, self.cfg, self.event())
        self.db.execute("UPDATE jobs SET state='running'")
        self.db.commit()
        other = runtime.connect(self.root)
        self.cfg['agent_command'] = [sys.executable, '-c', 'raise RuntimeError("must not run")']
        try:
            self.assertEqual(runtime.dispatch(other, self.cfg, True, self.root)['waiting'], 'another_worker_running')
        finally:
            other.close()

    def test_required_fields_and_state_boundaries(self):
        runtime.validate_task(self.record)
        del self.record['acceptance']
        with self.assertRaises(ValueError):
            runtime.validate_task(self.record)
        self.assertNotIn('passed', runtime.TRANSITIONS['draft'])
        self.assertNotIn('passed', runtime.TRANSITIONS['assigned'])

    def test_cancelled_task_queue_does_not_call_worker(self):
        runtime.ingest(self.db, self.cfg, self.event())
        self.record['state'] = 'cancelled'
        self.db.execute('UPDATE tasks SET data=?', (json.dumps(self.record),))
        self.db.commit()
        self.cfg['agent_command'] = [sys.executable, '-c', 'raise RuntimeError("must not run")']
        self.assertEqual(runtime.dispatch(self.db, self.cfg, True, self.root)['waiting'], 'no_ready_job')
        self.assertEqual(self.db.execute('SELECT state FROM jobs').fetchone()[0], 'processed')

if __name__ == '__main__':
    unittest.main()
