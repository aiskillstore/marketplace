# Audit Reference

## Supported Scope

- Support DICOM metadata anonymization with explicit tag handling and audit-log guidance.
- Support single-file and batch-processing workflows when inputs and dependencies are available.
- Keep outputs bounded to de-identification assistance rather than institutional compliance sign-off.

## Stable Audit Commands

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
python scripts/smoke_test.py
```

## Fallback Boundaries

- If no valid DICOM input or output path is available, stop and ask for the required paths.
- If `pydicom` is unavailable, report the dependency gap and provide a manual anonymization checklist.
- If the user asks for guarantees about release readiness, state that institutional QA is still required.

## Output Guardrails

- Separate metadata anonymization from pixel-data risks.
- Keep preserved tags and removed tags explicit.
- Call out manual QA for burned-in annotations, private tags, and downstream release checks.
