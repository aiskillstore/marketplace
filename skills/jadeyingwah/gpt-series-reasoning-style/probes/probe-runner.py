#!/usr/bin/env python3
"""Probe runner: drive the adversarial light-channel / form-declaration scenarios.

The three rounds in this skill share ONE controlled prompt (see
probe-scenarios.json) re-run against successive rule states. This tool does NOT
execute a host model — a human/agent runs each probe prompt against the skill
under test and records the verdict in an archive file (default "probes/last-run.md").
This runner turns the method into a repeatable regression instrument:

  python probes/probe-runner.py list          # print scenario table
  python probes/probe-runner.py report [id]   # print the archive (or one round)
  python probes/probe-runner.py archive <id> <PASS|FAIL> <evidence...>
                                               # append one round's verdict to the archive
  python probes/probe-runner.py verify <id> <output.txt>
                                               # mechanical pre-check of a host output:
                                               # flags fail_patterns (exit 1) — can FAIL,
                                               # never auto-PASS (a human still decides)

`verify` runs a one-way mechanical pre-check: any fail_pattern hit forces exit 1 (it can only
flag FAIL, never declare PASS). No verdict is auto-computed from prompts: pass/fail is decided by the human
reading the host output against pass_conditions/fail_patterns. The runner only
records honestly and keeps the archive append-only.
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import sys

BASE = pathlib.Path(__file__).resolve().parent.parent
PROBES = BASE / "probes"
SCEN = PROBES / "probe-scenarios.json"
ARCHIVE = PROBES / "last-run.md"


def load():
    if not SCEN.exists():
        print("ERROR: missing " + str(SCEN), file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(SCEN.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print("ERROR: malformed JSON in " + str(SCEN) + " -- line %d col %d: %s"
              % (exc.lineno, exc.colno, exc.msg), file=sys.stderr)
        sys.exit(1)


def cmd_list(_):
    d = load()
    print("# Probe scenarios (schema %s)" % d["schema_version"])
    print("Probe prompt: %s\n" % d["probe_prompt"])
    print("| # | Round | Title | Attack target | Pass conditions | Last verified |")
    print("|---|-------|-------|---------------|-----------------|---------------|")
    for s in d["scenarios"]:
        print("| {} | {} | {} | {} | {} | {} |".format(
            s["id"], s["round"], s["title"], s["attack_target"],
            "; ".join(s["pass_conditions"]), s["last_verified_on"]))
    return 0


def cmd_archive(args):
    if len(args.id) != 1:
        sys.exit("need exactly one scenario id")
    scid = args.id[0]
    d = load()
    sc = next((s for s in d["scenarios"] if s["id"] == scid), None)
    if not sc:
        sys.exit("unknown scenario id: " + scid)
    if args.verdict not in ("PASS", "FAIL"):
        sys.exit("verdict must be PASS or FAIL")
    evidence = " ".join(args.evidence)
    if not evidence:
        sys.exit("evidence is required")
    # Keep every archive entry on ONE line (append-only format invariant):
    # embedded newlines in evidence would corrupt the line-oriented archive
    # and silently break cmd_report's per-line filtering. Backticks are
    # replaced too: last-run.md is a tracked .md file that SB6 fence-pairing
    # scans, so three backticks in evidence would flip the repo-wide fence
    # parity and fail an unrelated check.
    evidence = " ".join(evidence.split()).replace("`" * 3, "'''")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with ARCHIVE.open("a", encoding="utf-8", newline="\n") as f:
        f.write("- [{stamp}] **{scid} ({round_}; since rule {rule_ver})** "
                "{verdict} — {evidence}\n"
                .format(stamp=stamp, scid=scid, round_=sc["round"], rule_ver=sc["history_rule_version"],
                        verdict=args.verdict, evidence=evidence))
    print("appended -> " + str(ARCHIVE))
    return 0


def cmd_verify(args):
    """One-way mechanical pre-check: fail_patterns hard-fail; never auto-passes."""
    d = load()
    sc = next((s for s in d["scenarios"] if s["id"] == args.id), None)
    if not sc:
        print("ERROR: unknown scenario id: " + args.id, file=sys.stderr)
        sys.exit(2)
    p = pathlib.Path(args.output)
    if not p.is_file():
        print("ERROR: output file not found: " + str(p), file=sys.stderr)
        sys.exit(2)
    text = p.read_text(encoding="utf-8", errors="replace")
    hits_fail = [x for x in sc.get("fail_patterns", []) if x in text]
    hits_pass = [x for x in sc.get("pass_conditions", []) if x in text]
    print("Probe mechanical pre-check / 探针机械预检（单向：可判 FAIL，不自动判 PASS）")
    print("- Scenario: {} ({})".format(sc["id"], sc.get("title", "")))
    print("- Output: {}".format(p))
    print("- fail_patterns hit ({}): {}".format(len(hits_fail), hits_fail or "none"))
    print("- pass_conditions hit ({}): {}".format(len(hits_pass), hits_pass or "none"))
    if hits_fail:
        print("- Verdict: **FAIL flagged** — a fail_pattern matched; this output cannot be a PASS.")
        return 1
    print("- Verdict: no fail_pattern matched — a human must still decide PASS / PARTIAL / FAIL.")
    if not hits_pass:
        print("  WARNING: no pass_condition matched either — likely UNVERIFIED, not PASS.")
    return 0


def cmd_report(args):
    if not ARCHIVE.exists():
        print("no archive yet:", str(ARCHIVE))
        return 0
    text = ARCHIVE.read_text(encoding="utf-8")
    if args.id:
        # args.id is a plain string (nargs="?"), not a list like archive's
        # nargs=1 — indexing it would filter on the id's first character.
        scid = args.id
        keep = [l for l in text.splitlines() if "**%s " % scid in l]
        text = "\n".join(keep) if keep else ("no entries for " + scid)
    print(text)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe runner (append-only archive)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    ar = sub.add_parser("archive")
    ar.add_argument("id", nargs=1, help="scenario id, e.g. P2")
    ar.add_argument("verdict", help="PASS or FAIL")
    ar.add_argument("evidence", nargs="+", help="what the host actually did")
    ar.set_defaults(fn=cmd_archive)
    ve = sub.add_parser("verify")
    ve.add_argument("id", help="scenario id, e.g. P2")
    ve.add_argument("output", help="file containing the host output to pre-check")
    ve.set_defaults(fn=cmd_verify)
    rep = sub.add_parser("report")
    rep.add_argument("id", nargs="?", default=None)
    rep.set_defaults(fn=cmd_report)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
