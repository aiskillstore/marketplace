---
name: AC-Nexus
version: 5.3.0
identifier: oywq00008-cell-AC-Nexus-for-agent-skill
description: 🎮 AI Agent 智能空调控制核心库 — 零 GUI 依赖，import 即用。支持 17 大品牌空调（格力/美的/海尔/大金等），直连 Broadlink RM 红外遥控器，同时接入所有支持 MIoT 协议的米家红外遥控器。MIoT spec 自动匹配 siid/piid，百度+和风双天气源，中央气象台+NHC 双风暴源，多日期组定时模板，Markdown 日志，故障诊断。适配树莓派/NAS/OpenWRT/桌面全平台。（原名 BroadlinkAC，现已更名为 AC-Nexus，正式成为空调中枢）
---

# AC-Nexus — AI Agent Smart AC Controller v5.3.0

Cross-platform AC control library for Broadlink RM series IR blasters and Xiaomi MIoT-compatible IR remote controllers. **Zero GUI dependency** — designed for AI agents to clone, install, and control air conditioners programmatically. Device-specific MIoT siid/piid auto-matched from miot-spec.org with 7-day local cache.

> 📢 **Rebrand Notice:** Formerly **BroadlinkAC**, now **AC-Nexus** (空调中枢). All Xiaomi IR remote controllers compatible with MIoT protocol are supported — just scan with Mi Home app to add, then control via local network. No brand limitations.

## ⚠️ Safety & Persistence

> **This skill writes durable state to the user's machine.** `init()` creates `~/.ac_controller/config.json` (API keys, device config, schedule templates) and starts a background scheduler daemon thread. The scheduler survives agent task completion — scheduled on/off times, auto-adjust, and storm auto-shutdown will continue to run autonomously. **Always confirm with the user before:**
> - Modifying or creating schedule templates
> - Enabling auto-adjust or typhoon auto-shutdown
> - Changing device configuration (brand, temperature rules, location)
>
> To fully disable automation: set `schedule_enabled=False` and `auto_adjust=False` for the device, then call `_cfg.save_config(_cfg.config)`.

## Quick Start (Agent)

```bash
git clone https://github.com/oywq00008-cell/AC-Nexus.git
cd AC-Nexus
pip install -r requirements-core.txt
```

```python
from acnexus_core import init, send_ac, fetch_weather

# One-time setup — all config persisted
init(
    baidu_key="your_baidu_key",
    location={"lat": 22.54, "lon": 114.05, "name": "Shenzhen"},
    brand="Gree"
)

# Control AC — auto-routes between Broadlink IR and Xiaomi MIoT
send_ac("on", "cool", 26, "auto")     # Turn on, cool 26°C, auto fan
send_ac("off", "cool", 26, "auto")    # Turn off

# Weather — dual source (Baidu default, falls back to QWeather)
weather = fetch_weather()

# Storm threat — quick check + smart shutdown
from acnexus_core import typhoon_threat_distance, typhoon
dist, name = typhoon_threat_distance()
print(f"Nearest: {name} at {dist}km")
# Intelligent: wind-speed + distance tiered, TD excluded, pauses scheduler
alerts = typhoon.judge_and_shutdown(print)
```

## Multi-Brand Architecture (v5.3.0)

AC-Nexus supports multiple device providers simultaneously. Devices are organized by brand type in the config:

```json
"devices": {
    "broadlink": {
        "e870723f41ee": {"host": "192.168.8.214", "model": "RM4 mini", ...}
    },
    "xiaomi_cloud": {
        "2003509235": {"host": "192.168.8.119", "token": "***", "model": "qjiang.acpartner.ac02",
                       "miot_spec": {"power": {"siid":3,"piid":1}, "mode": {"siid":3,"piid":2}, ...},
                       ...}
    }
}
```

Each provider's devices are fully isolated — separate schedules, temperature rules, and auto-adjust settings. `send_ac()` automatically detects the device type and routes commands:

- **Broadlink devices** → IR raw hex sent via UDP
- **Xiaomi devices** → MIoT protocol via local network (`set_properties`)

## API Reference

### Setup

> **First-time: install dependencies**
> ```bash
> pip install -r requirements-core.txt
> ```

