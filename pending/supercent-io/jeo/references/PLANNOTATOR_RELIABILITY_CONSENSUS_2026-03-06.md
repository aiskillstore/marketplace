# plannotator 신뢰성 이슈 합의서 (2026-03-06)

## 문제 정의
- 이슈: `jeo` PLAN 단계에서 `plannotator`가 시작되지 않아 승인 게이트가 막힘.
- 관측 에러:
  - `Failed to start server. Is port 0 in use?`
  - `code: "EADDRINUSE"`
- 영향: `approved=true`를 만들 수 없어 PLAN→EXECUTE 전이가 중단됨.

---

## 근거 기반 진단

### 1) 로컬 재현 (Codex sandbox)
- `bun -e "Bun.serve({port:0,...})"` 실행 시 동일 에러 재현.
- `node`로 localhost bind probe 시 `EPERM listen 127.0.0.1`.
- 결론: 일부 실행환경(특히 sandbox/CI/headless)은 localhost listen 자체가 차단됨.

### 2) 외부 근거
- Bun 공식 문서: `Bun.serve`는 실제로 포트를 bind하며 `port: 0`은 랜덤 포트에 listen하도록 설계됨.
  - https://bun.com/docs/api/http
- Claude Code 이슈에서도 동일한 plannotator/Bun 에러가 보고됨.
  - https://github.com/anthropics/claude-code/issues/11469
- Claude Code hooks는 `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Notification` 등 이벤트 기반 자동화를 지원.
  - https://docs.anthropic.com/en/docs/claude-code/hooks
- Gemini CLI hooks도 동기 이벤트 기반으로 동작 (`BeforeTool`, `AfterTool`, `UserPromptSubmit` 등)하며 설정 파일에서 관리.
  - https://developers.googleblog.com/tailor-gemini-cli-to-your-workflow-with-hooks/
- Codex는 `notify` 훅/이벤트를 지원하며 config에서 hook command를 연결 가능.
  - https://developers.openai.com/codex/config/

---

## 역할별 토론 결과

### QA 관점
- 현재 실패는 일회성 플루크가 아니라 환경 의존 재현 버그.
- 승인 게이트는 “실패 이유를 분류”해야 하며, 인프라 실패와 사용자 피드백 실패를 구분해야 함.
- 수용 기준:
  1. localhost bind 불가 시 즉시 감지
  2. 불필요한 3회 재시도 제거
  3. 대체 승인 루프 제공

### 시스템 엔지니어 관점
- 본질은 `plannotator` UI 서버 의존성 + 실행환경의 listen 제한.
- `EADDRINUSE`는 실제 포트 충돌이 아니라 listen 실패(권한/격리) 래핑일 수 있음.
- 안정화 전략:
  - 사전 probe (localhost listen)
  - 인프라 차단 전용 종료 코드
  - TTY/비TTY 분기 fallback

### Codex 관점
- notify hook 기반 자동 루프는 가능하지만 sandbox 정책에 따라 UI 서버가 실패할 수 있음.
- 따라서 PLAN gate는 “UI-only hard fail”이 아니라 “fallback-aware state machine”이어야 함.

### Claude 관점
- hook 체인은 강력하지만, 실행환경 제약(권한/네트워크) 문제는 hooks만으로 해결 불가.
- 실패를 빠르게 surfacing하고 수동 gate로 전환하는 것이 실용적.

### Gemini CLI 관점
- hook는 안전망으로 유효하지만, PLAN 단계는 blocking gate가 본질.
- UI 서버 실패 시에도 다음 턴으로 피드백 전달 가능한 deterministic fallback이 필요.

---

## 합의안 (최종)

1. PLAN gate를 2레인으로 분리
- Primary: `plannotator` hook mode (UI approve/feedback)
- Fallback: 수동 PLAN gate (TTY에서 approve/feedback/stop)

2. 인프라 실패 전용 exit code 도입
- `exit 32`: localhost bind 불가 또는 plannotator server bind 실패
- 기존 코드 유지:
  - `0` approved
  - `10` feedback
  - `30/31` stop/confirm

3. 재시도 정책 개선
- bind 불가 시 재시도 반복 대신 즉시 fallback 전환.
- 비TTY에서는 `exit 32`로 빠르게 사용자 확인 유도.

4. 문서/운영 규칙 업데이트
- JEO 문서에 `exit 32` 분기와 운영 가이드 추가.
- 플랫폼 설정 스크립트(setup-codex/setup-gemini 등)에서도 안내 문구 통일.

---

## 적용 내용

### 코드
- 수정: `.agent-skills/jeo/scripts/plannotator-plan-loop.sh`
  - localhost listen probe 추가
  - bind 실패 패턴 감지 (`EADDRINUSE/EPERM/...`)
  - TTY 수동 gate 추가 (`approve/feedback/stop`)
  - `exit 32` 표준화

### 문서
- 수정: `.agent-skills/jeo/SKILL.md`
  - PLAN 결과 분기에 `exit 32` 추가
  - 인프라 차단 시 운영 절차 명시

---

## 운영 권고

1. 로컬 개발(권장)
- sandbox 없는 로컬 터미널에서 PLAN gate 수행
- UI 승인 완료 후 EXECUTE 단계로 진입

2. 제한 환경(CI/강샌드박스)
- PLAN 단계는 수동 gate 또는 외부 승인 채널로 분리
- `exit 32`를 “환경 제약”으로 취급하고 실패 집계에서 분리

3. 장기 개선
- plannotator upstream에 Node HTTP fallback 또는 no-listen 승인 모드 제안
- 훅 체인에서 인프라 실패 telemetry를 수집해 자동 진단 메시지 제공
