# Runtime

Read for Functions, Queries, Mutations, Rules, and optional native HTTP routes. Schema owns callable
input/output, receiver, auth, and Policy; runtime implements that admitted contract.

## Owners and composition

- Put Actions and Workflows together in `functions/`; keep `defineAction` and `defineWorkflow` distinct.
  Register one exact `functions` collection; do not maintain parallel handler registries or path dispatch.
- One callable, Query, or Mutation per owner file; keep its projection helpers there unless reused.
  Use business submodules and curated layer facades, not a generic repository or decoder layer.
- Name files by intent: `read-project.ts`, `list-project-services.ts`, `archive-project.ts`, not
  `record.ts`, `get.ts`, or a catch-all `queries.ts`. A longer descriptive name beats an ambiguous one.
- Import the aggregate Schema as a type. Use the invocation's resolved `domain` for Classes/Properties;
  focused error, value, and StateMachine facades may supply runtime-safe values.
- An Action owns one semantic asynchronous operation. A Workflow owns multiple observations/effects,
  each in a stable `step.run`; pure Rules need neither steps nor dependency injection.
- The inline Workflow runner is not durable replay, retry, compensation, or exactly-once execution.
  Steps need portable results; do not return Clients, responses, or other live capabilities between steps.

## Authority and inputs

- Use public SDK bindings/executors, not hand-built endpoints, tokens, or routing. Transport is
  transparent to business code; consult `debugging.md` only when diagnosing discovery or invocation.
- Default `query`, `mutate`, and `kernel` use the installed Domain authority (`self`). Select
  `graph.caller` or `kernel.caller` to act for the incoming caller. Dependencies have no default
  `invoke`: choose `dependencies.alias.caller.invoke` or `.self.invoke`. In both modes the Domain signs
  the outgoing callback and remains its authenticated principal; `caller` carries the incoming caller
  Identity, `self` makes the Domain its own caller. There is no `union` mode: run Domain-owned work as
  `self` and work on the user's behalf as `caller`.
- Protected callables receive authenticated `caller` evidence and bound `kernel` sessions.
  An unauthenticated anonymous invocation has null `kernel`, `graph`, and `dependencies`.
- Use the handler's `kernel` session for admitted Kernel capabilities outside graph operations;
  keep reusable graph operations on Query/Mutation executors. `executeQuery(client, ...)` and
  `executeMutation(client, ...)` remain lower-level APIs for consumers that already own a Client.
- `self` is the admitted receiver's `NodeId`; static/top-level callables have no receiver. The SDK validates
  callable input before the handler and output afterward; do not repeat parsing or implement role checks there.
- For business references, default to canonical record IDs in public inputs and outputs for simplicity.
  Pass `NodeId` directly to Queries/Mutations where accepted. Use `Path` only when the developer explicitly
  requests it or a called API contract requires it; convert at that call boundary, without maintaining
  parallel path/id APIs.
- Use resolved definitions or their refs where accepted, not reconstructed locator strings. Position
  matters: a Query Class source selects instances, while a projected Class Path names the definition node.

## Queries: observe and project

- Name the business observation, not an authorization promise: `listProjectServices`, not
  `listAuthorizedServices`. `listServicesByOwner` is valid for an explicit business filter, not implicit access control.
- Author `defineQuery<typeof schema>()((domain) => ({ build, project, ... }))` with canonical `Query`
  builders from `@astrale-os/sdk/query`. Read once and project that result rather than fetching every node again.
- Schema-admitted properties need no second validator. If projection is not inferred, use a narrow
  Schema-derived type; do not build a decoder, use `any`, or invent defaults for required values.
- An ID alone does not prove existence, visibility, or Class. Keep checks for supplied references that
  the admitted contract or observation does not already establish. Absence from a caller-visible query
  is not proof of global nonexistence.
- A plain `defineQuery` executes one page. For a complete collection, declare `pagination.maximumPages`
  and project the completed pages, or use `defineCollectionQuery`; never treat the first page as complete.
- The SDK rejects a repeated cursor or exhausted page bound instead of returning a partial collection.
  Continuations and composite leaves are separate reads, not a shared point-in-time snapshot.

### Query mistakes that change the answer

- `Query.from({ nodes: [A, B] })` is a union, not an intersection. Class sources include concrete
  descendants; use an exact-Class filter when subclasses must not qualify.
