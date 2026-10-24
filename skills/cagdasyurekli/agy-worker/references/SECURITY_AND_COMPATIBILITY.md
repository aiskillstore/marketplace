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

### Worker instruction precedence

The worker prompt instructs the worker to respect applicable user and repository
instructions, including security, privacy, permission and scope constraints; conflicts
or missing answers needed to satisfy those constraints require `blocked` and
`requires_human=true`. It explicitly protects secrets, data destinations, destructive
actions and required permission to act, and forbids assuming authorization. For routine
questions that need no protected answer, it instructs the worker to record the question
in `open_questions` and a safe assumption in `summary`, then continue. Compatible report
requirements go inside the schema fields; incompatible templates yield to the run's
response format. These are prompt instructions; provider compliance still needs
independent review and verification.

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

`--provider-isolation` has no implicit value: the driver names the mode and its consequence in the approval request and never selects `session` on its own. `session` retains the caller's existing HOME/session
and normal filesystem/network authority, plus ambient enabled user plugins, hooks and MCP servers. Environment filtering and selected staging
cannot prevent or exhaustively observe host access.
AGY 1.3.5 was observed starting workspace `.agents/mcp_config.json` commands
before worker activity, including a whole-worktree session explore/plan run. It also
started MCP servers from enabled user-installed plugins in session mode. Disabling slash
commands does not suppress those servers. Global hooks in `~/.gemini/config/hooks.json`
and enabled-plugin hooks were observed executing in headless `-p` runs with
`--disable-slash-commands`. These hooks can observe or rewrite tool calls, including
shell commands. Hooks embedded in `~/.gemini/antigravity-cli/settings.json` and
`PreToolUse` decision outputs (`allow`/`auto_approve`/deny), including their effect on
headless permission prompts, were not tested.

A direct synthetic headless AGY 1.4.2 run with `--disable-slash-commands`
started MCP server commands from `mcp_config.json` in each of `.agents/`, `_agents/`,
`.agent/` and `_agent/`. Each server wrote a distinct marker outside the synthetic
workspace. This observed MCP startup, not a chained agy-worker dispatch; native
containment and ancestor-root loading were not exercised. Hooks, custom agents and
plugins under the three alias roots were not tested live.

Preview rejects known executable provider configuration in provider content; every
launch, including repairs, additionally checks the actual cwd and bounded ancestors.
The same policy applies in session and native modes to all four roots:
`.agents/`, `_agents/`, `.agent/` and `_agent/`. For each root, reserved leaves
anywhere below it are `mcp_config.json`, `hooks.json`, `skills.json`, `rules.json`,
`agents.json` and `plugins.json`; `plugin.json` below its `plugins/` directory is
also rejected, including nested plugin manifest directories. Immediate `agents/*.md`
and `agents/*/agent.md` nodes below each root are also reserved:
[AGY documents](https://www.antigravity.google/docs/subagents/) their discovery as
custom-agent configuration. The policy rejects these nodes regardless of
contents/type, symlinked roots, symlinks at/below each root's `plugins/`, and symlinked
`agents/` directories or their immediate children, using NFC/casefold path
classification. These are offline policy checks, not live discovery or invocation
proof for every reserved form. `.agents/hooks.json` execution was confirmed live;
the other reserved paths are conservative execution candidates.
Plain instructions, skills/rules Markdown and `marketplace.json` remain content.

Use scoped mode excluding executable configuration under all four roots; otherwise
use a disposable worktree without it. Unselected source configuration is allowed when it is not an
actual provider ancestor. Scoped preview checks known selected content; the final
stage/job path is resolved later and its actual ancestry is checked before launch.
Ancestors stop at the nearest `.git` file or directory, or conservatively at the
filesystem root for Gitless stages; this overapproximation can reject configuration
beyond AGY's actual project root. Trusted ambient HOME is exempt only as an ancestor,
never as the actual cwd or a repository/job-controlled directory. No user settings,
`.gemini` configuration or installed plugins are read, modified or suppressed by
this rejection. Finite checks do not isolate a hostile same-user process replacing
paths after observation or adding previously absent subtrees after enumeration.

Native's private HOME and generated private settings exclude ambient plugins and
global/plugin hooks. `tests/test-provider-containment.py` cases
`profile_and_environment_are_private` and `native_boundary_is_enforced` prove that
local mechanism; they are not a live AGY 1.3.5 native plugin or hook negative canary.

For each attempt, the controller derives the owning main worktree from the bound
workdir's Git common directory and compares a bounded source observation against
one immutable baseline per job, before later launches and before admitting a report
or retaining an inherited candidate. No-candidate cancellations and failures record
`deferred`; their next resume/continue/repair/restart must pass the comparison. A
cancelled repair also records `deferred` while keeping its inherited candidate; result,
finalize, verification copy, self-verification, and any relaunch compare first. The observation binds HEAD, index, tracked paths, and non-ignored
untracked paths. Clean tracked files use Git object IDs plus metadata; dirty tracked
and non-ignored untracked files are hashed from bytes. Ignored untracked files and
other host paths are excluded. A detected change, including an owner edit, blocks
candidate recognition and reuse; inspect the source and start a new job. The finite
before/after observations do not detect changes wholly reverted between them and do
not confine writes. A verified main-workdir helper skips the comparison; public
transmission preview still requires a linked disposable worktree.

The observation caps paths, listings, directly read bytes, and elapsed work. If the
prelaunch observation fails, the provider is not started; if the post-exit observation
fails, the candidate and reuse are blocked. Status gives an actionable next step. These
limits are not a throughput benchmark or a whole-file-byte guarantee for clean tracked
files.

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

Native binds only the dedicated Keychain
`<owner HOME from passwd>/Library/Keychains/agy-worker-provider.keychain-db`, never the
login or default Keychain. Exact `/usr/bin/security` receives the five reviewed
Keychain/trust services and read-only access to that one file. Binding checks its
owner/identity without reading or hashing contents, then creates a minimal private
`DefaultKeychain` preference naming it. No owner preferences or credentials are copied.
Prelaunch rechecks bind that preference and Keychain identity; repairs preserve them
and reject drift. Binding does not prove a usable token or silent-login permission.
A missing or locked dedicated Keychain fails closed before launch (exit 27, before the
task is read for a new job); the lock state is read without UI because a locked lookup
inside the sandbox hangs behind an unlock dialog. Setup and unlock:
[Dedicated agy keychain](TROUBLESHOOTING.md#dedicated-agy-keychain-for-native-isolation).

The file grant applies only to that helper: no provider/other-image access, parent
access, file write or extra network permission. Seatbelt cannot restrict helper
arguments, operations or items; broader same-user Keychain reads, additions, changes
and deletions may be allowed by the OS. The Mach services are unchanged, so the
sandbox still reaches the system's Keychain services, not only the one file. Authorize
both provider and helper exposure. Observed on macOS with the live test shape (a
sandboxed `show-keychain-info` on `login.keychain-db` failed with `Operation not
permitted`, and `list-keychains` showed only the dedicated Keychain and System), the
login Keychain was unreadable inside the sandbox; that is an observation, not a
guarantee for other macOS versions or profiles. When agy refreshes an expired access
token inside native mode it may be unable to write back to the Keychain and fall back
to writing a token file inside the private provider HOME (agy logs "falling back to
file"); that file stays under the job's private provider HOME.
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