| Function | Description |
|----------|-------------|
| `init(baidu_key=None, api_key=None, qw_host=None, location=None, brand=None)` | Initialize config + start background scheduler. **Writes to `~/.ac_controller/config.json`**. Idempotent. |
| `acnexus_core.xiaomi_local.fetch_miot_spec(model)` | Fetch per-device siid/piid from miot-spec.org. 7-day local cache at `~/.ac_controller/miot_instances.json`. Used automatically when adding devices — not needed by the Agent. |
| `acnexus_core.config.save_config(cfg)` | Save config to disk (atomic write) |
| `acnexus_core.config.find_device(mac)` | Find device by MAC across all providers → `(provider, device_dict)` |

> ⚠️ **Device naming is critical for Agent usability.** Each device's `name` field in config should be a human-readable room/location name (e.g. "二楼卧室", "客厅"). The Agent matches user intent ("关掉二楼房间的空调") by searching device names. Open the desktop app → click the ✏️ rename button next to the device dropdown to set meaningful names.

### AC Control (Broadlink IR + Xiaomi MIoT Local)
| Function | Description |
|----------|-------------|
| `send_ac(power, mode, temp, fan, source="手动", mac=None)` | Send command. Auto-routes: `broadlink` → IR hex, `xiaomi_cloud` → MIoT `set_properties`. `power`: `"on"`/`"off"`. `mode`: `"cool"`/`"heat"`/`"dry"`/`"fan"`/`"auto"`. `temp`: 16-30. `fan`: `"auto"`/`"1"`/`"2"`/`"3"`. Pass `mac=` to target a specific device. |
| `decide_ac(outdoor_temp, mac=None)` | Run temperature rules → returns `(target_temp, mode)` |
| `get_device()` | Get current Broadlink device (for IR learning) |
| `get_current_device()` | Get current device config dict from `devices[provider][mac]` |

> `send_ac` covers the minimum universal set across all brands. Xiaomi devices use per-model siid/piid from `dev["miot_spec"]` when available, falling back to hardcoded defaults (siid=3/4). No manual mapping needed.

### Adding Xiaomi MIoT Devices

**Step 1 — Get session via QR login:**
```python
from acnexus_core.xiaomi_cloud import login_qr
# In a terminal: prints ASCII QR code automatically
# In Jupyter/GUI: pass a callback to render the QR image
session = login_qr()
# Returns dict with auth tokens for listing devices
```

**Step 2 — Add device to config:**
```python
import acnexus_core.config as _cfg
from acnexus_core.xiaomi_cloud import list_devices
from acnexus_core.xiaomi_local import fetch_miot_spec

# List devices on this mi account
devices = list_devices(session)

# Pick an IR remote controller and add it
for d in devices:
    if d["model"] in ("lumi.acpartner.mcn02", "qjiang.acpartner.ac02"):
        spec = fetch_miot_spec(d["model"])  # Auto-match siid/piid
        _cfg.add_or_update_device(d["did"], {
            "did": d["did"],
            "host": d["ip"],
            "mac": d["mac"],
            "model": d["model"],
            "name": d["name"],
            "token": d["token"],  # Critical for local network control!
            "brand": "格力",      # Default brand, user changes in Mi Home app
            "miot_spec": spec,    # Device-specific siid/piid (optional, safe fallback)
        })
        break

_cfg.save_config(_cfg.config)
```

**Step 3 — Control via local network (no cloud after this):**
```python
send_ac("on", "cool", 25, "auto")  # Automatically uses MIoT local network
```

### Reading Xiaomi Device State

Unlike Broadlink (one-way IR), MIoT devices support reading current state:
```python
from miio import Device
d = Device("192.168.8.119", "97af6abc63a7f95da50dc8710005a42d")
r = d.send('get_properties', [
    {'siid': 3, 'piid': 1},  # Power (True/False)
    {'siid': 3, 'piid': 2},  # Mode (0=cool 1=heat 2=auto 3=fan 4=dry)
    {'siid': 3, 'piid': 4},  # Temperature (16-30)
    {'siid': 4, 'piid': 2},  # Fan speed (0=auto 1=low 2=med 3=high)
])
print(f"Power={r[0]} Mode={r[1]} Temp={r[2]} Fan={r[3]}")
```

### MIoT Protocol Details

MIoT-compatible IR remote controllers use standard service IDs in most cases:
- **siid=3, piid=1**: Power (True/False) — some devices use piid=5
- **siid=3, piid=2**: Mode (0=cool 1=heat 2=auto 3=fan 4=dry)
- **siid=3, piid=4**: Target temperature (16-30) — some use piid=3
- **siid=4, piid=2**: Fan speed (0=auto 1=low 2=med 3=high)

> ⚠️ **Per-device variation:** Not all devices use the same piid values. `fetch_miot_spec(model)` auto-matches the correct values from miot-spec.org. The Agent should prefer reading `dev["miot_spec"]` from config — if present, use those values; if absent, fall back to the hardcoded defaults above.

