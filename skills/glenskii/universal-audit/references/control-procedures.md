# Control Procedures - Practical Checks per Family

The catalog (spec Appendix A) defines objectives and minimum PASS evidence. This file
maps each control family to concrete, safe, read-only checks an auditor or agent can run.
Active tests marked ⚠ require Rules of Engagement authorization first.

Evidence rule for everything below: record what you ran, where, when, against which
commit/build, and the sanitized result in the evidence ledger. A check you did not run
is UNVERIFIED, not PASS.

## GOV - Governance, scope, threat model

- **GOV-SCOPE-001**: `git rev-parse HEAD`, build metadata, deployed version endpoint or
  artifact hash. PASS only when manifest identity and artifact identity agree.
- **GOV-ROE-001**: written authorization on file covering targets, methods, limits.
- **GOV-THREAT-001**: existing threat model, or run the spec 6.5 fallback: assets, actors,
  entry points, boundaries, top-5 abuse scenarios, existing controls.
- **GOV-RISK-001 / GOV-TRACE-001**: risk register fields complete; sample 3–5 material
  requirements and trace each to code and a test.

## SEC - Authentication, authorization, sessions

- Locate the auth middleware/decorators; confirm every protected route passes through it
  (grep route definitions against middleware application - list exceptions).
- **SEC-AUTHZ-001/002**: find object-fetch code paths; verify ownership/tenant scope is in
  the query or checked server-side, not inferred from the client. ⚠ Runtime: with two
  authorized test accounts, attempt cross-account object access.
- **SEC-SESS-001/002**: inspect cookie flags (Secure, HttpOnly, SameSite), token TTLs,
  and invalidation on logout/password change. ⚠ Runtime: reuse a logged-out token.
- **SEC-AUTHN-002/003, SEC-MFA-001**: password hashing algorithm and parameters
  (argon2/bcrypt/scrypt), reset-token expiry and single-use, rate limiting config,
  non-disclosing error messages.

## SEC - Input, injection, browser, API, secrets, crypto

- **SEC-INPUT/INJECT-001**: grep for query construction (`f"SELECT`, string concat into
  SQL/shell/paths/templates); confirm parameterization or safe APIs. Check upload
  handling for type/size/path constraints.
- **SEC-XSS-001**: identify render paths for untrusted content; confirm contextual
  encoding or a sanitizer with safe config.
- **SEC-SSRF-001**: any user-supplied URL fetched server-side needs parse → scheme check →
  IP-literal rejection → DNS-resolve check → allowlist. Blocklists fail.
- **SEC-WEB/CORS-001**: fetch representative routes; record CSP, HSTS, X-Frame-Options /
  frame-ancestors, cookie attributes, CORS origins and credentials mode.
- **SEC-API-001/002, SEC-HOOK-001**: route table vs auth matrix; pagination bounds,
  idempotency keys, quota config; webhook signature + timestamp verification code.
- **SEC-SECRET-001/002**: run a secret scanner over history where feasible; validate hits.
  Check client bundles and logs for keys. Confirm rotation is possible without deploy.
- **SEC-CRYPTO-001**: library inventory (no custom primitives), key storage, key rotation.

## ARC / CODE - Architecture and code correctness

- **ARC-BOUND-001 / ARC-STATE-001**: draw the actual data flow from code; compare with
  claimed architecture. Identify who owns each piece of critical state.
- **ARC-FAIL-001**: every external call site has a timeout and a defined failure behavior.
- **ARC-CPLX-001**: dependency graph and component sizes; flag circular imports,
  duplicate pathways, abstraction without a second consumer.
- **CODE-CORR-001**: locate the money/quantity/permission calculations; check invariants
  and their tests (accepted, rejected, boundary).
- **CODE-ERR-001**: empty catch blocks, swallowed promises, broad `except:`; sensitive
  data in error output.
- **CODE-TIME-001 / CODE-CONC-001**: naive datetime usage, timezone assumptions, locale
  parsing; shared mutable state, check-then-act races, idempotency of handlers.
- **CODE-MOD-001**: nonexistent API references (verify imports resolve and methods exist),
  placeholder branches, tests that assert the implementation rather than the requirement.

## SUP / CICD / INF - Supply chain, pipeline, infrastructure

