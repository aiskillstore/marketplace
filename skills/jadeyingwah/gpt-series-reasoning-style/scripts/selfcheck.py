#!/usr/bin/env python3
"""Static self-check for the gpt-series-reasoning-style skill.

The 77 behavioural self-tests are prompt->expected descriptions that only
genuinely pass when a host model decides to follow them. This tool does NOT
verify rule semantics. It verifies what a machine *can* verify cheaply and
honestly: version/numbering consistency, structural completeness, cross-file
references, code-fence pairing, identity/reference counts, gate-field surface
sync, prose-count sync, and the install-platform parameter set. Running it is a
fast regression check that the repo has not silently drifted.

Python 3.7+ stdlib only. Exit: 0=all passed, 1=failed, 2=usage.

Known blind spots (literal-layer checks only, documented by design after the
2026-09-10 external reviews): semantic drift; per-item bilingual parity
(incl. identities/); cross-file field-set unions; claims-vs-reality gaps
(use claim-check.py); install.sh parity; per-round ledger fields. Green
means the literal layer is intact — nothing more.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os.path
import pathlib
import re
import sys

import _selftest_parser

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
FENCE_RE = re.compile(r"^```")


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _yaml_step_count(text: str):
    """Count list items under the first YAML `steps:` key (stdlib only, no yaml).

    Indentation is measured RELATIVE to the `steps:` line, so reindenting the
    workflow does not change the count. An absolute-indent regex would have been
    as fragile as the `c = new(` scan SB21 exists to compensate for -- the guard
    must not itself break on whitespace.
    Returns None when no `steps:` list is found (caller fails loudly).
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not re.match(r"^\s*steps:\s*$", line):
            continue
        base = len(line) - len(line.lstrip())
        n = 0
        for later in lines[i + 1:]:
            if not later.strip():
                continue
            indent = len(later) - len(later.lstrip())
            if indent <= base:
                break
            if indent == base + 2 and later.lstrip().startswith("- "):
                n += 1
        return n
    return None


class Check:
    def __init__(self, code: str, title: str):
        self.code = code
        self.title = title
        self.ok = False
        self.detail = ""

    def pass_(self, detail: str = ""):
        self.ok = True
        self.detail = detail

    def fail(self, detail: str):
        self.ok = False
        self.detail = detail

    def line(self) -> str:
        flag = "PASS" if self.ok else "FAIL"
        return f"[{flag}] {self.code} {self.title} -- {self.detail}"


