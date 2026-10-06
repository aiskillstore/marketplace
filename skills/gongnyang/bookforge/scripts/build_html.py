#!/usr/bin/env python3
"""bookforge HTML engine: md -> themed HTML -> Chromium print (2-pass TOC).

Theme contract (styles/<style>/):
  theme.css   — full print stylesheet (@page, tokens via :root, component classes)
  theme.html  — python str.Template page skeleton with $title $subtitle $author
                $date $brand $toc $body $fonts_dir placeholders. 다면 목차 스타일은
                목차 섹션을 <!--BF:TOCPAGE-->로 감싸고 $toc/$toc_mod을 쓴다 —
                빌더가 substitute 전에 N회 복제해 $toc_i/$toc_mod_i로 만든다.
Page markers: each chapter opener embeds an invisible @@chNN@@ marker (sections
@@chNNsMM@@; captioned figures/tables @@fgNNN@@/@@tbNNN@@ when toc_lists opts
in); pass 1 extracts real page numbers with PyMuPDF into per-kind dicts,
injects them into .tocpg spans, pass 2 prints the final PDF. toc_lists opt-in
also publishes 그림 차례/표 차례 front-matter pages (extra BF:TOCPAGE copies,
after the TOC — book-anatomy ⑨) whose page numbers ride the same 2-pass stamp.
"""
import json, os, re, subprocess, sys
from html import escape as _esc
from pathlib import Path
from string import Template

try:  # PyMuPDF 1.24+ 신 모듈명, 구버전은 fitz만 제공
    import pymupdf as fitz
except ImportError:
    import fitz
from markdown_it import MarkdownIt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import g16_tokens  # noqa: E402  — 색 파싱·$key_label 파생의 단일 진리원

MD = MarkdownIt("commonmark", {"html": True, "typographer": True}) \
    .enable("table").enable("strikethrough")

CALLOUT_RE = re.compile(r"^:::\s*(info|tip|warn|quote|stat|pull)\s*(.*)$")

# ── 페이지 마커 어휘 (pass1 전용 — 최종 PDF에는 존재하지 않는다) ────────────────
# 종 3가지: ch(장 @@chNN@@ · 절 @@chNNsMM@@) / fg(캡션 그림 @@fgNNN@@) /
# tb(캡션 표 @@tbNNN@@). fg·tb는 tokens.json `toc_lists` 옵트인 스타일에서만 발행된다
# (선언 부재 = 발행 0 — 기본 off, 기존 스타일 산출물 불변).
# 회수(pass1)와 제거(pass2 직전)는 반드시 이 한 어휘를 봐야 한다 — 종전에는 ch 전용
# 정규식 리터럴이 두 곳에 따로 살아, 어휘를 넓힐 때 한쪽만 고치면 발행분이 회수되지
# 않거나(회수 누락 → 쪽번호 00) 잔존 마커가 최종 PDF 텍스트 레이어로 새는(제거 누락)
# 두 방향의 디싱크가 물리적으로 가능했다.
# 회수 결과는 반드시 종별 딕트로 분리한다 — 한 딕트에 섞으면 min(pages) 소비자
# (folio_offset, insight decorate.py:29의 무필터 min)가 그림·표 면을 장 시작면으로
# 오인해 폴리오 원점이 통째로 어긋난다(magazine 폴리오 7면 누락과 동형 결함).
MARKER_KINDS = ("ch", "fg", "tb")
_MK_CORE = r"(?:ch\d+(?:s\d+)?|fg\d+|tb\d+)"
MK_SCAN_RE = re.compile(rf"@@({_MK_CORE})@@")
MK_STRIP_RE = re.compile(rf'<span class="pgmark">@@{_MK_CORE}@@</span>')
# toc_lists 허용 어휘 → 마커 종. 마커(위)와 차례 별면(아래 LIST_*)이 같은 선언을 본다.
TOC_LIST_KINDS = {"figures": "fg", "tables": "tb"}


def die(msg: str):
    sys.exit("BUILD FAIL: " + msg)


# 빌드 경고 채널. die()는 아니지만 조용히 넘어가면 안 되는 사실을 남긴다 —
# stdout + typeset/tocplan.json["warnings"]에 함께 기록되고, qc_gate가 그 파일을 읽어
# 게이트 리포트의 warns로 올린다(사후 진단이 계획 파일만 보고 오도되지 않게).
BUILD_WARNS: list = []


def warn(msg: str):
    BUILD_WARNS.append(msg)
    print("BUILD WARN: " + msg)


# ─────────────────────────────────────────────────────────────────────────────
# 다면 목차 (insight) — 분량 함수 N면 발행
#
# 왜: `.toc-body{position:absolute}`라 목차가 판면(257mm)을 넘으면 다음 면으로 흐르지
# 않는다. Chromium print는 그 초과를 **문서 전체 shrink-to-fit 축소**로 처리한다
# (실측 사고: 목차 24행 책이 전권 0.804배로 축소돼 출하됐고 15개 게이트가 전부 통과 —
# 기존 게이트가 모두 문서 자신을 기준으로 하는 상대 지표였다). 절을 지우거나 급수를
# 줄이는 대응은 어느 STYLE.md도 선언하지 않으므로, 면 수를 분량의 함수로 늘린다.
#
# 높이 모델은 "행 글리프 top의 절대 y"를 누적한다. 단위 mm, 좌표계는 목차 면 상단 기준.
# Chromium은 행 박스 top을 정수 CSS px(0.2646mm) 격자에 스냅하지만 누적 오차는 없다
# (각 행이 정확 누적값을 반올림) → 모델 오차는 항상 ±0.14mm 이내.
#
# [실측] 출처 = probe-6c17s(6장 17절, 축소 없는 1면 목차)의 PyMuPDF 스팬 bbox 전수 +
#        전 프로브 재측정(report/w3.md 캘리브레이션 표). CSS 출처는 theme.css의
#        `.toc-body{top:41mm}` `.toc-word{30pt; margin-bottom:14mm}`
#        `.toc li{margin-top:8mm; line-height:1.3}` `li.toc-sec{margin-top:2.5mm}`.
#
# ── 캘리브레이션 프로파일 (toc_profile) ──────────────────────────────────────
# 아래 17개 스칼라는 전부 **하나의 목차 레이아웃**(insight의 `hanging-two-level`)을
# 실측한 값 묶음이다. 모듈 전역 상수로 흩어져 있던 동안에는 ㉠어느 값이 어느 레이아웃의
# 것인지 ㉡새 레이아웃을 붙이려면 무엇을 다시 재야 하는지가 코드 어디에도 없었고, 그래서
# "상수를 조금 고쳐 다른 스타일에도 쓴다"가 물리적으로 가능했다(그 경로의 실패는
# 조용한 전역 축소이고 신호는 G1-SCALE 하나뿐이다). 이름 붙은 프로파일 하나로 묶어
# 그 경계를 명시한다 — **값은 이전과 한 자리도 다르지 않다(순수 구조 리팩터)**.
#
# 저장 위치가 스타일 팩이 아니라 스킬(빌더)인 이유 — 코드 실태 근거 3:
#   ㉠ 이 값들은 팩의 **디자인 선언**이 아니라 팩 + Chromium 조합의 **렌더 실측**이다.
#      top_mm 61.429는 CSS 41mm에 워드 라인박스 6.174 · 붕괴마진 14 · 글리프 오프셋
#      0.255를 더한 값이고, pitch/fold는 Chromium이 행 박스를 정수 CSS px에 스냅하는
#      동작에서 나온다(주석 참조). 팩이 "선언"할 수 있는 종류의 수가 아니다.
#   ㉡ 팩으로 옮기면 html 팩 전부에 17키 필수 토큰이 생기고(부재는 die여야 의미가 있다),
#      단면 목차 팩(magazine)은 그 17키를 영원히 쓰지 않는다 — `toc_capacity`가 단면
#      전용으로 팩에 있는 것과 대칭이 아니라 **비대칭**이 커진다.
#   ㉢ 팩 선언은 곧 "팩마다 하나씩" 을 부르고, 2개째 프로파일은 재적합 없이는 만들 수
#      없다(아래 경고). 구조만 만들고 값을 늘리지 않는 것이 이번 사이클의 계약이다.
# 대신 팩과의 연결은 **이름**으로 한다: `tokens.json`의 `toc_layout`이 프로파일의
# `layout`과 일치해야 하고(아래 `toc_profile()`), 그 토큰 자체는 G16-SYNC가 theme 실물과
# 대조한다(g16_tokens.TOC_LAYOUTS). 팩·게이트·빌더가 같은 한 단어를 가리킨다.
#
# ⚠ **2개째 프로파일 금지(이번 사이클)**: 값은 CSS 좌표·급수·서체·letter-spacing이
#    전부 얽힌 최소자승 적합의 산물이라, 다른 레이아웃에 "비슷한 값"을 넣으면 예측이
#    조용히 어긋나고 목차가 넘쳐 Chromium 전역 축소로 나간다. 새 프로파일은 프로브
#    재렌더 → 스팬 bbox 실측 → 재적합 → tocplan 예측/실측 대조를 다시 밟아야 한다.
TOC_PROFILES = {
    "insight-hanging-v1": {
        # styles/insight/tokens.json의 `toc_layout`과 일치해야 한다(toc_profile()이 대조).
        "layout": "hanging-two-level",
        "top_mm": 61.429,          # [실측] 1면 첫 행 글리프 top (41 + 워드 라인박스 6.174 + 붕괴마진 14 + 글리프오프셋 0.255)
        "top_cont_mm": 49.258,     # [실측] 2면 이후 첫 행 글리프 top (워드 display:none → 붕괴마진이 8mm)
        "top_cont_sec_mm": 43.508, # [실측] 2면 이후가 절 행으로 시작할 때(장 내 분할) — 붕괴마진 8→2.5mm.
                                   #        fix-within(1장 40절)이 이 경로를 처음 실행해 확정했다
                                   #        (구 파생 추정 43.825 대비 −0.317)
        # 행 종류별 전이 피치(앞 행 글리프 top → 뒤 행 글리프 top). 3구간인 이유는 margin-top이
        # 장 8mm / 절 2.5mm로 다르고 행 높이도 급수(10.9 / 9.9pt)에 따라 다르기 때문.
        # [실측] 프로브 7권 × 목차 14면의 (마지막 행 top − 첫 행 top)에 대한 최소자승 적합
        #        (확정 후 9권 × 18면 전수 재검증: 예측 바닥 오차 최대 0.126mm).
        #        잔차 최대 0.128mm = Chromium이 행 박스 top을 정수 CSS px(0.2646mm)에 스냅하는
        #        ±½px 한계와 일치한다(누적 오차 없음 — 각 행이 정확 누적값을 개별 반올림).
        "pitch_mm": {
            ("sec", "sec"): 7.028,   # [실측] CSS 유래 2.5mm + 12.87pt = 7.039과 0.011 일치
            ("ch", "sec"): 7.761,    # [실측] CSS 유래 7.499보다 1px 큼 — 장 행 플렉스 baseline 정렬 실효 높이
            ("sec", "ch"): 12.525,   # [실측] CSS 유래 8mm + 12.87pt = 12.539와 0.014 일치
            ("ch", "ch"): 13.229,    # [실측] 절 0개 장 연속에서만 발생. adv-zero15 실렌더로 확정
                                     #        (구 파생 추정 13.261 대비 −0.032)
        },
        # 2줄 접힘 1행당 추가 높이 = **다음 행 top까지의 기여분**(행 안의 1→2행 델타가 아니다).
        # [실측] 구 값(장 5.027 / 절 4.498)은 한 행 안의 델타를 그대로 쓴 것이라 절에서 행마다
        # 0.055mm씩 모자랐고, 접힘 13건 도서에서 예측이 실측보다 0.80mm 낮게 나왔다(fix-fold·
        # fix-shrink 실측). Chromium이 행 박스를 정수 CSS px에 스냅해 델타가 4.498/4.762로
        # 교번하기 때문이며, 누적에 쓰는 값은 그 **평균 기여분**이어야 한다.
        #   절: (다음 행 top − 이 행 top) − pitch(sec,sec) 평균 = 4.553  [fix-fold 8구간·fix-shrink 45구간]
        #   장: 같은 방식 평균은 4.88이지만 표본 2건뿐이라 보수값 5.027을 유지한다(과대 = 안전).
        "fold_mm": {"ch": 5.027, "sec": 4.553},
        # 마지막 행의 글리프 top → 글리프 bottom(디센더 포함). 목차 바닥 측정값과 직접 비교되는 값.
        # [실측] sec 4.166(14면 전수 동일) / ch 4.586(probe-6c17s 장 행 bbox)
        "tail_mm": {"ch": 4.586, "sec": 4.166},
        # 제목 가용 폭 = .toc-body 폭 105mm − .tocpg 6.5mm − (절은 padding-left 2mm)
        "avail_mm": {"ch": 98.5, "sec": 96.5},
        # 폭 추정을 보수적으로 — 접힘을 늦게 잡으면 면이 넘친다
        "fold_safety": 0.98,
        # 미학 한계: 233mm. 여백 리듬 기준(가용 172mm = 233 − 61.43)이며 분할의 1차 목표.
        "limit_aesthetic_mm": 233.0,
        # 물리 한계: 판면은 257mm지만 실측으로 축소 미발생이 확인된 최대는 252.47mm이고
        # 발생 최소는 259.20mm다(ledger). 인증된 안전 구간 안쪽으로 잡는다 — 미학 한계가
        # 항상 실현 가능하므로 이 값은 사실상 단정문(assertion)이다.
        "limit_physical_mm": 252.0,
        # 장 내 분할(면이 절 행으로 시작) 벌점 — 장 제목 없는 절 나열 면은 마지막 면 균형을
        # 위해서만 허용한다. 단위는 (mm)^2와 같으므로 5000 ≈ 71mm 슬랙에 해당.
        "within_group_penalty": 5000.0,
    },
}
# 프로파일을 인자로 받지 않는 호출 경로(외부 진단 스크립트·단위 실험)를 위한 기본값.
# build()는 항상 toc_profile()로 명시 해석해 넘긴다 — 기본값에 기대지 않는다.
DEFAULT_TOC_PROFILE = "insight-hanging-v1"


