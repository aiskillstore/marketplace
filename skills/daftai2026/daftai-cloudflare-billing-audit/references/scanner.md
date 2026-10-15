<!-- L3 | skills/daftai-cloudflare-billing-audit/references/scanner.md -->
# Offline scanner contract

## Invocation and outputs

Run from the skill directory with Bun:

```sh
bun scripts/audit.ts --project /absolute/path/to/project [--output-dir /absolute/path/to/audit-workdir]
```

`--project` is required. The default report base is `${SKILL_DIR}/audit-results`; `--output-dir` selects a different audit work directory. The output path must be outside the target project and every path component must be a real directory, never a symlink. Reports are created in a unique directory with `inventory.json` and `inventory.md`; existing results are never overwritten. Output creation uses the same platform-selected filesystem adapter as reads; the platform guarantees below apply to both.

The scanner runs offline and read-only against the target. It does not execute project code, imports, package scripts, lifecycle hooks, or subprocesses, and makes no network requests. Inventory reports omit config values, secrets, resource IDs, routes, cron expressions, and source snippets.

## Controlled single-file review

Do not use raw project paths or `cat` for manual code review. Read one file at a time through the controlled reader:

```sh
bun scripts/audit.ts --project /absolute/path/to/project \
  --inventory /absolute/path/to/audit-workdir/cloudflare-billing-audit-.../inventory.json \
  --read-file src/worker.ts
```

The file must be an exact path in `reviewEvidenceFiles` in a schema `1.1` inventory. Only bounded source JS/TS, selected D1 migration SQL, or selected Workers workflow YAML are eligible. The inventory must be a safe regular file named `inventory.json`, outside the target project; inventory-provided limits are not trusted. Inventory metadata has a separate 16 MiB read/write ceiling; the writer refuses an oversized inventory before creating output. This does not increase the 256 KiB source-file limit. The reader validates fixed default limits, re-runs the offline inventory, checks the root fingerprint and exact file SHA-256/stat fingerprint/byte count, then re-reads the single requested file through the selected filesystem adapter. Detected changed or stale evidence is rejected and no source text is written to stdout. Config files, `.env*`, credentials, arbitrary paths, symlinks, FIFOs, and over-limit files are never eligible. On failure stdout is empty; CLI exits `3` for stale/invalid inventory or evidence and `2` for unsafe arguments, unsupported secure filesystem access, or other safety failures. On success stdout is the explicitly requested source file for local review only; do not copy secrets or source snippets into the audit report.

`reviewEvidenceFiles` entries have `path`, `kind`, `bytes`, `sha256`, and `statFingerprint`. `kind` is `source-js-ts`, `d1-migration-sql`, or `github-workflow-yaml`. `readSourceFiles` lists safe-read source files, including syntax the lexical matcher cannot analyze. `scannedSourceFiles` is the subset actually passed through the supported lexical candidate scanner. `readAuxiliaryFiles` is the selected SQL/YAML subset. Fingerprints are snapshot identity checks, not proof of an atomic filesystem snapshot. Linux pins root/directory descriptors; the portable adapter uses stable-tree path and identity checks. Both reject detected symlinks and identity changes and recheck before returning a controlled read. Neither promises isolation from arbitrary same-privilege concurrent filesystem mutation.

## Platform boundary and threat model

The filesystem factory selects the adapter for the actual runtime platform. The report records `runtimePlatform`, `secureReadMode`, and `projectRootFingerprint`; preserve them in the agent report rather than claiming identical guarantees across hosts.

- Linux uses `descriptor-anchored` access with a verified `/proc/self/fd` descriptor path and `O_NOFOLLOW` semantics. Its read-only capability probe checks pinned-descriptor access and no-follow rejection. If that capability is absent, it fails closed rather than silently downgrading to portable reads.
- macOS and Windows use `portable-stable-tree` access: component/type/identity checks, bounded regular-file reads, and pre/post checks detect observed path or content changes. This is useful only while the target, its ancestors, and the output location remain stable. It is weaker than Linux descriptor anchoring, not an equivalent native no-follow traversal primitive.
- Windows paths are limited to ordinary local drive paths; UNC/device namespaces, drive-relative paths, alternate data streams, reserved device names, trailing dots/spaces, and ambiguous components are refused. Use exact slash-separated relative evidence paths from the inventory on every platform. Detected symlinks/junction redirection is refused; this is not a claim of complete native reparse-tag coverage.
- Other platforms or a failed required capability refuse the operation. Do not replace the adapter with a raw read, resolve a rejected symlink and retry its target, or use another path to bypass a refusal.

