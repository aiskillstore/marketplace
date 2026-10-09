# Security and compatibility

The portable skill requires Bash, Python 3, Git and Antigravity CLI. Codex CLI and
Claude Code are supported driver hosts. The Claude Code host path was exercised with
synthetic live jobs; a provider model named `claude` alone says nothing about host support.

Use [Project lifecycle and verification](PROJECT_LIFECYCLE_AND_VERIFICATION.md) for
commands and [Troubleshooting](TROUBLESHOOTING.md) for failures.

## Execution boundaries

The driver reviews the diff and runs its own checks; the worker never owns acceptance.
A passing check proves only its exercised contract.

Prefer scoped dispatch for bounded jobs: `--provider-scope FILE --approve-transmission-sha SHA256`
binds reviewed read entries, content and a write subset, staged in a fresh owner-private
mode-`0700` Gitless cwd. Whole-worktree dispatch remains an explicit
`--approve-whole-worktree LAUNCH_APPROVAL_SHA256` exception. Every entry may reach
Google/Gemini; `--add-dir`, prompt restrictions and candidate-path gates do not narrow reads.
Exclude credentials, denied paths, unrelated private content, logs and state from
approved entries. Installation is not transmission approval.

Provider-scope approval binds reviewed content and policy; it grants neither provider execution, Git action, driver acceptance, nor publication.
The controller locally enumerates and validates paths, rejects unsafe copies, and
transactionally reconciles only authorized mutations. A disposable worktree itself
is not a security sandbox.

### Environments and verification

Provider children and dispatch-time `agy` version, help, and model-selection probes
receive only HOME, PATH, TMPDIR and locale variables by default. Approve additional
variables by exact name through `--provider-env NAME`; values are read at launch,
not persisted. Injection variables (`BASH_ENV`, `PYTHON*`, `LD_*`, `DYLD_*`, `GIT_*`,
`AGY_WORKER_SCHEMA`) cannot be opted in. Other local utilities, including diagnostics, are not provider dispatch
and are outside this environment guarantee.

The verifier baseline excludes HOME. Canonical `--verify-argv` arrays run without an
implicit shell; shell interpreters and all `env -S`/`--split-string` forms are rejected.
Explicit shell verification requires network and credential-access acknowledgements;
the historical `--verify` spelling also requires its legacy-shell acknowledgement.
Use `verify-job.sh --verify-env NAME` for approved ordinary variables. Credential-like
names, including HOME, require `--verify-credential-env NAME` and its acknowledgement.
Names bind into receipt policy; values cross a private descriptor, never the outer gate
environment or stored receipt. Acknowledgement supplies neither a value, network
isolation nor external-write authority. Candidate code remains untrusted.
The gate binds semantic Git index entries and the current branch/HEAD before and
after driver verification, rejecting changes to those entries or that branch/HEAD
even when worktree bytes are restored. The verifier runs untrusted candidate code
with the user's authority. The gate does not detect changes outside the candidate,
including Git hooks and configuration.

### Preview and staging

`transmission-preview` starts no AGY, provider or network process. It requires a real
registered branch-backed linked worktree through bounded fixed Git plumbing, excludes
the root `.git`, and emits digests rather than file contents or symlink targets.
Whole-worktree approval binds a double no-follow scan of paths, kinds, permissions,
bytes and literal symlink targets. Limits are 100,000 entries, 512 MiB, depth 128 and 30 seconds;
bounds or drift reject without path-only fallback. Provider scope binds policy,
readable manifest and selected content through the `transmission_sha256` subdigest.
Human approval uses the full `launch_approval_sha256`, also binding the exact task,
destination and launch settings described in the lifecycle guide. Preview shows the
full task and bound fields, while private manifest contents and environment values stay private.

