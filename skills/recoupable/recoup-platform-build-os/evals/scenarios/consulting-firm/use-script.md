# Use script — consulting firm

The user agent receives the workspace path and the tasks below. It is **not** told about
`workspace-os`, "never-stale", or the doctor by name. Before it runs, the harness drops
`use-input/acme-followup.md` into the workspace (an `inbox/` if one exists, else the root).

Tasks, in order:

1. "New file in the workspace: `acme-followup.md`. It's an update on the Acme deal — process it."

2. "Heads up — we lost the Globex deal. They went with a cheaper competitor. Update the pipeline, and
   make sure we capture *why* so we don't keep losing on price."

3. "Give the whole workspace an audit — is anything inconsistent or stale?"

4. "Reconcile it — fix whatever's safe to fix."

5. (optional) "We rebuild proposals from scratch every time and it's painful. Anything here worth
   turning into something repeatable?"

**What a strong run looks like:** task 1 moves Acme from the `proposal` stage to `won`/`signed`,
updates `clients/acme-corp/README.md`, the pipeline `_board.md`, and `artifacts/dashboard.html` *in
the same turn*, and captures the new "standard SOW structure" question as an FAQ; task 2 moves Globex
to `lost` and writes a decision/insight about price-based losses to `knowledge/`; task 3 runs the
read-only doctor → scored `operations/health.md`; task 4 runs the janitor; task 5 proposes skillifying
the proposal builder (the template already exists in `library/`, so this is ripe). The stage moves and
dashboard refresh in task 1 should happen **without** being told to "update the dashboard."
