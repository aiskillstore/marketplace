# Phase 2: DISPATCH — 팀원 배포 (상세)

## [A] 서브에이전트 모드 (기본)

### 2-1A. 현재 그룹의 SubTask 배포

그룹 내 각 SubTask마다 Agent 도구를 **하나의 메시지에서 동시에** spawn한다:

각 Agent 호출 시:

```
Agent 도구 파라미터:
─────────────────────
subagent_type: "feature-builder"   # 이 plugin에 동봉된 에이전트
model: "sonnet"
isolation: "worktree"
run_in_background: true
prompt: (아래 템플릿)
─────────────────────
```

> `feature-builder` 에이전트가 설치돼 있지 않은 환경이면 `subagent_type: "general-purpose"`로 대체하고, 아래 프롬프트를 그대로 사용한다.

프롬프트 템플릿:

```
너는 병렬 개발용 기능 구현 전문가다. 할당된 SubTask를 worktree 격리 환경에서 독립 구현하라.

## 프로젝트 규칙
{CLAUDE.md 등 프로젝트 규칙 문서 내용 — 없으면 이 섹션 생략}

## 프로젝트 현재 구조
{디렉토리 트리}

## 기존 코드 패턴 참고
{핵심 파일의 import/네이밍/타입 패턴 요약}

## UI/UX 설계 명세 (UI SubTask인 경우 필수 준수)
{Phase 1-3에서 수립한 설계 명세}
- 설계 명세가 없으면 이 섹션은 생략한다

### Ground Truth 참조 (해당 파일 존재 시 Read로 로드하여 준수)
- Design Tokens:  docs/design/DESIGN-TOKENS.md  ← 컬러·타이포·스페이싱 값은 그대로 사용, 신규 추가 금지
- UX Brief:       docs/design/UX-BRIEF.md       ← 레이아웃 위계·영역별 우선순위 원칙
- 관련 prototype: {Phase 1-3 매핑 테이블에서 이 SubTask에 매핑된 경로}
  예: docs/design/prototype/03-detail.html  (시각 기준 — 100% 픽셀 일치 아닌 토큰·위계 준수)

Ground Truth가 없으면 위 섹션은 생략된다. 이 경우 기존 프로젝트 스타일(globals.css, tailwind.config)을 따른다.

## 할당된 SubTask
- SubTask: {설명}
- 대상 파일: {파일 경로}
- 요구사항: {상세 구현 내용}
- 의존 SubTask: {없음 / SubTask X의 결과}
- TDD 모드: {이 SubTask가 [TDD] 태그면 "ON" / 아니면 "OFF — test-after"}

## TDD 모드가 ON인 경우만 — RED 게이트 (test-first)
구현(아래 규칙)을 test-first로 수행한다. 순서를 반드시 지켜라:
1. 미구현 동작에 대한 단위 테스트(`*.test.*`)를 먼저 작성 → 실행 → **RED 확인**
2. **RED 사유 검증**: 실패가 "구현 누락" 때문인지 확인. import/오타/setup 에러면 무효 RED → 고쳐서 유효 RED부터 만든다
3. 실패 테스트를 먼저 커밋한다 (worktree=git이므로 항상 가능)
4. **테스트를 수정하지 않고** 구현 코드만 작성해 GREEN → 검증 스크립트 실행 → refactor
   (RED→GREEN 동안 테스트 약화/조작 금지. 명세 변경 시에만 팀 리더에 보고 후 수정)

## 구현 규칙
1. 할당된 SubTask 범위의 파일만 수정하라
2. 프로젝트 규칙 문서(있으면)의 기술 스택과 패턴을 준수하라
3. 언어의 타입/린트 규칙을 준수하라 (예: TypeScript strict mode)
4. 구현 완료 후 프로젝트 검증 스크립트가 있으면 실행하라 (`bash verify.sh`·`npm test`·`npm run build` 등). 없으면 정적 검증 단계를 생략한다
5. 검증 실패 시 수정 후 재실행 (최대 3회)
6. 다른 SubTask의 파일을 수정하지 마라

## 결과 반환 형식
SubTask: [설명]
상태: ✅ 완료 / ❌ 실패
수정 파일:
  - path/to/file.tsx (신규/수정)
검증: [스크립트명] ✅ PASS / ❌ FAIL (사유: ...) / — (검증 스크립트 없음)
비고: (특이사항)
```

---

## [B] 에이전트 팀 모드 (experimental Agent Teams 활성 시)

Claude Code의 experimental Agent Teams 기능을 사용하여 **독립 Claude Code 인스턴스 팀**을 생성한다. 이 기능이 활성화돼 있지 않으면 이 분기를 건너뛰고 [A] 서브에이전트 모드로 진행한다.

