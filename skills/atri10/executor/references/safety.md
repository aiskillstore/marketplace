# Secret Hygiene

`.executor/` is git-ignored by default. The user may remove that ignore and
commit it — the execution record is valuable enough that some teams will
want it in history. **Write every Executor artifact as though it will be
public**, because it may become public without you being asked.

`docs/executor/` is tracked from the start. It is already public to anyone
with the repo.

## Never written into any Executor artifact

- Credentials, passwords, API keys, access tokens, refresh tokens
- Private keys, certificates, signing material
- Session cookies, bearer headers, authorization headers
- Database connection strings containing credentials
- Cloud account identifiers paired with access material
- Personal data beyond what the work genuinely requires
- Raw `.env` contents, raw secret-manager output, raw credential files

## What to write instead

A redacted existence statement plus a safe pointer:

```markdown
Auth uses a service-account token read from `AUTH_TOKEN` at startup;
the value lives in the deployment's secret store. Not recorded here.
```

```markdown
Reproduced with a local `.env` containing `DATABASE_URL` (value redacted).
Shape: `postgres://<user>:<pass>@<host>:5432/<db>`.
```

The reader learns what exists, where it comes from, and what shape it has.
Nothing recoverable is written down.

## The four live risks

**1. Implementer reports.** An implementer debugging an auth failure pastes
the failing request — headers included — into its report. The report is a
file in `.executor/`. Dispatch prompts carry the no-secrets rule; reports
get scanned before handoff.

**2. Review diffs.** `exec-review-package` captures the literal diff. If a
task accidentally committed a secret, the diff now contains it in a second
place. The scan covers `reviews/diffs/` for exactly this reason — and a
secret found in a diff means the secret is also in git history, which is a
bigger problem than the diff.

**3. Brainstorm session state.** Mockups and event logs can capture whatever
was on screen, including real data pulled in to make a mockup realistic. Use
synthetic data in mockups.

**4. Tooling runtime state.** A tool that serves or persists something on the
agent's behalf generates its own secrets — session keys, tokens, cookies,
signed URLs — and writes them beside its output by default. Those files are
operational state, not artifacts, and they **never** go inside `docs/executor/`
or `.executor/`; they belong in a runtime directory outside the repository.
The scan will not save you here: a freshly generated hex key matches no
known credential prefix. The visual companion is the worked example — its
`--project-dir` takes only `content/` and `events`, while `server-info`,
the log, and `.last-token` stay outside the repo.

## The required scan

Run before any handoff, before committing `.executor/` if the user chooses
to, and before marking an initiative complete:

```bash
../scripts/exec-scan-secrets                 # scans both stores
../scripts/exec-scan-secrets .executor/INIT-0004
```

The script flags high-signal patterns: private key headers, common token
prefixes (`sk-`, `ghp_`, `gho_`, `AKIA`, `xox[baprs]-`), `Authorization:`
headers with values, connection strings with embedded credentials,
assignments to names containing `secret`/`token`/`password`/`apikey` with a
literal value, and `.env`-shaped blocks.

It reports file and line. It **never prints the matched value** — printing
it would copy the secret into your context and the transcript.

## When a secret has already landed

1. **Do not** print, echo, or copy the value.
2. Tell the human immediately: which file, which line, what kind of
   credential.
3. If it is only in `.executor/` (git-ignored, never committed): the file is
   the only copy — the human decides whether to redact in place or discard
   the artifact.
4. If it reached git: this is credential rotation, not a file edit. The
   human rotates the credential. History rewriting is their call, never
   yours, and never something you do unasked.
5. Record the incident in the initiative's rulings log as a redacted
   statement: what kind of credential, which artifact, what was done. Never
   the value.

## Committing the execution store

If the user wants `.executor/` tracked:

1. Run the scan across the whole store and resolve every finding first.
2. Remove `.executor/.gitignore` (or narrow it to `brainstorm/*/state/`,
   which holds transient server state with no review value).
3. From then on, the scan runs before every commit that touches
   `.executor/` — the store is now public surface.

Do not make this change on the user's behalf. Offer it; they decide.
