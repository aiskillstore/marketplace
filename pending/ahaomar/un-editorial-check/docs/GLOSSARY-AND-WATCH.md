# Glossary import and watch mode

Two opt-in features added in Phase 7. Both are off by default: a run without
either flag behaves exactly as it did before.

- **Glossary import** — `--glossary <file>`, or a `glossary` key in
  `.un-editorial.json`. The reader imports their own terminology and the
  checker reports where the copy disagrees with it.
- **Watch mode** — `--watch`. The checker re-scans when a scanned file changes,
  so a writer sees the findings move as they type.

## Glossary import

### What a glossary is

A glossary is the reader's own house vocabulary. It is **not** a United Nations
requirement, and the checker never presents it as one. Every finding it raises
says so in the message, appears in its own report section, and is labelled with
the reader's file rather than with a rule document.

It answers one question, and only one: where does this draft disagree with the
terminology this organisation has decided on.

### The file format

One JSON object. Every key is optional except `glossaryVersion`, and at least
one term list must be non-empty.

```json
{
  "glossaryVersion": 1,
  "name": "House style",
  "requiredTerms": ["Sustainable Development Goal"],
  "forbiddenTerms": ["beneficiaries", "underprivileged"],
  "replacements": {
    "beneficiaries": "participants"
  }
}
```

| Key | Type | Meaning |
| --- | --- | --- |
| `glossaryVersion` | number | Must be `1`. Present so a future format is refused rather than misread. |
| `name` | string | Optional label for the glossary, used in every finding message. |
| `requiredTerms` | array of strings | Terms this copy must use. |
| `forbiddenTerms` | array of strings | Terms this copy must never use. |
| `replacements` | object | Preferred wording for a forbidden term. Guidance only; see below. |

### The two rules

| Rule | Fires when | Reports |
| --- | --- | --- |
| `UE-GL001` | A forbidden term appears in user-visible copy. | Every occurrence, at its line and column. |
| `UE-GL002` | A required term appears nowhere in a scanned file. | One finding for the file, anchored at line 1, column 1. |

`UE-GL002` judges the **file**, not the passage, because the promise a required
term makes is about the document as a whole: this document must call it *X*. A
file whose extracted copy never contains the term does not keep that promise. A
file that produced no copy spans at all is not judged, because nothing was read
to judge.

### Matching

Terms match **case-insensitively on whole words**, inside the copy spans the
extractors produced. Quoted material, cited titles, code spans, URLs and
comments are masked before any rule reads them, so they are structurally out of
reach — exactly as they are for every other rule in the tool.

A multi-word phrase must sit in one copy span. For the required-term presence
test, whitespace between the words is flexible, so a phrase broken across a line
is still recognised; this can under-report an absence but never invents a
position.

`<!-- ue:ignore UE-GL001 -->` inside a copy span silences that rule for that
span, as it does for any other rule. `ue:ignore all` silences both glossary
rules for the file.

### Honest provenance

This is the part that matters most, so it is stated explicitly.

A glossary finding carries the same five metadata fields as every other finding
— `source`, `profile`, `confidence`, `limitation`, `action` — and each one is
true for a user-supplied check:

- `source` names the mechanism — `user-supplied glossary (--glossary /
  config.glossary), not a United Nations rule` — and never a `rules/*.md`
  document and never the bundled United Nations baseline. It cannot name the
  reader's own path, because a catalogue entry is the same for every reader; the
  path travels in the finding's `glossary.file` and in its message.
- `profile` reads `glossary`, not `editorial baseline` and not a UN profile
  name.
- `lane` is `audit`, and the text report prints the finding under
  `OPTIONAL AUDIT - glossary`. It never appears under `EDITORIAL ERRORS`, and a
  reader cannot mistake it for a UN rule.
- The message itself ends with the words `this is the reader's house
  terminology, not a United Nations rule`.
- The PDF report carries an `Audit` row reading `glossary` alongside the five
  lane rows, and its Sources appendix names the file the reader wrote.

### The exit code

**A glossary finding never changes the exit code.** The rules are audit-lane,
which is the same treatment `--profile security` gets: a house convention is
not a United Nations requirement, so it must not decide whether a run claiming
United Nations compliance passes.

