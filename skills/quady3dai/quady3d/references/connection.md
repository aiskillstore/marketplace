# Connect the Quady3D tools

This Skill requires the local Quady3D MCP server. It does not embed credentials or generate models by itself. Use the MCP package's README for the installation and host configuration matching the installed version.

The server uses Node.js 22 or later. Configure `QUADY3D_API_KEY` in the host's environment or secure connection settings, not a chat message. Set project directories with repeated `--root /absolute/project` arguments or `QUADY3D_ALLOWED_ROOTS`, a JSON array of absolute directories. Reading and saving files require an allowed directory. Private recovery data must remain outside those directories.

Eight expected tools:

- `quady3d_list_models`
- `quady3d_get_account`
- `quady3d_upload_file`
- `quady3d_quote`
- `quady3d_create_job`
- `quady3d_get_job`
- `quady3d_list_jobs`
- `quady3d_download_asset`

Hosts may add their own prefix. Verify names and descriptions in the current host rather than guessing a prefix. Missing credentials do not prevent discovery; business calls return `connection_required`. Update or revoked-key issues belong in host settings. Do not replace the server with an unofficial script to bypass a permission error.

The MCP and Skill can be installed separately. Host discovery, credentials, cloud availability and download access are separate checks. Successful startup does not prove a generation will be accepted.

MCP alpha.3 adds `local_workspace` to the account result. It reports canonical allowed roots and whether they are currently available for a new generation. New paid submissions need a configured writable directory; quoted inputs remain free to inspect. Recovering an existing action or job remains available while the directory is being fixed. This readiness check does not guarantee a directory will remain available throughout a cloud task.

MCP 0.1.2 reports `local_recovery.scope` and `across_keys`. An authenticated account ID associates its saved connections on the same API; replacement keys retain the original request identity. Associate an older connection by reconnecting its old key once before revocation. An older API without account IDs keeps same-key recovery. Changing an account or API does not grant access to another connection's saved inputs, and each host still needs its own allowed project directories.

Account checks and automatic across-key association require `account:read`. Do not expand a key's scopes automatically. Existing unassociated jobs-only connections retain their original key-scoped workflow; a connection with a verified account cannot downgrade after an identity or permission failure.
