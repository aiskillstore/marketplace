---
name: team-dev
description: "팀 에이전트 병렬 개발 오케스트레이터. SubTask 목록을 의존성 분석 후 병렬 가능 그룹으로 분류하고, 팀원 에이전트가 git worktree 격리 환경에서 동시 구현한다. '/team-dev', '팀 개발', '병렬 구현', '팀으로 개발' 등 언급 시 호출"
argument-hint: "[Task 목록 또는 기능명] [--auto] [--dry-run]"
---


# Team Dev — 팀 에이전트 병렬 개발 오케스트레이터

$ARGUMENTS 에 대해 SubTask를 의존성 분석하고, 병렬 가능 그룹으로 분류한 후, 팀원 에이전트가 worktree 격리 환경에서 동시 구현한다.

```
ANALYZE → [ DISPATCH → BUILD → VERIFY → INTEGRATE ] × 그룹 → COMPLETE
```

---

## 전제 조건

- **Git 저장소 필수** — worktree 격리를 위해 `git init`이 완료된 상태여야 한다
- **SubTask 목록 필수** — SubTask 목록을 입력으로 받는다 ($ARGUMENTS에 있거나, 자연어 기능 설명에서 분리 가능해야 한다). 없으면 AskUserQuestion으로 요청한다
- **프로젝트 규칙 문서(선택)** — CLAUDE.md 등 프로젝트 규칙 파일이 있으면 팀원 프롬프트의 컨텍스트로 주입한다
- **검증 스크립트(선택)** — `verify.sh`·`npm test`·`npm run build` 등 프로젝트 검증 수단이 있으면 각 SubTask 완료 후 및 통합 시 실행한다 (없으면 정적 검증 단계를 생략한다)

---

## Phase 0: PARSE — 인자 파싱

$ARGUMENTS에서 아래를 추출한다:

| 항목 | 추출 대상 | 기본값 |
|---|---|---|
| **SubTask 목록** | TaskList 도구의 기존 목록 또는 자연어 기능 설명 | (필수 — 없으면 AskUserQuestion) |
| **--auto** | 그룹 간 자동 진행 여부 | OFF (그룹 완료마다 확인) |
| **--dry-run** | 의존성 분석 + 그룹 분류만 수행 | OFF |
| **--tdd** | TDD RED 게이트 발동 (test-first 구현) | OFF |
| **--no-tdd** | TDD 제안·태그 모두 끔 (escape hatch) | OFF |

> **TDD 의미론**: 인터랙티브(`--auto` 없음)에서는 적격 SubTask에 `[TDD]`를 붙여 Phase 1-6 승인게이트에 제안 노출한다. `--auto` 단독이면 자동태그 OFF(전부 test-after), `--auto --tdd`면 적격 SubTask에 자동 부착(제안 생략), `--no-tdd`면 판단·제안 모두 끈다. 적격 기준과 절대제외는 아래 Phase 1-1-1 참조. team-dev는 git 필수라 RED 게이트의 실패테스트 선커밋 안전망이 항상 가용하다.

### 실행 모드 분기

| 모드 | 플래그 | 실행 방식 |
|---|---|---|
| **서브에이전트 모드** (기본) | 없음 | Agent 도구로 worktree 격리 병렬 spawn |
| **에이전트 팀 모드** (experimental) | (Agent Teams 활성 시) | 팀 리더가 팀원 인스턴스 생성, Task 할당, 코드 리뷰, 통합 검증 |

> 에이전트 팀 모드는 Claude Code의 experimental Agent Teams 기능이 활성화된 환경에서만 동작한다. 활성화돼 있지 않으면 기본 서브에이전트 모드로 진행한다. 상세는 [phase-dispatch.md](phase-dispatch.md) [B] 참조.

---

## Phase 1: ANALYZE — 의존성 분석 및 그룹 분류

SubTask 수집 → 컨텍스트 수집 → UI/UX 설계 → 의존성 분석 → 그룹 구성 → 사용자 승인.
상세 절차는 [phase-analyze.md](phase-analyze.md) 참조.

---

## Phase 2: DISPATCH — 팀원 배포

그룹 내 각 SubTask를 팀원 에이전트에게 배포한다. 서브에이전트 모드(기본)와 에이전트 팀 모드(experimental) 두 가지 분기.
상세 절차 및 프롬프트 템플릿은 [phase-dispatch.md](phase-dispatch.md) 참조.

---

## Phase 3: BUILD — 빌드 대기

