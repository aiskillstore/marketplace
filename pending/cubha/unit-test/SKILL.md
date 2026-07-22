---
name: unit-test
description: "기능 단위 테스트 오케스트레이터. Git Diff/사용자 지정 범위에서 테스트 대상을 결정하고, 사용자 시나리오 스토리보드 → 테스트케이스 생성 → Playwright MCP 실행 → 결과 보고. '/unit-test', '단위테스트', '테스트해줘', '기능 테스트' 등 언급 시 호출. 시나리오 단위 회귀 검증(PASS/FAIL/WARN)에 사용하며, 버그 원인 특정·로그 삽입 디버깅이 필요하면 debugger 계열 스킬을 쓴다."
argument-hint: "[테스트 대상 기능명 또는 범위] [--happy-only] [--auto] [--fix] [--no-ux-review] [--strict-visual] [--gate-visual]"
---


# UNIT-TEST 기능 단위 테스트

$ARGUMENTS 에 대해 아래 파이프라인을 실행한다.

```
SCOPE → STORYBOARD → GENERATE → EXECUTE (+ 4.5 VISUAL-UX) → REPORT
```

---

## 분기 — 검증 vs 디버깅

| 상황 | 사용 방식 | 이유 |
|---|---|---|
| 기능이 의도대로 동작하는지 **검증** (PASS/FAIL/WARN) | `/unit-test` | 시나리오 단위 회귀 검증 |
| 버그 현상 발생 — **원인 특정** 필요 | 디버깅 워크플로우(예: debugger 스킬) | 가설 도출 → 로그 삽입 → 재현 → 수정/정리 |
| 신규 구현 직후 동작 확인 | `/unit-test --happy-only` | 빠른 정상 흐름 검증 |
| FAIL 발견 후 원인 추적·수정 | 디버깅 워크플로우로 전환 | unit-test는 **검증만**, 로그 삽입·정리 미수행 |

> `--fix` 플래그가 있어도 unit-test는 단순 재실행(최대 2회)만 수행. 원인 분석·로그 삽입·grep 검증이 필요하면 디버깅 워크플로우로 전환한다.

> **정적 단위 테스트 게이트와의 관계 (네이밍 주의)**: 이 스킬은 이름은 "unit-test"지만 실제로는 **Playwright 기반 E2E/시나리오 동적 검증**이다. vitest/jest 같은 정적 단위 테스트와는 레이어가 다르다 — 둘은 충돌이 아니라 **상보**다. 정적 단위 테스트(`npm test`)는 CI/빌드 게이트에서, 시나리오 동적 검증은 이 스킬에서 담당한다.

---

## 옵션 플래그

| 플래그 | 설명 |
|---|---|
| `--happy-only` | Happy Path 시나리오만 생성 (빠른 검증) |
| `--auto` | 승인 없이 전체 파이프라인 연속 실행 |
| `--fix` | FAIL 발견 시 자동 수정 + 재검증 |
| `--no-ux-review` | Phase 4.5 Section B(LLM 폴리시 제안)만 스킵. Section A(design-lint 게이트)는 저비용이라 이 플래그와 무관하게 항상 실행(설치돼 있을 때) |
| `--strict-visual` | Phase 4.5 Section A에 design-lint `--strict`를 전달(형제 겹침 D-LAYOUT-11 활성, low-confidence 기본 off). design-lint 미설치 시 무의미 |
| `--gate-visual` | Phase 4.5 Section A에 design-lint `--gate-runtime`을 전달(문서 레벨 가로 오버플로우만 error로 격상 — 해당 시나리오를 FAIL 취급). design-lint 미설치 시 무의미 |

---

## Phase 1: SCOPE (테스트 범위 결정)

테스트 대상을 아래 우선순위로 결정한다.

| 우선순위 | 소스 | 조건 | 수집 방법 |
|---|---|---|---|
| 1 | **사용자 지정** | `$ARGUMENTS`에 명시적 범위 존재 | 인자 파싱 |
| 2 | **Git Diff** | 인자 미지정 시 | `git diff HEAD~1 --name-only` + `git diff --cached --name-only` → 변경 파일에서 기능 영역 추론 |
| 3 | **최근 작업 맥락** | Diff도 없을 시 (non-git 또는 clean 상태) | 프로젝트의 최근 완료 작업/이슈 기록(있으면)에서 대상 추론, 없으면 사용자에게 대상 확인 |

