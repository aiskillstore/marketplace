---
name: run-tests
description: Run unit and integration tests for Catalyst-Relay. Use when asked to test, run tests, verify changes, or check if code works.
---

# Running Tests

## When to Use

- User asks to run tests or verify changes
- After implementing a feature or fix
- Before committing or publishing

## Unit Tests

```bash
bun test                      # All tests
bun test --watch              # Watch mode
bun test src/__tests__/core   # Specific directory
```

## Node.js Compatibility Check

Before publishing, verify library imports work in Node:

```bash
node --experimental-strip-types -e "import('.')"
```

## Integration Tests

Integration tests require SAP credentials and connect to a live SAP system.

### Credentials

There are two ways credentials can be provided:

1. **OS Keyring (recommended):** If `SAP_TEST_SYSTEM_ALIAS` is set in `.env` (e.g. `TKO-DS4`), the test helpers automatically read the password from the OS keyring where Catalyst-CLI stores it. No manual password entry needed.
2. **Environment variable:** `SAP_PASSWORD` can be set directly or passed to `./test.bat <password>`.

The keyring lookup uses the Catalyst-CLI service name and key format (`{alias}:basic:password`). If both are available, `SAP_PASSWORD` takes priority.

### Workflow

1. Confirm `.env` exists with system connection details (URL, client, username)
2. Run `bun test` (credentials resolve from keyring) or `./test.bat <SAP_PASSWORD>`
3. Read `test.output` for integration test results if using test.bat

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SAP_TEST_ADT_URL` | Yes | SAP ADT server URL |
| `SAP_TEST_CLIENT` | Yes | SAP client number |
| `SAP_TEST_USERNAME` | Yes | SAP username |
| `SAP_TEST_SYSTEM_ALIAS` | No | System alias for keyring credential lookup |
| `SAP_PASSWORD` | No* | SAP password (not needed if keyring is configured) |
| `SAP_TEST_PACKAGE` | No | Target package (default: `$TMP`) |
| `SAP_TEST_TRANSPORT` | No | Transport request |

See `.env.templ` for a template.

## Test Coverage Map

| Test File | Coverage |
|-----------|----------|
| `cds-workflow.test.ts` | CDS View + Access Control lifecycle |
| `abap-class-workflow.test.ts` | ABAP Class CRAUD |
| `abap-program-workflow.test.ts` | ABAP Program CRAUD |
| `table-workflow.test.ts` | Table + data preview |
| `discovery-workflow.test.ts` | Packages, tree, transports |
| `search-workflow.test.ts` | Search + where-used |
| `data-preview-workflow.test.ts` | Preview on T000 table |
| `upsert-workflow.test.ts` | Create vs update detection |
