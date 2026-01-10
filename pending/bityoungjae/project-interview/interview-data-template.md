# Interview Data Template

This template defines the structure for `interview-data.md`, which stores the conversation record.

---

## Template

```markdown
# Interview Data

> Generated: {TIMESTAMP}
> Status: {in_progress | completed}
> Language: {ko | en | ...}

---

## Conversation

**Interviewer**: 안녕하세요! 오늘은 어떤 걸 배워보고 싶으세요?

**Learner**: {user response}

**Interviewer**: {follow-up question}

**Learner**: {user response}

...

---

## Profile Summary

Presented to learner and confirmed:

- **Topic**: {what they want to learn}
- **Domain**: {technology | history | science | arts | general}
- **Level**: {beginner | intermediate | advanced}
- **Motivation**: {why they want to learn}
- **Style preference**: {theory-first | practice-first | examples-focused | ...}
- **Volume**: {small ~50p | medium ~100p | large ~200p}

---

## Key Insights

Observations for persona generation:

- {insight 1}
- {insight 2}
- {insight 3}

### Language & Tone Notes

- User formality: {formal | casual}
- Repeated keywords: {terms user emphasized}
- Special requests: {any specific requirements mentioned}

---

_This file is kept for reference when modifying persona.md._
```

---

## Example

```markdown
# Interview Data

> Generated: 2025-12-27T14:30:00+09:00
> Status: completed
> Language: ko

---

## Conversation

**Interviewer**: 안녕하세요! 오늘은 어떤 걸 배워보고 싶으세요?

**Learner**: Rust로 비동기 프로그래밍을 배우고 싶어요. 회사에서 백엔드 개발하는데, JavaScript로는 한계가 느껴져서요.

**Interviewer**: 아, 백엔드 개발자시군요! JavaScript의 어떤 부분이 한계로 느껴지셨어요? 그리고 Rust는 처음이신가요, 아니면 기초는 좀 아시나요?

**Learner**: 성능이랑 타입 안정성이요. Rust 기초 문법은 좀 봤어요. 소유권 개념까지는 이해했는데, 비동기 쪽은 아직이에요.

**Interviewer**: 그러시군요. 개발 환경은 주로 어떻게 되세요?

**Learner**: Ubuntu에서 작업해요.

**Interviewer**: 대화 나눠보니 이런 분이실 것 같아요:

- 배우려는 것: Rust 비동기 프로그래밍 (tokio, async/await)
- 배경: 현직 백엔드 개발자, JavaScript 경험 있음
- Rust 수준: 기초~중급 (소유권 이해, 비동기는 미경험)
- 동기: 성능과 타입 안정성 개선
- 환경: Linux (Ubuntu)

실무 적용이 목적이시니까, 중급자 대상으로 비동기 패턴에 집중한 100페이지 정도 분량이 적당할 것 같은데 어떠세요?

**Learner**: 좋아요! 근데 에러 핸들링도 좀 다뤄주시면 좋겠어요.

**Interviewer**: 물론이죠. 그럼 이대로 진행할까요?

**Learner**: 네!

---

## Profile Summary

- **Topic**: Rust 비동기 프로그래밍 (tokio, async/await, error handling)
- **Domain**: technology
- **Level**: intermediate
- **Motivation**: 업무 적용 (성능, 타입 안정성 개선)
- **Style preference**: theory-first, examples-focused
- **Volume**: medium (~100p)
- **Environment**: Linux (Ubuntu)

---

## Key Insights

- Backend developer transitioning from JavaScript to Rust
- Already understands ownership; async is the gap
- Practical focus: needs production-ready patterns
- Added request: error handling in async context

### Language & Tone Notes

- User formality: formal (존댓말)
- Repeated keywords: "업무", "성능", "한계"
- Special requests: error handling coverage

---

_This file is kept for reference when modifying persona.md._
```

---

## Usage Notes

1. Record the conversation naturally as it happens
2. Use exact quotes from the learner where relevant
3. Document the profile as presented and confirmed
4. Note insights that will inform persona generation
5. Keep language/tone notes for maintaining consistent voice
