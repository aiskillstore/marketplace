---
name: clojure-review
description: Review Clojure and ClojureScript code changes for compliance with Metabase coding standards, style violations, and code quality issues. Use when reviewing pull requests or diffs containing Clojure/ClojureScript code.
allowed-tools: Read, Grep, Bash, Glob
---

# Clojure Code Review Skill
<!-- Included from: .claude/skills/_shared/clojure-style-guide.md -->
# Metabase Clojure Style Guide

This guide covers Clojure and ClojureScript coding conventions for Metabase. See also: `CLOJURE_STYLE_GUIDE.adoc` for the Community Clojure Style Guide.

## Naming Conventions

**General Naming:**

- Acceptable abbreviations: `acc`, `i`, `pred`, `coll`, `n`, `s`, `k`, `f`
- Use `kebab-case` for all variables, functions, and constants

**Function Naming:**

- Pure functions should be nouns describing the value they return (e.g., `age` not `calculate-age` or `get-age`)
- Functions with side effects must end with `!`
- Don't repeat namespace alias in function names

**Destructuring:**

- Map destructuring should use kebab-case local bindings even if the map uses `snake_case` keys

## Documentation Standards

**Docstrings:**

- Every public var in `src` or `enterprise/backend/src` must have docstring
- Format using Markdown conventions
- Reference other vars with `[[other-var]]` not backticks

**Comments:**

- `TODO` format: `;; TODO (Name M/D/YY) -- description`

## Code Organization

**Visibility:**

- Make everything `^:private` unless it is used elsewhere
- Try to organize namespaces to avoid `declare` (put public functions near the end)

**Size and Structure:**

- Break up functions > 20 lines
- Lines ≤ 120 characters
- No blank lines within definition forms (except pairwise `let`/`cond`)

## Style Conventions

**Keywords and Metadata:**

- Prefer namespaced keywords for internal use: `:query-type/normal` not `:normal`
- Tag variables with `:arglists` metadata if they're functions but wouldn't otherwise have it

## Tests

**Organization:**

- Break large tests into separate `deftest` forms for logically separate test cases
- Test names should end in `-test` or `-test-<number>`

**Performance:**

- Mark pure function tests `^:parallel`

## Modules

**OSS Modules:**

- Follow `metabase.<module>.*` pattern
- Source in `src/metabase/<module>/`

**Enterprise Modules:**

- Follow `metabase-enterprise.<module>.*` pattern
- Source in `enterprise/backend/src/metabase_enterprise/<module>/`

**Module Structure:**

- REST API endpoints go in `<module>.api` or `<module>.api.*` namespaces
- Put module public API in `<module>.core` using Potemkin imports
- Put Toucan models in `<module>.models.*`
- Put settings in `<module>.settings`
- Put schemas in `<module>.schema`

**Module Linters:**

- Do not cheat module linters with `:clj-kondo/ignore [:metabase/modules]`

## REST API Endpoints

**Required Elements:**

- All new endpoints must have response schemas (`:- <schema>` after route string)
- All endpoints need Malli schemas for parameters (detailed and complete)
- All new REST API endpoints MUST HAVE TESTS

**Naming Conventions:**

- Query parameters use kebab-case
- Request bodies use `snake_case`
- Routes use singular nouns (e.g., `/api/dashboard/:id`)

**Behavior:**

- `GET` endpoints should not have side effects (except analytics)
- `defendpoint` forms should be small wrappers around Toucan model code

## MBQL (Metabase Query Language)

**Restrictions:**

- No raw MBQL introspection outside of `lib`, `lib-be`, or `query-processor` modules
- Use Lib and MBQL 5 in new source code; avoid legacy MBQL

## Database and Models

**Naming:**

- Model names and table names should be singular nouns
- Application database uses `snake_case` identifiers

**Best Practices:**

- Use `t2/select-one-fn` instead of fetching entire rows for one column
- Put correct behavior in Toucan methods, not separate helper functions

## Drivers

**Documentation:**

- New driver multimethods must be mentioned in `docs/developers-guide/driver-changelog.md`

**Implementation:**

- Driver implementations should pass `driver` argument to other driver multimethods
- Don't hardcode driver names in implementations
- Minimize logic inside `read-column-thunk` in JDBC-based drivers

## Miscellaneous

**Examples:**

