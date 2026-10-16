import argparse
from html import escape
import json
import re
import sys
from pathlib import Path

from clients import Bitbucket, WorkflowError, settings
from review_result import review_verdict, urls


MESSAGE = re.compile(
    r"^From: [^\n]*\((U\w+)\)\nTime: [^\n]*\nMessage TS: (\d+\.\d{6})\n(.*?)"
    r"(?=\n+(?:--- Reply \d+ of \d+ ---|=== THREAD REPLIES)|\Z)", re.M | re.S)


def thread_messages(text):
    return [{"user": user, "ts": ts, "text": body.strip()} for user, ts, body in MESSAGE.findall(text)]


def changed_commits(client, handoff):
    for pr in handoff["pull_requests"]:
        current = client.get(f"repositories/{pr['repository']}/pullrequests/{pr['id']}")
        if current["state"] != "OPEN" or current.get("draft"):
            return f"{pr['repository']} PR is no longer open and ready"
        for side in ("source", "destination"):
            if current[side]["commit"]["hash"] != pr[f"{side}_commit"]:
                return f"{pr['repository']} {side} commit changed; request a new review"
    return None


def engineering_message(handoff):
    lines = [escape(handoff["summary"].strip(), quote=False)]
    lines.extend(pr["url"] for pr in handoff["pull_requests"])
    return "\n".join(lines)


def check(thread_text, handoff, bitbucket, config):
    messages = thread_messages(thread_text)
    expected = set().union(*(urls(pr["url"]) for pr in handoff["pull_requests"]))
    if not messages or urls(messages[0]["text"]) != expected:
        return {"verdict": "needs_attention", "reason": "Review parent message does not match the PR batch"}
    verdict, reason = review_verdict(messages[1:], [pr["url"] for pr in handoff["pull_requests"]],
                                     config["review_bot_user_id"])
    if verdict == "clean":
        stale = changed_commits(bitbucket, handoff)
        if stale:
            return {"verdict": "needs_attention", "reason": stale}
        message = engineering_message(handoff)
        if len(message) > 3900:
            return {"verdict": "needs_attention", "reason": "Shorten the engineering summary"}
        return {"verdict": "clean", "reason": reason, "engineering_message": message}
    return {"verdict": verdict, "reason": reason}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument("--thread", type=Path, required=True)
    args = parser.parse_args()
    handoff = json.loads(args.handoff.read_text(encoding="utf-8"))
    result = check(args.thread.read_text(encoding="utf-8"), handoff, Bitbucket(), settings())
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (WorkflowError, ValueError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
