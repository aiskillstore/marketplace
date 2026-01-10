# History Domain Profile

> For historical events, periods, civilizations, and social history topics.

---

## Search Strategy

### Primary Sources

1. **Academic Journals**
   - JSTOR, Google Scholar
   - Historical journals (국사편찬위원회, 한국역사연구회)
   - Peer-reviewed articles

2. **Primary Sources / Archives**
   - National archives (국가기록원, 규장각)
   - Digital archives (한국사데이터베이스)
   - Original documents and manuscripts
   - Archaeological reports

3. **Reference Works**
   - Encyclopedias (Britannica, 한국민족문화대백과)
   - Historical dictionaries
   - Historiographical reviews

4. **Educational Resources**
   - University course materials
   - Museum educational content
   - Documentary transcripts

### Search Query Patterns

```
"{topic} primary sources"
"{topic} academic journal"
"{topic} historiography"
"{topic} archaeological evidence"
"{topic} 원전" (for Korean history)
"{topic} 사료"
"{period} {region} history"
"{topic} historical analysis"
"{topic} 연구사"
```

### Quality Indicators

- Academic peer review
- Primary source citations
- Recent historiographical perspective
- Multiple viewpoints presented
- Clear source attribution

---

## Special Fields

### Timeline

| Field              | Description         | Example               |
| ------------------ | ------------------- | --------------------- |
| `period`           | Historical period   | 조선 후기 (1700-1897) |
| `era_format`       | Date notation style | BCE/CE, 연호, 서기    |
| `key_dates`        | Important dates     | 1592 임진왜란         |
| `chronology_scope` | Time range covered  | 18-19세기             |

### Primary Sources

| Field           | Description              | Example                |
| --------------- | ------------------------ | ---------------------- |
| `source_types`  | Types of primary sources | 실록, 문집, 일기       |
| `archives`      | Key archives             | 규장각, 국사편찬위원회 |
| `languages`     | Original languages       | 한문, 이두, 한글       |
| `accessibility` | How to access            | 온라인 DB, 번역본      |

### Historiography

| Field                | Description                | Example            |
| -------------------- | -------------------------- | ------------------ |
| `major_scholars`     | Key historians             | 이병도, 신채호     |
| `schools_of_thought` | Historical interpretations | 실증사학, 민족사학 |
| `debates`            | Ongoing debates            | 임나일본부설 논쟁  |
| `revision_history`   | How views have changed     | 식민사관 극복 과정 |

---

## Terminology Policy

### Language Handling

| Type             | Policy                     | Example                |
| ---------------- | -------------------------- | ---------------------- |
| Historical terms | Original + modern Korean   | 봉건제(封建制)         |
| Names            | Korean reading + Chinese   | 정약용(丁若鏞)         |
| Foreign terms    | Original + transliteration | Renaissance (르네상스) |
| Dates            | 서기 기준 + 연호 병기      | 1592년 (선조 25년)     |

### First Occurrence Format

```markdown
## 실학(實學)

실학(實學, Silhak)은 조선 후기에 등장한 학문적 경향으로,
실제 생활에 유용한 학문을 추구했습니다.
```

### Citation Format

```markdown
> 『조선왕조실록』 선조실록 25년 4월 13일

> 정약용, 『목민심서』, 제1권 부임편
```

---

## Content Structure

### Recommended Organization

```
1. 시대적 배경
   - 이전 시대 상황
   - 사회적/정치적 맥락
   - 국제 정세

2. 핵심 사건/현상
   - 주요 사건 전개
   - 핵심 인물
   - 인과관계 분석

3. 다양한 관점
   - 동시대 시각
   - 후대 평가 변화
   - 현대적 해석

4. 사료와 증거
   - 1차 사료 소개
   - 고고학적 증거
   - 사료 비판

5. 영향과 의의
   - 후대에 미친 영향
   - 현대적 함의
   - 논쟁점과 과제
```

