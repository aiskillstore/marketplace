# Go dialect

How the universal core is spelled in Go, plus Go-specific idioms. Go's culture
prizes simplicity and explicitness; lean into that rather than importing patterns
from other languages.

## Tooling baseline

```sh
gofmt -l .            # or goimports; formatting is not negotiable in Go
go vet ./...
staticcheck ./...     # honnef.co/go/tools; the de facto strong linter
go test ./...
go build ./...
```

`golangci-lint` bundles vet, staticcheck, errcheck, and more; run it in CI. The
`errcheck` linter (no ignored error returns) is the most valuable one.

## Illegal states (core 1, 4)

- **Defined types over primitives** for domain values. Go has no generics-based
  branding need; a defined type is already nominal:
  ```go
  type UserID string
  type Cents int64
  ```
  `UserID` and a bare `string` are distinct types; the compiler stops the mix.
  Keep the underlying type unexported-constructed where an invariant matters
  (see below).
- **Enforce invariants with unexported fields + a constructor in the package.**
  Go has no private constructors per se, but a struct with unexported fields can
  only be built fully within its package, so a `NewEmail(raw string) (Email,
  error)` becomes the only door from outside:
  ```go
  type Email struct{ value string }            // unexported field
  func NewEmail(raw string) (Email, error) { /* validate */ return Email{raw}, nil }
  func (e Email) String() string { return e.value }
  ```
- **States:** Go has no sum types. Model a closed set of states with either a
  small `iota` enum plus a `String()` method, or a sealed interface (an
  interface with an unexported method so only this package can implement it) with
  one struct per variant. Use the sealed-interface form when each state carries
  different data.
  ```go
  type State interface{ isState() }
  type Loading struct{}
  type Ready struct{ Data []byte }
  func (Loading) isState() {} ; func (Ready) isState() {}
  ```
- Use the zero value deliberately: design types so their zero value is a valid,
  useful default (`bytes.Buffer`, `sync.Mutex`). If the zero value is invalid,
  force construction through a `New*` function.

## Parse, don't validate (core 2)

- Decode external data into a struct and validate in the same step, returning the
  parsed value:
  ```go
  func ParseConfig(b []byte) (Config, error) {
      var raw rawConfig
      if err := json.Unmarshal(b, &raw); err != nil { return Config{}, err }
      return raw.intoChecked()   // returns Config or error
  }
  ```
- Return the parsed `Config`, not a `validate(c) error` you call separately while
  still passing the raw struct around.
- Accept interfaces, return structs (below) is the Go form of "accept the general
  input."

## Errors (core 3)

- **Errors are values, returned explicitly.** Check every one. The
  `if err != nil { return ..., err }` boilerplate is the language working as
  intended; do not hide it.
- **Wrap with context using `%w`** so the chain is inspectable:
  ```go
  if err != nil {
      return fmt.Errorf("loading profile %q: %w", name, err)
  }
  ```
  `errors.Is` for sentinel comparison, `errors.As` to extract a typed error.
- **Sentinel and typed errors:** `var ErrNotFound = errors.New("not found")` for
  conditions callers branch on; a custom error type implementing `error` when the
  error carries data. Document which errors a function can return.
- **Never drop an error.** `_ = doThing()` must be a deliberate, commented
  decision; `errcheck` flags the accidental ones. Empty error handling is a bug.
- **Fail closed** in gates: an error from the check returns the deny path, never
  a default allow.
- Messages: lowercase, no trailing punctuation, no capitalization (they get
  wrapped: `fmt.Errorf("reading %s: %w", ...)`).
- `panic` only for truly unrecoverable programmer errors and package-init
  failures; never for ordinary control flow. `recover` only at well-defined
  boundaries (a server handler that must not crash the process).

## Interfaces and abstraction (core 8)

- **Accept interfaces, return structs.** Functions take the narrow interface they
  need; they return concrete types so callers keep full access.
- **Define interfaces at the consumer, keep them small.** The classic Go
  interface is one or two methods (`io.Reader`, `io.Writer`). Do not define a big
  interface next to its implementation "for testing"; define the small interface
  where it is used.
- **Do not reach for `interface{}`/`any`** to be generic. Since 1.18, use
  generics (`[T any]`) for genuinely type-parametric code, and concrete types
  otherwise. `any` is a smell outside true dynamic boundaries (JSON, reflection).
- No premature interfaces: a struct with one implementation needs no interface
  until a second implementation or a real test seam exists.

## Concurrency (Go-specific)

- **Share memory by communicating:** prefer channels for handoff, `sync.Mutex`
  for protecting a small piece of shared state. Do not over-rotate to channels
  where a mutex is simpler.
- **Pass `context.Context` as the first parameter** to anything that does IO,
  blocks, or spawns work; honor cancellation and deadlines. Never store a
  `Context` in a struct.
- **Every goroutine needs a known lifetime and exit.** A goroutine that nothing
  waits on and nothing can stop is a leak. Use `sync.WaitGroup`,
  `errgroup.Group` (parallel work with error propagation and cancellation), or a
  done channel.
- Guard against data races; run `go test -race` in CI. `golang.org/x/sync` gives
  `errgroup` and `semaphore` for bounded parallelism.

## Naming and style

`MixedCaps`/`mixedCaps`, never underscores. Exported = capitalized; keep the
exported surface small. Short names for short scopes (`i`, `r`, `buf`). No
`Get` prefix on getters (`user.Name()`, not `user.GetName()`). Interface names
often `-er` (`Reader`). Package names short, lowercase, no plurals, no
`util`/`common` grab-bags. Error variables `ErrFoo`. Avoid stutter
(`http.Server`, not `http.HTTPServer`).

## Project structure

Flat is good; resist deep nesting. Package by capability, not by layer. `cmd/`
for binaries, `internal/` for code you do not want importable outside the module.
Do not create `models/`, `controllers/`, `services/` layers by reflex; group by
domain. One package = one cohesive concern.

## Testing (core 6)

- **Table-driven tests** are the Go idiom:
  ```go
  tests := []struct{ name, in, want string }{ ... }
  for _, tt := range tests {
      t.Run(tt.name, func(t *testing.T) { /* got := f(tt.in); compare */ })
  }
  ```
- Standard `testing` package; `t.Run` for subtests, `t.Helper()` in helpers,
  `t.TempDir()`/`t.Cleanup()` for fixtures. `testify/require` is acceptable for
  assertions; do not pull in heavy frameworks.
- No mocks of your own code. Define the small consumer interface and pass a real
  test implementation, or use `httptest.Server` for HTTP, a real temp dir/db for
  storage. `go test -race` always.
- Property tests via `testing/quick` or `gopter`. Fuzz tests with `go test
  -fuzz`. Benchmarks with `testing.B` and `b.N`.
- Determinism: inject the clock and randomness; never `time.Sleep` to synchronize
  (use channels/WaitGroup).

## Anti-patterns to refuse

Ignored error returns; `panic` for control flow; naked returns in long
functions; `interface{}`/`any` where a concrete type or generic fits; large
interfaces defined next to their single implementation; storing `Context` in
structs; goroutines with no exit; getter `Get` prefixes; `util`/`common`
packages; deep layered package trees; mutating a shared map without a lock.