Stable-tree operation means no concurrent editor save/rename, checkout, generated-file writer, sync tool, or untrusted process mutating the relevant tree or ancestors. Stop if those conditions cannot be established. A pre/post check can miss an ABA replacement: a path may be replaced, used, and restored between observations. In portable mode this means the checks cannot prove that no outside-tree enumeration or read occurred under hostile concurrency, even if the result is later rejected. A hostile output-ancestor ABA replacement can likewise create an outside-directory file before the post-check; exclusive creation prevents overwriting an existing file but does not guarantee output containment under attack, so stable output ancestry is required. Fingerprints validate observed evidence consistency; they do not repair an already unsafe access or establish a snapshot.

Linux descriptor anchoring also is not an atomic snapshot or proof against every same-permission writer: hard links, mounts, content mutation, and renamed open directories remain threat-model limitations. Native macOS `openat` traversal and Windows root-handle-relative `NtCreateFile` with reparse-tag controls are not implemented or claimed. Windows `0600` mode bits are not a private ACL guarantee; choose an already appropriately restricted output directory. Treat reports as private even though source/config values are omitted.

## Parser and inventory coverage

- `wrangler.json` and `wrangler.jsonc`: comments are lexically removed while retaining line breaks; one valid trailing comma is accepted; duplicate object keys and malformed JSON/JSONC are rejected. Bun's built-in JSONC parser is used when present after duplicate-key validation; Node's built-in JSON parser fallback adds no dependency.
- `wrangler.toml`: parsed only when `Bun.TOML.parse` exists. Without it, the config is listed as `unsupported-no-bun-toml-parser`; no regex-based TOML fallback is used.
- Parser acceptance is not Wrangler schema validation. Malformed known binding/trigger/route/limit shapes and invalid roots remain unknown, and malformed configs do not authorize auxiliary evidence review.
- Wrangler environments are reported locally; bindings and values are not shallow-merged. `main` is checked as an in-project path and missing, excluded, symlink, invalid, or outside entry paths are explicit statuses. A present main does not prove it is loaded or a candidate is reachable.
- The inventory reports only normalized binding labels/types, vars counts, cron/route counts, and explicitly whitelisted numeric `limits.cpuMs`; it omits actual resource IDs and config values. A binding declaration alone is not a risk finding.

## Auxiliary evidence paths

Auxiliary formats are safe-read only and are not executed or treated as fully parsed:

- D1 SQL is considered only for valid parsed Wrangler object configs with object entries in `d1_databases`. Each binding's own `migrations_dir` is used; when absent, the scanner uses the workspace's `migrations/` directory. It selects bounded direct-child `.sql` files only. A root-level `migrations_dir` is not treated as a D1 binding setting. Invalid/sensitive/escaping paths, nested SQL paths, missing migrations, multiple-binding attribution, or truncation are explicit unknowns. If several bindings point at one folder, each SQL path is read once.
- YAML is considered only when a valid parsed Workers Wrangler config is found, and only direct children of `.github/workflows/` ending in `.yml` or `.yaml` are included. YAML is not parsed, validated, or executed.
- Other `.sql`/YAML files are not read as auxiliary evidence. Both classes use the same file/entry/depth/byte caps, sensitive-path exclusions, symlink rules, fingerprints, and controlled reader.

## Candidate findings

