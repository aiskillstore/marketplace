---
name: file-security-toolkit
description: Encrypt/decrypt local files, redact sensitive information in documents, and validate password strength when handling private data or preparing files for sharing.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# File Security Toolkit

## When to Use

- Use this skill when you need encrypt/decrypt local files, redact sensitive information in documents, and validate password strength when handling private data or preparing files for sharing in a reproducible workflow.
- Use this skill when a others task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/file_security.py` is the most direct path to complete the request.
- Use this skill when you need the `file-security-toolkit` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Encrypt/decrypt local files, redact sensitive information in documents, and validate password strength when handling private data or preparing files for sharing.
- Packaged executable path(s): `scripts/file_security.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Others/file-security-toolkit"
python -m py_compile scripts/file_security.py
python scripts/file_security.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/file_security.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/file_security.py`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## 1. When to Use
Use this skill when you need to:

- Encrypt and archive a folder (or multiple files) into a password-protected ZIP (AES-256) before sharing or storing.
- Encrypt a single file with a password (without creating a ZIP archive).
- Redact sensitive information (e.g., emails, phone numbers, IDs) from documents before distribution.
- Validate whether a password meets basic strength requirements before using it for encryption.

## 2. Key Features
- **ZIP AES-256 encryption/decryption** for files and folders (`zip-encrypt`, `zip-decrypt`).
- **Single-file password encryption/decryption** (`file-encrypt`, `file-decrypt`).
- **Privacy redaction** for common document formats (`redact`):
  - Supported: `txt`, `md`, `csv`, `docx`, `pptx`
  - Detects and removes/masks: email addresses, phone numbers, ID numbers, and name/address keywords.
- **Password strength checking** (`check-password`) based on simple composition rules.
- **Local-only processing**: operates on user-specified paths; no network access.

## 3. Dependencies
Install dependencies with:

```bash
python -m pip install pyzipper cryptography python-docx python-pptx pillow
```

> Python version is not specified in the source document. Ensure your environment supports the listed packages.

## 4. Example Usage
Entry point script:

```bash
python scripts/file_security.py --help
```

### Check password strength
```bash
python scripts/file_security.py check-password --password "Abcdefg1"
```

### Encrypt / decrypt a single file
```bash
python scripts/file_security.py file-encrypt \
  --input sample.txt \
  --output sample.txt.enc \
  --password "Abcdefg1"

python scripts/file_security.py file-decrypt \
  --input sample.txt.enc \
  --output sample_out.txt \
  --password "Abcdefg1"
```

### Encrypt / decrypt a folder or files as ZIP (AES-256)
```bash
python scripts/file_security.py zip-encrypt \
  --input ./my_folder \
  --output ./my_folder.zip \
  --password "Abcdefg1"

python scripts/file_security.py zip-decrypt \
  --input ./my_folder.zip \
  --output ./my_folder_out \
  --password "Abcdefg1"
```

### Redact sensitive information in documents
```bash
python scripts/file_security.py redact \
  --input ./docs/input.docx \
  --output ./docs/input.redacted.docx
```

## 5. Implementation Details

### Commands and behavior
- **`zip-encrypt` / `zip-decrypt`**
  - Creates or extracts a ZIP archive using **AES-256** encryption.
  - Intended for encrypting **multiple files or folders** as a single archive.
- **`file-encrypt` / `file-decrypt`**
  - Encrypts/decrypts the contents of **one file** using a user-provided password.
  - Output is written to the specified path; the original file is not modified unless you overwrite it.
- **`redact`**
  - Processes supported file types: `txt`, `md`, `csv`, `docx`, `pptx`.
  - Applies redaction rules targeting:
    - Email addresses
    - Phone numbers
    - ID numbers
    - Name/address keywords
  - Produces a redacted output file at the specified location.
- **`check-password`**
  - Validates password strength using basic rules:
    - Length **>= 8**
    - Contains **uppercase** letters
    - Contains **lowercase** letters
    - Contains **numbers**

### Security constraints (operational)
- **No network access**: the script only processes local files.
- **Path-scoped I/O**: reads only from user-provided input paths and writes only to user-provided output paths.
- **No sensitive logging**: avoids printing raw document content to logs.
- **No credential retention**: does not store passwords/keys.
