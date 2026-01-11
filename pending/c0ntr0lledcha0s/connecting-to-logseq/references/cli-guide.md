# Logseq CLI Guide

## Overview

The Logseq CLI (`@logseq/cli`) provides command-line access to Logseq graphs, enabling automation, CI/CD integration, and offline operations.

## Installation

### Global Install (Recommended)

```bash
npm install -g @logseq/cli
```

### Using npx (No Install)

```bash
npx @logseq/cli --help
```

## Basic Usage

```bash
logseq [command] [options]
```

### Common Options

| Option | Description |
|--------|-------------|
| `--graph <path>` | Path to local graph directory |
| `--in-app` | Connect to running Logseq instance |
| `-a, --auth <token>` | API token for in-app mode |
| `--format <type>` | Output format (json, table, etc.) |
| `--help` | Show help |

## Commands

### Query

Execute Datalog queries against a graph.

```bash
# Query local graph
logseq query "[:find ?title :where [?p :block/title ?title]]" --graph ~/logseq/my-graph

# Query running Logseq
logseq query "[:find ?title :where [?p :block/title ?title]]" --in-app -a $LOGSEQ_API_TOKEN

# Output as JSON
logseq query "..." --graph ~/graph --format json
```

### Graphs

List and manage graphs.

```bash
# List all graphs
logseq graphs list

# Show graph info
logseq graphs info --graph ~/logseq/my-graph
```

### Export

Export graph data.

```bash
# Export to EDN
logseq export edn --graph ~/logseq/my-graph -o export.edn

# Export to JSON
logseq export json --graph ~/logseq/my-graph -o export.json
```

### Validate

Validate graph structure and integrity.

```bash
logseq validate --graph ~/logseq/my-graph
```

## Graph Types

### DB Graphs (Full Support)

- SQLite-based storage
- Full query capabilities
- All CLI features available

### MD Graphs (Limited Support)

- Markdown file-based
- Some features may not work
- Better to use HTTP API for MD graphs

## Environment Variables

| Variable | Description |
|----------|-------------|
| `LOGSEQ_API_TOKEN` | Auth token for in-app mode |
| `LOGSEQ_GRAPH_PATH` | Default graph path |

## Examples

### Find All Pages

```bash
logseq query '
  [:find ?title
   :where
   [?p :block/title ?title]
   [?p :block/tags ?t]
   [?t :db/ident :logseq.class/Page]]
' --graph ~/logseq/my-graph
```

### Find Tasks

```bash
logseq query '
  [:find ?title ?status
   :where
   [?t :block/title ?title]
   [?t :block/tags ?tag]
   [?tag :db/ident :logseq.class/Task]
   [?t :logseq.property/status ?s]
   [?s :block/title ?status]]
' --graph ~/logseq/my-graph
```

### Find by Property

```bash
logseq query '
  [:find (pull ?b [:block/title :user.property/rating])
   :where
   [?b :user.property/rating ?r]
   [(>= ?r 4)]]
' --graph ~/logseq/my-graph --format json
```

## In-App Mode

Connect to a running Logseq instance instead of reading files directly.

### Setup

1. Start Logseq with HTTP API enabled
2. Create an API token
3. Use `--in-app` flag with `-a` token

### Benefits

- Real-time data
- Write operations available
- No file locking issues
- Works with sync

### Example

```bash
export LOGSEQ_API_TOKEN="your-token"

# Query via running Logseq
logseq query "[:find ?title :where [?p :block/title ?title]]" --in-app

# Or pass token directly
logseq query "..." --in-app -a "your-token"
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Logseq Export

on:
  schedule:
    - cron: '0 0 * * *'  # Daily

jobs:
  export:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install Logseq CLI
        run: npm install -g @logseq/cli

      - name: Export graph
        run: logseq export json --graph ./my-graph -o export.json

      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: graph-export
          path: export.json
```

## Troubleshooting

### "Graph not found"

- Check path is correct
- Ensure graph has `logseq/` folder or `db.sqlite`
- Try absolute path

### "Query failed"

- Verify Datalog syntax
- Check attribute names (DB vs MD differ)
- Try simpler query first

### "Permission denied"

- Check file permissions
- Ensure graph isn't locked by Logseq
- Try --in-app mode instead

### "Connection refused" (in-app mode)

- Ensure Logseq is running
- Verify HTTP API is enabled
- Check port 12315 is accessible
