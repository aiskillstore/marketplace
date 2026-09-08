# Inspector Output Schema

Use this reference when interpreting `scripts/inspect_skill_package.py --json` output, debugging findings, or integrating the inspector into a release gate or CI-style workflow.

The inspector is deterministic evidence collection, not the full audit. Always combine it with manual review of `SKILL.md`, resources, pressure tests, simulations, and the grading rubric.

## Top-Level Fields

| Field | Meaning |
|---|---|
| `schema_version` | Integer JSON-contract version. Version `6` replaces raw parsed frontmatter with a redacted structural summary. Version `5` added cross-platform path-policy evidence for ZIP and direct-folder inputs. Consumers requiring redacted frontmatter output must require version 6 or later. |
| `input` | Original path passed to the inspector, or an audit-local opaque display ID when sensitive. Never use an opaque ID as proof of candidate identity. |
| `input_exists` | Whether the path exists. |
| `input_type` | One of `zip`, `directory`, or `other`. |
| `target` | Backward-compatible requested target spelling. For supported profiles it matches `requested_target` and `canonical_target`. |
| `requested_target` | Exact target spelling supplied to `--target`. |
| `canonical_target` | Canonical profile actually evaluated: `portable` or `openai`. |
| `target_alias_used` | `false` for the supported profiles. Retained for schema compatibility. |
| `target_deprecation_note` | Reserved schema field; `null` for the supported profiles. |
| `target_profile` | Non-finding summary of the active profile's layout requirements and documented product upload limit, if one is known. |
| `summary` | Backward-compatible machine summary with `status`, `strict_pass`, finding counts, and finding codes. Present in JSON output for release gates and CI integrations. |
| `unpack_error` | Error string when the input cannot be safely unpacked or inspected. |
| `zip_bytes` | Size of the uploaded ZIP, when the input is a ZIP file. |
| `detected_root` | Local diagnostic path treated as the Skill root, or `null` when no safe root is available. This path is not stable across ZIP extractions because they use a temporary directory. |
| `detected_root_relative` | Stable POSIX path from the inspected package root to `detected_root` (for example `skill-forge` or `.`), or `null` when no safe root is available. Prefer this field in automation. |
| `coverage_complete` | Whether secret and dangerous-command safety scans completely covered all eligible installable content. A strict or release-gate pass requires `true`. ZIP inputs scan bounded members under `.git`, `node_modules`, `.venv`, caches, and metadata paths rather than skipping them. |
| `unscanned_paths` | Bounded relative evidence for paths omitted from direct-tree traversal or truncated by an explicit exploratory safety-scan cap. Normally empty for ZIP inputs. An empty list alone is not enough to claim complete coverage; check `coverage_complete`. |
| `coverage_findings` | Error findings explaining why full bounded safety coverage was not established. |
| `manifest_verification_complete` | Whether every applicable critical YAML manifest was fully parsed and verified. A strict or release-gate pass requires `true`; valid-but-unsupported YAML produces `false` without being mislabeled as malformed. |
| `unverified_manifests` | Stable relative paths of critical YAML manifests that use valid syntax outside the restricted verifier. Normally empty. |
| `excluded_directories` | Relative paths of VCS/cache directories skipped by direct-source-tree traversal for performance. Their presence produces `coverage_complete: false` and `scan_coverage_incomplete`; they are never silently skipped in ZIP inputs. |
| `tree` | Bounded list of files/directories under the detected Skill root. |
| `size_summary` | File count, total uncompressed bytes, and largest files under the detected Skill root. |
| `skill_md_files` | `SKILL.md` paths found under the detected Skill root, relative to that root. |
| `skill_md_count` | Count of `SKILL.md` files under the detected Skill root. |
| `frontmatter` | Redacted structural summary of parsed YAML frontmatter from the detected root `SKILL.md`, when available. Raw descriptions, metadata values, unknown key names, and other package-controlled scalar values are never included. |
| `frontmatter_error` | Frontmatter extraction error, if any. |
| `name_valid_hyphen_case` | Boolean check for lowercase hyphen-case Skill name. |
| `description_length` | Character count of the frontmatter description. |
| `top_level_resources` | Top-level resource folders/files such as `scripts`, `references`, `assets`, and platform metadata folders such as `agents`. |
| `resource_references` | Compatibility projection of reachable local dependencies: normalized package-relative `existing` and `missing` paths, original `unsafe` references and `unsafe_reasons`; `source_only` retains the reserved Skill Forge source-only script annotation. |
| `resource_graph` | Reachable local document graph: `documents`, `edges` with source document and 1-based line, original `reference`, normalized `target`, and `status` (`existing`, `missing`, `unsafe`); unsafe edges include `reason`. `unassessed` records omitted document/edge locations and reasons; `complete` is false whenever this list is nonempty. `text_bytes` counts inspected document bytes. |
| `orphaned_resource_candidates` | Resource files not referenced from `SKILL.md` or declared source-only. These are candidates for manual review, not automatic failures. |
| `template_marker_findings` | Files containing placeholder-like markers such as TODO or example-template text, with file and regex-pattern evidence. |
| `template_leftover_findings` | Warning findings derived from placeholder/template markers, using normal severity/code finding fields. |
| `secret_scan_note` | Reminder that secret scanning is heuristic and non-exhaustive. Eligible BOM-marked UTF-8, UTF-16, and UTF-32 text is decoded before matching so alternate Unicode encodings do not silently bypass the scan. |
| `dangerous_command_findings` | Findings for high-confidence destructive commands in bundled shell, PowerShell, Windows batch, Python, and JavaScript/TypeScript scripts. Findings inside or outside the Skill root are errors. |
| `dangerous_command_note` | Reminder that dangerous-command scanning is heuristic and non-exhaustive across shell, PowerShell, Windows batch, Python, and JavaScript/TypeScript, but high-confidence findings and executable code outside the root fail strict validation. |
| `strict_mode_note` | Summary of how `--strict` treats error-level findings, incomplete scan coverage, and unverified critical manifests. |
| `effective_limits` | Safety, scan, and output limits used for this run. `max_input_zip_bytes`, `inspector_input_zip_limit_bytes`, and the retained `skill_upload_limit_bytes` compatibility field are Skill Forge safety boundaries; `target_product_upload_limit_bytes` is a documented host limit when available. |

