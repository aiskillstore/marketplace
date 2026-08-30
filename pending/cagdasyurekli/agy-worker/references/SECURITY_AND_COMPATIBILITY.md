# Security and compatibility

`agy-worker` is a Codex Agent Skill. It requires the OpenAI Codex CLI, Bash, Python 3,
Git, and the Google Antigravity CLI (`agy`). It is not a Claude or Claude Code skill.
Provider model slugs that contain `claude` describe a selectable provider model; they
do not make a Claude host supported.

## Execution boundaries

The skill helps Codex delegate repository work to `agy`; it does not transfer final
acceptance to the worker. Codex reviews the resulting diff and runs driver-owned
verification before reporting a result. A passing check is evidence for the command
that ran, not a general security or correctness guarantee.

`agy` is an external provider-backed CLI. Before dispatch, the operator must approve
the repository and path scope that may be read and sent to the provider. Do not include
credentials, private keys, unrelated local files, raw worker logs, or local controller
state in the task prompt. Installation does not grant this approval.

Work happens in a disposable Git worktree, but that worktree is not a security sandbox.
The operator remains responsible for repository access, review, test selection, and
any credentials or network access available to commands they run.

Provider children and the dispatch-time `agy` version, help, and model-selection
probes receive only `HOME`, `PATH`, `TMPDIR`, and locale variables by default. Pass an
additional caller variable by exact name with repeated `--provider-env NAME`; the value
is read only at launch and is not written to the dispatch command or public status.
Startup and runtime injection variables such as `BASH_ENV`, `PYTHON*`, `LD_*`,
`DYLD_*`, `GIT_*`, and the gate's `AGY_WORKER_SCHEMA` selector cannot be opted in.

Other local utilities, including diagnostics and feedback-draft generation, are not
provider dispatch and are outside this environment-isolation guarantee.

Driver-owned verification uses the same closed baseline. Use repeated
`verify-job.sh --verify-env NAME` only when a chosen verifier genuinely needs an
additional caller variable. The authorized names are bound into the receipt policy
hash; their values cross a private descriptor directly into the `env -i` verifier
child and do not enter the outer gate environment or stored receipt. A driver-owned
command can still import and execute unreviewed candidate code, so do not expose
credentials merely because the command itself is trusted.

Environment filtering is not filesystem, network, `PATH`, `HOME`, or same-user
process isolation. Candidate code may still read accessible files or use available
network paths; a green gate never replaces human diff review.

## Supported distribution

The canonical runtime lives in `skills/agy-worker/runtime/`. Repository-root scripts
are compatibility wrappers. The Codex marketplace package and GitHub installation path
refer to that one bundle; they do not create a second runtime or authorize a provider
dispatch.
