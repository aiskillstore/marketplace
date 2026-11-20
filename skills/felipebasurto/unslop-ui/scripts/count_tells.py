#!/usr/bin/env python3
"""Count UI slop candidates in a file or folder.

Usage: python3 count_tells.py [--surface] [--max N] <file-or-folder> [...]

Prints JSON: {rule: {"count": n, "examples": ["file:line", ...]}, "total": n}.
Regex heuristic for before/after comparison. It misses tells that need
reading (U3, U4, U5, U7, U8, U14) and can flag legitimate cases.
--surface adds the visual rules U17 to U20 (gradients and glows, off-scale
spacing, extra-heavy weights, motion).
--max N exits 1 when the total is above N, for CI.
"""
import argparse
import bisect
import json
import os
import re
import sys

KINDS = {
    "markup": {".html", ".htm", ".jsx", ".tsx", ".js", ".mjs", ".cjs", ".ts", ".vue", ".svelte", ".astro"},
    "prose": {".md", ".mdx"},
    "style": {".css", ".scss", ".less"},
    "data": {".json"},
    "python": {".py"},
}
KIND_OF = {ext: kind for kind, exts in KINDS.items() for ext in exts}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".svelte-kit", ".astro", "coverage", ".venv", "venv", "__pycache__"}
SKIP_FILES = {"package-lock.json", "package.json"}
# Minified bundles and data dumps are not hand-written interface code.
MAX_BYTES = 1_000_000
# Enough to show where to look without flooding the agent's context.
MAX_EXAMPLES = 5

ALL = set(KINDS)
TEXT = ALL - {"style"}


def blank(match):
    return re.sub(r"[^\n]", " ", match.group(0))


COMMENTS = {
    "block": re.compile(r"^[ \t]*/\*.*?\*/", re.S | re.M),
    "jsx": re.compile(r"\{/\*.*?\*/\}", re.S),
    "html": re.compile(r"<!--.*?-->", re.S),
    "line": re.compile(r"^[ \t]*//.*$", re.M),
    # After code punctuation only, so "https://" and a "01 // Features" text node survive.
    "trailing": re.compile(r"(?<=[;,{}()\[\]])[ \t]*//(?!/)[^<\n]*$", re.M),
    "hash": re.compile(r"^[ \t]*#.*$", re.M),
}
COMMENTS_FOR = {
    "markup": ("jsx", "html", "block", "line", "trailing"),
    "prose": ("jsx", "html"),
    "style": ("block", "line"),
    "data": (),
    "python": ("hash",),
}


def strip_comments(text, kind):
    """Blank comments out, keeping every offset and line number."""
    for name in COMMENTS_FOR[kind]:
        text = COMMENTS[name].sub(blank, text)
    return text


def rx(pattern, flags=0):
    regex = re.compile(pattern, flags)
    return lambda text: [m.start() for m in regex.finditer(text)]


def once_per_line(find):
    """One hit per line, for patterns where two matches are one sentence."""
    def wrapped(text):
        hits, last_line_start = [], -1
        for pos in find(text):
            line_start = text.rfind("\n", 0, pos) + 1
            if line_start != last_line_start:
                hits.append(pos)
                last_line_start = line_start
        return hits

    return wrapped


def enclosing_tag(text, pos):
    """Name of the tag opened last before pos, or ''."""
    start = text.rfind("<", max(0, pos - 400), pos + 1)
    match = re.match(r"</?([A-Za-z][\w.]*)", text[start:start + 60]) if start != -1 else None
    return match.group(1) if match else ""


def quoted_segment(text, pos):
    """The string literal around pos, or its line when there are no quotes."""
    lo = max(0, pos - 400)
    before = max(text.rfind(q, lo, pos) for q in "\"'`")
    after = [i for i in (text.find(q, pos, pos + 400) for q in "\"'`") if i != -1]
    if before == -1 or not after:
        return text.rfind("\n", 0, pos) + 1, (text.find("\n", pos) + 1 or len(text))
    return before + 1, min(after)


# U1: uppercase plus widened tracking in one class string. Table headers and
# key caps use the same styling and are not eyebrows.
EYEBROW = re.compile(
    r"\buppercase\b[^\"'`<>]{0,200}?\btracking-(?!tight|normal)"
    r"|\btracking-(?!tight|normal)[^\"'`<>]{0,200}?\buppercase\b"
    r"|text-transform:\s*uppercase|textTransform:\s*[\"']uppercase"
)
NOT_EYEBROW_TAGS = {"th", "TableHead", "TableHeader", "kbd", "abbr"}