### 1-1. 변경 파일 분석

수집된 파일 목록에서:
1. 테스트와 무관한 파일 제외 (설정 파일, README, 스타일만 변경 등)
2. 남은 파일들의 **기능 영역** 분류 (컴포넌트, 훅, 유틸, 페이지 등)
3. 각 파일을 읽어 **사용자에게 노출되는 동작** 파악

### 1-2. 진입점 결정

프로젝트 설정(CLAUDE.md·README·package.json 스크립트 등)에서 개발 서버 포트를 확인하고, 대상 기능의 접근 경로를 결정한다.

### 1-3. 산출물

```
[테스트 범위]
대상 기능: {기능명}
소스: 사용자 지정 / Git Diff / 최근 작업 맥락
관련 파일: file1.tsx, file2.ts, ...
진입점 URL: http://localhost:{port}/{path}
선행 조건: {로그인 필요, 특정 데이터 존재 등}
```

---

## Phase 2: STORYBOARD (사용자 시나리오 설계)

대상 기능의 코드를 읽고 **실제 사용자가 수행할 동작 흐름**을 예측한다.

### 2-1. 시나리오 분류

| 유형 | 설명 | 예시 |
|---|---|---|
| **Happy Path** | 정상 흐름 (필수, 항상 포함) | 폼 입력 → 제출 → 성공 메시지 |
| **Edge Case** | 경계값·빈값·긴 문자열 | 빈 입력 제출, 특수문자 포함 |
| **Error Path** | 의도적 오류 유발 | 잘못된 형식 입력, 필수값 누락 |
| **Interaction** | 복합 인터랙션 | 드래그앤드롭, 키보드 단축키, 연속 클릭 |

> `--happy-only` 플래그 시 Happy Path만 생성한다.

### 2-2. 시나리오 작성

각 시나리오를 아래 형식으로 작성한다:

```
[S-{N}] {시나리오명}
유형: Happy Path / Edge Case / Error Path / Interaction
전제 조건: {초기 상태 — 페이지, 데이터, 로그인 등}
사용자 동작:
  1. {동작} → 기대 반응: {UI 변화}
  2. {동작} → 기대 반응: {UI 변화}
  ...
최종 기대 결과: {상태 / UI / 데이터}
```

### 2-3. 사용자 승인

시나리오 목록을 사용자에게 보여주고 피드백을 받는다.

| 응답 | 동작 |
|---|---|
| 승인 (`"ok"`, `"진행해"`) | Phase 3으로 진행 |
| 수정 지시 | 시나리오 추가/제거/수정 후 재승인 |
| 취소 | 파이프라인 중단 |

> `--auto` 플래그 시 승인 없이 즉시 Phase 3으로 진행한다.

---

## Phase 3: GENERATE (테스트케이스 생성)

승인된 시나리오를 **Playwright MCP 명령 시퀀스**로 변환한다.

### 3-1. 시나리오별 생성 항목

| 항목 | 내용 |
|---|---|
| **입력 데이터** | 각 인터랙션에 사용할 구체적 값 (텍스트, 클릭 대상, 키 조합) |
| **기대 출력** | 스냅샷에서 확인할 요소 (텍스트 내용, ARIA 속성, 요소 존재/부재) |
| **검증 기준** | PASS/FAIL 판정 조건 (정확히 어떤 상태를 확인하는지) |
| **MCP 명령 시퀀스** | Playwright MCP 도구 호출 순서 |

### 3-2. 명령 시퀀스 구성 규칙

```
시나리오 시작:
  → browser_navigate(url)          # 초기 상태로 이동
  → browser_snapshot()             # 초기 상태 확인

동작 수행:
  → browser_click(element)         # 클릭
  → browser_type(element, text)    # 텍스트 입력
  → browser_press_key(key)         # 키보드 입력
  → browser_select_option(...)     # 셀렉트 변경

검증:
  → browser_snapshot()             # 결과 상태 캡처
  → browser_console_messages()     # 콘솔 에러 수집
  → 기대 출력과 비교               # PASS / FAIL 판정
```

