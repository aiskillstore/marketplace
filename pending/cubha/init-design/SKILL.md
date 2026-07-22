---
name: init-design
description: "기존 프로젝트 코드베이스에서 디자인 시스템을 역추출해 docs/design/ Ground Truth 파일(DESIGN-TOKENS.md·UX-BRIEF.md)을 생성한다. UI 프리비전이나 리디자인 파이프라인을 거치지 않고 개발된 프로젝트에서 디자인 기준 파일을 수립할 때 사용. '/init-design', '디자인 역추출', '디자인 토큰 추출', 'DESIGN-TOKENS 만들어줘', 'UX-BRIEF 생성해줘', '디자인 기준 파일 없어', 'Ground Truth 만들어줘', '디자인 파일 없는데 만들어줘' 등 언급 시 호출."
argument-hint: "[대상 경로] [--deep] [--dry-run] [--skip-ux-brief]"
---

# INIT-DESIGN — 디자인 시스템 역추출 파이프라인

$ARGUMENTS 에 대해 아래 파이프라인을 실행한다.

```
SCAN → EXTRACT → NORMALIZE → GENERATE → [DEEP: CLEANUP] → REPORT
```

**존재 이유**: 이미 개발된 프로젝트에서 **기존 코드를 Ground Truth로 확정**하고 `docs/design/` 기준 파일을 역추출로 생성하는 전용 스킬이다. 디자인 토큰이 코드 곳곳에 흩어져 있어 문서화된 단일 기준이 없는 프로젝트에서, 이후 UI 작업의 최우선 참조 기준을 수립한다.

**리디자인과의 경계**

이 스킬은 기존 디자인을 **문서화**할 뿐, 교체하지 않는다.

| | 디자인 교체(리디자인) | `/init-design` |
|---|---|---|
| 목적 | 디자인 교체 | 현재 디자인 문서화 |
| 코드 변경 | 스타일 전면 교체 | 기본 없음 (`--deep` 시 한정적) |
| 기준 | 타겟 새 디자인 | 기존 코드 그대로 |
| 출력 | 새 DESIGN-TOKENS.md | 역추출 DESIGN-TOKENS.md |

---

## Phase 0: PARSE — 인자 파싱

| 인자 | 기본값 | 설명 |
|---|---|---|
| 대상 경로 | `src/` | 스캔할 소스 루트 |
| `--deep` | OFF | 하드코딩 교체 + 유틸 클래스 추출 + 컴포넌트 정리 |
| `--dry-run` | OFF | GENERATE 직전까지만 — 토큰 미리보기 출력, 파일 생성 없음 |
| `--skip-ux-brief` | OFF | UX-BRIEF.md 생성 생략 |

---

## Phase 1: SCAN — 현재 디자인 자산 스캔

### 1-1. 사전 확인

`docs/design/` 존재 여부를 Glob으로 확인한다:

| 상황 | 동작 |
|---|---|
| `docs/design/DESIGN-TOKENS.md` 없음 | 정상 진행 |
| `docs/design/DESIGN-TOKENS.md` 존재 | 사용자에게 경고: "이미 파일이 존재합니다. 덮어쓰면 기존 파일은 archive로 이동됩니다. 계속할까요?" → 승인 시 계속, 거절 시 종료 |

### 1-2. 디자인 자산 병렬 수집

아래를 **병렬로** Read·Glob한다:

| 수집 대상 | 경로 패턴 | 추출 내용 |
|---|---|---|
| CSS 전역 파일 | `**/globals.css`, `**/index.css`, `**/*.module.css` | CSS 커스텀 프로퍼티 (`:root`, `[data-theme]`) |
| Tailwind 설정 | `tailwind.config.*` | `theme.extend.*` 값 전체 |
| 레이아웃 컴포넌트 | `**/layout/**`, `**/Header.*`, `**/Footer.*`, `**/Sidebar.*` | 레이아웃 구조·영역 분류 |
| 페이지 파일 | `**/page.tsx`, `**/page.jsx`, `**/page.vue` | 라우트 목록 (화면 맵용) |
| 프로젝트 문서 | 프로젝트 루트 (`CLAUDE.md`, `README.md`, `package.json`) | 기술 스택, 구조 원칙 |

