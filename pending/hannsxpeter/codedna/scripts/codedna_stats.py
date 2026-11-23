#!/usr/bin/env python3
"""Best-effort style statistics for codedna."""

import argparse
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from statistics import median

MAX_FILES_PER_LANG = 800
MAX_FILE_BYTES = 1_000_000
MAX_BYTES_PER_LINE = 400

IGNORE = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "out",
    "target",
    "vendor",
    ".next",
    ".svelte-kit",
    "venv",
    ".venv",
    "__pycache__",
    "coverage",
}

EXT = {
    ".js": "js",
    ".jsx": "js",
    ".mjs": "js",
    ".cjs": "js",
    ".ts": "ts",
    ".tsx": "ts",
    ".mts": "ts",
    ".cts": "ts",
    ".py": "py",
    ".go": "go",
    ".rs": "rs",
    ".java": "java",
    ".rb": "rb",
    ".php": "php",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".cs": "cs",
    ".swift": "swift",
    ".kt": "kt",
    ".kts": "kt",
}

HASH_COMMENT = {"py", "rb"}
QUOTE_LANGS = {"js", "ts", "py", "rb", "php"}
BOOLEAN_PREFIX_RE = re.compile(r"^(?:is|has|should|can|will|did)(?:[A-Z_]|$)")
TODO_RE = re.compile(r"\b(?:TODO|FIXME)\b")
WORD_RE = re.compile(r"\b[\w][\w'-]*\b", re.UNICODE)
FIRST_PERSON_RE = re.compile(r"\b(?:I|me|my|mine|we|us|our|ours)\b", re.I)
SECOND_PERSON_RE = re.compile(r"\b(?:you|your|yours)\b", re.I)
CONTRACTION_RE = re.compile(
    r"\b(?:[A-Za-z]+n't|(?:I|you|we|they|he|she|it)'(?:m|re|ve|ll|d|s))\b",
    re.I,
)
MESSAGE_LITERAL = r'(?:"((?:\\.|[^"\\\r\n])*)"|\'((?:\\.|[^\'\\\r\n])*)\'|`((?:\\.|[^`\\\r\n])*)`)'
QUOTE_KINDS = {'"': "double", "'": "single", "`": "backtick"}
REGEX_LITERAL = (
    r"(?:(?<=[(,=:\[!&|?{};])|(?<=\breturn)|^)[ \t]*"
    r"/(?![/*])(?:\\.|\[(?:\\.|[^\]\\\n])*\]|[^/\\\[\n])+/"
)

ERROR_PREFIXES = {
    "js": r"\b(?:new\s+)?(?:[A-Za-z_$][\w$]*Error|Error)\s*\(\s*",
    "ts": r"\b(?:new\s+)?(?:[A-Za-z_$][\w$]*Error|Error)\s*\(\s*",
    "py": r"\braise\s+(?:[A-Za-z_]\w*(?:Error|Exception)|Error|Exception)\s*\(\s*",
    "go": r"\b(?:errors\.New|fmt\.Errorf)\s*\(\s*",
    "rs": r"(?:\bpanic!|\bbail!|\banyhow!|\.expect)\s*\(\s*",
    "java": r"\bthrow\s+new\s+(?:[A-Za-z_]\w*(?:Exception|Error)|Exception|Error)\s*\(\s*",
    "kt": r"\bthrow\s+(?:[A-Za-z_]\w*(?:Exception|Error)|Exception|Error)\s*\(\s*",
    "cs": r"\bthrow\s+new\s+(?:[A-Za-z_]\w*(?:Exception|Error)|Exception|Error)\s*\(\s*",
    "php": r"\bthrow\s+new\s+\\?(?:[A-Za-z_]\w*(?:Exception|Error)|Exception|Error)\s*\(\s*",
    "rb": r"\braise(?:\s+[A-Za-z_:]+\s*,)?\s*",
    "swift": r"\b(?:fatalError|preconditionFailure)\s*\(\s*",
    "cpp": r"\bthrow\s+(?:std::)?[A-Za-z_]\w*(?:error|exception)\s*\(\s*",
}

DOC_MARKERS = {
    "default": ("/**", "///"),
    "go": ("//",),
    "rs": ("///", "//!", "/**"),
}