### IR Learning (support any brand on Broadlink)
| Function | Description |
|----------|-------------|
| `learn_one(host)` | Enter learning mode, wait for IR signal → raw hex or `None` (45s timeout) |
| `get_raw_code(name, power, mode, temp, fan)` | Look up learned code for custom device |
| `load_custom_codes()` | Load all custom codes from `~/.ac_controller/custom_codes.json` |
| `save_custom_codes(data)` | Persist learned codes |
| `list_custom()` | List custom device names |

> IR learning only works with Broadlink devices. Xiaomi MIoT devices use the pre-built IR code library on the device itself.

### Weather & Alerts (Dual Source: Baidu + QWeather)
| Function | Description |
|----------|-------------|
| `fetch_weather()` | Current weather — auto-routes via Baidu/QWeather |
| `fetch_weather_alerts()` | Local weather warnings |

### Storm Tracking (Dual Source: China NMC + US NHC)
| Function | Description |
|----------|-------------|
| `fetch_typhoons()` | Active storms from NMC or NHC |
| `fetch_typhoon_detail(typhoon_id)` | Detailed track + forecast |
| `typhoon_threat_distance()` | **Agent-critical**: nearest storm distance (km) + name. Use `judge_and_shutdown()` for intelligent wind-speed+distance tiered shutdown. Never throws — returns `(99999, "")` on error |
| `typhoon.judge_and_shutdown(log_func)` | **One-call**: fetch typhoon data → wind-speed + distance tiered shutdown (≥41m/s <100km / ≥33m/s <70km / default <50km), TD excluded, shut down ALL devices across ALL brands + pause scheduler. Returns alerts list |

### Logger
| Function | Description |
|----------|-------------|
| `write_log(category, msg)` | Append daily log (thread-safe) |
| `read_log(date_str)` | Read log by date |
| `get_log_dates()` | List dates with logs |

## Supported AC Brands (17 + Xiaomi MIoT)

**hvac_ir:** Gree, Midea, Hisense, Daikin, Mitsubishi, Hitachi, Fujitsu, Ballu, Carrier MCA, Hyundai, Fuego

**Custom protocols:** Haier, AUX, Panasonic

**Xiaomi MIoT:** All MIoT-compatible IR remote controllers — add via QR scan, control via local network. Supports multiple devices per account. Per-device siid/piid auto-matched.

**Multi-brand mappings:** Xiaomi, Hualing → Midea protocol; Carrier NQV → Carrier MCA

## Weather Providers

| Provider | Free Tier | Features |
|----------|-----------|----------|
| Baidu (default) | 5,000 calls/day | Real-time + forecast + alerts |
| QWeather | 50,000 calls/month | Real-time + forecast + alerts |

## Key Design

- `import acnexus_core` has **zero side effects** — no I/O, no threads
- `init()` is idempotent — safe to call multiple times
- Config auto-persisted to `~/.ac_controller/config.json` (atomic write)
- Runs on any device with Python 3.9+ (macOS/Windows/Linux/Raspberry Pi)
- `typhoon_threat_distance()` never throws — returns `(99999, "")` on any error
- Thread-safe logging with `threading.Lock`
- Multi-provider architecture: `devices[provider][mac]` — fully isolated per brand
- `send_ac` auto-routes: Broadlink → IR hex / Xiaomi → MIoT local network
- Device-specific MIoT siid/piid auto-matched with 7-day local cache

## Common Agent Tasks

### "Control a specific device (multi-device setup)"
```python
from acnexus_core import init, send_ac
import acnexus_core.config as _cfg
init()

# List all devices across all providers
for provider, devs in _cfg.config["devices"].items():
    for did, dev in devs.items():
        print(f"[{provider}] {dev['name']} = {did[:8]}")

# Control a specific device by MAC/DID
send_ac("on", "cool", 25, "auto", mac="e870723f41ee")
```

### "Add a new Xiaomi device for the user"
```python
from acnexus_core.xiaomi_cloud import login_qr
from acnexus_core.xiaomi_cloud import list_devices
from acnexus_core.xiaomi_local import fetch_miot_spec
import acnexus_core.config as _cfg

# Step 1: Login (terminal prints ASCII QR, user scans with Mi Home)
session = login_qr()

# Step 2: List devices and add IR remote controllers
devices = list_devices(session)
ir_models = {"lumi.acpartner.mcn02", "qjiang.acpartner.ac02", "chuangmi.remote.v6"}
for d in devices:
    if d["model"] in ir_models:
        spec = fetch_miot_spec(d["model"])
        _cfg.add_or_update_device(d["did"], {
            "did": d["did"], "host": d["ip"], "mac": d["mac"],
            "model": d["model"], "name": d["name"], "token": d["token"],
            "brand": "格力", "miot_spec": spec,
        })
_cfg.save_config(_cfg.config)
print(f"Added {len(devices)} device(s)")
```

