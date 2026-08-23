# New project defaults

> When scaffolding a new project (or hardening a young one), reach for these by
> default. Pick once, lock it in repo config, stop bikeshedding.

These are opinionated defaults, not laws. Override per project when there is a
real reason, and say why. But absent a reason, take the default so the decision
costs nothing.

## Formatters: opinionated, zero-config, locked in

Auto-formatters end the entire category of style argument. The good ones have no
options worth tuning; you run them and accept the output. Run the formatter in
`--check` mode in CI so unformatted code cannot merge, and format on save
locally.

One formatter per language, committed to repo config, no per-developer variation.

## Linters: one default, stick with it

Same principle as formatters: pick the strong linter for the language, run it
with warnings-as-errors in CI, and do not let everyone bring their own.

## The per-language picks

| Language | Formatter | Linter | Type / build check |
|---|---|---|---|
| Rust | `rustfmt` (`cargo fmt`) | `clippy` (`-D warnings`) | `cargo build` / `cargo test` |
| Go | `gofmt` / `goimports` | `staticcheck` (or `golangci-lint`) + `go vet` | `go build`, `go test -race` |
| TypeScript | `oxfmt` | `oxlint --type-aware` (+ anti-slop) | `tsc --noEmit` |
| Python | `ruff format` | `ruff check` | `mypy --strict` (or `pyright`) |

Notes:

- **Rust and Go** ship their formatter in the toolchain. `rustfmt` and `gofmt`
  are the whole point: opinionated, no config, just do what they say.
- **TypeScript: `oxfmt` + `oxlint`** (the oxc toolchain, Rust-based). `oxfmt
  --check .` formats, `oxlint --type-aware .` lints, one `.oxlintrc.json`,
  committed. `tsc --noEmit` still runs separately for type-checking. Do not also
  run Prettier, ESLint, or Biome. **Ban the type-system escape hatches by
  default:** `no-explicit-any` (no `any`), `no-non-null-assertion` (no `!`),
  `no-floating-promises`, and the vendored
  [anti-slop](https://github.com/dmmulroy/anti-slop) plugin (`as` needs a
  `// SAFETY:` comment; no `unknown` in signatures; no `typeof` narrowing; no
  module mocks). **In React projects, also ban the `useEffect` and
  `useLayoutEffect` imports in product code** (`no-restricted-imports`);
  external-system effects live in one allow-listed wrapper directory. See
  [`../languages/typescript.md`](../languages/typescript.md) for the config
  blocks.
- **Python: `ruff` for both** format and lint (it replaces black, isort, flake8,
  pyupgrade, and more). One fast tool, one config block in `pyproject.toml`.
  Pair it with a strict type checker (`mypy --strict` or `pyright`) in CI.

CI must run the type/build check too: a green test suite with type errors or lint
failures is not green.

## Pre-commit: run the CI checks locally, from one source of truth

Catch failures before they reach CI by running the same checks in a git
pre-commit hook. The rule that keeps this from rotting: **the hook and CI call
the same command.** Define the check suite once, in one recipe, and have both
invoke it, so they can never drift.

1. **One recipe is the suite.** Put the full check sequence in a single target:
   a `just` recipe, a `Makefile` target, or a `scripts/check.sh`. It runs, in
   order: format `--check`, lint, type/build check, tests, and the agent-rules
   whole-tree check (see below).

   ```sh
   # justfile
   check:
       cargo fmt --check        # or: oxfmt --check . / ruff format --check . / gofmt -l .
       cargo clippy -- -D warnings   # or: oxlint --type-aware . / ruff check . / staticcheck ./...
       cargo test               # or: tsc --noEmit && vitest / mypy --strict && pytest / go test -race ./...
       # plus the agent-rules whole-tree check, if you run one
   ```

   A single `just check` (or equivalent) that runs fmt-check, lint, and tests is
   the pattern to reach for.

2. **CI calls the recipe.** The CI workflow runs `just check` (not a re-listed
   copy of the commands). Now CI and local cannot disagree about what "passing"
   means.

