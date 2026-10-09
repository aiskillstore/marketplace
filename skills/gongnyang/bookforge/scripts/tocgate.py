"""G14 — 목차·디자인 정합 게이트 (qc_gate.py가 호출).

세 축:
다면 목차: A·B는 `find_toc_pages`가 회수한 **전 목차 면**을 순회한다. `first_ch`를 넘기면
탐색 범위가 앞부속(표지 다음 ~ 첫 장 직전)으로 한정되고 연속 면 확장 임계가 완화된다 —
"장제목 1개 재등장 = 도비라"라는 보수 규칙(len(new) < 2)이 다면 목차의 2면 이후를
배제하던 실지점이고, 도비라가 범위 밖이면 그 규칙이 필요 없다.

  G14-A 인쇄 목차 쪽번호 ↔ 실제 폴리오 자기일관성.
        폴리오 관습(book-anatomy C9): 본문 1쪽부터 — 기대값 = 장 시작 절대페이지 − 오프셋
        (오프셋 = 첫 장 시작 − 1). 목차 면에서 장제목 행과 y-겹침으로 페어링한
        최우측 숫자를 인쇄값으로 읽어 대조한다. 외부 진리 불필요한 내부 일관성 검사.
  G14-B 목차 유채색 ↔ 도비라(장 오프너) 유채색의 색상(hue) 정합 — 목차가 본문과
        다른 색 계열을 쓰는 "다른 책 같은 목차"를 차단. 명도/채도 셰이드 변주는 허용.
  G14-C 유채색 텍스트의 배경 대비 WCAG 하한 — 전 면 스캔. 렌더 픽스맵에서 스팬
        주변 배경색을 추정해 대비를 계산한다. 하한은 `g16_tokens.contrast_floor`가
        단일 진리원 — WCAG 1.4.3 대형(≥18pt 또는 ≥14pt 볼드) 3:1, 그 외 4.5:1.
        배경 추정이 불안정한 스팬(이미지·그라데이션 위)은 건너뛴다.
  G14-E 그림·표 차례(toc_lists 옵트인 별면)의 인쇄 쪽번호 ↔ 실제 캡션 면 — A 동형.
        앞부속에서 차례 행(라벨 `그림 n-m`/`표 n-m.` 시작)을 재추출해 본문 캡션 실면과
        대조한다. toc_lists 미선언(현행 기본)이면 축 전체가 자명 통과·비용 0이다.

반환: (problems: list[str], warns: list[str], info: dict)
"""
import colorsys
import re
import sys
import unicodedata
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
# 대비 하한은 g16_tokens가 단일 진리원 — 여기서 값을 복제하지 않는다.
# (사전 게이트 G16-CONTRAST와 렌더 후 G14-C가 다른 수를 내면 사전 FAIL이 무의미해진다.)
# 하한 함수의 **두 번째 인자를 만드는 술어**도 같은 모듈에서 온다(is_bold_font) —
# 이쪽이 자체 판정(`"Bold" in font`)을 갖고 있던 동안 `Pretendard-SemiBold`(600)가
# 부분문자열 `Bold` 때문에 대형 자격을 얻어 하한이 4.5 -> 3.0으로 열렸다(W4 판정 D6).
from g16_tokens import contrast_floor, is_bold_font  # noqa: E402


def _norm(s):
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"[\s​]+", "", s)


def _int_rgb(c):
    return ((c >> 16) & 255, (c >> 8) & 255, c & 255)


def _is_colored(rgb, min_chroma=28):
    return max(rgb) - min(rgb) > min_chroma