def _prof(prof=None):
    """프로파일 해석 — None이면 기본 프로파일. 함수 시그니처 기본값에 dict를 두지 않으려는 우회."""
    return prof if prof is not None else TOC_PROFILES[DEFAULT_TOC_PROFILE]


def toc_profile(style_name, tokens):
    """다면 목차 스타일의 캘리브레이션 프로파일을 `toc_layout` 토큰으로 해석한다.

    팩이 선언한 레이아웃 이름과 프로파일의 `layout`이 일치할 때만 돌려준다 — 이름이
    맞지 않으면 그 레이아웃은 아직 캘리브레이션되지 않은 것이고, "비슷한 값으로 돌려
    보는" 경로는 조용한 전역 축소로 끝난다(위 ⚠). 그래서 폴백하지 않고 die한다."""
    lay = tokens.get("toc_layout")
    for name, prof in TOC_PROFILES.items():
        if prof["layout"] == lay:
            return prof
    have = ", ".join("%s(layout=%s)" % (n, p["layout"]) for n, p in TOC_PROFILES.items())
    die(f"styles/{style_name}: toc_layout={lay!r}에 대한 다면 목차 캘리브레이션 프로파일이 "
        f"없다(보유: {have}). "
        f"다면 목차(toc_overflow=paginate)는 높이 모델 17개 상수의 실측 적합이 선행돼야 "
        f"한다 — 프로브 재렌더 → 스팬 bbox 실측 → 재적합 → tocplan 예측/실측 대조를 "
        f"밟고 TOC_PROFILES에 새 프로파일을 추가할 것")


# ── 문자 폭: 동봉 폰트의 실제 advance에서 계산한다 ────────────────────────────
# 구 구현은 `ord(c) > 0x2E7F` 3분류(wide/space/other) 폭표였고, `— … → ① ★ ◆ ■ ● ℃`와
# `W M m w`가 전부 CJK 경계 **아래**라 `other`(가장 좁은 값)로 분류돼 절 기준 24~35%
# 과소추정했다(적대검토 D1: 접힘 누락 → 면 넘침 → 전역 축소 재발). 분류표를 늘리는
# 대응은 같은 결함을 반복하므로, 폰트 파일의 glyph advance를 직접 쓴다.
#
# [실측] Chromium(FreeType 힌팅)은 글리프 advance를 **정수 CSS px로 반올림**한 뒤
# letter-spacing을 더한다. 프로브 16권 × 목차 면의 rawdict 문자 origin 델타 전수에서:
#   advance_px = round(font_advance_em × size_px) + (−0.02 × size_px)
# 가 한글 잔차 −0.038px/자(10.9pt)·−0.011px/자(9.9pt)로 맞고, 힌팅이 위로 올라가는
# 일부 글리프(예: Pretendard-Bold `6 8 9`@10.9pt, Medium 숫자@9.9pt)에서만 최대
# −1.04px/자로 과소가 된다. 그 잔차 상한을 단일 상수로 흡수한다.
#
# ⚠ 단일 **배율** 보정 계수는 성립하지 않는다(반증): 같은 Pretendard 한글이 10.9pt에서
#   폰트 advance 대비 +1.5%, 9.9pt에서 −5.8%로 **부호가 반대**다. 원인은 위 정수 px
#   반올림이고 폰트 파일에서 유도되지 않는다. 그래서 보정은 배율이 아니라 **가산 슬랙**
#   한 개(TOC_HINT_SLACK_PX)이며, 남는 오차는 R1(렌더 후 실측 검증)이 닫는다.
TOC_LS_EM = -0.02            # theme.css body{letter-spacing:-0.02em} — 목차가 상속
# [실측] 남는 잔차를 흡수하는 **단일 가산 보정**. 한글은 −0.04px/자로 일정하므로 그 값을
# 그대로 쓴다(보정 후 fix-fold2 26자 행에서 모델 96.44 vs 실측 96.36 = +0.08mm).
# 힌팅이 1px 올라가는 일부 숫자·기호(−1.04px/자)까지 슬랙으로 덮으면 한글 45자 제목이
# 12mm 과대추정돼 불필요하게 3행이 된다(실측) — 그 몫은 보수 계수 fold_safety
# 0.98(절 기준 1.93mm ≈ 7px)과 R1 렌더 후 실측 검증이 받는다.
TOC_HINT_SLACK_PX = 0.04
PX_PER_PT = 4 / 3            # CSS px = 0.75pt
MM_PER_PX = 25.4 / 96

# 목차 행 종류별 서체·급수(insight theme.css: .toc-title 700/10.9pt, .toc-sec-title 500/9.9pt).
# theme.css의 @font-face weight 매핑과 함께 움직여야 한다.
TOC_FONT = {"ch": ("Pretendard-Bold", 10.9), "sec": ("Pretendard-Medium", 9.9)}

_FONTS_DIR = None            # build()가 설정(skill/assets/fonts)
_FONT_CACHE = {}


def _font(name):
    """동봉 폰트 파일의 fitz.Font. 폰트 폴더 미설정·파일 부재는 계약 위반이므로 die()."""
    if name not in _FONT_CACHE:
        if _FONTS_DIR is None:
            die("폰트 폴더 미설정 — build()가 _FONTS_DIR을 설정하기 전에 폭 계산이 불렸다")
        p = _FONTS_DIR / f"{name}.ttf"
        if not p.exists():
            die(f"동봉 폰트 없음: {p} (목차 폭 추정은 실제 advance를 쓴다)")
        _FONT_CACHE[name] = fitz.Font(fontfile=str(p))
    return _FONT_CACHE[name]


def _adv_mm(font, ch, size_pt):
    """글자 1개의 렌더 advance(mm). 글리프 부재는 폴백 폰트 몫이므로 1em으로 보수 계산."""
    size_px = size_pt * PX_PER_PT
    cp = ord(ch)
    adv_em = font.glyph_advance(cp)
    if not font.has_glyph(cp):
        # 이모지·미수록 기호는 폴백 폰트가 그린다 — advance를 알 수 없으므로 notdef 폭과
        # 1em 중 큰 값으로 보수 계산한다(과대 추정 = 일찍 접힘 = 안전 방향).
        adv_em = max(1.0, adv_em)
    px = round(adv_em * size_px) + TOC_LS_EM * size_px + TOC_HINT_SLACK_PX
    return max(px, 0.0) * MM_PER_PX


def _string_width_mm(font, text, size_pt):
    return sum(_adv_mm(font, c, size_pt) for c in text)


def _text_width_mm(kind, text):
    name, size = TOC_FONT[kind]
    return _string_width_mm(_font(name), text, size)


def _wrap_lines(kind, text, avail_mm, prof=None):
    """keep-all 환경의 그리디 어절 줄바꿈 시뮬레이션 → 행 수.
    공백 없는 단일 어절이 가용 폭을 넘으면 (lines, overflow=True)."""
    limit = avail_mm * _prof(prof)["fold_safety"]
    words = text.split()
    if not words:
        return 1, False
    lines, cur = 1, ""
    overflow = False
    for w in words:
        if _text_width_mm(kind, w) > limit:
            overflow = True          # word-break:keep-all — 어절 중간 개행 불가 → 가로 넘침
        trial = (cur + " " + w) if cur else w
        if _text_width_mm(kind, trial) <= limit or not cur:
            cur = trial
        else:
            lines += 1
            cur = w
    return lines, overflow


# ── 1면 커넥터 장식 예약 사각 (V2) ───────────────────────────────────────────
# theme.html의 Contents 커넥터: 원 중심 (144, 66) r6 → x 138–150 / y 60–72mm, 그 안에
# 십자 픽토그램. 목차 1면 첫 행들의 글리프 밴드가 이 사각과 y로 겹치면 24자 이상 장
# 제목이 픽토그램 위에 얹힌다(판정 V2 실측: 장 1행 x 57.0–153.4 / y 61.4–66.0).
# 검출(W4 G3-COLLIDE)로 미루지 않고 **예방**한다 — 겹치는 행만 가용 폭을 사각 좌변까지로
# 줄여 접힘을 유발하면, 각 행이 x57(절 x59)에서 시작해 사각 좌변 안에서 끝나므로 침범이
# 사라진다. 어느 행이 대상인지는 높이 모델에서 도출한다(현 좌표에서는 1~2행이 나온다:
# 장 1행 61.43–66.02 / 절 2행 69.19–73.34가 y 60–72와 교차, 3행 76.22는 교차 없음).
# 2면 이후는 .toc-cont가 커넥터를 감추므로 대상이 아니다.
TOC_CONNECTOR_RECT = (138.0, 150.0, 60.0, 72.0)   # x0, x1, y0, y1 (mm)
TOC_ROW_LEFT_MM = {"ch": 57.0, "sec": 59.0}       # .toc-body left 57 + 절 padding-left 2


def _row_band(y_top, r, prof=None):
    """행 글리프 밴드 [top, bottom] — 접힘분 포함."""
    P = _prof(prof)
    return y_top, y_top + P["tail_mm"][r["kind"]] + P["fold_mm"][r["kind"]] * (r["lines"] - 1)


def _connector_avail(rows, prof=None):
    """1면에서 커넥터 예약 사각과 y로 겹치는 행의 인덱스 → 축소 가용 폭(mm).

    접힘은 뒤 행을 아래로만 밀므로 교차 집합은 단조 축소한다 → 최대 4회로 수렴한다."""
    P = _prof(prof)
    cx0, _cx1, cy0, cy1 = TOC_CONNECTOR_RECT
    narrowed = {}
    for _ in range(4):
        # 현재 narrowed 가정으로 행 수를 다시 잡고 y를 누적
        for i, r in enumerate(rows):
            avail = narrowed.get(i, P["avail_mm"][r["kind"]])
            r["lines"], _ = _wrap_lines(r["kind"], r["title"], avail, P)
        hit = {}
        y = P["top_mm"]
        for i, r in enumerate(rows):
            top, bot = _row_band(y, r, P)
            if top > cy1:
                break                       # 이후 행은 전부 사각 아래
            if bot >= cy0:
                hit[i] = cx0 - TOC_ROW_LEFT_MM[r["kind"]]
            if i + 1 >= len(rows):
                break
            y += P["pitch_mm"][(r["kind"], rows[i + 1]["kind"])]
            y += P["fold_mm"][r["kind"]] * (r["lines"] - 1)
        if hit == narrowed:
            return narrowed
        narrowed = hit
    return narrowed


def _li_with_reserve(r, prof=None):
    """커넥터 예약으로 좁아진 행은 **렌더에도** 그 폭을 강제한다.

    모델에서만 좁히면 예측 높이만 커지고 브라우저는 여전히 전폭으로 1행에 그려 장식을
    침범한다(모델과 실물이 갈린다). 제목 스팬에 max-width를 인라인으로 실어 실제 접힘을
    만든다 — 폭 값의 단일 출처를 build_html.py에 두려고 CSS 클래스가 아니라 인라인이다.
    `.toc-leader{flex:1}`가 남는 폭을 흡수하므로 `.tocpg` 칼럼(우단 162mm)은 불변이다."""
    full = _prof(prof)["avail_mm"][r["kind"]]
    avail = r.get("avail_mm", full)
    if avail >= full:
        return r["li"]
    cls = "toc-title" if r["kind"] == "ch" else "toc-sec-title"
    return r["li"].replace(f'<span class="{cls}">',
                           f'<span class="{cls}" style="max-width:{avail:.1f}mm">', 1)


def toc_row_metrics(rows, connector_reserve=True, prof=None):
    """각 목차 행의 렌더 행 수를 확정한다(접힘 예산). 반환은 어절 단위로도 안 들어가는
    제목 목록. 넘침 판정은 **원 가용 폭** 기준이다 — 커넥터 예약으로 좁아진 폭에서만
    안 들어가는 제목은 빌드를 세울 사유가 아니라 장식 침범 경고 사유다."""
    P = _prof(prof)
    over = []
    narrowed = _connector_avail(rows, P) if connector_reserve else {}
    for i, r in enumerate(rows):
        avail = narrowed.get(i, P["avail_mm"][r["kind"]])
        r["lines"], _ = _wrap_lines(r["kind"], r["title"], avail, P)
        r["avail_mm"] = round(avail, 2)
        _, ovf_full = _wrap_lines(r["kind"], r["title"], P["avail_mm"][r["kind"]], P)
        if ovf_full:
            over.append(r["title"])
        elif i in narrowed:
            _, ovf_narrow = _wrap_lines(r["kind"], r["title"], avail, P)
            if ovf_narrow:
                warn(f"목차 1면 {i + 1}행 '{r['title'][:20]}'의 한 어절이 커넥터 예약 폭 "
                     f"{avail:.0f}mm를 넘는다 — 장식 침범이 남는다(제목 어절을 나눌 것)")
    return over


def _toc_page_bottom(rows, i, j, first_page, prof=None):
    """rows[i:j]를 한 면에 실을 때의 마지막 행 글리프 bottom(mm)."""
    P = _prof(prof)
    k0 = rows[i]["kind"]
    if first_page:
        y = P["top_mm"]
    else:
        y = P["top_cont_mm"] if k0 == "ch" else P["top_cont_sec_mm"]
    for k in range(i + 1, j):
        prev = rows[k - 1]
        y += P["pitch_mm"][(prev["kind"], rows[k]["kind"])]
        y += P["fold_mm"][prev["kind"]] * (prev["lines"] - 1)
    last = rows[j - 1]
    return y + P["tail_mm"][last["kind"]] + P["fold_mm"][last["kind"]] * (last["lines"] - 1)