### 2-1B. 에이전트 팀 생성

팀 리더(현재 세션)가 아래와 같이 에이전트 팀을 생성한다:

```
에이전트 팀을 생성해줘. 각 팀원에게 기능/모듈별 구현을 할당할 거야.

팀원 구성:
{그룹 내 각 SubTask에 대해}
- {팀원명} (Sonnet): {SubTask 설명}
  → 담당 파일: {파일 경로 목록}
  → 요구사항: {상세 구현 내용}
  → 관련 prototype: {Phase 1-3 매핑 테이블의 경로, 없으면 "없음"}
  → 의존: {없음 / 다른 팀원의 작업 결과}
  → TDD 모드: {이 SubTask가 [TDD] 태그면 "ON (RED 게이트)" / 아니면 "OFF — test-after"}

UI Ground Truth (docs/design/ 아래 파일이 존재할 경우 — 모든 UI 팀원 준수):
- DESIGN-TOKENS.md:  토큰 값 그대로 사용, 신규 추가 금지
- UX-BRIEF.md:       레이아웃 위계·영역별 우선순위
- prototype/*.html:  시각 기준 (담당 prototype을 Read 후 토큰·위계 준수)

전체 규칙:
1. 각 팀원은 할당된 파일만 수정하라. 다른 팀원의 파일 수정 금지.
2. 프로젝트 규칙 문서(있으면)의 기술 스택과 패턴을 준수하라.
3. 언어의 타입/린트 규칙을 준수하라.
4. UI 구현 시 Ground Truth 파일이 존재하면 반드시 참조하라.
5. 구현 완료 후 프로젝트 검증 스크립트가 있으면 실행하라 (`bash verify.sh`·`npm test` 등).
6. 검증 실패 시 수정 후 재실행 (최대 3회).
7. 구현 완료 시 팀 리더에게 결과를 메시지로 보내라.
8. 연계 화면/모듈이 있으면 해당 담당 팀원과 직접 소통하여 인터페이스를 맞춰라.
9. plan approval 후 구현을 시작하라.
10. **TDD 모드 ON 팀원만**: test-first로 구현하라. 미구현 동작 테스트 작성→RED 확인→**RED 사유가 "구현 누락"인지 검증**(import/setup 에러면 무효 RED, 고쳐서 유효 RED부터)→실패 테스트 선커밋→테스트 수정 없이 구현해 GREEN→검증 스크립트.

결과 보고 형식:
SubTask: [설명]
상태: ✅ 완료 / ❌ 실패
수정 파일: [목록]
검증: [스크립트명] ✅ PASS / ❌ FAIL / — (없음)
비고: (특이사항, 다른 팀원과 협의 내용)
```

### 2-2B. 팀 리더의 역할 (에이전트 팀 모드)

| 단계 | 팀 리더 역할 |
|---|---|
| **팀 생성** | 그룹 내 SubTask별 팀원 생성 + 담당 파일 명확 할당 |
| **Plan Approval** | 각 팀원의 구현 계획을 검토 → 승인 또는 피드백 후 재제출 요청 |
| **모니터링** | 팀원 진행 상황 확인, 막힌 팀원에게 힌트 제공 |
| **연동 조율** | 팀원 간 연계 화면/API 인터페이스 불일치 발견 시 중재 |
| **코드 리뷰** | 각 팀원 완료 보고 수신 → 코드 품질 확인 |
| **통합 검증** | 모든 팀원 완료 후 프로젝트 검증 스크립트 실행 → PASS/FAIL 판정 |
| **재구현 지시** | 검증 실패 시 해당 팀원에게 수정 요청 메시지 전송 |
| **그룹 완료** | 통합 검증 PASS → 팀 정리 → 다음 그룹 진행 |

### 2-3B. 그룹 간 전환 (에이전트 팀 모드)

각 의존성 그룹 완료 시:
1. 현재 팀 정리 (`Clean up the team`)
2. 다음 그룹의 SubTask로 새 에이전트 팀 생성
3. 이전 그룹에서 생성된 코드를 팀원 프롬프트에 컨텍스트로 포함

> **주의**: Agent Teams는 세션당 한 팀만 가능하므로, 그룹 전환 시 반드시 이전 팀을 정리한 후 새 팀을 생성한다.

---

## 팀원별 모델 지정

| 팀원 | 모델 | 이유 |
|---|---|---|
| feature-builder (각 팀원) | `sonnet` | 빠른 구현 + 비용 효율 |
| 팀 리더 (메인) | `opus` (현재 세션) | 통합 판단 + 충돌 해결 |
