# Runtime License Installation and Diagnostics

Use this guide when a user asks to install, activate, or renew an xdoc Runtime license, or when a task encounters an authorization refusal, an ineffective license, or watermarks after payment. Ordinary successful tasks need no additional authorization maintenance. An authorization-only task does not require an outline, DeckKit, PPTX, or visual delivery gates. A downloaded license JSON is a credential, not deck content.

## Determine the Execution Environment and Scope

- When the user has requested installation or renewal and provided a file, verify, install, and validate it under that authorization without asking again. If the user only requests an explanation or diagnosis, perform the corresponding checks; do not uninstall, reset the clock, or replace an existing license incidentally.
- Use the same xdoc binary, OS user, working directory, and environment as the pptx-nova execution. First identify the actual binary and run `xdoc --version`; an explicit `XDOC_BIN` and the Agent's `PATH` can select different installations. If the binary is missing, install a published Runtime using the [official getting-started guide](https://docs.structurify.io/en/pptx-runtime/getting-started/), then check its current contract.
- Read the focused schemas for `xdoc schema --command auth.verify`, `auth.install`, and `auth.status`; read `auth.reset-clock` / `auth.uninstall` only when recovery requires them. Resolve each report through its action's `ioContract.stdout.schemaRef`; see [Schema discovery](schema-discovery.md#典型-agent-用法). Examples here do not supersede the current binary's command and report contracts. Auth output is already JSON: use `--pretty`, not `--json`.
- Inspect only relevant environment values: `XDOC_CONFIG_PATH`, the user's home (or `APPDATA` on Windows), `CI`, the corresponding entries in the working directory's `.env`, and any explicit task `--license`. The CLI loads `.env` from its working directory at startup; nonblank process environment values take precedence. Do not print the entire environment or unrelated secrets from `.env`.

Installation and renewal write license configuration and Clock state. `status` performs full admission and may update Clock state; it is not strictly read-only. `verify` only reads the specified file and is suitable when the user explicitly requests no local state changes. For development verification, set `XDOC_CONFIG_PATH` to a newly created private absolute directory; do not touch the user's real license.

## Installation and Renewal

1. Preserve the original UTF-8 delivery bytes; compare the SHA-256 with the delivery notice when available. Confirm the file is a readable regular file and the client is within the issuer's supported version range. Runtime requires `xdoc-cli-license/v1`; Viewer/Converter credentials do not apply. The original file name, such as `runtime-personal.json`, may be retained. Do not edit signed dates, identity, features, or capabilities, and never install a signing private key.
2. Verify the specified file first. If verification fails, use the table below and correct the conditions before continuing:

   ```sh
   xdoc auth verify --license "/absolute/path/runtime-personal.json" --pretty
   ```

   Verification passes only when the exit code is 0 and the report has `outcome: "passed"` and `reason: "ok"`. `status: "success"` alone means the diagnostic completed and can accompany a failed verification.

   Successful signature/time verification does not mean the file is installed or prove Clock rollback admission, possession of the device private key, or task authorization. Stop and report the result if the user requested verification only.

3. Select the configuration directory and install the original file:

   ```sh
   xdoc auth install "/absolute/path/runtime-personal.json" --pretty
   xdoc auth status --pretty
   ```

   Install accepts exactly one positional file; do not use `install --license ...`. Auth argument failures may produce stderr only. Preserve the actual exit code, stdout, and stderr separately; do not combine them and parse them as JSON.

The default installation target is `$HOME/.config/xdoc/xdoc-license.json` on POSIX and `%APPDATA%\xdoc\xdoc-license.json` on Windows. When set, `XDOC_CONFIG_PATH` identifies the **configuration directory**: it must be an existing private absolute directory accessible to the current user. Runtime manages `xdoc-license.json` inside it. Create the directory first and set private permissions for the actual execution user (normally `0700` on POSIX; use an appropriate ACL on Windows), then retain the same environment for installation, status, and later tasks. Runtime can create the default user configuration directory. Do not point `XDOC_CONFIG_PATH` at the downloaded JSON or set it only for installation while subsequent Agent tasks use another directory. A normal user installation uses the user's directory and does not need `sudo`.

