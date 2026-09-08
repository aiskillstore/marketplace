# Example: help

## User says

```text
What can dedupe handle?
```

## Command

```text
$ python3 scripts/dedupe.py --help
usage: dedupe.py [-h] {inspect} ...

Inspect bounded collections for duplicates without changing input.

Usage:
  python3 scripts/dedupe.py inspect --request request.json

Exit codes:
  0  report written to stdout
  1  request or item could not be inspected
  2  command-line usage error

Example:
  python3 scripts/dedupe.py inspect --request examples/list-request.json

positional arguments:
  {inspect}
    inspect   write a non-mutating duplicate report

options:
  -h, --help  show this help message and exit
exit 0
```

## Reply

The skill supports text, file, record, URL, list, and skill adapters. Inspection is the default and never mutates input. Exact, normalized, and similarity candidate classes stay separate. Applying changes requires a reviewed report and explicit authority for the exact mutation plan.
