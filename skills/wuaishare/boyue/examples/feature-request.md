# Example: Feature Request

## Scenario A: low-risk reversible change

Request:

> Increase spacing between dashboard cards and shorten one label.

Assessment:

- easy to reverse;
- low consequence;
- no meaningful new ownership surface;
- no new product promise.

Boyue behavior:

> Use the fast path. Make the smallest safe change, verify layout and accessibility, and finish.

Do **not** create a PRFAQ, ADR, or formal Commitment review.

---

## Scenario B: “while we are here” scope expansion

Original request:

> Add an export button to the report page.

During implementation, an agent proposes:

> We could also add scheduled exports, cloud storage sync, sharing permissions, export templates, and a public Export API.

The additional ideas are useful **Options**, not automatic scope.

### Commitment Boundary

**COMMIT:** manual export in the required format.

**DEFER:** scheduled export.

Revisit trigger: repeated user evidence shows scheduled delivery is a common workflow.

**DISCARD for current scope:** cloud sync, template marketplace, public API.

### Delivery

Ship one coherent slice:

```text
User chooses Export
  ↓
System generates the supported format
  ↓
Failure is reported clearly
  ↓
Download succeeds and is observable
```

The project remains small even though AI made adjacent features easy to prototype.