## Schema 6 Frontmatter Migration

Schema 5 exposed the complete parsed frontmatter mapping. Schema 6 deliberately
replaces it with bounded structural evidence. Consumers must use
`frontmatter.validated_name`, `present_keys`, `value_types`,
`unrecognized_key_count`, and `description_length`; they must not expect
description text, dependency values, nested metadata, or unknown key names.

`validated_name` is non-null only after the selected target's name shape and
length checks pass and no high-confidence secret or PII shape is detected.
`present_keys` and `value_types` cover recognized top-level
keys only. Unknown keys and all parser-controlled internal markers are reduced
to counts or separate findings. The top-level `description_length` field is
retained for compatibility and matches `frontmatter.description_length`.

## Public Output Privacy Boundary

After deriving findings and the machine summary from raw validation data, the
inspector creates a presentation copy. All string values and dictionary keys
are checked for the same high-confidence secret and PII patterns used by the
frontmatter public-value policy. A matching string is replaced in full with an
audit-local opaque ID such as `[redacted-0001]`. This includes input paths,
directory and ZIP member names, resource-reference keys, and error messages.
JSON, Markdown, early inspection results, and argument-error diagnostics use
this boundary. Detection remains heuristic; an unchanged string is not proof
that it contains no sensitive information.

Repeated identical strings receive the same ID within one audit; different
strings receive distinct IDs, with literal-ID collisions avoided. IDs are not
cross-audit identifiers, content hashes, filesystem paths, or evidence bindings.
No raw-to-public mapping is emitted. Normal strings, machine field names,
finding codes, counts, booleans, and enums retain their existing schema-6
meaning. The raw validation object remains unchanged.

The package verifier consumes the unchanged summary and strict-exit contract.
The independent evaluator still requires exact equality with its neutral
scratch candidate path; redacted or unrelated reported input paths fail that
binding check. Sensitive original candidate names can be evaluated through the
existing pinned scratch copy, without treating matching display IDs as identity.

## Summary Field

The top-level `summary` object is retained for compatibility with release-gate and CI integrations. Exit codes are still the canonical machine signal for command success or failure, but JSON consumers may read `summary.status` or `summary.strict_pass` without walking every finding section.

| Field | Meaning |
|---|---|
| `status` | `pass` when the input exists, unpacking/inspection succeeded, safety coverage and manifest verification are complete, and no error-severity findings were found; otherwise `fail`. |
| `strict_pass` | Boolean equivalent of the JSON summary pass condition. It is always `false` when safety coverage or critical-manifest verification is incomplete. |
| `error_count` | Number of error-severity findings in inspector-owned severity-bearing sections. |
| `warning_count` | Number of warning-severity findings in inspector-owned severity-bearing sections. |
| `finding_count` | Total number of severity/code findings across all sections, including info findings. |
| `finding_codes` | Sorted unique finding codes found recursively in the output. |

## Finding Fields

Most findings use this shape:

```json
{
  "severity": "error",
  "code": "frontmatter_invalid_name",
  "message": "frontmatter name should be lowercase hyphen-case",
  "file": "SKILL.md"
}
```

Common properties:

| Property | Meaning |
|---|---|
| `severity` | `error`, `warning`, or `info`. Error findings fail `--strict`; warnings and info findings do not. |
| `code` | Stable machine-readable identifier. Audit reports may cite this code. |
| `message` | Human-readable explanation. |
| `file` | Relative file path when applicable. |
| `limit`, `bytes`, `compressed_bytes`, `crc32`, `ratio`, `risk`, `pattern` | Optional evidence fields for size, compression, directory-stream identity, and secret findings. |
| `expected` | Optional safe evidence for name/directory findings. For `zip_missing_top_level_skill_folder`, `expected` is the validated, non-sensitive skill name the archive's top-level folder should have used, or `null` when that value was suppressed. |
| `keys`, `key_count`, `length`, `normalized_path`, `conflicts_with` | Optional evidence for recognized frontmatter keys, redacted unknown-key counts, length findings, and ZIP identity findings. `conflicts_with` identifies the earlier colliding member path. |

## Severity-Bearing Finding Sections

