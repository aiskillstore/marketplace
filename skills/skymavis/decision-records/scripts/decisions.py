#!/usr/bin/env python3
"""
Decision-records registry tool — generate docs/decisions/INDEX.md and the cross-reference
path links across the docs tree, validate it, mint draft ids, and promote a draft
into a numbered decision.

Repository layout — everything the convention owns lives under docs/decisions/:

    docs/
      decisions/                    # the convention's namespace (the umbrella)
        INDEX.md                    # GENERATED registry over accepted/ + archived/
        README.md                   # human guide to the convention (scaffolded by install)
        AGENTS.md                   # agent rules: decisions are binding (scaffolded by install)
        _template.md                # decision-record template (numbered)
        accepted/                   # ACCEPTED numbered decisions
          architecture/  product/  security/   # one subdir per type (alphabetical)
        archived/                   # RETIRED numbered decisions (superseded | deprecated) — flat
        drafts/                     # WIP candidates — flat, 4-UPPERCASE-letter ids, NOT in INDEX
          _template.md
      threat-model.md               # other repo docs stay siblings; still cross-ref decisions

Lifecycle (there is NO "proposed" status — proposing is the *act* of opening a PR):
  decisions/drafts/<AAAA-title>.md
    --(promote: a PR assigns the next counter)--> decisions/accepted/<type>/NNNN-title.md (accepted)
  decisions/accepted/<type>/NNNN   --(supersede/deprecate)-->  decisions/archived/NNNN-title.md

Conventions this tool encodes and enforces:
  * Identity is the global counter ID (`0001`, …) for decisions; a 4-UPPERCASE-letter
    ID (`CONF`) for drafts — mint a mnemonic of the draft's topic; `check` enforces
    format + uniqueness. Permanent and canonical; the only thing cross-refs use.
  * A counter is minted against one tree, so two branches can each mint the same one
    and stay green until they meet. `check` therefore also reads `origin/main` and warns
    (never fails) when an ID there already names a different file. Read-only, never
    fetches, silent when the ref is not on disk — see `warn_upstream_collisions`.
  * `type` is any lowercase slug — the set is OPEN; your accepted/<type>/ subdirs are the
    suggested set (architecture/product/security, or policy/legal/finance for governance).
    It lives in front-matter and, for a decision, equals its directory. `status` -> lifecycle.
  * Cross-reference by writing the bare ID as inline code — `0006` or `CONF`. NEVER
    hand-author a path. `build --relink` rewrites every such ID (in every docs/*.md —
    records, drafts, and other docs) into a correct relative link and self-heals on moves.
  * An accepted decision may NEVER reference a draft (a breach); `promote` therefore
    promotes a whole reference-closure together and refuses a set that would breach.
    Co-promoted drafts take their counters in the order the arguments were given, so the
    record the others build on can be named first and read as the earlier decision.
  * INDEX.md and every path link are GENERATED build artifacts.
  * A record's H1 reads `# NNNN — <title>`; a title carrying its own em-dash renders it as
    a colon. `promote` carries the new ID into the heading, re-paths every hand-authored
    relative link for the extra directory level, and retires the mnemonic from prose. It
    edits nothing outside docs/ and nothing inside code — a 4-letter mnemonic doubles as a
    plausible identifier — and lists what it left for a human instead.

Dependency-free (no PyYAML). Usage (a bare invocation = `build`; draft IDs are 4 UPPERCASE letters):
    python scripts/decisions.py build                  # write docs/decisions/INDEX.md
    python scripts/decisions.py build --relink         # also refresh path links everywhere
    python scripts/decisions.py check                  # validate only; exit 1 if stale (CI)
    python scripts/decisions.py rename-draft-id <name> <NEW>   # re-ID a draft, repoint refs
    python scripts/decisions.py promote CONF [TIER ...]        # promote draft(s), counters in
                                                               # the order given -> accepted/
    python scripts/decisions.py promote CONF --deref           # invert refs, promote alone
    python scripts/decisions.py promote CONF --allow-replace   # also archive what it supersedes
    python scripts/decisions.py install [repo]                 # adopt: symlink + scaffold + check
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import subprocess
import sys
from pathlib import Path


def find_docs(start: Path | None = None) -> Path:
    """Locate the repo's docs/ by walking up from the CWD (not from __file__ — the
    script may be a symlink installed by the decision-records skill). Falls back to a
    path relative to this file for the unusual case of no match."""
    cur = (start or Path.cwd()).resolve()
    for p in (cur, *cur.parents):
        if (p / "docs" / "decisions").is_dir():
            return p / "docs"
    return Path(__file__).resolve().parent.parent / "docs"


# A type is any lowercase slug — the set is OPEN. The repo's accepted/<type>/ subdirs are
# the suggested set (e.g. architecture, product, security; or policy, legal, finance,
# people, compliance, operations for governance repos). New types create their dir on promotion.
TYPE_RE = re.compile(r"^[a-z][a-z0-9-]*$")
ACTIVE_STATUS = {"accepted"}  # -> decisions/accepted/
RETIRED_STATUS = {"superseded", "deprecated"}  # -> decisions/archived/

BLOCK_SCALAR_RE = re.compile(r"^([>|])[0-9+-]*$")  # folded (>) / literal (|), chomp/indent mods

RECORD_RE = re.compile(r"^\d{4}-.+\.md$")  # NNNN-kebab-title.md (decisions, archived)
DRAFT_ID_RE = re.compile(r"^[A-Z]{4}$")  # 4-uppercase-letter draft ID
# An inline-code ID — a counter (`0006`) or a draft tag (`CONF`) — not already linked.
ID_RE = re.compile(r"(?<!\[)`(\d{4}|[A-Z]{4})`")
COUNTER_RE = re.compile(r"(?<!\[)`(\d{4})`")  # numeric-only, for prose validation
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
LABEL_ID_RE = re.compile(r"`?(\d{4}|[A-Z]{4})`?$")  # link label that is just an ID
FILE_ID_RE = re.compile(r"^(\d{4}|[A-Z]{4})-")  # leading ID in a filename
STATUS_ICON = {"accepted": "🟢", "deprecated": "⚪", "superseded": "🔵"}

FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


def strip_fences(text: str) -> str:
    """Blank out fenced code blocks, preserving line structure."""
    out: list[str] = []
    fence = None
    for line in text.splitlines():
        m = FENCE_RE.match(line)
        if fence is not None:
            if m and m.group(1) == fence:
                fence = None
            out.append("")
        elif m:
            fence = m.group(1)
            out.append("")
        else:
            out.append(line)
    return "\n".join(out)


def strip_code(text: str) -> str:
    """Blank out fenced blocks and inline code spans — a link inside code is syntax on
    display, not a live link, so it must not be link-checked."""
    text = strip_fences(text)
    text = re.sub(r"``[^`]*``", "", text)
    return re.sub(r"`[^`\n]*`", "", text)


INLINE_CODE_RE = re.compile(r"``[^`]*``|`[^`\n]*`")


def code_regions(text: str) -> list[tuple[int, int]]:
    """Offset spans of every fenced block and inline code span — regions whose content is
    syntax on display, not live markdown. Rewrites that reinterpret prose skip them."""
    fenced: list[tuple[int, int]] = []
    pos, fence, start = 0, None, 0
    for line in text.splitlines(keepends=True):
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence, start = m.group(1), pos
        elif m and m.group(1) == fence:
            fenced.append((start, pos + len(line)))
            fence = None
        pos += len(line)
    if fence is not None:  # unterminated fence — protect to end of file
        fenced.append((start, pos))
    spans = list(fenced)
    spans += [
        m.span()
        for m in INLINE_CODE_RE.finditer(text)
        if not any(a <= m.start() < b for a, b in fenced)
    ]
    return spans


def sub_outside(pattern: re.Pattern, repl, text: str, spans, group: int = 0) -> str:
    """`pattern.sub(repl, text)`, skipping matches whose `group` overlaps `spans`. The
    callback sees original offsets (re.sub matches against the input), so the spans stay
    valid. `group` narrows the test: a link's target is live even when its label is a code
    span — ``[`../deploy.md`](../deploy.md)`` is a real link, not an example."""

    def guarded(m: re.Match) -> str:
        start, end = m.span(group)
        return m.group(0) if any(a < end and start < b for a, b in spans) else repl(m)

    return pattern.sub(guarded, text)


def heading_anchors(text: str) -> set[str]:
    """GitHub-style anchor slugs for every heading, -N suffixes for duplicates."""
    slugs: set[str] = set()
    seen: dict[str, int] = {}
    for line in strip_fences(text).splitlines():
        m = HEADING_RE.match(line)
        if not m:
            continue
        s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", m.group(2))  # links -> label
        s = s.replace("`", "").strip().lower()
        s = re.sub(r"[^\w\- ]", "", s).replace(" ", "-")
        n = seen.get(s, 0)
        seen[s] = n + 1
        slugs.add(s if n == 0 else f"{s}-{n}")
    return slugs


# ── layout ──────────────────────────────────────────────────────────────────
# Everything the convention owns nests under docs/decisions/ (the umbrella) so the three
# lifecycle dirs and the INDEX never collide with the repo's other docs/. `root` is docs/;
# other repo docs (threat-model.md, …) stay its direct children and keep their auto-links.
def decisions_dir(root: Path) -> Path:
    return root / "decisions"


def accepted_dir(root: Path) -> Path:
    return root / "decisions" / "accepted"


def archived_dir(root: Path) -> Path:
    return root / "decisions" / "archived"


def drafts_dir(root: Path) -> Path:
    return root / "decisions" / "drafts"


def index_path(root: Path) -> Path:
    return root / "decisions" / "INDEX.md"


# ── parsing ─────────────────────────────────────────────────────────────────
def _consume_block_scalar(
    lines: list[str], start: int, key_indent: int, folded: bool
) -> tuple[str, int]:
    """Consume a YAML block scalar (folded `>` / literal `|`) whose `key:` line sits at
    `key_indent`. Continuation lines are those indented past `key_indent`; the first
    such line sets the block's indentation, which is stripped from every line. Returns
    (joined text, index of the first line after the block)."""
    block: list[str] = []
    indent: int | None = None
    idx = start
    while idx < len(lines):
        raw = lines[idx]
        if not raw.strip():
            block.append("")
            idx += 1
            continue
        cur_indent = len(raw) - len(raw.lstrip(" "))
        if cur_indent <= key_indent:
            break
        if indent is None:
            indent = cur_indent
        block.append(raw[indent:])
        idx += 1
    while block and block[-1] == "":
        block.pop()
    if not folded:
        return "\n".join(block), idx
    paragraphs, para = [], []
    for line in block:
        if line == "":
            if para:
                paragraphs.append(" ".join(para))
                para = []
        else:
            para.append(line)
    if para:
        paragraphs.append(" ".join(para))
    return "\n\n".join(paragraphs), idx


def parse_front_matter(text: str) -> dict:
    if not text.startswith("---"):
        raise ValueError("missing front-matter")
    end = text.index("\n---", 3)
    lines = text[3:end].splitlines()
    data: dict = {}
    idx = 0
    while idx < len(lines):
        raw = lines[idx]
        line = raw.split(" #", 1)[0].rstrip()
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            idx += 1
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        block = BLOCK_SCALAR_RE.match(val)
        if block:
            key_indent = len(raw) - len(raw.lstrip(" "))
            folded = block.group(1) == ">"
            data[key], idx = _consume_block_scalar(lines, idx + 1, key_indent, folded)
            continue
        if val in ("", "null", "~"):
            data[key] = None if val in ("null", "~") else ""
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = [i.strip().strip('"').strip("'") for i in inner.split(",") if i.strip()]
        else:
            data[key] = val.strip('"').strip("'")
        idx += 1
    return data


def front_matter_errors(recs: list[dict], drafts: list[dict]) -> list[str]:
    """Plain-scalar YAML hazards that a spec-compliant parser (e.g. GitHub's renderer)
    rejects but the tolerant parser above accepts — chiefly an unquoted ": " inside a
    value, which YAML reads as a nested mapping and errors on mid-scalar."""
    errs = []
    for r in recs + drafts:
        path = r["_path"]
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        lines = text[3 : text.index("\n---", 3)].splitlines()
        idx = 0
        while idx < len(lines):
            raw = lines[idx]
            line = raw.split(" #", 1)[0].rstrip()
            idx += 1
            if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
                continue
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip()
            if BLOCK_SCALAR_RE.match(val):  # block scalars may contain anything
                key_indent = len(raw) - len(raw.lstrip(" "))
                while idx < len(lines):
                    nxt = lines[idx]
                    if nxt.strip() and (len(nxt) - len(nxt.lstrip(" "))) <= key_indent:
                        break
                    idx += 1
                continue
            if not val or val in ("null", "~") or val[0] in "[{":
                continue
            if val[0] in "\"'":
                if len(val) < 2 or val[-1] != val[0]:
                    errs.append(f"{path.name}: front-matter '{key}' has an unbalanced quote")
                continue
            if ": " in val or val.endswith(":"):
                errs.append(
                    f"{path.name}: front-matter '{key}' has an unquoted ':' in its value —"
                    " strict YAML parsers (GitHub) reject this; quote the value or rephrase"
                )
    return errs


def split_front_matter(text: str) -> tuple[str, str]:
    """(head, body). Files without front-matter (e.g. threat-model.md) are all body."""
    if not text.startswith("---"):
        return "", text
    fence = text.index("\n---", 3)
    nl = text.index("\n", fence + 1)
    return text[: nl + 1], text[nl + 1 :]


def set_field(text: str, key: str, value: str) -> str:
    head, body = split_front_matter(text)
    line = f"{key}: {value}" if value != "" else f"{key}:"  # empty -> no trailing space
    pat = re.compile(rf"^{re.escape(key)}:.*$", re.M)
    if pat.search(head):
        head = pat.sub(lambda _: line, head, count=1)
    else:
        head = head[:-4] + line + "\n---\n"
    return head + body


def drop_field(text: str, key: str) -> str:
    head, body = split_front_matter(text)
    return re.sub(rf"^{re.escape(key)}:.*\n", "", head, flags=re.M) + body


# ── loading ─────────────────────────────────────────────────────────────────
def _meta(p: Path, **extra) -> dict:
    text = p.read_text(encoding="utf-8")
    fm = parse_front_matter(text)
    fm.update(_file=p.name, _path=p, _text=text, **extra)
    return fm


def load_records(root: Path) -> list[dict]:
    """Numbered records: accepted/<type>/*.md (typed) and archived/*.md (flat)."""
    recs = []
    for p in sorted(accepted_dir(root).rglob("*.md")):
        if RECORD_RE.match(p.name):
            recs.append(_meta(p, _lifecycle="decisions", _typedir=p.parent.name))
    base = archived_dir(root)
    if base.exists():
        for p in sorted(base.glob("*.md")):
            if RECORD_RE.match(p.name):
                recs.append(_meta(p, _lifecycle="archived", _typedir=None))
    return recs


def load_drafts(root: Path) -> list[dict]:
    base = drafts_dir(root)
    return (
        [_meta(p) for p in sorted(base.glob("*.md")) if not p.name.startswith("_")]
        if base.exists()
        else []
    )


def ref_map(recs: list[dict], drafts: list[dict]) -> dict:
    """ID -> path, for both counters and draft IDs (the universe of cross-ref targets)."""
    m = {r["id"]: r["_path"] for r in recs}
    for d in drafts:
        m.setdefault(d.get("id"), d["_path"])
    return m


def reference_targets(
    root: Path, recs: list[dict], drafts: list[dict]
) -> list[tuple[Path, str | None]]:
    """Every docs/*.md whose body carries generated cross-reference links — records,
    drafts, and any other doc (threat-model, roadmap, …). Pairs (path, own_id); own_id is
    the record/draft ID (so it doesn't self-link), else None."""
    own = {r["_path"]: r["id"] for r in recs}
    own.update({d["_path"]: d.get("id") for d in drafts})
    return [(p, own.get(p)) for p in _md_files(root)]


def next_counter(recs: list[dict], root: Path | None = None) -> str:
    """The next counter free in this tree — and, given `root`, on origin/main as well.

    Minting is a write, which is why this asks and `check` only warns: by the time
    anything looks at the number, the record has been renamed, its H1 rewritten and
    every inbound link repathed, so a counter that is free only here costs far more to
    undo than to avoid. An absent ref falls back to this tree alone, exactly as before.

    Stepping over a counter origin/main holds leaves what reads as a hole until the
    rebase; `validate_records` is told to read those as held rather than missing.
    """
    nums = {int(r["id"]) for r in recs if str(r.get("id", "")).isdigit()}
    if root is not None:
        nums |= {int(c) for c in upstream_ids(root)[0] if c.isdigit()}
    return f"{(max(nums) + 1) if nums else 1:04d}"


# ── links ───────────────────────────────────────────────────────────────────
def rel(target: Path, start: Path) -> str:
    return os.path.relpath(target, start).replace(os.sep, "/")


def relink(text: str, refs: dict, own_id: str | None, self_dir: Path) -> str:
    """Render inline-code IDs (counters and draft tags) as relative links, looked up
    from `refs`. Refresh existing links first (moves self-heal), then linkify bare
    ones. Front-matter untouched. Idempotent."""
    head, body = split_front_matter(text)

    def fix_existing(m: re.Match) -> str:
        lm = LABEL_ID_RE.fullmatch(m.group(1).strip())
        if lm and lm.group(1) in refs and lm.group(1) != own_id:
            rid = lm.group(1)
            return f"[`{rid}`]({rel(refs[rid], self_dir)})"
        return m.group(0)

    def add_link(m: re.Match) -> str:
        rid = m.group(1)
        if rid == own_id or rid not in refs:
            return m.group(0)
        return f"[`{rid}`]({rel(refs[rid], self_dir)})"

    body = LINK_RE.sub(fix_existing, body)
    body = ID_RE.sub(add_link, body)
    return head + body


def check_links(root: Path, recs: list[dict], drafts: list[dict], refs: dict) -> list[str]:
    errs = []
    files = [
        (p.name, p, p.read_text(encoding="utf-8")) for p, _ in reference_targets(root, recs, drafts)
    ]
    index = index_path(root)
    if index.exists():
        files.append((index.name, index, index.read_text(encoding="utf-8")))
    anchors_cache: dict[Path, set[str]] = {}

    def anchors_of(p: Path) -> set[str]:
        rp = p.resolve()
        if rp not in anchors_cache:
            anchors_cache[rp] = heading_anchors(rp.read_text(encoding="utf-8"))
        return anchors_cache[rp]

    for name, path, text in files:
        for _, target in LINK_RE.findall(strip_code(text)):
            t, _sep, frag = target.partition("#")
            t = t.strip()
            if re.match(r"[a-z][a-z0-9+.-]*://", t) or t.startswith("mailto:"):
                continue
            if "…" in target or " " in t:
                continue
            if not t and not frag:
                continue
            dest = path.parent / t if t else path
            if not dest.exists():
                errs.append(f"{name}: broken link -> {target}")
                continue
            if frag and dest.suffix == ".md" and frag not in anchors_of(dest):
                errs.append(f"{name}: broken anchor -> {target}")
                continue
            if not t:
                continue
            cm = FILE_ID_RE.match(os.path.basename(t))
            if cm:
                rid = cm.group(1)
                if rid not in refs:
                    errs.append(f"{name}: link to unknown ID {rid} ({target})")
                elif dest.resolve() != refs[rid].resolve():
                    errs.append(f"{name}: stale link for {rid} -> {target}")
    return errs


# ── validation ──────────────────────────────────────────────────────────────
def validate_records(recs: list[dict], refs: dict, held_upstream: dict | None = None) -> list[str]:
    errs, ids = [], {}
    for r in recs:
        rid = r.get("id")
        if rid in ids:
            errs.append(f"duplicate ID {rid}: {r['_file']} and {ids[rid]['_file']}")
        ids[rid] = r
        summary = r.get("summary")
        if summary and BLOCK_SCALAR_RE.match(str(summary).strip()):
            errs.append(f"{r['_file']}: summary is an unresolved YAML scalar indicator {summary!r}")
        if r["_lifecycle"] == "decisions":
            if not TYPE_RE.match(str(r.get("type") or "")):
                errs.append(f"{r['_file']}: type {r.get('type')!r} must be a lowercase slug")
            elif r["_typedir"] != r.get("type"):
                errs.append(
                    f"{r['_file']}: in accepted/{r['_typedir']}/ but type is {r.get('type')}"
                )
            if r.get("status") not in ACTIVE_STATUS:
                errs.append(
                    f"{r['_file']}: in accepted/ but status {r.get('status')} is not accepted"
                )
        elif r.get("status") not in RETIRED_STATUS:
            errs.append(f"{r['_file']}: in archived/ but status {r.get('status')} is not retired")
    nums = sorted(int(r["id"]) for r in recs if str(r.get("id", "")).isdigit())
    if nums:
        # A counter origin/main already holds is not a hole. The record exists — it is
        # simply not on this branch yet — and the rebase closes the sequence. That is
        # the only thing which explains a gap: a number neither tree has is still a
        # missing record and still fails. With no ref on disk the set is empty and this
        # is the rule it has always been, which is also what a fresh clone sees.
        held = {int(c) for c in (held_upstream or {}) if str(c).isdigit()}
        missing = sorted(set(range(1, nums[-1] + 1)) - set(nums) - held)
        if missing:
            errs.append("gap in counters — missing " + ", ".join(f"{n:04d}" for n in missing))
    for r in recs:
        for ref in (r.get("relates_to") or []) + [r.get("supersedes"), r.get("superseded_by")]:
            if ref and ref not in refs:
                errs.append(f"{r['_file']}: dangling reference {ref}")
    return errs


def validate_drafts(root: Path, refs: dict, drafts: list[dict]) -> list[str]:
    errs, seen = [], {}
    for d in drafts:
        did = d.get("id")
        if not did or not DRAFT_ID_RE.match(str(did)):
            errs.append(f"drafts/{d['_file']}: ID must be 4 UPPERCASE letters (got {did!r})")
        elif did in seen:
            errs.append(f"drafts/{d['_file']}: duplicate draft ID {did} (also {seen[did]})")
        else:
            seen[did] = d["_file"]
        if not TYPE_RE.match(str(d.get("type") or "")):
            errs.append(f"drafts/{d['_file']}: type {d.get('type')!r} must be a lowercase slug")
        for ref in (d.get("relates_to") or []) + [d.get("supersedes"), d.get("superseded_by")]:
            if ref and ref not in refs:
                errs.append(f"drafts/{d['_file']}: references unknown ID {ref}")
    return errs


def warn_unknown_types(root: Path, drafts: list[dict]) -> list[str]:
    """Non-blocking: a draft whose type has no accepted/<type>/ dir yet — likely a typo,
    or a deliberately new type (its dir is created on promotion)."""
    base = accepted_dir(root)
    known = {p.name for p in base.iterdir() if p.is_dir()} if base.exists() else set()
    return [
        f"WARN drafts/{d['_file']}: new type {d['type']!r} — no accepted/{d['type']}/ yet "
        "(typo? otherwise it's created on promotion)"
        for d in drafts
        if TYPE_RE.match(str(d.get("type") or "")) and d.get("type") not in known
    ]


# ── upstream collisions ─────────────────────────────────────────────────────
# Every check above reads one tree, so a duplicate ID can only be seen once both
# copies are in it: after a rebase or a merge. On a branch the ID you minted is
# unique and everything is green, and the collision comes into being when the trees
# meet — by which point the record is written and cross-referenced. This asks the
# question one tree earlier, against the origin/main already on disk.
#
# It warns and never fails: origin/main moves under a branch on every fetch, so a gate
# here would fail correct work for a reason its author cannot act on. It never fetches:
# a hook that reaches the network is a hook people turn off. And when the ref is simply
# not there — a fresh clone, an offline machine, a CI checkout that took only the
# branch — it reports nothing, because a missing ref is not evidence of anything.
#
# lanh-ai runs the same shape over its PRD and migration counters from a shared
# scripts/upstream.py. This copy is deliberate: a skill has to run in a repo that has
# none of that. Keep the two in step.
UPSTREAM_REF = "origin/main"


def _git(directory: Path, *args: str) -> str | None:
    """stdout of a read-only git command, or None for any non-zero exit. Every caller
    treats failure as "no answer", so the reasons collapse: no git, no work tree, an
    unfetched ref, a path absent from that tree."""
    try:
        done = subprocess.run(
            ["git", "-C", str(directory), *args], capture_output=True, text=True, check=False
        )
    except OSError:
        return None
    return done.stdout.rstrip("\n") if done.returncode == 0 else None


def upstream_files(directory: Path, ref: str = UPSTREAM_REF) -> list[str] | None:
    """Every file `ref` holds under `directory`, posix-relative to it, recursive.

    None means there is nothing to compare against — not a git work tree, or `ref` is
    not fetched here — and callers fall silent on it. An empty list is different: the
    ref is there and holds no such directory.

    Read-only plumbing against the object store; nothing is checked out and no ref
    moves, so this is safe to run from any of a repo's worktrees.
    """
    if not directory.is_dir():
        return None
    root = _git(directory, "rev-parse", "--show-toplevel")
    if root is None:
        return None
    rel = directory.resolve().relative_to(Path(root).resolve()).as_posix()
    if _git(directory, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}") is None:
        return None
    # --full-tree, or ls-tree quietly limits its output to the cwd's own prefix, which
    # — run from inside the very directory it was handed as the tree-ish — is nothing.
    listing = _git(directory, "ls-tree", "-r", "--full-tree", "--name-only", "-z", f"{ref}:{rel}")
    return [] if listing is None else [name for name in listing.split("\0") if name]


def collision_warnings(
    family: str,
    local: dict,
    upstream: dict,
    free: str | None = None,
    fix: str = "renumber",
) -> list[str]:
    """One WARN line per ID both trees use for a *different* file. Same ID and same
    filename is that record, edited or moved — not a collision. `free`, where the family
    numbers itself, is the ID neither tree has taken, so the fix reads as an instruction
    rather than a lookup."""
    return [
        f"WARN {family}: {ident} is taken on {UPSTREAM_REF} by {upstream[ident]}, and here by "
        f"{name} — {f'{fix} to {free}' if free else f'{fix} it'} before the trees meet"
        for ident, name in sorted(local.items())
        if upstream.get(ident) not in (None, name)
    ]


def next_free_counter(ids: set) -> str | None:
    """One past the highest counter either tree has used. Both trees deliberately: the
    number free on origin/main alone can be the one this branch already took, and a fix
    that collides again is worse than none."""
    nums = {int(i) for i in ids if str(i).isdigit()}
    return f"{max(nums) + 1:04d}" if nums else None


def ids_by_family(paths: list[str]) -> tuple[dict, dict]:
    """(counter -> filename, mnemonic -> filename), over paths relative to decisions/.

    Filenames only — no record is parsed, on either side — so one whose front-matter is
    still being written reads like any other, and the same reading serves both trees.
    """
    counters: dict = {}
    mnemonics: dict = {}
    for rel in sorted(paths):
        head, _, base = rel.rpartition("/")
        top = head.split("/")[0]
        if top == "drafts" and not base.startswith("_"):
            if (m := FILE_ID_RE.match(base)) and DRAFT_ID_RE.match(m.group(1)):
                mnemonics.setdefault(m.group(1), base)
        elif top in ("accepted", "archived") and RECORD_RE.match(base):
            counters.setdefault(base[:4], base)
    return counters, mnemonics


def local_ids(root: Path) -> tuple[dict, dict]:
    base = decisions_dir(root)
    if not base.is_dir():
        return {}, {}
    return ids_by_family([p.relative_to(base).as_posix() for p in sorted(base.rglob("*.md"))])


def upstream_ids(root: Path) -> tuple[dict, dict]:
    """What origin/main gives each counter and draft ID. Empty when that ref is not on
    disk, so every caller then behaves exactly as it did before any of this existed."""
    names = upstream_files(decisions_dir(root))
    return ({}, {}) if names is None else ids_by_family(names)


def warn_upstream_collisions(local: tuple[dict, dict], upstream: tuple[dict, dict]) -> list[str]:
    """Counters and draft IDs origin/main already gives to a *different* filename. A
    record that moved accepted/ -> archived/ keeps its filename and is correctly silent."""
    return collision_warnings(
        "decisions",
        local[0],
        upstream[0],
        free=next_free_counter(set(local[0]) | set(upstream[0])),
    ) + collision_warnings("drafts", local[1], upstream[1], fix="re-mint")


def body_ref_ids(text: str) -> set:
    """Every ID a record's body cites, bare (`CONF`) or already markdown-linked
    ([`CONF`](...)). `build --relink` turns every bare ref into a link, so anything that
    reads only the bare form goes blind the moment a build has run."""
    _, body = split_front_matter(text)
    ids = set(ID_RE.findall(body))
    for label, _ in LINK_RE.findall(body):
        m = LABEL_ID_RE.fullmatch(label.strip())
        if m:
            ids.add(m.group(1))
    return ids


def draft_references(d: dict, draft_ids: set) -> set:
    """The draft IDs this record points at — and that would survive into a decision:
    front-matter relates_to/supersedes/superseded_by, plus body refs bare or linked."""
    refs = set(d.get("relates_to") or [])
    for k in ("supersedes", "superseded_by"):
        if d.get(k):
            refs.add(d[k])
    return (refs | body_ref_ids(d["_text"])) & draft_ids


def validate_no_breach(recs: list[dict], drafts: list[dict]) -> list[str]:
    """An accepted/retired decision must NOT reference a draft — that would bind a
    finalized record to unfinalized WIP. Promote the draft first."""
    draft_ids = {d.get("id") for d in drafts}
    errs = []
    for r in recs:
        for b in sorted(draft_references(r, draft_ids)):
            errs.append(f"{r['_file']}: decision references draft {b} (breach — promote {b} first)")
    return errs


def prose_unknown_counters(
    root: Path, recs: list[dict], drafts: list[dict], refs: dict
) -> list[str]:
    """Un-linkified numeric counters in prose must resolve (4-letter tokens are not
    flagged — they are ordinary words unless they match a known draft ID)."""
    errs = []
    for path, own in reference_targets(root, recs, drafts):
        _, body = split_front_matter(path.read_text(encoding="utf-8"))
        for cid in COUNTER_RE.findall(body):
            if cid != own and cid not in refs:
                errs.append(f"{path.name}: prose references unknown record {cid}")
    return errs


# ── render ──────────────────────────────────────────────────────────────────
def render_index(recs: list[dict], root: Path) -> str:
    recs = sorted(recs, key=lambda r: r["id"])
    base = decisions_dir(root)  # INDEX.md lives here; links are relative to it
    rows = (
        "\n".join(
            f"| [{r['id']}]({rel(r['_path'], base)}) | {r.get('type', '')} | {r.get('summary', '')}"
            f" | {STATUS_ICON.get(r.get('status', ''), '—')} | {', '.join(r.get('tags') or [])} |"
            for r in recs
        )
        or "| _none_ | | _no decisions yet — promote a draft_ | | |"
    )
    return f"""# Decision Records — Index

<!-- GENERATED by scripts/decisions.py — do not edit by hand. -->

**Agents read this file first**, then load only the records relevant to the task
(filter on `type`, `status`, `tags`). Skip `archived/` (`superseded`/`deprecated`) unless
tracing why a decision changed. Records are held firm once `accepted` — course changes only by
supersession; decider-approved maintenance edits are allowed.

## Identity & references
- Identity is the global counter (`0001`, …), assigned in creation order. Permanent;
  the only thing a human writes to cross-reference. Drafts use a 4-UPPERCASE-letter ID
  instead — a mnemonic of the draft's topic.
- Reference by ID. Path links — each ID rendered as a markdown link to its file — are
  **generated** by `scripts/decisions.py build --relink` and refreshed on every move,
  so they stay correct; never **hand-author** a path.
- `type` is an open lowercase slug — the `accepted/<type>/` subdirs are the set (e.g.
  architecture, product, security; or policy, legal, finance). For a decision it equals its
  directory and `status` selects the lifecycle dir; the tool enforces placement, not a fixed list.

## Status: 🟢 accepted · ⚪ deprecated · 🔵 superseded

| ID | Type | Summary | Status | Tags |
|:---|:-----|:--------|:------:|:-----|
{rows}

## Layout
Everything lives under `docs/decisions/`:

- `accepted/<type>/`: accepted numbered records, one subdir per type.
- `archived/`: retired records (`superseded`/`deprecated`), flat.
- `drafts/`: 4-letter WIP candidates, flat and not indexed.

Moving a record never breaks references, whether you reclassify it or retire it into `archived/`.
Records are keyed by ID, not path, and `build --relink` refreshes the generated links.
"""


# ── promote / rename ────────────────────────────────────────────────────────
def _md_files(root: Path) -> list[Path]:
    """Every markdown file under docs/ whose links the tool manages — all `*.md` EXCEPT
    template files (`_*.md`) and the generated `INDEX.md`."""
    return [
        p for p in sorted(root.rglob("*.md")) if not p.name.startswith("_") and p.name != "INDEX.md"
    ]


def heading_for(nid: str, title: str) -> str:
    """`# NNNN — <title>`. A title carrying its own em-dash renders that dash as a colon,
    so the heading holds exactly one (front-matter "Egress proxy — the outbound
    chokepoint" heads 0033 as `# 0033 — Egress proxy: the outbound chokepoint`)."""
    return f"# {nid} — {title.replace(' — ', ': ', 1)}"


def retitle_heading(text: str, old_id: str, new_id: str, title: str = "") -> tuple[str, str | None]:
    """Carry an ID change into the record's H1 — every accepted record reads
    `# NNNN — <title>`, so a promoted draft whose heading still leads with its mnemonic
    is off-convention. Returns (text, note) where a note flags the unusual shapes."""
    head, body = split_front_matter(text)
    lines = body.splitlines(keepends=True)
    lead = re.compile(rf"`?({re.escape(old_id)}|{re.escape(new_id)})`?(?=$|[ \t])")
    for i, bare in enumerate(strip_fences(body).splitlines()):  # a `#` in a fence is not an H1
        m = re.match(r"^#[ \t]+(.*?)[ \t]*$", bare)
        if not m:
            continue
        rest, nl = m.group(1), "\n" if lines[i].endswith("\n") else ""
        hit = lead.match(rest)
        if hit and hit.group(1) == new_id:
            return text, None  # already numbered
        if hit:
            lines[i] = f"# {new_id}{rest[hit.end():]}{nl}"
            return head + "".join(lines), None
        lines[i] = f"# {new_id} — {rest}{nl}"
        return head + "".join(lines), f"H1 did not lead with {old_id}; prefixed {new_id} — check it"
    if not title:
        return text, f"no H1 found — add one reading `# {new_id} — <title>`"
    return head + heading_for(new_id, title) + "\n\n" + body.lstrip("\n"), "inserted the H1"


def repath_links(text: str, old_dir: Path, new_dir: Path) -> str:
    """Re-express the body's hand-authored relative links so they resolve from `new_dir`.
    Promotion moves a record a directory deeper (drafts/ -> accepted/<type>/), so every
    path a human wrote — `../../glossary.md`, a research memo, a repo-root script — needs
    another `../`. ID links are regenerated by `build --relink`; these never were, and
    promotion used to leave them one level short."""
    head, body = split_front_matter(text)
    spans = code_regions(body)

    def moved(target: str) -> str | None:
        path, sep, frag = target.partition("#")
        if not path or path.startswith("/") or re.match(r"[a-z][a-z0-9+.-]*:", path):
            return None  # anchor-only, absolute, or a URL/mailto — not ours to move
        if "…" in target or " " in path:
            return None  # a placeholder or a link title, not a path
        out = os.path.relpath(os.path.normpath(old_dir / path), new_dir).replace(os.sep, "/")
        return (out + "/" if path.endswith("/") else out) + sep + frag

    def fix(m: re.Match) -> str:
        label, target = m.group(1), m.group(2).strip()
        new_target = moved(target)
        if new_target is None or new_target == target:
            return m.group(0)
        # a link labelled with its own path (`[`../../deploy.md`](../../deploy.md)`) moves too
        if label.strip().strip("`") == target:
            label = label.replace(target, new_target)
        return f"[{label}]({new_target})"

    return head + sub_outside(LINK_RE, fix, body, spans, group=2)


def rewrite_reference(root: Path, old: str, new: str) -> None:
    """Repoint every reference from ID `old` to ID `new` across the tree — front-matter
    ref fields (de-duplicated), inline-code body refs, and, for a draft mnemonic, the bare
    word in prose. Used when promotion changes a draft's ID so inbound references don't
    dangle. `build --relink` then re-paths them."""
    link = re.compile(r"\[`" + re.escape(old) + r"`\]\([^)]*\)")
    bare = re.compile(r"`" + re.escape(old) + r"`")
    # A mnemonic also reads as an ordinary word, so the prose sweep stays out of code
    # (fences and inline spans) and out of link targets — an `AUTH = "auth"` in a fenced
    # example is an identifier, and a path is a path.
    prose = re.compile(r"\b" + re.escape(old) + r"\b") if DRAFT_ID_RE.match(old) else None

    def fix_field(m: re.Match) -> str:
        key, val = m.group(1), m.group(2).strip()
        if val.startswith("[") and val.endswith("]"):
            out: list[str] = []
            for i in (x.strip().strip('"').strip("'") for x in val[1:-1].split(",") if x.strip()):
                i = new if i == old else i
                if i not in out:
                    out.append(i)
            val = "[" + ", ".join(f'"{x}"' for x in out) + "]"
        elif val.strip('"').strip("'") == old:
            val = f'"{new}"'
        return f"{key} {val}" if val else key  # an empty value keeps NO trailing space

    for p in _md_files(root):
        t = p.read_text(encoding="utf-8")
        head, body = split_front_matter(t)
        head = re.sub(
            r"^(relates_to:|supersedes:|superseded_by:)(.*)$", fix_field, head, flags=re.M
        )
        body = bare.sub(f"`{new}`", link.sub(f"`{new}`", body))
        if prose:
            # front-matter prose too — a summary reading "behind AUTH's door" is a reference.
            # `id:` is exempt: it is the file's own identity, not a reference to another.
            head = "\n".join(
                ln if ln.startswith("id:") else prose.sub(new, ln) for ln in head.split("\n")
            )
            spans = code_regions(body) + [m.span(2) for m in LINK_RE.finditer(body)]
            body = sub_outside(prose, lambda _: new, body, spans)
        if head + body != t:
            p.write_text(head + body, encoding="utf-8")


def rewrite_path(root: Path, src: Path, dest: Path) -> None:
    """Repoint a spelled-out path to a record the move invalidated — `docs/decisions/
    drafts/MEET-meeting-surface.md` in a research memo. The convention says reference by
    ID and never hand-author a path, but prose that does is left dangling otherwise. Unlike
    a mnemonic a full path is unambiguous, so this reaches inside code spans too — that is
    where such a path is usually written."""
    old, new = rel(src, root), rel(dest, root)  # docs-relative: any longer prefix survives
    for p in _md_files(root):
        t = p.read_text(encoding="utf-8")
        if old in t:
            p.write_text(t.replace(old, new), encoding="utf-8")


def match_drafts(root: Path, query: str) -> list[Path]:
    drafts = (
        [p for p in sorted(drafts_dir(root).glob("*.md")) if not p.name.startswith("_")]
        if drafts_dir(root).exists()
        else []
    )
    q = query.lower().strip()
    for p in drafts:  # an exact draft-ID match wins outright (no substring noise)
        if q == str(parse_front_matter(p.read_text(encoding="utf-8")).get("id", "")).lower():
            return [p]
    hits = []
    for p in drafts:
        fm = parse_front_matter(p.read_text(encoding="utf-8"))
        hay = f"{fm.get('id', '')} {fm.get('title', '')} {p.stem}".lower()
        if q in hay:
            hits.append(p)
    if not hits:
        names = {p.stem.lower(): p for p in drafts}
        hits = [names[m] for m in difflib.get_close_matches(q, list(names), n=5, cutoff=0.4)]
    seen, out = set(), []
    for p in hits:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def select_draft(root: Path, query: str, input_fn=input) -> tuple[Path | None, str | None]:
    """Resolve a draft from a fuzzy query, prompting to disambiguate if several match."""
    matches = match_drafts(root, query)
    if not matches:
        return None, f"no draft matches {query!r}"
    if len(matches) == 1:
        return matches[0], None
    for i, p in enumerate(matches, 1):
        print(f"  [{i}] {p.name}", file=sys.stderr)
    try:
        raw = input_fn(f"pick a candidate [1-{len(matches)}]: ").strip()
    except EOFError:
        return None, "ambiguous match and no input — pass the exact draft ID"
    if not raw.isdigit() or not (1 <= int(raw) <= len(matches)):
        return None, "no candidate selected"
    return matches[int(raw) - 1], None


def add_to_list_field(text: str, key: str, value: str) -> str:
    head, _ = split_front_matter(text)
    m = re.search(rf"^{key}:(.*)$", head, re.M)
    items: list[str] = []
    if m:
        cur = m.group(1).strip()
        if cur.startswith("[") and cur.endswith("]"):
            items = [x.strip().strip('"').strip("'") for x in cur[1:-1].split(",") if x.strip()]
        elif cur not in ("", "null", "~"):
            items = [cur.strip('"').strip("'")]
    if value not in items:
        items.append(value)
    return set_field(text, key, "[" + ", ".join(f'"{i}"' for i in items) + "]")


def remove_from_list_field(text: str, key: str, value: str) -> str:
    head, _ = split_front_matter(text)
    m = re.search(rf"^{key}:(.*)$", head, re.M)
    if not m:
        return text
    cur = m.group(1).strip()
    if cur.startswith("[") and cur.endswith("]"):
        items = [x.strip().strip('"').strip("'") for x in cur[1:-1].split(",") if x.strip()]
        items = [i for i in items if i != value]
        return set_field(text, key, "[" + ", ".join(f'"{i}"' for i in items) + "]")
    if cur.strip('"').strip("'") == value:
        return set_field(text, key, "")  # blank, not null (mdformat-stable; reads the same)
    return text


def classify_refs(d: dict, draft_ids: set, decision_ids: set, in_set: set) -> dict:
    """Bucket a draft's references to things OUTSIDE the promote set:
    deref          - front-matter relates_to/superseded_by to a draft (invertible)
    block          - `supersedes` to a draft, or a prose `DRFT` ref (can't invert)
    supersedes_dec - `supersedes` to an existing decision (the --allow-replace case)"""
    sup = d.get("supersedes")
    relates = (set(d.get("relates_to") or []) & draft_ids) - in_set
    superby = (({d["superseded_by"]} if d.get("superseded_by") else set()) & draft_ids) - in_set
    supdraft = (({sup} if sup else set()) & draft_ids) - in_set
    prose = (body_ref_ids(d["_text"]) & draft_ids) - in_set
    block = supdraft | prose
    return {
        "deref": (relates | superby) - block,
        "block": block,
        "supersedes_dec": ({sup} & decision_ids) if sup else set(),
    }


def blocking_closure(by_id: dict, seeds: set, decision_ids: set) -> set:
    """Seeds + every draft reachable by BLOCKING edges — the minimal set that must be
    promoted together (dereferenceable edges no longer pull drafts in)."""
    draft_ids, seen, stack = set(by_id), set(seeds), list(seeds)
    while stack:
        for ref in classify_refs(by_id[stack.pop()], draft_ids, decision_ids, set())["block"]:
            if ref not in seen:
                seen.add(ref)
                stack.append(ref)
    return seen


def _suggested_order(bclosure: set, seeds: list) -> list:
    """The order a suggested command should promote in: the requested drafts first, in the
    order they were given, then what the blocking set pulled in. Counters follow this order,
    so re-running the suggestion keeps the counters the caller asked for."""
    return list(seeds) + sorted(bclosure - set(seeds))


def _highlight(ids: list, seeds: list) -> str:
    return "\n".join(f"  → {i}  (requested)" if i in seeds else f"    {i}" for i in ids)


def _blocking_message(bclosure: set, seeds: list, block: set) -> str:
    ordered = _suggested_order(bclosure, seeds)
    cmd = "python scripts/decisions.py promote " + " ".join(ordered)
    prompt = (
        f"Promote draft(s) {', '.join(seeds)} with scripts/decisions.py. They are "
        f"blocked: as accepted decisions they would reference draft(s) "
        f"{', '.join(sorted(block))} via prose or `supersedes`, which cannot be "
        f"dereferenced. Either co-promote the whole set — `{cmd}` — or restructure the "
        f"draft(s) to cite only accepted decisions (counters). Then run "
        f"`python scripts/decisions.py check`."
    )
    return (
        "blocked: a promoted decision would reference draft(s) via prose or `supersedes`,\n"
        "which can't be dereferenced. Promote the whole blocking set together\n"
        "(counters are assigned in the order listed):\n"
        + _highlight(ordered, seeds)
        + f"\n\nRun:\n  {cmd}\n"
        + "\nOr copy this prompt to an agent to fix it:\n"
        + "─" * 70
        + "\n"
        + prompt
        + "\n"
        + "─" * 70
    )


def _deref_message(deref: set, seeds: list) -> str:
    cmd = "python scripts/decisions.py promote " + " ".join(seeds) + " --deref"
    return (
        "dereferenceable: the only cross-draft refs are front-matter "
        f"relates_to/superseded_by to {', '.join(sorted(deref))}.\n"
        "Re-run with --deref to move those links onto the referenced draft(s) (they point\n"
        f"back once promoted):\n  {cmd}"
    )


def _allow_replace_message(need: set, seeds: list) -> str:
    cmd = "python scripts/decisions.py promote " + " ".join(seeds) + " --allow-replace"
    return (
        f"promoting {', '.join(seeds)} would supersede existing decision(s) "
        f"{', '.join(sorted(need))},\nwhich will be archived. Re-run with --allow-replace "
        f" to confirm:\n  {cmd}"
    )


def _do_deref(by_id: dict, order: list, mapping: dict) -> None:
    """Invert each dereferenceable edge: drop it from the promoted draft and record the
    draft's new counter on the referenced draft, restoring the link when that draft is
    later promoted. Mutates _text; writes the referenced (still-draft) files."""
    draft_ids, seeds, touched = set(by_id), set(order), set()
    for s in order:
        d, nid = by_id[s], mapping[s]
        for t in (set(d.get("relates_to") or []) & draft_ids) - seeds:
            d["_text"] = remove_from_list_field(d["_text"], "relates_to", t)
            by_id[t]["_text"] = add_to_list_field(by_id[t]["_text"], "relates_to", nid)
            touched.add(t)
        if d.get("superseded_by") in draft_ids and d.get("superseded_by") not in seeds:
            t = d["superseded_by"]
            d["_text"] = set_field(d["_text"], "superseded_by", "")  # blank, not null
            by_id[t]["_text"] = set_field(by_id[t]["_text"], "supersedes", f'"{nid}"')
            touched.add(t)
    for t in touched:
        by_id[t]["_path"].write_text(by_id[t]["_text"], encoding="utf-8")


def promote(
    root: Path, queries: list[str], deref: bool = False, allow_replace: bool = False, input_fn=input
) -> tuple[list[Path] | None, str | None]:
    """Promote draft(s) into decisions/ as the next counters, assigned in the order the
    queries were given — co-promoting `A B` makes A the lower counter. Refuses with
    actionable guidance when the set isn't self-contained; `--deref` inverts front-matter
    edges so a draft promotes alone; `--allow-replace` confirms archiving what it
    supersedes."""
    recs = load_records(root)
    by_id = {d["id"]: d for d in load_drafts(root)}
    decision_ids = {r["id"] for r in recs}

    order: list[str] = []  # argument order, deduped — the counters follow it
    for q in queries:
        src, err = select_draft(root, q, input_fn)
        if err:
            return None, err
        did = parse_front_matter(src.read_text(encoding="utf-8")).get("id")
        if did not in order:
            order.append(did)
    seeds = set(order)
    bad = [by_id[i]["_file"] for i in order if not TYPE_RE.match(str(by_id[i].get("type") or ""))]
    if bad:
        return None, f"invalid type in {', '.join(bad)}"

    deref_t, block_t, supersedes_dec = set(), set(), set()
    for s in order:
        c = classify_refs(by_id[s], set(by_id), decision_ids, seeds)
        deref_t |= c["deref"]
        block_t |= c["block"]
        supersedes_dec |= c["supersedes_dec"]
    deref_t -= block_t

    if block_t:
        msg = _blocking_message(blocking_closure(by_id, seeds, decision_ids), order, block_t)
        if deref:
            msg = (
                f"--deref can't proceed — blocked by prose/`supersedes` refs to "
                f"{', '.join(sorted(block_t))}.\n" + msg
            )
        return None, msg
    if supersedes_dec and not allow_replace:
        return None, _allow_replace_message(supersedes_dec, order)
    if deref_t and not deref:
        return None, _deref_message(deref_t, order)

    here = int(next_counter(recs))
    base = int(next_counter(recs, root))
    if base > here:
        # Otherwise the jump is a mystery: the tree ends at 0048 and the record comes
        # back 0050. Naming the reason also names the fix.
        print(
            f"origin/main holds {here:04d}"
            + (f"..{base - 1:04d}" if base - 1 > here else "")
            + f", so this starts at {base:04d}. Rebase to close the sequence.",
            file=sys.stderr,
        )
    mapping = {did: f"{base + i:04d}" for i, did in enumerate(order)}
    if deref:
        _do_deref(by_id, order, mapping)

    dests, moved = [], []
    for did, nid in mapping.items():
        d = by_id[did]
        slug = re.sub(r"^[A-Z]{4}-", "", d["_path"].stem)
        dest = accepted_dir(root) / d["type"] / f"{nid}-{slug}.md"
        text = set_field(d["_text"], "id", f'"{nid}"')
        text = set_field(text, "status", "accepted")  # the PR proposes; merge accepts
        for f in ("change_kind", "author"):  # draft-only fields
            text = drop_field(text, f)
        text, note = retitle_heading(text, did, nid, str(d.get("title") or ""))
        if note:
            print(f"{dest.name}: {note}", file=sys.stderr)
        text = repath_links(text, d["_path"].parent, dest.parent)  # accepted/ sits a level deeper
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        moved.append((d["_path"], dest))
        d["_path"].unlink()
        dests.append(dest)
    for src, dest in moved:  # a hand-authored path to the file the move invalidated
        rewrite_path(root, src, dest)
    for old, new in mapping.items():  # repoint refs (intra-set -> counters; inbound too)
        rewrite_reference(root, old, new)
        report_residual_mnemonics(root, old, new)

    for s in order:  # --allow-replace: archive each decision a promoted draft supersedes
        sup = by_id[s].get("supersedes")
        if allow_replace and sup in supersedes_dec:
            r = next(x for x in recs if x["id"] == sup)
            text = set_field(
                set_field(r["_text"], "status", "superseded"), "superseded_by", f'"{mapping[s]}"'
            )
            archived_dir(root).mkdir(parents=True, exist_ok=True)
            (archived_dir(root) / r["_file"]).write_text(text, encoding="utf-8")
            r["_path"].unlink()
    return dests, None


SWEEP_SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".mypy_cache", ".ruff_cache",
    ".pytest_cache", ".tox", "dist", "build", "target", ".next", "docs",
}  # fmt: skip
SWEEP_SUFFIXES = {
    ".py", ".rs", ".go", ".rb", ".java", ".kt", ".ts", ".tsx", ".js", ".jsx", ".sql", ".sh",
    ".toml", ".yaml", ".yml", ".json", ".cfg", ".ini", ".txt", ".md", ".html", ".css", "",
}  # fmt: skip


def residual_mnemonics(repo: Path, old: str, limit: int = 30) -> list[str]:
    """Where the retired mnemonic still reads OUTSIDE docs/ — code comments, justfile
    recipes, test names. REPORTED, never rewritten: a 4-letter mnemonic doubles as a
    plausible identifier (`AUTH = "auth"` in an enum, `MEET = "https://…"` as a scope
    constant), and renaming an identifier is not what promoting a record means."""
    word = re.compile(r"\b" + re.escape(old) + r"\b")
    hits: list[str] = []
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in sorted(dirnames) if d not in SWEEP_SKIP_DIRS]
        for name in sorted(filenames):
            p = Path(dirpath) / name
            if p.suffix not in SWEEP_SUFFIXES or p.is_symlink():
                continue
            try:
                if p.stat().st_size > 2_000_000:  # a mnemonic doesn't live in a blob
                    continue
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for n, line in enumerate(text.splitlines(), 1):
                if word.search(line):
                    hits.append(f"  {p.relative_to(repo)}:{n}: {line.strip()[:88]}")
    extra = len(hits) - limit
    return hits[:limit] + ([f"  …and {extra} more"] if extra > 0 else [])


def report_residual_mnemonics(root: Path, old: str, new: str) -> None:
    hits = residual_mnemonics(root.parent, old)
    if not hits:
        return
    print(
        f"\n{old} still reads outside docs/ — review by hand, and leave any identifier "
        f"named {old} alone (it is not the record):",
        file=sys.stderr,
    )
    print("\n".join(hits), file=sys.stderr)
    print(f"Each one that means the record should now read {new}.\n", file=sys.stderr)


def rename_draft(
    root: Path, query: str, new_id: str, input_fn=input
) -> tuple[Path | None, str | None]:
    """Change a draft's 4-letter ID (e.g. a random one -> a mnemonic), renaming the
    file and repointing every inbound reference. Counters (decisions) are immutable."""
    new = new_id.upper()
    if not DRAFT_ID_RE.match(new):
        return None, f"{new_id!r} is not a 4-letter ID (A-Z)"
    if new in {str(d.get("id", "")).upper() for d in load_drafts(root)}:
        return None, f"draft ID {new} is already in use"
    src, err = select_draft(root, query, input_fn)
    if err:
        return None, err
    old = parse_front_matter(src.read_text(encoding="utf-8")).get("id")
    if old == new:
        return None, f"draft already has ID {new}"
    slug = re.sub(r"^[A-Z]{4}-", "", src.stem)
    dest = src.with_name(f"{new}-{slug}.md")
    text = set_field(src.read_text(encoding="utf-8"), "id", new)
    text, note = retitle_heading(text, old, new)  # the H1 carries the ID too
    if note:
        print(f"{dest.name}: {note}", file=sys.stderr)
    src.unlink()  # remove first (case-insensitive FS safe)
    dest.write_text(text, encoding="utf-8")
    rewrite_reference(root, old, new)
    report_residual_mnemonics(root, old, new)
    return dest, None


def ensure_gitignored(repo: Path, pattern: str) -> None:
    """Add `pattern` to <repo>/.gitignore (creating the file if absent) unless already
    listed. The symlinked scripts/decisions.py is a machine-specific relative symlink into
    the skill's copy — each clone recreates it via `install`, so it must not be committed."""
    gi = repo / ".gitignore"
    existing = gi.read_text(encoding="utf-8") if gi.exists() else ""
    if pattern in existing.splitlines():
        print(f".gitignore already ignores {pattern}")
        return
    comment = "# decision-records: machine-specific symlink — recreate via `decisions.py install`"
    head = existing if not existing or existing.endswith("\n") else existing + "\n"
    sep = "\n" if existing.strip() else ""
    gi.write_text(head + sep + comment + "\n" + pattern + "\n", encoding="utf-8")
    print(f"{'created' if not existing else 'updated'} .gitignore — ignoring {pattern}")


def wire_entry_point(repo: Path, name: str, body: str) -> None:
    """Create a root entry-point file (README.md / AGENTS.md) as a placeholder linking the
    scaffold, but only when it's MISSING — a fresh or empty repo. An existing file is left
    untouched: the agent adopting the skill wires the link into it instead (see SKILL.md)."""
    f = repo / name
    if f.exists():
        return
    f.write_text(body, encoding="utf-8")
    print(f"created {name} (placeholder linking the decision records)")


def install(repo: Path) -> None:
    """Set up the convention in a repo: symlink the tool (and gitignore that symlink),
    scaffold the docs/ skeleton, wire a root README.md/AGENTS.md when absent, and add a
    pre-commit `check` hook in a git repo. `repo` is the project root — install does NOT
    search upward; it sets up exactly where you point it (CLI default: the CWD). Idempotent:
    only creates what's missing, never overwrites. Run the first time via the skill's own copy
    (`python .../decision-records/scripts/decisions.py install`); the symlink works after."""
    canonical = Path(__file__).resolve()
    skill = canonical.parent.parent  # scripts/ -> skill dir
    repo = repo.resolve()
    scripts = repo / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    link, rel = scripts / "decisions.py", os.path.relpath(canonical, scripts)
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(rel)
    print(f"symlinked scripts/decisions.py -> {rel}")
    ensure_gitignored(repo, "scripts/decisions.py")

    # scaffold docs/decisions/ (idempotent — never overwrites)
    docs = repo / "docs"
    for d in (accepted_dir(docs), archived_dir(docs), drafts_dir(docs)):
        d.mkdir(parents=True, exist_ok=True)
    for keep in (accepted_dir(docs) / ".gitkeep", archived_dir(docs) / ".gitkeep"):
        keep.exists() or keep.write_text("", encoding="utf-8")
    for src, dst in (
        (skill / "templates" / "README.md", decisions_dir(docs) / "README.md"),
        (skill / "templates" / "AGENTS.md", decisions_dir(docs) / "AGENTS.md"),
        (skill / "templates" / "_template.md", decisions_dir(docs) / "_template.md"),
        (skill / "templates" / "drafts" / "_template.md", drafts_dir(docs) / "_template.md"),
    ):
        if src.exists() and not dst.exists():
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"created {dst.relative_to(repo)}")
    main(["build"], root=docs)  # INDEX.md is GENERATED, not scaffolded — build it

    # Wire the root entry points so people/agents discover the scaffold — only when missing
    # (a fresh/empty repo); an existing README/AGENTS is the adopter's to wire by hand.
    wire_entry_point(
        repo,
        "README.md",
        f"# {repo.name}\n\n"
        "<!-- TODO: describe this repo. -->\n\n"
        "## Decision records\n\n"
        "Significant decisions live under [`docs/decisions/`](docs/decisions/README.md) — "
        "browse the [decision index](docs/decisions/INDEX.md).\n",
    )
    wire_entry_point(
        repo,
        "AGENTS.md",
        f"# AGENTS.md — {repo.name}\n\n"
        "<!-- TODO: project-wide agent guidance. -->\n\n"
        "## Decision records\n\n"
        "Decisions under `docs/decisions/` are **binding** here — read "
        "[docs/decisions/AGENTS.md](docs/decisions/AGENTS.md) before changing what they cover.\n",
    )

    hook, line = (
        repo / ".git" / "hooks" / "pre-commit",
        "python scripts/decisions.py check || exit 1",
    )
    if (repo / ".git").is_dir():
        existing = hook.read_text(encoding="utf-8") if hook.exists() else ""
        if line in existing:
            print("pre-commit check already present")
        else:
            hook.write_text((existing or "#!/usr/bin/env bash\n") + line + "\n", encoding="utf-8")
            hook.chmod(0o755)
            print("installed pre-commit check")
    else:
        print("no .git here — add 'python scripts/decisions.py check' to CI")


# ── CLI ─────────────────────────────────────────────────────────────────────
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    raw = list(sys.argv[1:] if argv is None else argv)
    p = argparse.ArgumentParser(
        prog="decisions.py",
        description="Decision-records registry: build the INDEX, validate, rename/promote drafts.",
    )
    sub = p.add_subparsers(dest="cmd", metavar="{build,check,rename-draft-id,promote,install}")
    build = sub.add_parser(
        "build", help="write docs/decisions/INDEX.md (optionally relink everything)"
    )
    build.add_argument(
        "--relink",
        action="store_true",
        help="also refresh generated path links in every docs/*.md (records, drafts, docs)",
    )
    sub.add_parser("check", help="validate only; exit 1 if INDEX or any link is stale (CI-safe)")
    rn = sub.add_parser("rename-draft-id", help="change a draft's ID and repoint all references")
    rn.add_argument("query", help="draft ID, title, or filename fragment (fuzzy)")
    rn.add_argument("new", help="the new 4-letter ID (UPPERCASE)")
    pr = sub.add_parser(
        "promote", help="move one or more drafts into decisions/ as the next counters"
    )
    pr.add_argument(
        "query",
        nargs="+",
        help="one or more draft IDs/names (space- or comma-separated); counters are "
        "assigned in the order given",
    )
    pr.add_argument(
        "--deref",
        action="store_true",
        help="invert dereferenceable front-matter refs so a draft can promote alone",
    )
    pr.add_argument(
        "--allow-replace",
        dest="allow_replace",
        action="store_true",
        help="confirm archiving any decisions this promotion supersedes",
    )
    ins = sub.add_parser("install", help="symlink the tool into a repo + add a pre-commit check")
    ins.add_argument("repo", nargs="?", default=".", help="repo root (default: current dir)")
    known = ("build", "check", "rename-draft-id", "promote", "install", "-h", "--help")
    if not raw or raw[0] not in known:
        raw = ["build"] + raw
    return p.parse_args(raw)


def main(argv: list[str] | None = None, root: Path | None = None) -> int:
    args = parse_args(argv)
    if args.cmd == "install":
        install(Path(args.repo))
        return 0
    root = root or find_docs()
    index = index_path(root)

    if args.cmd == "rename-draft-id":
        dest, err = rename_draft(root, args.query, args.new)
        if err:
            print(err, file=sys.stderr)
            return 1
        print(f"renamed -> {dest.relative_to(root)}")
        return main(["build", "--relink"], root=root)

    if args.cmd == "promote":
        queries = [tok for q in args.query for tok in re.split(r"[,\s]+", q) if tok]
        dests, err = promote(root, queries, deref=args.deref, allow_replace=args.allow_replace)
        if err:
            print(err, file=sys.stderr)
            return 1
        for d in dests:
            print(f"promoted -> {d.relative_to(root)}")
        rc = main(["build", "--relink"], root=root)  # a link left broken must still exit 1
        print("finalize each record's front-matter (summary, supersedes/relates_to) in the PR")
        return rc

    recs = load_records(root)
    drafts = load_drafts(root)
    refs = ref_map(recs, drafts)
    for w in warn_unknown_types(root, drafts):  # non-blocking: typo / new-type heads-up
        print(w, file=sys.stderr)
    upstream = upstream_ids(root)  # ({}, {}) when origin/main is not on disk
    for w in warn_upstream_collisions(local_ids(root), upstream):  # non-blocking
        print(w, file=sys.stderr)
    struct_errs = validate_records(recs, refs, upstream[0])
    out = render_index(recs, root)

    if args.cmd == "check":
        problems = list(struct_errs)
        problems += front_matter_errors(recs, drafts)
        problems += validate_no_breach(recs, drafts)
        problems += check_links(root, recs, drafts, refs)
        problems += validate_drafts(root, refs, drafts)
        problems += prose_unknown_counters(root, recs, drafts, refs)
        current = index.read_text(encoding="utf-8") if index.exists() else ""
        if current.strip() != out.strip():
            problems.append("INDEX.md is stale — run scripts/decisions.py build")
        stale = [
            p.name
            for p, own in reference_targets(root, recs, drafts)
            if relink(p.read_text(encoding="utf-8"), refs, own, p.parent)
            != p.read_text(encoding="utf-8")
        ]
        if stale:
            problems.append(
                "links stale — run scripts/decisions.py build --relink: " + ", ".join(stale)
            )
        if problems:
            print("\n".join(problems), file=sys.stderr)
            return 1
        return 0

    if struct_errs:
        print("\n".join(struct_errs), file=sys.stderr)
        return 1

    index.write_text(out, encoding="utf-8")
    print(f"wrote {index} ({len(recs)} records)")

    if getattr(args, "relink", False):
        n = 0
        for path, own in reference_targets(root, recs, drafts):
            text = path.read_text(encoding="utf-8")
            new = relink(text, refs, own, path.parent)
            if new != text:
                path.write_text(new, encoding="utf-8")
                print(f"relinked {path.name}")
                n += 1
        print(f"relinked {n} file(s)")
        residual = check_links(root, recs, drafts, refs)
        if residual:
            print("\n".join(residual), file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
