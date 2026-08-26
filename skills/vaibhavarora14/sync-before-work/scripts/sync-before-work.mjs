#!/usr/bin/env node

import { existsSync } from "node:fs";
import { spawnSync } from "node:child_process";

const VERSION = "0.1.2";
const EXIT = {
  ok: 0,
  usage: 2,
  blocked: 3,
  conflict: 4,
  git: 5,
  recovery: 6,
};

function parseArguments(argv) {
  const options = {
    mode: "check",
    strategy: "merge",
    remote: undefined,
    base: undefined,
    json: false,
  };
  let selectedMode = false;

  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (["--check", "--preview", "--apply"].includes(argument)) {
      if (selectedMode) throw new Error("Choose only one of --check, --preview, or --apply.");
      options.mode = argument.slice(2);
      selectedMode = true;
    } else if (argument === "--strategy") {
      options.strategy = argv[++index];
      if (!options.strategy) throw new Error("--strategy requires merge or rebase.");
    } else if (argument === "--remote") {
      options.remote = argv[++index];
      if (!options.remote) throw new Error("--remote requires a remote name.");
    } else if (argument === "--base") {
      options.base = argv[++index];
      if (!options.base) throw new Error("--base requires a branch name.");
    } else if (argument === "--json") {
      options.json = true;
    } else if (argument === "--help" || argument === "-h") {
      options.help = true;
    } else if (argument === "--version" || argument === "-v") {
      options.version = true;
    } else {
      throw new Error(`Unknown option: ${argument}`);
    }
  }

  if (!["merge", "rebase"].includes(options.strategy)) {
    throw new Error("--strategy must be merge or rebase.");
  }
  return options;
}

function helpText() {
  return `sync-before-work ${VERSION}

Safely update the current Git branch from its remote default branch.

Usage:
  sync-before-work [--check | --preview | --apply] [options]

Modes:
  --check       Inspect local refs only (default; no fetch or branch change)
  --preview     Fetch the default branch and report what --apply would do
  --apply       Fetch and safely fast-forward, merge, or explicitly rebase

Options:
  --remote NAME             Override the remote (default: origin or sole remote)
  --base BRANCH             Override the default branch
  --strategy merge|rebase   Use merge (default) or rebase unpublished work
  --json                    Emit machine-readable JSON
  --help                    Show this help
  --version                 Show the version

The command never pushes, force-pushes, resets, stashes, switches branches,
or guesses through conflicts.`;
}

function git(args, options = {}) {
  return spawnSync("git", args, {
    cwd: options.cwd ?? process.cwd(),
    encoding: "utf8",
    env: {
      ...process.env,
      GIT_TERMINAL_PROMPT: "0",
      GIT_MERGE_AUTOEDIT: "no",
    },
  });
}

function stdout(result) {
  return result.stdout.trim();
}

function combinedError(result) {
  return [result.stderr, result.stdout].map((value) => value.trim()).filter(Boolean).join("\n");
}

function redactSensitiveText(value) {
  return value
    .replace(/\b([a-z][a-z0-9+.-]*:\/\/)([^/\s@]+)@/gi, "$1***@")
    .replace(/([?&](?:access_token|auth|key|token)=)[^&\s]+/gi, "$1***")
    .replace(/(authorization:\s*bearer\s+)[^\s]+/gi, "$1***");
}

function sanitizeOutput(value) {
  if (typeof value === "string") return redactSensitiveText(value);
  if (Array.isArray(value)) return value.map(sanitizeOutput);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([key, entry]) => [key, sanitizeOutput(entry)]),
    );
  }
  return value;
}

function emit(options, result, exitCode = EXIT.ok) {
  const safeResult = sanitizeOutput(result);
  if (options.json) {
    process.stdout.write(`${JSON.stringify(safeResult)}\n`);
  } else {
    const marker = exitCode === EXIT.ok ? "✓" : "!";
    process.stdout.write(`${marker} ${safeResult.message}\n`);
    if (safeResult.branch && safeResult.base) {
      process.stdout.write(`  ${safeResult.branch} ← ${safeResult.remote}/${safeResult.base}\n`);
    }
    if (safeResult.conflicts?.length) {
      process.stdout.write(`  Conflicts: ${safeResult.conflicts.join(", ")}\n`);
    }
  }
  process.exitCode = exitCode;
}

function fail(options, status, message, exitCode, context = {}) {
  emit(options, { status, message, changed: false, ...context }, exitCode);
}

function pathForGitState(name) {
  const result = git(["rev-parse", "--git-path", name]);
  return result.status === 0 ? stdout(result) : undefined;
}

function operationInProgress() {
  const stateNames = [
    "MERGE_HEAD",
    "CHERRY_PICK_HEAD",
    "REVERT_HEAD",
    "rebase-merge",
    "rebase-apply",
    "sequencer",
  ];
  return stateNames.find((name) => {
    const path = pathForGitState(name);
    return path && existsSync(path);
  });
}

