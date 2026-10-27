# Worked example: "Why did checkout break?"

This example uses synthetic data. The project, IDs, and values are not
real. It shows the order of the steps and what to record at each one.

The person asks: "Checkout started failing about an hour ago. Why?"

Scope from the person: project `00000000-0000-4000-8000-000000000001`,
environment `production`, service `checkout-api`. Reads only, no code
changes until the cause is clear.

## Access

```bash
logbrew status --json
```

Observed: account access is authenticated. Use the CLI.

## 1. Find the failing issue

```bash
logbrew read issues --project "$PROJECT_ID" --environment production --status unresolved --since 2h --json
```

Observed: 3 unresolved issues. 1 matches the symptom:
`TypeError: Cannot read properties of undefined (reading 'amount')` in
`checkout-api`, release `checkout-api@2.14.0`, 412 events. The other 2 are
older warnings in a different service.

## 2. Read the stack and the first-seen release

```bash
logbrew investigate issue "$ISSUE_ID" --occurrence recommended --json
```

Observed:

- First frame in our code: `src/pricing/applyDiscount.ts:48`, in
  `applyDiscount`.
- `subject.first_seen_at` is 14:02 UTC. The first occurrence has release
  `checkout-api@2.14.0`.
- `occurrence_selection.reason` says the occurrence has a linked trace.
- `cause.status` is `unknown`. `fix.status` is `unknown`.

Inferred: the issue started with release `checkout-api@2.14.0`, so it is
probably a regression in that release. Unknown: which input triggers it.

`git log` shows that `checkout-api@2.14.0` changed `applyDiscount.ts`: it
now reads `cart.discount.amount` instead of `cart.discountAmount`.

## 3. Pull the logs and the trace around the first event

`correlations.trace.status` is `available`, with trace
`4bf92f3577b34da6a3ce929d0e0e4736`.

```bash
logbrew read trace "$TRACE_ID" --project "$PROJECT_ID" --json
logbrew read logs --trace "$TRACE_ID" --project "$PROJECT_ID" --since 24h --json
```

Observed:

- The span `POST /api/checkout` has status error after 38 ms.
- The log before the failure: `cart loaded` with `discountCode: null`.
- No log mentions a discount object.

Inferred: carts without a discount code have no `discount` object, and the
new code reads `amount` from `undefined`.

## 4. Check who is affected

Observed from the investigation: 412 events in 58 minutes, rising.
`impact.user_impact.status` is `available`, with an approximate count of
affected users. All events are in `production` and `checkout-api@2.14.0`.

Report: checkout fails for carts without a discount code since the
14:02 UTC deploy. Do not list user IDs.

## 5. State what is still unknown

- The trace shows 1 failing request. Other routes that call
  `applyDiscount` are not checked.
- Exception messages from users' input are not part of this issue.

None of these block a fix: the failing frame is in our code and the input
shape is clear.

## 6. Write the fix

Test first: a cart with `discountCode: null` and no `discount` object must
return the full price. It fails with the same `TypeError`. Then the fix:
read `cart.discount?.amount ?? 0`. The test passes.

## 7. Check that new events stop

Before the deploy, record the occurrence ID from step 2 as
`OCCURRENCE_ID`. The release pipeline records deployment
`ci-run-8812` for `checkout-api@2.14.1`. After 20 minutes of traffic:

```bash
logbrew investigate issue "$ISSUE_ID" verify --baseline-occurrence "$OCCURRENCE_ID" --candidate-deployment ci-run-8812 --json
```

Observed: `status` is `no_recurrence_observed`.

## Report to the person

```text
Issue: TypeError in applyDiscount, project checkout, production, checkout-api, release checkout-api@2.14.0
Symptom: checkout fails for carts without a discount code
Observed: first seen 14:02 UTC with checkout-api@2.14.0; frame src/pricing/applyDiscount.ts:48;
  trace 4bf92f3577b34da6a3ce929d0e0e4736 shows cart loaded with discountCode null, then the error
Affected: 412 events in 58 minutes, rising; production only
Inferred cause: 2.14.0 reads cart.discount.amount, and carts without a code have no discount object
  (unknown: other callers of applyDiscount)
Proposed fix: default the discount amount to 0, with a regression test
Verify: no_recurrence_observed for deployment ci-run-8812 after 20 minutes; evidence, not proof
Commands run: status, read issues, investigate issue, read trace, read logs, investigate issue verify
```

The person decides whether to resolve the issue.