### 3-3. 검증 판정 기준

| 조건 | 판정 |
|---|---|
| 기대 요소 존재 + 콘솔 에러 없음 | **PASS** |
| 기대 요소 존재 + 콘솔 경고만 있음 | **WARN** |
| 기대 요소 부재 또는 콘솔 에러 존재 | **FAIL** |

> 이 표는 **기능(콘솔·DOM) 판정 전용**이며 상태값(PASS/FAIL/WARN)은 이 조건에서만 바뀐다. "동작은 정상인데 시각적으로 깨진 것"(오버플로우·텍스트 잘림·버튼 텍스트 초과)은 이 표를 건드리지 않는다 — Phase 4.5에서 **별도 애노테이션**(`🎨 UX결함`)으로만 부가한다. 두 레이어를 섞지 않는 이유: 기능 회귀와 시각 폴리시는 원인·수정 담당·긴급도가 다르고, 섞으면 "왜 PASS였던 시나리오가 갑자기 FAIL됐지"를 콘솔 에러 때문인지 레이아웃 때문인지 구분 못 하게 된다.

### 3-4. 안전장치

- 스냅샷 전 **핵심 DOM 요소 존재 확인** — SPA 라우팅/렌더링 완료 대기
- 비결정적 데이터(타임스탬프, UUID 등)는 **존재 여부만** 검증, 정확한 값 비교 제외
- 암호화 필드는 **UI 레벨 표시값**으로만 검증

---

## Phase 4: EXECUTE (테스트 실행)

### 4-0. 사전 체크

**① 테스트용 백엔드 서비스 확인 (해당 시)**

테스트에 DB·Redis 등 백엔드 서비스가 필요하면, 프로젝트의 기존 방식(예: `docker-compose up -d`, 로컬 서비스, `.env`의 테스트용 접속 정보)으로 기동한다. 이 스킬은 별도 인프라를 제공하지 않는다 — 운영 데이터를 건드리지 않도록 **테스트 전용 인스턴스/DB**를 사용하는 것을 권장한다.

- 백엔드가 필요 없는 순수 프론트엔드/정적 대상이면 이 단계는 스킵.

**② 개발 서버 실행 여부 확인**

`browser_navigate` → 진입점 URL

**미실행 시** → 사용자에게 안내 후 파이프라인 중단

```
⚠ 개발 서버가 실행되지 않았습니다.
→ 개발 서버를 실행한 후 다시 /unit-test 를 실행해 주세요.
```

### 4-1. 실행 루프

각 시나리오를 순서대로 실행한다:

```
for each scenario S-{N}:
  1. browser_navigate → 초기 URL (매 시나리오마다 초기화)
  2. browser_snapshot → 초기 상태 확인
  3. 동작 시퀀스 실행 (click, type, press_key 등)
     - 각 동작 후 필요 시 중간 스냅샷으로 상태 확인
     - 시나리오 유형이 Interaction(드래그앤드롭·키보드단축키·연속클릭 등 과도기 상태가 있는 유형)이면
       중간 스냅샷 시점에도 Phase 4.5 Section A를 조건부 실행한다 — 드롭다운 열림·호버 툴팁처럼
       "동작 중"에만 나타나고 최종 정착 상태에선 사라지는 시각 결함은 최종 스냅샷만 봐서는 놓친다.
  4. browser_snapshot → 최종 상태 캡처
  5. browser_console_messages → 에러 수집
  6. 기대 출력 vs 실제 결과 비교 → PASS / FAIL / WARN (기능 판정, 3-3 기준)
  7. Phase 4.5 VISUAL-UX 실행 → 이 시나리오의 시각 결함을 별도 애노테이션으로 수집 (상태값은 안 바꿈)
```

### 4-2. FAIL 처리

- 실패 시나리오의 **스냅샷 상태 + 콘솔 에러 + 기대값/실제값 차이**를 기록
- **다음 시나리오는 계속 진행** (전체 중단하지 않음)
- `--fix` 플래그 시: FAIL 발견 즉시 코드 수정 → 해당 시나리오만 재실행 (최대 2회)
- **Phase 4.5의 시각 결함(UX결함)은 `--fix` 트리거 대상이 아니다.** `--fix`는 기능 FAIL(3-3 기준: 기대요소 부재/콘솔에러) 전용이며, 시각 결함은 게이트가 아니라 보고 항목이므로 자동 수정 흐름에 섞이지 않는다.

