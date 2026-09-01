# Evaluation contract

## Scope

Evaluate activation, rejection, behavior, failure handling, recovery, and speed under both `with_skill` and `without_skill` conditions. Run each case twice. Keep activation, behavior, enrollment, and whole-package results separate.

## Activation

A direct user message must activate the skill even when it has no date or time words. Tool results, system events, and assistant continuations must not activate it. The exact mid-turn out-of-band user-message marker counts as a direct user message.

## Behavior

A passing response loads `starting-point`, acquires exactly one fresh anchor after the newest direct message and before interpretation, validates every clock field, binds `as_of`, resolves consequential temporal language before tool use, preserves the user's words and temporal direction, and stores the acquired date and time in the correct visible prefix.

The NOW header appears only on the first reply for a local date or after the local date changes. The date-time prefix appears on every normal user-facing reply. Tool calls and internal notes have neither prefix.

## Failure and recovery

A missing, invalid, stale, or failed anchor produces `temporal-anchor-unavailable:` and blocks date-dependent or time-dependent work. Resume or compaction requires a reload when the skill body is unavailable and a new clock call before retained dates or times are used.

## Model disclosure

A judge may assess only the supplied prompt, response, trace, case requirements, and vetoes. It must not infer hidden clock calls, source reads, or external actions. Missing direct evidence remains unproven.

## Decision rule

Every required item must pass and every veto must remain absent. One missed clock call, stale anchor, duplicate call, prompt rewrite, wrong absolute date, missing stored prefix, or fail-open fallback makes the case `BLOCKED`.
