# Knowledge-graph queries

`cargo-ai context graph get` returns the typed knowledge graph derived from every markdown/MDX file in the context repo. Pipe it through `jq` to slice it.

> Field names below (`nodes`, `slug`, `frontmatter`, `links`, etc.) are illustrative — run `cargo-ai context graph get | jq '. | keys'` once at the top of your session to confirm the exact shape for your workspace before scripting against it.

## List every node

```bash
cargo-ai context graph get | jq -r '.nodes[].slug' | sort
```

## Count entries per domain

```bash
cargo-ai context graph get \
  | jq -r '.nodes[].slug' \
  | awk -F/ '{print $1}' \
  | sort | uniq -c | sort -rn
```

## Find every persona

```bash
cargo-ai context graph get \
  | jq '.nodes[] | select(.slug | startswith("persona/")) | {slug, title: .frontmatter.title}'
```

## Find personas that link to a specific play

```bash
cargo-ai context graph get \
  | jq --arg target "play/funding-triggered-outbound" '
      .nodes[]
      | select(.slug | startswith("persona/"))
      | select((.links // []) | index($target))
      | .slug'
```

## Find dangling cross-references

Nodes referencing a `domain/slug` that doesn't exist in the graph:

```bash
cargo-ai context graph get | jq '
  . as $g
  | ($g.nodes | map(.slug)) as $slugs
  | $g.nodes[]
  | .slug as $from
  | (.links // [])[]
  | select(. as $t | ($slugs | index($t)) | not)
  | {from: $from, missing: .}
'
```

## Find plays with no proof attached

```bash
cargo-ai context graph get | jq '
  .nodes[]
  | select(.slug | startswith("play/"))
  | select(
      ((.links // []) | map(select(startswith("proof/"))) | length) == 0
    )
  | .slug
'
```

## Find objections with no proof point

Same pattern as plays, scoped to objections:

```bash
cargo-ai context graph get | jq '
  .nodes[]
  | select(.slug | startswith("objection/"))
  | select(
      ((.links // []) | map(select(startswith("proof/"))) | length) == 0
    )
  | {slug, title: .frontmatter.title}
'
```

## Show inbound references to a node

Which files cross-ref `proof/14-day-time-to-first-workflow`?

```bash
cargo-ai context graph get | jq --arg target "proof/14-day-time-to-first-workflow" '
  .nodes[]
  | select((.links // []) | index($target))
  | .slug
'
```

## Audit frontmatter completeness

Files missing `title` or `description`:

```bash
cargo-ai context graph get | jq '
  .nodes[]
  | select((.frontmatter.title // "") == "" or (.frontmatter.description // "") == "")
  | .slug
'
```

## Snapshot the graph to disk

Useful before a bulk edit so you can diff before/after:

```bash
cargo-ai context graph get > /tmp/graph.before.json
# ...make edits via context runtime write/edit...
cargo-ai context graph get > /tmp/graph.after.json
diff <(jq -r '.nodes[].slug' /tmp/graph.before.json | sort) \
     <(jq -r '.nodes[].slug' /tmp/graph.after.json | sort)
```
