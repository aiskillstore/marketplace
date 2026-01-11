# Experimentation Playbook

## RICE Scoring

| Factor         | Definition                          | Score              |
| -------------- | ----------------------------------- | ------------------ |
| **R**each      | How many users affected per quarter | 1-10               |
| **I**mpact     | Effect on target metric             | 0.25, 0.5, 1, 2, 3 |
| **C**onfidence | How sure are we                     | 10%-100%           |
| **E**ffort     | Person-weeks to implement           | 0.5+               |

### Score = (Reach × Impact × Confidence) / Effort

## ICE Scoring (Simpler)

| Factor         | Definition            | Score |
| -------------- | --------------------- | ----- |
| **I**mpact     | Potential effect      | 1-10  |
| **C**onfidence | How sure              | 1-10  |
| **E**ase       | How easy to implement | 1-10  |

### Score = (Impact + Confidence + Ease) / 3

## Test Documentation Template

```markdown
# Experiment: [Name]

## Metadata

- **Owner**: [Name]
- **Start Date**: [Date]
- **Status**: Draft | Running | Analyzing | Complete

## Hypothesis

If we [change], then [metric] will [improve/decrease] by [amount]
because [reasoning].

## Target Segment

- [User type, cohort, geography, etc.]

## Variants

| Variant     | Description        |
| ----------- | ------------------ |
| Control     | Current experience |
| Treatment A | [Description]      |

## Success Metrics

- **Primary**: [Metric + expected lift]
- **Secondary**: [Additional metrics]

## Guardrails

- [Metric] must not decrease by more than [X%]
- [Metric] must stay above [threshold]

## Sample Size & Duration

- Required sample: [N per variant]
- Estimated duration: [X days/weeks]
- Minimum detectable effect: [X%]

## Kill Criteria

Stop if:

- Guardrail breached by [X%]
- Clear loser after [N] days
- Technical issues affecting [X%] of users

## Results

[To be filled after experiment]

## Learnings & Next Steps

[To be filled after analysis]
```

## Statistical Rigor

### Sample Size Calculation

- Baseline conversion rate
- Minimum detectable effect (MDE)
- Statistical power (typically 80%)
- Significance level (typically 95%)

### Common Mistakes

- [ ] Peeking at results before adequate sample
- [ ] No correction for multiple comparisons
- [ ] Ignoring novelty effects
- [ ] Too short duration (need full week cycles)
- [ ] Selection bias in test assignment

### When to Use

| Method             | Use Case                                 |
| ------------------ | ---------------------------------------- |
| A/B test           | Clear control, adequate traffic          |
| Multi-armed bandit | Optimization, less learning              |
| Holdout            | Measuring cumulative impact              |
| Geo split          | When user-level randomization impossible |

## High-Impact Test Areas

### Onboarding (Usually Highest ROI)

- [ ] Number of steps
- [ ] Required vs optional fields
- [ ] Progress indicators
- [ ] First value moment
- [ ] Template/preset options
- [ ] Social proof placement

### Pricing & Packaging

- [ ] Price points
- [ ] Feature gating
- [ ] Plan names
- [ ] Annual vs monthly default
- [ ] Trial length
- [ ] Upgrade prompts

### Activation

- [ ] Definition of "activated"
- [ ] Time to activation
- [ ] Activation rate by cohort
- [ ] Blockers in flow

### Retention

- [ ] Re-engagement emails
- [ ] Push notification timing
- [ ] Feature discovery
- [ ] Habit formation hooks

### Referral

- [ ] Incentive structure (give/get)
- [ ] Share mechanism (link, email, social)
- [ ] Placement of referral prompt
- [ ] Copy and framing
