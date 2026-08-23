# Test behavior, not implementation; avoid mocks

> Test at real boundaries with real data. Prefer pure functions and real
> fixtures over mocks that assert on internal calls.

## Test the boundary, not the wiring

Pick the feature boundary first, then test inputs to outputs across it. Good
boundaries are the ones a user or a caller actually cares about: config parsing,
request handling, a planning/translation step, a state transition. Tests that
poke internal helpers directly tend to pin the current implementation and break
on every refactor while catching few real bugs.

A `check(input) -> expected_output` helper with a table of cases beats a dozen
tests that each call private functions. Data in, data out, assert on the data.

## Keep the core IO-free

Push IO (filesystem, network, clock, randomness) to the edges so the core logic
is a pure function you can test by building values in memory. A function that
takes the parsed config and returns a plan is trivial to test; one that reads
the file, calls the network, and writes the result is not. Separate them.

## Avoid mocks; use real things

Mocks that record "method X was called with Y" test the implementation, not the
behavior, and they drift from reality. Prefer, in order:

1. **Pure functions** with no dependencies to fake.
2. **Real lightweight resources**: temp directories, throwaway git repos,
   ephemeral databases (`sqlx::test`, testcontainers, an in-memory DB that
   behaves like the real one), a real local HTTP server.
3. **A real interface implementation** written for tests (a deterministic
   in-memory backend), when you control the seam and want to inject behavior.
   This is a real implementation of a real contract, not a recording mock.

Reserve mocking frameworks for true external services you cannot run and cannot
reasonably fake, and even then prefer a contract test against the real thing in
a separate suite. If you find yourself asserting on call counts and argument
matchers, you are testing the wrong layer.

## Determinism

Flaky tests are worse than no tests because they train people to ignore red.

- **No sleeps for synchronization.** Do not `sleep(100ms)` and hope the work
  finished. Expose a join handle, a completion channel, a callback, or an
  observable side effect, and wait on that.
- **Control time and randomness.** Inject the clock and the RNG/seed so a test
  is reproducible.
- **Isolate state.** Each test gets its own temp dir / database / fixture; no
  shared mutable global that leaks between tests and orderings.

## Names and shape

- Name the test for the behavior it pins: `parses_empty_config_as_default`, not
  `test_config_2`. The name should read as a sentence about the system.
- Structure as arrange / act / assert (given / when / then). One logical
  behavior per test; multiple asserts are fine if they describe one outcome.
- Cover the unhappy paths: invalid input, empty input, boundary values, the
  error branches. Bugs live there.

## Property-based tests

When the input space is large or has invariants (round-trip encode/decode, sort
is a permutation, parse then serialize equals input), use property tests
(proptest, fast-check, gopter, hypothesis) to generate cases and shrink
failures. They find the edge you did not think to write.

## What to test where

- **Unit / in-source tests** for the core logic, close to the code.
- **Integration tests** for the assembled boundary (the real binary, the real
  HTTP handler), kept few and high-value. Prefer one modular integration surface
  over many tiny separate test binaries.
- **Doctests / runnable examples** where the language supports them and the
  build cost is acceptable: they keep docs honest.

See the per-language files for the test runner, fixture tools, async test
attributes, and property-test library in each.
