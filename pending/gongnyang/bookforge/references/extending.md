# 스타일 팩 추가·수정 가이드 (메인테이너용)

## 스타일 팩 계약

`styles/<이름>/`에 다음을 둔다:

| 파일 | 역할 |
|---|---|
| `STYLE.md` | 디자인 규칙서(수치 포함). 집필 톤·지면 문법의 단일 진실 원천 |
| `tokens.json` | `engine`(typst\|html), `trim_mm`(G1이 PDF 실측과 ±0.5mm 대조 — 테마 하드코딩과 어긋나면 FAIL), **`body_pt`**(테마가 선언한 본문 급수. G1-SCALE이 PDF 본문 최빈 pt와 ±0.3pt 대조 — 전역 축소 차단. **미선언 시 WARN만 나가고 그 스타일은 축소 검출 불가**이므로 새 팩은 반드시 넣을 것), `length_pages`, `brand_default`, `fonts`(스타일이 실제 쓰는 동봉 패밀리 목록), `body_frame_mm`(pagemetrics 판면 정본), **`front_frame_mm`**(선택 — 앞부속(표지·목차) 텍스트 봉투 `[top,right,bottom,left]`mm. 리스트면 앞부속 전 면 공통, 객체면 `{"cover": [...], "toc": [...]}`로 1면=표지·나머지=목차. G3-FIT이 이 프레임 밖 텍스트를 FAIL시킨다. 표지·목차는 `body_frame_mm`이 아니라 자체 padding·절대배치를 쓰므로 body_frame을 재사용할 수 없고, **미선언이면 그 스타일은 앞부속 프레임 검사가 WARN과 함께 생략**된다 — 값을 CSS에서 확정할 수 없는 스타일에 억지로 넣지 말 것. 값은 CSS 선언 좌표에서 글리프 오버행을 흡수한 봉투로 잡고, 근거와 실측 여유를 같은 파일의 `_front_frame_mm_note`에 남긴다. **선언값 타당성은 G16-SYNC가 렌더 전에 기계 검증한다**: 4원소 수치 배열 · 각 값 ≥ 0 · `좌+우 < trim_w` ∧ `상+하 < trim_h` · 객체형이면 `cover`·`toc` **둘 다** 필수(하나만 선언하거나 한쪽이 `null`이면 나머지 면의 축이 경고 없이 전부 꺼지므로 HARD FAIL) — 전부 증명 가능한 모순이다. 프레임 면적이 지면의 95% 이상이면 축이 항등이 되므로 WARN(`[0,0,0,0]`이 그 형태), qc_gate도 같은 WARN을 리포트에 싣고 "선언은 있으나 검사한 면 0개"를 별도 WARN으로 남긴다 — **위조가 미선언보다 조용해서는 안 된다**), **`toc_levels`**(인쇄 목차에 노출하는 계층 수. 1이면 빌더가 절 엔트리도, `<h2>`의 `@@chNNsMM@@` 마커도, 레벨 2 북마크도 발행하지 않는다 — STYLE.md가 "계층 1단계까지만"을 선언한 스타일은 1로 둘 것. **미선언 시 2로 폴백**), **`toc_capacity`**(단면 목차 스타일 전용 — 아래 「단면 목차 팩」. TOCPAGE 블록이 없는 html 엔진 스타일이 이걸 선언하지 않으면 빌드가 `die()`), **`toc_overflow`**(html 엔진 전용 — `"paginate"`\|`"single"`. 아래 「HTML 테마 계약」 참조. 부재·오값, 또는 `theme.html`의 `BF:TOCPAGE` 블록 유무와 불일치하면 빌드가 `die()`. typst 4종은 이 키가 없다 — **typst 엔진 팩의 선언은 죽은 설정으로 G16-SYNC HARD FAIL**이다: typst 빌드 경로는 이 키를 소비하지 않으므로 선언이 있으면 "다면 목차 지원"이라는 거짓 계약이 조용히 산다, 적대검증 v-s1 ②), **`toc_layout`**(6스타일 **전부 필수** — 그 팩이 구현한 목차 문법의 이름. 허용값 표는 `scripts/g16_tokens.py`의 `TOC_LAYOUTS`가 단일 진리원이고, 아래 「목차 레이아웃 계약」 참조. 미선언·카탈로그 밖은 G16-SYNC HARD FAIL), **`toc_capacity_alt`**(오버레이 보유 팩 전용 — 대안 레이아웃 이름 → `toc_capacity`와 같은 7키. 아래 「대안 레이아웃 오버레이」. 실물 오버레이 CSS 없이 선언만 있어도, 선언 없이 실물만 있어도 G16-SYNC 오버레이 축 FAIL), **`toc_lists`**(선택 — 그림·표 차례 별면 옵트인. `["figures","tables"]`의 부분집합, **미선언 = 발행 0**. 다면 목차(`toc_overflow: "paginate"`) 스타일 전용이고 단면 스타일의 선언은 빌드 `die()`. 책 단위 `book.json`으로 덮어쓸 수 있다. 아래 「HTML 테마 계약」·G14-E 참조), `diagram`(`palette`·**`palette_roles`**·minFontPt·**`labelBand`**·widths·**`maxHeightMm`** — `minFontPt`는 라벨 급수 **하한**(HARD)이고 `labelBand`는 `body_pt` 대비 **상한** 계약 `{"maxRatio": 1.2, "enforce": bool}`이다(하우스 등급 1.2). 둘은 단위(절대 pt vs 상대 비)도 강도도 다르고 `minFontPt`는 G16-BRAND 대비 하한의 입력이기도 해서 한 객체로 합치지 않았다. `enforce`는 **스타일별 승격 스위치**로 `contrast_contract.enforce`와 같은 계약이다 — JSON bool만 허용하고 **부재·문자열은 G16-SYNC HARD FAIL**(문자열 `"false"`가 truthy로 읽혀 강제가 반대로 켜지는 구멍을 막는다). `true`면 상한 위반이 그 도해의 렌더 실패, `false`면 WARN이다. 승격 조건은 **그 스타일 코퍼스 위반 0**이고 근거는 같은 블록의 `_labelBand_evidence`에 실측과 함께 남긴다(6스타일 전부 `true` — W5 8단계). `labelBand` **객체 자체의 부재도 malformed**로 G16-SYNC HARD FAIL이다(palette와 같은 취급) — 키 한 줄을 지우면 상한 판정과 6단계 급수 주입이 **함께** 조용히 죽는다(W5 K2 실측: WARN 1행 뒤 본문의 2.5× 라벨이 그대로 발행됐다). `maxRatio`는 양수 수치 필수이고 **타당성 대역 `0.5 ≤ maxRatio ≤ 2.0` 밖도 malformed HARD FAIL**이다 — 하한 0.5는 상한이 `minFontPt`(8pt) 아래로 내려가 밴드가 공집합이 되는 지점, 상한 2.0은 본문의 두 배(등재 근거 없음)다. 종전엔 검사가 '양수인가' 하나여서 `maxRatio: 999`가 **경고 한 줄도 없이** 상한 검사와 급수 주입을 동시에 껐다(W5 K3). `labelBand` 객체는 `gateParams()`가 **통째로** 캐시 해시에 싣기 때문에 `enforce`를 뒤집는 순간 그 스타일 도해가 전건 재렌더·재판정된다(해시 파라미터를 따로 추가할 필요가 없다). `labelBand.maxRatio` 또는 `body_pt`가 없으면 상한 검사가 꺼지며 그 사실이 render_diagrams 경고로 나오고, `enforce: true`인 스타일에서는 **꺼짐 자체가 반려**다. `widths`는 `full`·`twothirds` 두 키가 양수 수치여야 하고, **관계 불변식 `0 < twothirds ≤ full ≤ trim_mm[0]`도 G16-SYNC HARD**다 — widths는 도해 pt 환산의 유일 기준이고 밴드·하한·급수 주입이 **전부 이 값을 공유**하므로, 값이 틀리면 셋이 같은 거짓 기준으로 자기정합해 게이트 전건 초록으로 통과한다(W5 K1 실측: `twothirds` 106 → 400에서 실 급수 2.3~2.9pt가 출하 가능했다). **`maxHeightMm`**는 도해 **배치 높이 상한**(mm, W7)이다 — figure(도해+캡션)가 한 면에 들어가는 한계로, 스타일 판면 높이 − figure 마진 − 캡션 실측에서 파생하고 산식을 같은 블록의 `_maxHeightMm_evidence`에 남긴다. `labelBand`와 같은 취급으로 **부재·비수치·`trim_mm[1]` 이상은 render_diagrams 시동 실패(malformed)**다 — 키 한 줄이 빠지면 높이 검사와 축소·반려가 함께 조용히 꺼져 세로 긴 도해가 면을 넘어 쪼개진 채 출하된다(실증: insight 세로 셰브런 254.8mm p5/p6 분단). 렌더러(figFitReport)가 배치 높이 `widths[bf.width]×(vbH/vbW)`를 사전 산출해 초과 시 폭 비례 축소를 결정(`metrics.fit`)하고 build_html·md2typ은 그 폭을 전사만 한다 — 축소가 `minFontPt` 하한을 깨면 그 도해는 반려다(가로 배치 재작성 처방). `gateParams()`가 이 값을 캐시 해시에 실으므로 값 변경 시 그 스타일 도해가 전건 재판정되고, 최종 PDF는 G17-FIGFIT이 이중 방어한다. `palette_roles`는 `palette`와 병렬인 **필수** 배열로 슬롯별 역할(`label`\|`fill`\|`stroke`)을 선언한다. 부재·길이 불일치·허용값 밖은 G16-SYNC HARD FAIL — 옵셔널이면 새 스타일이 빼먹고 G16-BRAND가 조용히 무력화된다. 0번 슬롯은 `render_diagrams.mjs:259`이 `book.json.brand`로 덮어쓰는 브랜드 치환 슬롯이라 `label`이어야 브랜드 대비 검증이 성립한다), **`contrast_contract`**(선택 — 렌더 전 대비 계약. `{"enforce": bool, "entries": [{"fg":, "bg":, "pt":, "bold":, "where":}, ...]}` 형식. `fg`/`bg`는 hex 리터럴이 아니라 **토큰명**(`--css-var` \| `brand` \| `palette[n]` \| `$key_label` \| 리터럴 `#hex`)으로 적어 브랜드가 바뀌어도 계약이 썩지 않는다. 하한은 저장하지 않고 `pt`/`bold`에서 WCAG로 파생한다(`scripts/g16_tokens.py`의 `contrast_floor`가 단일 진리원 — G14-C와 공유). `enforce:true`인 스타일만 미달이 G16-CONTRAST **HARD FAIL**, 그 외(부재·`false`)는 WARN — typst 4종처럼 키 자체가 없으면 그 스타일은 이 축이 N/A로 빠진다(절대 FAIL 아님)), **`key_label`**(선택 — `$key_label` 플레이스홀더가 파생할 라벨색의 배경·급수 계약. `{"bg": "--토큰", "pt": N, "bold": bool}`. brand를 명도만 낮춰 그 배경 위 대비 하한(×1.05 여유)을 처음 넘는 색을 결정론 파생한다(`derive_key_label`) — hue·채도는 보존해 브랜드 정체성과 G16-BRAND hue 정합을 깨지 않는다. 미선언이면 brand 원색을 그대로 쓴다. 대비 실측이 있는 스타일만 선언할 것(magazine `.callout-title` 4.45가 근거)) |
| `theme.typ` | (typst 엔진) 테마 구현 |
| `theme.html` + `theme.css` | (html 엔진) 페이지 골격 + 인쇄 스타일시트 |
| `decorate.py` | (html 엔진, 선택) 렌더 후 PyMuPDF 러닝 장식 스탬핑 |

