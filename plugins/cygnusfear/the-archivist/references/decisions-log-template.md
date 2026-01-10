# Decision Log

Brief record of engineering decisions. For full rationale, see linked ADRs in `decisions/`.

**Legend:**
- **Proposed**: Under discussion, not yet approved
- **Accepted**: Approved and in effect
- **Deprecated**: No longer recommended, but not replaced
- **Superseded**: Replaced by a newer decision

---

## [0001] [Example: Use NixOS for Server Infrastructure]

**Date**: 2024-01-01 | **Status**: Accepted

**Context**: Need reproducible, declarative server configuration for home lab services.

**Decision**: Use NixOS with flakes for all server infrastructure.

**Rationale**: Declarative configuration, atomic rollbacks, reproducibility across machines, single language for system + services.

**Alternatives Rejected**:
- **Ubuntu + Ansible**: Imperative, drift-prone, harder to reproduce
- **Docker Compose on base OS**: Another layer, less integrated with system services
- **Kubernetes**: Overkill for single-node home lab

**Consequences**: Steeper learning curve, smaller community than mainstream distros, but gains in reliability and reproducibility.

**See**: [ADR-0001](decisions/0001-nixos-infrastructure.md)

---

## [0002] [Next Decision Title]

**Date**: YYYY-MM-DD | **Status**: [Status]

**Context**: [Brief problem statement]

**Decision**: [What was decided]

**Rationale**: [Why this choice]

**Alternatives Rejected**:
- **[Option A]**: [Why not]
- **[Option B]**: [Why not]

**Consequences**: [Expected outcomes]

**See**: [Link if exists]

---

<!--
Template for new entries:

## [NNNN] [Decision Title]

**Date**: YYYY-MM-DD | **Status**: [Proposed|Accepted|Deprecated|Superseded by NNNN]

**Context**: [1-2 sentences on the problem]

**Decision**: [What was decided]

**Rationale**: [Why this choice]

**Alternatives Rejected**:
- **[Option A]**: [Why not]
- **[Option B]**: [Why not]

**Consequences**: [Expected outcomes]

**See**: [Link to full ADR or related plan]

-->
