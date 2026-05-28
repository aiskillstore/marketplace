---
name: co-tank-monitor
description: "IoT monitoring simulation to predict CO2 tank depletion and prevent weekend gas outages in cell culture facilities. Monitors cylinder pressure, calculates consumption rates, provides early warnings, and supports automated scheduling via cron."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# CO2 Tank Monitor

Monitor CO2 cylinder pressure and predict depletion times to prevent gas outages in cell culture incubators, particularly during weekends when laboratories are unmanned.

**Key Capabilities:**
- **Pressure-Based Depletion Prediction**: Calculate remaining cylinder life
- **Weekend Risk Detection**: Identify depletion during unmanned periods
- **Multi-Cylinder Support**: Handle 10L and 40L cylinder sizes
- **Automated Alert System**: Color-coded status with actionable recommendations
- **Simulation Mode**: Test monitoring scenarios for staff training

---

## Input Validation

This skill accepts: current cylinder pressure (MPa), daily consumption rate (MPa/day), cylinder capacity (10 or 40 L), and optional alert threshold (days).

If the request does not involve monitoring CO2 cylinder pressure or predicting depletion — for example, asking to monitor other gases, control incubator temperature, or manage lab inventory — do not proceed. Instead respond:
> "CO2 Tank Monitor is designed to predict CO2 cylinder depletion and detect weekend risk for cell culture facilities. Please provide current pressure and daily consumption rate. For other lab monitoring tasks, use a more appropriate tool."

---

## Quick Check

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## Workflow

1. Confirm current pressure, daily consumption rate, cylinder capacity, and alert threshold.
2. **Unit detection:** If pressure > 15 and < 220, assume PSI and auto-convert (MPa = PSI × 0.0069). If pressure > 15 and < 150, assume Bar and auto-convert (MPa = Bar × 0.1). State the unit assumption explicitly in the output.
3. Validate that inputs are within plausible ranges (pressure 0–15 MPa after conversion, consumption 0.1–5 MPa/day).
4. Run the script or apply the documented calculation path with only the inputs available.
5. Return a structured result separating assumptions, deliverables, risks, and unresolved items.
6. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

**Fallback:** If pressure is not provided, respond: "Required parameter `--pressure` not provided. Please supply current cylinder pressure in MPa. Use `--simulate` to generate a training scenario without real data."

---

## Core Capabilities

### 1. Depletion Prediction

```python
from scripts.main import calculate_remaining_days, calculate_depletion_time
remaining_days = calculate_remaining_days(pressure=8.0, daily_consumption=1.5)
depletion_time = calculate_depletion_time(remaining_days)
# Formula: remaining_days = pressure / daily_consumption
```

### 2. Weekend Risk Detection

```python
from scripts.main import is_weekend, will_deplete_on_weekend
weekend_risk = will_deplete_on_weekend(depletion_time, alert_days=2)
```

**Weekend Risk Scenarios:**

| Scenario | Risk Level | Action Required |
|----------|------------|-----------------|
| Depletion Saturday/Sunday | 🔴 High | Immediate replacement or weekend duty |
| Depletion Monday morning | 🟡 Medium | Replace Friday afternoon |
| Depletion mid-week | 🟢 Low | Schedule routine replacement |

### 3. Status Levels

| Code | Status | Condition | Action |
|------|--------|-----------|--------|
| **0** | 🟢 Normal | Days > alert_days + 2 | No action needed |
| **1** | 🟡 Caution | Days within alert_days + 2 | Monitor closely |
| **2** | 🔴 Danger | Days ≤ alert_days or weekend risk | Replace immediately |

### 4. Cylinder Specifications

| Capacity | Full Pressure | Duration (@1.5 MPa/day) |
|----------|---------------|------------------------|
| **10L** | ~15 MPa | ~10 days |
| **40L** | ~15 MPa | ~40 days |

### 5. Automated Scheduling

```bash
# Daily check at 9:00 AM (cron)
0 9 * * * cd /lab/scripts && python scripts/main.py --pressure $(cat sensor.log | tail -1) --quiet

# Pre-weekend check (Friday 5 PM)
0 17 * * 5 cd /lab/scripts && python scripts/main.py --pressure $(cat sensor.log | tail -1)
```

---

## CLI Usage

```text
# Manual morning check
python scripts/main.py --pressure 8.5 --daily-consumption 1.2

# Pre-weekend check with extended alert
python scripts/main.py --pressure 5.5 --alert-days 3

# Simulation for training
python scripts/main.py --simulate
```

---

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--pressure` | float | No | Current cylinder pressure in MPa |
| `--capacity` | int | No | Cylinder capacity (10 or 40 L) |
| `--daily-consumption` | float | No | Average daily consumption (MPa/day) |
| `--alert-days` | int | No | Alert threshold in days (default 2) |
| `--simulate` | flag | No | Generate random training scenario |
| `--quiet` | flag | No | Suppress verbose output (for cron) |

---

## Output Requirements

Every final response must make these explicit:

- Objective or requested deliverable
- Inputs used (pressure, consumption, capacity) and assumptions introduced (including unit conversion if applied)
- Calculation method applied
- Core result: remaining days, depletion datetime, weekend risk status, recommendations
- **Constraints:** Prediction assumes constant consumption rate. Actual depletion may vary with temperature, usage patterns, and weekend vs. weekday consumption.
- Unresolved items and next-step checks

---

## Error Handling

- If pressure is not provided, offer simulation mode or request the value explicitly.
- If values are outside plausible ranges (pressure >15 MPa or <0), flag as implausible.
- If `scripts/main.py` fails, report the failure point and provide manual calculation fallback using the formula above.
- Do not fabricate pressure readings or depletion predictions.

---

## Common Pitfalls

- **Inconsistent reading times**: Take readings at same time daily (e.g., 9:00 AM ± 30 min)
- **Wrong consumption estimates**: Calculate from actual usage over 2+ weeks
- **Pressure unit confusion**: Standardize on MPa; convert if gauge shows PSI or Bar
- **Alert fatigue**: Batch daily reports; only escalate urgent alerts immediately
- **Wrong cylinder capacity**: 10L vs 40L confusion causes 4× prediction error

---

## Pressure Conversion Reference

| Unit | MPa | PSI | Bar |
|------|-----|-----|-----|
| **MPa** | 1.0 | 145.0 | 10.0 |
| **PSI** | 0.0069 | 1.0 | 0.069 |
| **Bar** | 0.1 | 14.5 | 1.0 |

**Typical Cylinder Pressures:** Full ~15 MPa | Working 8–10 MPa | Replace threshold 3–5 MPa | Empty <1 MPa

---

## References

- Cell Culture CO2 Guidelines: https://www.thermofisher.com/cellculture
- Gas Cylinder Safety: https://www.osha.gov/gascylinders

