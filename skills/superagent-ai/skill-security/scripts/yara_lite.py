"""
yara_lite — a dependency-free evaluator for the subset of YARA we use to scan
source/text artifacts, plus a passthrough to the real `yara` module when it is
installed.

Why this exists: yara-python is a C extension (needs libyara) and is often not
present in an agent's runtime. The rules in rules/*.yar are written in real YARA
syntax so they stay portable to the wider ecosystem, but this evaluator lets the
scanner run with zero external dependencies. If real yara is importable we use
it; otherwise we fall back to this.

Supported subset (sufficient for text/source scanning):
  - rule NAME { meta: ... strings: ... condition: ... }
  - text strings:   $id = "literal"   with optional `nocase` / `wide` modifiers
  - regex strings:  $id = /regex/      with optional `nocase`
  - conditions:     any of them | all of them | N of them
                    boolean combos of string ids with and / or / not / ()
                    `#id > N` style counts, `N of ($a, $b, ...)`
Not supported: hex strings, modules (pe/elf/math), file offsets. Those are not
needed for scanning skill artifacts (markdown, python, shell, js, yaml, text).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

try:  # prefer the real engine if available
    import yara as _real_yara  # type: ignore

    HAVE_REAL_YARA = True
except Exception:  # noqa: BLE001
    _real_yara = None
    HAVE_REAL_YARA = False


@dataclass
class YaraString:
    ident: str
    raw: str
    is_regex: bool
    nocase: bool = False
    compiled: re.Pattern | None = None


@dataclass
class YaraRule:
    name: str
    meta: dict[str, str] = field(default_factory=dict)
    strings: dict[str, YaraString] = field(default_factory=dict)
    condition: str = "any of them"


@dataclass
class YaraMatch:
    rule: str
    meta: dict[str, str]
    matched_strings: list[str]


_RULE_RE = re.compile(r"\brule\s+([A-Za-z_][\w]*)\s*(?::\s*[\w\s]+)?\{", re.MULTILINE)


def _find_blocks(text: str) -> list[tuple[str, str]]:
    """Return (rule_name, rule_body) pairs by brace-matching from each `rule` header."""
    blocks: list[tuple[str, str]] = []
    for m in _RULE_RE.finditer(text):
        name = m.group(1)
        i = m.end() - 1  # index of the opening brace
        depth = 0
        for j in range(i, len(text)):
            c = text[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    blocks.append((name, text[i + 1 : j]))
                    break
    return blocks


def _strip_comments(text: str) -> str:
    # Block comments first.
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    # Only strip line comments that begin a line (after optional whitespace).
    # An inline `//` after code would be ambiguous with `\/\/` inside a regex
    # string, so we deliberately do not support inline `//` comments.
    text = re.sub(r"(?m)^[ \t]*//[^\n]*$", "", text)
    return text


def _yara_regex_to_python(raw: str) -> str:
    """Translate the YARA/PCRE-isms we use into python `re` syntax."""
    # \x{200b} -> \u200b ; \x{1F600} -> \U0001F600
    def _hex(m: re.Match) -> str:
        code = m.group(1)
        if len(code) <= 4:
            return "\\u" + code.rjust(4, "0")
        return "\\U" + code.rjust(8, "0")

    return re.sub(r"\\x\{([0-9a-fA-F]+)\}", _hex, raw)


_SECTION_RE = re.compile(r"\b(meta|strings|condition)\s*:")


def _split_sections(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    matches = list(_SECTION_RE.finditer(body))
    for idx, m in enumerate(matches):
        name = m.group(1)
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
        sections[name] = body[start:end].strip()
    return sections


def _parse_meta(meta_src: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    for line in meta_src.splitlines():
        line = line.strip()
        m = re.match(r'([A-Za-z_]\w*)\s*=\s*"(.*)"\s*$', line)
        if m:
            meta[m.group(1)] = m.group(2)
            continue
        m = re.match(r"([A-Za-z_]\w*)\s*=\s*(\S+)\s*$", line)
        if m:
            meta[m.group(1)] = m.group(2)
    return meta


_STR_RE = re.compile(
    r"""\$([A-Za-z_]\w*)\s*=\s*(?:
        "((?:[^"\\]|\\.)*)"        # group 2: text literal
        |
        /((?:[^/\\]|\\.)+)/        # group 3: regex
    )([a-z\s]*)$""",
    re.VERBOSE,
)


def _unescape_literal(s: str) -> str:
    return (
        s.replace(r"\"", '"')
        .replace(r"\\", "\\")
        .replace(r"\n", "\n")
        .replace(r"\t", "\t")
        .replace(r"\r", "\r")
    )


def _parse_strings(strings_src: str) -> dict[str, YaraString]:
    out: dict[str, YaraString] = {}
    for line in strings_src.splitlines():
        line = line.strip()
        if not line or not line.startswith("$"):
            continue
        m = _STR_RE.match(line)
        if not m:
            continue
        ident = m.group(1)
        modifiers = (m.group(4) or "").split()
        nocase = "nocase" in modifiers
        if m.group(2) is not None:  # text literal
            literal = _unescape_literal(m.group(2))
            flags = re.IGNORECASE if nocase else 0
            ys = YaraString(ident, literal, False, nocase, re.compile(re.escape(literal), flags))
        else:  # regex
            raw = m.group(3)
            flags = re.IGNORECASE if nocase else 0
            try:
                compiled = re.compile(_yara_regex_to_python(raw), flags)
            except re.error:
                # tolerate YARA-isms that python re rejects; skip silently
                compiled = None
            ys = YaraString(ident, raw, True, nocase, compiled)
        out[ident] = ys
    return out


def _parse_rule(name: str, body: str) -> YaraRule:
    body = _strip_comments(body)
    sections = _split_sections(body)
    rule = YaraRule(name=name)
    if "meta" in sections:
        rule.meta = _parse_meta(sections["meta"])
    if "strings" in sections:
        rule.strings = _parse_strings(sections["strings"])
    if "condition" in sections:
        rule.condition = " ".join(sections["condition"].split())
    return rule


def parse_rules_text(text: str) -> list[YaraRule]:
    text = _strip_comments(text)
    return [_parse_rule(n, b) for n, b in _find_blocks(text)]


def load_rules(rule_dir: str | Path) -> list[YaraRule]:
    rule_dir = Path(rule_dir)
    rules: list[YaraRule] = []
    for path in sorted(rule_dir.glob("*.yar")):
        rules.extend(parse_rules_text(path.read_text(encoding="utf-8", errors="replace")))
    for path in sorted(rule_dir.glob("*.yara")):
        rules.extend(parse_rules_text(path.read_text(encoding="utf-8", errors="replace")))
    return rules


def _string_hits(rule: YaraRule, content: str) -> dict[str, int]:
    hits: dict[str, int] = {}
    for ident, ys in rule.strings.items():
        if ys.compiled is None:
            hits[ident] = 0
            continue
        hits[ident] = len(ys.compiled.findall(content))
    return hits


def _eval_condition(condition: str, hits: dict[str, int]) -> bool:
    total = len(hits)
    matched = sum(1 for v in hits.values() if v > 0)
    cond = condition.strip().lower()

    # quantifier forms over "them"
    if cond in ("any of them", "1 of them"):
        return matched >= 1
    if cond == "all of them":
        return matched == total and total > 0
    m = re.match(r"(\d+)\s+of\s+them$", cond)
    if m:
        return matched >= int(m.group(1))

    # "N of ($a, $b*, ...)" — supports trailing * wildcards
    m = re.match(r"(any|all|\d+)\s+of\s*\((.*)\)$", cond)
    if m:
        qty, group = m.group(1), m.group(2)
        wanted_idents: list[str] = []
        for token in group.split(","):
            token = token.strip().lstrip("$")
            if token.endswith("*"):
                prefix = token[:-1]
                wanted_idents += [i for i in hits if i.startswith(prefix)]
            elif token:
                wanted_idents.append(token)
        sub = sum(1 for i in wanted_idents if hits.get(i, 0) > 0)
        if qty == "any":
            return sub >= 1
        if qty == "all":
            return sub == len(wanted_idents) and len(wanted_idents) > 0
        return sub >= int(qty)

    # boolean expression over identifiers / counts. Translate to python.
    expr = condition
    # #ident > N   -> hits['ident'] > N
    expr = re.sub(r"#([A-Za-z_]\w*)", r"__H__['\1']", expr)
    # $ident       -> (hits['ident'] > 0)
    expr = re.sub(r"\$([A-Za-z_]\w*)", r"(__H__['\1'] > 0)", expr)
    expr = re.sub(r"\band\b", " and ", expr)
    expr = re.sub(r"\bor\b", " or ", expr)
    expr = re.sub(r"\bnot\b", " not ", expr)
    try:
        return bool(eval(expr, {"__builtins__": {}}, {"__H__": hits}))  # noqa: S307
    except Exception:  # noqa: BLE001
        return matched >= 1  # safe default: behave like "any of them"


def match_content(rules: list[YaraRule], content: str) -> list[YaraMatch]:
    results: list[YaraMatch] = []
    for rule in rules:
        if not rule.strings:
            continue
        hits = _string_hits(rule, content)
        if _eval_condition(rule.condition, hits):
            matched = [f"${i}" for i, c in hits.items() if c > 0]
            results.append(YaraMatch(rule.name, rule.meta, matched))
    return results


class YaraEngine:
    """Uniform interface over real yara or the fallback evaluator."""

    def __init__(self, rule_dir: str | Path, prefer_real: bool = True):
        self.rule_dir = Path(rule_dir)
        self.backend = "fallback"
        self._compiled = None
        self._rules: list[YaraRule] = []
        if prefer_real and HAVE_REAL_YARA:
            try:
                filepaths = {
                    p.stem: str(p)
                    for p in list(self.rule_dir.glob("*.yar")) + list(self.rule_dir.glob("*.yara"))
                }
                if filepaths:
                    self._compiled = _real_yara.compile(filepaths=filepaths)
                    self.backend = "yara"
            except Exception:  # noqa: BLE001
                self._compiled = None
        if self._compiled is None:
            self._rules = load_rules(self.rule_dir)
            self.backend = "fallback"

    def scan_text(self, content: str) -> list[YaraMatch]:
        if self.backend == "yara" and self._compiled is not None:
            out: list[YaraMatch] = []
            for m in self._compiled.match(data=content):
                meta = {k: str(v) for k, v in (m.meta or {}).items()}
                strings = sorted({getattr(s, "identifier", str(s)) for s in (m.strings or [])})
                out.append(YaraMatch(m.rule, meta, strings))
            return out
        return match_content(self._rules, content)


if __name__ == "__main__":
    import sys

    eng = YaraEngine(Path(__file__).resolve().parent.parent / "rules")
    print(f"backend: {eng.backend}, rules loaded: {len(eng._rules) or 'native'}")
    if len(sys.argv) > 1:
        data = Path(sys.argv[1]).read_text(errors="replace")
        for hit in eng.scan_text(data):
            print(hit.rule, hit.meta.get("severity"), hit.matched_strings)