def _hue(rgb):
    h, _, _ = colorsys.rgb_to_hls(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
    return h * 360


def _hue_dist(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def _rel_lum(rgb):
    def f(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(rgb1, rgb2):
    l1, l2 = _rel_lum(rgb1), _rel_lum(rgb2)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def _spans(page):
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if s["text"].strip():
                    yield s


def _digit_spans(page):
    return sum(1 for s in _spans(page) if s["text"].strip().isdigit())


def find_toc_pages(doc, titles, search_upto=7, first_ch=None):
    """인쇄 목차 면(들). 장제목 과반이 실린 첫 면 + 히트가 이어지는 연속 면(다면 목차).

    first_ch(첫 장 시작 1-base 페이지)가 주어지면 탐색 범위를 앞부속으로 한정하고
    연속 면 확장 임계를 완화한다 — 도비라가 범위 밖이라 "장제목 1개 재등장 = 도비라"
    라는 보수 규칙(len(new) < 2)이 필요 없어지고, 그 규칙이 바로 다면 목차의 2면
    이후를 배제하던 실지점이다."""
    front_only = bool(first_ch) and first_ch > 2
    if front_only:
        # range(1, first_ch-1) = 0-base 1..first_ch-2 = 1-base 2..first_ch-1 (표지 제외 앞부속 전부)
        search_upto = first_ch - 1
    need = max(2, (len(titles) + 1) // 2)
    hits_by_page = {}
    for pno in range(1, min(search_upto, doc.page_count)):
        text = _norm(doc[pno].get_text())
        hits_by_page[pno] = sum(1 for t in titles if _norm(t)[:10] and _norm(t)[:10] in text)
    start = None
    if front_only:
        # 앞부속 범위에서는 **과반 규칙을 쓰지 않는다.** 다면 목차는 면당 장 수가
        # 24/(1+절수)로 떨어져 과반이 원리적으로 불가하다 — 14장×10절(목차 7면)은
        # 면당 장제목 2개인데 need=7이라 구 규칙이 []를 반환했고, G14-A가 "목차 면을
        # 찾지 못함"으로 오탐 FAIL하며 G14-B는 색 정합 축이 통째로 침묵했다(적대검토 D4:
        # 10장×10절·12장×8절·14장×6절·20장×4절이 모두 실패 영역).
        # 도비라가 범위 밖이므로 "장제목 1개 이상 또는 쪽번호 칼럼"으로 시작 면을 잡는다.
        for pno in sorted(hits_by_page):
            if hits_by_page[pno] >= 1 or _digit_spans(doc[pno]) >= 3:
                start = pno
                break
    else:
        for pno in sorted(hits_by_page):
            if hits_by_page[pno] >= need:
                start = pno
                break
        if start is None:  # 과반 면이 없어도, 연속 2면 합산이 과반이면 다면 목차로 인정
            for pno in sorted(hits_by_page)[:-1]:
                if hits_by_page[pno] >= 1 and hits_by_page[pno] + hits_by_page.get(pno + 1, 0) >= need:
                    start = pno
                    break
    if start is None:
        return []
    # 연속 면 확장은 "새 제목을 추가로 커버할 때만" — 도비라(장제목 1개 재등장)로
    # 목차가 본문까지 번지는 것을 막는다. 전 제목 커버 시 즉시 중단.
    def titles_on(pno):
        text = _norm(doc[pno].get_text())
        return {t for t in titles if _norm(t)[:10] and _norm(t)[:10] in text}
    out = [start]
    covered = titles_on(start)
    nxt = start + 1
    while nxt in hits_by_page:
        new = titles_on(nxt) - covered
        if front_only:
            # 앞부속(표지 다음 ~ 첫 장 직전) 안이므로 도비라가 범위 밖이다. 새 제목이
            # 0개여도 쪽번호 칼럼이 있으면 장 내 분할로 절만 실린 면이므로 계속 잇는다.
            # 전 제목 커버로 중단하지 않는다 — 마지막 면이 절만 실린 면일 수 있고, 그
            # 면을 빼면 절 쪽번호 축과 색 정합 축이 그 면을 통째로 놓친다.
            if not new and _digit_spans(doc[nxt]) < 3:
                break
        else:
            if len(covered) >= len(titles):
                break
            if len(new) < 2:  # 1개 재등장 = 도비라일 가능성 — 확장 중단
                break
        out.append(nxt)
        covered |= new
        nxt += 1
    return out


def _is_ordinal_decoration(text):
    """'01' '02' 같은 leading-zero 토큰은 장 서수 장식이지 쪽번호가 아니다."""
    t = text.strip()
    return len(t) >= 2 and t[0] == "0"


def _image_zones(page):
    """면의 이미지 배치 rect 목록 — 목차 이미지맵(썸네일) 캡션 스팬 제외의 좌표 기반.

    object-fit: cover 크롭은 클립으로 구현되므로 bbox가 보이는 상자보다 클 수 있다
    (w7-b3 실측: 64×28mm 상자에 배치 rect는 y로 36.5mm — 세로 크롭). x-축은 상자와
    일치하는 방향이 일반적이라 x-존 판정의 기준으로 삼는다."""
    return [tuple(i["bbox"]) for i in page.get_image_info()]


def _caption_zone(s, zones, pad_x=2, pad_top=2, pad_bot=20):
    """스팬 s가 이미지 소속 캡션 위치(이미지 x-존 안 · 이미지 세로 범위~직하)면
    그 존을, 아니면 None을 돌려준다.

    magazine $tocmap 썸네일의 캡션(.tocpg)은 장 폴리오 숫자인데 목차 행과 y-겹침이
    생긴다 — pair_score(수평거리 + 40×수직중심 이탈)에서 수직 정합인 캡션이 행의
    진짜 쪽번호(수직 2.2pt 이탈)를 이기는 오페어링이 실재했다(w7-b3: '대화의 업무화'
    행이 캡션 "1"과 페어링). pad_bot은 크롭 클립 밖·이미지 직하의 캡션 행까지 흡수한다
    (실측 최대 갭 9.7pt)."""
    cx = (s["bbox"][0] + s["bbox"][2]) / 2
    for z in zones:
        if (z[0] - pad_x <= cx <= z[2] + pad_x
                and s["bbox"][3] >= z[1] - pad_top and s["bbox"][1] <= z[3] + pad_bot):
            return z
    return None


def g14a_toc_numbers(doc, titles, ch_starts, toc_pages=None):
    problems, pairs = [], []
    if not ch_starts:
        return ["장 시작 페이지 불명(북마크 부재?)"], pairs
    offset = ch_starts[0] - 1
    if toc_pages is None:
        toc_pages = find_toc_pages(doc, titles, first_ch=ch_starts[0])
    if not toc_pages:
        return ["인쇄 목차 면을 찾지 못함(장제목 과반이 실린 면 없음)"], pairs
    spans_by_page = {p: list(_spans(doc[p])) for p in toc_pages}
    zones_by_page = {p: _image_zones(doc[p]) for p in toc_pages}
    for i, title in enumerate(titles):
        if i >= len(ch_starts):
            break
        expected = ch_starts[i] - offset
        key = _norm(title)[:10]
        t_span, t_page = None, None
        for p in toc_pages:
            hit = [s for s in spans_by_page[p] if key and key in _norm(s["text"])]
            if hit:
                t_span, t_page = hit[0], p
                break
        if t_span is None:
            all_joined = _norm("".join(s["text"] for p in toc_pages for s in spans_by_page[p]))
            if key not in all_joined:
                problems.append(f"목차 p{toc_pages[0] + 1}~: '{title[:16]}' 제목 미발견")
            else:
                # 이미지맵 캡션 숫자는 존재 검사에서도 뺀다 — 캡션이 우연히 기대값과
                # 같으면(자기 장 폴리오가 그 값이므로 흔하다) 틀린 인쇄값이 침묵 통과한다.
                nums = {s["text"].strip() for p in toc_pages for s in spans_by_page[p]
                        if s["text"].strip().isdigit()
                        and not _caption_zone(s, zones_by_page[p])}
                if str(expected) not in nums:
                    problems.append(f"목차 p{toc_pages[0] + 1}~: '{title[:16]}' 기대 쪽번호 {expected} 부재")
            continue
        y0, y1 = t_span["bbox"][1], t_span["bbox"][3]

        def in_image_col(s):
            # 이미지맵(썸네일 칼럼) 소속 캡션 숫자는 페어링 후보가 아니다. 단, 제목
            # 자신이 같은 존에 걸쳐 있으면(전폭 배경 아트 위 목차 등 — 존이 엔트리
            # 칼럼까지 덮는 형태) 제외하지 않는다: 그 형태에서 무조건 제외하면 진짜
            # 쪽번호까지 전멸해 "행에 쪽번호 없음" 오탐 FAIL이 된다.
            z = _caption_zone(s, zones_by_page[t_page])
            return (z is not None
                    and not (t_span["bbox"][2] > z[0] - 2 and t_span["bbox"][0] < z[2] + 2))
        # 같은 행(y 겹침)의 순수 숫자 스팬 — 좌우 무관, 서수 장식(leading zero) 제외,
        # 이미지맵 캡션 제외, 제목과 수평으로 가장 가까운 것이 쪽번호
        # (다단 목차의 이웃 칼럼 오탐 방지)
        cands = [s for s in spans_by_page[t_page]
                 if s["text"].strip().isdigit()
                 and not _is_ordinal_decoration(s["text"])
                 and not (s["bbox"][3] < y0 - 4 or s["bbox"][1] > y1 + 4)
                 and not in_image_col(s)]
        # 폴리오 위치 관습은 스타일에 따라 갈린다 — 제목 뒤(우측: practical 2단·
        # display-numeral 등) 또는 제목 앞(좌측: magazine 스프레드 17pt 폴리오).
        # 행에 우측 후보가 있으면 **제목 시작보다 완전히 왼쪽인 후보를 버린다** —
        # 그 자리는 장 서수 칩·대형 장번호 장식이 사는 자리다. 0-접두 필터는
        # '01'~'09'만 거르고 2자리 칩 '10'~'15'는 통과시켜, practical 2단 목차에서
        # 칩("10", hd 13.5)이 우단의 진짜 쪽번호("32", hd 47.8)를 pair_score로 이기는
        # 오탐 6건이 실재했다(w7-b5·cover-apply 실측). 우측 후보가 전무할 때만
        # 좌측을 쪽번호로 읽는다 — magazine 스프레드가 정확히 이 경로다.
        rights = [s for s in cands if s["bbox"][2] > t_span["bbox"][0]]
        if rights:
            cands = rights
        if not cands:
            problems.append(f"목차 p{t_page + 1}: '{title[:16]}' 행에 쪽번호 없음")
            continue

        t_cy = (y0 + y1) / 2

        def pair_score(s):
            # 수평 거리 + 수직 중심 이탈 페널티 — 인접 행(절 목록)의 숫자가
            # 미세한 x-지터로 이기는 것을 막는다
            if s["bbox"][2] <= t_span["bbox"][0]:
                hd = t_span["bbox"][0] - s["bbox"][2]
            elif s["bbox"][0] >= t_span["bbox"][2]:
                hd = s["bbox"][0] - t_span["bbox"][2]
            else:
                hd = 0.0
            cy = (s["bbox"][1] + s["bbox"][3]) / 2
            return hd + 40 * abs(cy - t_cy)
        printed = int(min(cands, key=pair_score)["text"].strip())
        pairs.append({"title": title, "printed": printed, "expected": expected})
        if printed != expected:
            problems.append(
                f"목차 p{t_page + 1}: '{title[:16]}' 인쇄 {printed} ≠ 폴리오 {expected} "
                f"(장 시작 abs p{ch_starts[i]}, 오프셋 {offset})")
    return problems, pairs


def _printed_toc_rows(doc, toc_pages):
    """인쇄 목차 면에서 **행**을 복원한다 → [{page, text, printed, x0}].

    행의 시작은 "그 라인의 최우측 스팬이 순수 숫자(쪽번호)"인 라인이고, 뒤따르는
    숫자 없는 라인은 접힌 제목의 연속행으로 앞 행에 이어붙인다. 빌더가 무엇을 발행했다고
    주장하든 상관없이 **PDF에 실제로 인쇄된 것**만 읽는다."""
    rows = []
    for p in toc_pages:
        lines = []
        for b in doc[p].get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                sp = [s for s in l["spans"] if s["text"].strip()]
                if sp:
                    lines.append(sp)
        lines.sort(key=lambda sp: min(s["bbox"][1] for s in sp))
        for sp in lines:
            right = max(s["bbox"][2] for s in sp)
            num_i = [i for i, s in enumerate(sp)
                     if s["text"].strip().isdigit()
                     and not _is_ordinal_decoration(s["text"])
                     and s["bbox"][2] >= right - 1]
            text = "".join(s["text"] for i, s in enumerate(sp) if i not in num_i)
            if num_i:
                rows.append({"page": p, "text": text,
                             "printed": int(sp[num_i[-1]]["text"].strip()),
                             "x0": min(s["bbox"][0] for s in sp)})
            elif rows and rows[-1]["page"] == p:
                rows[-1]["text"] += text
    return rows


def _page_lines(doc, pno, cache):
    if pno not in cache:
        out = []
        for b in doc[pno].get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                t = _norm("".join(s["text"] for s in l["spans"]))
                if t:
                    out.append(t)
        cache[pno] = out
    return cache[pno]


def _heading_pages(doc, key, lo, hi, cache):
    """[lo, hi) (1-base) 구간에서 `key`가 **제목 행으로** 실재하는 면(1-base) 목록.

    본문 문단 안의 우연한 언급을 배제하려고 '라인 1~3개의 연결이 제목과 정확히 일치'를
    요구한다(제목이 2행으로 접히는 경우까지 흡수)."""
    def matches(acc):
        # 테마가 h2::before로 "장.절 " 자동 번호를 붙인다(insight theme.css) — 인쇄 목차
        # 엔트리에는 그 번호가 없으므로 숫자·점만으로 된 접두는 허용한다.
        if not acc.endswith(key):
            return False
        return re.fullmatch(r"[\d.]*", acc[:len(acc) - len(key)]) is not None

    hit = []
    for p in range(max(1, lo), min(hi, doc.page_count + 1)):
        ls = _page_lines(doc, p - 1, cache)
        found = False
        for i in range(len(ls)):
            acc = ""
            for j in range(i, min(i + 3, len(ls))):
                acc += ls[j]
                if matches(acc):
                    found = True
                    break
                if len(acc) > len(key) + 8:
                    break
            if found:
                break
        if found:
            hit.append(p)
    return hit


def g14d_section_numbers(doc, toc_pages, titles, ch_starts):
    """G14-D 인쇄 목차의 **절 행 쪽번호 ↔ 실제 절 시작면**.

    왜 신설했나: 기존 축은 전부 빌더의 말을 믿었다 — G4 레벨 2는 `tocplan.json`의 기대값과
    빌더가 같은 리스트에서 만든 북마크 수를 대조하는 항등식이고(적대검토 D5), G14-A는 장
    제목만 순회한다. 그래서 절 마커 오배정(D3/V1: smoke-insight 10/15 오번호)이 전 게이트를
    통과해 출하됐다. 이 축은 **PDF에 인쇄된 절 행의 쪽번호**와 **본문에서 그 절 제목이
    처음 나오는 면**만 쓴다(빌더 산출물 불참조).

    앵커링: 절 제목은 장마다 중복될 수 있으므로 '해당 장 시작면 이후 첫 출현'으로 잡는다.
    한 장 안에서 같은 절 제목이 둘 이상이면 판정 불가이므로 WARN으로 빼고 FAIL하지 않는다.
    """
    problems, warns, pairs = [], [], []
    if not toc_pages or not ch_starts:
        return problems, warns, pairs
    offset = ch_starts[0] - 1
    rows = _printed_toc_rows(doc, toc_pages)
    keys = [_norm(t)[:10] for t in titles]
    ci = -1
    groups = []                      # [(chapter_index, [절 행 …])]
    for r in rows:
        nt = _norm(r["text"])
        if any(rx.match(nt) for rx in _LIST_ROW_RE.values()):
            # 그림·표 차례 행 — 차례 별면이 find_toc_pages의 앞부속 확장에 함께 회수되면
            # 마지막 장의 절 행으로 오인돼 "본문에서 못 찾음" WARN 소음이 된다.
            # 쪽번호 대조는 G14-E 소관이므로 D는 손대지 않는다.
            continue
        if ci + 1 < len(keys) and keys[ci + 1] and keys[ci + 1] in nt:
            ci += 1
            groups.append((ci, []))
            continue
        if ci >= 0 and groups:
            groups[-1][1].append(r)
    cache = {}
    for ci, secs in groups:
        if ci >= len(ch_starts):
            break
        lo = ch_starts[ci]
        hi = ch_starts[ci + 1] if ci + 1 < len(ch_starts) else doc.page_count + 1
        seen = {}
        for r in secs:
            seen[_norm(r["text"])] = seen.get(_norm(r["text"]), 0) + 1
        for r in secs:
            key = _norm(r["text"])
            if not key:
                continue
            if seen[key] > 1:
                warns.append(f"G14-D: '{r['text'][:16]}'가 장 {ci + 1} 목차에 {seen[key]}회 — "
                             "첫 출현 앵커링이 성립하지 않아 판정 제외")
                continue
            hit = _heading_pages(doc, key, lo, hi, cache)
            if not hit:
                warns.append(f"G14-D: 목차의 절 '{r['text'][:16]}'을 장 {ci + 1} 본문"
                             f"(p{lo}~{hi - 1})에서 제목 행으로 찾지 못함 — 판정 제외")
                continue
            expected = hit[0] - offset
            pairs.append({"section": r["text"], "printed": r["printed"], "expected": expected})
            if r["printed"] != expected:
                problems.append(
                    f"목차 p{r['page'] + 1}: 절 '{r['text'][:16]}' 인쇄 {r['printed']} ≠ "
                    f"실제 시작면 {expected} (본문 abs p{hit[0]}, 오프셋 {offset})")
    return problems, warns, pairs


# ---- G14-E 그림·표 차례(toc_lists) 쪽번호 ----
# 차례 행 식별자 — 라벨 발행 문법(build_html: `그림 n-m` / `표 n-m.`)의 정규화형.
# 본문 목차의 장·절 행은 이 어휘로 시작할 수 없다(제목이 정확히 `그림3-1…`로 시작하는
# 극단 케이스는 본문 대조에서 캡션 행 불일치 FAIL로 드러난다 — 침묵 통과 아님).
_LIST_ROW_RE = {"fg": re.compile(r"^그림\d+-\d+"), "tb": re.compile(r"^표\d+-\d+\.")}
_LIST_KIND_LABEL = {"fg": "그림 차례", "tb": "표 차례"}
_LIST_PLAN_KEY = {"fg": ("figures", "fig_markers"), "tb": ("tables", "tbl_markers")}


def _caption_pages(doc, key, lo, hi, cache):
    """[lo, hi) (1-base)에서 key가 **캡션 행 전체**로 실재하는 면 목록.

    _heading_pages와 달리 접두 허용이 없다 — 차례 행 텍스트(라벨+캡션)와 지면 캡션
    (figcaption/.tbl-caption 라인)은 같은 발행 경로의 같은 문자열이라 정규화 후 완전
    일치해야 한다. 본문 문장 안의 '그림 1-1에서 보듯' 류 언급은 행 전체가 일치하지
    않으므로 배제된다(접힌 캡션은 라인 4개까지 이어붙여 흡수)."""
    hit = []
    for p in range(max(1, lo), min(hi, doc.page_count + 1)):
        ls = _page_lines(doc, p - 1, cache)
        found = False
        for i in range(len(ls)):
            acc = ""
            for j in range(i, min(i + 4, len(ls))):
                acc += ls[j]
                if acc == key:
                    found = True
                    break
                if len(acc) >= len(key):
                    break
            if found:
                break
        if found:
            hit.append(p)
    return hit


def g14e_list_numbers(doc, ch_starts, declared_lists, plan):
    """G14-E 그림·표 차례 별면의 인쇄 쪽번호 ↔ 실제 캡션 면 (G14-A 동형).

    빌더의 스탬핑을 믿지 않는다 — 앞부속 면에서 차례 행을 재추출해 인쇄 쪽번호를 읽고,
    본문에서 같은 캡션 행이 처음 실재하는 면의 폴리오와 대조한다. 행 **수**는 tocplan의
    발행 대장(fig_markers/tbl_markers)과 대조한다(G4 ㉠과 같은 성격의 수 축 — 차례 행이
    조용히 누락된 면 손상을 잡는다. 값 축은 위의 PDF 전용 대조가 담당).

    스위치는 선언(tokens 또는 book 덮어쓰기)과 tocplan 기록의 **일치를 먼저 검사**한 뒤
    기록을 따른다 — 선언만 보면 스테일 산출물에서 축이 허수로 돌고, 기록만 보면 선언을
    지우고 옛 PDF를 재게이트하는 경로가 침묵한다. 양쪽 다 빈 책(현행 전 스타일 기본)은
    자명 통과·비용 0. 반환: (problems, warns, pairs, checked)"""
    problems, warns, pairs = [], [], []
    plan_lists = sorted((plan or {}).get("toc_lists") or [])
    decl = sorted(declared_lists or [])
    if decl != plan_lists:
        problems.append(
            f"toc_lists 선언 {decl} ≠ tocplan 기록 {plan_lists} — 빌더가 본 선언과 게이트가 "
            "보는 선언이 다르다(스테일 산출물 또는 선언 변경 후 미재빌드)")
        return problems, warns, pairs, 0
    if not plan_lists or not ch_starts:
        return problems, warns, pairs, 0
    first_ch = ch_starts[0]
    offset = first_ch - 1
    rows = {"fg": [], "tb": []}
    for p in range(1, first_ch - 1):          # 0-base 앞부속(표지 다음 ~ 첫 장 직전)
        for r in _printed_toc_rows(doc, [p]):
            t = _norm(r["text"])
            for kind, rx in _LIST_ROW_RE.items():
                if rx.match(t):
                    rows[kind].append(r)
                    break
    cache = {}
    for kind in ("fg", "tb"):
        token, plan_key = _LIST_PLAN_KEY[kind]
        if token not in plan_lists:
            continue
        got = rows[kind]
        want = plan.get(plan_key)
        if isinstance(want, int) and len(got) != want:
            problems.append(
                f"{_LIST_KIND_LABEL[kind]} 행 {len(got)}개 ≠ 발행 마커 {want}개 — "
                "차례 면 누락·행 손상 의심")
        seen = {}
        for r in got:
            seen[_norm(r["text"])] = seen.get(_norm(r["text"]), 0) + 1
        for r in got:
            key = _norm(r["text"])
            if not key:
                continue
            if seen[key] > 1:
                warns.append(f"G14-E: '{r['text'][:16]}'가 {_LIST_KIND_LABEL[kind]}에 "
                             f"{seen[key]}회 — 첫 출현 앵커링 불성립, 판정 제외")
                continue
            hit = _caption_pages(doc, key, first_ch, doc.page_count + 1, cache)
            if not hit:
                problems.append(f"{_LIST_KIND_LABEL[kind]}의 '{r['text'][:20]}'를 본문에서 "
                                f"캡션 행으로 찾지 못함(p{first_ch}~)")
                continue
            expected = hit[0] - offset
            pairs.append({"entry": r["text"], "printed": r["printed"], "expected": expected})
            if r["printed"] != expected:
                problems.append(
                    f"{_LIST_KIND_LABEL[kind]} p{r['page'] + 1}: '{r['text'][:16]}' 인쇄 "
                    f"{r['printed']} ≠ 실제 캡션 면 {expected} "
                    f"(본문 abs p{hit[0]}, 오프셋 {offset})")
    return problems, warns, pairs, len(pairs)


def _accent_colors_text(page):
    return {(_int_rgb(s["color"])) for s in _spans(page) if _is_colored(_int_rgb(s["color"]))}


def _accent_colors_drawings(page):
    out = set()
    for d in page.get_drawings():
        for c in (d.get("fill"), d.get("color")):
            if c:
                rgb = tuple(int(round(v * 255)) for v in c)
                if _is_colored(rgb):
                    out.add(rgb)
    return out


def g14b_key_color(doc, titles, ch_starts, brand_hex=None, tol=36, toc_pages=None):
    problems = []
    if not ch_starts:
        return problems  # A가 이미 잡는다
    if toc_pages is None:
        toc_pages = find_toc_pages(doc, titles, first_ch=ch_starts[0])
    if not toc_pages:
        # 구 구현은 여기서 빈 리스트를 돌려주며 **조용히 합격**했다 — find_toc_pages가
        # 실패하는 순간 색 정합 축이 통째로 사라진다(적대검토 D4). "A가 잡는다"는 가정은
        # 주석이 아니라 run()의 검사로 보장한다(아래 assert 성격의 축 참조).
        return ["목차 면을 찾지 못해 색 정합 축을 검사하지 못했다"]
    # 다면 목차 전 면 순회 — 한 면만 보면 2면 이후의 색 이탈을 놓친다
    toc_colors = {}
    for p in toc_pages:
        for rgb in _accent_colors_text(doc[p]):
            toc_colors.setdefault(rgb, p)
    if not toc_colors:
        return problems  # 무채색 목차 — 검사 대상 없음
    opener_hues = set()
    for p in ch_starts[:3]:  # 대표 오프너 3면
        pg = doc[p - 1]
        for rgb in _accent_colors_text(pg) | _accent_colors_drawings(pg):
            opener_hues.add(_hue(rgb))
    if brand_hex:
        try:
            b = brand_hex.lstrip("#")
            opener_hues.add(_hue(tuple(int(b[i:i + 2], 16) for i in (0, 2, 4))))
        except ValueError:
            pass
    if not opener_hues:
        return problems
    for rgb, pno in sorted(toc_colors.items(), key=lambda kv: (kv[1], kv[0])):
        h = _hue(rgb)
        if min(_hue_dist(h, oh) for oh in opener_hues) > tol:
            problems.append(
                f"목차 p{pno + 1}: 유채색 #{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
                f"(hue {h:.0f}°)가 도비라·브랜드 색상 계열과 무관 (Δ>{tol}°)")
    return problems


def g14c_contrast(doc, zoom=2.0):
    """전 면 유채색 텍스트 스팬의 배경 대비. (면, 색, 대비, 하한) 위반 목록.

    반환: (problems, info) — info = {"skipped_unstable": 배경 추정 불가 스킵 수,
    "skipped_dedup": 동일 (스타일, 양자화 배경) 재검 생략 수}. 중복제거 키에는
    양자화한 배경색이 포함된다 — 같은 스타일 스팬이라도 표 얼룩무늬 행·콜아웃
    박스처럼 배경이 다르면 별건으로 재검사한다(배경 무시 dedup의 침묵 누락 방지).
    """
    problems = []
    skipped_unstable, skipped_dedup = 0, 0
    for pno in range(1, doc.page_count):  # 표지 제외(아트 배경)
        page = doc[pno]
        # 검사 대상 = 근흑(近黑) 잉크가 아닌 모든 텍스트 — 유채색 + 회색(뮤트 캡션류).
        # 근흑(#000~#333대)은 어떤 지면 배경에서도 대비가 성립하므로 제외해 비용 절감.
        colored = [s for s in _spans(page) if max(_int_rgb(s["color"])) > 96]
        if not colored:
            continue
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        w, h, nc = pix.width, pix.height, pix.n
        buf = pix.samples
        seen = set()
        for s in colored:
            rgb = _int_rgb(s["color"])
            size = s["size"]
            bold = is_bold_font(s.get("font", ""))   # 단일 진리원: g16_tokens.is_bold_font
            floor = contrast_floor(size, bold)       # 단일 진리원: g16_tokens.contrast_floor
            x0, y0, x1, y1 = (int(v * zoom) for v in s["bbox"])
            # 배경 추정: bbox 바깥 2~5px 링의 최빈색
            # (dedup 키에 배경이 들어가므로 링 스캔은 dedup보다 먼저 수행해야 한다)
            ring = {}
            for (rx0, ry0, rx1, ry1) in (
                    (x0 - 5, y0 - 5, x1 + 5, y0 - 2), (x0 - 5, y1 + 2, x1 + 5, y1 + 5),
                    (x0 - 5, y0, x0 - 2, y1), (x1 + 2, y0, x1 + 5, y1)):
                for yy in range(max(0, ry0), min(h, ry1)):
                    row = yy * w * nc
                    for xx in range(max(0, rx0), min(w, rx1)):
                        o = row + xx * nc
                        px = (buf[o], buf[o + 1], buf[o + 2])
                        ring[px] = ring.get(px, 0) + 1
            if not ring:
                skipped_unstable += 1
                continue
            total = sum(ring.values())
            bg, cnt = max(ring.items(), key=lambda kv: kv[1])
            if cnt / total < 0.55:  # 배경 불균일(이미지·그라데이션) — 판정 불가
                skipped_unstable += 1
                continue
            # 중복제거 키 = 스타일 + 양자화 배경(16단계 버킷) — 같은 (색,크기,하한)
            # 스팬이라도 배경 계열이 다르면 재검사. 버킷 내 잔차는 대비에 유의미한
            # 차이를 만들지 않는다.
            key = (rgb, round(size, 1), floor, tuple(c // 16 for c in bg))
            if key in seen:
                skipped_dedup += 1
                continue
            seen.add(key)
            c = contrast(rgb, bg)
            if c < floor:
                problems.append(
                    f"p{pno + 1}: #{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x} {size:.1f}pt "
                    f"'{s['text'].strip()[:14]}' 대비 {c:.2f} < {floor} "
                    f"(배경 #{bg[0]:02x}{bg[1]:02x}{bg[2]:02x})")
    return problems, {"skipped_unstable": skipped_unstable, "skipped_dedup": skipped_dedup}


def run(doc, outline, ch_starts, book, tokens, toc_levels=None, tocplan=None):
    titles = [ch["title"].strip() for ch in outline["chapters"]]
    # 목차 면은 한 번만 회수해 전 축이 같은 집합을 본다(축마다 재탐색하면 축별로 다른
    # 면을 보는 사고가 조용히 생긴다).
    toc_pages = find_toc_pages(doc, titles, first_ch=ch_starts[0]) if ch_starts else []
    a_problems, pairs = g14a_toc_numbers(doc, titles, ch_starts, toc_pages=toc_pages)
    brand = book.get("brand") or tokens.get("brand_default")
    b_problems = g14b_key_color(doc, titles, ch_starts, brand, toc_pages=toc_pages)
    c_problems, c_info = g14c_contrast(doc)
    warns = []
    d_problems, d_pairs = [], []
    if toc_levels is None:
        toc_levels = tokens.get("toc_levels", 2)
    if toc_levels >= 2:
        d_problems, d_warns, d_pairs = g14d_section_numbers(doc, toc_pages, titles, ch_starts)
        warns += d_warns
    # "목차 면 미발견은 A가 잡는다"는 가정을 검사로 고정한다 — 가정이 깨지면 B·D가
    # 조용히 통과하는 상태가 되므로, 그 조합 자체를 A의 실패로 만든다.
    if ch_starts and not toc_pages and not a_problems:
        a_problems = ["인쇄 목차 면을 찾지 못했는데 G14-A가 아무 문제도 내지 않았다"
                      " — B·D 축이 침묵으로 통과하는 상태(게이트 결함)"]
    # E — 그림·표 차례. 선언(tokens 또는 book 덮어쓰기 — 빌더와 같은 해석 순서)이나
    # tocplan 기록 어느 쪽이든 켜져 있으면 돈다(불일치는 축 안에서 FAIL).
    # 선언 오형(비리스트·비문자 원소)의 die는 빌더 소관 — 게이트는 형만 방어해
    # 쓰레기 선언이 정렬·비교에서 TypeError로 게이트를 죽이지 않게 한다.
    declared_raw = book.get("toc_lists", tokens.get("toc_lists"))
    declared_lists = ([v for v in declared_raw if isinstance(v, str)]
                      if isinstance(declared_raw, list) else [])
    e_problems, e_warns, e_pairs, e_checked = [], [], [], 0
    if declared_lists or (tocplan or {}).get("toc_lists"):
        e_problems, e_warns, e_pairs, e_checked = g14e_list_numbers(
            doc, ch_starts, declared_lists, tocplan)
    return {
        "A": {"problems": a_problems, "pairs": pairs, "ok": not a_problems,
              "toc_pages": [p + 1 for p in toc_pages]},
        "B": {"problems": b_problems, "ok": not b_problems},
        "C": {"problems": c_problems, "skipped": c_info["skipped_unstable"],
              "dedup_skipped": c_info["skipped_dedup"], "ok": not c_problems},
        "D": {"problems": d_problems, "pairs": d_pairs, "warns": warns,
              "checked": len(d_pairs), "ok": not d_problems},
        "E": {"problems": e_problems, "pairs": e_pairs, "warns": e_warns,
              "checked": e_checked, "ok": not e_problems},
    }
