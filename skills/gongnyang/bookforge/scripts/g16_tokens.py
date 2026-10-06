#!/usr/bin/env python3
"""bookforge G16-TOKENS — 렌더 전 토큰 계약 게이트 (순수 함수 모듈).

Usage: python3 scripts/g16_tokens.py <style>        # 단일 스타일 사람 읽기용 출력

축 3개:
  G16-SYNC     : 스타일 팩의 색·수치 계약 정합. engine↔팩 실물 일치 · diagram.palette 존재 ·
                 palette_roles 무결성 · brand_default↔palette[0] 동기 ·
                 contrast_contract 형식(enforce bool)과 토큰명 해석 가능성 ·
                 diagram.labelBand 형식(maxRatio 양수 · enforce bool — 라벨 상한 승격 스위치) ·
                 front_frame_mm 선언값 타당성 · **diagram.widths ↔ theme.css $fig_* 치환
                 계약**(도해 폭의 단일 진리원이 tokens임을 배선으로 못박는다 — html 한정)
  G16-CONTRAST : contrast_contract 선언 페어의 WCAG 대비를 pt·bold 파생 하한과 대조
  G16-BRAND    : 브랜드 입력 사전 검증(형식·치환 지점 대비·고정 동반색과의 hue 정합)

설계 근거 둘.
  ① 렌더 전 경계이므로 HARD FAIL은 "증명 가능한 것"에만 준다 — fg·bg가 둘 다
     불투명 리터럴 hex로 해석되는 페어만이 어떤 렌더링으로도 구제되지 않는다.
     알파·그라데이션·해석 불가 배경은 전부 WARN이고, 물리적 강제는 렌더 후
     G14-C(tocgate.py)가 픽셀 샘플로 계속 담당한다.
  ② 승격은 전역 플래그가 아니라 스타일별 데이터 스위치(contrast_contract.enforce ·
     diagram.labelBand.enforce)다. 전역 --g16-warn-only는 긴급 탈출구로만 남는다(build.py).

부재는 결함이지만 잉여는 아니다 — 미사용 팔레트 슬롯·미사용 CSS 토큰은 영구 WARN이며
절대 FAIL로 올리지 않는다.

BRAND만 세 번째 원칙을 더 갖는다: **값 출처로 강도를 분기한다.** book.json.brand는
사용자 입력이 무검증으로 치환되는 구멍이라 FAIL, 스타일 팩의 brand_default는 이미
출하된 부채라 WARN이다. 후자를 FAIL로 두면 출하 기본색 하나가 그 스타일의 모든 책을
잠근다(business #C2662E는 백색 위 4.01로 자기 게이트에 걸린다).
"""
import colorsys
import json
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent

ROLES = ("label", "fill", "stroke")

# tokens.diagram.widths 키 ↔ theme.css 플레이스홀더명. build_html.fig_width_css가 이 표를
# 그대로 읽어 치환하므로 게이트와 빌더가 같은 계약을 본다(표가 두 벌이면 그 어긋남 자체가
# 이 축이 없애려는 결함이다). render_diagrams.mjs는 같은 키로 pt 환산 기준을 뽑는다.
FIG_WIDTH_KEYS = {"full": "fig_full_mm", "twothirds": "fig_twothirds_mm"}

# tokens.diagram.labelBand.maxRatio 타당성 대역 (W5 판정 K3 봉합).
# 종전 검사는 "양수 수치인가" 하나였고, 그래서 `maxRatio: 999`가 **WARN 한 줄도 없이**
# 통과했다(실측: 라벨 본문의 2.18×·2.51× 그대로 발행 + 6단계 급수 주입까지 무력화 —
# `iter===0 && inBand`가 참이 되어 주입 전에 break). 대역 근거:
#   · 하한 0.5 — 상한(body_pt × maxRatio)이 글자 하한(minFontPt 8pt)보다 낮으면 밴드가
#     공집합이 되어 어떤 도해도 통과할 수 없다. 6스타일 body_pt는 9.5~10.5pt이므로
#     0.5는 상한 4.75~5.25pt로 이미 8pt 하한 아래다 — 그 아래는 선언 오류가 확실하다.
#   · 상한 2.0 — 이 축의 사용자 원 지적이 "도해 라벨이 본문보다 크다"였고 실측 코퍼스의
#     max/본문 비는 중앙 0.96·p90 1.17, 하우스 등급은 1.20이다. 본문의 두 배는 어느
#     스타일에도 등재 근거가 없고, 그 위는 "검사를 끈다"와 실질적으로 같다.
# 대역 안의 값이 옳음을 증명하지는 않는다 — 그 판단은 스타일별 `_labelBand_evidence`가
# 진다. 이 축이 막는 것은 **판정을 무력화하는 값**이다.
LABEL_BAND_MIN_RATIO = 0.5
LABEL_BAND_MAX_RATIO = 2.0
LABEL_BAND_RATIO_RATIONALE = (
    "하한 0.5 = 상한이 minFontPt(8pt) 아래로 내려가 밴드가 공집합이 되는 지점, "
    "상한 2.0 = 본문의 두 배(등재 근거 없음, 그 위는 검사를 끄는 것과 같다). "
    "하우스 등급은 1.20이다"
)

# G14-B와 같은 값이어야 두 게이트가 다른 판정을 내지 않는다. 사전 FAIL의 존재 이유가
# "2-pass 렌더 후에야 G14-B에서 죽는 것"을 앞당기는 것이므로 값이 갈리면 목적이 무너진다.
# 출처: scripts/tocgate.py:368 `def g14b_key_color(..., tol=36, ...)` 기본 인자.
HUE_TOL_DEG = 36
# 유채/무채 경계도 같은 출처를 쓴다 — 출처: scripts/tocgate.py:39 `_is_colored(rgb, min_chroma=28)`.
MIN_CHROMA = 28
# 하한을 갓 넘긴 구간은 통과시키되 표시한다. 정적 토큰값과 렌더 샘플값의 관측 드리프트
# (0.63%)의 8배 여유 — 이 밴드 안은 렌더에서 하한 아래로 내려갈 수 있다.
THIN_BAND = 1.05


# ---------------------------------------------------------------- 대비 산술

def contrast_floor(pt, bold):
    """대비 하한의 **단일 진리원** — G16-CONTRAST(정적)와 G14-C(픽셀)가 함께 쓴다.

    WCAG 2.x 1.4.3 large-text 정의를 그대로 따른다: 18pt 이상, 또는 14pt 이상이면서
    볼드일 때만 대형 텍스트로 보고 3:1, 그 외에는 4.5:1.

    W4 7단계 이전에는 `pt >= 14 or (pt >= 10.5 and bold)`라는 자체 완화값을 썼다
    (두 갈래 모두 WCAG보다 느슨). 교정 근거·영향 실측은
    `/mnt/d/bookforge-verify/report/dualfloor-diff.md` — 출하 9권 전수 재스캔에서
    신규 FAIL은 business 2권의 accent #C2662E 10.5pt bold on white(4.01) 2건뿐이며,
    그 조판(styles/business/theme.typ `bf-exec-open`)은 같은 단계에서 수리했다.

    tocgate.py(G14-C)는 이 함수를 import해 쓴다 — 값 복제 금지. 두 게이트가 다른
    수를 내면 사전 게이트(렌더 전 FAIL 앞당기기)의 존재 이유가 무너진다.
    """
    return 3.0 if (pt >= 18 or (pt >= 14 and bold)) else 4.5


# WCAG 대형 텍스트 예외의 굵기 임계. CSS `font-weight` 수치 판정의 단일 진리원 —
# `tests/lint_contrast.py`가 이 상수를 import한다(값 복제 금지).
BOLD_MIN_WEIGHT = 700

# 카멜케이스·구분자(공백/‗/-/.)·숫자 토큰을 뽑는다. "ExtraBold" -> ["Extra","Bold"],
# "Pretendard-SemiBold" -> ["Pretendard","Semi","Bold"], "Pretendard-600" -> ["Pretendard","600"].
_WORD_TOKEN_RE = re.compile(r"[A-Z][a-z]+|[A-Z]+(?![a-z])|[a-z]+|\d+")

# 토큰 그대로 bold인 굵기 이름(700 이상, "Bold" 토큰 규칙과 별도로 단독 성립).
# ExtraBold/UltraBold는 토큰화하면 ["Extra","Bold"]/["Ultra","Bold"]가 되어
# 아래 "Bold" 토큰 규칙(직전 토큰이 Semi/Demi가 아니면 bold)으로 이미 걸린다.
_HEAVY_WORD_TOKENS = {"black", "heavy"}
# 이 토큰 바로 뒤에 "bold" 토큰이 오면 600(=bold 아님)이다 — Pretendard-SemiBold 등.
_LIGHTEN_BOLD_PREFIX = {"semi", "demi"}


def is_bold_font(font_name):
    """PDF 스팬 폰트명이 WCAG 기준 bold(700+)인가 — **단일 진리원**.

    `tocgate.py`(G14-C 픽셀 축)가 import한다. 예전에는 부분문자열 판정
    (`"Bold" in font` 계열)을 썼고, 그 결과 이원화됐다: `Pretendard-SemiBold`(600)가
    부분문자열 "Bold"를 포함해 대형 자격을 얻었고(W4 판정 D6), 반대 방향으로
    `Blackriver-Regular`(400)·`Boldoni-Light`(300)처럼 **가문명 자체에 굵기 낱말이
    섞여 있을 뿐인 폰트**도 bold로 오판했다(W4 재판정 E2 — 하한을 관대화하는 방향이라
    더 위험하다: 실제로는 400인 텍스트가 대형 자격(하한 3.0)을 받아 저대비가 통과한다).

    이번 버전은 **토큰화 후 토큰 단위로만** 판정한다 — 부분문자열 매칭을 하지 않으므로
    "Blackriver"(하나의 카멜 토큰)는 "black"과 다르고, "Boldoni"도 "bold"와 다르다.

    규칙(순서 무관, 하나라도 성립하면 True):
      1. 굵기 숫자 토큰(`\\d+`)이 100~950 범위면 **CSS font-weight 수치로 우선 해석**하고
         `BOLD_MIN_WEIGHT`(700)와 직접 비교한다 — `Pretendard-600`은 600 < 700이라 False,
         `Pretendard-700`은 True. (범위 밖 숫자는 버전 번호 등으로 보고 무시한다.)
      2. "black"·"heavy" 토큰이 그대로 존재하면 True(`Pretendard-Black`).
      3. "bold" 토큰이 있고, 그 **직전 토큰**이 "semi"/"demi"가 **아니면** True
         (`Pretendard-Bold`·`Pretendard-ExtraBold`=True, `Pretendard-SemiBold`=False).

    이름에 굵기 표기가 전혀 없는 폰트(`NotoSansKR-Bd` 같은 약어 포함)는 False다 —
    보수적 방향(하한 4.5 유지)이라 안전하고, 이 함수의 목적은 관대화 오판(위 D6·E2
    방향)을 막는 것이지 모든 표기 변종을 인식하는 것이 아니다.
    """
    if not font_name:
        return False
    tokens = [t.lower() for t in _WORD_TOKEN_RE.findall(str(font_name))]
    for i, tok in enumerate(tokens):
        if tok.isdigit():
            w = int(tok)
            if 100 <= w <= 950:
                return w >= BOLD_MIN_WEIGHT
            continue
        if tok in _HEAVY_WORD_TOKENS:
            return True
        if tok == "bold":
            prev = tokens[i - 1] if i > 0 else ""
            if prev in _LIGHTEN_BOLD_PREFIX:
                continue
            return True
    return False


