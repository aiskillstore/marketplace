#!/usr/bin/env python3
"""
refresh_meta.py — keep README.md and SKILL.md numbers in sync with the actual
reference content, so counts and coverage dates never drift after an update.

Deterministic (always applied): principle count, theme count, per-theme table
counts, coverage date range + post count — all derived from references/*.md
(counts) and the tweet ids themselves (dates, via Snowflake). No API calls.

Editorial (only with --updated): the "updated" badge and the "Last updated" line.
Omit --updated on a plain refresh so the timestamp isn't spuriously bumped.

Usage:
  python refresh_meta.py --check              # dry run: report what would change
  python refresh_meta.py                      # apply deterministic fixes
  python refresh_meta.py --updated 2026-07-15 # also bump the "updated" date

Stdlib only.
"""

import argparse
import datetime
import re
import sys

import skill_lib as sl


def human(d, month_fmt):
    return f"{d.day} {d.strftime(month_fmt)} {d.year}"


def build_ops(updated: datetime.date | None):
    t = sl.totals()
    P, T, posts = t["principles_total"], t["themes_total"], t["posts_total"]
    cov = f"{human(t['earliest'], '%b')} → {human(t['latest'], '%b')}"
    latest_full = human(t["latest"], "%b")

    readme = [
        (r"badge/principles-\d+-", f"badge/principles-{P}-"),
        (r"badge/themes-\d+-", f"badge/themes-{T}-"),
        (r"\*\*\d+ principles\*\*", f"**{P} principles**"),
        (r"from \*\*.+?\*\* \(\d+ posts\)", f"from **{cov}** ({posts} posts)"),
        (r"the latest included post \(\*\*[^*]+\*\*\)",
         f"the latest included post (**{latest_full}**)"),
        (r"index of \d+ of his public X posts",
         f"index of {posts} of his public X posts"),  # README provenance count
    ]
    for slug, count in t["principle_counts"].items():
        # The table is prettier-aligned, so tolerate any padding around the pipe.
        readme.append(
            (r"(\(references/" + re.escape(slug) + r"\.md\)[^|\n]*\|[ \t]*)\d+",
             r"\g<1>" + str(count)))

    skill = [
        (r"\*\*\d+ principles\*\*", f"**{P} principles**"),
        (r"\b\d+ curated posts by", f"{posts} curated posts by"),  # SKILL provenance count
    ]

    if updated is not None:
        badge = updated.strftime("%Y--%m--%d")
        readme += [
            (r"badge/updated-[\d-]+-", f"badge/updated-{badge}-"),
            (r"\*\*Last updated:\*\* [^\n]*", f"**Last updated:** {human(updated, '%B')}"),
        ]
    return {"README.md": (sl.README, readme), "SKILL.md": (sl.SKILL_MD, skill)}, t


def apply(path, ops, write):
    """Return the number of patterns that ACTUALLY changed the file (not mere matches),
    so an in-sync file reports 0 and the check is a true idempotency test."""
    orig = path.read_text()
    text = orig
    changed = 0
    for pat, repl in ops:
        new = re.sub(pat, repl, text)
        if new != text:
            changed += 1
        text = new
    if write and text != orig:
        path.write_text(text)
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report changes, don't write")
    ap.add_argument("--updated", metavar="YYYY-MM-DD",
                    help="also set the 'updated' badge + 'Last updated' line to this date")
    args = ap.parse_args()

    updated = None
    if args.updated:
        try:
            updated = datetime.date.fromisoformat(args.updated)
        except ValueError:
            sys.exit(f"ERROR: --updated must be YYYY-MM-DD, got {args.updated!r}")

    files, t = build_ops(updated)
    print(f"Computed from references/: {t['principles_total']} principles, "
          f"{t['themes_total']} themes, {t['posts_total']} posts, "
          f"coverage {t['earliest']} → {t['latest']}")
    for slug, count in t["principle_counts"].items():
        print(f"    {count:>3}  {slug}")

    total = 0
    for label, (path, ops) in files.items():
        n = apply(path, ops, write=not args.check)
        total += n
        verb = "would update" if args.check else "updated"
        print(f"{label}: {verb} {n} value(s)")

    if args.check:
        print(f"\n[check] {total} replacement(s) would be applied "
              f"({'in sync ✓' if total == 0 else 'run without --check to apply'})")
    else:
        print(f"\nApplied {total} replacement(s). Review the diff, then commit.")


if __name__ == "__main__":
    main()