- After `expand`, the default node binding is the reached node. Retain the earlier binding and select
  it explicitly to return the original records filtered by related facts; incoming traversal does not swap Edge endpoints.
- Property predicates currently offer `equals` and `isPresent`, not SQL ranges, substring search, or
  arbitrary callbacks. Equality does not coerce; `null` is present, and missing is not equal to `null`.
- Filtering one page in JavaScript is not a complete server-side search. If a predicate cannot be
  expressed, use a bounded complete read or change the product/query design; report the cost honestly.
- `page.size` and cursor are delivery options, not fields in `.select()` or the QueryAST. Ordering is
  one terminal Property order with explicit unranked placement and identity tie-breaks, not arbitrary multi-sort.
- A value projection can omit records whose properties the caller cannot read. Reference-only results
  prove identity visibility, not permission to fetch properties; changing projection can change the result set.

## Mutations: preserve the atomic invariant

- Author one `defineMutation<typeof schema>()((domain) => ({ build(input, mutation), ... }))`
  per atomic change. Related node/edge writes share that builder; never split a transaction automatically.
- Preconditions protect independently raceable facts: an observed version, lifecycle, or relationship.
  Do not add `expect` checks for endpoint Classes, property codecs, or cardinalities Schema already enforces.
- A prior Query is not an atomic guard. Use `mutation.transition` for StateMachine changes; it derives
  the target state and emits the stale-state precondition, so do not duplicate either.
- Omit `project` when the canonical Mutation result suffices; otherwise return the needed created IDs or
  committed outcome. Do not revalidate MutationResult or claim success before the commit resolves.
- Operations are an effect set, not a program: updating the same node twice rejects instead of applying
  sequential updates. Merge its property changes into one update; sibling effects cannot see each other's writes.
- All conditions observe the common pre-state. An Edge created in the Mutation cannot satisfy a sibling
  precondition or grant authority for another effect; use create bindings to reference new nodes, not future Paths.
- `expect.query` compares the complete ordered identity selection, not “contains” or a page. Truncated
  evidence cannot prove that no other related nodes exist; condition reads also need their own authority.
- Creates are not upserts, and deleting a missing target is not a successful no-op. After an uncertain
  network outcome, observe the result before retrying; a thrown request alone does not prove rollback.
- Structural precondition limits are available through `MutationAST.limits`; backend execution limits
  are separate. Never auto-chunk a rejected Mutation: that changes one atomic invariant into partial commits.

## One composed example

Assume Schema declares `Issue.close` returning boolean, an `open → closed` StateMachine on `status`,
and its callable Policy. These are separate owner files; imports of sibling owners are abbreviated.

```ts
// queries/issue/read-issue.ts
import { defineQuery, Query, queryResult, type QueryResult } from '@astrale-os/sdk/query'
import type { NodeId } from '@astrale-os/sdk/graph/node'
import type { StateOf } from '@astrale-os/sdk/state'
import type { schema } from '#schema'
import type { lifecycle } from '#schema/modules/issue/states'

export const readIssue = defineQuery<typeof schema>()((domain) => ({
  id: 'issue.read',
  build: ({ self }: { self: NodeId }) =>
    Query.from({ nodes: [self] }).select({ kind: 'nodes', projection: { kind: 'value' } }),
  project: (result: QueryResult) => {
    const node = queryResult.optionalNode(result, 'issue.read')
    return node === undefined ? undefined : {
      id: node.id,
      status: node.props[domain.classes.Issue.properties.status.key] as StateOf<typeof lifecycle>,
    }
  },
}))

// mutations/issue/close-issue.ts
import { defineMutation } from '@astrale-os/sdk/mutation'

export const closeIssueMutation = defineMutation<typeof schema>()((domain) => ({
  id: 'issue.close',
  build({ self }: { self: NodeId }, mutation) {
    mutation.transition({
      node: self, class: domain.classes.Issue, property: 'status', from: 'open', event: 'close',
    })
  },
  project: () => true,
}))

// rules/issue/can-close-issue.ts — pure eligibility over admitted observations, not authorization.
export function canCloseIssue(issue: { status: StateOf<typeof lifecycle> } | undefined): boolean {
  return issue?.status === 'open'
}

// functions/issue/close-issue.ts
import { defineWorkflow } from '@astrale-os/sdk/workflow'
import { canCloseIssue } from '#rules/issue'
import { issueNotClosable } from '#schema/modules/issue/errors'

export const closeIssue = defineWorkflow<typeof schema>()(
  'Issue.close',
  { errors: { ISSUE_NOT_CLOSABLE: issueNotClosable } },
  async ({ self, query, mutate, step, error }) => {
    const issue = await step.run('read-issue', () => query(readIssue, { self }))
    if (!canCloseIssue(issue)) throw error('ISSUE_NOT_CLOSABLE', { issueId: self })
    return step.run('close-issue', () => mutate(closeIssueMutation, { self }))
  },
)
```

