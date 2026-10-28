# ASP Refund-or-Evaluation decision

## Module Description

Use this Reference for `job_rejected`, `sub_user_reject`, a pending refund request,
or an explicit request to evaluate one rejected task.

A zero-price one-time task whose fresh status is Failed(9) is terminal and must
not enter this Reference. Notify the ASP owner of the Failed result and execute the
returned task-scoped cleanup action; do not offer refund or platform evaluation.


## Flow
### Refund request detail and decision

For a System entry, consume the fresh progression result already produced by
the A2A router. For a selected pending request, use the fresh `refund-detail`
result. Render [Buyer Refund Request](#buyer-refund-request).

### Resolve the decision

Bind an event-created card to its Job ID, decision ID, deadline, and choices in
`pending-decisions-v2`. Bind a card opened from a selected pending request to
its Job ID and fresh `refund-detail.nextAction` values. Render the complete
Template 6.4 view before waiting for a decision.

Apply this response matrix to either binding:

- `Approve refund`: resolve the matching `agree_refund` or
  `sub_agree_refund` action and run its returned command in the current
  conversation.
- `Request evaluation` with a non-blank reason: preserve the reason verbatim,
  resolve the matching Evaluation action, and run it in the current
  conversation.
- `Request evaluation` with a missing reason: retain the Evaluation intent and
  binding, render [Seller Refund Rejection](#seller-refund-rejection), and ask
  for the evaluation reason. Treat the next non-blank reply as the verbatim
  reason and run the matching action.
- A reason received while waiting for a decision: preserve it as draft context,
  re-render the complete Template 6.4 view, and wait for an action selection.

The returned action is the final authorization. Present one concise localized
result after the command completes.


## Output Rules
### Output Templates

The template below is an English source. Reply in the language of the current
conversation while preserving the full Job ID, amounts, token symbols,
timestamps, and user-authored reasons exactly.

#### Buyer Refund Request

```markdown
### Buyer Refund Request

- Service Name: {serviceName}
- Job ID: {jobId}
- Task Type: {taskType}
- Current Period: {currentPeriod}
- Requested Refund: {requestedRefund}
- Buyer’s Reason: {buyerReason}
- Response Deadline: {responseDeadline}
- Refund Status: {localizedStatusLabel}
- Status Description: {localizedStatusDescription}

Please respond by the deadline. Otherwise, a full refund will be issued automatically.

To refund the buyer, reply "Approve refund". To request platform evaluation, reply "Request evaluation" and include your evaluation reason.
```

#### Seller Refund Rejection

Render this decision card only after the ASP has chosen to reject the refund
but has not yet supplied an evaluation reason. It is not a new authorization;
the already-selected rejection and its task binding remain active.

```markdown
### Seller Refund Rejection

- Service Name: {serviceName}
- Job ID: {jobId}
- Task Type: {taskType}
- Current Period: {currentPeriod}
- Requested Refund: {requestedRefund}
- Buyer’s Reason: {buyerReason}
- Response Deadline: {responseDeadline}
- Seller Decision: Reject refund

Rejecting the refund will start a platform evaluation. Please provide your reason for requesting review; it will be preserved verbatim and submitted as the evaluation reason.
```

Display rules:

1. Show `Current Period` only for a subscription.
2. Preserve the full Job ID and the buyer-authored reason.
3. Use CLI-provided display values directly.
4. An explicit request to evaluate a selected task uses this same decision view.
5. Localize the title, field labels, explanatory copy, and action wording to the current conversation language.
6. Treat this Template 6.4 view as the ASP confirmation. Execute the returned action after `Approve refund`, or after `Request evaluation` with a reason.
7. Translate `Awaiting ASP decision` and its description into the user's
   language.
8. Translate the rejection-card title, decision, and reason prompt from their
   English source wording into the user's language; preserve the ASP-authored
   evaluation reason verbatim.
