#!/usr/bin/env python3
"""G14 뮤테이션 스위트 — 게이트의 감도(놓치지 않는가)를 회귀 자산으로 고정한다.

PASS 상태의 책 PDF에 고의 결함을 주입한 사본을 만들고, tocgate가 각 결함을
실제로 검출하는지 어서션한다. 전부 검출되어야 exit 0.

  M1  목차 쪽번호 변조  — 첫 장의 인쇄 쪽번호를 +7 틀리게 재스탬핑 → G14-A FAIL
  M18 이미지맵 캡션     — 목차 행과 y-겹침인 썸네일 이미지+캡션 숫자(기대값 +7)를 주입
                         → G14-A는 캡션을 무시하고 진짜 쪽번호와 페어링해 **문제 0건**
                         이어야 한다(w7-b3 실측 사고의 역방향 고정: 수리 전 pair_score는
                         수직 정합인 캡션을 골라 오판 FAIL — 값이 우연히 맞으면 침묵 통과)
  M20 좌측 서수 칩      — 첫 장 행의 **제목 왼쪽**에 2자리 칩 숫자(기대값과 다른 값)를
                         주입 → 우측에 진짜 쪽번호가 있으므로 좌측 칩은 버려져 **문제
                         0건**이어야 한다(w7-b5 실측 사고의 고정: 0-접두 필터가 '10'~
                         '15' 칩을 통과시켜 pair_score에서 칩이 진짜 쪽번호를 이겼다).
                         **좌측 폴리오 레이아웃(toc_layout=spread-single-level, 현행
                         magazine 유일)은 skip** — "우측에 진짜 쪽번호"라는 주입 전제
                         자체가 성립하지 않아 진짜 좌측 폴리오와 주입 칩이 같은 군에서
                         경쟁하고, 108c85b 우측 우선 2군 규칙의 설계 범위 밖이다(실측:
                         칩이 이겨 G14-A가 **시끄러운 오탐 FAIL** — 침묵 통과 방향 아님,
                         groom2.md §2). 그 레이아웃의 페어링 감도는 좌측 폴리오 재스탬핑
                         일회 검증이 담당한다 — w7-gatefix.md
  M2  목차 이색(異色)   — 목차 면에 도비라 색 계열과 무관한 마젠타 라벨 주입 → G14-B FAIL
  M3  저대비 텍스트     — 본문 면에 흰 바탕 연회색(#c8c8c8) 캡션 주입 → G14-C FAIL
  M8  절 쪽번호 변조   — 인쇄 목차의 **절 행** 쪽번호를 +5 틀리게 재스탬핑 → G14-D FAIL
                         (실측 사고 재현: 절 마커 오배정으로 절 쪽번호·레벨 2 북마크 10/15가
                          틀린 책이 G4 레벨 2 수 대조와 G14-A를 전부 통과해 출하됐다.
                          이 축만 빌더 산출물을 참조하지 않으므로 그 계열을 유일하게 잡는다)
  M7  전역 축소        — 전 면을 0.8035배로 재배치 → G1-SCALE FAIL
                         (실측 사고 재현: 출하된 insight-ondevice-ai.pdf가 정확히 이 상태였고
                          기존 15개 게이트를 전부 통과했다. 주입본 최빈 7.63pt = 사고본과 동일)
  M9  텍스트 겹침       — 도비라(장 오프너) 면의 **기존 행과 실제로 교차하도록** 좌표를 잡아
                         한 행을 스탬핑 → G3-COLLIDE FAIL
                         (실측 사고 재현: 목차가 넘쳐 도비라 면으로 흐르면서 도비라 제목 위에
                          목차 2행이 겹쳐 인쇄된 산출물이 실재한다 —
                          /mnt/d/bookforge-verify/_judge-fold2-head p3. 주입 좌표는 그 사고와
                          동형이 되도록 도비라 첫 행의 박스 안으로 잡는다)
  M11 앞부속 프레임 이탈 — 목차 면 하단(선언 front_frame_mm 밖)에 한 행을 스탬핑 → G3-FIT FAIL
  M10 저대비 토큰       — 스타일 팩을 **임시 복사본**에 복제(저장소 styles/ 불변조)한 뒤
                         contrast_contract.entries 중 정적으로 대비 산출 가능한 첫 페어를
                         골라 fg를 bg와 동일 색으로 재기록(ratio=1.0) → g16_tokens.run을
                         그 복사본 대상으로 실행해 G16-CONTRAST FAIL 검출
                         (enforce:true 스타일만 성립 — 현재 insight·magazine)
  M12 palette_roles 훼손 — 임시 스타일 팩 사본의 diagram.palette_roles를 허용값 밖으로
                         바꿔 → G16-SYNC FAIL (HARD를 내는 축인데 감도 자산이 없었다)
  M13 위반 브랜드      — book.json.brand 위치에 고정 동반색과 hue가 어긋나는 색을 넣어
                         → G16-BRAND FAIL (출처가 book.json이라 FAIL 강도)
  M14 pt 위조(린터 배선) — 임시 스타일 팩 사본에서 계약 엔트리의 pt만 theme.css에 없는
                         값으로 위조 → 린터 축② PT_UNATTAINABLE FAIL, 그리고 그 코드가
                         **qc_gate가 fails로 올리는 집합**(LINT_HARD_CODES)에 실재함을
                         함께 어서션한다. pt는 contrast_floor의 입력이라 위조하면 계약이
                         스스로 하한을 4.5 -> 3.0으로 낮춘다(W4 판정 D1-L2)
  M9b 본문 면 겹침·승인 — 본문 면(도비라·앞부속·전면도판 아님)에 ㉠머리카락 교차만 주입
                         → 검출, ㉡같은 면에 OVERLAP_APPROVED → **면제 성립**(collide_exempt
                         분기를 실제로 밟는다), ㉢같은 면에 상한 초과 겹침을 더 주입하고
                         승인 유지 → G11 선행조건 FAIL(면당 일괄 면제의 폭발 반경 상한)
  M9c 면제 차감 불변식  — `collide_exempt_pages`가 도비라·앞부속을 어떤 입력에서도 빼는지
                         (표지가 fullbleed여도) 직접 어서션 — W4 판정 D2의 회귀 고정
  M15 라벨 밴드 상한    — 임시 책 사본에 **합성 authored 도해**를 심는다: 폭·viewBox를 알고
                         있으므로 라벨 pt를 원하는 값으로 정확히 놓을 수 있다. 8단계에서
                         이 축이 스타일별 스위치(`diagram.labelBand.enforce`)로 승격되면서
                         **강도가 둘**이 됐으므로, 임시 스타일 사본 + `--style-dir`로
                         다섯 표본을 한 묶음으로 돌린다 — ㉠enforce:false + 상한 초과 →
                         **WARN**(exit 0)·verdict=violation·level=WARN(리스크 1 방어:
                         cap 0.92 HARD는 코퍼스 68/92를 구제 불가 상태로 반려해 릴리스를
                         세운다. 승격하지 않은 스타일에서 rc!=0이면 그 자체가 회귀다),
                         ㉡enforce:true + **같은 표본** → HARD(exit≠0, 사유가 밴드 상한),
                         ㉢enforce:true + 밴드 안 → exit 0·verdict=ok(승격이 오탐을 만들지
                         않는다), ㉣enforce가 문자열 "false" → malformed FAIL(truthy 오독
                         차단, contrast_contract.enforce와 같은 계약), ㉤enforce:true인데
                         body_pt 미선언으로 검사가 꺼짐 → FAIL(조용한 무력화 차단),
                         ㉥`labelBand` **키 통삭제** → malformed FAIL(W5 판정 K2 — 종전
                         구현은 부재를 면제해 한 줄 삭제로 상한 판정과 급수 주입이 함께
                         죽었다), ㉦`maxRatio` 극대값 999 → 타당성 대역 밖 FAIL(K3 — 종전
                         검사가 "양수인가" 하나여서 경고 한 줄도 없이 통과했다),
                         ㉧`widths.twothirds` **값 위조**(> full) → G16-SYNC FAIL + 렌더
                         이중 방어 FAIL(K1·K9 — widths는 밴드·하한·주입이 공유하는 유일
                         기준이라 값이 틀리면 셋이 같은 거짓 기준으로 자기정합한다),
                         ㉨`<style>` 블록 + `<tspan class>`로 준 **CSS 급수** → 밴드 FAIL
                         (K6 — 정규식 스캔의 사각지대였고, metrics 안에서 `sizesPt`와
                         `labelPaint.pt`가 다른 값을 말하는 이중 진리를 만들었다).
  M16 라벨 역할·대비   — 임시 책 사본에 **합성 authored 도해**를 심어 색만 결함으로 만든다
                         (급수는 밴드 안·하한 위에 정확히 앉혀 다른 축을 밟지 않는다).
                         ㉠role이 `label`이 아닌 팔레트 슬롯을 글자색으로(대비는 ≥4.5로 깔아
                         역할 축만 겨눔) → render_diagrams **HARD**(exit≠0), ㉡role은 label인데
                         실배경 대비가 4.5 미만 → HARD, ㉢대조군(label × 백색) → exit 0 ·
                         metrics.labelPaint 위반 0(오탐 없음 + 검사가 실제로 돌았다는 증거),
                         ㉣**그라데이션 배경**(`fill="url(#g)"`) 위 저대비 라벨 → HARD
                         (W5 판정 K4-ⓐ — 종전엔 `normHex("url(#g)")`가 null이라 레이어를
                         통째로 버려 "판면 백색 위"로 판정했다) + 대조군: 같은 그라데이션
                         구조인데 stop이 전부 어두운 표본은 통과(오탐 0 — 벤더 3D·mindmap
                         gradient 계열이 이 방향으로 9건 오탐 반려됐던 것의 회귀 고정),
                         ㉤**`fill:none` + 굵은 stroke 면** 위 저대비 라벨 → HARD(K4-ⓑ —
                         종전엔 `fill === "none"` 도형이 후보에서 탈락했다),
                         ㉥**경계 걸침**: 중심점은 백색인데 bbox 오른쪽 절반이 어두운 면
                         위인 라벨 → HARD(K4-ⓒ — 중심점 1표본이 놓치던 형태).
                         M15와 반대로 이 축은 **HARD여야** 정상이다 — WARN으로 미끄러지면 회귀다.
  M17 목차 레이아웃 계약 — 스타일 팩을 임시 사본에 복제해 toc_layout 축(G16-SYNC)의 세 축을
                         갈라 주입한다. ㉠`toc_layout`을 **다른 팩이 구현한 레이아웃** 이름으로
                         교체 → allowed_styles 축 FAIL, ㉡theme.css/theme.typ의 점선 리더를
                         **선언과 반대 방향으로** 뒤집되(없음 선언엔 `dotted`/`repeat[.]` 주입,
                         있음 선언(practical)에선 제거) 선언은 그대로 → 리더 축 FAIL,
                         ㉢목차 급수 리터럴을 상한 +6pt로 올림 → 급수 축 FAIL(상한이 None인
                         스타일은 성립하지 않아 skip), ㉣`toc_layout`을 **카탈로그에 없는
                         이름**으로 교체 → 카탈로그 축 FAIL(㉠과 다른 축이다 — ㉠은 실존
                         레이아웃의 남용, ㉣은 미등재 어휘). 넷을 한 사본에 몰지 않는 이유는
                         "하나가 잡으면 나머지가 죽어 있어도 초록"을 회귀 자산이 은폐하기 때문.
                         ㉩~㉬은 적대검증 v-s2의 리터럴 매칭 우회 8건(A~D)의 축별 대표 회귀:
                         ㉩`toc_levels: "2"`(str) → malformed FAIL(A — bool·float·부재 계열),
                         ㉪theme.css에 dashed 리더 → 리더 축 FAIL(B — dotted 밖 관용구),
                         ㉫`font-size: var(--x)` + :root 60pt → 급수 축 FAIL(C — var 1단 해석),
                         ㉬typst 헬퍼 간접 리더(정의 상단·목차 영역엔 호출만) → 리더 축 FAIL
                         (D — leader=False 선언 typst 팩만 성립, html 팩에선 ㉪㉫만 돈다).
  M-ORIGIN 마커 앵커 소실 — html 엔진 전용. `toc_lists`를 켠 **임시 스타일 사본**으로
                         캡션 그림 2·캡션 표 2짜리 최소 책을 실빌드해 ㉠앵커 온전(대조군)
                         → 빌드 성공 + fg/tb 마커 발행 각 2 + 최종 PDF 텍스트 레이어에
                         마커 잔존 0을 확인하고, ㉡같은 사본에서 `.mk-anchor{position:
                         relative}` 앵커 규칙만 비워 재빌드 → `.pgmark{position:absolute}`
                         가 문서 원점(1면)에 붙어 **전수 회수 사후조건(종별 집합 일치)은
                         충족되는** 상태를 포함 단조 사후조건이 die로 잡는지 어서션한다.
                         (스타일 팩·스크립트 변조는 임시 사본에만 — M10·M12·M15와 같은 원칙)
                         단면 목차 스타일(BF:TOCPAGE 부재 — magazine)에서는 S5부터
                         toc_lists 옵트인 자체가 die 계약이라 본편이 성립하지 않는다 —
                         대신 그 가드 die를 M-LISTPG-single-toc-guard로 고정한다.
  M-LISTPG 차례 쪽번호 오염 — 다면 목차 html 스타일 전용. M-ORIGIN 대조군 PDF에서
                         ㉢G14-E(차례 쪽번호 ↔ 실제 캡션 면) 0건·4쌍 대조를 확인하고,
                         ㉣차례 항목 하나의 인쇄 쪽번호만 +3으로 오염(회수 딕트 셔플의
                         지면 등가물)해 G14-E가 발화하는지 어서션한다. 빌더 사후조건은
                         pass1 회수만 보므로 스탬핑 이후의 오염은 지면 재추출 대조만이
                         잡는다 — 그 유일 방어선의 감도를 회귀 자산으로 고정한다.
                         드리프트 변형(-uniform-drift): `.mk-anchor .pgmark{top:-257mm}`
                         주입 빌드(적대검증 s4-verdict ① P-HOLE — 균일 드리프트는 포함
                         단조를 통과한 채 전 회수 면을 1면씩 어긋낸다) → 빌더 die(경계
                         초과) 또는 G14-E 전 쌍 FAIL(장내) 중 하나가 반드시 발화 —
                         "rc 0 + G14-E 침묵"의 조용한 오면 인쇄 경로를 봉쇄한다.
  M19 도해 배치 높이   — 과도 종횡비 authored 도해 주입(W7). 렌더 층: ㉠상한×1.6 높이 +
                         하한×1.15 라벨 → 축소가 하한을 깨므로 **반려**(exit≠0, "가로 배치"
                         처방), ㉡상한×1.15 + 하한×1.35 라벨 → **자동 축소**(fit.verdict=
                         shrunk, 실효 최소 라벨 ≥ 하한), ㉢상한×0.5 대조군 → ok(오탐 0).
                         게이트 층(G17-FIGFIT, 스탬핑 PDF 빌드 0회): ㉣라벨 2건을 p1/p2에
                         갈라 → ① 면 분단 FAIL, 판면 하단 밖 스탬핑 → ② 초과 FAIL,
                         판면 안 대조군 → 0건. 수리 전엔 이 표본 전부가 조용히 통과했다
                         (실증 사고: insight 세로 셰브런 254.8mm가 p5/p6 분단 출하).
  M0  무변조 대조군     — 원본은 G14 전 축 + G1-SCALE + G3-COLLIDE/FIT + G16(SYNC/CONTRAST/
                         BRAND 전 축, 원본 스타일 팩) PASS (오탐 없음 확인)

**결번 M4·M5·M6**: 플랜 단계에서 예약했다가 쓰지 않은 번호다(각각 G7 밀도·G8 공기·G9
고립용으로 잡았으나 그 세 축은 실측 코퍼스에 참양성 표본이 이미 있어 합성 주입이
불필요하다고 판단). 빠진 축이 아니라 **폐기된 번호**이므로 재사용하지 않는다.

Usage: python3 tests/mutations/run_mutations.py <book_dir>
       (book_dir는 게이트 PASS 상태의 draft/book.pdf + outline.json 보유)
"""
import colorsys
import importlib.util
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(SKILL / "scripts"))

