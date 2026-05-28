import argparse
import difflib
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from docx2python import docx2python

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
MAX_ITEMS = 20


def normalize_author(author):
    author = (author or "").strip()
    return author if author else "unknown"


def safe_text(text):
    text = (text or "").strip()
    return text if text else "(empty text/format changes)"


def extract_comments(path):
    comments = []
    with zipfile.ZipFile(path) as z:
        if "word/comments.xml" not in z.namelist():
            return comments
        root = ET.fromstring(z.read("word/comments.xml"))
        for c in root.findall("w:comment", NS):
            author = normalize_author(c.attrib.get(f"{{{NS['w']}}}author", ""))
            date_str = c.attrib.get(f"{{{NS['w']}}}date", "")
            texts = [t.text for t in c.findall(".//w:t", NS) if t.text]
            text = "".join(texts).strip()
            comments.append({"author": author, "date": date_str, "text": text})
    return comments


def extract_tracked_changes(path):
    insertions = []
    deletions = []
    with zipfile.ZipFile(path) as z:
        if "word/document.xml" not in z.namelist():
            return insertions, deletions
        root = ET.fromstring(z.read("word/document.xml"))
        for node in root.findall(".//w:ins", NS):
            author = normalize_author(node.attrib.get(f"{{{NS['w']}}}author", ""))
            date_str = node.attrib.get(f"{{{NS['w']}}}date", "")
            texts = [t.text for t in node.findall(".//w:t", NS) if t.text]
            insertions.append(
                {"author": author, "date": date_str, "text": "".join(texts)}
            )
        for node in root.findall(".//w:del", NS):
            author = normalize_author(node.attrib.get(f"{{{NS['w']}}}author", ""))
            date_str = node.attrib.get(f"{{{NS['w']}}}date", "")
            texts = [t.text for t in node.findall(".//w:delText", NS) if t.text]
            if not texts:
                texts = [t.text for t in node.findall(".//w:t", NS) if t.text]
            deletions.append(
                {"author": author, "date": date_str, "text": "".join(texts)}
            )
    return insertions, deletions


def extract_text_lines(path):
    with docx2python(path) as doc:
        text = doc.text
    lines = [ln.strip() for ln in text.splitlines()]
    return [ln for ln in lines if ln]


def normalize_lines(lines):
    normalized = []
    for line in lines:
        line = re.sub(r"<a[^>]*>", "", line)
        line = line.replace("</a>", "")
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            normalized.append(line)
    return normalized


def diff_lines(prev_lines, curr_lines):
    prev_norm = normalize_lines(prev_lines)
    curr_norm = normalize_lines(curr_lines)
    diff = difflib.ndiff(prev_norm, curr_norm)
    adds = [d[2:] for d in diff if d.startswith("+ ")]
    dels = [d[2:] for d in diff if d.startswith("- ")]
    return adds, dels


def version_sort_key(path):
    stem = path.stem
    mtime = path.stat().st_mtime
    match = re.search(r"[-_]?v(\d+)$", stem, re.IGNORECASE)
    if match:
        return (1, int(match.group(1)), mtime, stem)
    match = re.search(r"[-_](\d+)$", stem)
    if match:
        return (1, int(match.group(1)), mtime, stem)
    return (0, mtime, stem)


def round_label(path, unmarked_index):
    match = re.search(r"[-_]?v(\d+)$", path.stem, re.IGNORECASE)
    if match:
        return f"v{match.group(1)}"
    match = re.search(r"[-_](\d+)$", path.stem)
    if match:
        return f"v{match.group(1)}"
    return "v0" if unmarked_index == 1 else f"v0-{unmarked_index}"


def strip_version(stem):
    return re.sub(r"[-_]?v\d+$", "", stem, flags=re.IGNORECASE)


def strip_numeric_suffix(stem):
    return re.sub(r"[-_]\d+$", "", stem)


def base_title(path, sibling_stems=None):
    stem = path.stem
    match = re.search(r"[-_]?v(\d+)$", stem, re.IGNORECASE)
    if match:
        return strip_version(stem)
    match = re.search(r"[-_](\d+)$", stem)
    if match:
        candidate = strip_numeric_suffix(stem)
        if sibling_stems and candidate in sibling_stems:
            return candidate
    return stem


def has_version_suffix(stem):
    return bool(
        re.search(r"[-_]?v(\d+)$", stem, re.IGNORECASE)
        or re.search(r"[-_](\d+)$", stem)
    )


def add_list(lines, title, items):
    lines.append(f"{title}：")
    if not items:
        lines.append("- none")
        return
    for item in items[:MAX_ITEMS]:
        lines.append(f"- {item}")
    extra = len(items) - MAX_ITEMS
    if extra > 0:
        lines.append(f"- ... Also {extra} strip")


