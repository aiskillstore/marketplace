# npx -y @insforge/cli db export

Export database schema and/or data.

## Syntax

```bash
npx -y @insforge/cli db export [options]
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--format <format>` | `sql` or `json` | `sql` |
| `--tables <tables>` | Comma-separated table list | all tables |
| `--no-data` | Export schema only (no row data) | include data |
| `--include-functions` | Include stored functions | no |
| `--include-sequences` | Include sequences | no |
| `--include-views` | Include views | no |
| `--row-limit <n>` | Max rows per table | unlimited |
| `-o, --output <file>` | Output file path | stdout |

## Examples

```bash
# Full export to file
npx -y @insforge/cli db export --output backup.sql

# Schema only
npx -y @insforge/cli db export --no-data --output schema.sql

# Specific tables with functions
npx -y @insforge/cli db export --tables users,posts --include-functions --output partial.sql

# JSON format
npx -y @insforge/cli db export --format json --output backup.json

# Limited rows for development
npx -y @insforge/cli db export --row-limit 100 --output dev-data.sql
```