### 4-3. Chrome DevTools MCP 에스컬레이션 (FAIL 원인 불명 시, 선택)

Playwright `browser_console_messages`로 원인 특정 불가 시, **chrome-devtools MCP가 설치돼 있으면** 순차 사용한다(이 플러그인은 playwright만 동봉하므로 chrome-devtools는 별도 설치 시에만 사용 가능).
**Playwright 도구 완료 후에만 호출** — 동시 사용 금지.

| 증상 | 사용할 DevTools 도구 |
|---|---|
| API 요청 실패 의심 | `getNetworkRequests` |
| 응답 데이터 확인 필요 | `getNetworkRequests` + 응답 바디 |
| 렌더링 성능 문제 | `getCoreWebVitals` |
| 원인 불명 — 현재 DOM 구조 확인 | `getDocument` |

DevTools 수집 완료 후 → Phase 5 REPORT에 원인 포함해서 보고. (chrome-devtools 미설치 시 이 단계는 스킵하고, 수집된 스냅샷·콘솔 정보만으로 보고한다.)

---

## Phase 4.5: VISUAL-UX (동작은 정상, 시각만 깨진 것 검사)

> **왜 별도 Phase인가**: Phase 3-3의 기능 판정(PASS/FAIL/WARN)은 "의도대로 동작하는가"만 본다. "동작은 되는데 인터랙션 후 섹션이 틀어지거나, 버튼 텍스트가 잘리거나, 카드가 겹치는" 건 기능 버그가 아니라 UX 결함이라 별도 레이어로 다룬다. 각 시나리오의 (최종, 그리고 Interaction 유형은 필요 시 중간) 스냅샷 직후 실행하며, **Section A/B는 신뢰수준이 다르므로 REPORT에서 항상 구분 표기**한다.

각 시나리오의 관측 대상 상태(4-1 step 3~4)에서:

### 사전 공통 — DOM 덤프 (Section A/B 공유 입력)

먼저 현재 상태의 DOM outerHTML을 인라인 `<style>` 형태로 1회 덤프한다. **이 덤프는 Section A(설치 시)와 Section B(실행 시) 양쪽이 재사용하므로, design-lint 설치 여부·`--no-ux-review` 여부와 무관하게 항상 생성한다(재수집 금지).**

### A. 결정론 게이트 — design-lint 런타임 detector (**design-lint 플러그인이 함께 설치돼 있으면**)

같은 마켓의 `design-lint` 플러그인이 설치돼 있으면 아래를 실행한다(미설치 시 Section A 전체 스킵 — 이 스킬은 자립적으로 동작하며 design-lint는 선택적 강화다):

1. `browser_evaluate('document.fonts.ready')`로 폰트 로딩 완료를 먼저 대기한다(웹폰트 스왑 전 관측은 폴백폰트 metric으로 인한 일시적 오버플로우 오탐을 유발).
2. design-lint의 `--observe-snippet`으로 관측 스니펫을 얻어 `browser_evaluate`에 주입 → 반환 배열을 `obs.json`으로 저장 (**뷰포트 1280×800 고정 필수** — Section A 전체의 결정론 전제).
3. design-lint를 `<dump.html>`(위 공통 덤프) `--observed obs.json [--strict-visual 시 --strict] [--gate-visual 시 --gate-runtime]`로 실행한다.
4. `D-LAYOUT-08`(가로 오버플로우) · `D-LAYOUT-09`(텍스트 잘림) · `D-LAYOUT-10`(버튼 텍스트 초과) · (`--strict-visual` 시) `D-LAYOUT-11`(형제 겹침, low-confidence) warn을 수집.
5. **판정에 영향 없음** — 기능 PASS는 그대로 유지, 발견된 항목은 시나리오에 `🎨 UX결함` 애노테이션으로만 부가한다. 단 `--gate-visual`로 문서 레벨(html/body) 가로 오버플로우가 error로 격상된 경우는 해당 시나리오를 예외적으로 FAIL 취급한다(명시적 opt-in 시에만).

