import argparse
import json
import re
import sys
from pathlib import Path

import requests

import workflow_config


JIRA = ""
BOARD_ID = None
SPRINT_FIELD = ""
PROJECT = "DEMO"


def configure(config):
    global JIRA, BOARD_ID, SPRINT_FIELD, PROJECT
    JIRA = workflow_config.jira_url(config)
    BOARD_ID = int(workflow_config.required(config, "jira_board_id"))
    SPRINT_FIELD = str(workflow_config.required(config, "jira_sprint_field"))
    PROJECT = str(workflow_config.required(config, "jira_project"))


SUPPORTED_KEYS = {"summary", "description", "project", "issue_type", "assignee_account_id", "status"}


class JiraError(RuntimeError):
    pass


def request(session, method, path, **kwargs):
    try:
        response = session.request(method, JIRA + path, timeout=30, **kwargs)
    except requests.RequestException as exc:
        if method == "POST" and path == "/rest/api/3/issue":
            raise JiraError("Creation outcome unknown. Search Jira before retrying; do not create another copy.") from exc
        raise JiraError(f"Jira {method} {path} failed ({type(exc).__name__}).") from exc
    if not response.ok:
        if method == "POST" and path == "/rest/api/3/issue" and response.status_code >= 500:
            raise JiraError(f"Creation returned HTTP {response.status_code}; outcome may be unknown. Search Jira before retrying.")
        raise JiraError(f"Jira {method} {path} returned HTTP {response.status_code}.")
    try:
        return response.json() if response.content else None
    except ValueError as exc:
        if method == "POST" and path == "/rest/api/3/issue":
            raise JiraError("Creation returned an unreadable response. Search Jira before retrying.") from exc
        raise JiraError(f"Jira {method} {path} returned unreadable JSON.") from exc


UNRESOLVED_MARKERS = re.compile(r"open questions?|\bTBD\b|to be confirmed|to be decided", re.IGNORECASE)


def document_text(node):
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        return node.get("text", "") + " ".join(document_text(child) for child in node.get("content", []))
    return ""


def validate_spec(spec):
    if not isinstance(spec, dict):
        raise JiraError("Input must be a JSON object.")
    unknown = spec.keys() - SUPPORTED_KEYS
    if unknown:
        raise JiraError("Unsupported input keys: " + ", ".join(sorted(unknown)))
    for key in ("summary", "project", "issue_type", "assignee_account_id", "status"):
        if key in spec and (not isinstance(spec[key], str) or not spec[key].strip()):
            raise JiraError(f"{key} must be a nonempty string.")
    if not spec.get("summary") or len(spec["summary"].strip()) > 255:
        raise JiraError("summary must contain 1 to 255 characters.")
    if not re.fullmatch(r"[A-Z][A-Z0-9_]*", spec.get("project", PROJECT)):
        raise JiraError("project must be a Jira project key.")
    description = spec.get("description")
    marker = UNRESOLVED_MARKERS.search(document_text(description))
    if marker:
        raise JiraError(f"description contains unresolved item {marker.group(0)!r}; resolve it with the user before creating the card.")
    if isinstance(description, str) and description.strip():
        return
    if isinstance(description, dict) and description.get("type") == "doc" and description.get("version") == 1 and isinstance(description.get("content"), list) and description["content"]:
        return
    raise JiraError("description must be nonempty text or an Atlassian Document Format document.")


def description_document(description):
    if isinstance(description, dict):
        return description
    paragraphs = []
    for line in description.splitlines():
        paragraphs.append({"type": "paragraph", "content": [{"type": "text", "text": line}] if line else []})
    return {"type": "doc", "version": 1, "content": paragraphs}


