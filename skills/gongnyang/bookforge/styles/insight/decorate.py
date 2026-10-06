"""insight 러닝 장식 스탬핑 — build_html.py가 pass2 후 호출.

decorate(doc, ctx) 계약:
  doc: fitz.Document (draft/book.pdf, in place 수정)
  ctx: {"book": dict, "pages": {"chNN[sMM]": abs_page}, "fonts_dir": Path}
       — pages는 ch 종 마커만 담는다(빌더가 fg/tb를 종별 딕트로 분리해 넘기지 않는다).
         아래 min(pages) 폴리오 오프셋이 그림·표 면에 오염되지 않기 위한 계약.

STYLE.md 러닝 시스템: 시안 바(y 25.5mm, 좌 8mm·우 11mm) · 우측 세로 러닝헤드 ·
폴리오(Barlow Light 11.44pt, 우측 끝 = 재단폭 −12mm, baseline = 재단높이 −14mm).
생략 규칙: 표지(1)·목차(2)만 전부 생략 — 이후 전 면(도비라·판권면 포함)은
동일 러닝 시스템을 유지한다 (v2 예시 6권 판정 통과 실물 기준).
좌표는 page.rect에서 파생 — 판형이 바뀌어도 어긋나지 않는다.
"""
try:  # PyMuPDF 1.24+ 신 모듈명, 구버전은 fitz만 제공
    import pymupdf as fitz
except ImportError:
    import fitz

MM = 72 / 25.4
CYAN = (0x5E / 255, 0xC6 / 255, 0xDC / 255)
MUTE = (0x5A / 255, 0x61 / 255, 0x67 / 255)  # = theme.css --ink-mute. 백색 지면 위 대비 6.29


def decorate(doc, ctx):
    numfont = str(ctx["fonts_dir"] / "Barlow-Light.ttf")
    hanfont = str(ctx["fonts_dir"] / "Pretendard-Light.ttf")
    numfont_f = fitz.Font(fontfile=numfont)
    title = ctx["book"].get("title", "")
    # 폴리오는 본문 1쪽부터(book-anatomy C9) — 목차 스탬핑(build_html)과 같은 오프셋
    offset = min(ctx["pages"].values()) - 1 if ctx["pages"] else 0

    for pno in range(doc.page_count):
        page = doc[pno]
        n = pno + 1
        if n <= offset:      # 앞부속(표지·목차): 전부 생략
            continue
        pw, ph = page.rect.x1, page.rect.y1
        y = 25.5 * MM
        page.draw_rect(fitz.Rect(0, y, 8 * MM, y + 1 * MM), color=None, fill=CYAN)
        page.draw_rect(fitz.Rect(pw - 11 * MM, y, pw, y + 1 * MM),
                       color=None, fill=CYAN)
        page.insert_text(
            fitz.Point(pw - 5 * MM, 43 * MM), title,
            fontsize=7, fontfile=hanfont, fontname="F-han", rotate=270, color=MUTE)
        # 폴리오는 도비라에도 유지 — 앞부속만 생략(위에서 continue). 본문 1쪽부터.
        folio = n - offset
        w = numfont_f.text_length(str(folio), fontsize=11.44)
        page.insert_text(
            fitz.Point(pw - 12 * MM - w, ph - 14 * MM), str(folio),
            fontsize=11.44, fontfile=numfont, fontname="F-num", color=MUTE)
