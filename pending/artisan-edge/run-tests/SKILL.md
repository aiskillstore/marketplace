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

### Workflow

1. Confirm environment variables are set (see below)
2. Ask the user to run: `./test.bat <SAP_PASSWORD>`
3. Wait for user confirmation that tests completed
4. Read `test.output` to see results

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SAP_TEST_ADT_URL` | Yes | SAP ADT server URL |
| `SAP_TEST_CLIENT` | Yes | SAP client number |
| `SAP_TEST_USERNAME` | Yes | SAP username |
| `SAP_PASSWORD` | Yes | Passed to test.bat |
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
