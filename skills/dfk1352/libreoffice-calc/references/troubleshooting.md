# Troubleshooting

## UNO import fails after setting `PYTHONPATH`

Symptom examples:

- `ModuleNotFoundError: No module named 'uno'`
- Calc imports work, but opening a spreadsheet fails before LibreOffice starts

Cause:

- `PYTHONPATH=<skill_base_dir>/scripts` exposes the bundled skill modules, but
  some environments still need the system LibreOffice Python packages on the
  Python import path.

What to check:

1. LibreOffice is installed on the machine.
2. The Python process can import `uno`.
3. If `uno` is missing, add the distro LibreOffice Python path before running
   your script. A common Linux path is `/usr/lib/python3/dist-packages`.

Example:

```bash
PYTHONPATH="skills/libreoffice-calc/scripts:/usr/lib/python3/dist-packages" python3 your_script.py
```

If your platform uses a different LibreOffice Python location, use that path
instead.

## Patch result says `document_persisted = false`

Meaning:

- `document_persisted` reports whether the patch mutations currently exist in a
  saved spreadsheet state.
- Standalone `calc.patch(...)` saves the file when successful mutations should
  persist.
- `session.patch(...)` reports `true` when the session now holds successful
  in-memory mutations, even before the session is later closed and stored.

## Chart follow-up targeting feels unclear

Recommendations:

1. When `create_chart()` sets `title`, reuse that same string as the most
   stable later chart target name.
2. Use `CalcTarget(kind="chart", sheet=..., name=...)` when the chart title or
   assigned name is known.
3. Use chart `index` only when chart order is stable and intentional.
