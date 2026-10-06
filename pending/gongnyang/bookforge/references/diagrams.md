# 도해 계약 (정본) — 사이드카 2트랙 (antv DSL / authored SVG)

본문 도해는 두 트랙 중 하나로 만든다: ① **antv** — 인포그래픽형 요점 시각화는 AntV
Infographic DSL로 선언(직접 그리지 않음), ② **authored** — 기술도해(시퀀스·상태머신·
ER·스위밍레인 등 AntV 미커버 11계열)는 에이전트가 SVG를 직접 그린다(§authored 트랙).
양쪽 다 빌드(P1.5)가 정규화해 `assets/fig-NN.svg` + `labels.json`을 산출한다.
antv 트랙의 핵심 우회: AntV 원본 출력은 텍스트가 `<foreignObject>`라 Typst(usvg)에서
**에러 없이 텍스트만 전멸**하므로 네이티브 `<text>`로 변환한다(fo2text).

## 파일 3점 세트 (이름 일치 강제)

```
<book_dir>/diagrams/fig-01.json      ← 콘텐츠가 작성 (DSL 사이드카)
<book_dir>/assets/fig-01.svg         ← 빌드 산출 (직접 만들지 않는다)
<book_dir>/assets/fig-01.labels.json ← 빌드 산출 (G13 대조 정본)
<book_dir>/assets/fig-01.metrics.json ← 빌드 산출 (라벨 급수·도장 실측 — 밴드 판정 근거이자
                                          diagram-ledger 재도출 입력. antv는 `template` 축을 갖는다)
chapters/ch-NN.md 안: ![캡션](../assets/fig-01.svg "출처: …")   ← 단독 문단
```

## 사이드카 스키마

```json
{
  "kind": "antv",
  "bf": { "width": "full", "icons": false },
  "dsl": [
    "infographic sequence-ascending-steps",
    "data",
    "  title 단계 제목",
    "  sequences",
    "    - label 1단계",
    "      desc 설명 문장",
    "    - label 2단계"
  ]
}
```

- `kind`: `"antv"`(기본 — 생략 가능) | `"authored"`. authored면 `dsl` 대신
  `diagrams/fig-NN.svg`(에이전트가 직접 그린 SVG 소스)가 입력이다 — 아래 §authored 트랙.
- `dsl`: (antv 전용) 문자열 또는 줄 배열. 첫 줄은 반드시 `infographic <template-name>`.
  템플릿 문법은 infographic-creator 스킬(~/.claude/skills/infographic-creator)이 정본.
- `bf.width`: `full`(기본) | `twothirds`. **검사와 실렌더의 단일 진리원**이다 —
  지면에 실제로 앉는 물리 폭이면서 동시에 도해 라벨 급수 검사(하한 `minFontPt` HARD ·
  상한 `labelBand.maxRatio`)가 pt를 환산하는 기준 폭이고, **둘은 같은 값이어야 한다**.
  이 둘이 갈라지면 검사는 지면에 없는 폭을 재게 된다: W5 이전에는 선언폭이 실렌더폭과
  최대 1.128배(essay 78 vs 88) 어긋나 하한이 과엄격하게, business는 1.072배 느슨하게
  돌았다. 값은 스타일 팩의 `tokens.json diagram.widths.<키>`(mm) 하나뿐이고 CSS·typst는
  파생이다. HTML 트랙은 빌더가 `twothirds`를
  `<figure class="svgfig twothirds">`로 발행하고 theme.css가 `$fig_full_mm`·`$fig_twothirds_mm`
  치환으로 그 mm를 받는다(G16-SYNC widths 축이 배선을 HARD로 지킨다).
  Typst 트랙은 `md2typ.py`가 사이드카를 읽어 `#bf-fig(..., width: Nmm)`으로 같은 mm를 발행한다
  (`full`도 수치로 발행한다 — `bf-fig` 기본값 `width: 100%`를 그대로 두면 판면폭이 제1의
  진리원이 되고 tokens는 그것을 추정하는 제2의 값으로 남는다). 여기서도 같은 축이
  `widths.full == theme.typ 판면폭(trim.w − margin.left − margin.right)`을 HARD로 대조한다.
- `bf.icons`: 기본 `false`. `true`는 HTML 트랙 스타일(insight·magazine)에서만 허용되며
  **네트워크가 필요**하다(아이콘 API). 렌더러가 요청 아이콘 수와 SVG `<symbol>` 수를
  대조해 조용한 탈락을 차단한다. `false`면 DSL의 `icon` 줄을 자동 제거한다.

