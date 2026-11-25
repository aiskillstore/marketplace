# Pressure Test Results

- Skill: `cinematic-shot-prompting`
- Date: 2026-08-31
- Method: main-agent fallback self-test
- Independent blind test: not completed. The two remaining extraction agents hit the environment's subagent usage limit; no additional agents were available for blind forward-testing.

## Results

| Case | Trigger decision | Expected action check | Result |
|---|---|---|---|
| should-trigger-01 | Trigger | Slow dolly-in contract includes start/end, subject lock and continuity | Pass |
| should-trigger-02 | Trigger | Occlusion reveal chosen; output can remain prompt-only | Pass |
| should-trigger-03 | Trigger | Detects fixed-camera/rising-camera contradiction before rewrite | Pass |
| should-trigger-04 | Trigger | English orbit prompt preserves radius, subject lock and background reveal | Pass |
| should-not-trigger-01 | Do not trigger | Static image prompt remains outside scope | Pass |
| should-not-trigger-02 | Do not trigger | Editing order remains outside scope | Pass |
| should-not-trigger-03 | Do not trigger | Color grading remains outside scope | Pass |
| should-not-trigger-04 | Do not trigger | Model/price comparison remains outside scope | Pass |
| edge-01 | Limited trigger | Converts effect word to task; asks only a material question | Pass |
| edge-02 | Trigger with boundary | Refuses false precision; requests keyframes/split | Pass |
| edge-03 | Trigger | Produces only requested prompt | Pass |
| edge-04 | Do not run full workflow | Gives a concise definition unless prompting is requested | Pass |

## Score

- Passed: 12/12 (self-test)
- Should-not-trigger passed: 4/4
- Self-test pass rate: 100%
- Confidence adjustment: moderate, because this was not an independent blind evaluation.

## Observed Design Corrections

1. The description explicitly excludes static image prompting, editing, grading and model recommendations to reduce over-triggering.
2. The workflow distinguishes “limited trigger” for vague cinematic intent from a full prompt-generation request.
3. The boundary requires keyframes or shot decomposition when the requested geometry cannot be supported by the available image.
4. Output format obeys “prompt only” requests instead of always adding teaching material.

## Remaining Risk

Automatic trigger precision should be rechecked in a fresh Codex session after installation. A future independent run should use the same test prompts without exposing their types or expected behaviors.
