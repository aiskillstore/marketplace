# design-lint 게이트 배선 가이드

> design-lint는 standalone `/design-lint`로 보고만 할 수도 있고, `--gate`로 상위 파이프라인·CI에 **결정론적 게이트**로 꽂을 수도 있다. 이 문서는 후자의 배선 패턴을 정리한다.

## 핵심 계약

- `--gate` **없이** 실행 → error가 있어도 항상 `exit 0` (순수 리포터). 판정은 stdout JSON의 `verdict`/`summary.error`에 담긴다.
- `--gate` **있이** 실행 → error-severity finding이 하나라도 있으면 `exit 1`. 셸 `&&`/CI step이 여기서 멈춘다.
- warn은 게이트를 막지 않는다. 안티패턴이 의도된 디자인 결정일 수 있으므로 사람이 본다. **error(객관적 계약 위반)만 자동 차단**한다.

## CI / verify 스크립트에 꽂기

시각 산출물(렌더된 HTML 프로토타입, 변경된 UI 파일)이 있으면 빌드/검증 스크립트에 다음을 추가한다:

```bash
node <plugin>/skills/design-lint/scripts/design-lint.mjs \
  docs/design/prototype/*.html \
  --tokens docs/design/DESIGN-TOKENS.md \
  --gate
```

- `<plugin>`은 이 플러그인이 설치된 경로. 스킬 실행 컨텍스트에서는 `${SKILL_DIR}/scripts/design-lint.mjs`로 참조된다.
- **error**(토큰 위생 위반 등) → 비-제로 종료로 파이프라인 차단. warn은 리포트에 포함만.
- `--tokens`를 생략하면 `docs/design/DESIGN-TOKENS.md`를 자동탐색하며, 없으면 토큰 위생 검사를 스킵한다(false positive 방지).

## 후속 워크플로우(리팩토링·리디자인 등)에 게이트로 삽입

리팩토링/리디자인처럼 시각 산출물을 바꾸는 워크플로우가 있으면 그 **시각 검증 단계**에 design-lint를 `--gate`로 병행한다:

- **리팩토링류 검증 단계**: verify(빌드/테스트) 직후 시각 산출물이 있으면 `--gate` 실행. error → 재수정 이슈로 환류.
- **리디자인류 시각 회귀 단계**: 스크린샷 diff와 **함께** `--gate` 실행. 토큰 위생 error 시 → 해당 컴포넌트 묶음 롤백 후 재매핑.
  - (시각 회귀 = 의도치 않은 변화 감지 / design-lint = 토큰 계약 위반 감지 — 상보적이다.)

모델이 오케스트레이션하는 파이프라인은 셸 `&&`가 아니라 stdout JSON의 `summary.error ≥ 1`을 읽어 판정하는 것이 자연스럽다. `--gate`의 비-제로 종료는 순수 CI/셸 게이트용 신호다.

## 라이브 URL을 게이트에 넣을 때

정적 HTML이 아니라 배포본을 게이팅하려면 Group A 관측 경로가 필요하다:

1. Playwright MCP로 대상 URL을 **1280×800 고정 뷰포트**로 렌더.
2. `node scripts/design-lint.mjs --observe-snippet`로 얻은 스니펫을 `browser_evaluate`에 주입 → 관측 배열을 `obs.json`으로 저장.
3. 본 실행에 `--observed obs.json --gate`를 전달.

`--observed` 없이 라이브 URL을 넣으면 Group A(대비비·box-model·구조·런타임 오버플로우) detector는 skip되고 정규식 detector만 게이팅된다.

## 배선 전 검증

라이브 배선 전, 안티패턴을 심은 HTML / 깨끗한 HTML / 토큰 위생 위반 fixture로 **precision(거짓양성 없음)·recall(놓침 없음)**을 정량 확인한다. 게이트가 false positive로 파이프라인을 막지 않는지, 실제 위반을 놓치지 않는지를 배선 전에 실증해야 한다.
