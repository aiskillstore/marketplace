# Prisma Detection Cookbook

How to detect and extract Prisma schema definitions for schema alignment.

## Detection Patterns

### Prisma Schema Location

Default: `prisma/schema.prisma`

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  posts     Post[]
  createdAt DateTime @default(now())
}
```

## Type Mapping

| Prisma Type | PostgreSQL Type | TypeScript Type |
|-------------|-----------------|-----------------|
| `Int` | `INTEGER` | `number` |
| `BigInt` | `BIGINT` | `bigint` |
| `Float` | `DOUBLE PRECISION` | `number` |
| `Decimal` | `DECIMAL` | `Prisma.Decimal` |
| `String` | `TEXT` | `string` |
| `Boolean` | `BOOLEAN` | `boolean` |
| `DateTime` | `TIMESTAMP` | `Date` |
| `Json` | `JSONB` | `JsonValue` |
| `Bytes` | `BYTEA` | `Buffer` |

## Attribute Mapping

| Prisma Attribute | Meaning |
|------------------|---------|
| `@id` | Primary key |
| `@unique` | Unique constraint |
| `@default(...)` | Default value |
| `@relation(...)` | Foreign key relationship |
| `@map("...")` | Column name mapping |
| `@@map("...")` | Table name mapping |
| `?` (optional) | Nullable column |

## Relationship Detection

### One-to-Many

```prisma
model User {
  id    Int    @id
  posts Post[]
}

model Post {
  id       Int  @id
  userId   Int
  user     User @relation(fields: [userId], references: [id])
}
```

### Many-to-Many (Implicit)

```prisma
model User {
  id    Int    @id
  roles Role[]
}

model Role {
  id    Int    @id
  users User[]
}
```

Creates junction table: `_RoleToUser`

### Many-to-Many (Explicit)

```prisma
model User {
  id        Int        @id
  userRoles UserRole[]
}

model Role {
  id        Int        @id
  userRoles UserRole[]
}

model UserRole {
  userId Int
  roleId Int
  user   User @relation(fields: [userId], references: [id])
  role   Role @relation(fields: [roleId], references: [id])

  @@id([userId, roleId])
}
```

## Common Issues

### Issue: Optional Field Mismatch

```prisma
// Prisma says optional
name String?

// TypeScript type generated as nullable
name: string | null

// But code treats as non-null - potential runtime error
```

### Issue: String Length

Prisma `String` maps to PostgreSQL `TEXT` (unlimited).
If you need VARCHAR with length, use `@db.VarChar(255)`.

```prisma
email String @db.VarChar(255)
```

### Issue: Enum Sync

```prisma
enum Status {
  PENDING
  ACTIVE
  CANCELLED
}

model Order {
  status Status @default(PENDING)
}
```

Ensure code and database enum values match exactly.

## Migration Detection

Check migration status:

```bash
# List migrations
ls -la prisma/migrations/

# Check for pending migrations
npx prisma migrate status
```

Migration files follow pattern: `YYYYMMDDHHMMSS_name/migration.sql`

## File Patterns to Search

```bash
# Find Prisma schema
find . -name "schema.prisma"

# Find generated client
find . -path "*/@prisma/client*"

# Find migration files
find . -path "*/prisma/migrations/*"
```

## Parsing Strategy

1. Parse `prisma/schema.prisma`
2. Extract model definitions
3. Parse field attributes
4. Extract relationships
5. Map to database schema
6. Compare with generated client types