Each finding contains `ruleId` (the scanner's narrow candidate signal), `matchesRuleId` (a related topic in `references/sources.json`), `product`, `file`, `line`, `triggerChain`, `evidence`, `condition`, `possibleConsequence`, `recommendation`, and `sources`. `triggerChain` is always `unknown`: the scanner does not resolve imports, aliases, dataflow, dynamic dispatch, external triggers, or runtime reachability. `matchesRuleId` is a research cross-reference, not a verdict.

Current candidates:

| Scanner `ruleId` | Related `matchesRuleId` | Lexical signal |
| --- | --- | --- |
| `CFBA-DO-ALARM-SELF-REARM-CANDIDATE` | `CF-DO-ALARM-LOOP` | `setAlarm()` token inside a method or class-field arrow handler named `alarm` |
| `CFBA-DO-LOOP-ALARM-CANDIDATE` | `CF-DO-ALARM-LOOP` | `setAlarm()` token inside a loop block or single-statement loop |
| `CFBA-QUEUE-RETRY-CANDIDATE` | `CF-QUEUES-RETRY-FANOUT` | `retry()` token inside a method or class-field arrow handler named `queue` |
| `CFBA-QUEUE-CONSUMER-SEND-CANDIDATE` | `CF-QUEUES-SELF-REENQUEUE-LOOP` | `send()`/`sendBatch()` token inside a `queue` handler |
| `CFBA-QUEUE-LOOP-SEND-CANDIDATE` | `CF-QUEUES-SELF-REENQUEUE-LOOP` | `send()`/`sendBatch()` token inside a loop |

These are candidate indicators only. For example, a queue send target may differ from the consumer queue, and a retry or alarm may be guarded or intentional. Verify the actual entry point, call chain, configuration, guards, limits, and current Cloudflare terms before drawing a conclusion.

## Bounds and explicit gaps

Defaults: depth 8, 500 files, 4,000 directory entries, 2 MiB total bytes, 256 KiB per file, and 200 findings. Limits are clamped to these hard defaults; any reached or failed boundary is an explicit unknown and makes the report partial. A scanned status or empty finding list is never a safety proof.

Source candidates include `.js`, `.jsx`, `.mjs`, `.cjs`, `.ts`, `.tsx`, `.mts`, and `.cts`. `.jsx`/`.tsx`, likely inline JSX, template interpolation, ambiguous regex-versus-division forms, and handler syntax not recognized by the small lexical matcher are not passed to the lexical matcher and are explicitly unknown. A deterministic lexical work budget also turns unusually complex input into `source-work-budget-exceeded`; the bounded file remains eligible for controlled manual review. This is not a JavaScript/TypeScript parser, linter, call-graph engine, or bill estimator.

The scan excludes `.git`, `.hg`, `.svn`, `node_modules`, `build`, `dist`, `out`, `target`, `coverage`, `.wrangler`, `.next`, `.nuxt`, `.vercel`, `.turbo`, and `vendor`. It never reads `.env*`, `.dev.vars`, `.npmrc`, secret/credential-named files or directories, `.pem`, `.key`, `.p12`, or `.pfx`. Symlinks, FIFOs, sockets, devices, and other non-regular files are not read. Do not manually read excluded paths, symlink targets, or files absent from the controlled evidence allowlist.

## Behavior tests and installed-artifact acceptance

From the skill directory, with Bun and its native TOML parser:

```sh
bun test scripts/*.test.ts
```

The suites cover parser behavior, Wrangler inventory redaction, bounded candidates and unknowns, D1/workflow evidence selection, controlled-reader freshness/allowlisting, project/output containment, symlink/FIFO rejection where supported, deterministic path-substitution checks, and source-work budgets. `audit.portable.test.ts` tests the actual host-selected adapter and explicitly selects the portable adapter separately; it does not spoof `process.platform`. A Linux portable-adapter test is not a native macOS/Windows run. Platform-specific capabilities may skip; report those skips, not as passes.

For an unpacked/installable artifact, run its acceptance harness on each real host:

```sh
bun scripts/installed-smoke.ts --skill-dir "/absolute/path/to/unpacked-skill" --output "/absolute/path/to/external-results/native-smoke.json"
```

In PowerShell, use ordinary quoted drive paths, for example:

```powershell
bun scripts/installed-smoke.ts --skill-dir "C:\audit-tools\daftai-cloudflare-billing-audit" --output "C:\audit-results\native-smoke.json"
```

Run from the skill directory. The smoke runner exercises only synthetic fixtures, imports the selected installed module, runs its CLI inventory/controlled reader, and executes all installed `*.test.ts` suites using explicit installed paths. Linux-only descriptor/hostile-concurrency/FIFO coverage is recorded as skipped on non-Linux hosts. It records OS/runtime/adapter, per-file SHA-256 values, an aggregate artifact hash, result logs, and a `nativeMatrix` with unexecuted hosts labeled `NOT_RUN`. Keep the result file outside the installed skill so it does not alter the hashed artifact. Inspect the logs for skipped features; an overall passing harness does not certify unavailable capabilities or hostile-concurrency isolation. Preserve a separate native result for Linux, macOS, and Windows, with matching artifact hashes, before claiming tested compatibility across those hosts.

Expected host selection:

| Real host | Default mode | Required result evidence |
| --- | --- | --- |
| Linux | `descriptor-anchored` | Native smoke plus Linux descriptor/security suite; portable-explicit tests are separate |
| macOS (`darwin`) | `portable-stable-tree` | Native smoke on a stable tree; record unavailable features/skips |
| Windows (`win32`) | `portable-stable-tree` | Native smoke on a stable local drive tree; record unavailable features/skips and path/junction limitations |

Only a receipt from the actual host establishes that host's result. A matrix or runner by itself does not establish verified compatibility.

On Node 24, the narrower behavior check is:

```sh
node --experimental-strip-types --test scripts/audit.test.ts
```

That Node run does not verify Bun's native TOML parser, the Bun acceptance runner, or native behavior on another OS. A skip is not a pass for those capabilities.
