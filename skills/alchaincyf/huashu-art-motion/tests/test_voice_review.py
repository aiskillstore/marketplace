import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from voice_review import review_status


class ReviewTests(unittest.TestCase):
    def test_missing_corrupt_stale_future_and_fresh(self):
        with tempfile.TemporaryDirectory() as d:
            config = Path(d) / 'media.json'
            record = config.with_name('voice-model-review.json')
            now = datetime(2026, 10, 15, tzinfo=timezone.utc)
            def check():
                return review_status('qwen', 'requested-model', config, now)
            self.assertTrue(check()['needs_check'])
            record.write_text('invalid json')
            self.assertTrue(check()['needs_check'])
            for stamp, stale in [('2026-10-15T00:00:00+00:00', False),
                                 ('2026-10-08T00:00:00+00:00', True),
                                 ('2026-10-16T00:00:00+00:00', True),
                                 ('2026-10-15T00:00:00', True)]:
                record.write_text(json.dumps({'providers': {'qwen': {'checked_at': stamp}}}))
                self.assertEqual(check()['needs_check'], stale)
                self.assertEqual(check()['selected_model'], 'requested-model')
                self.assertTrue(review_status('volcengine', 'other', config, now)['needs_check'])


if __name__ == '__main__':
    unittest.main()