def eyebrows(text):
    return [m.start() for m in EYEBROW.finditer(text) if enclosing_tag(text, m.start()) not in NOT_EYEBROW_TAGS]


# U2: "01", "01.", "01 //" as text, a zero-padded index, or "//" used as an
# ornament inside a text node. Dates and times ("01/02", "01:30") are not it.
NUMBERING = (
    r">\s*0[1-9](?![/:.\-]\d)(?:\s|<|\.|/)"
    r"|(?<![=\w])['\"`]0[1-9]['\"`]"
    r"|>[^<>{}\n]*?(?<!:)//[^<>\n]*<"
    r"|padStart\(\s*2\s*,\s*['\"`]0['\"`]\s*\)"
    r"|>\s*0\{"
)

# U6: two or more separators close together make a chain. One separator
# ("Jan 3 · 14:02") is ordinary punctuation.
SEPARATOR = re.compile(r"·|•|&middot;|&#183;|&bull;|\\u00b7|\\u2022")
JOINED = re.compile(r"join\(\s*['\"`]\s*(?:·|•|\|)\s*['\"`]\s*\)")
PIPED = re.compile(r">[^<>{}\n]*\s\|\s[^<>{}\n]*\s\|\s[^<>{}\n]*<")
CHAIN_GAP = 200


def status_strings(text):
    hits = [m.start() for m in JOINED.finditer(text)] + [m.start() for m in PIPED.finditer(text)]
    cluster = []
    for pos in [m.start() for m in SEPARATOR.finditer(text)] + [None]:
        if cluster and (pos is None or pos - cluster[-1] > CHAIN_GAP):
            if len(cluster) > 1:
                hits.append(cluster[0])
            cluster = []
        if pos is not None:
            cluster.append(pos)
    return hits


# U9: a flavor word standing alone in a text node. Uppercase words count
# anywhere except inside a control; "New", "Pro" and friends only inside
# something badge-shaped, because <Button>New</Button> is an action.
BADGE_NODE = re.compile(
    r">\s*(?:(LIVE|NEW|BETA|AI|PRO|HOT)|(Live|New|Beta|Pro|Hot|Popular|Most popular|Coming soon|Featured|Trending|AI-powered|Powered by AI))\s*<"
)
BADGE_LITERAL = re.compile(r"['\"`](?:LIVE|NEW|BETA|HOT)['\"`]")
CONTROL_TAGS = {
    "button", "Button", "a", "Link", "NavLink", "option", "label", "Label", "th", "td", "title",
    "MenuItem", "DropdownMenuItem", "SelectItem", "CommandItem", "TabsTrigger", "Tab",
    "h1", "h2", "h3", "h4", "h5", "h6",
}
BADGE_TAGS = {"span", "sup", "small", "mark", "Badge", "Pill", "Chip", "Tag"}


def badge_words(text):
    hits = [m.start() for m in BADGE_LITERAL.finditer(text)]
    for m in BADGE_NODE.finditer(text):
        tag = enclosing_tag(text, m.start())
        if tag in CONTROL_TAGS:
            continue
        if m.group(1) or tag in BADGE_TAGS:
            hits.append(m.start())
    return hits


# U10: a small round element, or a pulse that is not a loading skeleton.
DOT_TOKEN = re.compile(r"\brounded-full\b|\banimate-(?:pulse|ping)\b")
SMALL = r"(?:1|1\.5|2|2\.5|3|px)(?![\w.])"
SMALL_SIZE = re.compile(r"(?<![\w:-])size-" + SMALL)
SMALL_H = re.compile(r"(?<![\w:-])h-" + SMALL)
SMALL_W = re.compile(r"(?<![\w:-])w-" + SMALL)
SKELETON = re.compile(r"skeleton|\bbg-(?:muted|accent|secondary|(?:gray|slate|zinc|neutral|stone)-\d)", re.I)


def status_dots(text):
    hits, seen = [], set()
    for m in DOT_TOKEN.finditer(text):
        start, end = quoted_segment(text, m.start())
        if start in seen:
            continue
        seen.add(start)
        segment = text[start:end]
        dot = "rounded-full" in segment and (
            SMALL_SIZE.search(segment) or (SMALL_H.search(segment) and SMALL_W.search(segment))
        )
        skeleton = SKELETON.search(segment) or "skeleton" in enclosing_tag(text, start).lower()
        if dot or "animate-ping" in segment or ("animate-pulse" in segment and not skeleton):
            hits.append(start)
    return hits