PATS = {
    "js": {
        "function": [
            r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\(",
            r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?function\b",
            r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>",
        ],
        "type": [r"\b(?:interface|type)\s+([A-Za-z_$][\w$]*)"],
        "class": [r"\bclass\s+([A-Za-z_$][\w$]*)"],
        "constant": [r"\bconst\s+([A-Z_][A-Z0-9_]{2,})\b"],
        "variable": [r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\b"],
    },
    "py": {
        "function": [r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)"],
        "class": [r"^\s*class\s+([A-Za-z_]\w*)"],
        "constant": [r"^([A-Z_][A-Z0-9_]{2,})\s*="],
        "variable": [r"^\s*([A-Za-z_]\w*)\s*="],
    },
    "go": {
        "function": [r"\bfunc\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)"],
        "type": [r"\btype\s+([A-Za-z_]\w*)"],
    },
    "rs": {
        "function": [r"\bfn\s+([A-Za-z_]\w*)"],
        "type": [r"\b(?:struct|enum|trait)\s+([A-Za-z_]\w*)"],
    },
}
PATS["ts"] = PATS["js"]


def case(name):
    text = name.strip("_")
    if not text:
        return "other"
    if "-" in text:
        return "kebab"
    if "_" in text:
        if text.isupper():
            return "SCREAMING_SNAKE"
        if text.islower():
            return "snake_case"
        return "mixed"
    if text.isupper():
        return "UPPER"
    if text.islower():
        return "lower"
    return "PascalCase" if text[0].isupper() else "camelCase"


def walk_files(target):
    for root, dirs, names in os.walk(target):
        dirs[:] = [d for d in dirs if d not in IGNORE and not d.startswith(".")]
        for name in names:
            yield os.path.join(root, name)


def git_files(target):
    try:
        proc = subprocess.run(
            ["git", "-C", str(target), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    paths = []
    for raw in proc.stdout.split(b"\0"):
        parts = os.fsdecode(raw).split("/")
        if not raw or any(part in IGNORE or part.startswith(".") for part in parts[:-1]):
            continue
        path = os.path.join(target, *parts)
        if parts[-1]:
            paths.append(path)
        else:
            paths.extend(source_files(path))
    return paths


def source_files(target):
    return git_files(target) or list(walk_files(target))


def collect_files(target):
    files = defaultdict(set)
    for path in source_files(target):
        lang = EXT.get(os.path.splitext(path)[1].lower())
        if lang and os.path.isfile(path):
            files[lang].add(path)
    return {lang: sorted(paths) for lang, paths in files.items()}


def sample_paths(paths):
    if len(paths) <= MAX_FILES_PER_LANG:
        return paths
    step = len(paths) / MAX_FILES_PER_LANG
    return [paths[int(index * step)] for index in range(MAX_FILES_PER_LANG)]


def read_text(path):
    with open(path, encoding="utf-8-sig", errors="replace") as handle:
        return handle.read()


def comment_config(lang):
    token = "#" if lang in HASH_COMMENT else "//"
    if lang == "py":
        block = [('"""', '"""'), ("'''", "'''")]
    elif lang in HASH_COMMENT:
        block = []
    else:
        block = [("/*", "*/")]
    return token, block


def open_block(stripped, block, token):
    if not any(opener == closer for opener, closer in block):
        return None
    index = 0
    limit = len(stripped)
    while index < limit:
        rest = stripped[index:]
        if rest.startswith(token):
            return None
        for opener, closer in block:
            if opener == closer and rest.startswith(opener):
                end = stripped.find(closer, index + len(opener))
                if end < 0:
                    return closer
                index = end + len(closer)
                break
        else:
            char = stripped[index]
            if char in "'\"`":
                end = stripped.find(char, index + 1)
                index = limit if end < 0 else end + 1
            else:
                index += 1
    return None


def count_lines(lang, text):
    token, block = comment_config(lang)
    code = comment = tabs = spaces = 0
    pending = None
    for line in text.splitlines():
        stripped = line.strip()
        if pending is not None:
            closer, is_comment = pending
            if stripped:
                if is_comment:
                    comment += 1
                else:
                    code += 1
            if closer in line:
                pending = None
            continue
        if not stripped:
            continue
        if stripped.startswith(token):
            comment += 1
            continue
        hit = False
        for opener, closer in block:
            if stripped.startswith(opener):
                comment += 1
                if closer not in stripped[len(opener):]:
                    pending = (closer, True)
                hit = True
                break
        if hit:
            continue
        code += 1
        leading = line[: len(line) - len(line.lstrip())]
        if leading.startswith("\t"):
            tabs += 1
        elif leading.startswith(" "):
            spaces += 1
        closer = open_block(stripped, block, token)
        if closer:
            pending = (closer, False)
    return code, comment, tabs, spaces


def literal_pattern(lang):
    if lang in HASH_COMMENT:
        parts = [r"#[^\n]*"]
    else:
        parts = [r"//[^\n]*", r"(?<![\\\[])/\*[\s\S]*?\*/"]
    if lang == "py":
        parts += [r'"""[\s\S]*?"""', r"'''[\s\S]*?'''"]
    parts += [r'"(?:[^"\\\n]|\\.)*"', r"'(?:[^'\\\n]|\\.)*'"]
    if lang in {"js", "ts"}:
        parts.append(r"`(?:[^`\\]|\\[\s\S])*`")
        parts.append(REGEX_LITERAL)
    return re.compile("|".join(parts), re.M)


def count_quotes(lang, text):
    if lang not in QUOTE_LANGS:
        return Counter()
    counts = Counter({"double": 0, "single": 0})
    if lang in {"js", "ts"}:
        counts["backtick"] = 0
    for match in literal_pattern(lang).finditer(text):
        literal = match.group()
        if literal[:3] not in ('"""', "'''") and literal[0] in QUOTE_KINDS:
            counts[QUOTE_KINDS[literal[0]]] += 1
    return counts


def clean_comment_text(value):
    text = value.strip()
    if text.startswith("*"):
        text = text[1:].strip()
    return text


def comment_texts(lang, text):
    token, block = comment_config(lang)
    comments = []
    pending = None

    for line in text.splitlines():
        stripped = line.strip()
        if pending is not None:
            closer, is_comment = pending
            end = stripped.find(closer)
            if is_comment:
                value = stripped if end < 0 else stripped[:end]
                value = clean_comment_text(value)
                if value:
                    comments.append(value)
            if end >= 0:
                pending = None
            continue
        if not stripped:
            continue
        if stripped.startswith(token):
            value = clean_comment_text(stripped[len(token):])
            if value:
                comments.append(value)
            continue
        for opener, closer in block:
            if not stripped.startswith(opener):
                continue
            value = stripped[len(opener):]
            end = value.find(closer)
            if end >= 0:
                value = value[:end]
            else:
                pending = (closer, True)
            value = clean_comment_text(value)
            if value:
                comments.append(value)
            break
        else:
            closer = open_block(stripped, block, token)
            if closer:
                pending = (closer, False)

    return comments


def code_text_lines(lang, text):
    token, block = comment_config(lang)
    pending = None

    for line in text.splitlines():
        stripped = line.strip()
        if pending is not None:
            if pending in line:
                pending = None
            continue
        if not stripped or stripped.startswith(token):
            continue
        for opener, closer in block:
            if not stripped.startswith(opener):
                continue
            if closer not in stripped[len(opener):]:
                pending = closer
            break
        else:
            yield line
            closer = open_block(stripped, block, token)
            if closer:
                pending = closer


def error_messages(lang, text):
    prefix = ERROR_PREFIXES.get(lang)
    if not prefix:
        return []
    messages = []
    for line in code_text_lines(lang, text):
        for match in re.finditer(prefix + MESSAGE_LITERAL, line, re.I):
            messages.append(next(group for group in match.groups() if group is not None))
    return messages


def is_capitalized(text):
    first = next((char for char in text if char.isalpha()), "")
    return bool(first and first.isupper())


def has_terminal_punctuation(text):
    trimmed = text.rstrip().rstrip("`*_)]}'\"")
    return bool(trimmed and trimmed[-1] in ".?!")


def share(count, total):
    return round(100 * count / total, 1) if total else 0


def comment_voice(texts):
    samples = [text for text in texts if WORD_RE.search(text)]
    word_lengths = [len(WORD_RE.findall(text)) for text in samples]
    capitalized = sum(1 for text in samples if is_capitalized(text))
    punctuated = sum(1 for text in samples if has_terminal_punctuation(text))
    sentence_like = sum(
        1 for text in samples if is_capitalized(text) and has_terminal_punctuation(text)
    )
    first_person = sum(1 for text in samples if FIRST_PERSON_RE.search(text))
    second_person = sum(1 for text in samples if SECOND_PERSON_RE.search(text))
    contractions = sum(1 for text in samples if CONTRACTION_RE.search(text))
    total = len(samples)
    return {
        "lines": total,
        "word_lengths": summarize(word_lengths),
        "sentence_like_percent": share(sentence_like, total),
        "fragment_like_percent": share(total - sentence_like, total),
        "capitalized_percent": share(capitalized, total),
        "terminal_punctuation_percent": share(punctuated, total),
        "first_person_percent": share(first_person, total),
        "second_person_percent": share(second_person, total),
        "contractions_percent": share(contractions, total),
    }


def message_voice(messages):
    samples = [message.strip() for message in messages if WORD_RE.search(message)]
    total = len(samples)
    capitalized = sum(1 for message in samples if is_capitalized(message))
    punctuated = sum(1 for message in samples if has_terminal_punctuation(message))
    return {
        "messages": total,
        "capitalized_percent": share(capitalized, total),
        "terminal_punctuation_percent": share(punctuated, total),
    }


def percentile(values, pct):
    if not values:
        return 0
    ordered = sorted(values)
    index = round((pct / 100) * (len(ordered) - 1))
    return ordered[index]


def summarize(values):
    if not values:
        return {"count": 0, "median": 0, "p90": 0}
    return {
        "count": len(values),
        "median": median(values),
        "p90": percentile(values, 90),
    }


def add_file_case(naming, path):
    base = os.path.splitext(os.path.basename(path))[0]
    if base:
        naming["file"][case(base)] += 1


def add_identifier_cases(lang, text, naming, lengths, boolean_names):
    claimed = set()
    for kind, patterns in PATS.get(lang, {}).items():
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.M):
                if match.start(1) in claimed:
                    continue
                claimed.add(match.start(1))
                name = match.group(1)
                naming[kind][case(name)] += 1
                lengths[kind].append(len(name.strip("_")))
                if name and name[0].islower():
                    boolean_names.append(name)


def leading_indent(line):
    return len(line) - len(line.lstrip())


def py_function_lengths(text):
    lengths = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not re.match(r"^\s*(?:async\s+)?def\s+[A-Za-z_]\w*", line):
            continue
        indent = leading_indent(line)
        end = index + 1
        for cursor in range(index + 1, len(lines)):
            stripped = lines[cursor].strip()
            if not stripped:
                continue
            if leading_indent(lines[cursor]) <= indent and not stripped.startswith("#"):
                break
            end = cursor + 1
        lengths.append(max(1, end - index))
    return lengths


def brace_function_lengths(text):
    starts = re.compile(
        r"\bfunction\s+[A-Za-z_$][\w$]*\s*\(|"
        r"\b(?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=\s*(?:async\s*)?(?:function\b|\([^)]*\)\s*=>|[A-Za-z_$][\w$]*\s*=>)|"
        r"\bfunc\s+(?:\([^)]*\)\s*)?[A-Za-z_]\w*|"
        r"\bfn\s+[A-Za-z_]\w*"
    )
    lengths = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not starts.search(line):
            continue
        if "=>" in line and "{" not in line:
            lengths.append(1)
            continue
        balance = 0
        saw_brace = False
        end = index
        for cursor in range(index, len(lines)):
            balance += lines[cursor].count("{")
            balance -= lines[cursor].count("}")
            saw_brace = saw_brace or "{" in lines[cursor]
            end = cursor
            if saw_brace and balance <= 0:
                break
        lengths.append(max(1, end - index + 1))
    return lengths


def function_lengths(lang, text):
    if lang == "py":
        return py_function_lengths(text)
    if lang in {"js", "ts", "go", "rs"}:
        return brace_function_lengths(text)
    return []


def closes_doc_block(lines, cursor):
    if not lines[cursor].strip().endswith("*/"):
        return False
    opener = cursor
    while opener >= 0 and "/*" not in lines[opener]:
        opener -= 1
    return opener >= 0 and lines[opener].strip().startswith("/**")


def doc_coverage(lang, text):
    lines = text.splitlines()
    total = 0
    documented = 0
    for index, line in enumerate(lines):
        if lang == "py":
            match = re.match(r"^\s*(?:async\s+)?def\s+[A-Za-z_]\w*", line)
        else:
            match = re.search(
                r"\bfunction\s+[A-Za-z_$][\w$]*\s*\(|"
                r"\b(?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=\s*(?:async\s*)?(?:function\b|\([^)]*\)\s*=>|[A-Za-z_$][\w$]*\s*=>)|"
                r"\bfunc\s+(?:\([^)]*\)\s*)?[A-Za-z_]\w*|"
                r"\bfn\s+[A-Za-z_]\w*",
                line,
            )
        if not match:
            continue
        total += 1
        if lang == "py":
            for cursor in range(index + 1, len(lines)):
                stripped = lines[cursor].strip()
                if not stripped:
                    continue
                if stripped.startswith(('"""', "'''")):
                    documented += 1
                break
        else:
            cursor = index - 1
            while cursor >= 0 and not lines[cursor].strip():
                cursor -= 1
            if cursor < 0:
                continue
            markers = DOC_MARKERS.get(lang, DOC_MARKERS["default"])
            if lines[cursor].strip().startswith(markers) or closes_doc_block(lines, cursor):
                documented += 1
    return documented, total


def analyze_language(lang, paths):
    result = {
        "language": lang,
        "files_total": len(paths),
        "files_read": 0,
        "files_skipped_large": 0,
        "files_skipped_minified": 0,
        "read_errors": 0,
        "code_lines": 0,
        "comment_lines": 0,
        "indent": {"tabs": 0, "spaces": 0, "style": "spaces"},
        "quotes": {},
        "naming": {},
        "identifier_lengths": {},
        "function_lengths": {"count": 0, "median": 0, "p90": 0},
        "boolean_prefix_share": {"count": 0, "prefixed": 0, "percent": 0},
        "todo_markers": 0,
        "doc_comment_coverage": {"functions": 0, "documented": 0, "percent": 0},
        "comment_voice": comment_voice([]),
        "error_message_voice": message_voice([]),
    }
    naming = defaultdict(Counter)
    lengths = defaultdict(list)
    quotes = Counter()
    fn_lengths = []
    boolean_names = []
    documented_functions = 0
    total_functions = 0
    comments = []
    messages = []

    for path in sample_paths(paths):
        try:
            if os.path.getsize(path) > MAX_FILE_BYTES:
                result["files_skipped_large"] += 1
                continue
            text = read_text(path)
        except OSError:
            result["read_errors"] += 1
            continue

        lines = text.splitlines()
        if lines and len(text) / len(lines) > MAX_BYTES_PER_LINE:
            result["files_skipped_minified"] += 1
            continue

        result["files_read"] += 1
        code, comment, tabs, spaces = count_lines(lang, text)
        result["code_lines"] += code
        result["comment_lines"] += comment
        result["indent"]["tabs"] += tabs
        result["indent"]["spaces"] += spaces
        quotes.update(count_quotes(lang, text))
        add_file_case(naming, path)
        add_identifier_cases(lang, text, naming, lengths, boolean_names)
        fn_lengths.extend(function_lengths(lang, text))
        documented, total = doc_coverage(lang, text)
        documented_functions += documented
        total_functions += total
        result["todo_markers"] += len(TODO_RE.findall(text))
        comments.extend(comment_texts(lang, text))
        messages.extend(error_messages(lang, text))

    result["files_capped"] = max(len(paths) - MAX_FILES_PER_LANG, 0)
    total_lines = result["code_lines"] + result["comment_lines"]
    result["comment_density"] = round(100 * result["comment_lines"] / total_lines, 1) if total_lines else 0
    result["indent"]["style"] = "tabs" if result["indent"]["tabs"] > result["indent"]["spaces"] else "spaces"
    result["quotes"] = dict(quotes)
    result["naming"] = {kind: dict(counter) for kind, counter in naming.items()}
    result["identifier_lengths"] = {kind: summarize(values) for kind, values in lengths.items()}
    result["function_lengths"] = summarize(fn_lengths)
    prefixed = sum(1 for name in boolean_names if BOOLEAN_PREFIX_RE.match(name))
    result["boolean_prefix_share"] = {
        "count": len(boolean_names),
        "prefixed": prefixed,
        "percent": round(100 * prefixed / len(boolean_names), 1) if boolean_names else 0,
    }
    result["doc_comment_coverage"] = {
        "functions": total_functions,
        "documented": documented_functions,
        "percent": round(100 * documented_functions / total_functions, 1) if total_functions else 0,
    }
    result["comment_voice"] = comment_voice(comments)
    result["error_message_voice"] = message_voice(messages)
    return result


def analyze(target):
    files = collect_files(target)
    return [
        analyze_language(lang, paths)
        for lang, paths in sorted(files.items(), key=lambda item: -len(item[1]))
    ]


def pct(counter, key):
    total = sum(counter.values())
    return round(100 * counter[key] / total) if total else 0


def print_text(results, target):
    if not results:
        print("No recognized source files under", target)
        return

    for result in results:
        lang = result["language"]
        total = result["files_total"]
        read = result["files_read"]
        if read == total:
            sample = "%d files" % total
        else:
            sample = "read %d of %d files" % (read, total)
        print("\n== %s (%s, %d code lines) ==" % (lang, sample, result["code_lines"]))
        if result["files_capped"]:
            print("  sampled  : capped at %d files, spread evenly by path" % MAX_FILES_PER_LANG)
        if result["files_skipped_large"]:
            print("  skipped  : %d oversized files" % result["files_skipped_large"])
        if result["files_skipped_minified"]:
            print("  skipped  : %d minified or generated files" % result["files_skipped_minified"])
        if result["read_errors"]:
            print("  unread   : %d files" % result["read_errors"])
        print("  comments : %s%% of non-blank lines" % result["comment_density"])
        print(
            "  indent   : %s (tabs %d / spaces %d indented lines)"
            % (
                result["indent"]["style"],
                result["indent"]["tabs"],
                result["indent"]["spaces"],
            )
        )

        quotes = Counter(result["quotes"])
        if sum(quotes.values()):
            parts = ["%s %d%%" % (name, pct(quotes, name)) for name in ["double", "single", "backtick"] if quotes.get(name)]
            print("  quotes   : " + " / ".join(parts))
        if result["function_lengths"]["count"]:
            print(
                "  fn size  : median %s lines / p90 %s (%d functions)"
                % (
                    result["function_lengths"]["median"],
                    result["function_lengths"]["p90"],
                    result["function_lengths"]["count"],
                )
            )
        if result["doc_comment_coverage"]["functions"]:
            print("  doc cov  : %s%% of functions" % result["doc_comment_coverage"]["percent"])
        if result["todo_markers"]:
            print("  markers  : TODO/FIXME %d" % result["todo_markers"])
        if result["comment_voice"]["lines"]:
            voice = result["comment_voice"]
            print(
                "  voice    : comments median %s words / %s%% sentence-like / %s%% first person"
                % (
                    voice["word_lengths"]["median"],
                    voice["sentence_like_percent"],
                    voice["first_person_percent"],
                )
            )
            print(
                "             %s%% second person / %s%% contractions"
                % (voice["second_person_percent"], voice["contractions_percent"])
            )
        if result["error_message_voice"]["messages"]:
            voice = result["error_message_voice"]
            print(
                "  errors   : %s%% capitalized / %s%% terminal punctuation (%d messages)"
                % (
                    voice["capitalized_percent"],
                    voice["terminal_punctuation_percent"],
                    voice["messages"],
                )
            )

        for kind, counts in result["naming"].items():
            counter = Counter(counts)
            total_names = sum(counter.values())
            if not total_names:
                continue
            top = ", ".join(
                "%s %d%%" % (name, round(100 * count / total_names))
                for name, count in counter.most_common(3)
            )
            print("  %-9s: %s" % (kind, top))
        for kind, length in result["identifier_lengths"].items():
            if length["count"]:
                print("  %-9s: median len %s / p90 %s" % (kind + " len", length["median"], length["p90"]))
        if result["boolean_prefix_share"]["count"]:
            print("  bool pref: %s%% of lowercase identifiers" % result["boolean_prefix_share"]["percent"])
        if any("lower" in counts for counts in result["naming"].values()):
            print("  note     : lower means single-word names compatible with snake_case or camelCase")
        if any("UPPER" in result["naming"].get(kind, {}) for kind in ("constant", "variable")):
            print("  note     : UPPER means a single-word all-caps constant, compatible with SCREAMING_SNAKE")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Print best-effort code and prose style statistics.")
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args(argv)

    results = analyze(args.target)
    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        print_text(results, args.target)


if __name__ == "__main__":
    main()