## Typst 테마 계약

`theme.typ`는 `templates/base.typ`(빌드 시 같은 폴더로 스냅샷됨)를 `#import "base.typ"`로 가져오고, 다음 심볼을 반드시 export한다 — 생성되는 main.typ과 md 변환 결과가 이 이름들을 호출한다:

`meta`(= `json("meta.json")`) · `theme-tokens` · `TT` · `book(meta:, tokens:, cover:, toc:, body)` · `make-cover(meta)` · `colophon(meta, t)` · `bf-chapter(title, summary:)` · `bf-callout(kind:, title:, body)` · `bf-stat(value, label)` · `bf-fig(path, caption:, source:, width:)`

base의 `book()`을 그대로 쓰거나(practical처럼 토큰만 교체), 완전히 대체할 수 있다(essay·business·academic처럼). base가 제공하는 부품: `default-tokens`, `keep-words`(제목 어절 단위 줄바꿈 우회 — Typst는 keep-all 미지원), `full-bleed`, `chapter-state`, `numpad`.

**표지 variant 계약(practical)**: `make-cover(meta)`는 `meta.cover_variant`(← `book.json` — `brand` 덮어쓰기와 같은 자리, `meta.json` 경유)로 표지를 디스패치한다. 허용값 `numeral`(**기본** — 미선언 시)·`ribbon`(구 기본, 옵트인 강등 보존)·`block`·`grid`·`obi`, 카탈로그 밖 값은 침묵 폴백 없이 panic. 미선언 산출은 `numeral` 명시 선언과 단어좌표 수준 동일이어야 한다. 표지의 모든 텍스트 블록은 재단 안(±1.5 pt)이어야 한다 — G3-OVERFLOW는 표지 면도 스캔하고, 재단 밖 크롭 연출은 클립을 걸어도 추출 bbox가 줄지 않아 성립하지 않는다(pymupdf 실측). 각 variant의 지면 사양은 `styles/practical/STYLE.md` 「표지 문법」이 정본.