3. **The pre-commit hook calls the recipe.** Install a hook that runs the same
   thing. Pick a manager and commit its config so every clone gets the hook:
   - **lefthook** (language-agnostic, fast, parallel) is a good default for any
     project.
   - **pre-commit** (the Python framework) if the project is Python-centric.
   - **husky + lint-staged** for JS/TS monorepos that want staged-file scoping.
   - Or a plain committed `scripts/hooks/pre-commit` that runs the recipe, wired
     up via `core.hooksPath`.

4. **Keep it fast enough not to bypass.** If the full suite is slow, scope the
   heavy steps to changed files in the hook (lint-staged / lefthook globs) while
   CI always runs the complete suite on everything. A hook people routinely skip
   with `--no-verify` is worse than a fast one they keep. CI is the real backstop;
   the hook is the fast feedback loop.

## Set up a deterministic agent-rules layer

Adopt a tool that enforces project conventions at the moment a coding agent
edits, rather than leaving them in a doc the agent may not reload. The category
to reach for gives agents deterministic, testable rules (plus, ideally, a
learned-notes memory for past incidents), so a convention is enforced in the
edit loop instead of merely hoped for.

What to look for in such a tool:

- **Structural matchers, not just text.** Rules that can target real syntax
  (a regex, or better a tree-sitter AST query) so they match the construct, not
  an incidental string.
- **Edit-time actions.** A rule should be able to pass through, inject guidance,
  interrupt a write, or rewrite a command, handing the agent a correction
  message so it self-fixes in the loop.
- **A whole-tree check for CI.** The single most important property. The
  edit-time hooks only fire when an agent edits; a whole-tree check runs the same
  rules over the entire repo with no agent in the loop, so the rules gate every
  commit and every PR regardless of who or what wrote the code.

**Always wire the whole-tree check into CI and the pre-commit recipe.** That is
what makes the rules *authoritative* instead of agent-dependent. Put it in the
same one-recipe check suite as the formatter and linter (see Pre-commit above),
so CI and local enforce identical rules and cannot drift. Without the check in
CI, an agent rule is only a suggestion; with it, the rule is a gate.

**Layering the three enforcement layers.** A linter/compiler, an agent-rules
layer, and an agentic review gate overlap; put each rule at the *lowest layer
that can express it faithfully* rather than duplicating it.

- A real **linter or compiler is the enforcer of record wherever it has the
  rule.** It runs for everyone (editor, pre-commit, and the CI merge gate)
  regardless of who or what wrote the code, it is the authoritative gate that
  blocks merge, and it usually autofixes. Banning `any`/`!`/`as` (oxlint + anti-slop), ignored
  errors (Go `errcheck`), bare `except:` (ruff `E722`), `.unwrap()` in prod (a
  clippy lint), and `validate* -> Result<()>` (clippy `unnecessary_wraps`) all
  belong here. If a lint rule exists, turn it on and let it be the gate.
- **The agent-rules layer is precise too, and adds what a linter cannot.** With
  tree-sitter matchers it can target real syntax nodes, not just text (for
  example a function-definition node, or a TS `any` type node). What sets it
  apart from a linter is *when and what*: it intercepts a coding agent at
  write-time and hands back a correction message so the agent self-fixes in the
  loop, and it expresses conventions no linter ships, like
  do-not-edit-this-directory, command rewrites, and lessons from past incidents.
  So for a rule a linter already gates, the agent-rules layer is a precise
  agent-time front line rather than a duplicate gate; for a structural rule no
  linter offers, a tree-sitter query makes it a first-class enforcer on its own
  (paired with the whole-tree check in CI).
- **The agentic review gate is the judgment layer.** The principles here that
  need a human-level read (is this the right abstraction, does this boundary
  actually parse, is the error model coherent, does the architecture doc still
  match) live as reviewers, not as regex or lint rules.

