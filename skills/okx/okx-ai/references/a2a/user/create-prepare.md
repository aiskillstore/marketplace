# One-Time Task Preparation

## Module Description

Use this leaf only after the User explicitly selects an A2A Service. Keep the
selected numeric `sid` internal and run:

```bash
onchainos agent task-create-prepare --sid <selected-sid>
```

Run this read exactly once for the selected `sid` in one turn. Once the
command has started, wait for that invocation and never start a duplicate
because output is delayed. Reuse its returned result for the rest of the turn.

The CLI already checks login, User identity, authoritative Service state,
subscription conflicts, effective price or trial, and payable balance. Do not
repeat those reads in the Skill. A successful response contains
`phase/decision/reason/nextAction/payload` under `data`; select exactly one row
from the Result matrix below without re-entering a router.

## Flow

### Result matrix

| Phase / reason | Required behavior |
|---|---|
| `login_validation / login_required` | Run only the returned `login` action; then rerun this prepare with the same `sid`. |
| `identity_validation / user_identity_required` | Register a User Agent; then rerun this prepare with the same `sid`. |
| `service_validation / unsupported_service_type` | Explain the returned reason and stop. |
| `subscription_validation / duplicate_subscription` | Read `duplicate-subscription.md` and use only the returned restore/stop actions. |
| `funding_required / insufficient_balance` | Enter the [`okx-agentic-wallet` funding leaf](../../../../okx-agentic-wallet/references/funding.md) using the returned bundle. Do not create; after funding, rerun prepare. |
| `creation / all_checks_passed` | Bind the returned Service payload and enter `create.md`. |

`decision=ready` means preparation succeeded; it is not authorization to create
or pay. Invalid Service data and dependency failures are command errors, not
new business cases. Never derive an action from `phase`, prose, or a previous
prepare result.

A2MCP services are rejected here. Prepare them through the explicit MCP branch
in [`../../a2mcp/handoff.md`](../../a2mcp/handoff.md).

Use `payload.serviceId` as the later creation UUID. `payload.sid` remains only
the search/preparation selector. A non-blank `serviceGuide` carries its matching
CLI-derived `serviceGuideHash`; retain both exactly.