try:
    import pymupdf as fitz
except ImportError:
    import fitz

from tocgate import (find_toc_pages, g14a_toc_numbers, g14b_key_color, g14c_contrast,
                     g14d_section_numbers, g14e_list_numbers, _printed_toc_rows,
                     _LIST_ROW_RE, _norm as _toc_norm)
from qc_gate import (g1_scale_check, line_records, g3_collide_page, _column_bands,
                     front_frame_for, collide_exempt_pages, LINT_HARD_CODES,
                     COLLIDE_OX_PT, OVERLAP_APPROVE_MAX_OX_PT, MM2PT, TOL)
import g16_tokens as g16


def style_tokens(book_dir):
    book = json.loads((book_dir / "book.json").read_text(encoding="utf-8"))
    return book["style"], json.loads(
        (SKILL / "styles" / book["style"] / "tokens.json").read_text(encoding="utf-8"))


def collide_scan(doc, style, tokens):
    """qc_gate와 같은 함수 경로로 면별 원시 교차를 센다(면제 미적용)."""
    out = {}
    for pno in range(doc.page_count):
        page = doc[pno]
        recs = line_records(page.get_text("dict").get("blocks", []),
                            _column_bands(style, tokens.get("body_frame_mm"), page.rect))
        hits = g3_collide_page(recs)
        if hits:
            out[pno + 1] = hits
    return out


def fit_scan(doc, tokens, first_ch):
    """앞부속 프레임 적합 — qc_gate G3-FIT과 같은 판정(양성 조건 + 프레임 축)."""
    decl = tokens.get("front_frame_mm")
    probs = []
    for pg in range(1, first_ch):
        page = doc[pg - 1]
        recs = line_records(page.get_text("dict").get("blocks", []), None)
        if not recs:
            probs.append(f"p{pg}: 텍스트 0행")
            continue
        fr = front_frame_for(decl, pg) if decl else None
        if not fr:
            continue
        top, right, bottom, left = fr
        pr = page.rect
        box = fitz.Rect(left * MM2PT - TOL, top * MM2PT - TOL,
                        pr.width - right * MM2PT + TOL, pr.height - bottom * MM2PT + TOL)
        for r in recs:
            if not box.contains(fitz.Rect(r["raw"])):
                probs.append(f"p{pg}: '{r['text'][:16]}'")
    return probs


def _stamp_font():
    return str(SKILL / "assets" / "fonts" / "Pretendard-Regular.ttf")


def mutate_overlap(doc, ch_starts):
    """도비라(장 오프너) 면에서 **기존 행의 박스 안**에 한 행을 스탬핑해 실제 교차를 만든다.
    행 위/아래에 찍으면 교차가 성립하지 않아 감도 검증 자체가 무의미해지므로, 대상 행의
    세로 중앙에 베이스라인을 놓아 oy가 두 박스의 0.35배를 확실히 넘게 한다."""
    pno = ch_starts[0] - 1
    page = doc[pno]
    recs = line_records(page.get_text("dict").get("blocks", []), None)
    assert recs, "도비라 면에 텍스트 행이 없다 — M9 주입 불가"
    target = max(recs, key=lambda r: (r["box"][2] - r["box"][0]) * (r["box"][3] - r["box"][1]))
    x0, y0, x1, y1 = target["box"]
    size = 10.0
    page.insert_text(fitz.Point(x0 + 2, (y0 + y1) / 2 + 0.25 * size),
                     "겹침 변조 표본 라인", fontsize=size, fontfile=_stamp_font(),
                     fontname="F-ovl", color=(0, 0, 0))
    return pno + 1, target["text"][:18], [round(v, 1) for v in target["box"]]


def mutate_front_overflow(doc, tokens, first_ch):
    """마지막 목차 면의 선언 front_frame **밖**(하단 6pt 바깥)에 한 행을 스탬핑."""
    decl = tokens.get("front_frame_mm")
    if not decl or first_ch < 3:
        return None
    pg = first_ch - 1
    fr = front_frame_for(decl, pg)
    if not fr:
        return None
    top, right, bottom, left = fr
    page = doc[pg - 1]
    y = page.rect.height - bottom * MM2PT + 6
    page.insert_text(fitz.Point(left * MM2PT + 4, y), "프레임 이탈 변조 표본",
                     fontsize=9, fontfile=_stamp_font(), fontname="F-fit", color=(0, 0, 0))
    return pg, round(y, 1)


def mutate_low_contrast_tokens(style_dir, tokens, theme_text):
    """contrast_contract.entries 중 정적으로 대비 산출 가능한(fg·bg 둘 다 불투명
    리터럴 hex로 풀리는) 첫 페어를 골라 fg를 bg와 동일 색으로 되쓴다 —
    ratio=1.0이라 pt·bold와 무관하게 어떤 하한도 확실히 미달한다.

    style_dir는 임시 복사본이어야 한다(저장소 styles/ 절대 변조 금지). tokens.json을
    그 자리에서 덮어써, 이후 g16_tokens.style_inputs(style_dir=...)로 다시 읽으면
    검사가 실제로 "그 복사본"을 본다."""
    ctx = g16._ctx(tokens, theme_text)
    entries = (tokens.get("contrast_contract") or {}).get("entries") or []
    for i, e in enumerate(entries):
        fk, _fv = g16._resolve_token(e.get("fg"), ctx)
        bk, bv = g16._resolve_token(e.get("bg"), ctx)
        if fk == "hex" and bk == "hex":
            victim = dict(e, fg=bv)
            new_entries = entries[:i] + [victim] + entries[i + 1:]
            new_cc = dict(tokens["contrast_contract"], entries=new_entries)
            new_tokens = dict(tokens, contrast_contract=new_cc)
            (Path(style_dir) / "tokens.json").write_text(
                json.dumps(new_tokens, ensure_ascii=False, indent=2), encoding="utf-8")
            return i, victim
    raise AssertionError(
        "contrast_contract에 정적 판정 가능한 페어가 없음 — M10 주입 불가")


def mutate_palette_roles(style_dir, tokens):
    """diagram.palette_roles를 허용값(label|fill|stroke) 밖으로 바꿔 되쓴다.

    G16-SYNC는 build.py를 die()시키는 HARD 축인데 감도 회귀 자산이 없었다(W4 판정 D8).
    palette_roles는 G16-BRAND가 "0번 슬롯이 라벨색인가"를 판정하는 입력이라, 여기가
    조용히 부패하면 브랜드 대비 축이 통째로 빗나간다."""
    roles = list((tokens.get("diagram") or {}).get("palette_roles") or [])
    assert roles, "palette_roles가 없다 — M12 주입 불가"
    victim = list(roles)
    victim[0] = "labl"          # 오타 한 글자 — 사람이 실제로 내는 형태의 부패
    new_dg = dict(tokens["diagram"], palette_roles=victim)
    (Path(style_dir) / "tokens.json").write_text(
        json.dumps(dict(tokens, diagram=new_dg), ensure_ascii=False, indent=2), encoding="utf-8")
    return roles[0], victim[0]


def mutate_toc_layout_name(style_dir, tokens, style):
    """tokens.json의 `toc_layout`을 **다른 팩이 구현한 레이아웃** 이름으로 바꿔 되쓴다.

    G16-SYNC toc_layout 축 ②(allowed_styles). 레이아웃은 theme 실물에 사는 물건이라
    이름만 빌려 오면 선언과 지면이 갈라지는데, 선언 자체가 없던 동안에는 그 괴리가
    어느 게이트에도 보이지 않았다(S1 toc_overflow와 같은 무선언 구멍)."""
    was = tokens.get("toc_layout")
    other = next(n for n, sp in g16.TOC_LAYOUTS.items() if style not in sp["styles"])
    (Path(style_dir) / "tokens.json").write_text(
        json.dumps(dict(tokens, toc_layout=other), ensure_ascii=False, indent=2), encoding="utf-8")
    return was, other


def mutate_toc_leader(style_dir, style, tokens):
    """theme 실물의 **점선 리더를 선언과 반대로 뒤집는다** → 축 ④ 불일치.

    방향은 선언이 정한다 — 리더 없음으로 선언한 팩에는 심고, 리더 있음으로 선언한 팩
    (practical)에서는 없앤다. 한 방향(주입)만 쓰면 리더를 **가진** 팩에서는 주입 후에도
    실물이 여전히 "있음"이라 불일치가 만들어지지 않아, 그 팩에 대해서는 축이 죽어 있어도
    회귀 자산이 초록으로 통과한다(실제로 practical에서 그렇게 나왔다).
    리더 유무는 각 팩 STYLE.md가 명시로 금지/허용한 목차 문법의 식별 자질이므로,
    실물만 바뀌면 그 규범이 선언 없이 뒤집힌다.
    반환은 (파일명, 변조 설명) — 변조가 실제로 일어났는지 로그로 남긴다."""
    sd = Path(style_dir)
    declared = g16.TOC_LAYOUTS[tokens["toc_layout"]]["leader"]
    if tokens.get("engine") == "html":
        css = sd / "theme.css"
        t = css.read_text(encoding="utf-8")
        if not declared:
            assert ".toc-leader {" in t, f"{style}: .toc-leader 규칙이 없어 M17-㉡ 주입 불가"
            t = t.replace(".toc-leader {", ".toc-leader { border-bottom: 0.4pt dotted #999;", 1)
            note = "+ border-bottom: 0.4pt dotted"
        else:
            n = t.count("dotted")
            assert n, f"{style}: 제거할 dotted 리터럴이 없다"
            t = t.replace("dotted", "solid")
            note = f"dotted → solid ×{n}"
        css.write_text(t, encoding="utf-8")
        return "theme.css", note
    typ = sd / "theme.typ"
    t = typ.read_text(encoding="utf-8")
    if not declared:
        anchor = "if toc {"
        assert anchor in t, f"{style}: `if toc {{` 블록이 없어 M17-㉡ 주입 불가"
        t = t.replace(anchor, anchor + "\n    let bf-mut-leader = box(width: 1fr, repeat[.])", 1)
        note = "+ repeat[.]"
    else:
        n = len(re.findall(r"(?<![\w-])repeat\s*[(\[]", t))
        assert n, f"{style}: 제거할 repeat( 리터럴이 없다"
        t = re.sub(r"(?<![\w-])repeat(\s*[(\[])", r"stack\1", t)
        note = f"repeat( → stack( ×{n}"
    typ.write_text(t, encoding="utf-8")
    return "theme.typ", note


def mutate_toc_size(style_dir, style, tokens):
    """목차 급수 리터럴을 상한 위로 올린다 → 축 ⑤. 상한 None(변수 주입) 스타일은 skip.

    상한 해석은 g16.toc_size_cap 하나만 안다 — 스칼라/스타일별 dict(display-numeral) 양쪽."""
    sd = Path(style_dir)
    cap = g16.toc_size_cap(g16.TOC_LAYOUTS[tokens["toc_layout"]], style)
    if cap is None:
        return None
    over = cap + 6.0
    if tokens.get("engine") == "html":
        css = sd / "theme.css"
        t = css.read_text(encoding="utf-8")
        t = t.replace(".toc-title {", ".toc-title { font-size: %.1fpt;" % over, 1)
        css.write_text(t, encoding="utf-8")
        return over
    typ = sd / "theme.typ"
    t = typ.read_text(encoding="utf-8")
    t = t.replace("if toc {", "if toc {\n    let bf-mut-size = text(size: %.1fpt, \"\")" % over, 1)
    typ.write_text(t, encoding="utf-8")
    return over


def origin_probe_book(root):
    """fg/tb 마커 앵커 감도용 최소 책 — 캡션 그림 1·캡션 표 1을 가진 장 2개(합 2·2).

    (book, outline) 반환 — build_html.build()를 직접 부르므로 book.json은 파일로 만들지
    않고 dict로 준다. 그림은 실물 PNG를 심는다(깨진 src는 Chromium이 alt 폴백으로
    레이아웃을 바꿔 면 배치가 흔들린다).
    """
    d = Path(root)
    (d / "chapters").mkdir(parents=True, exist_ok=True)
    (d / "assets").mkdir(exist_ok=True)
    pm = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 64, 40), False)
    pm.clear_with(200)
    pm.save(str(d / "assets" / "probe.png"))
    para = "앵커 프로브 본문 문단이다. 마커 회수 면 검증을 위한 채움 문장이 이어진다. " * 12
    tbl = ("[표] 앵커 표본 표 | 자료: 뮤테이션\n\n"
           "| 항목 | 값 |\n| --- | --- |\n| 가 | 1 |\n| 나 | 2 |\n")
    fig = "![앵커 표본 그림](../assets/probe.png)\n"
    for n, name in ((1, "첫째"), (2, "둘째")):
        (d / "chapters" / f"ch{n}.md").write_text(
            f"# {name} 장\n\n## {name} 절 하나\n\n{para}\n\n{fig}\n{para}\n\n{tbl}\n"
            f"{para}\n\n## {name} 절 둘\n\n{para}\n", encoding="utf-8")
    book = {"style": "-", "title": "앵커 프로브", "author": "mutation"}
    outline = {"chapters": [{"file": "ch1.md", "title": "첫째 장 표본"},
                            {"file": "ch2.md", "title": "둘째 장 표본"}]}
    return book, outline


def run_origin_build(book_dir, book, outline, style_dir):
    """build_html.build를 in-process로 돌린다. 성공 시 None, die() 시 그 메시지(str)."""
    import build_html
    build_html.BUILD_WARNS.clear()
    try:
        build_html.build(Path(book_dir), book, outline, Path(style_dir), SKILL)
        return None
    except SystemExit as e:
        return str(e.code)


def violating_brand(tokens, theme_text):
    """고정 동반색 계열에서 hue가 가장 먼 유채색을 찾아 돌려준다(book.json.brand 위치용).

    임의의 색을 박으면 그 스타일의 동반색과 우연히 계열이 맞을 수 있어 감도 검증이
    무의미해진다 — 12색환을 돌며 **실제로 Δ > HUE_TOL_DEG인 색**을 고른다."""
    comps = g16._hue_companions(tokens)
    if not comps:
        return None
    best = None
    for deg in range(0, 360, 5):
        r, g_, b = colorsys.hls_to_rgb(deg / 360.0, 0.35, 0.9)
        rgb = (int(r * 255), int(g_ * 255), int(b * 255))
        if not g16.is_chromatic(rgb):
            continue
        h = g16.hue_deg(rgb)
        d = min(g16.hue_dist(h, c[1]) for c in comps)
        if best is None or d > best[0]:
            best = (d, "#%02x%02x%02x" % rgb)
    if best and best[0] > g16.HUE_TOL_DEG:
        return best[1]
    return None


