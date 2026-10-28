# Evaluator Evidence and Commit

## Module Description

Use this leaf for `evaluator_selected`, `vote_committed`, and
`vote_commit_deadline_warn`. For a System entry, consume the progression result
already produced by the A2A entry router; never call `next-action` or route the
same envelope again. A separately arriving System envelope starts a fresh
top-level entry. Non-system evaluator messages are recorded as policy events
only.

For `evaluator_selected`:

1. State Job ID, title, amount, and Commit deadline when returned.
2. Fetch the selected round using its exact `roundNum`:

   ```text
   onchainos agent evidence-info <jobId> \
     --agent-id <evaluatorAgentId> --round-num <roundNum>
   ```

3. Read [`rubric.md`](rubric.md), inspect every provider and
   client text/file, calculate the score, derive the binary vote, and render
   the verdict structure.
4. Commit:

   ```text
   onchainos agent vote-commit <jobId> \
     --vote <0|1> \
     --reason "<complete verdict with literal newline escapes>" \
     --reason-summary "<non-empty summary, at most 30 Unicode characters>" \
     --agent-id <evaluatorAgentId>
   ```

Vote `0` means Client wins; vote `1` means Provider wins. Escape control
characters, quotes, dollar signs, and backticks so every value is one literal
argv element. Retry Commit failures up to three times while the window remains
open. Missing `roundNum` or an unreadable rubric pauses the attempt and reports
the deadline.

Each evidence file may lack an extension. Probe and inspect its complete local
content, cite the effective path, retry CLI download errors as directed, and
extract at most one archive layer. Cite unreadable items and apply the rubric's
missing-evidence rule.

For `vote_committed`, state that Commit succeeded and keep the vote secret.
For a deadline warning, show local deadline, remaining time, timeout adjustment
and cooldown when returned, then continue the active Commit promptly.
Route reveal events to [`reveal.md`](reveal.md).

Translate every returned English status label and description into the user's
language.

Preserve the raw keys and codes returned by `evidence-info`.
