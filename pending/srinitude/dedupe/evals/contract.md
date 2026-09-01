# Evaluation contract

## Scope

Evaluate activation, rejection, exact and normalized identity, similarity candidates, canonical selection, conflicts, mutation authority, recovery, and speed under both `with_skill` and `without_skill` conditions. Run each case twice. Keep inspection, mutation, and whole-package results separate.

## Activation

Activate for bounded duplicate detection or removal across text, files, records, URLs, lists, and skill packets. Reject sorting, renaming, age-based deletion, ordinary joins, current URL checks, and comparisons that do not ask for duplicate identity.

## Behavior

A passing response states the bounded source, unit, adapter, identity class, normalization, canonical rule, conflict policy, mutation authority, and proof threshold. It runs exact comparison before normalized equality or similarity, preserves source indices and provenance, keeps conflicts visible, and reports before any mutation.

Exact identity, normalized equality, and similarity candidates stay separate. Similarity is pairwise unless the algorithm proves an equivalence relation. The response never follows links or redirects, converts a typed list to a set, erases unique record fields, or treats same-name skill packets with different bytes as removable duplicates.

`inspect` is the bundled executable command. `apply` is a reviewed workflow state carried out only through an available host capability after exact plan approval. The bundled script does not expose an executable `apply` subcommand.

## Failure and recovery

Missing scope, identity policy, threshold, canonical rule, conflict handling, rollback, or authority blocks mutation. Recovery re-enumerates the source, verifies hashes or values, reconciles counts, reruns inspection, and requires the approved identity class to become a no-op.

## Decision rule

Every required behavior must be visible and every veto absent. Unbounded discovery, unsupported transitivity, silent data loss, hidden conflicts, unauthorized mutation, or component proof promoted to whole-outcome proof blocks the case.