The inspector can place severity-bearing findings in these sections:

<!-- inspector-severity-sections:start -->
- `zip_preflight_findings`
- `directory_preflight_findings`
- `coverage_findings`
- `outside_root_findings`
- `secret_risk_findings`
- `platform_metadata_findings`
- `agent_metadata_findings` (backward-compatible alias for OpenAI metadata findings)
- `package_size_findings`
- `frontmatter_validation_findings`
- `structural_findings`
- `template_leftover_findings`
- `dangerous_command_findings`
<!-- inspector-severity-sections:end -->

Only the inspector-owned sections listed above contribute to summaries, markdown finding lists, or `--strict`. Parsed frontmatter and other package-controlled data never become findings merely by containing `severity` and `code` keys. Findings surfaced under more than one listed key (such as the `platform_metadata_findings` / `agent_metadata_findings` alias, which share one list object) are counted once, by object identity.

## Configurable Limits

The inspector uses conservative defaults for normal Skill audits and includes the active values in `effective_limits`. Override them only for CI policy enforcement, targeted regression tests, or unusual legitimate packages.

<!-- inspector-limits-table:start -->
| CLI flag | JSON field | Default | Meaning |
|---|---|---:|---|
| `--tree-limit` | `tree_limit` | `200` | Maximum tree entries included in output. |
| `--max-zip-members` | `max_zip_members` | `1000` | Maximum ZIP entries. |
| `--max-zip-uncompressed-bytes` | `max_zip_uncompressed_bytes` | `104857600` | Maximum total uncompressed ZIP bytes. |
| `--max-zip-member-bytes` | `max_zip_member_bytes` | `26214400` | Maximum uncompressed bytes for one ZIP member. |
| `--max-directory-files` | `max_directory_files` | `1000` | Maximum files in a direct folder input. |
| `--max-directory-entries` | `max_directory_entries` | `5000` | Maximum total directory entries in a direct folder input. |
| `--max-directory-depth` | `max_directory_depth` | `32` | Maximum directory nesting depth in a direct folder input. |
| `--max-directory-entries-per-directory` | `max_directory_entries_per_directory` | `1000` | Maximum entries in any one direct-input directory. |
| `--max-directory-total-bytes` | `max_directory_total_bytes` | `104857600` | Maximum total bytes in a direct folder input. |
| `--max-directory-file-bytes` | `max_directory_file_bytes` | `26214400` | Maximum bytes for one direct-folder file. |
| `--max-compression-ratio` | `max_compression_ratio` | `100.0` | Maximum allowed ZIP member compression ratio. It applies to every non-empty member; finite positive values only. |
| `--max-input-zip-bytes` | `max_input_zip_bytes` | `30000000` | Pre-open ZIP safety boundary. It is explicitly configurable and separate from documented host upload limits. |
| `--max-read-bytes` | `max_read_bytes` | `1000000` | Maximum bytes read for bounded display/template scans. It does not limit safety scans or critical manifests. |
| `--max-safety-scan-bytes` | `max_safety_scan_bytes` | `null` | Explicit exploratory cap for each eligible secret/dangerous-command scan. Any truncation emits an info finding and makes coverage incomplete, so strict validation exits 2. |
| derived | `safety_scans_read_full_eligible_files` | `true` | `true` when no exploratory safety cap was requested; eligible files are then read completely within the package preflight limits. |
| derived | `inspector_input_zip_limit_bytes` | `30000000` | Active Skill Forge pre-open ZIP safety boundary; not a platform upload claim. |
| derived | `skill_upload_limit_bytes` | `30000000` | Backward-compatible name for the same Skill Forge pre-open ZIP safety boundary; never a platform upload claim. |
| derived | `target_product_upload_limit_bytes` | `null` | No supported profile currently encodes a documented product upload limit. |
<!-- inspector-limits-table:end -->

### Effective Limits Field Contract

`effective_limits` always records the values actually used, including derived
context that distinguishes inspector resource bounds from a host product
upload limit.

<!-- inspector-effective-limits:start -->
| Field | Source |
|---|---|
| `max_zip_members` | Active ZIP member limit. |
| `max_zip_uncompressed_bytes` | Active total ZIP expansion limit. |
| `max_zip_member_bytes` | Active per-ZIP-member limit. |
| `max_directory_files` | Active direct-folder file limit. |
| `max_directory_entries` | Active direct-folder entry limit. |
| `max_directory_depth` | Active direct-folder nesting limit. |
| `max_directory_entries_per_directory` | Active per-directory entry limit. |
| `max_directory_total_bytes` | Active direct-folder total-byte limit. |
| `max_directory_file_bytes` | Active direct-folder file-byte limit. |
| `max_compression_ratio` | Active ZIP compression-ratio limit. |
| `max_input_zip_bytes` | Active pre-open ZIP safety boundary. |
| `max_read_bytes` | Active display/template-read cap. |
| `max_safety_scan_bytes` | Optional exploratory safety-scan cap. |
| `max_resource_documents` | Reachable document cap, additionally bounded by package file limits. |
| `max_resource_edges` | Reachable dependency edge cap. |
| `max_resource_depth` | Reachable document depth cap, additionally bounded by directory depth. |
| `max_resource_text_bytes` | Total graph document text cap, additionally bounded by package bytes. |
| `safety_scans_read_full_eligible_files` | Whether safety scans read every eligible bounded file fully. |
| `skill_upload_limit_bytes` | Retained compatibility name for the inspector ZIP safety boundary. |
| `inspector_input_zip_limit_bytes` | Explicit inspector ZIP safety boundary. |
| `tree_limit` | Active tree-output entry cap. |
| `target_product_upload_limit_bytes` | Documented selected-target product upload limit, if any. |
<!-- inspector-effective-limits:end -->

