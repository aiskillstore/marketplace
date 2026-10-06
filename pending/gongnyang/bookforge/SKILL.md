---
name: bookforge
description: Generate commercial-book-quality Korean ebook PDFs from a topic or a finished manuscript. Six design styles (practical, insight, academic, essay, business, magazine) with real book anatomy — cover, TOC with page numbers, chapter openers, running heads, QC gates. Use when the user wants an ebook, a PDF book or report, book typesetting, or mentions 전자책, PDF 책, 책 조판, 북포지, bookforge.
---

# bookforge — 상업도서급 전자책 PDF 공장

주제 한 줄 또는 완성 원고를 받아, 실제 단행본 해부 구조(표지·차례·장 도비라·러닝 시스템·판권면)를 갖춘 PDF를 만든다. 콘텐츠는 마크다운으로만 쓰고, 조판은 스타일 팩과 스크립트가 전담한다. 품질은 QC 게이트가 물리적으로 강제한다 — 게이트를 통과하지 못한 PDF는 `final/`에 존재할 수 없다.

이 파일의 경로가 `<SKILL>`이다. 모든 명령은 `<SKILL>`을 이 스킬 폴더의 절대 경로로 치환해 실행한다.

## 실행 전 점검

```bash
typst --version        # 0.14.x 필요 (Typst 트랙 — 내장 폰트가 버전에 묶이므로 0.14 계열 고정)
python3 -c "import pymupdf, markdown_it"   # PyMuPDF + markdown-it-py (QC·변환)
# HTML 트랙(insight·magazine) + 도해 프리렌더: 전역 playwright + Chromium 실물이 전제다.
# (스크립트가 `npm root -g`에서 playwright를 해석한다 — 프로젝트 로컬 설치로는 안 잡힌다)
npm root -g >/dev/null                                       # npm 자체
node -e "require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright')" \
  || npm i -g playwright                                     # 전역 playwright
npx playwright install chromium                              # Chromium 바이너리 (없으면 pass1에서 죽는다)
# 도해(diagrams/)를 쓰는 책: 렌더러는 커밋된 벤더 번들(vendor/antv-ssr.bundle.mjs)을
# 쓴다 — npm ci 불필요, 레지스트리 소멸에도 재현. 번들 유실 시에만 복구:
ls <SKILL>/vendor/antv-ssr.bundle.mjs \
  || (cd <SKILL> && npm ci && node vendor/build-bundle.mjs)
```

없는 것이 있으면 사용자에게 설치를 요청하고 중단한다. HTML 트랙·도해 없이 Typst 4스타일만 쓸 거라면 playwright·Chromium·npm ci는 생략 가능.

## 파이프라인 (체크리스트를 복사해 진행하며 체크)

```
[ ] P0 계약: 모드·스타일·분량 확정 → 책 프로젝트 스캐폴드
[ ] P1 콘텐츠: outline.json + chapters/ch-NN.md 완성
[ ] P1.5 도해(선택): diagrams/fig-NN.json 작성 → build.py가 자동 프리렌더 (계약: references/diagrams.md)
[ ] P2-3 빌드: build.py → draft/book.pdf
[ ] P4 게이트: qc_gate.py PASS → final/ 생성 확인
[ ] P5 시각 검수: contact_sheet.py → 표지·차례·도비라·본문 4면 이상 눈으로 확인
```

## P0 — 계약

1. **모드 감지**: 사용자가 원고 파일(md/txt/docx)을 줬으면 manuscript 모드 → [modes/manuscript.md](modes/manuscript.md)를 읽고 따른다. 주제·아이디어만 줬으면 topic 모드 → [modes/topic.md](modes/topic.md)를 읽고 따른다.
2. **스타일 선택**: 사용자가 지정하지 않았으면 아래 표에서 내용 성격에 맞는 것을 골라 진행한다(질문하지 않는다).

| 스타일 | 성격 | 판형 | 엔진 |
|---|---|---|---|
| `practical` | IT·실용 활용서, 단계별 가이드, 용어집 | 153×225 | typst |
| `insight` | 기술 동향·인사이트 리포트, 데이터 브리핑 | 182×257 | html |
| `academic` | 학술 단행본, 연구 개론, 이론서 | 153×225 | typst |
| `essay` | 산문집, 회고, 문학적 글 | 128×188 | typst |
| `business` | 컨설팅 리포트, 시장 분석, 전략 백서 | 200×280 | typst |
| `magazine` | 트렌드북, 큐레이션, 룩북 | 200×265 | html |

