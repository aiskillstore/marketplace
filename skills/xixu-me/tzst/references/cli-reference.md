# tzst CLI Reference

This reference is for the `tzst` CLI only. It is grounded in the upstream README plus `src/tzst/cli.py`; if those disagree, trust the CLI source.

## Install and Preflight

```bash
tzst --version
tzst --help
uv tool install tzst
pip install tzst
```

If the user wants a standalone binary instead of a Python install, use the release assets at <https://github.com/xixu-me/tzst/releases/latest>.

## Command Matrix

| Goal                    | Command                        | Key flags                                                | Notes                                                                 |
| ----------------------- | ------------------------------ | -------------------------------------------------------- | --------------------------------------------------------------------- |
| Create archive          | `tzst a archive.tzst files...` | `-c`, `-l`, `--level`, `--no-atomic`                     | Aliases: `add`, `create`. Default compression level is `3`.           |
| Extract with paths      | `tzst x archive.tzst`          | `-o`, `--streaming`, `--filter`, `--conflict-resolution` | Preserve directory structure. Preferred default for extraction.       |
| Extract flat            | `tzst e archive.tzst`          | `-o`, `--streaming`, `--filter`, `--conflict-resolution` | Use only when flattening is explicitly wanted. Alias: `extract-flat`. |
| List contents           | `tzst l archive.tzst`          | `-v`, `--streaming`                                      | Alias: `list`.                                                        |
| Test integrity          | `tzst t archive.tzst`          | `--streaming`                                            | Alias: `test`.                                                        |
| Machine-readable output | `tzst --json --no-banner ...`  | `--json`, `--no-banner`                                  | Prefer for scripts and automation.                                    |

## Safety Defaults

- Use `x` before `e` unless the user clearly wants flattened output.
- Keep `--filter data` as the extraction default.
- Keep atomic creation enabled by default. `--no-atomic` is an exception, not the normal path.
- Prefer `--streaming` for large archives or constrained memory.
- For automated extraction, set an explicit `--conflict-resolution` value instead of relying on the interactive default.

## Security Filters

| Filter          | Use When                                                          | Notes                                                     |
| --------------- | ----------------------------------------------------------------- | --------------------------------------------------------- |
| `data`          | Default choice for normal extraction                              | Safest option. Good for untrusted archives.               |
| `tar`           | The user needs standard tar compatibility                         | Less strict than `data`, but still safer than full trust. |
| `fully_trusted` | Only when the archive source is explicitly and completely trusted | Never recommend this by default.                          |

## Conflict Resolution

Use these values with `x` or `e`:

- `replace`
- `skip`
- `replace_all`
- `skip_all`
- `auto_rename`
- `auto_rename_all`
- `ask`

Guidance:

- `ask` is the interactive default for humans.
- For automation, prefer an `_all` value so the command cannot block on prompts.
- When using `--json`, do not rely on `ask`; choose an explicit non-interactive value.

## Copy-Paste Examples

```bash
# Create an archive with the default atomic behavior
tzst a backup.tzst documents/ photos/ config.json

# Create with higher compression
tzst a backup.tzst documents/ -l 10

# Extract while preserving paths
tzst x backup.tzst -o restore/

# Extract specific members
tzst x backup.tzst config.json docs/readme.md -o restore/

# Extract flat into one directory
tzst e backup.tzst -o flat/

# List contents with details
tzst l backup.tzst -v

# Test a large archive with streaming
tzst t backup.tzst --streaming

# Extract with the safest filter and streaming mode
tzst x backup.tzst -o restore/ --filter data --streaming

# Automated extraction with an explicit conflict policy
tzst x backup.tzst -o restore/ --conflict-resolution replace_all

# Machine-readable list output for scripts
tzst --json --no-banner l backup.tzst

# Machine-readable extract output with non-interactive conflict handling
tzst --json --no-banner x backup.tzst -o restore/ --conflict-resolution auto_rename_all
```

## Exit Codes

| Exit Code | Meaning                                                           |
| --------- | ----------------------------------------------------------------- |
| `0`       | Success                                                           |
| `1`       | General operation error such as missing files or archive failures |
| `2`       | Argument parsing or invalid flag error                            |
| `130`     | Interrupted by the user                                           |
