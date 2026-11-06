# First session

Install the runtime from crates.io or use a Linux x86-64 or macOS ARM release archive:

```sh
cargo install deloreis --locked
```

Cargo installation needs Rust 1.96 or later. Binaries and checksums:
https://github.com/jeffreykentjr/deloreis/releases

Put the archive's `bin/deloreis`, or Cargo's binary directory, on `PATH`.
Confirm `deloreis --help` runs. These registration examples use a POSIX shell.

Create a fresh disposable project for this demonstration; do not add its sample
characters and decisions to an existing story. Register its local MCP server
with Claude Code:

```sh
deloreis init my-story
cd my-story
claude mcp add --scope project deloreis -- "$(command -v deloreis)" mcp --project "$PWD"
```

Reload the client's MCP configuration. Other clients can run the same server
command, pointing `--project` at the directory containing `deloreis.toml`.
No hosted DLI account or model API is needed by the server. The writing
assistant still uses its own model.

## Establish one detail, then check a proposed change

Call `author.open` with `{"scope":"world"}`. In every following argument,
replace `WORKSPACE` with the returned workspace ID.

Call `author.record_decision`:

```json
{"workspace":"WORKSPACE","decision":"d-0001"}
```

For each object below call `author.add_entity`:

```json
{"workspace":"WORKSPACE","kind":"person","id":"wren","name":"Wren","provenance":{"kind":"proposed","origin":"first-session"}}
```

```json
{"workspace":"WORKSPACE","kind":"place","id":"thornfield","name":"Thornfield","provenance":{"kind":"proposed","origin":"first-session"}}
```

```json
{"workspace":"WORKSPACE","kind":"place","id":"ashby","name":"Ashby","provenance":{"kind":"proposed","origin":"first-session"}}
```

For this example the writer has chosen to allow only one home. Call
`author.declare_functional`:

```json
{"workspace":"WORKSPACE","pred":"home","provenance":{"kind":"proposed","origin":"first-session"}}
```

Call `author.add_fact`, then `author.materialize` with the workspace ID:

```json
{"workspace":"WORKSPACE","entity":"wren","key":"home","value":"thornfield","provenance":{"kind":"cited","decisions":["d-0001"],"state":"ratified"}}
```

Now call `author.record_decision` with decision `d-0002` and stage another
`author.add_fact`:

```json
{"workspace":"WORKSPACE","entity":"wren","key":"home","value":"ashby","provenance":{"kind":"cited","decisions":["d-0002"],"state":"ratified"}}
```

Run `author.check`. The conflicting settled home claims produce findings;
`author.materialize` refuses the conflicting change. Show the findings and
supporting rulings to the user. They can reject the addition, revise a ruling,
or change the model. Call `author.discard` to discard staged changes. Decisions
were recorded directly: discard does not undo `d-0002`.

For real notes, choose constraints with the writer and retain a source index
mapping decision names to passages, for example in a `sources.md` file
beside the manuscript. Do not mechanically declare every field
single-valued. A current home and an earlier home may need event-anchored states.

## Read and export

For specialist tools, replace the existing registration and reload the client:

```sh
claude mcp remove --scope project deloreis
claude mcp add --scope project deloreis -- "$(command -v deloreis)" mcp --project "$PWD" --tools all
```


Use MCP queries for a stored project. CLI `check` and `query` take `.dli` files;
they do not query the project store. To get text from the project, start MCP
with `--tools all`, call `dli.corpus.export` with
`{"document":"world","format":"rendered"}`, and save the returned rendered
documents as `.dli` files. An export is a separate operation from editing notes.

Continue with sourced, reproducible examples:
https://jeffreykentjr.github.io/deloreis/casebook-01.html

Bring your own notes and make a wiki:
https://jeffreykentjr.github.io/deloreis/guide-your-world.html

For the single-document demonstration above, save the rendered world as
`world.dli`. Export that saved text as a linked Markdown wiki with
`deloreis export --profile static-wiki --corpus world.dli` and follow the
wiki-writing steps in the notes guide above. Edit the source lore and re-export;
editing wiki pages does not update the store.