def mutate_contract_pt(style_dir, tokens, theme_text):
    """계약 엔트리 하나의 **pt만** theme.css의 어떤 font-size에도 없는 값으로 위조한다.

    색은 그대로 두는 것이 핵심이다 — 색까지 바꾸면 유령 엔트리(GHOST)로 잡히지만,
    현실의 자기완화는 "하한을 3.0으로 낮추려고 pt를 올리는" 형태다. 그 경로를 잡는
    유일한 축이 린터 ②(PT_UNATTAINABLE)이고, 그 린터가 파이프라인에서 실행되지 않아
    출하 경로가 전부 통과하던 것이 W4 판정 D1이다."""
    entries = (tokens.get("contrast_contract") or {}).get("entries") or []
    assert entries, "contrast_contract.entries가 없다 — M14 주입 불가"
    for i, e in enumerate(entries):
        if not isinstance(e.get("pt"), (int, float)) or isinstance(e.get("pt"), bool):
            continue
        # 13.7pt: 어떤 theme.css에도 없는 값이면서 하한 갈래(14)를 갓 밑도는 값이라
        # "위조하려다 실수한 값"처럼 보이지 않는다. 실제 완화 시도는 14~18로 올린다.
        victim = dict(e, pt=13.7)
        new_cc = dict(tokens["contrast_contract"], entries=entries[:i] + [victim] + entries[i + 1:])
        (Path(style_dir) / "tokens.json").write_text(
            json.dumps(dict(tokens, contrast_contract=new_cc), ensure_ascii=False, indent=2),
            encoding="utf-8")
        return i, e.get("pt"), victim
    raise AssertionError("pt를 가진 엔트리가 없다 — M14 주입 불가")


def band_probe_ink(dg):
    """밴드 프로브 라벨 잉크 — 팔레트 안 · role=label · 백색 판면 대비 ≥ 4.5.

    palette[0]을 그대로 쓰면 첫 슬롯의 역할이 label이 아닌 스타일(magazine: #0E7C7B가
    stroke)에서 7단계 역할 HARD가 밴드 검사보다 먼저 발화한다 — 픽스처가 검사 대상
    축(밴드)을 밟기 전에 다른 축(role)이 표본을 죽이는 구조라, 밴드 검사의 유일한
    결함이 되도록 세 제약을 전부 만족하는 색만 고른다."""
    pal = dg["palette"]
    roles = dg.get("palette_roles") or []
    cands = ([c for c, r in zip(pal, roles) if r == "label"]
             if len(roles) == len(pal) else list(pal))
    for c in cands:
        if g16.contrast_ratio(_rgb(c), (255, 255, 255)) >= 4.5:
            return c
    return cands[0] if cands else pal[0]


def band_probe_book(root, style, tokens, ratio_of_cap):
    """합성 authored 도해 1건짜리 최소 책을 만든다 (render_diagrams 전용 — 빌드하지 않는다).

    viewBox 폭을 `widths.full × MM2PT`로 잡으면 트림 전 환산이 1pt/user-unit이라
    라벨 pt를 사실상 직접 지정할 수 있다(트림 패딩만큼만 살짝 줄어들고, 그 오차는
    어서션이 실측 metrics를 읽으므로 흡수된다). 색은 스타일 팔레트의 label 역할
    슬롯에서만 고른다(band_probe_ink) — authored 트랙 alienColors가 팔레트 밖 색을,
    7단계 역할·대비 HARD가 role 위반·저대비 색을 각각 죽이기 때문에, 색 때문에 죽으면
    밴드 감도를 재는 것이 아니라 다른 축을 재게 된다.

    ratio_of_cap: 상한(body_pt × maxRatio) 대비 최대 라벨 배수. >1이면 위반 표본.
    """
    dg = tokens["diagram"]
    body = tokens["body_pt"]
    cap = body * dg["labelBand"]["maxRatio"]
    floor = dg["minFontPt"]
    vb_w = dg["widths"]["full"] * MM2PT          # 트림 전 1pt == 1 user unit
    vb_h = 200.0
    pad = max(2.0, 0.008 * max(vb_w, vb_h))      # render_diagrams.trimViewBox와 동일 식
    scale = vb_w / (vb_w + 2 * pad)              # 트림 후 pt/user-unit
    big = (cap * ratio_of_cap) / scale
    small = (floor * 1.15) / scale               # 하한은 넉넉히 통과시킨다(HARD 회피)
    ink = band_probe_ink(dg)
    d = Path(root)
    (d / "diagrams").mkdir(parents=True, exist_ok=True)
    (d / "book.json").write_text(json.dumps({"style": style, "title": "밴드 프로브"},
                                            ensure_ascii=False), encoding="utf-8")
    (d / "diagrams" / "fig-01.json").write_text(
        json.dumps({"kind": "authored", "bf": {"width": "full"}}), encoding="utf-8")
    # rect는 bbox를 고정해 트림 결과를 예측 가능하게 만드는 용도(fill:none → alienColors 무관)
    (d / "diagrams" / "fig-01.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w:.2f} {vb_h:.2f}">'
        f'<rect x="0" y="0" width="{vb_w:.2f}" height="{vb_h:.2f}" fill="none" stroke="none"/>'
        f'<text x="4" y="60" font-size="{big:.3f}" fill="{ink}">밴드 표본</text>'
        f'<text x="4" y="170" font-size="{small:.3f}" fill="{ink}">하한 표본</text>'
        f'</svg>', encoding="utf-8")
    return {"cap_pt": cap, "floor_pt": floor, "expect_max_pt": big * scale}


def tspan_band_probe_book(root, style, tokens):
    """합성 authored 도해 — **`<style>` 블록 + `<tspan class>`로만 준 급수**(W5 판정 K6).

    `band_probe_book`과 같은 환산 트릭을 쓰되, 상한을 넘는 급수를 `font-size` 속성이
    아니라 CSS 클래스로 준다. 종전 파이프라인은 `<text>`에만 computed 급수를 굽고
    `scanLabelPt`는 속성/인라인 style만 정규식으로 훑어서 이 글자를 **못 봤다** —
    같은 metrics 안에서 `sizesPt`(9.974)와 `labelPaint.pt`(30.83)가 갈렸다.
    """
    dg = tokens["diagram"]
    body = tokens["body_pt"]
    cap = body * dg["labelBand"]["maxRatio"]
    floor = dg["minFontPt"]
    vb_w = dg["widths"]["full"] * MM2PT
    vb_h = 200.0
    pad = max(2.0, 0.008 * max(vb_w, vb_h))
    scale = vb_w / (vb_w + 2 * pad)
    big = (cap * 1.8) / scale                    # 상한의 1.8배 — CSS로만 준다
    small = (floor * 1.15) / scale
    ink = band_probe_ink(dg)
    d = Path(root)
    (d / "diagrams").mkdir(parents=True, exist_ok=True)
    (d / "book.json").write_text(json.dumps({"style": style, "title": "tspan 급수 프로브"},
                                            ensure_ascii=False), encoding="utf-8")
    (d / "diagrams" / "fig-01.json").write_text(
        json.dumps({"kind": "authored", "bf": {"width": "full"}}), encoding="utf-8")
    (d / "diagrams" / "fig-01.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w:.2f} {vb_h:.2f}">'
        f'<style>.bigcss{{font-size:{big:.3f}px}}</style>'
        f'<rect x="0" y="0" width="{vb_w:.2f}" height="{vb_h:.2f}" fill="none" stroke="none"/>'
        f'<text x="4" y="60" font-size="{small:.3f}" fill="{ink}">하한 표본</text>'
        f'<text x="4" y="170" font-size="{small:.3f}" fill="{ink}">'
        f'<tspan class="bigcss">CSS급수</tspan></text>'
        f'</svg>', encoding="utf-8")
    return {"cap_pt": cap, "floor_pt": floor, "expect_max_pt": big * scale}


def figfit_probe_book(root, style, tokens, mode):
    """합성 authored 도해 1건짜리 최소 책 — **W7 배치 높이 상한(figFitReport) 전용**.

    band_probe_book과 같은 환산 트릭(viewBox 폭 = widths.full × MM2PT → 트림 후
    1pt ≈ 1 user unit)으로 라벨 pt를 밴드 안·하한 위에 앉히고, **viewBox 높이만**
    결함으로 만든다 — 검출된 FAIL이 높이 축의 것임을 증명하기 위해서다.

    mode:
      "reject"  — 배치 높이 = 상한 × 1.6, 라벨 = 하한 × 1.15. 필요 축소 ×0.625가
                  허용 한계 ×0.870(= floor ÷ floor×1.15)을 깨므로 **반려**여야 한다.
      "shrink"  — 배치 높이 = 상한 × 1.15, 라벨 = 하한 × 1.35. 필요 축소 ×0.870이
                  허용 한계 ×0.741 위이므로 **자동 축소**(fit.verdict=shrunk)여야 한다.
      "control" — 배치 높이 = 상한 × 0.5 → fit.verdict=ok (오탐 0 확인).
    """
    dg = tokens["diagram"]
    floor = dg["minFontPt"]
    max_h = dg["maxHeightMm"]
    w_mm = dg["widths"]["full"]
    vb_w = w_mm * MM2PT
    ratio = {"reject": 1.6, "shrink": 1.15, "control": 0.5}[mode]
    vb_h = vb_w * (max_h / w_mm) * ratio
    pad = max(2.0, 0.008 * max(vb_w, vb_h))      # render_diagrams.trimViewBox와 동일 식
    scale = vb_w / (vb_w + 2 * pad)              # 트림 후 pt/user-unit
    lab = (floor * (1.35 if mode == "shrink" else 1.15)) / scale
    ink = band_probe_ink(dg)
    d = Path(root)
    (d / "diagrams").mkdir(parents=True, exist_ok=True)
    (d / "book.json").write_text(json.dumps({"style": style, "title": "피그핏 프로브"},
                                            ensure_ascii=False), encoding="utf-8")
    (d / "diagrams" / "fig-01.json").write_text(
        json.dumps({"kind": "authored", "bf": {"width": "full"}}), encoding="utf-8")
    (d / "diagrams" / "fig-01.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w:.2f} {vb_h:.2f}">'
        f'<rect x="0" y="0" width="{vb_w:.2f}" height="{vb_h:.2f}" fill="none" stroke="none"/>'
        f'<text x="4" y="60" font-size="{lab:.3f}" fill="{ink}">높이 표본</text>'
        f'<text x="4" y="{vb_h - 30:.1f}" font-size="{lab:.3f}" fill="{ink}">하단 표본</text>'
        f'</svg>', encoding="utf-8")
    return {"floor_pt": floor, "max_h": max_h,
            "placed_h_nominal": w_mm * (vb_h + 2 * pad) / (vb_w + 2 * pad)}


def figfit_gate_probe(root, tokens, variant):
    """G17-FIGFIT 지면 술어 프로브 — 최소 book_dir + 스탬핑 PDF(빌드 0회, M1 계열 스탬핑).

    variant:
      "split"    — 도해 라벨 2건을 p1/p2에 갈라 스탬핑 → ① 면 분단 FAIL이어야 한다.
      "overflow" — 두 라벨을 p1에 두되 하나를 body_frame 하단 밖에 스탬핑 → ② FAIL.
      "control"  — 두 라벨 모두 p1 판면 안 → 문제 0건(오탐 0)이어야 한다.
    반환: g17_figfit_check(...) 결과 problems 리스트.
    """
    from qc_gate import g17_figfit_check, line_records as _lr
    d = Path(root)
    (d / "chapters").mkdir(parents=True, exist_ok=True)
    (d / "assets").mkdir(exist_ok=True)
    (d / "diagrams").mkdir(exist_ok=True)
    (d / "outline.json").write_text(json.dumps(
        {"chapters": [{"file": "ch-01.md", "title": "프로브", "summary": ""}]},
        ensure_ascii=False), encoding="utf-8")
    (d / "chapters" / "ch-01.md").write_text(
        "# 프로브\n\n![프로브 캡션](../assets/fig-01.svg)\n", encoding="utf-8")
    labels = ["피그핏 상단 라벨", "피그핏 하단 라벨"]
    (d / "assets" / "fig-01.labels.json").write_text(
        json.dumps(labels, ensure_ascii=False), encoding="utf-8")
    # 종횡비가 낮은 합법 SVG — 정적 술어 ③은 여기서 통과시켜 ①·②만 겨눈다
    (d / "assets" / "fig-01.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 368 100"></svg>',
        encoding="utf-8")
    (d / "diagrams" / "fig-01.json").write_text(
        json.dumps({"kind": "authored", "bf": {"width": "full"}}), encoding="utf-8")
    trim = tokens.get("trim_mm") or [182, 257]
    top, _r, bottom, left = tokens.get("body_frame_mm") or [40, 20, 25, 25]
    w_pt, h_pt = trim[0] * MM2PT, trim[1] * MM2PT
    doc = fitz.open()
    for _ in range(2):
        doc.new_page(width=w_pt, height=h_pt)
    x = left * MM2PT + 10
    y_in1, y_in2 = top * MM2PT + 60, top * MM2PT + 90
    y_out = h_pt - bottom * MM2PT + 12   # 판면 하단 밖(overflow 변형)
    stamps = {"split": [(0, y_in1, labels[0]), (1, y_in1, labels[1])],
              "overflow": [(0, y_in1, labels[0]), (0, y_out, labels[1])],
              "control": [(0, y_in1, labels[0]), (0, y_in2, labels[1])]}[variant]
    for pno, y, txt in stamps:
        doc[pno].insert_text(fitz.Point(x, y), txt, fontsize=10,
                             fontname="probe", fontfile=_stamp_font())
    page_texts = [doc[i].get_text() for i in range(2)]
    line_recs = {i + 1: _lr(doc[i].get_text("dict").get("blocks", []), None)
                 for i in range(2)}
    page_size = {i + 1: (doc[i].rect.width, doc[i].rect.height) for i in range(2)}
    doc.close()
    outline = json.loads((d / "outline.json").read_text(encoding="utf-8"))
    return g17_figfit_check(d, outline, page_texts, line_recs, page_size, tokens, 1)


def _rgb(hex_):
    return tuple(int(hex_[1 + 2 * i:3 + 2 * i], 16) for i in range(3))