function selectRemote(requested) {
  const result = git(["remote"]);
  if (result.status !== 0) return { error: combinedError(result) };
  const remotes = stdout(result).split("\n").filter(Boolean);
  if (requested) {
    return remotes.includes(requested)
      ? { remote: requested }
      : { error: `Remote '${requested}' does not exist.` };
  }
  if (remotes.includes("origin")) return { remote: "origin" };
  if (remotes.length === 1) return { remote: remotes[0] };
  if (remotes.length === 0) return { error: "No Git remote is configured." };
  return { error: "Multiple remotes exist; select one with --remote." };
}

function baseFromRemoteHead(remote) {
  const result = git(["symbolic-ref", "--quiet", "--short", `refs/remotes/${remote}/HEAD`]);
  if (result.status !== 0) return undefined;
  const prefix = `${remote}/`;
  const ref = stdout(result);
  return ref.startsWith(prefix) ? ref.slice(prefix.length) : undefined;
}

function baseFromCandidates(remote) {
  for (const candidate of ["main", "master"]) {
    const result = git(["show-ref", "--verify", "--quiet", `refs/remotes/${remote}/${candidate}`]);
    if (result.status === 0) return candidate;
  }
  return undefined;
}

function baseFromRemote(remote) {
  const result = git(["ls-remote", "--symref", remote, "HEAD"]);
  if (result.status !== 0) return { error: combinedError(result) };
  const match = result.stdout.match(/^ref:\s+refs\/heads\/(.+)\s+HEAD$/m);
  return match ? { base: match[1] } : { error: `Could not determine ${remote}'s default branch.` };
}

function dirtyEntries() {
  const result = git(["status", "--porcelain", "--untracked-files=normal"]);
  if (result.status !== 0) return { error: combinedError(result) };
  return { entries: stdout(result).split("\n").filter(Boolean) };
}

function isAncestor(ancestor, descendant) {
  return git(["merge-base", "--is-ancestor", ancestor, descendant]).status === 0;
}

function branchIsPublished(branch, remote) {
  const upstream = git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"]);
  if (upstream.status === 0) return true;
  const remoteBranch = git(["ls-remote", "--exit-code", "--heads", remote, branch]);
  return remoteBranch.status === 0 && stdout(remoteBranch).length > 0;
}

function abortOperation(kind) {
  return git([kind, "--abort"]);
}

function context(options, values = {}) {
  return {
    mode: options.mode,
    strategy: options.strategy,
    ...values,
  };
}

let options;
try {
  options = parseArguments(process.argv.slice(2));
} catch (error) {
  const json = process.argv.includes("--json");
  fail({ json }, "invalid_arguments", error.message, EXIT.usage);
}

