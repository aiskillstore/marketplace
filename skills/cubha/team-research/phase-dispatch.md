# Phase 2: DISPATCH — 팀원 배포 (상세)

## 2-1. 리서치 주제 결정

프로젝트 정보를 바탕으로 각 리서처에게 전달할 **구체적 리서치 주제**를 결정한다.

예시 (프로젝트: "SI 프리랜서용 접속 정보 관리 도구"):
- tech-researcher: "오프라인 퍼스트 웹앱을 위한 로컬 DB(IndexedDB/SQLite) + 암호화 라이브러리 비교"
- architecture-researcher: "오프라인 퍼스트 SPA의 데이터 동기화 패턴, 암호화 레이어 설계"
- market-researcher: "개발자용 비밀번호/접속 정보 관리 도구 (1Password, Bitwarden, KeePass 등) 비교"

## 2-2. 오케스트레이터의 Context7 리서치 (설치돼 있으면)

리서처 배포와 **병렬로**, 오케스트레이터(메인 세션)가 Context7 MCP가 설치돼 있으면 직접 활용한다:

1. `mcp__..._Context7__resolve-library-id` — 핵심 라이브러리 ID 확인
2. `mcp__..._Context7__query-docs` — 최신 API, breaking changes, 권장 패턴 조회

> Context7는 MCP 도구이므로 서브에이전트/리서처에서 직접 호출할 수 없다. 오케스트레이터가 직접 수행한다. 미설치이거나 `--no-context7` 지정 시 이 단계를 생략하고 리서처의 WebSearch/WebFetch 결과만으로 진행한다.

---

## 2-3. 리서처 병렬 배포

**하나의 메시지에서** 모든 리서처를 동시에 Agent 도구로 spawn한다 (독립 작업이므로 병렬 실행).

각 Agent 호출 시 포함할 내용:
- `subagent_type`: 해당 리서처 이름 (`tech-researcher`, `architecture-researcher`, `market-researcher`, `ux-researcher`). 동봉 에이전트가 로드되지 않는 환경이면 `"general-purpose"`로 spawn하고 아래 프롬프트에 각 리서처 `.md`의 역할·출력 형식을 인라인으로 포함한다.
- `run_in_background`: `true` (완료 시 알림을 받아 COLLECT로 진행)
- `prompt`: 아래 템플릿에 따라 작성

```
에이전트 프롬프트 템플릿:
──────────────────────────────────
너는 {에이전트 역할}이다.

## 프로젝트 정보
- 프로젝트명: {이름}
- 설명: {한줄 설명}
- 타겟: {타겟 사용자}
- 선호 기술: {있으면 기재}
- 제외 기술: {있으면 기재}

## 리서치 주제
{구체적 리서치 주제}

## 출력 규칙
- 반드시 아래 형식으로 결과를 반환하라
- 출처를 명시하라
- 코드를 수정하지 마라

{에이전트별 출력 형식 — 각 에이전트 MD 파일의 출력 형식 참조}
──────────────────────────────────
```

리서처끼리 발견한 내용이 서로 관련되면, 오케스트레이터가 COLLECT/SYNTHESIZE 단계에서 교차 검증한다.

---

## 리서처별 모델 지정

| 리서처 | 권장 모델 | 이유 |
|---|---|---|
| tech-researcher | `sonnet` | 빠른 검색 + 비교 분석 |
| architecture-researcher | `sonnet` | 패턴 조사 + 정리 |
| market-researcher | `sonnet` | 제품 탐색 + 비교 |
| ux-researcher (--deep) | `sonnet` | 트렌드 조사 + 정리 |
| 오케스트레이터 (메인 세션) | 현재 세션 모델 | 취합 + 판단 + 보고서 작성 |
