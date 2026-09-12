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

`agy` is an external provider-backed CLI. Prefer scoped dispatch for bounded jobs: it binds exact reviewed read
entries, their selected-content digest, and a write subset into the approved
transmission SHA, then copies only selected entries to a fresh owner-private
mode-`0700` Gitless provider cwd. Whole-worktree dispatch remains an explicit
`--approve-whole-worktree LAUNCH_APPROVAL_SHA256` exception; it makes the entire disposable
worktree worker-readable and potentially transmissible, and `--add-dir`, prompt
instructions, and candidate-path gates do not narrow that read boundary. The operator must approve the exact mode and content
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
Default `--provider-isolation session` retains the caller's existing HOME/session
through the filtered environment. Explicit `--provider-isolation native` replaces
HOME/TMP/XDG with private directories for scoped launches. Version/help probes are
separate local preflight processes.

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
copy and reconciliation controls apply in both execution modes. Default session mode
uses normal user filesystem/network authority without AGY sandbox or native host
containment. It cannot prevent or exhaustively observe access outside the staged
workspace. The initial approval includes this mode; it remains bound throughout the
job. Explicit native mode adds macOS containment for scoped launches. Unsupported
hosts reject native mode; failures never switch to session mode. Whole-worktree
dispatch retains its separate, explicit authority and does not acquire containment.

The native profile permits the fresh selected stage, private persistent provider HOME,
per-attempt TMP, the exact agy executable, the bound result-schema file as read-only
input, and reviewed system runtime/tool paths. It denies access to the original
checkout, Git administration, and ambient HOME. The
whole stage is writable; the write subset is a controller reconciliation boundary,
not an OS file-by-file permission list. Fresh copies and prelaunch identity/content
checks reject hardlinks and stage drift.

Only the bound agy process image receives non-local TCP 443, DNS resolution through
the local mDNSResponder socket, and local TCP bind/listen permissions. It also receives
the reviewed Keychain service access. The macOS `localhost` listener selector also permits IPv4
and IPv6 wildcard binds: it does not guarantee a loopback-only listener, and the
agy image can expose a listener to the local network. Outbound connections to local
TCP services remain denied. This is neither a Google recipient allowlist nor
TLS protocol enforcement. A fork without exec retains that image privilege; exec to
a different program removes its network authority. The exact `/usr/bin/security`
helper also receives the same five reviewed Keychain/trust Mach services so AGY can
reuse its saved account session. It receives no additional network or filesystem
access. Seatbelt cannot limit helper arguments, operations, or Keychain items: this
permits broader same-user Keychain reads, additions, changes, and deletions where
the OS allows them, not only an AGY-token lookup. Other executable images receive
neither exception. Local self-verification has no network or Keychain access.
Authorize both the provider and helper exposure in the initial job package.

Filesystem and network restrictions are inherited by children. Cleanup binds and
reaps the original process group; a descendant that detaches through posix_spawn
attributes remains confined but is not proven reaped. A known cleanup uncertainty
prevents candidate reconciliation. The local owner, same-UID processes, and OS
administrators remain trusted; same-user tamper resistance is not claimed.

Environment filtering is not filesystem, network, `PATH`, `HOME`, or same-user
process isolation. Candidate code may still read accessible files or use available
network paths; a green gate never replaces human diff review.

### Boost authority boundary

`--boost` is an explicit advanced raw-dispatch profile, not a performance-only switch.
The provider may invoke subagents and protected tools. The wrapper therefore binds the
reviewed warning to the exact job ID, requires `task`/`accept-edits`, one cycle, no
persona, and slash-command protection, and records the approval in command V8. This
acknowledgement does not grant a provider permission, expand selected-content or
whole-worktree scope, or authorize acceptance, Git, or publication. The controller
requires the first init frame to report `agent=Boost` and
`permission_mode=request-review`; mismatch is a terminal `boost_contract` failure.
Boost dispatches have no resume, restart, or continuation path, so a new attempt needs
a new job ID, a new transmission decision, and a fresh risk acknowledgement.

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

Resolve the installed package, then run `"$PIPELINE/ground-truth.sh"` without arguments
and inspect `agy --help` before changing agy-facing flags or public claims. The default
interface phase invokes only `agy --version` and `agy --help`; `--account` is a separate
explicit action because it inspects account-owned model, agent, plugin, and local-settings
state. agy may exit zero while ordinary output is empty; the structured result is
`result.structured_output`, never the echoed schema.

For an exact version policy, manifest-bound model-inventory capture can require the
disposable snapshot to execute from a macOS kernel-reported read-only mount (for example,
an owner-prepared UDRO image). It binds the snapshot digest and descriptor/path evidence,
checks the mount's read-only flag before and after the sole child, and fails closed on
drift. This blocks the observed in-place self-update route; it does not prove that a
self-updater cannot execute a different writable binary, nor establish resistance to the
local owner, same-UID processes, or an OS administrator. The installed `agy` binary and
user configuration are never modified.

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
