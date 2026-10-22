# Contract layer (optional)

The contract layer is opt-in. Nothing reads source code until someone runs `node <skill>/scripts/transit.mjs index`, and a page shows contracts only when it is built with `--contracts`. The skill asks the user before indexing.

## Pipeline

1. **Extract**, file by file (`contracts/extractors/`). Each extractor is `{name, kind, test(src, file), symbols?(src), routes?(src)}`. Add one by writing a module and listing it in `contracts/extractors/index.mjs`.

   | extractor | reads | gives |
   | --- | --- | --- |
   | `zod` | `const X = z.object({...})`, `type T = z.infer<typeof X>` | validator shapes (high confidence) |
   | `joi` | `const X = Joi.object({...})`; fields optional unless `.required()` | validator shapes (high) |
   | `class-validator` | DTO classes; with class-validator decorators the shape is validated (high), otherwise it is a plain type (medium) | DTO shapes |
   | `ts-types` | `interface` and `type` declarations | type-only shapes (medium as a request) |
   | `express` | `app/router.<verb>('/path', ...)`. Request from `validate(X)`, `celebrate({ body: X })` or `X.parse(req.body)`; response from `Response<T>` | http entries |
   | `nest` | `@Controller` + `@Get/@Post/...`, `@GrpcMethod('Svc','Method')`, `@EventPattern('topic')`. Request from the `@Body()`/`@Payload()`/first parameter type or `X.parse(param)`; response from the return type (Promise/Observable unwrapped) | http, rpc and topic-consumer entries |
   | `topic-producer` | `.emit('topic', payload satisfies T)`, `publish<T>('topic', ...)` | topic-producer entries |
   | `protobuf` | `.proto`: `service`/`rpc` (incl. `stream`) become rpc entries. Messages (nested ones as `Outer.Inner` and `Inner`), enums, `repeated`, `optional`, `map<K,V>`, `oneof` (members optional) and well-known types are read, and `import`s are followed (relative to the file, then `config.protoPaths`) | rpc entries + IDL shapes (high) |
   | `openapi` | OpenAPI 3 JSON: requestBody and first 2xx `application/json` schemas, with `$ref` resolved | http entries (high) |

   The parsers are bracket-aware regex scanners, not a compiler. They miss unusual code shapes; when that happens they leave a gap rather than guessing.

2. **Resolve.** Each request/response symbol is looked up in the file's own declarations, then its imports. Relative paths and workspace packages (`config.packages`) are followed, including `export *` / `export { X } from` re-exports and `z.infer` aliases. The shape is then inlined. An unresolved name keeps the entry, at low confidence, with a note.

3. **Entry.** Each entry records `service`, `kind` (http/rpc/topic), method+path / rpc / topic+role, `source` (file:line of the route), `extractor` (e.g. `express+zod+ts-types`) and `confidence`. Each side also records its schema, its own source file:line, its extractor kind, whether it came from a shared package, and notes. Missing sides are listed in `gaps`.

4. **Match** (`contracts/match.mjs`, run by `<skill>/../../core/build.mjs --contracts`):
   - Server spans match on service + `rpc.service/rpc.method` (package prefix dropped) or service + method + path.
   - Paths are normalized: `:id`, `{id}`, numbers, uuids and long hex become `{}`. `/api/vN` and the configured prefixes are optional.
   - Consumers match the topic's consumer entry. If there is none, they fall back to the producer's shape at medium confidence.
   - Client spans to databases, caches or brokers (or names in `config.infra`) are **infrastructure** hops.
   - Everything else is **unmatched**, with a reason. It is listed in the hop table and the panel, never hidden.

## Cache and determinism

- **Per-file cache:** results go in `.transit-cache/contracts/files/<sha256(extractor version + path + content)>.json`.
- **Index:** written to `.transit-cache/contracts/index-<key>.json` (key = hash of the file hashes and the service config), plus `index.json` for the latest run.
- **Determinism:** keys are sorted, there are no timestamps, and the git commit is recorded when there is one. Same inputs give the same bytes.
- **Never committed:** `.transit-cache/` is gitignored.

## Not yet

- Pydantic/FastAPI
- queue-handler event switches
- contract diff (`--baseline`, story 3)