- Example data should be bird-themed if possible

**Linter Suppressions:**

- Use proper format for kondo suppressions
- No `#_:clj-kondo/ignore` (keyword form)

**Configurable Options:**

- Don't define configurable options that can only be set with environment variables
- Use `:internal` `defsetting` instead

<!-- End: .claude/skills/_shared/clojure-style-guide.md -->
<!-- Included from: .claude/skills/_shared/clojure-commands.md -->
## Linting and Formatting

- **Lint PR:** `./bin/mage kondo-updated master` (or whatever target branch)
  - Call the command one time at the beginning, record the results, then work through the problems one at a time.
  - If the solution is obvious, then please apply the fix. Otherwise skip it.
  - If you fix all the issues (and verify by rerunning the kondo-updated command):
    - commit the change with a succinct and descriptive commit message
- **Lint File:** `./bin/mage kondo <file or files>`
  - Use the linter as a way to know that you are adhering to conventions in place in the codebase
- **Lint Changes:** `./bin/mage kondo-updated HEAD`
- **Format:** `./bin/mage cljfmt-files [path]`

## Testing

- **Run a test:** `./bin/mage run-tests namespace/test-name`
- **Run all tests in a namespace:** `./bin/mage run-tests namespace`
- **Run all tests for a module:** `./bin/mage run-tests test/metabase/notification` Because the module lives in that directory.

Note: the `./bin/mage run-tests` command accepts multiple args, so you can pass
`./bin/mage run-tests namespace/test-name namespace/other-test namespace/third-test`
to run 3 tests, or
`./bin/mage run-tests test/metabase/module1 test/metabase/module2` to run 2 modules.

## Code Readability

- **Check Code Readability:** `./bin/mage -check-readable <file> [line-number]`
  - Run after every change to Clojure code
  - Check specific line first, then entire file if readable

## REPL Usage

> **Note:** If you have `clojure-mcp` tools available (check for tools like `clojure_eval`),
> **always prefer those over `./bin/mage -repl`**. The MCP tools provide better integration,
> richer feedback, and avoid shell escaping issues. Only use `./bin/mage -repl` as a fallback
> when clojure-mcp is not available.

- **Evaluating Clojure Code:** `./bin/mage -repl '<code>'`
  - See "Sending Code to the REPL" section for more details

### Sending Code to the REPL

- Send code to the metabase process REPL using: `./bin/mage -repl '(+ 1 1)'` where `(+ 1 1)` is your Clojure code.
  - See `./bin/mage -repl -h` for more details.
  - If the Metabase backend is not running, you'll see an error message with instructions on how to start it.

#### Working with Files and Namespaces

1. **Load a file and call functions with fully qualified names**:

To call `your.namespace/your-function` on `arg1` and `arg2`:

```
./bin/mage -repl --namespace your.namespace '(your-function arg1 arg2)'
```

DO NOT use "require", "load-file" etc in the code string argument.

#### Understanding the Response

The `./bin/mage -repl` command returns three separate, independent outputs:

- `value`: The return value of the last expression (best for data structures)
- `stdout`: Any printed output from `println` etc. (best for messages)
- `stderr`: Any error messages (best for warnings and errors)

Example call:

```bash
./bin/mage -repl '(println "Hello, world!") '\''({0 1, 1 3, 2 0, 3 2} {0 2, 1 0, 2 3, 3 1})'
```

Example response:

```
ns: user
session: 32a35206-871c-4553-9bc9-f49491173d1c
value:  ({0 1, 1 3, 2 0, 3 2} {0 2, 1 0, 2 3, 3 1})
stdout:  Hello, world!
stderr:
```

For effective REPL usage:

- Return data structures as function return values
- Use `println` for human-readable messages
- Print errors to stderr

<!-- End: .claude/skills/_shared/clojure-commands.md -->
## Review guidelines

**What to flag:**

- Check compliance with the Metabase Clojure style guide (included above)
- If `CLOJURE_STYLE_GUIDE.adoc` exists in the working directory, also check compliance with the community Clojure style guide
- Flag all style guide violations

**What NOT to post:**

- Do not post comments congratulating someone for trivial changes or for following style guidelines
- Do not post comments confirming things "look good" or telling them they did something correctly
- Only post comments about style violations or potential issues

Example bad code review comments to avoid:

> This TODO comment is properly formatted with author and date - nice work!