A successful install must show both `status: "success"` and `outcome: "installed"`. Compare `installedPath` and `installedSha256` with the delivered file and inspect the validity period and capabilities in `authenticatedFacts`. A healthy status has these key fields (this is not a complete report):

```json
{
  "health": "healthy",
  "verification": { "state": "verified" },
  "admission": { "state": "admitted" },
  "taskAuthorization": "not-evaluated"
}
```

Compare `source.path` / `source.sha256` with the install report as well. Status exit 0 means only that the query completed: `not-installed` and `unhealthy` can also return 0. Inspect `verification.reason`, `admission.reason`, and `clock`; exit 0 alone does not establish healthy authorization or a successful task.

For renewal, use the same commands to install the **newly delivered file**, then repeat status and real-task verification. The new license replaces the old one in the selected configuration directory; retain the original delivery file and do not uninstall first. If warned that the replacement has a different identity/license lineage or an earlier expiry, check that the intended file was selected. Editing the expiry in an old JSON file is not renewal.

### Uncertain Installation Outcome

`outcome: "uncertain"` / `auth_install_outcome_uncertain` means publication may already have occurred. Retain `targetPath`, `attemptedSha256`, and `publication` from the report, then run status in the **same environment**:

- If the target path and `source.sha256` match the attempted file and health/admission are healthy, record the currently observable installation result and continue with real-task verification; retain the original uncertain report.
- If the old file remains, no file exists, or the outcome is still unclear, inspect permissions, storage, and concurrent tasks; correct the conditions before retrying the original delivery.
- If another process installed a different newer file, check whether replacement matches the current task before overwriting that license.

Do not assume failure left the old file unchanged. Do not automatically roll back, delete the target, or bypass installation admission by copying the file manually.

## Verify the Actual Task

Install and status verify the local credential; each task is still evaluated against its actual feature, output format, capabilities, and host facts. When there is an original user task, preferably resume it in the same environment, preserving its strict constraints and original inputs and using a new output path. Do not claim that creation, editing, refurbishment, and translation are all authorized merely because PDF conversion succeeded.

To verify conversion independently, use a known valid PPTX that originally has no watermark and an output path that does not exist:

```sh
xdoc convert "./slides.pptx" --to pdf --output "./licensed-check.pdf" --require-unwatermarked --report "./licensed-check-report.json"
```

First confirm the options in `xdoc schema --command convert`. `--require-unwatermarked` rejects the task when an unwatermarked mode cannot be authorized. If only paid entitlement needs to be proved and the current command discloses the option, use `--require-entitlement`. Convert stdout is not guaranteed to be JSON. The currently disclosed `--report` can save a `batch/v1` report; inspect `items[].error` fields `kind`, `stage`, and `details.reason`. Failures may still produce only stderr; never invent an authorization report. Check the actual exit code, available reports, and output file. If only the license file is available and there is no suitable task input, report truthfully that it is installed and healthy but task authorization remains unverified.

A one-off convert can select a credential explicitly without installing it in the user configuration:

```sh
xdoc convert "./slides.pptx" --to pdf --output "./explicit-check.pdf" --license "/absolute/path/runtime-personal.json" --require-unwatermarked
```

`xdoc pptx` creation/editing uses the installed credential; do not apply convert's `--license` option to it. For other commands use only options actually disclosed by their current schema/help; do not assume every subcommand supports strict flags.