def paint_probe_book(root, style, tokens, mode):
    """합성 authored 도해 1건짜리 최소 책 — **7단계 역할·대비 HARD 전용**.

    `band_probe_book`과 같은 트릭(viewBox 폭 = widths.full × MM2PT → 1pt ≈ 1 user unit)으로
    라벨 pt를 밴드 안(하한 위)에 정확히 앉히고, **색만** 결함으로 만든다. 그래야 검출된
    FAIL이 색 축의 것임이 증명된다(급수 하한 HARD를 밟으면 다른 축을 재게 된다).

    mode:
      "role"     — role이 `label`이 **아닌** 팔레트 슬롯을 글자색으로. 대비는 충분히
                   확보되도록(≥ 4.5) 어두운 label 슬롯을 배경으로 깔아 **역할 축만** 겨눈다.
      "contrast" — role `label` 슬롯을 글자색으로 쓰되(역할 축은 통과) 대비가 4.5 미만이
                   되는 팔레트 색을 배경으로 깔아 **대비 축만** 겨눈다.
      "control"  — label 슬롯 × 백색 배경(대조군, 오탐 0 확인).
    W5 재작업이 더한 세 모드(판정 K4의 세 결함을 하나씩 겨눈다 — 전부 **배경 산출**의
    문제이고 색 자체는 `contrast`와 같은 쌍을 쓴다):
      "gradient"    — 배경이 `fill="url(#g)"` 그라데이션이고 stop 하나가 저대비 색.
                      종전엔 `normHex("url(#g)") → null`이라 레이어를 통째로 버려
                      "판면 백색 위"로 판정했다(K4-ⓐ 위음성).
      "gradient-ok" — **대조군**: 같은 그라데이션 구조인데 stop이 전부 합법 대비.
                      그라데이션을 통째로 반려하지 않는다는 증거다(같은 결함이 벤더
                      3D·mindmap gradient 계열을 9건 오탐 반려시켰던 방향의 회귀 고정).
      "stroke"      — 배경이 `fill:none` + 굵은 stroke 면. 종전엔 후보에서 탈락했다(K4-ⓑ).
      "edge"        — 글자 bbox **중심은 백색**인데 오른쪽 절반이 저대비 면 위.
                      중심점 1표본이 놓치던 형태다(K4-ⓒ). `textLength`로 글자 폭을
                      못 박아 면 경계를 결정론적으로 놓는다.
    색은 전부 스타일 팔레트에서 고른다 — authored 트랙 alienColors(strict)가 팔레트 밖
    색을 먼저 죽이기 때문이다(그라데이션 `stop-color`도 같은 검사를 받는다).
    고를 수 없으면 None을 돌려 그 스타일에서 건너뛴다.
    """
    dg = tokens["diagram"]
    pal = dg["palette"]
    roles = dg.get("palette_roles") or []
    if len(roles) != len(pal):
        return None
    labels = [c for c, r in zip(pal, roles) if r == "label"]
    others = [c for c, r in zip(pal, roles) if r != "label"]
    if not labels:
        return None
    if mode == "role":
        # 역할 위반 색 × 그 색과 대비가 가장 큰 label 배경 — 대비 축은 통과시킨다.
        # others[0] 고정이면 첫 후보가 저대비일 때(magazine: #0E7C7B×#111111 = 3.77)
        # 표본 구성 자체가 None으로 죽어 role 축이 자명 통과한다 — 전 후보를 순회한다.
        pair = None
        for f in others:
            b = max(labels, key=lambda c: g16.contrast_ratio(_rgb(f), _rgb(c)))
            if g16.contrast_ratio(_rgb(f), _rgb(b)) >= 4.5:
                pair = (f, b)
                break
        if not pair:
            return None
        fg, bg = pair
    elif mode in ("contrast", "gradient", "stroke", "edge"):
        pair = None
        for f in labels:                     # 역할은 합법(label), 대비만 깬다
            # edge/gradient는 "백색 위에서는 합법"이 표본의 전제다(중심점·나머지 stop)
            if mode in ("edge", "gradient") and g16.contrast_ratio(_rgb(f), (255, 255, 255)) < 4.5:
                continue
            for b in pal:
                # 같은 색끼리(대비 1.0)는 퇴화 표본이다 — 서로 다른 두 색으로 하한을 깬다
                if b.lower() == f.lower():
                    continue
                if g16.contrast_ratio(_rgb(f), _rgb(b)) < 4.5:
                    pair = (f, b)
                    break
            if pair:
                break
        if not pair:
            return None
        fg, bg = pair
    elif mode == "gradient-ok":
        # 대조군: 글자색과 대비가 **전부** 합법인 stop 둘. 없으면 백색 2점으로 퇴화시키지
        # 않고 건너뛴다 — 퇴화 표본은 "그라데이션을 해석했다"를 증명하지 못한다.
        ok = None
        for f in labels:
            cands = [c for c in list(pal) + ["#FFFFFF"]
                     if c.lower() != f.lower() and g16.contrast_ratio(_rgb(f), _rgb(c)) >= 4.5]
            if len(cands) >= 2:
                ok = (f, cands[0], cands[1])
                break
        if not ok:
            return None
        fg, bg, bg2 = ok
    else:
        fg, bg = labels[0], "#FFFFFF"
    body = tokens["body_pt"]
    floor = dg["minFontPt"]
    vb_w = dg["widths"]["full"] * MM2PT
    vb_h = 120.0
    pad = max(2.0, 0.008 * max(vb_w, vb_h))
    scale = vb_w / (vb_w + 2 * pad)
    size = (max(floor * 1.15, body * 0.95)) / scale   # 하한 위·14pt 아래(하한 4.5 성립)
    d = Path(root)
    (d / "diagrams").mkdir(parents=True, exist_ok=True)
    (d / "book.json").write_text(json.dumps({"style": style, "title": "도장 프로브"},
                                            ensure_ascii=False), encoding="utf-8")
    (d / "diagrams" / "fig-01.json").write_text(
        json.dumps({"kind": "authored", "bf": {"width": "full"}}), encoding="utf-8")
    head = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w:.2f} {vb_h:.2f}">'
    label = "도장 표본"
    if mode in ("gradient", "gradient-ok"):
        # 백색 판면 위에 그라데이션 면 하나. 저대비 stop을 **왼쪽 끝**에 둬서 종전
        # 중심점 판정이었다면 백색으로 보였을 자리에도 실색이 있게 한다.
        stop2 = bg2 if mode == "gradient-ok" else "#FFFFFF"
        body_svg = (
            f'<defs><linearGradient id="pg" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{bg}"/><stop offset="1" stop-color="{stop2}"/>'
            f'</linearGradient></defs>'
            f'<rect x="0" y="0" width="{vb_w:.2f}" height="{vb_h:.2f}" fill="#FFFFFF"/>'
            f'<rect x="0" y="30" width="{vb_w:.2f}" height="60" fill="url(#pg)"/>'
            f'<text x="8" y="70" font-size="{size:.3f}" fill="{fg}">{label}</text>')
    elif mode == "stroke":
        body_svg = (
            f'<rect x="0" y="0" width="{vb_w:.2f}" height="{vb_h:.2f}" fill="#FFFFFF"/>'
            f'<path d="M0 65 L{vb_w:.2f} 65" stroke="{bg}" stroke-width="56" fill="none"/>'
            f'<text x="8" y="70" font-size="{size:.3f}" fill="{fg}">{label}</text>')
    elif mode == "edge":
        # textLength로 글자 폭을 못 박아 면 경계를 결정론적으로 놓는다: 글자는 [8, 8+tw],
        # 저대비 면은 그 **오른쪽 45%**만 덮는다 → 중심점(50%)은 백색, 70·90% 표본만 실색.
        tw = min(vb_w * 0.5, size * len(label) * 1.1)
        cut = 8 + tw * 0.55
        body_svg = (
            f'<rect x="0" y="0" width="{vb_w:.2f}" height="{vb_h:.2f}" fill="#FFFFFF"/>'
            f'<rect x="{cut:.2f}" y="40" width="{vb_w - cut:.2f}" height="50" fill="{bg}"/>'
            f'<text x="8" y="70" font-size="{size:.3f}" fill="{fg}" '
            f'textLength="{tw:.2f}" lengthAdjust="spacingAndGlyphs">{label}</text>')
    else:
        body_svg = (
            f'<rect x="0" y="0" width="{vb_w:.2f}" height="{vb_h:.2f}" fill="{bg}"/>'
            f'<text x="8" y="70" font-size="{size:.3f}" fill="{fg}">{label}</text>')
    (d / "diagrams" / "fig-01.svg").write_text(head + body_svg + "</svg>", encoding="utf-8")
    return {"fg": fg, "bg": bg, "expect_pt": size * scale,
            "ratio": g16.contrast_ratio(_rgb(fg), _rgb(bg)),
            "role": dict(zip(pal, roles)).get(fg)}


def run_render_diagrams(book_dir, style, style_dir=None):
    """render_diagrams.mjs를 실제로 돌린다. (rc, stdout+stderr) 반환.

    style_dir를 주면 `--style-dir`로 스타일 팩 **임시 사본**을 읽힌다(저장소 styles/는
    절대 변조하지 않는다는 M10·M12·M14와 같은 원칙). 승격 스위치처럼 저장소 값에 따라
    강도가 달라지는 축은 이 통로가 없으면 한쪽 분기를 영영 밟지 못한다.
    """
    import os
    import subprocess
    env = dict(os.environ)
    try:
        env["NODE_PATH"] = subprocess.run(["npm", "root", "-g"], capture_output=True,
                                          text=True).stdout.strip()
    except OSError:
        pass
    cmd = ["node", str(SKILL / "scripts" / "render_diagrams.mjs"),
           str(book_dir), "--style", style]
    if style_dir:
        cmd += ["--style-dir", str(style_dir)]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def pick_body_page(doc, ch_starts, first_ch):
    """도비라·앞부속이 아닌 본문 면 중 라인이 넉넉한 면. (면번호, recs)."""
    for pno in range(first_ch - 1, doc.page_count):
        pg = pno + 1
        if pg in ch_starts or pg < first_ch:
            continue
        recs = line_records(doc[pno].get_text("dict").get("blocks", []), None)
        if len(recs) >= 12:
            return pg, recs
    return None, None


def mutate_hairline_overlap(doc, pg, recs):
    """기존 행 끝단에 **머리카락만큼**(ox ≈ 2pt) 물리는 장식 글리프를 찍는다.
    OVERLAP_APPROVED가 존재하는 사유(정당한 조판)와 같은 크기의 교차다."""
    t = recs[3]
    x0, y0, x1, y1 = t["box"]
    doc[pg - 1].insert_text(fitz.Point(x1 - 2.0, (y0 + y1) / 2 + 2.0), "·",
                            fontsize=8, fontfile=_stamp_font(), fontname="Fhl", color=(0, 0, 0))
    return t["text"][:16]


def mutate_severe_overlap(doc, pg, recs):
    """본문 행 위에 온전한 한 행을 통째로 덮어쓴다(ox ≫ 상한). 명백한 결함."""
    t = recs[9]
    x0, y0, x1, y1 = t["box"]
    doc[pg - 1].insert_text(fitz.Point(x0, (y0 + y1) / 2 + 2.5),
                            "중대한 겹침 주입 행 이 문장은 아래 본문과 완전히 겹쳐 인쇄된다",
                            fontsize=9.5, fontfile=_stamp_font(), fontname="Fsv", color=(0, 0, 0))
    return t["text"][:16]


def load(book_dir):
    outline = json.loads((book_dir / "outline.json").read_text(encoding="utf-8"))
    titles = [c["title"].strip() for c in outline["chapters"]]
    doc = fitz.open(book_dir / "draft" / "book.pdf")
    ch_starts = sorted({p for l, _, p in doc.get_toc(simple=True) if l == 1})
    return doc, titles, ch_starts


def declared_body_pt(book_dir):
    """book.json의 style → styles/<style>/tokens.json의 body_pt."""
    book = json.loads((book_dir / "book.json").read_text(encoding="utf-8"))
    tokens = json.loads((SKILL / "styles" / book["style"] / "tokens.json").read_text(encoding="utf-8"))
    return tokens.get("body_pt")


def mutate_global_shrink(src, dst, k=0.8035):
    """전 면을 k배로 축소 재배치 — Chromium shrink-to-fit 산출물과 동형.
    show_pdf_page는 form XObject 변환으로 싣기 때문에 텍스트 레이어 급수도 k배가 된다
    (실측: 9.49pt 원본 → 7.63pt, 출하 사고본과 동일값)."""
    s = fitz.open(src)
    out = fitz.open()
    for page in s:
        np_ = out.new_page(width=page.rect.width, height=page.rect.height)
        np_.show_pdf_page(fitz.Rect(0, 0, page.rect.width * k, page.rect.height * k),
                          s, page.number)
    out.save(dst)
    out.close()
    s.close()


def mutate_toc_number(doc, titles, ch_starts):
    """첫 장의 목차 인쇄 쪽번호를 지우고 +7 값으로 재스탬핑."""
    toc_pages = find_toc_pages(doc, titles)
    assert toc_pages, "목차 면 미발견 — 뮤테이션 불가"
    page = doc[toc_pages[0]]
    offset = ch_starts[0] - 1
    target = str(ch_starts[0] - offset)  # 첫 장 폴리오(=1)
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if s["text"].strip() == target:
                    r = fitz.Rect(s["bbox"])
                    page.add_redact_annot(r, fill=(1, 1, 1))
                    page.apply_redactions()
                    page.insert_text(fitz.Point(r.x0, r.y1 - 1), str(int(target) + 7),
                                     fontsize=s["size"], color=(0, 0, 0))
                    return True
    return False


def mutate_tocmap_caption(doc, titles, ch_starts):
    """목차 면 첫 장 행의 제목~쪽번호 사이에 합성 썸네일 이미지 + y-정합 캡션 숫자를
    주입한다 — magazine $tocmap 이미지맵 오페어링(w7-b3)의 지면 등가물.

    실측 사고 재현: display-numeral 목차에서 .toc-map 썸네일 캡션(장 폴리오)이 목차
    행과 y-겹침을 만들자 pair_score(수평거리 + 40×수직중심 이탈)가 수직 정합인 캡션을
    행의 진짜 쪽번호(수직 2.2pt 이탈) 대신 골랐다. 캡션 값이 기대 폴리오와 우연히
    일치하면 침묵 통과, 어긋나면 오판 FAIL — 어느 쪽도 페어링이 틀렸다는 사실은 같다.
    주입 캡션은 기대값 +7로 어긋나게 둔다: 수리 전 코드는 캡션을 페어링해 G14-A가
    오판 FAIL하고, 수리 후(이미지 x-존 캡션 제외)는 진짜 쪽번호와 페어링해 문제
    0건 + printed == expected여야 한다. 반환: (title, expected) 또는 None(공백 부족)."""
    toc_pages = find_toc_pages(doc, titles, first_ch=ch_starts[0])
    if not toc_pages:
        return None
    offset = ch_starts[0] - 1
    for i, title in enumerate(titles):
        if i >= len(ch_starts):
            break
        expected = ch_starts[i] - offset
        key = "".join(title.split())[:10]
        t_span = page = None
        for p in toc_pages:
            for b in doc[p].get_text("dict")["blocks"]:
                for l in b.get("lines", []):
                    for s in l["spans"]:
                        if key and key in "".join(s["text"].split()):
                            t_span, page = s, doc[p]
                            break
                    if t_span:
                        break
                if t_span:
                    break
            if t_span:
                break
        if t_span is None:
            continue
        y0, y1 = t_span["bbox"][1], t_span["bbox"][3]
        cy = (y0 + y1) / 2
        # 같은 행의 진짜 쪽번호(PASS 상태이므로 값 == expected) — 그 왼쪽 리더 공백에 주입
        num = None
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if (s["text"].strip() == str(expected)
                            and not (s["bbox"][3] < y0 - 4 or s["bbox"][1] > y1 + 4)
                            and s["bbox"][0] > t_span["bbox"][2]):
                        num = s
        if num is None or num["bbox"][0] - t_span["bbox"][2] < 40:
            continue                       # 리더 공백 부족 — 다음 장 행 시도
        ix0, ix1 = t_span["bbox"][2] + 6, num["bbox"][0] - 6
        pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 8, 8))
        pix.clear_with(180)
        page.insert_image(fitz.Rect(ix0, cy - 14, ix1, cy - 3), pixmap=pix)
        page.insert_text(fitz.Point(ix0 + 6, cy + 3), str(expected + 7),
                         fontsize=7.5, color=(0.35, 0.35, 0.35))
        return title, expected
    return None


def mutate_ordinal_chip(doc, titles, ch_starts):
    """목차 첫 장 행의 제목 **왼쪽**에 2자리 칩 숫자(기대값+66)를 주입 — practical
    2단 목차의 장 서수 칩(w7-b5) 지면 등가물. 0-접두가 아니므로 서수 장식 필터를
    통과하고, 제목에 인접해 pair_score에서 우단의 진짜 쪽번호를 이기는 위치다.
    수리 후 코드는 우측 후보 존재 시 좌측을 버리므로 정페어링이어야 한다.
    반환: (title, expected) 또는 None(제목 왼쪽 공간 부족)."""
    toc_pages = find_toc_pages(doc, titles, first_ch=ch_starts[0])
    if not toc_pages:
        return None
    offset = ch_starts[0] - 1
    for i, title in enumerate(titles):
        if i >= len(ch_starts):
            break
        expected = ch_starts[i] - offset
        key = "".join(title.split())[:10]
        for p in toc_pages:
            page = doc[p]
            for b in page.get_text("dict")["blocks"]:
                for l in b.get("lines", []):
                    for s in l["spans"]:
                        if key and key in "".join(s["text"].split()) and s["bbox"][0] >= 30:
                            cy = (s["bbox"][1] + s["bbox"][3]) / 2
                            page.insert_text(fitz.Point(s["bbox"][0] - 22, cy + 3),
                                             str(expected + 66), fontsize=7,
                                             color=(0.3, 0.3, 0.3))
                            return title, expected
    return None


