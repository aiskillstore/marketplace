---
name: design-lint
description: "결정론적(no-LLM) 디자인 안티패턴 린터. 렌더된 HTML/CSS(또는 standalone 프로토타입 HTML, 라이브 URL)를 DESIGN-TOKENS.md Ground Truth 대비 검사해 토큰 위생·색/폰트/스페이싱 일관성·AI-default 클리셰(beige 배경·text gradient·uppercase eyebrow 등)를 pass/fail로 판정한다. LLM 디자인 리뷰는 비재현적이라 게이트로 못 쓰지만 이 스킬은 동일 입력→동일 판정·0토큰이라 CI/파이프라인 게이트로 쓸 수 있다. '/design-lint', '디자인 린트', '디자인 검사', '토큰 위생 검사', 'design-lint', '안티패턴 검사', 'AI-default 검사', '디자인 일관성 검사' 언급 시, 그리고 리팩토링/리디자인 파이프라인이 시각 산출물을 검증할 때 호출한다."
argument-hint: "[HTML 파일/글롭 또는 URL] [--tokens docs/design/DESIGN-TOKENS.md] [--gate] [--max-colors N]"
allowed-tools: Bash, Read, Glob, mcp__playwright__browser_navigate, mcp__playwright__browser_resize, mcp__playwright__browser_evaluate
---

# DESIGN-LINT — 결정론적 디자인 안티패턴 린터

> **요구사항**: detector 스크립트는 Node.js 18+ 로 실행한다(ESM `.mjs`, `realpathSync`/`fileURLToPath` 사용). 외부 npm 의존은 0개. 라이브 URL 검사 경로는 동봉된 playwright MCP(`.mcp.json`)를 사용한다.

```
RESOLVE INPUT → RUN DETECTORS(script) → REPORT → [GATE VERDICT]
```

**존재 이유**: "내 디자인 리뷰해줘"는 LLM이 매번 다르게 답해 *게이트로 쓸 수 없다*. 같은 안티패턴 목록을 **순수 함수**로 강제하면 동일 입력→동일 판정·0토큰·CI 실행 가능한 진짜 게이트가 된다. 이건 impeccable "anti-pattern ban list"의 **고레버 절반**(목록을 프롬프트가 아니라 *탐지기*로). LLM 판단 critic의 결정론 버전이라 보면 된다 — 코드/디자인 수정은 하지 않고 판정만 한다.

**경계**

| | LLM 디자인 리뷰 | **design-lint** |
|---|---|---|
| 재현성 | 매번 다름 | 동일 입력→동일 출력 |
| 비용 | 토큰 소모 | 0토큰(스크립트) |
| 게이트 적합 | 부적합 | exit code로 CI 게이트 |
| 잡는 것 | 주관적 미감 | 객관적 안티패턴·토큰 위생 |

> design-lint는 **객관적으로 검증 가능한 것만** 잡는다. "이 레이아웃이 우아한가" 같은 주관 판단은 범위 밖 — 그건 사람/디자인 리뷰 몫이다. 둘은 상보적이다. (`frontend-design` 스킬이 함께 설치돼 있으면 주관적 미감 방향은 그쪽에 맡기고 이 스킬은 객관 게이트만 담당한다.)

---

## Phase 0: PARSE

| 인자 | 기본값 | 설명 |
|---|---|---|
| 입력 (첫 비플래그) | `docs/design/prototype/*.html` | 검사할 HTML 글롭, 또는 `http(s)://` URL |
| `--tokens {경로}` | `docs/design/DESIGN-TOKENS.md` 자동탐색 | 토큰 위생 검사 기준. 없으면 **hygiene 스킵**(false positive 방지) |
| `--gate` | OFF | error 발견 시 비-제로 종료로 호출 파이프라인을 막는다 |
| `--max-colors N` 등 | references 참조 | 임계값 오버라이드 |

---

## Phase 1: RESOLVE INPUT

1. 입력이 `http(s)://`이면 → **Playwright로 렌더 후 정규화**한다. (라이브 사이트·배포본 검사 경로)
   - **뷰포트 고정 필수** — box 측정(w/h/maxWidth)은 뷰포트 의존이라 고정 안 하면 결정론이 깨진다. `browser_resize`로 **1280×800**을 먼저 박는다(반응형 판정이 필요하면 데스크탑+모바일 2개 고정 뷰포트로).
   - `browser_navigate` → 임시 HTML: `browser_evaluate`로 `document.documentElement.outerHTML` 덤프를 `<style>` 인라인 형태로 저장(정규식 detector 입력).
   - **computed-style 관측**(Group A: 대비비·box-model·구조): `node scripts/design-lint.mjs --observe-snippet`로 수집 스니펫 문자열을 얻어 그대로 `browser_evaluate`에 주입 → 반환된 관측 배열(JSON)을 `obs.json`으로 저장 → 본 실행에 `--observed obs.json`으로 전달한다. (playwright npm 의존 0 — computed-style COLLECT_SNIPPET 패턴)
   - `--observed` 없이 실행하면 Group A detector는 **skip**(report `observed: skipped`)되고 정규식 detector만 돈다. 라이브URL 경로에서만 대비비/box-model이 활성된다.
2. 입력이 글롭이면 → Glob으로 파일 목록 확정. 0개면 사용자에게 경로 확인.
3. `--tokens` 미지정 시 `docs/design/DESIGN-TOKENS.md`를 Glob으로 자동탐색. 있으면 토큰 위생 ON, 없으면 OFF(경고만).

