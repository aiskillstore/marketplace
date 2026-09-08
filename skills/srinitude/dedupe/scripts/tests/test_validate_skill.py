"""Regression tests for native user-local skill metadata."""
import unittest

from scripts import validate_skill


class TestFrontmatterMetadata(unittest.TestCase):
    def test_version_and_author_are_allowed(self):
        fields = {"name": "dedupe", "description": "Use when testing.",
                  "version": "1.0.0", "author": "Kiren Srinivasan"}
        problems = []
        validate_skill.check_fields(fields, "dedupe", problems)
        self.assertEqual(problems, [])

    def test_unknown_field_stays_rejected(self):
        fields = {"name": "dedupe", "description": "Use when testing.",
                  "startup_command": "do-not-run"}
        problems = []
        validate_skill.check_fields(fields, "dedupe", problems)
        self.assertIn("unknown top-level frontmatter field: startup_command",
                      problems)

    def test_description_rejects_sixty_characters(self):
        fields = {"name": "dedupe", "description": "Use when " + "x" * 51}
        problems = []
        validate_skill.check_fields(fields, "dedupe", problems)
        self.assertIn("description must be 1 to 59 characters", problems)


if __name__ == "__main__":
    unittest.main()