3. **스캐폴드** (책 프로젝트는 스킬 폴더 밖 작업 디렉토리에 만든다):

```bash
python3 <SKILL>/scripts/scaffold.py <book_dir> --style practical \
  --title "제목" --subtitle "부제" --length short --author "저자" --date "2026-08"
```

`--length`: short/standard/long — **쪽수 범위의 정본은 각 스타일 `tokens.json`의 `length_pages`**(short는 스타일별 22~70쪽 대역, INV-1에 따라 산출물 쪽수는 WARN만). `--brand "#hex"`로 브랜드색 교체, `--images vector|generated|none`으로 이미지 정책(벡터만·생성 아트 포함·없음) 지정.

## P1 — 콘텐츠 계약

`outline.json`의 각 장에 `file`·`title`·`summary`(도비라에 실리는 1~2문장)를 채우고, `chapters/ch-NN.md`를 아래 문법만으로 쓴다:

- `# 장제목`(파일당 1개, outline의 title과 일치) / `##` 절 / `###` 소제목
- 문단, `**볼드**`, 리스트, `> 인용`, GFM 표, ``` 코드블록
- 이미지: `![캡션](../assets/파일.png "출처: 어디")` — 파일을 `<book_dir>/assets/`에 먼저 넣고, **반드시 `../assets/` 경로 + 이미지 단독 문단**으로 쓴다(텍스트가 섞이면 조판에서 조용히 증발)
- 벡터 도해 2트랙: ① 요점 시각화는 `diagrams/fig-NN.json`(AntV DSL 사이드카) ② 기술도해(시퀀스·상태머신·ER·스위밍레인·간트 등)는 SVG를 직접 그려 `diagrams/fig-NN.svg` + 사이드카 `{"kind":"authored"}`. 빌드가 정규화해 `assets/fig-NN.svg`로 산출. 본문 참조는 `![캡션](../assets/fig-NN.svg "출처: …")`. 작성 계약·타입 라우팅·커넥터 규칙·복잡도 예산은 [references/diagrams.md](references/diagrams.md)가 정본
- 콜아웃(줄 단위 디렉티브):

```
::: tip 제목
내용 (stat은 첫 줄=수치, 둘째 줄=설명)
:::
```

종류 `info|tip|warn|quote|stat|pull`(pull은 magazine 풀퀘트 — **본문에 실재하는 문장만**, 없는 인용은 G10 하드 실패).
- 표 캡션: 표 **바로 앞 문단**에 `[표] 제목 | 자료: 출처` 한 줄 — 이 줄을 준 표만 번호 라벨이 붙는다. 캡션 없는 표는 라벨 없이 렌더된다(자동 필러 캡션은 존재하지 않는다).
- `stat`의 수치는 같은 장 본문에 실재해야 한다(G10) — 박스에만 있는 숫자는 날조로 판정된다.

표지·도비라용 생성 아트를 쓸 경우 [references/art-policy.md](references/art-policy.md)를 읽고 따른다(무텍스트 원칙).

완료 기준: outline의 모든 장 파일이 존재하고, 각 파일 첫 줄이 `# {title}`이며, 분량 프리셋에 맞는 총 글자수(short 기준 본문 1.0만~2.1만 자 = 장 5~7개 × 2,000~3,000자 — modes/topic.md와 동일 기준)를 갖춘다. 각 장의 `toc_line`(목차 전용 완결 카피 한 줄)을 채운다 — 없으면 summary 앞 40자가 잘려 실린다.

## P2-4 — 빌드와 게이트

```bash
python3 <SKILL>/scripts/build.py <book_dir>          # → draft/book.pdf
python3 <SKILL>/scripts/qc_gate.py <book_dir>        # PASS 시에만 final/<slug>.pdf 생성
```

