---
name: AIR Cryptographer
description: This skill should be used when the user asks about "AIR", "algebraic intermediate representation", "ZK constraints", "trace design", "constraint soundness", "polynomial commitments", "FRI", "STARK", "lookup arguments", "permutation arguments", "memory consistency", "transition constraints", "boundary constraints", "vanishing polynomial", "quotient polynomial", "Fiat-Shamir", or needs expert-level cryptographic review of constraint systems.
---

# AIR Cryptographer Expertise

Expert-level knowledge for designing, implementing, and auditing Algebraic Intermediate Representations (AIRs) in zero-knowledge proof systems.

## Core Mindset

**Soundness-first thinking**: Every constraint review starts with "how could a cheater slip through?" Think adversarially. Construct counterexample traces by hand. Exploit polynomial identity loopholes.

**Algebraic precision**: Constraints define solution spaces over finite fields. A missing constraint isn't just a bug—it's extra degrees of freedom for a malicious prover.

## Finite Field Foundations

Essential intuitions:

- **Characteristics and inverses**: Every non-zero element has a multiplicative inverse. No zero divisors.
- **Roots of unity**: Multiplicative subgroups of order 2^k enable FFT-friendly evaluation domains.
- **Extension fields**: When you need more algebraic structure (e.g., M31 → QM31 for Stwo).
- **Frobenius endomorphism**: The map x → x^p is field-linear; crucial for extension field arithmetic.

## Polynomial Mechanics

**Interpolation**: Given n points, unique polynomial of degree < n passes through them. Lagrange basis makes this explicit.

**Vanishing polynomials**: Z_H(x) = ∏(x - h) for h ∈ H vanishes exactly on domain H. This is the foundation of constraint enforcement.

**Degree behavior**:

- Multiplication: deg(f·g) = deg(f) + deg(g)
- Composition: deg(f∘g) = deg(f) · deg(g)
- Low-degree testing verifies a function is "close to" a low-degree polynomial

**Evaluation domains**: Multiplicative cosets for separation. Blowup factor determines security margin between trace degree and domain size.

## Trace Design Principles

### Column Classification

| Type                | Definition                   | Example                      |
| ------------------- | ---------------------------- | ---------------------------- |
| **Source of truth** | Canonical witness data       | PC, registers, memory values |
| **Derived**         | Computed from source columns | Flags, decompositions        |
| **Auxiliary**       | Added to reduce degree       | Intermediate products        |

**Critical rule**: Every column must be constrained. An unconstrained column is a free variable for the prover.

### Row Semantics

Define precisely what each row represents:

- CPU cycle / instruction
- Memory operation
- Padding (must be distinguishable!)

Row types require selectors. Selectors must be:

- Boolean: `s(s-1) = 0`
- Mutually exclusive: `Σ s_i = 1` (or coverage proof)
- Actually constrained (not just documented)

### Minimal vs Redundant Columns

Start minimal. Add auxiliary columns only when:

- Degree reduction is necessary
- Soundness requires explicit intermediate values
- Verification cost dominates

## Constraint Categories

### Transition Constraints (Local)

Express correct step relation between row i and row i+1:

```text
next_pc = pc + instruction_size  (when not branching)
next_register[k] = f(current_state, opcode)
```

**Danger**: Writing a relation instead of a function. Multiple valid next-states = unsound.

### Boundary Constraints

Pin specific rows to specific values:

- **Initial**: Row 0 state matches expected start
- **Final**: Last row satisfies termination condition
- **I/O**: Public inputs/outputs bound at known positions

**Danger**: "Final row" must be uniquely defined. Variable-length traces need explicit halt handling.

### Booleanity and Range Constraints

For boolean b: `b(b-1) = 0`

For k-bit value x with bits b*0...b*{k-1}:

```text
x = Σ b_i · 2^i
b_i(b_i - 1) = 0  for all i
```

**Danger**: Forgetting booleanity constraints on decomposition bits.

### Selector Discipline

Selectors gate which constraints apply to which rows.

**Checklist**:

- [ ] Each selector is boolean
- [ ] Exactly one selector active per row (or explicit coverage)
- [ ] No "ghost mode" where all selectors = 0
- [ ] Selector itself is constrained (not free)

**Classic bug**: All selectors zero makes all gated constraints vacuously true.

## Global Consistency Arguments

### Permutation / Multiset Equality

Prove two multisets are equal via grand product:

```text
∏(α - a_i) = ∏(α - b_i)
```