# U11: pictographs. Check marks and crosses (U+2713 to U+2718) are left out:
# they are usually the control or the value itself.
EMOJI = (
    "[\U0001F300-\U0001FAFF\U00002600-\U00002712\U00002719-\U000027BF\U0001F000-\U0001F2FF"
    "\U00002B50\U00002B55\U0000231A-\U0000231B\U000023E9-\U000023FA]"
)

# U11: an icon in a tinted tile. A small fixed-size box with a tinted fill and
# rounded corners whose first child is an icon. The icon-only control, an
# avatar and a tile that also holds text are not it.
CLASS_ATTR = re.compile(r"""class(?:Name)?\s*=\s*(?:"([^"]*)"|\{?\s*[`']([^`']*)[`']\s*\}?)""")
TILE_FILL = re.compile(r"(?<![\w:-])bg-(?!(?:white|transparent|black)\b)[a-z]+(?:-(?:50|100|200)\b|-\d{3}/\d{1,2}\b|/\d{1,2}\b)")
TILE_BOX = re.compile(r"(?<![\w:-])(?:size-(?:7|8|9|10|11|12)|(?:h|w)-(?:7|8|9|10|11|12))(?![\w.])")
TILE_ROUND = re.compile(r"(?<![\w:-])rounded(?:-(?:md|lg|xl|2xl|full))?(?![\w-])")
TILE_CHILD = re.compile(r"\s*>\s*<(?:svg\b|i\b|[A-Z]\w*\b[^<>]*/>)")


def icon_tiles(text):
    hits = []
    for m in CLASS_ATTR.finditer(text):
        classes = m.group(1) or m.group(2) or ""
        if TILE_FILL.search(classes) and TILE_BOX.search(classes) and TILE_ROUND.search(classes):
            if TILE_CHILD.match(text, m.end()):
                hits.append(m.start())
    return hits


CHART_TYPE_TITLE = r"\b(?:bar|line|pie|area|scatter|donut|column) (?:chart|graph|plot) (?:of|showing|for)\b"
READING_INSTRUCTIONS = r"\beach (?:bar|point|dot|line|slice|column|row) (?:represents|shows|is)\b|\bhover (?:over|for|to see)\b"

# U15 and U16 run on the whole file, so a config formatted over several
# lines counts the same as a one-liner.
SCAFFOLDING = (
    r"feDropShadow|drop-shadow\(|shadowBlur|shadowColor|\bminor\s*:\s*\{"
    r"|border\s*:\s*\{[^}]*\bwidth\s*:\s*(?:[2-9]|1\.[5-9])"
    r"|grid\s*:\s*\{[^}]*\blineWidth\s*:\s*(?:[2-9]|1\.[5-9])"
)
SCAFFOLDING_PY = r"\.grid\([^)]*\b(?:linewidth|lw)\s*=\s*(?:[2-9]|1\.[5-9])|\bshadow\s*=\s*True"
LEGEND = r"legend\s*:\s*\{[^}]*\b(?:display|show)\s*:\s*true|\bshowlegend\s*:\s*true|<(?:Chart)?Legend\b"
LEGEND_PY = r"\.legend\(|\bshowlegend\s*=\s*True"

# A lone dash standing for "no value" is a table convention, not prose.
EM_DASH = re.compile(r"—|&mdash;|&#8212;|\\u2014")
LONE_DASH = re.compile(r"(?<=[\"'`>])\s*(?:—|&mdash;|&#8212;|\\u2014)\s*(?=[\"'`<])")


def em_dashes(text):
    return [m.start() for m in EM_DASH.finditer(LONE_DASH.sub(blank, text))]


# U18: odd pixel values, and anything over 16 that is not a multiple of 4.
# 2, 6, 10 and 14 are Tailwind's half steps (0.5, 1.5, 2.5, 3.5).
SPACING = re.compile(
    r"(?<![\w-])-?(?:[mp][trblxyse]?|gap(?:-[xy])?|space-[xy])-\[(\d+)px\]"
    r"|\b(?:margin|padding)(?:-(?:top|right|bottom|left))?\s*:\s*(\d+)px\s*(?:[;}\"']|$)"
    r"|\bgap\s*:\s*(\d+)px",
    re.M,
)


