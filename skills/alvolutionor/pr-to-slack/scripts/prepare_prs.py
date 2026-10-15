import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

from clients import Bitbucket, WorkflowError, settings


def git(repository, *arguments):
    result = subprocess.run(["git", "-C", str(repository), *arguments], capture_output=True, text=True)
    if result.returncode:
        raise WorkflowError("Git command failed: " + " ".join(arguments))
    return result.stdout.strip()


def repository_name(remote):
    match = re.fullmatch(r"(?:git@bitbucket\.org:|https://bitbucket\.org/|ssh://git@bitbucket\.org/)([\w.-]+/[\w.-]+?)(?:\.git)?/?", remote)
    if not match:
        raise WorkflowError("Expected a Bitbucket origin remote")
    return match[1]


def inspect_repository(client, entry, config):
    repository = Path(entry["repository"]).resolve()
    if git(repository, "status", "--porcelain"):
        raise WorkflowError(f"Uncommitted changes in {repository}; commit only when explicitly requested")
    branch = git(repository, "branch", "--show-current")
    base = entry.get("base", config["base_branch"])
    if not branch or branch in {base, "main", "master"}:
        raise WorkflowError("Select the intended feature branch before preparing a PR")
    name = repository_name(git(repository, "remote", "get-url", "origin"))
    root = f"repositories/{name}"
    source = client.get(f"{root}/refs/branches/{quote(branch, safe='')}")
    destination = client.get(f"{root}/refs/branches/{quote(base, safe='')}")
    head = git(repository, "rev-parse", "HEAD")
    if source["target"]["hash"] != head:
        raise WorkflowError(f"{name}: publish the intended branch commits before creating the PR")
    if source["target"]["hash"] == destination["target"]["hash"]:
        raise WorkflowError(f"{name}: source and destination are the same commit")
    query = f'source.branch.name={json.dumps(branch)} AND destination.branch.name={json.dumps(base)}'
    candidates = list(client.pages(f"{root}/pullrequests", params={"state": "OPEN", "q": query, "pagelen": 50}))
    if len(candidates) > 1:
        raise WorkflowError(f"{name}: multiple open PRs match this branch and destination")
    return {"repository": name, "branch": branch, "base": base, "source_commit": head,
            "destination_commit": destination["target"]["hash"], "existing": candidates[0] if candidates else None}


def ensure_pr(client, snapshot, entry, reviewers):
    root = f"repositories/{snapshot['repository']}/pullrequests"
    existing = snapshot["existing"]
    required = {reviewer["uuid"] for reviewer in reviewers}
    if existing:
        current = client.get(f"{root}/{existing['id']}")
        if current["source"]["commit"]["hash"] != snapshot["source_commit"]:
            raise WorkflowError("PR source changed during preparation")
        required.discard(current.get("author", {}).get("uuid"))
        present = {reviewer["uuid"] for reviewer in current.get("reviewers", [])}
        if required - present or current.get("draft"):
            client.request("PUT", f"{root}/{current['id']}", json={
                "reviewers": [{"uuid": uuid} for uuid in sorted(present | required)], "draft": False})
        pr_id = current["id"]
    else:
        created = client.request("POST", root, json={
            "title": entry["title"], "description": entry["description"],
            "source": {"branch": {"name": snapshot["branch"]}},
            "destination": {"branch": {"name": snapshot["base"]}},
            "reviewers": [{"uuid": uuid} for uuid in sorted(required)],
            "draft": False, "close_source_branch": False})
        pr_id = created["id"]
    verified = client.get(f"{root}/{pr_id}")
    required.discard(verified.get("author", {}).get("uuid"))
    if verified["state"] != "OPEN" or verified.get("draft"):
        raise WorkflowError("PR is not open and ready for review")
    if not required <= {reviewer["uuid"] for reviewer in verified.get("reviewers", [])}:
        raise WorkflowError("Required reviewer assignment could not be verified")
    if verified["source"]["commit"]["hash"] != snapshot["source_commit"]:
        raise WorkflowError("PR source changed before verification")
    if verified["destination"]["commit"]["hash"] != snapshot["destination_commit"]:
        raise WorkflowError("PR destination changed before verification")
    return {key: snapshot[key] for key in ("repository", "branch", "base", "source_commit", "destination_commit")} | {
        "id": verified["id"], "url": verified["links"]["html"]["href"], "title": verified["title"]}


def prepare(client, request, apply=False):
    config = settings()
    entries = request.get("pull_requests", [])
    if not entries or not request.get("summary", "").strip():
        raise WorkflowError("Provide pull_requests and a factual overall summary")
    for entry in entries:
        if not entry.get("title", "").strip() or not entry.get("description", "").strip():
            raise WorkflowError("Each PR needs an English title and description")
        if re.search(r"co-authored-by:|generated with (?:claude|codex)|generated by (?:claude|codex)", entry["description"], re.I):
            raise WorkflowError("Remove attribution trailers from the PR description")
    snapshots = [inspect_repository(client, entry, config) for entry in entries]
    if len({item["repository"] for item in snapshots}) != len(snapshots):
        raise WorkflowError("Each repository may appear only once in a delivery")
    if not apply:
        return {"dry_run": True, "summary": request["summary"], "plans": [
            {key: value for key, value in snapshot.items() if key != "existing"} |
            {"action": "reuse" if snapshot["existing"] else "create"} for snapshot in snapshots]}
    prs = [ensure_pr(client, snapshot, entry, config["reviewers"]) for snapshot, entry in zip(snapshots, entries)]
    return {"summary": request["summary"], "pull_requests": prs}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    result = prepare(Bitbucket(), request, args.apply)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    try:
        main()
    except WorkflowError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