### 1-3. 인벤토리 요약 출력

```
📋 스캔 결과
CSS 변수:    {N}개 (`:root` / `[data-theme]`)
Tailwind 확장: {M}개
커스텀 유틸 클래스: {K}개 (globals.css)
인라인 스타일 하드코딩: {W}개 (대략)
페이지(라우트): {P}개
```

---

## Phase 2: EXTRACT — 토큰 추출

스캔 결과에서 아래 6개 카테고리로 토큰을 추출한다.

### 2-1. 추출 소스 우선순위

| 우선순위 | 소스 | 신뢰도 |
|---|---|---|
| 1 | CSS `:root` / `[data-theme]` 커스텀 프로퍼티 | 높음 — 이미 토큰화된 값 |
| 2 | Tailwind `theme.extend.*` | 높음 — 구조적 확장 |
| 3 | globals.css 커스텀 유틸 클래스 (`.btn`, `.sv-label` 등) | 중간 — 프로젝트 전용 클래스 |
| 4 | 컴포넌트 `className` 반복 패턴 | 중간 — 암묵적 토큰 |
| 5 | `style={{...}}` 인라인 하드코딩 | 낮음 — 정규화 필요 |

### 2-2. 추출 카테고리

**Color**: 배경(`bg`), 전경(`fg`), 강조(`accent`), 테두리(`border`), 음소거(`muted`), 코드 배경 등. 다크/라이트 모드 분리.

**Typography**: 폰트 패밀리(display/body/mono), 사이즈 스케일, 웨이트, 줄 간격.

**Spacing**: 마진·패딩·간격 값. 4px 기반 스케일 식별.

**Border Radius / Shadow**: 둥글기 값, 그림자 레이어.

**Motion / Animation**: 트랜지션 duration·easing, `@keyframes`.

**커스텀 유틸 클래스**: 프로젝트 전용 클래스 (예: `.sv-label`, `.h-1`, `.btn-primary`, `.metallic`). 역할과 적용 컨텍스트를 함께 기록.

---

## Phase 3: NORMALIZE — 정규화

추출한 원시 값을 정제한다.

| 정규화 대상 | 규칙 |
|---|---|
| 유사 컬러 | HSL 거리 ≤ 5 → 대표값 하나로 통합, 나머지는 별칭 표기 |
| 스페이싱 | 4·8·12·16·24·32·48·64·96·128px 표준 스케일에 스냅 (±2px 허용) |
| 중복 폰트 | 동일 계열 폰트 통합 (Inter / Pretendard / JetBrains Mono 등) |
| 시맨틱 역할 분류 | 값 → 역할 이름 매핑 (`--bg-base`, `--fg-primary`, `--accent`, `--border-default` 등) |
| 하드코딩 값 | 기존 CSS 변수와 매핑 가능하면 "→ {변수명}" 표기, 신규면 "신규 토큰 필요" 표기 |

정규화 결과를 간략히 출력한다:
```
🔧 정규화 결과
통합된 유사 컬러: {N}쌍
스케일 스냅: {M}건
시맨틱 분류: {K}개
신규 토큰 필요: {W}건
```

---

## Phase 4: GENERATE — Ground Truth 파일 생성

`--dry-run` 시 이 단계에서 미리보기만 출력하고 종료한다.

### 4-1. 디렉토리 준비

```bash
mkdir -p docs/design/archive
```

기존 `DESIGN-TOKENS.md` / `UX-BRIEF.md` 존재 시 → `docs/design/archive/{YYYY-MM-DD}/`로 이동 후 생성.

### 4-2. DESIGN-TOKENS.md 생성

경로: `docs/design/DESIGN-TOKENS.md`

