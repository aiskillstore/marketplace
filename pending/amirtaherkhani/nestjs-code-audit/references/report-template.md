# NestJS Code Audit Report Template

Use this template as a contract, not as filler. Remove empty sections only when the report explicitly states why they are not applicable.

```markdown
# NestJS Code Audit

## Audit verdict

- Verdict: pass | pass with risks | fail
- Scope: <repository root or relative path>
- Baseline: <one sentence describing observed architecture>
- Revision: <branch and commit, plus dirty state>

## Quality gates

| Gate | Result | Evidence |
| --- | --- | --- |
| TypeScript/syntax | pass/fail/not run | `<command>` or reason |
| Lint | pass/fail/not run | `<command>` or reason |
| Tests | pass/fail/not run | `<command>` or reason |
| Semantic audit | pass/fail/partial | reviewed files and exclusions |

## Finding summary

| Owner | Critical | High | Medium | Low |
| --- | ---: | ---: | ---: | ---: |
| Toolchain | 0 | 0 | 0 | 0 |
| Architecture | 0 | 0 | 0 | 0 |
| OOP/design | 0 | 0 | 0 | 0 |
| Runtime | 0 | 0 | 0 | 0 |
| Security | 0 | 0 | 0 | 0 |
| Testing | 0 | 0 | 0 | 0 |

## Confirmed findings

### ARCH-001 [high] <specific problem>

- Owner: `nestjs-architecture-principles`
- Evidence: `src/example/example.service.ts:42` plus import/call path or diagnostic
- Impact: <current or credible consequence>
- Minimal remedy: <smallest safe change>
- Validation: <test, static rule, or runtime check>

## Needs verification

| Candidate | Why unconfirmed | Smallest next check |
| --- | --- | --- |
| <signal> | <missing evidence> | <read-only or controlled check> |

## Healthy patterns

- <verified control and evidence>

## Recommended order

1. <root-cause or critical correctness/security issue>
2. <dependent boundary or toolchain repair>
3. <lower-risk maintainability improvement>
```

Do not include a numeric quality score. A single number hides severity, audit coverage, and checks that were not run.