게이트: G10 인용·수치 실재(렌더 전) / G0 도해 SVG 소스(렌더 전 — foreignObject·외부참조·단독문단·아이콘 탈락) / G1 렌더·판형(tokens `trim_mm` 대조)·**본문 급수(tokens `body_pt` ±0.3pt — 전역 축소 차단)**·분량범위(WARN — `--strict-pages`만 HARD) / G2 폰트 임베드+Type3 0 / **G3 면 기하 3축**(OVERFLOW 재단 밖 bbox 0 · COLLIDE 텍스트 라인 교차 0 · FIT 앞부속 텍스트가 tokens `front_frame_mm` 안) / G4 목차·북마크 정합 / G7 밀도(백면·꼬리 채움·판면 드리프트) / G8 공기 채움 / G9 제목 고립·widow / G11 사유 코드 무결성 / G12 필러 백면 / G13 도해 라벨 PDF 실재 / G17 도해 면 정합(figure가 한 면 안 — 면 분단·판면 초과·`diagram.maxHeightMm` 대조) / G14 목차·디자인 정합(인쇄 목차 쪽번호↔폴리오·목차↔도비라 색 계열·텍스트 대비 하한) / **G16-TOKENS 스타일 팩 토큰 계약 3축**(SYNC 색·수치 계약 정합 — `palette_roles`·`front_frame_mm` 선언값 타당성 포함 / CONTRAST 선언 페어의 WCAG 대비 / BRAND 브랜드 입력 사전 검증) / **G16-LINT `contrast_contract` ↔ theme.css·렌더 DOM 실물 대조**(html 엔진 한정 — pt 정합·값 커버리지는 HARD, 완전성은 WARN). 기준 수치와 대응법은 [references/pagination.md](references/pagination.md)가 정본이다.

실패 시 `gate-report.json`의 원인 항목만 고치고 재실행한다. **예외 — G16-TOKENS**: 이 축만 `build.py`가 렌더 전에 그 자리에서 중단시키므로 그 시점엔 `gate-report.json`이 아직 없다(있다면 이전 실행의 낡은 파일이다). stderr에 찍힌 축·사유를 읽고 `styles/<style>/tokens.json`을 고칠 것 — 게이트 리포트를 찾지 말 것. **금지 대응**: 분량 미달을 부록·용어집 추가로 메우기, 절별 강제 개면, 빈 줄·행간 확대로 면 채우기 — 전부 게이트가 다시 잡는다. 올바른 대응: G7 꼬리 미달은 `python3 <SKILL>/scripts/refit.py <book_dir>`(자간 미세조정 자동 탐색) → 해 없으면 문단 1~2개 국소 증감 또는 `pageroles.json` 사유 코드(의도된 여백 선언, G11이 진위 검증). 같은 게이트 3회 연속 실패면 원인을 사용자에게 보고한다.

## P5 — 시각 검수 (필수, 생략 금지)

```bash
python3 <SKILL>/scripts/contact_sheet.py <book_dir>/final/*.pdf <book_dir>/qc --dpi 90 --pages 1,2,3,4,5
# 게이트 실패를 진단할 때는 final/ 대신 draft/book.pdf 를 같은 방식으로 렌더해 본다
```

표지·차례·도비라·본문 펼침면 PNG를 직접 열어 보고 판단한다: 글자 겹침 없음, 목차 쪽번호=실제 쪽, 도비라 스타일 성립, 본문 여백 리듬 정상. 이상이 있으면 콘텐츠(md)나 book.json을 고쳐 P2-4를 재실행한다. **파일이 생성되었다는 것은 완료가 아니다 — 눈으로 본 것만 완료다.**

## 더 읽을 것 (필요할 때만)

- [modes/topic.md](modes/topic.md) — 주제만 받았을 때: 조사→목차→집필 절차
- [modes/manuscript.md](modes/manuscript.md) — 원고를 받았을 때: 인제스트·장 분할 절차
- [references/pagination.md](references/pagination.md) — **배치 규칙서(정본)**: 채움/비움의 사유, 레버 사다리, 밀도 게이트 수치, 사유 코드
- [references/art-policy.md](references/art-policy.md) — 생성 아트(표지·도비라) 규칙: 무텍스트 원칙, 스타일별 사용처
- [references/orchestration.md](references/orchestration.md) — (Claude Code 전용, 선택) 장별 집필을 codex 스웜·서브에이전트로 병렬화하는 법
- [references/extending.md](references/extending.md) — 새 스타일 팩 추가·테마 수정 가이드
- `styles/<이름>/STYLE.md` — 각 스타일의 전체 디자인 규칙서(집필 시 톤·구성 참고)