## 스타일이 강제하는 것 (콘텐츠가 지정해도 덮어쓴다)

- **팔레트**: `styles/<style>/tokens.json`의 `diagram.palette`. DSL의 `theme` 블록은
  빌드가 제거·재작성한다. `book.json`의 `brand`가 있으면 강조색(1번)만 교체.
- **라벨 급수 밴드**: 하한과 상한이 **다른 키·다른 강도**다.
  - 하한 `diagram.minFontPt`(전 스타일 8pt) — `bf.width` 물리 폭으로 환산해 위반 시
    렌더가 **실패(HARD)**한다. 대응은 라벨 축약 또는 항목 수 축소(글자 확대 아님).
  - 상한 `diagram.labelBand.maxRatio`(전 스타일 1.2 [하우스]) — 라벨 최대 pt가
    `body_pt × maxRatio`를 넘으면 위반이고, **강도는 같은 블록의 `labelBand.enforce`가 정한다**:
    `true`면 그 도해가 **실패(HARD)**하고 `false`면 WARN이다. 6스타일 전부 `true`
    (W5 8단계 승격 — 승격 조건은 "그 스타일 코퍼스 위반 0"이었고, 스타일별 근거는
    각 `tokens.json`의 `_labelBand_evidence`에 실측과 함께 남아 있다). `enforce`는 JSON bool만
    허용하며 부재·문자열은 G16-SYNC HARD FAIL이다(`contrast_contract.enforce`와 같은 계약 —
    문자열 `"false"`가 truthy로 읽혀 강제가 반대로 켜지는 구멍을 막는다).
    대응 방향이 하한과 정반대다: **라벨 font-size 축소 또는 viewBox 확대**
    (폭 확대·글자 확대는 위반을 키운다). 축척은 상·하한을 함께 옮기므로, 도해 내부
    최대/최소 활자비가 `(body_pt × maxRatio) ÷ minFontPt`를 넘으면 어떤 폭으로도 두 술어를
    동시에 만족할 수 없다 — 그때는 라벨 간 상대 급수를 좁혀야 한다(렌더러가 그 진단을 낸다).
  - **AntV DSL 트랙은 렌더러가 자동으로 맞춘다(6단계).** 사이드카를 고칠 필요가 없다 —
    빌드가 테마에 역할별 `font-size`(케밥 표기)를 주입해 title `body_pt×1.15` ·
    label/value `×1.0` · desc `×0.9`(단, `minFontPt×1.07` 하한)로 강제하고, 테마가 닿지
    않는 템플릿 하드코딩 급수(단계번호 배지 등)는 변환 전 원본 SVG에서 같은 밴드 안으로
    클램프한다. 급수만 줄이면 트림 폭이 함께 줄어 pt/u가 커지므로(= 글자는 안 줄고 도형만
    커진다) **폭 프레임을 무주입 실측값으로 고정**한다 — 도형은 지면에서 원래 크기 그대로이고
    글자만 줄며, 남는 폭은 오른쪽 여백이 된다(`metrics.labelScale.frameSlack`).
  - 도해마다 실측이 `assets/fig-NN.metrics.json`(급수 전량·min/max pt·본문 대비 비)으로 남는다.
    `labels.json` 스키마는 건드리지 않는다(G13 무영향).
  - `labelBand.maxRatio`·`body_pt` 중 하나라도 없으면 상한 검사가 꺼지고, **꺼졌다는 사실이
    출력된다** — 미선언이 위반보다 조용해서는 안 된다. `enforce: true`인 스타일에서는
    **꺼짐 자체가 반려**다(승격 선언이 아무것도 뜻하지 않게 되므로).
