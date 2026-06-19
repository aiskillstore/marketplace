# Description Drift Snapshots

This directory stores description-optimization snapshots.

Each snapshot records:

- date
- label
- per-target winner token counts
- visible holdout errors
- blind holdout errors when available
- judge-backed blind holdout errors and agreement when available
- adversarial holdout errors when available
- calibration summaries for blind and adversarial gates when available
- family coverage summaries for blind and adversarial gates when available
- short drift notes for route wording changes or new acceptance gates

Use `python3 scripts/render_description_drift_history.py` to rebuild `reports/description_drift_history.md`.
