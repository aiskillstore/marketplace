---
id: "optimistic-ui"
title: "Optimistic UI and reconciliation"
category: "frontend"
summary: "Show immediate low-risk changes while reconciling server truth and out-of-order responses."
aliases: ["optimistic ui","rollback mutation","pending state","client reconciliation","stale response","buton sonucunu hemen ekrana yansıtma","başarısız ekleme ekrandan geri alınsın","eski tıklama yeni durumu geri aldı"]
decisions: [{"when":"The action is reversible and succeeds most of the time","use":"Use a scoped optimistic patch with a mutation version, pending state and reconciliation.","tradeoff":"Failure and later mutations need explicit recovery semantics."},{"when":"The action is irreversible or failure is costly","use":"Show pending status until the server confirms the effect.","tradeoff":"Feedback feels slower but the displayed outcome remains trustworthy."}]
checks: ["Resolve repeated mutations in reverse order and assert the last intent wins when accepted.","Force a failed mutation and verify accessible recovery without corrupting newer state."]
sources: [{"title":"React useOptimistic API","url":"https://react.dev/reference/react/useOptimistic"},{"title":"TanStack Query optimistic updates","url":"https://tanstack.com/query/latest/docs/framework/react/guides/optimistic-updates"}]
---

<!-- Generated record title. -->
# Optimistic UI and reconciliation

## Scenario

A user toggles a bookmark quickly on and off while a slow request is still pending.

## Failure modes

Restoring a snapshot from the first failed request can overwrite a newer action. Optimistically confirming irreversible or uncertain operations can mislead users.

## Explain it simply

Show the likely update right away for safe actions, then reconcile it with the confirmed result in the right order.

## Implementation guidance

Attach a mutation identity or revision to each optimistic action and merge acknowledgements against the latest requested state. If the first bookmark action fails after a later toggle succeeds, remove only its projection and leave the later action intact. Keep irreversible or externally pending operations visible as pending until confirmed. Test arrival orders of both successes and errors, plus authoritative refetch after disconnect.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The action is reversible and succeeds most of the time** Use a scoped optimistic patch with a mutation version, pending state and reconciliation. Failure and later mutations need explicit recovery semantics.
- **The action is irreversible or failure is costly** Show pending status until the server confirms the effect. Feedback feels slower but the displayed outcome remains trustworthy.

## Verification

- Resolve repeated mutations in reverse order and assert the last intent wins when accepted.
- Force a failed mutation and verify accessible recovery without corrupting newer state.

## Sources

- [React useOptimistic API](https://react.dev/reference/react/useOptimistic)
- [TanStack Query optimistic updates](https://tanstack.com/query/latest/docs/framework/react/guides/optimistic-updates)

<!-- End generated record details. -->