`run_in_background: true`로 실행했으므로, 각 에이전트 완료 시 자동 알림을 받는다.

각 에이전트의 반환값을 수집한다:
- **성공**: worktree 경로 + 브랜치명 + 수정 파일 목록
- **실패**: 실패 사유 + 현재 상태

실패 처리:

| 상황 | 대응 |
|---|---|
| 1개 실패, 나머지 성공 | 실패한 SubTask만 팀 리더가 직접 수정 |
| 과반 실패 | 사용자에게 보고, 계획 재검토 제안 |
| 전체 실패 | 사용자에게 보고, 순차 구현 모드로 전환 제안 |

---

## Phase 4: VERIFY — 통합 검증

worktree 코드 통합 → 통합 검증 → 그룹 완료 보고.
상세 절차(merge 충돌 해결, 2단계 검증)는 [phase-verify.md](phase-verify.md) 참조.

---

## Phase 5: NEXT — 다음 그룹 진행

**auto 모드 OFF** 일 때:

사용자에게 진행 여부를 묻는다:

| 사용자 입력 | 동작 |
|---|---|
| 승인 / `next` | 다음 그룹 Phase 2로 진행 |
| `--auto` | auto 모드 ON — 남은 그룹 전부 자동 진행 |
| 수정 지시 | 수정 적용 후 Phase 4 재검증 |
| `stop` | 중단 |

**auto 모드 ON** 일 때:

- 즉시 다음 그룹 Phase 2로 진행
- **Phase 4 FAIL 시** → auto 모드 자동 해제, 사용자에게 보고 후 대기

다음 그룹의 프롬프트에 이전 그룹의 완료된 코드(타입 정의, export 경로 등)를 컨텍스트로 반영한다.

---

## Phase 6: COMPLETE — 최종 보고

모든 그룹 완료 시:

```
🎉 팀 개발 완료
══════════════════════════════════
Task:        {기능명}
총 SubTask:  {N}개 완료
병렬 그룹:   {M}개
══════════════════════════════════
→ 이후 커밋·PR·배포 워크플로우로 연결
```

응답 마지막에 `---DONE---` 블록을 포함한다.

---

## 순차 구현과의 역할 구분

병렬 개발이 항상 유리한 것은 아니다. SubTask 간 의존성이 높거나 규모가 작으면 순차 구현이 더 빠르고 안전하다.

| 항목 | 순차 구현 | /team-dev (병렬) |
|---|---|---|
| **실행 방식** | SubTask **순차** 구현 | SubTask **병렬** 구현 |
| **적합한 상황** | SubTask 간 의존성 높음, 소규모 | 독립 SubTask 다수, 대규모 |
| **검증** | SubTask마다 즉시 검증 | 개별 검증 + 통합 검증 2단계 |
| **권장 SubTask 수** | 2~5개 | 4개 이상 (병렬 이점) |

```
SubTask 3개 이하 → 순차 구현 (더 빠르고 안전)
SubTask 4개 이상 + 독립성 높음 → /team-dev (병렬 이점)
SubTask 4개 이상 + 의존성 높음 → 순차 구현 (더 안전)
```

---

## 특수 인자

| 인자 | 설명 |
|---|---|
| `--auto` | 그룹 간 자동 진행 (FAIL 시 자동 해제) |
| `--dry-run` | 의존성 분석 + 그룹 분류만 수행, 실제 구현 안 함 |
| `--tdd` / `--no-tdd` | TDD RED 게이트 발동 / 완전 끔 (Phase 0 참조) |

---

## 주의사항

- 팀원 에이전트는 **할당된 SubTask의 파일만** 수정한다.
- merge 충돌 자동 해결이 불확실하면 **반드시 사용자에게 확인**한다.
- 병렬 에이전트 수는 **최대 5개**로 제한한다.
- 이 스킬은 코드 구현 전용이다. 리서치·계획은 다른 워크플로우에서 수행한다. `team-research`가 함께 설치돼 있으면 사전 리서치에 활용할 수 있다.

---

## Known Pitfalls

> 본 skill 실행 중 반복 발생한 실패 패턴. 신규 패턴 발견 시 entry를 추가한다.

_(현재 누적 entry 없음.)_

### 작성 형식
- **[패턴명]** — YYYY-MM-DD
  - **상황**: 어떤 단계(SubTask 분리/병렬 실행/merge)·조건에서 발생
  - **원인**: 무엇 때문에 실패 (worktree 충돌 / 의존성 misjudge / merge 충돌 등)
  - **회피**: 다음 실행 시 적용할 가이드
