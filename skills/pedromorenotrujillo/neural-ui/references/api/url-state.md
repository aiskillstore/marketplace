# @neural-ui/core/url-state

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuUrlStateService

Supported imperative members:

```typescript
readonly params: Signal<Params>;
getParam(key: string): Signal<string | null>;
setParam(key: string, value: string | null, replaceUrl?: boolean): void;
patchParams(params: Record<string, string | null>, replaceUrl?: boolean): void;
clearParams(replaceUrl?: boolean): void;
```

