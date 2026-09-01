# Security and compatibility

`agy-worker` is a Codex Agent Skill. It requires the OpenAI Codex CLI, Bash, Python 3,
Git, and the Google Antigravity CLI (`agy`). It is not a Claude or Claude Code skill.
Provider model slugs that contain `claude` describe a selectable provider model; they
do not make a Claude host supported.

For command sequencing and candidate acceptance, read
[Project lifecycle and verification](PROJECT_LIFECYCLE_AND_VERIFICATION.md). For
failure recovery, read [Troubleshooting](TROUBLESHOOTING.md).

## Execution boundaries

The skill helps Codex delegate repository work to `agy`; it does not transfer final
acceptance to the worker. Codex reviews the resulting diff and runs driver-owned
verification before reporting a result. A passing check is evidence for the command
that ran, not a general security or correctness guarantee.

`agy` is an external provider-backed CLI. Default dispatch without
`--provider-scope` makes the entire disposable worktree worker-readable and
potentially transmissible; `--add-dir`, prompt instructions, and candidate-path gates
do not narrow that read boundary. Optional scoped dispatch binds exact reviewed read
entries, their selected-content digest, and a write subset into the approved
transmission SHA, then copies only selected entries to a fresh owner-private
mode-`0700` Gitless provider cwd. The operator must approve the exact mode and content
boundary before launch. Credentials, private keys, user-denied paths, unrelated private files,
raw worker logs, and controller state must be absent from every entry approved for
transmission. Installation grants no such approval.

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

Driver-owned verification uses a stricter closed baseline that excludes `HOME`.
Use repeatable canonical JSON arrays with `--verify-argv`; they execute from the
repository root without an implicit shell. Direct shell interpreters, including
`env ... sh|bash|zsh|dash|ksh|fish`, are rejected in argv mode. Every `env -S` and
`env --split-string` form is rejected rather than partially parsed. Explicit shell
verification requires separate network and credential-access acknowledgements;
the historical `--verify` spelling additionally requires the legacy-shell flag.

Use repeated
`verify-job.sh --verify-env NAME` only when a chosen verifier genuinely needs an
additional caller variable. The authorized names are bound into the receipt policy
hash; their values cross a private descriptor into the trusted gate process, which
then builds the `env -i` verifier child environment. Values do not
enter the outer gate environment or stored receipt. Credential-like names, including
`HOME`, require `--verify-credential-env NAME` and the credential-access acknowledgement.
An acknowledgement grants neither a value, network isolation, nor external-write
authority. A driver-owned
command can still import and execute unreviewed candidate code, so do not expose
credentials merely because the command itself is trusted.

`agy-worker.sh transmission-preview --workdir ABSOLUTE_DISPOSABLE_WORKTREE` is a
provider-free review surface. It double-scans a bounded no-follow path
manifest, excludes the root `.git` marker, and uses fixed, bounded local
`/usr/bin/git worktree list` plumbing to require a real registered branch-backed linked
worktree. With `--provider-scope FILE`, it evaluates the closed scope JSON against
the worktree and computes the policy digest, complete readable path/kind manifest,
selected-content manifest and digest, and unified `transmission_sha256`. It starts no
`agy`, provider, or network process. It is not approval and does not bind a future
provider launch. When dispatched with
`--provider-scope FILE --approve-transmission-sha SHA256`, a fresh owner-private
mode-`0700` Gitless stage is materialized with only selected entries. The write list
must be a subset of the read list; after provider completion, only authorized staged
mutations are transactionally reconciled to the source worktree.

Provider-scope approval binds reviewed content and policy; it grants neither provider
execution, Git action, driver acceptance, nor publication. The controller still
locally enumerates and validates worktree paths and scope entries before staging. The
copy and reconciliation controls reduce the provider-visible surface but are not
filesystem, network, `PATH`, `HOME`, or same-user isolation and retain documented
local-owner and portable mutation-race residuals. Failures preserve recovery evidence
and fail closed rather than silently broadening scope.

Environment filtering is not filesystem, network, `PATH`, `HOME`, or same-user
process isolation. Candidate code may still read accessible files or use available
network paths; a green gate never replaces human diff review.

## Model and interface compatibility

Model and effort selection are caller-owned. Recommendations are advisory and cannot
change selection, permission, authentication, provider scope, or a human-required
outcome. With no selector, leave the provider default unresolved rather than inventing
a model slug or thinking level.

The reviewed model/effort matrix is compatibility evidence for its exact accepted
bytes and agy version. Before every reviewed direct dispatch, including an exact
version match, Codex inspects current bounded raw `agy --help` and stops when the
caller-selected model or effort cannot be honored. Installed-version drift requires
an explicit compatibility disposition bound to the reviewed help SHA; structural help
acceptance alone is not semantic approval or a provider-availability claim.

Run the repository `ground-truth.sh` and inspect `agy --help` before changing
agy-facing flags or public claims. agy may exit zero while ordinary output is empty;
the structured result is `result.structured_output`, never the echoed schema.

## Supported distribution

The canonical runtime lives in `skills/agy-worker/runtime/`. Repository-root scripts
are compatibility wrappers. The Codex marketplace package and GitHub installation path
refer to that one bundle; they do not create a second runtime or authorize a provider
dispatch.

The package-owned [README](../README.md), [skill router](../SKILL.md), and references
are part of the standalone bundle. They intentionally require no decorative image or
repository-root documentation to explain safe use. Release state, external catalog
state, and an installed local bundle are separate facts and must be verified
independently.
