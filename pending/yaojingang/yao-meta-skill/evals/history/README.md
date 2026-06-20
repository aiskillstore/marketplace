# Regression History Snapshots

This directory stores milestone-level regression snapshots.

Each snapshot records:

- date
- label
- trigger-suite summary
- route-summary when route confusion tracking is active
- enabled quality gates
- governance score when available
- governed example count
- notable milestone notes

Use `python3 scripts/render_regression_history.py` to rebuild the markdown report in `reports/regression_history.md`.
