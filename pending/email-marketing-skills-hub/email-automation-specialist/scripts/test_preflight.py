import unittest
from preflight import CHECKS, check

class PreflightTests(unittest.TestCase):
    def test_complete_is_only_checklist_pass(self):
        result = check(dict.fromkeys(CHECKS, True))
        self.assertTrue(result['checklist_complete'])
        self.assertIn('Not authorization', result['notice'])

    def test_empty_fails_closed(self):
        self.assertEqual(check({})['outstanding'], list(CHECKS))

    def test_each_gate_blocks(self):
        for key in CHECKS:
            with self.subTest(key=key):
                data = dict.fromkeys(CHECKS, True)
                data[key] = False
                self.assertEqual(check(data)['outstanding'], [key])

    def test_missing_gate_blocks(self):
        data = dict.fromkeys(CHECKS, True)
        del data['external_action_authorization_verified']
        self.assertFalse(check(data)['checklist_complete'])

    def test_no_truthy_shortcut(self):
        for value in ('true', 1, None, [], {}):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    check({'suppression_tested': value})

    def test_typo_rejected(self):
        with self.assertRaises(ValueError):
            check({'consent_looks_fine': True})

    def test_wrong_root_rejected(self):
        with self.assertRaises(ValueError):
            check([])

if __name__ == '__main__':
    unittest.main()
