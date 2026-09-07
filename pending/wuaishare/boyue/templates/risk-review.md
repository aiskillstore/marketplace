# Risk Review

Use this template when a committed decision may be expensive or hard to reverse.

## Decision under review

What is changing?

## Reversibility

- [ ] Easy to undo
- [ ] Moderately difficult
- [ ] Hard to reverse
- [ ] Effectively irreversible after adoption/data creation

Why?

## Failure consequence

- [ ] Low — local inconvenience or easy rework
- [ ] Medium — meaningful user or engineering impact
- [ ] High — broad outage, data, financial, security, or compatibility impact
- [ ] Critical — severe or irreversible harm

## Blast radius

Who and what can be affected?

## Material unknowns

- 

## Evidence required before ownership

Select only what reduces a material unknown:

- [ ] Disposable Spike
- [ ] PoC
- [ ] Prototype
- [ ] ADR
- [ ] Benchmark / load test
- [ ] User test
- [ ] Security review
- [ ] Migration rehearsal
- [ ] Rollback rehearsal
- [ ] AI evaluation on realistic inputs
- [ ] Other:

## Rollback / containment

How can the change be disabled, reversed, or contained if wrong?

## Shaping depth decision

- [ ] Fast path — proceed with normal implementation
- [ ] Focused validation — resolve named unknowns first
- [ ] Deep shaping — require stronger evidence and explicit Ownership Review

## Rationale

Why is this depth proportional to the cost of being wrong?
