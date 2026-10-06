// bookforge P1.5 도해 프리렌더 — diagrams/fig-NN.json (AntV Infographic DSL 사이드카)
// → assets/fig-NN.svg (+ fig-NN.labels.json, G13 대조 정본).
//
// Usage: node render_diagrams.mjs <book_dir> --style <style> [--style-dir <dir>]
//   --style-dir : 스타일 팩 디렉토리 override(**테스트 전용**). 출하 경로(build.py)는 절대
//                 넘기지 않으며, 넘겨도 `--style` 이름은 로그·metrics에 그대로 남는다.
//                 뮤테이션이 저장소 styles/를 변조하지 않고 승격 스위치(labelBand.enforce)의
//                 양쪽 분기를 실물로 밟기 위한 통로다(g16_tokens.style_inputs(style_dir=)와 같은 선례).
// 계약(references/diagrams.md):
//   사이드카 {bf:{width:"full"|"twothirds", icons:false}, dsl:"..."|[줄배열]}
//   테마는 스타일 토큰(diagram 블록)이 강제 — 콘텐츠 theme 블록은 덮어쓴다.
//   렌더는 오프라인 재현 가능해야 한다: 산출 SVG 첫 줄의 dsl 해시가 일치하면 skip.
import { createRequire } from "node:module";
import { execSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { convertForeignObjectText, fontFaceCss, normalizeAuthoredSvg, pixelSelfCheck } from "./fo2text.mjs";
import { contrastFloor, contrastRatio, isBoldSvgText } from "./wcag.mjs";

const SKILL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const FONT_DIR = path.join(SKILL, "assets", "fonts");
const CONVERTER_VERSION = 6; // fo2text/트림 알고리즘 변경 시 올려서 캐시 전체 무효화
// 대비 판정 **산술 자체**의 지문 (W5 판정 K10 봉합). `paintPolicy`는 손으로 올리는
// 상수라 `wcag.mjs`의 `contrastFloor`를 4.5 → 7.0으로 강화해도 캐시가 히트해 **강화된
// 규칙이 돌지 않았다**(실측: `0 rendered, 2 cached` rc 0 / 캐시 없는 책은 6건 반려).
// 파일 내용을 해시에 넣으면 사람 개입 없이 닫힌다 — 대비 하한을 건드리는 순간 그
// 하한으로 판정된 적 없는 도해가 전건 재렌더된다. fo2text.mjs도 같은 계열의 부채라
// (CONVERTER_VERSION ↔ 변환기) 함께 싣는다.
// W5 재판정 N5: 해시 전 주석 정규화. 저장소 선례(`g16_tokens._strip_comments`, CSS `/* */`
// 제거)를 JS로 재사용한다 — 문자열·템플릿 리터럴 내용은 그대로 두고(경로·URL의 `//`가
// 줄주석으로 오인되면 안 된다: fo2text.mjs의 `file://`·`http://` 리터럴이 실례다) 그 밖의
// `//`·`/* */`만 걷어낸다. 정규식 리터럴 내부의 `//`(예: `/a\/\/b/`)는 이 근사가 못 잡는
// 알려진 한계다 — 세 파일 모두 그런 리터럴이 없음을 확인했다(_strip_comments도 CSS의
// 같은 계열 근사를 이미 감수한다). 대가: 코드(숫자 상수·로직)는 주석이 아니므로 이 정규화가
// K10(하한 상수 변경 → 재렌더 강제)을 약화시키지 않는다 — 오직 산문 편집(주석·공백)만
// 해시에서 사라진다. 문자열 밖 공백은 단일 스페이스로 접는다 — 주석 한 줄이
// 늘거나 줄면 그 자리의 개행·들여쓰기도 함께 바뀌는데, 접지 않으면 "주석만 지웠는데
// 공백이 달라서" 여전히 재렌더가 뜬다(실측).
function stripJsComments(src) {
  let out = "";
  let i = 0;
  let lastWasSpace = true; // 선두 공백도 접어서 파일 첫 줄 여백 변화를 흡수한다
  let lastSig = ""; // 정규식 리터럴 vs 나눗셈 연산자 판별용 — 직전 유의 문자
  // 이 문자들 뒤에 오는 `/`는 정규식 리터럴 시작이다(연산자·구두점 뒤에 값이 아니라
  // 새 식이 온다). 그 밖(식별자·숫자·`)`·`]`·문자열 뒤)은 나눗셈으로 본다. `return`류
  // 키워드 뒤 정규식(`return /re/`)은 이 근사가 못 잡는 알려진 한계 — 세 파일에 그런
  // 구문이 없음을 확인했다.
  const REGEX_PRECEDERS = new Set("([{,;:=!&|?+-*%^~<>".split(""));
  const n = src.length;
  const pushCode = (ch) => {
    if (/\s/.test(ch)) {
      if (!lastWasSpace) {
        out += " ";
        lastWasSpace = true;
      }
    } else {
      out += ch;
      lastWasSpace = false;
      lastSig = ch;
    }
  };
  const canBeRegexStart = () => lastSig === "" || REGEX_PRECEDERS.has(lastSig);
  while (i < n) {
    const c = src[i];
    const c2 = src[i + 1];
    if (c === "/" && c2 === "/") {
      while (i < n && src[i] !== "\n") i++;
      continue;
    }
    if (c === "/" && c2 === "*") {
      i += 2;
      while (i < n && !(src[i] === "*" && src[i + 1] === "/")) i++;
      i += 2;
      continue;
    }
    // 정규식 리터럴은 통째로 보존한다 — 안 그러면 리터럴 안의 `'`/`"`(예: `["']?`)를
    // 문자열 시작으로 오인해 이후 전체 스캔이 어긋난다(실측: 파일 끝 블록주석이
    // 안 지워지는 형태로 드러났다).
    if (c === "/" && canBeRegexStart()) {
      let j = i + 1;
      let inClass = false;
      let closed = false;
      while (j < n) {
        if (src[j] === "\\") {
          j += 2;
          continue;
        }
        if (src[j] === "[") {
          inClass = true;
          j++;
          continue;
        }
        if (src[j] === "]") {
          inClass = false;
          j++;
          continue;
        }
        if (src[j] === "/" && !inClass) {
          j++;
          closed = true;
          break;
        }
        if (src[j] === "\n") break; // 정규식은 줄을 못 넘는다 — 미종결이면 나눗셈으로 재해석
        j++;
      }
      if (closed) {
        while (j < n && /[a-z]/i.test(src[j])) j++; // 플래그
        out += src.slice(i, j);
        lastWasSpace = false;
        lastSig = ")"; // 값이 생성됐으니 다음 `/`는 나눗셈 문맥
        i = j;
        continue;
      }
      pushCode(c);
      i++;
      continue;
    }
    if (c === "'" || c === '"' || c === "`") {
      const quote = c;
      out += c;
      lastWasSpace = false;
      lastSig = quote;
      i++;
      while (i < n && src[i] !== quote) {
        if (src[i] === "\\") {
          out += src[i];
          i++;
          if (i < n) {
            out += src[i];
            i++;
          }
          continue;
        }
        out += src[i];
        i++;
      }
      if (i < n) {
        out += src[i];
        i++;
      }
      continue;
    }
    pushCode(c);
    i++;
  }
  return out.trim();
}
const codeHash = (p) =>
  createHash("sha256").update(stripJsComments(readFileSync(p, "utf8"))).digest("hex").slice(0, 16);
const HERE = path.dirname(fileURLToPath(import.meta.url));
const WCAG_HASH = codeHash(path.join(HERE, "wcag.mjs"));
const CONVERTER_HASH = codeHash(path.join(HERE, "fo2text.mjs"));
// 이 파일 자신도 싣는다. 배경 산출식(`measureLabelPaint`/`compositeCandidates`)이 여기 있고,
// 그것이 바뀌었는데 `paintPolicy` 상수를 올리는 것을 잊으면 **강화된 판정이 돌지 않는다** —
// K10이 wcag.mjs에서 실증한 것과 **정확히 같은 실패**를 이 파일에서 한 번 더 겪었다
// (pattern·rgba 알파 수리 후 코퍼스가 `0 rendered, 64 cached`로 통과했다).
// 대가는 이 파일을 고칠 때마다 전건 재렌더이고, 그것이 fail-closed 방향이다.
const RENDERER_HASH = codeHash(fileURLToPath(import.meta.url));
const PIXEL_TOLERANCE = 0.02;
const MM2PT = 72 / 25.4;

function fail(msg) { console.error(`DIAGRAM FAIL: ${msg}`); process.exit(1); }

const args = process.argv.slice(2);
const bookDir = args[0] && !args[0].startsWith("--") ? path.resolve(args[0]) : null;
const style = args.includes("--style") ? args[args.indexOf("--style") + 1] : null;
if (!bookDir || !style) fail("usage: node render_diagrams.mjs <book_dir> --style <style>");

const styleDirArg = args.includes("--style-dir") ? args[args.indexOf("--style-dir") + 1] : null;
const styleDir = styleDirArg ? path.resolve(styleDirArg) : path.join(SKILL, "styles", style);
const tokensPath = path.join(styleDir, "tokens.json");
if (!existsSync(tokensPath)) fail(`unknown style: ${style}${styleDirArg ? ` (--style-dir ${styleDir})` : ""}`);
const tokens = JSON.parse(readFileSync(tokensPath, "utf8"));
const dg = tokens.diagram;
if (!dg) fail(`styles/${style}/tokens.json에 diagram 블록 없음 — 이 스타일은 도해 미지원`);

// 라벨 밴드 상한의 **스타일별 승격 스위치**(8단계). 선례는 `contrast_contract.enforce`이고
// 형식 계약도 그대로 가져온다: **JSON bool만 허용, 부재도 malformed**.
//   · 문자열 `"false"`/`"off"`는 truthy로 읽혀 강제가 반대로 켜진다(g16_tokens.py:800 S9 오탐).
//   · 부재를 조용히 false로 읽으면 "이 스타일은 아직 판단하지 않았다"와 "false로 판단했다"가
//     구별되지 않는다 — 미선언이 위반보다 조용해서는 안 된다는 저장소 관례에 어긋난다.
// **정본 게이트는 G16-SYNC**(build.py가 렌더 전에 die)다. 여기 검사는 그 게이트를 거치지 않는
// 직접 호출(뮤테이션·수동 재렌더·--style-dir)에서도 같은 계약이 서게 하는 이중 방어다.
// **부재도 malformed다**(W5 판정 K2 봉합 — 종전 `if (labelBand != null)` 가드는 키 통삭제를
// 면제해, 한 줄 삭제로 상한 판정과 6단계 급수 주입이 **함께** 조용히 꺼졌다).
// maxRatio 타당성 대역은 g16_tokens.LABEL_BAND_{MIN,MAX}_RATIO의 복제값이다(K3) — 그쪽
// 주석이 대역 근거의 정본이고, 여기 검사는 G16-SYNC를 거치지 않는 직접 호출에서도 같은
// 계약이 서게 하는 이중 방어다.
const LABEL_BAND_MIN_RATIO = 0.5;  // 출처: g16_tokens.py LABEL_BAND_MIN_RATIO
const LABEL_BAND_MAX_RATIO = 2.0;  // 출처: g16_tokens.py LABEL_BAND_MAX_RATIO
if (dg.labelBand === undefined || dg.labelBand === null) {
  fail(`styles/${style} tokens.diagram.labelBand 부재 — {maxRatio, enforce}는 필수 계약이다(palette와 같은 취급). `
    + `부재 시 라벨 상한 판정과 6단계 급수 주입이 함께 꺼진다`);
}
if (typeof dg.labelBand !== "object" || Array.isArray(dg.labelBand)) {
  fail(`styles/${style} tokens.diagram.labelBand가 객체가 아님(${Array.isArray(dg.labelBand) ? "배열" : typeof dg.labelBand}) — {maxRatio, enforce} 형식`);
}
{
  const mr = dg.labelBand.maxRatio;
  if (typeof mr !== "number" || !isFinite(mr) || mr <= 0) {
    fail(`styles/${style} tokens.diagram.labelBand.maxRatio=${JSON.stringify(mr)} — 양수 수치여야 한다(부재 시 상한 검사가 통째로 꺼진다)`);
  }
  if (mr < LABEL_BAND_MIN_RATIO || mr > LABEL_BAND_MAX_RATIO) {
    fail(`styles/${style} tokens.diagram.labelBand.maxRatio=${mr} — 타당성 대역 [${LABEL_BAND_MIN_RATIO}, ${LABEL_BAND_MAX_RATIO}] 밖(malformed). `
      + `하한 0.5 = 상한이 minFontPt(8pt) 아래로 내려가 밴드가 공집합이 되는 지점, 상한 2.0 = 본문의 두 배(등재 근거 없음). `
      + `대역 밖 값은 판정을 무력화한다 — 극대값은 상한 검사와 급수 주입을 동시에 끈다`);
  }
}
if (typeof dg.labelBand.enforce !== "boolean") {
  fail(`styles/${style} tokens.diagram.labelBand.enforce=${JSON.stringify(dg.labelBand.enforce)} — true/false(JSON bool)만 허용(부재·문자열 불가). `
    + `문자열은 truthy로 읽혀 승격이 오작동한다(contrast_contract.enforce와 같은 계약)`);
}
// widths 관계 불변식 `0 < twothirds ≤ full ≤ trim_mm[0]` — G16-SYNC widths 값 축(K1·K9)의
// 이중 방어. widths는 pt 환산의 유일 기준이고 밴드·하한·주입이 **전부 이 값을 공유**하므로,
// 값이 틀리면 셋이 같은 거짓 기준으로 자기정합해 전건 통과한다(실측: twothirds 400 →
// 게이트 초록, 산출 실 급수 2.3~2.9pt). 정본 판정은 G16-SYNC(렌더 전 die)이고 여기는
// --style-dir·수동 재렌더처럼 그 게이트를 거치지 않는 호출을 위한 것이다.
{
  const w = dg.widths || {};
  const num = (v) => typeof v === "number" && isFinite(v) && v > 0;
  const trimW = Array.isArray(tokens.trim_mm) && num(tokens.trim_mm[0]) ? tokens.trim_mm[0] : null;
  if (num(w.twothirds) && num(w.full) && w.twothirds > w.full) {
    fail(`styles/${style} tokens.diagram.widths.twothirds ${w.twothirds}mm > full ${w.full}mm — 2/3폭이 전폭보다 넓다(pt 환산 기준 오류)`);
  }
  for (const k of ["full", "twothirds"]) {
    if (trimW && num(w[k]) && w[k] > trimW) {
      fail(`styles/${style} tokens.diagram.widths.${k} ${w[k]}mm > trim_mm[0] ${trimW}mm(재단 폭) — 판면폭이 판형을 넘을 수 없다(pt 환산 기준 오류)`);
    }
  }
}
// 배치 높이 상한 계약(W7 신설) — labelBand와 같은 취급(**부재도 malformed**). 부재 시
// 높이 검사와 축소·반려가 통째로 꺼져, 세로 긴 도해가 면을 넘어 쪼개진 채 출하된다
// (실증: insight b2-20 fig-01 세로 셰브런 130mm 폭 × 종횡비 1.96 = 254.8mm → p5/p6 분단).
{
  const mh = dg.maxHeightMm;
  if (typeof mh !== "number" || !isFinite(mh) || mh <= 0) {
    fail(`styles/${style} tokens.diagram.maxHeightMm=${JSON.stringify(mh)} — 양수 mm 수치 필수(도해 배치 높이 상한, `
      + `스타일별 판면·캡션 실측 파생 — _maxHeightMm_evidence 참조). 부재 시 도해 면 분단 방어가 통째로 꺼진다`);
  }
  const trimH = Array.isArray(tokens.trim_mm) && typeof tokens.trim_mm[1] === "number" && isFinite(tokens.trim_mm[1])
    ? tokens.trim_mm[1] : null;
  if (trimH !== null && mh >= trimH) {
    fail(`styles/${style} tokens.diagram.maxHeightMm ${mh}mm ≥ trim_mm[1] ${trimH}mm(재단 높이) — `
      + `판면을 넘는 상한은 높이 검사를 무력화한다(widths ≤ trim_mm[0] 불변식과 같은 계열)`);
  }
}
// maxRatio가 타당성 대역 안에서 검증됐다는 사실 — 주입 스킵 조건이 이 값에만 기댄다.
const MAXRATIO_VALIDATED = typeof dg.labelBand.maxRatio === "number"
  && dg.labelBand.maxRatio >= LABEL_BAND_MIN_RATIO && dg.labelBand.maxRatio <= LABEL_BAND_MAX_RATIO;
// true면 밴드 상한 위반이 그 도해의 fail()(7단계 역할·대비 HARD와 같은 관례),
// false면 5단계 출생 강도 그대로 WARN. gateParams가 labelBand 객체를 통째로 싣기 때문에
// 이 스위치는 **자동으로 캐시 해시 파라미터**다 — 승격 순간 그 스타일 도해가 전건 재판정된다.
const BAND_ENFORCE = !!(dg.labelBand && dg.labelBand.enforce === true);
// build_html.py와 동일 우선순위: book.json brand가 있으면 강조색(팔레트 1번)만 교체
const bookMeta = JSON.parse(readFileSync(path.join(bookDir, "book.json"), "utf8"));
const palette = [...dg.palette];
if (bookMeta.brand) palette[0] = bookMeta.brand;

// 템플릿 적합성 실측 원장 — blocked 템플릿은 SSR 전에 차단 (minFontPt 사후 검사와 이중 방어)
const ledger = JSON.parse(readFileSync(path.join(SKILL, "references", "diagram-ledger.json"), "utf8"));

// authored SVG 팔레트 강제 — 허용색 = 스타일 팔레트 + 뉴트럴(백·먹·회색 램프)
// CSS Color Level 4 named colors → hex (transparent/currentColor는 alienColors에서 별도 처리)
const CSS_NAMED_COLORS = {
  aliceblue: "#f0f8ff", antiquewhite: "#faebd7", aqua: "#00ffff", aquamarine: "#7fffd4", azure: "#f0ffff",
  beige: "#f5f5dc", bisque: "#ffe4c4", black: "#000000", blanchedalmond: "#ffebcd", blue: "#0000ff",
  blueviolet: "#8a2be2", brown: "#a52a2a", burlywood: "#deb887", cadetblue: "#5f9ea0", chartreuse: "#7fff00",
  chocolate: "#d2691e", coral: "#ff7f50", cornflowerblue: "#6495ed", cornsilk: "#fff8dc", crimson: "#dc143c",
  cyan: "#00ffff", darkblue: "#00008b", darkcyan: "#008b8b", darkgoldenrod: "#b8860b", darkgray: "#a9a9a9",
  darkgreen: "#006400", darkgrey: "#a9a9a9", darkkhaki: "#bdb76b", darkmagenta: "#8b008b", darkolivegreen: "#556b2f",
  darkorange: "#ff8c00", darkorchid: "#9932cc", darkred: "#8b0000", darksalmon: "#e9967a", darkseagreen: "#8fbc8f",
  darkslateblue: "#483d8b", darkslategray: "#2f4f4f", darkslategrey: "#2f4f4f", darkturquoise: "#00ced1",
  darkviolet: "#9400d3", deeppink: "#ff1493", deepskyblue: "#00bfff", dimgray: "#696969", dimgrey: "#696969",
  dodgerblue: "#1e90ff", firebrick: "#b22222", floralwhite: "#fffaf0", forestgreen: "#228b22", fuchsia: "#ff00ff",
  gainsboro: "#dcdcdc", ghostwhite: "#f8f8ff", gold: "#ffd700", goldenrod: "#daa520", gray: "#808080",
  green: "#008000", greenyellow: "#adff2f", grey: "#808080", honeydew: "#f0fff0", hotpink: "#ff69b4",
  indianred: "#cd5c5c", indigo: "#4b0082", ivory: "#fffff0", khaki: "#f0e68c", lavender: "#e6e6fa",
  lavenderblush: "#fff0f5", lawngreen: "#7cfc00", lemonchiffon: "#fffacd", lightblue: "#add8e6",
  lightcoral: "#f08080", lightcyan: "#e0ffff", lightgoldenrodyellow: "#fafad2", lightgray: "#d3d3d3",
  lightgreen: "#90ee90", lightgrey: "#d3d3d3", lightpink: "#ffb6c1", lightsalmon: "#ffa07a",
  lightseagreen: "#20b2aa", lightskyblue: "#87cefa", lightslategray: "#778899", lightslategrey: "#778899",
  lightsteelblue: "#b0c4de", lightyellow: "#ffffe0", lime: "#00ff00", limegreen: "#32cd32", linen: "#faf0e6",
  magenta: "#ff00ff", maroon: "#800000", mediumaquamarine: "#66cdaa", mediumblue: "#0000cd",
  mediumorchid: "#ba55d3", mediumpurple: "#9370db", mediumseagreen: "#3cb371", mediumslateblue: "#7b68ee",
  mediumspringgreen: "#00fa9a", mediumturquoise: "#48d1cc", mediumvioletred: "#c71585", midnightblue: "#191970",
  mintcream: "#f5fffa", mistyrose: "#ffe4e1", moccasin: "#ffe4b5", navajowhite: "#ffdead", navy: "#000080",
  oldlace: "#fdf5e6", olive: "#808000", olivedrab: "#6b8e23", orange: "#ffa500", orangered: "#ff4500",
  orchid: "#da70d6", palegoldenrod: "#eee8aa", palegreen: "#98fb98", paleturquoise: "#afeeee",
  palevioletred: "#db7093", papayawhip: "#ffefd5", peachpuff: "#ffdab9", peru: "#cd853f", pink: "#ffc0cb",
  plum: "#dda0dd", powderblue: "#b0e0e6", purple: "#800080", rebeccapurple: "#663399", red: "#ff0000",
  rosybrown: "#bc8f8f", royalblue: "#4169e1", saddlebrown: "#8b4513", salmon: "#fa8072", sandybrown: "#f4a460",
  seagreen: "#2e8b57", seashell: "#fff5ee", sienna: "#a0522d", silver: "#c0c0c0", skyblue: "#87ceeb",
  slateblue: "#6a5acd", slategray: "#708090", slategrey: "#708090", snow: "#fffafa", springgreen: "#00ff7f",
  steelblue: "#4682b4", tan: "#d2b48c", teal: "#008080", thistle: "#d8bfd8", tomato: "#ff6347",
  turquoise: "#40e0d0", violet: "#ee82ee", wheat: "#f5deb3", white: "#ffffff", whitesmoke: "#f5f5f5",
  yellow: "#ffff00", yellowgreen: "#9acd32",
};
// 색 문자열이 **자체에 싣고 있는 알파**. `normHex`는 색상 성분만 돌려주므로(팔레트 대조는
// 색상만 보면 된다) 합성에는 이 값을 따로 곱해야 한다 — 곱하지 않으면 `rgba(0,0,0,0.03)`
// 같은 3% 해치가 **불투명 먹**으로 합성되어 멀쩡한 라벨을 반려한다(실측: 벤더
// `letter-card-*-pattern`). `getComputedStyle().fill`은 `transparent`도
// `rgba(0, 0, 0, 0)`로 돌려주므로 이 함수가 없으면 투명면이 검은 면이 된다.
function colorAlpha(c) {
  if (!c) return 1;
  const v = String(c).trim().toLowerCase();
  if (v === "transparent") return 0;
  // 4번째 성분이 **명시된** 경우만 알파다(`rgb(30, 122, 173)`의 3번째를 알파로 읽으면 안 된다)
  const m = v.match(/^(?:rgba?|hsla?)\(\s*[-\d.%deg]+\s*[, ]\s*[\d.%]+\s*[, ]\s*[\d.%]+\s*[,/]\s*([\d.]+%?)\s*\)$/);
  if (m) {
    const s = m[1];
    return Math.max(0, Math.min(1, s.endsWith("%") ? parseFloat(s) / 100 : parseFloat(s)));
  }
  if (/^#[0-9a-f]{8}$/.test(v)) return parseInt(v.slice(7, 9), 16) / 255;
  if (/^#[0-9a-f]{4}$/.test(v)) return parseInt(v[4] + v[4], 16) / 255;
  return 1;
}
function hslToHex(h, s, l) {
  s /= 100; l /= 100;
  const k = (n) => (n + h / 30) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = (n) => l - a * Math.max(-1, Math.min(k(n) - 3, 9 - k(n), 1));
  return "#" + [f(0), f(8), f(4)].map((v) => Math.round(v * 255).toString(16).padStart(2, "0")).join("");
}
// 정규화 성공 시 "#rrggbb", 실패 시 null — null은 alienColors에서 위반으로 승격(침묵 통과 금지)
function normHex(c) {
  if (!c) return null;
  c = c.trim().toLowerCase();
  let m = c.match(/^rgba?\(\s*([\d.]+)(%?)\s*[, ]\s*([\d.]+)(%?)\s*[, ]\s*([\d.]+)(%?)/);
  if (m) {
    return "#" + [[m[1], m[2]], [m[3], m[4]], [m[5], m[6]]]
      .map(([v, pct]) => Math.max(0, Math.min(255, Math.round(pct ? (+v * 255) / 100 : +v))))
      .map((v) => v.toString(16).padStart(2, "0")).join("");
  }
  m = c.match(/^hsla?\(\s*(-?[\d.]+)(?:deg)?\s*[, ]\s*([\d.]+)%\s*[, ]\s*([\d.]+)%/);
  if (m) return hslToHex(((+m[1] % 360) + 360) % 360, +m[2], +m[3]);
  if (c in CSS_NAMED_COLORS) return CSS_NAMED_COLORS[c];
  if (/^#[0-9a-f]{3,4}$/.test(c)) c = "#" + [...c.slice(1)].map((ch) => ch + ch).join("");
  if (/^#[0-9a-f]{8}$/.test(c)) c = c.slice(0, 7); // 알파 채널 절단 — 색상 성분만 대조
  if (/^#[0-9a-f]{6}$/.test(c)) return c;
  return null;
}
function alienColors(svg, palette, strict = false) {
  // strict(authored 트랙): 허용색 = 스타일 팔레트 + paper(#ffffff)뿐 — 토큰 밖 색은
  // 무채색이라도 빌드 실패 (STYLE 「금지 사항」 2번, 토큰 밖 색 금지).
  // 비-strict(antv 트랙): 템플릿 산출 무채색 램프는 종전대로 허용.
  const allowed = new Set([...palette.map((c) => normHex(c)), "#ffffff"]);
  const out = new Set();
  const check = (raw) => {
    const v = raw.trim().toLowerCase();
    if (!v || v === "none" || v === "transparent" || v === "currentcolor" || v.startsWith("url(")) return;
    const hex = normHex(v);
    if (!hex) { out.add(`${v}(해석불가)`); return; } // 정규화 불가 색 문자열도 위반 — 무검증 통과 금지
    if (allowed.has(hex)) return;
    // 뉴트럴 허용: 무채색(채도 미미) 램프 — antv 트랙 한정
    const r = parseInt(hex.slice(1, 3), 16), g = parseInt(hex.slice(3, 5), 16), b = parseInt(hex.slice(5, 7), 16);
    if (!strict && Math.max(r, g, b) - Math.min(r, g, b) <= 16) return;
    out.add(hex);
  };
  scanColorLiterals(svg, check);
  return [...out];
}

// SVG에서 잉크가 되는 색 리터럴 전량을 콜백에 넘긴다 — alienColors와 벤더 폴백색 검사가
// **같은 스캔**을 쓰게 한다(두 벌이 갈리면 한쪽이 보는 색을 다른 쪽이 못 본다).
function scanColorLiterals(svg, check) {
  // 색을 지면에 내는 속성 전량. **`stop-color`가 빠져 있던 것이 W5 판정 K5**다 —
  // 그라데이션 스톱은 `fill=`/`stroke=`에 나타나지 않으므로 팔레트 강제를 통째로
  // 우회했다(실측: `stop-color="#ff0000"`·`"#00ff00"`이 산출 SVG에 그대로 남아 통과).
  // `flood-color`(filter)·`lighting-color`도 같은 계열의 잉크다.
  const COLOR_PROPS = "fill|stroke|stop-color|flood-color|lighting-color";
  for (const m of svg.matchAll(new RegExp(`(?:${COLOR_PROPS})="([^"]+)"`, "gi"))) check(m[1]);
  // style="fill:...;stroke:..." 인라인 CSS도 동일 검사 (fill-opacity 등 접미 속성은 비매칭)
  for (const s of svg.matchAll(/style="([^"]*)"/gi)) {
    for (const d of s[1].matchAll(new RegExp(`(?:^|;)\\s*(?:${COLOR_PROPS})\\s*:\\s*([^;]+)`, "gi"))) check(d[1]);
  }
  // <style> 블록 선언도 같은 잉크다 — 속성만 훑으면 CSS 클래스 한 줄로 우회된다
  // (같은 우회로가 급수 축에서 tspan CSS 급수로 실재했다 — K6).
  for (const s of svg.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)) {
    for (const d of s[1].matchAll(new RegExp(`(?:^|[;{])\\s*(?:${COLOR_PROPS})\\s*:\\s*([^;}]+)`, "gi"))) check(d[1]);
  }
}

// ---- AntV 벤더 폴백색 (8단계·W5 재작업) ----
//
// `#FF356A`는 벤더 번들의 **`colorPrimary` 미도달 폴백**이다 — 실측 8지점:
// `createBaseTheme({primaryColor}) → safeFormatHex(primaryColor, "#FF356A")`,
// `DEFAULT_COLOR = "#FF356A"`(getColorPrimary), `HorizontalArrow/VerticalArrow`류
// 컴포넌트의 기본 prop `fill = "#FF356A"`, `parsedThemeConfig.colorPrimary ||= "#FF356A"`.
// 즉 이 색이 산출 SVG에 남았다는 것은 **우리 팔레트가 그 요소에 도달하지 못했다**는
// 증거이고, 팔레트 강제(STYLE 「토큰 밖 색 금지」)가 그 지점에서 뚫렸다는 뜻이다.
//
// 왜 antv 트랙에 alienColors(strict)를 걸지 않고 이것만 잡는가: 템플릿은 팔레트 색에서
// **정당하게 파생한 틴트**를 쓴다(실측 `sequence-circle-arrows-indexed-card`의
// `#78afce`·`#729ab1`은 `#1e7aad`의 틴트다). "팔레트 밖 색 전량"을 반려하면 그 정당한
// 파생까지 죽는다 — 그래서 **팔레트가 닿지 않았음을 스스로 증명하는 색**만 잡는다.
// 이 축이 없던 동안 `compare-binary-horizontal-underline-text-vs`의 'VS'는 대비 축이
// 우연히(백색 글자였으므로) 잡았지만, `list-sector-plain-text`·
// `relation-network-simple-circle-node`의 `#ff356a` 면은 **전 게이트를 통과해 출하됐다**.
// `#1677ff`는 같은 계열의 두 번째 구멍이다 — 번들의 템플릿 정의가 **자기 `themeConfig`에
// 박아 둔** 기본 primary(`"sequence-funnel-simple": {themeConfig:{colorPrimary:"#1677ff"}}`
// 형태)이고, `applyTheme`가 `theme.palette`를 써도 이 값을 쓰는 요소는 팔레트를 안 받는다.
// **팔레트가 그 색을 실제로 선언했으면 면제한다** — 그 경우엔 우연의 일치가 아니라
// 사용자가 고른 색이므로 폴백 증거가 아니다.
const ANTV_FALLBACK_HEXES = new Set(["#ff356a", "#1677ff"]);
function vendorFallbackColors(svg, pal) {
  const declared = new Set(pal.map((c) => normHex(c)).filter(Boolean));
  const out = new Set();
  scanColorLiterals(svg, (raw) => {
    const hex = normHex(raw);
    if (hex && ANTV_FALLBACK_HEXES.has(hex) && !declared.has(hex)) out.add(hex);
  });
  return [...out];
}

// ---- 팔레트 역할(palette_roles) 색인 — 7단계 「역할·대비 HARD」의 기준 ----
//
// 기준 팔레트는 **해석 팔레트(pal_res)**다: book.json.brand가 있으면 0번 슬롯이 치환된
// 뒤의 팔레트(:38). g16_tokens.g16_sync가 팔레트↔CSS를 양방향 모두 pal_res로 대조하는
// 것과 같은 기준이다(W4-A 3단계 §3b — 한쪽만 치환하면 브랜드 지정 책에서 오탐이 난다).
//
// 같은 hex가 여러 슬롯에 있으면(브랜드가 기존 슬롯과 겹치는 경우) **역할의 합집합**을
// 갖는다 — 그 색이 어느 슬롯에서든 label로 선언돼 있으면 라벨로 쓸 수 있다.
const PAPER_HEX = "#ffffff"; // 판면 바탕. alienColors(:108)가 팔레트 밖이어도 허용하는 유일한 색
const paletteRoles = Array.isArray(dg.palette_roles) ? dg.palette_roles : null;
const roleOf = new Map();
if (paletteRoles) {
  palette.forEach((c, i) => {
    const h = normHex(c);
    if (!h) return;
    if (!roleOf.has(h)) roleOf.set(h, new Set());
    roleOf.get(h).add(paletteRoles[i] ?? null);
  });
}
const isNeutral = (hex) => {
  // alienColors 비-strict 분기(:118)와 **같은 임계**. 두 곳이 갈리면 색 게이트가 허용한
  // 색을 역할 게이트가 죽이는(또는 그 반대) 모순이 생긴다.
  const r = parseInt(hex.slice(1, 3), 16), g = parseInt(hex.slice(3, 5), 16), b = parseInt(hex.slice(5, 7), 16);
  return Math.max(r, g, b) - Math.min(r, g, b) <= 16;
};

// ---- AntV 트랙에 넘길 팔레트 채널 (7단계 수리) ----
//
// AntV의 `theme.palette`는 시리즈 색이 아니라 **항목별 강조 채움(colorPrimary)** 채널이다
// (vendor 번들 `getPaletteColors`/`getPaletteColor` — palette[i % len]). 템플릿은 그 채움 위에
// **백색 knockout 라벨**(단계번호 배지 `01/02/03`, `themeColors.colorWhite`)을 얹는다.
// 그래서 백색을 얹을 수 없는 밝은 슬롯(role `fill`의 틴트, `stroke`의 괘선색)을 이 채널에
// 넣으면 **항목이 그 슬롯에 닿는 순간 반드시 대비 미달**이 된다 — 실측: insight
// palette[2] `#5ec6dc` 위 백색 = 1.98(코퍼스 dsl 4건 전건 FAIL, G14-C도 같은 값 1.99를
// PDF에서 독립 실측했다).
//
// 이것은 W4-A 3단계 §5 인계 1 「AntV 트랙은 role을 지키지 않는다」의 본체다. 팔레트 **값**은
// 건드리지 않고(스타일 토큰 불변조), 이 채널에 넣을 **슬롯만** 고른다:
//   · 0번(브랜드·키색)은 정체성이라 **항상 남긴다** — 밝아서 위험하면 조용히 빼는 대신
//     새 대비 HARD가 소리내어 반려하는 쪽이 옳다(미선언이 위반보다 조용해서는 안 된다).
//   · 나머지는 백색 knockout이 가능한 슬롯만. 판정식은 대비의 대칭성 덕에 한 줄이다 —
//     contrast(slot, #ffffff) ≥ 4.5는 "백색 글자를 얹을 수 있다"와 "백색 위 글자로 쓸 수
//     있다"를 동시에 뜻한다. 하한이 4.5 고정인 이유: 도해 라벨은 밴드 상한
//     (body_pt × maxRatio ≈ 11.4pt)이 14pt 미만이라 contrast_floor가 언제나 4.5다.
const KNOCKOUT_SAFE_MIN = 4.5;
function knockoutSafe(hex) {
  const h = normHex(hex);
  if (!h) return false;
  const rgb = [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  return contrastRatio(rgb, [255, 255, 255]) >= KNOCKOUT_SAFE_MIN;
}
function antvPaletteChannel(pal) {
  const out = pal.filter((c, i) => i === 0 || knockoutSafe(c));
  return out.length ? out : pal; // 빈 채널은 AntV가 기본색(#FF356A)으로 폴백한다 — 방지
}

const diagramsDir = path.join(bookDir, "diagrams");
const sidecars = existsSync(diagramsDir)
  ? readdirSync(diagramsDir).filter((f) => /^fig-\d+\.json$/.test(f)).sort()
  : [];
if (!sidecars.length) { console.log("no diagrams — skip"); process.exit(0); }

// SSR 모듈: 1순위 = 커밋된 벤더 번들(vendor/antv-ssr.bundle.mjs — 레지스트리·
// node_modules 불필요, byte-identical 검증 완료). 폴백 = 로컬 node_modules.
const skillRequire = createRequire(path.join(SKILL, "package.json"));
let renderToString, getTemplate;
const bundlePath = path.join(SKILL, "vendor", "antv-ssr.bundle.mjs");
if (existsSync(bundlePath)) {
  ({ renderToString, getTemplate } = await import(bundlePath));
} else {
  try {
    ({ renderToString } = await import(skillRequire.resolve("@antv/infographic/ssr")));
    ({ getTemplate } = await import(skillRequire.resolve("@antv/infographic")));
  } catch {
    fail("도해 렌더러 부재 — vendor/antv-ssr.bundle.mjs 유실 시 스킬 루트에서 `npm ci` 후 `node vendor/build-bundle.mjs`");
  }
}

// Playwright: print_pdf.mjs와 동일하게 NODE_PATH(글로벌 npm root) 우선, 폴백으로 직접 해석
let chromium;
try {
  ({ chromium } = createRequire(import.meta.url)("playwright"));
} catch {
  try {
    const g = execSync("npm root -g", { encoding: "utf8" }).trim();
    ({ chromium } = createRequire(path.join(g, "noop.js"))("playwright"));
  } catch {
    fail("playwright 미가용 — `npm i -g playwright && npx playwright install chromium`");
  }
}

// AntV DSL 트랙 라벨 급수 강제 (6단계) — 역할별 목표 pt를 body_pt 배수로 선언한다.
//
// 왜 역할별인가: 5단계 실측에서 dsl 6건 전건이 **내부비(최대/최소) 1.714×**로
// 밴드 허용 내부비 1.425×(= 상한 11.4pt ÷ 하한 8pt)를 넘었다. 균일 축척은 상·하한을
// 함께 옮기므로 상한을 맞추면 하한이 깨진다(×0.478 축소 시 최소 6.65pt < 8pt).
// 따라서 title(대)·text(중)·desc(소)의 **격차 자체를 좁혀** 넣어야 한다.
//
// 키 표기는 반드시 케밥 `font-size`다 — 소비 지점이 SVG 속성명을 그대로 쓰므로
// `fontSize`는 조용히 무시된다(1단계 S0-2 실측).
//
// 이 상수가 바뀌면 산출 SVG가 바뀐다 → dsl 캐시 해시에 통째로 싣는다(labelScaleHash).
// authored 트랙 해시에는 넣지 않는다(주입은 dsl 전용 — authored는 캐시 히트 유지).
const LABEL_SCALE = {
  version: 1,
  title: 1.15,       // body_pt 배수. 밴드 상한 1.20의 96% — 반복 수렴 오차 여유
  text: 1.0,         // base.text / item.label / item.value = 본문과 같은 급수
  desc: 0.9,         // 보조 설명. 하한 대비 여유는 floorMargin이 별도로 보장
  capMargin: 0.96,   // title은 capPt×0.96을 넘지 않는다(밴드 상한 직격 방지)
  floorMargin: 1.07, // desc는 minFontPt×1.07 아래로 내려가지 않는다(하한 HARD 방지)
};
const LABEL_SCALE_MAX_ITER = 2; // 보정 반복 상한(= 최대 3회 렌더). 프레임 고정이라 실측은 2회에 끝난다.

// 목표 pt 산출. 반환 null이면 주입하지 않는다(판정 기준이 없으면 강제도 없다 — 5단계
// 「검사가 꺼지는 경우」와 같은 원칙으로, 꺼짐은 labelBandReport가 WARN으로 드러낸다).
function labelScalePlan() {
  const band = dg.labelBand && typeof dg.labelBand === "object" ? dg.labelBand : null;
  const maxRatio = band && typeof band.maxRatio === "number" ? band.maxRatio : null;
  const bodyPt = typeof tokens.body_pt === "number" ? tokens.body_pt : null;
  if (maxRatio === null || bodyPt === null) return null;
  const floorPt = typeof dg.minFontPt === "number" ? dg.minFontPt : 0;
  const capPt = bodyPt * maxRatio;
  const titlePt = Math.min(bodyPt * LABEL_SCALE.title, capPt * LABEL_SCALE.capMargin);
  const descPt = Math.max(bodyPt * LABEL_SCALE.desc, floorPt * LABEL_SCALE.floorMargin);
  if (descPt > titlePt) return null; // 밴드 상한과 글자 하한이 모순 — 주입으로 풀 수 없다
  const textPt = Math.min(Math.max(bodyPt * LABEL_SCALE.text, descPt), titlePt);
  return { bodyPt, floorPt, capPt, titlePt, textPt, descPt };
}
// dsl 해시에 실리는 주입 정책 지문 — 정책이 바뀌면 dsl 도해만 정확히 재렌더된다.
function labelScaleHash() {
  const plan = labelScalePlan();
  if (!plan) return null;
  return stableSort({
    ...LABEL_SCALE, maxIter: LABEL_SCALE_MAX_ITER,
    targetPt: { title: r3(plan.titlePt), text: r3(plan.textPt), desc: r3(plan.descPt) },
  });
}
// 주입은 스칼라 t(= title의 user unit) 하나로 매개한다 — 세 역할이 고정 비율로 함께 움직인다.
function injectFromT(plan, t) {
  const u = (pt) => Math.round((t * (pt / plan.titlePt)) * 1000) / 1000;
  return { title: Math.round(t * 1000) / 1000, text: u(plan.textPt), desc: u(plan.descPt) };
}
const injectEq = (a, b) => !!a && !!b && a.title === b.title && a.text === b.text && a.desc === b.desc;

// 왜 "밀착 트림 + 급수 주입"만으로는 안 되는가 (실측으로 뒤집힌 전제):
//   도해는 지면에서 **고정 물리 폭**(bf.width = 130/106/164mm)으로 발행된다. 세로 리스트
//   템플릿은 트림 폭의 대부분이 글자 폭이라, 급수를 줄이면 트림 폭이 같이 줄고 pt/u가 커진다
//   — 즉 **글자는 안 줄고 도형만 커진다**. iso-base-dsl/fig-02 실측: 밀착 트림으로 목표
//   10.925pt를 맞추면 viewBox 302.63u → 150.39u가 되어 원 지름이 10.5mm → 21.2mm로 배가되고
//   종횡비가 0.66 → 0.32로 무너져 발행 높이가 161mm → 326mm(판면 초과)가 된다.
// 해법: **폭 프레임 고정**. 무주입 0회차의 트림 폭 vbW0을 그대로 프레임으로 쓰면 pt/u가
//   scalePt0으로 보존되므로 주입 user unit = 목표pt / scalePt0 **한 방에 정확히 맞는다**
//   (반복 수렴 불필요). 도형은 지면에서 원래 크기 그대로이고 글자만 줄어든다. 남는 폭은
//   오른쪽 여백이 되며, 좌측 정렬축(판면 27mm 라인)은 트림이 지키던 대로 유지된다.
//   세로는 밀착 트림하므로(pt/u는 폭만의 함수) 타이틀이 줄며 생긴 윗여백은 회수된다.

function applyTheme(dsl, palette, inject) {
  // 콘텐츠의 theme 블록(들여쓰기 연속 줄 포함)을 제거하고 스타일 팔레트를 강제한다.
  const stripped = dsl.replace(/^theme\r?\n(?:[ \t]+.*\r?\n?)*/gm, "").replace(/\s+$/, "");
  let block = `theme\n  palette ${palette.join(" ")}\n`;
  if (inject) {
    // 도달 확인된 5개 역할 전부에 명시 주입한다. base.text는 미지 역할의 폴백이므로
    // 빠뜨리면 템플릿에 따라 강제 밖 라벨이 남는다(실측: base.text만 주면 title·desc까지 함께 먹는다).
    block += `  title\n    font-size ${inject.title}\n`
      + `  desc\n    font-size ${inject.desc}\n`
      + `  base\n    text\n      font-size ${inject.text}\n`
      + `  item\n    label\n      font-size ${inject.text}\n`
      + `    desc\n      font-size ${inject.desc}\n`
      + `    value\n      font-size ${inject.text}\n`;
  }
  return `${stripped}\n${block}`;
}

// 템플릿 하드코딩 급수(단계번호 배지 `01/02/03` = fontSize:16, ItemLabel 미경유)는 테마로
// 도달하지 않는다(1단계 S0-2 실증). 이들은 **SSR 원본에서 native `<text>`로만** 나타난다 —
// 테마 경유 라벨은 전부 foreignObject라 fo2text 변환 후에야 `<text>`가 된다(실측: fig-02
// 원본 native text 3 = 배지 3, foreignObject 7 = 타이틀 1 + label 3 + desc 3).
// 그래서 **변환 전 raw**에 클램프를 걸면 배지만 정확히 잡히고, pixelSelfCheck는 클램프된
// raw와 변환본을 비교하므로 "변환이 외형을 보존했는가"라는 자기검증의 의미도 그대로 남는다.
// (이는 생성 이미지 위 글자 합성이 아니라 렌더 파이프라인 내부의 결정론적 SVG 변환이다.)
// 배지는 text-anchor="middle" + dominant-baseline="central"이라 급수만 줄여도 중심이 유지된다.
function clampNativeText(svg, plan, scalePt) {
  let count = 0;
  const rewrite = (whole, num, unit) => {
    let user = parseFloat(num);
    if (unit === "pt") user *= 96 / 72;
    else if (unit && unit !== "px") return whole; // 미지 단위는 건드리지 않는다(하한 검사가 HARD로 잡는다)
    const pt = user * scalePt;
    const target = Math.min(Math.max(pt, plan.descPt), plan.titlePt);
    if (Math.abs(target - pt) < 1e-6) return whole;
    let nu = target / scalePt;
    if (unit === "pt") nu *= 72 / 96;
    count++;
    return whole.replace(/font-size="[\d.]+[a-z%]*"/i, `font-size="${Math.round(nu * 1000) / 1000}"`);
  };
  const out = svg.replace(/<(?:text|tspan)\b[^>]*?font-size="([\d.]+)([a-z%]*)"[^>]*>/gi,
    (whole, num, unit) => rewrite(whole, num, unit));
  return { svg: out, count };
}

function stripIconLines(dsl) {
  return dsl.split("\n").filter((l) => !/^\s+icon\s+\S/.test(l)).join("\n");
}

function sortDefsSymbols(svg) {
  // <symbol> id가 콘텐츠 해시라 정렬 = 결정론화 (네트워크 완료 순서 비결정 흡수)
  return svg.replace(/<defs\b[^>]*>([\s\S]*?)<\/defs>/, (whole, inner) => {
    const symbols = inner.match(/<symbol\b[\s\S]*?<\/symbol>/g);
    if (!symbols || symbols.length < 2) return whole;
    const rest = symbols.reduce((acc, s) => acc.replace(s, ""), inner);
    const sorted = [...symbols].sort((a, b) => {
      const ida = (a.match(/id="([^"]*)"/) || [])[1] || "";
      const idb = (b.match(/id="([^"]*)"/) || [])[1] || "";
      return ida < idb ? -1 : ida > idb ? 1 : 0;
    });
    return whole.replace(inner, rest.trim() ? rest + sorted.join("") : sorted.join(""));
  });
}

// viewBox 트림 — SVG 내부의 빈 좌우/상하 패딩을 제거해, 지면에서 도해가 판면
// 좌측 라인(27mm)에 정확히 물리고 폭이 명목 폭(130/86mm)과 일치하게 한다.
// (내부 여백이 있으면 콘텐츠가 8~36mm 안쪽에서 시작해 본문 정렬축이 어긋난다.)
// 반드시 pixelSelfCheck 이후에 적용할 것 — 트림은 원본과 프레이밍이 달라진다.
// frameW: 트림 폭의 **하한**(user unit). 6단계 라벨 급수 강제가 쓴다 — 글자만 줄이면
// 트림이 같이 좁아져 pt/u가 커지므로(= 도형이 지면에서 커지고 종횡비가 무너진다),
// 폭 프레임을 무주입 회차 값으로 고정해 pt/u를 보존한다. 세로는 그대로 밀착 트림한다.
// 트림·대비 실측이 **같은 하네스**를 보게 한다(배경 #fff·Pretendard 강제). 두 벌이 갈리면
// 측정한 지면과 판정한 지면이 달라진다.
function stageHtml(svg) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>
${fontFaceCss(FONT_DIR)}
html,body{margin:0;padding:0;background:#fff;}
#stage svg text, #stage svg tspan { font-family:'Pretendard' !important; }
</style></head><body><div id="stage">${svg}</div></body></html>`;
}

async function trimViewBox(page, svg, frameW = null) {
  const harness = stageHtml(svg);
  await page.setContent(harness, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  return page.evaluate((fw) => {
    const el = document.querySelector("#stage svg");
    if (!el) return null;
    const bb = el.getBBox();
    if (!bb || bb.width < 1 || bb.height < 1) return null;
    // 패딩: 스트로크 폭·마커(getBBox 비포함)를 덮는 소여백
    const pad = Math.max(2, 0.008 * Math.max(bb.width, bb.height));
    const tight = bb.width + 2 * pad;
    const w = Math.max(tight, fw || 0); // 프레임 고정 시 남는 폭은 오른쪽 여백(좌측 정렬축 유지)
    el.setAttribute("viewBox",
      `${(bb.x - pad).toFixed(2)} ${(bb.y - pad).toFixed(2)} ` +
      `${w.toFixed(2)} ${(bb.height + 2 * pad).toFixed(2)}`);
    el.removeAttribute("width");
    el.removeAttribute("height");
    return { svg: new XMLSerializer().serializeToString(el), tightW: tight };
  }, frameW);
}

// ---- 라벨 도장(塗裝) 실측 — 글자색과 **그 글자 밑에 실제로 깔린 색** ----
//
// 왜 SVG 문자열 파싱이 아니라 렌더 DOM인가: 배경은 마크업이 아니라 **겹침 순서**가 정한다
// (SVG는 z-index가 없고 문서 순서가 곧 도장 순서). 색만 긁으면 "어느 면 위의 글자인지"를
// 영영 알 수 없다. 그래서 S0에서 쓴 SSR 하네스를 그대로 재사용해 실좌표에서 찍는다.
//
// 배경 결정 규칙(결정론) — **W5 재작업에서 세 곳을 고쳤다(판정 K4)**:
//   1. 대상 = 그 요소가 **직접 품은** 텍스트 노드들의 합집합 bbox에서 뽑은 **다점 표본**
//      (가로 5점: 폭의 10/30/50/70/90%, 세로 중앙). 종전 중심점 1표본은 **경계에 걸친
//      라벨**을 놓쳤다 — 실측 fig-04: 오른쪽 절반이 어두운 면 위(실 대비 1.000)인데
//      중심점이 백색이라 `ratio 16.217 · ok`로 통과했다. 판정은 표본 전체의 **최악값**이다.
//   2. 후보 = 문서 순서상 **글자보다 앞서 그려진**(= 밑에 깔린) 도형. 채움뿐 아니라
//      **stroke만으로 칠해진 면**(`fill:none` + 굵은 stroke)도 후보다 — 지면에서 그
//      stroke는 실색 띠이고, 종전 `if (!gcs.fill || gcs.fill === "none") continue`가
//      그것을 통째로 떨어뜨렸다(실측 fig-02: 56u stroke 위 라벨 실 대비 2.077 → `ok`).
//      `isPointInStroke`로 명중을 재고, 한 요소 안에서 stroke는 fill 위에 얹힌다.
//      `<defs>/<symbol>/<clipPath>/<mask>/<marker>/<pattern>` 안은 그려지지 않으므로 제외.
//   3. 명중 판정은 `isPointInFill`/`isPointInStroke`(요소 로컬 좌표) — elementsFromPoint는
//      뷰포트 밖(1600×1200을 넘는 세로 긴 도해의 아래쪽)에서 빈 배열을 돌려주므로 쓸 수 없다
//      (실측: 배지 02/03이 배경 없음으로 잡혀 백색 위 백색 = 대비 1.0 오탐이 났다).
//   4. **`url(#…)` 페인트서버는 버리지 않는다.** 종전 `normHex("url(#g)") → null`이
//      레이어를 조용히 떨어뜨려, 그라데이션 면 위 어두운 라벨이 "판면 백색 위"로 판정됐다
//      (위음성 fig-01 실 대비 1.000~2.077 → 보고 16.217). 동시에 **오탐 방향으로도** 같은
//      결함이 실재했다 — 벤더 템플릿 `sequence-ascending-stairs-3d-simple`의 큐브 면은
//      `fill="url(#cube-gradient-*)"`인데 게이트가 `#ffffff on #ffffff = 1`로 9건 반려했다.
//      그래서 그라데이션은 **stop 전량을 해석**해 각 stop을 하나의 후보 배경으로 펼치고
//      (stop-opacity 포함), 판정은 그중 **최악 대비**를 쓴다. 해석 불가한 페인트서버
//      (pattern·미존재 참조)는 낙관하지 않고 **판정 불가로 반려**한다.
//   5. 명중한 레이어들을 **도장 순서대로** 판면 백색 위에 알파 합성(fill/stroke-opacity ×
//      opacity 누적)한다. 8% 틴트 띠 같은 반투명 면이 실제로 만드는 색을 그대로 얻는다.
// `<use>`로 심긴 아이콘 내부는 shadow tree라 후보에 잡히지 않는다 — 아이콘은 라벨 배경이
// 아니므로(라벨과 겹치면 fo2text 겹침 검사가 먼저 죽인다) 미검출 방향이라 안전하다.
const PAINT_SAMPLE_FRACTIONS = [0.1, 0.3, 0.5, 0.7, 0.9]; // 최소 5점(bbox 가로)
async function measureLabelPaint(page, svg) {
  await page.setContent(stageHtml(svg), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  return page.evaluate((FRACS) => {
    const root = document.querySelector("#stage svg");
    if (!root) return null;
    const doc = root.ownerDocument;
    const painted = [...root.querySelectorAll("path,rect,circle,ellipse,polygon,polyline,line")]
      .filter((g) => !g.closest("defs,symbol,clipPath,mask,marker,pattern"));
    const alphaOf = (el, stop) => {
      let a = 1;
      for (let n = el; n && n !== stop; n = n.parentElement) {
        const o = parseFloat(getComputedStyle(n).opacity);
        if (!isNaN(o)) a *= o;
      }
      return a;
    };
    // 페인트 문자열 → {kind:"color"|"stops"|"unresolved"}. href 간접(스톱 상속)은 1단 따라간다.
    const paintCache = new Map();
    const resolvePaint = (paint) => {
      const m = /^\s*url\(\s*["']?#([^"')\s]+)["']?\s*\)/.exec(paint || "");
      if (!m) return { kind: "color", value: paint };
      const id = m[1];
      if (paintCache.has(id)) return paintCache.get(id);
      let res = { kind: "unresolved", ref: `url(#${id})` };
      let node = doc.getElementById(id);
      for (let hop = 0; node && hop < 4; hop++) {
        const tag = node.tagName ? node.tagName.toLowerCase() : "";
        // <pattern>: 타일 조각들의 색이 각각 배경 후보이고, **타일의 빈틈**(밑면이 그대로
        // 보이는 자리)도 후보다. 그래서 opacity 0짜리 항목을 하나 넣어 "기여 없음"을
        // 후보 집합에 남긴다. 벤더 `letter-card-*-pattern`(3% 먹 해치)이 이 형태다 —
        // 통째로 반려하면 compare-swot 계열이 전부 막히고, 통째로 무시하면 진한 타일이
        // 만드는 어두운 면을 놓친다.
        if (tag === "pattern") {
          const tiles = [{ color: "#ffffff", opacity: 0 }];
          for (const c of node.querySelectorAll("path,rect,circle,ellipse,polygon,polyline,line")) {
            const ccs = getComputedStyle(c);
            if (ccs.fill && ccs.fill !== "none") {
              const fo = parseFloat(ccs.fillOpacity);
              tiles.push({ color: ccs.fill, opacity: isNaN(fo) ? 1 : fo });
            }
            if (ccs.stroke && ccs.stroke !== "none") {
              const so = parseFloat(ccs.strokeOpacity);
              tiles.push({ color: ccs.stroke, opacity: isNaN(so) ? 1 : so });
            }
          }
          if (tiles.length > 1) res = { kind: "stops", stops: tiles };
          break;
        }
        if (tag !== "lineargradient" && tag !== "radialgradient") break;
        const stopEls = [...node.querySelectorAll("stop")];
        if (stopEls.length) {
          res = {
            kind: "stops",
            stops: stopEls.map((s) => {
              const scs = getComputedStyle(s);
              const so = parseFloat(scs.stopOpacity);
              return { color: scs.stopColor || s.getAttribute("stop-color") || "#000000",
                opacity: isNaN(so) ? 1 : so };
            }),
          };
          break;
        }
        // 스톱이 없으면 href가 가리키는 그라데이션에서 상속한다(SVG 1.1/2 공통 규칙)
        const href = node.getAttribute("href") || node.getAttribute("xlink:href") || "";
        const hm = /^#(.+)$/.exec(href.trim());
        node = hm ? doc.getElementById(hm[1]) : null;
      }
      paintCache.set(id, res);
      return res;
    };
    const mkLayer = (g, gcs, paintStr, alpha, via) => {
      const r = resolvePaint(paintStr);
      const base = { tag: g.tagName.toLowerCase(), via, alpha };
      if (r.kind === "color") return { ...base, fill: r.value };
      if (r.kind === "stops") return { ...base, fill: paintStr, stops: r.stops };
      return { ...base, fill: paintStr, unresolved: true };
    };
    const layersAt = (el, cx, cy) => {
      const layers = [];
      for (const g of painted) {
        if (!(el.compareDocumentPosition(g) & Node.DOCUMENT_POSITION_PRECEDING)) continue;
        const gcs = getComputedStyle(g);
        if (gcs.display === "none" || gcs.visibility === "hidden") continue;
        const hasFill = gcs.fill && gcs.fill !== "none";
        const sw = parseFloat(gcs.strokeWidth);
        const hasStroke = gcs.stroke && gcs.stroke !== "none" && !isNaN(sw) && sw > 0;
        if (!hasFill && !hasStroke) continue;
        const m = g.getScreenCTM();
        if (!m) continue;
        const p = new DOMPoint(cx, cy).matrixTransform(m.inverse());
        const ga = alphaOf(g, root.parentNode);
        if (hasFill) {
          let hit = false;
          try { hit = g.isPointInFill(p); } catch { hit = false; }
          if (hit) {
            const fo = parseFloat(gcs.fillOpacity);
            layers.push(mkLayer(g, gcs, gcs.fill, (isNaN(fo) ? 1 : fo) * ga, "fill"));
          }
        }
        if (hasStroke) {           // stroke는 같은 요소의 fill 위에 얹힌다 — 순서 유지
          let hit = false;
          try { hit = g.isPointInStroke(p); } catch { hit = false; }
          if (hit) {
            const so = parseFloat(gcs.strokeOpacity);
            layers.push(mkLayer(g, gcs, gcs.stroke, (isNaN(so) ? 1 : so) * ga, "stroke"));
          }
        }
      }
      return layers;
    };
    const out = [];
    for (const el of root.querySelectorAll("text,tspan")) {
      const cs = getComputedStyle(el);
      if (cs.display === "none" || cs.visibility === "hidden") continue;
      // 이 요소가 **직접** 품은 텍스트 노드만 — 자식 tspan은 자기 차례에 따로 잰다
      let box = null;
      for (const node of el.childNodes) {
        if (node.nodeType !== 3 || !node.textContent.trim()) continue;
        const r = document.createRange();
        r.selectNodeContents(node);
        const b = r.getBoundingClientRect();
        if (!b.width && !b.height) continue;
        box = box
          ? { left: Math.min(box.left, b.left), right: Math.max(box.right, b.right),
              top: Math.min(box.top, b.top), bottom: Math.max(box.bottom, b.bottom),
              text: box.text + node.textContent }
          : { left: b.left, right: b.right, top: b.top, bottom: b.bottom, text: node.textContent };
      }
      if (!box) continue;
      const cy = (box.top + box.bottom) / 2;
      const w = box.right - box.left;
      const samples = FRACS.map((f) => {
        const cx = box.left + w * f;
        return { at: f, layers: layersAt(el, cx, cy) };
      });
      const tfo = parseFloat(cs.fillOpacity);
      out.push({
        text: box.text.replace(/\s+/g, " ").trim().slice(0, 24),
        tag: el.tagName.toLowerCase(),
        fill: cs.fill,
        alpha: (isNaN(tfo) ? 1 : tfo) * alphaOf(el, root.parentNode),
        weight: cs.fontWeight,
        family: el.getAttribute("font-family") || cs.fontFamily,
        fontUser: parseFloat(cs.fontSize), // SVG 유저 단위(= scanLabelPt의 font-size와 같은 계)
        samples,
      });
    }
    return out;
  }, PAINT_SAMPLE_FRACTIONS);
}

// 판면 백색 위에 도장 순서대로 알파 합성 — 색 1개를 낸다(반투명 글자색 합성에도 쓴다).
function compositeOne(paints, base = [255, 255, 255]) {
  let bg = base;
  for (const { hex, alpha } of paints) {
    const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
    const a = Math.max(0, Math.min(1, alpha));
    bg = bg.map((v, i) => Math.round(c[i] * a + v * (1 - a)));
  }
  return bg;
}
// 레이어 스택 → **배경 후보 집합**. 그라데이션 레이어는 stop 하나마다 후보를 낳는다
// (그 면 위 어느 지점이든 stop들의 보간색이므로, stop 집합이 색 범위의 극점을 덮는다).
// 판정은 이 후보들 중 **최악 대비**를 쓴다 — 낙관하지 않는 방향(K4-ⓐ).
// 해석 불가 페인트서버(pattern·미존재 참조)는 후보를 만들 수 없으므로 unresolved로 표시해
// 호출부가 **판정 불가 반려**하게 한다(종전엔 조용히 버려서 배경이 백색이 됐다).
const CAND_CAP = 48;
function compositeCandidates(layers, base = [255, 255, 255]) {
  let cands = [{ rgb: base, unresolved: null }];
  for (const L of layers) {
    const a = Math.max(0, Math.min(1, L.alpha));
    if (L.unresolved) {
      cands = cands.map((c) => ({ ...c, unresolved: c.unresolved || L.fill }));
      continue;
    }
    // 색 문자열 자체의 알파(`rgba(…, 0.03)`·`#rrggbbaa`·`transparent`)를 함께 곱한다.
    const paints = L.stops && L.stops.length
      ? L.stops.map((s) => ({ hex: normHex(s.color),
          alpha: a * (typeof s.opacity === "number" ? s.opacity : 1) * colorAlpha(s.color) }))
      : [{ hex: normHex(L.fill), alpha: a * colorAlpha(L.fill) }];
    const next = [];
    for (const c of cands) {
      for (const p of paints) {
        if (!p.hex) { next.push({ ...c, unresolved: c.unresolved || L.fill }); continue; }
        next.push({ rgb: compositeOne([p], c.rgb), unresolved: c.unresolved });
      }
    }
    // 같은 색이 여러 경로로 나오면 하나로 — 조합 폭발 방지(스톱 n개 × 레이어 m개)
    const seen = new Map();
    for (const c of next) {
      const k = `${c.rgb.join(",")}|${c.unresolved || ""}`;
      if (!seen.has(k)) seen.set(k, c);
    }
    cands = [...seen.values()].slice(0, CAND_CAP);
  }
  return cands;
}
const toHex = (rgb) => "#" + rgb.map((v) => v.toString(16).padStart(2, "0")).join("");

// ---- 7단계 HARD: 역할 · 대비 ----
//
// ① 역할 — 글자의 fill은 **palette_roles가 `label`이라 선언한 색**이거나 **백색 knockout**
//    이어야 한다. 팔레트 밖 색은 트랙별 색 계약을 그대로 따른다: authored는
//    alienColors(strict)가 이미 죽였으므로 여기 오면 위반, antv는 무채색 램프가 허용되므로
//    (:118과 같은 임계) 무채색만 통과시키고 대비 검사에 넘긴다. **유채색 팔레트 밖 글자는
//    양 트랙 모두 위반** — antv 트랙에는 alienColors가 걸려 있지 않아(현재 호출 지점은
//    authored 한 곳뿐) 이 축이 유일한 방어선이다.
// ② 대비 — 글자색 × 실배경색의 대비가 contrast_floor(pt, bold) 이상이어야 한다.
//    **백색 knockout에 면제는 없다.** ①이 백색을 통과시키는 것은 "역할표가 백색을
//    말하지 않는다"는 뜻일 뿐이고, 백색 글자가 밝은 면에 얹혔는지는 ②가 본다
//    (실측 참양성: `#ffffff` on `#5ec6dc` = 1.98).
//
// 강도는 **HARD**다. 다만 렌더 전 정적 게이트가 아니라 렌더 파이프라인 내부이므로
// die가 아니라 해당 도해의 `fail()` 관례를 따른다(호출부에서 fail).
function labelPaintReport(measures, scan, { name, kind, widthKey }) {
  const rows = [];
  const roleV = [], contrastV = [];
  const notes = [];
  if (!paletteRoles) notes.push("tokens.diagram.palette_roles 미선언 — 역할 검사 꺼짐");
  if (scan.scalePt === null) notes.push(`pt 환산 불가(widths.${widthKey} 또는 viewBox 폭 부재) — 대비 검사 꺼짐`);
  for (const m of measures || []) {
    const hex = normHex(m.fill);
    const pt = scan.scalePt === null ? null : m.fontUser * scan.scalePt;
    const bold = isBoldSvgText(m.weight, m.family);
    const roles = hex && roleOf.has(hex) ? [...roleOf.get(hex)] : null;
    // 표본(bbox 다점) × 배경 후보(그라데이션 stop)를 전부 펼쳐 **최악 대비**를 고른다.
    let worst = null, unresolved = null, maxLayers = 0;
    for (const s of m.samples || []) {
      maxLayers = Math.max(maxLayers, s.layers.length);
      for (const c of compositeCandidates(s.layers)) {
        if (c.unresolved && !unresolved) unresolved = c.unresolved;
        if (c.unresolved) continue;             // 판정 불가는 대비 수치를 만들지 않는다
        // 반투명 글자는 배경과 먼저 합성한다(=실제로 보이는 색). 대비를 낙관하지 않는 방향.
        const fg = hex ? compositeOne([{ hex, alpha: m.alpha * colorAlpha(m.fill) }], c.rgb) : null;
        const ratio = fg ? contrastRatio(fg, c.rgb) : null;
        if (ratio !== null && (worst === null || ratio < worst.ratio)) {
          worst = { ratio, bgRgb: c.rgb, fgRgb: fg, at: s.at };
        }
      }
    }
    const bgRgb = worst ? worst.bgRgb : [255, 255, 255];
    const bg = toHex(bgRgb);
    const fgRgb = worst ? worst.fgRgb : null;
    const row = {
      text: m.text, tag: m.tag, fill: hex || m.fill, knockout: hex === PAPER_HEX,
      role: roles, bg, bgLayers: maxLayers,
      samples: (m.samples || []).length, bgWorstAt: worst ? worst.at : null,
      pt: r3(pt), bold, ratio: null, floor: null, verdict: "ok",
    };
    // 해석 불가 페인트서버(pattern 등) 위 글자는 배경을 알 수 없다 — 낙관하지 않고 반려한다.
    if (unresolved) {
      contrastV.push(`'${m.text}' 배경 페인트서버 '${unresolved}' 해석 불가 — `
        + `그라데이션(stop)이 아닌 페인트서버 위 글자는 실배경을 산출할 수 없어 대비를 판정할 수 없다. `
        + `단색 또는 그라데이션 면 위로 옮기거나, 그 면을 단색으로 그릴 것`);
      row.verdict = "contrast";
      row.bg = unresolved;
    }
    // ① 역할
    if (paletteRoles && hex !== PAPER_HEX) {
      if (!hex) {
        roleV.push(`'${m.text}' 색 '${m.fill}' 해석 불가 — 글자색은 hex/rgb()/명명색으로 지정할 것`);
        row.verdict = "role";
      } else if (roles) {
        if (!roles.includes("label")) {
          roleV.push(`'${m.text}' ${hex}은 palette_roles상 '${roles.join("/")}' 역할 — `
            + `글자에는 role 'label' 슬롯 또는 백색 knockout만 허용`);
          row.verdict = "role";
        }
      } else if (kind === "authored" || !isNeutral(hex)) {
        roleV.push(`'${m.text}' ${hex}은 styles/${style} tokens.diagram.palette 밖의 색 — `
          + `글자에는 role 'label' 슬롯 또는 백색 knockout만 허용`);
        row.verdict = "role";
      }
    }
    // ② 대비 (역할 위반이어도 함께 잰다 — 반려 메시지가 두 사실을 다 말하게)
    if (pt !== null && fgRgb) {
      const ratio = contrastRatio(fgRgb, bgRgb);
      const floor = contrastFloor(pt, bold);
      row.ratio = Math.round(ratio * 1000) / 1000;
      row.floor = floor;
      if (ratio < floor) {
        contrastV.push(`'${m.text}' ${hex} on ${bg} 대비 ${row.ratio} < ${floor} `
          + `(${row.pt}pt${bold ? " bold" : ""}${maxLayers ? "" : " · 배경 = 판면 백색"}`
          + `${worst && worst.at !== 0.5 ? ` · bbox 가로 ${Math.round(worst.at * 100)}% 표본이 최악` : ""})`);
        if (row.verdict === "ok") row.verdict = "contrast";
      }
    }
    rows.push(row);
  }
  const ratios = rows.map((r) => r.ratio).filter((v) => typeof v === "number");
  const metrics = {
    checked: rows.length,
    knockout: rows.filter((r) => r.knockout).length,
    roleViolations: roleV.length,
    contrastViolations: contrastV.length,
    minRatio: ratios.length ? Math.min(...ratios) : null,
    notes,
    labels: rows,
  };
  const lines = notes.map((n) => `WARN DIAGRAM-PAINT ${name}: ${n}`);
  return { metrics, lines, violations: [...roleV, ...contrastV] };
}

// 캐시 해시에 실리는 「판정 파라미터」 — 도해 SVG는 이 값들로 검사·환산되므로
// 값이 바뀌면 캐시가 그 도해만 정확히 무효화되어야 한다(전역 CONVERTER_VERSION 대신).
//   widthMm   : fontFloorViolations의 pt 환산 기준 폭 — 2·3단계 폭 동기화의 재렌더 트리거
//   minFontPt : 글자 하한(HARD)
//   labelBand : 라벨 밴드 상한 {maxRatio}(5단계 신설) — 부재 시 null로 고정.
//               null → 실값으로 바뀌는 순간 해당 스타일 도해 전건 재렌더가 **의도된 동작**이다.
// 키를 재귀 정렬해 tokens.json의 키 순서가 바뀌어도 해시가 흔들리지 않게 한다.
function stableSort(v) {
  if (Array.isArray(v)) return v.map(stableSort);
  if (v && typeof v === "object") {
    return Object.fromEntries(Object.keys(v).sort().map((k) => [k, stableSort(v[k])]));
  }
  return v === undefined ? null : v;
}
function gateParams(widthKey) {
  return stableSort({
    widthMm: (dg.widths || {})[widthKey] ?? null,
    minFontPt: dg.minFontPt ?? null,
    labelBand: dg.labelBand ?? null,
    // 7단계: 역할·대비 HARD의 판정 입력. **팔레트 값은 이미 양 트랙 해시에 있었지만
    // palette_roles는 없었다** — roles만 고쳐도 판정이 뒤집히는데 캐시가 히트해
    // 옛 판정이 남는 구멍이었다. paintPolicy는 검사 자체의 지문(판정식이 바뀌면
    // 재검사가 필요하다) — 대비 하한은 wcag.mjs(=g16_tokens.contrast_floor) 소관이라
    // 여기엔 버전만 싣는다.
    paletteRoles: dg.palette_roles ?? null,
    // W7: 배치 높이 상한 — figFitReport의 판정 입력. 값이 바뀌면 축소 폭(metrics.fit)이
    // 바뀌므로 그 스타일 도해가 전건 재판정되어야 한다(widths와 같은 계열).
    maxHeightMm: dg.maxHeightMm ?? null,
    // paintPolicy: 판정식(배경 산출 규칙)의 지문. 2 = W5 재작업 — 그라데이션 stop 해석 ·
    // stroke 면 후보 편입 · bbox 다점 표본 최악값(K4).
    paintPolicy: 3,
    // K10: 판정을 정하는 **세 파일의 내용 해시**. 손으로 올리는 상수가 아니라 파일
    // 자체를 싣는다 — 대비 하한(wcag)·변환기(fo2text)·배경 산출식(이 파일)을 건드리면
    // 사람 개입 없이 그 기준으로 판정된 적 없는 도해가 전건 재렌더된다.
    wcagHash: WCAG_HASH,
    converterHash: CONVERTER_HASH,
    rendererHash: RENDERER_HASH,
    // 5단계: 상한이 body_pt에 상대적이므로 본문 급수도 판정 파라미터다. 이게 없으면
    // body_pt만 바뀐 스타일에서 캐시된 metrics의 밴드 판정이 옛 기준으로 남는다.
    bodyPt: tokens.body_pt ?? null,
  });
}

// 라벨 급수 실측 — <text>/<tspan>의 font-size(속성·인라인 style)를 **트림 후 최종 좌표계**에서
// pt로 환산한다. 하한(fontFloorViolations, HARD)과 상한(labelBandReport, WARN)이 반드시 같은
// 스캔을 보게 해 두 판정이 서로 다른 숫자를 말하는 일이 없게 한다.
const BAND_TOL_PT = 0.05; // 하한 판정과 대칭인 부동소수 여유
function scanLabelPt(svg, widthKey) {
  const widthMm = (dg.widths || {})[widthKey] ?? null;
  const vb = svg.match(/viewBox="[-\d. ]*?([\d.]+) ([\d.]+)"\s*/);
  const vbW = vb ? parseFloat(vb[1]) : null;
  const vbH = vb ? parseFloat(vb[2]) : null; // 배치 높이 산출(figFitReport)용 — pt 환산은 폭만 쓴다
  const scalePt = widthMm && vbW ? (widthMm * MM2PT) / vbW : null; // user unit -> 실제 pt
  const sizes = [];
  const unitErrors = [];
  const take = (tag, num, unit) => {
    let user = parseFloat(num);
    if (unit === "pt") user *= 96 / 72; // CSS pt → user unit(px)
    else if (unit && unit !== "px") { // 미지 단위는 검증 불가 — 침묵 통과 금지
      unitErrors.push(`${tag} font-size 단위 '${unit}' 미지원 — px/pt/무단위로 지정할 것`);
      return;
    }
    sizes.push({ tag, raw: `${num}${unit || "u"}`, pt: scalePt === null ? null : user * scalePt });
  };
  // <text>뿐 아니라 <tspan>의 font-size 속성·style 내 font-size도 검사 (하한 우회 차단)
  for (const m of svg.matchAll(/<(text|tspan)\b[^>]*?font-size="([\d.]+)([a-z%]*)"/gi)) take(m[1], m[2], m[3]);
  for (const m of svg.matchAll(/<(text|tspan)\b[^>]*?style="[^"]*?font-size\s*:\s*([\d.]+)([a-z%]*)/gi)) take(m[1], m[2], m[3]);
  return { widthMm, vbW, vbH, scalePt, sizes, unitErrors };
}

// 밴드 하한 — 기존 계약 그대로 **HARD**. (minFontPt 미선언·widths 미선언 시 검사가 꺼지는
// 종전 동작도 그대로 둔다 — 그 침묵은 labelBandReport가 WARN으로 드러낸다.)
function fontFloorViolations(scan) {
  const minPt = dg.minFontPt;
  if (!minPt || !scan.widthMm) return [];
  if (!scan.vbW) return [`viewBox 폭을 읽지 못함 — minFontPt 검사 불가`];
  const out = [...scan.unitErrors];
  for (const s of scan.sizes) {
    if (s.pt < minPt - BAND_TOL_PT) out.push(`${s.tag} ${s.raw} ≈ ${s.pt.toFixed(1)}pt < ${minPt}pt 하한`);
  }
  return out;
}

const r3 = (v) => (typeof v === "number" && isFinite(v) ? Math.round(v * 1000) / 1000 : null);

// ---- 도해 배치 높이 상한 (W7 신설 — 세로 셰브런 면 분단 사고의 근본 수리) ----
//
// 도해는 지면에서 bf.width의 물리 폭으로 발행되므로 배치 높이 = widthMm × (vbH/vbW)다.
// 이 높이가 tokens.diagram.maxHeightMm(스타일별 판면·캡션 실측 파생 — 단일 진리원)를
// 넘으면 figure(도해+캡션)가 한 면에 못 들어가고, HTML 트랙(Chromium print)은
// break-inside:avoid를 지킬 수 없어 면 경계에서 **도해를 쪼갠다**(실증: insight b2-20
// fig-01 130mm × 종횡비 1.96 = 254.8mm → p5 단계 01~03 / p6 단계 04+캡션). typst 트랙은
// 쪼개는 대신 판면 아래로 넘친다 — 어느 쪽도 출하 가능한 지면이 아니다.
//
// 수리는 **폭 비례 축소**다(높이 상한을 폭으로 역산: fitW = widthMm × maxH/배치높이).
// 단 라벨 실효 pt가 실렌더 폭에 비례하므로(scalePt = widthMm×MM2PT/vbW) 축소 허용
// 한계는 라벨 하한에서 역산된다:
//   필요 축소 k = maxHeightMm / 배치높이,  허용 하한 k_min = minFontPt / (최소 라벨 pt).
// k < k_min이면 자동 축소가 하한 HARD를 깨므로 그 도해는 **반려**다 — 처방은 재작성
// (세로 항목 수 축소 또는 가로 배치 템플릿)이고, 수용 가능한 최대 배치 높이
// maxH/k_min을 진단에 싣는다. 축소 결정은 여기 **단일 지점**에서 내려 metrics.fit에
// 싣고, 배치자(build_html.py figure 인라인 width · md2typ.py #bf-fig width:)는 그 값을
// 전사만 한다 — CSS max-height는 인라인 SVG를 뷰포트 안에서 letterbox(가운데 정렬)해
// 판면 좌측 정렬축을 깨고 typst에는 등가물이 없으므로 쓰지 않는다.
// 밴드 상한과의 상호작용: 축소는 모든 라벨 pt를 함께 줄이므로 상한(cap) 방향으로는
// 언제나 안전하고, 하한만 위 k_min이 지킨다. 대비 하한 급수 분기(14pt)는 밴드 상한
// (body_pt×1.2 ≤ 12.6pt)이 이미 14pt 아래라 축소로 갈리지 않는다.
const FIT_TOL_MM = 0.5; // G1 판형 대조와 같은 자릿수의 실측 여유
function figFitReport(scan, { name }) {
  const maxH = dg.maxHeightMm; // 계약 검증(양수·<trim 높이)은 시동 시 완료
  const { widthMm, vbW, vbH } = scan;
  if (!widthMm || !vbW || !vbH) {
    const reason = !widthMm ? "widths 부재(pt 환산 축과 같은 꺼짐)" : "viewBox 폭/높이를 읽지 못함";
    return { metrics: { verdict: "skip", reason, maxHeightMm: maxH },
      lines: [`WARN DIAGRAM-FIT ${name}: 배치 높이 검사 꺼짐 — ${reason}`] };
  }
  const placedH = widthMm * (vbH / vbW);
  const base = { maxHeightMm: maxH, nominalWidthMm: widthMm, placedHMm: r3(placedH) };
  if (placedH <= maxH + FIT_TOL_MM) {
    return { metrics: { verdict: "ok", ...base, widthMm }, lines: [] };
  }
  const k = maxH / placedH;
  const pts = scan.sizes.map((s) => s.pt).filter((p) => typeof p === "number" && isFinite(p));
  const minPt = pts.length ? Math.min(...pts) : null;
  const maxPt = pts.length ? Math.max(...pts) : null;
  const floorPt = typeof dg.minFontPt === "number" ? dg.minFontPt : null;
  if (floorPt !== null && minPt !== null && minPt * k < floorPt - BAND_TOL_PT) {
    const kMin = floorPt / minPt;
    fail(`${name}: 도해 배치 높이 ${r3(placedH)}mm > 상한 ${maxH}mm(styles/${style} diagram.maxHeightMm) — `
      + `한 면에 넣으려면 ×${k.toFixed(3)} 축소가 필요한데 라벨 하한 ${floorPt}pt가 `
      + `×${kMin.toFixed(3)}(= ${floorPt}pt ÷ 최소 라벨 ${r3(minPt)}pt)까지만 허용한다`
      + `(축소 시 최소 라벨 ${(minPt * k).toFixed(2)}pt). 자동 축소 대상이 아니다 — `
      + `세로 항목 수를 줄이거나 가로 배치로 재작성하라(원장 verdict=ok 가로형: `
      + `list-row-simple-horizontal-arrow · sequence-timeline-simple · list-grid-simple). `
      + `이 라벨 구성이 수용 가능한 최대 배치 높이 = ${r3(maxH / kMin)}mm`);
  }
  const fitW = r3(widthMm * k);
  return {
    metrics: { verdict: "shrunk", ...base, widthMm: fitW, k: r3(k),
      effMinPt: minPt === null ? null : r3(minPt * k), effMaxPt: maxPt === null ? null : r3(maxPt * k) },
    lines: [`DIAGRAM-FIT ${name}: 배치 높이 ${r3(placedH)}mm > 상한 ${maxH}mm — 폭 `
      + `${widthMm} → ${fitW}mm(×${k.toFixed(3)}) 축소로 한 면 수용`
      + (minPt === null ? "" : ` · 실효 라벨 ${r3(minPt * k)}~${r3(maxPt * k)}pt`
        + (floorPt === null ? "" : `(하한 ${floorPt}pt 위)`))],
  };
}

// 밴드 상한 — 라벨 최대 pt ≤ body_pt × labelBand.maxRatio.
//
// **WARN으로 태어난다** (설계 정본 report/w5-design.md 「최대 리스크」 1).
// 사용자 원 지적은 "도해 라벨이 본문보다 크다"였지만, 실측 코퍼스의 max/본문 비는 중앙 0.96·
// p90 1.17이고 도해 내부 활자비(중앙 1.095×)가 창 폭 비(8.74/8.00 = 1.0925×)를 넘는 도해가
// 다수라 상·하한을 **축척으로 동시에 만족시킬 수 없다**(축척은 두 끝을 함께 옮긴다).
// cap 0.92를 HARD로 내면 authored 대다수와 AntV 트랙 전체가 즉시 반려되어 릴리스가 선다.
// 따라서 cap 1.20[하우스 등급] · 강도 WARN으로 출생시켰고, **8단계에서 스타일별
// `labelBand.enforce`로 승격**했다(위반 0인 스타일만 true — contrast_contract 선례).
// enforce:true면 위반이 그 도해의 fail()이다(7단계 HARD 관례). 강도는 metrics.band.level에
// 그대로 남으므로 리포트만 봐도 "이 판정이 릴리스를 세우는가"를 알 수 있다.
//
// 반환: 콘솔 출력용 lines + assets/fig-NN.metrics.json에 실릴 metrics.
function labelBandReport(scan, { name, kind, widthKey, scaled = false, template = null, cacheKey = null }) {
  const band = dg.labelBand && typeof dg.labelBand === "object" ? dg.labelBand : null;
  const maxRatio = band && typeof band.maxRatio === "number" ? band.maxRatio : null;
  const bodyPt = typeof tokens.body_pt === "number" ? tokens.body_pt : null;
  const floorPt = typeof dg.minFontPt === "number" ? dg.minFontPt : null;
  const pts = scan.sizes.map((s) => s.pt).filter((p) => typeof p === "number" && isFinite(p));
  const metrics = {
    schema: "bf-diagram-metrics/2",
    fig: name, kind, style, widthKey,
    // 이 metrics를 낳은 산출 SVG의 캐시 해시. **캐시 히트 조건에 이 값의 일치를 넣는다** —
    // 넣지 않으면 metrics와 SVG가 갈라질 수 있다: HARD 반려(밴드 enforce·역할·대비)는
    // metrics를 쓴 뒤 SVG를 쓰기 전에 죽으므로, 직전 성공 렌더의 SVG 옆에 **실패한 회차의
    // metrics**가 남는다. 그 상태에서 소스를 되돌리면 SVG 해시는 맞아 캐시가 히트하고
    // 판정은 옛 위반 metrics를 재생한다(실측으로 잡은 오탐).
    cacheKey,
    // 8단계: 원장(diagram-ledger.json)이 **템플릿별** 원장이므로 집계 키가 metrics 안에
    // 있어야 재도출이 metrics만으로 닫힌다(사이드카를 다시 파싱하지 않는다). authored는 null.
    template,
    widthMm: scan.widthMm, viewBoxW: r3(scan.vbW),
    // 환산 계수는 3자리로 자르면 pt 재산출이 어긋난다 — 5자리 유지
    ptPerUnit: scan.scalePt === null ? null : Math.round(scan.scalePt * 1e5) / 1e5,
    bodyPt, minFontPt: floorPt, maxRatio,
    sizeCount: pts.length,
    minPt: pts.length ? r3(Math.min(...pts)) : null,
    maxPt: pts.length ? r3(Math.max(...pts)) : null,
    ratio: null, capPt: null,
    band: { level: BAND_ENFORCE ? "FAIL" : "WARN", enforce: BAND_ENFORCE, verdict: "skip", reason: null },
    sizesPt: pts.map(r3).sort((a, b) => a - b),
  };
  const lines = [];
  // 강도 표기는 한 곳에서 만든다 — 승격 스타일에서 사실 행만 FAIL이고 처방 행은 WARN인
  // 식으로 갈리면 로그가 강도에 대해 두 말을 하게 된다.
  const tagB = BAND_ENFORCE ? "DIAGRAM-BAND(enforce)" : "WARN DIAGRAM-BAND";
  // 검사가 꺼지는 모든 경우를 소리내어 알린다 — 미선언이 위반보다 조용해서는 안 된다.
  const off = maxRatio === null ? "tokens.diagram.labelBand.maxRatio 미선언"
    : bodyPt === null ? "tokens.body_pt 미선언(G1-SCALE도 같은 이유로 꺼진다)"
    : scan.scalePt === null ? `pt 환산 불가(widths.${widthKey} 또는 viewBox 폭 부재)`
    : !pts.length ? "font-size 실측 0건" : null;
  if (off) {
    metrics.band.reason = off;
    // enforce:true는 "이 스타일에서 상한이 지켜진다"는 선언이다. 검사가 꺼진 채로 통과하면
    // 그 선언이 아무것도 뜻하지 않게 되므로, 승격한 스타일에서는 **꺼짐 자체가 반려**다
    // (미선언이 위반보다 조용해서는 안 된다 — 5단계가 꺼짐을 WARN으로 드러낸 것의 연장).
    lines.push(`${tagB} ${name}: 라벨 밴드 상한 검사 꺼짐 — ${off}`);
    return { metrics, lines, violated: false, off };
  }
  const minPt = Math.min(...pts), maxPt = Math.max(...pts);
  const capPt = bodyPt * maxRatio;
  metrics.ratio = r3(maxPt / bodyPt);
  metrics.capPt = r3(capPt);
  const violated = maxPt > capPt + BAND_TOL_PT;
  metrics.band.verdict = violated ? "violation" : "ok";
  // 콘솔 수치는 metrics.json에 실리는 값과 같은 반올림을 쓴다(두 산출물이 다른 숫자를 말하지 않게).
  const fact = `최대 라벨 ${metrics.maxPt}pt = 본문 ${bodyPt}pt × ${metrics.ratio} `
    + `(상한 ${maxRatio}× = ${metrics.capPt}pt) · 최소 라벨 ${metrics.minPt}pt`
    + (floorPt ? `(하한 ${floorPt}pt)` : "")
    + ` · 급수 ${pts.length}건 · bf.width=${widthKey} ${scan.widthMm}mm ÷ viewBox ${scan.vbW}u `
    + `= ${scan.scalePt.toFixed(5)}pt/u`;
  if (!violated) return { metrics, lines, violated: false };

  // ---- 반려 진단 (트랙별 분기) ----
  // 상한 위반이므로 수리 방향은 **라벨 축소 / viewBox 확대**다. 하한 위반의 처방
  // (폭 확대·font-size 확대)과 부호가 반대라는 점을 명시한다.
  const shrink = capPt / maxPt;                               // 균일 축척 계수(<1)
  const uniformOk = !floorPt || minPt * shrink >= floorPt - BAND_TOL_PT;
  const internal = maxPt / minPt;                             // 도해 내부 활자비
  const allowedInternal = floorPt ? capPt / floorPt : null;   // 밴드가 허용하는 최대 내부비
  // 강도는 스타일 스위치가 정한다 — 같은 사실을 두 등급으로 말한다(문구가 갈리면 두 산출물이
  // 다른 숫자를 말하게 되므로 사실 문장 `fact`는 공유한다).
  lines.push(`${tagB} ${name}: 라벨 밴드 상한 초과 — ${fact}`);
  if (kind === "antv" && scaled) {
    // 6단계 주입이 이미 걸렸는데도 넘는 경우 — 테마·클램프 어느 쪽으로도 못 잡은 급수가 남았다.
    lines.push(`${tagB} ${name}:   → 라벨 급수 강제(역할별 font-size 주입 + 하드코딩 급수 클램프)를`
      + ` 적용한 뒤에도 상한 초과. 이 템플릿에 테마·native <text> 어느 경로로도 도달하지 않는 급수가 남아 있다`
      + `(예: CSS 클래스·<style> 블록 경유). fig-NN.metrics.json의 labelScale.iterations로 회차별 실측을 확인하고,`
      + ` 해소 불가면 8단계 원장에서 이 템플릿 자체를 판정할 것.`);
  } else if (kind === "antv") {
    lines.push(`${tagB} ${name}:   → AntV DSL 트랙 = **6단계 스케일 강제 대상**`
      + `(applyTheme에 font-size 주입). 템플릿이 급수를 하드코딩하므로 사이드카·폭 조정으로는 해소되지 않는다.`
      + (uniformOk ? "" : ` 균일 축척(×${shrink.toFixed(3)})으로는 최소 라벨이 ${(minPt * shrink).toFixed(2)}pt로`
        + ` 하한 ${floorPt}pt 미달 — 6단계는 역할별(label/desc/title) 분리 주입이어야 한다.`));
  } else if (uniformOk) {
    lines.push(`${tagB} ${name}:   → 수리: 라벨 font-size를 ×${shrink.toFixed(3)} 이하로 **축소**하거나,`
      + ` viewBox 폭을 ${scan.vbW}u → ${(scan.vbW / shrink).toFixed(1)}u 이상으로 **확대**할 것`
      + `(폭 확대 = 유효 pt 축소). ※ 하한 위반의 처방(폭 축소·font-size 확대)과 방향이 반대다.`);
  } else {
    lines.push(`${tagB} ${name}:   → 균일 축척으로는 해소 불가(축척은 상·하한을 함께 옮긴다):`
      + ` ×${shrink.toFixed(3)} 축소 시 최소 라벨이 ${(minPt * shrink).toFixed(2)}pt로 하한 ${floorPt}pt 미달이고,`
      + ` viewBox 확대도 같은 이유로 막힌다. 이 도해의 라벨 최대/최소 비 ${internal.toFixed(3)}×가`
      + ` 밴드 허용 내부비 ${allowedInternal.toFixed(3)}×(= 상한 ${capPt.toFixed(2)}pt ÷ 하한 ${floorPt}pt)를 넘는다`
      + ` — 폭이 아니라 **라벨 간 상대 급수**를 좁혀야 한다(최대 라벨만 축소).`);
  }
  return { metrics, lines, violated: true };
}

// 실측을 도해별로 축약 없이 남긴다: 콘솔 1행 + assets/fig-NN.metrics.json(8단계 원장 입력).
// 캐시 히트 때도 저장된 metrics로 같은 줄을 다시 낸다 — 2회차 빌드에서 조용해지는 경고는
// 없는 경고와 같다.
function emitBand(report, outMetricsPath) {
  writeFileSync(outMetricsPath, JSON.stringify(report.metrics, null, 2));
  for (const l of report.lines) console.log(l);
  return report;
}
function bandSummary(m) {
  if (!m || m.maxPt === null) return "라벨 실측 없음";
  const r = m.ratio === null ? "" : ` = 본문 ${m.bodyPt}pt × ${m.ratio}`
    + (m.band && m.band.verdict === "violation" ? ` **상한 ${m.maxRatio}× 초과**` : "");
  const s = m.labelScale && m.labelScale.applied
    ? `, 급수 강제 적용(${m.labelScale.passes}회 수렴, 하드코딩 클램프 ${m.labelScale.nativeClamped}건)` : "";
  // 7단계: 통과한 대비도 소리내어 남긴다 — "검사가 돌았고 최악이 얼마였다"가 안 보이면
  // 꺼진 검사와 구별되지 않는다(8단계 원장의 입력이기도 하다).
  const p = m.labelPaint
    ? `, 대비 최악 ${m.labelPaint.minRatio ?? "—"}(knockout ${m.labelPaint.knockout}/${m.labelPaint.checked})` : "";
  // W7: 캐시 히트 때도 축소 사실이 보이게 — 조용해지는 축소는 없는 축소와 같다
  const f = m.fit && m.fit.verdict === "shrunk"
    ? `, 배치 ${m.fit.placedHMm}mm>상한 → 폭 ${m.fit.widthMm}mm(×${m.fit.k}) 축소` : "";
  return `라벨 ${m.minPt}~${m.maxPt}pt${r}${s}${p}${f}`;
}
// 캐시 히트 선행조건 — metrics가 **이 해시로 렌더된 것**인가. 파일 존재만 보면
// 실패 회차가 남긴 metrics를 성공 SVG 옆에서 그대로 재생하게 된다(위 cacheKey 주석).
function metricsKeyMatches(outMetricsPath, key) {
  if (!existsSync(outMetricsPath)) return false;
  try { return JSON.parse(readFileSync(outMetricsPath, "utf8")).cacheKey === key; }
  catch { return false; }
}
function replayBand(outMetricsPath, name) {
  if (!existsSync(outMetricsPath)) return null;
  let m;
  try { m = JSON.parse(readFileSync(outMetricsPath, "utf8")); } catch { return null; }
  const tag = BAND_ENFORCE ? "DIAGRAM-BAND(enforce)" : "WARN DIAGRAM-BAND";
  if (m && m.band && m.band.verdict === "violation") {
    console.log(`${tag} ${name}: 라벨 밴드 상한 초과(캐시 유지) — `
      + `최대 ${m.maxPt}pt = 본문 ${m.bodyPt}pt × ${m.ratio} > 상한 ${m.maxRatio}× (${m.capPt}pt)`);
    // **구조상 도달 불가 어서션**: gateParams가 labelBand를 통째로 실으므로 enforce:true로
    // 렌더된 도해는 위반이면 svg가 쓰이기 전에 fail()했고, enforce:false로 렌더된 svg는
    // 해시가 달라 여기까지 오지 않는다. 그래도 남긴다 — 해시 계약이 미래에 좁아지면
    // "캐시가 위반을 통과시키는" 구멍이 조용히 열리기 때문이다(5단계가 캐시 히트에도
    // 경고를 다시 낸 것과 같은 이유). 도달 불가라 뮤테이션 어서션 대상이 아니며,
    // 대신 M15가 **해시 편입 자체**(enforce 변조 → 재렌더)를 어서션한다.
    if (BAND_ENFORCE) fail(`${name}: 라벨 밴드 상한 초과(캐시된 판정) — labelBand.enforce=true인 스타일에서 캐시가 위반을 통과시켰다(해시 계약 파손 의심)`);
  } else if (m && m.band && m.band.verdict === "skip") {
    console.log(`${tag} ${name}: 라벨 밴드 상한 검사 꺼짐(캐시 유지) — ${m.band.reason}`);
    if (BAND_ENFORCE) fail(`${name}: 라벨 밴드 상한 검사 꺼짐(캐시된 판정) — ${m.band.reason}. enforce:true는 검사가 실제로 도는 것을 전제한다`);
  }
  return m;
}

async function ssrWithRetry(dsl, name) {
  // SSR 내장 타임아웃(10s)은 미지 템플릿 등 일부 경로에서 발화하지 않는다(실측) —
  // 외부 30s 레이스로 무한 대기를 차단한다.
  const withTimeout = (p, ms) => Promise.race([
    p, new Promise((_, rej) => setTimeout(() => rej(new Error(`timeout ${ms}ms`)), ms).unref?.()),
  ]);
  for (let attempt = 1; attempt <= 3; attempt++) {
    try { return await withTimeout(renderToString(dsl), 30_000); }
    catch (e) {
      if (attempt === 3) fail(`${name}: SSR 3회 실패 — ${e.message}`);
      console.error(`${name}: SSR attempt ${attempt} failed (${e.message}) — retry`);
    }
  }
}

const assetsDir = path.join(bookDir, "assets");
mkdirSync(assetsDir, { recursive: true });
const checkDir = path.join(bookDir, "typeset", "diagcheck");
mkdirSync(checkDir, { recursive: true });

let browser = null;
let page = null;
let rendered = 0, skipped = 0, bandWarns = 0;

for (const file of sidecars) {
  const name = file.replace(/\.json$/, "");
  const sidecar = JSON.parse(readFileSync(path.join(bookDir, "diagrams", file), "utf8"));
  const bf = sidecar.bf || {};
  const widthKey = bf.width || "full";
  if (!["full", "twothirds"].includes(widthKey)) fail(`${name}: bf.width는 full|twothirds`);
  const kind = sidecar.kind || "antv";
  if (!["antv", "authored"].includes(kind)) fail(`${name}: kind는 antv|authored`);

  if (kind === "authored") {
    // ---- authored SVG 트랙: 에이전트가 그린 diagrams/fig-NN.svg를 동일 정규화 파이프라인에 통과 ----
    const srcPath = path.join(bookDir, "diagrams", `${name}.svg`);
    if (!existsSync(srcPath)) fail(`${name}: kind=authored인데 diagrams/${name}.svg 부재`);
    const rawAuthored = readFileSync(srcPath, "utf8");
    if (/xml-stylesheet/.test(rawAuthored) || /(?:href|src)="https?:\/\//.test(rawAuthored)) {
      fail(`${name}: 외부 참조(CDN 폰트·원격 자원) 금지 — 자립 SVG로 그릴 것`);
    }
    // palette 포함 필수: 스타일(팔레트) 교체 재빌드 시 캐시 미스로 alienColors 재검증 강제
    const hashA = createHash("sha256")
      .update(JSON.stringify({ svg: rawAuthored, width: widthKey, palette, gate: gateParams(widthKey), v: CONVERTER_VERSION }))
      .digest("hex");
    const outSvgA = path.join(assetsDir, `${name}.svg`);
    const outLabelsA = path.join(assetsDir, `${name}.labels.json`);
    const outMetricsA = path.join(assetsDir, `${name}.metrics.json`);
    if (existsSync(outSvgA) && existsSync(outLabelsA) && metricsKeyMatches(outMetricsA, hashA)) {
      const head = readFileSync(outSvgA, "utf8").slice(0, 130);
      if (head.includes(`bf:authored=sha256:${hashA}`)) {
        skipped++;
        const m = replayBand(outMetricsA, name);
        console.log(`${name}: cache hit — skip (${bandSummary(m)})`);
        continue;
      }
    }
    const tA = Date.now();
    if (!browser) {
      browser = await chromium.launch();
      page = await browser.newPage({ viewport: { width: 1600, height: 1200 }, deviceScaleFactor: 2 });
    }
    let normalized, labelsA;
    try {
      ({ svg: normalized, labels: labelsA } = await normalizeAuthoredSvg(page, rawAuthored, FONT_DIR));
    } catch (e) {
      fail(`${name}: ${e.message.replace(/^.*Error: /s, "").split("\n")[0]}`);
    }
    if (!labelsA.length) fail(`${name}: 라벨 0개`);
    const aliens = alienColors(normalized, palette, true);
    if (aliens.length) {
      // 구 토큰으로 그린 authored SVG를 위한 안내: insight --ink-mute가 대비 하한 미달로
      // 교체됐다(#6d747a는 tint #ecf8fe 위 4.37 < 4.5 — 실물 사고 사례가 있다).
      const migrated = aliens.includes("#6d747a")
        ? " · #6d747a는 대비 미달로 #5a6167로 교체됐다 — SVG의 해당 색을 바꿀 것"
        : "";
      fail(`${name}: 팔레트 밖 색 ${aliens.join(", ")} — authored SVG는 styles/${style} tokens.diagram.palette + #ffffff만 허용(토큰 밖 색 금지)${migrated}`);
    }
    const checkA = await pixelSelfCheck(browser, rawAuthored, normalized, FONT_DIR, path.join(checkDir, name));
    if (checkA.ratio > PIXEL_TOLERANCE) {
      fail(`${name}: 정규화 자기검증 실패 — 픽셀 상이율 ${(checkA.ratio * 100).toFixed(2)}% (${checkDir}/${name}.diff.png)`);
    }
    normalized = (await trimViewBox(page, normalized))?.svg || normalized;
    // 글자 밴드는 트림 후 최종 좌표계 기준으로 검사 (트림은 실크기를 키우는 방향).
    // 하한 = HARD(빌드 중단), 상한 = WARN(5단계 출생 강도).
    const scanA = scanLabelPt(normalized, widthKey);
    const floorsA = fontFloorViolations(scanA);
    if (floorsA.length) fail(`${name}: 글자 크기 하한 위반 — ${floorsA.join("; ")} (bf.width=${widthKey})`);
    // W7 배치 높이 상한 — 초과 시 폭 비례 축소를 결정(metrics.fit), 하한 충돌이면 여기서 반려
    const fitA = figFitReport(scanA, { name });
    for (const l of fitA.lines) console.log(l);
    // 7단계 HARD — 역할·대비. 트림 후 최종 좌표계에서 재고, 위반이면 이 도해를 반려한다.
    const paintA = labelPaintReport(await measureLabelPaint(page, normalized), scanA,
      { name, kind, widthKey });
    for (const l of paintA.lines) console.log(l);
    if (paintA.violations.length) {
      fail(`${name}: 도해 라벨 역할·대비 위반 ${paintA.violations.length}건 — ${paintA.violations.join("; ")}`);
    }
    const reportA = labelBandReport(scanA, { name, kind, widthKey, cacheKey: hashA });
    reportA.metrics.labelPaint = paintA.metrics;
    reportA.metrics.fit = fitA.metrics;
    const bandA = emitBand(reportA, outMetricsA);
    // 8단계 승격: enforce:true인 스타일에서 상한 위반(과 검사 꺼짐)은 그 도해의 반려다.
    // metrics는 emitBand가 이미 썼고 SVG는 아직 안 썼다 — 반려된 도해가 캐시에 남지 않는다.
    if (BAND_ENFORCE && (bandA.violated || bandA.off)) {
      fail(`${name}: 라벨 밴드 상한 ${bandA.off ? `검사 꺼짐 — ${bandA.off}` : `위반 — ${bandA.metrics.maxPt}pt = 본문 ${bandA.metrics.bodyPt}pt × ${bandA.metrics.ratio} > 상한 ${bandA.metrics.maxRatio}× (${bandA.metrics.capPt}pt)`} (styles/${style} labelBand.enforce=true)`);
    }
    writeFileSync(outSvgA, `<!--bf:authored=sha256:${hashA}-->\n${normalized}`);
    writeFileSync(outLabelsA, JSON.stringify(labelsA, null, 2));
    rendered++;
    if (bandA.violated) bandWarns++;
    console.log(`${name}: OK (authored) ${labelsA.length} labels, diff ${(checkA.ratio * 100).toFixed(2)}%, `
      + `${bandSummary(bandA.metrics)}, ${Date.now() - tA}ms`);
    continue;
  }

  let dsl = Array.isArray(sidecar.dsl) ? sidecar.dsl.join("\n") : sidecar.dsl;
  if (typeof dsl !== "string" || !dsl.trim().startsWith("infographic ")) {
    fail(`${name}: dsl은 'infographic <template>'로 시작하는 문자열(또는 줄 배열)`);
  }
  // AntV는 미지 템플릿명을 조용히 기본 템플릿으로 폴백한다(실측) — 오타 침묵 통과 차단
  const tplName = dsl.trim().split(/\s+/)[1];
  if (!getTemplate(tplName)) {
    fail(`${name}: 미지 템플릿 '${tplName}' — infographic-creator 스킬의 템플릿 목록 참조`);
  }
  // 실측 원장 사전 차단 (references/diagram-ledger.json). **차단 사유는 원장이 말한다** —
  // v1은 사유가 "8pt 하한 도달 불가" 하나였지만 v2에서 축이 넷으로 늘었고(하한 축 차단은
  // 6단계 급수 강제로 근거를 잃어 0건이 됐다), 코드가 사유를 하드코딩하면 원장과 갈라진다.
  const blockedPrefix = ledger.blocked_prefixes.find((p) => tplName.startsWith(p));
  if (blockedPrefix) {
    const row = (ledger.blocked || []).find((b) => b.template === blockedPrefix) || {};
    const ok = (ledger.measurements || []).filter((m) => m.verdict === "ok").map((m) => m.template);
    fail(`${name}: 템플릿 '${tplName}'은 실측 원장(references/diagram-ledger.json)에서 차단`
      + `${row.axis ? ` — 축 ${row.axis}` : ""}${row.evidence ? ` · ${row.evidence}` : ""}`
      + `${row.reason ? `\n  사유: ${row.reason}` : ""}`
      + `\n  대안(원장 verdict=ok): ${ok.slice(0, 6).join(" · ") || "sequence-timeline-simple"}`);
  }
  const wantIcons = bf.icons === true;
  if (wantIcons && !dg.iconsAllowed) fail(`${name}: 이 스타일(${style})은 icons 미허용`);
  if (!wantIcons) dsl = stripIconLines(dsl);
  const dslBase = dsl;
  // AntV에 넘기는 팔레트는 **knockout 안전 슬롯만**(antvPaletteChannel 참조) — 밝은
  // fill/stroke 슬롯이 배지 채움으로 순환하면 백색 라벨이 반드시 대비 미달이 된다.
  // 이 값은 dsl 문자열에 그대로 박히므로 캐시 해시(:hash)가 자동으로 정확히 무효화한다.
  const antvPalette = antvPaletteChannel(palette);
  dsl = applyTheme(dslBase, antvPalette, null); // 해시 입력 = 주입 이전의 결정론적 DSL

  const hash = createHash("sha256")
    // scale: 6단계 주입 정책 지문. **dsl 트랙에만** 실어 authored 캐시를 흔들지 않는다.
    .update(JSON.stringify({ dsl, width: widthKey, icons: wantIcons, gate: gateParams(widthKey), scale: labelScaleHash(), v: CONVERTER_VERSION }))
    .digest("hex");
  const outSvg = path.join(assetsDir, `${name}.svg`);
  const outLabels = path.join(assetsDir, `${name}.labels.json`);
  const outMetrics = path.join(assetsDir, `${name}.metrics.json`);
  if (existsSync(outSvg) && existsSync(outLabels) && metricsKeyMatches(outMetrics, hash)) {
    const head = readFileSync(outSvg, "utf8").slice(0, 120);
    if (head.includes(`bf:dsl=sha256:${hash}`)) {
      skipped++;
      const m = replayBand(outMetrics, name);
      console.log(`${name}: cache hit — skip (${bandSummary(m)})`);
      continue;
    }
  }

  const t0 = Date.now();
  // ---- 라벨 급수 강제 (6단계) ----
  // 0회차: 무주입 밀착 트림 → vbW0·scalePt0 실측(= 전후 비교의 "전").
  // 1회차: 목표pt/scalePt0을 역할별로 주입 + 하드코딩 급수 클램프 → 폭 프레임을 vbW0로 고정.
  //        프레임이 고정이므로 pt/u가 보존되어 목표 pt에 **한 방에** 맞는다.
  // 2회차(예외): 폭이 프레임을 넘겨(라벨이 오히려 커진 경우) pt/u가 바뀐 때만 1회 보정.
  const plan = labelScalePlan();
  let raw, rawUsed, converted, convertedPreTrim, labels, scan;
  let inject = null, scalePtEst = null, frameW = null, tightW = null, nativeClamped = 0, passes = 0, pre = null;
  const iterLog = [];
  for (let iter = 0; ; iter++) {
    passes = iter + 1;
    raw = await ssrWithRetry(inject ? applyTheme(dslBase, antvPalette, inject) : dsl, name);
    if (wantIcons) {
      const symbols = (raw.match(/<symbol\b/g) || []).length;
      if (!symbols) fail(`${name}: icons:true인데 <symbol> 0개 — 아이콘 API 미도달(오프라인?). 조용한 탈락 금지`);
    }
    if (!browser) {
      browser = await chromium.launch();
      page = await browser.newPage({ viewport: { width: 1600, height: 1200 }, deviceScaleFactor: 2 });
    }
    // 테마 미도달 하드코딩 급수(배지)는 변환 **전** raw에서 밴드 안으로 클램프한다.
    rawUsed = raw;
    nativeClamped = 0;
    if (plan && scalePtEst) {
      const c = clampNativeText(raw, plan, scalePtEst);
      rawUsed = c.svg; nativeClamped = c.count;
    }
    let convertedRaw;
    try {
      ({ svg: convertedRaw, labels } = await convertForeignObjectText(page, rawUsed, FONT_DIR));
    } catch (e) {
      fail(`${name}: ${e.message.replace(/^.*Error: /s, "").split("\n")[0]}`);
    }
    if (!labels.length) fail(`${name}: 변환 후 텍스트 줄 0개 — DSL에 라벨이 없거나 변환 실패`);
    converted = sortDefsSymbols(convertedRaw);
    if ((converted.match(/<foreignObject/g) || []).length) fail(`${name}: foreignObject 잔존`);
    convertedPreTrim = converted;
    const trimmed = await trimViewBox(page, converted, frameW);
    converted = trimmed?.svg || converted;
    tightW = trimmed ? r3(trimmed.tightW) : null;
    scan = scanLabelPt(converted, widthKey);
    const pts = scan.sizes.map((s) => s.pt).filter((p) => typeof p === "number" && isFinite(p));
    const maxPt = pts.length ? Math.max(...pts) : null, minPt = pts.length ? Math.min(...pts) : null;
    iterLog.push({ pass: iter, inject, frameW: r3(frameW), contentW: tightW, nativeClamped, viewBoxW: r3(scan.vbW),
      ptPerUnit: scan.scalePt === null ? null : Math.round(scan.scalePt * 1e5) / 1e5,
      minPt: r3(minPt), maxPt: r3(maxPt) });
    if (iter === 0) pre = { viewBoxW: r3(scan.vbW), minPt: r3(minPt), maxPt: r3(maxPt),
      ratio: plan ? r3(maxPt / plan.bodyPt) : null };
    if (!plan || scan.scalePt === null || !pts.length) break;      // 주입 불가 — 종전 동작
    const inBand = maxPt <= plan.capPt + BAND_TOL_PT && minPt >= plan.floorPt - BAND_TOL_PT;
    // 이미 밴드 안이면 손대지 않는다 — **단, 그 판단이 타당성 검증된 maxRatio에 기댈 때만**.
    // 대역 밖 극대값(999)은 `inBand`를 항상 참으로 만들어 주입을 통째로 껐다(W5 K3 실측:
    // 「급수 강제」 로그 부재). 지금은 대역 검사가 렌더 전에 죽이므로 이 가드는 도달 불가에
    // 가깝지만, 스킵의 근거를 **검증된 값**에 명시적으로 묶어 두는 쪽이 계약이 분명하다.
    if (iter === 0 && inBand && MAXRATIO_VALIDATED) break;
    if (inject && inBand) break;                                   // 목표 달성
    if (iter >= LABEL_SCALE_MAX_ITER) break;                       // 반복 상한 — 남은 초과는 WARN이 말한다
    // 프레임을 고정하므로 다음 회차 pt/u = 이번 회차 pt/u. 목표 pt를 그대로 나누면 정확히 맞는다.
    // (0회차는 밀착 트림 폭이 곧 프레임이 되고, 이후 보정 회차는 그때의 실측 폭을 프레임으로 갱신.)
    frameW = scan.vbW;
    scalePtEst = scan.scalePt;
    const next = injectFromT(plan, plan.titlePt / scalePtEst);
    if (injectEq(inject, next)) break;                             // 고정점 도달(더 돌려도 같은 값)
    inject = next;
  }

  // pixelSelfCheck는 **최종 회차의** raw(클램프 반영) ↔ 변환본(트림 전)을 비교한다 —
  // 클램프를 변환 전에 걸었으므로 이 자기검증은 여전히 "fo2text 변환이 외형을 보존했는가"다.
  const check = await pixelSelfCheck(browser, rawUsed, convertedPreTrim, FONT_DIR, path.join(checkDir, name));
  if (check.ratio > PIXEL_TOLERANCE) {
    fail(`${name}: 변환 자기검증 실패 — 픽셀 상이율 ${(check.ratio * 100).toFixed(2)}% > ${PIXEL_TOLERANCE * 100}% (${checkDir}/${name}.diff.png 확인)`);
  }
  // 글자 밴드는 트림 후 최종 좌표계 기준으로 검사 (트림은 실크기를 키우는 방향).
  // 하한 = HARD(빌드 중단), 상한 = WARN(5단계 출생 강도).
  const floors = fontFloorViolations(scan);
  if (floors.length) fail(`${name}: 도해 내 글자 크기 하한 위반 — ${floors.join("; ")} (bf.width=${widthKey} 기준)`);
  // W7 배치 높이 상한 — 최종(트림 후) 좌표계에서 판정. 6단계 주입이 폭 프레임을 고정하므로
  // 세로 리스트 템플릿의 종횡비는 주입 후에도 남는다 — 넘치면 폭 축소, 하한 충돌이면 반려.
  const fitD = figFitReport(scan, { name });
  for (const l of fitD.lines) console.log(l);
  // 팔레트 미도달 증거색(HARD) — 벤더 폴백 `#ff356a`가 산출에 남으면 그 요소에는
  // 스타일 팔레트가 닿지 않은 것이다. 템플릿 자체의 결함이므로 처방은 템플릿 교체다.
  const vendorAliens = vendorFallbackColors(converted, palette);
  if (vendorAliens.length) {
    fail(`${name}: AntV 벤더 폴백색 ${vendorAliens.join(", ")} 잔존 — 이 템플릿('${tplName}')의 일부 요소에 `
      + `스타일 팔레트가 도달하지 않는다(theme.palette 미소비 컴포넌트). 팔레트 강제가 그 지점에서 뚫리므로 `
      + `원장 verdict=ok 템플릿으로 교체할 것`);
  }
  // 7단계 HARD — 역할·대비. 트림 후 최종 좌표계에서 재고, 위반이면 이 도해를 반려한다.
  const paintD = labelPaintReport(await measureLabelPaint(page, converted), scan,
    { name, kind, widthKey });
  for (const l of paintD.lines) console.log(l);
  if (paintD.violations.length) {
    fail(`${name}: 도해 라벨 역할·대비 위반 ${paintD.violations.length}건 — ${paintD.violations.join("; ")}`);
  }
  const reportD = labelBandReport(scan, { name, kind, widthKey, scaled: !!inject, template: tplName, cacheKey: hash });
  reportD.metrics.labelPaint = paintD.metrics;
  reportD.metrics.fit = fitD.metrics;
  reportD.metrics.labelScale = plan ? {
    version: LABEL_SCALE.version, applied: !!inject, passes,
    targetPt: { title: r3(plan.titlePt), text: r3(plan.textPt), desc: r3(plan.descPt) },
    injectedUnits: inject, nativeClamped, pre,
    // frameSlack: 프레임 고정으로 생긴 오른쪽 여백 비율(= 1 − 실내용폭/프레임폭).
    // 라벨을 줄이면 그림이 명목 폭을 다 채우지 않는다 — 8단계 원장의 "템플릿·폭 적합" 축 입력.
    frameW: r3(frameW), contentW: tightW,
    frameSlack: frameW && tightW ? r3(1 - tightW / frameW) : 0,
    iterations: iterLog,
  } :{ version: LABEL_SCALE.version, applied: false, passes, reason: "labelBand.maxRatio 또는 body_pt 미선언", pre, iterations: iterLog };
  const bandD = emitBand(reportD, outMetrics);
  // 8단계 승격 — authored 트랙과 같은 자리, 같은 강도. SVG를 쓰기 전에 죽는다.
  if (BAND_ENFORCE && (bandD.violated || bandD.off)) {
    fail(`${name}: 라벨 밴드 상한 ${bandD.off ? `검사 꺼짐 — ${bandD.off}` : `위반 — ${bandD.metrics.maxPt}pt = 본문 ${bandD.metrics.bodyPt}pt × ${bandD.metrics.ratio} > 상한 ${bandD.metrics.maxRatio}× (${bandD.metrics.capPt}pt) · 템플릿 '${tplName}'`} (styles/${style} labelBand.enforce=true)`);
  }

  writeFileSync(outSvg, `<!--bf:dsl=sha256:${hash}-->\n${converted}`);
  writeFileSync(outLabels, JSON.stringify(labels, null, 2));
  rendered++;
  if (bandD.violated) bandWarns++;
  if (inject) {
    console.log(`${name}: 라벨 급수 강제 — 목표 title/text/desc `
      + `${r3(plan.titlePt)}/${r3(plan.textPt)}/${r3(plan.descPt)}pt · 주입 `
      + `${inject.title}/${inject.text}/${inject.desc}u · 배지 등 하드코딩 클램프 ${nativeClamped}건 · `
      + `${passes}회 수렴 · 전 ${pre.minPt}~${pre.maxPt}pt(×${pre.ratio}) → 후 `
      + `${bandD.metrics.minPt}~${bandD.metrics.maxPt}pt(×${bandD.metrics.ratio}) · `
      + `프레임 ${r3(frameW)}u 고정(pt/u 보존), 실내용 ${tightW}u — 오른쪽 여백 `
      + `${((bandD.metrics.labelScale.frameSlack || 0) * 100).toFixed(1)}%`);
  }
  console.log(`${name}: OK ${labels.length} labels, diff ${(check.ratio * 100).toFixed(2)}%, `
    + `${bandSummary(bandD.metrics)}, ${Date.now() - t0}ms`);
}

if (browser) await browser.close();
console.log(`diagrams done: ${rendered} rendered, ${skipped} cached`
  + (bandWarns ? ` — 라벨 밴드 상한 WARN ${bandWarns}건(재렌더분 기준)` : ""));