def plan_toc_pages(rows, limit_mm=None, prof=None):
    """목차 행 리스트를 N면으로 분할. 그리디 금지 — refit.py §관례에 따라 후보를
    전수 평가하고(DP) ①면 수 최소 ②균형 최적 순으로 고른다.

    제약: 장 엔트리와 그 장의 첫 절은 같은 면(고아 금지) → rows[j-1]이 **절을 가진**
    장이면 j는 분할점이 될 수 없다. 절이 0개인 장에는 떼어놓을 첫 절이 없으므로 고아가
    존재하지 않는다 — 이 구분이 없으면 절 0개 장이 연속될 때 분할점이 전멸해 미학 한계
    해가 사라지고 물리 한계 폴백으로 떨어진다(적대검토 D2: 15장에서 251.7mm, 18.7mm
    침묵 위반). 균형 비용 = Σ(limit − 면 바닥)² + 장 내 분할 벌점 → 마지막 면만 1~2행
    남는 분할은 비용이 커서 자동으로 배제되고, 필요하면 앞 면에서 행을 넘겨 균형을
    맞춘다."""
    P = _prof(prof)
    if limit_mm is None:
        limit_mm = P["limit_aesthetic_mm"]
    n = len(rows)
    if n == 0:
        return []
    INF = (10 ** 9, float("inf"))
    best = [INF] * (n + 1)
    nxt = [None] * (n + 1)
    best[n] = (0, 0.0)
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n + 1):
            if j < n:
                if rows[j - 1]["kind"] == "ch" and rows[j - 1].get("has_sec"):
                    continue            # 장 고아 금지: 절 있는 장 행이 면 마지막일 수 없다
            bottom = _toc_page_bottom(rows, i, j, i == 0, P)
            if bottom > limit_mm:
                break                   # bottom은 j에 단조증가 — 더 큰 j는 전부 초과
            if best[j] == INF:
                continue
            pen = P["within_group_penalty"] if (j < n and rows[j]["kind"] == "sec") else 0.0
            cand = (best[j][0] + 1, best[j][1] + (limit_mm - bottom) ** 2 + pen)
            if cand < best[i]:
                best[i] = cand
                nxt[i] = j
    if best[0] == INF:
        return None
    out, i = [], 0
    while i < n:
        j = nxt[i]
        out.append((i, j))
        i = j
    return out


# ── 렌더 후 실측 검증 (모델은 계획자, pass1.pdf가 검증자) ────────────────────
# 모델 예측과 실측의 허용 오차. [실측] 프로브 18면 전수 잔차 최대 0.126mm = Chromium이
# 행 박스 top을 정수 CSS px(0.2646mm)에 스냅하는 ±½px 한계. 여기서는 그 4배를 허용
# 임계로 두고, 넘으면 "상수가 낡았다"는 신호로 WARN을 남긴다.
# 접힘이 많은 도서에서 스냅 교번의 잔차가 행당 ±0.05mm 남으므로 0.8mm로 둔다.
# 미학 233 ↔ 물리 252의 19mm 헤드룸에 비하면 여전히 조기 경보다.
TOC_MODEL_TOL_MM = 0.8
PT_TO_MM = 25.4 / 72


def _measure_doc_scale(doc, first_body_pno, body_pt):
    """Chromium shrink-to-fit 배율 = 본문 최빈 급수(글자 수 가중) / 선언 급수.

    목차가 판면을 넘으면 Chromium은 흐름을 만들지 않고 **문서 전체를 축소**한다. 그러면
    목차 면의 스팬 좌표도 같은 배율로 줄어들어, 실측 바닥을 그대로 읽으면 초과가 보이지
    않는다(적대검토 재현 B: 실제 바닥 ≈331mm가 축소 후 248.6mm로 읽혔다). 배율을 역산해
    실측을 원좌표로 되돌린다."""
    if not body_pt:
        return 1.0
    hist = {}
    for pno in range(max(0, first_body_pno), doc.page_count):
        for b in doc[pno].get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    t = s["text"].strip()
                    if not t or not (6.0 <= s["size"] <= 14.0):
                        continue
                    hist[round(s["size"], 2)] = hist.get(round(s["size"], 2), 0) + len(t)
    if not hist:
        return 1.0
    mode = max(hist.items(), key=lambda kv: kv[1])[0]
    return mode / float(body_pt)


def _measure_page_text_bottom_mm(page):
    """면의 최하단 텍스트 글리프 bottom(mm). 목차 면에서는 마지막 목차 행의 바닥이다."""
    bot = 0.0
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if s["text"].strip():
                    bot = max(bot, s["bbox"][3])
    return bot * PT_TO_MM


# W5 재판정 N2 — HTML 트랙 widths 값 축. typst 트랙 g16_tokens.typ_body_width_mm
# (`trim.w − margin.left − margin.right` 정적 계산)의 CSS 대응. 이름 없는 `@page { … }`만
# 잡는다 — `@page full`/`@page nofolio` 같은 변형은 margin만 국소 재정의하고 size는
# 공유하는 관례라 대상이 아니다. `[^}]*` 대신 여는 중괄호 뒤 창(윈도) 탐색을 쓰는 이유는
# magazine의 `@page { … @bottom-right { content: none; } }`처럼 중첩 블록이 있으면
# 첫 `}`가 `@page` 자신이 아니라 중첩 규칙의 닫는 괄호이기 때문이다(실측 확인).
_PAGE_BLOCK_RE = re.compile(r"@page\s*\{")
_PAGE_SIZE_RE = re.compile(r"size\s*:\s*([\d.]+)mm\s+([\d.]+)mm")
_PAGE_MARGIN_RE = re.compile(r"margin\s*:\s*([\d.]+)mm\s+([\d.]+)mm\s+([\d.]+)mm\s+([\d.]+)mm")


def _page_geometry_mm(css_text):
    """theme.css 첫 `@page {size: Wmm Hmm; margin: T R B L;}`에서 (trim폭, 우측여백, 좌측여백)mm.
    형태가 다르면 None — typst 쪽과 마찬가지로 추정하지 않는다."""
    m = _PAGE_BLOCK_RE.search(css_text)
    if not m:
        return None
    window = css_text[m.end(): m.end() + 400]
    ms = _PAGE_SIZE_RE.search(window)
    mg = _PAGE_MARGIN_RE.search(window)
    if not ms or not mg:
        return None
    trim_w = float(ms.group(1))
    _top, right, _bottom, left = (float(x) for x in mg.groups())
    return trim_w, right, left


def _norm_txt(s):
    return re.sub(r"\s+", "", s)


def _measure_row_lines(page, rows):
    """목차 면의 실제 렌더 행 수를 행(mk)별로 잰다 → {mk: lines}.

    PDF 라인을 y 순으로 훑으며 rows의 제목 문자열을 순서대로 소비한다. 접힘이면 한 제목이
    여러 라인에 걸치므로 그 라인 수가 곧 실측 행 수다. 쪽번호 스팬(우측 정렬 순수 숫자)은
    제외한다. 매칭이 어긋나면 None(측정 실패)."""
    lines = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            xs = [s for s in l["spans"] if s["text"].strip()]
            if not xs:
                continue
            right = max(s["bbox"][2] for s in xs)
            txt = "".join(s["text"] for s in xs
                          if not (s["text"].strip().isdigit() and s["bbox"][2] >= right - 1))
            lines.append((l["bbox"][1], _norm_txt(txt)))
    lines.sort(key=lambda t: t[0])
    seq = [t for _, t in lines if t]
    out, i = {}, 0
    for r in rows:
        want = _norm_txt(r["title"])
        if not want:
            return None
        while i < len(seq) and not want.startswith(seq[i][:2]):
            i += 1                      # 워드마크 등 목차 행이 아닌 라인 건너뛰기
        if i >= len(seq):
            # 면을 넘겨 클리핑된 행 — 텍스트 레이어에 없다. 여기까지가 측정 가능분이고,
            # 부분 측정이라도 재계획에는 충분한 정보다(넘침 상황에서 정확히 필요한 데이터).
            break
        acc, cnt = "", 0
        while i < len(seq) and len(acc) < len(want):
            acc += seq[i]; cnt += 1; i += 1
        if acc != want:
            return None
        out[r["mk"]] = cnt
    return out


TOCPAGE_RE = re.compile(r"<!--BF:TOCPAGE.*?-->(?P<block>.*?)<!--/BF:TOCPAGE-->", re.S)


def expand_toc_pages(tpl_text, n_pages):
    """`<!--BF:TOCPAGE-->…<!--/BF:TOCPAGE-->` 블록을 N회 복제하고 각 복제본의
    `$toc`→`$toc_i`, `$toc_mod`→`$toc_mod_i`로 치환한다. Template.substitute **전에**
    원본 템플릿 텍스트에서 수행 — 목차 마크업과 장식을 theme.html에 남기기 위한 방식이다
    (커넥터가 이차 베지어(Q)라 PyMuPDF로 옮길 수 없고, 장식을 decorate.py로 옮기면
    겹침 게이트가 사고 지점을 통째로 면제한다)."""
    blocks = list(TOCPAGE_RE.finditer(tpl_text))
    if not blocks:
        die("theme.html에 BF:TOCPAGE 블록이 없다")
    if len(blocks) > 1:
        # 구 구현은 search()로 첫 블록만 확장하고 나머지의 $toc를 남겨 Template.substitute가
        # KeyError 트레이스백을 냈다. 조용한 오작동 대신 명시 실패로 세운다.
        die(f"theme.html에 BF:TOCPAGE 블록이 {len(blocks)}개다 — 정확히 1개여야 한다"
            "(다면 목차는 한 블록을 N회 복제해 발행한다)")
    m = blocks[0]
    block = m.group("block")
    if not re.search(r"\$toc\b", block):
        die("BF:TOCPAGE 블록에 $toc 플레이스홀더가 없다 — 복제해도 목차가 들어갈 자리가 없다")
    if n_pages < 1:
        die(f"목차 면 수가 {n_pages}면이다 — 장이 0개이거나 분할 결과가 비었다. "
            "outline.json의 chapters를 확인할 것(목차 섹션을 무언 삭제하지 않는다)")
    copies = []
    for i in range(1, n_pages + 1):
        b = re.sub(r"\$toc_mod\b", f"$toc_mod_{i}", block)
        b = re.sub(r"\$toc\b", f"$toc_{i}", b)
        copies.append(b)
    # 복제본 사이 개행 — 블록 말미가 플레이스홀더로 끝나면 다음 복제본 첫 문자와 식별자가
    # 융합돼 KeyError가 난다($brand + '<' 는 안전하지만 $brand + 'x'는 융합).
    return tpl_text[:m.start()] + "\n".join(copies) + tpl_text[m.end():]


# ── 단면 목차(1면 고정) 스타일의 용량 계약 ────────────────────────────────────
# 구 구현은 `if style != "magazine": return`으로 **폴더 이름**이 방어선이었고, 단면 목차
# 팩을 하나 더 만들면 용량 검사가 조용히 사라졌다(적대검토 D6). 상수를 tokens.json의
# `toc_capacity`로 올려 계약으로 바꾼다 — 선언이 없으면 빌드를 세운다.
# 7키 튜플의 정본은 g16_tokens(오버레이 축 ⑪이 같은 키로 toc_capacity_alt를 판정) —
# 별칭만 남긴다. 두 벌이면 게이트와 빌더가 서로 다른 "필수 키"를 갖게 된다.
TOC_CAPACITY_KEYS = g16_tokens.TOC_CAPACITY_KEYS

# tokens.json `toc_overflow` 허용값 ↔ theme.html BF:TOCPAGE 블록 유무. 종전엔 이 분기가
# 토큰이 아니라 템플릿 실물(`"<!--BF:TOCPAGE" in tpl_src`)만으로 갈렸다 — 계약이 코드에
# 숨어 있어 tokens.json만 보고는 그 스타일이 다면인지 단면인지 알 수 없었고, 실물과
# 계약이 갈라져도(예: BF:TOCPAGE를 지웠는데 토큰은 남는 미래의 리팩터) 아무도 잡지
# 못했다. html 엔진 스타일 전용 키다 — typst 4종은 이 분기 자체가 없다.
TOC_OVERFLOW_MULTIPAGE = {"paginate": True, "single": False}


# 단면 목차 제목 폭의 렌더 마진 — Chromium 실렌더 advance가 fontTools 모델보다 약
# +1.0~1.4% 넓다(적대검증 v-s6 ③ 이분탐색 실측: 모델 48.6mm 제목이 렌더 48.31~49+mm로
# 접힘, 공백 0.96→1.11mm 등). 마진 없이는 선언 가용 폭의 마지막 ~2% 대역 제목이 검사를
# 통과한 뒤 실렌더에서 접혀(쪽번호 고아화) qc_gate PASS로 출하됐다 — 기본 스프레드
# (75mm/22pt)·display-numeral(49mm/15pt) 공통, S3 시대부터의 상속 결함. 다면 목차의
# 접힘 추정이 이미 같은 계수(fold_safety 0.98)를 쓰므로 단면도 같은 보수 방향으로 맞춘다
# — 실효 가용 폭 75→73.5 / 49→48.02mm는 실측 접힘 경계(≈73.5 / ≈48.0) 바로 안쪽이다.
TOC_TITLE_RENDER_SAFETY = 0.98


