# Runtime Checklist

- Category: `Data Analysis`
- Validate the user goal, required inputs, and output format before taking action.
- Ask a targeted clarification question when a required input is missing.
- Keep the response scoped to the documented workflow and state assumptions explicitly.
- Run a non-destructive smoke check before any file-dependent or data-dependent command.
- Recommended smoke check: `python -m py_compile scripts/main.py`
- If execution fails, stop and return a concise recovery path instead of fabricating results.
