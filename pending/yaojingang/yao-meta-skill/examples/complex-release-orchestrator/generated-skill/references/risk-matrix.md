# Risk Matrix

## Severity Guide

- `low`: internal-only changes, no migrations, rollback is trivial
- `medium`: user-facing changes with limited blast radius or known manual recovery
- `high`: schema changes, cross-service dependencies, or rollback with coordination cost
- `critical`: irreversible data impact, unclear rollback, or no monitoring confidence

## Decision Rules

- `GO`: no unresolved high/critical risks and rollback path is clear
- `GO WITH CONDITIONS`: risks remain but owners, mitigations, and gates are explicit
- `NO-GO`: missing migration details, missing rollback criteria, or critical unknowns