The Query projects, the imported Rule decides eligibility, and the Workflow maps refusal to its
declared error. Policy owns authorization; the Mutation still guards state changes after the read.

## Expected errors

- Declare reusable errors with `error` from `@astrale-os/sdk/schema` under the owning Schema module's
  `errors/`. Each callable imports that focused facade and registers only its applicable alternatives.

```ts
// schema/modules/issue/errors/issue-not-closable.ts
import { error } from '@astrale-os/sdk/schema'
import { z } from 'zod'

export const issueNotClosable = error({
  family: 'CONFLICT',
  message: 'The issue is unavailable or cannot be closed.',
  details: z.strictObject({ issueId: z.string() }),
})
```

- Registration keys supply stable codes; declarations own fixed safe messages and details contracts.
  Keeping them under Schema source does not make them installed Schema members or generated-client alternatives.
- Preserve structured dependency failures; map only recognized expected errors. Unexpected exceptions
  remain defects, not invalid input or successful error-shaped output.

## Installation requirements

- A Schema dependency pins definitions, not capability. Declare exact protected Kernel/foreign Functions
  called as the Domain, including Policy-admitted calls: `can_use` supplies principal usability, while
  the caller must independently pass admission. See `policies.md` and `users.md`.

```ts
import { defineDomain, requirements } from '@astrale-os/sdk/domain'
import { K, schema as language } from '@astrale-os/sdk/schema'
import { schema } from '#schema'

// Schema declares dependencies: { kernel: KernelSchema, messaging: MessagingSchema }.
// Resolve that exact declared dependency, not a separately chosen foreign version.
// This supplies Domain-principal usability; Messaging.send still checks its caller.
const Messaging = language.resolve(schema).dependencies.messaging

export const domain = defineDomain({
  schema, runtime,
  requirements: requirements({
    functions: [K.functions.query, K.functions.mutate, Messaging.functions.send],
  }),
})
```

- Add `K.functions.register` when using an admitted `auth.register(...)` capability. Inspect requested
  and materialized authority for the Domain principal; do not grant the human rights to conceal a gap.
- Call an exact dependency with
  `dependencies.messaging.caller.invoke((messaging) => messaging.functions.send, input)` to act for
  the incoming caller; an instance Method
  also takes its NodeId before input. Providers use their invocation-scoped typed `invoke` capability.
  Read `integrations.md` for consumer-owned Integrations/Providers; do not import a foreign handler
  or claim atomicity across Domains.
- For explicit authority selection, use `kernel.caller.invoke(reference(domain, declaration), input)`.
  References retain the full callable key and declaring revision; no `expect` or `schemaExpectation` option
  is needed. An instance reference requires the exact declaring Class, not a descendant. Raw instance
  paths use the entire key, such as `@id::files.example:class.Resource.method.rename`; raw revision is optional.

## Optional native HTTP routes

- Use top-level `routes/` only for a needed native wire surface: webhook, passthrough, or compatibility API.
  Ordinary SDK Functions and frontend navigation do not need this layer.
- A route maps HTTP method/path, receiver, headers/body, and credentials to an admitted callable.
  Keep behavior in `functions/`, not the route; compose the route collection in `domain.ts`.

```ts
// routes/document/download-document-route.ts
import { route } from '@astrale-os/sdk/domain'
import { downloadDocument } from '#functions/document'

export const downloadDocumentRoute = route(downloadDocument, {
  name: 'download-document',
  path: '/documents/{documentId}/download',
  method: 'GET',
  receiver: 'documentId',
})
```

A locally declared Method with `abstract: true` on a concrete Class requires an Action or Workflow
just like any other executable Method. Its descendants must declare their own implementations;
there is no handler fallback. A missing handler rejects the Runtime before it can serve calls.