def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def rel_luminance(rgb):
    """WCAG 2.x 상대휘도 (sRGB 표준식)."""
    r, g, b = (_lin(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg_rgb, bg_rgb):
    a, b = rel_luminance(fg_rgb), rel_luminance(bg_rgb)
    if a < b:
        a, b = b, a
    return (a + 0.05) / (b + 0.05)


# ------------------------------------------------------------------- 색상각

def is_chromatic(rgb):
    """유채색 판정. tocgate.py:39 `_is_colored`와 같은 식·같은 임계."""
    return max(rgb) - min(rgb) > MIN_CHROMA


def hue_deg(rgb):
    """HLS 색상각(0~360). tocgate.py:44 `_hue`와 같은 산식(colorsys)."""
    return colorsys.rgb_to_hls(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)[0] * 360


def hue_dist(a, b):
    """원형 거리. tocgate.py:49 `_hue_dist`와 동일."""
    d = abs(a - b) % 360
    return min(d, 360 - d)


# ------------------------------------------------------- $key_label 결정론 파생

def derive_key_label(key_rgb, bg_rgb, pt, bold, step=0.004):
    """key를 **명도만** 단계적으로 낮춰 bg 위 대비가 하한을 처음 넘는 색.

    hue·채도를 보존하는 이유는 둘이다 — 브랜드 정체성이 라벨에서 유지되고,
    G16-BRAND ③ hue 정합이 파생 때문에 깨지지 않는다(색상각이 그대로다).
    밝은 배경에서 대비는 명도에 단조이므로 첫 통과값이 곧 최소 변형이다.

    목표를 하한이 아니라 하한×THIN_BAND로 잡는다 — 하한을 갓 넘긴 값으로 파생하면
    렌더 후 G14-C가 픽셀에서 재실측할 때 드리프트만으로 다시 미달이 될 수 있다.
    드리프트를 파생 단계에서 흡수해야 두 게이트가 같은 결론에 선다.
    """
    floor = contrast_floor(pt, bold) * THIN_BAND
    h, l, s = colorsys.rgb_to_hls(*(c / 255.0 for c in key_rgb))
    for i in range(int(l / step) + 2):
        li = max(0.0, l - i * step)
        rgb = tuple(int(round(c * 255)) for c in colorsys.hls_to_rgb(h, li, s))
        if contrast_ratio(rgb, bg_rgb) >= floor:
            return rgb
    return (0, 0, 0)   # 순흑으로도 못 넘는 배경 = 배경 자체가 결함(CONTRAST 축 소관)


# 4·8자리(알파 포함)도 인식한다. Chromium은 `#1b6e9cff`를 정상 파싱하므로(실측)
# 8자리를 "해석 불가"로 두면 렌더되는 입력을 게이트가 잠근다 — S1의 뿌리였다.
# 교대는 긴 것부터 — 짧은 대안이 먼저 물면 뒤 두 자리가 잘린다.
_HEX_RE = re.compile(r"#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})(?![0-9a-fA-F])")

# rgb()/rgba() 함수 표기 — 콤마·공백 구분자, 채널 %/정수, 알파 0~1 또는 %.
_RGB_FN_RE = re.compile(r"""rgba?\(\s*
    ([0-9.]+%?)\s*(?:,\s*|\s+)
    ([0-9.]+%?)\s*(?:,\s*|\s+)
    ([0-9.]+%?)\s*
    (?:(?:,|/)\s*([0-9.]+%?)\s*)?
\)""", re.X | re.I)


def _chan(tok, scale=255.0):
    v = float(tok[:-1]) / 100.0 * scale if tok.endswith("%") else float(tok)
    return max(0.0, min(scale, v))


def parse_color(s):
    """리터럴 색 -> (r,g,b,a) (a는 0~255). hex 3/4/6/8자리와 rgb()/rgba() 표기 지원.

    그 밖(var()·gradient·색이름·$플레이스홀더)은 None. 알파는 버리지 않고 실어 보낸다 —
    '반투명이라 정적 대비 산출 불가'(WARN)와 '아예 색이 아님'(FAIL)은 다른 판정이다.
    """
    if not isinstance(s, str):
        return None
    s = s.strip()
    m = _HEX_RE.fullmatch(s)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        a = int(h[6:8], 16) if len(h) == 8 else 255
        return rgb + (a,)
    m = _RGB_FN_RE.fullmatch(s)
    if m:
        rgb = tuple(int(round(_chan(m.group(i)))) for i in (1, 2, 3))
        a = 255 if m.group(4) is None else int(round(_chan(m.group(4), 1.0) * 255))
        return rgb + (a,)
    return None


def parse_hex(s):
    """불투명 리터럴 색 -> (r,g,b). 반투명·비리터럴은 None(정적 대비 산출 대상 아님)."""
    c = parse_color(s)
    return None if c is None or c[3] != 255 else c[:3]


def norm_hex(s):
    """불투명 리터럴 색 -> '#rrggbb'. `#1b6e9cff`는 `#1b6e9c`로 정규화된다."""
    rgb = parse_hex(s)
    return None if rgb is None else "#%02x%02x%02x" % rgb


def _literal_res(s):
    """리터럴 색 문자열의 3분 해석. 리터럴이 아니면 None(호출자가 다음 경로로).

    반투명(알파<FF)은 FAIL이 아니라 nonliteral — 렌더는 되지만 정적 대비는 배경에
    의존하므로 증명이 성립하지 않는다(G14-C 픽셀 샘플 소관).
    """
    c = parse_color(s)
    if c is None:
        return None
    if c[3] != 255:
        return ("nonliteral", f"{s.strip()} (알파 {c[3]}/255 — 반투명)")
    return ("hex", "#%02x%02x%02x" % c[:3])


def _strip_important(val):
    """CSS `!important` 접미 제거 — 값의 색 해석에는 영향이 없다."""
    return re.sub(r"\s*!\s*important\s*$", "", val, flags=re.I)


# ------------------------------------------------------- theme.css 토큰 그래프

def _strip_comments(text):
    return re.sub(r"/\*.*?\*/", " ", text, flags=re.S)


_DECL_RE = re.compile(r"(--[A-Za-z0-9_-]+)\s*:\s*([^;{}]*)")


def css_root_vars(theme_text):
    """theme.css 전체의 커스텀 프로퍼티 선언 맵(값은 미해석 원문). 마지막 선언이 이긴다.

    **캐스케이드 근사임을 명시한다.** 선택자 특정성·@media 조건·상속 문맥을 해석하지
    않고 파일 등장 순서만 본다. 정확한 계산은 브라우저만 할 수 있으므로 여기서는
    "뒤에 오는 선언이 앞을 덮는다"는 동일 특정성 규칙만 근사한다.

    이전 구현은 첫 `:root` 블록의 첫 `}`까지만 읽어, 두 번째 `:root`나 @media 안의
    재정의를 통째로 무시하고 브라우저가 쓰지 않을 구값으로 대비를 계산했다(S5, 무신호).
    전수 수집은 그 무신호를 없앤다. 대가로 `.foo{--x:...}` 같은 국소 선언도 :root와
    같은 층으로 섞이지만, 계약이 참조하는 토큰은 전역 토큰이라 실무상 근사가 성립한다.
    """
    if not theme_text:
        return {}
    out = {}
    for name, val in _DECL_RE.findall(_strip_comments(theme_text)):
        out[name] = val.strip()   # 마지막 선언이 이긴다(dict 덮어쓰기)
    return out


def css_literal_hexes(theme_text):
    """theme.css에 리터럴로 등장하는 모든 hex(정규화). 주석은 제외 —
    주석 안의 '구 #6d747a' 같은 이력 기록이 사용 근거로 오인되면 안 된다.
    반투명 hex(알파<FF)는 불투명 색이 아니므로 집합에 넣지 않는다."""
    if not theme_text:
        return set()
    hexes = (norm_hex(m.group(0)) for m in _HEX_RE.finditer(_strip_comments(theme_text)))
    return {h for h in hexes if h}


# 해석 결과 종류: ("hex", "#rrggbb") / ("nonliteral", 사유) / ("unresolved", 사유)
# 2번째 원소는 hex일 때만 값이고, 나머지 둘은 **사람이 읽는 사유 문자열**이다.
# 사유를 여기서 만들어야 오귀속이 없다 — brand발 실패를 스타일 팩 탓으로 돌리던 게 S1의 부수 결함.
def _resolve_value(val, ctx, depth=0, trace=None):
    if depth > 8:
        return ("nonliteral", f"var() 참조 깊이 8 초과: {val}")
    val = _strip_important(val.strip())
    # build_html.py의 치환부가 렌더 전에 꽂는 세 플레이스홀더 — 완전 재현 가능하다.
    ph = _placeholder_res(val, ctx, trace)
    if ph:
        return ph
    lit = _literal_res(val)
    if lit:
        return lit
    # var(--x, fallback)의 fallback 해석은 **의도적으로 하지 않는다** — 어느 쪽이
    # 쓰일지는 --x의 정의 여부에 달렸고 그건 캐스케이드 문맥이라 정적 증명이 아니다.
    m = re.fullmatch(r"var\(\s*(--[a-z0-9-]+)\s*\)", val, re.I)
    if m:
        return _resolve_token(m.group(1), ctx, depth + 1, trace)
    return ("nonliteral", val)


def _placeholder_res(val, ctx, trace=None):
    """build_html.py가 치환하는 $플레이스홀더 3종. 리터럴이 아니면 None.

    trace는 "이 값이 브랜드에서 왔는가"를 기록한다 — G16-BRAND가 치환 지점만
    골라 검사하려면 해석 경로가 brand를 지나갔는지 알아야 한다.
    """
    if val not in ("$key_color", "$key_tint", "$key_label"):
        return None
    if trace is not None:
        trace.add("brand")
    if val == "$key_color":
        return _brand_res(ctx)
    if val == "$key_tint":
        return ("nonliteral", "rgba(brand, 0.08) — 알파")   # 알파 — 정적 대비 산출 불가
    return ctx.get("key_label_res") or _brand_res(ctx)


def _resolve_token(name, ctx, depth=0, trace=None):
    """토큰명 -> 색. 지원 형식:
      '--ink'      theme.css :root 변수(체인·$key_color 치환 포함)
      'brand'      book.json brand > tokens.brand_default
      'palette[3]' tokens.diagram.palette 슬롯
      '#1e7aad'    리터럴 hex
      '$key_label' build_html.py가 파생해 꽂는 값(brand을 명도만 낮춘 라벨색)
      '~...'       비리터럴 배경의 명시 선언(그라데이션·이미지) — 대비 산출 대상 아님
    """
    if not isinstance(name, str):
        return ("unresolved", f"{name!r}는 문자열이 아님")
    name = name.strip()
    if name.startswith("~"):
        return ("nonliteral", name[1:] or "declared-nonliteral")
    ph = _placeholder_res(name, ctx, trace)
    if ph:
        return ph
    lit = _literal_res(name)
    if lit:
        return lit
    if name == "brand":
        if trace is not None:
            trace.add("brand")
        return _brand_res(ctx)
    m = re.fullmatch(r"palette\[(\d+)\]", name)
    if m:
        pal = ctx.get("palette") or []
        i = int(m.group(1))
        if i >= len(pal):
            return ("unresolved", f"palette[{i}] 범위 밖 — tokens.json diagram.palette는 {len(pal)}슬롯")
        return _literal_res(pal[i]) or ("nonliteral", f"palette[{i}]={pal[i]!r}")
    if name.startswith("--"):
        raw = ctx.get("vars", {}).get(name)
        if raw is None:
            return ("unresolved", f"{name}이 theme.css의 커스텀 프로퍼티 선언에 없음")
        return _resolve_value(raw, ctx, depth + 1, trace)
    return ("unresolved",
            f"{name!r}은 지원 형식(--토큰 | brand | $key_label | palette[n] | #hex | ~비리터럴) 밖")


def _brand_res(ctx):
    """brand(=$key_color) 해석 결과. 사유 문자열이 출처를 스스로 지목한다."""
    return ctx.get("brand_res") or ("unresolved", "brand 미선언")


def _ctx(tokens, theme_text, brand=None):
    # 출처를 붙들어 둔다 — brand는 book.json(사용자 데이터)에서 오고 brand_default는
    # 스타일 팩에서 온다. 해석 실패 메시지가 엉뚱한 파일을 지목하면 수리자가 헤맨다.
    from_book = isinstance(brand, str) and brand.strip() != ""
    raw = (brand if from_book else tokens.get("brand_default")) or ""
    src = "book.json brand" if from_book else "tokens.json brand_default"
    if not str(raw).strip():
        res = ("unresolved", f"{src} 미선언 — $key_color/brand 참조를 풀 수 없음")
    else:
        lit = _literal_res(raw)
        # 반투명 brand는 렌더는 되므로 nonliteral(WARN), 색이 아닌 값만 unresolved(FAIL).
        res = lit or ("unresolved", f"{src}={raw!r}가 리터럴 색(#hex | rgb())이 아님")
        if lit and lit[0] == "nonliteral":
            res = ("nonliteral", f"{src}={raw!r} — {lit[1]}")
    ctx = {
        "vars": css_root_vars(theme_text),
        "brand": res[1] if res[0] == "hex" else None,
        "brand_res": res,
        "brand_src": src,
        "brand_from_book": from_book,
        "brand_raw": str(raw),
        "palette": (tokens.get("diagram") or {}).get("palette") or [],
        # 파생 중 자기참조(key_label.bg에 $key_label을 적는 실수)로 무한재귀에 빠지지 않게
        # 먼저 자리를 막아 둔다.
        "key_label_res": ("unresolved", "key_label 파생 중 자기참조"),
    }
    ctx["key_label_res"] = _key_label_res(tokens, ctx)
    return ctx


def _key_label_res(tokens, ctx):
    """tokens.json `key_label` 계약대로 brand에서 라벨색을 파생한다.

    계약이 없는 스타일은 brand 그대로 — 파생은 "이 자리 대비가 하한에 못 미친다"는
    실측이 있는 스타일만 선언한다(magazine `.callout-title` 4.45).
    """
    base = ctx["brand_res"]
    spec = tokens.get("key_label")
    if base[0] != "hex" or not isinstance(spec, dict):
        return base       # brand 해석 실패 사유를 그대로 승계한다(오귀속 방지)
    bk, bv = _resolve_token(spec.get("bg"), ctx)
    if bk != "hex":
        return ("unresolved", f"key_label.bg={spec.get('bg')!r} 해석 불가 — {bv}")
    pt, bold = spec.get("pt"), spec.get("bold")
    if not isinstance(pt, (int, float)) or isinstance(pt, bool) or not isinstance(bold, bool):
        return ("unresolved", f"key_label.pt/bold 형식 오류 (pt={pt!r} bold={bold!r})")
    rgb = derive_key_label(parse_hex(base[1]), parse_hex(bv), pt, bold)
    return ("hex", "#%02x%02x%02x" % rgb)


def key_label_hex(tokens, theme_text, brand=None):
    """build_html.py의 치환부가 쓰는 공개 진입점 — 파생 진리원은 여기 하나뿐이다.

    파생 불가(브랜드가 색이 아님 등)면 None을 돌려 호출자가 폴백을 고르게 한다.
    """
    kind, val = _ctx(tokens, theme_text, brand)["key_label_res"]
    return val if kind == "hex" else None


def _f(axis, level, msg):
    return {"axis": axis, "level": level, "msg": msg}


# ------------------------------------------------ front_frame_mm 선언값 타당성

# 프레임이 지면의 이 비율을 넘으면 G3-FIT 축이 사실상 항등이 된다(`[0,0,0,0]`이면
# 프레임 = 지면 전체 +TOL이라 어떤 텍스트도 밖으로 나갈 수 없다). 물리적 모순은
# 아니므로 WARN이지만, **위조가 미선언보다 조용한 상태**(선언은 declared:true에
# WARN 0, 미선언은 WARN 1건)를 뒤집는 것이 이 축의 목적이다.
FRONT_FRAME_AREA_WARN = 0.95


def front_frame_area_ratio(fr_mm, trim_mm):
    """선언 프레임이 판형에서 차지하는 면적 비율. 계산 불가면 None."""
    if not (trim_mm and len(trim_mm) == 2):
        return None
    top, right, bottom, left = fr_mm
    w, h = trim_mm[0] - left - right, trim_mm[1] - top - bottom
    if trim_mm[0] <= 0 or trim_mm[1] <= 0 or w <= 0 or h <= 0:
        return None
    return (w * h) / (trim_mm[0] * trim_mm[1])


def _front_frame_one(style, where, fr, trim_mm):
    """단일 프레임 `[top,right,bottom,left]`의 타당성. (findings, 유효한가)."""
    out = []
    if not isinstance(fr, list) or len(fr) != 4:
        return [_f("SYNC", "FAIL",
                   f"front_frame_mm{where} = {fr!r} — [top,right,bottom,left] 4원소 배열이어야 한다. "
                   f"qc_gate G3-FIT가 이 값을 그대로 봉투로 쓰므로 형식이 깨지면 축이 조용히 꺼진다")], False
    for i, v in enumerate(fr):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            out.append(_f("SYNC", "FAIL",
                          f"front_frame_mm{where}[{i}] = {v!r} — 수치가 아니다(mm)"))
        elif v < 0:
            out.append(_f("SYNC", "FAIL",
                          f"front_frame_mm{where}[{i}] = {v} — 음수 여백은 지면보다 큰 프레임을 만든다. "
                          f"G3-FIT 축이 원리적으로 무력화된다"))
    if out:
        return out, False
    if trim_mm and len(trim_mm) == 2:
        top, right, bottom, left = fr
        if left + right >= trim_mm[0]:
            out.append(_f("SYNC", "FAIL",
                          f"front_frame_mm{where} 좌+우 = {left + right}mm >= 판형 폭 {trim_mm[0]}mm "
                          f"— 폭이 0 이하인 프레임"))
        if top + bottom >= trim_mm[1]:
            out.append(_f("SYNC", "FAIL",
                          f"front_frame_mm{where} 상+하 = {top + bottom}mm >= 판형 높이 {trim_mm[1]}mm "
                          f"— 높이가 0 이하인 프레임"))
        if not out:
            r = front_frame_area_ratio(fr, trim_mm)
            if r is not None and r >= FRONT_FRAME_AREA_WARN:
                out.append(_f("SYNC", "WARN",
                              f"front_frame_mm{where} 프레임 면적이 지면의 {r:.1%} "
                              f"(>= {FRONT_FRAME_AREA_WARN:.0%}) — 봉투가 판형과 사실상 같아 "
                              f"G3-FIT가 항등이 된다(축 무력화 의심). 표지·목차의 실제 "
                              f"padding에서 도출한 값인지 `_front_frame_mm_note`와 대조할 것"))
    return out, not any(x["level"] == "FAIL" for x in out)


def front_frame_findings(style, tokens):
    """tokens `front_frame_mm` 선언값 타당성 — G16-SYNC의 수치 계약 축.

    G16-SYNC는 "색·**수치** 계약 정합"을 표방하면서 이 키를 보지 않았고, 그 침묵 위에서
    선언값 위조 5종이 전부 G3-FIT의 참양성 4건을 0건으로 만들었다(W4 판정 D3).
    **위조가 미선언보다 조용했다** — 미선언은 `declared:false` + WARN을 남기지만
    위조는 `declared:true`에 WARN 0이었다.

    HARD FAIL은 증명 가능한 모순에만 준다: 형식(4원소 수치 배열) · 음수 · 프레임이
    판형보다 큼 · 객체형인데 `cover`/`toc` 중 하나만 유효. 값의 "적정함"(그 스타일의
    실제 padding과 맞는가)은 정적으로 증명할 수 없으므로 검사하지 않는다.
    """
    decl = tokens.get("front_frame_mm")
    if decl is None:
        return []          # 미선언은 결함이 아니다 — G3-FIT이 WARN + 축 생략으로 처리한다
    trim = tokens.get("trim_mm")
    if isinstance(decl, dict):
        out = []
        # `{"cover": ...}`만 선언하면 목차 면이 **조용히** 전부 생략된다
        # (front_frame_for가 None을 돌려 continue). 꺼지는 축이 하필 원 사고 계열
        # (목차 넘침)이라 가장 위험한 형태다 — 두 키를 계약으로 못박는다.
        for key in ("cover", "toc"):
            if key not in decl:
                out.append(_f("SYNC", "FAIL",
                              f"front_frame_mm이 객체형인데 키 {key!r} 부재 — cover(1면)·toc(나머지 "
                              f"앞부속) 둘 다 필수다. 하나만 선언하면 나머지 면의 G3-FIT 프레임 축이 "
                              f"경고 없이 전부 생략된다"))
                continue
            if decl[key] is None:
                out.append(_f("SYNC", "FAIL",
                              f"front_frame_mm[{key!r}] = null — 키 부재와 같은 침묵 생략이다. "
                              f"프레임을 정할 수 없으면 키 자체를 빼고(전 스타일 미선언 폴백) "
                              f"G3-FIT WARN을 받을 것"))
                continue
            out += _front_frame_one(style, f"[{key!r}]", decl[key], trim)[0]
        for key in decl:
            if key not in ("cover", "toc"):
                out.append(_f("SYNC", "WARN",
                              f"front_frame_mm의 미지 키 {key!r} — front_frame_for()가 읽지 않는다"))
        return out
    if isinstance(decl, list):
        return _front_frame_one(style, "", decl, trim)[0]
    return [_f("SYNC", "FAIL",
               f"front_frame_mm = {decl!r} — 리스트(앞부속 공통) 또는 "
               f"{{cover, toc}} 객체만 허용")]


# --------------------------------------------------- diagram.widths 치환 계약

# `... figure`(요소 자신)를 겨냥하는 셀렉터 한 갈래.
_FIG_SEL = re.compile(r"(^|[\s>+~])figure(\.[\w-]+|:[\w-]+(\([^)]*\))?|\[[^\]]*\])*$")
# figure **자손**(`figure svg`·`figure img`)을 겨냥하는 셀렉터. W5 판정 K7-ⓑ 실측:
# `.chapter-body figure svg{width:170mm !important}`는 figure 박스를 129.997mm로 두고
# `<svg>`만 169.999mm로 그린다 — **지면에서 도해의 실폭을 정하는 것은 figure 박스가
# 아니라 그 안의 `<svg>`**이므로 이쪽도 제2의 진리원이다. 다만 자손의 `width: 100%`는
# figure 폭에서 **파생**되는 값이라 진리원이 아니다(insight/magazine의 `figure img`가
# 정확히 그 형태) — 그래서 자손 축은 **절대 길이만** 본다.
_FIG_DESC_TAIL = re.compile(
    r"(^|[\s>+~])(svg|img|picture|canvas|object|embed)(\.[\w-]+|:[\w-]+(\([^)]*\))?|\[[^\]]*\])*$")
_FIG_ANY = re.compile(r"(^|[\s>+~])figure([\s>+~.:\[]|$)")
_CSS_RULE = re.compile(r"([^{}@;]+)\{([^{}]*)\}")
_ABS_LEN = re.compile(r"\d\s*(mm|cm|in|pt|pc|px|em|rem|ch|ex)\b")
_ANY_LEN = re.compile(r"\d\s*(mm|cm|in|pt|pc|px|em|rem|ch|ex|%)")
_COMMENT = re.compile(r"/\*.*?\*/", re.S)

# 폭을 재정의할 수 있는 속성 전량. `width`/`inline-size`(논리 축)는 어떤 길이 리터럴도
# 허용하지 않고(퍼센트 포함), 상·하한 계열은 절대 길이만 잡는다 — `max-width:none`·
# `min-width:0`·`100%`는 상자 폭을 재정의하지 않기 때문이다.
# **`min-width`·`inline-size`는 W5 판정 K7-ⓐⓒ의 실측 우회로다**(둘 다 figure 실폭을
# 129.997 → 169.999mm로 바꾸는데 종전 축은 `width|max-width`만 봐서 통과시켰다).
_FIG_WIDTH_PROPS_ANY = ("width", "inline-size")
_FIG_WIDTH_PROPS_ABS = ("max-width", "min-width", "max-inline-size", "min-inline-size")
_FIG_WIDTH_PROP_RE = re.compile(
    r"(?<![\w-])(max-inline-size|min-inline-size|inline-size|max-width|min-width|width)\s*:\s*([^;{}]+)")


def _css_code(css_text):
    """주석을 걷어낸 CSS. 이 팩들의 주석은 근거를 길게 적어 셀렉터 파싱을 오염시키고
    (쉼표·콜론·중괄호 없는 산문), 무엇보다 **주석에 적힌 `$fig_full_mm`이 실제 치환
    자리로 오인되면** 축이 통째로 무력해진다 — 계약은 코드에만 있어야 한다."""
    return _COMMENT.sub(" ", css_text)


def figure_width_literals(css_text):
    """theme.css에서 figure 폭을 **리터럴로** 못 박은 자리. (셀렉터, 속성, 값, 범위) 목록.

    `width`는 어떤 길이 리터럴도 허용하지 않는다(퍼센트 포함 — magazine의 `width: 100%`가
    바로 tokens 151과 실렌더 164를 갈라놓은 형태다). `max-width`는 절대 길이만 잡는다
    (`none`·`100%`는 상한을 씌우지 않으므로 폭 계약을 훼손하지 않는다).

    범위(scope)는 `"figure"`(상자 자신) 또는 `"descendant"`(figure 안의 `<svg>`/`<img>`).
    자손 축은 W5 판정 K7-ⓑ가 실측한 제2의 진리원이며(figure 130mm · svg 170mm),
    파생값인 퍼센트를 잡지 않도록 절대 길이만 본다.
    """
    out = []
    for sel, body in _CSS_RULE.findall(_css_code(css_text)):
        s = sel.strip()
        if not s or s.startswith("@"):
            continue
        parts = [p.strip() for p in s.split(",")]
        own = any(_FIG_SEL.search(p) for p in parts)
        desc = any(_FIG_ANY.search(p) and _FIG_DESC_TAIL.search(p) for p in parts)
        if not (own or desc):
            continue
        scope = "figure" if own else "descendant"
        for prop, val in _FIG_WIDTH_PROP_RE.findall(body):
            v = val.strip()
            if "$" in v:          # 치환 자리는 계약 성립 — 이 축이 요구하는 형태다
                continue
            rx = _ANY_LEN if (own and prop in _FIG_WIDTH_PROPS_ANY) else _ABS_LEN
            if rx.search(v):
                out.append((" ".join(s.split()), prop, v, scope))
    return out


# --- typst 트랙: theme.typ 판면폭 산출 ---------------------------------------
# `#let theme-tokens = default-tokens + (trim: (w: …mm, …), margin: (…, left: …mm,
#  right: …mm), …)` — 4종 팩이 모두 이 형태이고 값은 mm 리터럴이라 정적으로 읽힌다.
# 판면폭 = trim.w − margin.left − margin.right 이고, base.typ:123 `bookfig(width: 100%)`
# 및 각 팩 `bf-fig`가 이 판면폭을 그대로 도해 폭으로 쓴다(4종 PDF 벡터 실측 확인:
# practical 121.000 / academic 106.000 / essay 88.000 / business 132.500mm).
_TYP_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_TYP_LINE_COMMENT = re.compile(r"//[^\n]*")
_TYP_TRIM_W = re.compile(r"trim\s*:\s*\(\s*w\s*:\s*([\d.]+)\s*mm")
_TYP_MARGIN = re.compile(r"margin\s*:\s*\(([^()]*)\)")
_TYP_SIDE = {s: re.compile(r"(?<![\w-])%s\s*:\s*([\d.]+)\s*mm" % s) for s in ("left", "right")}
_TYP_BFFIG_W = re.compile(r"#let\s+bf-fig\s*\([^)]*\bwidth\s*:")
# 시그니처에 `width:`가 있는지만 보면 **받고 버려도** 통과한다(W5 판정 K8 — practical
# 사본에서 `bookfig(…, width: width, …)`를 `width: 90mm`로 바꿔도 TOTAL FAIL=0이었다).
# 3단계가 고친 결함(md2typ가 width를 안 넘김)이 함수 한 줄 안쪽으로 이동한 것과 동치다.
# 그래서 **본문이 그 인자를 실제로 소비하는가**(`width: width`)를 함께 본다.
_TYP_BFFIG_DEF = re.compile(r"#let\s+bf-fig\s*\(")
_TYP_BFFIG_CONSUME = re.compile(r"\bwidth\s*:\s*width\b")


def typ_bffig_body(code):
    """`#let bf-fig(...)` 정의 본문(다음 최상위 `#let`까지). 없으면 None."""
    m = _TYP_BFFIG_DEF.search(code)
    if not m:
        return None
    nxt = re.search(r"\n#let\s", code[m.end():])
    return code[m.start(): m.end() + (nxt.start() if nxt else len(code))]


def typ_code(text):
    """주석을 걷어낸 .typ 소스. 이 팩들은 근거를 `//` 주석으로 길게 적는데, 거기
    적힌 예시 수치가 계약값으로 오인되면 축이 통째로 헛돈다(2단계 CSS에서 실제로
    난 위음성 — 주석 속 `$fig_full_mm`을 치환 자리로 셌다)."""
    return _TYP_LINE_COMMENT.sub(" ", _TYP_COMMENT.sub(" ", text))


def typ_body_width_mm(theme_typ_text):
    """theme.typ가 선언한 판면폭(mm). 형태가 다르면 None — 추정하지 않는다."""
    code = typ_code(theme_typ_text)
    mt = _TYP_TRIM_W.search(code)
    if not mt:
        return None
    # trim 바로 뒤의 margin 튜플만 본다. 뒷부분의 `margin: (top: t.margin.top, …)`
    # 재선언은 mm 리터럴이 아니라 애초에 잡히지 않지만, 범위를 좁혀 두는 편이 안전하다.
    mm = _TYP_MARGIN.search(code, mt.end())
    if not mm:
        return None
    sides = {}
    for side, rx in _TYP_SIDE.items():
        ms = rx.search(mm.group(1))
        if not ms:
            return None
        sides[side] = float(ms.group(1))
    return round(float(mt.group(1)) - sides["left"] - sides["right"], 6)


def widths_relation_findings(style, tokens, widths):
    """G16-SYNC widths **값** 축 — 관계 불변식 `0 < twothirds ≤ full ≤ trim_mm[0]`. HARD.

    W5 판정 K1(치명)의 봉합이다. `diagram.widths`는 pt 환산의 유일 기준이고 6단계 라벨
    급수 주입은 그 기준으로 목표 pt를 **역산**한다. 그래서 값이 틀리면 주입이 그 틀린
    값에 정확히 맞춰 라벨을 줄이고, 하한·상한 두 판정도 같은 틀린 값으로 재므로
    **셋이 사이좋게 통과한다** — 셋이 같은 입력을 공유하기 때문에 서로를 견제하지 못한다
    (실측: insight `twothirds` 106 → 400에서 게이트 전건 초록, 산출 SVG의 실 급수는 2.3~2.9pt).

    값의 "옳음"은 정적으로 증명할 수 없지만 **관계**는 증명할 수 있다. 이 세 부등식은
    tokens 안에서 닫히므로(trim_mm은 판형 선언이고 widths와 독립적으로 쓰인다) html·typst
    양 트랙 공통으로 성립한다 — typst ③'(판면폭 대조)이 `full`만 보고 `twothirds`를
    어느 트랙에서도 보지 않던 좌표(K9)가 이 축으로 닫힌다.

      · `twothirds ≤ full` — 2/3폭이 전폭보다 넓을 수는 없다(이름 자체의 계약).
      · `full ≤ trim_mm[0]` — 판면폭은 재단 폭을 넘을 수 없다(여백이 0 이상이므로).
    등호를 허용하는 이유: 여백 0(전면 도해)·full == twothirds(2/3폭 미사용) 스타일을
    이 축이 발명해서 막지 않기 위해서다. 실 6스타일은 전부 강부등식으로 통과한다.
    """
    out = []

    def _num(x):
        return isinstance(x, (int, float)) and not isinstance(x, bool)

    full_v, tt_v = widths.get("full"), widths.get("twothirds")
    trim = tokens.get("trim_mm")
    trim_w = trim[0] if (isinstance(trim, list) and len(trim) == 2 and _num(trim[0])) else None
    if _num(tt_v) and _num(full_v) and tt_v > 0 and full_v > 0 and tt_v > full_v:
        out.append(_f("SYNC", "FAIL",
                      f"diagram.widths.twothirds {tt_v}mm > full {full_v}mm — 2/3폭이 전폭보다 넓다. "
                      f"widths는 도해 pt 환산의 유일 기준이고 라벨 급수 주입이 이 값으로 목표 pt를 "
                      f"역산하므로, 값이 틀리면 밴드·하한·주입이 **같은 거짓 기준으로 자기정합**해 "
                      f"전건 통과한다(W5 K1)"))
    if trim_w is None:
        if _num(full_v):
            out.append(_f("SYNC", "WARN",
                          f"trim_mm 부재/형식 오류 — diagram.widths.full({full_v}) 상한 대조 생략, "
                          f"수동 감사 항목"))
    else:
        for key, v in (("full", full_v), ("twothirds", tt_v)):
            if _num(v) and v > 0 and v > trim_w:
                out.append(_f("SYNC", "FAIL",
                              f"diagram.widths.{key} {v}mm > trim_mm[0] {trim_w:g}mm(재단 폭) — "
                              f"판면폭이 판형을 넘을 수 없다. 도해 pt 환산 기준이 물리적으로 불가능한 "
                              f"값이면 밴드·하한·주입이 전부 그 값으로 재므로 조용히 통과한다(W5 K1·K9)"))
    return out


def widths_findings(style, tokens, theme_text, engine, style_dir=None):
    """G16-SYNC widths 축 — tokens.diagram.widths ↔ theme.css 치환 계약.

    셋이 갈라진 상태(선언 tokens / 실렌더 CSS / 정본 STYLE.md)가 W5 조사에서 6스타일 중
    5스타일에 있었고, 그중 magazine은 151 선언 대 164 실렌더로 도해 글자 하한 검사가
    1.086배 과엄격하게 돌았다. 값의 "옳음"은 정적으로 증명할 수 없지만 **CSS가 tokens를
    받고 있는가**는 증명할 수 있다 — 그래서 이 축은 오직 배선만 본다:

      ① `diagram.widths`가 full·twothirds 두 키를 양수로 갖는다
         (부재 시 render_diagrams.mjs:240 `if (!minPt || !widthMm) return []`로
          글자 하한 검사가 **조용히 꺼진다** — 침묵 생략이라 HARD)
      ② theme.css에 두 플레이스홀더가 실존한다(= 치환 계약 성립)
      ③ figure 폭을 리터럴로 다시 못 박은 자리가 없다(= 파생이 아니라 제2의 진리원)

    ②③은 CSS를 실제로 렌더하는 html 엔진 한정이다. typst 4종은 theme.css 자체가 없고
    폭이 md2typ.py → theme.typ `bf-fig(width:)` 경로로 간다 — 대칭 배선 검사가 따로 붙는다:

      ②' theme.typ `bf-fig`가 `width:` 인자를 받는다(= md2typ가 발행한 폭이 도달한다)
      ③' `diagram.widths.full` == theme.typ 판면폭(trim.w − margin.left − margin.right)

    ③'은 CSS 축과 성격이 다르다 — 배선이 아니라 **값**을 본다. typst는 폭 산출식이
    theme.typ의 mm 리터럴 두 줄에 그대로 있어(플랜 전제교정 ③의 "스캔 범위 밖"이 여기엔
    해당하지 않는다) 판면폭을 정적으로 계산할 수 있고, `bf-fig`의 기본값 `width: 100%`가
    그 판면폭이라는 것을 4종 PDF 벡터 실측이 확인했다. 그래서 HTML 트랙에서는 증명 불가였던
    "선언 == 실렌더"가 typst에서는 증명 가능하다. 실제로 이 축이 없던 동안 practical 115
    (실 121)·essay 78(실 88)·business 142(실 132.5)가 갈라져 있었고, business는 **느슨한**
    쪽이라 하한 미달 도해가 통과할 수 있었다.
    """
    out = []
    dg = tokens.get("diagram") if isinstance(tokens.get("diagram"), dict) else {}
    widths = dg.get("widths")
    if not isinstance(widths, dict):
        out.append(_f("SYNC", "FAIL",
                      f"diagram.widths 부재/비객체({type(widths).__name__}) — "
                      f"{'·'.join(FIG_WIDTH_KEYS)} 두 키가 도해 폭의 단일 진리원이다. "
                      f"부재 시 render_diagrams의 글자 하한 검사가 경고 없이 꺼진다"))
        widths = {}
    for key in FIG_WIDTH_KEYS:
        v = widths.get(key)
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            out.append(_f("SYNC", "FAIL",
                          f"diagram.widths.{key} = {v!r} — 수치(mm)여야 한다. "
                          f"bf.width={key} 도해의 pt 환산 기준이 사라진다"))
        elif v <= 0:
            out.append(_f("SYNC", "FAIL", f"diagram.widths.{key} = {v} — 양수(mm)여야 한다"))
    out += widths_relation_findings(style, tokens, widths)
    if engine != "html" or theme_text is None:
        # ---- typst 트랙: theme.typ 배선 + 판면폭 대조 ----
        sd = Path(style_dir) if style_dir else (SKILL / "styles" / style)
        tp = sd / "theme.typ"
        if not tp.exists():
            return out                  # 팩 실물이 없다 — 다른 축이 다룰 문제다
        typ = tp.read_text(encoding="utf-8")
        typ_src = typ_code(typ)
        if not _TYP_BFFIG_W.search(typ_src):
            out.append(_f("SYNC", "FAIL",
                          f"styles/{style}/theme.typ의 bf-fig가 width 인자를 받지 않는다 — "
                          f"md2typ가 발행하는 `#bf-fig(..., width: Nmm)`이 도달하지 못하고 "
                          f"(unknown argument로 typst 컴파일이 죽는다) bf.width 선언이 무시된다"))
        else:
            body = typ_bffig_body(typ_src)
            if body is not None and not _TYP_BFFIG_CONSUME.search(body):
                out.append(_f("SYNC", "FAIL",
                              f"styles/{style}/theme.typ의 bf-fig가 width 인자를 **받고 버린다** — "
                              f"본문에 `width: width` 전달이 없다. 시그니처만 맞추면 md2typ가 발행한 "
                              f"폭이 조용히 무시되고 도해가 다른 폭으로 그려진다"
                              f"(render_diagrams는 여전히 tokens.diagram.widths로 pt를 환산한다)"))
        body_mm = typ_body_width_mm(typ)
        full = widths.get("full")
        if body_mm is None:
            # 형태가 바뀌면 조용히 통과시키지 않는다 — 다만 판면 산출식을 추정하지도
            # 않으므로 FAIL이 아니라 수동 감사 요청(WARN)이다.
            out.append(_f("SYNC", "WARN",
                          f"styles/{style}/theme.typ에서 판면폭(trim.w − margin.left/right)을 "
                          f"읽지 못했다 — diagram.widths.full({full}) 대조 생략, 수동 감사 항목"))
        elif isinstance(full, (int, float)) and not isinstance(full, bool) and full > 0 \
                and abs(full - body_mm) > 0.01:
            out.append(_f("SYNC", "FAIL",
                          f"diagram.widths.full {full}mm != theme.typ 판면폭 {body_mm:g}mm "
                          f"(trim.w − margin.left − margin.right) — bf-fig가 판면폭으로 그리는데 "
                          f"render_diagrams.mjs는 {full}로 pt를 환산한다"
                          f"({'과엄격' if full < body_mm else '느슨'} "
                          f"{max(full, body_mm) / min(full, body_mm):.3f}배). "
                          f"tokens가 단일 진리원이므로 이 값을 판면폭에 맞출 것"))
        return out
    code = _css_code(theme_text)
    for key, ph in FIG_WIDTH_KEYS.items():
        if not re.search(r"\$\{?%s\}?(?![\w])" % re.escape(ph), code):
            out.append(_f("SYNC", "FAIL",
                          f"theme.css에 ${ph} 플레이스홀더 부재 — diagram.widths.{key}"
                          f"({widths.get(key)})가 실렌더에 도달하지 못한다. "
                          f"figure 폭은 CSS 리터럴이 아니라 이 치환으로 받을 것"))
    for sel, prop, val, scope in figure_width_literals(theme_text):
        where = ("figure 폭 리터럴 잔존" if scope == "figure"
                 else "figure 안 그림(<svg>/<img>) 폭 리터럴 — 지면에서 도해의 실폭을 정하는 것은 "
                      "figure 상자가 아니라 그 안의 그림이다")
        out.append(_f("SYNC", "FAIL",
                      f"theme.css `{sel}`의 {prop}: {val} — {where}. "
                      f"tokens.diagram.widths와 갈라지는 제2의 진리원이다"
                      f"(${FIG_WIDTH_KEYS['full']}/${FIG_WIDTH_KEYS['twothirds']}로 받을 것)"))
    return out


# ------------------------------------------------- toc_layout 카탈로그 (G16-SYNC)
# 왜: 각 스타일의 목차는 이미 **서로 다른 레이아웃**이지만(insight 행잉 2레벨 /
# magazine 대형 단면 / business 대형 번호 / practical 2단 균형 / academic 번호칼럼
# 흐름 / essay 무리더 단일 레벨) 그 사실이 어디에도 선언돼 있지 않았다. 선언이 없으면
# ㉠팩을 고칠 때 "이 스타일이 어떤 목차 문법인가"가 theme 파일을 읽어야만 알 수 있고
# ㉡레벨 수·리더·급수 같은 레이아웃 불변식이 조용히 깨져도 신호가 없다(리더 점선을
# 넣어도, 급수를 올려도 전 게이트 초록 — S1 toc_overflow와 같은 형태의 무선언 구멍).
#
# 카탈로그를 **스킬 한 곳**에 둔다(팩이 아니라). 레이아웃은 여러 팩이 공유할 수 있는
# 어휘이고, 팩마다 정의를 복제하면 그 자체가 제2의 진리원이 된다. 팩은 이름만 고른다
# (tokens.json `toc_layout`) — toc_overflow가 값만 선언하고 허용값 표는 build_html의
# TOC_OVERFLOW_MULTIPAGE에 있는 것과 같은 배치다.
#
# 각 필드의 출처는 **theme 실물**이며 값은 현행 구현의 실측이다:
#   styles       : 그 레이아웃을 실제로 구현한 팩. 레이아웃은 theme 파일에 사는 물건이라
#                  목록에 스타일을 추가하려면 그 팩에 구현이 먼저 있어야 한다.
#   max_levels   : 목차가 싣는 최대 표제 레벨(html은 tokens.toc_levels와 대조).
#   leader       : 점선 리더 사용 여부. theme.css/theme.typ 리터럴과 대조한다.
#   size_cap_pt  : `.toc*`(html) / 목차 코드(typst)에 리터럴로 박힌 급수의 상한.
#                  값은 현행 최대치 그대로다 — 여백이 아니라 **캘리브레이션 잠금**이다
#                  (insight 30pt는 build_html 다면 프로파일 top_mm 61.429의 입력이고, magazine
#                  22pt는 toc_capacity.size_pt와 같은 수다. 올리면 재캘리브레이션 없이는
#                  목차가 넘치고 Chromium 전역 축소로 조용히 나간다).
#                  None = 급수가 리터럴이 아니라 변수 주입이라 정적 상한이 성립하지 않음.
TOC_LAYOUTS = {
    "hanging-two-level": {
        "styles": ("insight",),
        "max_levels": 2,
        "leader": False,
        "size_cap_pt": 30.0,   # .toc-word 30pt(Contents 워드마크) — 높이 모델의 입력
        "_why": "장 행 + 들여쓴 절 행, 리더 없이 우단 쪽번호. 넘치면 다면 발행(toc_overflow=paginate)",
    },
    "spread-single-level": {
        "styles": ("magazine",),
        "max_levels": 1,
        "leader": False,
        "size_cap_pt": 22.0,   # .toc-title 22pt = tokens.toc_capacity.size_pt
        "_why": "스프레드 1면 고정 · 장 레벨만 · 대형 제목 + 요약 꼬리. 넘침은 die(toc_overflow=single)",
    },
    "display-numeral": {
        # W6 S6: magazine이 HTML 이식을 보유(오버레이 toc-display-numeral.css — 기본
        # 레이아웃이 아니라 book.json `toc_layout` 선언으로만 켜지는 대안 구현이다).
        "styles": ("business", "magazine"),
        "max_levels": 2,
        "leader": False,
        # 급수 상한이 구현마다 다르다 — business는 tier 변수 주입이라 정적 상한이 없고
        # (None), magazine 오버레이는 리터럴이라 40pt 잠금이다(.toc-bn-num 40pt =
        # toc_capacity_alt["display-numeral"] 캘리브레이션의 입력. 해석은 toc_size_cap()).
        "size_cap_pt": {"business": None, "magazine": 40.0},
        "_why": "좌측 대형 장번호 칼럼 + 우측 제목/절, 리더 없음. business는 1면 완결 "
                "tier 적응 축소, magazine은 단면 고정 + toc_capacity_alt 용량 계약",
    },
    "twocol-balanced": {
        "styles": ("practical",),
        "max_levels": 2,
        "leader": True,        # toc-leader = repeat(circle) 점선
        "size_cap_pt": 23.0,
        "_why": "헤더 밴드 + CH│NN 칩 · 점선 리더 · 넘치면 2단 균형 분할(S0 가드가 잘림을 panic으로)",
    },
    "academic-flow": {
        "styles": ("academic",),
        "max_levels": 2,
        "leader": False,
        "size_cap_pt": 16.0,
        "_why": "번호 칼럼 14mm + 제목 + 우단 쪽번호, 리더 점선 없음(theme.typ:297 선언)",
    },
    "flush-single-level": {
        "styles": ("essay",),
        "max_levels": 1,
        "leader": False,
        "size_cap_pt": 13.0,
        "_why": "장 레벨만 · 좌측 정렬 + 우단 쪽번호 · 리더선 금지(theme.typ:230 선언)",
    },
}

# 단면 목차 용량 계약의 필수 7키 — build_html.check_single_page_toc와
# toc_capacity_alt 오버레이 축(아래 overlay_findings)이 같은 튜플을 소비한다.
# 정의를 여기(단일 진리원) 두고 build_html이 별칭으로 가져간다 — 반대 방향이면
# 게이트가 빌더를 import해야 해서 순환이 된다.
TOC_CAPACITY_KEYS = ("top_mm", "pitch_mm", "tail_mm", "bottom_mm",
                     "title_avail_mm", "font", "size_pt")

# html 빌더의 toc_levels 폴백(미선언 = 2레벨). 정본을 여기 두고 build_html이 가져간다 —
# 축 ③이 "부재 시 빌더가 실제로 쓸 값"을 대조하려면 게이트와 빌더가 같은 수를 봐야
# 하는데, 빌더에 리터럴 2가 따로 살면 폴백만 바꿔도 축 ③이 낡은 수로 판정한다.
TOC_LEVELS_DEFAULT = 2


def toc_size_cap(spec, style):
    """레이아웃 급수 상한의 단일 해석기 — 스칼라(전 스타일 공통) 또는 스타일별 dict.

    dict에 그 스타일 키가 없으면 None(상한 미선언)으로 떨어진다 — 구현이 없는 스타일에
    상한을 발명하지 않는다. 소비자는 layout_findings 축 ⑤·overlay_findings·M17-㉢."""
    cap = spec["size_cap_pt"]
    return cap.get(style) if isinstance(cap, dict) else cap


# `.toc`로 시작하는 클래스만 겨냥한다(.toc / .toc-title / .tocpg / .toc-page …).
# `.subtoc` 같은 뒤섞임을 막으려 앞에 단어문자·하이픈이 오면 제외한다.
_TOC_SEL_RE = re.compile(r"(?<![\w-])\.toc[\w-]*")
# font-size 선언은 **값 전체**를 잡는다 — pt/px/mm 리터럴만 잡으면 var()·em 경유가
# 무음 통과한다(적대검증 v-s2 C1: `font-size: var(--x)`에 :root 60pt를 실어도 전 축
# 초록이었다). 리터럴 해석은 아래 _size_value_pt가, 못 푸는 값은 unresolved로 올린다.
_TOC_FONT_SIZE_DECL_RE = re.compile(r"(?<![\w-])font-size\s*:\s*([^;}]+)")
_SIZE_LITERAL_RE = re.compile(r"^\s*([\d.]+)\s*(pt|px|mm)\s*(?:!important\s*)?$")
_CSS_VAR_USE_RE = re.compile(r"^\s*var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*))?\)\s*(?:!important\s*)?$")
# 커스텀 프로퍼티 정의(`--x: 60pt`). 1단 해석의 재료 — var(var(…)) 다단은 풀지 않고
# unresolved로 올린다(정적 해석의 선, 아래 _layout_axes 주석).
_CSS_VAR_DEF_RE = re.compile(r"(--[\w-]+)\s*:\s*([^;{}]+)")
# CSS 점선 리더의 실현 수단 목록 — 이 목록 자체가 계약이다(정규식이 아는 관용구만 잡는다).
# border 계열 dotted/**dashed**(dashed 짧은 대시도 지면에선 리더선이다 — v-s2 B1) ·
# 점 배경 그라데이션 · 생성 콘텐츠 점열(ASCII `.` 나열 + **미들닷·리더 도트류 유니코드**
# — v-s2 B2의 `content:"······"`) · leader() 함수.
_CSS_LEADER_RE = re.compile(
    r"(?<![\w-])dotted(?![\w-])|(?<![\w-])dashed(?![\w-])"
    r"|repeating-linear-gradient|radial-gradient"
    r"|(?<![\w-])leader\s*\(|content\s*:\s*[^;}]*\.\s*\.\s*\."
    r"|content\s*:\s*[^;}]*[·•․‥‧∙・]\s*[·•․‥‧∙・]"
    r"|content\s*:\s*[^;}]*[…⋯]")
# typst의 직접 리더 관용구는 `repeat(...)`/`repeat[...]`다(practical toc-leader).
# 간접(정의는 밖, 호출만 목차 영역)은 toc_typ_leader가 #let 이름 추적으로 1단 잡는다.
_TYP_LEADER_RE = re.compile(r"(?<![\w-])repeat\s*[(\[]")
_TYP_SIZE_PT_RE = re.compile(r"(?<![\w-])size\s*:\s*([\d.]+)\s*pt(?![\w-])")
# typst 상대 급수(`size: 3em`) — 상속 컨텍스트가 렌더에서 정해지므로 정적 확정은 불가,
# 보수 환산으로 침묵만 막는다(해석은 _layout_axes ⑤).
_TYP_SIZE_EM_RE = re.compile(r"(?<![\w-])size\s*:\s*([\d.]+)\s*em(?![\w-])")
_PT_PER = {"pt": 1.0, "px": 0.75, "mm": 72.0 / 25.4}


def _size_value_pt(value, css_vars):
    """font-size 값 하나를 pt로. (pt, None) | 해석 불가면 (None, 사유)."""
    v = value.strip()
    m = _SIZE_LITERAL_RE.match(v)
    if m:
        return float(m.group(1)) * _PT_PER[m.group(2)], None
    m = _CSS_VAR_USE_RE.match(v)
    if m:
        name, fallback = m.group(1), m.group(2)
        if name in css_vars:
            lit = _SIZE_LITERAL_RE.match(css_vars[name].strip())
            if lit:
                return float(lit.group(1)) * _PT_PER[lit.group(2)], None
            return None, f"var({name})가 비리터럴 {css_vars[name].strip()!r}로 정의(다단 간접)"
        if fallback is not None:
            lit = _SIZE_LITERAL_RE.match(fallback.strip())
            if lit:
                return float(lit.group(1)) * _PT_PER[lit.group(2)], None
        return None, f"var({name}) 정의 미발견"
    return None, f"비리터럴 값 {v!r}"


def toc_css_facts(css_text, var_src=None):
    """CSS의 `.toc*` 겨냥 규칙만 골라 (최대 급수pt, 점선 리더 유무, 미해석 급수 목록).

    급수가 하나도 없으면 (None, …) — "관측 대상 없음"과 "0pt"를 구별한다.
    var() 간접은 커스텀 프로퍼티 정의에서 **1단만** 해석한다(css_text + var_src 합산 —
    오버레이는 theme.css 뒤에 이어붙는 캐스케이드라 :root 정의를 theme.css에서 상속받는다).
    다단 간접·em·calc 등 못 푸는 선언은 unresolved로 올린다 — 축 ⑤가 WARN으로 발화해
    "리터럴만 훑고 초록"이 되지 않게 한다(적대검증 v-s2 C1).
    """
    code = _css_code(css_text)
    css_vars = dict(_CSS_VAR_DEF_RE.findall(_css_code(var_src) if var_src else ""))
    css_vars.update(_CSS_VAR_DEF_RE.findall(code))
    mx, leader, unresolved = None, False, []
    for sel, body in _CSS_RULE.findall(code):
        s = sel.strip()
        if not s or s.startswith("@"):
            continue
        if not any(_TOC_SEL_RE.search(p) for p in s.split(",")):
            continue
        for value in _TOC_FONT_SIZE_DECL_RE.findall(body):
            pt, why = _size_value_pt(value, css_vars)
            if pt is not None:
                mx = pt if mx is None else max(mx, pt)
            else:
                unresolved.append(f"`{' '.join(s.split())}` font-size:{value.strip()} — {why}")
        if _CSS_LEADER_RE.search(body):
            leader = True
    return mx, leader, unresolved


def toc_typ_lines(typ_text):
    """theme.typ의 **목차 코드 줄**. `toc`를 언급하는 줄에서 시작해 빈 줄까지 이어진다.

    왜 중괄호 균형이 아니라 줄 단위인가: typst의 목차 코드는 `#let toc-leader(pad) =
    box(...)`처럼 **괄호 본문**으로도 쓰여 중괄호 매칭이 통째로 빗나간다(practical
    toc-leader가 정확히 그 형태이고, 그것이 이 팩에서 유일한 리더 선언이다). 반면 4종
    팩 모두 목차 코드는 빈 줄로 구분된 덩어리 안에 있고 그 덩어리의 첫 줄은 반드시
    `toc`를 이름에 포함한다(`#let toc-*`, `if toc {`, `#let practical-toc`).
    주석은 먼저 걷어낸다 — `// ---- TOC ----` 같은 표제가 구간을 열면 안 된다.
    """
    out, inreg = [], False
    for line in typ_code(typ_text).split("\n"):
        if "toc" in line.lower():
            inreg = True
        elif inreg and not line.strip():
            inreg = False
        if inreg:
            out.append(line)
    return out


_TYP_LET_NAME_RE = re.compile(r"#let\s+([A-Za-z_][\w-]*)")


def toc_typ_leader(typ_text, toc_lines):
    """typst 목차 영역의 점선 리더 유무 — 직접 관용구 + **헬퍼 간접 1단**.

    직접: 영역 줄의 `repeat(`/`repeat[`. 간접: 파일 어디서든 `#let 이름 = … repeat …`으로
    정의된 헬퍼를 목차 영역이 이름으로 호출하는 형태 — 정의 줄엔 toc가 없고 호출 줄엔
    repeat가 없어 영역 줄 스캔만으로는 무음 통과했다(적대검증 v-s2 D1). 전체 소스에서
    repeat를 품은 #let 이름을 모아 영역 줄의 호출과 대조한다.

    **정적 한계(계약)**: 추적은 1단이다 — 헬퍼가 리더 헬퍼를 다시 감싸는 2단 체인은
    잡지 못한다. 렌더 후 게이트에 리더를 보는 축이 없으므로(G14는 쪽번호·색·대비,
    G1은 축소, G3은 겹침·프레임 — 리더 점열은 정상 텍스트로 렌더된다. w6 재작업2
    실측: academic 사본에 2단 체인 주입 → 컴파일 성공·점열 실렌더·qc_gate FAIL 축이
    무주입 베이스라인과 완전 동일 = 신규 검출 0) 이 목록·추적이 **유일 방어선**이고,
    새 리더 관용구·다단 체인은 이 함수에 등재해야 잡힌다.
    """
    if any(_TYP_LEADER_RE.search(ln) for ln in toc_lines):
        return True
    code = typ_code(typ_text)
    helpers = [name for line in code.split("\n")
               for name in _TYP_LET_NAME_RE.findall(line)
               if _TYP_LEADER_RE.search(line)]
    for name in helpers:
        call = re.compile(r"(?<![\w-])%s\s*[(\[]" % re.escape(name))
        for ln in toc_lines:
            # 정의 줄 자신은 호출이 아니다(practical toc-leader처럼 정의가 영역 안에
            # 있으면 직접 관용구가 이미 잡았다).
            if call.search(ln) and not _TYP_LET_NAME_RE.match(ln.strip()):
                return True
    return False


def layout_findings(style, tokens, theme_text, engine, style_dir=None):
    """G16-SYNC toc_layout 축 전체 = 기본 레이아웃 5축 + 오버레이 축.

    기본 5축(_layout_axes)이 어느 지점에서 끊기든(카탈로그 밖 이름·theme 부재 WARN)
    오버레이 축은 반드시 돈다 — 오버레이 파일은 기본 선언과 독립된 실물이라, 기본
    선언이 깨졌다고 오버레이 검사가 조용히 꺼지면 그 틈이 두 번째 무선언 구멍이 된다.
    """
    sd = Path(style_dir) if style_dir else (SKILL / "styles" / style)
    return (_layout_axes(style, tokens, theme_text, engine, sd)
            + overlay_findings(style, tokens, sd))


def _layout_axes(style, tokens, theme_text, engine, sd):
    """기본 toc_layout 5축 — 선언한 목차 레이아웃과 theme 실물의 일치.

    판정 5축(전부 텍스트 레벨 — 렌더 0회):
      ① toc_layout 값이 카탈로그에 있는가
      ② 이 스타일이 그 레이아웃의 allowed_styles(=구현 보유 팩)에 있는가
      ③ tokens.toc_levels ≤ 레이아웃 max_levels — 비int(float/str/bool)는 malformed
         FAIL(labelBand·enforce와 같은 "JSON 타입이 계약" 교리), html은 **부재도 빌더
         폴백값(TOC_LEVELS_DEFAULT)으로 대조**한다(키 삭제가 검사 밖이면 magazine처럼
         max_levels=1인 팩에서 폴백 2가 무검사로 절 마커·레벨2 북마크를 발행한다 —
         적대검증 v-s2 A1~A4)
      ④ theme 실물의 점선 리더 유무 ↔ 선언 leader 일치 — html은 theme.css + theme.html
         <style> 블록 + 오버레이가 아닌 인라인, typst는 목차 영역 직접 관용구 + 헬퍼
         간접 1단(toc_typ_leader)
      ⑤ `.toc*`(html) / 목차 코드(typst) 급수 ≤ size_cap_pt — var() 1단 해석 포함,
         못 푸는 선언은 WARN으로 발화(침묵 금지). theme.html의 **인라인 font-size는
         값 무관 FAIL**이다: 축 ⑤의 잠금은 CSS 스캔으로만 성립하므로 인라인 급수는
         어느 값이든 잠금 밖 선언이다(v-s2 C2 — 종전엔 theme.html을 아예 읽지 않았다).
         typst `size: Nem`은 상속 컨텍스트가 렌더에서 정해져 정적 확정이 불가하다 —
         영역 내 최대 pt 리터럴(없으면 typst 기본 11pt)을 보수 기저로 환산해 상한
         초과면 FAIL, 아니면 "확정 불가" WARN(어느 쪽이든 침묵하지 않는다. v-s2 D2).

    **정적 판정의 한계(계약)**: 리더 관용구 목록 밖의 실현 수단·typst 2단 헬퍼 체인·
    치환 변수(`$…`)에 실려 오는 인라인 값은 렌더 전 스캔이 원리적으로 못 잡는다.
    렌더 후 게이트는 이 축들의 2차 방어가 **아니다** — 리더 점열은 정상 텍스트로
    렌더되고(w6 재작업2 실측: 체인 리더 주입 → 점열 실렌더·qc_gate 신규 검출 0,
    toc_typ_leader 주석), 급수 초과는 넘침이 문서 전역 축소로 이어지는 경우에만
    G1-SCALE이 늦게 잡는다(insight-ondevice-ai 실사고 — M7이 회귀 고정). 그래서
    이 목록·해석기가 유일 방어선이고, 새 관용구는 여기 등재가 곧 방어다.

    **폭발 금지**: theme 실물이 하나도 없는 디렉토리(styles/blueprint-web처럼 tokens.json
    만 있는 작업 중 산출물)는 목차 구현 자체가 없으므로 WARN 1행으로 skip한다 —
    전수 스캔이 그런 디렉토리에서 FAIL 더미를 뱉으면 게이트가 무시당하고, 무시당하는
    게이트는 없는 게이트다.
    """
    out = []
    typ_p, html_p, css_p = sd / "theme.typ", sd / "theme.html", sd / "theme.css"
    if not (typ_p.exists() or html_p.exists() or css_p.exists()):
        return [_f("SYNC", "WARN",
                   f"styles/{style}: theme.css/theme.html/theme.typ 모두 부재 — 목차 구현이 "
                   f"없는 디렉토리라 toc_layout 축 skip(계약 없는 팩은 전수 스캔의 폭발원이다)")]

    # ---- ① 값 ∈ 카탈로그 ----
    name = tokens.get("toc_layout")
    spec = TOC_LAYOUTS.get(name) if isinstance(name, str) else None
    if spec is None:
        out.append(_f("SYNC", "FAIL",
                      f"styles/{style}/tokens.json의 `toc_layout`={name!r} — 카탈로그 밖이거나 "
                      f"미선언이다. 허용값 {'|'.join(sorted(TOC_LAYOUTS))} "
                      f"(g16_tokens.TOC_LAYOUTS가 단일 진리원). 선언이 없으면 목차 문법이 "
                      f"theme 파일 실물에만 있어 레벨 수·리더·급수 불변식이 조용히 깨진다"))
        return out

    # ---- ② 스타일 ∈ allowed_styles ----
    if style not in spec["styles"]:
        out.append(_f("SYNC", "FAIL",
                      f"toc_layout={name!r}는 {'/'.join(spec['styles'])}가 구현한 레이아웃인데 "
                      f"styles/{style}이 선언했다 — 레이아웃은 theme 실물에 사는 물건이라 "
                      f"이름만 빌려 오면 선언과 지면이 갈라진다. 이 팩에 구현을 먼저 넣고 "
                      f"TOC_LAYOUTS['{name}']['styles']에 추가할 것"))

    # ---- ③ toc_levels ≤ max_levels ----
    # 비int는 malformed다 — 빌더는 값을 산술·비교에 그대로 소비하므로 float는 절삭 없는
    # 우연 통과, str는 비교 오동작, bool True는 `>= 2` 비교에서 1레벨로 **조용히 뒤집힌다**
    # (v-s2 A4 실측). labelBand "부재도 malformed"·enforce "JSON bool만" 과 같은 교리.
    lv_declared = "toc_levels" in tokens
    lv = tokens.get("toc_levels")
    if lv_declared and (not isinstance(lv, int) or isinstance(lv, bool)):
        out.append(_f("SYNC", "FAIL",
                      f"toc_levels={lv!r}({type(lv).__name__}) — JSON 정수만 허용한다. "
                      f"빌더가 이 값을 폴백 없이 그대로 소비하므로 bool은 1레벨로 뒤집히고 "
                      f"float/str는 비교가 우연에 좌우된다(labelBand.enforce와 같은 계약)"))
    else:
        if lv_declared:
            lv_eff, how = lv, f"toc_levels={lv}"
        elif engine == "html":
            # html 빌더는 부재를 TOC_LEVELS_DEFAULT로 폴백한다 — 검사가 선언값만 보면
            # 키 한 줄 삭제가 max_levels=1 팩에서 폴백 2를 무검사로 통과시킨다(v-s2 A1).
            lv_eff = TOC_LEVELS_DEFAULT
            how = f"toc_levels 부재(빌더 폴백 {TOC_LEVELS_DEFAULT})"
        else:
            lv_eff = None   # typst 빌더는 toc_levels를 소비하지 않는다 — 부재가 정상.
        if lv_eff is not None and lv_eff > spec["max_levels"]:
            out.append(_f("SYNC", "FAIL",
                          f"{how} > toc_layout={name!r}의 max_levels {spec['max_levels']} — "
                          f"레이아웃이 싣지 못하는 레벨을 목차 계약이 요구한다"
                          + ("" if lv_declared else
                             ". max_levels=1 팩은 toc_levels: 1을 명시로 선언할 것")))

    # ---- ④⑤ theme 실물 스캔 ----
    inline_notes = []
    if engine == "html":
        if theme_text is None:
            out.append(_f("SYNC", "WARN",
                          f"styles/{style}: engine=html인데 theme.css를 읽지 못했다 — "
                          f"toc_layout ④리더·⑤급수 축 skip"))
            return out
        # theme.html도 실물이다 — <style> 블록은 CSS 스캔에 합류시키고(`.toc*` 규칙만
        # 관측), 인라인 style 속성은 아래에서 별도 판정한다. 종전엔 theme.html을 한 번도
        # 읽지 않아 인라인 60pt·<style> 블록 리더가 전부 검사 밖이었다(v-s2 C2).
        html_text = html_p.read_text(encoding="utf-8") if html_p.exists() else ""
        style_blocks = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html_text,
                                            re.S | re.I))
        size_pt, leader, unresolved = toc_css_facts(theme_text + "\n" + style_blocks)
        for m in re.finditer(r"""style\s*=\s*(['"])(.*?)\1""", html_text, re.S):
            decl = m.group(2)
            if re.search(r"(?<![\w-])font-size\s*:", decl):
                inline_notes.append(("size", decl.strip()[:60]))
            if _CSS_LEADER_RE.search(decl):
                inline_notes.append(("leader", decl.strip()[:60]))
        where, unit_note = "theme.css `.toc*` 규칙", "font-size"
    else:
        if not typ_p.exists():
            out.append(_f("SYNC", "WARN",
                          f"styles/{style}: engine={engine}인데 theme.typ 부재 — "
                          f"toc_layout ④리더·⑤급수 축 skip"))
            return out
        typ_text = typ_p.read_text(encoding="utf-8")
        lines = toc_typ_lines(typ_text)
        leader = toc_typ_leader(typ_text, lines)
        sizes = [float(m.group(1)) for ln in lines for m in _TYP_SIZE_PT_RE.finditer(ln)]
        size_pt = max(sizes) if sizes else None
        # em은 상속 기저를 렌더가 정한다 — 영역 내 최대 pt 리터럴(그 영역에서 성립 가능한
        # 최대 컨텍스트)을 보수 기저로, 리터럴이 없으면 typst 기본 본문 11pt로 환산한다.
        # 과대 추정 = 이르게 FAIL = 안전 방향이고, 상한 안이어도 WARN으로 남긴다(v-s2 D2).
        em_base = size_pt if size_pt is not None else 11.0
        unresolved = [f"목차 코드 `size: {m.group(1)}em` — 보수 환산 "
                      f"{float(m.group(1)) * em_base:g}pt(기저 {em_base:g}pt), 정적 확정 불가"
                      for ln in lines for m in _TYP_SIZE_EM_RE.finditer(ln)]
        em_sizes = [float(m.group(1)) * em_base
                    for ln in lines for m in _TYP_SIZE_EM_RE.finditer(ln)]
        if em_sizes:
            size_pt = max(em_sizes + ([size_pt] if size_pt is not None else []))
        where, unit_note = "theme.typ 목차 코드", "size:"

    # ---- ④ 점선 리더 ----
    if leader != spec["leader"]:
        got = "있음" if leader else "없음"
        decl = "있음" if spec["leader"] else "없음"
        out.append(_f("SYNC", "FAIL",
                      f"점선 리더 실물 {got} ≠ toc_layout={name!r} 선언 {decl} ({where}). "
                      f"리더는 목차 문법의 식별 자질이고 각 팩 STYLE.md가 명시로 금지/허용한다 — "
                      f"실물만 바꾸면 그 규범이 선언 없이 뒤집힌다"))
    for kind, decl in inline_notes:
        if kind != "leader":
            continue
        out.append(_f("SYNC", "FAIL",
                      f"theme.html 인라인 style에 점선 리더 관용구: `{decl}` — 리더 선언 대조는 "
                      f"CSS 규칙 스캔으로 성립하므로 인라인 실현은 선언 밖 리더다. "
                      f"theme.css `.toc*` 규칙으로 옮길 것"))

    # ---- ⑤ 급수 상한 ----
    cap = toc_size_cap(spec, style)
    if cap is None:
        pass   # 급수가 변수 주입이라 정적 상한이 성립하지 않는다(카탈로그 _why에 근거). 침묵.
    else:
        if size_pt is None and not unresolved:
            out.append(_f("SYNC", "WARN",
                          f"{where}에 {unit_note} 리터럴 0건 — toc_layout={name!r}의 급수 상한 "
                          f"{cap}pt가 관측 대상을 잃었다(축이 조용히 꺼진 상태). 급수를 변수로 "
                          f"옮겼다면 TOC_LAYOUTS['{name}']['size_cap_pt']를 None으로 명시할 것"))
        elif size_pt is not None and size_pt > cap + 1e-6:
            out.append(_f("SYNC", "FAIL",
                          f"{where}의 최대 급수 {size_pt:g}pt > toc_layout={name!r} 상한 {cap}pt — "
                          f"목차 급수는 높이 모델·용량 계약의 입력이라 재캘리브레이션 없이 올리면 "
                          f"목차가 넘치고 Chromium 전역 축소로 조용히 출하된다"))
        # 미해석 선언은 잡혔든 안 잡혔든 침묵하지 않는다 — 종전엔 "리터럴 0건"일 때만
        # WARN이라, 리터럴이 하나라도 남아 있으면 var() 간접 60pt가 무음이었다(v-s2 C1).
        for note in unresolved:
            out.append(_f("SYNC", "WARN",
                          f"{where}의 미해석 급수 선언 — {note}. 정적 상한 {cap}pt 판정이 "
                          f"이 선언을 확정하지 못한다(다단 var·상대 단위는 해석 밖 — 계약상 "
                          f"목차 급수는 pt/px/mm 리터럴 또는 :root 1단 var로 선언할 것)"))
        for kind, decl in inline_notes:
            if kind != "size":
                continue
            out.append(_f("SYNC", "FAIL",
                          f"theme.html 인라인 style에 font-size: `{decl}` — 축 ⑤의 급수 잠금은 "
                          f"CSS 규칙 스캔으로 성립하므로 인라인 급수는 값과 무관하게 잠금 밖 "
                          f"선언이다(종전엔 theme.html 자체를 읽지 않았다). "
                          f"theme.css `.toc*` 규칙으로 옮길 것"))
    return out


