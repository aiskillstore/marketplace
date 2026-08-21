# Verifying that builds actually run remotely (vs. cache)

A successful `--config=limrun` build is **not** proof that anything ran on the
remote workers. Bazel has two cache layers that make builds green with zero
remote work:

- **`remote cache hit`** — the action's output was fetched from Limrun's cache
  (over the tunnel). The action did **not** re-execute. The cache is shared
  across instances, so the *first* build of an unchanged target often hits cache
  for everything.
- **`action cache hit`** (note: no "remote") — Bazel's **local** action cache.
  Once outputs are materialized locally, repeat builds do nothing and never
  contact the tunnel. This is why a build can "succeed" after the Xcode instance
  and tunnel are gone — there was simply no work to do.

Read the `INFO: N processes:` summary line:
- `… M remote` → M actions **executed** on the workers (this is real RBE).
- `… remote cache hit` → fetched from the remote cache, not executed.
- `… action cache hit` / `internal` → local no-op.

A tell that work did run remotely: action stdout shows worker paths under
`/Users/<worker-user>/.../.rbe-<id>/runner/build/…/root/…`. Local execution
would show your own paths.

## Force and prove remote execution

**Positive — make a cache miss with the tunnel up, then look for `remote`:**
```
# lim xcode rbe running (background by default)
echo '// poke' >> path/to/Some.swift            # or any source edit
bazelisk --digest_function=sha256 build --config=limrun //App
# INFO: N processes: … M remote   ← M > 0 means it executed on the worker
```
Or skip the edit and ignore cached results for one run:
```
bazelisk --digest_function=sha256 build --config=limrun //App --noremote_accept_cached
```

**Decisive negative — make a cache miss with the tunnel DOWN; it must fail:**
```
lim xcode rbe --stop                            # close the tunnel + stop the stack
echo '// poke again' >> path/to/Some.swift
bazelisk --digest_function=sha256 build --config=limrun //App
# expect: connection error to 127.0.0.1:<port> / Remote Execution Failure
```
`--config=limrun` sets `--noremote_local_fallback`, so a cache miss with no
remote cannot silently fall back to local. If this fails, the build genuinely
depends on the remote. If it succeeds, it was a cache/no-op.
