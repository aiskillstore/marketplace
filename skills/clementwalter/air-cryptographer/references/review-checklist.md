# AIR Soundness Review Checklist

Systematic procedure for auditing AIR constraint systems.

## 0) One-Page Summary (Force Clarity)

Before diving into details, answer these questions:

| Question              | Answer                                             |
| --------------------- | -------------------------------------------------- |
| **Claimed statement** | What does the proof certify, in one sentence?      |
| **Trace length**      | Fixed or variable? How is n bound into transcript? |
| **Public inputs**     | What are they? Where enforced (which rows)?        |
| **Witness**           | What can the prover choose freely?                 |

---

## 1) Trace & State Model

### 1.1 Column Inventory

Create a table for every column:

| Column Name | Meaning             | Source/Derived | Range   | Where Constrained     |
| ----------- | ------------------- | -------------- | ------- | --------------------- |
| pc          | Program counter     | Source         | Field   | Transition            |
| opcode      | Current instruction | Derived        | 0-31    | Boundary + Transition |
| flag_halt   | Halt indicator      | Derived        | Boolean | Transition            |
| ...         | ...                 | ...            | ...     | ...                   |

**Red flags**:

- Column only "documented" but never constrained
- Derived column's derivation constraint is gated or incomplete

### 1.2 Row Semantics

Answer:

- What does a row represent? (cycle, instruction, event, memory op, padding)
- Are there distinct row types? How are they selected?
- Is padding distinguishable from real rows?

**Red flags**:

- Padding rows can leak into "real" rows (selector not enforced)
- Ambiguous row interpretation (no row-type selector)

---

## 2) Boundary Constraints

### 2.1 Initial State

| Column | Expected Value | Constraint         |
| ------ | -------------- | ------------------ |
| pc     | 0              | `boundary_pc_init` |
| fp     | initial_fp     | `boundary_fp_init` |
| ...    | ...            | ...                |

**Check**: Are equalities unconditional (not gated)?

### 2.2 Final State / Termination

- [ ] Machine halts correctly proven?
- [ ] Halt flag becomes 1 and stays 1?
- [ ] Variable length: "early stop" / "late garbage" prevented?

### 2.3 Public I/O Placement

- [ ] Where are public inputs bound? (row index, hash, etc.)
- [ ] Bound to transcript?
- [ ] Enforced in constraints?

**Red flags**:

- "Final output equals public output" but final row not uniquely defined
- Output constrained only on subset prover can avoid via selectors

---

## 3) Transition Constraints

### 3.1 Deterministic Step Relation

For each semantic update rule:

| Rule            | Next-State Function    | Constraint Name      |
| --------------- | ---------------------- | -------------------- |
| PC increment    | next_pc = pc + size    | `trans_pc_increment` |
| Register update | next_reg = f(op, args) | `trans_register_*`   |
| ...             | ...                    | ...                  |

**Red flags**:

- Proving a relation (multiple next states) not a function
- Next-state gated by unconstrained selector

### 3.2 Selectors & Opcode Logic

**Checklist**:

- [ ] Booleanity: `s(s-1) = 0` for each selector
- [ ] Exclusivity: `Σ s_i = 1` (or ≤1 + coverage)
- [ ] No "ghost mode": every row has defined opcode/type

**Red flags**:

- Missing `Σ s_i = 1` allows all selectors 0 → transitions vacuous
- Overlapping selectors mix instruction semantics

### 3.3 Wrap-Around / Last Row Handling

- [ ] If `next` at last row wraps to first: is that intended?
- [ ] If not: transition constraints disabled on last row correctly?
- [ ] Last-row selector enforced (e.g., via counter)?

**Red flags**:

- Last row unconstrained → prover dumps inconsistencies there
- "Last row" flag not uniquely pinned to single row

---

## 4) Range, Booleanity, and Representation

### 4.1 Booleans

For each boolean column:

- [ ] Booleanity constraint exists: `b(b-1) = 0`
- [ ] Constraint is unconditional where needed

### 4.2 Decompositions (Limbs/Bits)

For decomposition `x = Σ limb_i · B^i`:

- [ ] Reconstruction constraint present
- [ ] Limb range constraints present
- [ ] Carry constraints (if addition/multiplication)

### 4.3 Zero Checks / Inverses

For pattern "prove a ≠ 0 via `a · a_inv = 1`":

- [ ] `a_inv` exists only when needed (properly gated)
- [ ] If using `is_zero` gadgets: both branches enforced

**Red flags**:

- Inverse unconstrained when a=0 due to gating mistake
- Missing link between `is_zero` flag and actual value

---

## 5) Global Consistency Arguments

### 5.1 Multiset Equality / Permutation

**Definition**: What multisets are being matched?

| Left Multiset  | Right Multiset | Purpose            |
| -------------- | -------------- | ------------------ |
| CPU memory ops | Memory table   | Memory consistency |
| ...            | ...            | ...                |