def overlay_findings(style, tokens, sd):
    """대안 목차 레이아웃 오버레이(`toc-<layout>.css`)와 그 용량 계약의 정합 (W6 S6).

    오버레이 = 팩 **기본이 아닌** 레이아웃의 실물 CSS. build_html은 book.json이
    `toc_layout`으로 그 이름을 선언한 빌드에서만 theme.css 뒤에 이어붙인다 — theme.css에
    섞으면 기본 레이아웃의 급수 잠금(축 ⑤)이 오버레이 리터럴에 오염돼 상한을 올리거나
    (잠금 해체) 상시 FAIL(오탐)이 되므로 파일을 물리로 가른다. 그 대가로 오버레이
    자신이 여기서 기본과 같은 강도의 검사를 받는다:
      ⑥ 파일명의 레이아웃 이름 ∈ 카탈로그(TOC_LAYOUTS)
      ⑦ 이 스타일 ∈ 그 레이아웃의 styles(구현 보유 팩 선언)
      ⑧ html 엔진 전용 · 팩 기본 toc_layout과 같은 이름 금지(기본 구현은 theme.css가 정본)
      ⑨ 오버레이의 점선 리더 리터럴 유무 ↔ 카탈로그 leader 선언 일치
      ⑩ 오버레이 `.toc*` 급수 리터럴 최대 ≤ toc_size_cap — 상한 미선언(None)이면 그
         자체가 FAIL이다(오버레이는 리터럴 구현이라 "변수 주입이라 상한 없음"이 성립
         하지 않고, 상한 없는 리터럴은 캘리브레이션 잠금이 아예 없다는 뜻이다)
      ⑪ 단면(toc_overflow=single) 스타일이면 tokens `toc_capacity_alt[이름]`이
         TOC_CAPACITY_KEYS 7키 전부로 실재하고 size_pt ≤ 상한. 역방향 —
         toc_capacity_alt에만 있고 오버레이 실물이 없는 이름도 FAIL(선언만 있는
         용량 계약은 실물 없는 레이아웃을 약속한다)
    오버레이가 하나도 없고 toc_capacity_alt도 없으면 산출 0 — 기존 5팩 오탐 0의 근거.
    """
    out = []
    engine = tokens.get("engine", "typst")
    # `_` 접두 키는 메타(_why류)다 — toc_capacity의 _why와 같은 관례.
    alt_caps = {k: v for k, v in (tokens.get("toc_capacity_alt") or {}).items()
                if not k.startswith("_")}
    seen = set()
    for ov in sorted(sd.glob("toc-*.css")):
        oname = ov.stem[len("toc-"):]
        seen.add(oname)
        # ---- ⑧ 엔진 ----
        if engine != "html":
            out.append(_f("SYNC", "FAIL",
                          f"styles/{style}/{ov.name}: engine={engine}인데 목차 오버레이 CSS가 있다 — "
                          f"오버레이는 html 엔진 전용 실물이라 이 팩에서는 소비자가 없다(죽은 "
                          f"구현은 선언과 지면의 괴리 그 자체다)"))
            continue
        # ---- ⑥ 이름 ∈ 카탈로그 ----
        ospec = TOC_LAYOUTS.get(oname)
        if ospec is None:
            out.append(_f("SYNC", "FAIL",
                          f"styles/{style}/{ov.name}: 오버레이 레이아웃 {oname!r}은 카탈로그 밖이다 — "
                          f"허용값 {'|'.join(sorted(TOC_LAYOUTS))} (TOC_LAYOUTS가 단일 진리원). "
                          f"카탈로그가 모르는 오버레이는 어떤 불변식도 못 받는다"))
            continue
        # ---- ⑦ 스타일 ∈ styles ----
        if style not in ospec["styles"]:
            out.append(_f("SYNC", "FAIL",
                          f"styles/{style}/{ov.name}: {oname!r}은 {'/'.join(ospec['styles'])}가 "
                          f"구현 보유를 선언한 레이아웃이다 — 오버레이를 두려면 "
                          f"TOC_LAYOUTS['{oname}']['styles']에 이 팩을 먼저 추가할 것"))
        # ---- ⑧ 기본과 중복 ----
        if oname == tokens.get("toc_layout"):
            out.append(_f("SYNC", "FAIL",
                          f"styles/{style}/{ov.name}: 팩 기본 toc_layout={oname!r}과 같은 이름의 "
                          f"오버레이 — 기본 레이아웃 구현은 theme.css가 정본이라 같은 문법의 "
                          f"실물이 두 곳이 되면 축 ④⑤가 어느 쪽을 보는지 갈라진다"))
        text = ov.read_text(encoding="utf-8")
        # 오버레이는 theme.css 뒤에 이어붙는 캐스케이드다 — :root 커스텀 프로퍼티를
        # theme.css에서 상속받으므로 var() 1단 해석의 정의 소스로 theme.css를 합산한다.
        theme_css_p = sd / "theme.css"
        osize, oleader, ounres = toc_css_facts(
            text, var_src=theme_css_p.read_text(encoding="utf-8")
            if theme_css_p.exists() else None)
        # ---- ⑨ 점선 리더 ----
        if oleader != ospec["leader"]:
            got = "있음" if oleader else "없음"
            decl = "있음" if ospec["leader"] else "없음"
            out.append(_f("SYNC", "FAIL",
                          f"styles/{style}/{ov.name}: 점선 리더 실물 {got} ≠ toc_layout={oname!r} "
                          f"선언 {decl} — 리더는 목차 문법의 식별 자질이다(기본 레이아웃 축 ④와 "
                          f"같은 계약)"))
        # ---- ⑩ 급수 상한 ----
        cap = toc_size_cap(ospec, style)
        if cap is None:
            out.append(_f("SYNC", "FAIL",
                          f"styles/{style}/{ov.name}: toc_layout={oname!r}의 급수 상한이 이 스타일에 "
                          f"미선언(None)이다 — 오버레이는 리터럴 CSS 구현이라 상한 없는 잠금이 "
                          f"성립하지 않는다. TOC_LAYOUTS['{oname}']['size_cap_pt']에 "
                          f"{style} 상한을 실측으로 선언할 것"))
        elif osize is None and not ounres:
            out.append(_f("SYNC", "WARN",
                          f"styles/{style}/{ov.name}: `.toc*` 규칙에 font-size 리터럴 0건 — "
                          f"상한 {cap}pt가 관측 대상을 잃었다(축이 조용히 꺼진 상태)"))
        elif osize is not None and osize > cap + 1e-6:
            out.append(_f("SYNC", "FAIL",
                          f"styles/{style}/{ov.name}: 오버레이 최대 급수 {osize:g}pt > "
                          f"toc_layout={oname!r} 상한 {cap}pt — 목차 급수는 toc_capacity_alt "
                          f"용량 계약의 입력이라 재캘리브레이션 없이 올리면 목차가 넘치고 "
                          f"Chromium 전역 축소로 조용히 출하된다"))
        if cap is not None:
            # 기본 레이아웃 축 ⑤와 같은 계약 — 미해석 급수 선언은 침묵하지 않는다.
            for note in ounres:
                out.append(_f("SYNC", "WARN",
                              f"styles/{style}/{ov.name}: 미해석 급수 선언 — {note}. "
                              f"정적 상한 {cap}pt 판정이 이 선언을 확정하지 못한다"))
        # ---- ⑪ 용량 계약 (단면 스타일만 — 다면은 toc_profile 소관) ----
        if tokens.get("toc_overflow") == "single":
            alt = alt_caps.get(oname)
            if not isinstance(alt, dict):
                out.append(_f("SYNC", "FAIL",
                              f"styles/{style}/tokens.json: 오버레이 {ov.name} 실물이 있는데 "
                              f"`toc_capacity_alt[{oname!r}]` 용량 계약이 없다 — 단면 목차는 "
                              f"용량 선언 없이는 넘침이 검사 없이 전역 축소로 간다"
                              f"(toc_capacity와 같은 7키: {', '.join(TOC_CAPACITY_KEYS)})"))
            else:
                missing = [k for k in TOC_CAPACITY_KEYS if k not in alt]
                if missing:
                    out.append(_f("SYNC", "FAIL",
                                  f"styles/{style}/tokens.json `toc_capacity_alt[{oname!r}]`에 "
                                  f"키 누락: {missing}"))
                sz = alt.get("size_pt")
                if cap is not None and isinstance(sz, (int, float)) \
                        and not isinstance(sz, bool) and sz > cap + 1e-6:
                    out.append(_f("SYNC", "FAIL",
                                  f"styles/{style}/tokens.json `toc_capacity_alt[{oname!r}]` "
                                  f"size_pt {sz:g} > 상한 {cap}pt — 용량 계약이 자기 레이아웃의 "
                                  f"급수 잠금을 넘는 급수로 접힘을 판정하게 된다"))
    # ---- ⑪ 역방향: 실물 없는 용량 선언 ----
    for oname in sorted(set(alt_caps) - seen):
        out.append(_f("SYNC", "FAIL",
                      f"styles/{style}/tokens.json `toc_capacity_alt[{oname!r}]`: 대응하는 "
                      f"오버레이 실물(toc-{oname}.css)이 없다 — 선언만 있는 용량 계약은 "
                      f"구현 없는 레이아웃을 약속한다(빌드는 die하지만 계약은 썩는다)"))
    return out


