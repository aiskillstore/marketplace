# 인터페이스 폴리시 룰 — Section B (LLM 제안, 게이트 아님)

**출처**: [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) — `skills/make-interfaces-feel-better/SKILL.md` (MIT 라이선스, "OSS stays free. This repo is MIT-licensed forever."). 원문 11룰 prose를 재구성해 내재화했다 — 런타임 의존성이 아니다(스킬을 설치해 매번 호출하지 않는다).
**확인일**: 2026-07-01. 정확한 원본 commit sha는 미기록 — 드리프트 우려 시 위 저장소를 직접 방문해 최신본과 대조 후 이 파일을 갱신할 것(권장 주기: 반기 1회).

## 이 파일을 쓰는 곳

`/unit-test` Phase 4.5 **Section B**(폴리시 제안)에서, 시나리오 최종 상태의 스크린샷 + Phase 4.5 공통 단계에서 만든 DOM 덤프를 근거로 아래 9룰을 참고 체크리스트 삼아 "동작은 정상인데 미감이 아쉬운" 지점을 제안한다.

**참고용(비재현) — 게이트 아님.** design-lint(Section A)와 달리 이 룰들은 정성적 prose라 동일 화면도 매번 다른 하위집합이 나올 수 있다. PASS/FAIL을 바꾸지 않고, `--fix`도 트리거하지 않는다.

**원본 11룰 중 2개는 여기 없음(design-lint에 결정론으로 이미 있어 중복 제거)**: 히트영역 44×44px → `D-A11Y-02`, `transition:all` 금지 → `D-MOTION-03`. 이 둘은 design-lint(Section A)가 설치돼 있으면 게이트로 잡히며, 없으면 이 9룰과 함께 참고 항목으로만 다룬다.

---

## 9룰

1. **Concentric Radius** — 중첩된 둥근 요소는 바깥 radius = 안쪽 radius + padding이어야 시각적으로 "동심"으로 보인다. 부모-자식 padding 값을 함께 봐야 판단 가능(스크린샷만으론 부족 — DOM outerHTML의 인라인/computed 스타일 참고).
2. **Optical Alignment** — 기하학적 중앙과 시각적 중앙은 다르다. 비대칭 아이콘(재생▶ 아이콘 등)은 픽셀 단위 보정이 필요할 수 있다.
3. **Shadows & Borders** — border는 분리, 레이어드 shadow는 깊이감을 준다. 배경색이 바뀌어도 무너지지 않게 alpha 투명도를 쓴다.
4. **Text Wrapping** — 헤딩엔 `text-wrap: balance`, 본문엔 `pretty`. 긴 산문형 텍스트엔 적용하지 않는다.
5. **Font Smoothing** — macOS 렌더링에서 `-webkit-font-smoothing: antialiased`.
6. **Image Outlines** — 이미지에 중립 black/white alpha의 은은한 inset outline. 브랜드색 쓰지 않는다.
7. **Motion Enter/Exit 비대칭** — opacity+작은 translateY 조합, **exit는 enter보다 짧게**. (duration 임계값·시작 scale·easing 자체는 design-lint `D-MOTION-01/02/05`가 이미 결정론으로 잡음 — 여기선 "exit가 enter보다 짧은가"라는 **상대적 관계**만 본다.)
8. **Press States** — 인터랙티브 요소 클릭 시 `scale(0.96)` 같은 촉각 피드백.
9. **Tabular Numbers** — 카운터·가격처럼 자릿수가 바뀌는 숫자에 `font-variant-numeric: tabular-nums` (자릿수 변할 때 레이아웃이 흔들리지 않게).

---

## Section B 실행 지침

- **입력**: 시나리오 최종 상태 스크린샷 + Phase 4.5 공통 단계에서 만든 DOM outerHTML 덤프(재수집 금지 — 중복 비용). 이 덤프는 design-lint 설치 여부와 무관하게 항상 생성되므로 Section B는 Section A 실행 여부에 의존하지 않는다.
- **비용 통제**: `--happy-only`에서도 저비용 항목은 유지하되, Section B는 `--no-ux-review` 플래그로 옵트아웃 가능하게 한다(고비용 LLM 리뷰만 통제).
- **출력 라벨**: REPORT에 `[B/제안·비재현]`처럼 Section A(`[A/게이트]`)와 신뢰수준이 다름을 명시한다.
- 9룰 중 실제 판단 가능성이 다르다 — 1(radius)·3(shadow depth)은 DOM/CSS 구조를 더 봐야 하고, 2·4·6·8·9는 스크린샷만으로도 유추 가능, 5(font-smoothing)는 렌더 해상도 의존이라 판단 신뢰도가 낮음을 유의.