- **SUP-DEP-001/002**: lockfile present and consistent; run SCA (`npm audit`, `pip-audit`,
  `pnpm audit`); triage each material hit for reachability before accepting severity.
- **SUP-LIC-001**: license inventory vs intended distribution model.
- **SUP-BUILD-001**: registries, install scripts, build plugins, artifact signing.
- **CICD-***: branch protection, required checks, secret handling in workflows, runner
  isolation, artifact-to-source traceability, deploy health checks, rollback path tested.
- **INF-***: exposed ports/services, TLS config (protocol, cert chain, expiry), IAM roles
  vs least privilege, prod/dev isolation, IaC drift, patch status of runtimes.

## DATA / PRIV - Data and privacy

- **DATA-SCHEMA-001**: constraints in the schema (NOT NULL, FK, UNIQUE, CHECK) for
  critical invariants - not just app-layer validation. ⚠ attempt an invalid insert in a
  test environment.
- **DATA-TXN/MIG-001**: multi-step operations wrapped in transactions; migration
  up/down tested; rollback evidence.
- **DATA-QUERY-001**: EXPLAIN critical queries at representative volume; find N+1 loops.
- **PRIV-***: data map vs actual collection (code, telemetry, vendors); retention jobs
  actually run; export/deletion workflows exercised end-to-end; published privacy notice
  compared with observed behavior.

## REL / OPS / BAK / DR - Reliability, operations, recovery

- **REL-***: timeouts, bounded retries with backoff, queue poison-message handling,
  graceful startup/shutdown. ⚠ induced-delay and failure tests in a safe environment.
- **OPS-LOG-001**: sample logs across success/failure/security events; check for secrets
  and PII in logs; correlation IDs.
- **OPS-ALERT/IR-001**: alert rules exist, route to an owner, and fired recently or were
  tested; incident runbook current.
- **BAK-***: backup jobs succeed, scope covers all state, access-controlled and encrypted.
  **BAK-REST-001 requires restoration evidence** - a configured backup is not a verified
  recovery. ⚠ restore into an isolated environment and measure RPO/RTO.
- **DR-DEP-001**: recovery accounts for identity, keys, DNS, and vendor dependencies.

## PERF / COST

- **PERF-BASE-001**: measure critical-journey latency and resource use against the exact
  build; record environment. Bundle size for web frontends.
- **PERF-CAP-001 / PERF-DEGRADE-001**: ⚠ authorized representative load only; otherwise
  operational evidence or UNVERIFIED. Never load-test production without written RoE.
- **COST-ABUSE-001**: user-triggerable expensive work (model calls, exports, emails, media
  processing) has quotas/budgets; test the abuse path with limits in place.

## QA / A11Y / UX / I18N

- **QA-***: risk-to-test mapping; run the suite against the audited commit; check for
  skipped/quarantined tests influencing the release decision; compatibility matrix.
- **A11Y-***: manual keyboard walk of critical journeys (visible focus, logical order),
  semantic inspection (names, roles, labels, status announcements), contrast measurement,
  automated scan (axe or equivalent) as supporting evidence only.
- **UX-CRIT/TRUST-001**: walk critical journeys as a target user; verify consequential
  actions communicate scope and consequence, and that errors are recoverable.
- **I18N-***: boundary tests with long strings, non-Latin scripts, RTL where declared,
  plural rules, date/number formats per supported locale.

## DESK / MOB / MOD / DOC / RET / ADM

- **DESK-***: clean-machine install/update/uninstall; signing verified; update channel
  integrity (⚠ attempt a tampered update in a test rig); IPC and protocol-handler input
  handling; local secret storage (OS keychain, not plaintext).
- **MOB-***: manifest permissions vs need; secure storage APIs; lifecycle interruption
  and deep-link tests on device or emulator.
- **MOD-***: model output validated before consequential actions; ⚠ authorized prompt
  injection tests through untrusted content channels; tenant/data boundaries in prompt
  assembly and retrieval; evaluation dataset with thresholds and current results;
  fallback and budget behavior on provider failure.
- **DOC-***: execute the setup docs on a clean environment or verify by sampling;
  runbooks match the current release.
- **RET-***: account closure, export, deletion lifecycle test; retired endpoints and DNS
  actually gone.
- **ADM-***: enumerate admin accounts and effective permissions; privileged actions
  produce protected, attributable audit events (retrieve one to prove it); break-glass
  procedure exists and is monitored.
