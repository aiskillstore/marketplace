#!/usr/bin/env python
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import requests

import create_jira
import workflow_config

JIRA = ""
BB = ""
LOCAL_ROOT = Path(".")
BOARD_ID = None
SPRINT_FIELD = ""
TODO_STATUS = "To Do"


def configure(config, with_bitbucket=True):
    global JIRA, BB, LOCAL_ROOT, BOARD_ID, SPRINT_FIELD
    JIRA = workflow_config.jira_url(config)
    BOARD_ID = int(workflow_config.required(config, "jira_board_id"))
    SPRINT_FIELD = str(workflow_config.required(config, "jira_sprint_field"))
    create_jira.configure(config)
    if with_bitbucket:
        workspace = str(workflow_config.required(config, "bitbucket_workspace"))
        if not re.fullmatch(r"[A-Za-z0-9_-]+", workspace):
            raise ValueError("Invalid Bitbucket workspace")
        BB = "https://api.bitbucket.org/2.0/repositories/" + workspace
        LOCAL_ROOT = Path(workflow_config.required(config, "local_root")).expanduser().resolve()


def sessions(with_bitbucket=True):
    config = workflow_config.load_settings()
    configure(config, with_bitbucket=with_bitbucket)
    return workflow_config.jira_session(config), workflow_config.bitbucket_session() if with_bitbucket else None


def call(session, method, url, **kwargs):
    try:
        r = session.request(method, url, timeout=30, **kwargs)
    except requests.RequestException:
        sys.exit("ERROR request outcome unavailable; inspect the service before retrying a write")
    if not r.ok:
        sys.exit(f"ERROR {method} request returned HTTP {r.status_code}; inspect the service before retrying a write")
    return r.json() if r.content else None


def branch_slug(key, summary):
    text = re.sub(r"[^a-z0-9 _.\-]", "", summary.strip().lower()).replace(" ", "-")
    return f"{key}-{text}"[:40]


def adf_text(node):
    if isinstance(node, dict):
        if node.get("type") == "text":
            return node.get("text", "")
        sep = "\n" if node.get("type") in ("paragraph", "heading", "listItem") else ""
        return "".join(adf_text(c) for c in node.get("content", [])) + sep
    return ""


def default_kind(issue_type):
    return "bugfix" if issue_type.lower() == "bug" else "feature"


def plan_repo(bb, repo, kind, slug, base_override):
    model = call(bb, "GET", f"{BB}/{repo}/effective-branching-model")
    prefixes = {t["kind"]: t["prefix"] for t in model["branch_types"]}
    if kind not in prefixes:
        sys.exit(f"ERROR {repo} has no '{kind}' branch type; available: {sorted(prefixes)}")
    model_base = model["production" if kind == "hotfix" else "development"]["branch"]["name"]
    base = base_override or model_base
    name = prefixes[kind] + slug
    key = slug.split("-", 2)
    existing = call(bb, "GET", f"{BB}/{repo}/refs/branches",
                    params={"q": f'name ~ "{key[0]}-{key[1]}-"', "fields": "values.name"})["values"]
    if len(existing) > 1:
        sys.exit(f"ERROR {repo} has multiple matching branches; resolve the intended branch")
    base_hash = call(bb, "GET", f"{BB}/{repo}/refs/branches/{requests.utils.quote(base, safe='')}")["target"]["hash"]
    return {"repo": repo, "name": name, "base": base, "base_hash": base_hash, "exists": [b["name"] for b in existing]}


