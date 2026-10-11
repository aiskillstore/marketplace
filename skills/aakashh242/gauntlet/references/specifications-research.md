# Specifications, architecture, documentation, and research lens

Trigger: plans, architecture decisions, requirements, prose claims, experiments, or non-executable artifacts.

Identify the objective, stakeholders, authoritative constraints, assumptions, and acceptance criteria. Find contradictions, undefined terms, missing failure behavior, scope creep, hidden dependencies, unowned responsibilities, and requirements that cannot be tested as written. Distinguish a genuine gap from a deliberate tradeoff; propose a decision where product intent is missing rather than declaring one design universally correct.

Attack architecture claims with concrete counterexamples: a dependency is unavailable, data arrives twice or late, a tenant exceeds quota, a rollout is partial, a key actor lacks the assumed permissions, or recovery starts from an inconsistent state. Trace how the stated design handles the scenario. Review operational and migration feasibility rather than only an ideal request path.

For research or factual prose, retrieve primary sources when available and check that each claim matches what the source actually establishes. Separate observation, assumption, inference, and speculation. Review baselines, confounders, sample size, uncertainty, external validity, leakage, reproducibility, and whether the metric measures the intended goal. Do not turn a result from a toy benchmark into a guarantee about production systems.

For numerical claims, reconstruct the calculation, units, denominators, and sensitivity to assumptions. For proofs or invariants, state the model and the domain of the claim; a bounded exhaustive check does not cover an unbounded system. For specialized high-stakes decisions, identify where qualified domain review is needed.

A useful finding contains the exact contradictory statement or missing condition, why it matters to the goal, supporting evidence or counterexample, and a bounded correction. A stylistic preference is not a defect unless it violates an explicit communication requirement.

Verification can use a requirements traceability table, a concrete counterexample resolved by the revised design, a recalculated result, a primary-source check, or an explicit small model. Mark it as inspection/model evidence rather than executable production behavior. Re-review downstream claims whenever the corrected premise changes.
