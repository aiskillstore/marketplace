---
name: prisma-postgres-upgrade
description: Upgrade a PostgreSQL app from Prisma ORM 6 or 7 straight to Prisma 8 in one pass, keeping the existing schema.prisma, database and data. Use when a Postgres project on Prisma 6 or 7 wants Prisma 8, including before deploying it on Prisma Compute, which runs only Prisma 8. Triggers on "upgrade prisma 6 to 8", "upgrade prisma 7 to 8", "upgrade to prisma 8 postgres", "prisma7Schema", "migrations/app", "move off @prisma/client", "Console says move to Prisma 8".
license: MIT
metadata:
  author: prisma
  version: "2.0.0"
---

# Prisma Postgres Upgrade: Prisma ORM 6 or 7 to Prisma 8

Move a Node.js server on Prisma ORM 6 or 7 and PostgreSQL to Prisma 8 in one pass. The schema,
the database and its data stay, and the app keeps running wherever it runs today.

This skill is the bridge. It covers only what is specific to leaving Prisma ORM 6 or 7. Prisma 8
itself (the contract, migrations, queries, errors) is covered by the `prisma-8` skill that ships
inside `@prisma/orm-postgres`, which step 2 installs. Follow it for anything Prisma 8 specific;
it matches the installed version, and this skill does not.

`prisma-8` says it does not apply to a project that still has `schema.prisma` and
`@prisma/client`. That is expected mid-upgrade: this skill keeps both until step 5, and
`prisma7Schema(...)` reads that `schema.prisma`. Use `prisma-8` for the Prisma 8 side anyway.

The [Prisma ORM 6 or 7 to 8 (PostgreSQL) guide](https://www.prisma.io/docs/guides/upgrade-prisma-orm/postgresql)
is the source of truth for the steps.

**Never do either of these:**

- Never route a PostgreSQL Prisma ORM 6 app through Prisma ORM 7 first. Prisma 8 reads a
  Prisma ORM 6 `schema.prisma` unchanged, so `prisma-upgrade-v7` is only for apps that stay on 7.
- Never install `prisma@latest` or `@prisma/orm-postgres@latest` when the app will deploy on
  Prisma Compute: the latest pair does not work with the Composer version the Console's setup
  installs, so the deploy fails.

## When to Apply

- A PostgreSQL project on Prisma ORM 6 or 7 asks to upgrade to Prisma 8 in one pass
- A Prisma ORM 6 or 7 app wants to deploy on Prisma Compute, or the Console blocked its setup
  with "move to Prisma 8": upgrade here, then deploy with `prisma-compute`

Not for: deploying on Compute (use `prisma-compute`, `deploy-existing-app`), MongoDB (use
`prisma-mongodb-upgrade`), a Prisma ORM 7 app moving one route at a time beside Prisma 8
(follow the [route-by-route guide](https://www.prisma.io/docs/guides/upgrade-prisma-orm/postgresql-incremental)),
a project already on Prisma 8 (use the synced `prisma-8` skill), or a new project (use
`prisma-orm-setup`).

## Versions

Install exact versions with `--save-exact`. For an app headed to Compute, use the versions the
Console's setup uses: today `prisma` `8.0.0-rc.27` (dev dependency) and `@prisma/orm-postgres`
`8.0.0-rc.20`. If the Console's message or an existing setup pull request names other versions,
use those. Use Node.js 24.11 or newer if the app will run under `prisma dev`.

## The path

| Step | What happens | Where the detail is |
|------|--------------|---------------------|
| 0 | Run the repo's own checks and record the results | `verify-upgrade-checklist` |
| 1 | Remove `prisma`, install the versions above, remove `prisma generate` from scripts | this file |
| 2 | Write the Prisma 8 `prisma.config.ts`, then `npx prisma skills sync` | `adopt-schema-and-migrations` |
| 3 | `contract emit`, `db sign`, baseline migration, retire `prisma/migrations` | `adopt-schema-and-migrations` |
| 4 | Create the Prisma 8 client and rewrite every query | `client-api-mapping` |
| 5 | Remove `@prisma/client`, the adapter and the generated client | this file |
| 6 | Run the same checks again and start the app | `verify-upgrade-checklist` |

In step 1, also remove `prisma generate` from `build`, `postinstall` and any other script: the
Prisma 8 CLI has no `generate` and fails with `CLI.UNKNOWN_COMMAND`. Step 1 removes the only
command that generated the old client. It keeps working locally, but a fresh install (CI, a new
clone) has none, so finish step 4 before pushing to a branch CI builds.

The sync in step 2 installs `prisma-8`, `prisma-platform-core-concepts` and
`prisma-composer-core-concepts` in one go, because the CLI depends on Composer. It writes them
for every agent it knows unless `skills.agents` in the config lists only the ones the repository
uses. In a Prisma ORM 7 app, replace the old `prisma.config.ts` before syncing: the sync fails
with `CLI.CONFIG_UNREADABLE` while the old one is in place.

Commit what Prisma 8 writes: `src/prisma/contract.json`, `src/prisma/contract.d.ts` and the
whole `migrations/` folder. There is no generate step to recreate them in CI.

In step 5, `npm uninstall @prisma/client` leaves the generated client behind; delete
`node_modules/.prisma` too, then run a fresh install and the checks so nothing still imports it.

## Deploying on Compute

When the upgrade is done and the checks pass, deploy with the `prisma-compute` skill
(`references/deploy-existing-app.md`). Compute runs only Prisma 8, so the upgrade has to be
finished first.

## What the user does

The agent cannot do these; stop and ask:

- Decide what to do about a database time zone other than UTC (see `client-api-mapping`).
- Sign every other existing database (staging, production) with `npx prisma db sign`. The agent
  has only the local one.
- Review the change before it ships, especially when the repository has no tests.

## Reference files

| Reference | What it covers |
|-----------|----------------|
| `references/adopt-schema-and-migrations.md` | The first `prisma.config.ts`, keeping `schema.prisma` as the contract, CommonJS `tsconfig`, the baseline, retiring the old migration setup |
| `references/client-api-mapping.md` | The Prisma 8 client, Prisma ORM 6/7 calls to Prisma 8, and the differences that break rewrites |
| `references/verify-upgrade-checklist.md` | Proving the upgrade with the repo's own checks |

## Verified against

A Prisma ORM 6.19 app (Express 4, EJS, `tsc`, CommonJS) on PostgreSQL 18, with `prisma`
8.0.0-rc.27 and `@prisma/orm-postgres` 8.0.0-rc.20. Two agents with no context and only these
skills upgraded it: pages and API output were identical before and after against the same
database, and `prisma db verify` passed.

## Hand-off rule

Once the app runs on Prisma 8, use the synced `prisma-8` skill for day-to-day work and
`prisma-compute` to deploy and operate it on Compute. This skill covers the upgrade only.
