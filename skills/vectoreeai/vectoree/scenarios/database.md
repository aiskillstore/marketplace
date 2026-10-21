# Database

Use this playbook for **S20–S24** and **C02**. Parent skill: `SKILL.md` in this folder (or https://raw.githubusercontent.com/VectoreeAI/vectoree-skills/main/skills/vectoree/SKILL.md)

Need a project API key first (`scenarios/connect.md`). Always `db list` / `db schema` before writes. Drop / full-table delete: stop and confirm.

---

## S20: which tables?

```bash
npx @vectoree/cli db list
npx @vectoree/cli db schema <table>
```

---

## S21 / C02: create a todos table (or notes / orders)

`id`, `created_at`, and `updated_at` are reserved and auto-added. `--columns` **replaces** the CLI default, so include a primary key plus at least one custom column:

```bash
npx @vectoree/cli db list
npx @vectoree/cli db create todos --columns '[
  {"columnName":"id","type":"uuid","isPrimaryKey":true,"isNullable":false,"isUnique":true,"defaultValue":"gen_random_uuid()"},
  {"columnName":"title","type":"string","isNullable":false,"isUnique":false},
  {"columnName":"done","type":"boolean","isNullable":false,"isUnique":false}
]'
npx @vectoree/cli db insert todos --data '{"title":"First task","done":false}'
npx @vectoree/cli db query todos --limit 20
```

Column types: `string` | `integer` | `float` | `boolean` | `uuid` | `date` | `datetime` | `json`.

For notes / orders, same pattern: one custom title/name column plus whatever fields the user asked for.

If they asked for **login / accounts**, that is **C09** (`scenarios/auth.md`). Do not `CREATE TABLE users`. Identity is Vectoree `auth.users`; business tables use `user_id` = JWT `sub`.

App CRUD: `npx @vectoree/cli docs get db-sdk`. Launch path is REST `/api/database/records/{table}` with `Authorization: Bearer $VECTOREE_API_KEY`, from a **server** route. Do not ship `@vectoree/sdk` as if it were a launch deliverable. Do not put the project key in a browser bundle.

C02 done when `db query todos` shows sample rows and the page can list/add.

---

## S22: add a column

```bash
npx @vectoree/cli db schema users
npx @vectoree/cli db sql "ALTER TABLE users ADD COLUMN avatar text"
```

Show the SQL first. Use `--yes` only after the user agrees.

There is no `db alter` in the launch CLI.

---

## S23: last 20 rows

```bash
npx @vectoree/cli db query <table> --limit 20
```

Optional: `--select id,title` and `--filter '{"status":"eq.active"}'` (PostgREST-style).

---

## S24: run this SQL

Show the statement. Then:

```bash
npx @vectoree/cli db sql "SELECT 1"
```

The CLI prompts unless `--yes`. Do not pass `--yes` for DROP / DELETE without an explicit user confirmation in this turn.

---

## Not in this launch slice

File-based migrations, RLS helpers, and index helpers are later. For a one-off, use `db sql`. Point at Dashboard → Database for visual editing.