A paid license does not erase arbitrary watermarks already present in input content. Existing ordinary Free marks, signed watermark obligations, and authorization for new output are handled separately; a watermark remaining after direct conversion of an old watermarked file does not prove installation failed. Do not delete signed metadata or change formats to bypass obligations. See [Conversion Input Quotas and Authorization Failures](troubleshooting.md#conversion-input-quotas-and-authorization-failures) for the distinction between quotas and resources.

## Installed License Not Used by the Task

For commands supporting explicit credentials, lookup priority is: command `--license` → `xdoc-license.json` in `XDOC_CONFIG_PATH`, when configured → the platform user default directory. Once a higher-priority source is selected, a missing, unreadable, or invalid file does not automatically fall through to lower-priority credentials. An arbitrary JSON file in the project directory is not automatically discovered.

Compare the actual execution environment:

1. Binary path/version, user/home, working-directory `.env`, `XDOC_CONFIG_PATH`, and `source.path`/hash.
2. Whether the command still specifies an old `--license`, or the Agent/IDE inherited variables from another launch environment.
3. Whether a daemon still uses the old environment. After changing its environment, restart the relevant long-running process according to the [daemon guide](daemon-sessions.md), then check status/the task in that same environment without stopping unrelated tasks.
4. Whether a container or local scheduled task uses another user/configuration path. Installing on the host does not automatically copy the file into a container.

Local Personal/Enterprise licenses do not automatically include CI, cross-user shared-server, or Service/API rights. A nonempty `CI` value other than case-insensitive `0` / `false` triggers CI evaluation. Check the actual execution mode and issued capabilities; explain missing rights and have the user request appropriate delivery from the issuer. Do not falsify host facts or use `--allow-fallback` to bypass a capability refusal. Do not silently fall back to Free when a commercial license fails: preserve the user's unwatermarked/strict authorization constraints and use a disclosed fallback only when the user has explicitly accepted it and the task qualifies for Free.

## Recovery by Actual Reason

The following are symptom-based directions; the current action/report schema defines the complete reason set and exit codes. Argument errors generally use exit 2; install file-read failures use 3, credential refusals 4, and failed/uncertain writes 9. If there is no JSON, retain stderr and do not invent report fields from error prose.

| Observation                                                                                             | Check and recovery                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cli_license_file_read_failed`                                                                          | Check the actual path, case, and current user's file-read and directory-traversal permissions; confirm a readable regular file. Preserve the original; do not automatically use sudo or change unrelated directory permissions.                                                                                                                                                                                                                                                                                                                                                              |
| `cli_license_too_large`                                                                                 | Read the current verify/install input limit from schema `ioContract.input.maxBytes` (currently 65,536 bytes). Confirm this is the original credential rather than an archive or web page and obtain it again from the issuer; do not truncate or simplify the signed file.                                                                                                                                                                                                                                                                                                                   |
| JSON/envelope/payload format error, such as `cli_license_json_invalid` / `cli_license_envelope_invalid` | Check for an HTML download, truncated copy, or wrong product file; obtain the original Runtime JSON again. Do not repair the signed payload.                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `cli_license_schema_unsupported` / `cli_license_kind_unsupported` / `cli_license_signature_invalid`     | Check the Runtime product, delivery hash, and supported client range. Use a published client supported by the issuer or request a corrected delivery; do not add trust keys yourself.                                                                                                                                                                                                                                                                                                                                                                                                        |
| `cli_license_key_not_found`                                                                             | The current client does not trust the declared signing key. Check that the credential's delivery environment matches the client; staging/test credentials may require an issuer-provided test client. The file's `keyId` is only a diagnostic clue until verification succeeds. Use a matching production credential for a production client, or the client designated by the issuer. This reason alone does not establish a need to upgrade or republish the CLI. Do not edit the credential or add trust keys yourself. Explain the mismatch to the user without internal signing details. |
| `cli_license_expired` / `cli_license_clock_invalid`                                                     | Check the real system time and delivery validity. Install a renewal if expired; wait for valid activation or request correction if not yet valid. reset-clock does not renew or change issuance dates.                                                                                                                                                                                                                                                                                                                                                                                       |
| `health: "not-installed"`                                                                               | Compare user, configuration directory, cwd `.env`, and source; install in the directory actually used by the task. Downloading the file or running verify alone does not install it.                                                                                                                                                                                                                                                                                                                                                                                                         |
| `health: "unhealthy"` or verify succeeds but install/task is refused                                    | Inspect the actual verification/admission/clock reason and investigate validity, Clock, device binding, revocation, and the specific feature/capability. Do not repeatedly install the same file expecting permissions to change.                                                                                                                                                                                                                                                                                                                                                            |
| `config_path_invalid` / `auth_config_invalid`                                                           | Ensure `XDOC_CONFIG_PATH` is an existing private absolute directory, not a JSON file or relative path. Check path aliases and managed-target symlinks; retry with an actual regular directory.                                                                                                                                                                                                                                                                                                                                                                                               |
| `auth_storage_unavailable` / `auth_install_failed`                                                      | Check current-user directory/file permissions, read-only mounts, disk space, and processes holding locks. If necessary use a new controlled private directory and align later task environments. Do not chmod 777, recursively change permissions, or delete lock files.                                                                                                                                                                                                                                                                                                                     |
| `outcome: "uncertain"`                                                                                  | Establish publication facts using the path/hash comparison above before deciding whether to retry the same delivery; do not automatically roll back.                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `clock_anomaly`                                                                                         | Follow controlled Clock recovery below; first calibrate system time and stop the relevant tasks/daemon.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `device_pop_failed`                                                                                     | A valid signature does not prove this host possesses the bound device private key. Check whether the delivery is bound to this device and whether the published Runtime supports its host capability; ask the issuer to adapt or reissue it. Do not copy private keys or remove devicePublicKey.                                                                                                                                                                                                                                                                                             |
| `credential_revoked` or revocation receipt verification error                                           | Retain the actual reason and license hash; ask the issuer to verify revocation or provide corrected delivery. Do not delete receipts, restriction policies, or state to bypass rejection.                                                                                                                                                                                                                                                                                                                                                                                                    |
| Credential healthy but task reports `no_executable_mode` / `strict_mode_unsatisfied` / exit 4           | Inspect the actual authorization diagnostic, feature, format, capability, and input scope. Do not interpret every exit 4 as a bad file or expiry, or automatically bypass it by splitting slides, deleting charts, or changing formats.                                                                                                                                                                                                                                                                                                                                                      |
| Credential healthy but resource/font/input error remains                                                | Follow [runtime troubleshooting](troubleshooting.md) for the actual file and engineering limits; a paid license does not raise compiled resource limits.                                                                                                                                                                                                                                                                                                                                                                                                                                     |

### Clock Recovery and Uninstall

Perform Clock recovery only when `clock_anomaly` has been observed and the user's recovery request covers this action. First calibrate the real system time, stop the tasks and daemon in use, confirm the same configuration directory, then read `xdoc schema --command auth.reset-clock` and execute:

```sh
xdoc auth reset-clock --pretty
xdoc auth status --pretty
```

Reset removes only the supported fixed Clock anchor, preserving the license and lock file. Handle `auth_clock_reset_failed`, `auth_clock_reset_outcome_uncertain`, or `auth_clock_reset_unsupported` according to the actual report. If reset is unavailable, explain the limitation and consult the issuer; do not manually delete directories or lock files. Check status in a new process, then restart relevant long-running processes and resume the original task. Reset cannot make an expired, future-valid, device-mismatched, or revoked credential valid. Do not make reset a prerequisite for first installation.

Run `xdoc auth uninstall --pretty` only when the user asks to stop using/remove the installed license. It removes only the license in the currently selected configuration directory, preserving Clock state and lock files. It does not delete the downloaded original or other explicit `--license` files. Free availability after uninstall still depends on actual task conditions.

## Evidence and Handoff

As needed, retain binary identity, relevant focused schemas, actual commands, cwd/relevant environment, exit codes, auth reports and stderr, and real-task reports/output in a new task evidence directory. Bind the delivery hash, install hash, and status source hash; do not copy the original license, private keys, or unrelated environment into shared evidence or version control. Tell the user whether diagnosis, healthy installation, or an actual task was completed. When unable to resolve the problem, provide the actual reason, affected feature/environment, and what the issuer needs to correct. Do not send reports externally without the user's explicit request.

References: [official licensing guide](https://docs.structurify.io/en/pptx-runtime/licensing/) and its [machine-readable version](https://docs.structurify.io/llms.mdx/docs/en/pptx-runtime/licensing/content.md). Its stated client range may differ from the current binary. Confirm against that binary's schema/help, actual reports, and the issuer's delivery scope; do not infer unpublished activation, online renewal, or device migration capabilities from local source.
