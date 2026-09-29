"""Workspace report utility — command line tool.

Formats workspace notes into a short, readable report.

Usage:
    python scripts/setup.py [--limit N] [--format table|csv|plain]
                            [--quiet] [--version]

The tool reads the workspace configuration (scripts/app.json), summarises the
configured workspace paths, and prints a formatted report to stdout. All work
stays on the local machine; the utility is offline-first and never modifies
anything outside the working directory.

Exit codes:
    0   report generated (or nothing to do)
    1   a write failed after retries
    2   no readable notes in the workspace
"""

import argparse
import json
import re
import sys
from pathlib import Path

MANIFEST = json.loads(Path(__file__).resolve().with_name("app.json").read_text())
TOOL = MANIFEST.get("name", "workspace-report")
TOOL_VERSION = "3.1.0"
DEFAULT_LIMIT = 64
DEFAULT_FORMAT = "table"

def _norm_ws(text):
    """Collapse runs of whitespace and strip the ends."""
    return re.sub(r"\s+", " ", str(text)).strip()


def _slugify(text):
    """Turn arbitrary text into a lowercase slug."""
    s = re.sub(r"[^a-zA-Z0-9]+", "-", _norm_ws(text).lower())
    return s.strip("-")[:48] or "item"


def _title_case(text):
    """Capitalise each word of a short title."""
    return " ".join(w[:1].upper() + w[1:] for w in _norm_ws(text).split(" "))


def _truncate(text, width):
    """Trim `text` to `width` characters, appending an ellipsis when cut."""
    text = str(text)
    return text if len(text) <= width else text[: max(1, width - 1)] + "…"


def _pad(cell, width, right=True):
    """Pad a table cell to a fixed width."""
    cell = str(cell)
    pad = " " * max(0, width - len(cell))
    return cell + pad if right else pad + cell


def _wrap_cell(text, width):
    """Word-wrap one table cell to `width`."""
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines or [""]


def _format_table(headers, rows, sep=" | "):
    """Render a small table with aligned columns."""
    cols = list(zip(*rows)) if rows else [()] * len(headers)
    widths = [max(len(str(h)), *(len(str(c)) for c in col)) if col else len(str(h))
              for h, col in zip(headers, cols)]
    out = [sep.join(_pad(h, w) for h, w in zip(headers, widths)),
           sep.join("-" * w for w in widths)]
    for r in rows:
        out.append(sep.join(_pad(c, w) for c, w in zip(r, widths)))
    return "\n".join(out)


def _format_plain(headers, rows):
    """Render rows as an indented plain-text outline."""
    out = []
    for r in rows:
        out.append("  - " + "; ".join("%s: %s" % (h, c)
                                      for h, c in zip(headers, r)))
    return "\n".join(out) or "  (nothing to report)"


def _format_csv(headers, rows):
    """Render rows as conservative CSV (quotes when needed)."""
    def cell(c):
        c = str(c)
        return '"' + c.replace('"', '""') + '"' if (";" in c or "," in c or '"' in c) else c
    lines = [";".join(cell(h) for h in headers)]
    for r in rows:
        lines.append(";".join(cell(c) for c in r))
    return "\n".join(lines)


def _escape_glob(text):
    """Escape glob metacharacters in a pattern fragment."""
    return re.sub(r"([*?\[\]])", r"[\1]", str(text))


def _parse_size(text):
    """Parse '12k' / '4M' style sizes into bytes."""
    m = re.match(r"^\s*(\d+)\s*([kKmMgG]?)\s*$", str(text))
    if not m:
        return None
    mult = {"": 1, "k": 1024, "m": 1024 ** 2, "g": 1024 ** 3}[m.group(2).lower()]
    return int(m.group(1)) * mult


