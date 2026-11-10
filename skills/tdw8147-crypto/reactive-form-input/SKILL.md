---
name: reactive-form-input
description: Use when a form displays a value but validation or dependent state disagrees; report whether the input actually took effect without submitting.
---
# Reactive Form Input

Stop reporting “the field is filled” as success when the application has not accepted the value.

## When to use

- A controlled field shows the expected text while its dependent state remains unchanged.
- A page has a visible contact field, a hidden duplicate, and a similarly named search box.
- A valid-looking value leaves a spinner, validation error, or disabled control.
- A client-side navigation replaced the field while a test was in progress.
- The user wants an evidence record from page notes even though no browser is available.

## When NOT to use

- The user wants to send a finished application or complete a payment.
- A submission already timed out and the question is whether it reached the destination.
- The input is in a local text editor, not a form with app-level state.
- The task is to implement validation logic rather than observe a field.
- The user only needs to know what format to type, not whether the application accepted it.

## Core rules

1. **Identify the visible, editable control within its own form.** Hidden duplicates and same-named search fields can produce convincing but irrelevant observations.
2. **Prefer normal fill or keyboard input; say how replacement clears the old value.** Ordinary interaction exercises the app's expected path while preserving the requested format and units.
3. **Do not claim success from DOM property changes.** A rendered string is not proof that the application accepted it; honor control limits and normal validation.
4. **Record display and acceptance separately.** A correct display with unsynced validation is not an effective input.
5. **Wait for business state within a bound.** Page load does not settle asynchronous validation; don't report final failure while it is running.
6. **Blur only in the normal flow.** A final-submit click or an unproven event sequence changes the test instead of observing the input.
7. **Re-locate after navigation and retain rejection messages.** Stale handles and silent value substitutions break the link to the intended interaction.
8. **Deliver even without page access.** An unverified record is useful if it distinguishes supplied evidence, missing observations, and suggested actions.
9. **Do not submit to get more evidence.** If a prior submit is already uncertain, query its original request only; never replay.

## Workflow

### 1. Locate the target

- Record the page version, parent form, field label or accessible name, and expected format or unit.
- Exclude hidden copies and unrelated same-name controls.
- Check visibility and editability; record why a field is covered or disabled if known.
- After navigation, establish the new page context and locate the control again.

### 2. Record the action and displayed result

- In live, authorized work, use ordinary fill or keyboard input.
- Before replacing an existing value, state the clear behavior; do not append accidentally.
- Do not silently convert a rejected value to a different business value.
- Write the interaction method, observation moment, and display-match result. Mask sensitive values.
- In document-only work, report supplied actions as supplied and mark future actions as proposed.

### 3. Look for a field-specific app signal

- Note the validation text, linked button, or derived value with an evidence location.
- Tie a change to the intended field and the current page, not a previous render.
- If a button depends on several fields, don't use its disabled state alone as proof this field failed.
- If normal interaction requires leaving the field, blur by that ordinary path, not by submission.

### 4. Classify what is known

- `effective`: display matches and a relevant application signal confirms acceptance.
- `not effective`: a settled rejection or observed state mismatch shows the input did not take effect.
- `validating`: an identifiable asynchronous check is still running; record the pending signal.
- `unverified`: the evidence or access does not establish the app state; name the missing layer.
- State what supports the classification and what is still unknown.

### 5. Give one next step or stop

- Name one normal interaction or observation, its bound, and its completion signal.
- Wait for the specified application state, not just for the page to load.
- Stop once effective. If submission is the only way to see more, state that limit and stop.
- If draft/submit tools are provided, read the needed material, write the full record, and submit it in order in the same round.

## Output template

```markdown
# Input effectiveness — [field]
Page / form: [version or view] / [parent form]
Target: [label or accessible name] | [visible / editable / blocker]
Expected format / unit: [format or not provided]

## Action and display
- [method and clear behavior] | [observation moment] | [display match, masked]
- Source: [live observation / supplied note / proposed only]

## Application signal
- [validation text / linked control / derived field] | [evidence locator]
- Relevance: [why it applies to this field and page]

## Conclusion
- [effective / not effective / validating / unverified] because [evidence]
- Gap: [missing signal or none]
- Next: [one normal step, bound, completion signal / stop]
- Final submit: not performed
```

## Worked examples

### Example 1 — Contact email is visible but not in app state

**Input.** On account page r8, Contact email belongs to Profile, not the header search. A hidden field has the same internal name.
An earlier script set the visible DOM value. The supplied r8 inspection records an empty model for the intended field and no validation running.
Save is disabled, but it also depends on other fields. The test must not save.

**Bad**

> The address is visible. Force-enable Save and click it to verify.

**Good**

> Target: Profile → Contact email, r8; visible control only, email format. Exclude the hidden copy and header search.
> Display: matches after DOM assignment, value masked. Source: supplied r8 inspection.
> App signal: the same inspection shows an empty field model with no pending validation. Save being disabled is not field-specific.
> Conclusion: not effective in that observation. Proposed next: clear and replace once via ordinary keyboard entry, then observe within the available test window for a matching accepted field value or a settled validation message.
> No interaction was performed for this record. Final submit not performed.

### Example 2 — The app is still checking a workspace slug

**Input.** In the new-workspace form r12, the visible slug field already showed a previous draft. The tester selected all and typed the requested lowercase slug.
The UI shows the correct value and a “Checking availability…” indicator. The test budget allows five seconds from the observation.
The expected app signal is “Available” for the same slug; the test does not create a workspace.

**Bad**

> Continue is still disabled; use a different slug and click Create to see what happens.

**Good**

> Target: New workspace → Slug, r12; visible and editable, lowercase slug format.
> Action: select-all replacement via keyboard. At the post-entry observation the displayed slug matched.
> App signal: “Checking availability…” next to that field; the acceptance signal has not appeared.
> Conclusion: validating, not rejected. Next: observe the same field for up to five seconds, stopping on “Available,” a settled rejection, or expiry; at expiry report the last observed state.
> Keep the requested slug. Final submit not performed.

## Common mistakes / red flags

| Red flag | Better record |
|---|---|
| “Selector found one element” | Name the visible editable control, form, and page. |
| “The value looks right, so it worked” | Record the app signal independently. |
| “Disabled means this field is invalid” | Identify the actual dependency or report uncertainty. |
| “Still checking, therefore rejected” | Mark validating and observe within a bound. |
| “Use the old element after navigation” | Locate the control again in the new context. |
| “Click Submit just to test” | State the observation limit and stop without submitting. |

## Self-check

- [ ] Target identity excludes hidden copies and unrelated forms.
- [ ] Format, units, and clear behavior preserve the requested value.
- [ ] Display evidence and application evidence are separate and sensitive data is masked.
- [ ] Signals apply to the current page and target field.
- [ ] Async validation is not misreported as a final rejection.
- [ ] The record distinguishes observed, supplied, and proposed actions.
- [ ] There is one bounded next observation, or a clear stop.
- [ ] No final submit or replay was performed.

## Stop at delivery

Deliver the record, not a submitted form. Effective input is not evidence of submission.
When the next observation requires a final submit, state the limitation and stop there.
