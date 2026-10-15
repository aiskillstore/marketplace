import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from clients import WorkflowError, settings
from prepare_prs import ensure_pr, inspect_repository, prepare, repository_name
from check_review import check, thread_messages
from review_result import review_verdict, urls


FIXTURES = json.loads((Path(__file__).parent / "fixtures" / "review_messages.json").read_text(encoding="utf-8"))
CONFIG = {"base_branch": "develop", "review_bot_user_id": "UREVIEWBOT", "reviewers": [{"uuid": "{00000000-0000-4000-8000-000000000001}"}, {"uuid": "{00000000-0000-4000-8000-000000000002}"}]}
BOT = CONFIG["review_bot_user_id"]
SOURCE = "a" * 40
DESTINATION = "b" * 40
URL = "https://bitbucket.org/example-workspace/service/pull-requests/205"


def handoff():
    return {"summary": "Allow item editing for authorized users.", "pull_requests": [{
        "repository": "example-workspace/service", "branch": "feature/items", "base": "develop",
        "id": 205, "url": URL, "title": "DEMO-1: Enable item editing",
        "source_commit": SOURCE, "destination_commit": DESTINATION}]}


def current_pr():
    return {"id": 205, "state": "OPEN", "draft": False, "title": "DEMO-1: Enable item editing",
            "author": {"uuid": "author"}, "reviewers": [], "links": {"html": {"href": URL}},
            "source": {"commit": {"hash": SOURCE}}, "destination": {"commit": {"hash": DESTINATION}}}


class ReviewResultTests(unittest.TestCase):
    def verdict(self, name):
        messages = FIXTURES[name]
        return review_verdict(messages, urls(messages[0]["text"]), BOT)[0]

    def test_synthetic_clean_review_passes(self):
        self.assertEqual(self.verdict("clean"), "clean")

    def test_synthetic_published_finding_blocks(self):
        self.assertEqual(self.verdict("findings"), "findings")

    def test_synthetic_withheld_claim_is_not_a_clean_review(self):
        self.assertEqual(self.verdict("needs_context"), "needs_attention")

    def test_synthetic_failed_review_waits_for_resume(self):
        self.assertEqual(self.verdict("failed"), "waiting")

    def test_untrusted_sender_cannot_approve(self):
        messages = copy.deepcopy(FIXTURES["clean"])
        messages[-1]["user"] = "some-human"
        self.assertEqual(review_verdict(messages, [URL], BOT)[0], "waiting")

    def test_completion_from_another_job_cannot_approve(self):
        messages = copy.deepcopy(FIXTURES["clean"])
        messages[-1]["text"] = messages[-1]["text"].replace("sample-job", "another-job")
        self.assertEqual(review_verdict(messages, [URL], BOT)[0], "waiting")

    def test_partial_batch_cannot_approve_the_delivery(self):
        self.assertEqual(review_verdict(FIXTURES["clean"], [URL, URL.replace("205", "206")], BOT)[0], "needs_attention")

    def test_complete_two_pr_batch_can_pass_together(self):
        messages = copy.deepcopy(FIXTURES["clean"])
        second = URL.replace("205", "206")
        messages[0]["text"] = messages[0]["text"].replace("1 PR\n", "2 PRs\n") + "\n• " + second
        self.assertEqual(review_verdict(messages, [URL, second], BOT)[0], "clean")

    def test_latest_running_job_invalidates_an_older_clean_result(self):
        messages = copy.deepcopy(FIXTURES["clean"])
        next_start = copy.deepcopy(messages[0])
        next_start["ts"] = "1000000003.000000"
        next_start["text"] = next_start["text"].replace("sample-job", "new-job")
        messages.append(next_start)
        self.assertEqual(review_verdict(messages, [URL], BOT)[0], "waiting")

    def test_unknown_format_requires_inspection(self):
        messages = copy.deepcopy(FIXTURES["clean"])
        messages[-1]["text"] = messages[-1]["text"].split("\nSummary:")[0] + "\nSummary:\nLooks good."
        self.assertEqual(review_verdict(messages, [URL], BOT)[0], "needs_attention")

    def test_existing_duplicate_findings_are_not_clean(self):
        messages = copy.deepcopy(FIXTURES["clean"])
        messages[-1]["text"] = messages[-1]["text"].replace("0 duplicate(s) skipped", "1 duplicate(s) skipped")
        self.assertEqual(review_verdict(messages, [URL], BOT)[0], "findings")


