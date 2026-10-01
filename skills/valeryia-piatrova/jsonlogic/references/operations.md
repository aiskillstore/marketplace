# JsonLogic operations

## Compliance

The JsonLogic specification provides test suites — concrete inputs with expected
outputs that validate the implementation of operations. The specification comes in
two variants:

- **CORE** – [original JsonLogic website](https://jsonlogic.com/tests.json)
- **EXTRA** – [extensions built on top of the core](https://github.com/json-logic/compat-tables/tree/main/suites)

"Extra" exists because "core" hasn't changed in years — and that's fine, "core" is a
solid, finished foundation. Think of it as v1, while "extra" is the v2+ evolution:
there are no visible plans to change the original.

## Supported Operations (Built-in)

| Operator | Source | Description |
|---|---|---|
| [Data / Presence](https://jsonlogic.com/operations.html#accessing-data) | | |
| `var` | **CORE** | Retrieve data from the provided data object. |
| `val` | **EXTRA** | Community successor to `var` — array-form paths, deep defaults, scope traversal. |
| `missing` | **CORE** | Returns an array of any keys that are missing from the data object, or an empty array. |
| `missing_some` | **CORE** | Returns an empty array if the minimum is met, or an array of the missing keys otherwise. |
| `exists` | **EXTRA** | Boolean counterpart to `missing` — true or false for whether a single path exists in the data. |
| [Logic and Boolean Operations](https://jsonlogic.com/operations.html#logic-and-boolean-operations) | | |
| `if` | **CORE** | Takes a condition and returns one of two values based on whether the condition is true or false. Also supports `if/elseif/.../else` chains with more paired arguments. |
| `?:` | **CORE** | Ternary shorthand for a 3-argument `if` — not its own entry on jsonlogic.com/operations.html, but treated as an alias by compliant engines. |
| `and` | **CORE** | Returns the first falsy argument, or the last argument. |
| `or` | **CORE** | Returns the first truthy argument, or the last argument. |
| `!` | **CORE** | Logical negation (not). |
| `!!` | **CORE** | Double negation, or cast to a boolean. |
| [Comparison Operations](https://jsonlogic.com/operations.html#logic-and-boolean-operations) | | |
| `==` | **CORE** | Tests equality, with type coercion. |
| `===` | **CORE** | Tests strict equality. |
| `!=` | **CORE** | Tests not-equal, with type coercion. |
| `!==` | **CORE** | Tests strict not-equal. |
| `>` | **CORE** | Greater than comparison operator. Also usable with three arguments as a range test: `min < val < max`. |
| `>=` | **CORE** | Greater than or equal to comparison operator. |
| `<` | **CORE** | Less than comparison operator. Also usable with three arguments as a range test: `min < val < max`. |
| `<=` | **CORE** | Less than or equal to comparison operator. |
| [Numeric Operations](https://jsonlogic.com/operations.html#numeric-operations) | | |
| `+` | **CORE** | Addition operator; with one argument, casts to a number. |
| `-` | **CORE** | Subtraction operator; with one argument, returns arithmetic negative. |
| `*` | **CORE** | Multiplication operator. |
| `/` | **CORE** | Division operator. |
| `%` | **CORE** | Finds the remainder after the first argument is divided by the second. |
| `min` | **CORE** | Return the minimum from a list of values. |
| `max` | **CORE** | Return the maximum from a list of values. |
| [Array Operations](https://jsonlogic.com/operations.html#array-operations) | | |
| `map` | **CORE** | Perform an action on every member of an array. |
| `reduce` | **CORE** | Combine all elements in an array into a single value. Inside the rule, `current` and `accumulator` refer to the element and running value. |
| `filter` | **CORE** | Keep only elements of an array that pass a test. |
| `all` | **CORE** | Perform a test on each member of an array; returns true if all pass. False on an empty array. |
| `none` | **CORE** | Perform a test on each member of an array; returns true if none pass. True on an empty array. |
| `some` | **CORE** | Perform a test on each member of an array; returns true if any pass. |
| `merge` | **CORE** | Takes one or more arrays and merges them into one array. |
| [String Operations](https://jsonlogic.com/operations.html#string-operations) | | |
| `in` | **CORE** | Tests membership in an array or substring presence in a string — same operator name, dispatched by argument type. |
| `cat` | **CORE** | Concatenate all the supplied arguments, with no separator. |
| `substr` | **CORE** | Get a portion of a string. Negative start counts from the end; negative length stops that many characters before the end. |
| [Community Extensions](https://github.com/json-logic/compat-tables/tree/main/suites) | | |
| `??` | **EXTRA** | Nullish coalescing — returns the first argument that isn't null/undefined. |
| `try` | **EXTRA** | Attempts each argument in order, falling through to the next if one throws. |
| `throw` | **EXTRA** | Raises an error — paired with `try` to give rules their own error handling. |
| `preserve` | **EXTRA** | Marks a value so engines don't traverse it as a nested rule. |
| Docs-only / Not implemented | | |
| `log` | **DOCS-ONLY** | Logs the first value to console, then passes it through unmodified — documented, but not every engine implements it as a runnable operation. |

## References

- Source: https://jsonlogic.com/operations.html (fetched 2026-09-16)
- Community extension suites: https://github.com/json-logic/compat-tables/tree/main/suites