def check_single_page_toc(style, rows, cap_spec):
    """스프레드 1면 목차의 용량·접힘 검사. 다면화는 STYLE.md 선언과 충돌하므로 초과 시
    조용히 자르지 않고 빌드를 세운다.

    접힘은 **예산에 넣지 않고 금지한다**: `.toc li{flex-wrap:wrap}`이라 제목이 1행에 안
    들어가면 높이만 느는 게 아니라 정렬이 파손된다(판정 V3 실측: 제목 좌단 36.99→20.00mm
    로 17mm 이탈, 쪽번호가 제목 **위** 독립 행으로 고아화, 피치 23.55→39.69mm). 그 상태로
    전 게이트를 통과해 출하되므로 근사 높이(구 MAG_WRAP_EXTRA_MM)로 흡수할 대상이 아니다.
    """
    if not rows:
        die("목차에 실을 장이 0개다 — outline.json의 chapters를 확인할 것"
            "(목차 섹션을 빈 채로 발행하지 않는다)")
    if not cap_spec:
        die(f"styles/{style}/tokens.json에 `toc_capacity` 선언이 없다 — TOCPAGE 블록이 없는 "
            "html 엔진 스타일은 단면 목차이므로 용량 계약을 반드시 선언해야 한다"
            f"(필수 키: {', '.join(TOC_CAPACITY_KEYS)}. references/extending.md 참조). "
            "선언이 없으면 목차가 넘쳐도 검사 없이 전역 축소로 간다.")
    missing = [k for k in TOC_CAPACITY_KEYS if k not in cap_spec]
    if missing:
        die(f"styles/{style}/tokens.json `toc_capacity`에 키 누락: {missing}")
    font = _font(cap_spec["font"])
    size = float(cap_spec["size_pt"])
    decl_avail = float(cap_spec["title_avail_mm"])
    avail = decl_avail * TOC_TITLE_RENDER_SAFETY
    folded = [(r["title"], _string_width_mm(font, r["title"], size)) for r in rows
              if _string_width_mm(font, r["title"], size) > avail]
    if folded:
        # 22pt 기준 권장 자수 — 한글 1자 폭으로 나눈 보수값
        per_char = _adv_mm(font, "가", size)
        rec = int(avail // per_char)
        lst = "; ".join(f"'{t[:24]}' {w:.1f}mm" for t, w in folded[:4])
        die(f"{style} 목차 제목 {len(folded)}건이 1행에 들어가지 않는다(실효 가용 폭 "
            f"{avail:.1f}mm = 선언 {decl_avail:.0f}mm × 렌더 마진 {TOC_TITLE_RENDER_SAFETY}): "
            f"{lst}. flex-wrap 접힘은 높이만 늘리는 것이 아니라 제목 좌단이 쪽번호 칼럼보다 "
            f"왼쪽으로 17mm 이탈하고 쪽번호가 제목 위 독립 행으로 고아가 된다 — 정렬 파손이라 "
            f"허용하지 않는다. 제목을 {size:.0f}pt 기준 {rec}자 이내로 줄일 것.")
    n = len(rows)
    top = float(cap_spec["top_mm"]); pitch = float(cap_spec["pitch_mm"])
    tail = float(cap_spec["tail_mm"]); bottom_lim = float(cap_spec["bottom_mm"])
    bottom = top + pitch * (n - 1) + tail
    if bottom <= bottom_lim:
        return bottom
    cap = max(1, int((bottom_lim - top - tail) // pitch) + 1)
    die(f"{style} 목차 용량 초과 — 장 {n}개(예측 바닥 {bottom:.1f}mm > 콘텐츠 하단 "
        f"{bottom_lim}mm). STYLE.md「목차 문법」이 '스프레드 1면 사용'을 선언하므로 "
        f"다면화하지 않는다. 이 원고의 상한은 장 {cap}개다 — 대응: ①장을 병합해 {cap}개 "
        f"이하로 줄인다(절을 장으로 승격하지 말 것) ②style을 insight로 바꾼다(다면 목차 "
        "지원). 폰트·행간 축소로 밀어 넣는 대응은 금지한다.")

# ── 그림·표 차례 별면 (toc_lists 옵트인 — 다면 목차 스타일 전용) ────────────────
# 규격 근거: 별면 위치(차례 뒤 = book-anatomy 앞부속 ⑨)·표제 동일 규격·항목 9.5pt/
# 행송 15pt/라벨 칼럼 16mm는 academic/STYLE.md「목차 문법」의 그림·표 차례 선언을
# insight 목차 문법(리더 점선 금지, 쪽번호 칼럼 6.5mm 고정)으로 옮긴 값이다. 기본 off —
# book-anatomy가 소책자에서 그림·표 목록 생략을 권장하므로 선언 없이는 아무것도 변하지
# 않는다(발행 0 = 기존 산출물 불변).
# 면은 BF:TOCPAGE 복제본으로 발행한다 — 목차와 같은 지면 가구(사이드바·걸침 아이콘)를
# theme.html에 남겨야 겹침·프레임 게이트가 이 면도 검사한다(장식을 빌더가 새로 만들면
# 게이트가 사고 지점을 통째로 면제한다). 그래서 toc_lists는 다면 목차(BF:TOCPAGE 보유)
# 스타일 전용이고 단면 스타일의 선언은 die다 — 조용한 발행 0은 "차례가 꺼진 것과 선언
# 오타가 구별되지 않는" 바로 그 상태다.
LIST_WORD = {"fg": "그림 차례", "tb": "표 차례"}
LIST_LABEL_FONT = ("Pretendard-Medium", 9.5)   # .lof-no — theme.css 규칙과 동행
LIST_TITLE_FONT = ("Pretendard-Light", 9.5)    # .lof-title — 접힘(행 수) 추정용
LIST_LABEL_MM = 16.0                            # 라벨 칼럼(academic 선언 16mm 고정)
LIST_AVAIL_MM = 105.0 - LIST_LABEL_MM - 6.5     # .toc-body 105 − 라벨 − 쪽번호 칼럼 6.5
LIST_LINE_MM = 15 * (25.4 / 72)                 # 항목 행송 15pt
LIST_GAP_MM = 3.0                               # li.lof margin-top (theme.css와 동행)
# 면 배치 계획값 — toc 높이 모델(±0.14mm 실측 적합)과 달리 **보수 계획값**이다: 여기서는
# 어느 면에 몇 항목을 싣나만 정하고, 실제 바닥은 pass1 실측이 물리 한계와 대조해 die로
# 지킨다(모델은 계획자, pass1.pdf가 검증자 — 목차와 같은 원칙). 보수 방향 = top은 실제보다
# 낮게(늦게) 잡아 용량을 과소평가한다. 미학 한계 233 대비 물리 252의 19mm 헤드룸이
# 계획값 오차(±1mm대)를 흡수하고, 넘어서면 실측 die가 세운다.
LIST_TOP_MM = 62.5        # 표제면 첫 행 글리프 top(표제 30pt + 붕괴마진 14mm — toc 1면 61.43과 동일 구조 + 15pt 행박스 하프리딩)
LIST_TOP_CONT_MM = 46.0   # 연속면(표제 없음, margin-top 3mm) 보수값
LIST_TAIL_MM = 2.0        # 마지막 행 디센더 여유(행박스 누적이 이미 디센더를 덮는 위의 순여유)


def _list_row_lines(text_html, prof=None):
    """차례 항목 한 건의 렌더 행 수 — keep-all 어절 그리디(_wrap_lines와 같은 원리),
    서체·급수·가용 폭만 차례 규격(.lof-title Light 9.5pt / 82.5mm)."""
    from html import unescape as _unesc
    font = _font(LIST_TITLE_FONT[0])
    size = LIST_TITLE_FONT[1]
    limit = LIST_AVAIL_MM * _prof(prof)["fold_safety"]
    words = _unesc(text_html).split()
    if not words:
        return 1
    lines, cur = 1, ""
    for w in words:
        trial = (cur + " " + w) if cur else w
        if _string_width_mm(font, trial, size) <= limit or not cur:
            cur = trial
        else:
            lines += 1
            cur = w
    return lines


def plan_list_kind_pages(entries, prof=None):
    """한 종(그림/표)의 차례 항목을 면 단위로 나눈다 → [(rows, predicted_bottom_mm)].

    순차 채움인 이유(목차 plan_toc_pages의 DP와 다른 선택): 차례 항목에는 고아 제약
    (장-첫 절 결속 같은)이 없고 어느 STYLE.md도 차례 면 균형을 규범으로 선언하지 않는다 —
    제약 없는 순차 채움은 면 수 최소를 자명하게 만족하고 결정론이라 재계획 축도 필요 없다."""
    P = _prof(prof)
    limit = P["limit_aesthetic_mm"]
    pages, cur, bottom = [], [], 0.0
    for e in entries:
        h = _list_row_lines(e["text"], P) * LIST_LINE_MM
        if not cur:
            cur = [e]
            bottom = (LIST_TOP_MM if not pages else LIST_TOP_CONT_MM) + h
            continue
        nb = bottom + LIST_GAP_MM + h
        if nb + LIST_TAIL_MM > limit:
            pages.append((cur, round(bottom + LIST_TAIL_MM, 2)))
            cur = [e]
            bottom = LIST_TOP_CONT_MM + h
        else:
            cur.append(e)
            bottom = nb
    if cur:
        pages.append((cur, round(bottom + LIST_TAIL_MM, 2)))
    return pages


def list_page_sections(kind, entries, prof=None):
    """한 종의 차례 면 콘텐츠 블록들 → ([html, …], [predicted_bottom_mm, …]).

    표제(.lists-word)는 첫 면에만 — Contents 워드마크와 동일 규격이고, 연속면 생략은
    다면 목차 2면 이후의 정체성 규범과 같은 원리다. 항목은 목차와 같은 .tocpg[data-mk]
    자리표를 쓰므로 2-pass 쪽번호 스탬핑·칼럼 폭 고정 계약이 그대로 적용된다."""
    out, bottoms = [], []
    for pi, (rows, bottom) in enumerate(plan_list_kind_pages(entries, prof)):
        head = f'<div class="lists-word">{LIST_WORD[kind]}</div>' if pi == 0 else ""
        lis = "\n".join(
            f'<li class="lof"><span class="lof-no">{e["label"]}</span>'
            f'<span class="lof-title">{e["text"]}</span>'
            f'<span class="toc-leader"></span>'
            f'<span class="tocpg" data-mk="{e["mk"]}">00</span></li>' for e in rows)
        out.append(head + '<ol class="toc lists">' + lis + "</ol>")
        bottoms.append(bottom)
    return out, bottoms


H2_RE = re.compile(r"<h2>(?P<inner>.*?)</h2>", re.S)
TAG_RE = re.compile(r"<[^>]+>")


def md_to_html(md: str, book_dir: Path | None = None, ch_idx: int | None = None,
               sec_marker: str | None = None, sec_titles_out: list | None = None,
               fg_counter: list | None = None, fg_marks_out: list | None = None) -> str:
    """markdown subset -> html, with ::: callout directive support.

    sec_marker(예 "ch01")를 주면 **비콜아웃 청크의 렌더 결과**에 있는 `<h2>`에만 절
    쪽번호 마커 `@@chNNsMM@@`를 주입하고, 주입한 제목을 순서대로 `sec_titles_out`에
    넣는다.

    fg_counter([n], 호출자 보유)를 주면 라벨(`그림 n-m`)이 붙는 그림에만 쪽번호 마커
    `@@fgNNN@@`을 figure 첫 자식으로 주입하고 (마커명, 라벨, 캡션 텍스트)를 순서대로
    `fg_marks_out`에 넣는다 — 라벨·캡션은 그림 차례 별면 발행의 재료이며, 지면 캡션과
    같은 문자열이 한 경로에서 나와야 차례↔캡션 대조 축(G14-E)이 성립한다.
    카운터가 장 경계를 넘어 이어지는 **전역 카운터**인 이유: 마커명은 회수 딕트의 키라
    문서 전역에서 유일해야 한다 — 장별 리셋(fg{장}-{n})은 라벨 문법(`그림 n-m`)과 어휘가
    겹쳐 보이지만 회수·재스탬핑 어디에도 장 번호가 필요 없고 자릿수만 늘린다. 절 목록과 절 마커가 한 경로에서 나오게 하는 것이 요점이다 —
    구 구현은 원고 줄 스캔으로 목록을 만들고(콜아웃 안 `## ` 제외) 마커는
    `re.sub(r"<h2>", …, body_html)`로 렌더 결과 전체에 매겼기 때문에
      ㉠ 콜아웃 안 `## `  → 마커만 생기고 목록엔 없다(번호가 한 칸씩 밀림)
      ㉡ 코드블록 안 `## ` → 목록엔 있고 마커는 없다(반대 방향 이탈)
      ㉢ 리터럴 `<h2>` / `:::` 미종료
    가 전부 두 경로를 어긋나게 했다(적대검토 D3, 판정 V1: 절 쪽번호 10/15 오배정이
    전 게이트를 통과해 출하). 이 구조에서는 세 경우가 자동으로 일치한다.
    """
    out, lines, buf = [], md.split("\n"), []
    sec_no = [0]

    def mark(chunk_html):
        if sec_marker is None:
            return chunk_html
        def rep(m):
            sec_no[0] += 1
            inner = m.group("inner")
            if sec_titles_out is not None:
                from html import unescape as _unesc
                sec_titles_out.append(re.sub(r"\s+", " ", _unesc(TAG_RE.sub("", inner))).strip())
            return (f'<h2><span class="pgmark">@@{sec_marker}s{sec_no[0]:02d}@@</span>'
                    f'{inner}</h2>')
        return H2_RE.sub(rep, chunk_html)

    def flush():
        if buf:
            out.append(mark(MD.render("\n".join(buf))))
            buf.clear()
    i = 0
    while i < len(lines):
        m = CALLOUT_RE.match(lines[i].strip())
        if m:
            flush()
            kind, title = m.group(1), m.group(2).strip()
            body, i = [], i + 1
            while i < len(lines) and lines[i].strip() != ":::":
                body.append(lines[i]); i += 1
            i += 1
            if kind == "pull":
                ls = [l.strip() for l in body if l.strip()]
                quote_t = ls[0] if ls else ""
                speaker = ls[1] if len(ls) > 1 else ""
                sp = f'<div class="pull-speaker">{speaker}</div>' if speaker else ""
                out.append(f'<section class="pullquote"><div class="pull-text">{quote_t}</div>{sp}</section>')
            elif kind == "stat":
                ls = [l.strip() for l in body if l.strip()]
                value = ls[0] if ls else ""
                label = ls[1] if len(ls) > 1 else ""
                out.append(f'<div class="stat"><span class="stat-value">{value}</span>'
                           f'<span class="stat-label">{label}</span></div>')
            else:
                t = f'<div class="callout-title">{title}</div>' if title else ""
                out.append(f'<div class="callout callout-{kind}">{t}{MD.render(chr(10).join(body))}</div>')
        else:
            buf.append(lines[i]); i += 1
    flush()
    html = "\n".join(out)
    # 이미지 문단 -> figure/figcaption (alt=캡션, title="출처: …")
    # 그림 캡션 계약(STYLE 캡션 규약): 장별 자동 번호 `그림 n-m` 라벨을 앞에 단다
    # (표 캡션 tbl-caption의 `표 n-m.`과 동일 문법 — 한 책 안에서 캡션 문법 통일).
    fig_no = [0]
    def fig(m):
        src, alt, title = m.group("src"), m.group("alt") or "", m.group("title") or ""
        cap = alt
        if title:
            cap = f"{cap} · {title}" if cap else title
        fmark = ""
        if cap and ch_idx is not None:
            fig_no[0] += 1
            lab = f"그림 {ch_idx}-{fig_no[0]}"
            if fg_counter is not None:
                fg_counter[0] += 1
                fmk = f"fg{fg_counter[0]:03d}"
                if fg_marks_out is not None:
                    fg_marks_out.append((fmk, lab, cap))
                # 앵커는 figure 자신 — 마커를 품는 figure에만 mk-anchor 클래스를 발행하고
                # theme.css `.mk-anchor{position:relative}`가 회수 면 = 그림 실면을 만든다.
                # 앵커가 없으면 .pgmark{position:absolute}가 문서 원점(1면)에 붙는데,
                # 그 상태는 전수 회수 사후조건을 통과한다 — 포함 단조 사후조건이 잡는다.
                # (figure 전역 position:relative는 금지 — 페인트 순서가 밀려 마커 없는
                # 기존 책의 PDF 텍스트 스트림까지 바뀐다. theme.css 주석 참조)
                fmark = f'<span class="pgmark">@@{fmk}@@</span>'
            cap = f'<span class="fig-label">{lab}</span> {cap}'
        c = f"<figcaption>{cap}</figcaption>" if cap else ""
        # SVG 도해는 <img src> 대신 원문 인라인 — SVG-as-image 모드는 외부 @font-face를
        # 차단해 도해 <text>가 폴백 폰트로 렌더되므로.
        if book_dir and src.endswith(".svg") and src.startswith("../assets/"):
            svg_path = book_dir / "assets" / src[len("../assets/"):]
            if svg_path.exists():
                svg = svg_path.read_text(encoding="utf-8")
                svg = re.sub(r"^<!--bf:dsl=[^>]*-->\n?", "", svg)
                svg = re.sub(r'(<svg\b[^>]*?)\s+style="[^"]*"', r"\1", svg, count=1)
                svg = re.sub(r"<svg\b", '<svg style="width:100%;height:auto"', svg, count=1)
                # 사이드카 bf.width=twothirds — 세로형 도해가 전폭으로 부풀어 면을
                # 통째로 먹는 것을 막는다 (HTML 트랙은 float가 없어 폭이 유일한 레버).
                # 🚨 여기서 폭 수치를 만들지 않는다. 구 구현은 `width:66%`를 인라인으로
                # 박았고 그 값이 tokens.diagram.widths.twothirds와 독립이라 두 값이
                # 갈라졌다(insight 66%×130=85.8mm vs 선언 86, magazine 66%×164=108.2 vs
                # 선언 100). 클래스만 발행하고 실수치는 theme.css의 $fig_twothirds_mm
                # 치환 = tokens 단일 진리원에 맡긴다.
                fig_cls = "svgfig"
                sidecar = book_dir / "diagrams" / (Path(src).stem + ".json")
                if sidecar.exists():
                    bf = json.loads(sidecar.read_text(encoding="utf-8")).get("bf", {})
                    if bf.get("width") == "twothirds":
                        fig_cls = "svgfig twothirds"
                if fmark:
                    fig_cls += " mk-anchor"
                # W7 배치 높이 상한 — render_diagrams가 metrics.fit에 내린 축소 폭을 전사한다.
                # 인라인 mm는 제2진리원이 아니다: 값의 출처는 tokens.diagram.maxHeightMm
                # 하나이고(render_diagrams figFitReport가 폭으로 역산), 여기는 그 결정의
                # 배치 전사일 뿐이다 — theme.css에 mm 리터럴을 적는 것과 달리 도해별로
                # 종횡비가 달라 CSS 상수로는 표현할 수 없다.
                fit_style = ""
                metrics_p = book_dir / "assets" / (Path(src).stem + ".metrics.json")
                if metrics_p.exists():
                    try:
                        fit = (json.loads(metrics_p.read_text(encoding="utf-8"))
                               .get("fit") or {})
                    except ValueError:
                        fit = {}
                    fw = fit.get("widthMm")
                    if (fit.get("verdict") == "shrunk"
                            and isinstance(fw, (int, float)) and not isinstance(fw, bool)
                            and fw > 0):
                        fit_style = f' style="width:{fw:g}mm"'
                return f'<figure class="{fig_cls}"{fit_style}>{fmark}{svg}{c}</figure>'
        if fmark:
            return f'<figure class="mk-anchor">{fmark}<img src="{src}" alt="{alt}">{c}</figure>'
        return f'<figure><img src="{src}" alt="{alt}">{c}</figure>'
    html = re.sub(
        r'<p><img src="(?P<src>[^"]+)" alt="(?P<alt>[^"]*)"(?: title="(?P<title>[^"]*)")?\s*/?></p>',
        fig, html)
    return html

def fig_width_css(tokens: dict) -> dict:
    """`{플레이스홀더명: CSS 길이}` — tokens.diagram.widths(mm)의 CSS 전사.

    값이 없거나 수치가 아니면 `100%`로 떨어진다. 조용한 폴백처럼 보이지만 그 상태는
    G16-SYNC widths 축이 HARD FAIL로 이미 막았고(build.py는 렌더 앞에서 죽는다),
    --g16-warn-only 강등 시에만 여기까지 온다 — 그때는 렌더가 계속돼야 한다.
    """
    widths = (tokens.get("diagram") or {}).get("widths") or {}
    out = {}
    # 플레이스홀더명↔토큰 키 표는 g16_tokens에 하나만 둔다 — 표가 두 벌이면 게이트와
    # 빌더가 서로 다른 계약을 갖게 되고, 그 어긋남이야말로 이 단계가 없애려는 것이다.
    for key, ph in g16_tokens.FIG_WIDTH_KEYS.items():
        v = widths.get(key)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0:
            out[ph] = "100%"
        else:
            out[ph] = f"{v:g}mm"
    return out

def build(book_dir: Path, book: dict, outline: dict, style_dir: Path, skill: Path):
    global _FONTS_DIR
    _FONTS_DIR = skill / "assets" / "fonts"
    ts = book_dir / "typeset"
    ts.mkdir(exist_ok=True)
    (book_dir / "draft").mkdir(exist_ok=True)

    tokens = json.loads((style_dir / "tokens.json").read_text(encoding="utf-8"))
    key = book.get("brand") or tokens.get("brand_default", "#0E7C7B")
    # 구 구현은 `int(key.lstrip('#')[4:6], 16)`이라 3자리 hex(`#abc`)에 ValueError로 죽었다.
    # 색 해석은 g16_tokens 하나만 안다 — 게이트가 통과시킨 형식을 빌더가 못 읽으면
    # 두 곳이 서로 다른 "유효한 색"을 갖게 된다. 색이 아닌 값은 G16-BRAND가 FAIL로
    # 이미 막았으므로 여기 오는 경우는 --g16-warn-only 강등뿐이고, 그때는 렌더가
    # 계속돼야 하므로 팩 기본색으로 떨어진다.
    r_, g_, b_ = (g16_tokens.parse_hex(key)
                  or g16_tokens.parse_hex(tokens.get("brand_default") or "")
                  or (14, 124, 123))
    cover_img = book_dir / "assets" / "cover.png"
    if not cover_img.exists():
        cover_img = book_dir / "assets" / "cover.jpg"

    tpl_text = (style_dir / "theme.html").read_text(encoding="utf-8")
    # toc_levels: 인쇄 목차에 노출하는 계층 수. 1이면 절 엔트리도, <h2>의 절 마커
    # (@@chNNsMM@@)도 발행하지 않는다 — 마커가 pages 딕트에 섞이면 decorate.py의
    # openers가 절 시작면을 장 오프너로 오인한다(magazine 폴리오 7면 누락의 원인).
    # 폴백값의 정본은 g16_tokens.TOC_LEVELS_DEFAULT — G16-SYNC 축 ③이 "부재 시 빌더가
    # 실제로 쓸 값"을 max_levels와 대조하므로 리터럴이 여기 따로 살면 판정이 갈라진다.
    toc_levels = tokens.get("toc_levels", g16_tokens.TOC_LEVELS_DEFAULT)
    # toc_lists: 그림·표 차례 옵트인(fg/tb 마커 발행 + 별면 조판). 선언이 없으면 발행 0 —
    # 기존 스타일 산출물은 바이트 수준 불변이어야 한다. 켜는 곳은 스타일 팩(tokens.json)
    # 또는 책 단위 book.json 덮어쓰기 — brand/toc_layout이 쓰는 것과 같은 자리다. 별면은
    # 앞부속 선택 요소(book-anatomy ⑨, 소책자 생략 권장)라 책이 스타일 기본을 덮을 수
    # 있어야 하고, 프로브·검증도 저장소 팩 변조 없이 이 경로로 옵트인한다.
    # off는 **부재(None)와 빈 리스트만**이다 — `or []`로 받으면 0/false/"" 같은 falsy
    # 오값이 조용히 off로 삼켜져 "오값은 die" 계약이 깨진다(적대검증 s4-verdict ④).
    # 원소도 str 여부를 먼저 본다 — unhashable 원소(리스트·딕트)가 `in` 검사에서
    # TypeError 트레이스백으로 죽으면 die 메시지 계약이 깨진다(같은 판정 ④).
    toc_lists = book.get("toc_lists", tokens.get("toc_lists"))
    if toc_lists is None:
        toc_lists = []
    if (not isinstance(toc_lists, list)
            or any(not isinstance(v, str) or v not in TOC_LIST_KINDS for v in toc_lists)):
        die(f"toc_lists가 올바르지 않다(현재: {toc_lists!r}) — {sorted(TOC_LIST_KINDS)}의 "
            f"부분집합 리스트여야 한다(선언 위치: styles/{style_dir.name}/tokens.json 또는 "
            "book.json의 책 단위 덮어쓰기. off는 미선언 또는 빈 리스트만 — 0/false 같은 "
            "falsy 오값도 die다). "
            "오값을 조용히 무시하면 차례가 꺼진 것과 선언 오타가 구별되지 않는다")
    emit_fg = "figures" in toc_lists
    emit_tb = "tables" in toc_lists
    css_src = (style_dir / "theme.css").read_text(encoding="utf-8")
    # $key_label: 브랜드를 **명도만** 낮춰 tokens.json `key_label`이 지정한 배경 위에서
    # 대비 하한을 처음 넘기는 값. 키색을 그대로 쓰면 미달인 자리(magazine
    # .callout-title은 tint 위 4.45 < 4.5)를 브랜드가 바뀌어도 자동으로 맞춘다.
    # 파생 산식은 g16_tokens에 하나만 있고 G16-BRAND도 같은 함수의 결과를 판정한다.
    key_label = g16_tokens.key_label_hex(tokens, css_src, book.get("brand")) or key
    # $fig_full_mm / $fig_twothirds_mm: 도해 figure의 실렌더 폭. tokens.diagram.widths가
    # **단일 진리원**이고 CSS는 그 파생이다 — 같은 값을 render_diagrams.mjs가 글자 하한의
    # pt 환산 기준으로 쓰므로(scalePt = widths[key]×2.835 ÷ viewBox폭) 두 곳이 갈라지면
    # 게이트가 실제와 다른 폭으로 판정한다(magazine 151 선언 / 164 실렌더 = 1.086배 과엄격).
    # 계약 성립(플레이스홀더 실존 · mm 리터럴 부재)은 G16-SYNC widths 축이 렌더 전에 지킨다.
    fig_widths = fig_width_css(tokens)
    css = Template(css_src).safe_substitute(
        fonts_dir=(skill / "assets" / "fonts").as_uri(),
        key_color=key,
        key_tint=f"rgba({r_},{g_},{b_},0.08)",
        key_label=key_label,
        **fig_widths,
    )

    # refit-params.json: 장별 자간 미세조정(pagination.md §5 L2). 주의 — inline
    # letter-spacing은 테마 기본값을 대체하므로 refit.py가 (테마 기본 + Δ) 절대값을 준다.
    refit = {}
    rp = book_dir / "refit-params.json"
    if rp.exists():
        refit = json.loads(rp.read_text(encoding="utf-8"))

    toc_rows, sections, tocmap_items, first_pull = [], [], [], None
    sec_by_ch = {}
    # fg/tb 전역 카운터 + 발행 대장 [(마커명, 소속 장 idx)] — 발행 순서 = 지면 순서라
    # 이 대장이 그대로 포함 단조 사후조건의 기대 집합·순서가 된다. entries는 차례 별면의
    # 재료(라벨·캡션 텍스트) — 지면 캡션과 같은 경로에서 나온 같은 문자열이어야
    # 차례↔캡션 대조 축(G14-E)이 성립한다.
    fg_counter, tb_counter = [0], [0]
    fg_marks, tb_marks = [], []
    fg_entries, tb_entries = [], []
    for idx, ch in enumerate(outline["chapters"], 1):
        mk = f"ch{idx:02d}"
        src = book_dir / "chapters" / ch["file"]
        raw = src.read_text(encoding="utf-8")
        # strip the leading H1 (title comes from outline)
        raw = re.sub(r"^#\s+.*\n", "", raw, count=1)
        # 목차 이미지 맵(magazine $tocmap): 챕터 첫 **래스터** 컷 4~6장. SVG 도해는
        # 제외한다 — 본문은 SVG를 인라인해 @font-face를 살리지만(md_to_html의 svgfig
        # 경로 주석) 여기는 <img src>라 SVG-as-image 모드가 되고, 도해 <text>가 폴백
        # 폰트로 떨어져 **목차 면에 Type3 글리프**가 유입된다(G2 FAIL — w7-b3 실측:
        # 도해가 장 첫 이미지인 magazine 북은 역대 전부 이 경로로 실패했다). 64×28mm
        # cover-크롭에서 도해는 시각적으로도 의미가 없으므로 래스터 컷만 쓴다.
        # 캡션은 해당 쪽번호만 — 좌측 리스트와 같은 .tocpg[data-mk] 마크업이라 2-pass
        # 스탬핑이 같이 채운다.
        img_m = next((m for m in re.finditer(r"!\[[^\]]*\]\((\.\./assets/[^) \"]+)", raw)
                      if not m.group(1).endswith(".svg")), None)
        if img_m and len(tocmap_items) < 5:
            tocmap_items.append(
                f'<figure><img src="{img_m.group(1)}" alt="">'
                f'<figcaption><span class="tocpg" data-mk="{mk}">00</span></figcaption></figure>')
        if first_pull is None:
            pm = re.search(r"^::: pull\n(.+)$", raw, re.M)
            if pm:
                first_pull = pm.group(1).strip()
        # 목차 2레벨(STYLE 목차 문법): 절 제목과 절 쪽번호 마커는 **한 경로**에서 나온다 —
        # md_to_html이 비콜아웃 청크를 렌더하는 그 자리에서 <h2>에 마커를 주입하고 주입한
        # 제목을 순서대로 돌려준다. 원고 줄 스캔(구 in_callout 루프)은 삭제됐다.
        # toc_levels < 2면 소비자가 없으므로 수집도 발행도 하지 않는다.
        sec_titles = []
        ch_fg = []
        body_html = md_to_html(raw, book_dir, idx,
                               sec_marker=(mk if toc_levels >= 2 else None),
                               sec_titles_out=sec_titles,
                               fg_counter=(fg_counter if emit_fg else None),
                               fg_marks_out=ch_fg)
        fg_marks.extend((fmk, idx) for fmk, _lab, _txt in ch_fg)
        fg_entries.extend({"mk": fmk, "label": lab, "text": txt} for fmk, lab, txt in ch_fg)
        sec_by_ch[idx] = sec_titles
        # 표 캡션 계약: 콘텐츠가 "[표] 제목 | 자료: 출처" 문단을 준 표만 라벨을 단다.
        # 자동 필러 라벨 금지 — 캡션 없는 표는 라벨 없이 그대로 렌더된다.
        tno = [0]
        def wrap_tbl(m):
            tno[0] += 1
            title = m.group(1).strip()
            source = (m.group(2) or "").strip()
            tmark, tcls = "", "tablewrap"
            if emit_tb:
                # 앵커는 .tablewrap 자신 — fg 마커와 동일 계약(mk-anchor 조건 발행)
                tb_counter[0] += 1
                tmk = f"tb{tb_counter[0]:03d}"
                tb_marks.append((tmk, idx))
                # 차례 항목 = 지면 캡션(.tbl-caption)과 같은 라벨·제목 문자열(G14-E 대조 재료)
                tb_entries.append({"mk": tmk, "label": f"표 {idx}-{tno[0]}.", "text": title})
                tmark = f'<span class="pgmark">@@{tmk}@@</span>'
                tcls = "tablewrap mk-anchor"
            src_html = f'<div class="tbl-source">자료: {source}</div>' if source else ""
            return (f'<div class="{tcls}">{tmark}<div class="tbl-caption">'
                    f'<span class="no">표 {idx}-{tno[0]}.</span> {title}</div>'
                    f'{m.group(3)}{src_html}</div>')
        body_html = re.sub(
            r"<p>\[표\]\s*(.+?)(?:\s*\|\s*자료\s*[:：]\s*(.+?))?</p>\s*(<table>.*?</table>)",
            wrap_tbl, body_html, flags=re.S)
        # 전면 요소(풀퀘트)는 다단 chapter-body 밖으로 분리
        body_html = re.sub(
            r'(<section class="pullquote">.*?</section>)',
            r'</div>\1<div class="chapter-body">',
            body_html, flags=re.S)
        summary = ch.get("summary") or ""
        sec = (
            f'<section class="chapter" id="{mk}">\n'
            f'<div class="opener"><span class="pgmark">@@{mk}@@</span>'
            f'<div class="opener-num">{idx:02d}</div>'
            f'<h1 class="opener-title">{ch["title"]}</h1>'
            f'<p class="opener-summary">{summary}</p></div>\n'
            f'<div class="chapter-body">{body_html}</div>\n</section>')
        # 풀퀘트 분리로 생긴 빈 chapter-body 제거 (백지면 방지) — refit 주입보다 먼저
        sec = re.sub(r'<div class="chapter-body">\s*</div>', "", sec)
        prm = refit.get(Path(ch["file"]).stem, {})
        if prm.get("letter_spacing_em") is not None:
            sec = sec.replace('<div class="chapter-body">',
                              f'<div class="chapter-body" style="letter-spacing:{prm["letter_spacing_em"]}em">')
        sections.append(sec)
        # data-sum: 목차 한줄 카피. outline의 toc_line(목차 전용 완결 카피)이 있으면 그것을,
        # 없으면 summary 40자 말줄임. 속성이라 이를 쓰지 않는 테마는 무시한다.
        tsum = re.sub(r"\s+", " ", ch.get("toc_line") or summary).strip()
        if len(tsum) > 40:
            tsum = tsum[:40].rstrip(" ,.·") + "…"
        toc_rows.append({
            "kind": "ch", "title": ch["title"], "mk": mk, "lines": 1,
            # num·sum: 대안 레이아웃(display-numeral)의 행 마크업 재조립 재료 — 기본
            # 레이아웃은 아래 "li" 완성본만 쓰므로 이 두 키는 소비자가 없어도 무해하다.
            "num": idx, "sum": tsum,
            # has_sec: 이 장이 목차에 실을 절을 가졌는가. 장 고아 금지 제약은 떼어놓을
            # 첫 절이 있을 때만 의미가 있다(plan_toc_pages 주석 참조).
            "has_sec": bool(sec_titles),
            "li": f'<li data-sum="{_esc(tsum, quote=True)}"><span class="toc-title">{ch["title"]}</span>'
                  f'<span class="toc-leader"></span>'
                  f'<span class="tocpg" data-mk="{mk}">00</span></li>'})
        # 2레벨(절) 엔트리 — 색 위계(1레벨 cyan / 2레벨 teal)는 테마 CSS가 결정
        for sidx, stitle in enumerate(sec_titles, 1):
            smk = f"{mk}s{sidx:02d}"
            toc_rows.append({
                "kind": "sec", "title": stitle, "mk": smk, "lines": 1,
                "li": f'<li class="toc-sec"><span class="toc-sec-title">{_esc(stitle)}</span>'
                      f'<span class="toc-leader"></span>'
                      f'<span class="tocpg" data-mk="{smk}">00</span></li>'})

    # ---- 장 제목 계약(D9) — 검사를 무력화하는 제목을 빌드 단계에서 막는다 ----
    ch_titles = [ch["title"] for ch in outline["chapters"]]
    if any(not t.strip() for t in ch_titles):
        die("빈 장 제목이 있다 — 빈 제목은 사후조건('' in txt)과 G14-A(_norm(title)[:10] "
            "가드)를 항등적으로 통과시켜 그 장이 어떤 쪽번호 검사도 받지 않는다. "
            "outline.json의 chapters[].title을 채울 것")
    keyed = {}
    for t in ch_titles:
        k = re.sub(r"\s+", "", t)[:10]
        keyed.setdefault(k, []).append(t)
    dup = {k: v for k, v in keyed.items() if len(v) > 1}
    if dup:
        die(f"장 제목이 앞 10자까지 동일한 짝이 있다: {list(dup.values())[:2]}. "
            "G14-A는 목차에서 '첫 매치 스팬'과 페어링하므로 둘 중 하나는 반드시 "
            "'인쇄 X ≠ 폴리오 Y' 오탐이 되고, find_toc_pages의 covered 집합도 전 제목에 "
            "도달하지 못해 목차 면 확장이 폭주한다 — 대응: 제목을 구별되게 고치거나"
            "('부록 A'/'부록 B') 장을 병합할 것")

    # ---- 목차 면 발행 + 렌더 후 실측 검증 ----
    # 모델(폭·높이 추정)은 계획자일 뿐이고, **pass1.pdf가 검증자**다. 추정이 틀리면 목차가
    # 조용히 넘치고 Chromium이 문서 전체를 shrink-to-fit으로 줄이며, 남는 신호는 G1-SCALE
    # 하나인데 tocplan.json은 "목차 정상"을 증언해 진단을 오도한다(적대검토 D1·D2·D8).
    # 그래서 스팬 bbox로 실제 바닥을 재고, 물리 한계를 넘으면 **실측 접힘 실태로 한 번
    # 재계획해 pass1을 다시 렌더**한다(결정론·최대 1회).
    style_name = style_dir.name
    tpl_src = tpl_text
    overflow_token = tokens.get("toc_overflow")
    if overflow_token not in TOC_OVERFLOW_MULTIPAGE:
        die(f"styles/{style_name}/tokens.json에 `toc_overflow` 선언이 없거나 값이 올바르지 "
            f"않다(현재: {overflow_token!r}) — html 엔진 스타일은 {'|'.join(TOC_OVERFLOW_MULTIPAGE)} "
            "중 하나를 반드시 선언해야 한다(references/extending.md 참조). 선언이 없으면 "
            "다면·단면 분기가 코드(theme.html의 BF:TOCPAGE 유무)에만 숨어 tokens.json만 "
            "보고는 그 스타일의 목차 동작을 알 수 없다")
    template_multipage = "<!--BF:TOCPAGE" in tpl_src
    multipage = TOC_OVERFLOW_MULTIPAGE[overflow_token]
    if multipage != template_multipage:
        die(f"styles/{style_name}/tokens.json toc_overflow={overflow_token!r}"
            f"({'다면' if multipage else '단면'})가 theme.html 실물(BF:TOCPAGE 블록 "
            f"{'있음(다면)' if template_multipage else '없음(단면)'})과 어긋난다 — 계약(토큰)과 "
            "실물(템플릿)의 디싱크는 조용히 넘어가지 않는다. tokens.json의 toc_overflow를 "
            "고치거나 theme.html의 BF:TOCPAGE 블록을 맞출 것")
    # 다면 목차만 캘리브레이션 프로파일이 필요하다 — toc_layout 이름으로 명시 해석하고
    # (기본값 폴백 금지), 이름에 대응하는 프로파일이 없으면 toc_profile()이 die한다.
    prof = toc_profile(style_name, tokens) if multipage else None

    # ── 대안 목차 레이아웃 (W6 S6) ────────────────────────────────────────────
    # book.json `toc_layout`은 팩 기본(tokens.json toc_layout)이 아닌 레이아웃을 **책
    # 단위로** 켜는 선언이다(brand가 brand_default를 덮는 것과 같은 자리). 미선언이면
    # active == 기본이고 아래 분기 전부가 잠들어 산출이 바이트 수준으로 불변이다.
    # 실물은 팩의 오버레이 CSS(toc-<이름>.css) — theme.css에 섞으면 G16-SYNC 축 ⑤의
    # 기본 레이아웃 급수 잠금이 오버레이 리터럴에 오염되므로 파일을 갈라 두고, 선언된
    # 빌드에서만 theme.css 뒤에 이어붙인다(뒤가 이긴다). 오버레이 자체의 불변식은
    # g16_tokens.overlay_findings가 렌더 전에 지킨다.
    declared_layout = tokens.get("toc_layout")
    active_layout = book.get("toc_layout") or declared_layout
    if active_layout != declared_layout:
        spec = g16_tokens.TOC_LAYOUTS.get(active_layout)
        if spec is None:
            die(f"book.json toc_layout={active_layout!r} — 카탈로그 밖이다. 허용값 "
                f"{'|'.join(sorted(g16_tokens.TOC_LAYOUTS))} (g16_tokens.TOC_LAYOUTS가 "
                f"단일 진리원)")
        if style_name not in spec["styles"]:
            die(f"book.json toc_layout={active_layout!r}는 {'/'.join(spec['styles'])}가 구현한 "
                f"레이아웃인데 style={style_name}이 선언했다 — 구현 없는 이름 전환은 "
                f"기본 레이아웃 CSS 위에 남의 문법 마크업을 얹는다")
        if multipage:
            die(f"book.json toc_layout 전환은 단면 목차(toc_overflow=single) 스타일 전용이다 — "
                f"다면 스타일({style_name})의 레이아웃 전환은 높이 모델 17상수 재적합 없이는 "
                f"예측이 전부 허수가 된다(toc_profile 캘리브레이션 참조)")
        if toc_levels >= 2:
            die(f"toc_layout={active_layout!r} 전환은 레벨 1 목차만 구현돼 있다 — "
                f"toc_levels={toc_levels}면 절 엔트리 행 마크업이 없어 절이 조용히 "
                f"목차에서 빠진다")
        overlay_p = style_dir / f"toc-{active_layout}.css"
        if not overlay_p.exists():
            die(f"styles/{style_name}에 toc_layout={active_layout!r}의 오버레이 실물 "
                f"({overlay_p.name})이 없다 — 선언은 카탈로그에 있으나 이 팩에 CSS 구현이 "
                f"없다(TOC_LAYOUTS[...]['styles'] 선언과 실물이 갈라진 상태)")
        css += "\n" + Template(overlay_p.read_text(encoding="utf-8")).safe_substitute(
            fonts_dir=(skill / "assets" / "fonts").as_uri(),
            key_color=key, key_tint=f"rgba({r_},{g_},{b_},0.08)", key_label=key_label,
            **fig_widths)
    tocplan = {"style": style_name, "toc_levels": toc_levels,
               "rows": len(toc_rows),
               "section_markers": sum(len(v) for v in sec_by_ch.values())}
    # 그림·표 차례 별면 계획 — 옵트인 + 다면 목차 스타일 전용(LIST_* 주석의 근거).
    # 항목이 0인 종은 면을 만들지 않는다(빈 차례 면은 anatomy 위반이고 정보가 0이다).
    n_list_pages, list_specs, list_bottoms = 0, [], []
    if toc_lists:      # 옵트인 스타일만 — 미선언 스타일의 tocplan은 종전과 동일하게 유지
        if not multipage:
            die(f"styles/{style_name}: toc_lists는 다면 목차(toc_overflow=paginate) 스타일 "
                "전용이다 — 차례 별면은 BF:TOCPAGE 복제 배관으로만 발행되므로 단면 목차 "
                "스타일의 선언은 조용한 발행 0이 된다. 선언을 지우거나 다면 목차 스타일을 "
                "쓸 것")
        lf = _font(LIST_LABEL_FONT[0])
        for kind, ents in (("fg", fg_entries), ("tb", tb_entries)):
            for e in ents:
                # 라벨 칼럼은 16mm 고정 flex-basis — 넘치면 라벨이 제목 위로 흐른다.
                # 렌더 전에 세운다(현실 한계: 장 99·항목 99까지 여유).
                w = _string_width_mm(lf, e["label"], LIST_LABEL_FONT[1])
                if w > LIST_LABEL_MM - 0.5:
                    die(f"차례 라벨 '{e['label']}' 폭 {w:.1f}mm가 라벨 칼럼 "
                        f"{LIST_LABEL_MM}mm를 넘는다 — 장·항목 번호 자릿수를 확인할 것")
            if not ents:
                continue
            secs, bots = list_page_sections(kind, ents, prof)
            list_specs.extend(secs)
            list_bottoms.extend(bots)
        n_list_pages = len(list_specs)
        tocplan.update({"toc_lists": toc_lists,
                        "fig_markers": len(fg_marks), "tbl_markers": len(tb_marks),
                        "list_pages": n_list_pages,
                        "list_predicted_bottom_mm": list_bottoms})
    body_pt = tokens.get("body_pt")
    if not body_pt:
        warn(f"styles/{style_name}/tokens.json에 body_pt가 없다 — 렌더 후 실측 검증이 "
             "전역 축소 배율을 역산할 수 없어 실측 바닥을 축소 좌표 그대로 읽는다")

    env = dict(os.environ)
    env["NODE_PATH"] = subprocess.run(["npm", "root", "-g"], capture_output=True,
                                      text=True).stdout.strip()
    printer = skill / "scripts" / "print_pdf.mjs"
    pdf1 = ts / "pass1.pdf"
    page1 = ts / "book.html"

    measured_lines = {}        # mk -> 실측 렌더 행 수 (재계획 입력)
    replanned = False
    for attempt in range(2):
        if multipage:
            overflow_titles = toc_row_metrics(toc_rows, prof=prof)
            for r in toc_rows:                       # 실측 접힘 실태를 하한으로 반영
                r["lines"] = max(r["lines"], measured_lines.get(r["mk"], 1))
            if overflow_titles:
                die("목차 제목이 어절 단위로도 가용 폭에 들어가지 않는다(word-break:keep-all이라 "
                    f"어절 중간 개행 불가 → 가로 넘침): {overflow_titles[:3]}. "
                    "outline.json의 제목을 줄이거나 어절을 나눌 것")
            limit_used = prof["limit_aesthetic_mm"]
            spans = plan_toc_pages(toc_rows, prof=prof)
            if spans is None:
                limit_used = prof["limit_physical_mm"]
                spans = plan_toc_pages(toc_rows, prof["limit_physical_mm"], prof=prof)
                zero_sec = sum(1 for r in toc_rows if r["kind"] == "ch" and not r.get("has_sec"))
                warn(f"목차 미학 한계 {prof['limit_aesthetic_mm']}mm 해 없음 — 물리 한계 "
                     f"{prof['limit_physical_mm']}mm로 폴백했다(절 0개 장 {zero_sec}개). "
                     "STYLE.md가 규범으로 선언한 여백 리듬이 그만큼 침해된다")
            if spans is None:
                die("목차 분할 해 없음 — 물리 한계 "
                    f"{prof['limit_physical_mm']}mm 안에 들어가는 분할이 존재하지 않는다. "
                    "원인은 보통 ㉠분할점 부족(절이 0개인 장이 연속되면 그 구간은 통째로 한 "
                    "면에 들어간다) ㉡한 항목의 접힘 과다다 — 대응: 절이 없는 장에 절을 "
                    "추가하거나 장을 병합하고, 접히는 제목을 줄일 것. "
                    f"(장 {sum(1 for r in toc_rows if r['kind']=='ch')}개 / 절 "
                    f"{sum(1 for r in toc_rows if r['kind']=='sec')}개 / 접힘 "
                    f"{sum(1 for r in toc_rows if r['lines'] > 1)}건)")
            bottoms = [round(_toc_page_bottom(toc_rows, i, j, i == 0, prof), 2) for (i, j) in spans]
            over = [b for b in bottoms if b > prof["limit_physical_mm"]]
            if over:
                die(f"목차 면 예측 바닥 {over}mm > 물리 한계 {prof['limit_physical_mm']}mm — "
                    "분할 로직 결함(높이 모델과 제약을 재확인할 것)")
            tpl_text = expand_toc_pages(tpl_src, len(spans) + n_list_pages)
            toc_pages_html = {}
            for pi, (i, j) in enumerate(spans, 1):
                toc_pages_html[f"toc_{pi}"] = ('<ol class="toc">'
                                               + "\n".join(_li_with_reserve(r, prof)
                                                           for r in toc_rows[i:j])
                                               + "</ol>")
                toc_pages_html[f"toc_mod_{pi}"] = "" if pi == 1 else "toc-cont"
            # 그림·표 차례 별면 — 목차 뒤 연속 복제본. toc-cont로 Contents 워드마크·커넥터를
            # 감추고 사이드바·걸침 아이콘(면의 정체성)은 유지한다. 표제는 블록 안
            # .lists-word가 진다(list_page_sections).
            for li, sec_html in enumerate(list_specs, len(spans) + 1):
                toc_pages_html[f"toc_{li}"] = sec_html
                toc_pages_html[f"toc_mod_{li}"] = "toc-cont lists-page"
            n_toc_pages = len(spans)
            tocplan.update({"toc_pages": n_toc_pages,
                            "page_rows": [j - i for (i, j) in spans],
                            "predicted_bottom_mm": bottoms,
                            "limit_used_mm": limit_used,
                            "folded_rows": [r["title"] for r in toc_rows if r["lines"] > 1]})
            print(f"목차 {n_toc_pages}면 발행 — 행 {[j - i for (i, j) in spans]}, "
                  f"예측 바닥 {bottoms}mm (미학 {prof['limit_aesthetic_mm']} / 물리 {prof['limit_physical_mm']})")
            limit_phys, limit_aes = prof["limit_physical_mm"], prof["limit_aesthetic_mm"]
        else:
            # 단면 목차 스타일 — 1면 고정. 넘치면 조용히 잘리므로 명시 실패.
            # 용량 계약은 **활성 레이아웃의 것**을 쓴다: 기본이면 toc_capacity, 대안이면
            # toc_capacity_alt[이름] — 행 문법이 다르면 top/pitch/tail 전부 다른 실측이라
            # 기본 용량으로 대안 레이아웃을 판정하면 예측이 통째로 허수다.
            if active_layout == declared_layout:
                cap_spec = tokens.get("toc_capacity")
            else:
                cap_spec = (tokens.get("toc_capacity_alt") or {}).get(active_layout)
                if not cap_spec:
                    die(f"styles/{style_name}/tokens.json에 `toc_capacity_alt`"
                        f"[{active_layout!r}] 선언이 없다 — 대안 레이아웃의 단면 용량 계약 "
                        f"없이는 넘침이 검사 없이 전역 축소로 간다"
                        f"(필수 키: {', '.join(TOC_CAPACITY_KEYS)})")
            pred = check_single_page_toc(style_name, toc_rows, cap_spec)
            tpl_text = tpl_src
            if active_layout == "display-numeral" and active_layout != declared_layout:
                # business 대형 번호 문법의 HTML 이식(레벨 1): 좌측 대형 장번호 칼럼 +
                # 우측 제목·우단 쪽번호, 리더 없음. .tocpg[data-mk]는 그대로라 2-pass
                # 스탬핑·G14-A가 레이아웃과 무관하게 성립한다.
                rows_html = "\n".join(
                    f'<li data-sum="{_esc(r["sum"], quote=True)}">'
                    f'<span class="toc-bn-num">{r["num"]:02d}</span>'
                    f'<span class="toc-title">{r["title"]}</span>'
                    f'<span class="tocpg" data-mk="{r["mk"]}">00</span></li>'
                    for r in toc_rows)
                toc_pages_html = {"toc": f'<ol class="toc toc-bn">{rows_html}</ol>'}
            else:
                toc_pages_html = {"toc": '<ol class="toc">'
                                         + "\n".join(r["li"] for r in toc_rows) + "</ol>"}
            n_toc_pages = 1
            bottoms = [round(pred, 2)]
            tocplan.update({"toc_pages": 1, "predicted_bottom_mm": bottoms})
            if active_layout != declared_layout:
                tocplan["toc_layout"] = active_layout   # 미선언 빌드의 tocplan은 불변
            limit_phys = limit_aes = float(cap_spec["bottom_mm"])

        tpl = Template(tpl_text)
        html = tpl.substitute(
            title=book.get("title", ""), subtitle=book.get("subtitle") or "",
            author=book.get("author", "bookforge"), date=book.get("date", ""),
            brand=key,
            cover_art=f"background-image:url('{cover_img.as_uri()}')" if cover_img.exists() else "",
            tocmap="\n".join(tocmap_items),
            **toc_pages_html,
            backquote=book.get("backquote") or first_pull or book.get("subtitle") or "",
            body="\n".join(sections),
            css=css,
        )
        page1.write_text(html, encoding="utf-8")
        r = subprocess.run(["node", str(printer), str(page1), str(pdf1)],
                           capture_output=True, text=True, env=env)
        if r.returncode != 0:
            sys.exit("HTML pass1 print failed:\n" + r.stderr)

        # pass 1: locate markers + 목차 면 실측. 회수는 종별 딕트로 분리한다(어휘 주석 참조)
        doc = fitz.open(pdf1)
        pass1_pages = doc.page_count
        pages_by_kind = {k: {} for k in MARKER_KINDS}
        for pno in range(doc.page_count):
            norm = re.sub(r"\s+", "", doc[pno].get_text())
            for m in MK_SCAN_RE.findall(norm):
                pages_by_kind[m[:2]].setdefault(m, pno + 1)
        # pages = ch 종만 — folio_offset·목차 스탬핑·북마크·decorate ctx가 전부 이걸 본다
        pages = pages_by_kind["ch"]
        toc_pnos = list(range(1, 1 + n_toc_pages))          # 0-base: 표지(0) 다음 연속
        # 차례 별면은 목차 바로 뒤 연속 — 앞부속 = 표지 1 + 목차 n_toc + 차례 n_list
        n_front = n_toc_pages + n_list_pages
        first_ch_abs = min(pages.values()) if pages else None
        if first_ch_abs is not None and first_ch_abs != n_front + 2:
            die(f"앞부속 구조 가정 위반 — 목차 {n_toc_pages}면+차례 {n_list_pages}면이면 "
                f"첫 장은 abs {n_front + 2}면이어야 하는데 {first_ch_abs}면이다. 목차·차례 "
                "면 실측 검증이 어느 면을 재야 하는지 알 수 없다(theme.html의 섹션 순서 확인)")
        scale = _measure_doc_scale(doc, (first_ch_abs or n_front + 2) - 1, body_pt)
        meas_bottoms = [round(_measure_page_text_bottom_mm(doc[p]) / scale, 2) for p in toc_pnos]
        list_pnos = list(range(1 + n_toc_pages, 1 + n_front))   # 0-base 차례 별면
        list_meas = [round(_measure_page_text_bottom_mm(doc[p]) / scale, 2) for p in list_pnos]
        if multipage:
            lines_now = {}
            for pi, p in enumerate(toc_pnos):
                i, j = spans[pi]
                got = _measure_row_lines(doc[p], toc_rows[i:j])
                if got is None:
                    warn(f"목차 {pi + 1}면의 행↔제목 매칭 실패 — 접힘 실태를 재지 못했다")
                else:
                    lines_now.update(got)
        # W5 재판정 N2: 실제 출력 PDF(pdf1 — 이 attempt가 이미 만든 것, 추가 렌더 아님)의
        # 물리 MediaBox 폭. `preferCSSPageSize:true`가 실제로 먹혔는지까지 포함한 **실측**이고,
        # theme.css `@page size`의 정적 값과 다를 수 있다(치환 실패·단위 오류 등) — 그래서
        # 정적 파싱이 아니라 이 값을 쓴다. 여백(margin)은 물리 PDF에서 독립 복원할 수 없어
        # (빈 PDF는 어디까지가 "여백"인지 모른다) 그 부분만 theme.css를 정적으로 읽는다.
        measured_trim_w_mm = doc[0].rect.width * PT_TO_MM
        doc.close()

        tocplan["render_scale"] = round(scale, 4)
        tocplan["measured_bottom_mm"] = meas_bottoms
        if multipage:
            tocplan["measured_folded_rows"] = sorted(k for k, v in lines_now.items() if v > 1)
            tocplan["model_folded_rows"] = sorted(r["mk"] for r in toc_rows if r["lines"] > 1)
        if scale < 0.995:
            warn(f"pass1 전역 축소 감지 — 배율 {scale:.4f}(본문 최빈 pt / 선언 {body_pt}pt). "
                 "목차 초과가 원인일 가능성이 높다")
        worst = max(meas_bottoms) if meas_bottoms else 0.0
        if worst > limit_phys:
            if multipage and attempt == 0:
                measured_lines = {k: v for k, v in lines_now.items()}
                replanned = True
                warn(f"목차 실측 바닥 {meas_bottoms}mm > 물리 한계 {limit_phys}mm "
                     f"(예측 {bottoms}mm) — 실측 접힘 실태로 1회 재계획한다. "
                     f"실측 접힘 {sum(1 for v in measured_lines.values() if v > 1)}건")
                continue
            die(f"목차 실측 바닥 {meas_bottoms}mm > 물리 한계 {limit_phys}mm "
                f"(예측 {bottoms}mm, 재계획 {'후' if replanned else '없음'}). "
                "목차가 판면을 넘으면 Chromium이 문서 전체를 축소한다 — "
                "제목을 줄이거나 장·절 구성을 조정할 것")
        for k, (pm, bm) in enumerate(zip(bottoms, meas_bottoms)):
            if abs(pm - bm) > TOC_MODEL_TOL_MM:
                warn(f"목차 {k + 1}면 높이 모델 이탈 — 예측 {pm}mm vs 실측 {bm}mm "
                     f"(허용 {TOC_MODEL_TOL_MM}mm). 상수가 낡았거나 폭 추정이 어긋났다")
        # 차례 별면 실측 — 계획값(LIST_*)은 보수 배치용이고 여기가 검증자다. 넘침의 결말은
        # 목차와 같은 전역 축소이므로 물리 한계는 die, 재계획 경로는 없다(항목은 정적이라
        # 재어도 결과가 같다 — 대응은 캡션 축약뿐이고 그건 원고의 일이다).
        if n_list_pages:
            tocplan["list_measured_bottom_mm"] = list_meas
            over_l = [b for b in list_meas if b > limit_phys]
            if over_l:
                die(f"그림·표 차례 실측 바닥 {list_meas}mm > 물리 한계 {limit_phys}mm"
                    f"(계획 {list_bottoms}mm) — 면이 넘치면 Chromium이 문서 전체를 "
                    "축소한다. 캡션을 줄이거나 LIST_* 계획값을 재실측할 것")
        if worst > limit_aes:
            warn(f"목차 실측 바닥 {worst}mm > 미학 한계 {limit_aes}mm — "
                 f"여백 리듬 규범 위반이 {worst - limit_aes:.1f}mm 남는다"
                 + (" (미학 한계 해 없어 물리 폴백)" if multipage and limit_used > limit_aes else ""))

        # W5 재판정 N2 — HTML 트랙 widths 값 축. 이게 없으면 `widths.full`이 재단폭(trim)
        # 이내이기만 하면(판면보다 커도) 기존 widths_relation_findings가 통과시킨다 — 6단계
        # 라벨 급수 강제가 그 부풀린 값으로 pt를 환산해 실제 판면(예: 130mm)에서는 하한(8pt)
        # 미달인 활자를 하한 검사가 통과시킨다(판정 K1/N2, 재현: widths.full=180 · 판면 130mm ·
        # 재단 182mm → 보고 pt × 130/180배 축소된 활자가 실 발행됨). typst 트랙 ③'과 대칭 —
        # 판면폭을 trim − margin.left − margin.right로 대조하되, trim은 이 attempt가 이미
        # 만든 pdf1의 **실측** MediaBox(measured_trim_w_mm, 위)를 쓰고 margin만 theme.css를
        # 정적으로 읽는다(빈 PDF에서 여백은 독립 복원할 수 없다).
        geo = _page_geometry_mm(css_src)
        declared_full = ((tokens.get("diagram") or {}).get("widths") or {}).get("full")
        if geo is not None and isinstance(declared_full, (int, float)) \
                and not isinstance(declared_full, bool) and declared_full > 0:
            _decl_trim_w, margin_right, margin_left = geo
            content_width_mm = round(measured_trim_w_mm - margin_right - margin_left, 3)
            delta = abs(content_width_mm - declared_full)
            if delta > 0.5:
                die(f"diagram.widths.full {declared_full}mm != 실렌더 판면폭 {content_width_mm}mm "
                    f"(pdf1 실측 trim {measured_trim_w_mm:.3f}mm − theme.css margin.right "
                    f"{margin_right}mm − margin.left {margin_left}mm, 오차 {delta:.3f}mm > 허용 "
                    f"0.5mm) — render_diagrams.mjs는 {declared_full}mm를 라벨 pt 환산 기준으로 "
                    f"쓰는데 지면의 실제 판면은 {content_width_mm}mm다. widths.full이 재단폭 "
                    f"이내라는 것만으로는 안전하지 않다(K1/N2) — 이 값을 실측 판면폭에 맞출 것"
                    f"({'과다' if declared_full > content_width_mm else '과소'} "
                    f"{max(declared_full, content_width_mm) / min(declared_full, content_width_mm):.3f}배)")
        elif geo is None:
            warn("theme.css에서 `@page {size:…;margin:…}` 형태를 정적으로 읽지 못했다 — "
                 "diagram.widths.full 대조 생략(N2 값 축), 수동 감사 항목")
        break

    tocplan["replanned"] = replanned
    tocplan["warnings"] = list(BUILD_WARNS)
    (ts / "tocplan.json").write_text(
        json.dumps(tocplan, ensure_ascii=False, indent=2), encoding="utf-8")

    # 사후조건 ① 마커 전수 회수 — **종별로** 발행 집합과 회수 집합이 정확히 일치해야
    # 한다. 미회수는 마커가 잘렸거나(면 넘침) 텍스트 레이어에서 사라진 것이고, 그 상태의
    # 목차 쪽번호·북마크·차례는 조용히 틀린다. 역방향(잉여)도 본다 — 구 구현은 단방향이라
    # **목차 행이 없는 잉여 마커**를 통과시켰고, 그 잉여가 절 번호를 한 칸씩 밀어 절
    # 쪽번호·레벨 2 북마크를 조용히 오배정했다(적대검토 D3, md_to_html R2 통합의 사후조건).
    # 종을 나눠 검사하므로 종 사이 오염(fg가 ch 딕트에 섞이는 류)도 같은 검사가 잡는다.
    # fg/tb 발행 0인 스타일(현행 전부 — S5 전)은 공집합==공집합으로 자명 통과한다.
    want_by_kind = {"ch": {r["mk"] for r in toc_rows},
                    "fg": {fmk for fmk, _ in fg_marks},
                    "tb": {tmk for tmk, _ in tb_marks}}
    for kind in MARKER_KINDS:
        got_mk = set(pages_by_kind[kind])
        missing = sorted(want_by_kind[kind] - got_mk)
        if missing:
            die(f"pass1에서 {kind} 마커 {len(missing)}개 미회수: {missing[:6]} "
                f"(발행 {len(want_by_kind[kind])} / 회수 {len(got_mk)}) — "
                "목차 넘침·클리핑 의심")
        extra = sorted(got_mk - want_by_kind[kind])
        if extra:
            die(f"pass1에서 발행 대장에 없는 잉여 {kind} 마커 {len(extra)}개 회수: "
                f"{extra[:6]} — 발행 경로와 회수 어휘가 어긋났다"
                "(md_to_html/wrap_tbl의 마커 주입 경로 확인)")

    # 사후조건 ①′ 포함 단조 — fg/tb 마커의 회수 면이 **소속 장의 면 구간 안**에 있고
    # 발행 순서(=지면 순서)대로 **단조 비감소**해야 한다. 집합 일치(①)만으로는 못 잡는
    # 함정이 있다: 마커를 품는 figure/.tablewrap의 mk-anchor(position:relative)가 사라지면
    # .pgmark{position:absolute}가 문서 원점(1면)에 붙어 모든 마커가 1면으로 회수되는데,
    # 전수 회수 자체는 성공하므로 ①은 충족된다 — 그 상태로 S5 차례가 발행되면 전 항목
    # 쪽번호가 1로 인쇄된다(magazine theme.css의 h2 실측과 동형). 발행 0이면 자명 통과.
    # 감도는 M-ORIGIN 뮤테이션(tests/mutations)이 회귀 자산으로 고정한다.
    ch_start = {i: pages[f"ch{i:02d}"] for i in range(1, len(outline["chapters"]) + 1)
                if f"ch{i:02d}" in pages}
    for kind, marks in (("fg", fg_marks), ("tb", tb_marks)):
        prev_p = 0
        for mk2, ci in marks:
            p = pages_by_kind[kind][mk2]
            lo = ch_start.get(ci)
            hi = ch_start.get(ci + 1, pass1_pages + 1) - 1
            if lo is None or not (lo <= p <= hi):
                die(f"{kind} 마커 {mk2}의 회수 면 {p}이 소속 장 ch{ci:02d} 구간 "
                    f"[{lo}, {hi}] 밖이다 — mk-anchor(position:relative) 앵커 소실 의심"
                    "(전형 증상: 전 마커가 1면으로 회수). theme.css의 .mk-anchor 규칙과 "
                    "빌더의 mk-anchor 클래스 발행을 확인할 것")
            if p < prev_p:
                die(f"{kind} 마커 {mk2}의 회수 면 {p}이 직전 마커 면 {prev_p}보다 앞이다 — "
                    "발행 순(지면 순)과 회수 면이 단조가 아니다(앵커·발행 경로 확인)")
            prev_p = p

    # 목차 쪽번호는 폴리오 기준(본문 1쪽부터 — book-anatomy.md C9). 앞부속(표지·목차)
    # 오프셋 = 첫 장 시작 절대페이지 - 1. 지면 폴리오는 decorate.py가 같은 오프셋으로 찍는다.
    folio_offset = min(pages.values()) - 1 if pages else 0
    # .tocpg 폭은 3자리 기준으로 고정돼 있다(theme.css) — 4자리가 나오면 칼럼을 넘겨
    # 제목 폭을 줄이고 접힘을 유발한다. 조용히 어긋나게 두지 않는다. 차례(fg/tb) 항목도
    # 같은 칼럼 계약이므로 전 종을 함께 본다.
    max_folio = max((p - folio_offset for kd in pages_by_kind.values() for p in kd.values()),
                    default=0)
    if max_folio >= 1000:
        die(f"목차 쪽번호 최대 {max_folio}(4자리) — .tocpg 칼럼 폭은 3자리(6.5mm) 계약이다. "
            "theme.css의 .tocpg flex-basis와 이 검사를 함께 올릴 것")
    html2 = html
    # 차례(fg/tb) 항목도 같은 .tocpg[data-mk] 자리표라 한 루프가 전 종을 스탬핑한다 —
    # 종별 딕트는 합치지 않고 순회만 합친다(pages 딕트의 ch 전용 계약 유지).
    for kd in pages_by_kind.values():
        for mk, abs_page in kd.items():
            html2 = html2.replace(f'<span class="tocpg" data-mk="{mk}">00</span>',
                                  f'<span class="tocpg" data-mk="{mk}">{abs_page - folio_offset}</span>')
    # pass 2에는 마커 불필요 — 잉크·텍스트 레이어 오염 방지를 위해 전 종 제거
    # (.pgmark은 absolute 포지션이라 제거해도 리플로우 없음; 북마크는 pass 1 페이지맵
    # 사용. 제거 어휘는 회수와 같은 MK_* 단일 진리원 — 갈라지면 잔존 마커가 최종 PDF로 샌다)
    html2 = MK_STRIP_RE.sub("", html2)
    page2 = ts / "book-final.html"
    page2.write_text(html2, encoding="utf-8")

    out = book_dir / "draft" / "book.pdf"
    r = subprocess.run(["node", str(printer), str(page2), str(out)],
                       capture_output=True, text=True, env=env)
    if r.returncode != 0:
        sys.exit("HTML pass2 print failed:\n" + r.stderr)

    # PDF outline(bookmarks): Chromium print emits none — stamp from markers
    doc = fitz.open(out)
    # 사후조건 ② pass 2 면 밀림 검사. pass 1 HTML 검사만으로는 밀림을 원리적으로 볼 수
    # 없다(pass 2에서 마커를 제거하므로 draft에서는 마커를 재회수할 수 없다 — 실측 확인).
    # 그래서 ㉠ page_count 동일성 ㉡ 각 장 제목이 pass 1이 회수한 그 면에 실재하는지로
    # 대체한다. 절 제목은 여러 장에 중복될 수 있어 동일성 판정에 쓰지 않는다(G14-A가
    # 인쇄 쪽번호↔폴리오 대조로 그 축을 덮는다).
    if doc.page_count != pass1_pages:
        doc.close()
        die(f"pass1 {pass1_pages}면 vs pass2 {doc.page_count}면 — 쪽번호 주입이 면을 밀었다. "
            ".tocpg 폭 고정(theme.css)이 깨졌는지 확인할 것")
    shifted = []
    for idx, ch in enumerate(outline["chapters"], 1):
        mk = f"ch{idx:02d}"
        if mk not in pages:
            continue
        txt = re.sub(r"\s+", "", doc[pages[mk] - 1].get_text())
        if re.sub(r"\s+", "", ch["title"]) not in txt:
            shifted.append((ch["title"][:16], pages[mk]))
    if shifted:
        doc.close()
        die(f"pass2 면 밀림 — 장 제목이 pass1 회수 면에 없다: {shifted[:4]}")
    toc = []
    for idx, ch in enumerate(outline["chapters"], 1):
        mk = f"ch{idx:02d}"
        if mk in pages:
            toc.append([1, ch["title"], pages[mk]])
            # 레벨 2(절) 북마크 — toc_levels >= 2인 스타일만. 없으면 PDF 열람기에서
            # 절 단위 이동이 불가하고 G4가 그 부재를 검출하지 못한다.
            for sidx, stitle in enumerate(sec_by_ch.get(idx, []), 1):
                smk = f"{mk}s{sidx:02d}"
                if smk in pages:
                    toc.append([2, stitle, pages[smk]])
    if toc:
        doc.set_toc(toc)
    doc.saveIncr()
    doc.close()

    # optional theme post-decoration (running marks, folio) via PyMuPDF
    dec = style_dir / "decorate.py"
    if dec.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("theme_decorate", dec)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        doc = fitz.open(out)
        mod.decorate(doc, {"book": book, "pages": pages,
                           "fonts_dir": skill / "assets" / "fonts"})
        doc.saveIncr()
        doc.close()
    print(f"OK draft: {out} (chapter pages: {pages})")
