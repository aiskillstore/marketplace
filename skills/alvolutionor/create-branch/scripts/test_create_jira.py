import unittest
from unittest.mock import Mock

import requests

import create_jira as jira


def response(value, status=200):
    return Mock(ok=status < 400, status_code=status, content=b"json" if value is not None else b"", json=Mock(return_value=value))


def issue(status="To Do", account="self-user", sprint=True):
    return {"fields": {"assignee": {"accountId": account, "displayName": account} if account else None, "status": {"name": status}, jira.SPRINT_FIELD: [{"id": 7}] if sprint else []}}


class CreateJiraTests(unittest.TestCase):
    def setUp(self):
        self.spec = {"summary": "Investigate missing item visibility", "description": "Observed: the inventory page does not list saved items.\nExpected: saved items are visible."}
        self.me = {"active": True, "accountId": "self-user", "displayName": "Configured user"}
        self.project = {"key": "DEMO", "issueTypes": [{"id": "task-id", "name": "Task", "subtask": False}, {"id": "bug-id", "name": "Bug", "subtask": False}]}

    def session(self, *results):
        return Mock(request=Mock(side_effect=[response(self.me), response(self.project), response({"values": [{"id": 7, "name": "Current sprint"}]}), *results]))

    def test_preview_reads_only_and_sets_defaults(self):
        session = self.session()
        result = jira.execute(session, self.spec)
        self.assertFalse(result["applied"])
        self.assertEqual(result["plan"]["status"], "To Do")
        self.assertEqual(result["plan"]["sprint"], {"id": 7, "name": "Current sprint"})
        self.assertEqual(result["plan"]["fields"]["assignee"], {"accountId": "self-user"})
        self.assertEqual(result["plan"]["fields"]["project"], {"key": "DEMO"})
        self.assertTrue(all(call.args[0] == "GET" for call in session.request.call_args_list))

    def test_create_includes_assignee_and_requires_final_read(self):
        session = self.session(response({"key": "DEMO-1"}), response(issue()), response(issue()))
        events = []
        result = jira.execute(session, self.spec, apply=True, emit=events.append)
        self.assertTrue(result["verified"])
        self.assertEqual(events[0]["key"], "DEMO-1")
        creation = session.request.call_args_list[3]
        self.assertEqual(creation.kwargs["json"]["fields"]["assignee"]["accountId"], "self-user")
        self.assertEqual(session.request.call_args_list[-1].args[0], "GET")

    def test_transition_to_todo(self):
        transitions = {"transitions": [{"id": "todo-id", "to": {"name": "To Do"}}]}
        session = self.session(response({"key": "DEMO-1"}), response(issue("Open")), response(transitions), response(None), response(issue()))
        result = jira.execute(session, self.spec, apply=True)
        self.assertTrue(result["verified"])
        self.assertEqual(session.request.call_args_list[6].kwargs["json"], {"transition": {"id": "todo-id"}})

    def test_corrects_unassigned_creation(self):
        session = self.session(response({"key": "DEMO-1"}), response(issue(account=None)), response(None), response(issue()))
        self.assertTrue(jira.execute(session, self.spec, apply=True)["verified"])
        assignment = session.request.call_args_list[5]
        self.assertEqual(assignment.args[0], "PUT")
        self.assertEqual(assignment.kwargs["json"], {"accountId": "self-user"})

    def test_missing_transition_reports_existing_card(self):
        session = self.session(response({"key": "DEMO-1"}), response(issue("Open")), response({"transitions": []}))
        with self.assertRaisesRegex(jira.JiraError, "Created DEMO-1.*Do not create another copy"):
            jira.execute(session, self.spec, apply=True)
        self.assertEqual(sum(call.args[0] == "POST" for call in session.request.call_args_list), 1)

    def test_final_read_rejects_ignored_assignment(self):
        session = self.session(response({"key": "DEMO-1"}), response(issue()), response(issue(account="another-user")))
        with self.assertRaisesRegex(jira.JiraError, "completion is unverified"):
            jira.execute(session, self.spec, apply=True)

    def test_final_read_rejects_changed_status(self):
        session = self.session(response({"key": "DEMO-1"}), response(issue()), response(issue("In Progress")))
        with self.assertRaisesRegex(jira.JiraError, "completion is unverified"):
            jira.execute(session, self.spec, apply=True)

    def test_creation_timeout_is_not_retried(self):
        session = self.session(requests.Timeout())
        with self.assertRaisesRegex(jira.JiraError, "outcome unknown"):
            jira.execute(session, self.spec, apply=True)
        self.assertEqual(session.request.call_count, 4)

    def test_creation_server_error_is_not_retried(self):
        session = self.session(response({}, status=500))
        with self.assertRaisesRegex(jira.JiraError, "outcome may be unknown"):
            jira.execute(session, self.spec, apply=True)
        self.assertEqual(session.request.call_count, 4)

    def test_creation_without_key_is_not_reported_complete(self):
        session = self.session(response(None))
        with self.assertRaisesRegex(jira.JiraError, "without returning a key"):
            jira.execute(session, self.spec, apply=True)

    def test_post_create_permission_error_keeps_key(self):
        session = self.session(response({"key": "DEMO-1"}), response({}, status=403))
        with self.assertRaisesRegex(jira.JiraError, "Created DEMO-1.*HTTP 403"):
            jira.execute(session, self.spec, apply=True)

    def test_inactive_current_account_fails_before_creation(self):
        self.me["active"] = False
        session = self.session()
        with self.assertRaisesRegex(jira.JiraError, "inactive"):
            jira.execute(session, self.spec, apply=True)
        self.assertEqual(session.request.call_count, 1)

    def test_explicit_assignee_status_and_type_override(self):
        spec = {**self.spec, "assignee_account_id": "other-user", "status": "Open", "issue_type": "Bug"}
        user = {"active": True, "accountId": "other-user", "displayName": "Requested user"}
        session = self.session(response(user), response({"key": "DEMO-1"}), response(issue("Open", "other-user")), response(issue("Open", "other-user")))
        result = jira.execute(session, spec, apply=True)
        self.assertEqual(result["status"], "Open")
        self.assertEqual(session.request.call_args_list[4].kwargs["json"]["fields"]["issuetype"], {"id": "bug-id"})

    def test_ticket_only_adds_current_sprint_and_verifies_it(self):
        session = self.session(response({"key": "DEMO-1"}), response(issue(sprint=False)), response(None), response(issue()))
        result = jira.execute(session, self.spec, apply=True)
        addition = session.request.call_args_list[5]
        self.assertEqual(addition.args[:2], ("POST", jira.JIRA + "/rest/agile/1.0/sprint/7/issue"))
        self.assertEqual(addition.kwargs["json"], {"issues": ["DEMO-1"]})
        self.assertEqual(result["sprint"], {"id": 7, "name": "Current sprint"})

    def test_final_read_rejects_missing_sprint(self):
        session = self.session(response({"key": "DEMO-1"}), response(issue(sprint=False)), response(None), response(issue(sprint=False)))
        with self.assertRaisesRegex(jira.JiraError, "Created DEMO-1.*active sprint"):
            jira.execute(session, self.spec, apply=True)

    def test_missing_current_sprint_prevents_creation(self):
        session = Mock(request=Mock(side_effect=[response(self.me), response(self.project), response({"values": []})]))
        with self.assertRaisesRegex(jira.JiraError, "found 0"):
            jira.execute(session, self.spec, apply=True)
        self.assertTrue(all(call.args[0] == "GET" for call in session.request.call_args_list))

    def test_ambiguous_current_sprint_prevents_creation(self):
        session = Mock(request=Mock(side_effect=[response(self.me), response(self.project), response({"values": [{"id": 7}, {"id": 8}]})]))
        with self.assertRaisesRegex(jira.JiraError, "found 2"):
            jira.execute(session, self.spec, apply=True)
        self.assertTrue(all(call.args[0] == "GET" for call in session.request.call_args_list))

    def test_invalid_input_never_contacts_jira(self):
        for updates in ({"assignee_account_id": None}, {"summary": " "}, {"description": ""}, {"sprint": 1}, {"project": "../DEMO"}):
            with self.subTest(updates=updates):
                session = Mock()
                with self.assertRaises(jira.JiraError):
                    jira.execute(session, {**self.spec, **updates}, apply=True)
                session.request.assert_not_called()

    def test_unresolved_questions_block_creation(self):
        adf = {"type": "doc", "version": 1, "content": [{"type": "heading", "content": [{"type": "text", "text": "Open questions"}]}]}
        for description in ("Scope\nOpen questions\n- Should admins edit?", "Limit is TBD.", adf):
            with self.subTest(description=description):
                session = Mock()
                with self.assertRaisesRegex(jira.JiraError, "unresolved"):
                    jira.execute(session, {**self.spec, "description": description}, apply=True)
                session.request.assert_not_called()

    def test_adf_description_is_preserved(self):
        document = {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Observed behavior"}]}]}
        plan = jira.plan_issue(self.session(), {**self.spec, "description": document})
        self.assertEqual(plan["fields"]["description"], document)

    def test_unsupported_issue_type_fails_before_creation(self):
        session = self.session()
        with self.assertRaisesRegex(jira.JiraError, "not an available standalone type"):
            jira.execute(session, {**self.spec, "issue_type": "Unknown"}, apply=True)
        self.assertTrue(all(call.args[0] == "GET" for call in session.request.call_args_list))


if __name__ == "__main__":
    unittest.main()