# ------------------------------------------------------------------- G16-SYNC

def g16_sync(style, tokens, theme_text, brand=None, style_dir=None):
    """색·역할 계약 정합. HARD FAIL은 증명 가능한 것에만."""
    out = []
    ctx = _ctx(tokens, theme_text, brand)
    engine = tokens.get("engine", "typst")
    dg = tokens.get("diagram")
    sd = Path(style_dir) if style_dir else (SKILL / "styles" / style)

    # ---- HARD ⓪ engine ↔ 팩 실물 일치 ----
    # theme.html이 실존하는데 engine이 html이 아니면 렌더 경로 선택이 틀린다. engine 키를
    # 한 줄 지우면 기본값 typst로 떨어져 html 전용 HARD들이 통째로 강등되던 구멍(S4).
    # 파일 실존 대조라 증명 가능하다 — 추정이 아니다.
    if (sd / "theme.html").exists() and engine != "html":
        out.append(_f("SYNC", "FAIL",
                      f"styles/{style}/theme.html이 실존하는데 engine={engine!r} — "
                      f"engine 키 누락/오기(기본값 typst)로 html 전용 검사가 강등된다"))

    # ---- HARD ⓪' typst 팩의 죽은 toc_overflow ----
    # toc_overflow는 html 빌더만 소비한다(build_typst 경로는 이 키를 한 번도 읽지 않는다 —
    # 적대검증 v-s1 ②: essay에 "paginate"를 주입해도 경고 0으로 빌드됐다). 죽은 선언은
    # "이 팩이 다면 목차를 지원한다"는 거짓 계약이 tokens.json에 사는 상태다 — extending.md
    # "typst 4종은 이 키가 없다"를 문서가 아니라 게이트가 강제한다(오버레이 축 ⑧과 같은
    # "소비자 없는 실물/선언 = FAIL" 교리).
    if engine != "html" and "toc_overflow" in tokens:
        out.append(_f("SYNC", "FAIL",
                      f"styles/{style}/tokens.json에 toc_overflow="
                      f"{tokens.get('toc_overflow')!r} — engine={engine!r}는 이 키의 소비자가 "
                      f"없다(html 전용). 죽은 설정은 조용히 무시되는 거짓 계약이다 — 키를 "
                      f"지우거나 engine을 html로 바꿀 것"))

    # ---- HARD ① diagram.palette 존재 + palette_roles 무결성 (필수 계약) ----
    # 옵셔널이면 새 스타일이 빼먹고 G16-BRAND가 조용히 무력화된다.
    # `if dg:`(falsy 우회, S3)를 버리고 palette 부재 자체를 FAIL로 못박는다 —
    # 6스타일 전부 palette를 계약으로 가지며 render_diagrams.mjs:37 `[...dg.palette]`가
    # 이를 그대로 소비한다(부재 시 그쪽에서 터진다).
    if not isinstance(dg, dict):
        out.append(_f("SYNC", "FAIL",
                      f"diagram 블록 부재/비객체({type(dg).__name__}) — "
                      f"palette·palette_roles는 스타일 팩의 필수 계약이다"))
        dg = {}
    pal = dg.get("palette")
    if not isinstance(pal, list) or not pal:
        out.append(_f("SYNC", "FAIL",
                      f"diagram.palette 부재/빈 배열 — render_diagrams.mjs:37이 "
                      f"`[...dg.palette]`로 소비하는 필수 계약이다"))
        pal = pal if isinstance(pal, list) else []
    roles = dg.get("palette_roles")
    if roles is None:
        out.append(_f("SYNC", "FAIL", f"diagram.palette_roles 부재 — palette {len(pal)}슬롯과 "
                                      f"병렬 배열로 필수 선언(허용값 {'|'.join(ROLES)})"))
    elif not isinstance(roles, list) or len(roles) != len(pal):
        out.append(_f("SYNC", "FAIL", f"diagram.palette_roles 길이 {len(roles) if isinstance(roles, list) else '비배열'}"
                                      f" != palette {len(pal)}"))
    else:
        bad = [(i, r) for i, r in enumerate(roles) if r not in ROLES]
        for i, r in bad:
            out.append(_f("SYNC", "FAIL", f"diagram.palette_roles[{i}]={r!r} — 허용값 {'|'.join(ROLES)} 밖"))

    # ---- HARD ①' diagram.labelBand 형식 (승격 스위치) ----
    # contrast_contract.enforce와 **같은 계약**이다: JSON bool만 허용하고 부재도 malformed다.
    # 문자열 "false"는 truthy로 읽혀 승격이 반대로 켜지고(S9 오탐의 재발), 부재를 조용히
    # false로 읽으면 "아직 판단하지 않았다"와 "false로 판단했다"가 구별되지 않는다.
    # maxRatio도 함께 못박는다 — 미선언이면 render_diagrams의 상한 검사가 통째로 꺼진다.
    lb = dg.get("labelBand")
    if lb is None:
        # **부재도 malformed다.** 이 줄이 `if lb is not None:` 가드였던 동안 `labelBand`
        # 키를 통째로 지우면 G16-SYNC가 침묵하고 렌더는 WARN 1행 뒤 통과했다 —
        # 라벨 상한 판정과 6단계 급수 주입이 **함께** 죽는데(labelScalePlan이 null을
        # 돌려 주입 자체가 없다) 키 한 줄 삭제가 W5 5·6·8단계 성과를 조용히 되돌렸다
        # (W5 판정 K2). 주석·문서(extending.md)는 이미 "부재도 malformed"라고 선언하고
        # 있었으므로 이것은 **구현을 문서에 맞추는** 수정이다. palette가 필수인 것과 같은 취급.
        out.append(_f("SYNC", "FAIL",
                      f"diagram.labelBand 부재 — {{maxRatio: 수치, enforce: bool}}는 스타일 팩의 "
                      f"필수 계약이다(palette와 같은 취급). 부재 시 render_diagrams의 라벨 상한 "
                      f"판정과 6단계 급수 주입이 함께 꺼지고, '아직 판단하지 않았다'와 "
                      f"'검사 불필요로 판단했다'가 구별되지 않는다"))
    else:
        if not isinstance(lb, dict):
            out.append(_f("SYNC", "FAIL",
                          f"diagram.labelBand가 객체가 아님({type(lb).__name__}) — "
                          f"{{maxRatio: 수치, enforce: bool}} 형식"))
        else:
            mr = lb.get("maxRatio")
            if not isinstance(mr, (int, float)) or isinstance(mr, bool) or mr <= 0:
                out.append(_f("SYNC", "FAIL",
                              f"diagram.labelBand.maxRatio={mr!r} — 양수 수치여야 한다. "
                              f"부재 시 render_diagrams의 라벨 상한 검사가 통째로 꺼진다"))
            elif not (LABEL_BAND_MIN_RATIO <= mr <= LABEL_BAND_MAX_RATIO):
                out.append(_f("SYNC", "FAIL",
                              f"diagram.labelBand.maxRatio={mr} — 타당성 대역 "
                              f"[{LABEL_BAND_MIN_RATIO}, {LABEL_BAND_MAX_RATIO}] 밖(malformed). "
                              f"{LABEL_BAND_RATIO_RATIONALE}"))
            if not isinstance(lb.get("enforce"), bool):
                out.append(_f("SYNC", "FAIL",
                              f"diagram.labelBand.enforce={lb.get('enforce')!r} — true/false(JSON bool) "
                              f"만 허용(부재·문자열 불가). 문자열은 truthy로 읽혀 승격이 오작동한다 "
                              f"(contrast_contract.enforce와 같은 계약)"))

    # ---- HARD ② brand_default ↔ palette[0] 동기 ----
    # render_diagrams.mjs:38이 book.json brand로 palette[0]을 덮어쓴다 = 0번 슬롯은
    # 브랜드 슬롯이라는 계약. 둘이 어긋나면 브랜드 없는 책의 도해 주색과 지면 키색이
    # 갈라진다. 단 typst 4종은 meta.brand가 theme.typ 계산식 안에서 재바인딩되어
    # (business: accent, brand는 navy-700 별도) 정적으로 증명할 수 없다 —
    # 스캔 범위 밖(플랜 전제교정 ③)이므로 WARN으로만 남긴다.
    bd = norm_hex(tokens.get("brand_default") or "")
    p0 = norm_hex(pal[0] or "") if pal else None
    if bd and p0 and bd != p0:
        lv = "FAIL" if engine == "html" else "WARN"
        note = "" if engine == "html" else " (typst: theme.typ 재바인딩은 정적 해석 범위 밖 — 수동 감사 항목)"
        out.append(_f("SYNC", lv, f"brand_default {bd} != diagram.palette[0] {p0}{note}"))

    # ---- HARD ③ contrast_contract 토큰명 해석 가능성 ----
    cc = tokens.get("contrast_contract")
    if isinstance(cc, dict):
        # enforce는 승격 스위치다. 문자열 "false"/"no"/"off"가 truthy로 읽혀 강제가
        # 켜지던 오탐(S9)을 막으려면 형식 자체를 계약으로 못박아야 한다 — 부재도 malformed다.
        if not isinstance(cc.get("enforce"), bool):
            out.append(_f("SYNC", "FAIL",
                          f"contrast_contract.enforce={cc.get('enforce')!r} — true/false(JSON bool) "
                          f"만 허용(부재·문자열 불가). 문자열은 truthy로 읽혀 강제가 오작동한다"))
        entries = cc.get("entries")
        if not isinstance(entries, list):
            out.append(_f("SYNC", "FAIL", "contrast_contract.entries가 배열이 아님"))
            entries = []
        for i, e in enumerate(entries):
            if not isinstance(e, dict):
                out.append(_f("SYNC", "FAIL", f"contrast_contract.entries[{i}]가 객체가 아님"))
                continue
            for k, ty in (("fg", str), ("bg", str), ("pt", (int, float)), ("bold", bool), ("where", str)):
                if not isinstance(e.get(k), ty) or isinstance(e.get(k), bool) != (ty is bool):
                    out.append(_f("SYNC", "FAIL",
                                  f"contrast_contract.entries[{i}] ({e.get('where', '?')}) 키 {k} 누락/형식 오류"))
            for side in ("fg", "bg"):
                kind, why = _resolve_token(e.get(side), ctx)
                if kind == "unresolved":
                    # 사유는 해석기가 만든다 — 실패 원인이 book.json이면 book.json을 지목한다.
                    out.append(_f("SYNC", "FAIL",
                                  f"contrast_contract.entries[{i}] ({e.get('where', '?')}) "
                                  f"{side}={e.get(side)!r} 해석 불가 — {why}"))

    # ---- HARD ④ front_frame_mm 선언값 타당성 (수치 계약) ----
    # 이 축이 없던 동안 G3-FIT은 선언만 바꿔 5가지 방법으로 무력화할 수 있었다(D3).
    out += front_frame_findings(style, tokens)

    # ---- HARD ⑤ diagram.widths ↔ 실렌더 폭 계약 (폭 3원 동기화) ----
    # html: theme.css $fig_*_mm 치환 배선 / typst: theme.typ bf-fig 배선 + 판면폭 값 대조
    out += widths_findings(style, tokens, theme_text, engine, sd)

    # ---- HARD ⑥ toc_layout ↔ theme 실물 (목차 문법 계약) ----
    # 새 게이트명을 만들지 않는다 — 이것은 "스타일 팩의 색·**수치** 계약 정합"이라는
    # G16-SYNC의 표방 범위 안이고, 축을 이름으로 쪼개면 qc_gate·build 양쪽에 배선이
    # 늘어나 어느 하나가 빠지는 순간 조용히 꺼진다(G16-SYNC는 이미 그 배선을 가진다).
    out += layout_findings(style, tokens, theme_text, engine, sd)

    # ---- WARN: 팔레트↔theme.css 교집합 (부재는 결함, 잉여는 아님) ----
    if pal and engine == "html":
        css_hex = css_literal_hexes(theme_text)
        if ctx["brand"]:
            css_hex.add(ctx["brand"])   # $key_color 치환 결과
        # 양방향 모두 **렌더가 실제로 쓰는 팔레트**로 대조한다 — render_diagrams.mjs:38이
        # `if (bookMeta.brand) palette[0] = bookMeta.brand`로 0번 슬롯을 치환하므로,
        # 브랜드를 준 책에서 tokens의 brand_default는 지면에도 도해에도 나타나지 않는
        # 죽은 값이고 그것을 CSS와 대조하면 양쪽 방향 모두 오탐이 난다.
        # HARD ②가 brand_default == palette[0]을 이미 못박으므로 브랜드 미지정 책에서는 항등.
        pal_res = list(pal)
        if ctx["brand"]:
            pal_res[0] = ctx["brand"]
        for i, c in enumerate(pal_res):
            h = norm_hex(c)
            if h and h not in css_hex:
                role = roles[i] if (isinstance(roles, list) and i < len(roles)) else None
                out.append(_f("SYNC", "WARN",
                              f"palette[{i}] {h} (role={role})이 theme.css 리터럴에 없음 — 도해 전용 슬롯"))
        pal_hex = {norm_hex(c) for c in pal_res if norm_hex(c)}
        for name, raw in ctx["vars"].items():
            kind, v = _resolve_value(raw, ctx)
            if kind != "hex" or v == "#ffffff":   # 백색은 alienColors가 암묵 허용(render_diagrams.mjs:108)
                continue
            if v not in pal_hex:
                out.append(_f("SYNC", "WARN", f"CSS 토큰 {name} {v}이 diagram.palette에 없음 — 도해에서 사용 불가"))
    elif pal and engine != "html":
        out.append(_f("SYNC", "WARN",
                      f"engine={engine} — theme.typ 색은 .darken()/.transparentize() 계산식이라 "
                      f"팔레트↔테마 대조는 스캔 범위 밖(수동 감사 항목)"))
    return out


