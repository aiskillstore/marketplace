#!/usr/bin/env python3
"""bookforge refit — 실패 장만 자간 단일 축 격자 재조판 (pagination.md §5).

Usage: python3 refit.py <book_dir>

원리(실측 근거):
  - 총행수를 바꾸는 허용 레버는 자간/어간뿐이고 둘은 엔진상 등가 → 단일 축.
  - 행간·문단간격은 계단 스위치라 탐색 축에서 제외(책 단위 상수).
  - 당겨오기는 흡수예산(꼬리 행수 ≤ 0.022 × 장 본문 행수) 안에서만 시도.
    예산 밖이면 밀어내기(+자간)로 꼬리를 하한 위로 키운다.
  - 그리디 금지: 후보 전수 → 밴드 통과 해 중 |Δ| 최소(최소 개입) 선택.

산출: <book_dir>/refit-params.json (build.py/build_html.py가 재빌드 시 적용)
      장별 {"tracking_em": Δ}(typst) / {"letter_spacing_em": 절대값}(html)
해 없음 → 그 장은 파라미터 0으로 두고 "원고 국소 개입 필요"로 보고(L6 에스컬레이션).
"""
import json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pagemetrics import analyze  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent

# 자간 하드캡(pagination.md §5 — 폰트 사이드베어링 산출값, 테마 소비분 반영)
CAP_NEG = {"practical": -0.015, "academic": -0.015, "essay": -0.015, "business": -0.015,
           "insight": -0.015, "magazine": -0.015}   # Δ 기준(테마 기본 대비 추가분)
CAP_POS = 0.010
# HTML 테마가 이미 소비한 letter-spacing (inline이 대체하므로 절대값 = base + Δ)
HTML_BASE = {"insight": -0.02, "magazine": 0.0}
NEG_GRID = [-0.0025, -0.005, -0.0075, -0.010, -0.0125, -0.015]
POS_GRID = [0.0025, 0.005, 0.0075, 0.010]

TAIL_HARD = {"essay": 0.35, "magazine": 0.35}
TAIL_WARN = {"practical": 0.70, "insight": 0.70, "academic": 0.70,
             "business": 0.65, "essay": 0.55, "magazine": 0.50}
MID_MIN = {"essay": 0.88}


def build(book_dir):
    r = subprocess.run([sys.executable, str(SKILL / "scripts" / "build.py"), str(book_dir)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        return False
    return True


def chapter_spans(pdf_path, n_pages):
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
    doc = fitz.open(pdf_path)
    lvl1 = [(t.strip(), p) for (l, t, p) in doc.get_toc(simple=True) if l == 1]
    doc.close()
    starts = sorted({p for (_, p) in lvl1})
    spans = []
    for i, s in enumerate(starts):
        end = (starts[i + 1] - 1) if i + 1 < len(starts) else n_pages
        spans.append((s, end))
    return spans


def judge_chapter(pages_by_no, span, style, n_grid, ch_starts):
    """returns (ok, tail_reach, tail_lines, mid_min_reach)"""
    s, e = span
    tail_hard = TAIL_HARD.get(style, 0.45)
    tail_warn = TAIL_WARN.get(style, 0.70)
    mid_min = MID_MIN.get(style, 0.90)
    tail = pages_by_no.get(e)
    mids = [pages_by_no[p] for p in range(s + 1, e) if p in pages_by_no]
    ok = True
    if tail:
        if tail["lines"] < 6 or tail["reach"] < max(tail_hard, tail_warn):
            ok = False
    for p in mids:
        if p["imgarea"] >= 0.60:
            continue
        if p["reach"] < mid_min:
            ok = False
    return ok, (tail["reach"] if tail else None), (tail["lines"] if tail else 0), \
        (min((p["reach"] for p in mids), default=1.0))


def main():
    book_dir = Path(sys.argv[1]).resolve()
    book = json.loads((book_dir / "book.json").read_text(encoding="utf-8"))
    outline = json.loads((book_dir / "outline.json").read_text(encoding="utf-8"))
    style = book["style"]
    tokens = json.loads((SKILL / "styles" / style / "tokens.json").read_text(encoding="utf-8"))
    engine = tokens.get("engine", "typst")
    frame = tokens["body_frame_mm"]
    pdf = book_dir / "draft" / "book.pdf"
    rp = book_dir / "refit-params.json"
    params = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else {}

    def key_for(delta):
        if engine == "typst":
            return {"tracking_em": round(delta, 4)}
        return {"letter_spacing_em": round(HTML_BASE.get(style, 0.0) + delta, 4)}

    def measure():
        m = analyze(pdf, frame)
        by_no = {p["page"]: p for p in m["pages"]}
        spans = chapter_spans(pdf, len(m["pages"]))
        return m, by_no, spans

    if not pdf.exists() and not build(book_dir):
        sys.exit(1)
    m, by_no, spans = measure()
    ch_starts = [s for (s, _) in spans]
    chapters = [Path(c["file"]).stem for c in outline["chapters"]]
    if len(spans) != len(chapters):
        print(f"WARN: 북마크 장 수 {len(spans)} != outline {len(chapters)} — 대응 순서 가정")

    escalate = []
    for ci, ch in enumerate(chapters):
        if ci >= len(spans):
            break
        span = spans[ci]
        ok, treach, tlines, midmin = judge_chapter(by_no, span, style, m["n_grid"], ch_starts)
        if ok:
            continue
        ch_lines = sum(by_no[p]["lines"] for p in range(span[0], span[1] + 1) if p in by_no)
        budget_ok = tlines <= 0.022 * ch_lines * 1.5   # 당겨오기 물리 예산(여유 1.5배)
        grid = (NEG_GRID if budget_ok else []) + POS_GRID
        grid = [d for d in grid if CAP_NEG.get(style, -0.015) <= d <= CAP_POS]
        print(f"[{ch}] tail reach={treach} lines={tlines} mid_min={midmin} "
              f"budget={'pull-up 가능' if budget_ok else 'pull-up 불가(밀어내기만)'} — 후보 {len(grid)}개")
        solutions = []
        for delta in grid:
            params[ch] = key_for(delta)
            rp.write_text(json.dumps(params, ensure_ascii=False, indent=2), encoding="utf-8")
            if not build(book_dir):
                continue
            m2, by2, spans2 = measure()
            if ci >= len(spans2):
                continue
            ok2, tr2, tl2, mm2 = judge_chapter(by2, spans2[ci], style, m2["n_grid"], None)
            print(f"  Δ={delta:+.4f}em → tail reach={tr2} lines={tl2} mid_min={mm2} {'PASS' if ok2 else ''}")
            if ok2:
                solutions.append((abs(delta), delta))
        if solutions:
            best = min(solutions)[1]
            params[ch] = key_for(best)
            print(f"[{ch}] 채택 Δ={best:+.4f}em (최소 개입)")
        else:
            params.pop(ch, None)
            escalate.append(ch)
            print(f"[{ch}] 해 없음 — 원고 국소 개입 필요(문단 ±1~2개 또는 요소 이동/사유 코드)")
        rp.write_text(json.dumps(params, ensure_ascii=False, indent=2), encoding="utf-8")

    build(book_dir)  # 최종 파라미터로 재빌드
    if escalate:
        print("ESCALATE:", ", ".join(escalate))
        sys.exit(2)
    print("refit done")


if __name__ == "__main__":
    main()
