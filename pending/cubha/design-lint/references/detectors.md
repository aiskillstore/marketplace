# design-lint detector 분류표 (47개 구현)

각 detector는 순수 함수 `(css/decls/ctx) => Finding[]`. severity=`error`는 게이트 차단(객관적 계약 위반), `warn`은 보고. 출처 표기: [imp]=impeccable ban list, [a11y]=WCAG, [std]=표준 design-lint, [tok]=토큰 위생.

## A. COLOR (색) — 9
| id | severity | 검사 | 구현 |
|---|---|---|---|
| D-COLOR-01 | warn | 토큰 외 distinct 하드코딩 색 > N(기본8) | ✅ |
| D-COLOR-02 | **error** | DESIGN-TOKENS.md에 없는 하드코딩 색 사용 [tok] | ✅ |
| D-COLOR-03 | warn | text gradient(background-clip:text) [imp] | ✅ |
| D-COLOR-04 | warn | accent 색이 페이지 내 불일치(2개 이상 경쟁 accent) [imp] | ✅ |
| D-COLOR-05 | **error** | 본문 텍스트 대비 < WCAG AA 4.5:1 [a11y] | ✅ |
| D-COLOR-06 | warn | 큰 텍스트 대비 < 3:1 [a11y] | ✅ |
| D-COLOR-07 | warn | 순수 검정(#000) 본문/그림자 (소프트 권장) [std] | ✅ |
| D-COLOR-08 | warn | 채도 과포화 그라데이션(rainbow) [imp] | ✅ |
| D-AIDEFAULT-01 | warn | cream/sand/beige 배경(AI-default 팔레트) [imp] | ✅ |

## B. TYPOGRAPHY (타이포) — 8
| id | severity | 검사 | 구현 |
|---|---|---|---|
| D-TYPE-01 | warn | distinct font-family > 2 | ✅ |
| D-TYPE-02 | warn | system-ui/arial가 primary display face [imp] | ✅ |
| D-TYPE-03 | warn | font-size 스케일 외 값 남발(타입스케일 위반) [std] | ✅ |
| D-TYPE-04 | warn | line-height 단위 없는 비율 누락/과소(<1.3 본문) [std] | ✅ |
| D-TYPE-05 | warn | uppercase + wide letter-spacing eyebrow [imp] (현 D-AIDEFAULT-02) | ✅ |
| D-TYPE-06 | warn | font-weight 종류 > 4 | ✅ |
| D-TYPE-07 | **error** | 본문 font-size < 12px [a11y] | ✅ |
| D-TYPE-08 | warn | 텍스트 정렬 justify(가독성 저하) [std] | ✅ |

## C. SPACING / SHAPE (스페이싱·형태) — 8
| id | severity | 검사 | 구현 |
|---|---|---|---|
| D-SPACE-01 | warn | off-grid 스페이싱(4/8 배수 아님) | ✅ |
| D-SPACE-02 | warn | distinct 스페이싱 값 > N(스케일 부재) [std] | ✅ |
| D-SHAPE-01 | warn | distinct corner radius > 3 [std] | ✅ |
| D-SHAPE-02 | warn | radius 혼용(완전 둥금 + 각짐 무근거 혼재) [imp] | ✅ |
| D-EFFECT-01 | warn | ad-hoc box-shadow > N(섀도 스케일 부재) | ✅ |
| D-EFFECT-02 | warn | shadow가 토큰 var 미참조 [tok] | ✅ |
| D-SPACE-03 | warn | 컨테이너 max-width 부재(전폭 텍스트) [std] | ✅ |
| D-SHAPE-03 | warn | border 굵기 종류 남발 | ✅ |

## D. LAYOUT / EFFECT (레이아웃·효과) — 7
| id | severity | 검사 | 구현 |
|---|---|---|---|
| D-LAYOUT-01 | warn | 무동기 glassmorphism(backdrop blur 2+) [imp] | ✅ |
| D-LAYOUT-02 | warn | side-stripe border 클리셰 [imp] | ✅ |
| D-LAYOUT-03 | warn | hero-metric 템플릿(동일 통계 카드 3열) [imp] | ✅ |
| D-LAYOUT-04 | warn | 동일 card grid 반복(시각 단조) [imp] | ✅ |
| D-LAYOUT-05 | warn | z-index 매직넘버 남발 [std] | ✅ |
| D-LAYOUT-06 | warn | 고정 px 너비로 비반응형(specified width) [std] | ✅ |
| D-LAYOUT-07 | warn | !important 남발 [std] | ✅ |

## E. TOKEN HYGIENE / MOTION (토큰 위생·모션) — 11
| id | severity | 검사 | 구현 |
|---|---|---|---|
| D-TOKEN-01 | **error** | 하드코딩 px가 spacing 토큰 미참조 [tok] | ✅ |
| D-TOKEN-02 | warn | 정의됐으나 미사용 토큰(dead token) [tok] | ✅ |
| D-TOKEN-03 | warn | 동일 값 다른 토큰명(중복 토큰) [tok] | ✅ |
| D-MOTION-01 | warn | transition-duration > 300ms(UI) [emil] | ✅ |
| D-MOTION-02 | warn | scale(0)에서 시작하는 등장 애니메이션 [emil] | ✅ |
| D-MOTION-03 | warn | transform/opacity 외 속성 애니메이션(perf) [emil] | ✅ |
| D-MOTION-04 | warn | prefers-reduced-motion 미대응 [a11y][emil] | ✅ |
| D-MOTION-05 | warn | 등장에 ease-in 사용(ease-out 권장) [emil] | ✅ |
| D-A11Y-01 | **error** | 포커스 outline:none 제거 후 대체 없음 [a11y] | ✅ |
| D-A11Y-02 | warn | 인터랙티브 요소 최소 타깃 < 44px [a11y] | ✅ |
| D-TOKEN-04 | warn | 색 정의가 OKLCH/HSL 아닌 raw hex만(스케일 파생 곤란) [imp] | ✅ |

## F. LAYOUT RUNTIME (관측 기반 — "동작은 정상, 시각만 깨짐" 게이트) — 4
| id | severity | 검사 | 구현 |
|---|---|---|---|
| D-LAYOUT-08 | warn (`--gate-runtime` 시 문서 레벨만 **error**) | 가로 오버플로우: `scrollWidth>clientWidth` | ✅ |
| D-LAYOUT-09 | warn | 텍스트 잘림(말줄임/line-clamp 없이 `overflow:hidden`) | ✅ |
| D-LAYOUT-10 | warn | 인터랙티브 요소(버튼/링크) 텍스트가 컨테이너 초과 | ✅ |
| D-LAYOUT-11 | warn, **기본 OFF**(`--strict`로만 활성) | 형제 요소 bounding-box 비의도 겹침 [low-confidence] | ✅ |

**존재 이유**: 나머지 43개 detector는 전부 정적 CSS/토큰 검사라 "인터랙션 후 깨짐"(오버플로우·텍스트 잘림·버튼 텍스트 초과)을 못 잡는다. 이 4개는 Group A 관측 경로(`ctx.observed`, `--observed obs.json`)에 얹혀 "동작은 정상인데 UX가 깨진 것"을 결정론적으로 잡는다. 인터랙션 후 상태를 덤프해 먹이는 용도다(`unit-test` 스킬이 함께 설치돼 있으면 그 인터랙션 실행 단계가 이 상태를 만들어 넘겨줄 수 있다) — 정적 프로토타입 린트가 아니라 **렌더+인터랙션 상태** 검사다.

**오탐 방지 예외(오탐 0 계약 유지를 위해 필수)**:
- **sr-only 제외**(`w≤1 && h≤1`): `.sr-only{width:1px;height:1px;overflow:hidden}`은 WCAG 표준 스크린리더 패턴 — 잘림 버그가 아니다. D-LAYOUT-08/09/10 전부 이 조건이면 스킵.
- **의도된 스크롤 컨테이너 제외**(`overflow-x: auto|scroll`): 캐러셀·코드블록처럼 가로 스크롤 어포던스가 이미 있으면 D-LAYOUT-08/10에서 스킵.
- **line-clamp 인정**(`-webkit-line-clamp`/`line-clamp` ≠ `none`): 다줄 말줄임은 의도된 잘림이므로 D-LAYOUT-09에서 스킵.
- **D-LAYOUT-11은 기본 OFF**: "겹침이 버그인지 의도(배지·스택카드·sticky)인지"는 의미 판단이라 결정론 게이트 오탐 0 계약을 깬다(구 D-A11Y-03과 같은 함정). `--strict`로 opt-in한 경우만 warn 노출, 최종 판정은 스크린샷으로 사람/LLM에게 위임.

**뷰포트 한계**: 다른 Group A detector와 동일하게 **1280×800 고정 뷰포트 전제**. 모바일 전용(예: 375px)에서만 나타나는 오버플로우/잘림은 이 검사로 **원천적으로 못 잡는다** — design-lint 통과가 모바일 안전을 보장하지 않는다.

**폰트 로딩 주의**: `scrollW`/`clientW` 관측 직전 호출자가 `document.fonts.ready`를 먼저 대기해야 한다(OBSERVE_SNIPPET 자체에는 안 넣음 — 동기 반환 계약 유지). 웹폰트 스왑 전 폴백폰트 metric으로 관측하면 일시적 오버플로우가 오탐으로 잡힌다.

**기각된 안 — `D-MOTION-06`(`transition:all` 금지)**: 최초 설계에 포함됐으나 구현 착수 전 코드 실측(`nonCompositedMotion`, L357-366)으로 기존 **D-MOTION-03이 이미 `transition:all`을 `bad.add("all")`로 잡고 있음**을 확인 → 신규 id 추가 시 findings 중복이라 **폐기**. `transition:all` 검사는 D-MOTION-03이 계속 담당한다.

> **D-A11Y-01 한계(error-grade 주의)**: 정규식이 **단일 룰 블록 내**에서만 outline 제거+대체를 본다. `:focus{outline:none}`와 `:focus{box-shadow:…}`를 **별도 룰로 분리**한 코드는 false-positive로 파이프라인을 막을 수 있다. standalone 프로토타입은 보통 한 블록에 모으므로 빈도는 낮지만, error severity라 비용이 크다 — 분리 패턴이 흔한 코드베이스는 Playwright computed-style(`:focus` 실측 상태) 경로로 이관 검토.
> **(폐기) 색만으로 상태 구분 — 구 D-A11Y-03, 재구현 금지**: "색 옆에 텍스트/아이콘이 **병행되는지**"는 DOM 자식 콘텐츠에 있어 CSS 정규식은 물론 computed-style 관측으로도 결정 불가(상태=색인지 vs 장식인지, 동반 단서가 "충분"한지는 의미 판단). 어떤 구현도 고오탐을 내 결정론 게이트의 "오탐 0" 계약을 깨므로 **DEFER가 아니라 폐기**한다(나중에 추가하지 않는다). 회귀 가드: eval은 이 ID가 출력되지 않음을 검증한다.
> **확장 원칙**: 새 detector는 ①분류표에 정의 ②순수 함수로 구현 ③evals에 양성/음성 케이스 추가 ④precision/recall 확인 후 활성. 이 4단계를 건너뛰고 프롬프트로 "이런 것도 봐줘" 하지 않는다 — 결정론성이 무너진다.
> **모션(D-MOTION-*)은 emil-design-eng 규칙의 결정론 버전** — emil 스킬을 설치하는 대신 그 규칙을 detector로 흡수하면 모션 게이트가 0토큰·재현적이 된다(연구 DEFER 항목의 대안 경로).
