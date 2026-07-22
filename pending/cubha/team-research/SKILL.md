---
name: team-research
description: "팀 에이전트 병렬 리서치 오케스트레이터. 프로젝트 시작 전 기술 스택, 아키텍처, 경쟁 제품을 리서처 서브에이전트로 병렬 조사하고 결과를 취합한다. '/team-research', '팀 리서치', '리서치해줘', '사전 조사' 등 언급 시 호출"
argument-hint: "[프로젝트명 또는 설명] [--quick|--deep] [--no-context7] [--stdout]"
---

# Team Research — 팀 에이전트 병렬 리서치 오케스트레이터

$ARGUMENTS 에 대해 리서처 서브에이전트를 병렬로 spawn하여 사전 리서치를 수행하고, 결과를 취합하여 보고서를 생성한다.

```
BRIEF → DISPATCH → COLLECT → SYNTHESIZE → REPORT
```

이 플러그인은 리서처 서브에이전트 4종을 동봉한다: `tech-researcher`, `architecture-researcher`, `market-researcher`, `ux-researcher`(`--deep` 전용).

---

## Phase 0: PARSE — 인자 파싱

$ARGUMENTS 에서 아래를 추출한다:

| 항목 | 추출 대상 | 기본값 |
|---|---|---|
| **프로젝트명** | 첫 번째 인자 또는 자연어에서 추출 | (필수 — 없으면 AskUserQuestion) |
| **깊이 옵션** | `--quick`, `--deep`, 없음 | 기본 (4개 에이전트) |

깊이별 에이전트 구성:

| 옵션 | 에이전트 수 | 구성 |
|---|---|---|
| `--quick` | 3개 | tech-researcher + architecture-researcher + market-researcher |
| 기본 | 4개 | tech-researcher + architecture-researcher + market-researcher + 제약사항 (오케스트레이터 직접) |
| `--deep` | 5개 | 기본 + ux-researcher |

---

## Phase 1: BRIEF — 프로젝트 브리핑 수집

기존 자료 탐색 (`CLAUDE.md`, `ANALYSIS-*.md`, `RESEARCH-*.md`, `package.json`) 후, 없으면 사용자에게 브리핑 요청:
1. 어떤 프로젝트인가? 2. 타겟 사용자? 3. 선호/제외 기술? 4. 특별 조사 항목?

---

## Phase 2: DISPATCH — 팀원 배포

리서치 주제 결정 → 오케스트레이터 Context7 리서치(병렬, 설치돼 있으면) → 리서처 서브에이전트 병렬 배포.
상세 절차 및 프롬프트 템플릿은 [phase-dispatch.md](phase-dispatch.md) 참조.

---

## Phase 3: COLLECT — 결과 수집

각 에이전트 완료 시 결과를 검증한다:

| 검증 항목 | 판정 |
|---|---|
| 출력 형식이 올바른가 | 형식 불량 → 핵심만 추출 |
| 출처가 명시되어 있는가 | 출처 없음 → 신뢰도 낮음 표기 |
| 프로젝트 목적과 관련 있는가 | 무관한 내용 → 제외 |
| 다른 에이전트 결과와 모순되는가 | 양쪽 근거 비교 후 판단 |

오케스트레이터의 Context7 결과도 통합한다(수행한 경우).

---

## Phase 4: SYNTHESIZE — 종합 분석

크로스 분석:
- tech-researcher 추천 기술 ↔ architecture-researcher 패턴 호환성
- market-researcher 경쟁 분석 ↔ 차별화에 필요한 기술 요구사항
- (--deep 시) ux-researcher UX 방향 ↔ 기술 스택 UI 프레임워크 적합성

통합 권장안 도출 (1순위 조합 + 2순위 대안 + 주의사항).

---

## Phase 5: REPORT — 보고서 생성

`docs/research/RESEARCH-{주제}-{YYYY-MM-DD}.md` 파일을 생성한다.
보고서 포맷은 [report-template.md](report-template.md) 참조.

사용자에게 요약 출력:
```
📊 팀 리서치 완료
══════════════════════════════════
프로젝트:       {프로젝트명}
참여 에이전트:  {N}명
보고서:         {경로}
══════════════════════════════════
```

---

## 후속 워크플로우 연결

RESEARCH 파일은 후속 프로젝트 범위산정·스택 확정·초기화 단계에서 근거로 재사용된다. 조사(team-research)와 결정(범위·스택 확정)의 역할을 분리하는 것이 핵심이다.

같은 마켓의 관련 스킬이 **함께 설치돼 있으면** 자연스럽게 이어진다:
- **`/scope`** — 그린필드 다음 단계. RESEARCH 파일을 범위산정과 스택 확정의 근거로 로드한다.
- **`/analyze`** — 기존 코드베이스가 있는 경우, RESEARCH 존재 시 이미 조사된 항목을 생략하고 "기술 트렌드 대비" 섹션에 참조한다. (그린필드에서는 `/analyze` 대신 `/scope` 사용)

설치돼 있지 않아도 RESEARCH 파일 자체가 독립적인 리서치 산출물로 기능한다.

---

## 특수 인자

| 인자 | 설명 |
|---|---|
| `--quick` | 핵심 3개 에이전트만 |
| `--deep` | 기본 + ux-researcher |
| `--no-context7` | Context7 리서치 생략 |
| `--stdout` | 파일 생성 없이 터미널에 결과 출력 |

---

## 주의사항

- **코드 수정 금지** — 이 스킬은 리서치 전용이다.
- 리서처 서브에이전트 결과가 모순될 경우, **출처가 더 신뢰할 수 있는 쪽**을 채택한다.
- Context7 MCP 도구는 설치돼 있을 때 오케스트레이터가 직접 호출한다 (서브에이전트에서는 MCP 도구 사용 불가). 미설치 시 WebSearch/WebFetch만으로 진행한다.
- 기존 RESEARCH 파일이 있으면 덮어쓰지 않고 주제+날짜로 구분한다.
- 보고서에 API 키, 비밀번호 등 민감 정보를 포함하지 않는다.