**Checklist**:

- Initial product = 1 (boundary constraint)
- Final products equal (boundary constraint)
- Challenge α bound to transcript after commitments
- Duplicates handled correctly

**Danger**: Product hitting zero, missing boundary constraints, challenge reuse.

### Lookup Arguments

Prove all values in column A appear in table T.

**Checklist**:

- Table is committed/fixed
- Compression is collision-resistant (sufficient randomness)
- Repeated lookups soundly counted

**Danger**: Weak compression allows out-of-table values.

### Memory Consistency

Memory operations form a log: (address, timestamp, value, is_write)

**Patterns**:

- Sort by address, then by timestamp
- Consecutive same-address ops: read sees last write
- Permutation links memory log to CPU trace

**Danger**:

- Address aliasing across different trace sections
- Timestamp not proven monotonic
- Read-before-write not enforced

## Quotient and Composition

Constraint polynomial C(x) should vanish on trace domain H.

Quotient: `Q(x) = C(x) / Z_H(x)`

If C doesn't vanish on H, Q has poles → not low-degree → FRI rejects.

### Row-Set Control

Constraints apply to different row sets:

- All rows: divide by Z_H(x)
- All but last: divide by Z_H(x) / (x - ω^{n-1})
- First only: multiply by Lagrange selector for row 0
- Last only: multiply by Lagrange selector for row n-1

**Danger**: Constraint meant for "all rows" accidentally only enforced on subset due to incorrect vanishing factor.

### Degree Accounting

Track degree of every constraint:

```text
Base constraint degree: d
After selector multiplication: d + deg(selector)
After boundary polynomial: d + deg(boundary)
```

Composition polynomial degree must stay below domain size with sufficient margin (blowup factor).

## Fiat-Shamir Hygiene

**Transcript must bind**:

- All commitments (trace, lookup tables, etc.)
- Public inputs
- Trace length / domain parameters
- Any prover messages

**Challenge separation**: Different arguments need independent challenges. Reusing challenges creates algebraic vulnerabilities.

**Danger**: Challenge derived before commitment → prover can adapt witness.

## Adversarial Witness Exercises

Before declaring an AIR sound, try to break it:

1. **All selectors = 0**: Do constraints still enforce anything?
2. **Corrupt one column**: Can it drift without detection?
3. **Attack last row**: Dump inconsistency into wrap-around?
4. **Duplicate/omit memory events**: Does global check catch it?
5. **Force product to zero**: Exploit grand product boundary?
6. **Exploit gating**: Make "if flag then X" vacuous by leaving flag unconstrained?

If you find a counterexample trace, you found a bug.

## Common Vulnerability Patterns

| Pattern              | Symptom                    | Fix                                |
| -------------------- | -------------------------- | ---------------------------------- |
| Unconstrained column | Prover sets arbitrarily    | Add constraint                     |
| Missing booleanity   | Non-binary "boolean"       | Add b(b-1)=0                       |
| Selector leakage     | Constraint bypassed        | Enforce exclusivity                |
| Last row escape      | Inconsistency hidden       | Proper terminal constraints        |
| Product zero         | Permutation argument fails | Boundary checks, domain separation |
| Challenge reuse      | Algebraic cancellation     | Separate challenges per argument   |
| Weak compression     | Lookup collision           | Increase randomness                |

## Performance-Aware Design

Understand tradeoffs without being an engineer:

| Choice            | Prover Cost          | Verifier Cost | Soundness    |
| ----------------- | -------------------- | ------------- | ------------ |
| More columns      | Higher memory        | Unchanged     | Neutral      |
| Higher degree     | More FRI rounds      | More queries  | Watch blowup |
| More rows         | Linear scaling       | Log scaling   | Neutral      |
| Auxiliary columns | Memory + constraints | Unchanged     | Can improve  |

**Rules of thumb**:

- Auxiliary columns to reduce degree often worth it
- Local constraints cheaper than global arguments
- Precomputation tables vs dynamic checks: depends on table size

## Review Deliverables

When reviewing an AIR, produce:

1. **Column inventory**: Name, meaning, range, where constrained
2. **Constraint map**: Each semantic claim → which constraint enforces it
3. **Degree table**: Every constraint's degree contribution
4. **Adversarial tests**: Attempted counterexamples
5. **Risk ranking**: Critical / High / Medium findings
6. **Proposed fixes**: Concrete constraint additions/modifications

See `references/review-checklist.md` for the complete systematic review sheet.