- **배치 높이 상한**: `diagram.maxHeightMm`(스타일별 판면·캡션 실측 파생 — 근거는 각
  `tokens.json`의 `_maxHeightMm_evidence`). 도해의 배치 높이 `widthMm × (viewBox H/W)`가
  이 상한을 넘으면 figure(도해+캡션)가 한 면에 못 들어간다 — HTML 트랙은
  `break-inside: avoid`를 지킬 수 없어 면 경계에서 도해를 **쪼개고**(실증: insight 세로
  셰브런 254.8mm가 p5/p6로 분단 출하), typst 트랙은 판면 아래로 넘친다. 렌더러가 트림 후
  최종 좌표계에서 배치 높이를 사전 산출해:
  - 상한 이내면 그대로(`metrics.fit.verdict: "ok"`).
  - 초과면 **폭을 비례 축소**해 한 면에 넣는다(`"shrunk"` — 축소 폭 `fit.widthMm`를
    build_html(figure 인라인 width)·md2typ(`#bf-fig width:`)가 전사한다. 라벨 실효 pt는
    폭에 비례해 함께 줄지만 상한(cap) 방향으로는 언제나 안전하다).
  - **축소 허용 한계는 라벨 하한에서 역산**된다: 필요 축소 `k = maxHeightMm ÷ 배치높이`가
    허용 하한 `k_min = minFontPt ÷ 최소 라벨 pt`보다 작으면 자동 축소가 하한 HARD를
    깨므로 그 도해는 **반려(HARD)**다 — 처방은 세로 항목 수 축소 또는 가로 배치 템플릿
    재작성이고, 진단이 수용 가능한 최대 배치 높이(`maxHeightMm ÷ k_min`)를 말해 준다.
  - `maxHeightMm`는 필수 계약이다(`labelBand`와 같은 취급 — 부재·비수치·재단 높이 이상은
    렌더 시동 실패). 값이 바뀌면 그 스타일 도해가 전건 재판정된다(캐시 해시 파라미터).
  - 최종 PDF에서는 **G17-FIGFIT**이 이중 방어한다(qc_gate) — ① 도해 라벨 전부를 품는
    본문 단일 면 부재(면 분단) ② 도해 라벨 라인이 판면 세로 범위 밖 ③ 배치 높이 정적
    재산출 초과. 뮤테이션 M19가 렌더 층(반려/축소/대조군)과 게이트 층(분단/초과/대조군)의
    감도를 회귀 자산으로 고정한다.
- **라벨 색의 역할과 대비**: 렌더 후 SVG를 실좌표에서 다시 재 **HARD**로 판정한다(7단계).
  - ① 역할 — 글자의 fill은 `diagram.palette_roles`가 `label`이라 선언한 슬롯이거나
    백색 knockout(`#ffffff`)이어야 한다(브랜드 치환을 반영한 해석 팔레트 기준). 채움용
    틴트·괘선색을 글자로 쓰면 반려된다. AntV 트랙의 무채색 램프는 팔레트 밖이라 역할표가
    말하지 않으므로 통과시키고 ②에 맡긴다 — 팔레트 밖 **유채색** 글자는 양 트랙 모두 위반.
  - ② 대비 — 글자색 × **그 글자 밑에 실제로 깔린 색**의 대비가 `contrast_floor(pt, bold)`
    (WCAG 2.x: 18pt 이상 또는 14pt 이상 볼드면 3.0, 그 외 4.5) 이상이어야 한다. 배경은
    **문서 순서상 앞서 그려진 도형**을 알파 합성해 결정한다(8% 틴트 띠 같은 반투명 면이
    실제로 만드는 색을 그대로 본다). 실배경 산출 규칙 넷 — 전부 **낙관하지 않는 방향**이다:
    - **표본은 글자 bbox 가로 5점**(10/30/50/70/90%)이고 판정은 그 **최악값**이다. 중심점
      1표본은 경계에 걸친 라벨(오른쪽 절반만 어두운 면 위)을 통째로 놓쳤다.
    - **`fill:none` + 굵은 stroke 도형도 배경 후보**다(`isPointInStroke`). 지면에서 그
      stroke는 실색 띠이고, 한 요소 안에서 stroke는 fill 위에 얹힌다.
    - **`url(#…)` 그라데이션은 stop 전량을 해석**해(`stop-opacity` 포함) stop 하나마다
      배경 후보를 만들고 그중 최악 대비를 쓴다. 버리면 그 면이 판면 백색으로 둔갑한다.
    - **해석 불가한 페인트서버**(pattern·미존재 참조) 위 글자는 배경을 산출할 수 없으므로
      통과가 아니라 **판정 불가로 반려**한다.
  - **백색 knockout에 대비 면제는 없다.** ①이 백색을 통과시키는 것은 역할표가 백색을
    말하지 않는다는 뜻일 뿐이고, 밝은 면 위의 백색 글자는 ②가 반려한다.
  - **AntV 벤더 폴백색 `#ff356a`는 HARD 반려다.** 이 색은 번들의 `colorPrimary` 미도달
    폴백(`createBaseTheme`·`getColorPrimary`·화살표 컴포넌트 기본 prop 등 8지점)이므로,
    산출에 남았다는 것은 **그 요소에 스타일 팔레트가 도달하지 못했다**는 증거다. antv
    트랙에 `alienColors`(strict)를 걸지 않는 이유는 템플릿이 팔레트 색에서 정당하게
    파생한 틴트를 쓰기 때문이고(실측 `#1e7aad` → `#78afce`), 그래서 "팔레트 밖 색 전량"이
    아니라 **팔레트가 닿지 않았음을 스스로 증명하는 색**만 잡는다. 처방은 템플릿 교체다.
  - AntV 트랙은 `theme.palette`가 **항목별 강조 채움**(배지·화살표) 채널이라, 백색을 얹을 수
    없는 밝은 슬롯이 들어가면 항목이 그 슬롯에 닿는 순간 반드시 대비 미달이 된다. 그래서
    빌드는 이 채널에 **knockout 안전한 슬롯만**(0번 브랜드 슬롯은 항상 유지) 넘긴다 —
    팔레트 값은 그대로다. 0번이 밝아서 위험하면 조용히 빼지 않고 ②가 소리내어 반려한다.
  - 실측은 `assets/fig-NN.metrics.json`의 `labelPaint`(글자별 fill·역할·실배경·대비·pt·bold,
    knockout 수, 최악 대비)로 남고, 콘솔 요약에도 최악 대비가 나온다.
  - 대비 산술은 `scripts/wcag.mjs`이며 `scripts/g16_tokens.py`의 **복제본**이다 — 동치는
    `tests/test_wcag_parity.py`가 어서션한다(값을 고치면 양쪽을 함께 고칠 것).
