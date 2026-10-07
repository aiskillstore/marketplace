# Root-cause repair, not symptom suppression

## A finding must explain a causal chain

Write the observed symptom, minimum trigger, failing mechanism, enabling condition, and the invariant that should have prevented the failure. Separate observed facts from hypotheses. For a missing requirement, the root may be an undefined contract; do not invent product policy and call its implementation a fix.

Ask a counterfactual: **if this mechanism were corrected, would the failure still be possible through another caller or schedule?** Search for sibling uses of the same primitive and duplicate checks. Bound that search by the actual causal mechanism, not an unrelated full-codebase rewrite.

## Choose the smallest sufficient boundary

Prefer enforcing an invariant at its owner. A database uniqueness rule may need a constraint and a caller-compatible conflict path; a local precheck alone may still race. A retry duplication issue may require an idempotency key plus durable deduplication at the commit boundary, not a sleep. A tenant leak may need tenant-scoped authorization in a shared data access path, not hiding one UI button. The correct design depends on the actual system; these are mechanisms to investigate, not mandatory prescriptions.

Document why the chosen boundary blocks the failure class and what assumptions remain. A root cause can be a single incorrect operator. Do not inflate “root cause” into architectural replacement when a narrow, causally complete correction is safer.

## Test the proposed fix before accepting it

A regression should fail on the original behavior for the intended reason and pass on the repaired behavior. Distinguish a real reproduction from a model of the behavior. When a pre-fix execution would be unsafe or unavailable, label the substitute evidence and the verification gap rather than inventing a failure log.

Test a neighboring instance of the defect class: another caller, another tenant, an alternate encoding, repeated delivery, a different cancellation point, or an independent schedule. Include unaffected valid behavior. Generated tests must derive expectations from the requirement, not simply echo the patched implementation.

## Reject these shortcuts

Suppressing an exception without restoring the invariant; widening a timeout without understanding an unbounded wait; retries without idempotency; deleting or weakening failing tests; hardcoding a single input; treating string prefixes as authorization; compensating for inconsistent writes only at rendering time; swallowing partial failures; silently changing a public contract; upgrading a dependency blindly; introducing a new abstraction unrelated to the defect.

A mitigation can be appropriate during an incident. Label it **mitigation**, record the residual mechanism and expiry/owner, and do not mark the root-cause repair verified. The user must authorize operational incident actions independently.

## Patch acceptance record

Record original trigger and evidence, root cause, affected sites, invariant after the change, exact patch snapshot, defect regression, neighboring-class coverage, compatibility/rollout risks, and verification result. Review the patch itself for a new failure mechanism. When two attempts do not resolve the same defect, revisit the causal model and oracle before trying another modification.

Stop for authorization when the repair requires changing product semantics, widening permissions, a destructive migration, substantial public API breakage, production access, or a broad refactor outside scope. Preserve the evidence and propose the smallest next decision.