def plan_issue(session, spec):
    validate_spec(spec)
    me = request(session, "GET", "/rest/api/3/myself")
    if not me.get("active") or not me.get("accountId"):
        raise JiraError("The configured Jira account is inactive or missing its account ID.")
    project_key = spec.get("project", PROJECT)
    project = request(session, "GET", f"/rest/api/3/project/{project_key}")
    active = request(session, "GET", f"/rest/agile/1.0/board/{BOARD_ID}/sprint", params={"state": "active"})["values"]
    if len(active) != 1:
        raise JiraError(f"Expected one active sprint on configured board {BOARD_ID}; found {len(active)}. Resolve the target before creating a card.")
    sprint = {"id": active[0]["id"], "name": active[0]["name"]}
    issue_type = spec.get("issue_type", "Task").strip()
    matches = [item for item in project.get("issueTypes", []) if item.get("name", "").casefold() == issue_type.casefold() and not item.get("subtask")]
    if len(matches) != 1:
        raise JiraError(f"Issue type {issue_type!r} is not an available standalone type in {project_key}.")
    assignee = spec.get("assignee_account_id", me["accountId"]).strip()
    if assignee != me["accountId"]:
        user = request(session, "GET", "/rest/api/3/user", params={"accountId": assignee})
        if not user.get("active"):
            raise JiraError("The requested assignee is inactive.")
    else:
        user = me
    fields = {
        "project": {"key": project_key},
        "issuetype": {"id": matches[0]["id"]},
        "summary": spec["summary"].strip(),
        "description": description_document(spec["description"]),
        "assignee": {"accountId": assignee},
    }
    return {"fields": fields, "issue_type": matches[0]["name"], "assignee": user.get("displayName", assignee), "status": spec.get("status", "To Do").strip(), "sprint": sprint}


def read_issue(session, key):
    return request(session, "GET", f"/rest/api/3/issue/{key}", params={"fields": f"summary,assignee,status,{SPRINT_FIELD}"})["fields"]


def execute(session, spec, apply=False, emit=None):
    plan = plan_issue(session, spec)
    if not apply:
        return {"applied": False, "plan": plan}
    created = request(session, "POST", "/rest/api/3/issue", json={"fields": plan["fields"]})
    key = created.get("key") if isinstance(created, dict) else None
    if not key:
        raise JiraError("Jira accepted creation without returning a key. Search Jira before retrying.")
    result = {"key": key, "url": f"{JIRA}/browse/{key}", "verified": False}
    if emit:
        emit({"event": "created", **result})
    try:
        fields = read_issue(session, key)
        assignee = plan["fields"]["assignee"]["accountId"]
        if (fields.get("assignee") or {}).get("accountId") != assignee:
            request(session, "PUT", f"/rest/api/3/issue/{key}/assignee", json={"accountId": assignee})
        if fields["status"]["name"] != plan["status"]:
            transitions = request(session, "GET", f"/rest/api/3/issue/{key}/transitions")["transitions"]
            transition = next((item for item in transitions if item["to"]["name"] == plan["status"]), None)
            if transition is None:
                raise JiraError(f"No available transition to {plan['status']!r}.")
            request(session, "POST", f"/rest/api/3/issue/{key}/transitions", json={"transition": {"id": transition["id"]}})
        sprint = plan["sprint"]
        if sprint["id"] not in {item["id"] for item in fields.get(SPRINT_FIELD) or []}:
            request(session, "POST", f"/rest/agile/1.0/sprint/{sprint['id']}/issue", json={"issues": [key]})
        verified = read_issue(session, key)
        if (verified.get("assignee") or {}).get("accountId") != assignee or verified["status"]["name"] != plan["status"] or sprint["id"] not in {item["id"] for item in verified.get(SPRINT_FIELD) or []}:
            raise JiraError("Final read did not confirm the intended assignee, status and active sprint.")
        result.update({"verified": True, "applied": True, "assignee": verified["assignee"].get("displayName", assignee), "status": verified["status"]["name"], "sprint": sprint})
        return result
    except (JiraError, KeyError, TypeError, ValueError) as exc:
        raise JiraError(f"Created {key} ({result['url']}), but completion is unverified: {exc} Do not create another copy.") from exc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        spec = json.loads(args.input.read_text(encoding="utf-8-sig"))
        validate_spec(spec)
        config = workflow_config.load_settings()
        configure(config)
        with workflow_config.jira_session(config) as session:
            result = execute(session, spec, apply=args.apply, emit=lambda value: print(json.dumps(value, ensure_ascii=False), flush=True))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (JiraError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
