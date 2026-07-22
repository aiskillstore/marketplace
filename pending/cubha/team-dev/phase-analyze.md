# Phase 1: ANALYZE — 의존성 분석 및 그룹 분류 (상세)

## 1-1. SubTask 목록 수집

아래 순서로 SubTask를 확인한다:

1. TaskList 도구로 기존 등록된 Task 확인
2. 없으면 $ARGUMENTS에서 기능 설명 추출 → SubTask 단위로 분리
3. 분리 불가하면 AskUserQuestion으로 사용자에게 SubTask 목록 요청

### 1-1-1. TDD 적격 판단

각 SubTask에 아래 **3-AND 기준**을 모두 만족하면 `[TDD]` 태그를 붙인다:

1. **결정론적 입출력** — 입력에 대해 기대 출력이 명확히 정의 가능
2. **단위 테스트 러너 존재** — 프로젝트에 테스트 프레임워크(vitest·jest·pytest 등)가 이미 있음
3. **로직 중심** — 순수 함수·상태 변환·검증 규칙 등 비즈니스 로직

> **절대제외** (`--tdd`라도 태그하지 않음): UI 렌더링·E2E 흐름·탐색적 구현·비결정적 출력(LLM·랜덤·시각)·단위 러너 부재.

| 플래그 (Phase 0 파싱) | 동작 |
|---|---|
| 인터랙티브 (`--auto` 없음) | 적격 SubTask에 `[TDD]` → 1-6 승인게이트에 **제안** 노출 |
| `--auto` 단독 | 자동태그 OFF — 판단 생략, 전부 test-after |
| `--auto --tdd` | 판단함(제안 생략) → 적격 SubTask에 `[TDD]` 자동 부착 |
| `--no-tdd` | 판단·제안 모두 끔 |

> `[TDD]` SubTask는 Phase 2 DISPATCH에서 RED 마이크로플로우(실패 테스트 선작성→선커밋→구현)로 구현된다.

## 1-2. 컨텍스트 수집

병렬로 아래를 수집한다:

- **프로젝트 규칙 문서** — CLAUDE.md 등이 있으면 기술 스택, 구조, 규칙을 읽는다
- **프로젝트 구조** — 현재 디렉토리 트리, 주요 파일
- **기존 코드 패턴** — import 방식, 네이밍 컨벤션, 타입 정의 위치

## 1-3. UI/UX 설계 (UI SubTask가 1개 이상 포함된 경우)

**원칙**: 프로젝트에 이미 수립된 디자인 기준 파일(Ground Truth)이 있으면 그것을 참고하여 동일하게 진행하는 것이 기본이며, 기준이 없을 때만 디자인 탐색을 수행한다. `frontend-design` 같은 디자인 스킬이 설치돼 있으면 미매칭/신규 화면 설계에 활용할 수 있다.

### 1-3-1. Ground Truth 탐색 (병렬 Glob)

```
docs/design/DESIGN-TOKENS.md     ← canonical 토큰 (있으면 최우선)
docs/design/UX-BRIEF.md          ← 스토리보드·레이아웃 원칙
docs/design/prototype/*.html     ← 시각 기준 프로토타입
```

### 1-3-2. 분기 결정

**분기 A: Ground Truth 존재**

각 UI SubTask의 대상 화면을 `prototype/*.html`과 매칭하고 **SubTask-prototype 매핑 테이블**을 구성한다:

```
| SubTask ID | 대상 화면 | 매칭 prototype | 매칭 상태 |
|---|---|---|---|
| 1-1 | 상세 페이지 편집 | 03-detail.html | ✅ |
| 1-2 | 검색 결과 필터 | 04-search.html | ✅ |
| 1-3 | (신규) 설정 모달 | — | ❌ 미매칭 |
```

매칭 결과별 동작:

| 매칭 상태 | 동작 |
|---|---|
| **전 SubTask 매칭** | 디자인 스킬 호출 생략. 기준 파일 경로 + 매핑 테이블을 `[UI/UX 설계 명세]`로 emit |
| **일부 미매칭** | 미매칭 SubTask에 대해서만 디자인 스킬(설치 시) 호출 + **CONSISTENCY LOCK** 주입. 매칭 SubTask는 기준 파일 경로만 emit |
| **전부 미매칭** (대규모 신규) | 디자인 스킬(설치 시) 호출 (CONSISTENCY LOCK). 규모가 크면 전용 UI 프리비전 워크플로우 선행을 안내 |