if (options && options.help) {
  process.stdout.write(`${helpText()}\n`);
} else if (options && options.version) {
  process.stdout.write(`${VERSION}\n`);
} else if (options) {
  const repository = git(["rev-parse", "--show-toplevel"]);
  if (repository.status !== 0) {
    fail(options, "not_a_repository", "Run this command inside a Git working tree.", EXIT.usage);
  } else {
    const branchResult = git(["symbolic-ref", "--quiet", "--short", "HEAD"]);
    if (branchResult.status !== 0) {
      fail(options, "detached_head", "Detached HEAD: create or switch to a branch before syncing.", EXIT.blocked);
    } else {
      const branch = stdout(branchResult);
      const activeOperation = operationInProgress();
      if (activeOperation) {
        fail(
          options,
          "operation_in_progress",
          `Git operation state '${activeOperation}' is already present; finish or abort it first.`,
          EXIT.blocked,
          { branch },
        );
      } else {
        const remoteSelection = selectRemote(options.remote);
        if (remoteSelection.error) {
          fail(options, "remote_unknown", remoteSelection.error, EXIT.usage, { branch });
        } else {
          const remote = remoteSelection.remote;
          let base = options.base ?? baseFromRemoteHead(remote) ?? baseFromCandidates(remote);

          if (!base && options.mode !== "check") {
            const remoteBase = baseFromRemote(remote);
            if (remoteBase.error) {
              fail(options, "base_unknown", remoteBase.error, EXIT.git, { branch, remote });
            } else {
              base = remoteBase.base;
            }
          }

          if (!base) {
            fail(
              options,
              "base_unknown",
              "Could not determine the default branch from local refs; use --base or run --preview.",
              EXIT.usage,
              { branch, remote },
            );
          } else {
            const baseContext = { branch, base, remote, upstreamRef: `${remote}/${base}` };
            const state = dirtyEntries();
            if (state.error) {
              fail(options, "git_error", state.error, EXIT.git, baseContext);
            } else if (options.mode === "apply" && state.entries.length > 0) {
              fail(
                options,
                "blocked_dirty",
                "Working tree has staged, unstaged, or untracked changes; commit or remove them before syncing.",
                EXIT.blocked,
                { ...baseContext, dirtyEntries: state.entries },
              );
            } else {
              const remoteRef = `refs/remotes/${remote}/${base}`;
              if (options.mode !== "check") {
                const fetch = git([
                  "fetch",
                  "--prune",
                  "--no-tags",
                  remote,
                  `refs/heads/${base}:${remoteRef}`,
                ]);
                if (fetch.status !== 0) {
                  fail(options, "fetch_failed", combinedError(fetch), EXIT.git, baseContext);
                  base = undefined;
                }
              }

              if (base) {
                const verifyBase = git(["rev-parse", "--verify", remoteRef]);
                if (verifyBase.status !== 0) {
                  fail(
                    options,
                    "base_missing",
                    `${remote}/${base} is unavailable locally; run --preview or --apply to fetch it.`,
                    EXIT.git,
                    baseContext,
                  );
                } else {
                  const before = stdout(git(["rev-parse", "HEAD"]));
                  const remoteCommit = stdout(verifyBase);
                  const baseAlreadyIncluded = isAncestor(remoteRef, "HEAD");
                  const canFastForward = isAncestor("HEAD", remoteRef);
                  const resultContext = context(options, {
                    ...baseContext,
                    before,
                    remoteCommit,
                    dirty: state.entries.length > 0,
                  });

                  if (branch === base && baseAlreadyIncluded && before !== remoteCommit) {
                    fail(
                      options,
                      "blocked_ahead_default",
                      `Local ${base} contains commits that are not on ${remote}/${base}; start a feature branch or reconcile the default branch explicitly.`,
                      EXIT.blocked,
                      resultContext,
                    );
                  } else if (baseAlreadyIncluded) {
                    emit(options, {
                      ...resultContext,
                      status: "up_to_date",
                      message: `${branch} already contains the latest ${remote}/${base}.`,
                      after: before,
                      changed: false,
                    });
                  } else if (options.mode !== "apply") {
                    const operation = canFastForward ? "fast-forward" : options.strategy;
                    emit(options, {
                      ...resultContext,
                      status: canFastForward ? "would_fast_forward" : `would_${options.strategy}`,
                      message: `${branch} would ${operation} from ${remote}/${base}.`,
                      changed: false,
                    });
                  } else if (branch === base && !canFastForward) {
                    fail(
                      options,
                      "blocked_diverged_default",
                      `Local ${base} has diverged from ${remote}/${base}; refusing to create a merge on the default branch.`,
                      EXIT.blocked,
                      resultContext,
                    );
                  } else if (canFastForward) {
                    const merge = git(["merge", "--ff-only", remoteRef]);
                    if (merge.status !== 0) {
                      fail(options, "sync_failed", combinedError(merge), EXIT.git, resultContext);
                    } else {
                      const after = stdout(git(["rev-parse", "HEAD"]));
                      emit(options, {
                        ...resultContext,
                        status: "fast_forwarded",
                        message: `Fast-forwarded ${branch} to ${remote}/${base}.`,
                        after,
                        changed: after !== before,
                      });
                    }
                  } else if (options.strategy === "rebase" && branchIsPublished(branch, remote)) {
                    fail(
                      options,
                      "blocked_shared_rebase",
                      `Refusing to rebase published branch ${branch}; use the default merge strategy.`,
                      EXIT.blocked,
                      { ...resultContext, shared: true },
                    );
                  } else {
                    const operation = options.strategy;
                    const sync = operation === "merge"
                      ? git(["merge", "--no-edit", remoteRef])
                      : git(["rebase", remoteRef]);

                    if (sync.status === 0) {
                      const after = stdout(git(["rev-parse", "HEAD"]));
                      emit(options, {
                        ...resultContext,
                        status: operation === "merge" ? "merged" : "rebased",
                        message: `${operation === "merge" ? "Merged" : "Rebased"} ${remote}/${base} ${operation === "merge" ? "into" : "under"} ${branch}.`,
                        after,
                        changed: after !== before,
                      });
                    } else {
                      const conflictsResult = git(["diff", "--name-only", "--diff-filter=U"]);
                      const conflicts = stdout(conflictsResult).split("\n").filter(Boolean);
                      const abort = abortOperation(operation);
                      const afterAbort = git(["rev-parse", "HEAD"]);
                      if (abort.status !== 0 || afterAbort.status !== 0 || stdout(afterAbort) !== before) {
                        fail(
                          options,
                          "recovery_failed",
                          `The ${operation} failed and automatic recovery could not be verified. Inspect the repository before continuing.`,
                          EXIT.recovery,
                          { ...resultContext, conflicts, gitError: combinedError(sync) },
                        );
                      } else if (conflicts.length > 0) {
                        fail(
                          options,
                          "conflict_aborted",
                          `The ${operation} conflicted and was aborted; the branch was restored to its original commit.`,
                          EXIT.conflict,
                          { ...resultContext, conflicts, gitError: combinedError(sync), after: before },
                        );
                      } else {
                        fail(
                          options,
                          "sync_failed",
                          `The ${operation} was rejected and aborted; the branch was restored to its original commit.`,
                          EXIT.git,
                          { ...resultContext, gitError: combinedError(sync), after: before },
                        );
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
