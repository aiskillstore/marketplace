# Troubleshooting

## UNO import fails after setting `PYTHONPATH`

Symptom examples:

- `ModuleNotFoundError: No module named 'uno'`
- Impress imports work, but opening a presentation fails before LibreOffice starts

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
PYTHONPATH="skills/libreoffice-impress/scripts:/usr/lib/python3/dist-packages" python3 your_script.py
```

If your platform uses a different LibreOffice Python location, use that path
instead.

## Snapshot export differs slightly from requested size

Meaning:

- PNG exports can differ by a small amount from the requested width and height.
- Treat the snapshot as a layout-verification artifact, not as an exact pixel
  contract.

## Slide indices behave unexpectedly

Recommendations:

1. Impress slide indices are zero-based.
2. Re-check indices after adding, deleting, or moving slides.
3. Prefer reading slide inventory when a workflow mutates deck order.