# --------------------------------------------------------------- G16-CONTRAST

def g16_contrast(style, tokens, theme_text, brand=None):
    """선언 페어의 정적 대비 판정.

    fg·bg가 둘 다 불투명 리터럴 hex로 풀릴 때만 계산한다(그때만 증명이 성립).
    미달 시 contrast_contract.enforce가 true면 FAIL, false면 WARN.
    """
    out = []
    cc = tokens.get("contrast_contract")
    if not isinstance(cc, dict):
        # typst 4종이 이 경로다 — 축 N/A. 절대 FAIL이 아니다(잠김 차단).
        out.append(_f("CONTRAST", "WARN",
                      f"styles/{style}/tokens.json에 contrast_contract 미선언 — 축 N/A"))
        return out
    ctx = _ctx(tokens, theme_text, brand)
    # `is True` 엄격 판정 — "false"/"no"/"off" 같은 문자열이 truthy로 읽혀 강제를 켜던
    # 오탐(S9)을 차단한다. bool이 아닌 값 자체는 SYNC가 malformed FAIL로 이미 잡는다.
    enforce = cc.get("enforce") is True
    for i, e in enumerate(cc.get("entries") or []):
        if not isinstance(e, dict):
            continue
        where = e.get("where", f"entries[{i}]")
        pt, bold = e.get("pt"), bool(e.get("bold"))
        if not isinstance(pt, (int, float)) or isinstance(pt, bool):
            continue   # 형식 오류는 SYNC가 이미 FAIL로 잡았다
        fk, fv = _resolve_token(e.get("fg"), ctx)
        bk, bv = _resolve_token(e.get("bg"), ctx)
        src = f" [{e['source']}]" if e.get("source") else ""
        if fk != "hex" or bk != "hex":
            side, why = ("fg", fv) if fk != "hex" else ("bg", bv)
            out.append(_f("CONTRAST", "WARN",
                          f"{where}{src}: {side}={e.get(side)!r}가 불투명 리터럴이 아님 ({why}) "
                          f"— 정적 판정 불가, G14-C 픽셀 샘플 소관"))
            continue
        ratio = contrast_ratio(parse_hex(fv), parse_hex(bv))
        floor = contrast_floor(pt, bold)
        if ratio < floor:
            out.append(_f("CONTRAST", "FAIL" if enforce else "WARN",
                          f"{where}{src}: {e['fg']} {fv} on {e['bg']} {bv} "
                          f"= {ratio:.2f} < {floor} ({pt}pt{'/bold' if bold else ''})"))
    return out


