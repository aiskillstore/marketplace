# Evidence and verification

## Evidence ladder

Prefer direct execution against the relevant artifact in a safe environment. Next-best evidence may be an exact source-level causal trace, a small bounded formal model, differential behavior against an independent reference, or an authoritative specification contradiction. Label the kind and its limits. A model opinion, majority agreement, green linter, or test name is not proof of behavioral correctness.

Every reported check needs a command/procedure, relevant environment/version, target snapshot, observed outcome, and evidence location or concise result. Record execution failures, timeouts, missing services, skipped tests, and fixture limitations. Redact secrets from logs while retaining the parts needed to reproduce. Do not report a proposed command as executed.

## Build useful tests

Select techniques based on the failure mechanism:

| Mechanism | Useful technique | Watch for |
| --- | --- | --- |
| Boundary/parse logic | Equivalence partitions and boundary-value tests | Empty vs absent, inclusive bounds, invalid encodings |
| Invariants over many inputs | Property-based or bounded fuzz tests | Meaningful oracle, valid generators, reproducible seed |
| State/order sensitivity | Model-based sequences and controlled scheduling | Event interleavings, cancellation, reconnect/restart |
| Partial failure | Fault injection at commit/side-effect boundaries | Invisible state after an error, retry behavior |
| Alternate implementation exists | Differential tests | Shared assumptions and matching bugs |
| Output transformations | Metamorphic relations | Relation must actually follow from the contract |
| Weak tests suspected | Targeted mutation/manual mutant | Non-equivalent mutant and expected failure reason |
| Resource/latency concern | Bounded workload and profiling | Warmup, input size, tail latency, resource ceilings |

Use project-native tools when already installed. A missing optional fuzzer does not prevent directed boundary testing. Never silently fetch executables or enable uncontrolled load tests. Inspection of untrusted package scripts comes before running them, even if the command is called `test`.

## Independence and the oracle

A different agent with the same model can share the author's blind spots. Give it the requirements and final artifact before the author's explanation. Require it to check the oracle as well as the patch. In solo mode, write the expected behavior before looking at the implementation's outputs. Report the actual independence level.

Keep factual confirmation and severity separate. A proven issue may be low impact; a plausible severe scenario may remain unconfirmed. Do not fabricate exploitability, data loss, performance figures, or test coverage percentages.

## Revision binding

A commit hash does not identify a dirty worktree. Record a scoped manifest/digest or equivalent host snapshot for code, relevant config, fixtures, and dependencies. Do not modify the target while a worker is testing it. Capture which snapshot each evidence item covers. Revalidate after edits, dependency updates, changed assumptions, or modified fixtures.

The helper intentionally invalidates **all** recorded checks and completed lens tasks on a target revision change and reopens verified fixes as patched. This conservative choice avoids a fragile dependency-analysis engine. A manual/host tracker may reuse an unaffected check only with an explicit dependency argument; it must still reset the clean streak and review the changed surface.

## Required checks and blocked checks

Register the checks chosen during triage before attempting closure. An additional failing relevant check must not be hidden merely because it was not registered. Restore or explain a baseline failure; do not relabel it as a pass. For a known unrelated baseline failure, keep the distinction in the report and require an explicit scoped decision before removing it from the acceptance contract.

If execution was required and cannot happen, the result is partial/blocked, not a clean execution-backed pass. A documentation/design review can use inspection if that was honestly its verification scope. An absent independent agent is disclosed as a limitation rather than fabricated.
