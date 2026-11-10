# adopt-schema-and-migrations

Keep the Prisma ORM 6 or 7 `schema.prisma` as the contract, and hand migrations to Prisma 8 once.

## Priority

CRITICAL

## Why It Matters

Porting the schema by hand risks a contract that no longer matches the tables, which makes
`db sign` fail or plans a destructive migration. And the Compute deploy builds each database
from `migrations/app/`, so without a baseline there, previews and production start with no
tables.

## The first `prisma.config.ts` (step 2)

```typescript
import "dotenv/config"; // only if the app already uses dotenv
import { defineConfig as orm, prisma7Schema } from "@prisma/orm-postgres/config";
import { definePrismaConfig } from "prisma/config";

export default definePrismaConfig({
  orm: orm({
    contract: prisma7Schema("prisma/schema.prisma"), // the same file, Prisma ORM 6 or 7
    output: "src/prisma",
    db: { connection: process.env["DATABASE_URL"]! },
  }),
  skills: { agents: ["claude"] }, // only the agents the repository uses
});
```

Then run `npx prisma skills sync`. Deploying on Compute later adds a `composer` section to the same
config; that belongs to the `prisma-compute` skill, not to this upgrade.

## What is specific to coming from 6 or 7

- **`prisma7Schema(...)` also reads a Prisma ORM 6 schema unchanged**, including the
  `generator client` block and `url = env(...)`. Do not edit `schema.prisma` or port it to a
  `contract.prisma`. `output: "src/prisma"` puts `contract.json` and `contract.d.ts` where `tsc`
  and the Compute service find them. In a Prisma ORM 7 app, this file replaces the old
  `prisma.config.ts`: Prisma 8 reads only its own format under that name.
- **A CommonJS app built with `tsc` stays CommonJS.** Set `"module"` and `"moduleResolution"`
  to `"nodenext"`, add `"resolveJsonModule": true`, keep `include` at `src`, and do not add
  `"type": "module"`.
- **Sign the existing database, then plan the baseline:** `npx prisma contract emit`,
  `npx prisma db sign`, `npx prisma migration plan`. The first plan on a signed database writes
  `migrations/app/<timestamp>_baseline/` and ignores `--name`; `db verify` then passes and
  `db migrate` has nothing to apply, whatever its hint says. Commit `migrations/`. Sign every
  other existing database (staging) too; databases the Compute deploy creates do not need it.
- **Retire the old migration setup:** delete `prisma/migrations` (with `migration_lock.toml`),
  remove `prisma generate`, `prisma migrate *` and `prisma db seed` from scripts (including
  `postinstall`), and remove the `"prisma": { "seed": ... }` key. Prisma 8 has no `generate` or
  seed command; keep the seed script and run it with `tsx` (`client-api-mapping.md` shows its
  client). The `_prisma_migrations` table stays in the database; dropping it is the user's call.

For `contract emit`, `db sign`, the migration commands and every later schema change, follow the
synced `prisma-8` skill (`references/contract.md`, `references/migration-model.md`,
`references/migrations.md`). Where it shows `definePrismaConfig` from another package, use
`prisma/config` as above: that is what the installed CLI exports.

## Bad

```bash
# Rewriting schema.prisma into contract.prisma, or keeping prisma/migrations "for now"
npx prisma7 migrate dev
```

## Good

```bash
npx prisma contract emit && npx prisma db sign && npx prisma migration plan
rm -r prisma/migrations
```

## References

- [Guide, steps 2 and 3](https://www.prisma.io/docs/guides/upgrade-prisma-orm/postgresql#2-create-the-contract-from-your-schema)
- The synced `prisma-8` skill, authoritative for the installed version
