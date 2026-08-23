# Python dialect

How the universal core is spelled in Python, plus Python-specific idioms.
Python's dynamism makes the discipline opt-in: type hints, a strict type checker,
and boundary parsing are what buy you the safety other languages give by default.

## Tooling baseline

```sh
ruff check .          # lint (replaces flake8/isort/pyupgrade and more)
ruff format .         # format (black-compatible)
mypy --strict .       # or: pyright / basedpyright
pytest
```

`ruff` is the locked default: one fast tool for both format and lint (it replaces
black, isort, flake8, and pyupgrade). `pyproject.toml` is the single config home.
Run a type checker in CI in strict mode: untyped Python silently rots. Pin Python
version and dependencies (uv, poetry, or pip-tools). See
[`../principles/new-project-defaults.md`](../principles/new-project-defaults.md).

```toml
[tool.mypy]
strict = true
warn_unreachable = true
```

## Type hints everywhere (foundation)

Type hints are not decoration; they are the type system you are choosing to turn
on. Annotate every function signature and every public attribute. Without them
mypy/pyright have nothing to check and the rest of this file does not apply.

- Modern syntax: `list[str]`, `dict[str, int]`, `X | None` (not `Optional[X]`),
  `X | Y` unions. `from __future__ import annotations` or 3.10+.
- `typing.Final` for constants, `Literal["a", "b"]` for closed string sets,
  `Self` for fluent returns.

## Illegal states (core 1, 4)

- **Dataclasses / frozen dataclasses for structured data,** not bare dicts or
  tuples passed around:
  ```python
  @dataclass(frozen=True, slots=True)
  class User:
      id: UserId
      email: Email
  ```
  `frozen=True` for immutability, `slots=True` for memory and typo-safety.
- **`NewType` for cheap nominal IDs,** a class with a validating constructor when
  there is an invariant:
  ```python
  UserId = NewType("UserId", int)              # zero-cost label

  @dataclass(frozen=True)
  class Email:
      value: str
      def __post_init__(self) -> None:
          if "@" not in self.value: raise ValueError("invalid email")
  ```
- **States: `enum.Enum` for closed sets;** a union of dataclasses plus
  `match`/`case` for states that carry different data:
  ```python
  match state:
      case Loading():        ...
      case Ready(data=d):    ...
      case Error(message=m): ...
  ```
  Make the checker prove exhaustiveness: annotate the union and let mypy flag a
  missing case (an `assert_never(state)` in a fallthrough forces it).
- Avoid passing `dict[str, Any]` as a pseudo-object through the codebase. That is
  the Python form of stringly-typed data. Parse it into a dataclass/model at the
  edge.

## Parse, don't validate (core 2)

- **Use pydantic (v2) or attrs+cattrs to parse external data into typed models at
  the boundary:**
  ```python
  class Config(BaseModel):
      port: int = Field(gt=0)
      host: str

  config = Config.model_validate(raw_json)   # raises on bad shape; config is typed
  ```
  The model is the parser and the type in one. Do not write
  `def is_valid(d: dict) -> bool` and keep handing the dict around.
- Boundaries that must be parsed: `json.loads` output, `os.environ` values (all
  `str`), request bodies, config files, CSV rows, subprocess output. Each returns
  untyped data; convert it once.
- Push the model down: inner functions take `Config`, not `dict`.

## Errors (core 3)

- **Exceptions are Python's value channel.** Raise specific exception types, not
  bare `Exception`. Define a small exception hierarchy for your domain so callers
  can catch precisely:
  ```python
  class AppError(Exception): ...
  class ConfigError(AppError): ...
  ```
- **Chain with `raise ... from err`** so the traceback shows the cause:
  ```python
  raise ConfigError(f"loading profile {name!r}") from err
  ```
- **Catch narrowly.** `except SpecificError:`, never a bare `except:` or
  `except Exception:` that hides bugs. Re-raise what you cannot handle.
- **Never swallow:** no `except SomeError: pass` without a logged, commented
  reason. The silent pass is a data-corruption bug.
- **Fail closed** in gates: an exception or timeout in a check returns deny, not a
  default allow.
- EAFP over LBYL where it reads cleanly (try the operation and catch, rather than
  pre-checking), but not as an excuse to catch broadly.
- Use `contextlib` (`with`, `contextmanager`) for cleanup; do not hand-roll
  try/finally where a context manager exists.

## Async (Python-specific)

- `asyncio` with `async`/`await`. `asyncio.gather(*aws)` for parallel,
  `asyncio.TaskGroup` (3.11+) for structured concurrency with proper cancellation
  and error aggregation (prefer it over bare `gather` on new code).
- Do not block the event loop: no synchronous IO or CPU-bound work in a coroutine;
  use `asyncio.to_thread` / `run_in_executor`. Do not mix `time.sleep` into async
  code (`await asyncio.sleep`).
- `asyncio.timeout()` for deadlines, cancellation via task cancellation.

## Naming and style (PEP 8)

`snake_case` functions/variables/modules, `PascalCase` classes,
`UPPER_SNAKE` constants. Booleans `is_`/`has_`/`can_`. Leading underscore for
non-public (`_internal`); module `__all__` to declare the public surface. No
single-char names except short loop indices. Avoid shadowing builtins (`list`,
`id`, `type`, `dict`).

## Project structure

A real package (`src/mypackage/` layout), not loose scripts. `__init__.py`
curates the public API. Group by feature/domain, not by technical layer. Keep IO
at the edges (a thin CLI/HTTP shell) and the core as pure, typed functions that
are trivial to test. `pyproject.toml` for all config.

## Testing (core 6)

- pytest. Plain `assert`, fixtures via `@pytest.fixture`, `tmp_path` for temp
  dirs, `@pytest.mark.parametrize` for table-style cases (the Python form of
  table-driven tests).
- **Avoid `unittest.mock` of your own code.** Patching internal functions pins the
  implementation and rots. Prefer real objects, real `tmp_path`, a real in-memory
  fake you wrote, `responses`/`respx` or a local server for HTTP, a real test DB.
  Reserve mocking for genuine external services, and prefer a contract test
  against the real thing.
- `hypothesis` for property-based testing (excellent, use it where inputs have
  invariants or round-trips). `pytest-asyncio` for async tests.
- Determinism: `freezegun` or an injected clock for time; seed randomness; never
  `time.sleep` to synchronize, use the actual completion signal. `monkeypatch`
  the environment, not global state mutation.

## Anti-patterns to refuse

Missing type hints; `Any` to silence the checker; `dict[str, Any]` passed around
as a pseudo-object; bare `except:`/`except Exception: pass`; `raise` without
`from` when chaining; mutable default arguments (`def f(x=[])`); `*` imports;
shadowing builtins; blocking the event loop; patching your own internals in
tests; `assert` for runtime validation in production paths (it is stripped under
`-O`); business logic at module import time.