The write list must be a subset of the read list. Copies reject aliases, hardlinks,
special nodes and path collisions; source drift rejects reconciliation. New launches
recheck the approved content before the provider starts. Finish or discard retired
jobs with their creating release; see
[controller state and actions](PROJECT_LIFECYCLE_AND_VERIFICATION.md#controller-state-and-actions).

### Session and native modes

Default `--provider-isolation session` retains the caller's existing HOME/session
and normal filesystem/network authority. Environment filtering and selected staging
cannot prevent or exhaustively observe host access.
Explicit native mode requires supported macOS scoped containment; failure never falls
back to session. Preserve the selected mode and grant profile throughout repairs.
Whole-worktree mode does not acquire native containment.
Native macOS Seatbelt containment cannot start when the driver host is already inside
a sandbox that prohibits nested `sandbox_apply` (observed with Codex `workspace-write`).
The same native path worked from an unsandboxed Claude Code host. Keep the selected
mode and resolve the host prerequisite; do not silently fall back to session mode.

Native permits the selected stage, private persistent provider HOME, per-attempt TMP,
exact AGY executable, read-only result schema and reviewed system runtime/tool paths.
The bound provider image gets metadata/existence access to its executable's exact
parent for Core Foundation and private-HOME ancestors for SQLite. This grants no
listing, sibling/ancestor data or equivalent access to another executable image;
self-verification has no such exception. Original checkout, Git administration and
ambient HOME remain denied apart from named runtime exceptions.

The entire stage is writable: the write subset is a reconciliation boundary, not an
OS file-by-file permission list. Private AGY settings express approved staged reads
and exact write selectors without copying user settings or granting commands, URLs,
MCP tools or ambient paths. Settings bytes/identity bind before launch, stay read-only
and are reused unchanged for repair; drift stops instead of being overwritten.
Other stages remain denied. Session and self-verification get no generated settings.
Trusted same-user processes or a malicious provider binary are not tamper-isolated.

### Native network, credentials and cleanup limits

Only the bound AGY image receives non-local TCP 443, local DNS resolver access,
TCP bind/listen and reviewed Keychain services. The listener rule permits IPv4/IPv6
wildcard binds, not just loopback; outbound local TCP remains denied. This is not a
Google recipient allowlist or TLS enforcement. Fork without exec retains image
privileges; exec to another program removes its network authority.

Exact `/usr/bin/security` receives the five reviewed Keychain/trust services and
read-only access to the bound default Keychain file. A bounded read-only lookup checks
its owner/identity without reading or hashing contents, then creates a minimal private
`DefaultKeychain` preference. No owner preferences or credentials are copied.
Prelaunch rechecks bind that preference and Keychain identity; repairs preserve them
and reject drift. Discovery does not prove a usable token or silent-login permission.

The file grant applies only to that helper: no provider/other-image access, parent
access, file write or extra network permission. Seatbelt cannot restrict helper
arguments, operations or items; broader same-user Keychain reads, additions, changes
and deletions may be allowed by the OS. Authorize both provider and helper exposure.
Local self-verification has no network or Keychain access.

Children inherit restrictions. Cleanup owns the original process group; detached
descendants remain confined but are not proven reaped. Known cleanup uncertainty
prevents reconciliation. The owner, same-UID processes and OS administrators remain
trusted; no same-user tamper resistance is claimed.

### Git evidence

Gate/snapshot reads ignore inherited Git variables and system/global configuration,
neutralize hooks/fsmonitor and external diff/textconv, and reject effective repository
clean/process/required filters, including Git LFS. Diagnostics do not expose filter
commands or values. A green gate never replaces independent diff review.

## Model and interface compatibility

Model and effort are caller-owned. Default model/effort remain unresolved;
literal values pass through without catalog substitution.

Each launch, including recovery, uses bounded local version/help capability checks
and rechecks the same executable immediately before launch. Missing flags or required
mode/output values reject. Version text is diagnostic only; help does not certify
authentication, model/backend identity, effective mode semantics or task quality.

Run `"$PIPELINE/ground-truth.sh"` before changing AGY-facing claims. Its default phase
is version/help only; `--account` explicitly inspects models, agents, plugins and
settings. Neither phase authorizes dispatch or configuration changes. Parse
`result.structured_output`, never echoed schema.

## Supported distribution

`skills/agy-worker/runtime/` is the portable core; matching root entrypoints wrap it.
Update/notifier tools are repository-only. The package [README](../README.md),
[skill](../SKILL.md) and references explain use without decorative assets or root docs.
Source, release, external catalog and installed bundle states require separate evidence.

## Host-specific compatibility surfaces

`direct-codex` means direct driver implementation on either host; its spelling is a
compatibility identifier. Codex sandbox settings remain Codex-only. Claude workflow
and doctor need no Codex binary; checkout maintenance does not discover plugins by
an old identity.