### Timeline Format

```markdown
## 연표

| 연도   | 사건          | 비고      |
| ------ | ------------- | --------- |
| 1592년 | 임진왜란 발발 | 선조 25년 |
| 1593년 | 행주대첩      |           |
| 1598년 | 전쟁 종결     | 노량해전  |
```

### Source Citation Requirements

- **1차 사료**: 원전 표기 + 현대어 해석
- **2차 사료**: 저자, 출처, 발행연도
- **다중 관점**: 최소 2개 이상의 해석 제시
- **출처 명시**: 모든 주장에 근거 표시

---

## Historiographical Notes

When presenting historical interpretations:

```markdown
> **역사학적 논쟁**: 실학의 성격에 대해서는 여러 해석이 존재합니다.
>
> - **근대화 맹아론**: 실학을 자생적 근대화의 싹으로 보는 시각
> - **체제 내 개혁론**: 유교 질서 내에서의 개혁 시도로 보는 시각
> - **비판적 재검토**: 실학이라는 범주 자체를 재검토하는 최근 연구
```

---

## Perspective Balance

When presenting controversial topics:

```markdown
## 다양한 시각

### 당대의 시각

조선 조정에서는 이를 어떻게 보았는가...

### 일본 측 시각

당시 일본 측 기록에 따르면...

### 현대 역사학의 평가

오늘날 역사학자들은 이 사건을...
```

---

## Review Criteria

Review criteria for the reviewer agent when evaluating history domain documents.

### Critical Checks (ERROR if failed)

These issues trigger `NEEDS_REVISION` status:

| Check | Detection | Example |
|-------|-----------|---------|
| Missing citations | Factual claims without source | "1592년에 발생" without citation |
| Unsupported interpretations | Opinions presented as facts | Subjective claims without "~라는 견해가 있다" |
| Anachronistic errors | Modern concepts imposed on past | Using modern political terms for historical contexts |
| Single-perspective bias | Only one viewpoint presented | Only Japanese or Korean view of colonial period |

### Quality Checks (WARN if issues)

These issues are noted but don't block publication:

| Check | Expectation | Notes |
|-------|-------------|-------|
| Primary source inclusion | 1차 사료 인용 권장 | 실록, 문집 등 원전 참조 |
| Timeline accuracy | Dates should be verified | Cross-reference with established chronologies |
| Multiple perspectives | 2+ viewpoints for contested topics | 역사적 논쟁 시 다양한 관점 |
| Historiographical context | Major debates acknowledged | 학계 논쟁 소개 |

### Style Checks (INFO)

Minor issues for optional improvement:

| Check | Expectation | Notes |
|-------|-------------|-------|
| Era notation consistency | 서기 + 연호 병기 | 1592년 (선조 25년) |
| Name format | 한국 독음 + 한자 | 정약용(丁若鏞) |
| Citation format | Consistent style | 『서명』 권, 편 형식 |
| Terminology glosses | Original + modern | 봉건제(封建制) |

### Content Balance Guidelines

```markdown
# Perspective balance checklist for controversial topics:

□ 당대의 시각 - How contemporaries viewed the event
□ 다른 당사자 시각 - Perspectives of other involved parties
□ 후대 평가 변화 - How interpretations changed over time
□ 현대 역사학 관점 - Current scholarly consensus and debates
```

---

## Domain-Specific Sections for persona.md

```markdown
## Domain Guidelines: History

**Primary Sources**: 원전 인용 시 출처 명시 필수
**Timeline Format**: {ERA_FORMAT} 표기, 세기 단위 사용
**Perspectives**: 다양한 역사적 관점 균형있게 제시

**Citation Conventions**:

- 1차 사료: 『서명』 권, 편, 날짜
- 2차 문헌: 저자, 『저서명』, 출판사, 연도

**Critical Approach**:

- 사료 비판적 읽기
- 다중 사료 대조
- 역사적 맥락 고려
```
