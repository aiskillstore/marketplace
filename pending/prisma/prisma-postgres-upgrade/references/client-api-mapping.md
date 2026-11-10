# client-api-mapping

Create the Prisma 8 client, then map each Prisma ORM 6 or 7 call to it; five differences break most rewrites.

## Priority

CRITICAL

## Why It Matters

The Prisma 8 client chains calls instead of taking one options object, and a schema read
through `prisma7Schema(...)` changes a few lookups and types. Some of these compile and then
fail at runtime or write wrong data.

## The client

One client for the app and the seed script, reading the same `DATABASE_URL` as before:

```typescript
// src/db.ts
import postgres from "@prisma/orm-postgres/runtime";
import { contractFromJson } from "@prisma/orm-postgres/static";
import type { Contract } from "./prisma/contract.js";
import contractJson from "./prisma/contract.json";

export const db = postgres({ contract: contractFromJson<Contract>(contractJson), url: process.env["DATABASE_URL"]! });
```

In a CommonJS `.ts` file, import the JSON without the `with { type: "json" }` attribute the
`prisma-8` skill shows: the attribute fails there with TS2856 and is only valid in `.mts` files.
On Compute, `prisma-compute` replaces this client with `service.load().db.client`.

## Old call to new call

Queries start at `db.orm.public.<Model>`. For anything not listed here, follow the synced
`prisma-8` skill (`references/queries.md`, `references/runtime.md`).

| Prisma ORM 6 / 7 | Prisma 8 |
|------------------|----------|
| `findMany({ where, orderBy })` | `.where({...}).orderBy((m) => m.field.asc()).all()` |
| `include: { _count: { select: { posts: true } } }` | `.include("posts", (p) => p.count())`; the number is `row.posts`, not `row._count.posts` |
| `orderBy: { votes: { _count: "desc" } }` | `.orderBy((p) => p.votes.count().desc())` |
| `findUnique({ where: { id } })` | `.first({ id })` |
| `findUnique` on an `@unique` or `@@unique` field | `.where({...}).first()` |
| `create({ data: { ..., votes: { create: {...} } } })` | `.create({ ..., votes: (v) => v.create([{...}]) })` |
| `deleteMany({ where })` then `.count` | `.where({...}).deleteAndCount()` |
| `deleteMany()` with no filter (seeds, tests) | `.where((m) => m.id.isNotNull()).deleteAll()`: writes need a filter |
| `createMany({ data: [...] })` | `.createAll([...])` |
| `count({ where })` | `.where({...}).aggregate((a) => ({ total: a.count() }))` |
| `Object.values(PostStatus)` from `@prisma/client` | `db.nativeEnums.public.PostStatus.values` |
| ``$queryRaw`SELECT 1` `` (health checks) | ``db.execute(db.raw.sql`SELECT 1`.affectedCount().build())`` |

What has no Prisma 8 form yet, such as `increment` in an update, is listed in
[Coming from Prisma ORM 7](https://www.prisma.io/docs/orm/coming-from-prisma-orm-7#queries).

## The five differences

1. **Unique lookups use `.first(...)` or `.where(...).first()`.** A 6/7 `@unique` or `@@unique`
   becomes a unique index, which `whereUnique` does not accept, so do not reach for it.
2. **Enums are under `db.nativeEnums`**, not `db.enums`. The values are the same strings.
3. **`DateTime` may read as a string** (`"2026-11-06 09:10:48.497"`, UTC, no offset) at
   `@prisma/orm-postgres@8.0.0-rc.20`. `row.createdAt.toISOString()` then throws at runtime,
   often in a template `tsc` never checks. Check the installed version's behavior in the
   `prisma-8` skill before converting.
4. **`@default(now())` is filled by the database** at rc.20, so a `timestamp` column gets the
   database's local time where 6/7 sent UTC. If `SHOW timezone` is not `UTC`, tell the user
   rather than changing data: new rows will store a different time than before, which is a
   behavior change the user has to decide on.
5. **Templates and other code `tsc` does not check still read the old shapes.** Search views
   (`.ejs`, `.hbs`, `.pug`) and plain `.js` files for `_count.`, `.toISOString()` on dates, and
   enum imports, and change them with the queries.

## Bad

```text
const board = await db.orm.public.Board.whereUnique({ slug }).first(); // does not compile
<%= post._count.votes %> <!-- an .ejs view tsc never checks: undefined after the rewrite -->
```

## Good

```typescript
const board = await db.orm.public.Board.where({ slug }).first();
const post = await db.orm.public.Post.include("votes", (v) => v.count()).first({ id }); // post.votes
```

## References

- [Guide, step 5](https://www.prisma.io/docs/guides/upgrade-prisma-orm/postgresql#5-rewrite-your-queries)
- The synced `prisma-8` skill, authoritative for the installed client
