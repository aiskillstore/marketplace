"""Original, conservative helpers for the read-only writing tools (Python 3.9+).

These are lightweight text heuristics, not a Markdown parser or a meaning model.
All offsets refer to the unmodified input, measured in Unicode code points.
"""

import bisect
from dataclasses import dataclass
import re
import sys


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    kind: str
    text: str


WORD = re.compile(r"[^\W\d_]+(?:[\u200c'’-][^\W\d_]+)*", re.UNICODE)
URL = re.compile(r"(?:https?://|ftp://|www\.)[^\s<>`\"«»]+", re.I)


def mask_spans(text, spans):
    """Blank protected content but retain newlines and exact original offsets."""
    chars = list(text)
    for span in spans:
        for index in range(span.start, span.end):
            if chars[index] not in "\r\n":
                chars[index] = " "
    return "".join(chars)


def protected_spans(text, quotes=False):
    """Find code, link destinations and URLs; optionally literal quotations.

    Indented code is included conservatively. Nested Markdown and escaped quote
    punctuation are only partially recognized; exact invariants handle critical
    passages whose syntax is outside these conventions.
    """
    spans = []
    occupied = [False] * len(text)

    def add(start, end, kind, enclose=False):
        if start >= end:
            return
        overlaps = [span for span in spans if span.start < end and start < span.end]
        if overlaps:
            # A quotation containing a URL or inline code is still one literal
            # quotation. Do not drop the quotation merely because it encloses
            # an already protected token. Partial overlaps remain conservative.
            if not enclose or any(span.start < start or span.end > end for span in overlaps):
                return
            spans[:] = [span for span in spans if span not in overlaps]
        spans.append(Span(start, end, kind, text[start:end]))
        occupied[start:end] = [True] * (end - start)

    fence = None
    cursor = 0
    for line in text.splitlines(keepends=True):
        match = re.match(r" {0,3}(`{3,}|~{3,})(.*?)(?:\r?\n)?$", line)
        if fence:
            marker, begin = fence
            if match and match.group(1)[0] == marker[0] and len(match.group(1)) >= len(marker) and not match.group(2).strip():
                add(begin, cursor + len(line), "code")
                fence = None
        elif match and not (match.group(1)[0] == "`" and "`" in match.group(2)):
            fence = (match.group(1), cursor)
        elif line.startswith("    ") or line.startswith("\t"):
            add(cursor, cursor + len(line), "code")
        cursor += len(line)
    if fence:
        add(fence[1], len(text), "code")

    index = 0
    while index < len(text):
        if text[index] != "`" or occupied[index]:
            index += 1
            continue
        end_run = index
        while end_run < len(text) and text[end_run] == "`":
            end_run += 1
        marker = text[index:end_run]
        search = end_run
        while True:
            close = text.find(marker, search)
            if close < 0:
                break
            after = close + len(marker)
            if (close == 0 or text[close - 1] != "`") and (after == len(text) or text[after] != "`") and not any(occupied[index:after]):
                add(index, after, "code")
                index = after
                break
            search = after
        else:  # pragma: no cover - loop exits explicitly
            close = -1
        if close < 0:
            index = end_run

    # Balanced destinations, including local paths, nested parentheses and titles.
    for match in re.finditer(r"\]\(", text):
        start = match.end()
        if any(occupied[match.start():start]):
            continue
        depth, cursor = 1, start
        while cursor < len(text) and text[cursor] not in "\r\n":
            if text[cursor] == "\\":
                cursor += 2
                continue
            if text[cursor] == "(":
                depth += 1
            elif text[cursor] == ")":
                depth -= 1
                if not depth:
                    add(start, cursor, "destination")
                    break
            cursor += 1
    # Reference-link definitions: the identifier is prose, destination is not.
    for match in re.finditer(r"(?m)^ {0,3}\[[^\]\n]+\]:[ \t]*(\S+)(?:[ \t]+[^\n]*)?$", text):
        add(match.start(1), match.end(), "destination")

    for match in URL.finditer(text):
        end = match.end()
        while end > match.start() and text[end - 1] in ".,;:!?،؛؟":
            end -= 1
        while end > match.start() and text[end - 1] == ")" and text[match.start():end].count(")") > text[match.start():end].count("("):
            end -= 1
        add(match.start(), end, "url")

    if quotes:
        # Whole blockquote lines are source-like content, even across paragraphs.
        for match in re.finditer(r"(?m)^ {0,3}>[^\n]*(?:\n|$)", text):
            add(match.start(), match.end(), "quote", enclose=True)
        for pattern in (r"«[^«»\n]*»", r"“[^“”\n]*”", r'"[^"\n]*"'):
            for match in re.finditer(pattern, text):
                add(match.start(), match.end(), "quote", enclose=True)
    return sorted(spans, key=lambda span: (span.start, span.end, span.kind))