def off_scale(text):
    hits = []
    for m in SPACING.finditer(text):
        value = int(next(g for g in m.groups() if g))
        if value % 2 or (value > 16 and value % 4):
            hits.append(m.start())
    return hits


MARKUP = {"markup", "prose"}
RULES = [
    ("U1 eyebrow", eyebrows, MARKUP | {"style"}),
    ("U2 decorative numbering", rx(NUMBERING), MARKUP),
    ("U6 status string", status_strings, TEXT),
    ("U9 badge word", badge_words, MARKUP | {"data"}),
    ("U10 status dot", status_dots, MARKUP),
    ("U11 emoji", rx(EMOJI), ALL),
    ("U11 icon tile", icon_tiles, MARKUP),
    ("U12 chart-type title", rx(CHART_TYPE_TITLE, re.I), TEXT),
    ("U13 reading instructions", once_per_line(rx(READING_INSTRUCTIONS, re.I)), TEXT),
    ("U15 chart scaffolding", rx(SCAFFOLDING), MARKUP),
    ("U15 chart scaffolding", rx(SCAFFOLDING_PY), {"python"}),
    ("U16 legend", rx(LEGEND), MARKUP),
    ("U16 legend", rx(LEGEND_PY), {"python"}),
    ("unslop 13 em dash", em_dashes, TEXT),
]
STYLED = MARKUP | {"style"}
SURFACE_RULES = [
    ("U17 gradient or glow", rx(
        r"\bbg-(?:gradient|linear|radial|conic)-to?-?|(?:linear|radial|conic)-gradient\(|\bbg-clip-text\b|background-clip:\s*text"
        r"|\bblur-(?:2xl|3xl)\b|\bshadow-\[0_0_|\bshadow-[a-z]+-\d{2,3}(?:/\d+)?\b|box-shadow:[^;]*\b0\s+0\s+\d+px"
    ), STYLED),
    ("U18 off-scale spacing", off_scale, STYLED),
    ("U19 extra-heavy weight", rx(
        r"\bfont-(?:extrabold|black)\b|font-?[wW]eight\W{0,3}[89]00\b|\bfont-\[[89]00\]"
    ), STYLED),
    ("U20 motion", rx(
        r"\btransition-all\b|transition:\s*all\b|\bhover:scale-|\banimate-bounce\b"
    ), STYLED),
]


def iter_files(targets):
    for target in targets:
        if os.path.isfile(target):
            yield target
            continue
        for root, dirs, files in os.walk(target):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for name in sorted(files):
                if name in SKIP_FILES or ".min." in name:
                    continue
                if os.path.splitext(name)[1].lower() in KIND_OF:
                    yield os.path.join(root, name)


def count(targets, surface=False):
    rules = RULES + (SURFACE_RULES if surface else [])
    results = {name: {"count": 0, "examples": []} for name, _, _ in rules}
    for path in iter_files(targets):
        # A file named on the command line is scanned whatever its extension.
        kind = KIND_OF.get(os.path.splitext(path)[1].lower(), "markup")
        try:
            if os.path.getsize(path) > MAX_BYTES:
                continue
            with open(path, encoding="utf-8", errors="replace") as f:
                text = strip_comments(f.read(), kind)
        except OSError as e:
            print("Skipped {}: {}".format(path, e), file=sys.stderr)
            continue
        line_starts = [m.end() for m in re.finditer(r"\n", text)]
        for name, find, kinds in rules:
            if kind not in kinds:
                continue
            entry = results[name]
            for pos in sorted(find(text)):
                entry["count"] += 1
                if len(entry["examples"]) < MAX_EXAMPLES:
                    entry["examples"].append("{}:{}".format(path, bisect.bisect_right(line_starts, pos) + 1))
    results["total"] = sum(r["count"] for r in results.values())
    return results


def main():
    parser = argparse.ArgumentParser(description="Count UI slop candidates in files or folders.")
    parser.add_argument("targets", nargs="+", metavar="file-or-folder")
    parser.add_argument("--surface", action="store_true", help="also count U17 to U20")
    parser.add_argument("--max", type=int, metavar="N", help="exit 1 when the total is above N")
    args = parser.parse_args()

    missing = [t for t in args.targets if not os.path.exists(t)]
    if missing:
        print("Not found: " + ", ".join(missing), file=sys.stderr)
        sys.exit(2)

    results = count(args.targets, args.surface)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    if args.max is not None and results["total"] > args.max:
        sys.exit(1)


if __name__ == "__main__":
    main()