All integer custom limit values must be positive. `--max-compression-ratio` must be finite and positive: `nan`, `inf`, and `-inf` are rejected during argument parsing. Invalid values fail argument parsing before inspection. Schema version 4 keeps version 3's profile and limit data while adding fail-closed critical-manifest verification.

Example:

```bash
python3 scripts/inspect_skill_package.py skill.zip --json --strict --max-zip-member-bytes 50000000
```

## Strict Mode Behavior

Run strict mode with:

```bash
python3 scripts/inspect_skill_package.py /path/to/skill-or-skill.zip --json --strict
```

Exit codes:

| Exit code | Meaning |
|---:|---|
| `0` | Input exists, bounded safety coverage and critical-manifest verification are complete, and no error-severity findings were found. Warnings may still be present. |
| `1` | Input does not exist or cannot be inspected in a basic way. |
| `2` | Strict validation found an error-severity finding, could not establish complete safety-scan coverage, or could not fully verify an applicable critical YAML manifest. |

Warnings do not fail strict mode by themselves. A `*_yaml_unsupported` warning is paired with `manifest_verification_complete: false`, so valid-but-unverified critical YAML cannot strict-pass without being mislabeled malformed. Other warning examples include benign outside-root files and suspicious filenames without high-confidence secret content. Error-level findings include incomplete safety coverage, unsafe archives, symlinks in direct folder inputs, likely bundled secrets, invalid or incompatible frontmatter, missing/multiple `SKILL.md`, directory/name mismatches, missing referenced resources, high-confidence dangerous executable commands anywhere in the Skill, and executable code outside the detected Skill root.

For ZIP inputs, the inspector scans every member that passes the configured archive bounds, including `.git`, `node_modules`, `.venv`, caches, and metadata paths. For direct source trees, non-strict inspection may skip large VCS/cache directories; it records the bounded paths and emits `scan_coverage_incomplete`. Such an output can support exploratory review, but never a strict or release-gate pass.

## Common Finding Codes

### ZIP and Archive Safety

| Code | Meaning |
|---|---|
| `zip_bad_archive` | Input is not a valid ZIP archive. |
| `zip_too_many_members` | ZIP has too many entries. |
| `zip_unsafe_member_path` | ZIP member uses an absolute path, traversal, or otherwise unsafe name. |
| `zip_nonportable_separator_member` | ZIP member uses a backslash separator, which has different path semantics across hosts. |
| `zip_control_character_member` | ZIP member path contains an unsafe control character. |
| `zip_directory_member_has_payload` | A slash-suffixed directory member declares or yields non-empty uncompressed content, or cannot be verified as an empty stream. Empty stored and deflated directory entries remain valid; compressed size alone is not a rejection signal. |
| `zip_windows_ads_member` | A ZIP path segment contains a colon and could address a Windows alternate data stream. |
| `zip_windows_invalid_character_member` | A ZIP path segment contains `<`, `>`, `"`, `|`, `?`, or `*`, which Windows does not permit in file names. |
| `zip_windows_trailing_dot_space_member` | A ZIP path segment ends in a space or period, which Windows ignores. |
| `zip_windows_reserved_name_member` | A ZIP path segment uses a Windows device basename such as `CON`, `NUL`, `COM1`, or `LPT1`, including with an extension. |
| `zip_path_component_too_long` | A ZIP path segment exceeds the 255-byte UTF-8 or 255-code-unit UTF-16 portability boundary. |
| `zip_path_too_long` | A ZIP relative path exceeds Skill Forge's conservative 240 UTF-16-code-unit extraction policy. This is a portability policy, not a vendor limit guarantee. |
| `zip_duplicate_member` | ZIP contains the same normalized member path more than once. |
| `zip_case_collision_member` | Two members collide case-insensitively (for example `File.txt` and `file.txt`). |
| `zip_unicode_normalization_collision_member` | Two members collide after Unicode NFC normalization (for example NFC and NFD spellings of `café`). |
| `zip_unicode_casefold_collision_member` | Two members collide only after both Unicode NFC normalization and case-folding. |
| `zip_file_directory_prefix_conflict_member` | A file member is also the parent path of another member, so no portable filesystem layout can represent both. |
| `zip_encrypted_member` | ZIP member is encrypted. |
| `zip_symlink_member` | ZIP member is a symlink. |
| `zip_unsupported_member_type` | ZIP member uses a special POSIX type such as a FIFO, device, or socket rather than a normal file or directory. |
| `zip_member_too_large` | A ZIP member exceeds the configured per-file limit. |
| `zip_uncompressed_size_too_large` | Total ZIP uncompressed size exceeds the configured limit. |
| `zip_high_compression_ratio` | A member has suspiciously high compression ratio. |
| `zip_zero_compressed_size` | A non-empty ZIP member has zero compressed size, which is suspicious or malformed. |
| `zip_missing_top_level_skill_folder` | The archive has no top-level folder named after the skill; `SKILL.md` sits at the archive root. Warning; `expected` carries the intended folder name. |
| `zip_read_error` | The ZIP could not be read from disk (I/O or stat error). |
| `package_zip_too_large` | The ZIP file on disk exceeds Skill Forge's pre-open inspector safety limit; the archive is refused before it is opened. It is not a platform upload-limit claim. |
| `target_upload_limit_exceeded` | Reserved finding code for a documented product upload limit. No supported profile currently emits it. |