# ------------------------------------------------------------------ G16-BRAND

# base.typ:17이 `paper: white`를 기본값으로 주고 스타일이 재선언할 때만 바뀐다
# (essay/theme.typ:17 `paper: rgb("#FBFAF7")`). 정적으로 읽히는 건 이 리터럴 형태뿐이다.
_TYP_PAPER_RE = re.compile(r"paper\s*:\s*rgb\(\s*\"(#[0-9a-fA-F]{3,8})\"\s*\)")


def _typst_paper(style_dir):
    """typst 스타일의 지면 바탕색. 선언이 없으면 templates/base.typ:17 기본값 백색."""
    tp = Path(style_dir) / "theme.typ" if style_dir else None
    if tp and tp.exists():
        m = _TYP_PAPER_RE.search(tp.read_text(encoding="utf-8"))
        if m:
            return norm_hex(m.group(1)) or "#ffffff"
    return "#ffffff"


def _brand_sites(style, tokens, ctx, engine, style_dir):
    """브랜드가 **글자로** 치환되는 자리 목록 -> [(where, fg_hex, bg_hex, pt, bold)].

    fg는 브랜드 원값이 아니라 **그 자리에 실제로 꽂히는 해석 결과**다 —
    $key_label처럼 파생을 거치는 자리는 파생 후 값으로 판정해야 파생과 검사가
    다른 수를 내지 않는다.

    자리를 상상하지 않고 치환 코드에서 역산한다.
      (a) build_html.py의 `$key_color`/`$key_label` 치환 -> contrast_contract 중
          fg 해석 경로가 brand을 지나간 엔트리. 배경도 그 엔트리가 선언한 실제 배경이다.
      (b) render_diagrams.mjs:38 `if (bookMeta.brand) palette[0] = bookMeta.brand`
          -> palette_roles[0]가 "label"일 때만(글자용 슬롯일 때만) 검사한다.
          도해 SVG의 허용 배경은 팔레트 + 백색이고(:108) 실제 지면은 백색이다.
      (c) typst 4종: theme.typ:14류의 `rgb(meta.at("brand", ...))`가 accent로 쓰이지만
          정확한 사용 지점은 `.darken()`/`.transparentize()` 계산식이라 스캔 범위 밖이다.
          그래서 계약이 보장하는 최소치 — 지면 바탕 위 본문급 글자 — 로만 근사한다.
    """
    sites = {}
    brand_hex = ctx["brand_res"][1] if ctx["brand_res"][0] == "hex" else None

    def add(where, fg, bg, pt, bold):
        fg, bg = norm_hex(fg or ""), norm_hex(bg or "")
        if not fg or not bg:
            return
        key = (fg, bg, contrast_floor(pt, bold))
        if key in sites:
            sites[key][0].append(where)
        else:
            sites[key] = ([where], fg, bg, pt, bold)

    cc = tokens.get("contrast_contract")
    if isinstance(cc, dict):
        for i, e in enumerate(cc.get("entries") or []):
            if not isinstance(e, dict):
                continue
            pt, bold = e.get("pt"), bool(e.get("bold"))
            if not isinstance(pt, (int, float)) or isinstance(pt, bool):
                continue
            trace = set()
            fk, fv = _resolve_token(e.get("fg"), ctx, trace=trace)
            if "brand" not in trace or fk != "hex":
                continue   # 브랜드 무관이거나 알파 전경 — 후자는 G14-C 소관
            bk, bv = _resolve_token(e.get("bg"), ctx)
            if bk != "hex":
                continue   # 알파·그라데이션 배경은 정적 증명 불가(G14-C 소관)
            add(e.get("where", f"entries[{i}]"), fv, bv, pt, bold)

    dg = tokens.get("diagram") or {}
    roles = dg.get("palette_roles")
    if ctx["brand_from_book"] and isinstance(roles, list) and roles and roles[0] == "label":
        mf = dg.get("minFontPt")
        if isinstance(mf, (int, float)) and not isinstance(mf, bool):
            add("도해 라벨 palette[0] (render_diagrams.mjs:38 치환)", brand_hex, "#ffffff", mf, False)

    if engine != "html":
        pt = tokens.get("body_pt")
        if isinstance(pt, (int, float)) and not isinstance(pt, bool):
            add("typst accent 근사 — 지면 바탕 위 본문급 글자 (정확한 치환 지점은 스캔 범위 밖)",
                brand_hex, _typst_paper(style_dir), pt, False)

    return [(" / ".join(w), fg, bg, pt, bold) for w, fg, bg, pt, bold in sites.values()]


