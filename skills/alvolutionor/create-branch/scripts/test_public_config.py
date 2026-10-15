import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import create_branch as branch
import create_jira
import workflow_config


class PrivateConfigurationTests(unittest.TestCase):
    def test_missing_configuration_fails_without_network(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaisesRegex(ValueError, "WORKFLOW_CONFIG"):
            workflow_config.load_settings()

    def test_jira_only_does_not_require_bitbucket_configuration_or_credentials(self):
        config = {"jira_url": "https://jira.example.com", "jira_project": "DEMO", "jira_board_id": 1, "jira_sprint_field": "customfield_1"}
        with patch.object(workflow_config, "load_settings", return_value=config), patch.object(workflow_config, "jira_session", return_value="jira-session"), patch.object(workflow_config, "bitbucket_session") as bitbucket:
            self.assertEqual(branch.sessions(with_bitbucket=False), ("jira-session", None))
        bitbucket.assert_not_called()
        self.assertEqual(branch.JIRA, config["jira_url"])
        self.assertEqual(create_jira.PROJECT, "DEMO")

    def test_jira_url_cannot_embed_credentials_or_target_a_path(self):
        for url in ("http://jira.example.com", "https://name:secret@jira.example.com", "https://jira.example.com/path", "https://jira.example.com?q=x"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                workflow_config.jira_url({"jira_url": url})

    def test_wrong_origin_blocks_before_a_push(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "service").mkdir()
            result = Mock(stdout="git@bitbucket.org:other-workspace/service.git")
            with patch.object(branch, "LOCAL_ROOT", root), patch.object(branch, "BB", "https://api.bitbucket.org/2.0/repositories/example-workspace"), patch.object(branch.subprocess, "run", return_value=result) as run, self.assertRaisesRegex(SystemExit, "origin does not match"):
                branch.push_branch({"repo": "service", "base_hash": "a" * 40, "name": "feature/DEMO-1-items"})
            self.assertEqual(run.call_count, 1)

    def test_ambiguous_active_sprints_block_board_writes(self):
        issue = {"fields": {"assignee": {"accountId": "self-user"}}}
        with patch.object(branch, "call", return_value={"values": [{"id": 1}, {"id": 2}]}), self.assertRaisesRegex(SystemExit, "exactly one"):
            branch.board_actions(Mock(), issue, "self-user")


if __name__ == "__main__":
    unittest.main()