def build_change_log(paths, doc_title):
    paths = sorted(paths, key=version_sort_key)
    unmarked_index = 0
    labels = []
    for p in paths:
        if has_version_suffix(p.stem):
            labels.append(round_label(p, 0))
        else:
            unmarked_index += 1
            labels.append(round_label(p, unmarked_index))

    rounds = []
    for path in paths:
        comments = extract_comments(path)
        insertions, deletions = extract_tracked_changes(path)
        lines = extract_text_lines(path)
        rounds.append(
            {
                "path": path,
                "comments": comments,
                "insertions": insertions,
                "deletions": deletions,
                "lines": lines,
            }
        )

    output = []
    output.append("# Modification instructions")
    output.append("")
    output.append(f"document：{doc_title}")
    output.append(f"Version：{', '.join(labels)}")
    output.append("Organized by:OpenCode")
    output.append(f"date：{date.today().isoformat()}")
    output.append("")

    for idx, info in enumerate(rounds, start=1):
        prev_info = rounds[idx - 2] if idx > 1 else None
        output.append("")
        output.append(f"## No. {idx} wheel - {labels[idx - 1]}")
        output.append("")

        comments = info["comments"]
        insertions = info["insertions"]
        deletions = info["deletions"]

        output.append("Overall summary:")
        summary_lines = []
        summary_lines.append(
            f"- annotation {len(comments)} strip，English {len(insertions)} strip，revision delete {len(deletions)} strip。"
        )

        diff_adds = []
        diff_dels = []
        if not insertions and not deletions and prev_info is not None:
            diff_adds, diff_dels = diff_lines(prev_info["lines"], info["lines"])
            summary_lines.append(
                f"- Version difference added {len(diff_adds)} OK，English {len(diff_dels)} OK（Unable to attribute author）。"
            )

        output.extend(summary_lines)
        output.append("")

        output.append("Author changes:")
        author_set = set()
        for c in comments:
            author_set.add(normalize_author(c.get("author")))
        for c in insertions:
            author_set.add(normalize_author(c.get("author")))
        for c in deletions:
            author_set.add(normalize_author(c.get("author")))

        if not author_set:
            output.append("- No author information detected.")
        else:
            ins_counter = Counter(
                [normalize_author(c.get("author")) for c in insertions]
            )
            del_counter = Counter(
                [normalize_author(c.get("author")) for c in deletions]
            )
            com_counter = Counter([normalize_author(c.get("author")) for c in comments])
            for author in sorted(author_set):
                output.append(
                    f"- {author}：English {ins_counter.get(author, 0)}，revision delete {del_counter.get(author, 0)}，annotation {com_counter.get(author, 0)}。"
                )

        output.append("")

        if insertions:
            add_items = [safe_text(c.get("text")) for c in insertions]
            add_list(output, "New content", add_items)
        elif diff_adds:
            add_list(output, "New content", diff_adds)
        else:
            add_list(output, "New content", [])

        output.append("")

        if deletions:
            del_items = [safe_text(c.get("text")) for c in deletions]
            add_list(output, "Remove content", del_items)
        elif diff_dels:
            add_list(output, "Remove content", diff_dels)
        else:
            add_list(output, "Remove content", [])

        output.append("")
        output.append("Annotation and processing:")
        if not comments:
            output.append("- none")
        else:
            for c in comments[:MAX_ITEMS]:
                text = safe_text(c.get("text"))
                author = normalize_author(c.get("author"))
                output.append(f"- [{author}] {text}")
            extra = len(comments) - MAX_ITEMS
            if extra > 0:
                output.append(f"- ... Also {extra} strip")

        output.append("")
        output.append("Pending matters:")
        if not comments:
            output.append("- none")
        else:
            for c in comments[:MAX_ITEMS]:
                output.append(f"- {safe_text(c.get('text'))}")
            extra = len(comments) - MAX_ITEMS
            if extra > 0:
                output.append(f"- ... Also {extra} strip")

    return "\n".join(output) + "\n"


def collect_paths(args):
    if args.dir:
        base = Path(args.dir)
        if not base.exists():
            raise FileNotFoundError(f"Directory not found: {base}")
        return [p for p in base.glob(args.pattern) if p.suffix.lower() == ".docx"]
    return [Path(p) for p in args.files]


def main():
    parser = argparse.ArgumentParser(description="DOCX feedback tracker")
    parser.add_argument("files", nargs="*", help="DOCX files")
    parser.add_argument("--dir", help="Directory containing DOCX files")
    parser.add_argument("--pattern", default="*.docx", help="Glob pattern")
    args = parser.parse_args()

    paths = collect_paths(args)
    if not paths:
        raise SystemExit("No DOCX files found.")

    stems_by_parent = defaultdict(set)
    for path in paths:
        stems_by_parent[path.parent].add(path.stem)

    groups = defaultdict(list)
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        key = (path.parent, base_title(path, stems_by_parent[path.parent]))
        groups[key].append(path)

    for (parent, title), group in groups.items():
        text = build_change_log(group, title)
        out_path = parent / f"{title}-change-log.md"
        out_path.write_text(text, encoding="utf-8")
        print(out_path)


if __name__ == "__main__":
    main()
