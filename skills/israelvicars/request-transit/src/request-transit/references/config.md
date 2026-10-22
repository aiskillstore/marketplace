# Config: transit.config.json (optional; only the contract layer reads it)

Story 2a (the map and video) needs no config. The contract layer reads this file only when you run
`node <skill>/scripts/transit.mjs index --config <file>`. Paths are relative to the config file.

```json
{
  "packages": ["packages/*"],
  "protoPaths": ["proto"],
  "prefixes": ["/api/v1"],
  "infra": ["valkey-cart", "kafka", "postgres"],
  "services": {
    "checkout": { "repo": "services/checkout" },
    "quote": { "repo": "services/quote", "openapi": "openapi.json" }
  }
}
```

- `services`: service name exactly as it appears in spans → local repo or folder (`repo`), plus an optional OpenAPI JSON document (`openapi`, relative to `repo`).
- `packages`: folders (`dir/*` globs) of shared workspace packages. Their `package.json` `name` → `types`/`main` is how cross-package schema imports (`import { X } from '@shop/schemas'`) are resolved.
- `protoPaths`: folders that `.proto` `import "x/y.proto"` paths are resolved against (after the importing file's own folder).
- `prefixes`: route prefixes that may or may not appear in a span (mount points, gateways). A leading `/api/vN` is always optional.
- `infra`: dependency names that are always infrastructure hops (never counted as contract misses). Uninstrumented databases, caches and brokers are infrastructure anyway.
- `rpcPackagePrefix` (optional): the regex stripped from `rpc.service` before matching. By default everything up to the last `.` is stripped (`oteldemo.CartService` → `CartService`).

A worked example is in `<skill>/examples/astronomy-shop/transit.config.json`.
