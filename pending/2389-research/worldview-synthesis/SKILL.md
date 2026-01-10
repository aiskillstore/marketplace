---
name: worldview-synthesis
description: This skill should be used when someone wants to articulate, explore, or document their personal worldview, values, or philosophy. Triggers on "articulate my values", "figure out what I believe", "document my philosophy", "write a manifesto", "define my leadership philosophy", "explore my beliefs". Surfaces beliefs through systematic interrogation, identifies tensions, and generates narrative outputs.
---

# Worldview Synthesis

**Core principle:** A worldview isn't a list of opinions—it's a graph of beliefs with tensions. The goal is to surface what someone already believes, name the contradictions, and synthesize into something they can share.

## When to Use

- Someone says "I want to articulate my values"
- Someone says "help me figure out what I believe"
- Someone wants to document their philosophy
- Someone is preparing for leadership, writing a manifesto, or defining a company culture

## The Method

### Phase 1: Bootstrap Structure

Create project structure:

```
worldview/
├── data/
│   ├── schema.yaml      # Structure definitions
│   ├── ideas.yaml       # Belief nodes
│   ├── sources.yaml     # Influences (books, people, experiences)
│   └── tensions.yaml    # Productive paradoxes
├── narrative/
│   ├── mission.md       # One-liner + principles
│   ├── thesis.md        # One page
│   ├── synopsis.md      # Three sections
│   └── full-narrative.md
└── README.md
```

### Phase 2: Seed from Sources

Ask: "What books, articles, people, or experiences shaped how you see the world?"

For each source, extract 3-5 key ideas. This gives you initial nodes to build from.

### Phase 3: Interrogation Rounds

Run 4-6 rounds of questions. Each round covers 3-4 domains.

**Question Design Rules:**
- 2-4 options per question, each with label + description
- Use `multiSelect: true` when beliefs can coexist
- Leave room for custom "Other" answers
- Options should be genuinely different, not leading

**Domains to Cover:**

| Domain | Example Questions |
|--------|-------------------|
| **Mortality** | How does knowing you'll die shape how you live? |
| **Metaphysics** | What's your relationship with spirituality/religion? |
| **Relationships** | How do you think about romantic partnership? |
| **Parenting** | Philosophy on having/raising children? |
| **Body** | How do you relate to physical health and aging? |
| **Vices** | Relationship with alcohol, drugs, pleasure? |
| **Money** | Beyond spending—freedom, obligation, suspicion? |
| **Competition** | Collaboration vs ruthlessness? |
| **Trust** | Default open or earned? |
| **Learning** | Autodidact, mentorship, formal education? |
| **Nature** | Essential or nice to visit? |
| **Leadership** | Natural, reluctant, servant, example? |
| **Emotion** | Relationship with anger? |
| **Recognition** | Need fame? Already had it? |
| **Rest** | Protect sleep or run on fumes? |
| **Conflict** | Clear air fast or avoid? |
| **Work** | Philosophy on effort, failure, shipping? |
| **Ethics** | Hard lines vs softer truths? |
| **Society** | Diagnosis of what's broken? |
| **Future** | Optimism, pessimism, preparation? |

### Phase 4: Capture Tensions

When beliefs contradict, DON'T resolve—NAME:

```yaml
- id: collaboration-vs-ruthlessness
  ideas: [collaboration-over-competition, strategic-ruthlessness]
  description: "Default to positive-sum, but crush when necessary"
  resolution: |
    Different contexts call for different modes. Collaboration is default.
    Ruthlessness is available when needed. The key is knowing when to switch.
  status: embraced  # or: unresolved, resolved
```

Tensions are often the most interesting part of a worldview.

### Phase 5: Generate Narratives

From data, generate at ascending scales:

1. **Mission** (~100 words): The one-liner + 5-7 principles
2. **Thesis** (~300 words): One page that captures the core
3. **Synopsis** (~500 words): Three sections (Diagnosis, Orientation, Ethics)
4. **Full Narrative** (~2000 words): Complete essay with all major themes

### Phase 6: Iterate

A worldview is living. Add new beliefs, update old ones, regenerate narratives.

## Idea Node Schema

```yaml
- id: kebab-case-unique-id
  title: "Human Readable Title"
  domain: personal | ethics | society | technology | metaphysics
  claim: "The actual belief in one clear sentence"
  confidence: 0.0-1.0  # how sure?
  importance: 0.0-1.0  # how central to worldview?
  tags: [relevant, keywords]
  sources: [source-ids-if-any]
  supports: [ideas-this-reinforces]
  tensions: [ideas-this-contradicts]
  notes: "Context, caveats, origins"
```

## Tension Statuses

- **embraced**: Both sides are true. Live in the paradox.
- **resolved**: Found synthesis that dissolves the tension.
- **unresolved**: Genuinely don't know. Honest about uncertainty.

## Sample Interrogation Round

```
Round 3: Money, Competition, Trust

Q1: How do you think about money beyond 'spend it'?
- Tool for freedom: Money buys optionality and autonomy
- Obligation to share: If you have more, redistribute
- Wealth is suspect: Getting rich usually means exploitation
- Generational thinking: Think about what to leave behind
[multiSelect: true]

Q2: What's your orientation toward competition?
- Compete hard, play fair: Want to win but not by cheating
- Collaboration over competition: Prefer positive-sum games
- Against yourself mostly: Real competition is self-improvement
- Strategic ruthlessness: Sometimes you have to crush opponents
[multiSelect: true]

Q3: How do you approach trust with new people?
- Trust until betrayed: Default open, pull back if needed
- Trust is earned: Start cautious, let people prove themselves
- Read the situation: Neither default—assess individually
- Trust systems not people: Rely on structures over character
[multiSelect: false]
```

## Red Flags

- **"I don't have a worldview"** → Everyone does. Start with sources.
- **No tensions found** → Dig deeper. Everyone has contradictions.
- **All high confidence** → Push on uncertainty. What don't you know?
- **Only "should" beliefs** → Ask what they actually DO, not just believe.
- **Avoiding hard questions** → Death, money, conflict—go there.

## Output Quality Checklist

- [ ] Core thesis is one sentence
- [ ] Mission fits on a card
- [ ] Tensions are named, not hidden
- [ ] Hard lines are clear (non-negotiables)
- [ ] Softer truths acknowledged (where grace lives)
- [ ] Narrative voice sounds like the person
- [ ] Contradictions are embraced, not resolved away

## Example Mission Output

```markdown
# Mission Statement

**Put people first. Prepare for what's coming. Fight anyway.
Find the cracks. Leave no trace.**

---

We operate with systemic pessimism and local optimism.
We hold strong opinions weakly.
We embrace productive paradoxes.
We draw hard lines on human rights.
We extend grace for pain, never for harm.

People first. Always.
```