def run_checks() -> list:
    checks = []

    def new(code, title):
        c = Check("SB" + str(code), title)
        checks.append(c)
        return c

    # SB1 version consistency
    c = new(1, "version consistency")
    version = read_text(REPO_ROOT / "VERSION").strip()
    skill_text = read_text(REPO_ROOT / "SKILL.md")
    readme = read_text(REPO_ROOT / "README.md")
    selftest = read_text(REPO_ROOT / "references" / "self-test.md")
    if not re.search(r"Current version: " + re.escape(version), skill_text):
        c.fail("SKILL.md does not declare current version " + version)
    elif re.search(re.escape(version), selftest) is None:
        c.fail("self-test.md does not reference version " + version)
    elif re.search(r"version-" + re.escape(version), readme) is None:
        c.fail("README badge does not show version-" + version)
    # Batch 47: the site badge (v1.1.0) was outside this guard while the site
    # had already drifted twice on other numbers (10-field, Lite tokens) --
    # same family: a live surface nobody watches.
    elif re.search(r"\bv" + re.escape(version) + r"\b",
                   read_text(REPO_ROOT / "site" / "index.html")) is None:
        c.fail("site badge does not show v" + version)
    else:
        residue = []
        for name, text in (("SKILL.md", skill_text), ("README.md", readme),
                           ("self-test.md", selftest)):
            if re.search(r"\b3\.2\.[0-9]\b", text):
                residue.append(name)
        if residue:
            c.fail("stale 3.2.x residue in: " + ", ".join(residue))
        else:
            c.pass_("all surfaces agree on " + version + "; no 3.2.x residue")

    # Shared parse (M1: single parser for self-test.md — selfcheck and
    # selftest-runner.py must never disagree on the format).
    cases, malformed_headers = _selftest_parser.parse(selftest)

    # SB2 self-test numbering contiguous
    c = new(2, "self-test numbering 1..N")
    nums = [c["num"] for c in cases]
    if not cases:
        c.fail("self-test.md contains no Test blocks")
    elif malformed_headers:
        c.fail("malformed Test headers (hidden from numbering): "
               + "; ".join(malformed_headers[:3]))
    elif len(nums) != len(set(nums)):
        c.fail("duplicate Test numbers")
    elif nums != list(range(1, len(nums) + 1)):
        c.fail("numbering not contiguous 1.." + str(len(nums)))
    else:
        c.pass_("contiguous Test 1.." + str(len(nums)) + " (" + str(len(nums)) + " tests)")

    # SB3 structural completeness
    c = new(3, "self-test structural completeness")
    missing = []
    if not cases:
        c.fail("self-test.md contains no test blocks")
    else:
        for case in cases:
            raw = case["raw"]
            name = "Test {}: {}".format(case["num"], case["title"])
            # case-insensitive (L2): format drift to lowercase must not slip past
            has_prompt = ("prompt" in raw.lower()) and ("```" in raw)
            low = raw.lower()
            has_expected = ("expected" in low or "期望" in raw) and bool(re.search(r"^- ", raw, re.M))
            if not (has_prompt and has_expected):
                missing.append(name)
        if missing:
            c.fail("tests lacking prompt or expectation: " + ", ".join(missing[:6]))
        else:
            c.pass_("all " + str(len(cases)) + " test blocks complete")

    # SB4 identity count == 21
    c = new(4, "identity file count == 21")
    idir = REPO_ROOT / "identities"
    names = {p.name for p in idir.glob("*.md")}
    names.discard("_template.md"); names.discard("README.md")
    if len(names) != 21:
        c.fail("found " + str(len(names)) + " identity files, expected 21")
    else:
        c.pass_("21 identity files present")

    # SB5 references count == 13
    # (11 originals + series-reasoning-workflow-en.md mirror + project-artifacts.md)
    c = new(5, "reference file count == 13")
    refs = list((REPO_ROOT / "references").glob("*.md"))
    if len(refs) != 13:
        c.fail("found " + str(len(refs)) + " reference files, expected 13")
    else:
        c.pass_("13 reference .md files")

    # SB6 code-fence pairing (+ escaped-fence detection, A2: a backslash-escaped
    # fence is invisible to the parser and silently drops content from tooling)
    c = new(6, "markdown code-fence pairing")
    bad = []
    escaped = []
    # Backslash-escaped fence (no regex: multi-layer escaping proved error-prone)
    backslash_fence = chr(92) + chr(96) * 3
    for p in sorted(REPO_ROOT.rglob("*.md")):
        if ".git" in p.parts:
            continue
        raw_lines = p.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(raw_lines, 1):
            if line.lstrip().startswith(backslash_fence):
                escaped.append("{}:{}".format(p.relative_to(REPO_ROOT), idx))
        n = sum(1 for line in raw_lines if FENCE_RE.match(line))
        if n % 2 != 0:
            bad.append(str(p.relative_to(REPO_ROOT)) + " (" + str(n) + ")")
    if escaped:
        bad.append("escaped fences (invisible to parser): " + ", ".join(escaped[:4]))
    if bad:
        c.fail("unpaired fences: " + "; ".join(bad))
    else:
        c.pass_("all markdown fences paired")

    # SB7 cross-file references exist
    c = new(7, "cross-file reference existence")
    missing_refs = set()
    root = REPO_ROOT / "references"
    for m in re.findall(r"references/([\w\-.]+?\.md)", selftest):
        if not (root / m).exists():
            missing_refs.add(m)
    for m in re.findall(r"identities/([\w\-.]+?\.md)", selftest):
        if not (REPO_ROOT / "identities" / m).exists():
            missing_refs.add("identities/" + m)
    if missing_refs:
        c.fail("missing referenced files: " + ", ".join(sorted(missing_refs)))
    else:
        c.pass_("all referenced reference/identity files exist")

    # SB8 authoritative field counts
    c = new(8, "authoritative field counts consistent")
    live = "\n".join([skill_text, readme, selftest])
    leaked = []
    if re.findall(r"24\s*字段|24-field", live):
        leaked.append("24-field mention in live surfaces")
    if not re.search(r"23\s*字段|23[- ]field", live):
        leaked.append("no 23-field mention")
    if not re.search(r"6\s*字段|six[- ]field|6-field", live):
        leaked.append("no 6-field mini package mention")
    if leaked:
        c.fail("; ".join(leaked))
    else:
        c.pass_("23-field/6-field present; no 24-field leak in live surfaces")

    # SB9 gate-field surface sync
    c = new(9, "gate-field surface sync")
    oai = read_text(REPO_ROOT / "agents" / "openai.yaml")
    missing_tokens = []
    for tk in ["风险分档", "形态选择", "已盘点可用资源", "最高影响问题", "需要你确认", "宿主对齐"]:
        if tk not in skill_text:
            missing_tokens.append("SKILL.md:" + tk)
        if tk not in readme:
            missing_tokens.append("README:" + tk)
    # "confirmation scope" added after batch 47 caught openai.yaml listing only
    # 10 of the 11 gate fields (GATE_FIELDS[10] was missing from default_prompt).
    for tk in ["form selection", "risk tier", "surveyed", "confirmation scope"]:
        if tk not in oai:
            missing_tokens.append("openai.yaml:" + tk)
    if missing_tokens:
        c.fail("missing gate tokens: " + ", ".join(missing_tokens))
    else:
        c.pass_("CN gate tokens + EN tokens synced across surfaces")

    # SB10 install platform parameter set
    c = new(10, "install platform parameter set")
    try:
        ps1 = read_text(REPO_ROOT / "scripts" / "install.ps1")
    except FileNotFoundError:
        # Do NOT return early: skipping SB11-SB17 would silently shrink the
        # reported total and mask seven checks as "not applicable". Fail this
        # check and let the remaining checks run (each guards its own I/O).
        c.fail("scripts/install.ps1 missing")
    else:
        keys = set(re.findall(r"^\s+(\w+)\s+= Join-Path", ps1, flags=re.M))
        required = {"agents", "codex", "claude", "cursor", "windsurf", "cline",
                    "gemini", "kiro", "trae", "goose", "opencode", "roo", "antigravity"}
        diff = required - keys
        if diff:
            c.fail("install.ps1 missing platform keys: " + ", ".join(sorted(diff)))
        elif len(keys) < 13:
            c.fail("expected >=13 platform keys, found " + str(len(keys)))
        else:
            c.pass_("install.ps1 covers " + str(len(keys)) + " platform keys")

    # SB11 light-channel exclusion boundary cross-surface sync
    c = new(11, "light-channel exclusion boundary sync")
    surf = {
        "SKILL.md": "从零新建产物默认中档",
        "references/series-reasoning-workflow.md": "从零新建产物默认中档",
        "references/agent-modes.md": "从零新建产物未完整指定",
        "README.md": "全新产物默认中档",
        "agents/openai.yaml": "fully specifies type, location, and form",
        "docs/minimal-discipline.md": "完整指定类型/位置/形态",
        "references/self-test.md": "multi-deliverable",
    }
    miss = []
    for rel, tk in surf.items():
        try:
            txt = read_text(REPO_ROOT / rel)
        except FileNotFoundError:
            miss.append(rel + ":MISSING")
            continue
        if tk not in txt:
            miss.append(rel + ":" + tk)
    if miss:
        c.fail("light-channel boundary token missing: " + "; ".join(miss))
    else:
        c.pass_("new-from-scratch boundary + exclusions present on all 7 surfaces")

    # SB12 agentskills.io spec compliance (machine-checkable subset)
    c = new(12, "agentskills.io spec compliance")
    issues = []
    m = re.match(r"^---\s*\nname:\s*([^\s]+)\s*\n", skill_text)
    name = m.group(1) if m else ""
    if name != REPO_ROOT.name:
        issues.append("name != directory name: " + name)
    if not re.match(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$", name):
        issues.append("name format invalid: " + name)
    md = re.search(r"^description:\s*(.+)$", skill_text, flags=re.M)
    desc = md.group(1).strip().strip("\"'") if md else ""
    if not desc:
        issues.append("description missing")
    elif len(desc) > 1024:
        issues.append("description > 1024 chars: " + str(len(desc)))
    body = skill_text.split("---", 2)[2] if skill_text.startswith("---") else skill_text
    nlines = len(body.splitlines())      # 与 SB21 同一行数口径（splitlines）
    if nlines > 500:
        issues.append("SKILL.md body > 500 lines: " + str(nlines))
    if issues:
        c.fail("; ".join(issues))
    else:
        c.pass_("name/description/body within spec (desc=" + str(len(desc)) +
                " chars, body=" + str(nlines) + " lines)")

    # SB13 probe scenario registry consistent
    c = new(13, "probe scenario registry consistent")
    pj = REPO_ROOT / "probes" / "probe-scenarios.json"
    try:
        reg = json.loads(read_text(pj))
    except Exception as exc:  # noqa: BLE001 - machine-truth any parse failure
        c.fail("probe-scenarios.json unreadable: " + str(exc))
    else:
        scen = reg.get("scenarios", [])
        ids = [s.get("id") for s in scen]
        docs = read_text(REPO_ROOT / "docs" / "field-tests" / "field-test-2-probe-series.md")
        rounds = ["第一轮", "第二轮", "第三轮"]
        prob = []
        if not scen:
            prob.append("no scenarios")
        if sorted(ids) != ["P1", "P2", "P3"]:
            prob.append("ids != P1/P2/P3: " + str(ids))
        if not reg.get("probe_prompt"):
            prob.append("probe_prompt missing")
        for r in rounds:
            if r not in docs:
                prob.append("field-test-2 missing round " + r)
        if prob:
            c.fail("; ".join(prob))
        else:
            c.pass_("3 probe scenarios (P1/P2/P3) + prompt; field-test-2 documents all 3 rounds")

    # SB14 language-policy declaration anchored in README + layers exist
    c = new(14, "language-policy declaration synced")
    if "## Language Policy / 语言策略" not in readme:
        c.fail("README language-policy section missing")
    elif not re.search(r"分层双语", readme) or not re.search(r"layered bilingual", readme):
        c.fail("language-policy wording drifted (need 分层双语 + layered bilingual)")
    else:
        layers = [
            "references/series-reasoning-workflow.md",
            "references/series-reasoning-examples.md",
            "references/project-policy-template.md",
            "references/agent-modes.md",
            "docs/minimal-discipline.md",
        ]
        missed = [r for r in layers if not (REPO_ROOT / r).exists()]
        if missed:
            c.fail("matrix-listed layer files missing: " + ", ".join(missed))
        else:
            c.pass_("language policy declared (中文主导 / CN-primary); matrix layer files present")

    # SB15 self-test prompt uniqueness
    c = new(15, "self-test prompt uniqueness")
    seen = {}
    dup = []
    for case in cases:
        pp = case["text_prompt"]
        if not pp:
            continue
        if pp in seen:
            dup.append("Test " + seen[pp] + " & Test " + str(case["num"]))
        else:
            seen[pp] = str(case["num"])
    if dup:
        c.fail("duplicated prompts: " + "; ".join(dup[:6]))
    else:
        c.pass_("all " + str(len(seen)) + " non-empty prompts distinct")

    # SB16 bilingual coverage — tiered. Tier A (rule surfaces loaded by every
    # session) must stay bilingual; tier B (long-form reference docs) is
    # informational only — forcing full bilingual on 500+ line docs would either
    # stay red forever or double file size (see README Complexity Budget).
    c = new(16, "bilingual section coverage (tiered)")

    def _collect_bilingual_gaps(rel):
        gaps = []
        p = REPO_ROOT / rel
        if not p.exists():
            return gaps
        txt = read_text(p)
        parts = re.split(r"(?m)^(#{1,4}[ \t]+.*)$", txt)
        for i in range(1, len(parts), 2):
            title = parts[i].strip()
            body = parts[i + 1] if i + 1 < len(parts) else ""
            zh = sum(1 for ch in body if chr(0x4e00) <= ch <= chr(0x9fff))
            en = len(re.findall(r"[A-Za-z]{3,}", body))
            if zh + en < 40:
                continue
            if en == 0:
                gaps.append("{} :: {} (纯中文{}字/无英文)".format(rel, title, zh))
            elif zh / max(en, 1) > 4:
                gaps.append("{} :: {} (中{}/英{})".format(rel, title, zh, en))
            elif en / max(zh, 1) > 4:
                gaps.append("{} :: {} (英{}/中{})".format(rel, title, en, zh))
        return gaps

    tier_a = [
        "references/multi-agent-closure-rules.md",
        "references/agent-modes.md",
    ]
    tier_b = [
        "references/series-reasoning-workflow.md",
    ]
    gaps_a, gaps_b = [], []
    # SKILL.md is Chinese-primary by design (language policy); bilingual sections
    # were moved down to the references (EN sections) to halve the always-loaded
    # cost. Only an English entry pointer is required here.
    if "Complete English rules live" not in skill_text:
        gaps_a.append("SKILL.md :: English entry pointer missing (see language policy)")
    for rel in tier_a:
        gaps_a.extend(_collect_bilingual_gaps(rel))
    for rel in tier_b:
        gaps_b.extend(_collect_bilingual_gaps(rel))
    if gaps_a:
        c.fail("tier-A bilingual gaps ({}): ".format(len(gaps_a)) + "; ".join(gaps_a[:6]))
    elif gaps_b:
        c.pass_("tier-A rule surfaces bilingual OK; tier-B long-form docs carry "
                + str(len(gaps_b)) + " informational gaps (not force-translated)")
    else:
        c.pass_("all rule-layer sections carry both languages")

    # SB17 AGENTS.md cross-runtime entry consistency (C4-1: the new surface
    # must stay aligned with SKILL.md or it drifts unguarded).
    c = new(17, "AGENTS.md entry consistency")
    ag_path = REPO_ROOT / "AGENTS.md"
    if not ag_path.exists():
        c.fail("AGENTS.md missing (cross-runtime entry alias expected at repo root)")
    else:
        ag = read_text(ag_path)
        problems = []
        if "SKILL.md" not in ag or "VERSION" not in ag:
            problems.append("does not route to SKILL.md/VERSION")
        if "宣布阶段序列不是确认。" not in ag:
            problems.append("quoted first hard rule missing/drifted")
        if "gpt-series-reasoning-style" not in ag:
            problems.append("skill name missing")
        for m in re.findall(r"references/([\w\-.]+\.md)", ag):
            if not (REPO_ROOT / "references" / m).exists():
                problems.append("routes to missing file references/" + m)
        if problems:
            c.fail("; ".join(problems))
        else:
            c.pass_("AGENTS.md routes to SKILL.md/VERSION; hard-rule quote intact; routed files exist")

    # SB18 forbidden-authorization-phrase parity (evidence: P0-4, a real 2026-09-10
    # external-review finding — the CN authority workflow.md lagged its EN mirror and
    # SKILL.md on the third phrase). The three phrases must appear on all three
    # hard-rule surfaces; the check cannot judge semantics, only presence parity.
    c = new(18, "forbidden-authorization-phrase parity")
    phrases = ["开始", "现在开始", "直接做"]
    surfaces = {
        "SKILL.md": skill_text,
        "references/series-reasoning-workflow.md": read_text(REPO_ROOT / "references" / "series-reasoning-workflow.md"),
        "references/series-reasoning-workflow-en.md": read_text(REPO_ROOT / "references" / "series-reasoning-workflow-en.md"),
    }
    missing_phrases = []
    for rel, txt in surfaces.items():
        for ph in phrases:
            if ph == "直接做":
                if "直接做" not in txt:
                    missing_phrases.append(rel + ":" + ph)
            else:
                if ('"' + ph + '"') not in txt and ("\u201c" + ph + "\u201d") not in txt:
                    missing_phrases.append(rel + ":" + ph)
    if missing_phrases:
        c.fail("forbidden phrases missing on: " + ", ".join(missing_phrases))
    else:
        c.pass_("开始/现在开始/直接做 present on SKILL.md + workflow CN/EN")

    # SB19 identity-count prose consistency across surfaces (evidence: commit
    # 9d32cbb — the qa-engineer/test-engineer merge updated SB4 and two README
    # spots but left five prose surfaces still saying "22 个身份"; SB4 only counts
    # FILES, so the prose drift was invisible to every check we had).
    # Admitted under README's own rule for a 19th check: it demonstrates a real
    # defect with an identifiable commit hash.
    # It scans an explicit allowlist of LIVE surfaces. Deliberately excluded:
    # CHANGELOG.md / INTERNAL-HISTORY.md / docs/reviews/ / docs/field-tests/
    # (dated records — a past count is correct for its date) and
    # docs/selftest-run/ (generated per run, not repo content).
    c = new(19, "identity-count prose consistency")
    expected_ids = 21
    id_surfaces = [
        "SKILL.md", "README.md", "AGENTS.md", "agents/openai.yaml",
        "identities/README.md", "docs/minimal-discipline.md", "site/index.html",
    ] + sorted(
        p.relative_to(REPO_ROOT).as_posix()
        for p in (REPO_ROOT / "references").glob("*.md")
    )
    id_cn = re.compile(r"(\d+)\s*(?:个|类)(?:内置)?(?:身份|角色|契约)")
    id_ctx = re.compile(r"(?:当前|全部|至全部)\s*(\d+)\s*个")
    id_ctx_guard = "内置身份"
    id_en = re.compile(r"(\d+)\s+(?:built-in\s+)?(?:identities|roles)\b")
    # Bold markers split the phrase ("内置身份 **22** 个文件"), so the guard is
    # "line mentions identity AND files", and the count may sit on either side
    # of the noun in either language.
    id_file_cnt = re.compile(r"(\d+)\s*(?:\*\*)?\s*个\s*文件")
    id_file_en_before = re.compile(r"(\d+)\s+(?:built-in\s+)?(?:identity|role)\s+files")
    id_file_en_after = re.compile(r"(?:identity|role)\s+files\s*(?:\*\*)?\s*(\d+)")
    id_file_guard = ("身份", "identity files")
    id_bad = []
    for rel in id_surfaces:
        p = REPO_ROOT / rel
        if not p.exists():
            id_bad.append(rel + ": missing (surface listed for the count check)")
            continue
        for ln, line in enumerate(read_text(p).splitlines(), 1):
            found = set()
            for rx in (id_cn, id_en):
                for m in rx.finditer(line):
                    if int(m.group(1)) != expected_ids:
                        found.add(m.group(0))
            # The catalog size is often stated apart from the noun
            # ("（当前 22 个，硬编码必然漂移）"). Only apply this second form on a
            # line that also says 内置身份 -- a bare "共 N 个角色" is legitimate
            # prose and must not trip the check.
            if id_ctx_guard in line:
                for m in id_ctx.finditer(line):
                    if int(m.group(1)) != expected_ids:
                        found.add(m.group(0))
            # The count can also attach to the word file(s) ("内置身份 22 个文件").
            # Only on a line that talks about identity files, so ordinary file
            # counts elsewhere never trip the check.
            if ("身份" in line and "文件" in line) or "identity files" in line:
                for rx in (id_file_cnt, id_file_en_before, id_file_en_after):
                    for m in rx.finditer(line):
                        if int(m.group(1)) != expected_ids:
                            found.add(m.group(0))
            for f in sorted(found):
                id_bad.append("{}:{}: {}".format(rel, ln, f))
    if id_bad:
        c.fail("identity count != {} on: {}".format(expected_ids, "; ".join(id_bad[:8])))
    else:
        c.pass_("all {} live surfaces state {} identities".format(len(id_surfaces), expected_ids))

    # SB20 text-write call sites pin newline="\n" (evidence: commit bf566b9 —
    # four write sites did not, so on Windows every \n became \r\n and the
    # generated sheet / selfcheck reports / the probe's append-only archive
    # silently disagreed with the repo's LF policy declared in .gitattributes).
    # Admitted under README's own rule: the defect is reproducible (unpinned
    # call measured at 1 CRLF, pinned at 0) and has an identifiable hash.
    # Static on purpose: a worktree CRLF scan would be a no-op on Linux CI,
    # while this catches the root cause on every platform.
    # Known blind spot: single-line scan only -- a call split across lines is
    # not seen (no such call exists today).
    c = new(20, "text-write call sites pin newline")
    py_files = sorted(p for p in REPO_ROOT.rglob("*.py")
                      if ".git" not in p.parts and "__pycache__" not in p.parts)
    write_mode = re.compile(r"['\"][wax+]{1,2}b?['\"]")

    def _after_open(line: str) -> str:
        """只看 `open(` 之后的参数片段（避免行内其它短字面量误触发写模式匹配）。"""
        idx = line.rfind("open(")
        return line[idx + 5:] if idx >= 0 else ""

    nl_bad = []
    for p in py_files:
        rel = p.relative_to(REPO_ROOT).as_posix()
        for ln, line in enumerate(read_text(p).splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if "write_text(" in line and "newline=" not in line:
                nl_bad.append("{}:{}: write_text without newline=".format(rel, ln))
                continue
            if "open(" in line and write_mode.search(_after_open(line)) and "newline=" not in line:
                # 2026-09-11 batch 44: 只在 `open(` 之后的片段里找写模式字面量。
                # 之前是全行搜索，同行出现 `d["a"]` / `"x" in s` 这类短字面量即误报
                # （字符类 [wax+] 太宽），把无关行判成"未固定 newline"。
                nl_bad.append("{}:{}: open(write-mode) without newline=".format(rel, ln))
    if nl_bad:
        c.fail("write sites without newline= on: " + "; ".join(nl_bad[:8]))
    else:
        c.pass_("all text-write call sites pin newline= ({} python files scanned)".format(len(py_files)))

    # SB22 gate field-count prose matches artifact-check GATE_FIELDS (evidence:
    # commits 65def17..8437a6d -- batch 34 grew the gate to 11 fields
    # (artifact-check GATE_FIELDS, SKILL.md, workflow CN/EN, project-artifacts
    # snapshot all updated) but README still said "10 字段门禁 / 10 字段确认单"
    # in THREE live places and project-artifacts.md said "10 字段标题齐全"
    # while its own snapshot line said 11 -- batch 35's audit even asserted
    # such remnants only existed on dated surfaces, which this disproves.
    # Admitted under README's own rule for a 22nd check: reproducible defect,
    # identifiable hashes (65def17 introduced the drift, 8437a6d still had it).
    # Truth source: the GATE_FIELDS list in scripts/artifact-check.py itself
    # (parsed, not imported, so the check cannot be fooled by import order).
    c = new(22, "gate field-count prose matches GATE_FIELDS")
    ac_text = read_text(REPO_ROOT / "scripts" / "artifact-check.py")
    m_gate = re.search(r"GATE_FIELDS\s*=\s*\[(.*?)\]", ac_text, re.S)
    if not m_gate:
        c.fail("cannot locate GATE_FIELDS in scripts/artifact-check.py")
    else:
        n_gate = len(re.findall(r'"[^"]+"', m_gate.group(1)))
        gfam = [
            ("README.md", r"过\s*(\d+)\s*字段门禁", "gate field count (intro)"),
            ("README.md", r"输出\s*(\d+)\s*字段确认单", "gate field count (mechanism)"),
            ("references/project-artifacts.md", r"【实现前确认】（(\d+)\s*字段快照）", "gate snapshot header"),
            ("references/project-artifacts.md", r"gate record 的\s*(\d+)\s*字段标题齐全", "artifact-check prose"),
            ("references/series-reasoning-workflow-en.md", r"confirmation\)\s*[—-]+\s*(\d+)\s*fields:", "EN gate header"),
            ("site/index.html", r"输出\s*(\d+)\s*字段确认单", "gate field count (site)"),
            # batch 47: the site's EN line silently kept "A 10-field confirmation"
            # while the CN line, README and GATE_FIELDS all said 11 — the CN-only
            # regex above cannot see the EN form, so the drift lasted unnoticed.
            ("site/index.html", r"An?\s*(\d+)-field confirmation", "gate field count (site EN)"),
        ]
        gf_bad = []
        for rel, rx, label in gfam:
            p = REPO_ROOT / rel
            if not p.exists():
                gf_bad.append(rel + ": missing (surface listed for the gate-count check)")
                continue
            hits = 0
            for ln, line in enumerate(read_text(p).splitlines(), 1):
                for mm in re.finditer(rx, line):
                    hits += 1
                    if int(mm.group(1)) != n_gate:
                        gf_bad.append("{}:{}: {} states {} != {}".format(
                            rel, ln, label, mm.group(1), n_gate))
            # 同 SB21 的守卫生效性自检：零命中 = 该族空转，不得静默报"一致"。
            if hits == 0:
                gf_bad.append("{}: {} guard is a no-op (regex matched 0 lines)".format(rel, label))
        # 中文数字形态（batch 44 实证缺陷）：README 工具表曾写「`docs/gate/*.md` 十字段标签」，
        # 而 GATE_FIELDS 实为 11。中文数词不便并进上面的正则族，单独按字面拦截——
        # 字段数若真变成 10，这里会红，那正是"改了实现就该改散文"的预期行为。
        if n_gate != 10 and "十字段" in read_text(REPO_ROOT / "README.md"):
            gf_bad.append("README.md: stale 十字段 wording (GATE_FIELDS={})".format(n_gate))
        if gf_bad:
            c.fail("gate field-count drift: " + "; ".join(gf_bad[:8]))
        else:
            c.pass_("GATE_FIELDS={} consistent across {} prose surfaces".format(n_gate, len(gfam)))

    # SB21 prose counts match their source of truth (evidence: commits
    # dacb935..eef524f -- selfcheck.py defined 17 checks while README's
    # Complexity-Budget line AND site/index.html both still stated "SB1-SB16";
    # d99f353..9d32cbb -- site/index.html stated "SB1-SB17" while selfcheck.py
    # defined 18; 95d1b03 -- README advertised a "13-step" CI pipeline while the
    # workflow has had 12 steps ever since. Surfaces lag their source for
    # six-plus commits because nothing derived a prose number from its source.
    # SB4/SB5 count FILES and SB19 guards identity-count prose only -- none of
    # them tied a *check count*, a *line count*, a *frozen test count*, a
    # *reference count* or a *CI step count* stated in prose to reality.
    # Admitted under README's own rule for a 21st check: reproducible defects
    # with identifiable hashes.
    # Two-layer truth source: len(checks) at run time (immune to renames and
    # whitespace) PLUS a definition scan of this file. They must agree; if a
    # future check is appended after SB21, or the definition syntax is
    # refactored, the two disagree and this fails loudly instead of silently
    # demanding a wrong number from every surface.
    # Scope is deliberately narrow: only counts that (a) appear as prose on a
    # LIVE surface and (b) have one unambiguous source. Dated records
    # (CHANGELOG / INTERNAL-HISTORY / docs/reviews / docs/field-tests) stay
    # excluded -- a past count is correct for its date, same rationale as SB19.
    c = new(21, "prose counts match their source")
    sc_rel = "scripts/selfcheck.py"
    n_sb = len(checks)                                 # 运行时真值（SB21 即最后一项）
    n_sb_scan = len(re.findall(r"\bc\s*=\s*new\(\s*\d+", read_text(REPO_ROOT / sc_rel)))
    n_skill = len(read_text(REPO_ROOT / "SKILL.md").splitlines())
    n_tests = len(cases)
    n_refs = len(list((REPO_ROOT / "references").glob("*.md")))
    wf_rel = ".github/workflows/selfcheck.yml"
    n_ci = _yaml_step_count(read_text(REPO_ROOT / wf_rel))
    # 黑名单类数（batch 44 实证缺陷）：README 写「24 类破坏性命令黑名单」而
    # claim-check.py 的 DANGEROUS_RES 实为 25 —— 与 SB22 的门禁字段漂移同族
    # （工具自己的常量被手抄进散文）。真值源解析而非导入，防导入顺序欺骗。
    m_bl = re.search(r"DANGEROUS_RES\s*=\s*\[(.*?)\n\]",
                     read_text(REPO_ROOT / "scripts" / "claim-check.py"), re.S)
    n_black = len(re.findall(r'^\s*r"', m_bl.group(1), re.M)) if m_bl else None
    if n_sb_scan != n_sb:
        c.fail("SB truth source is unreliable: definition scan found {} entries but {} "
               "checks are registered. Move SB21 to the end of run_checks() or fix the "
               "scan pattern in {} -- refusing to compare surfaces against either "
               "number.".format(n_sb_scan, n_sb, sc_rel))
    elif n_ci is None:
        c.fail("cannot locate a `steps:` list in " + wf_rel)
    elif n_black is None:
        c.fail("cannot locate DANGEROUS_RES in scripts/claim-check.py")
    else:
        # (relative path, per-line regex, expected group tuple, human label)
        fam = [
            ("README.md", r"selfcheck-SB1--SB(\d+)_(\d+)%2F(\d+)", (n_sb,) * 3, "selfcheck badge"),
            ("README.md", r"selfcheck\.py\s+#\s+SB1[–—-]+SB(\d+)", (n_sb,), "selfcheck tree"),
            ("README.md", r"\*\*SB1[–—-]+SB(\d+) 静态自检\*\*", (n_sb,), "selfcheck table"),
            ("README.md", r"selfcheck SB1[–—-]+SB(\d+)", (n_sb,), "selfcheck CI line"),
            ("README.md", r"静态检查上限\s*(\d+)\s*项（SB1[–—-]+SB(\d+)）", (n_sb, n_sb), "complexity budget"),
            ("README.md", r"selfcheck\.py`（(\d+)/(\d+)）", (n_sb, n_sb), "pre-release checklist"),
            ("site/index.html", r"selfcheck\.py</code>\s*SB1[–—-]+SB(\d+)", (n_sb,), "selfcheck table"),
            (wf_rel, r"SB1\.\.SB(\d+)", (n_sb,), "workflow step name"),
            ("README.md", r"CI 步数由 SB21 守卫（当前\s*(\d+)/(\d+)\s*步", (n_ci, n_ci), "CI step count"),
            # Anchored forms: the number must sit where the claim lives, so an
            # unrelated sentence elsewhere in the file cannot trip the check.
            ("README.md", r"SKILL\.md[^\n]*?（≈(\d+)\s*行", (n_skill,), "SKILL.md line count"),
            ("README.md", r"≤\s*250\s*行\*\*（当前约\s*(\d+)\s*行", (n_skill,), "SKILL.md line count"),
            ("README.md", r"behavioural_self--tests-(\d+)_frozen", (n_tests,), "frozen self-test count"),
            ("README.md", r"self-test\.md\s+#\s+(\d+) 条行为自测", (n_tests,), "frozen self-test count"),
            ("README.md", r"\*\*(\d+) 条行为自测\*\*", (n_tests,), "frozen self-test count"),
            ("README.md", r"(\d+) 条自测解析", (n_tests,), "frozen self-test count"),
            ("README.md", r"\*\*(\d+) 条行为自测冻结\*\*", (n_tests,), "frozen self-test count"),
            ("site/index.html", r"(\d+) 条 · <code>references/self-test\.md", (n_tests,), "frozen self-test count"),
            ("references/self-test.md", r"自测条数冻结于\s*\*\*(\d+)\*\*", (n_tests,), "frozen self-test count"),
            ("README.md", r"^(\d+) 份 references", (n_refs,), "reference file count"),
            ("README.md", r"references/\s+#\s+(\d+) 份按需规则文档", (n_refs,), "reference file count"),
            ("README.md", r"\*\*(\d+) 类破坏性命令黑名单\*\*", (n_black,), "blacklist class count"),
        ]
        pc_bad = []
        for rel, rx, want, label in fam:
            p = REPO_ROOT / rel
            if not p.exists():
                pc_bad.append(rel + ": missing (surface listed for the prose-count check)")
                continue
            hits = 0
            for ln, line in enumerate(read_text(p).splitlines(), 1):
                for m in re.finditer(rx, line):
                    hits += 1
                    got = tuple(int(g) for g in m.groups() if g is not None)
                    if got != want:
                        pc_bad.append("{}:{}: {} states {} != {}".format(rel, ln, label, got, want))
            # 守卫生效性自检（batch 44）：正则零命中 = 这个族已经空转，永远报"无漂移"。
            # 实证缺陷：CI 步数族写的是「全绿（N/N 步」，而 README 实际措辞是
            # 「（当前 N/N 步」——CI 从 12→13→14 步它全程绿灯，因为根本没比过。
            # 空转守卫比没有守卫更危险（它给出"已检查"的假信号），故显式判失败。
            if hits == 0:
                pc_bad.append("{}: {} guard is a no-op (regex matched 0 lines -- the "
                              "prose wording drifted away from the pattern)".format(rel, label))
        # The next-check ordinal only counts on a line that already states the SB
        # range ("新增第 22 项（SB1–SB21）"); a bare "新增第 3 项" elsewhere must not.
        for rel in ("README.md", "site/index.html"):
            p = REPO_ROOT / rel
            if not p.exists():
                continue
            for ln, line in enumerate(read_text(p).splitlines(), 1):
                if not re.search(r"SB1[–—-]+SB\d+", line):
                    continue
                for m in re.finditer(r"新增第\s*(\d+)\s*项", line):
                    if int(m.group(1)) != n_sb + 1:
                        pc_bad.append("{}:{}: next-check ordinal states {} != {}".format(
                            rel, ln, m.group(1), n_sb + 1))
        if pc_bad:
            c.fail("prose counts drift: " + "; ".join(pc_bad[:8]))
        else:
            c.pass_("SB={} SKILL={} tests={} refs={} CI={} consistent across {} prose surfaces".format(
                n_sb, n_skill, n_tests, n_refs, n_ci, len(fam)))

    return checks


def _write_report(args, lines: list) -> None:
    """Write the report inside the repository only (C1-3 guard).

    `--out` is an in-repo convenience; absolute paths or `..` traversal would
    let a typo drop the report anywhere on disk.
    """
    if pathlib.Path(args.out).is_absolute():
        print("ERROR: --out must be a repo-relative path, got: " + args.out)
        raise SystemExit(2)
    dest = (REPO_ROOT / args.out)
    resolved_root = REPO_ROOT.resolve()
    resolved = dest.resolve()
    rel = os.path.relpath(str(resolved), str(resolved_root))
    if rel == ".." or rel.startswith(".." + os.sep):
        print("ERROR: --out escapes the repository: " + args.out)
        raise SystemExit(2)
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Path.write_text(newline=) exists only on Python 3.10+; CI runs 3.9.
    # open(newline=) is supported everywhere and keeps the LF pin.
    with dest.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    print("\nreport written: " + str(dest))


def main() -> int:
    ap = argparse.ArgumentParser(description="Static self-check")
    ap.add_argument("--out", help="write a markdown report to this path")
    ap.add_argument("--label", default="local", help="tag for the report")
    args = ap.parse_args()

    try:
        checks = run_checks()
    except (OSError, UnicodeDecodeError) as exc:
        # Environment-level failure (missing/undecodable core file): report a
        # structured failure instead of a traceback. Genuine code bugs are NOT
        # swallowed — unexpected exception types still surface loudly.
        print("[FAIL] SB0 environment error -- " + str(exc))
        print("Static selfcheck aborted: core file missing or undecodable (see SB0 above).")
        return 1

    lines = [c.line() for c in checks]
    passed = sum(1 for c in checks if c.ok)
    total = len(checks)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    fingerprint = hashlib.sha1("\n".join(lines).encode("utf-8")).hexdigest()[:12]
    summary = ("Static selfcheck {}/{} passed (label={} ts={} fingerprint={})"
               .format(passed, total, args.label, stamp, fingerprint))

    out_lines = [
        "# Static Self-Check Report / 静态自检报告", "",
        "- Label / 标签: `{}`".format(args.label),
        "- Time / 时间 (UTC): `{}`".format(stamp),
        "- Result / 结果: `{}/{}` passed".format(passed, total),
        "- Fingerprint / 指纹: `{}`".format(fingerprint), "",
        "```text", *lines, summary, "```", "",
    ]
    print("\n".join(out_lines))

    if args.out:
        _write_report(args, out_lines)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())