def push_branch(r):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", r["repo"]) or r["repo"] in {".", ".."}:
        sys.exit("ERROR invalid repository slug")
    repo_dir = (LOCAL_ROOT / r["repo"]).resolve()
    if not repo_dir.is_relative_to(LOCAL_ROOT):
        sys.exit("ERROR repository path is outside local_root")
    from urllib.parse import urlparse
    remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=repo_dir, capture_output=True, text=True, check=True).stdout.strip()
    expected = BB.removeprefix("https://api.bitbucket.org/2.0/repositories/") + "/" + r["repo"]
    parsed = urlparse(remote if not remote.startswith("git@bitbucket.org:") else remote.replace("git@bitbucket.org:", "ssh://git@bitbucket.org/", 1))
    if parsed.hostname != "bitbucket.org" or parsed.path.strip("/").removesuffix(".git") != expected:
        sys.exit("ERROR origin does not match the configured workspace and repository")
    if not (repo_dir / ".git").exists():
        sys.exit(f"ERROR no local clone at {repo_dir}; a git push is needed for Jira to index the branch")
    for cmd in (["git", "fetch", "origin", r["base_hash"]],
                ["git", "push", "origin", f"{r['base_hash']}:refs/heads/{r['name']}"]):
        if subprocess.run(cmd, cwd=repo_dir).returncode:
            sys.exit(f"ERROR {' '.join(cmd)} failed in {repo_dir}")


def board_actions(jira, issue, me, assignee_account_id=None, target_status=None):
    fields = issue["fields"]
    actions = []
    assignee = fields.get("assignee") or {}
    target_assignee = assignee_account_id or me
    if assignee.get("accountId") != target_assignee:
        actions.append(("assign", target_assignee))
    active = call(jira, "GET", f"{JIRA}/rest/agile/1.0/board/{BOARD_ID}/sprint", params={"state": "active"})["values"]
    if not active:
        sys.exit(f"ERROR board {BOARD_ID} has no active sprint")
    if len(active) != 1:
        sys.exit(f"ERROR expected exactly one active sprint; found {len(active)}")
    sprint = active[0]
    if sprint["id"] not in {s["id"] for s in fields.get(SPRINT_FIELD) or []}:
        actions.append(("sprint", sprint))
    status = fields["status"]
    if target_status is not None:
        if status["name"] != target_status:
            actions.append(("status", target_status))
    elif status["statusCategory"]["key"] == "new" and status["name"] != TODO_STATUS:
        actions.append(("status", TODO_STATUS))
    return actions