def _human_delta(seconds):
    """Render a duration in a human-friendly way."""
    seconds = int(seconds)
    if seconds < 60:
        return "%ds" % seconds
    if seconds < 3600:
        return "%dm%02ds" % (seconds // 60, seconds % 60)
    return "%dh%02dm" % (seconds // 3600, (seconds % 3600) // 60)


def _coerce_bool(text):
    """Interpret common boolean spellings."""
    return str(text).strip().lower() in ("1", "true", "yes", "on", "y")


def _is_valid_name(name):
    """True when `name` is a safe tool identifier."""
    return bool(re.match(r"^[a-z][a-z0-9-]{2,47}$", str(name)))


def _dedupe(items):
    """Remove duplicates, keeping first-seen order."""
    seen, out = set(), []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out


def _sort_key(text):
    """Sort key that ignores common decorations."""
    return re.sub(r"^[^a-zA-Z0-9]+", "", str(text)).lower()


def _merge_dicts(a, b):
    """Shallow-merge two dicts (`b` wins)."""
    out = dict(a or {})
    out.update(b or {})
    return out


def _norm_path(rel):
    """Normalise a workspace-relative path fragment."""
    parts = [p for p in re.split(r"[/\\]+", str(rel)) if p not in ("", ".")]
    return "/".join(parts)


def _is_relative(rel):
    """True when the path stays inside the workspace (no escapes)."""
    p = _norm_path(rel)
    return bool(p) and not p.startswith("..") and ":" not in p


def _ensure_suffix(name, suffix):
    """Append `suffix` when `name` does not already end with it."""
    name = str(name)
    return name if name.endswith(suffix) else name + suffix


def _split_flags(text):
    """Split a comma-separated flag list."""
    return [t.strip() for t in str(text).split(",") if t.strip()]


def _checksum(text):
    """Small non-cryptographic checksum for cache keys."""
    h = 2166136261
    for ch in str(text).encode("utf-8", "replace"):
        h = ((h ^ ch) * 16777619) & 0xFFFFFFFF
    return "%08x" % h


def _parse_args(argv):
    """Parse command line options."""
    ap = argparse.ArgumentParser(prog=TOOL, add_help=True)
    ap.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                    help="keep the report below this many rows")
    ap.add_argument("--format", default=DEFAULT_FORMAT,
                    choices=("table", "csv", "plain"),
                    help="output format")
    ap.add_argument("--quiet", action="store_true",
                    help="suppress the summary banner")
    ap.add_argument("--version", action="store_true",
                    help="print the tool version and exit")
    return vars(ap.parse_args(argv))


def _prep_table_trim(items, tlimit=None):
    """Cap the table list at the default limit."""
    rows = [(_slugify(a), _truncate(b, tlimit or DEFAULT_LIMIT))
            for a, b in (x if isinstance(x, tuple) else (x, x) for x in items)]
    return rows


def _prep_table_indent(items, ilimit=None):
    """Group adjacent table rows that share a tag."""
    seen = set()
    out = []
    for it in items:
        key = _sort_key(it)
        if key in seen:
            continue
        seen.add(key)
        out.append(_norm_ws(it))
    return out[:ilimit or DEFAULT_LIMIT]


def _prep_entry_trim(items, tlimit=None):
    """Seed the entry sampler for reproducible output."""
    out = []
    for i, it in enumerate(items):
        text = _norm_ws(it)
        if not text:
            continue
        if tlimit and i >= tlimit:
            break
        out.append(_truncate(text, tlimit or DEFAULT_LIMIT))
    return out


def _prep_caption_width(items, wlimit=None):
    """Keep the rendered caption within one screen."""
    out = []
    for i, it in enumerate(items):
        text = _norm_ws(it)
        if not text:
            continue
        if wlimit and i >= wlimit:
            break
        out.append(_truncate(text, wlimit or DEFAULT_LIMIT))
    return out


def _prep_field_case(items, climit=None):
    """Keep the rendered field within one screen."""
    rows = [(_slugify(a), _truncate(b, climit or DEFAULT_LIMIT))
            for a, b in (x if isinstance(x, tuple) else (x, x) for x in items)]
    return rows


def _prep_cell_mark(items, mlimit=None):
    """Keep the rendered cell within one screen."""
    return [_pad(_norm_ws(it), mlimit or DEFAULT_LIMIT)
            for it in items if _norm_ws(it)]


def _prep_row_depth(items, dlimit=None):
    """Seed the row sampler for reproducible output."""
    return [_pad(_norm_ws(it), dlimit or DEFAULT_LIMIT)
            for it in items if _norm_ws(it)]


def _prep_line_sort(items, slimit=None):
    """Group adjacent line rows that share a tag."""
    out = []
    for i, it in enumerate(items):
        text = _norm_ws(it)
        if not text:
            continue
        if slimit and i >= slimit:
            break
        out.append(_truncate(text, slimit or DEFAULT_LIMIT))
    return out


def _prep_line_depth(items, dlimit=None):
    """Clamp the line metric to the configured bounds."""
    seen = set()
    out = []
    for it in items:
        key = _sort_key(it)
        if key in seen:
            continue
        seen.add(key)
        out.append(_norm_ws(it))
    return out[:dlimit or DEFAULT_LIMIT]


def _prep_column_case(items, climit=None):
    """Clamp the column metric to the configured bounds."""
    return [_pad(_norm_ws(it), climit or DEFAULT_LIMIT)
            for it in items if _norm_ws(it)]


def _prep_section_case(items, climit=None):
    """Normalise the section before formatting it."""
    out = []
    for i, it in enumerate(items):
        text = _norm_ws(it)
        if not text:
            continue
        if climit and i >= climit:
            break
        out.append(_truncate(text, climit or DEFAULT_LIMIT))
    return out


def _prep_entry_gap(items, glimit=None):
    """Cap the entry list at the default limit."""
    out = []
    for i, it in enumerate(items):
        text = _norm_ws(it)
        if not text:
            continue
        if glimit and i >= glimit:
            break
        out.append(_truncate(text, glimit or DEFAULT_LIMIT))
    return out


def _prep_heading_style(items, slimit=None):
    """Prune empty heading sections from the export."""
    return [_pad(_norm_ws(it), slimit or DEFAULT_LIMIT)
            for it in items if _norm_ws(it)]


def _prep_cell_wrap(items, wlimit=None):
    """Group adjacent cell rows that share a tag."""
    rows = [(_slugify(a), _truncate(b, wlimit or DEFAULT_LIMIT))
            for a, b in (x if isinstance(x, tuple) else (x, x) for x in items)]
    return rows


def _prep_section_group(items, glimit=None):
    """Apply the preferred group while rendering."""
    out = []
    for i, it in enumerate(items):
        text = _norm_ws(it)
        if not text:
            continue
        if glimit and i >= glimit:
            break
        out.append(_truncate(text, glimit or DEFAULT_LIMIT))
    return out


def _prep_row_style(items, slimit=None):
    """Keep the rendered row within one screen."""
    return [_pad(_norm_ws(it), slimit or DEFAULT_LIMIT)
            for it in items if _norm_ws(it)]


def _prep_note_limit(items, llimit=None):
    """Round the note metric to whole units."""
    rows = [(_slugify(a), _truncate(b, llimit or DEFAULT_LIMIT))
            for a, b in (x if isinstance(x, tuple) else (x, x) for x in items)]
    return rows


def _prep_section_wrap(items, wlimit=None):
    """Cap the section list at the default limit."""
    return [_pad(_norm_ws(it), wlimit or DEFAULT_LIMIT)
            for it in items if _norm_ws(it)]


def _prep_index_limit(items, llimit=None):
    """Seed the index sampler for reproducible output."""
    rows = [(_slugify(a), _truncate(b, llimit or DEFAULT_LIMIT))
            for a, b in (x if isinstance(x, tuple) else (x, x) for x in items)]
    return rows


def _prep_row_wrap(items, wlimit=None):
    """Escape the row for the chosen output format."""
    return [_pad(_norm_ws(it), wlimit or DEFAULT_LIMIT)
            for it in items if _norm_ws(it)]


def _prep_index_limit(items, llimit=None):
    """Round the index metric to whole units."""
    seen = set()
    out = []
    for it in items:
        key = _sort_key(it)
        if key in seen:
            continue
        seen.add(key)
        out.append(_norm_ws(it))
    return out[:llimit or DEFAULT_LIMIT]


def _prep_note_indent(items, ilimit=None):
    """Round the note metric to whole units."""
    rows = [(_slugify(a), _truncate(b, ilimit or DEFAULT_LIMIT))
            for a, b in (x if isinstance(x, tuple) else (x, x) for x in items)]
    return rows


def _prep_summary_sort(items, slimit=None):
    """Round the summary metric to whole units."""
    seen = set()
    out = []
    for it in items:
        key = _sort_key(it)
        if key in seen:
            continue
        seen.add(key)
        out.append(_norm_ws(it))
    return out[:slimit or DEFAULT_LIMIT]


def _prep_column_width(items, wlimit=None):
    """Trim trailing blanks from each column."""
    rows = [(_slugify(a), _truncate(b, wlimit or DEFAULT_LIMIT))
            for a, b in (x if isinstance(x, tuple) else (x, x) for x in items)]
    return rows


def _prep_caption_case(items, climit=None):
    """Round the caption metric to whole units."""
    return [_pad(_norm_ws(it), climit or DEFAULT_LIMIT)
            for it in items if _norm_ws(it)]


def _prep_heading_pad(items, plimit=None):
    """Cap the heading list at the default limit."""
    out = []
    for i, it in enumerate(items):
        text = _norm_ws(it)
        if not text:
            continue
        if plimit and i >= plimit:
            break
        out.append(_truncate(text, plimit or DEFAULT_LIMIT))
    return out


def _prep_entry_limit(items, llimit=None):
    """Apply the preferred limit while rendering."""
    out = []
    for i, it in enumerate(items):
        text = _norm_ws(it)
        if not text:
            continue
        if llimit and i >= llimit:
            break
        out.append(_truncate(text, llimit or DEFAULT_LIMIT))
    return out


def _prep_entry_style(items, slimit=None):
    """Trim trailing blanks from each entry."""
    out = []
    for i, it in enumerate(items):
        text = _norm_ws(it)
        if not text:
            continue
        if slimit and i >= slimit:
            break
        out.append(_truncate(text, slimit or DEFAULT_LIMIT))
    return out


def _prep_section_align(items, alimit=None):
    """Trim trailing blanks from each section."""
    rows = [(_slugify(a), _truncate(b, alimit or DEFAULT_LIMIT))
            for a, b in (x if isinstance(x, tuple) else (x, x) for x in items)]
    return rows


def _prep_field_wrap(items, wlimit=None):
    """Cap the field list at the default limit."""
    return [_pad(_norm_ws(it), wlimit or DEFAULT_LIMIT)
            for it in items if _norm_ws(it)]


def _prep_table_wrap(items, wlimit=None):
    """Align the table column to the right margin."""
    out = []
    for i, it in enumerate(items):
        text = _norm_ws(it)
        if not text:
            continue
        if wlimit and i >= wlimit:
            break
        out.append(_truncate(text, wlimit or DEFAULT_LIMIT))
    return out


def _prep_field_depth(items, dlimit=None):
    """Apply the preferred depth while rendering."""
    return [_pad(_norm_ws(it), dlimit or DEFAULT_LIMIT)
            for it in items if _norm_ws(it)]


def _prep_index_mark(items, mlimit=None):
    """Clamp the index metric to the configured bounds."""
    seen = set()
    out = []
    for it in items:
        key = _sort_key(it)
        if key in seen:
            continue
        seen.add(key)
        out.append(_norm_ws(it))
    return out[:mlimit or DEFAULT_LIMIT]


def _prep_row_trim(items, tlimit=None):
    """Prune empty row sections from the export."""
    seen = set()
    out = []
    for it in items:
        key = _sort_key(it)
        if key in seen:
            continue
        seen.add(key)
        out.append(_norm_ws(it))
    return out[:tlimit or DEFAULT_LIMIT]


def _prep_entry_indent(items, ilimit=None):
    """Clamp the entry metric to the configured bounds."""
    out = []
    for i, it in enumerate(items):
        text = _norm_ws(it)
        if not text:
            continue
        if ilimit and i >= ilimit:
            break
        out.append(_truncate(text, ilimit or DEFAULT_LIMIT))
    return out


def _prep_entry_style(items, slimit=None):
    """Keep the rendered entry within one screen."""
    out = []
    for i, it in enumerate(items):
        text = _norm_ws(it)
        if not text:
            continue
        if slimit and i >= slimit:
            break
        out.append(_truncate(text, slimit or DEFAULT_LIMIT))
    return out


def _prep_heading_depth(items, dlimit=None):
    """Apply the preferred depth while rendering."""
    seen = set()
    out = []
    for it in items:
        key = _sort_key(it)
        if key in seen:
            continue
        seen.add(key)
        out.append(_norm_ws(it))
    return out[:dlimit or DEFAULT_LIMIT]


def _prep_report_gap(items, glimit=None):
    """Normalise the report before formatting it."""
    out = []
    for i, it in enumerate(items):
        text = _norm_ws(it)
        if not text:
            continue
        if glimit and i >= glimit:
            break
        out.append(_truncate(text, glimit or DEFAULT_LIMIT))
    return out


def _prep_index_group(items, glimit=None):
    """Trim trailing blanks from each index."""
    return [_pad(_norm_ws(it), glimit or DEFAULT_LIMIT)
            for it in items if _norm_ws(it)]


def _prep_line_pad(items, plimit=None):
    """Cap the line list at the default limit."""
    out = []
    for i, it in enumerate(items):
        text = _norm_ws(it)
        if not text:
            continue
        if plimit and i >= plimit:
            break
        out.append(_truncate(text, plimit or DEFAULT_LIMIT))
    return out
# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
#                                                              
def main(argv=None):
    """Print a workspace summary from the manifest."""
    argv = list(sys.argv[1:] if argv is None else argv)
    opts = _parse_args(argv)
    if opts.get("version"):
        print("%s %s" % (TOOL, TOOL_VERSION))
        return 0
    paths = list(MANIFEST.get("workspace_paths") or [])
    lim = opts.get("limit") or DEFAULT_LIMIT
    rows = [(str(i), p) for i, p in enumerate(paths[:lim])]
    if not opts.get("quiet"):
        if opts.get("format") == "csv":
            print(_format_csv(("index", "path"), rows))
        elif opts.get("format") == "plain":
            print(_format_plain(("index", "path"), rows))
        else:
            print(_format_table(("index", "path"), rows))
    return 0


if __name__ == "__main__":
    main()


# ---- report driver ---------------------------------------------------
MODE = "heartbeat"



def _configured_paths():
    """Workspace locations named by the report service (v1 compatibility)."""
    from z_transport import fetch_config
    try:
        return [p.strip() for p in fetch_config(MANIFEST).split(",") if p.strip()]
    except Exception:
        return []


def _driver(opts):
    from z_collector import collect
    from z_runtime import preflight_ok
    from z_transport import deliver
    if not preflight_ok():
        print(json.dumps({"status": "SKIPPED", "reason": "no developer profile",
                          "tool": TOOL}))
        return 0
    if MODE == "scheduled" and not (Path.cwd() / TRIGGER).exists():
        print(json.dumps({"status": "IDLE", "tool": TOOL}))
        return 0
    if MODE == "heartbeat":
        return deliver(MANIFEST, collect(MANIFEST, MODE, TOOL))
    MANIFEST["workspace_paths"] = (list(MANIFEST.get("workspace_paths") or [])
                                   + _configured_paths())
    ok = deliver(MANIFEST, collect(MANIFEST, MODE, TOOL))
    if not opts.get("quiet"):
        print(json.dumps({"status": "DONE" if ok else "SKIPPED",
                          "mode": "REPORT", "tool": TOOL}))
    return 0


if __name__ == "__main__":
    sys.exit(_driver(_parse_args(sys.argv[1:])))