The audit lane is what does this, not the severity. Warning is the default a
reader sees, but re-grading a glossary rule to `error` through
`config.severities` still exits 0, and the finding is still reported in its
audit section. The same holds for the bundled audit profiles, which is why
this is the audit lane's contract rather than a glossary special case. The
invariant is locked at error severity in `tests/audit-lanes.mjs`, section 6b.

One asymmetry to know when you escalate an audit rule yourself: `config.severities`
does **not** reach a bundled audit. Use `config.rules.<id>.severity`, which is the
key the audit runner reads:

```json
{ "rules": { "UE-AX001": { "severity": "error" } } }
```

That raises the finding's severity without ever raising the exit code, which is
the point.

If a build should fail on your own terminology, assert on the output yourself:

```sh
un-editorial-check draft.md --glossary house.json --format json \
  | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{
      const gl=JSON.parse(s).findings.filter(f=>f.ruleId.startsWith("UE-GL"));
      process.exit(gl.length ? 1 : 0);})'
```

`config.severities` can re-grade a glossary rule and `config.rules` can switch
one off, exactly as for any other rule:

```json
{
  "glossary": "house.json",
  "rules": { "UE-GL002": { "enabled": false } }
}
```

### Never auto-rewritable

`--fix` never rewrites a glossary finding, on three independent grounds:

1. The rule ids are not on the `--fix` allow-list. The list stays exactly
   `UE-GR001, UE-GR002, UE-GR003, UE-NU002, UE-SP001`, and `planFixes` is
   fail-closed: a finding for any rule outside the list produces no edit even
   when a deterministic replacement is attached.
2. A glossary finding never passes a replacement. The `replacements` map is
   printed as guidance in the report and in the finding suggestion, and the
   report marks the finding `not --fix-able`.
3. Terminology is `NEVER_AUTO` in the remediation brief §8. `--fix` and
   `--fix --apply` leave a draft that disagrees with a glossary byte-for-byte
   unchanged.

So `--glossary` composes with `--fix`, and the fixable edits in a file are
still applied while the terminology findings stand.

### Failure is closed

Every problem below stops the run with exit code 2 and a message naming the
problem. A malformed glossary never degrades into a smaller rule set.

| Problem | Example message |
| --- | --- |
| File missing or unreadable | `glossary house.json cannot be read: ENOENT ...` |
| Not a regular file | `glossary house.json is not a regular file` |
| Invalid JSON | `glossary house.json is not valid JSON: ...` |
| Duplicate key | `glossary house.json contains duplicate keys: forbiddenTerms` |
| Unknown field | `glossary house.json contains unknown fields: spelling` |
| Missing or wrong version | `glossary house.json must declare glossaryVersion 1` |
| Term list not an array | `glossary house.json.forbiddenTerms must be an array` |
| Empty or non-string entry | `glossary house.json.forbiddenTerms[1] must be a non-empty string` |
| Term that can never match | `glossary house.json.forbiddenTerms[0] ("---") contains no letter, digit or underscore, so it can never match` |
| Both term lists empty | `glossary house.json declares no terms: requiredTerms and forbiddenTerms are both empty` |
| Replacement key not forbidden | `glossary house.json.replacements has a key that is not a forbidden term: "programme"` |
| Term listed twice | `glossary house.json lists "A" more than once` |
| Bad path in config | `config glossary must be a non-empty path to a glossary file` |
| Catalogue entry missing | `glossary rules are not registered: rules/catalogue.json has no UE-GL001 entry` |

The last row matters for a packaged install: if the catalogue entries for
`UE-GL001` and `UE-GL002` are absent, a glossary run refuses rather than
labelling a user-supplied finding with a United Nations rule file.

### The config key

```json
{
  "glossary": "editorial/house-glossary.json"
}
```

`--glossary` wins over the `glossary` key when both are given. The path is
resolved from the **working directory**, like `--profile` and `--config`, not
from the directory holding the config file. A relative path that only resolves
next to the config file is refused with exit 2 rather than silently missed.

`--glossary` is refused together with `--init`, `--self-test` and `--preview`,
since none of those reads the copy.

### Not in the source registry

