# Rule Format (Simplified Version)

A compact structured format for describing organization/backup rules, designed for easy execution and reuse.

## Example

```
root: "D:/Projects"
mode: "copy"           # copy | move
conflict: "rename"     # rename | skip | overwrite
include_ext: [".pdf", ".docx", ".xlsx"]
exclude_glob: ["**/node_modules/**", "**/.git/**"]
rules:
  - name: "reports"
    match_name: "*report*"
    target: "Sorted/Reports"
    rename: "{stem}_{yyyy}-{mm}-{dd}{ext}"
  - name: "images"
    include_ext: [".png", ".jpg", ".jpeg"]
    target: "Sorted/Images/{yyyy}/{mm}"
backup:
  enabled: true
  destination: "D:/Backups/Projects"
  archive: true
  retain_latest: 5
split:
  enabled: true
  min_size_mb: 500
  part_size_mb: 100
```

## Field Descriptions

- `root`: Root directory
- `mode`: Prefer `copy` for the first execution; use `move` after verification
- `conflict`: Defaults to `rename` or `skip`; `overwrite` requires user confirmation
- `rules`: Ordered matching; defaults to the first match if not specified
- `rename`: Available variables: `{stem}`, `{ext}`, `{yyyy}`, `{mm}`, `{dd}`