---
name: ship
description: "현재 브랜치의 변경사항을 commit → push → PR 생성 → merge → 브랜치 정리까지 한 번에 처리한다. develop 브랜치가 있으면 git-flow(feature→develop→main), 없으면 GitHub Flow(feature→main)로 자동 적응하고, 머지 전 기능 게이트+보안 스캔+DB 검토+민감파일 차단을 실행한다. '/ship', 'ship', '배포해줘', '커밋하고 머지까지' 등 언급 시 호출"
argument-hint: "[--dev | --main] [커밋 메시지] [--merge | --rebase]"
---

# Ship 파이프라인 (Commit → Push → PR → Merge)

$ARGUMENTS 를 파싱해 모드를 결정하고 전체 파이프라인을 실행한다.

> **브랜치 전략 자동 적응**: 리포지토리에 `develop` 브랜치가 있으면 git-flow(feature → develop → main)로, 없으면 GitHub Flow(feature → main)로 자동 동작한다. 별도 설정 없이 현재 리포의 브랜치 구조를 감지해 맞춘다.

---

## 파이프라인 구성

```
[파이프라인 A]  --dev  : feature/* → develop
[파이프라인 B]  --main : develop   → main

[GitHub Flow]   develop 브랜치 없음 → feature/* → main

[체인 모드]     --main + feature/* + 미push 변경사항
                = 파이프라인 A 자동 실행 → 완료 후 파이프라인 B 자동 실행
```

---

## Step 0 — $ARGUMENTS 파싱

$ARGUMENTS에서 아래 항목을 순서대로 추출한다:

| 항목 | 추출 대상 | 기본값 |
|---|---|---|
| 타겟 플래그 | `--dev` 또는 `--main` | 없음 (브랜치로 자동 결정) |
| 머지 방식 | `--merge` 또는 `--rebase` | squash |
| 커밋 메시지 | 플래그 제외 나머지 문자열 | 변경사항 분석해 자동 생성 |

두 타겟 플래그 동시 입력 시 → **즉시 중단**: "플래그는 --dev 또는 --main 중 하나만 사용 가능합니다."

---

## Step 1 — 사전 확인 및 모드 결정

### 1-1. 기본 정보 수집

```bash
git branch --show-current          # 현재 브랜치
git status --short                 # 변경사항 여부
git remote get-url origin          # owner/repo 파싱
git ls-remote --heads origin develop  # develop 브랜치 존재 여부
```

origin 미설정 시 → **즉시 중단**: "git remote add origin <URL> 후 재시도하세요."

### 1-2. 모드 결정 분기

```
develop 브랜치 없음?
  └─▶ GitHub Flow MODE (Step 2L)

develop 브랜치 있음?
  ├─ 현재: main/master → 즉시 중단
  ├─ 현재: develop + --dev 플래그 → 즉시 중단
  │        ("develop에서 --dev 불가. feature 브랜치에서 사용하세요.")
  │
  ├─ 현재: develop + (--main | 플래그 없음)
  │   └─▶ PIPELINE B (Step 2B)
  │
  └─ 현재: feature/*
      ├─ --dev 또는 플래그 없음
      │   └─▶ PIPELINE A (Step 2A)
      │
      └─ --main
          ├─ 변경사항 없음 → checkout develop → PIPELINE B (Step 2B)
          └─ 변경사항 있음 → CHAIN MODE (Step 2A → Step 2B 자동 연결)
```

변경사항 없고 현재 브랜치 = develop이며 develop == main 이면 → **즉시 중단**: "develop이 이미 main과 동일합니다."

### 1-3. 기능·보안·DB 사전검토

커밋 직전 기능 검증 게이트를 통과시킨 뒤 경량 보안/DB 검토를 수행한다.

**1-3-0. 기능 검증 게이트 (verify.sh — 항상 우선 실행)**

커밋·머지 전에 코드가 정적+단위 게이트를 통과하는지 확인한다. `--no-verify` 금지(아래 정책)의 상위 보증.