```markdown
# Design Tokens

> 생성일: {날짜}
> 출처: /init-design 역추출 — {대상 경로}
> 프로젝트: {CLAUDE.md 또는 package.json에서 추출}
> 갱신 방법: /init-design --dry-run (재확인)

---

## Color

| 토큰명 | 다크 | 라이트 | 역할 |
|---|---|---|---|
| `--bg` | `#0D0D0D` | `#FAFAF8` | 페이지 배경 |
| ... | ... | ... | ... |

## Typography

| 토큰명 / 클래스 | 값 | 용도 |
|---|---|---|
| `--font-display` | `Pretendard` | 헤딩 |
| `.h-1` | `font-size: clamp(...)` | 페이지 주제목 |
| ... | ... | ... |

## Spacing

| 스케일 | 값 | 주 사용처 |
|---|---|---|
| `--space-4` | `4px` | 인라인 간격 |
| ... | ... | ... |

## Border Radius / Shadow

(추출된 값)

## Motion / Animation

(추출된 값)

## 커스텀 유틸 클래스

> 이 프로젝트 전용 클래스. 신규 구현 시 이 클래스를 우선 사용한다.

| 클래스 | 역할 | 대표 적용처 |
|---|---|---|
| `.sv-label` | 섹션 레이블 (대문자 모노) | 사이드바 제목 |
| `.h-1` ~ `.h-4` | 제목 위계 | 페이지·섹션 제목 |
| `.btn`, `.btn-primary` | 버튼 | CTA |
| ... | ... | ... |

---

> 이 파일은 UI 작업 시 최우선 참조 기준입니다.
> 신규 토큰 추가는 이 파일에 먼저 등록 후 사용하세요.
```

### 4-3. UX-BRIEF.md 생성 (`--skip-ux-brief` 시 생략)

경로: `docs/design/UX-BRIEF.md`

페이지 파일(`page.tsx`)과 레이아웃 컴포넌트에서 역추출:

```markdown
# UX Brief — {프로젝트명}

> 생성일: {날짜}
> 출처: /init-design 역추출 (기존 코드 기반)
> 주의: 신규 프로젝트 설계 브리프가 아닌 현행 구현 문서화

---

## 1. 화면 맵 (라우트 구조)

(page.tsx 파일에서 역추출한 라우트 목록)

```
/ (홈)
├── /about
├── /projects
├── /blog
│   └── /blog/[slug]
├── /contact
└── /login
```

## 2. 레이아웃 구조

(Header/Footer/Layout 컴포넌트에서 역추출)

- **글로벌 헤더**: {설명}
- **푸터**: {설명}
- **공통 레이아웃**: {설명}

## 3. 구현 시 준수 원칙

- DESIGN-TOKENS.md의 토큰 값을 Ground Truth로 사용
- 임의 컬러·스페이싱 추가 금지 (필요 시 DESIGN-TOKENS.md에 먼저 등록)
- 커스텀 유틸 클래스 우선 사용 (신규 인라인 스타일 최소화)
- 프로젝트 기술 스택 고정값 준수
```

---

## Phase 5 (`--deep`): CLEANUP — 디자인 코드 정리

`--deep` 미지정 시 이 단계를 완전히 건너뛴다.

`--deep`은 GENERATE 완료 후 실행된다. 코드 변경이 수반되므로 **각 단계 전 사용자 승인**을 받는다.

### 5-1. 하드코딩 → CSS 변수 교체

Phase 2에서 추출한 인라인 하드코딩 값 중 DESIGN-TOKENS.md의 토큰과 매핑 가능한 항목을 치환한다.

```
🔄 하드코딩 교체 후보
  파일: src/components/blog/TableOfContents.tsx
  - style={{ color: '#64748B' }}  →  style={{ color: 'var(--accent)' }}
  파일: src/app/page.tsx
  - style={{ background: '#0D0D0D' }}  →  style={{ background: 'var(--bg)' }}
  ...
  총 {N}건 — 자동 치환합니까? (y/N)
