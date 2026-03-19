# Troubleshooting

## UNO import fails after setting `PYTHONPATH`

Symptom examples:

- `ModuleNotFoundError: No module named 'uno'`
- Writer imports work, but opening a document fails before LibreOffice starts

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
PYTHONPATH="skills/libreoffice-writer/scripts:/usr/lib/python3/dist-packages" python3 your_script.py
```

If your platform uses a different LibreOffice Python location, use that path
instead.

## Patch result says `document_persisted = false`

Meaning:

- `document_persisted` reports whether the patch mutations currently exist in a
  saved document state.
- Standalone `writer.patch(...)` saves the file when successful mutations should
  persist.
- `session.patch(...)` reports `true` when the session now holds successful
  in-memory mutations, even before the session is later closed and stored.

## Target matching feels brittle

Recommendations:

1. Anchor text targets with full sentences or paragraph-sized phrases, not
   single words.
2. Add `after` and `before` when the same wording may appear elsewhere.
3. Use `occurrence` only when repeated matches are intentional and stable.