```bash
[ -f verify.sh ] && bash verify.sh --full
```

- `--full`: 커밋 전 시점이라 git diff 스코프가 좁을 수 있으므로 전체 검사로 vacuous-pass(아무것도 검사 안 하고 통과)를 방지한다.
- **`verify.sh` 부재 시 → 조용히 통과시키지 않는다.** 프로젝트에 통합 검증 스크립트가 없다는 뜻이므로:
  1. 프로젝트에 관례적 검증 명령이 있으면(`package.json`의 `test`/`build`/`lint`, `Makefile`의 `test` 등) 그걸 실행한다.
  2. 그것도 없으면 **REPORT 상단에 "⚠️ 기능 게이트 없음 — 미검증 코드 ship" 경고를 크게 표시**하고, 네이티브 `/verify`(앱 실행·동작 확인)·`/security-review`(변경 diff 보안 검토)로 최소 확인을 권한다.
  3. 사용자가 명시적으로 진행을 승인하지 않는 한, 완전 미검증 상태로 protected 브랜치 머지까지 자동 진행하지 않는다.
- FAIL → **즉시 중단**, 사용자에게 실패 항목 보고. tsc/lint/build/단위테스트 미통과 코드는 ship하지 않는다.
- 이미 구현·리팩토링 파이프라인을 거쳐 통과 상태라면 빠르게 재확인되어 통과한다 — `/ship` 직접 진입 시의 최소 기능 안전망.

**변경 파일 목록 추출 (보안/DB 검토용):**
```bash
git diff --name-only HEAD
```

**1-3-1. 보안 검토 (항상 실행)**

`security-auditor` 에이전트(이 플러그인에 동봉)를 QUICK 모드로 호출한다.
- 전달: 변경된 코드 파일 목록 (.ts, .tsx, .js, .jsx, .py, .go, .sql)
- Critical 발견 시 → 사용자에게 보고 후 수정 여부 확인
- Warning/Info만 → 계속 진행 (REPORT에 포함)
- 코드 파일 없으면 건너뜀
- > `security-auditor` 에이전트가 설치돼 있지 않은 환경이면 네이티브 `/security-review`(변경 diff 보안 검토)로 대체하고, 그것도 없으면 REPORT에 "보안 검토 미실행" 경고를 남긴다.

**1-3-2. DB 스키마 검토 (migration 파일 변경 시에만)**

```bash
git diff --name-only HEAD | grep -E "(\.sql$|migration|schema\.(ts|js|prisma)|drizzle|prisma/migrations|supabase/migrations)"
```

- 패턴 매칭 없음 → 건너뜀
- 패턴 매칭 있음 → `db-schema-reviewer` 에이전트(이 플러그인에 동봉) QUICK 모드 호출
  - Critical 발견 시 → 사용자에게 보고 후 수정 여부 확인
  - Warning/Info만 → 계속 진행
  - > `db-schema-reviewer` 에이전트가 없는 환경이면 REPORT에 "DB 스키마 검토 미실행 — 마이그레이션 수동 검토 권장" 경고를 남기고 계속 진행한다.

> **보안/DB 검토는 QUICK 모드**: 커밋 직전 머지 전 최소 안전망. 이미 별도 보안/리뷰 단계를 거쳤다면 중복이 되지만 가볍게 통과된다. (기능 게이트 1-3-0은 QUICK이 아닌 전체 verify.sh다 — 머지 전 기능 보증의 핵심.)

---

## Step 2L — GitHub Flow MODE (develop 없음)