- **폰트**: Pretendard 고정 (fo2text가 실측·방출).

## 금지 사항

- **회전·세로쓰기 라벨 금지** — fo2text가 감지 시 즉시 실패한다.
- **템플릿명 오타 주의** — AntV는 미지 템플릿을 조용히 기본형으로 폴백하지만,
  빌드가 벤더 번들 카탈로그로 실명 검증해 미지명은 즉시 실패시킨다. **계열 이름은
  템플릿이 아니다**: `list-grid`·`sequence-snake-steps`·`sequence-roadmap-vertical` 같은
  bare name은 문서에 자주 등장하지만 `getTemplate`이 해석하지 못한다(실제 등록명은
  `list-grid-simple`처럼 변형 접미사까지 붙은 이름이며, 번들 실측 **123종**이다).
  bare name을 쓰면 즉시 반려된다 — 원장 v1이 실측치를 그런 이름에 귀속시켜 두었던 것이
  W5 8단계 재도출의 발단이었다.
- **라벨 겹침** — SSR 박스 계산과 Pretendard 실폭의 차이로 긴 라벨이 이웃 텍스트를
  덮으면 변환기가 감지해 실패한다. 대응은 라벨 축약(글자 확대 아님).
- 산출 `assets/fig-NN.svg` 수동 편집 금지 — 첫 줄 해시가 어긋나도 캐시가 남는다.
  수정은 항상 사이드카 DSL에서, 재빌드로만.
- 도해로 수치를 새로 만들지 않는다 — 본문에 실재하는 수치·주장만 시각화 (G10 정신).
- magazine 목차 이미지맵은 장의 첫 이미지를 쓴다 — 장 첫 이미지가 도해면 사진 컷을
  먼저 배치할 것 (도해는 `<img>` 썸네일로 어울리지 않는다).

## 템플릿 선택 지침 (전량 목록은 infographic-creator 스킬)

이 표의 이름은 **전부 원장 v3에서 `verdict: ok`로 실측된 등록 템플릿**이다(계열 와일드카드가
아니라 실명 — bare name은 `getTemplate`이 해석하지 못해 즉시 반려된다).
**이 판정은 insight 팩 · full 130mm 단일 조건에서 도출됐다** — 다른 스타일·폭(예: essay 88/52mm)으로
그대로 가져오면 안 된다(아래 한계 항목 참조. 실측: 12조합 중 5조합 HARD).

| 정보 구조 | 템플릿 (원장 v3 ok, insight·130mm 기준) |
|---|---|
| 병렬 요점 | `list-column-simple-vertical-arrow` · `list-grid-simple` · `list-row-horizontal-icon-arrow` |
| 순서·단계 | `sequence-timeline-simple` · `sequence-ascending-steps` |
| 비교 | `compare-quadrant-quarter-circular` (※ `compare-swot`·`compare-binary-*-vs`는 원장 blocked) |
| 계층·구조 | `hierarchy-structure` · `hierarchy-mindmap-*-gradient-*` |
| 수치 추이 | `chart-line-plain-text` `chart-bar-plain-text` (본문 실재 수치만) |

판형이 좁은 스타일(essay 88mm)은 가로형 템플릿(`list-row-*`, 가로 타임라인)을 피한다.