def _hue_companions(tokens):
    """브랜드와 한 지면에서 공존하는 **고정** 유채색(색상각 목록).

    출처는 diagram.palette의 0번을 뺀 슬롯이다 — 0번만 브랜드로 치환되고(:38)
    나머지는 어떤 책에서도 고정이며, alienColors(:108)가 도해 색을 이 집합으로
    강제하므로 "브랜드와 반드시 함께 놓이는 색"의 정의가 코드로 보장된다.
    insight는 palette[1] #14577d가 곧 목차 1레벨 고정색 `--blue-800`이라
    G14-B가 실제로 비교하는 그 색이 여기 그대로 들어온다.
    무채색 슬롯은 색상각이 의미를 갖지 않으므로 제외한다.
    """
    pal = (tokens.get("diagram") or {}).get("palette") or []
    out = []
    for c in pal[1:]:
        rgb = parse_hex(c or "")
        if rgb and is_chromatic(rgb):
            out.append((norm_hex(c), hue_deg(rgb)))
    return out


def g16_brand(style, tokens, theme_text, brand=None, style_dir=None):
    """브랜드 입력 사전 검증 3종 — 형식 · 치환 지점 대비 · 고정 동반색과의 hue 정합.

    강도는 값 출처가 정한다: book.json.brand 위반은 FAIL(무검증 치환 구멍 봉쇄),
    brand_default 위반은 WARN(출하 부채 — 어떤 책도 잠그지 않는다).
    """
    out = []
    ctx = _ctx(tokens, theme_text, brand)
    src, raw = ctx["brand_src"], ctx["brand_raw"]
    sev = "FAIL" if ctx["brand_from_book"] else "WARN"
    engine = tokens.get("engine", "typst")
    sd = Path(style_dir) if style_dir else (SKILL / "styles" / style)

    # ---- ① 형식 ----
    kind, val = ctx["brand_res"]
    if kind == "unresolved":
        # 색이 아닌 값(`navy` 같은 CSS 색이름 포함)은 $key_color 치환 결과가 CSS에서
        # 조용히 무효가 되거나 build_html의 hex 산술을 터뜨린다.
        # 사유 문자열은 해석기가 출처를 지목해 이미 만들어 둔다 — 여기서 다시 붙이면 중복된다.
        out.append(_f("BRAND", sev if raw.strip() else "WARN",
                      f"{val}. 허용 형식은 #hex 3/4/6/8자리 또는 rgb()/rgba()"))
        return out
    if kind != "hex":
        # 반투명 브랜드는 렌더는 되지만 배경 합성 없이는 대비·hue가 성립하지 않는다.
        out.append(_f("BRAND", "WARN",
                      f"{val}. 대비·hue 축은 배경 합성이 필요해 N/A(G14-C 소관)"))
        return out
    rgb = parse_hex(val)

    # ---- ② 치환 지점 대비 ----
    for where, fg, bg, pt, bold in _brand_sites(style, tokens, ctx, engine, sd):
        ratio = contrast_ratio(parse_hex(fg), parse_hex(bg))
        floor = contrast_floor(pt, bold)
        derived = "" if fg == val else f"→{fg}"   # $key_label 파생을 거친 자리
        tag = f"{src}={val}{derived} on {bg} = {ratio:.2f}"
        note = f"({pt}pt{'/bold' if bold else ''}) @ {where}"
        if ratio < floor:
            out.append(_f("BRAND", sev, f"{tag} < {floor} {note}"))
        elif ratio < floor * THIN_BAND:
            # 렌더 샘플값은 토큰값과 최대 0.63% 어긋난다 — 하한을 갓 넘긴 값은
            # 렌더 후 G14-C에서 뒤집힐 수 있으므로 통과시키되 표시한다.
            out.append(_f("BRAND", "WARN", f"{tag} 여유 얇음 (하한 {floor} 대비 +{ratio - floor:.2f}) {note}"))

    # ---- ③ 고정 동반색과의 hue 정합 ----
    companions = _hue_companions(tokens)
    if not is_chromatic(rgb):
        # 무채색 근처는 HLS 색상각이 잡음이다(회색의 hue는 채널 반올림이 정한다).
        # 검사를 건너뛰되 침묵하지 않는다 — G14-B도 `_is_colored` 밖 색은 비교하지 않으므로
        # 사전·사후 판정이 같은 이유로 같이 침묵한다는 사실을 기록으로 남긴다.
        out.append(_f("BRAND", "WARN",
                      f"{src}={val} 채도 {max(rgb) - min(rgb)} ≤ {MIN_CHROMA} — 무채색이라 "
                      f"hue 정합 축 N/A (G14-B도 같은 임계로 비교 대상에서 뺀다)"))
    elif companions:
        h = hue_deg(rgb)
        near = min(companions, key=lambda c: hue_dist(h, c[1]))
        d = hue_dist(h, near[1])
        if d > HUE_TOL_DEG:
            out.append(_f("BRAND", sev,
                          f"{src}={val} (hue {h:.0f}°)가 고정 동반색 계열 밖 — 가장 가까운 "
                          f"{near[0]} (hue {near[1]:.0f}°)와 Δ{d:.0f}° > {HUE_TOL_DEG}°. "
                          f"이대로 두면 2-pass 렌더를 다 지불한 뒤 G14-B에서 죽는다"))
    # companions가 비면(무채색 팔레트) 비교 대상이 없다 — 침묵한다. 없는 계약을
    # 매 빌드 WARN으로 알리면 4스타일이 영구 소음이 된다.
    return out


