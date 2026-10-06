# topic 모드 — 주제 한 줄에서 책 한 권까지

입력이 주제·아이디어뿐일 때의 콘텐츠 생산 절차. 산출물은 SKILL.md의 P1 완료 기준(outline.json + chapters/*.md)이다.

## 1. 조사

주제에 대해 웹 조사를 수행해 조사 노트를 만든다(`<book_dir>/research.md`, 책에는 미포함).

- 수집: 핵심 개념 정의, 실제 사례, 수치·통계(출처·연도 필수), 논쟁점, 최신 동향
- 수치·통계·고유 사건은 **출처를 확인한 것만** 본문에 쓴다. 확인 못 한 수치는 쓰지 않는다 — 일반 원리로 서술한다.
- 조사 없이 집필하는 것은 분량 프리셋 short + 사용자가 속도를 요구할 때만 허용.

완료 기준: 장 후보 6개 이상을 뒷받침할 재료가 research.md에 정리돼 있다.

## 2. 목차 설계

스타일별 목차 문법이 다르다 — 선택한 스타일의 `styles/<스타일>/STYLE.md` 정체성·지면 템플릿 절을 읽고 장 구조를 정한다:

- practical: 반복 단위(패턴·활용·용어 N개)를 장으로 묶는 구조가 강하다
- insight/business: Executive Summary 성격의 1장 + 본론 + 시사점 마무리
- academic: 서론(문제 제기)→본론(장별 논점)→결론, 절 번호 위계 활용
- essay: 주제 궤적을 따라 흐르는 글(꼭지) 묶음
- magazine: 피처(기사) 단위 — 서로 다른 각도의 꼭지들

`outline.json`에 장별 `file`·`title`·`summary`를 채운다. summary는 도비라에 그대로 실린다 — 1~2문장, 그 장이 답하는 질문을 담는다.

분량 산정: short = 5~7장 × 본문 2,000~3,000자, standard = 8~12장 × 3,000~4,500자.

## 3. 장별 집필

장마다 `chapters/ch-NN.md`를 SKILL.md의 콘텐츠 계약 문법으로 쓴다.

- 첫 줄 `# {outline의 title}` 일치 필수
- 스타일의 STYLE.md가 규정한 구성 요소를 활용한다(키 스탯은 ::: stat, 팁 박스는 ::: tip, 인용은 > 또는 ::: quote)
- 표·리스트·콜아웃을 장당 2개 이상 섞어 지면 리듬을 만든다 (essay 제외 — essay는 문단·인용 중심)
- 중립 문어체, 과장 금지, AI 자기언급 금지

장이 많으면 병렬화할 수 있다 — Claude Code 환경이면 [../references/orchestration.md](../references/orchestration.md) 참조. 단일 에이전트면 순서대로 쓴다.

완료 기준: 모든 장 파일 존재 + 각 장이 계약 문법만 사용 + 총 분량이 프리셋 범위를 감당(short는 도비라·차례 포함 30쪽을 넘겨야 하므로 본문 합계 1.2만 자 이상).

## 4. 이미지 (책이 이미지를 쓰는 경우만)

- 도해·차트: SVG로 직접 그려 `assets/`에 넣고 본문에서 참조
- 표지·도비라 아트: [../references/art-policy.md](../references/art-policy.md)의 무텍스트 규칙을 따른다
- 이미지 없는 책도 성립한다 — practical·academic·business는 무이미지로 완결 가능
