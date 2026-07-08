# SQL Database — Node.js — REFERENCE ONLY

## Prisma + Azure SQL Setup

### npm Packages

```bash
npm install prisma @prisma/client mssql
npm install -D prisma
npx prisma init
```

### Prisma Schema

Update `prisma/schema.prisma`:

```prisma
datasource db {
  provider = "sqlserver"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model TodoItem {
  id         Int     @id @default(autoincrement())
  title      String  @db.NVarChar(200)
  isComplete Boolean @default(false)
}
```

### Database Client

Create `src/db.js`:

```javascript
const { PrismaClient } = require("@prisma/client");

const prisma = new PrismaClient();
module.exports = { prisma };
```

### API Endpoints

Add to `src/index.js`:

```javascript
const { prisma } = require("./db");

app.get("/api/todos", async (req, res) => {
  const todos = await prisma.todoItem.findMany();
  res.json(todos);
});

app.post("/api/todos", async (req, res) => {
  const body = req.body || {};
  const title = typeof body.title === "string" ? body.title.trim() : "";
  if (!title) {
    return res.status(400).json({ error: "title is required and must be a non-empty string" });
  }
  const isComplete = body.isComplete === undefined ? false : body.isComplete;
  if (typeof isComplete !== "boolean") {
    return res.status(400).json({ error: "isComplete must be a boolean" });
  }
  const todo = await prisma.todoItem.create({ data: { title, isComplete } });
  res.status(201).json(todo);
});

app.get("/api/todos/:id", async (req, res) => {
  const todo = await prisma.todoItem.findUnique({
    where: { id: parseInt(req.params.id) },
  });
  if (!todo) return res.status(404).json({ error: "Not found" });
  res.json(todo);
});
```

### Connection String

**Azure (managed identity):**

Set as app setting in Bicep — the format Prisma uses for SQL Server:
```
sqlserver://<server>.database.windows.net:1433;database=<db>;authentication=ActiveDirectoryMsi;clientId=<mi-client-id>
```

```bicep
{ name: 'DATABASE_URL', value: 'sqlserver://${sqlServer.properties.fullyQualifiedDomainName}:1433;database=${sqlDatabase.name};authentication=ActiveDirectoryMsi;clientId=${managedIdentity.properties.clientId}' }
```

**Local development (SQL auth):**

```bash
# .env (local only — never commit)
DATABASE_URL="sqlserver://localhost:1433;database=myapp;user=<username>;password=<your-strong-password>;trustServerCertificate=true"
```

### EF Migrations (postprovision hook)

Create `infra/scripts/setup-db.sh`:

```bash
#!/bin/bash
npx prisma migrate deploy --schema src/prisma/schema.prisma
```

## Files to Add

| File | Action |
|------|--------|
| `prisma/schema.prisma` | Create — data model definitions |
| `src/db.js` | Create — Prisma client instance |
| `src/index.js` | Modify — add CRUD endpoints |
| `package.json` | Modify — add prisma, @prisma/client |

## Common Patterns

- Use `prisma.todoItem.findMany()` for read-only queries
- Use `prisma.$disconnect()` in shutdown hooks for clean teardown
- Run `npx prisma generate` after schema changes to regenerate the client