def mutate_alien_color(doc, titles):
    """목차 면에 마젠타(어느 스타일과도 다른 hue) 텍스트 주입."""
    toc_pages = find_toc_pages(doc, titles)
    page = doc[toc_pages[0]]
    page.insert_text(fitz.Point(60, 60), "MUTANT", fontsize=12, color=(0.9, 0.05, 0.55))
    return True


def mutate_low_contrast(doc, ch_starts):
    """본문 면에 흰 바탕 위 #c8c8c8 8pt 텍스트 주입 (대비 1.6:1)."""
    pno = ch_starts[0]  # 첫 장 시작 다음 면쯤이 무난
    page = doc[min(pno, doc.page_count - 1)]
    page.insert_text(fitz.Point(page.rect.x1 / 2, page.rect.y1 / 2),
                     "저대비 변조 표본", fontsize=8, fontfile=str(
                         SKILL / "assets" / "fonts" / "Pretendard-Regular.ttf"),
                     fontname="F-mut", color=(0.784, 0.784, 0.784))
    return True


def mutate_section_number(doc, titles, ch_starts):
    """인쇄 목차의 첫 **절 행** 쪽번호를 지우고 +5 값으로 재스탬핑.
    장 행이 아니라 절 행을 고른다 — G14-A는 장만 순회하므로 이 변조는 G14-D만 잡는다."""
    toc_pages = find_toc_pages(doc, titles, first_ch=ch_starts[0])
    if not toc_pages:
        return False
    for r in _printed_toc_rows(doc, toc_pages):
        txt = "".join(r["text"].split())
        if any(txt.startswith("".join(t.split())[:10]) for t in titles):
            continue                       # 장 행 — 건너뛴다
        page = doc[r["page"]]
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if s["text"].strip() == str(r["printed"]) and \
                            abs(s["bbox"][1] - min(x["bbox"][1] for x in l["spans"])) < 1:
                        rect = fitz.Rect(s["bbox"])
                        page.add_redact_annot(rect, fill=(1, 1, 1))
                        page.apply_redactions()
                        page.insert_text(fitz.Point(rect.x0, rect.y1 - 1),
                                         str(r["printed"] + 5),
                                         fontsize=s["size"], color=(0, 0, 0))
                        return True
    return False


