# Language / General Domain Profile

> For general education, linguistics, language learning, writing, and topics that don't fit other domains.

---

## Search Strategy

### Primary Sources

1. **Educational Encyclopedias**
   - Wikipedia (overview, then verify)
   - Britannica, World Book
   - Subject-specific encyclopedias
   - 한국민족문화대백과

2. **Academic Resources**
   - Google Scholar
   - Open access journals
   - University course materials
   - Library databases

3. **Quality Educational Content**
   - Khan Academy
   - Coursera, edX
   - TED-Ed
   - Educational YouTube channels

4. **Reference Works**
   - Dictionaries (language topics)
   - Style guides (writing topics)
   - Handbooks and manuals

### Search Query Patterns

```
"{topic} introduction"
"{topic} explained simply"
"{topic} beginner guide"
"{topic} fundamentals"
"learn {topic}"
"{topic} course syllabus"
"{topic} textbook"
"{topic} overview"
"{topic} 입문"
"{topic} 기초"
```

### Quality Indicators

- Authoritative sources
- Clear explanations
- Well-organized structure
- Appropriate for target audience
- Balanced perspective

---

## Special Fields

### For Language Learning Topics

| Field               | Description             | Example                |
| ------------------- | ----------------------- | ---------------------- |
| `target_language`   | Language being learned  | 영어, 일본어, 스페인어 |
| `proficiency_level` | CEFR or similar         | A1, B2, N3             |
| `skills_focus`      | Speaking, writing, etc. | 회화, 작문, 독해       |
| `practice_methods`  | Learning activities     | 쉐도잉, 다독           |

### For Linguistics Topics

| Field              | Description             | Example                |
| ------------------ | ----------------------- | ---------------------- |
| `subfield`         | Linguistics branch      | 음운론, 통사론, 의미론 |
| `notation_system`  | IPA, syntax trees, etc. | IPA 표기               |
| `language_samples` | Example languages       | 한국어, 영어, 일본어   |

### For General Topics

| Field               | Description    | Example              |
| ------------------- | -------------- | -------------------- |
| `topic_category`    | Broad category | 심리학, 철학, 경제학 |
| `key_concepts`      | Core ideas     | 인지 편향, 수요 공급 |
| `application_areas` | Practical uses | 일상생활, 직장       |

---

## Terminology Policy

### Language Handling

| Type             | Policy                 | Example                                       |
| ---------------- | ---------------------- | --------------------------------------------- |
| Technical terms  | Context-dependent      | 형태소(morpheme)                              |
| Foreign concepts | Original + translation | zeitgeist (시대정신)                          |
| Abbreviations    | Spell out first use    | CEFR (Common European Framework of Reference) |
| Jargon           | Explain simply         | 코드 스위칭 → 언어 전환                       |

### First Occurrence Format

```markdown
## 화용론 (Pragmatics)

화용론(pragmatics)은 언어가 맥락 속에서 어떻게 사용되고
해석되는지를 연구하는 언어학의 분야입니다.
```

### Citation Format

```markdown
> Crystal, D. (2010). _The Cambridge Encyclopedia of Language_ (3rd ed.). Cambridge University Press.

> 국립국어원 표준국어대사전
```

---

## Content Structure

### Recommended Organization

```
1. 주제 소개
   - 정의와 범위
   - 왜 중요한가
   - 학습 목표

2. 핵심 개념
   - 기본 원리
   - 주요 용어
   - 개념 간 관계

3. 상세 설명
   - 세부 주제별 탐구
   - 예시와 사례
   - 일반적인 오해

4. 실생활 적용
   - 실용적 활용
   - 연습 활동
   - 자가 점검

5. 더 나아가기
   - 심화 주제
   - 추천 자료
   - 다음 단계
```

### Example Format

When explaining concepts:

```markdown
## 개념 설명: 인지 편향

### 정의

인지 편향(cognitive bias)은 사고 과정에서 발생하는
체계적인 오류 패턴입니다.

### 일상 예시

**확증 편향 (Confirmation Bias)**

상황: 새 스마트폰을 구매한 후

- 자신의 선택을 지지하는 리뷰만 눈에 들어옴
- 단점을 지적하는 의견은 무시하거나 반박
- "역시 내 선택이 옳았어"라고 확신

### 왜 중요한가?

- 의사결정의 질에 영향
- 대인관계에서 오해 발생
- 학습과 성장을 방해할 수 있음

### 극복 방법

1. 반대 의견을 의도적으로 찾아보기
2. "내가 틀렸다면?" 질문하기
3. 다양한 출처에서 정보 수집
```

