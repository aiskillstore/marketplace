#!/usr/bin/env python3
"""Shared parser for references/self-test.md `## Test N:` blocks.

Single source of truth for self-test parsing — used by BOTH selfcheck.py
(SB2/SB3/SB15) and selftest-runner.py. Before this module existed there were
four independent implementations with slightly different format assumptions;
a format drift could make the two tools disagree silently (F4-class risk).

Parses blocks of the form:

    ## Test 12: title
    Prompt:
    ```text
    ...prompt body...
    ```
    Fixture: <optional pre-supplied truth>
    Expected:
    - expectation line
    - another line

Returns (cases, malformed_headers):
  cases     - list of dicts: num/title/raw/text_prompt/fences/expect/fixture
              raw        = full block text after the `## Test ` marker
              text_prompt= content of the first ```text fence (SB15 semantics)
              fences     = ALL fenced blocks (bare ``` or ```text) joined with
                           "\n---\n" (selftest-runner semantics)
  malformed_headers - first-line snippets of blocks whose header did not match
                      `N: title` (callers decide whether that is fatal)
"""

from __future__ import annotations

import re

HEADER_LINE_RE = re.compile(r"^(\d+)\s*:\s*(.+)$")
TEXT_FENCE_RE = re.compile(r"```text\n(.*?)```", re.S)
FENCE_RE = re.compile(r"```(?:text)?\n(.*?)```", re.S)


def parse(text: str):
    cases, malformed_headers = [], []
    for block in re.split(r"^## Test ", text, flags=re.M)[1:]:
        head = block.splitlines()[0].strip()
        m = HEADER_LINE_RE.match(head)
        if not m:
            malformed_headers.append(head[:60])
            continue
        num, title = int(m.group(1)), m.group(2).strip()
        text_prompts = [b.strip() for b in TEXT_FENCE_RE.findall(block)]
        fences = [b.strip() for b in FENCE_RE.findall(block)]
        tail = block.split("Expected")[-1] if "Expected" in block else block
        expect = [x.strip() for x in re.findall(r"^-\s+(.+)$", tail, flags=re.M)]
        fm = re.search(r"^Fixture:\s*(.+)$", block, flags=re.M)
        fixture = fm.group(1).strip() if fm else ""
        cases.append({
            "num": num,
            "title": title,
            "raw": block,
            "text_prompt": text_prompts[0] if text_prompts else "",
            "fences": fences,
            "expect": expect,
            "fixture": fixture,
        })
    cases.sort(key=lambda d: d["num"])
    return cases, malformed_headers
