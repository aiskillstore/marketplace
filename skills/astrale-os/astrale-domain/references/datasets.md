# Demo datasets

Read when authoring or updating the Datasets a Domain ships under `tests/`.

A Dataset is a readable example graph for Studio, not a production seed or a substitute for runtime
tests. Dataset Policy evaluation does not prove credentials or installed callable authority.

## Story

- Choose a small coherent story in the product's language.
- One example per idea. Add records only when they explain a relationship, lifecycle, or access rule.
- Show relevant active/terminal states and optional relationships present and absent.
- Split unrelated stories into separate Datasets rather than enforcing a node count.

## Names

- Use meaningful product names rather than numbered placeholders.
- A card shows only name and class. The name says what the object is and which one:
  *Review landing page copy*, not *Task 1*.
- Use stable readable fixture IDs where useful. These are local to the Dataset, not canonical IDs
  assigned to application data by a live Kernel.

## Policies

- For each demonstrated Policy: one pair that passes, one near miss that fails for its own reason.
- `anyOf`: one pair per branch. `allOf` / `exists`: one proof, one with a single condition missing.
  `repeat { min, max }`: chains of `min`, `max`, `max + 1`.
- Subjects are `Identity` descendants. Include an outsider when relevant, and a concrete descendant
  when illustrating polymorphic access.

## Schema

Cover the Classes, Edges, and state distinctions needed for the story. Do not turn one demo into an
exhaustive test matrix. Do not add foreign-ID properties for a relationship already owned by an Edge.

## Code

```ts
import { defineDataset } from '@astrale-os/sdk/testing'
import { schema } from '#schema'

export default defineDataset(schema, {
  id: 'demo',
  title: 'Website launch',
  graph({ classes: { Project, Task, task_in_project }, node, edge }) {
    const launch = node(Project, { id: 'website-launch', props: { name: 'Website launch' } })
    const review = node(Task, { id: 'review-copy', props: { name: 'Review landing page copy' } })
    edge(task_in_project, review, launch)
    return { launch, review }
  },
})
```

This illustrative Schema owns `Project`, `Task`, and `task_in_project`; supply the actual Classes'
required properties, including inherited ones. Reference the module lazily from `astrale.config.ts`
with `tests: tests({ datasets: [dataset('./tests/datasets/demo.ts')] })`. Build and deployment do not
import the Dataset or install its facts.

- Admission checks properties, concrete Classes, endpoint compatibility, and duplicate IDs. It is
  not proof of business dates, lifecycle eligibility, or live cardinality enforcement.
- Endpoints must be Dataset nodes. For a local or direct-dependency Core/Class/Function/Policy node,
  use the graph callback's `ref(domain.core.nodes.inbox)` (or the appropriate definition). This
  retains its reference identity; copying properties into `node(...)` does not. Dataset refs are
  resolved from Schema, not fetched from a live installation.
- Returned nodes become named variables for inspection.
- Verify extraction with the project's SDK; inspect the Studio Tests tab when changing its demo.