> design-lint를 호출할 때 플러그인 설치 경로를 하드코딩하지 않는다 — 슬래시 커맨드/스킬로 노출된 형태를 사용하거나, 프로젝트에 스크립트가 존재하면 그 경로로 호출한다. 경로를 모르면 Section A를 건너뛰고 Section B(스크린샷 기반)만 수행한다.

### B. 폴리시 제안 — LLM 리뷰 (`--no-ux-review` 시 스킵)

- 입력: 현재 상태 스크린샷 + 위 공통 DOM 덤프(재수집 금지).
- `references/interface-polish-rules.md`의 9룰(concentric radius·optical alignment·shadow depth·text-wrap·font-smoothing·image outline·motion enter/exit 비대칭·press state·tabular-nums)을 참고해 "동작은 OK지만 미감이 아쉬운" 항목을 제안.
- **게이트 아님, 참고용(비재현)** — PASS/FAIL/WARN 상태값도, `--fix` 트리거도 건드리지 않는다.
- 비용 통제: Section A(설치 시)가 이미 결함을 찾은 시나리오만 우선 실행하거나(권장), `--no-ux-review`로 전체 스킵 가능. `--happy-only`와는 무관하게 저비용 항목은 유지하고 고비용 LLM 리뷰만 통제한다.

---

## Phase 5: REPORT (결과 보고)

### 5-1. 결과 요약

```
╔══════════════════════════════════════╗
║  Unit Test 결과                       ║
╠══════════════════════════════════════╣
║  대상: {기능명}                        ║
║  시나리오: {총}개 실행                  ║
║  ✅ PASS: {n}  ❌ FAIL: {n}  ⚠ WARN: {n} ║
║  🎨 UX결함: {n} (시각, 기능 상태 무관)   ║
╚══════════════════════════════════════╝
```

> `🎨 UX결함`은 Phase 4.5에서 수집된 시각 결함 개수다. **PASS/FAIL/WARN 집계와 별도**이며 콘솔 경고(기존 WARN)와 절대 합산하지 않는다 — 원인(콘솔 vs 시각)을 구분 못 하게 되는 걸 막기 위함.

### 5-2. 시나리오별 상세

```
[S-1] ✅ {시나리오명} — PASS
[S-2] ❌ {시나리오명} — FAIL
  ├ 실패 지점: 동작 {N} 이후
  ├ 기대: {기대 상태}
  ├ 실제: {실제 상태}
  └ 콘솔: {에러 메시지 또는 "없음"}
[S-3] ⚠ {시나리오명} — WARN
  └ 경고: {콘솔 경고 내용}
[S-4] ✅ {시나리오명} — PASS  🎨 UX결함 2건
  ├ [A/게이트] D-LAYOUT-09 텍스트 잘림(말줄임 없음): .card-title
  ├ [A/게이트] D-LAYOUT-10 버튼 텍스트 초과: button.submit
  └ [B/제안·비재현] .cart-count에 tabular-nums 권장(자릿수 변할 때 흔들림)
```

### 5-3. 후속 액션

| 결과 | 동작 |
|---|---|
| 전체 PASS | 완료 메시지 출력 |
| FAIL 존재 + `--fix` | 자동 수정 시도 (Phase 4-2에서 이미 처리) |
| FAIL 존재 + `--fix` 없음 | 사용자에게 수정 여부 확인 |

사용자 응답:

| 입력 | 동작 |
|---|---|
| `"수정해줘"` | 실패 원인 분석 → 코드 수정 → 실패 시나리오만 재실행 |
| `"괜찮아"` / `"종료"` | 보고서 출력 후 종료 |

---

## Known Pitfalls

> 본 skill 실행 중 반복 발생한 실패 패턴. 신규 패턴 발견 시 entry를 추가한다.

_(현재 누적 entry 없음.)_

### 작성 형식
- **[패턴명]** — YYYY-MM-DD
  - **상황**: 어떤 단계(시나리오 생성/실행/검증)·조건에서 발생
  - **원인**: 무엇 때문에 실패 (시나리오 누락 / mock 오류 / 환경 문제 등)
  - **회피**: 다음 실행 시 적용할 가이드

---