### Direct Folder Safety

| Code | Meaning |
|---|---|
| `directory_root_symlink` | The input folder path itself is a symlink. |
| `directory_symlink_found` | A symlink exists inside the directory tree. |
| `directory_file_outside_root` | A file resolves outside the inspected root. |
| `directory_nonportable_path` | A direct-folder entry violates the shared cross-platform path policy. `path_rule` identifies the rule. It is an error for supported profiles. |
| `directory_portable_identity_collision` | Direct-folder entries collide by case-folded or Unicode-normalized identity. `identity_kind` identifies the collision. It is an error for supported profiles. |
| `directory_file_directory_prefix_conflict` | A direct-folder file has the same portable identity as an ancestor directory of another entry. It is an error for supported profiles. |
| `directory_too_many_files` | Direct folder input has too many files. |
| `directory_file_too_large` | Direct folder file exceeds the configured per-file limit. |
| `directory_total_size_too_large` | Direct folder total size exceeds the configured limit. |
| `directory_root_lstat_failed` | The input folder root could not be inspected (lstat error). |
| `directory_root_resolve_failed` | The input folder root could not be resolved to a real path. |
| `package_folder_large` | A direct folder input's uncompressed size exceeds Skill Forge's generic review threshold. Warning only; it is not a platform upload-limit claim. |
| `scan_coverage_incomplete` | Bounded secret/dangerous-command safety coverage was not established. Strict inspection exits 2 and release validation must fail. |

### Root and Structure

| Code | Meaning |
|---|---|
| `skill_md_missing` | No `SKILL.md` found under detected root. |
| `skill_md_multiple` | Multiple `SKILL.md` files found under detected root. |
| `root_skill_md_missing` | Detected root does not contain `SKILL.md`. |
| `missing_resource_reference` | A reachable local instruction/reference document references a missing file. |
| `resource_graph_incomplete` | Bounded local dependency traversal could not inspect every reachable document/edge; strict inspection fails independently of safety-scan coverage. |
| `archive_directory_outside_skill_root` | Archive contains an extra directory outside the detected Skill root. |
| `archive_file_outside_skill_root` | Archive contains an extra file outside the detected Skill root. |
| `archive_executable_code_outside_skill_root` | Archive contains executable code outside the detected Skill root. Error; strict inspection fails. |

### Frontmatter and Platform Metadata

| Code | Meaning |
|---|---|
| `frontmatter_missing_or_invalid` | YAML frontmatter is missing or malformed. |
| `frontmatter_unavailable` | Frontmatter cannot be inspected because the detected root `SKILL.md` is missing. |
| `frontmatter_parse_error` | Frontmatter is malformed within the restricted YAML subset (for example duplicate keys, tags/anchors/aliases, bad indentation, unclosed values, non-finite numeric scalars, or integers beyond the verifier bound). |
| `frontmatter_yaml_unsupported` | Frontmatter uses valid YAML syntax outside the restricted parser subset or exceeds the bounded nesting verifier. It remains a warning rather than a malformed-YAML error, but marks critical-manifest verification incomplete so strict mode cannot pass. |
| `frontmatter_unexpected_keys` | Frontmatter contains keys not recognized by this portable Agent Skills inspector. |
| `frontmatter_name_missing` | `name` is absent or not a string. |
| `frontmatter_invalid_name` | `name` is not lowercase hyphen-case. |
| `frontmatter_name_too_long` | `name` exceeds the 64-character Agent Skills compatibility limit. |
| `frontmatter_name_directory_mismatch` | Skill directory name does not match the frontmatter `name`. |
| `frontmatter_description_missing` | `description` is absent or not a string. |
| `frontmatter_description_angle_brackets` | Description contains angle brackets. |
| `frontmatter_description_short` | Retired advisory code; no longer emitted. Length alone cannot establish trigger quality. |
| `frontmatter_description_weak_trigger` | Retired advisory code; no longer emitted. English keyword absence cannot establish trigger quality. |
| `frontmatter_platform_optional_keys` | Optional platform-specific frontmatter keys are present (`dependencies`, `license`, `allowed-tools`, `metadata`, `version`); info only — validate against the target host. Genuinely unknown keys are still `frontmatter_unexpected_keys`. |
| `openai_metadata_unreadable` | `agents/openai.yaml`, when present, cannot be read as text. |
| `openai_metadata_yaml_invalid` | `agents/openai.yaml` is malformed within the restricted YAML subset. |
| `openai_metadata_yaml_unsupported` | `agents/openai.yaml` uses valid YAML syntax outside the restricted parser subset or bounded nesting verifier. It remains a warning rather than a malformed-YAML error, but marks critical-manifest verification incomplete when this metadata is applicable. |
| `openai_metadata_missing_interface` | OpenAI metadata is missing interface metadata. |
| `openai_metadata_interface_invalid` | OpenAI interface metadata is not a mapping. |
| `openai_metadata_missing_display_name` | OpenAI UI display name is missing. |
| `openai_metadata_display_name_invalid` | OpenAI UI display name is not a non-empty string. |
| `openai_metadata_missing_short_description` | OpenAI UI short description is missing. |
| `openai_metadata_short_description_invalid` | OpenAI UI short description is not a non-empty string. |
| `openai_metadata_short_description_length` | OpenAI UI short description is outside the documented 25–64 character range. |
| `openai_metadata_default_prompt_invalid` | An optional OpenAI default prompt is not a non-empty string. |
| `openai_metadata_default_prompt_missing_skill_reference` | An optional OpenAI default prompt does not explicitly reference the declared frontmatter Skill name as `$skill-name`. |
| `openai_metadata_icon_path_invalid` | An optional OpenAI icon value is not a safe relative path to a regular file within the Skill directory. |
| `openai_metadata_icon_missing` | An optional OpenAI icon path does not exist. |