> Good addition of limit 1 to the query - this makes the test more efficient without changing its behavior.

> The kondo ignore comment is appropriately placed here

> Test name properly ends with -test as required by the style guide.

**Special cases:**

- Do not post comments about missing parentheses (these will be caught by the linter)

## Quick review checklist

Use this to scan through changes efficiently:

### Naming

- [ ] Descriptive names (no `tbl`, `zs'`)
- [ ] Pure functions named as nouns describing their return value
- [ ] `kebab-case` for all variables and functions
- [ ] Side-effect functions end with `!`
- [ ] No namespace-alias repetition in function names

### Documentation

- [ ] Public vars in `src` or `enterprise/backend/src` have useful docstrings
- [ ] Docstrings use Markdown conventions
- [ ] References use `[[other-var]]` not backticks
- [ ] `TODO` comments include author and date: `;; TODO (Name 1/1/25) -- description`

### Code Organization

- [ ] Everything `^:private` unless used elsewhere
- [ ] No `declare` when avoidable (public functions near end)
- [ ] Functions under 20 lines when possible
- [ ] No blank lines within definition forms (except pairwise constructs in `let`/`cond`)
- [ ] Lines ≤ 120 characters

### Tests

- [ ] Separate `deftest` forms for distinct test cases
- [ ] Pure tests marked `^:parallel`
- [ ] Test names end in `-test` or `-test-<number>`

### Modules

- [ ] Correct module patterns (OSS: `metabase.<module>.*`, EE: `metabase-enterprise.<module>.*`)
- [ ] API endpoints in `<module>.api` namespaces
- [ ] Public API in `<module>.core` with Potemkin
- [ ] No cheating module linters with `:clj-kondo/ignore [:metabase/modules]`

### REST API

- [ ] Response schemas present (`:- <schema>`)
- [ ] Query params use kebab-case, bodies use `snake_case`
- [ ] Routes use singular nouns (e.g., `/api/dashboard/:id`)
- [ ] `GET` has no side effects (except analytics)
- [ ] Malli schemas detailed and complete
- [ ] All new endpoints have tests

### MBQL

- [ ] No raw MBQL manipulation outside `lib`, `lib-be`, or `query-processor` modules
- [ ] Uses Lib and MBQL 5, not legacy MBQL

### Database

- [ ] Model and table names are singular nouns
- [ ] Uses `t2/select-one-fn` instead of selecting full rows for one column
- [ ] Logic in Toucan methods, not helper functions

### Drivers

- [ ] New multimethods documented in `docs/developers-guide/driver-changelog.md`
- [ ] Passes `driver` argument to other driver methods (no hardcoded driver names)
- [ ] Minimal logic in `read-column-thunk`

### Miscellaneous

- [ ] Example data is bird-themed when possible
- [ ] Kondo linter suppressions use proper format (not `#_:clj-kondo/ignore` keyword form)

## Pattern matching table

Quick scan for common issues:

| Pattern                                      | Issue                                                       |
| -------------------------------------------- | ----------------------------------------------------------- |
| `calculate-age`, `get-user`                  | Pure functions should be nouns: `age`, `user`               |
| `update-db`, `save-model`                    | Missing `!` for side effects: `update-db!`, `save-model!`   |
| `snake_case_var`                             | Should use kebab-case                                       |
| Public var without docstring                 | Add docstring explaining purpose                            |
| `;; TODO fix this`                           | Missing author/date: `;; TODO (Name 1/1/25) -- description` |
| `(defn foo ...)` in namespace used elsewhere | Should be `(defn ^:private foo ...)`                        |
| Function > 20 lines                          | Consider breaking up into smaller functions                 |
| `/api/dashboards/:id`                        | Use singular: `/api/dashboard/:id`                          |
| Query params with `snake_case`               | Use kebab-case for query params                             |
| New API endpoint without tests               | Add tests for the endpoint                                  |

## Feedback format examples

**For style violations:**

> This pure function should be named as a noun describing its return value. Consider `user` instead of `get-user`.

**For missing documentation:**

> This public var needs a docstring explaining its purpose, inputs, and outputs.

**For organization issues:**

> This function is only used in this namespace, so it should be marked `^:private`.

**For API conventions:**

> Query parameters should use kebab-case. Change `user_id` to `user-id`.
