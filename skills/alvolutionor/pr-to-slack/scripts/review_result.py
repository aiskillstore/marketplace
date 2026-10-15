import re
from decimal import Decimal


PR_URL = re.compile(r"https://bitbucket\.org/([\w.-]+/[\w.-]+)/pull-requests/(\d+)")
JOB_START = re.compile(r"\AAI Review job `([\w-]+)`\nRequested by [^\n]+mode: cross [^\n]+ (\d+) PRs?\n")
JOB_STATE = re.compile(r"\AAI Review job `([\w-]+)` reached state: ([\w-]+)\.")
PUBLICATION = re.compile(r"^Automatic publication: (\d+) published and verified, (\d+) duplicate\(s\) skipped, (\d+) unverified\.$", re.M)
SUMMARY = re.compile(
    r"^Cross review complete\. Shared sources \(also adjudicated\): (\d+); "
    r"Codex-confirmed candidates: (\d+); final gap-scan additions: (\d+); "
    r"rejected: (\d+); explicitly merged duplicates: (\d+); uncertain summary-only: (\d+)\.$", re.M)


def urls(text):
    return {f"https://bitbucket.org/{repository}/pull-requests/{number}" for repository, number in PR_URL.findall(text)}


def review_verdict(messages, expected_urls, bot_user_id):
    expected = set().union(*(urls(url) for url in expected_urls))
    trusted = sorted((message for message in messages if message.get("user") == bot_user_id),
                     key=lambda message: Decimal(message["ts"]))
    starts = [(message, JOB_START.match(message.get("text", ""))) for message in trusted]
    starts = [(message, match) for message, match in starts if match]
    if not starts:
        return "waiting", "Waiting for the review bot to acknowledge this PR batch"
    start, match = starts[-1]
    if urls(start["text"]) != expected or int(match[2]) != len(expected):
        return "needs_attention", "The review job covers a different PR batch"
    states = [(message, JOB_STATE.match(message.get("text", ""))) for message in trusted
              if Decimal(message["ts"]) >= Decimal(start["ts"])]
    states = [(message, state) for message, state in states if state and state[1] == match[1]]
    if not states:
        return "waiting", "Review is still running"
    completion, state = states[-1]
    if state[2] != "completed":
        return "waiting", f"Review job is {state[2]}; waiting for a successful completion"
    text = completion["text"]
    publications = PUBLICATION.findall(text)
    summaries = SUMMARY.findall(text)
    if len(publications) != 1 or len(summaries) != 1:
        return "needs_attention", "Completed review has an unrecognized or incomplete result format"
    if any(int(value) for value in publications[0]):
        return "findings", "Review has published findings, existing duplicates, or unverified publication"
    shared, confirmed, additions, rejected, duplicates, uncertain = map(int, summaries[0])
    if any((shared, confirmed, additions, duplicates, uncertain)):
        return "findings", "Review has findings or unresolved candidates"
    if re.search(r"^\d+ (?:advisory/needs-context decision|finding)\(s\) retained", text, re.M):
        return "needs_attention", "Review retained decisions requiring inspection"
    return "clean", f"Review job {match[1]} completed with zero findings and zero uncertain decisions"
