#!/usr/bin/env python3
"""WCAG 산술 이식본 동치 검증 — `scripts/wcag.mjs` ↔ `scripts/g16_tokens.py`.

왜 이 테스트가 존재하는가: 도해 렌더의 대비 HARD는 node(`render_diagrams.mjs`)에서
돌고 게이트(G16-CONTRAST·G14-C)는 python에서 돈다. mjs는 python을 import할 수 없어
`contrast_floor`·`is_bold_font`·상대휘도/대비 산식이 **두 벌 복제**돼 있다. 두 구현이
갈리면 같은 도해를 두 게이트가 다르게 판정하는데, G16-SYNC는 스타일 토큰 ↔ theme.css만
보므로 이 어긋남을 **볼 수단이 없다**. 그래서 동치를 자산으로 고정한다.

축 3개:
  ① contrast_floor(pt, bold) — WCAG large-text 경계(14/18pt)를 포함한 격자 전수
  ② is_bold_font(name)       — 토큰 판정 규칙(SemiBold=600, Blackriver≠black, Boldoni≠bold,
                               수치 토큰 우선)의 실제 함정 사례 전수
  ③ contrast_ratio(fg, bg)   — 실팔레트 색쌍(스타일 팩 전량 × 백색·상호)에서 1e-12 이내

Usage: python3 tests/test_wcag_parity.py
"""
import json
import subprocess
import sys
from itertools import combinations
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "scripts"))

import g16_tokens as g16  # noqa: E402

# ---- ① 하한: 경계(14·18)와 그 ±ε, 실제 도해 라벨 급수대(8~24pt) ----
PT_CASES = [0, 1, 7.9, 8, 8.56, 9.5, 10.5, 10.925, 12, 13.99, 14, 14.01, 15.9, 17.99,
            18, 18.01, 24, 40, 126]
# ---- ② 굵기: g16_tokens.is_bold_font docstring이 지목한 함정 전량 ----
FONT_CASES = [
    "", "Pretendard", "Pretendard-Regular", "Pretendard-Medium", "Pretendard-SemiBold",
    "Pretendard-DemiBold", "Pretendard-Bold", "Pretendard-ExtraBold", "Pretendard-UltraBold",
    "Pretendard-Black", "Pretendard-Heavy", "Pretendard-300", "Pretendard-400",
    "Pretendard-600", "Pretendard-700", "Pretendard-950", "Pretendard-1000", "Pretendard-2",
    "Blackriver-Regular", "Boldoni-Light", "NotoSansKR-Bd", "AppleSDGothicNeo-Bold",
    "ABCBold", "semibold", "SEMIBOLD", "demi bold", "bold", "BOLD", "heavy", "black",
    "Times-BoldItalic", "Font Awesome 5 Free-Solid-900",
]

NODE_SRC = r"""
import { contrastFloor, isBoldFont, contrastRatio } from "%s";
// 입력은 환경변수로 넘긴다 — `node -e`의 argv 배치는 버전에 따라 흔들린다.
const input = JSON.parse(process.env.BF_PARITY_PAYLOAD);
console.log(JSON.stringify({
  floor: input.pts.flatMap((pt) => [contrastFloor(pt, false), contrastFloor(pt, true)]),
  bold: input.fonts.map((f) => isBoldFont(f)),
  ratio: input.pairs.map(([a, b]) => contrastRatio(a, b)),
}));
"""


def palette_pairs():
    """실팔레트 색쌍 — 스타일 6종의 diagram.palette 전량 + 백색, 상호 조합."""
    cols = {"#ffffff"}
    for tok in (SKILL / "styles").glob("*/tokens.json"):
        d = json.loads(tok.read_text(encoding="utf-8"))
        cols.update((d.get("diagram") or {}).get("palette") or [])
    rgb = sorted({tuple(int(c[1 + 2 * i:3 + 2 * i], 16) for i in range(3)) for c in cols})
    return [[list(a), list(b)] for a, b in combinations(rgb, 2)]


def main():
    pairs = palette_pairs()
    payload = {"pts": PT_CASES, "fonts": FONT_CASES, "pairs": pairs}
    src = NODE_SRC % (SKILL / "scripts" / "wcag.mjs")
    import os
    env = dict(os.environ, BF_PARITY_PAYLOAD=json.dumps(payload))
    r = subprocess.run(["node", "--input-type=module", "-e", src],
                       capture_output=True, text=True, env=env)
    if r.returncode != 0:
        print(f"FAIL  node 실행 실패 — {r.stderr.strip()[:400]}")
        sys.exit(1)
    got = json.loads(r.stdout)

    bad = []
    want_floor = [v for pt in PT_CASES for v in (g16.contrast_floor(pt, False),
                                                 g16.contrast_floor(pt, True))]
    for i, (w, g) in enumerate(zip(want_floor, got["floor"])):
        if w != g:
            bad.append(f"contrast_floor #{i} (pt={PT_CASES[i // 2]}, bold={bool(i % 2)}): py {w} vs mjs {g}")
    want_bold = [g16.is_bold_font(f) for f in FONT_CASES]
    for f, w, g in zip(FONT_CASES, want_bold, got["bold"]):
        if w != g:
            bad.append(f"is_bold_font('{f}'): py {w} vs mjs {g}")
    for (a, b), g in zip(pairs, got["ratio"]):
        w = g16.contrast_ratio(tuple(a), tuple(b))
        if abs(w - g) > 1e-12:
            bad.append(f"contrast_ratio({a},{b}): py {w!r} vs mjs {g!r}")

    n = len(want_floor) + len(want_bold) + len(pairs)
    for m in bad:
        print(f"  {m}")
    print(f"{'FAIL' if bad else 'PASS'}  wcag.mjs ↔ g16_tokens.py 동치 — "
          f"{n - len(bad)}/{n} 일치 (하한 {len(want_floor)} · 굵기 {len(want_bold)} · 대비 {len(pairs)})")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
