# Troubleshooting & Anti-Excuse Rules

Load this file when encountering build failures, test failures, or any temptation to stop mid-migration.

## Anti-Excuse Rules (MANDATORY)

- **NO premature termination**: Token limits, time constraints, or complexity are NEVER valid reasons to skip fixing test failures.
- **NO "close enough" acceptance**: 95% is NOT 100%. Every failing test requires a fix attempt with documented root cause.
- **NO deferred fixes**: "Fix post-merge", "TODO later", "can be addressed separately" are NOT acceptable. Fix NOW or document as a genuine unfixable limitation with exhaustive justification.
- **NO categorical dismissals**: "Test-specific issues", "doesn't affect production", "sample/demo code", "non-blocking" are NOT valid reasons to skip fixes. ALL tests must pass.
- **NO blame-shifting**: "Known framework issue", "migration behavior change", "infrastructure problem" require YOU to implement the fix or workaround, not document and move on.
- **Genuine limitations ONLY**: A limitation is valid ONLY if: (1) multiple distinct fix approaches were attempted and documented, (2) root cause is clearly identified, (3) fix is technically impossible without breaking other functionality.

## Critical: Do Not Stop Mid-Migration

You are expected to carry the migration to completion — either fully succeed or encounter an unrecoverable error. The following behaviors are **strictly prohibited**:

- **Do NOT stop to summarize progress.** Never output a message listing "what was done" and "what remains" as your final response.
- **Do NOT treat partial migration as acceptable.** Migrating some files but not others is not a valid stopping point. You must attempt every file and every dependency.
- **Do NOT hand off work to the user.** Never suggest the user "continue" or "complete the remaining items." You are responsible for finishing everything.
- **If you hit an error on one file, move on to the next.** A failure in one source file should not prevent you from migrating the rest. Come back to fix it after attempting all files.
- **If a build fails after migration, debug and fix it.** Do not stop at "build failed." Investigate the errors, fix them, and rebuild. Repeat until the build passes or you have exhausted all reasonable approaches.

**The only acceptable stopping conditions are:**
1. The migration is fully complete and the build passes.
2. You have attempted everything and an unrecoverable error prevents further progress (e.g., a fundamental API incompatibility with no workaround). In this case, clearly state the blocker.
