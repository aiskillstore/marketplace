# Script Policy

Scripts should be deterministic, non-destructive by default, and reviewable.

Minimum expectations:

- expose a command-line entrypoint or clear function boundary
- prefer `argparse` and `--help` for operator-facing scripts
- keep `python3 scripts/name.py --help` safe, non-mutating, and fast enough for trust smoke checks
- avoid hidden interactive prompts unless the command is explicitly interactive
- state network or filesystem side effects in nearby docs or trust metadata
- declare allowed network hosts in `security/network_policy.json` before team distribution
- emit structured JSON when used by `scripts/yao.py`