### "Read current state of a Xiaomi AC"
```python
import acnexus_core.config as _cfg
from miio import Device

# Get device info from config
dev = _cfg.config["devices"]["xiaomi_cloud"]["2003509235"]
# Use device-specific siid/piid from miot_spec when available
spec = dev.get("miot_spec")
if spec:
    props = [spec["power"], spec["mode"], spec["temp"], spec["fan"]]
else:
    props = [{"siid":3,"piid":1}, {"siid":3,"piid":2}, {"siid":3,"piid":4}, {"siid":4,"piid":2}]

d = Device(dev["host"], dev["token"])
r = d.send('get_properties', props)
POWER = {True: "开", False: "关"}
MODE = {0: "制冷", 1: "制热", 2: "自动", 3: "送风", 4: "除湿"}
FAN = {0: "自动", 1: "低", 2: "中", 3: "高"}
print(f"{dev['name']}: {POWER[r[0]['value']]} {MODE[r[1]['value']]} {r[2]['value']}°C {FAN[r[3]['value']]}")
```

### "Is there a storm nearby?" / "Shut down all ACs due to storm"
```python
from acnexus_core import init, typhoon
init()
# ✅ One-liner: intelligent wind-speed + distance tiered shutdown
#    (≥41m/s<100km / ≥33m/s<70km / <50km default),
#    tropical depressions excluded, also pauses scheduler
alerts = typhoon.judge_and_shutdown(print)
if not alerts:
    print("No storm threat — all clear")
```

### "Auto-adjust based on outdoor temperature"
```python
from acnexus_core import init, fetch_weather, decide_ac, send_ac
init()
w = fetch_weather()
if w:
    target, mode = decide_ac(float(w["temp"]))
    send_ac("on", mode, target, "auto")
```

### "Learn IR codes for a custom brand"
```python
from acnexus_core.ir_learner import learn_one, save_learned_codes
hex_code = learn_one("192.168.8.214")  # Broadlink device IP
save_learned_codes("MyAC", "gree", {"关机": hex_code})
send_ac("off", "cool", 26, "auto")  # Routes to learned code automatically
```

## Scheduling & Automation

> ⚠️ **All schedule changes are persistent** — they survive Python process exit and will be executed by the background scheduler daemon. Always confirm with the user before enabling or modifying schedules.

The scheduler runs all devices across all providers. Typhoon auto-shutdown (intelligent wind-speed + distance tiered) pauses the scheduler for all devices.

### Read current schedule
```python
import acnexus_core.config as _cfg
from acnexus_core import init
init()

# Navigate the nested structure: devices[provider][mac]
provider = _cfg.config.get("current_brand_type", "broadlink")
mac = _cfg.config.get("current_device_mac", "")
dev = _cfg.config["devices"][provider][mac]
print(dev.get("active_template"))
print(dev.get("schedule_enabled"))
```

### Create a schedule template (multi-group)
```python
templates = _cfg.config.setdefault("schedule_templates", {})
templates["工作日"] = {
    "groups": [{
        "days": [1, 2, 3, 4, 5],
        "slots": [{
            "on": "08:00", "on_enabled": True,
            "off": "18:00", "off_enabled": True
        }]
    }, {
        "days": [6, 7],
        "slots": [{
            "on": "12:00", "on_enabled": True,
            "off": "23:00", "off_enabled": True
        }]
    }]
}
dev["active_template"] = "工作日"
dev["schedule_enabled"] = True
_cfg.save_config(_cfg.config)
```

### Enable/disable auto-adjust (per device)
```python
dev["auto_adjust"] = True
_cfg.save_config(_cfg.config)
```

## Desktop GUI

Pre-built installers (Windows/macOS/Linux), auto-built by GitHub Actions. Download from [Releases](https://github.com/oywq00008-cell/AC-Nexus/releases/latest).

## OpenWRT Router Plugin

7×24 unattended AC control on OpenWRT routers. See [AC-Nexus-OpenWRT](https://github.com/oywq00008-cell/AC-Nexus-OpenWRT).
