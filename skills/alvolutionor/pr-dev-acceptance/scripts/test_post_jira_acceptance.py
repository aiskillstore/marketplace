import unittest
import contextlib
import io
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import post_jira_acceptance as posting
from post_jira_acceptance import markdown_to_wiki


class MarkdownToWikiTests(unittest.TestCase):
    def test_converts_headings_tables_images_and_inline_marks(self):
        markdown = (
            '### Dev acceptance: PASS\n'
            '\n'
            '| What | Screenshot |\n'
            '|---|---|\n'
            '| Add **item** | ![](screenshots/a.png) |\n'
            '\n'
            '- Users `qa@example.invalid`, see [card](https://example.invalid/1)\n'
        )
        self.assertEqual(
            markdown_to_wiki(markdown, 'demo1-'),
            'h3. Dev acceptance: PASS\n'
            '\n'
            '||What||Screenshot||\n'
            '|Add *item*|!demo1-a.png|thumbnail!|\n'
            '\n'
            '* Users {{qa@example.invalid}}, see [card|https://example.invalid/1]\n',
        )


class PostingBoundaryTests(unittest.TestCase):
    def test_default_cli_only_previews(self):
        with tempfile.TemporaryDirectory() as folder:
            draft = Path(folder) / 'jira-comment.md'
            draft.write_text('### Dev acceptance: BLOCKED\nMissing test access.\n', encoding='utf-8')
            session = Mock()
            session.get.return_value.json.return_value = {'fields': {'status': {'name': 'To Do'}, 'attachment': []}}
            with patch('sys.argv', ['post_jira_acceptance.py', '--issue', 'DEMO-1', '--comment-file', str(draft)]), patch.object(posting, 'jira_session', return_value=session), contextlib.redirect_stdout(io.StringIO()):
                posting.main()
            session.post.assert_not_called()
            session.put.assert_not_called()

    def test_screenshot_outside_report_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder) / 'report'
            base.mkdir()
            (Path(folder) / 'private.png').write_bytes(b'private-file')
            with self.assertRaisesRegex(SystemExit, 'inside the report directory'):
                posting.referenced_images('![](../private.png)', base, 'demo1-')

    def test_distinct_image_paths_cannot_alias_one_attachment(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            for subfolder in ('first', 'second'):
                target = base / subfolder
                target.mkdir()
                (target / 'a.png').write_bytes(b'example')
            with self.assertRaisesRegex(SystemExit, 'distinct filenames'):
                posting.referenced_images('![](first/a.png) ![](second/a.png)', base, 'demo1-')


if __name__ == '__main__':
    unittest.main()