### Language Learning Content Format

```markdown
## 영어 시제: 현재완료

### 형태

have/has + 과거분사 (p.p.)

| 주어          | 동사       | 예문                 |
| ------------- | ---------- | -------------------- |
| I/You/We/They | have eaten | I have eaten lunch.  |
| He/She/It     | has eaten  | She has eaten lunch. |

### 용법 1: 경험

"~해본 적 있다"
```

I have visited Paris.
(나는 파리에 가본 적이 있다.)

Have you ever tried sushi?
(초밥을 먹어본 적 있니?)

```

### 용법 2: 완료된 동작 (결과 강조)

```

I have finished my homework.
(숙제를 끝냈다 → 지금 다 된 상태)

```

### 연습문제

다음 문장을 현재완료로 바꾸세요:

1. I (see) this movie before.
2. She (never/eat) Korean food.
3. They (already/leave).

<details>
<summary>정답 보기</summary>

1. I have seen this movie before.
2. She has never eaten Korean food.
3. They have already left.

</details>
```

---

## Flexibility Guidelines

For general/mixed topics:

```markdown
> **참고**: 이 주제는 여러 분야에 걸쳐 있습니다.
>
> - 심리학적 관점: 인지 과정과 의사결정
> - 경제학적 관점: 행동경제학과 시장 행동
> - 사회학적 관점: 집단 역학과 사회 규범
>
> 이 문서에서는 주로 심리학적 관점에서 다루되,
> 필요에 따라 다른 관점도 소개합니다.
```

---

## Review Criteria

Review criteria for the reviewer agent when evaluating language/general domain documents.

### Critical Checks (ERROR if failed)

These issues trigger `NEEDS_REVISION` status:

| Check | Detection | Example |
|-------|-----------|---------|
| Undefined jargon | Technical terms without explanation | Using "화용론" without defining it |
| Missing practice exercises | Concept without application | Theory-only sections |
| Factual errors | Incorrect definitions or rules | Wrong grammar explanations |
| Ambiguous examples | Examples that don't illustrate concept | Confusing or edge-case examples |

### Quality Checks (WARN if issues)

These issues are noted but don't block publication:

| Check | Expectation | Notes |
|-------|-------------|-------|
| Theory-practice balance | ~50% each | Not purely theoretical |
| Everyday examples | Relatable scenarios | 일상적 상황 사용 |
| Self-check activities | 자가 점검 provided | Quiz or reflection questions |
| Progressive difficulty | Simple to complex | Clear difficulty escalation |

### Style Checks (INFO)

Minor issues for optional improvement:

| Check | Expectation | Notes |
|-------|-------------|-------|
| Bilingual glosses | Original + translation | zeitgeist (시대정신) |
| Abbreviation expansion | Spell out first use | CEFR (Common European...) |
| Cross-domain connections | Related fields noted | 심리학적/경제학적 관점 |
| Recommendation format | Next steps provided | 추천 자료, 다음 단계 |

### Accessibility Checklist

```markdown
# Accessibility requirements for general education:

□ No assumed prior knowledge beyond stated prerequisites
□ Technical terms defined on first use
□ Abstract concepts have concrete examples
□ Multiple learning modalities (text, examples, exercises)
□ Self-study friendly structure (summaries, checkpoints)
□ Clear learning objectives stated upfront
```

---

## Domain-Specific Sections for persona.md

```markdown
## Domain Guidelines: General/Language

**Approach**: 학습자 수준에 맞는 명확한 설명
**Examples**: 일상적이고 친숙한 예시 활용
**Practice**: 자가 점검 및 연습 활동 포함

**Terminology Handling**:

- 전문 용어 첫 등장 시 정의 제공
- 한국어/영어 병기 원칙
- 약어 풀어쓰기

**Content Balance**:

- 이론 50% + 예시/적용 50%
- 추상적 개념은 구체적 예시로 보완
- 다양한 관점 균형있게 제시

**Accessibility**:

- 전문가가 아닌 학습자 기준
- 단계별 난이도 조절
- 자가 학습 가능한 구조
```