A glossary has no URL, no publisher and no retrieval date, so it is never
recorded in `rules/sources.json`. That registry holds published, citable
sources with those fields, and inventing an entry for a local file would make
it a citation it is not. The provenance is recorded where it is honest instead:
in the finding message, in the `source` and `profile` fields, in the PDF report
block and its Sources appendix, and in a structured `glossary` object on every
JSON finding:

```json
{
  "ruleId": "UE-GL001",
  "audit": "glossary",
  "source": "user-supplied glossary (--glossary / config.glossary), not a United Nations rule",
  "profile": "glossary",
  "lane": "audit",
  "glossary": {
    "file": "house.json",
    "name": "House style",
    "kind": "forbidden",
    "term": "beneficiaries",
    "replacement": "participants"
  }
}
```

## Watch mode

### What it does

`--watch` prints the ordinary report, then re-scans whenever a scanned file
changes, and keeps running until you stop it with Ctrl+C.

### It never resolves an exit code

**Watch mode is a local interactive loop. It is not a continuous-integration
facility, and it never resolves an exit code.** A run that keeps going has no
result to hand a caller: a script waiting for its status would wait forever
rather than learn anything about the copy. Use an ordinary run in CI.

The first scan's exit code is discarded as well. The only way to stop the loop
is the keyboard, and the process then leaves with status `130` — the value a
shell reports for any interrupted command. It is deliberately not `0`, so an
interrupted watch can never be misread as a clean run.

Exit code 2 still applies, and applies **before** the first scan: a mistyped
flag, a missing path or an unreadable glossary stops the process instead of
starting a loop.

### Refused combinations

Each of these is defined by an exit code or by a single output document, which a
repeating loop cannot provide, so each is refused with exit code 2 and a
message naming the flag, rather than quietly ignored:

`--fix`, `--apply`, `--report`, `--quiet`, `--baseline`, `--json`,
`--format sarif`, `--self-test`, `--init`, `--preview`.

For example:

```
$ un-editorial-check draft.md --watch --quiet
un-editorial-check: --watch cannot be combined with --quiet: watch mode never
resolves an exit code, so a flag defined by one is refused rather than ignored
```

`--glossary` is **not** refused: both features are local and opt-in, and the two
compose. Watch mode also composes with `--profile` and `--config`.

### Reading the exit code from a watch run

Do not. The loop prints the report, never a status. If a script needs one, run
the checker without `--watch`, or read what the loop printed:

```sh
un-editorial-check draft.md --watch | tee /tmp/watch.log
grep -q 'EDITORIAL ERRORS' /tmp/watch.log && echo 'findings present'
```

### How it watches

`fs.watch` is the only dependency-free mechanism available at the project's
Node 18 floor, and it brings two caveats worth stating plainly.

**Directories are watched, not files.** An editor that saves through a temporary
file and a rename replaces the file's inode, and a watch on the old inode would
go quiet forever. The checker therefore watches the containing directory of
every input path, which sees the replacement. A directory input is watched as
itself.

**Recursive watching is not requested, on purpose.** `fs.watch` gained a
`recursive` option on macOS and Windows in Node 20 and is still unsupported on
Linux at the Node 18 floor, so asking for it would make the same command work on
one machine and fail on another. This is a compatibility decision, not an
oversight. The one consequence: a brand new nested sub-directory is noticed on
the next change inside it, not on the moment it is created.

**There is no polling loop.** Rescans are driven purely by filesystem events,
debounced so that the several events one editor save emits produce one scan
rather than a spin of them. An idle watcher is silent.

### Robustness

| Event | Behaviour |
| --- | --- |
| A scanned file is edited | One rescan after the debounce window. |
| A scanned file is deleted | The change is observed; the next scan reports what it can still read. |
| A file is replaced by a rename | Observed, because the directory is watched rather than the file. |
| A watched directory is removed | Survived without crashing; the watcher closes. |
| A path that does not exist yet | Refused before the loop starts, with `path not found` and exit 2. A *new file* appearing inside a directory that is already being watched is picked up on the next rescan. |
| A rescan throws | Reported as `rescan failed: ...`; the loop continues. |
| Ctrl+C | Every watcher is closed, then the process leaves with status 130. |

No watcher is leaked: stopping clears the pending debounce timer and closes
every handle, and stopping twice is safe.

### Stopping

Ctrl+C. That is the documented way out, and it is the only one: the loop has no
keypress handling, so nothing else ends it.