def citation_spans(text, protected):
    """Recognize common numeric and author-year citation shapes, conservatively."""
    masked = mask_spans(text, protected)
    patterns = [
        r"\[(?:\d+[a-z]?(?:\s*[,;،؛–-]\s*\d+[a-z]?)*|[^\]\n]{0,80}\d{4}[a-z]?[^\]\n]{0,40})\]",
        r"\((?=[^()\n]{1,120}\))(?=[^()\n]*[^\W\d_])[^()\n]*?\b\d{4}[a-z]?[^()\n]*\)",
        r"\[\^[^\]\n]+\]",
    ]
    spans = []
    for pattern in patterns:
        for match in re.finditer(pattern, masked, re.UNICODE):
            if not any(span.start < match.end() and match.start() < span.end for span in spans):
                spans.append(Span(match.start(), match.end(), "citation", text[match.start():match.end()]))
    return sorted(spans, key=lambda span: span.start)


def language(text):
    fa = len(re.findall(r"[\u0620-\u064a\u0670-\u06d3]", text))
    en = len(re.findall(r"[A-Za-z]", text))
    if fa and en:
        return "mixed"
    if fa:
        return "fa"
    if en:
        return "en"
    return "undetermined"


def location(text, offset):
    starts = [0] + [match.end() for match in re.finditer("\n", text)]
    row = bisect.bisect_right(starts, offset)
    return row, offset - starts[row - 1] + 1


def finding(text, offset, code, message, severity="advisory", **extra):
    line, column = location(text, offset)
    begin = text.rfind("\n", 0, offset) + 1
    end = text.find("\n", offset)
    if end < 0:
        end = len(text)
    excerpt_start = max(begin, offset - 60)
    excerpt_end = min(end, excerpt_start + 180)
    excerpt = text[excerpt_start:excerpt_end].rstrip("\r")
    result = {"line": line, "column": column, "code": code, "severity": severity,
              "message": message, "excerpt": excerpt}
    result.update(extra)
    return result


def read_utf8(path):
    if path == "-":
        if hasattr(sys.stdin, "buffer"):
            return sys.stdin.buffer.read().decode("utf-8-sig")
        return sys.stdin.read().lstrip("\ufeff")
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        return handle.read()


def human_report(report):
    print("{}: {} advisory finding(s)".format(report["tool"], len(report["findings"])))
    print("Language: {}".format(report.get("lang", "comparison")))
    if report["tool"] == "audit_text":
        metrics = report["metrics"]
        print("Prose: {words} words; {sentences} sentences; {paragraphs} paragraphs".format(**metrics))
    for item in report["findings"]:
        source = (item.get("source", "") + ":") if item.get("source") else ""
        print("{}{}:{} [{}] {}".format(source, item["line"], item["column"], item["code"], item["message"]))
        if item["excerpt"]:
            print("  " + item["excerpt"])
    print("Heuristic review only; no authorship score or factual verification.")


def report_order(item):
    return (item.get("source", ""), item["line"], item["column"], item["code"], item["message"])