### 배치 높이 저술 규범 (W7) — 도해는 캡션까지 **한 면**에 들어가야 한다

- **산식**: 배치 높이 = `widths[bf.width]` × (viewBox 높이 ÷ viewBox 폭). 이 값이
  스타일의 `diagram.maxHeightMm`(스타일별 tokens, 판면 − figure 마진 − 캡션 실측 파생)를
  넘으면 figure가 한 면에 못 들어간다 — HTML 트랙은 면 경계에서 도해가 **쪼개지고**
  (실증: insight 세로 셰브런 254.8mm → p5/p6 분단 출하), typst 트랙은 판면 아래로 넘친다.
- **허용 종횡비(vbH/vbW) 상한** = `maxHeightMm ÷ widths[bf.width]`. 전폭 기준:
  insight 1.28 · magazine 1.20 · academic 1.36 · business 1.52 · essay 1.34 · practical 1.38.
  `bf.width: twothirds`는 폭이 좁아지는 만큼 허용 종횡비가 커진다(insight 1.58) — 세로형
  구제책이지만 라벨 실효 pt도 함께 줄어드는 것을 하한 HARD가 잰다.
- **초과 시 렌더러가 자동 처리한다**: 폭 비례 축소(`metrics.fit.verdict: "shrunk"`)로 한 면에
  넣되, **축소 한계는 라벨 하한 역산**(k_min = `minFontPt` ÷ 최소 라벨 pt)이다. 필요 축소가
  그보다 크면 **반려(HARD)** — 저술자가 도해를 재작성해야 하고, 진단이 수용 가능한 최대
  배치 높이를 말해 준다. 6단계 급수 강제 직후의 전형적 라벨(하한×1.05~1.15)에서는 축소
  여유가 5~13%뿐이므로, **자동 축소를 설계 여유로 믿지 말고 종횡비를 상한 안에서 저술**하라.
- **세로 스텝형 항목 수 상한**: `list-column-simple-vertical-arrow` 실측(항목당 ≈131u +
  헤더)은 insight 전폭에서 **항목 2개까지만** 허용 종횡비 안이고 3개부터 판면을 넘는다
  (3개 ≈ 198mm > 167mm). 순서·단계가 **3개 이상이면 세로 스텝형을 쓰지 말고 가로·격자·
  순환형으로 전환**하라: `list-row-simple-horizontal-arrow` · `sequence-timeline-simple` ·
  `list-grid-simple` · `sequence-circle-arrows-indexed-card`(팔레트 틴트 정합 실측).
  `sequence-roadmap-vertical-*` 등 세로 로드맵 계열도 같은 산식으로 항목 수를 먼저 셈하라.
- 최종 PDF에서는 **G17-FIGFIT**이 분단·판면 초과를 잡는다 — 게이트에 걸렸다면 처방은
  언제나 도해 쪽(항목 수 축소·가로 전환)이지 판면 쪽이 아니다.

**템플릿 적합성의 정본은 `references/diagram-ledger.json`이다**(v3, W5 재작업 재도출). 여기에
수치를 옮겨 적지 않는다 — 두 곳이 갈리면 원장이 무의미해진다. 원장이 판정하는 축 넷:
`min_pt`(8pt 하한) · `max_ratio`(밴드 상한) · `frame_slack`(도형이 명목 폭을 채우는가) ·
`label_paint`(역할·대비). 읽을 때 알아 둘 것:

- **원장 v3는 등록 123종을 전건 판정한다**(v2는 25종·21%였다). 결과(W5 재판정 N1 반영):
  ok 87 · blocked 29 · content-sensitive 4 · palette-sensitive 3.
- **하한(8pt) 축으로 차단된 템플릿은 없다.** 6단계 라벨 급수 강제 이후 하한 미달이 0건이다.
- **차단 축은 셋이다.** ① `palette_reach`(18종) — 템플릿의 일부 요소가 `theme.palette`를
  소비하지 않아 벤더 기본색(`#ff356a`·`#1677ff`)이 지면에 남는다(실측: `sequence-snake-steps-simple`
  화살표가 청록 팔레트 책에 연분홍 픽셀을 찍는다. `sequence-snake-steps-compact-card`도 동일 결함 —
  W5 재판정 N1에서 content-sensitive 오분류를 바로잡아 여기로 옮겼다). ② `label_paint`(9종) — 백색
  knockout이 팔레트의 밝은 틴트 위에 얹히거나, 텍스트 fill이 그라데이션이거나, 템플릿이 팔레트 밖
  파생색을 글자로 쓴다. ③ `text-overlap(structural)`(2종, `chart-pie-plain-text`·
  `chart-pie-donut-plain-text`) — 라벨 1자까지 줄여도 겹침이 사라지지 않는 레이아웃 결함이라
  content-sensitive(처방=라벨 축약)로 구제되지 않는다.
