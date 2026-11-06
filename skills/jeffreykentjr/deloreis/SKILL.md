---
name: deloreis
description: Keep fiction and worldbuilding consistent with De Lore Is. Use when maintaining lore for AI-assisted novels, series bibles, campaigns, competing story ideas, retcons, or checks on generated additions to a fictional world. Record and query persistent lore through local MCP tools. Also use for explicit De Lore Is, DLI, or deloreis project requests.
license: MIT
---

# Authoring with De Lore Is

Use De Lore Is when a writing task needs an established world to check against:
continuing a novel, adding lore, revising an account, or exploring another version
of a story. It records structured lore and checks the rules supplied for that
world. Keep the manuscript and prose references in their existing files.

For installation and a complete first check, read
[First session](references/first-session.md). The skill does not install the
runtime. Start with a small section of the user's notes, not a whole-book
migration. Ask which details are established and which are ideas. Propose rules
instead of assuming, for example, that every character can have only one home.

Use the `author.*` tools to add lore. Read every returned finding. Repair
mechanical input errors; resolve continuity findings using the user's rulings
rather than change lore just to make a check pass. Do not edit `.dli` as an agent
authoring a world. People can write `.dli` directly and import or check it;
the store is the source of truth for an authoring session.

Register `deloreis mcp --project <directory>` with the client, then call its
tools. If they are not available, use the first-session setup instead of
simulating a stored world in the chat. The server
also offers newline-delimited JSON through `deloreis serve --project
<directory>`. Contract 2.0.0 is the served contract. `--tools all` advertises
specialist tools beyond the default profile. Use installed help and `tools/list`
for the exact arguments rather than guessing tool schemas.

## Authoring loop

1. `author.open` a scope and retain its returned workspace ID and digest.
   When fencing writes, pass the current digest as `expected_digest`; read the
   updated `workspace_digest` from the result or `author.status` after each
   change rather than reuse an earlier one.
2. Use typed operations such as `author.add_entity`, `author.add_fact`,
   `author.add_relation`, `author.add_event`, and `author.add_before`.
   Declare single-valued predicates with `author.declare_functional` and
   changing predicates with `author.declare_inertial` where appropriate.
3. Check the project's source/decision index before choosing a new decision ID;
   reuse an ID only for that same ruling. For a ruling, use `author.record_decision` and cite that decision with
   `{"kind":"cited","decisions":["d-0001"],"state":"ratified"}`. An
   unruled proposal can use `{"kind":"proposed","origin":"session-name"}`.
   Unknown citations are errors and cannot make a claim certain.
4. Inspect `author.check`, `author.findings`, `author.query`, and `author.why`.
   `author.diff` shows staged consequences. Check the returned findings even
   if the call itself succeeded.
5. `author.materialize` checks and commits staged changes. It refuses errors.
   `author.discard` rejects staged work. Keep returned root hashes and claim
   IDs when they are useful for review or later retcons.

`author.record_decision`, `author.defeat`, and standing operations can update
the store directly; do not assume that every mutation is only staged. Use the
user's agreed rulings and the host's review policy before these calls; do not
silently turn an idea into an accepted account. The
caller supplies attribution, decision state, and review policy. The server
checks references and continuity, not who is authorized to rule.

## Use it during a writing task

- **Continue a chapter:** query the people, places, and established facts relevant
  to the scene. After drafting, propose the new factual claims through the tools,
  check them, and show the user any conflicts. Review extracted claims against
  the prose; a clean check covers those claims and recorded rules.
- **Brainstorm:** keep alternatives proposed or in a hypothetical fork. Use
  `author.open_question` and `author.add_option` for a choice between accounts;
  `author.add_hypothesis` and `author.suppose` support hypothetical exploration. Accepting
  a note into the store does not by itself make it established canon. Query
  established claims with `layer: "certain"`. Use `layer: "possible"` or `"all"`
  to inspect open accounts as well; those layers also include certain claims.
  A known claim can evaluate dead, but there is no `dead` query layer: inspect
  its blocked support with `author.why`.
- **Revise:** inspect `author.diff` and `author.why`, then record the user's chosen
  new ruling before calling `author.defeat` on the earlier support. Retain the old claim ID. Use a named
  branch for a separate durable version; branch tools are advertised with `--tools all`.
- **Track change within the story:** record event-anchored states and query
  `author.as_of`. A character changing allegiance is not necessarily a retcon.
  Declare known event ordering; leave unknown ordering open.

New workspaces see current committed lore; an already-open workspace retains its
base. Open a fresh workspace when another session has changed the accepted
world. The host application owns approval, access control, and concurrent-write
policy. Do not describe DLI as general-purpose agent memory or infer a character's
knowledge from world facts.

For CLI reads and wiki export, see [Read and export](references/first-session.md#read-and-export).

## Core tools

The default MCP profile keeps 29 common tools. It advertises `dli.check`, `dli.name.check`, and:

- Workspace and inspection: `author.open`, `author.status`, `author.check`,
  `author.findings`, `author.predicates`, `author.query`, `author.why`,
  `author.as_of`, `author.diff`, and `author.entity_candidates`.
- Lore: `author.add_entity`, `author.add_fact`, `author.add_relation`,
  `author.add_event`, `author.add_before`, `author.add_state`,
  `author.declare_functional`, and `author.declare_inertial`.
- Rulings and exploration: `author.record_decision`, `author.open_question`,
  `author.add_option`, `author.defeat`, `author.set_standing`,
  `author.add_hypothesis`, and `author.suppose`.
- Acceptance: `author.materialize` and `author.discard`.

`author.add_option` can name a fact that follows if that option is chosen,
using its optional `implies` field. Give options distinct names and add them
before materializing their question.

Use `tools/list` for the exact schemas. `author.query` returns claim IDs when
available; `author.why` explains supporting and blocked paths. For a retcon,
`author.defeat` takes a claim ID, a new decision, and the decision it defeats.
Defeating the retcon can restore the original support. Use `--tools all` for
named branches, specialist authoring, corpus import/export, and other tools.

The [Holmes casebook](https://jeffreykentjr.github.io/deloreis/casebook-01.html) is produced from a
replay that exercises the server. The [concept glossary](https://jeffreykentjr.github.io/deloreis/concepts.html) explains
the terms. DLI checks structured claims, not prose, and a functional conflict
is detected only for a predicate declared single-valued.

## Reading rendered lore

These are supported readable `.dli` forms. Agents author through the tools
instead of editing these snippets into the project:

```dli
person wren "Wren" proposed session
```

```dli
functional home proposed session
```

```dli
home(wren, thornfield) ratified d-0001
```
