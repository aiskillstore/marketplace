# Migration Template

Use this shape whenever the release changes schema, data contracts, or runtime configuration.

## Required Fields

- migration type
- affected service or datastore
- execution timing
- rollback expectation
- operator warning

## Template

```md
### Migration
- Type:
- Affected Surface:
- Run Before Rollout:
- Rollback Safe:
- Operator Warning:
```
