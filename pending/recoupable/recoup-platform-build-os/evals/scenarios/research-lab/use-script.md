# Use script — research lab

The user agent receives the workspace path and the tasks below. It is **not** told about
`workspace-os`, "never-stale", or the doctor by name — only realistic asks. Before it runs, the
harness drops `use-input/experiment-001-results.md` into the workspace (at an `inbox/` if one exists,
otherwise the workspace root) to simulate a freshly added raw file.

Tasks, in order:

1. "I just added a new file, `experiment-001-results.md`, to the workspace — it's the writeup from our
   first real experiment. Get it into the system."

2. "Let's lock in a decision so we stop relitigating it: our primary eval metric is **AUROC**, and we
   use a **cosine learning-rate schedule** with a 5-epoch warmup as the baseline. Make sure that's
   captured where the team will find it."

3. "Can you give the workspace a once-over and tell me whether everything's consistent?"

4. "Okay — go ahead and tidy up anything that's stale or out of place."

5. (optional) "Is there anything we keep doing by hand here that's worth making repeatable, or any way
   the system itself should be improved?"

**What a strong run looks like:** task 1 files the raw note into its dated home, updates the relevant
experiment/study record + the dashboard *in the same turn*; task 2 deposits a durable decision in
`knowledge/`; task 3 runs the read-only doctor and writes a scored report to `operations/health.md`;
task 4 runs the janitor (fixes safe drift, re-scores); task 5 logs a grounded improvement or proposes
a skillify. Crucially, the updates in task 1 happen **without** being told to "update the dashboard."