When `agents/openai.yaml` exists, the inspector applies these checks to both
the `openai` and `portable` profiles.

The restricted parser fully validates its supported subset, including duplicate
keys and malformed scalars, with a 64-level nesting bound. When it encounters
valid YAML outside that subset or bound, it emits an explicit
`*_yaml_unsupported` warning instead of claiming an Artifact Fail and records
the manifest as unverified. Use a full YAML-aware validator before treating
that manifest as verified. Its numeric subset accepts finite decimal and
scientific-notation floats plus base-10 integers up to 4096 digits. Non-finite
YAML float spellings and larger integers return a bounded parse finding without
echoing the target-controlled scalar. A frontmatter closing `---` must begin at column zero, so an indented
`---` inside a block scalar remains scalar content.

### Template Marker Findings

| Code | Meaning |
|---|---|
| `template_marker_found` | A text-like file contains a placeholder or template marker such as TODO, placeholder text, or generated example-resource wording. Warning only. |

### Secret Risk Findings

| Code | Meaning |
|---|---|
| `secret_suspicious_filename` | Filename suggests credentials or secrets. Warning only. |
| `secret_suspicious_filename_outside_root` | Outside-root filename suggests credentials or secrets. Warning only. |
| `secret_openai_api_key` | Possible OpenAI API key pattern. |
| `secret_provider_api_key` | Possible other provider-style API key. |
| `secret_github_fine_grained_token` | Possible GitHub fine-grained personal access token beginning with `github_pat_`. |
| `secret_github_token` | Possible GitHub token. |
| `secret_slack_token` | Possible Slack token. |
| `secret_google_service_account` | Possible Google service account JSON. |
| `secret_jwt_like_token` | Possible JWT-like token. |
| `secret_api_key_assignment` | Possible API key, token, or client secret assignment. |
| `secret_password_assignment` | Possible password assignment. Warning only. |
| `secret_private_key_block` | Possible private key block. |

Outside-root secret codes append `_outside_root`, for example `secret_openai_api_key_outside_root`.

Secret detection is heuristic and non-exhaustive. It scans common text/config formats, credential-like names, and regular files that pass bounded content sniffing. Eligible files are read completely within the package preflight limits unless `--max-safety-scan-bytes` explicitly requests exploratory partial scanning. A clean scan is not proof that no secrets exist.

| Code | Meaning |
|---|---|
| `secret_stripe_live_key` | Possible Stripe live secret or restricted key. |
| `secret_aws_access_key` | Possible AWS access key ID. |
| `secret_google_api_key` | Possible Google API key. |
| `secret_gitlab_token` | Possible GitLab personal access token. |
| `secret_scan_truncated` | An eligible file exceeded the explicit exploratory safety-scan cap; only its prefix was inspected. Info only, but `coverage_complete` becomes `false` and strict inspection exits 2. |
| `secret_scan_unreadable` | An eligible file could not be read or statted for secret scanning, so strict inspection fails rather than claiming complete coverage. |

### Dangerous Command Findings

| Code | Meaning |
|---|---|
| `script_dangerous_command` | A bundled shell, PowerShell, Windows batch, Python, or JavaScript/TypeScript script contains a high-confidence destructive command (including remote content piped/evaluated into a shell, recursive forced deletion of root/home/system paths through command or language filesystem APIs, fork bombs, raw disk writes, or `mkfs`). The finding includes detected-language evidence. Error; strict inspection fails. |
| `dangerous_command_scan_truncated` | An eligible executable script exceeded the explicit exploratory safety-scan cap; only its prefix was inspected. Info only, but `coverage_complete` becomes `false` and strict inspection exits 2. |
| `dangerous_command_scan_unreadable` | An eligible executable script could not be read or statted for dangerous-command scanning, so strict inspection fails rather than claiming complete coverage. |
| `script_dangerous_command_outside_root` | An executable script outside the detected Skill root contains a high-confidence destructive command. Error; strict inspection fails. |