```

승인 후 `replace_all`로 일괄 처리. 이후 프로젝트 검증(아래 5-3 참조) — FAIL 시 해당 파일만 롤백.

### 5-2. 반복 Tailwind 패턴 → 유틸 클래스 등록

3개 이상 컴포넌트에서 동일한 Tailwind 클래스 조합이 반복되는 경우 `globals.css`에 커스텀 유틸 클래스로 추출을 제안한다.

```
📦 유틸 클래스 추출 후보
  패턴: "text-xs font-mono uppercase tracking-widest text-[var(--fg-muted)]"
  사용처: TableOfContents.tsx, PostNavigation.tsx, BlogList.tsx (3곳)
  제안: .sv-label { ... } (이미 존재하면 스킵)

  패턴: "border border-[var(--border)] rounded-sm px-2 py-0.5 text-xs"
  사용처: BlogList.tsx, PostNavigation.tsx, page.tsx (3곳)
  제안: .tag { ... }
  ...
  총 {N}패턴 — 추출하겠습니까? (y/N)
```

승인 후:
1. `globals.css`에 `@layer utilities { .클래스명 { ... } }` 추가
2. 해당 컴포넌트의 `className` 값 교체
3. `DESIGN-TOKENS.md` 커스텀 유틸 클래스 섹션 갱신
4. 프로젝트 검증 실행 (아래 5-3 참조)

### 5-3. 검증

모든 `--deep` 정리 완료 후 최종 검증한다. 프로젝트에 검증 스크립트가 있으면 실행한다 (`verify.sh`, `npm test`, `npm run build`, `npm run lint` 등 프로젝트에 맞는 것):

```bash
# 예: 프로젝트에 verify.sh가 있으면
bash verify.sh
# 또는 빌드/타입체크
npm run build
```

- **PASS** → Phase 6 진행
- **FAIL** → 실패한 파일만 롤백 + 사용자 보고
- **검증 스크립트 없음** → 사용자에게 수동 검증 권고 후 진행

---

## Phase 6: REPORT

```
🎨 init-design 완료
══════════════════════════════════════════
프로젝트:  {이름}
출처:      역추출 ({대상 경로})
══════════════════════════════════════════
[토큰]
  컬러:          {N}개 (다크/라이트)
  타이포:        {M}개
  간격:          {K}개
  유틸 클래스:   {J}개

[생성 파일]
  ✅ docs/design/DESIGN-TOKENS.md
  ✅ docs/design/UX-BRIEF.md        (또는 ⏭ --skip-ux-brief)
  📁 기존 파일 백업: docs/design/archive/{날짜}/  (해당 시)
──────────────────────────────────────────
[--deep 결과]  (해당 시)
  하드코딩 교체: {X}건
  유틸 클래스 추가: {Y}개
  검증: ✅ PASS / ❌ FAIL (롤백됨)
══════════════════════════════════════════
→ 생성된 DESIGN-TOKENS.md는 이후 모든 UI 작업의 최우선 참조 기준이다.
→ 후속 UI 구현·리디자인 워크플로우가 있으면 이 파일을 baseline으로 연결한다.
```

---

## 주의사항

- **기본 모드는 읽기 전용**: Phase 1~4는 파일 생성만 하며 기존 소스 코드를 수정하지 않는다.
- **`--deep`은 코드 변경 수반**: 각 단계 전 사용자 승인 필수. 승인 없이 자동 치환하지 않는다.
- **검증 기반 롤백**: `--deep` 실행 중 프로젝트 검증(verify.sh·`npm run build` 등) FAIL 시 해당 배치만 롤백하고 계속 진행한다.
- **DESIGN-TOKENS.md 는 값만 정의**: 스택별 주입 구문(`tailwind.config.ts` 반영 등)은 이 스킬의 범위 밖이다.
- **UX-BRIEF.md 는 현행 구현 문서화**: 신규 기획 브리프가 아님. 라우트·레이아웃을 있는 그대로 기록.
