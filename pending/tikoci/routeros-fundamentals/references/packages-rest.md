# RouterOS `/system/package` REST API Reference

Lab-verified against CHR 7.22.1 (x86_64). All responses confirmed via curl.

## Package Object Shape

`GET /rest/system/package` returns a JSON array. Each element:

| Field | Type | Description |
|-------|------|-------------|
| `.id` | string | RouterOS internal ID (e.g. `*1`) |
| `name` | string | Package name (e.g. `routeros`, `container`) |
| `version` | string | Installed version, or `""` if not installed |
| `available` | string | `"true"` if not yet installed, `"false"` if installed |
| `disabled` | string | `"true"` if disabled/not-active, `"false"` if active |
| `scheduled` | string | Pending action (see below), or `""` |
| `build-time` | string | Build timestamp |
| `size` | string | Package size in bytes |

## Package States

| State | `available` | `disabled` | `version` |
|-------|-------------|------------|-----------|
| Installed + active | `"false"` | `"false"` | `"7.22.1"` |
| Installed + disabled | `"false"` | `"true"` | `"7.22.1"` |
| Available (not installed) | `"true"` | `"true"` | `""` |

## Built-In Optional Packages (CHR 7.22.1)

These 12 packages are built into the CHR image — no SCP upload or download needed:

`routeros` (always installed), `calea`, `container`, `dude`, `gps`, `iot`, `openflow`, `rose-storage`, `tr069-client`, `ups`, `user-manager`, `wireless`

## Package Visibility

- **Fresh boot**: only installed packages appear (typically just `routeros`).
- **After check-for-updates**: all available built-in packages appear in the list.
- **After disable + apply-changes**: disabled packages remain visible with `disabled="true"`.

## Endpoints

### GET /rest/system/package

Returns all visible packages.

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/system/package
```

### GET /rest/system/package/update

Returns update channel and installed version.

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/system/package/update
```

Before check-for-updates:

```json
{"channel":"stable","installed-version":"7.22.1"}
```

After check-for-updates adds `latest-version` and `status`:

```json
{"channel":"stable","installed-version":"7.22.1","latest-version":"7.22.1","status":"System is already up to date"}
```

### POST /rest/system/package/update/check-for-updates

**Async command** — returns a progressive-status array with `.section` indices:

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/system/package/update/check-for-updates \
  -X POST -H "Content-Type: application/json" -d '{}'
```

```json
[
  {".section":"0","channel":"stable","installed-version":"7.22.1","status":"finding out latest version..."},
  {".section":"1","channel":"stable","installed-version":"7.22.1","latest-version":"7.22.1","status":"System is already up to date"}
]
```

**Side effect**: reveals all available optional packages in subsequent `GET /rest/system/package`.

### POST /rest/system/package/enable

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/system/package/enable \
  -X POST -H "Content-Type: application/json" -d '{"numbers":"container"}'
```

Response: `[]` (empty array = success). Sets `scheduled="scheduled for enable"` on the package.

### POST /rest/system/package/disable

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/system/package/disable \
  -X POST -H "Content-Type: application/json" -d '{"numbers":"container"}'
```

Response: `[]` (empty array = success). Sets `scheduled="scheduled for disable"` on the package.

### POST /rest/system/package/apply-changes

Triggers reboot **and** applies all scheduled package changes.

```bash
curl -s -u admin: http://127.0.0.1:9100/rest/system/package/apply-changes \
  -X POST -H "Content-Type: application/json" -d '{}'
```

Response: `[]` — connection drops as router reboots.

## Scheduled Field Values

| Value | Meaning |
|-------|---------|
| `""` | No pending changes |
| `"scheduled for enable"` | Will be installed/enabled on apply-changes |
| `"scheduled for disable"` | Will be disabled on apply-changes |

Note: the value is `"scheduled for enable"`, NOT `"scheduled for install"`.

## Critical: apply-changes vs reboot

| Endpoint | Applies scheduled changes | Triggers reboot |
|----------|--------------------------|-----------------|
| `POST /rest/system/package/apply-changes` | ✅ Yes | ✅ Yes |
| `POST /rest/system/reboot` | ❌ No | ✅ Yes |

**This is the biggest gotcha.** A plain `/system/reboot` discards all pending package changes. Always use `/system/package/apply-changes` to commit enable/disable operations.

**⚠️ Version requirement:** `/system/package/apply-changes` was added in **RouterOS 7.18**. On versions <7.18, `/system/reboot` IS the correct (and only) method — and it DOES apply pending changes on those older versions. The "reboot discards changes" behavior is specific to 7.18+ where `apply-changes` exists. (Verified: rosetta `routeros_command_version_check` + live test on CHR 7.10, session 2025-07-17.)

## Device-Mode Dependency

The `container` package can be enabled and installed without device-mode. However, `/container` commands will fail with `"not allowed by device-mode"` until device-mode is set:

```routeros
/system/device-mode/update container=yes
```

This requires a power-cycle confirmation (see device-mode reference).

## Recommended Pattern for quickchr

```
1. POST /rest/system/package/update/check-for-updates   → reveals available packages
2. POST /rest/system/package/enable {"numbers":"<name>"}  → schedule enable
3. POST /rest/system/package/apply-changes {}             → reboot + apply
4. waitForBoot()                                          → poll until REST ready
5. GET /rest/system/package                               → verify installed
```

SCP upload is **not needed** for built-in packages on CHR 7.22.1+. The enable + apply-changes flow is sufficient.
