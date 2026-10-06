#!/usr/bin/env python3
"""커밋된 예제 PDF에서 뮤테이션용 book_dir를 재구성한다 — 빌드 0회.

뮤테이션 스위트가 필요로 하는 것은 `draft/book.pdf` + `outline.json`(장 제목) +
`book.json`(style)뿐이고, 장 제목은 PDF 레벨1 북마크에 그대로 남아 있다. 따라서
examples/*.pdf만으로 스위트를 저장소 안에서 돌릴 수 있다.

한계: chapters/*.md가 없으므로 이 픽스처로는 **재빌드가 불가능**하다. 빌드 경로까지
검증하려면 tests/fixtures/<style>-min/(원고 포함)이 따로 필요하다.

Usage:
  python3 tests/mutations/fixture_from_example.py examples/insight-agent-protocols.pdf <out_dir>
"""
import json
import shutil
import sys
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz


def build(pdf: Path, out: Path) -> Path:
    style = pdf.stem.split("-", 1)[0]
    doc = fitz.open(pdf)
    lvl1 = [(t.strip(), p) for (l, t, p) in doc.get_toc(simple=True) if l == 1]
    doc.close()
    if not lvl1:
        sys.exit(f"{pdf.name}: 레벨1 북마크 0건 — 픽스처를 만들 수 없다")

    (out / "draft").mkdir(parents=True, exist_ok=True)
    shutil.copy(pdf, out / "draft" / "book.pdf")
    (out / "book.json").write_text(json.dumps(
        {"title": pdf.stem, "style": style, "length": "short",
         "_note": "examples PDF에서 재구성된 뮤테이션 전용 픽스처 — 재빌드 불가"},
        ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "outline.json").write_text(json.dumps(
        {"chapters": [{"file": f"ch-{i:02d}.md", "title": t, "summary": ""}
                      for i, (t, _) in enumerate(lvl1, 1)]},
        ensure_ascii=False, indent=2), encoding="utf-8")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    d = build(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
    print(f"픽스처: {d}")