Dangerous-command scanning is heuristic, non-exhaustive, and inspects bundled shell scripts (including `.command` and `.ksh`), PowerShell (`.ps1`, `.psm1`, `.psd1`), Windows batch (`.bat`, `.cmd`), Python, and JavaScript/TypeScript files. Documentation is not command-scanned merely for mentioning these commands. High-confidence matches inside or outside the detected Skill root are errors. A clean scan is not proof that a package is safe to run.

For remote-content shell pipelines, the scanner recognizes supported bare
shell targets, quoted or unquoted absolute shell paths, and bare or absolute
`env`/`command` wrappers. A downloader token that begins inside a shell string
literal or after a shell comment marker is treated as inert evidence, except
for known shell `-c`, command-substitution, backtick, and `eval`
string-execution contexts.

### Complete Machine-Checked Finding Catalog

This is the complete documented set of finding codes. The inspector rejects an
unregistered emitted code, and `validate_audit_contract.py` rejects a catalog
entry that implementation cannot emit. The topical sections above describe
their meaning.

<!-- inspector-finding-catalog:start -->
`archive_directory_outside_skill_root` `archive_executable_code_outside_skill_root` `archive_file_outside_skill_root`


`dangerous_command_scan_truncated` `dangerous_command_scan_truncated_outside_root` `dangerous_command_scan_unreadable` `dangerous_command_scan_unreadable_outside_root`

`directory_depth_exceeded` `directory_file_directory_prefix_conflict` `directory_file_outside_root` `directory_file_too_large` `directory_nonportable_path` `directory_portable_identity_collision` `directory_root_lstat_failed` `directory_root_resolve_failed` `directory_root_symlink` `directory_scan_incomplete` `directory_symlink_found` `directory_too_many_entries` `directory_too_many_entries_in_directory` `directory_too_many_files` `directory_total_size_too_large` `directory_unsupported_entry`

`frontmatter_description_too_long` `frontmatter_compatibility_invalid` `frontmatter_compatibility_too_long` `frontmatter_metadata_invalid` `frontmatter_description_angle_brackets` `frontmatter_description_missing` `frontmatter_description_short` `frontmatter_description_weak_trigger` `frontmatter_invalid_name` `frontmatter_missing_or_invalid` `frontmatter_name_directory_comparison_invalid` `frontmatter_name_directory_mismatch` `frontmatter_name_missing` `frontmatter_name_too_long` `frontmatter_parse_error` `frontmatter_platform_optional_keys` `frontmatter_unavailable` `frontmatter_unexpected_keys` `frontmatter_yaml_unsupported`

`missing_resource_reference`

`openai_metadata_default_prompt_invalid` `openai_metadata_default_prompt_missing_skill_reference` `openai_metadata_display_name_invalid` `openai_metadata_icon_missing` `openai_metadata_icon_path_invalid` `openai_metadata_interface_invalid` `openai_metadata_missing` `openai_metadata_missing_display_name` `openai_metadata_missing_interface` `openai_metadata_missing_short_description` `openai_metadata_short_description_invalid` `openai_metadata_short_description_length` `openai_metadata_unreadable` `openai_metadata_yaml_invalid` `openai_metadata_yaml_unsupported`

`package_folder_large` `package_zip_too_large` `resource_graph_incomplete` `resource_reference_outside_root` `resource_reference_unsafe` `root_skill_md_missing` `scan_coverage_incomplete` `script_dangerous_command` `script_dangerous_command_outside_root`

`secret_provider_api_key` `secret_provider_api_key_outside_root` `secret_api_key_assignment` `secret_api_key_assignment_outside_root` `secret_aws_access_key` `secret_aws_access_key_outside_root` `secret_github_fine_grained_token` `secret_github_fine_grained_token_outside_root` `secret_github_token` `secret_github_token_outside_root` `secret_gitlab_token` `secret_gitlab_token_outside_root` `secret_google_api_key` `secret_google_api_key_outside_root` `secret_google_service_account` `secret_google_service_account_outside_root` `secret_jwt_like_token` `secret_jwt_like_token_outside_root` `secret_openai_api_key` `secret_openai_api_key_outside_root` `secret_password_assignment` `secret_password_assignment_outside_root` `secret_private_key_block` `secret_private_key_block_outside_root` `secret_scan_truncated` `secret_scan_truncated_outside_root` `secret_scan_unreadable` `secret_scan_unreadable_outside_root` `secret_slack_token` `secret_slack_token_outside_root` `secret_stripe_live_key` `secret_stripe_live_key_outside_root` `secret_suspicious_filename` `secret_suspicious_filename_outside_root`

`skill_md_missing` `skill_md_multiple` `target_upload_limit_exceeded` `target_zip_root_layout_invalid` `template_marker_found`

`zip_bad_archive` `zip_case_collision_member` `zip_control_character_member` `zip_directory_member_has_payload` `zip_duplicate_member` `zip_encrypted_member` `zip_file_directory_prefix_conflict_member` `zip_high_compression_ratio` `zip_member_too_large` `zip_missing_top_level_skill_folder` `zip_nonportable_separator_member` `zip_path_component_too_long` `zip_path_too_long` `zip_read_error` `zip_symlink_member` `zip_too_many_members` `zip_uncompressed_size_too_large` `zip_unicode_casefold_collision_member` `zip_unicode_normalization_collision_member` `zip_unsafe_member_path` `zip_unsupported_member_type` `zip_windows_ads_member` `zip_windows_invalid_character_member` `zip_windows_reserved_name_member` `zip_windows_trailing_dot_space_member` `zip_zero_compressed_size`
<!-- inspector-finding-catalog:end -->

