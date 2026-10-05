# Source-monitor nested-name recurrence — 2026-10-05

## Incident and prior repair

[PR #3659](https://github.com/aiskillstore/marketplace/pull/3659), old head `86b2fa73c3e1e00fe665d3fd195de08d054b65f3`, failed `validate` because `skills/consiliency/orchestration/native-invoke/SKILL.md` changed from `orchestration-native-invoke` to `orchestration:native-invoke`.

- [Original CI failure](https://github.com/aiskillstore/marketplace/actions/runs/37204429094/job/111442646474)
- [Prior canonical name in main](https://github.com/aiskillstore/marketplace/blob/f6c9924178/skills/consiliency/orchestration/native-invoke/SKILL.md)

The earlier artifact repair was present in main. Source refresh copied the upstream colon name back over that correction. The validator correctly rejected it; neither relaxing name validation nor rerunning the same failing SHA repairs the cause.

## Immediate repair: verified

[Repair commit](https://github.com/aiskillstore/marketplace/commit/e345fef15a811275869bc43cf317d8e2c55a7241): restore the nested canonical name and rebind the parent `skill-report.json` tree hash. Only those two lines change. The parent SKILL.md content hash and source lineage remain unchanged.

- New head: `e345fef15a811275869bc43cf317d8e2c55a7241`.
- [Validate Marketplace success](https://github.com/aiskillstore/marketplace/actions/runs/37303773422).
- [Publication admission success](https://github.com/aiskillstore/marketplace/actions/runs/37303773418).
- All three required checks are SUCCESS; PR state was OPEN / CLEAN at readback.
- Merge and downstream provider sync are not claimed by this incident repair record.

## Recurrence prevention: implemented, pending independent review / merge

Monitor path: upstream refresh → changed published roots → report rebinding with `--preserve-nested-names` → restage exact packaged bytes → update-safety verification → PR.

The opt-in flag in `rebind-skill-report-hashes.mjs` preserves only **existing nested SKILL.md** names when:

1. The same path is an ordinary tracked file at baseline HEAD.
2. Its baseline name is canonical lowercase/hyphen form.
3. Incoming name is a simple colon-delimited lowercase name whose colon-to-hyphen conversion equals the exact baseline name.
4. The current path is an ordinary file, not a symlink or symlink traversal.

Only the exact name scalar is replaced; other frontmatter and body bytes are retained. Hashes are calculated afterwards and both corrected nested files and the report are staged. This does not add dependencies or runtime checkout files.

Other callers retain default hash-only behavior. Root skill identities, verified aliases, new nested skills, genuinely changed names, arbitrary malformed names, approval requirements and validation rules are not broadened. Unsupported cases still require ordinary validation/manual repair.

## Reproducible verification

```sh
CI=true node --test \
  scripts/tests/source-monitor-runtime-workflow.test.mjs \
  scripts/tests/rebind-skill-report-hashes.test.mjs \
  scripts/tests/validate-marketplace-autofix.test.mjs \
  scripts/tests/source-monitor-update-safety.test.mjs
node --check scripts/rebind-skill-report-hashes.mjs
git diff --check
```

Local result: 37/37 tests passed, none skipped. The workflow integration regression first failed with the original colon name, then passed after the implementation. It executes the actual workflow shell block and verifies working bytes, Git index bytes, rebound tree hash and unchanged source lineage. Negative cases cover real renames, mismatched colon names, non-ASCII/uppercase/malformed names, new/invalid baselines and symlinks. A frontmatter description containing the same name text proves replacement is confined to the name field.

Immediate-repair worktree: existing `validate-marketplace-autofix.test.mjs` first failed on the original head, then 13/13 validation/rebinding tests passed after repair.

## Recovery procedure

1. Read the current PR head and exact failing file; check the main/baseline version instead of assuming the old fix remains in the incoming tree.
2. Restore only a proven canonical name. Do not rename the enclosing canonical skill root or weaken validation.
3. Rebind hashes at the enclosing report root, not the nested documentation directory. Preserve source lineage and other report fields.
4. Run affected validation tests, push normally only if the original PR head still matches, then read back the new head and its three required CI checks. Do not reuse old checks.
5. Treat prevention-code acceptance/merge and source-monitor rollout separately from the immediate content repair. Normal merge/sync rules remain in force; do not replay unknown provider effects.

Rollback of prevention is a code revert of the optional flag/function and corresponding restaging change; it does not require reverting the valid immediate artifact repair. This change does not dispatch a scan or write provider state.
