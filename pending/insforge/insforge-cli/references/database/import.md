# npx -y @insforge/cli db import

Import database from a SQL file.

## Syntax

```bash
npx -y @insforge/cli db import <file> [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--truncate` | Truncate existing tables before import |

## Examples

```bash
# Import SQL file
npx -y @insforge/cli db import backup.sql

# Import with table truncation
npx -y @insforge/cli db import backup.sql --truncate
```

## Output

Displays filename, number of tables processed, and rows imported.

## Notes

- The file must be a valid SQL file (e.g., from `npx -y @insforge/cli db export`).
- Use `--truncate` carefully — it removes all existing data from tables before importing.