def mutate_list_number(doc, first_ch):
    """그림·표 차례 별면의 첫 항목 쪽번호를 지우고 +3 값으로 재스탬핑.

    회수 딕트가 오염된 채(예: 셔플) 스탬핑된 상태의 지면 등가물이다 — 빌더 사후조건
    (전수 회수·포함 단조)은 pass1 회수를 보므로 이 오염을 원리적으로 못 보고,
    G14-E(PDF 재추출 대조)만이 잡아야 한다."""
    for p in range(1, first_ch - 1):
        for r in _printed_toc_rows(doc, [p]):
            if not any(rx.match(_toc_norm(r["text"])) for rx in _LIST_ROW_RE.values()):
                continue
            page = doc[r["page"]]
            for b in page.get_text("dict")["blocks"]:
                for l in b.get("lines", []):
                    for s in l["spans"]:
                        if s["text"].strip() == str(r["printed"]):
                            rect = fitz.Rect(s["bbox"])
                            page.add_redact_annot(rect, fill=(1, 1, 1))
                            page.apply_redactions()
                            page.insert_text(fitz.Point(rect.x0, rect.y1 - 1),
                                             str(r["printed"] + 3),
                                             fontsize=s["size"], color=(0, 0, 0))
                            return r["text"][:16], r["printed"]
    return None


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    book_dir = Path(sys.argv[1]).resolve()
    results = {}

    # M0 대조군 — 원본은 전 축 PASS여야 뮤테이션 판정이 의미 있다
    doc, titles, ch_starts = load(book_dir)
    decl_pt = declared_body_pt(book_dir)
    a0, _ = g14a_toc_numbers(doc, titles, ch_starts)
    b0 = g14b_key_color(doc, titles, ch_starts)
    c0, _ = g14c_contrast(doc)
    s0 = g1_scale_check(doc, decl_pt)[1] if decl_pt else []
    tp0 = find_toc_pages(doc, titles, first_ch=ch_starts[0])
    d0, _w0, d0_pairs = g14d_section_numbers(doc, tp0, titles, ch_starts)
    style, tokens = style_tokens(book_dir)
    col0 = collide_scan(doc, style, tokens)
    fit0 = fit_scan(doc, tokens, ch_starts[0])
    _tokens_g16_0, theme_text_0 = g16.style_inputs(style)  # 원본 styles/<style> (변조 없음)
    res_g16_0 = g16.run(style, _tokens_g16_0, theme_text_0)
    g16_fails0 = {ax: g16.fails_of(fs) for ax, fs in res_g16_0.items() if g16.fails_of(fs)}
    results["M0-clean"] = (not a0 and not b0 and not c0 and not s0 and not d0
                           and not col0 and not fit0 and not g16_fails0)
    if col0:
        print(f"      (M0 G3-COLLIDE 오탐 {sum(len(v) for v in col0.values())}건 {sorted(col0)})")
    if fit0:
        print(f"      (M0 G3-FIT 오탐 {len(fit0)}건 {fit0[:3]})")
    if g16_fails0:
        n = sum(len(v) for v in g16_fails0.values())
        print(f"      (M0 G16 오탐 {n}건 {list(g16_fails0)})")
    has_sections = bool(d0_pairs)
    doc.close()

    with tempfile.TemporaryDirectory() as td:
        # M1
        work = Path(td) / "m1.pdf"
        shutil.copy(book_dir / "draft" / "book.pdf", work)
        doc = fitz.open(work)
        assert mutate_toc_number(doc, titles, ch_starts), "M1 주입 실패"
        a1, _ = g14a_toc_numbers(doc, titles, ch_starts)
        results["M1-toc-number"] = bool(a1)
        doc.close()

        # M18 — M1과 반대 방향의 축: 주입이 **검출되면 안 된다**(캡션은 쪽번호가 아니다).
        # 수리 전 코드는 캡션 +7 값을 그 행의 쪽번호로 페어링해 오판 FAIL했다.
        work = Path(td) / "m18.pdf"
        shutil.copy(book_dir / "draft" / "book.pdf", work)
        doc = fitz.open(work)
        hit18 = mutate_tocmap_caption(doc, titles, ch_starts)
        if hit18:
            t18, exp18 = hit18
            a18, pairs18 = g14a_toc_numbers(doc, titles, ch_starts)
            pr18 = next((p for p in pairs18 if p["title"] == t18), None)
            results["M18-tocmap-caption"] = (not a18 and pr18 is not None
                                             and pr18["printed"] == exp18)
            print(f"      (M18 '{t18[:12]}' 행에 캡션 {exp18 + 7} 주입 → 문제 {len(a18)}건 · "
                  f"페어링 printed={pr18['printed'] if pr18 else '?'} == {exp18})")
        else:
            print("      (M18 건너뜀 — 목차 행 리더 공백 부족)")
        doc.close()

        # M20 — 좌측 서수 칩: M18과 같은 방향(주입이 검출되면 안 된다).
        # 좌측 폴리오 레이아웃은 skip — 주입 전제("우측에 진짜 쪽번호")가 성립하지
        # 않아 진짜 좌측 폴리오와 칩이 같은 군에서 경쟁, 우측 우선 2군 규칙(108c85b)의
        # 설계 범위 밖이다. 실측(groom2.md §2): 칩이 이겨 G14-A 시끄러운 오탐 FAIL.
        # 그 레이아웃의 감도는 좌측 폴리오 재스탬핑 일회 검증(w7-gatefix.md) 담당.
        work = Path(td) / "m19.pdf"
        shutil.copy(book_dir / "draft" / "book.pdf", work)
        doc = fitz.open(work)
        hit19 = (None if tokens.get("toc_layout") == "spread-single-level"
                 else mutate_ordinal_chip(doc, titles, ch_starts))
        if tokens.get("toc_layout") == "spread-single-level":
            print("      (M20 건너뜀 — 좌측 폴리오 레이아웃(spread-single-level): "
                  "우측 우선 규칙의 주입 전제 불성립, 도큐스트링 M20 항 참조)")
        elif hit19:
            t19, exp19 = hit19
            a19, pairs19 = g14a_toc_numbers(doc, titles, ch_starts)
            pr19 = next((p for p in pairs19 if p["title"] == t19), None)
            results["M20-ordinal-chip"] = (not a19 and pr19 is not None
                                           and pr19["printed"] == exp19)
            print(f"      (M20 '{t19[:12]}' 제목 왼쪽에 칩 {exp19 + 66} 주입 → 문제 {len(a19)}건 · "
                  f"페어링 printed={pr19['printed'] if pr19 else '?'} == {exp19})")
        else:
            print("      (M20 건너뜀 — 제목 왼쪽 공간 부족)")
        doc.close()

        # M2
        work = Path(td) / "m2.pdf"
        shutil.copy(book_dir / "draft" / "book.pdf", work)
        doc = fitz.open(work)
        mutate_alien_color(doc, titles)
        b2 = g14b_key_color(doc, titles, ch_starts)
        results["M2-alien-color"] = bool(b2)
        doc.close()

        # M3
        work = Path(td) / "m3.pdf"
        shutil.copy(book_dir / "draft" / "book.pdf", work)
        doc = fitz.open(work)
        mutate_low_contrast(doc, ch_starts)
        c3, _ = g14c_contrast(doc)
        results["M3-low-contrast"] = bool(c3)
        doc.close()

        # M8 — toc_levels: 1 스타일(절 행 없음)에서는 성립하지 않으므로 건너뛴다
        if has_sections:
            work = Path(td) / "m8.pdf"
            shutil.copy(book_dir / "draft" / "book.pdf", work)
            doc = fitz.open(work)
            assert mutate_section_number(doc, titles, ch_starts), "M8 주입 실패"
            tp8 = find_toc_pages(doc, titles, first_ch=ch_starts[0])
            d8, _w8, _p8 = g14d_section_numbers(doc, tp8, titles, ch_starts)
            a8, _ = g14a_toc_numbers(doc, titles, ch_starts)
            results["M8-section-number"] = bool(d8)
            print(f"      (M8 G14-D {len(d8)}건 검출 / G14-A는 {len(a8)}건 — 장 축은 못 본다)")
            doc.close()
        else:
            print("      (M8 건너뜀 — toc_levels 1 또는 절 행 없음)")

        # M9 — 도비라 기존 행과 실제로 교차하는 겹침
        work = Path(td) / "m9.pdf"
        shutil.copy(book_dir / "draft" / "book.pdf", work)
        doc = fitz.open(work)
        pg9, victim, vbox = mutate_overlap(doc, ch_starts)
        col9 = collide_scan(doc, style, tokens)
        results["M9-text-overlap"] = pg9 in col9
        print(f"      (M9 도비라 p{pg9} '{victim}' 박스 {vbox} 안에 주입 → "
              f"교차 {len(col9.get(pg9, []))}건)")
        doc.close()

        # M9b — **본문 면** 겹침과 OVERLAP_APPROVED. M9는 도비라(면제가 차단된 면)에만
        # 주입하므로 `collide_exempt` 분기를 한 번도 밟지 않았다(W4 판정 D8). 여기서
        # 세 상태를 한 면에서 순서대로 확인한다: 머리카락 교차 검출 → 승인으로 면제 성립
        # → 상한 초과 겹침을 얹으면 승인이 무효(G11 선행조건 FAIL).
        work = Path(td) / "m9b.pdf"
        shutil.copy(book_dir / "draft" / "book.pdf", work)
        doc = fitz.open(work)
        pgb, recsb = pick_body_page(doc, ch_starts, ch_starts[0])
        assert pgb, "본문 면을 찾지 못했다 — M9b 주입 불가"
        hl_victim = mutate_hairline_overlap(doc, pgb, recsb)
        colb = collide_scan(doc, style, tokens)
        hits_hair = colb.get(pgb, [])
        exempt_hair = collide_exempt_pages(set(), {pgb}, ch_starts, ch_starts[0])
        ok_detect = bool(hits_hair)
        ok_exempt = pgb in exempt_hair                       # 승인이 실제로 면제를 만든다
        ok_bound_hair = all(h["ox"] <= OVERLAP_APPROVE_MAX_OX_PT for h in hits_hair)
        mutate_severe_overlap(doc, pgb, recsb)
        colc = collide_scan(doc, style, tokens)
        over = [h for h in colc.get(pgb, []) if h["ox"] > OVERLAP_APPROVE_MAX_OX_PT]
        results["M9b-body-overlap-approve"] = ok_detect and ok_exempt and ok_bound_hair and bool(over)
        print(f"      (M9b 본문 p{pgb} '{hl_victim}' — 머리카락 교차 {len(hits_hair)}건 "
              f"ox {[h['ox'] for h in hits_hair]} <= 상한 {OVERLAP_APPROVE_MAX_OX_PT}pt: {ok_bound_hair} · "
              f"승인 면제 성립 {ok_exempt} / 중대 겹침 추가 후 상한 초과 {len(over)}건 "
              f"ox {[h['ox'] for h in over][:2]} → G11 선행조건 FAIL)")
        doc.close()

        # M9c — 면제 차감 불변식. 표지가 fullbleed(imgarea 1.0)여도, 도비라에 승인이
        # 찍혀도 그 면들은 면제 집합에 들어갈 수 없다(W4 판정 D2 회귀 고정).
        fc = ch_starts[0]
        ex = collide_exempt_pages({1, 2, fc, fc + 1}, {1, 2, fc, fc + 1}, ch_starts, fc)
        results["M9c-exempt-front-cut"] = (1 not in ex and 2 not in ex
                                           and fc not in ex and (fc + 1) in ex)
        print(f"      (M9c 표지·목차·도비라 전부 fullbleed+승인 입력 → 면제 집합 {sorted(ex)} "
              f"(앞부속 1~{fc - 1}·도비라 {ch_starts[:3]} 차감 확인))")

        # M11 — 앞부속 프레임 이탈 (front_frame_mm 미선언 스타일에서는 성립하지 않는다)
        inj = None
        if tokens.get("front_frame_mm") and ch_starts[0] >= 3:
            work = Path(td) / "m11.pdf"
            shutil.copy(book_dir / "draft" / "book.pdf", work)
            doc = fitz.open(work)
            inj = mutate_front_overflow(doc, tokens, ch_starts[0])
            f11 = fit_scan(doc, tokens, ch_starts[0])
            results["M11-front-frame"] = bool(f11)
            print(f"      (M11 p{inj[0]} 프레임 하단 밖 y={inj[1]}pt 주입 → G3-FIT {len(f11)}건)")
            doc.close()
        if inj is None:
            print("      (M11 건너뜀 — front_frame_mm 미선언 또는 앞부속 목차 면 없음)")

        # M10 — G16-CONTRAST 저대비 토큰. 스타일 팩을 임시 복사본에 복제해 그 사본만
        # 변조한다(저장소 styles/는 절대 변조하지 않는다). enforce:true가 아니면
        # G16-CONTRAST가 WARN까지만 올리므로 이 스타일에서는 성립하지 않는다.
        cc = (tokens.get("contrast_contract") or {})
        if cc.get("enforce") is True:
            style_copy = Path(td) / "style10"
            shutil.copytree(SKILL / "styles" / style, style_copy)
            tokens10, css10 = g16.style_inputs(style, style_dir=style_copy)
            idx10, victim10 = mutate_low_contrast_tokens(style_copy, tokens10, css10)
            # 검사는 방금 되쓴 파일을 다시 읽어서 돈다 — "그 복사본"을 실제로 본다.
            tokens10b, css10b = g16.style_inputs(style, style_dir=style_copy)
            res10 = g16.run(style, tokens10b, css10b, style_dir=style_copy)
            fails10 = g16.fails_of(res10["G16-CONTRAST"])
            results["M10-low-contrast-tokens"] = bool(fails10)
            print(f"      (M10 entries[{idx10}] {victim10['where']} fg={victim10['fg']} "
                  f"(=bg, ratio 1.0) → G16-CONTRAST FAIL {len(fails10)}건)")
        else:
            print(f"      (M10 건너뜀 — {style} contrast_contract.enforce != true)")

        # M12 — G16-SYNC palette_roles 훼손. M10과 같은 임시 사본 원칙.
        style12 = Path(td) / "style12"
        shutil.copytree(SKILL / "styles" / style, style12)
        tok12, css12 = g16.style_inputs(style, style_dir=style12)
        was, now = mutate_palette_roles(style12, tok12)
        tok12b, css12b = g16.style_inputs(style, style_dir=style12)
        f12 = g16.fails_of(g16.run(style, tok12b, css12b, style_dir=style12)["G16-SYNC"])
        results["M12-palette-roles"] = bool(f12)
        print(f"      (M12 palette_roles[0] {was!r} → {now!r} → G16-SYNC FAIL {len(f12)}건)")

        # M17 — G16-SYNC toc_layout 축(목차 문법 계약). M10·M12와 같은 임시 사본 원칙.
        #   ㉠ 허용 밖 스타일 배정(축 ②)  ㉡ 리더 점선 주입(축 ④)  ㉢ 급수 상한 초과(축 ⑤)
        #   ㉣ 카탈로그 밖 이름 주입(축 ①)
        # 넷을 갈라 주입하는 이유: 한 사본에 몰아 넣으면 어느 축이 잡았는지 구별되지 않아
        # "하나가 잡으면 나머지가 죽어 있어도 초록"인 상태를 회귀 자산이 은폐한다.
        ok17 = {}
        s17a = Path(td) / "style17a"
        shutil.copytree(SKILL / "styles" / style, s17a)
        t17a, c17a = g16.style_inputs(style, style_dir=s17a)
        was17, now17 = mutate_toc_layout_name(s17a, t17a, style)
        t17ab, c17ab = g16.style_inputs(style, style_dir=s17a)
        f17a = g16.fails_of(g16.run(style, t17ab, c17ab, style_dir=s17a)["G16-SYNC"])
        ok17["a"] = any("toc_layout" in x["msg"] for x in f17a)
        print(f"      (M17-㉠ toc_layout {was17!r} → {now17!r} → G16-SYNC FAIL {len(f17a)}건)")

        s17b = Path(td) / "style17b"
        shutil.copytree(SKILL / "styles" / style, s17b)
        t17b, _ = g16.style_inputs(style, style_dir=s17b)
        file17, inj17 = mutate_toc_leader(s17b, style, t17b)
        t17bb, c17bb = g16.style_inputs(style, style_dir=s17b)
        f17b = g16.fails_of(g16.run(style, t17bb, c17bb, style_dir=s17b)["G16-SYNC"])
        ok17["b"] = any("점선 리더" in x["msg"] for x in f17b)
        print(f"      (M17-㉡ {file17}에 `{inj17}` 주입 → G16-SYNC FAIL {len(f17b)}건)")

        s17c = Path(td) / "style17c"
        shutil.copytree(SKILL / "styles" / style, s17c)
        t17c, _ = g16.style_inputs(style, style_dir=s17c)
        over17 = mutate_toc_size(s17c, style, t17c)
        if over17 is None:
            ok17["c"] = True
            print(f"      (M17-㉢ 건너뜀 — {style} 레이아웃의 size_cap_pt가 None(급수 변수 주입))")
        else:
            t17cb, c17cb = g16.style_inputs(style, style_dir=s17c)
            f17c = g16.fails_of(g16.run(style, t17cb, c17cb, style_dir=s17c)["G16-SYNC"])
            ok17["c"] = any("최대 급수" in x["msg"] for x in f17c)
            print(f"      (M17-㉢ 목차 급수 {over17}pt 주입 → G16-SYNC FAIL {len(f17c)}건)")

        # ㉣ 카탈로그 밖 이름(축 ①). ㉠과 다른 축이다 — ㉠은 **실존** 레이아웃을 구현 없는
        # 팩이 빌려 쓰는 남용(축 ②)이고, ㉣은 카탈로그가 모르는 어휘라 축 ②~⑤가 아예
        # 시작되지 못하는 경로다. 축 ①이 죽으면 오타 하나로 전 축이 조용히 꺼진다.
        s17d = Path(td) / "style17d"
        shutil.copytree(SKILL / "styles" / style, s17d)
        t17d, _ = g16.style_inputs(style, style_dir=s17d)
        bogus = "mut-nonexistent-layout"
        assert bogus not in g16.TOC_LAYOUTS
        (s17d / "tokens.json").write_text(
            json.dumps(dict(t17d, toc_layout=bogus), ensure_ascii=False, indent=2),
            encoding="utf-8")
        t17db, c17db = g16.style_inputs(style, style_dir=s17d)
        f17d = g16.fails_of(g16.run(style, t17db, c17db, style_dir=s17d)["G16-SYNC"])
        ok17["d"] = any("카탈로그 밖" in x["msg"] for x in f17d)
        print(f"      (M17-㉣ toc_layout {bogus!r} 주입 → G16-SYNC FAIL {len(f17d)}건)")

        # ㉩~㉬ — 적대검증 v-s2가 실측한 리터럴 매칭 우회 8건(A~D)의 축별 회귀 고정.
        # 축마다 대표 1건: ㉩=A(toc_levels 타입) ㉪=B(리더 관용구 dashed) ㉫=C(급수 var
        # 간접) ㉬=D(typst 헬퍼 간접 리더). ㉠~㉣과 같은 원칙 — 축마다 다른 임시 사본.
        s17i = Path(td) / "style17i"
        shutil.copytree(SKILL / "styles" / style, s17i,
                        ignore=shutil.ignore_patterns("__pycache__"))
        t17i, _ = g16.style_inputs(style, style_dir=s17i)
        (s17i / "tokens.json").write_text(
            json.dumps(dict(t17i, toc_levels="2"), ensure_ascii=False, indent=2),
            encoding="utf-8")
        t17ib, c17ib = g16.style_inputs(style, style_dir=s17i)
        f17i = g16.fails_of(g16.run(style, t17ib, c17ib, style_dir=s17i)["G16-SYNC"])
        ok17["i"] = any("toc_levels" in x["msg"] and "정수" in x["msg"] for x in f17i)
        print(f"      (M17-㉩ toc_levels '2'(str) 주입 → G16-SYNC FAIL {len(f17i)}건)")

        if tokens.get("engine") == "html":
            s17j = Path(td) / "style17j"
            shutil.copytree(SKILL / "styles" / style, s17j,
                            ignore=shutil.ignore_patterns("__pycache__"))
            p = s17j / "theme.css"
            p.write_text(p.read_text(encoding="utf-8")
                         + "\n.toc-mut-row { border-bottom: 0.4pt dashed #999; }\n",
                         encoding="utf-8")
            t17jb, c17jb = g16.style_inputs(style, style_dir=s17j)
            f17j = g16.fails_of(g16.run(style, t17jb, c17jb, style_dir=s17j)["G16-SYNC"])
            ok17["j"] = any("점선 리더" in x["msg"] for x in f17j)
            print(f"      (M17-㉪ theme.css에 dashed 리더 주입 → G16-SYNC FAIL {len(f17j)}건)")

            s17k = Path(td) / "style17k"
            shutil.copytree(SKILL / "styles" / style, s17k,
                            ignore=shutil.ignore_patterns("__pycache__"))
            p = s17k / "theme.css"
            p.write_text(p.read_text(encoding="utf-8")
                         + "\n:root { --bf-mut-size: 60pt; }\n"
                           ".toc-mut { font-size: var(--bf-mut-size); }\n",
                         encoding="utf-8")
            t17kb, c17kb = g16.style_inputs(style, style_dir=s17k)
            f17k = g16.fails_of(g16.run(style, t17kb, c17kb, style_dir=s17k)["G16-SYNC"])
            ok17["k"] = any("최대 급수" in x["msg"] for x in f17k)
            print(f"      (M17-㉫ var() 간접 60pt 주입 → G16-SYNC FAIL {len(f17k)}건)")
        else:
            # typst 팩 전용 — 헬퍼 간접 리더(정의는 파일 상단, 목차 영역엔 이름 호출만).
            # 상한이 None인 business도 리더 축은 성립하지만 leader=True 선언 팩(practical)
            # 은 주입이 선언과 일치해 버리므로 leader=False 선언 팩에서만 성립한다.
            spec17 = g16.TOC_LAYOUTS.get(tokens.get("toc_layout")) or {}
            if spec17.get("leader") is False:
                s17l = Path(td) / "style17l"
                shutil.copytree(SKILL / "styles" / style, s17l,
                                ignore=shutil.ignore_patterns("__pycache__"))
                p = s17l / "theme.typ"
                t_ = "#let bf-mut-dots(pad) = box(width: 1fr, repeat[.])\n\n" \
                     + p.read_text(encoding="utf-8")
                t_ = t_.replace("  if toc {\n", "  if toc {\n    bf-mut-dots(0pt)\n", 1)
                assert "bf-mut-dots(0pt)" in t_, f"{style}: `if toc {{` 앵커 없음 — ㉬ 주입 불가"
                p.write_text(t_, encoding="utf-8")
                t17lb, c17lb = g16.style_inputs(style, style_dir=s17l)
                f17l = g16.fails_of(g16.run(style, t17lb, c17lb, style_dir=s17l)["G16-SYNC"])
                ok17["l"] = any("점선 리더" in x["msg"] for x in f17l)
                print(f"      (M17-㉬ typst 헬퍼 간접 리더 주입 → G16-SYNC FAIL {len(f17l)}건)")
            else:
                print(f"      (M17-㉬ 건너뜀 — {style}은 leader=True 선언(주입이 선언과 일치))")
        results["M17-toc-layout"] = all(ok17.values())

        # M17 오버레이 축(W6 S6) — 대안 레이아웃 실물(toc-<이름>.css)과 용량 계약
        # (toc_capacity_alt)의 감도. 오버레이를 보유한 팩(현재 magazine)만 성립한다.
        # ㉠~㉣과 같은 원칙: 축마다 다른 임시 사본, 저장소 styles/ 무변조.
        #   ㉤ 오버레이에 점선 리더 주입          → 축 ⑨ FAIL
        #   ㉥ 오버레이 급수를 상한 +6pt로 주입    → 축 ⑩ FAIL
        #   ㉦ 오버레이 파일명을 카탈로그 밖으로   → 축 ⑥ FAIL + 용량 계약 고아 FAIL
        #   ㉧ toc_capacity_alt 항목 삭제         → 축 ⑪ FAIL
        overlays = sorted((SKILL / "styles" / style).glob("toc-*.css"))
        if not overlays:
            print(f"      (M17 오버레이 축 건너뜀 — {style}에 toc-*.css 오버레이 없음)")
        else:
            oname = overlays[0].stem[len("toc-"):]
            okov = {}

            def ov_fails(tag, mutate):
                sdir = Path(td) / f"style17{tag}"
                shutil.copytree(SKILL / "styles" / style, sdir)
                mutate(sdir)
                t_, c_ = g16.style_inputs(style, style_dir=sdir)
                return g16.fails_of(g16.run(style, t_, c_, style_dir=sdir)["G16-SYNC"])

            def inj_leader(sdir):
                p = sdir / overlays[0].name
                p.write_text(p.read_text(encoding="utf-8")
                             + "\n.toc-bn .toc-leader { border-bottom: 0.4pt dotted #999; }\n",
                             encoding="utf-8")

            f_e = ov_fails("e", inj_leader)
            okov["e"] = any("점선 리더" in x["msg"] for x in f_e)
            print(f"      (M17-㉤ {overlays[0].name}에 dotted 주입 → G16-SYNC FAIL {len(f_e)}건)")

            cap_ov = g16.toc_size_cap(g16.TOC_LAYOUTS[oname], style)
            over_ov = (cap_ov or 0) + 6.0

            def inj_size(sdir):
                p = sdir / overlays[0].name
                p.write_text(p.read_text(encoding="utf-8")
                             + "\n.toc-bn .toc-title { font-size: %.1fpt; }\n" % over_ov,
                             encoding="utf-8")

            f_f = ov_fails("f", inj_size)
            okov["f"] = any("최대 급수" in x["msg"] for x in f_f)
            print(f"      (M17-㉥ 오버레이 급수 {over_ov}pt 주입 → G16-SYNC FAIL {len(f_f)}건)")

            def rename_ov(sdir):
                (sdir / overlays[0].name).rename(sdir / "toc-mut-nonexistent-layout.css")

            f_g = ov_fails("g", rename_ov)
            okov["g"] = (any("카탈로그 밖" in x["msg"] for x in f_g)
                         and any("toc_capacity_alt" in x["msg"] for x in f_g))
            print(f"      (M17-㉦ 오버레이 파일명 카탈로그 밖 개명 → G16-SYNC FAIL {len(f_g)}건)")

            def drop_alt(sdir):
                tk = json.loads((sdir / "tokens.json").read_text(encoding="utf-8"))
                tk.get("toc_capacity_alt", {}).pop(oname, None)
                (sdir / "tokens.json").write_text(
                    json.dumps(tk, ensure_ascii=False, indent=2), encoding="utf-8")

            f_h = ov_fails("h", drop_alt)
            okov["h"] = any("toc_capacity_alt" in x["msg"] for x in f_h)
            print(f"      (M17-㉧ toc_capacity_alt[{oname!r}] 삭제 → G16-SYNC FAIL {len(f_h)}건)")
            results["M17-toc-overlay"] = all(okov.values())

        # M-ORIGIN — fg/tb 마커 앵커 소실(포함 단조 사후조건의 감도). html 엔진 전용 —
        # typst 트랙에는 pgmark 마커 계약 자체가 없다. 옵트인(toc_lists)·앵커 제거 전부
        # **임시 스타일 사본**에만 주입한다(저장소 styles/ 절대 변조 금지).
        if tokens.get("engine") == "html":
            so = Path(td) / "style-origin"
            shutil.copytree(SKILL / "styles" / style, so,
                            ignore=shutil.ignore_patterns("__pycache__"))
            tko = json.loads((so / "tokens.json").read_text(encoding="utf-8"))
            (so / "tokens.json").write_text(
                json.dumps(dict(tko, toc_lists=["figures", "tables"]),
                           ensure_ascii=False, indent=2), encoding="utf-8")
            if "<!--BF:TOCPAGE" not in (so / "theme.html").read_text(encoding="utf-8"):
                # 단면 목차 스타일 — S5부터 toc_lists 옵트인은 die가 계약이다(차례 별면은
                # BF:TOCPAGE 복제 배관에만 실리므로 조용한 발행 0은 선언 오타와 구별
                # 불가). 앵커 감도(M-ORIGIN 본편)는 빌드가 그 앞에서 서므로 이 스타일에선
                # 성립하지 않는다 — 대신 가드 die 자체를 회귀 자산으로 고정한다.
                bd_g = Path(td) / "origin-guard"
                book_g, outline_g = origin_probe_book(bd_g)
                err_g = run_origin_build(bd_g, book_g, outline_g, so)
                ok_g = bool(err_g) and "다면 목차" in (err_g or "")
                results["M-LISTPG-single-toc-guard"] = ok_g
                print(f"      (M-ORIGIN 본편 건너뜀 — {style}은 단면 목차(BF:TOCPAGE 부재). "
                      f"M-LISTPG 가드: toc_lists 옵트인 die "
                      f"{'발화' if ok_g else '불발'} — {(err_g or '(없음)')[:80]})")
            else:
                # ㉠ 대조군: 앵커 온전 → 빌드 성공 + 발행 2·2 + 최종 PDF에 마커 잔존 0
                bd_ok = Path(td) / "origin-ok"
                book_o, outline_o = origin_probe_book(bd_ok)
                err_ok = run_origin_build(bd_ok, book_o, outline_o, so)
                plan_o, leak = {}, None
                if err_ok is None:
                    plan_o = json.loads((bd_ok / "typeset" / "tocplan.json")
                                        .read_text(encoding="utf-8"))
                    dko = fitz.open(bd_ok / "draft" / "book.pdf")
                    leak = [p + 1 for p in range(dko.page_count) if "@@" in dko[p].get_text()]
                    dko.close()
                # ㉡ 같은 옵트인 사본에서 mk-anchor 앵커 규칙만 비운다 — .pgmark가 문서
                # 원점(1면)으로 떨어져 종별 집합 일치(전수 회수)는 그대로 충족되는 상태
                sm = Path(td) / "style-origin-mut"
                shutil.copytree(so, sm)
                css_o = (sm / "theme.css").read_text(encoding="utf-8")
                anchor_rule = ".mk-anchor { position: relative; }"
                n_anchor = css_o.count(anchor_rule)
                assert n_anchor == 1, \
                    f"{style} theme.css에서 mk-anchor 앵커 규칙 미발견({n_anchor}) — M-ORIGIN 주입 불가"
                css_o = css_o.replace(anchor_rule, ".mk-anchor { }")
                (sm / "theme.css").write_text(css_o, encoding="utf-8")
                bd_mut = Path(td) / "origin-mut"
                book_m, outline_m = origin_probe_book(bd_mut)
                err_mut = run_origin_build(bd_mut, book_m, outline_m, sm)
                ok_ctl = (err_ok is None and plan_o.get("fig_markers") == 2
                          and plan_o.get("tbl_markers") == 2 and leak == [])
                ok_mut = bool(err_mut) and "앵커 소실" in (err_mut or "")
                results["M-ORIGIN-marker-anchor"] = ok_ctl and ok_mut
                print(f"      (M-ORIGIN 대조군: 빌드 {'OK' if err_ok is None else 'FAIL'} · "
                      f"발행 fg {plan_o.get('fig_markers')}/tb {plan_o.get('tbl_markers')} · "
                      f"최종 PDF 마커 잔존 {leak} → {ok_ctl} / 앵커 제거본: "
                      f"die {'발화' if ok_mut else '불발'} — {(err_mut or '(없음)')[:96]})")

                # M-LISTPG — 차례 쪽번호 오염. 대조군 PDF에서 ㉢G14-E 0건(오탐 없음)을
                # 확인하고, 차례 항목 하나의 인쇄 쪽번호만 +3으로 오염 → ㉣G14-E 발화.
                # 빌더 사후조건은 pass1 회수를 보므로 이 오염을 원리적으로 못 본다 —
                # 지면 재추출 대조(G14-E)가 유일한 방어선임을 회귀 자산으로 고정한다.
                ok_e = False
                if ok_ctl:
                    dke = fitz.open(bd_ok / "draft" / "book.pdf")
                    ch_o = sorted({pg for lv, _t, pg in dke.get_toc() if lv == 1})
                    e0p, _w0, _pr0, e0n = g14e_list_numbers(
                        dke, ch_o, ["figures", "tables"], plan_o)
                    inj = mutate_list_number(dke, ch_o[0]) if ch_o else None
                    e1p, _w1, _pr1, _n1 = g14e_list_numbers(
                        dke, ch_o, ["figures", "tables"], plan_o)
                    dke.close()
                    ok_e = (not e0p) and e0n == 4 and bool(inj) and bool(e1p)
                    print(f"      (M-LISTPG 대조군 G14-E {len(e0p)}건/{e0n}쌍 → "
                          f"'{inj[0] if inj else '?'}' {inj[1] if inj else '?'}→"
                          f"{inj[1] + 3 if inj else '?'} 주입 → G14-E {len(e1p)}건 발화: "
                          f"{(e1p[0][:76] if e1p else '(없음)')})")
                else:
                    print("      (M-LISTPG 건너뜀 — M-ORIGIN 대조군 실패)")
                results["M-LISTPG-list-numbers"] = ok_e

                # M-LISTPG-드리프트 — 균일 앵커 드리프트 주입(적대검증 s4-verdict ①
                # P-HOLE 경로 그대로). `.mk-anchor .pgmark{top:-257mm}`(판면 1면 높이)는
                # 전 fg/tb 마커를 정확히 1면씩 위로 밀어, 장내에 머무는 한 포함 단조
                # 사후조건(장 구간·단조 비감소)을 **통과한 채** 회수 면을 어긋낸다 —
                # 사후조건만으로는 쪽번호 정확성이 보증되지 않음이 실증된 구멍이다.
                # 고정하는 성질: 이 상태가 조용히 인쇄에 도달하지 않는다 — 드리프트가
                # 장 경계를 넘으면 빌더 포함 단조가 die하고, 장내에 머물면 G14-E(인쇄
                # 쪽번호 vs 캡션 실면, 양쪽 최종 PDF 독립 추출)가 대조한 전 쌍을
                # FAIL로 낸다. "rc 0 + G14-E 침묵"만이 이 뮤테이션의 실패다.
                sdr = Path(td) / "style-origin-drift"
                shutil.copytree(so, sdr)
                with open(sdr / "theme.css", "a", encoding="utf-8") as fh:
                    fh.write("\n.mk-anchor .pgmark { top: -257mm; }\n")
                bd_dr = Path(td) / "origin-drift"
                book_d, outline_d = origin_probe_book(bd_dr)
                err_dr = run_origin_build(bd_dr, book_d, outline_d, sdr)
                if err_dr is not None:
                    ok_dr = ("구간" in err_dr) or ("단조" in err_dr)
                    print(f"      (M-LISTPG-드리프트: 빌더 die 발화(경계 초과 경로) — "
                          f"{err_dr[:88]})")
                else:
                    ddr = fitz.open(bd_dr / "draft" / "book.pdf")
                    ch_d = sorted({pg for lv, _t, pg in ddr.get_toc() if lv == 1})
                    plan_d = json.loads((bd_dr / "typeset" / "tocplan.json")
                                        .read_text(encoding="utf-8"))
                    edp, _wd, prd, ndr = g14e_list_numbers(
                        ddr, ch_d, ["figures", "tables"], plan_d)
                    ddr.close()
                    mism = [p for p in prd if p["printed"] != p["expected"]]
                    ok_dr = bool(edp) and ndr >= 1 and len(mism) == ndr
                    print(f"      (M-LISTPG-드리프트: rc 0(장내 드리프트) → G14-E "
                          f"{len(edp)}건 발화, 대조 {ndr}쌍 전부 불일치 {len(mism) == ndr} — "
                          f"{(edp[0][:70] if edp else '(없음)')})")
                results["M-LISTPG-uniform-drift"] = ok_dr
        else:
            print("      (M-ORIGIN·M-LISTPG 건너뜀 — typst 엔진(pgmark 마커 계약 없음))")

        # M13 — G16-BRAND. brand는 book.json 위치(=FAIL 강도)로 주입한다.
        bad_brand = violating_brand(tokens, g16.style_inputs(style)[1])
        if bad_brand:
            tok13, css13 = g16.style_inputs(style)
            f13 = g16.fails_of(g16.run(style, tok13, css13, brand=bad_brand)["G16-BRAND"])
            results["M13-violating-brand"] = bool(f13)
            print(f"      (M13 book.json brand={bad_brand} → G16-BRAND FAIL {len(f13)}건: "
                  f"{f13[0]['msg'][:76] if f13 else ''})")
        else:
            print("      (M13 건너뜀 — 고정 동반색이 없어 hue 정합 축이 성립하지 않음)")

        # M14 — 린터 배선. pt만 위조하고 색은 그대로 두어 축②(PT_UNATTAINABLE)를 겨눈다.
        # 두 가지를 함께 어서션한다: ㉠린터가 위조를 잡는가 ㉡그 코드가 qc_gate가 fails로
        # 올리는 집합에 실재하는가(배선 — 린터가 잡아도 아무도 부르지 않으면 무효였다).
        html14 = book_dir / "typeset" / "book-final.html"
        if html14.exists():
            style14 = Path(td) / "style14"
            shutil.copytree(SKILL / "styles" / style, style14)
            tok14, css14 = g16.style_inputs(style, style_dir=style14)
            idx14, old_pt, victim14 = mutate_contract_pt(style14, tok14, css14)
            spec = importlib.util.spec_from_file_location(
                "bf_lint_contrast", SKILL / "tests" / "lint_contrast.py")
            lint = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lint)
            lint._VIRT_CACHE.clear()
            r14 = lint.lint_book(book_dir, style_dir_override=style14)
            codes14 = {x["code"] for x in r14["findings"] if x["level"] == "FAIL"}
            hard14 = codes14 & LINT_HARD_CODES
            results["M14-linter-pt-forgery"] = ("PT_UNATTAINABLE" in codes14
                                                and "PT_UNATTAINABLE" in LINT_HARD_CODES
                                                and bool(hard14))
            print(f"      (M14 entries[{idx14}] {victim14.get('where', '?')[:30]} "
                  f"pt {old_pt} → 13.7 → 린터 FAIL 코드 {sorted(codes14)} · "
                  f"qc_gate가 fails로 올리는 코드 {sorted(hard14)})")
        else:
            print("      (M14 건너뜀 — typeset/book-final.html 부재(typst 엔진))")

        # M15 — 라벨 밴드 상한. 5단계에 **WARN으로 출생**해 8단계에서 스타일별 데이터
        # 스위치(`diagram.labelBand.enforce`)로 승격됐다. 그래서 이 축은 이제 강도가
        # **둘**이고, 어느 쪽도 검증 없이 두면 안 된다:
        #   ㉠ enforce:false → 위반이 WARN이고 exit 0 (릴리스를 세우지 않는다 = 리스크 1 방어)
        #   ㉡ enforce:true  → 같은 위반이 그 도해의 fail() (승격이 실제로 문다)
        #   ㉢ enforce:true  → 합법 도해는 그대로 통과 (승격이 오탐을 만들지 않는다)
        #   ㉣ enforce가 bool이 아니면 malformed FAIL (문자열 "false"가 truthy로 읽히는 구멍)
        #   ㉤ enforce:true인데 검사가 꺼지면(body_pt 미선언) FAIL (조용한 무력화 차단)
        # 저장소 styles/의 현재 값에 의존하면 승격 상태가 바뀔 때마다 이 뮤테이션의
        # 의미가 흔들린다 → **임시 스타일 사본 + `--style-dir`**로 두 분기를 직접 만든다
        # (M10·M12·M14가 g16에 대해 쓰는 것과 같은 원칙: 저장소 styles/는 절대 변조하지 않는다).
        dgm = tokens.get("diagram") or {}
        if not (isinstance(dgm.get("labelBand"), dict) and tokens.get("body_pt")
                and (dgm.get("widths") or {}).get("full") and dgm.get("palette")):
            print("      (M15 건너뜀 — 이 스타일에 diagram.labelBand/body_pt/widths.full 미선언)")
        else:
            def band_style(tag, enforce, drop_body_pt=False, mutate=None):
                """스타일 팩 임시 사본에 enforce를 강제로 심는다. (dir, tokens) 반환.

                mutate: tokens dict를 직접 손대는 콜백(키 삭제·극대값·폭 위조용).
                """
                sd = Path(td) / f"m15-style-{tag}"
                shutil.copytree(SKILL / "styles" / style, sd)
                tk = json.loads((sd / "tokens.json").read_text(encoding="utf-8"))
                tk["diagram"]["labelBand"] = dict(tk["diagram"]["labelBand"], enforce=enforce)
                if drop_body_pt:
                    tk.pop("body_pt", None)
                if mutate:
                    mutate(tk)
                (sd / "tokens.json").write_text(json.dumps(tk, ensure_ascii=False, indent=2),
                                                encoding="utf-8")
                return sd, tk

            def band_run(tag, ratio_of_cap, style_dir):
                bd = Path(td) / f"m15-{tag}"
                spec_ = band_probe_book(bd, style, tokens, ratio_of_cap)
                rc_, out_ = run_render_diagrams(bd, style, style_dir=style_dir)
                mp = bd / "assets" / "fig-01.metrics.json"
                met = json.loads(mp.read_text(encoding="utf-8")) if mp.exists() else None
                return spec_, rc_, out_, met

            sd_off, _ = band_style("off", False)
            sd_on, _ = band_style("on", True)
            sd_bad, _ = band_style("bad", "false")           # 문자열 — malformed
            sd_off2, _ = band_style("nobody", True, drop_body_pt=True)
            # ㉥키 통삭제 ㉦극대값 ㉧폭 위조 — 전부 "판정을 무력화하는 선언"이다
            sd_del, _ = band_style("delband", True, mutate=lambda t: t["diagram"].pop("labelBand"))
            sd_999, _ = band_style("ratio999", True,
                                   mutate=lambda t: t["diagram"].update(
                                       labelBand={"maxRatio": 999, "enforce": True}))
            fake_w = max(tokens["trim_mm"][0], dgm["widths"]["full"]) * 3
            sd_wfake, _ = band_style("widthfake", True,
                                     mutate=lambda t: t["diagram"]["widths"].update(twothirds=fake_w))

            _, rc_w, out_w, met_w = band_run("warn", 1.8, sd_off)     # ㉠
            _, rc_h, out_h, met_h = band_run("hard", 1.8, sd_on)      # ㉡
            _, rc_c, out_c, met_c = band_run("control", 0.9, sd_on)   # ㉢
            _, rc_m, out_m, _ = band_run("malformed", 0.9, sd_bad)    # ㉣
            _, rc_o, out_o, _ = band_run("off-axis", 0.9, sd_off2)    # ㉤
            _, rc_d, out_d, _ = band_run("delband", 0.9, sd_del)      # ㉥
            _, rc_9, out_9, _ = band_run("ratio999", 1.8, sd_999)     # ㉦
            _, rc_f, out_f, _ = band_run("widthfake", 0.9, sd_wfake)  # ㉧(렌더 이중 방어)
            # ㉧의 **정본 판정**은 렌더 전 정적 게이트다 — G16-SYNC를 직접 돌려 어서션한다.
            g16_wfake = [x for fs in g16.run(style, json.loads(
                (sd_wfake / "tokens.json").read_text(encoding="utf-8")),
                (sd_wfake / "theme.css").read_text(encoding="utf-8")
                if (sd_wfake / "theme.css").exists() else None,
                None, style_dir=str(sd_wfake)).values() for x in fs if x["level"] == "FAIL"]
            # ㉨ tspan CSS 급수 — 승격 스타일(enforce:true)에서 밴드 HARD로 잡혀야 한다.
            bd_ts = Path(td) / "m15-tspan"
            spec_ts = tspan_band_probe_book(bd_ts, style, tokens)
            rc_t, out_t = run_render_diagrams(bd_ts, style, style_dir=sd_on)
            mp_ts = bd_ts / "assets" / "fig-01.metrics.json"
            met_t = json.loads(mp_ts.read_text(encoding="utf-8")) if mp_ts.exists() else None

            if met_w and met_h and met_c:
                # ㉠ WARN 강도: 검출되고, metrics가 강도를 WARN이라 말하고, **exit 0**이다.
                ok_warn = (rc_w == 0 and "상한 초과" in out_w
                           and met_w["band"]["verdict"] == "violation"
                           and met_w["band"]["level"] == "WARN"
                           and met_w["band"].get("enforce") is False
                           and met_w["maxPt"] > met_w["capPt"]
                           and met_w["minPt"] >= met_w["minFontPt"])   # 하한 HARD를 안 밟았다
                # ㉡ HARD 강도: **같은 표본**이 exit != 0이고 사유가 밴드 상한이라고 말한다.
                ok_hard = (rc_h != 0 and "DIAGRAM FAIL" in out_h and "라벨 밴드 상한" in out_h
                           and "labelBand.enforce=true" in out_h
                           and met_h["band"]["verdict"] == "violation"
                           and met_h["band"]["level"] == "FAIL"
                           and met_h["band"].get("enforce") is True
                           and met_h["minPt"] >= met_h["minFontPt"])
                # ㉢ 특이도: 승격 상태에서도 합법 도해는 통과한다(오탐 0).
                ok_ctl = (rc_c == 0 and "상한 초과" not in out_c
                          and met_c["band"]["verdict"] == "ok"
                          and met_c["maxPt"] <= met_c["capPt"])
                # ㉣ 형식 계약: 문자열 "false"는 truthy로 읽히면 안 된다 — 실행 자체를 막는다.
                ok_mal = rc_m != 0 and "enforce" in out_m and "bool" in out_m.lower()
                # ㉤ 승격 스타일에서 검사가 꺼지면 그 자체가 반려다.
                ok_off = rc_o != 0 and "검사 꺼짐" in out_o
                # ㉥ 키 통삭제 = malformed(부재도 위반) — WARN 뒤 통과가 아니라 실행 중단.
                ok_del = rc_d != 0 and "labelBand 부재" in out_d
                # ㉦ 극대값 = 타당성 대역 밖 malformed — 상한 검사와 급수 주입을 동시에 끈다.
                ok_999 = rc_9 != 0 and "타당성 대역" in out_9 and "999" in out_9
                # ㉧ 폭 위조 — 정본은 G16-SYNC(렌더 전), 렌더는 이중 방어.
                ok_wf = (any("widths.twothirds" in x["msg"] for x in g16_wfake)
                         and rc_f != 0 and "widths.twothirds" in out_f)
                # ㉨ tspan CSS 급수 — 밴드 HARD + **metrics 두 축이 같은 글자에 같은 pt**를
                #    말한다(sizesPt 최댓값 == labelPaint 최댓값). 이중 진리가 없어졌다는 증거.
                if met_t:
                    lp_pts = [r["pt"] for r in (met_t.get("labelPaint") or {}).get("labels", [])
                              if isinstance(r.get("pt"), (int, float))]
                    ok_tspan = (rc_t != 0 and "라벨 밴드 상한" in out_t
                                and met_t["band"]["verdict"] == "violation"
                                and met_t["maxPt"] > met_t["capPt"]
                                and bool(lp_pts) and abs(max(lp_pts) - met_t["maxPt"]) < 0.05)
                else:
                    ok_tspan = False
                results["M15-label-band"] = bool(ok_warn and ok_hard and ok_ctl
                                                 and ok_mal and ok_off
                                                 and ok_del and ok_999 and ok_wf and ok_tspan)
                print(f"      (M15 위반본 max {met_w['maxPt']}pt = 본문 {met_w['bodyPt']}pt × "
                      f"{met_w['ratio']} > 상한 {met_w['maxRatio']}×({met_w['capPt']}pt) "
                      f"· 최소 {met_w['minPt']}pt ≥ 하한 {met_w['minFontPt']}pt → "
                      f"enforce:false exit {rc_w}/WARN {ok_warn} · enforce:true exit {rc_h}/HARD "
                      f"{ok_hard} · 대조군(enforce:true) max {met_c['maxPt']}pt ≤ {met_c['capPt']}pt "
                      f"exit {rc_c} {ok_ctl} · enforce=\"false\"(문자열) exit {rc_m} {ok_mal} · "
                      f"enforce:true+body_pt 미선언 exit {rc_o} {ok_off} · "
                      f"labelBand 키 삭제 exit {rc_d} {ok_del} · maxRatio 999 exit {rc_9} {ok_999} · "
                      f"widths.twothirds {fake_w}mm 위조 → G16-SYNC FAIL {len(g16_wfake)}건/렌더 exit "
                      f"{rc_f} {ok_wf} · tspan CSS 급수 exit {rc_t} "
                      f"max {(met_t or {}).get('maxPt')}pt {ok_tspan})")
            else:
                results["M15-label-band"] = False
                head = (out_w or out_h or out_c).strip().splitlines()[-1:] or [""]
                print(f"      (M15 실행 실패 — rc {rc_w}/{rc_h}/{rc_c}/{rc_m}/{rc_o}, "
                      f"metrics {bool(met_w)}/{bool(met_h)}/{bool(met_c)}: {head[0][:120]})")

        # M16 — 도해 라벨 **역할·대비 HARD**(7단계). 두 결함을 갈라서 주입하고 대조군까지
        # 셋을 한 묶음으로 돌린다. 밴드(M15)와 달리 이 축은 **HARD여야** 정상이므로
        # rc!=0을 어서션한다 — 강도가 WARN으로 미끄러지면 그것이 회귀다.
        if not (isinstance(dgm.get("palette_roles"), list) and dgm.get("palette")
                and tokens.get("body_pt") and (dgm.get("widths") or {}).get("full")
                and dgm.get("minFontPt")):
            print("      (M16 건너뜀 — 이 스타일에 diagram.palette_roles/widths.full 미선언)")
        else:
            def paint_run(tag, mode):
                bd = Path(td) / f"m16-{tag}"
                spec_ = paint_probe_book(bd, style, tokens, mode)
                if spec_ is None:
                    return None, None, None, None
                rc_, out_ = run_render_diagrams(bd, style)
                mp = bd / "assets" / "fig-01.metrics.json"
                met = json.loads(mp.read_text(encoding="utf-8")) if mp.exists() else None
                return spec_, rc_, out_, met

            spec_r, rc_r, out_r, _ = paint_run("role", "role")
            spec_x, rc_x, out_x, _ = paint_run("contrast", "contrast")
            spec_c, rc_c, out_c, met_c = paint_run("control", "control")
            # W5 재작업 — 배경 산출 3결함(K4)을 갈라서 겨눈다 + 그라데이션 대조군.
            spec_g, rc_g, out_g, _ = paint_run("gradient", "gradient")
            spec_go, rc_go, out_go, met_go = paint_run("gradient-ok", "gradient-ok")
            spec_s, rc_s, out_s, _ = paint_run("stroke", "stroke")
            spec_e, rc_e, out_e, _ = paint_run("edge", "edge")
            if spec_c is None or (spec_r is None and spec_x is None):
                print("      (M16 건너뜀 — 이 팔레트에서 역할/대비 결함 색쌍을 만들 수 없다)")
            else:
                # ㉠역할 축: 팔레트 밖이 아니라 **역할이 label이 아닌** 색을 글자로 → HARD
                # (대비는 ≥4.5로 깔아두었으므로 반려 사유가 역할 하나임이 메시지로 증명된다)
                ok_r = spec_r is None or (rc_r != 0 and "palette_roles" in out_r
                                          and "위반 1건" in out_r
                                          and spec_r["fg"].lower() in out_r.lower())
                # ㉡대비 축: 역할은 합법인데 실배경 대비가 하한 미달 → HARD
                ok_x = spec_x is None or (rc_x != 0 and "대비" in out_x
                                          and spec_x["bg"].lower() in out_x.lower())
                # ㉢대조군: 오탐 0 + 검사가 실제로 돌았다는 증거(labelPaint.checked ≥ 1)
                lp = (met_c or {}).get("labelPaint") or {}
                ok_c = (rc_c == 0 and lp.get("checked", 0) >= 1
                        and lp.get("roleViolations") == 0 and lp.get("contrastViolations") == 0)
                # ㉣그라데이션 배경 — stop을 해석하지 않으면 "판면 백색 위"로 통과한다
                ok_g = spec_g is None or (rc_g != 0 and "대비" in out_g
                                          and spec_g["bg"].lower() in out_g.lower())
                # ㉣' 대조군 — 그라데이션이라고 통째로 반려하지 않는다(오탐 0)
                lpg = (met_go or {}).get("labelPaint") or {}
                ok_go = spec_go is None or (rc_go == 0 and lpg.get("checked", 0) >= 1
                                            and lpg.get("contrastViolations") == 0)
                # ㉤stroke 면 — fill:none 도형이 후보에서 탈락하면 백색 위로 통과한다
                ok_s = spec_s is None or (rc_s != 0 and "대비" in out_s
                                          and spec_s["bg"].lower() in out_s.lower())
                # ㉥경계 걸침 — **중심 아닌 표본이 최악**이었다는 사실까지 어서션한다
                #    (중심점 1표본이었다면 백색 위로 통과했을 표본이다)
                ok_e = spec_e is None or (rc_e != 0 and "대비" in out_e
                                          and spec_e["bg"].lower() in out_e.lower()
                                          and "표본이 최악" in out_e)
                results["M16-label-paint"] = bool(ok_r and ok_x and ok_c
                                                  and ok_g and ok_go and ok_s and ok_e)
                print(f"      (M16-K4 그라데이션 exit {rc_g} {ok_g} / 그라데이션 대조군 exit "
                      f"{rc_go} 위반 {lpg.get('contrastViolations')} {ok_go} / stroke 면 exit "
                      f"{rc_s} {ok_s} / 경계 걸침 exit {rc_e} {ok_e})")
                print(f"      (M16 역할본 fg {spec_r['fg']}(role={spec_r['role']}) on {spec_r['bg']} "
                      f"대비 {spec_r['ratio']:.2f}(≥4.5, 역할만 결함) → exit {rc_r} 검출 {ok_r} / "
                      f"대비본 fg {spec_x['fg']}(role=label) on {spec_x['bg']} 대비 "
                      f"{spec_x['ratio']:.2f} < 4.5 → exit {rc_x} 검출 {ok_x} / "
                      f"대조군 {spec_c['fg']} on {spec_c['bg']} 대비 {spec_c['ratio']:.2f} → "
                      f"exit {rc_c} · 실측 {lp.get('checked')}건 위반 0 {ok_c})"
                      if spec_r and spec_x else
                      f"      (M16 부분 실행 — role {bool(spec_r)}/contrast {bool(spec_x)}, "
                      f"대조군 exit {rc_c} 위반 0 {ok_c})")

        # M19 — 도해 **배치 높이 상한**(W7 figFitReport + G17-FIGFIT). 과도 종횡비 도해를
        # 주입해 수리 전이라면 통과했을 표본이 수리 후 검출되는지 어서션한다.
        # 렌더 층(반려/자동 축소/대조군)과 게이트 층(면 분단/판면 초과/대조군)을 다 밟는다.
        dg19 = (tokens.get("diagram") or {})
        if not (isinstance(dg19.get("maxHeightMm"), (int, float))
                and (dg19.get("widths") or {}).get("full") and dg19.get("minFontPt")):
            print("      (M19 건너뜀 — 이 스타일에 diagram.maxHeightMm/widths.full 미선언)")
        else:
            bd_rj = Path(td) / "m19-reject"
            spec_rj = figfit_probe_book(bd_rj, style, tokens, "reject")
            rc_rj, out_rj = run_render_diagrams(bd_rj, style)
            bd_sh = Path(td) / "m19-shrink"
            figfit_probe_book(bd_sh, style, tokens, "shrink")
            rc_sh, out_sh = run_render_diagrams(bd_sh, style)
            mp_sh = bd_sh / "assets" / "fig-01.metrics.json"
            fit_sh = (json.loads(mp_sh.read_text(encoding="utf-8")).get("fit") or {}
                      ) if mp_sh.exists() else {}
            bd_cl = Path(td) / "m19-control"
            figfit_probe_book(bd_cl, style, tokens, "control")
            rc_cl, out_cl = run_render_diagrams(bd_cl, style)
            mp_cl = bd_cl / "assets" / "fig-01.metrics.json"
            fit_cl = (json.loads(mp_cl.read_text(encoding="utf-8")).get("fit") or {}
                      ) if mp_cl.exists() else {}
            # ㉠ 반려: 축소가 라벨 하한을 깨는 종횡비 → HARD + 재작성 처방이 진단에 실린다
            ok_rj = rc_rj != 0 and "배치 높이" in out_rj and "가로 배치" in out_rj
            # ㉡ 자동 축소: 하한 위에서 수용 가능한 초과 → exit 0 + fit.verdict=shrunk +
            #    실효 최소 라벨이 하한 위(축소가 하한 HARD를 대체하지 않았다는 증거)
            ok_sh = (rc_sh == 0 and fit_sh.get("verdict") == "shrunk"
                     and isinstance(fit_sh.get("widthMm"), (int, float))
                     and fit_sh["widthMm"] < dg19["widths"]["full"]
                     and (fit_sh.get("effMinPt") or 0) >= dg19["minFontPt"] - 0.05)
            # ㉢ 대조군: 낮은 종횡비는 손대지 않는다(오탐 0)
            ok_cl = rc_cl == 0 and fit_cl.get("verdict") == "ok" and "DIAGRAM-FIT" not in out_cl
            # ㉣ 게이트 층 — 면 분단·판면 초과·대조군 (스탬핑 PDF, 빌드 0회)
            p_sp = figfit_gate_probe(Path(td) / "m19-g-split", tokens, "split")
            p_ov = figfit_gate_probe(Path(td) / "m19-g-overflow", tokens, "overflow")
            p_ct = figfit_gate_probe(Path(td) / "m19-g-control", tokens, "control")
            ok_g17 = (any("면 분단" in p for p in p_sp)
                      and any("판면 세로 범위 밖" in p for p in p_ov)
                      and not p_ct)
            results["M19-figfit"] = bool(ok_rj and ok_sh and ok_cl and ok_g17)
            print(f"      (M19 반려본 배치 {spec_rj['placed_h_nominal']:.1f}mm > 상한 "
                  f"{spec_rj['max_h']}mm → exit {rc_rj} {ok_rj} · 축소본 fit "
                  f"{fit_sh.get('verdict')} 폭 {fit_sh.get('widthMm')}mm eff "
                  f"{fit_sh.get('effMinPt')}pt {ok_sh} · 대조군 {fit_cl.get('verdict')} "
                  f"{ok_cl} · G17 분단 {len(p_sp)}건/초과 {len(p_ov)}건/대조군 "
                  f"{len(p_ct)}건 {ok_g17})")

        # M7 — body_pt 미선언 스타일 팩에서는 검사 자체가 성립하지 않으므로 건너뛴다
        if decl_pt:
            work = Path(td) / "m7.pdf"
            mutate_global_shrink(book_dir / "draft" / "book.pdf", work)
            doc = fitz.open(work)
            meas7, s7 = g1_scale_check(doc, decl_pt)
            results["M7-global-shrink"] = bool(s7)
            print(f"      (M7 주입본 본문 {meas7}pt vs 선언 {decl_pt}pt)")
            doc.close()
        else:
            print("      (M7 건너뜀 — tokens.json에 body_pt 미선언)")

    ok = all(results.values())
    for k, v in results.items():
        print(f"{'PASS' if v else 'FAIL'}  {k}")
    if not ok:
        sys.exit(1)
    print("전 뮤테이션 검출 — G14·G1-SCALE·G3-COLLIDE/FIT·G16 3축·린터 배선·"
          "도해 라벨 밴드/역할·대비 감도 확인")


if __name__ == "__main__":
    main()
