# Business Logic & Race Conditions

Merged from yaklang/hack-skills `business-logic-vulnerabilities` (SKILL/CHECKLIST/METHODOLOGY/SCENARIOS), ekomsSavior/bizlogic, and PayloadsAllTheThings.

## When scanners miss → manual logic testing

Traditional scanners find injection; logic flaws require modeling **the application's rules** (money, inventory, workflow, identity) and breaking them.

## Nine heuristic checks (from bizlogic)

1. **Unverified ownership claims/transfers** — account/email/domain change without proving control.
2. **Auth bypass via alternate channels** — same action reachable through less-protected path (API vs UI, email link vs session).
3. **Authorization via user-controlled keys** — role/tenant/permission passed in body/query instead of server-side session.
4. **Weak password recovery** — predictable tokens, no expiry, no rate limit, user enumeration via error timing/messages.
5. **Incorrect ownership assignment** — created resource assigned to attacker-controllable user_id/owner field.
6. **Resource allocation without limits** — unlimited coupons, seats, storage, API credits.
7. **Premature resource release** — state transitions that free/commit before validation completes.
8. **Single unique action enforcement flaws** — "one vote/coupon/claim" enforced only client-side or by non-atomic check.
9. **Client-side workflow enforcement** — step skipping: hide Step 3 in UI but POST /complete still works.

## Payment manipulation matrix (hack-skills)

| Attack | Test |
|---|---|
| Negative quantity/price | `quantity=-1`, `price=-100` → credit balance? |
| Discount stacking | apply two coupons; percent + fixed together |
| Currency confusion | pay in weak currency, refund in strong |
| Precision/rounding | 0.001×1000; `99.999` → rounds down |
| Server trusts client totals | change `total`/`amount` in POST body |
| Free shipping / tax bypass | flip `shipping=0`, `tax_exempt=true` |
| Refund/return abuse | refund item without returning; double refund |
| Plan downgrade timing | use annual plan features after refund window |
| Trial extension | replay start-trial endpoint |
| Promo reapply | remove/re-add promo to reset limits |

## State machine bypass methodology

1. Map the legit state machine (e.g. `draft → review → approved → paid → shipped → delivered`).
2. Replay out-of-order transitions: call `/ship` while still `draft`.
3. Replay reverse transitions: `/cancel` after `delivered`, `/unpay`.
4. Skip validation states: direct `/complete` without intermediate approvals.
5. Concurrent transitions: fire `approve` and `cancel` at once (race) → check final invariant.
6. Force terminal states via IDOR on state field or hidden form field.

## Race condition playbook

- **Goal**: exceed once-per-X limits, double-spend, stock overrun, vote/coupon reuse.
- **Setup**: two identical authenticated sessions (or one), capture exact request.
- **Techniques**:
  - HTTP/1.1 last-byte sync (Turbo Intruder): send all but final byte, flush together.
  - HTTP/2 single-packet attack (if backend supports multiplexing).
  - Interleaved keep-alive connections with synchronized barriers.
- **Verify**: check server-side invariant after burst (balance, coupon count, stock, vote tally) — not just HTTP 200s.
- **Classic bugs**: coupon race, gift-card drain, "first 100 users" oversell, idempotency-key reuse, TOCTOU on file paths.

## Coupon / promo testing checklist

- [ ] Single-use enforced server-side after redemption?
- [ ] Concurrent redemption of same code (race)?
- [ ] Stackable with other coupons? Order of application changes total?
- [ ] Expiry enforced server-side (client date only)?
- [ ] Scope enforcement: coupon for Product A applied to Product B?
- [ ] Negative amount / over-discount → store credit?
- [ ] Re-apply after failed payment resets usage count?

## Ownership & transfer

- Change registered email/phone without verifying new address (accept-link or skip).
- Transfer workspace/organization ownership to attacker ID.
- Invite flow: accept invite for email you don't own (token not bound to recipient).

## Evidence for logic reports

1. Business rule as intended (quote docs/normal behavior).
2. Manipulated request/response showing rule broken.
3. Quantified impact (money moved, limit exceeded, other users affected).
4. Minimal PoC steps + screenshots/tokens redacted.
5. Remediation: server-side enforcement, atomic checks (DB transactions with row locks), idempotency keys, re-auth for sensitive transitions.

## Tool assist

- **bizlogic** (`python bizlogic_scanner.py`): conservative same-origin crawl → 9 heuristic checks → optional safe exploitation (IDOR seq, token manipulation, recovery tests) with rate limits; exports text/JSON/HTML/Nuclei templates.
- **AutorizePro**: authorization enforcement replay (low-priv session vs high-priv requests) + optional AI triage to cut false positives.
- **BurpAPISecuritySuite** Auth Replay / Passive Discovery: multi-role replay, counterfactual drift, token lineage, abuse chains.