# ------------------------------------------------------------------ 러너/도구

def style_inputs(style, skill=SKILL, style_dir=None):
    """스타일 팩에서 (tokens, theme_text)를 읽는다. theme.css가 없으면 None.

    style_dir가 주어지면 `skill/styles/<style>` 대신 그 경로를 직접 읽는다 —
    뮤테이션 테스트가 저장소 styles/를 변조하지 않고 임시 복사본을 검사하기 위함
    (기본값 None이면 기존 호출 전부와 동일하게 동작한다).
    """
    sd = Path(style_dir) if style_dir else (Path(skill) / "styles" / style)
    tokens = json.loads((sd / "tokens.json").read_text(encoding="utf-8"))
    css = sd / "theme.css"
    return tokens, (css.read_text(encoding="utf-8") if css.exists() else None)


def run(style, tokens, theme_text, brand=None, style_dir=None):
    """세 축을 한 번에. build.py·qc_gate.py가 공유하는 단일 진입점.

    style_dir는 engine↔팩 실물 대조(HARD ⓪)와 typst 지면색 판독에 쓰이며,
    생략하면 SKILL/styles/<style>.
    """
    return {
        "G16-SYNC": g16_sync(style, tokens, theme_text, brand, style_dir),
        "G16-CONTRAST": g16_contrast(style, tokens, theme_text, brand),
        "G16-BRAND": g16_brand(style, tokens, theme_text, brand, style_dir),
    }


def fails_of(findings):
    return [f for f in findings if f["level"] == "FAIL"]


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python3 scripts/g16_tokens.py <style> [brand]")
    style = sys.argv[1]
    # 2번째 인자는 book.json.brand를 흉내 낸다 — 브랜드 입력 검증을 책 하나 짓지 않고
    # 확인할 수 있어야 한다. 생략하면 팩의 brand_default(=출하 기본)를 본다.
    brand = sys.argv[2] if len(sys.argv) > 2 else None
    if not (SKILL / "styles" / style).exists():
        sys.exit(f"unknown style: {style}")
    tokens, css = style_inputs(style)
    res = run(style, tokens, css, brand)
    nf = nw = 0
    print(f"G16-TOKENS  style={style}  engine={tokens.get('engine', 'typst')}  "
          f"theme.css={'있음' if css else '없음'}  "
          f"brand={brand or tokens.get('brand_default')}"
          f"{'' if brand else ' (brand_default)'}")
    for axis in ("G16-SYNC", "G16-CONTRAST", "G16-BRAND"):
        fs = res[axis]
        f_n = len([x for x in fs if x["level"] == "FAIL"])
        w_n = len(fs) - f_n
        nf, nw = nf + f_n, nw + w_n
        print(f"\n  [{axis}] FAIL {f_n} · WARN {w_n}")
        for x in fs:
            print(f"    {x['level']:4} {x['msg']}")
        if not fs:
            print("    (없음)")
    print(f"\n  합계: FAIL {nf} · WARN {nw}")
    return 1 if nf else 0


if __name__ == "__main__":
    sys.exit(main())