So: where a linter owns the rule, keep it as the CI gate (it autofixes and shows
in the editor) and use the agent-rules layer as the precise agent-time front
line; where no linter can express the rule, a tree-sitter query plus the
whole-tree check in CI is a first-class, authoritative gate; and the review gate
covers the judgment calls. With the whole-tree check wired in, the agent-rules
layer is universal too, so do not duplicate one rule across layers: put it where
it is expressed best (a native linter rule, or a tree-sitter query for structural
rules linters do not offer), and let that layer gate.

## Set up an agentic review gate

Adopt an agentic code-review gate: single-concern AI reviewers run as fitness
functions over a changeset, both locally before a PR and in CI, and aggregate
into one merge gate. Adopt it so the conventions above are reviewed on every
changeset, not just hoped for.

Keep a reviewer registry in the repo, run the review in the local loop before a
PR, and wire the review check into CI as a required gate. Reviewers are governed
policy: author them deliberately and keep them under CODEOWNERS so reviewer
definitions cannot change without human review. The gate fails closed: a reviewer
that cannot produce a valid verdict blocks, never silently passes.

## CLI binary distribution

When a project ships a CLI binary, distribute it as a checksummed, multi-platform
release:

- **Tag-triggered release.** Pushing a `vX.Y.Z` tag fires a release workflow that
  builds the platform matrix and opens a (draft) GitHub Release. A pre-release
  suffix (`v0.2.0-rc.1`) ships as a prerelease. The binary's version comes from
  the tag, not a hand-bumped constant in source.
- **Prebuilt multi-platform binaries** attached to the release: Linux x86_64 and
  aarch64 (glibc and musl), macOS Intel and Apple silicon, Windows x86_64.
- **Each archive bundles** the binary plus `README`, `LICENSE`, and `NOTICE`.
- **`checksums.txt` with SHA-256** for every archive, published alongside them.
- **Install scripts** that detect the platform, download the matching archive and
  `checksums.txt`, verify the hash, and place the binary on `PATH`:
  - `curl -sSfL .../install.sh | bash` (macOS/Linux)
  - `irm .../install.ps1 | iex` (Windows PowerShell)
  - Support version pinning and a custom install dir.
- **Fail closed on any checksum mismatch.** The install must abort, never install
  unverified bytes. Pin this behavior with a test.
- Not published to a language registry (crates.io/npm) unless that is an explicit
  goal; a release is just a tag plus artifacts.

## Community and governance files

At the repo root:

- **LICENSE** for the code.
- **NOTICE** stating the copyright and, if docs use a different license, the
  dual-licensing split and where each applies. Note that third-party/vendored
  material keeps its own license.
- **CODE_OF_CONDUCT.md** with conduct guidelines and a contact.
- **SECURITY.md** with a private reporting path (GitHub private vulnerability
  reporting or a security email), the kinds of reports that are useful, and an
  explicit **threat model** (what the project does and does not defend against).
- **CONTRIBUTING.md** with the dev loop and the release runbook (the build
  matrix, version derivation, any self-review pin to bump).

Under `.github/`:

- `ISSUE_TEMPLATE/` (bug report, feature request, `config.yml`),
  `PULL_REQUEST_TEMPLATE.md`, `dependabot.yml`.
- Workflows: `ci.yml` (fmt-check, lint, type-check, test), `release.yml`
  (tag-triggered, the matrix above), `security.yml` (dependency/audit scanning),
  and `installers.yml` if you ship install scripts (smoke-test them against
  published releases on a schedule, not in PR CI).

**On the license choice specifically:** there are exactly two options. Pick one;
treat every other license as noise.

- **AGPL-3.0-or-later** for strong copyleft, including the network-use clause.
  When using it, dual-license documentation as **CC-BY-SA-4.0** via the NOTICE.
- **Apache-2.0** for a permissive license with an explicit patent grant.

Do not reach for MIT, BSD, GPL, or anything else; they add nothing over these
two here. **The agent must ask the human which of the two during bootstrap** and
must not assume one. This is a deliberate decision the human
owns; everything else in this checklist is a default the agent can just take.
