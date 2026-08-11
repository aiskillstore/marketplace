# Use script — record label

The user agent receives the workspace path and the tasks below. It is **not** told about the OS
builder, "never-stale", or the doctor by name. Before it runs, the harness drops
`use-input/new-release-brief.md` into the workspace (an `inbox/` if one exists, else the root).

Tasks, in order:

1. "New file in the workspace: `new-release-brief.md`. It's the brief for Gatsby Grace's next single —
   process it."

2. "Heads up — Neon Vow's EP slipped; production pushed it a month. Update their release, and capture
   *why* so we learn from the slip."

3. "Give the whole workspace an audit — is anything inconsistent or stale?"

4. "Reconcile it — fix whatever's safe to fix."

5. (optional) "We rebuild the DSP pitch one-sheet from scratch every release and it's painful.
   Anything here worth turning into something repeatable?"

**What a strong run looks like:** task 1 creates/updates
`artists/gatsby-grace/releases/{release-slug}/RELEASE.md` from the brief, refreshes the artist's
release list and `artifacts/dashboard.html` *in the same turn*, and captures any new recurring
question as an FAQ; task 2 updates Neon Vow's release stage + date and writes a decision/insight about
the slip to `knowledge/`; task 3 runs the read-only doctor → scored `operations/health.md`; task 4
runs the janitor; task 5 proposes skillifying the DSP one-sheet (the template already exists in
`library/`, so it is ripe). The release + dashboard updates in task 1 should happen **without** being
told to "update the dashboard".