**분기 B: Ground Truth 없음** (기존 프로젝트)

1. 기존 코드에서 토큰 추출: `app/globals.css`·`src/index.css` → `tailwind.config.*` → 기존 컴포넌트 순
2. 디자인 스킬(설치 시) 호출:
   - 토큰 추출 성공 → **CONSISTENCY LOCK** 주입
   - 추출 실패 → 자유 탐색
3. **Persist**: 구현 완료 후 사용 토큰을 `docs/design/DESIGN-TOKENS.md`로 저장 (없으면 생성). 다음 Phase부터는 분기 A로 진입

### 1-3-3. CONSISTENCY LOCK 블록

디자인 스킬 호출 시 프롬프트 최상단에 반드시 포함:

```
CONSISTENCY LOCK — OVERRIDE DEFAULT VARIATION DIRECTIVES.

This task extends an existing project with an established visual language.
You MUST reuse the EXACT tokens below (no variation allowed):

  --font-display / --font-body / --color-* / --space-* / --radius-* / --shadow-*
  (DESIGN-TOKENS.md 또는 추출 토큰 전체)

Context (for layout/interaction reference only):
  UX-BRIEF: {요약 또는 경로}
  관련 프로토타입: {경로 목록}

Task: layout/composition for the listed UI SubTasks ONLY.
Do NOT invent new fonts, colors, or aesthetic directions.
Match the established visual language 1:1.
```

### 1-3-4. 설계 산출물 emit

`[UI/UX 설계 명세]`는 Phase 2 팀원 프롬프트에 주입된다. 구조:

- **Ground Truth 경로**: DESIGN-TOKENS / UX-BRIEF 경로 (필수)
- **SubTask-prototype 매핑 테이블**: 위 1-3-2 표 (팀원이 자기 SubTask의 관련 prototype을 바로 Read 가능)
- **레이아웃·인터랙션·비주얼·접근성 명세**: 미매칭 SubTask에 대해 생성한 설계

## 1-4. 의존성 분석

각 SubTask 간 의존성을 분석하여 **병렬 실행 가능 그룹**으로 분류한다:

| 의존성 유형 | 판정 | 예시 |
|---|---|---|
| **같은 파일 수정** | 순차 (같은 그룹 불가) | SubTask A: types.ts 수정, SubTask B: types.ts 수정 |
| **타입/인터페이스 의존** | 순차 (생산자 먼저) | SubTask A: 타입 정의, SubTask B: 해당 타입 사용 |
| **컴포넌트 의존** | 순차 (하위 먼저) | SubTask A: Button 생성, SubTask B: Button 사용 |
| **독립 파일 수정** | 병렬 가능 | SubTask A: sidebar.tsx, SubTask B: editor.tsx |
| **독립 기능** | 병렬 가능 | SubTask A: 검색 기능, SubTask B: 설정 모달 |

## 1-5. 그룹 구성 결과 출력

```
📋 병렬 개발 계획
══════════════════════════════════
Task: {기능명}
총 SubTask: {N}개
병렬 그룹: {M}개
══════════════════════════════════

[그룹 1] 병렬 {n}개 — 기반 레이어
  ├── SubTask 1-1: {설명} → {파일}
  ├── SubTask 1-2: {설명} → {파일}
  └── SubTask 1-3: {설명} → {파일}

[그룹 2] 병렬 {n}개 — 그룹 1 의존 (대기)
  ├── SubTask 2-1: {설명} → {파일} (← SubTask 1-1 의존)
  └── SubTask 2-2: {설명} → {파일} (← SubTask 1-2 의존)

[그룹 3] 순차 1개 — 통합 레이어
  └── SubTask 3-1: {설명} → {파일} (← 전체 의존)

══════════════════════════════════
```

## 1-6. 사용자 승인

AskUserQuestion으로 승인을 요청한다:

| 응답 | 동작 |
|---|---|
| 승인 | Phase 2로 진행 (일반 모드) |
| 승인 + `--auto` | auto 모드 ON — 그룹 간 확인 없이 연속 진행 |
| 수정 지시 | 그룹 재구성 후 1-4 재출력 |
| `stop` | 중단 |

> **`[TDD]` 제안 노출** (인터랙티브 한정): 1-1-1에서 `[TDD]` 태그한 SubTask를 그룹 출력에 표시하고, 이 승인 시점에 사용자가 태그를 빼거나 추가하게 한다. `--auto --tdd`는 제안 없이 자동 부착분이 그대로 Phase 2로 간다.