주의: 문단 간격을 0으로 쓰는 스타일은 `list/enum spacing`과 블록 above/below를 반드시 명시하라 — 기본값 상속 시 줄겹침이 난다.

**도해 폭 계약(신설 HARD)**: `bf-fig`는 `width:` 인자를 반드시 받아 `image(..., width: width)`로
넘긴다 — `md2typ.py`가 도해 사이드카의 `bf.width`를 `tokens.diagram.widths`로 환산해
`#bf-fig(..., width: Nmm)`으로 발행하기 때문이다. 그리고 `tokens.diagram.widths.full`은
`theme-tokens`의 `trim.w − margin.left − margin.right`(= 판면폭, `width: 100%`가 앉는 폭)와
같아야 한다. 둘이 갈라지면 조판은 tokens 폭으로 그리는데 `render_diagrams.mjs`도 같은 값으로
글자 하한을 환산하므로 지면에서만 티가 나고 게이트는 침묵한다. G16-SYNC widths 축이
`bf-fig`의 `width:` 인자 실존과 이 등식을 렌더 전에 HARD로 지킨다(판면 산출식을 읽지 못하는
형태면 FAIL이 아니라 수동 감사 WARN — 추정하지 않는다).

## HTML 테마 계약

`theme.html`은 python `string.Template` — `$title $subtitle $author $date $brand $cover_art $toc $body $css` + `$tocmap`(magazine 목차 이미지 맵) `$backquote`(뒤표지 인용) 플레이스홀더. `$` 문자를 리터럴로 쓰려면 `$$`. css 쪽 플레이스홀더는 `$fonts_dir $key_color $key_tint $key_label $fig_full_mm $fig_twothirds_mm`.