- **원장 판정 조건은 insight 팩 · full 130mm 단일 조건이다.** 다른 스타일·폭에서는 이전되지
  않는다 — essay(88mm 단폭/52mm 2/3폭)에서 v3 ok 6종을 재렌더하면 12조합 중 5조합이 text-overlap
  HARD로 반려된다(`list-grid-simple`·`compare-quadrant-quarter-circular`는 두 폭 모두 반려).
  좁은 스타일에서 이 표의 이름을 쓸 때는 렌더 시 겹침 검사 결과를 반드시 확인할 것 — 표 자체는
  폭·스타일을 교차검증하지 않는다.
- **v2가 차단했던 `*-badge-card`·`*-pill-badge`·`*-candy-card-lite` 4종은 해제됐다.** v2의 근거
  `#262626 on #1e7aad = 3.201`은 채움 카드의 알파(8~12%)를 무시한 오탐이었다 — 실배경은 `#e8f1f7`,
  실대비 13.3이며 Chromium 실픽셀과 1/255 안에서 일치한다.
- **`palette-sensitive` 3종은 사전 차단하지 않는다.** insight에서 4.0~4.2로 근소 미달인데, 대비가
  `contrast(label,#ffffff) × 약 0.88`로 결정되므로 label 슬롯이 백색 대비 5.2 이상인 팔레트에서는
  통과한다 — 렌더 시 역할·대비 HARD가 스타일별로 판정한다.
- **세로형·항목 적은 템플릿은 `frame_slack`을 본다.** `sequence-timeline-simple`은 130mm에서
  여백 49%로, 도형이 명목 폭의 절반만 채운다 — `bf.width`를 `twothirds`로 내리거나 항목을 늘릴 것.

## 캐시와 오프라인

산출 SVG 첫 줄 `<!--bf:dsl=sha256:…-->`가 DSL+옵션 해시다. 일치하면 프리렌더를
건너뛰므로 **재빌드는 네트워크 없이 재현**된다(아이콘 API 재접근 불필요).
**캐시 히트 조건은 3점 세트 전부**다: SVG 첫 줄 해시 + `labels.json` 존재 +
`metrics.json`의 `cacheKey`가 같은 해시일 것. 마지막 조건이 없으면 metrics와 SVG가
갈라진다 — HARD 반려(밴드 enforce·역할·대비)는 metrics를 쓴 뒤 SVG를 쓰기 전에 죽으므로
직전 성공 SVG 옆에 실패 회차의 metrics가 남고, 소스를 되돌리면 SVG 해시는 맞아
캐시가 히트하면서 **옛 위반 판정이 재생**된다(W5 8단계에서 실측으로 잡은 오탐).
DSL·팔레트·변환기 버전, 그리고 **판정 파라미터**(해당 폭의 실검사 `widthMm` ·
`minFontPt` · `labelBand` · `maxHeightMm` · `body_pt` · `palette_roles` · 도장 판정 정책 ·
**`wcag.mjs`·`fo2text.mjs`의 내용 해시**)가 바뀌면 자동 재렌더 — 검사 기준이 바뀐 도해가 옛 캐시로
조용히 통과하는 일이 없다. DSL 트랙 해시에는 **라벨 급수 주입 정책**(역할별 배수·목표 pt)도
실린다. 이 정책은 authored 트랙 해시에 없으므로, 정책을 바꾸면 DSL 도해만 재렌더된다.

## 게이트

- **G0 (렌더 전)**: foreignObject 잔존 / `<text>` 부재 / 외부 참조(CDN) / 이미지 문단에
  텍스트 혼합 / 참조 SVG 부재 / icons:true인데 symbol 0.
- **G13 (렌더 후)**: `fig-NN.labels.json`의 렌더 줄 단위 라벨이 PDF 실텍스트에 존재.
- 실패 대응: `typeset/diagcheck/fig-NN.diff.png`(변환 자기검증 차분)를 먼저 본다.


---

## authored SVG 트랙 (v2) — 기술도해는 직접 그린다

AntV 카탈로그는 "인포그래픽형 요점 시각화"에 강하고, **UML 시퀀스·상태머신·ER·
스위밍레인·간트·레이더·벤·산점도·조직도·루프·권한 매트릭스** 같은 기술도해는 0건이다
(카탈로그 접두어 실측 — 번들 등록 123종은 list·sequence·compare·hierarchy·chart·relation 6계열뿐이다). 이 11계열은 에이전트가 SVG를 직접 그려 `diagrams/fig-NN.svg`에
두고, 사이드카를 `{"kind":"authored","bf":{"width":...}}`로 선언한다.

