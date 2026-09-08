# Report and mutation contract

Owner: `dedupe`. Load before producing a report or mutation plan. Backlink: `SKILL.md` PD-005.

## Inspector request

A request JSON object contains:

| Field                  | Required            | Meaning                                             |
| ---------------------- | ------------------- | --------------------------------------------------- |
| `adapter`              | yes                 | `text`, `file`, `record`, `url`, `list`, or `skill` |
| `mode`                 | yes                 | `exact`, `normalized`, or supported `similarity`    |
| `items`                | yes                 | bounded array of source items                       |
| `normalization`        | for normalized text | Unicode, case, and whitespace policy                |
| `similarity_threshold` | for similarity      | explicit score threshold from 0 to 1                |
| `key_fields`           | normalized records  | ordered identity fields                             |
| `url_policy`           | normalized URLs     | explicit component changes                          |
| `encoding`             | normalized files    | text encoding                                       |
| `follow_symlinks`      | optional files      | inspection authority, default false                 |

Run:

```text
python3 scripts/dedupe.py inspect --request /absolute/path/request.json
```

Exit 0 returns JSON to stdout. Exit 1 reports an invalid request or unreadable source to stderr. Exit 2 is command-line misuse.

## Report fields

| Field                   | Meaning                                                |
| ----------------------- | ------------------------------------------------------ |
| `mutated`               | always false for the inspector                         |
| `source_count`          | all requested items                                    |
| `canonical_count`       | retained representatives among resolved items          |
| `duplicate_count`       | non-canonical strict equality members                  |
| `unresolved_count`      | items excluded from comparison                         |
| `canonical_indices`     | stable source indices kept by first-seen report policy |
| `groups`                | strict equality groups and hashed keys                 |
| `similarity_candidates` | pairwise candidates that do not reduce counts          |
| `identity_conflicts`    | same identity label with different evidence            |
| `unresolved`            | index and reason for each uninspected item             |
| `provenance`            | adapter facts, paths, hashes, versions, and link data  |
| policy fields           | disclosed normalization and URL rules                  |

Comparison keys are hashed in output. Keep raw data in its source unless the user explicitly requests it in the report.

## Mutation plan

A plan must bind:

- report digest and creation clock anchor
- source identity and scope
- canonical selector and tie-breakers
- each source index and canonical target
- exact action per item
- conflict decision per field or passage
- preserved unique information
- destination and writer
- reconstruction or rollback method
- verification commands and expected evidence

Hash the final plan bytes. Any plan edit, source drift, or policy change invalidates prior authority.

## Approval shape

Require explicit authority that identifies the plan digest and chosen action. Generic requests such as "clean this up" or "remove duplicates" authorize inspection, not deletion.

Authority does not extend to:

- new items discovered after inspection
- parent or sibling directories
- redirect targets
- linked skills or records
- conflicts absent from the report
- recursive cleanup
- a different destination

## Apply sequence

1. Recheck source evidence against the report.
2. Recompute and compare the plan digest.
3. Confirm one writer and current authority.
4. Preserve rollback or reconstruction evidence.
5. Apply actions in stable order.
6. Record applied, skipped, and failed actions separately.
7. Stop on drift, conflict, or proof failure unless the plan names safe partial behavior.
8. Re-enumerate source and destination.
9. Rerun inspection with the same policy.
10. Run the final logic audit before reporting completion.

## Verification report

Report component status separately:

- enumeration
- identity extraction
- grouping
- canonical selection
- conflict resolution
- authority
- mutation
- reconstruction evidence
- post-apply inspection
- whole outcome

Never turn a focused adapter PASS into a package or whole-task PASS.

## Package verification

From the skill root, run:

```text
mise run ci
```

If Mise is absent, run in task order:

```text
python3 -m unittest discover -s scripts/tests -p 'test_*.py'
python3 scripts/validate_skill.py .
python3 scripts/lint_writing.py .
python3 scripts/check_code_rules.py .
python3 scripts/check_placeholders.py .
python3 scripts/check_evals.py .
```

State which route ran and every exit code. A direct-command pass does not prove `mise run ci` ran.

## Failure responses

A blocked report names:

- failed adapter or item index
- missing policy, authority, or source fact
- affected evidence
- safe partial results
- exact next fact or action needed

Do not invent a result, drop the item, or hide it inside a duplicate count.
