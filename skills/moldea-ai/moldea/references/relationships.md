# Declared relationships

Use this policy for context, decisions, agents, tools, and skills when an authorized task assesses or changes their manifest relationships. A relationship records material ownership and relevance. It is not a dependency inventory or proof that the prose and code agree.

## Bindings establish relevance

A binding names the regular file, and optionally the exported symbol, that implements an owner's fact or behavior. Core checks the declared file and supported exports. The binding itself makes a change to that path relevant; do not repeat the bound file as an exact `affectedBy` entry. A glob may also cover the file when it covers other material files in the same coherent subsystem. A passing file or export check never proves runtime wiring or behavior.

## Impact paths

An `affectedBy` path names repository content whose change can make the owner's stated material facts or an agent's behavior wrong. For context and decisions, this can include policy sources, deployment and operating documents, and configuration that sets runtime behavior. For agents, tools, and skills, it can include policy modules, schema sources, tool implementations, instruction loaders, routing, and runtime integration not already named by a binding. Package manifests and lockfiles qualify when they select dependencies or runtime settings that materially affect the owner, not by default. Compiler settings and type declarations require an evidenced behavioral effect beyond compilation participation. Relate tests only to the behavior they protect. These are evidence rules, not filename bans. Relate each path to the owner whose facts or behavior it can actually affect.

## Material facts only

Record product rules, contracts, invariants, security, billing, data and retention guarantees, and agent behavior. Layout, styling, navigation, scrolling, and component composition do not create a relationship, even when an owner document mentions them. A link from `/moldea/project.md` to focused context is navigation, not an impact relationship; the project document owns project-wide facts only.

## Shared infrastructure

A module shared across features, including shared UI components, routers, query and data helpers, and error or logging services, is not an impact path of a feature owner merely because that feature uses it. Relate the feature module that uses the shared code. Relate a shared module only to an owner that states the shared module's own contract.

## Granularity

Use an exact file when the material relationship belongs to that file. Use `/<directory>/**` when a coherent subsystem owns the behavior. Never use a catch-all such as `/src/**`. Exact entries identify regular files; a bare directory is invalid and removing a trailing slash does not turn it into a file. Preserve the supported version 1 field shapes and repository-root-absolute logical paths.

## Lifecycle

During ordinary maintenance, add or correct relationships only for owners whose canonical content this task changes, using already-inspected source that materially governs that content under the rules above. For such a changed owner, add an established missing relationship or correct an established wrong one; reporting the gap alone is incomplete. An owner merely assessed during ordinary code work gets no manifest write; an established missing relationship permits at most a one-line gap note. For an owner only assessed during ordinary code work, only correct or remove an existing declaration made invalid by a file move or deletion in this task; this exception adds no new relationships. Read-only work reports gaps without writing. Initialization registers evidenced new content; explicit relationship maintenance, including a requested path relocation, and explicit repair retain their own authorized scope. A match calls for reconsideration, not an automatic edit. Preserve accurate declarations, and do not scan for candidate paths or run background freshness audits. Correct dead exact paths and no-match globs only within authorized maintenance or repair. In explicit repair, remove an entry that demonstrably cannot change the owner's material facts or behavior and give the reason under **Fixed**.

## Report uncertainty

Bind only paths the task has already inspected. If a path's role cannot be established, name the path and the reason under **Needs input** in explicit repair, or report the unresolved relationship in ordinary work. Do not silently add, remove, or omit a material relationship, invent an owner, or widen a pattern to hide uncertainty.