### 파이프라인 (antv 트랙과 동일 산출 계약)

빌드(P1.5)가 소스를 Chromium 하네스에 실측 마운트해 정규화한다:
① 폰트는 **Pretendard로 강제 베이크**(font-family 속성 재작성 — 다른 지정은 조용히 교정).
  급수도 **DOM 실측(computed)을 `<text>`·`<tspan>` 전부에 속성으로 굽는다** — `<style>`
  블록·CSS 클래스로 준 급수가 정규식 스캔의 사각지대가 되어 밴드 축과 도장 축이 같은
  글자에 다른 pt를 기록하는 이중 진리를 없앤다(표현 속성은 CSS 선언에 지므로 외형 불변)
② 렌더 실측 라벨 수집 → `labels.json` (G13 대조 정본 — antv와 동일)
③ 회전·전단 라벨 즉시 실패 ④ 텍스트 겹침 실측 감지 즉시 실패
⑤ 팔레트 강제(**strict**): `tokens.diagram.palette` + `#ffffff` 밖의 색은 **무채색이라도** 즉시 실패
  (실측: `#808080` 괘선 1줄 → `DIAGRAM FAIL: 팔레트 밖 색 #808080`). 뉴트럴 램프 허용은 antv
  트랙 전용이다 — 두 트랙의 색 계약이 다르다. `fill`/`stroke` 속성·인라인 `style`뿐 아니라
  **`stop-color`(그라데이션 스톱)·`flood-color`·`lighting-color`와 `<style>` 블록 선언**까지 훑는다
⑥ 글자 하한(minFontPt) 검사(HARD) + 상한(labelBand.maxRatio) 판정(강도는 labelBand.enforce)
  + 라벨 역할·실배경 대비 검사(HARD) ⑦ 외부 참조(CDN·원격) 즉시 실패
⑧ 원본↔정규화 pixelmatch 자기검증 ⑨ `<!--bf:authored=sha256:…-->` 해시 캐시.

### viewBox 환산 규칙 (라벨 급수 위반의 90%가 여기서 발생)

렌더 pt = `font-size(u) × 폭mm × 2.835 ÷ viewBox폭(u)`. 여기에 **상한과 하한이 함께**
걸린다 — 이전 판이 "좁게 그리고 크게 라벨하라"고만 적어 상한을 말하지 않은 것이
본문보다 큰 도해 라벨(최대 실측 본문 ×3.88)이 통과하던 공동 원인이다. 축척은 두 끝을
**같이** 옮기므로 한쪽만 보고 폭을 정하면 반대쪽이 반드시 깨진다.

**양방 공식** (`W` = `bf.width` mm, `V` = 트림 후 viewBox 폭 u, `s` = `minPt` 실 최소
font-size u, `L` = 실 최대 font-size u, `body` = `tokens.body_pt`, `cap` = `labelBand.maxRatio`):

```
하한(HARD)  s × W × 2.835 ÷ V ≥ minFontPt        → V ≤ W × 2.835 × s ÷ minFontPt
상한(HARD·enforce)  L × W × 2.835 ÷ V ≤ body × cap → V ≥ W × 2.835 × L ÷ (body × cap)
⇒ 안전 대역   W × 2.835 × L ÷ (body×cap)  ≤  V  ≤  W × 2.835 × s ÷ minFontPt
```

- 예(insight full 130mm · body 9.5pt · cap 1.20 · 하한 8pt · 라벨 10~13u):
  `130×2.835×13 ÷ 11.4 = 420u ≤ V ≤ 130×2.835×10 ÷ 8 = 460u` — **420~460u가 안전 대역**이다.
- **대역이 비면 폭으로는 못 푼다.** 대역이 성립할 조건은 `L ÷ s ≤ (body×cap) ÷ minFontPt`,
  즉 **도해 내부 활자비 ≤ 밴드 허용 내부비**(insight면 11.4 ÷ 8 = 1.425×)다. 이걸 넘으면
  viewBox를 어떻게 잡아도 두 술어를 동시에 만족할 수 없고, 처방은 폭이 아니라
  **라벨 간 상대 급수를 좁히는 것**(최대 라벨만 축소)이다. 반려 메시지가 이 수치를 직접 적어준다.
