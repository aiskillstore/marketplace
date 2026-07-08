# Phase 4: Summarize & Validate

Load this file when executing Phase 4. Refer back to [`upgrade-success-criteria`](../rules/upgrade-success-criteria.md) and [`upgrade-strategy`](../rules/upgrade-strategy.md) for success criteria and strategy, and [`../rules/troubleshooting.md`](../rules/troubleshooting.md) when failures occur.

1. Create `.github/java-upgrade/{RUN_ID}/summary.md` from the Summary Template — replace placeholders and follow HTML-comment instructions to populate final results.
2. Apply the validation checklist from the Migration Guidelines:
   - Migrated project passes compilation
   - All tests pass — don't silently skip tests
   - No legacy SDK dependencies/references exist
   - If `azure-sdk-bom` is used, ensure no explicit version dependencies for Azure libraries in the BOM
   - For each migration guide recorded during migration, fetch and verify the migrated code follows the guide's recommendations. Fix any deviations.
3. Populate `summary.md` (Upgrade Result, Tech Stack Changes, Commits, Challenges, Limitations, Next Steps)
4. Clean up temp files; remove HTML comments from all `.md` files
5. Verify all goals met
