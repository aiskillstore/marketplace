---
name: file-management
description: Organize, back up, compress, split, and merge files/folders using rule-driven plans; use when you need safe previews, conflict handling, and verification before executing file operations.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# File Management

## When to Use

- You need to **reorganize a directory** (move/copy/rename) based on include/exclude patterns and a target folder structure.
- You want a **repeatable backup workflow** (copy or archive) with optional retention rules and verification manifests.
- You need to **compress** a folder or a set of files to reduce size or package deliverables.
- You must **split very large files** into fixed-size parts for transfer/storage limits (binary-safe).
- You need to **merge previously split parts** back into the original file reliably (binary-safe).

## Key Features

- **Safety-first planning**: generate a preview/manifest of intended actions before writing changes.
- **Rule-driven scope control**: root path + include/exclude patterns + thresholds + target structure (see `references/rule-schema.md`).
- **Conflict handling**: default to skip/rename on collisions; overwrite only with explicit confirmation.
- **Non-destructive defaults**: avoid deletion unless explicitly requested.
- **Verification support**: compare counts/sizes and optionally generate hashes for critical backups.
- **Binary-safe split/merge**: split by fixed size and merge parts without corrupting binary data (`scripts/`).

## Dependencies

- PowerShell 5.1+ (Windows PowerShell) or PowerShell 7+
  - Cmdlets used: `Get-ChildItem`, `Copy-Item`, `Move-Item`, `Compress-Archive`, `Get-FileHash`
- Python 3.8+ (for split/merge scripts)
  - `scripts/split_file.py`
  - `scripts/merge_parts.py`

## Example Usage

### 1) Organize files with a preview plan (PowerShell)

```powershell
# Inputs (adjust to your case)
$Root = "D:\Inbox"
$Target = "D:\Organized"
$Include = @("*.pdf","*.docx")
$ExcludeDirs = @("node_modules",".git")
$WhatIf = $true  # set to $false to execute

# Build a manifest (preview plan)
$files = Get-ChildItem -Path $Root -Recurse -File |
  Where-Object {
    ($Include | ForEach-Object { $_ }) -contains $_.Extension -eq $false
  }

# Practical include filter (simple example)
$files = Get-ChildItem -Path $Root -Recurse -File -Include $Include

# Exclude directories by path segment
$files = $files | Where-Object {
  $p = $_.FullName
  -not ($ExcludeDirs | Where-Object { $p -match [regex]::Escape("\$_\") })
}

$plan = foreach ($f in $files) {
  # Example target structure: by extension
  $ext = $f.Extension.TrimStart(".").ToLower()
  $destDir = Join-Path $Target $ext
  $destPath = Join-Path $destDir $f.Name

  [pscustomobject]@{
    Source = $f.FullName
    Destination = $destPath
    Action = "Copy"  # start with Copy; switch to Move after verification
  }
}

# Preview
$plan | Format-Table -AutoSize

# Execute (safe defaults: create dirs; do not overwrite unless you decide to)
foreach ($item in $plan) {
  $destDir = Split-Path $item.Destination -Parent
  if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir | Out-Null }

  if (Test-Path $item.Destination) {
    # Default conflict strategy: rename
    $base = [IO.Path]::GetFileNameWithoutExtension($item.Destination)
    $ext  = [IO.Path]::GetExtension($item.Destination)
    $dir  = Split-Path $item.Destination -Parent
    $item.Destination = Join-Path $dir ("{0}_{1}{2}" -f $base, (Get-Date -Format "yyyyMMddHHmmss"), $ext)
  }

  if ($item.Action -eq "Copy") {
    Copy-Item -LiteralPath $item.Source -Destination $item.Destination -WhatIf:$WhatIf
  } else {
    Move-Item -LiteralPath $item.Source -Destination $item.Destination -WhatIf:$WhatIf
  }
}
```

### 2) Backup + hash manifest (PowerShell)

```powershell
$Source = "D:\Project"
$BackupRoot = "E:\Backups"
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = Join-Path $BackupRoot ("Project_{0}" -f $Stamp)

# Copy backup
Copy-Item -Path $Source -Destination $BackupDir -Recurse

# Create a hash manifest for verification
$manifestPath = Join-Path $BackupDir "hash-manifest.sha256.txt"
Get-ChildItem -Path $BackupDir -Recurse -File |
  ForEach-Object {
    $h = Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName
    "{0}  {1}" -f $h.Hash, ($_.FullName.Substring($BackupDir.Length + 1))
  } | Set-Content -Encoding UTF8 $manifestPath
```

### 3) Compress a folder (PowerShell)

```powershell
$SourceDir = "D:\Project"
$ZipPath = "E:\Archives\Project.zip"

Compress-Archive -Path (Join-Path $SourceDir "*") -DestinationPath $ZipPath -Force
```

### 4) Split and merge a large file (Python)

```bash
# Split into 100MB parts (binary-safe)
python scripts/split_file.py --input "E:\ISO\big.iso" --part-size 100MB --output-dir "E:\ISO\parts"

# Merge parts back (binary-safe)
python scripts/merge_parts.py --input-dir "E:\ISO\parts" --output "E:\ISO\big.iso"
```

> Note: CLI flags may vary depending on the scripts’ implementation. If the scripts do not expose flags, adapt the commands to match their actual parameters.

## Implementation Details

- **Rule schema and planning**
  - Prefer structured rules to define:
    - `rootPath`
    - include/exclude patterns (glob-like)
    - optional size thresholds (e.g., split if `> N MB`)
    - target structure mapping (e.g., by extension/date/project)
    - conflict strategy (`skip`, `rename`, `overwrite`)
  - Use `references/rule-schema.md` as the canonical format for describing these rules.

- **Preview-first execution**
  - Generate a **manifest/plan** listing `(source, destination, action)` before any write operation.
  - Use PowerShell `-WhatIf` (or an explicit “dry run” mode) to validate the plan.

- **Conflict handling**
  - Default behavior should be **non-destructive**:
    - If destination exists: **rename** (append timestamp or counter) or **skip**
    - Only **overwrite** after explicit user confirmation

- **Verification**
  - Basic checks: file counts and total sizes before/after.
  - Strong checks for critical backups: `SHA256` via `Get-FileHash`, stored as a manifest for later validation.

- **Binary-safe splitting/merging**
  - Splitting should read/write raw bytes in fixed-size chunks (no text encoding).
  - Merging should concatenate parts in deterministic order (e.g., numeric suffix ordering) to reproduce the original byte stream exactly.