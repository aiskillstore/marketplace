// bookforge WCAG 산술 — **scripts/g16_tokens.py의 이식본이다(값 복제)**.
//
// 왜 복제가 존재하는가: 도해 렌더는 node(render_diagrams.mjs)에서 돌고 게이트는
// python(g16_tokens.py·tocgate.py)에서 돈다. mjs는 python을 import할 수 없다.
// 그래서 이 파일의 수(數)는 **파생값이 아니라 복제값**이고, 두 벌이 갈리면
// 같은 도해를 두 게이트가 다르게 판정한다 — G16-SYNC는 스타일 토큰 ↔ CSS만 보므로
// 이 어긋남을 볼 수단이 없다(SYNC가 잡을 방법이 없는 결함이다).
//
// 그래서 **tests/test_wcag_parity.py가 두 구현의 동치를 어서션한다.** 이 파일의 값을
// 바꾸면 그 테스트가 먼저 깨져야 한다. python 쪽을 바꿀 때도 마찬가지다.
//
// 출처(값 복제 원본):
//   contrast_floor  ← scripts/g16_tokens.py:59  `def contrast_floor(pt, bold)`
//   BOLD_MIN_WEIGHT ← scripts/g16_tokens.py:79  `BOLD_MIN_WEIGHT = 700`
//   is_bold_font    ← scripts/g16_tokens.py:93  `def is_bold_font(font_name)`
//   _lin/rel_luminance/contrast_ratio ← scripts/g16_tokens.py:137-152

/** sRGB 성분 선형화. 출처: g16_tokens.py:137 `_lin`. */
function lin(c) {
  const v = c / 255;
  return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
}

/** WCAG 2.x 상대휘도. 출처: g16_tokens.py:142 `rel_luminance`. */
export function relLuminance([r, g, b]) {
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
}

/** 대비비. 출처: g16_tokens.py:148 `contrast_ratio`. */
export function contrastRatio(fg, bg) {
  let a = relLuminance(fg), b = relLuminance(bg);
  if (a < b) { const t = a; a = b; b = t; }
  return (a + 0.05) / (b + 0.05);
}

/**
 * 대비 하한. 출처: g16_tokens.py:59 `contrast_floor(pt, bold)` — 그 docstring이 정본이다.
 * WCAG 2.x 1.4.3 large-text 정의: 18pt 이상, 또는 14pt 이상이면서 볼드일 때만 3:1.
 */
export function contrastFloor(pt, bold) {
  return (pt >= 18 || (pt >= 14 && bold)) ? 3.0 : 4.5;
}

/** WCAG 대형 텍스트 예외의 굵기 임계. 출처: g16_tokens.py:79 `BOLD_MIN_WEIGHT`. */
export const BOLD_MIN_WEIGHT = 700;

// 출처: g16_tokens.py:83 `_WORD_TOKEN_RE`. 카멜케이스·구분자·숫자 토큰을 뽑는다.
const WORD_TOKEN_RE = /[A-Z][a-z]+|[A-Z]+(?![a-z])|[a-z]+|\d+/g;
// 출처: g16_tokens.py:88 `_HEAVY_WORD_TOKENS` / :90 `_LIGHTEN_BOLD_PREFIX`.
const HEAVY_WORD_TOKENS = new Set(["black", "heavy"]);
const LIGHTEN_BOLD_PREFIX = new Set(["semi", "demi"]);

/**
 * 폰트명이 WCAG 기준 bold(700+)인가. 출처: g16_tokens.py:93 `is_bold_font` — 규칙 정본은
 * 그 docstring이다(부분문자열 금지·토큰 단위 판정: "Blackriver"≠black, "Boldoni"≠bold).
 */
export function isBoldFont(fontName) {
  if (!fontName) return false;
  const tokens = (String(fontName).match(WORD_TOKEN_RE) || []).map((t) => t.toLowerCase());
  for (let i = 0; i < tokens.length; i++) {
    const tok = tokens[i];
    if (/^\d+$/.test(tok)) {
      const w = parseInt(tok, 10);
      if (w >= 100 && w <= 950) return w >= BOLD_MIN_WEIGHT;
      continue;
    }
    if (HEAVY_WORD_TOKENS.has(tok)) return true;
    if (tok === "bold") {
      const prev = i > 0 ? tokens[i - 1] : "";
      if (LIGHTEN_BOLD_PREFIX.has(prev)) continue;
      return true;
    }
  }
  return false;
}

/**
 * SVG 텍스트의 굵기 판정 — **mjs 전용**(python에 대응물이 없다).
 *
 * PDF 스팬은 폰트명만 남지만(그래서 게이트는 `is_bold_font`를 쓴다) SVG에는 CSS
 * `font-weight`가 수치로 살아 있다. 같은 임계(`BOLD_MIN_WEIGHT`)를 쓰되 수치를 우선
 * 해석하고, 수치가 없을 때만 가문명 토큰 판정으로 내려간다.
 */
export function isBoldSvgText(fontWeight, fontFamily) {
  const w = String(fontWeight || "").trim().toLowerCase();
  if (/^\d+$/.test(w)) return parseInt(w, 10) >= BOLD_MIN_WEIGHT;
  if (w === "bold" || w === "bolder") return true;
  if (w === "normal" || w === "lighter") return false;
  return isBoldFont(fontFamily);
}
