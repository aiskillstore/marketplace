import contextlib
import io
import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import create_branch as branch


def card(account="self-user", status="To Do", category="new", sprint=True):
    return {"fields": {"summary": "Investigate missing item visibility", "issuetype": {"name": "Bug"}, "assignee": {"accountId": account}, "status": {"name": status, "statusCategory": {"key": category}}, branch.SPRINT_FIELD: [{"id": 1}] if sprint else []}}


class BoardActionsTests(unittest.TestCase):
    def actions(self, issue, **kwargs):
        with patch.object(branch, "call", return_value={"values": [{"id": 1, "name": "Current sprint"}]}):
            return branch.board_actions(Mock(), issue, "self-user", **kwargs)

    def test_default_assignment_todo_and_sprint(self):
        actions = self.actions(card("another-user", "Open", sprint=False))
        self.assertIn(("assign", "self-user"), actions)
        self.assertIn(("status", "To Do"), actions)
        self.assertIn(("sprint", {"id": 1, "name": "Current sprint"}), actions)

    def test_default_does_not_move_progress_backward(self):
        self.assertEqual(self.actions(card(status="In Progress", category="indeterminate")), [])

    def test_explicit_creation_choices_are_preserved(self):
        self.assertEqual(self.actions(card("requested-user", "Open"), assignee_account_id="requested-user", target_status="Open"), [])

    def test_explicit_status_replaces_todo_default(self):
        actions = self.actions(card(), target_status="In Progress")
        self.assertEqual(actions, [("status", "In Progress")])

    def test_apply_uses_requested_transition(self):
        with patch.object(branch, "call", side_effect=[{"transitions": [{"id": "31", "to": {"name": "In Progress"}}]}, None]) as call:
            branch.apply_board(Mock(), "DEMO-1", [("status", "In Progress")])
        self.assertEqual(call.call_args.kwargs["json"], {"transition": {"id": "31"}})


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.spec = {"summary": "Investigate missing item visibility", "description": "A saved item is missing from the inventory page.", "issue_type": "Bug"}
        self.result = {"key": "DEMO-1", "verified": True, "status": "To Do"}

    def run_new(self, args, spec=None, result=None):
        with contextlib.ExitStack() as stack:
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            stack.enter_context(patch.object(Path, "read_text", return_value=json.dumps(spec or self.spec)))
            sessions = stack.enter_context(patch.object(branch, "sessions", return_value=(Mock(), Mock())))
            create = stack.enter_context(patch.object(branch.create_jira, "execute", return_value=result or self.result))
            call = stack.enter_context(patch.object(branch, "call", side_effect=[card(), {"accountId": "self-user"}, {"target": {"hash": "abc123"}}, card()]))
            stack.enter_context(patch.object(branch, "BB", "https://api.bitbucket.org/2.0/repositories/example-workspace"))
            actions = stack.enter_context(patch.object(branch, "board_actions", return_value=[]))
            plan = stack.enter_context(patch.object(branch, "plan_repo", return_value={"repo": "service", "name": "bugfix/DEMO-1-test", "base": "develop", "base_hash": "abc123", "exists": []}))
            push = stack.enter_context(patch.object(branch, "push_branch"))
            apply_board = stack.enter_context(patch.object(branch, "apply_board"))
            branch.main(["--input", "actual-request.json", *args])
            return sessions, create, call, actions, plan, push, apply_board

    def test_ticket_only_leaves_sprint_to_jira_helper_without_branch_work(self):
        sessions, create, call, actions, plan, push, apply_board = self.run_new(["--apply"])
        sessions.assert_called_once_with(with_bitbucket=False)
        self.assertTrue(create.call_args.kwargs["apply"])
        for mocked in (call, actions, plan, push, apply_board):
            mocked.assert_not_called()

    def test_new_issue_preview_never_creates_branches(self):
        sessions, create, call, actions, plan, push, apply_board = self.run_new(["--repo", "service"], result={"applied": False, "plan": {}})
        self.assertFalse(create.call_args.kwargs["apply"])
        for mocked in (call, actions, plan, push, apply_board):
            mocked.assert_not_called()

    def test_combined_workflow_uses_created_key_and_preserves_choices(self):
        spec = {**self.spec, "assignee_account_id": "requested-user", "status": "Open"}
        sessions, create, call, actions, plan, push, apply_board = self.run_new(["--repo", "service", "--apply"], spec=spec)
        self.assertIn("/issue/DEMO-1", call.call_args_list[0].args[2])
        self.assertEqual(plan.call_args.args[2], "bugfix")
        self.assertTrue(plan.call_args.args[3].startswith("DEMO-1-"))
        for action_call in actions.call_args_list:
            self.assertEqual(action_call.args[-2:], ("requested-user", "Open"))
        push.assert_called_once()
        apply_board.assert_called_once()

    def test_cli_choices_override_json_choices_consistently(self):
        sessions, create, call, actions, plan, push, apply_board = self.run_new(["--repo", "service", "--apply", "--assignee-account-id", "requested-user", "--status", "Open"])
        self.assertEqual(create.call_args.args[1]["assignee_account_id"], "requested-user")
        self.assertEqual(create.call_args.args[1]["status"], "Open")
        self.assertEqual(actions.call_args.args[-2:], ("requested-user", "Open"))

    def test_existing_key_does_not_create_another_card(self):
        with contextlib.redirect_stdout(io.StringIO()), patch.object(branch, "sessions", return_value=(Mock(), None)), patch.object(branch, "call", side_effect=[card(), {"accountId": "self-user"}]), patch.object(branch.create_jira, "execute") as create:
            branch.main(["DEMO-1"])
        create.assert_not_called()

    def test_issue_key_and_new_input_are_mutually_exclusive(self):
        with contextlib.redirect_stderr(io.StringIO()), patch.object(branch, "sessions") as sessions, self.assertRaises(SystemExit):
            branch.main(["DEMO-1", "--input", "actual-request.json"])
        sessions.assert_not_called()


if __name__ == "__main__":
    unittest.main()