feature/* → main 단일 흐름으로 수행한다.

**현재 브랜치가 feature/* 가 아니면(main/master 등에서 바로 ship 시도) 작업용 feature 브랜치를 생성한다:**

```bash
CUR=$(git branch --show-current)
# feature/* 이면 그대로 사용. 아니면 커밋 메시지에서 파생한 슬러그로 새 브랜치 생성.
#   슬러그 = 커밋 메시지 첫 줄을 kebab-case로 (예: "add login" → feature/add-login)
#   메시지 자동생성 전이라 파생 불가하면 feature/work 사용
git checkout -b feature/<슬러그>
```

- main/master에서 직접 커밋하지 않기 위한 안전장치다. 절대 protected 브랜치에 직접 push하지 않는다.
- 이미 feature/* 브랜치면 이 단계를 건너뛴다.

- 변경사항 없으면 중단
- 민감 파일 체크 → `git add -A` → `git commit -m "{메시지}"` → `git push -u origin {브랜치}`
- PR 생성: head={feature 브랜치}, base=main
- PR 머지 (squash 기본)
- `git checkout main && git pull origin main`
- `git fetch --prune`
- `git checkout {feature 브랜치} && git rebase main`

---

## Step 2A — PIPELINE A (feature → develop)

### 민감 파일 체크

`git status --short` 결과에 `.env`, `credentials`, `secrets` 등 포함 시 → **즉시 중단**.

### Commit & Push

```bash
git add -A
git commit -m "{커밋 메시지}"
git push -u origin {feature 브랜치}
```

### PR 생성 및 머지

`gh pr create` 또는 MCP GitHub 도구 사용 (gotchas 참조):

- **head**: 현재 feature 브랜치
- **base**: `develop`
- **title**: 커밋 메시지 첫 줄
- **body**:
  ```
  ## Summary
  {변경 파일 목록 및 작업 요약}

  ## Branch
  `{feature 브랜치}` → `develop`
  ```
- **merge_method**: squash (기본) / `--merge` / `--rebase` 옵션 반영

### 머지 후 동기화

```bash
git checkout develop && git pull origin develop
git checkout {feature 브랜치} && git rebase develop
```

---

## Step 2B — PIPELINE B (develop → main)

### develop 최신화

```bash
git checkout develop
git pull origin develop
```

### PR 생성 및 머지

- **head**: `develop`
- **base**: `main`
- **title**: 커밋 메시지 첫 줄 (체인 모드에서는 "release: {원본 메시지}")
- **body**:
  ```
  ## Summary
  {변경 파일 목록 및 작업 요약}

  ## Branch
  `develop` → `main`
  ```
- **merge_method**: squash (기본) / `--merge` / `--rebase` 옵션 반영

### 머지 후 동기화

```bash
git checkout main && git pull origin main
git checkout develop && git rebase main
git push origin develop    # develop도 main 기준으로 최신화
```

---

## Step 3 — 결과 보고

### GitHub Flow MODE / PIPELINE A 단독

```
✅ Ship 완료
──────────────────────────────────────
PR:      #{번호} (merged → {develop | main})
커밋:    {메시지}
현재:    {브랜치명} ({타겟 브랜치} 동기화 완료)
──────────────────────────────────────
```

### PIPELINE B 단독

```
✅ Ship 완료
──────────────────────────────────────
PR:      #{번호} (merged → main)
커밋:    {메시지}
현재:    develop (main 동기화 완료)
──────────────────────────────────────
```

### CHAIN MODE (A → B)

```
✅ Ship 완료 (체인 모드)
──────────────────────────────────────
PR #{번호}:   {feature 브랜치} → develop (merged)
PR #{번호+1}: develop → main (merged)
커밋:         {메시지}
현재:         {feature 브랜치} (develop 동기화 완료)
──────────────────────────────────────
```

---

## 주의사항

- merge 실패 시 (충돌 등) 즉시 중단하고 원인 보고. 강제 머지 시도 금지.
- `--no-verify` 절대 사용 금지
- 체인 모드에서 Pipeline A 실패 시 Pipeline B 실행하지 않음
- 체인 모드에서 Pipeline A 완료 후 Pipeline B 실패 시: "feature→develop은 완료. `git checkout develop && /ship --main`으로 재시도하세요." 안내