def apply_board(jira, key, actions):
    for action, value in actions:
        if action == "assign":
            call(jira, "PUT", f"{JIRA}/rest/api/3/issue/{key}/assignee", json={"accountId": value})
        elif action == "sprint":
            call(jira, "POST", f"{JIRA}/rest/agile/1.0/sprint/{value['id']}/issue", json={"issues": [key]})
        elif action == "status":
            transitions = call(jira, "GET", f"{JIRA}/rest/api/3/issue/{key}/transitions")["transitions"]
            target = next((t for t in transitions if t["to"]["name"] == value), None)
            if not target:
                sys.exit(f"ERROR no transition to '{value}' for {key}")
            call(jira, "POST", f"{JIRA}/rest/api/3/issue/{key}/transitions", json={"transition": {"id": target["id"]}})


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("issue", nargs="?")
    p.add_argument("--input", type=Path, help="JSON input for a new Jira issue; omit issue key")
    p.add_argument("--repo", action="append", default=[], help="Bitbucket repository slug in the configured workspace; repeatable")
    p.add_argument("--type", choices=["feature", "bugfix", "hotfix", "release"])
    p.add_argument("--from", dest="base", help="override base branch")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--assignee-account-id", help="Explicitly requested assignee instead of the current user")
    p.add_argument("--status", help="Explicitly requested Jira status")
    a = p.parse_args(argv)
    if any(not re.fullmatch(r"[A-Za-z0-9_.-]+", repo) or repo in {".", ".."} for repo in a.repo):
        p.error("Repository slugs must contain only letters, digits, dots, underscores and hyphens")
    if a.issue and not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*-[0-9]+", a.issue):
        p.error("Expected a Jira issue key")
    if bool(a.issue) == bool(a.input):
        p.error("Provide either an existing issue key or --input for a new issue.")
    for option in ("assignee_account_id", "status"):
        value = getattr(a, option)
        if value is not None:
            if not value.strip():
                p.error(f"{option} must not be empty.")
            setattr(a, option, value.strip())

    jira, bb = sessions(with_bitbucket=bool(a.repo))
    if a.input:
        try:
            spec = json.loads(a.input.read_text(encoding="utf-8-sig"))
            create_jira.validate_spec(spec)
            if a.assignee_account_id is not None:
                spec["assignee_account_id"] = a.assignee_account_id
            if a.status is not None:
                spec["status"] = a.status
            created = create_jira.execute(jira, spec, apply=a.apply,
                                          emit=lambda value: print(json.dumps(value, ensure_ascii=False), flush=True))
        except (create_jira.JiraError, OSError, ValueError, KeyError) as exc:
            sys.exit(f"ERROR {exc}")
        print(json.dumps(created, ensure_ascii=False, indent=2))
        if not a.apply or not a.repo:
            if a.repo:
                print("Branch repositories after issue creation: " + ", ".join(a.repo))
                print("Branch names, base commits and existing branches are resolved once the new issue key exists.")
            return
        key = created["key"]
        a.assignee_account_id = spec.get("assignee_account_id")
        a.status = spec.get("status", TODO_STATUS)
    else:
        key = a.issue.upper()
    issue = call(jira, "GET", f"{JIRA}/rest/api/3/issue/{key}",
                 params={"fields": f"summary,issuetype,status,assignee,description,{SPRINT_FIELD}"})
    f = issue["fields"]
    kind = a.type or default_kind(f["issuetype"]["name"])
    slug = branch_slug(key, f["summary"])
    me = call(jira, "GET", f"{JIRA}/rest/api/3/myself")["accountId"]

    print(f"{key} [{f['issuetype']['name']}] {f['summary']}")
    print(f"status: {f['status']['name']} | assignee: {(f.get('assignee') or {}).get('displayName')}")
    print(f"type: {kind} | slug: {slug}")
    if not a.repo:
        print("\n--- description ---\n" + adf_text(f.get("description")).strip())
        return

    repos = [plan_repo(bb, r, kind, slug, a.base) for r in a.repo]
    actions = board_actions(jira, issue, me, a.assignee_account_id, a.status)
    for r in repos:
        state = f"skip, already has {r['exists']}" if r["exists"] else f"create from {r['base']}@{r['base_hash'][:7]}"
        print(f"branch {r['repo']}: {r['name']} ({state})")
    print("board: " + (", ".join(f"{action} {value['name']}" if action == "sprint" else f"{action} {value}" for action, value in actions) or "nothing to change"))
    if a.status is None and f["status"]["statusCategory"]["key"] != "new":
        print(f"note: status '{f['status']['name']}' is past To Do; not moved back")
    if not a.apply:
        print("\n(dry run; add --apply)")
        return

    for r in repos:
        if not r["exists"]:
            push_branch(r)
        name = r["exists"][0] if r["exists"] else r["name"]
        remote = call(bb, "GET", f"{BB}/{r['repo']}/refs/branches/{requests.utils.quote(name, safe='')}")
        if not r["exists"] and remote["target"]["hash"] != r["base_hash"]:
            sys.exit("ERROR remote branch does not match the intended base commit")
        workspace = BB.rsplit('/', 1)[-1]
        print(f"OK https://bitbucket.org/{workspace}/{r['repo']}/branch/{name}")
    apply_board(jira, key, actions)
    verified = call(jira, "GET", f"{JIRA}/rest/api/3/issue/{key}",
                    params={"fields": f"assignee,status,{SPRINT_FIELD}"})
    if board_actions(jira, verified, me, a.assignee_account_id, a.status):
        sys.exit(f"ERROR Jira board changes for {key} did not pass final verification; reuse this issue and existing branches.")
    verified_fields = verified["fields"]
    verified_assignee = verified_fields.get("assignee") or {}
    print(f"verified assignee: {verified_assignee.get('displayName', verified_assignee.get('accountId'))} | status: {verified_fields['status']['name']}")
    print(f"OK {JIRA}/browse/{key}")


if __name__ == "__main__":
    main()
