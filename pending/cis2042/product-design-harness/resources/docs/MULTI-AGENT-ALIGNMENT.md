# Autonomous Multi-Agent Alignment & Boundary Governance Protocol

## 1. Executive Principle: An Alignment Harness for Machine Swarms

In modern software development driven by autonomous multi-agent teams (e.g. **1 Integrator/Admin + N Workers + 1 QC Auditor**), Product Design Harness serves as the **machine-readable boundary constitution**, rather than a bureaucratic form for human developers.

- **Human's Role**: Sole Judge and Strategic Founder (sets high-level intent, evaluates trade-offs, grants external permissions).
- **Integrator / Admin**: Deconstructs work packages, enforces path locks, and dispatches tasks bounded by the Harness contract.
- **Workers (Autonomous Coding Agents)**: Execute with maximum speed *strictly within* the `may_do` scope in isolated worktrees; zero scope expansion.
- **QC Auditor (Independent Review Agent)**: Read-only auditor validating code diffs against the Harness `must_not_do` boundaries; 1-second rejection on scope violation.

---

## 2. Zero-Stall Guarantee (Non-Blocking Architecture)

To prevent the harness from freezing developer flow or multi-agent pipelines after installation:

1. **Bypass by Default (90% Fast Path)**:
   - Routine maintenance (styling, text, isolated bug fixes, internal refactors preserving public contracts) completely bypasses review gates.
   - Zero latency, zero review JSON generation, zero blocking.
2. **Sub-Second System One Classification via Decision Gating**:
   - When intent classification or boundary checking is required, it is handled via lightweight decision models or deterministic rules in `scripts/jev_gate.py`.
   - Evaluates risk, evidence tier, and 3-lane verdict in **under 300ms**, returning strongly-typed answers without generative prose.
3. **Worst-Verdict Hard Brakes**:
   - The harness only interrupts execution when one of four critical tripwires is triggered:
     - **t0 Evidence Violation**: Large feature proposed with zero traceable evidence (forced `stop_reframe`).
     - **Destructive State Mutation**: Unplanned database schema migrations, drops, or table corruption.
     - **Irreversible Boundary Breach**: Modifying security rules, auth protocols, or external network access without authorization.
     - **Inter-Flow Contradiction**: Conflict between user value and business viability.

---

## 3. Lossless Context Preservation

In long-running autonomous sessions (30~100+ turns), generative chat summaries often dilute or erase negative constraints (e.g. generalizing negative database constraints into broad feature summaries).

This harness integrates with lossless context compaction:
- All Harness Context Packs and boundary files carry the `boundary-lock` invariant.
- When context compaction runs, expired tool execution logs and test outputs are pruned, while the **exact verbatim text** of `may_do`, `must_not_do`, and `stop_conditions` is retained at 100% fidelity at the top of the context window.

---

## 4. Role Mapping & Boundary Enforcement

| Role | Responsibility | Input Contract | Output Requirement |
|---|---|---|---|
| **Integrator / Admin** | Package slicing & lock enforcement | Product intent | Task Context Pack with digest locks |
| **Worker (Builder)** | Atomic implementation & local tests | `may_do` & `must_not_do` | Clean patch + unit test evidence |
| **QC Auditor** | Defect-first boundary audit | Git diff + Context Pack | PASS or Scope Drift Rejection |
| **System One Gate** | Millisecond triage & gating | State + Typed Questions | `choice` / `noul` / `score` typed decision |

---

## 5. Pilot Validations

This protocol has been pilot-tested against three production codebases:

1. **Twin3 SDK**:
   - *Challenge*: Worker attempting unauthorized external telemetry webhook.
   - *Harness Action*: Gate tripped on Evidence Flow (t0 unconsented telemetry); locked negative constraints on external HTTP requests and Secret Manager mutation.
   - *Result*: Zero-stall on standard tools, immediate halt on external network breach.
2. **xAgent Identity**:
   - *Challenge*: Worker extending authentication routes inside a 732KB monolithic server file and risking enterprise store schema corruption.
   - *Harness Action*: Locked `may_do` to specific route handlers, strictly forbidden from modifying the enterprise store or core contract schemas.
   - *Result*: Zero collision, protected monolithic state.
3. **xHuman Identity**:
   - *Challenge*: Worker attempting cloud sync for user media in violation of local-preview-only contract.
   - *Harness Action*: Irreversible privacy boundary tripped; forced `stop_reframe` back to frontend blob URL preview.
   - *Result*: Zero cloud leakage, customer privacy preserved.