## Minimal Successful Output Example

```json
{
  "schema_version": 6,
  "target": "portable",
  "requested_target": "portable",
  "canonical_target": "portable",
  "target_alias_used": false,
  "target_deprecation_note": null,
  "target_profile": {
    "name": "portable",
    "summary": "Conservative shared Agent Skills baseline; does not prove each host-specific workflow.",
    "product_upload_limit_bytes": null,
    "directory_name_mode": "exact",
    "requires_zip_top_level_folder": false
  },
  "input_type": "zip",
  "coverage_complete": true,
  "unscanned_paths": [],
  "coverage_findings": [],
  "manifest_verification_complete": true,
  "unverified_manifests": [],
  "summary": {
    "status": "pass",
    "strict_pass": true,
    "error_count": 0,
    "warning_count": 0,
    "finding_count": 0,
    "finding_codes": []
  },
  "unpack_error": null,
  "detected_root": "/tmp/skill_inspect_x/skill-forge",
  "detected_root_relative": "skill-forge",
  "skill_md_count": 1,
  "skill_md_files": ["SKILL.md"],
  "frontmatter": {
    "redacted": true,
    "validated_name": "skill-forge",
    "present_keys": ["description", "name"],
    "value_types": {
      "description": "string",
      "name": "string"
    },
    "unrecognized_key_count": 0,
    "description_length": 175
  },
  "description_length": 175,
  "zip_preflight_findings": [],
  "directory_preflight_findings": [],
  "outside_root_findings": [],
  "frontmatter_validation_findings": [],
  "structural_findings": [],
  "secret_risk_findings": [],
  "effective_limits": {
    "tree_limit": 200,
    "max_zip_members": 1000,
    "max_zip_uncompressed_bytes": 104857600,
    "max_zip_member_bytes": 26214400,
    "max_directory_files": 1000,
    "max_directory_entries": 5000,
    "max_directory_depth": 32,
    "max_directory_entries_per_directory": 1000,
    "max_directory_total_bytes": 104857600,
    "max_directory_file_bytes": 26214400,
    "max_compression_ratio": 100.0,
    "max_input_zip_bytes": 30000000,
    "max_read_bytes": 1000000,
    "max_safety_scan_bytes": null,
    "max_resource_documents": 200,
    "max_resource_edges": 1000,
    "max_resource_depth": 32,
    "max_resource_text_bytes": 10485760,
    "safety_scans_read_full_eligible_files": true,
    "skill_upload_limit_bytes": 30000000,
    "inspector_input_zip_limit_bytes": 30000000,
    "target_product_upload_limit_bytes": null
  }
}
```

## Failed Output Example

```json
{
  "input_type": "zip",
  "summary": {
    "status": "fail",
    "strict_pass": false,
    "error_count": 1,
    "warning_count": 1,
    "finding_count": 2,
    "finding_codes": [
      "archive_directory_outside_skill_root",
      "secret_openai_api_key_outside_root"
    ]
  },
  "unpack_error": null,
  "detected_root": "/tmp/skill_inspect_x/one-skill",
  "skill_md_count": 1,
  "outside_root_findings": [
    {
      "severity": "warning",
      "code": "archive_directory_outside_skill_root",
      "message": "archive contains a directory outside the detected skill root",
      "file": "docs"
    }
  ],
  "secret_risk_findings": [
    {
      "severity": "error",
      "code": "secret_openai_api_key_outside_root",
      "message": "possible OpenAI API key pattern found outside the detected skill root",
      "file": "outside-root:.env"
    }
  ]
}
```

## Local dependency traversal

Markdown inline and reference-style links resolve relative to their containing
document, including root documents, angle-bracket destinations with spaces,
percent escapes, and fragments. Standalone inline paths under `scripts/`,
`references/`, `assets/`, `./`, or `../` follow the same rule. Inline commands,
fenced examples, HTML code examples, external URLs, and source-code imports do
not establish document dependencies. External URLs are never fetched.

Normalized paths must stay inside the package, and symlink traversal is unsafe.
Only reachable `.md`, `.markdown`, `.txt`, and `.rst` documents are traversed,
starting at `SKILL.md`; cycles terminate. Defaults are 200 documents, 1,000 edges,
depth 32, and 10 MiB of text, additionally constrained by existing package file,
byte, and depth limits. These graph limits are recorded in `effective_limits`.
A document or edge limit, unreadable document, or undecodable document produces
`resource_graph_incomplete`. Dependency completeness is separate from
`coverage_complete`, which still describes secret and dangerous-command scans.

The published Agent Skills field constraints (verified 2026-09-06) apply in both targets: description at most 1024 characters, optional compatibility a nonempty string at most 500 characters, and metadata a string-to-string map. These are validity checks, not description-quality heuristics. New finding codes identify each invalid field without emitting its value.
