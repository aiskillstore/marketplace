---
name: jsonlogic
description: "Work with JsonLogic business rules — the JSON-based conditional-logic format at jsonlogic.com. Use whenever the user wants to turn a business requirement into a JsonLogic rule, needs an existing JsonLogic expression explained or debugged, asks whether a rule is valid, wants to execute JsonLogic in a specific language (JavaScript, TypeScript, Python, Ruby, Java, PHP, Go, C#, others), is choosing or comparing a JsonLogic library, or is integrating JsonLogic into an application. Trigger on mentions of JsonLogic, json-logic, JSON rule objects shaped like {\"var\": ...}, or requests to express conditions and business rules as portable JSON. Do not use for general programming tasks that don't involve the JsonLogic format."
---

# JsonLogic

A skill for work with JsonLogic.

[JsonLogic](https://jsonlogic.com) is a small, portable format for expressing conditional
logic as JSON. 

The JsonLogic standard is the universal rule format and defines its semantics. A rule at this level is language-agnostic. See [references/jsonlogic.md](references/jsonlogic.md) and
[references/operations.md](references/operations.md).

A specific library is the code that executes JsonLogic in a particular language, such as **json-logic-js** for **JavaScript** or **json-logic-rb** for **Ruby**. Libraries can differ in the operations they support, as well as their API shape and error handling.

## Running JsonLogic

### Library

If a specific implementation is named, such as **json-logic-js**, use that exact implementation. A language name alone, such as **“in Python”**, means use the library for that language from [references/libraries.md](references/libraries.md). If neither a library nor a language is named, default to [scripts/jsonlogic.rb](scripts/jsonlogic.rb).


### Support

A
rule can be valid JsonLogic and still be unsupported by the selected library or its
current version. Flag unsupported operations. Never rewrite a valid JsonLogic rule just because one library can't run it. Say which level the limitation is at and offer the real options: 
- a custom operation
- a different library if operation is not supported in specific implementation
- logic change

## Playground artifact

Whenever a concrete rule is in play (created, explained, fixed, or executed), render it
live instead of only describing it in text: seed [assets/playground.html](assets/playground.html)
with that rule and data, then publish it with the Artifact tool. This runs under whoever
installed the skill — each publish call creates the artifact under that person's own
account, so it works the same way for every installer with no sharing step needed. The
artifact is private by default, and publishing here just updates the same URL, so
there's no separate decision to check on each time.

Two files, one static and one templated: [assets/jsonlogic-core.js](assets/jsonlogic-core.js)
is the JsonLogic interpreter — it never changes between invocations, so publish it once
per conversation (via the Artifact tool's `files` param) and never again.
[assets/playground.html](assets/playground.html) is the thin page with the placeholders
below; it's the only one that gets re-templated and republished on every change.

1. Read `assets/playground.html`. It's a fixed-design page (rule, live result, data) —
   never hand-edit its CSS/layout; only the placeholders below change per invocation.
2. Replace `__INITIAL_RULE__` and `__INITIAL_DATA__` with the rule/data objects, each as
   a JS/JSON literal (the output of `JSON.stringify(...)`, valid to drop in as-is). No
   concrete rule yet → leave both untouched, the template falls back to a built-in
   default.
3. Replace `__CURRENT_LANG_MODE__` with `"ruby"` when the target language is Ruby,
   otherwise `"jsonlogic"` (every other language shown here follows JsonLogic's own
   truthy/falsy rules; only Ruby's diverge). No language decided yet → leave it
   untouched, falls back to `"jsonlogic"`.
4. Replace `__VERIFY_LIB_LABEL__` with the same library **Running JsonLogic → Library**
   (above) resolved to for this task — this is what the page's "Verify in chat" button
   names when asking to confirm against the real implementation, so it must match, not
   default to Ruby just because that's this file's own fallback:
   - Ruby → `"json-logic-rb (scripts/jsonlogic.rb)"`
   - JavaScript / TypeScript → `"json-logic-js"`
   - Python → `"maykin-json-logic-py"`
   - Java → `"json-logic-java"`
   - PHP → `"json-logic-php (jwadhams/json-logic-php)"`
   - Go → `"diegoholiveira/jsonlogic"`
   - C# / .NET → `"JsonLogic (json-everything)"`
   - Any other language from [references/libraries.md](references/libraries.md) → that library's name as given there.
   No language/library decided yet → leave it untouched, falls back to Ruby's
   `"json-logic-rb (scripts/jsonlogic.rb)"`, matching this skill's own default.
5. Write the result to a working file and publish it — the **first** time in a
   conversation: Artifact tool, `action:"publish"`, that file's path,
   `title:"JSON Logic Playground"`, `icon:"code"`, plus
   `files:{"jsonlogic-core.js":"assets/jsonlogic-core.js"}` so the interpreter ships
   alongside it unmodified.
6. Whenever the rule, data, or language changes later in the same conversation, redo
   steps 1–4 with the new values and publish again with the **same file path** and the
   same `url` — but omit `files` this time, since `jsonlogic-core.js` never changes and
   an omitted file is kept as-is. This updates the same artifact in place instead of
   creating a new one.

Skip this for requests that never produce a concrete rule (e.g. "what does `missing`
do").

The user can edit the rule/data directly in the artifact to test things — that's the
point, it recalculates live. Never republish over those manual edits. Only republish
when the user asks for a new or changed rule/condition in chat.

## Writing JsonLogic

**Step 1: Get the data shape**

Always ask how to get the data’s field names before creating a new rule. Present this as choice. Use the client’s structured question mechanism, such as buttons or a picker, when available. Otherwise, present the choices as plain text.

Question: "How should I get your data's field names?". Offer three options:
  - Option **Schema** — "I'll paste a schema — JSON Schema, OpenAPI, whatever format."
  - Option **Sample data** — "I'll paste a real JSON example."
  - Option **Just guess** — "Infer field names from my description."

The dialog only picks the method. The actual answer still comes as a normal follow-up
message, not inside the dialog itself.

**Step 2: Build the expression**

Write the rule using the field names from Step 1.

 Before writing a new rule, check [references/operations.md](references/operations.md)
for the full supported list and [examples/](examples/) for worked patterns. For real
upstream test cases per operator, see [references/tests/](references/tests/). 

#### Customization
Don’t expect JsonLogic to include every specialized operation. It’s intentionally small and not a programming language. It will never do everything. However JsonLogic support extentions. Before you reach for a custom solution, see if you can express your logic using the supported operations (built-in). Often, a simple change in perspective is all you need to get the job done with what's already there.


**Step 3: Explain what it does**

Cover:

- the requirement being encoded
- the operations used and what each does
- the expected input shape
- what the rule returns
- edge cases worth flagging (missing fields, type coercion, empty arrays)

Skip items that don't apply.


### Missing information

If business condition unclear – you should ask what the rule should check, but don't ask about things you can already resolve from context.

## Validate JsonLogic

Checking shape against [references/jsonlogic.md](references/jsonlogic.md),
[references/operations.md](references/operations.md), or
[scripts/validate_skill.rb](scripts/validate_skill.rb) only confirms the rule is
shaped like JsonLogic.

Real validation means writing test cases and running them through
[scripts/jsonlogic.rb](scripts/jsonlogic.rb). See
[references/testing.md](references/testing.md) for how to pick them. Cover the normal
case and the boundary, but weight it toward edge cases especially: missing fields,
empty arrays, unexpected types. A rule with no test cases isn't safe to hand off —
there's no way to guarantee it behaves as expected.

For the individual operators a rule uses, check
[references/tests/](references/tests/) first — real upstream cases for both the core
spec (`core.json`) and the community extensions (`community/`), bundled locally.
Reuse a matching case as a sanity check before writing new ones from scratch; these
test the operators in isolation, not the rule's actual business logic, so still add
rule-specific cases on top.


## Debug JsonLogic

**Step 1: Reproduce it**

Use **Running JsonLogic** with the rule and data as reported. 
See the actual output yourself before diagnosing anything.

**Step 2: Find the actual cause**

Lead with the real cause, not just the symptom — common culprits: type coercion,
missing fields, operator misuse.

**Step 3: Fix and verify**

Give the corrected rule, then re-run Step 1 with the fix to confirm the new output is
right. If the fix needs to be handed back as runnable code, continue to **Execute
JsonLogic** below.



## After any

### Verify running

See **Running JsonLogic** above to actually execute the rule. If there's no data
example on hand yet, create a representative one first. Verifying needs real input to
run against, not just a description of what the rule should do.

### Flag concerns
Don't claim JsonLogic is "safe" just because it's JSON.


## Reference files

Read these as needed rather than loading everything up front:

- [references/jsonlogic.md](references/jsonlogic.md) — core
  semantics: truthiness, type coercion, `var` path resolution, how missing data
  behaves, what "compliant" means.
- [references/operations.md](references/operations.md) — every standard operation:
  syntax plus behavior notes worth knowing (short-circuiting, three-argument
  comparisons, `reduce`'s `current`/`accumulator`, etc).
- [references/libraries.md](references/libraries.md) —
  the library landscape across languages: what was found, what was verified, what
  wasn't. Read before writing any language-specific code, including for languages not
  listed — check there first rather than assuming none exists.
- [references/testing.md](references/testing.md) — how to verify a rule or
  implementation, and how to be honest about what "verified" means in a given answer.
- [references/tests/](references/tests/) — bundled upstream test cases (core spec +
  community extensions) for validating individual operators.
- [examples/](examples/) — worked examples:
  - [basic-rules.json](examples/basic-rules.json)
  - [conditions.json](examples/conditions.json)
