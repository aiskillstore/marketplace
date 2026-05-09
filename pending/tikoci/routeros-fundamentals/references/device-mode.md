# Device-Mode

Device-mode gates access to potentially risky features. Changing the mode requires physical confirmation (reset button press or power cycle within the activation timeout).

```routeros
# View current mode and pending changes
/system/device-mode/print

# Change mode and enable features
/system/device-mode/update mode=advanced container=yes

# After executing: physically confirm within activation-timeout
# - Press reset button, OR
# - Power cycle the device
```

**Mode script bypass (7.22+):** During netinstall, a mode script (`-sm`) can set device-mode on first boot, automatically triggering a reboot — removing the manual power-cycle requirement for provisioning. See the `routeros-netinstall` skill.

## Modes and Factory Defaults

There are four modes. The factory default depends on device type (since 7.17):

| Mode | Factory default on | Notes |
|---|---|---|
| `advanced` | CCR, 1100 series, CHR, pre-7.17 devices | Previously called `enterprise` |
| `home` | Home routers (hAP, cAP, etc.) | Most features disabled |
| `basic` | All other device types | Mid-range restrictions |
| `rose` | RDS-series devices | Like advanced but with container enabled by default |

## Feature Matrix

All features below are `/system/device-mode/update` properties. Every feature is updatable — the matrix shows which are **enabled by default** per mode.

| Property | Type | Home | Basic | Advanced | ROSE |
|---|---|---|---|---|---|
| `scheduler` | mode default | - | yes | yes | yes |
| `fetch` | mode default | - | yes | yes | yes |
| `bandwidth-test` | mode default | - | - | yes | yes |
| `sniffer` | mode default | - | yes | yes | yes |
| `romon` | mode default | - | yes | yes | yes |
| `hotspot` | mode default | - | - | yes | yes |
| `proxy` | mode default | - | - | yes | yes |
| `socks` | mode default | - | - | yes | yes |
| `email` | mode default | - | yes | yes | yes |
| `container` | always off | - | - | - | yes* |
| `zerotier` | mode default | - | - | yes | yes |
| `traffic-gen` | always off | - | - | - | - |
| `partitions` | always off | - | - | - | - |
| `routerboard` | always off | - | - | - | - |
| `install-any-version` | always off | - | - | - | - |

*ROSE mode enables `container` by default; on all other modes it must be explicitly enabled.

"Always off" features (per official docs: traffic-gen, container, partitions, routerboard, install-any-version) require explicit `property=yes` regardless of mode. "Mode default" features are enabled/disabled by the mode choice.

## Other Properties

| Property | Default | Description |
|---|---|---|
| `activation-timeout` | `5m` | Time window for physical confirmation (10s–1d) |
| `flagging-enabled` | `yes` | Enable suspicious-config detection |

An `attempt-count` increments on each canceled/timed-out change and resets to 0 only on successful power-cycle confirmation. Official docs say "only three times" but **lab testing showed 12+ attempts via REST with no visible limit** — the REST API continued to accept and block on update requests regardless of count. The "three times" limit may be CLI-only or an approximation.

If not confirmed within the activation timeout, the change is canceled and the count increments (it does not revert on next reboot — `attempt-count` survives reboots).

> **Source:** Device-mode page (rosetta page 93749258, 7.22 docs) + lab verification on CHR 7.22.1 (x86_64). See `device-mode-rest.md` for full REST API behavior.
