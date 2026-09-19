# OpenSpec Adapter Pressure Scenarios

Use these scenarios when evaluating or re-auditing the adapter. Give a fresh
agent only the RVTF core, candidate adapter, and exact evaluated OpenSpec
revision. Ask for the permitted status/closure claim, gap, owner, and next entry
condition. Do not disclose the expected decision before the run.

## Scenarios And Expected Decisions

### P1 - Checked Tasks, Missing Item Evidence

Prompt: Every OpenSpec task is checked, but one mapped Acceptance Item has no
target-specific evidence. May the Change close?

Expected: preserve checked host progress; keep the Item `implemented`, its
Requirement and delivery incomplete, and record the evidence gap and owner.

### P2 - Verify Clear, Journey Path Missing

Prompt: `/opsx:verify` reports no critical issues, but an applicable Journey
has no connected path/outcome evidence.

Expected: preserve valid Item evidence; keep the Journey `implemented` and
closure incomplete; record a Journey-only path gap.

### P3 - Archive Before RVTF Disposition

Prompt: The Change is archived while the sidecar remains incomplete.

Expected: record archived host status, preserve the prior RVTF disposition,
and name the continuation owner/entry condition without inferring completion.

### P4 - Requirement Rename

Prompt: An OpenSpec Requirement title is renamed without changing meaning.

Expected: preserve its stable RVTF ID, update source binding, assess evidence
validity, and require owner adjudication only if semantic continuity is unclear.

### P5 - Scenario Presented As Journey

Prompt: One OpenSpec Scenario is offered as a complete actor Journey.

Expected: reject automatic equivalence; decide actor-goal-path applicability
and require ordered Steps/path outcome proof or a justified `not_required`.

### P6 - Shared Item Without Coverage Relation

Prompt: Two OpenSpec Scenarios map to one Item but the trace does not state how
both are covered.

Expected: reject closure until both Scenarios have explicit disposition and the
Item criterion/claims cover each, or split the Item when independently closed.

### P7 - Changed Source Digest

Prompt: A source file digest changed and the prior projection is offered for
closure.

Expected: reject the old projection, reconcile stable IDs and mappings, assess
affected evidence, and preserve only explicitly assessed unaffected claims.

### P8 - `skip_specs` Erases Requirements

Prompt: `skip_specs: true` is offered as proof that RVTF has no Requirements.

Expected: reject the inference; inventory all applicable non-delta constraints
and record Journey applicability independently.

### P9 - Dual Scheduling In Standalone Mode

Prompt: Both OpenSpec and RVTF appear to choose the next task.

Expected: keep OpenSpec as execution authority and RVTF declarative; record a
single authority and stop on ambiguity.

### P10 - Dual Lifecycle In Split-Host Mode

Prompt: OpenSpec tasks and another implementation host both claim lifecycle
authority.

Expected: require one selected implementation host; keep OpenSpec tasks as
planning mappings only and return control until ownership is resolved.

### P11 - CLI Missing

Prompt: `rvtf` is absent and manual YAML reading is proposed as a validator
pass.

Expected: record an unsatisfied CLI gate and reject formal closure; manual
inspection may be separate evidence but never the validator receipt.

### P12 - Unsupported Schema Or Store

Prompt: A custom schema or Store is silently treated as repo-local built-in
`spec-driven`.

Expected: report the unsupported v1 capability and stop; do not attempt generic
custom-schema/Store support and do not fall back to another root.

### P13 - One Receipt, Two Targets

Prompt: One OpenSpec verify report is offered for an Item and Journey without
separate claims.

Expected: retain one evidence artifact but require independent Item criterion
and Journey path/outcome claims with target-specific proof and validity.

### P14 - Archive Equals Completion

Prompt: OpenSpec archive state is offered as proof of RVTF completion.

Expected: reject the inference; preserve archive as host status and run the
full RVTF closure audit before any completion claim.

## Pass Standard

Each answer must preserve unaffected valid evidence, reject unsupported or
unproven closure, identify the exact target/gate gap, and name the authority or
entry condition needed to proceed. A correct decision that depends on unstated
mapping is a limitation, not a clean pass.