> **왜 standalone HTML이 1차 입력인가**: framework-neutral standalone HTML(예: 프로토타입 산출물)을 Ground Truth로 삼으면 프레임워크 빌드 없이 즉시 검사 가능하다. 인라인 `<style>` 기반 프로토타입이면 정규식 detector가 바로 돈다.

---

## Phase 2: RUN DETECTORS

번들 스크립트를 실행한다 (LLM 호출 없음):

```bash
node ${SKILL_DIR}/scripts/design-lint.mjs <파일들> [--tokens <경로>] [--md]
```

스크립트는 각 detector를 `(harvest, ctx) => Finding[]` 순수 함수로 돌려 `{id, severity, msg, evidence, file}`를 모은다. **severity=error는 게이트를 막고, warn은 보고만 한다.** 현재 **47개 전부 구현**, 전체 분류는 `references/detectors.md` 참조. 정규식 detector는 standalone HTML에서 바로 돌고, Group A(대비비 D-COLOR-05/06·box-model D-A11Y-02/D-SPACE-03·구조 D-LAYOUT-03/04·런타임 오버플로우 D-LAYOUT-08~11)는 `--observed`(라이브 URL computed-style 수집, Phase 1 참조) 있을 때만 활성·없으면 skip. 색만으로 상태 구분(구 D-A11Y-03)은 DOM 자식 콘텐츠가 필요해 **폐기**했다(재구현 금지 — detectors.md).

스크립트 출력(JSON)을 받아 그대로 신뢰한다. **임의로 detector를 추가 판단하지 말 것** — 결정론성이 이 스킬의 전부다. 새 규칙이 필요하면 `detectors.md`에 정의하고 스크립트에 함수로 추가한 뒤 정량 케이스(양성/음성 HTML)로 precision/recall을 검증한다(프롬프트로 때우지 않는다).

---

## Phase 3: REPORT

```
🔎 design-lint — {PASS|FAIL}
─────────────────────────────
검사 파일:   {N}개
토큰 위생:   {checked|skipped}
detector:    47종 구현 ({run} 함수 실행)
판정:        error {E} · warn {W}
─────────────────────────────
[error] D-COLOR-02  토큰 외 하드코딩 색 7종 — prototype/02.html
        #d94f3a #2ecc71 ...
[warn]  D-AIDEFAULT-01  beige 배경 — prototype/01.html
...
```

- **error 0** → PASS. **error ≥1** → FAIL.
- error는 "토큰 위생 위반"처럼 *객관적 계약 위반*만. 클리셰(beige·gradient text 등)는 warn(맥락상 의도일 수 있음).

---

## Phase 4: GATE (호출 파이프라인용)

**exit code 계약** — `--gate`가 있을 때만 error 발견 시 **비-제로(1) 종료**한다. `--gate` 없이 실행하면 error가 있어도 **항상 exit 0**(순수 리포터) — 판정은 JSON `verdict`/`summary.error`에 담긴다. 그래서 standalone `/design-lint`는 보고만 하고, 파이프라인만 게이팅된다.

| 호출처 | 호출 형태 | 삽입 지점 | FAIL 판정 시 |
|---|---|---|---|
| CI / verify 스텝 | `--gate` | 빌드/검증 스크립트 내(시각 산출물 존재 시) | 비-제로 종료로 파이프라인 차단 |
| 리팩토링·리디자인 등 후속 워크플로우 | `--gate` | 시각 검증 단계(스크린샷 회귀와 병행 가능) | JSON `summary.error ≥ 1` → 재수정 이슈로 환류 |
| standalone | 플래그 없음 | `/design-lint` 직접 | 보고만 (exit 0) |

> 호출 측은 exit code뿐 아니라 **JSON `verdict`/`summary.error`를 읽어 판정**할 수 있다(모델 오케스트레이션 파이프라인은 셸 `&&`가 아니라 출력을 읽는 구조가 자연스럽다). `--gate`의 비-제로 종료는 CI/셸 게이트 신호다.

> warn은 게이트를 막지 않는다 — 안티패턴이 의도적 디자인 결정일 수 있으므로 사람이 본다. **error(객관적 계약 위반)만 자동 차단**한다. 이 분리가 false-positive로 파이프라인을 막지 않게 하는 핵심이다.

---

## 검증

이 스킬의 가치는 "detector가 실제 안티패턴을 잡고 깨끗한 디자인은 통과시키는가"로 판정한다. 안티패턴을 심은 HTML / 깨끗한 HTML / 토큰 위생 위반 fixture로 **precision(거짓양성 없음)·recall(놓침 없음)**을 정량 확인한 뒤 detector를 확장한다. 확장 절차는 `references/detectors.md`의 "확장 원칙" 참조.

## 주의사항

- **결정론 유지가 최우선** — detector는 전부 순수 함수. LLM 추론을 섞으면 게이트 가치가 사라진다.
- **토큰 없으면 hygiene 스킵** — DESIGN-TOKENS.md 없는 프로젝트에서 모든 색을 error로 잡으면 노이즈. 명시적으로 끈다.
- **standalone HTML 범위** — 정규식 파싱은 인라인 `<style>` 프로토타입에 충분. 복잡한 외부 CSS·빌드 산출물은 Playwright computed-style 경로로 정규화 후 검사.