def connector_thread(parent_text, replies):
    blocks = [f"=== THREAD PARENT MESSAGE ===\nFrom: Example User <user@example.invalid> (UEXAMPLE)\nTime: x\nMessage TS: 1000000000.000000\n{parent_text}",
              f"=== THREAD REPLIES ({len(replies)} total) ==="]
    for index, reply in enumerate(replies, 1):
        blocks.append(f"--- Reply {index} of {len(replies)} ---\nFrom: Example Review <bot@example.invalid> ({reply['user']})\n"
                      f"Time: x\nMessage TS: {reply['ts']}\n{reply['text']}")
    return "\n\n".join(blocks)


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.bitbucket = Mock()
        self.bitbucket.get.return_value = current_pr()

    def run_check(self, replies=None, parent=f"<{URL}/overview|bitbucket.org/x>", changed=None):
        return check(connector_thread(parent, FIXTURES["clean"] if replies is None else replies),
                     changed or handoff(), self.bitbucket, CONFIG)

    def test_connector_text_parses_into_messages(self):
        messages = thread_messages(connector_thread(URL, FIXTURES["clean"]))
        self.assertEqual([message["user"] for message in messages], ["UEXAMPLE", BOT, BOT])
        self.assertEqual(messages[2]["text"], FIXTURES["clean"][1]["text"].strip())

    def test_clean_batch_returns_engineering_message(self):
        result = self.run_check()
        self.assertEqual(result["verdict"], "clean")
        self.assertIn(handoff()["summary"], result["engineering_message"])
        self.assertIn(URL, result["engineering_message"])
        self.assertEqual(result["engineering_message"].splitlines()[1:], [URL])

    def test_changed_source_or_destination_blocks_announcement(self):
        for side in ("source", "destination"):
            with self.subTest(side=side):
                current = current_pr()
                current[side]["commit"]["hash"] = "c" * 40
                self.bitbucket.get.return_value = current
                result = self.run_check()
                self.assertEqual(result["verdict"], "needs_attention")
                self.assertNotIn("engineering_message", result)

    def test_wrong_parent_thread_blocks_announcement(self):
        self.assertEqual(self.run_check(parent=URL.replace("205", "201"))["verdict"], "needs_attention")

    def test_running_review_keeps_waiting(self):
        self.assertEqual(self.run_check(FIXTURES["clean"][:1])["verdict"], "waiting")

    def test_titles_and_summary_cannot_inject_slack_mentions(self):
        changed = handoff()
        changed["summary"] = "Allow <@U123> & dispatch"
        changed["pull_requests"][0]["title"] = "Change <!channel>"
        text = self.run_check(changed=changed)["engineering_message"]
        self.assertNotIn("<@U123>", text)
        self.assertNotIn("<!channel>", text)

    def test_synthetic_findings_never_reach_engineering(self):
        messages = copy.deepcopy(FIXTURES["findings"])
        original_url, = urls(messages[0]["text"])
        for message in messages:
            message["text"] = message["text"].replace(original_url, URL)
        result = self.run_check(messages)
        self.assertEqual(result["verdict"], "findings")
        self.assertNotIn("engineering_message", result)


class PreparePRTests(unittest.TestCase):
    def test_bitbucket_origin_formats(self):
        for remote in ("git@bitbucket.org:example-workspace/service.git", "https://bitbucket.org/example-workspace/service.git", "ssh://git@bitbucket.org/example-workspace/service.git"):
            with self.subTest(remote=remote):
                self.assertEqual(repository_name(remote), "example-workspace/service")

    def test_new_pr_assigns_both_verified_reviewers(self):
        client = Mock()
        verified = current_pr()
        verified["reviewers"] = CONFIG["reviewers"]
        client.request.return_value = {"id": 205}
        client.get.return_value = verified
        snapshot = handoff()["pull_requests"][0] | {"existing": None}
        result = ensure_pr(client, snapshot, {"title": "Item editing", "description": "Allow item editing."}, CONFIG["reviewers"])
        self.assertEqual(result["url"], URL)
        self.assertEqual(client.request.call_args.args[0], "POST")
        assigned = {user["uuid"] for user in client.request.call_args.kwargs["json"]["reviewers"]}
        self.assertEqual(assigned, {user["uuid"] for user in CONFIG["reviewers"]})

    def test_existing_pr_preserves_other_reviewers(self):
        client = Mock()
        existing = current_pr()
        existing["reviewers"] = [{"uuid": "another-reviewer"}]
        verified = copy.deepcopy(existing)
        verified["reviewers"] += CONFIG["reviewers"]
        client.get.side_effect = [existing, verified]
        snapshot = handoff()["pull_requests"][0] | {"existing": existing}
        ensure_pr(client, snapshot, {}, CONFIG["reviewers"])
        self.assertEqual(client.request.call_args.args[0], "PUT")
        assigned = {user["uuid"] for user in client.request.call_args.kwargs["json"]["reviewers"]}
        self.assertIn("another-reviewer", assigned)

    def test_dry_run_never_creates_a_pr(self):
        client = Mock()
        snapshot = handoff()["pull_requests"][0] | {"existing": None}
        request = {"summary": "Overall change", "pull_requests": [{"repository": "local-path", "title": "Change", "description": "Useful change."}]}
        with patch("prepare_prs.inspect_repository", return_value=snapshot), patch("prepare_prs.settings", return_value=CONFIG):
            result = prepare(client, request)
        self.assertTrue(result["dry_run"])
        client.request.assert_not_called()

    def test_destination_change_during_pr_creation_blocks_handoff(self):
        client = Mock()
        verified = current_pr()
        verified["reviewers"] = CONFIG["reviewers"]
        verified["destination"]["commit"]["hash"] = "c" * 40
        client.request.return_value = {"id": 205}
        client.get.return_value = verified
        snapshot = handoff()["pull_requests"][0] | {"existing": None}
        with self.assertRaisesRegex(WorkflowError, "destination changed"):
            ensure_pr(client, snapshot, {"title": "Item editing", "description": "Allow item editing."}, CONFIG["reviewers"])

    def test_unpublished_local_commit_blocks_creation(self):
        client = Mock()
        client.get.side_effect = [{"target": {"hash": "c" * 40}}, {"target": {"hash": DESTINATION}}]
        with patch("prepare_prs.git", side_effect=["", "feature/items", "git@bitbucket.org:example-workspace/service.git", SOURCE]):
            with self.assertRaises(WorkflowError):
                inspect_repository(client, {"repository": "local-path"}, CONFIG)
        client.request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