**Checklist**:

- [ ] Duplicates handled correctly
- [ ] Challenges mixed with sufficient entropy
- [ ] Initial product = 1 (boundary constraint)
- [ ] Final products equal (boundary constraint)

**Red flags**:

- Product starts at 0 or can hit 0 easily
- Missing boundary conditions for product column
- Prover can omit rows from one multiset (row-type not bound)

### 5.2 Lookups

**Definition**: What is being looked up?

| Source Column(s) | Table         | Compression        |
| ---------------- | ------------- | ------------------ |
| opcode_bits      | Valid opcodes | Linear combination |
| ...              | ...           | ...                |

**Checklist**:

- [ ] Out-of-table values prevented
- [ ] Repeated lookups soundly handled
- [ ] Compression collision-resistant

**Red flags**:

- Lookup only checks "in compressed set" but compression weak
- Table rows not committed or can be altered

### 5.3 Memory Model

**Schema**: (address, timestamp, value, is_write, ...)

**Semantics**:

- [ ] Last-write-wins defined
- [ ] Read-before-write rules specified
- [ ] Global enforcement: sorting / permutation / multiset

**Red flags**:

- Address aliasing (same address, different interpretation)
- Reads not linked to prior writes
- Timestamp/counter not enforced monotone

---

## 6) Composition / Quotient Correctness

### 6.1 Constraint Row Sets

For each constraint, specify enforcement set:

| Constraint       | Row Set      | Mechanism           |
| ---------------- | ------------ | ------------------- |
| `trans_pc`       | All but last | Z_H / (x - ω^{n-1}) |
| `boundary_init`  | First only   | Lagrange L_0        |
| `boundary_final` | Last only    | Lagrange L\_{n-1}   |
| `selector_bool`  | All          | Z_H                 |

**Red flags**:

- Constraint meant "all rows" but only holds on subset
- Selector used in gating not constrained on same row set

### 6.2 Degree Accounting

| Constraint     | Base Degree | After Gating | After Boundary | Final |
| -------------- | ----------- | ------------ | -------------- | ----- |
| `trans_pc`     | 2           | 3            | 3              | 3     |
| `opcode_check` | 5           | 6            | 6              | 6     |
| ...            | ...         | ...          | ...            | ...   |
| **Max**        |             |              |                | **X** |

**Red flags**:

- Unnoticed degree blowup from selector products
- Composition degree too close to domain size

---

## 7) Fiat-Shamir Binding

**Checklist** - These must be in transcript before challenges:

- [ ] Trace commitments
- [ ] Public inputs
- [ ] Trace length / domain parameters
- [ ] Lookup tables / permutation commitments

**Challenge Separation**:

- [ ] Distinct challenges per argument
- [ ] No accidental reuse creating cancellation

**Red flags**:

- Challenge depends on something prover can adapt after seeing it
- Reused challenge creates algebraic cancellation

---

## 8) Adversarial Witness Exercises

**Mandatory attack attempts**:

### 8.1 All Selectors = 0

Set every selector to 0. Do constraints still enforce anything meaningful?

**Result**: [ ] Sound / [ ] Vulnerable
**Notes**: **\*\***\_\_\_**\*\***

### 8.2 Corrupt One Column

Pick a column. Can it drift arbitrarily without other constraints catching it?

**Result**: [ ] Sound / [ ] Vulnerable
**Notes**: **\*\***\_\_\_**\*\***

### 8.3 Attack Last Row

Can you dump inconsistency into last row / exploit wrap-around?

**Result**: [ ] Sound / [ ] Vulnerable
**Notes**: **\*\***\_\_\_**\*\***

### 8.4 Duplicate/Omit Memory Events

Can you add fake memory ops or remove real ones?

**Result**: [ ] Sound / [ ] Vulnerable
**Notes**: **\*\***\_\_\_**\*\***

### 8.5 Product Zero Attack

Can you force grand product to 0 and bypass permutation check?

**Result**: [ ] Sound / [ ] Vulnerable
**Notes**: **\*\***\_\_\_**\*\***

### 8.6 Exploit Gating

Find "if flag then X" constraint. Leave flag unconstrained. Does X still hold?

**Result**: [ ] Sound / [ ] Vulnerable
**Notes**: **\*\***\_\_\_**\*\***

---

## 9) Review Output

### Findings (Ranked by Severity)

| Severity | Finding | Location | Description |
| -------- | ------- | -------- | ----------- |
| Critical |         |          |             |
| High     |         |          |             |
| Medium   |         |          |             |
| Low      |         |          |             |

### Proposed Fixes

| Finding | Fix | Complexity |
| ------- | --- | ---------- |
|         |     |            |

### Summary

- Total constraints reviewed: \_\_\_
- Columns verified constrained: **_/_**
- Degree budget used: **_/_**
- Global arguments verified: **_/_**
- Adversarial tests passed: \_\_\_/6