`theme.css`엔 `$fonts_dir`(폰트 폴더 file:// URI), `$key_color`, `$key_tint`, `$key_label`(tokens `key_label` 계약에서 파생한 라벨색), `$fig_full_mm`·`$fig_twothirds_mm`(tokens `diagram.widths`의 CSS 전사 — 아래 참조)가 주입된다. 규칙:

- **도해 figure 폭은 반드시 `$fig_full_mm`·`$fig_twothirds_mm`으로 받는다.** 두 값의 단일 진리원은 `tokens.json diagram.widths`이고 CSS는 그 파생이다 — 같은 값을 `render_diagrams.mjs`가 도해 글자 하한의 pt 환산 기준(`scalePt = widths[key]×2.835 ÷ viewBox폭`)으로 쓰므로, CSS가 폭을 따로 적으면 게이트가 실렌더와 다른 폭으로 판정한다(magazine이 선언 151 / 실렌더 164로 1.086배 과엄격하게 돌던 사고). `bf.width: twothirds` 사이드카는 빌더가 `<figure class="svgfig twothirds">`로 발행하므로 팩은 `figure.twothirds` 규칙에서 `$fig_twothirds_mm`을 받아야 한다. **G16-SYNC widths 축이 HARD로 강제한다**: `diagram.widths.full`·`.twothirds`가 양수 수치일 것 · 두 플레이스홀더가 theme.css에 실존할 것 · figure를 겨냥한 규칙에 `width` 길이 리터럴(퍼센트 포함)이나 `max-width` 절대 길이가 없을 것.
- `@page { size: <trim>mm; margin: ... }` + 풀페이지 섹션(표지·목차)용 `@page full { margin: 0 }` — 해당 섹션에 `page: full; width/height = trim` 지정. 네거티브 마진으로 판형을 흉내내지 말 것(깨진다).
- 목차 쪽번호는 빌더가 2-pass로 주입 — 장 오프너에 `<span class="pgmark">@@chNN@@</span>` 마커와 목차에 `<span class="tocpg" data-mk="chNN">00</span>`을 유지할 것. `toc_levels >= 2`면 절 마커 `@@chNNsMM@@`도 발행되므로 `<h2>`에 **`position: relative`가 필수**다 — 없으면 마커가 문서 원점(1면)에 붙어 모든 쪽번호가 어긋나고 사후조건은 충족된다. 마커 어휘는 `@@(ch|fg|tb)…@@` 3종이고 회수·제거 정규식은 `scripts/build_html.py`의 `MK_SCAN_RE`/`MK_STRIP_RE`가 단일 진리원이다. 본문에 마커 형태의 리터럴 텍스트(`@@fg001@@` 등 — 코드 예제 포함)가 있으면 `toc_lists` 미선언 스타일에서도 잉여 마커로 빌드가 die한다(fail-loud — 양방향 전수 검사의 의도된 거동, 마커 일반화 이전에는 조용히 통과했다) — `tokens.json`에 `toc_lists`(`["figures","tables"]`의 부분집합, **미선언 = 발행 0**)를 선언한 스타일에서는 캡션 있는 그림/표에 `@@fgNNN@@`/`@@tbNNN@@`(문서 전역 카운터)이 발행되고, 빌더가 마커를 품는 figure/`.tablewrap`에만 `mk-anchor` 클래스를 붙이므로 theme.css에 **`.mk-anchor { position: relative; }` 규칙이 필수**다(figure/`.tablewrap` 자체에 무조건 `position:relative`를 주지 말 것 — positioned 요소는 페인트 단계가 뒤로 밀려 마커 없는 기존 책의 PDF 텍스트 스트림 순서까지 바뀐다). 회수는 종별 딕트로 분리되며(`decorate.py`의 `ctx["pages"]`는 ch 종만 받는다 — fg/tb가 섞이면 `min(pages)` 폴리오 오프셋이 오염된다), 빌더 사후조건은 종별 전수 회수(양방향) + **포함 단조**(fg/tb 회수 면이 소속 장 구간 안이고 발행 순으로 단조 — 앵커 소실 시 전 마커가 1면으로 회수되는데 전수 회수만으로는 통과하는 함정을 잡는다)다. 감도는 M-ORIGIN 뮤테이션이 고정한다. `toc_lists`를 켜면(스타일 tokens.json 또는 책 단위 `book.json` 덮어쓰기 — brand/toc_layout과 같은 자리) 빌더가 본문 차례 뒤에 `그림 차례`/`표 차례` 별면도 발행한다(book-anatomy 앞부속 ⑨) — 면은 **BF:TOCPAGE 복제본**으로 나가므로 `toc_lists`는 다면 목차(`toc_overflow: paginate`) 스타일 전용이고 단면 스타일의 선언은 die다. 항목은 캡션 발행 경로와 같은 라벨·캡션 문자열 + 같은 `.tocpg[data-mk]` 2-pass 스탬핑이고, 렌더 후 **G14-E**가 PDF에서 차례 행을 재추출해 실제 캡션 면과 전건 대조한다(감도는 M-LISTPG 뮤테이션). 차례 별면을 받는 스타일은 theme.css에 `.lists-word`·`.lof-no`·`.lof-title`·`li.lof` 규칙(insight 참조)을 선언해야 한다.
- **`.tocpg` 칼럼 폭은 고정해야 한다.** pass 2에서 `00`이 실제 쪽번호로 바뀔 때 제목의 가용 폭이 변하면 경계 길이 제목이 접혀 면이 밀리고, 그 밀림은 pass 1 HTML 검사로 볼 수 없다(insight `flex: 0 0 6.5mm` = 3자리 실측폭 + 여유. 4자리 폴리오는 빌더가 `die()`).
- **`tokens.json`에 `toc_overflow`를 반드시 선언한다**(html 엔진 전용 키 — typst 4종은 이 키 자체가 없어야 하며, typst 팩의 선언은 G16-SYNC HARD FAIL이다(죽은 설정). html 팩의 부재·오값은 빌드가 `die()`). 값은 `"paginate"`(다면 목차 — 분량에 따라 목차 면 수가 늘어남) 또는 `"single"`(단면 목차 — 스프레드 1면 고정) 둘 중 하나다. 빌더는 이 토큰과 `theme.html`의 `BF:TOCPAGE` 블록 유무(아래)가 **일치하는지**를 렌더 전에 대조하고, 어긋나면(예: 토큰은 `"single"`인데 템플릿엔 `BF:TOCPAGE`가 있음) `die()`한다 — 계약(토큰)과 실물(템플릿)의 디싱크는 조용히 넘어가지 않는다. 종전엔 이 분기가 토큰 없이 템플릿 실물만으로 갈렸다(`"<!--BF:TOCPAGE" in tpl_src`) — tokens.json만 읽어서는 그 스타일이 다면인지 단면인지 알 수 없었다.
- **다면 목차**(`toc_overflow: "paginate"`, 분량에 따라 목차 면 수가 늘어나는 스타일)는 `theme.html`의 목차 섹션 전체를 `<!--BF:TOCPAGE-->` … `<!--/BF:TOCPAGE-->`로 감싼다. 빌더가 `Template.substitute` **전에** 이 블록을 잘라내 N회 복제하고 각 복제본의 `$toc`→`$toc_i`, `$toc_mod`→`$toc_mod_i`로 치환한다. 2면 이후는 `$toc_mod = "toc-cont"`이므로 1면에만 두는 요소는 CSS에서 `.toc-page.toc-cont` 선택자로 감춘다. 목차 마크업·장식을 `decorate.py`로 옮기지 말 것 — 겹침 게이트가 스탬핑 가구를 면제하면 사고 지점이 통째로 검사 밖으로 나간다.
- 빌더는 `<book_dir>/typeset/tocplan.json`(면 수·면별 행 수·**예측 바닥 mm·실측 바닥 mm·렌더 배율·재계획 여부**·발행 절 마커 수·빌드 경고)을 남긴다. G4가 레벨 2 북마크 수를 이 파일의 `section_markers`와 대조하고, 빌드 경고를 게이트 리포트의 warns로 올린다. **html 엔진인데 이 파일이 없으면 G4가 FAIL**한다.
- **높이·폭 모델은 계획자일 뿐이고 `pass1.pdf`가 검증자다.** 빌더는 렌더 후 목차 면의 스팬 bbox로 실제 바닥(mm)을 재고, 전역 축소 배율(본문 최빈 pt / `body_pt`)로 원좌표를 복원한다. 물리 한계 초과면 **실측 접힘 실태로 1회 재계획하고 pass1을 다시 렌더**하며(결정론·최대 1회) 그래도 넘치면 `die()`. 미학 한계 초과·모델 이탈은 WARN으로 남는다. 추정 정확도만으로는 "조용한 넘침 → 문서 전역 축소" 계열을 닫을 수 없다는 것이 이 구조의 이유다.

### 단면 목차 팩 (TOCPAGE 블록이 없는 html 엔진 스타일)

목차를 스프레드 1면에 고정하는 스타일(magazine 계열)은 `tokens.json`에 `toc_overflow: "single"`을 선언하고(위 참조), **`toc_capacity`도 반드시 선언**한다. 선언이 없으면 빌드가 `die()`한다 — 구 구현은 `if style != "magazine": return`으로 **폴더 이름**이 방어선이어서, magazine 파생 팩을 하나 만들면 용량 검사가 조용히 사라지고 넘침이 전역 축소로 갔다.

```json
"toc_capacity": {
  "top_mm": 41.36,        // 첫 항목 제목 글리프 top
  "pitch_mm": 23.548,     // 항목 피치
  "tail_mm": 14.217,      // 마지막 항목 top → 콘텐츠 bottom
  "bottom_mm": 238.0,     // 콘텐츠 하단 = 재단높이 − padding-bottom
  "title_avail_mm": 75.0, // 제목 1행 가용 폭 — 검사는 ×0.98 렌더 마진을 적용한 실효 폭
                          // (73.5mm)으로 접힘을 판정한다(build_html.TOC_TITLE_RENDER_SAFETY:
                          // Chromium 실렌더 advance가 폭 모델보다 +1.0~1.4% 넓다는 실측 —
                          // 마진 없이는 상한 마지막 ~2% 대역 제목이 통과 후 접혀 출하됐다)
  "font": "Paperlogy-7Bold", "size_pt": 22.0   // assets/fonts 파일명(확장자 제외)
}
```

값은 전부 `[실측]`이어야 한다(실렌더 PDF의 스팬 bbox). 빌더는 이 선언으로 ①제목이 1행에 들어가는지 ②예측 바닥이 `bottom_mm` 이하인지를 검사하고, 초과 시 상한 장 수와 대응 3종을 담아 `die()`한다. **`overflow:hidden`으로 잘라내거나 폰트·행간을 줄여 밀어 넣는 대응은 금지** — 잘린 목차는 어떤 게이트도 검출하지 못한다.

**접힘은 예산이 아니라 금지다.** `.toc li{flex-wrap:wrap}` 구조에서 제목이 1행을 넘으면 높이만 느는 게 아니라 정렬이 파손된다(실측: 제목 좌단이 쪽번호 칼럼보다 왼쪽으로 17mm 이탈, 쪽번호가 제목 위 독립 행으로 고아화). 근사 높이로 흡수하지 말고 `die()`할 것.
- **절 목록과 절 마커는 한 경로에서만 나온다.** `md_to_html(md, …, sec_marker="chNN", sec_titles_out=lst)`가 비콜아웃 청크를 렌더하는 그 자리에서 `<h2>`에 마커를 주입하고 주입한 제목을 순서대로 돌려준다. 원고를 줄 단위로 다시 스캔해 절 목록을 만들지 말 것 — 콜아웃 안 `## `(마커만 생김)·코드블록 안 `## `(목록만 생김)·리터럴 `<h2>`·`:::` 미종료가 전부 두 경로를 어긋나게 하고, 그 어긋남은 절 쪽번호와 레벨 2 북마크를 조용히 오배정한다. 빌더는 pass 1에서 `발행 마커 == 회수 마커`를 **양방향**으로 검사한다(단방향이면 잉여 마커가 통과한다).
- 러닝 장식(폴리오·바·세로 러닝헤드)은 CSS 마진박스보다 `decorate.py` 스탬핑이 정확하다: `decorate(doc, ctx)` — `ctx = {book, pages(마커→쪽), fonts_dir}`. 페이지별 생략 규칙을 코드로 구현.
- 폰트는 전부 로컬 `@font-face`(assets/fonts). 웹 CDN 금지 — 결정론 훼손.

## 목차 레이아웃 계약 (`toc_layout`, 6스타일 공통)

각 팩은 이미 **서로 다른 목차 레이아웃**을 구현하고 있었지만 그 사실이 어디에도 선언돼 있지 않았다. 선언이 없으면 레벨 수·리더·급수 같은 레이아웃 불변식이 조용히 깨져도 신호가 없다(리더 점선을 넣어도, 급수를 올려도 전 게이트 초록). `toc_overflow`와 같은 형태의 무선언 구멍이다.

- **`tokens.json`에 `toc_layout`을 반드시 선언한다**(엔진 무관 — html·typst 6종 전부). 값은 카탈로그의 레이아웃 이름이고, 허용값·불변식의 단일 진리원은 `scripts/g16_tokens.py`의 **`TOC_LAYOUTS`** 딕셔너리다. 팩은 이름만 고른다 — 정의를 팩마다 복제하면 그 자체가 제2의 진리원이 된다(`toc_overflow`의 허용값 표가 `build_html.TOC_OVERFLOW_MULTIPAGE`에 있는 것과 같은 배치).
- 현행 6종: `hanging-two-level`(insight) · `spread-single-level`(magazine 기본) · `display-numeral`(business, magazine 오버레이) · `twocol-balanced`(practical) · `academic-flow`(academic) · `flush-single-level`(essay).
- 카탈로그 항목의 필드와 출처(전부 theme 실물 실측): `styles`(그 레이아웃을 **구현한** 팩 — 레이아웃은 theme 파일에 사는 물건이라 목록에 스타일을 추가하려면 구현이 먼저 있어야 한다) · `max_levels`(싣는 최대 표제 레벨) · `leader`(점선 리더 사용 여부) · `size_cap_pt`(목차 급수 리터럴 상한. **여백이 아니라 캘리브레이션 잠금**이다 — insight 30pt는 `build_html`의 목차 높이 모델 입력이고 magazine 22pt는 `toc_capacity.size_pt`와 같은 수다. `None`이면 급수가 변수 주입이라 정적 상한이 성립하지 않는다는 뜻).
- **G16-SYNC가 렌더 전에 5축을 기계 검증한다**(새 게이트명 없이 기존 배열에 합류 — 축을 이름으로 쪼개면 배선이 늘고 어느 하나가 빠지는 순간 조용히 꺼진다): ①값 ∈ 카탈로그 ②스타일 ∈ `styles` ③`toc_levels` ≤ `max_levels` — **비int(float/str/bool)는 malformed HARD FAIL**(빌더가 값을 그대로 소비해 bool은 1레벨로 뒤집힌다 — `labelBand.enforce`와 같은 "JSON 타입이 계약" 교리)이고, html 팩은 **부재도 빌더 폴백값(`TOC_LEVELS_DEFAULT`=2)으로 대조**한다(키 삭제가 `max_levels: 1` 팩에서 폴백 2를 무검사 통과시키던 구멍 — 적대검증 v-s2 A1~A4) ④theme 실물의 점선 리더 유무 ↔ 선언 `leader` 일치 — html은 `theme.css` + `theme.html`의 `<style>` 블록·인라인 style, 관용구는 `dotted`/`dashed`·점 그라데이션·생성 콘텐츠 점열(ASCII·**미들닷/줄임표류 유니코드**); typst는 목차 영역의 `repeat(` 직접 + **`#let` 헬퍼 간접 1단 추적**(정의는 파일 어디든, 목차 영역엔 이름 호출만 있는 형태 — v-s2 D1) ⑤`.toc*` 겨냥 규칙(html) 또는 목차 코드 줄(typst)의 최대 급수 ≤ `size_cap_pt` — html은 **`var()` 1단 해석 포함**(`:root` 커스텀 프로퍼티 — v-s2 C1), `theme.html` **인라인 `font-size`는 값 무관 FAIL**(급수 잠금은 CSS 스캔으로만 성립 — v-s2 C2), 다단 var·상대 단위 등 **미해석 선언은 리터럴이 남아 있어도 WARN으로 발화**(침묵 금지); typst `size: Nem`은 영역 내 최대 pt 리터럴(없으면 11pt)을 보수 기저로 환산해 초과면 FAIL, 아니면 "확정 불가" WARN(v-s2 D2).
- **정적 판정의 한계(계약)**: 리더 관용구 목록 밖의 실현 수단·typst **2단 이상 헬퍼 체인**·치환 변수(`$…`)로 실려 오는 인라인 값은 렌더 전 스캔이 원리적으로 못 잡는다. 렌더 후 게이트는 이 축들의 2차 방어가 **아니다** — 리더 점열은 정상 텍스트로 렌더되어 어느 픽셀 축도 보지 않고(w6 재작업2 실측: academic에 2단 체인 리더 주입 → 컴파일 성공·점열 실렌더·qc_gate 신규 검출 0), 급수 초과는 넘침이 문서 전역 축소로 이어지는 경우에만 G1-SCALE이 늦게 잡는다. **관용구 목록·해석기 등재가 곧 방어다** — 새 리더 실현 수단을 쓰려면 `g16_tokens._CSS_LEADER_RE`/`toc_typ_leader`에 먼저 등재할 것.
- **`theme.css`/`theme.html`/`theme.typ`이 하나도 없는 디렉토리는 WARN 1행으로 skip한다** — 목차 구현이 없는 작업 중 산출물에서 FAIL 더미를 뱉으면 게이트가 무시당하고, 무시당하는 게이트는 없는 게이트다.
- 감도 회귀 자산은 `tests/mutations/run_mutations.py`의 **M17**(㉠허용 밖 스타일 배정 ㉡리더 실물 뒤집기 ㉢급수 상한 초과 ㉣카탈로그 밖 이름 + v-s2 우회 축별 대표 ㉩`toc_levels` 문자열 malformed ㉪dashed 리더 ㉫`var()` 간접 급수 ㉬typst 헬퍼 간접 리더)이며, 각각 다른 임시 사본에 주입한다. 오버레이 보유 팩은 **M17 오버레이 축**(㉤오버레이 리더 주입 ㉥오버레이 급수 초과 ㉦파일명 카탈로그 밖 개명 ㉧`toc_capacity_alt` 항목 삭제)이 추가로 돈다.

### 대안 레이아웃 오버레이 (책 단위 `toc_layout` 전환 — html 단면 전용, W6 S6)

한 팩이 **두 번째 목차 레이아웃**을 구현할 수 있다(magazine의 `display-numeral`이 최초 사례 — business 대형 번호 문법의 HTML 이식). 규칙:

- **켜는 곳은 `book.json`의 `toc_layout`이다**(brand가 `brand_default`를 덮는 것과 같은 자리). 미선언 책은 팩 기본(tokens.json `toc_layout`)으로 빌드되고 **산출이 바이트 수준으로 불변**이어야 한다 — 대안 레이아웃 분기는 전부 `active != declared`일 때만 깬다(`build_html.py`「대안 목차 레이아웃」).
- **실물 CSS는 `toc-<레이아웃이름>.css` 오버레이 파일이다. `theme.css`에 섞지 말 것** — 축 ⑤의 기본 레이아웃 급수 잠금이 오버레이 리터럴에 오염되면 상한을 올리거나(잠금 해체) 상시 FAIL(오탐)이 된다. 빌더는 선언된 빌드에서만 오버레이를 theme.css 뒤에 이어붙인다(뒤가 이긴다). 행 골격(`li` flex·`.tocpg[data-mk]`·요약 `data-sum`)은 기본 레이아웃 것을 상속해 2-pass 스탬핑·G14-A·접힘 금지가 레이아웃 무관으로 남게 한다.
- **용량 계약은 `tokens.json` `toc_capacity_alt[<이름>]`** — `toc_capacity`와 같은 7키. 행 문법이 다르면 top/pitch/tail 전부 다른 실측이라 기본 용량으로 판정할 수 없다. 값은 프로브 실측 재적합으로만 넣고 근거를 `_why`에 남긴다.
- 카탈로그 `size_cap_pt`는 **스타일별 dict를 허용한다**(`{"business": None, "magazine": 40.0}`) — 같은 문법이라도 구현마다 잠금이 다르다. 해석은 `g16_tokens.toc_size_cap()` 하나만 안다.
- **G16-SYNC 오버레이 축(⑥~⑪, `overlay_findings`)이 렌더 전에 지킨다**: ⑥파일명 이름 ∈ 카탈로그 ⑦스타일 ∈ `styles` ⑧html 엔진 전용·팩 기본과 같은 이름 금지 ⑨오버레이 리더 리터럴 ↔ 선언 ⑩오버레이 최대 급수 ≤ 상한(오버레이는 리터럴 구현이라 상한 `None` 자체가 FAIL) ⑪단면 스타일이면 `toc_capacity_alt[<이름>]` 7키 실재·`size_pt` ≤ 상한, 역방향(실물 없는 용량 선언)도 FAIL.
- 다면(paginate) 스타일의 책 단위 전환은 **금지**(빌더 die) — 높이 모델 17상수 재적합 없이는 예측이 전부 허수다(리스크: 조용한 전역 축소 재발). `toc_levels ≥ 2`도 금지(대안 레이아웃은 레벨 1 행 마크업만 구현).

## 검증 루프

수정 후엔 반드시 스모크 북으로 실렌더한다:

```bash
python3 scripts/scaffold.py /tmp/smoke --style <이름> --title "스모크" --length short
# outline·chapters에 표·코드·콜아웃·리스트가 다 들어간 짧은 검증 콘텐츠를 넣고
python3 scripts/build.py /tmp/smoke && python3 scripts/qc_gate.py /tmp/smoke
python3 scripts/contact_sheet.py /tmp/smoke/draft/book.pdf /tmp/smoke/qc --dpi 85
# 대비 계약 린터(G16-LINT)는 qc_gate가 자동으로 부른다. 축① 완전성은 qc_gate에서
# WARN이므로, **스타일 팩을 고친 뒤에는** 전 요소를 밟는 이 스모크 북에서 직접 돌려
# MISSING까지 0으로 만든다 — 그 축이 강제력을 갖는 자리가 여기다:
python3 tests/lint_contrast.py /tmp/smoke
python3 tests/mutations/run_mutations.py /tmp/smoke   # 게이트 감도 회귀
python3 tests/test_wcag_parity.py                    # wcag.mjs ↔ g16_tokens.py 동치(대비 산술 복제본)
```

`scripts/wcag.mjs`는 `scripts/g16_tokens.py`의 대비 산술(`contrast_floor`·`is_bold_font`·
상대휘도)을 **복제**한 것이다 — 도해 렌더는 node에서 돌아 python을 import할 수 없다.
둘 중 한쪽 값을 고치면 반드시 다른 쪽도 고치고 위 동치 테스트를 돌릴 것(G16-SYNC는
이 어긋남을 보지 못한다).

렌더 PNG를 눈으로 확인하기 전까지 완료가 아니다.

`contrast_contract`를 손댔다면 린터의 세 축이 각각 무엇을 잡는지 알고 볼 것:
① 완전성(theme.css 규칙 ↔ 계약 엔트리 양방향 diff) ② pt 정합(계약이 신고한 급수가
theme.css에 실재하는가 — pt는 `contrast_floor`의 입력이라 위조하면 계약이 스스로
하한을 낮춘다) ③ 값 커버리지(theme.css의 모든 `color:`/`background:` 리터럴이 어떤
엔트리에든 등장하는가 — 원고와 무관해 새 색의 조용한 추가를 잡는다).
②③과 유령 엔트리는 `qc_gate`가 `fails`로 올린다(HTML 엔진 한정, typst는 명시 skip).
