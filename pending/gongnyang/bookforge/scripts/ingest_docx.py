#!/usr/bin/env python3
"""bookforge: docx -> markdown ingest (manuscript mode).

Usage: python3 ingest_docx.py <input.docx> <out_dir>
Maps Heading 1 -> chapter split (ch-NN.md with # title), Heading 2/3 -> ##/###,
bold/italic runs -> **/*, lists -> -/1., tables -> GFM tables.
Writes <out_dir>/chapters/ch-NN.md + <out_dir>/outline.json (titles, no summaries).
Requires python-docx (pip install python-docx).
"""
import json, re, sys
from pathlib import Path

try:
    import docx  # python-docx
except ImportError:
    sys.exit("python-docx가 필요합니다: pip install python-docx")

def run_md(run):
    t = run.text
    if not t:
        return ""
    if run.bold and run.italic:
        return f"***{t}***"
    if run.bold:
        return f"**{t}**"
    if run.italic:
        return f"*{t}*"
    return t

def para_md(p):
    return "".join(run_md(r) for r in p.runs).strip()

def table_md(tb):
    rows = [[c.text.strip().replace("\n", " ") for c in row.cells] for row in tb.rows]
    if not rows:
        return ""
    out = ["| " + " | ".join(rows[0]) + " |",
           "|" + "---|" * len(rows[0])]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)

def main():
    src, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    d = docx.Document(src)
    (out_dir / "chapters").mkdir(parents=True, exist_ok=True)

    chapters, cur, cur_title = [], [], None
    def flush():
        nonlocal cur, cur_title
        if cur_title or cur:
            chapters.append((cur_title or f"{len(chapters)+1}장", cur))
        cur, cur_title = [], None

    from docx.table import Table
    from docx.text.paragraph import Paragraph
    body = d.element.body
    for child in body.iterchildren():
        if child.tag.endswith("}p"):
            p = Paragraph(child, d)
            style = (p.style.name or "").lower()
            text = para_md(p)
            if not text:
                continue
            if re.match(r"heading 1|제목 1", style):
                flush()
                cur_title = p.text.strip()
            elif re.match(r"heading 2|제목 2", style):
                cur.append(f"## {p.text.strip()}")
            elif re.match(r"heading 3|제목 3", style):
                cur.append(f"### {p.text.strip()}")
            elif "list" in style or "목록" in style:
                cur.append(f"- {text}")
            elif "quote" in style or "인용" in style:
                cur.append(f"> {text}")
            else:
                cur.append(text)
        elif child.tag.endswith("}tbl"):
            cur.append(table_md(Table(child, d)))
    flush()

    outline = {"chapters": []}
    for i, (title, blocks) in enumerate(chapters, 1):
        fn = f"ch-{i:02d}.md"
        (out_dir / "chapters" / fn).write_text(
            f"# {title}\n\n" + "\n\n".join(blocks) + "\n", encoding="utf-8")
        outline["chapters"].append({"file": fn, "title": title,
                                    "summary": None})
    (out_dir / "outline.json").write_text(
        json.dumps(outline, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {len(chapters)} chapters -> {out_dir}")

if __name__ == "__main__":
    main()