- 방향이 반대라는 점을 기억할 것: 하한 위반의 처방(viewBox 축소 = 유효 pt 확대)과
  상한 위반의 처방(viewBox 확대 = 유효 pt 축소)은 서로를 되돌린다.
- AntV(dsl) 트랙은 이 계산을 사람이 하지 않는다 — 렌더가 역할별 목표 pt(title `body×1.15` ·
  text `body×1.00` · desc `max(body×0.90, minFontPt×1.07)`)를 주입하고 폭 프레임을 고정해
  대역 안에 앉힌다. authored 트랙만 저자가 위 대역을 지켜 그려야 한다.

### 타입 라우팅 (무엇을 그릴 것인가)

| 보여줄 것 | 타입 | 트랙 |
|---|---|---|
| 시스템 구성요소 + 연결 | 아키텍처 | authored |
| 분기 있는 결정 논리 | 플로우차트 | authored |
| 행위자 간 시간순 메시지 | **시퀀스** | authored |
| 상태 + 전이 + 조건 | **상태머신** | authored |
| 엔티티 + 필드 + 관계 | **ER** | authored |
| 부서·역할 교차 프로세스(핸드오프) | **스위밍레인** | authored |
| 작업·단계의 일정 배치 | **간트** | authored |
| 다항목 정량 비교(3~5축) | 레이더 | authored |
| 집합 간 겹침 | 벤 | authored |
| 두 변수 분포·상관 | 산점도 | authored |
| 보고·소유·에스컬레이션 | 조직도 | authored |
| 순환·플라이휠 | 루프 | authored |
| 역할×자원 권한 표 | 매트릭스 | authored |
| 병렬 요점·순서 단계·비교·SWOT·트리·타임라인·계층·수치 추이 | (기존 표 참조) | antv |

### 커넥터 규칙 (authored 필수 — 위반은 시각 판정 반려 사유)

1. **직교(orthogonal) 커넥터만.** 대각선 금지. 꺾임은 반경 6~8u 라운드 엘보.
   직선 `<line>`은 두 끝점이 같은 x 또는 y를 공유할 때만.
2. **라벨은 커넥터에서 6~10u 띄운다.** 화살표 위에 앉히지 않는다 — 선이 보여야 추적된다.
3. **커넥터끼리 겹침 금지.** 교차가 불가피하면 점프(bridge) 처리, 평행 주행은 ≥12u 이격.
   커넥터가 쌓이면 레이아웃 실패 — 개요+상세 2장으로 분할하라.
4. **같은 변에 여러 커넥터가 닿으면 접점을 분산한다** — 변 길이 L에 N개면 `L·k/(N+1)`
   지점, 인접 접점 ≥12u.
5. **출발·도착이 아닌 박스 뒤를 통과하지 않는다.** 우회가 기하학적으로 불가한 경우만
   파선(`stroke-dasharray`)으로 "통과"임을 표시하고 라벨은 보이는 끝에 둔다.
6. **라벨이 다른 노드를 덮지 않는다** (정규화기의 렌더 실측 겹침 감지가 강제).

### 복잡도 예산 (초과분은 도해 분할로 — 축소 금지)

노드 ≤9 · 화살표 ≤12 · 강조색 요소 ≤2 · 시퀀스 라이프라인 ≤5 · 스위밍레인 ≤5 ·
ER 엔티티 ≤8 · 트리 깊이 ≤4 · 조직도 ≤12노드/깊이 4 · 레이어 ≤6 · 벤 ≤3원 ·
레이더 5축·5계열 · 바 ≤8 · 선 그래프 ≤5계열 · 간트 ≤12작업 · 산점도 ≤30점 ·
주석 콜아웃 ≤2. **예산을 넘기면 글자를 줄이는 게 아니라 도해를 나눈다.**

### 수치 규율

도해로 수치를 새로 만들지 않는다 — 본문에 실재하는 수치·주장만 시각화(G10 정신).
차트형(바·선·산점도·레이더)의 모든 수치는 같은 장 본문에 문장으로 실재해야 한다.

> 타입 분류·커넥터 규칙·복잡도 예산은 cathrynlavery/diagram-design(MIT, Copyright
> 2025 Cathryn Lavery)의 명세를 bookforge 파이프라인(한국어 조판·Pretendard·팔레트
> 토큰·게이트 체계)에 맞게 재서술한 것이다. 템플릿·코드는 가져오지 않았다(한글 미지원·
> 판형 하한 충돌 실측). 겹침 검사는 원본의 정적 기하 검사(verify-geometry) 대신
> 렌더 실측(Chromium)으로 대체 — 목적 동일, 검출력 상위.
