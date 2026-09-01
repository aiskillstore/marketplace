# Generation contract

Every skill this factory creates must meet every rule in this file. The rule set is recursive: a generated skill that builds another skill passes this same contract on, unchanged, through its own copy of this file. No skill is exempt, the factory included.

## Layout

A skill is one directory whose name equals the frontmatter name. It holds SKILL.md at the root plus five support directories and a test directory at scripts/tests/, all present and all referenced from the SKILL.md body with load conditions: references/, assets/, examples/, scripts/, scripts/tests/, evals/. Generated skills also carry mise.toml and a CI workflow at .github/workflows/ci.yml. Relative paths stay close to the skill root: one subdirectory at most, as in assets/ci/ci.yml or scripts/tests/test_scripts.py.

## Frontmatter

The file opens with three dashes at byte 0 and the fence closes on its own line. Allowed top-level fields, and no others: name, description, license, compatibility, metadata, allowed-tools.

- name: 1 to 64 characters matching `^[a-z0-9][a-z0-9._-]*$`, equal to the directory name.
- description: quoted, 1 to 1024 characters, says what the skill does and when it applies, contains "Use when", and carries the keywords a user would type.
- license: MIT unless the user directs otherwise.
- metadata: author and a quoted version string.

## Body

Keep the body under 200 lines and the file under 100000 characters. Order: title, short intro, command grammar, numbered procedure, load conditions per directory, gotchas, completion criteria. The command grammar starts with help and adds the subcommands the skill needs. Write for the least capable executor:

- Numbered steps, one action and one observable result per step.
- The full plan visible upfront, never improvised midway.
- A mechanical check after each consequential step, with an explicit branch for failure.
- A stop-and-report branch wherever required information can be missing. Guessing is the failure mode, stopping is the contract.
- One default path per job, no menus of equal options.
- Progress written to an external log file after each step.
- Completion claims backed by fresh command output, never memory.

## Markdown layout

Every markdown file lays wrappable prose out as one physical line per block: a paragraph, or a list item plus its continuation lines, never holds an internal hard line break, and no maximum line length applies. Blank lines between elements stay exactly as markdown readability requires. YAML frontmatter, headings, table rows, code fences and their content, indented code, and blank lines are exempt. The writing lint enforces this rule on every markdown file.

## Examples

Every skill ships examples/ with at least one worked example per command in its grammar, and one more for the failure the skill is most likely to cause. An example is a complete run, not a fragment: the user's words, the executor's visible reply, every command with its real output and exit code, and every file the run created with its full contents. Each example names the guess it removes at the top and stays consistent with SKILL.md, so a rule change that outdates an example changes the example in the same commit. SKILL.md points at examples/ with a load condition, and the writing lint and structure validator both cover the directory.

## Code

Caps for every code file: 200 lines of code per file, 30 per function or class counting its own lines, block nesting depth 3 inside any function, measured from the test declaration in tests. No work markers, mocks, stubs, or placeholder branches. Real behavior only. Prefer the standard library.

Every script supports --help with usage, exit codes, and an example. Scripts take input from flags or stdin, never from a prompt. Data goes to stdout, diagnostics to stderr. Exit 0 on success, 1 on a failed check, 2 on bad usage. Reruns are safe.

## Tests, tasks, CI

Build order is fixed and test-first: mise.toml, then the CI workflow and the tests that pin the task graph, then script tests, then scripts, then docs, then evals. A behavior starts as a failing test. Local runs and remote CI use one command, `mise run ci`. Tests cover contracts users touch: flags, exit codes, file outputs, integration boundaries. Never private internals.

## Evals

evals/evals.json holds at least four realistic cases with prompts, expected output, and verifiable assertions. evals/trigger-queries.json holds positive and negative trigger queries, near misses included. A skill destined for the srinitude/skills registry also emits the registry eval artifact set described in references/eval-authoring.md: manifest.json, cases.json, trigger-cases.json, contract.md, rubric.md, speed-budgets.json, and source-lineage.json carrying real sha256 hashes of the source files.

## Reuse before building

Check for installed registry skills before writing anything new, starting with starting-point from https://github.com/srinitude/skills. Look for skills/starting-point/SKILL.md in the surrounding skills directory; the raw fallback is https://raw.githubusercontent.com/srinitude/skills/main/skills/starting-point/SKILL.md. Defer to an installed skill for the jobs its description names.

## Prohibited content

No file names an agent product, an agent harness, a company that ships one, or a model. Describe capabilities instead: run in a terminal, read the file, search the tree. Skills stay portable across executors, so nothing may assume host state beyond declared needs.
