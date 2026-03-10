# JSON to LLM Context Rules

## Goal

Turn JSON trees into short readable summaries that are easier for LLMs to consume than pretty JSON.

## Output Modes

- `sectioned`: default; best for LLM prompting because sections are easier to reference
- `flat`: simpler bullet list; useful when section headers feel too verbose for tiny payloads

## Safety Controls

- `strict`: keep more literal structure and stop dropping default-false flags
- `preserve`: force-keep keys or dotted paths such as `status`, `profile.email`, or `orders`
- `expand collections`: add sample sub-bullets under list summaries
- `expand details`: add nested sub-bullets under detail summaries
- `expand all`: expand both details and collections
- `show-paths`: add `[@path]` markers so the model can trace each rendered line back to source locations

## Core Heuristics

- Group root output into:
  - `Summary` for status, contact, timestamps, and other headline facts
  - `Details` for nested objects or extra attributes
  - `Collections` for arrays and list-like fields
- Remove noise:
  - `null`
  - empty strings
  - empty arrays
  - empty objects
  - selected default-false flags such as `deleted=false`
- Preserve high-signal fields:
  - `id`
  - `name`, `title`, `label`, `username`
  - `status`
  - timestamps
  - relationship IDs
  - contact fields such as `email`
- Prefer readable phrases:
  - `active=true` → `active`
  - `email + email_verified=true` → `email x (verified)`
- Summarize arrays:
  - small scalar arrays → report line with total and values
  - object arrays → report line with count, top status distribution, and a few examples
- Summarize nested objects:
  - prefer report-style fragments when possible
  - avoid dumping raw nested JSON unless the structure is too irregular

## Entity Header Heuristics

Prefer:

```text
Type[id]: name
```

Type selection order:
1. explicit `type`
2. parent key name
3. conservative built-in hints such as `User`, `Order`, `Event`
4. fallback `Record`

Name selection order:
1. `name`
2. `title`
3. `label`
4. `username`
5. `email`

## Array Examples

Input:

```json
{"orders":[
  {"id":"A12","status":"paid","total":42},
  {"id":"A13","status":"pending","total":18},
  {"id":"A14","status":"paid","total":9}
]}
```

Readable:

```text
Context

Details
- Meta: count: 3.

Collections
- Orders: 3 total; statuses: paid 2, pending 1; examples: Order[A12] with status: paid and total: 42, and Order[A13] with status: pending and total: 18.
```

## Tuning

- Lower `--max-samples` to reduce token usage further
- Lower `--max-depth` for deeply nested payloads
- Lower `--max-string-len` when text blobs dominate output
- Raise `--max-depth` only when nested relationship details are important
