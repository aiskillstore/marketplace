# File Search Quick Reference

## Supported Commands

- `rg --files --glob "<pattern>" <path>`: list matching files.
- `rg "<regex>" <path>`: search content by regex.
- `rg -C <n> "<regex>" <path>`: include context lines.
- `rg --type <type> "<regex>" <path>`: restrict matches by file type.

## Validation Rules

- Confirm `rg` is installed before running any search command.
- Confirm the requested path exists and is readable.
- Confirm the file glob, regex, and file type filters are explicit.
- Report zero matches as a valid outcome instead of treating it as an error.
