---
name: homeassistant-config
description: Create and manage Home Assistant YAML configuration files including automations, scripts, templates, blueprints, Lovelace dashboards, and file organization. Use when working with Home Assistant configuration files (.yaml, .yml) or discussing HA automations, scripts, sensors, or dashboards.
---

# Home Assistant Configuration Skill

Create and manage Home Assistant YAML configuration files including automations, scripts, templates, blueprints, and file organization.

## Slash Commands

| Command | Description |
|---------|-------------|
| `/ha-find-duplicates [path]` | Find duplicate automations and scripts in configuration |

### /ha-find-duplicates
Scans Home Assistant configuration files to find:
- **Exact duplicates**: Automations/scripts with identical triggers and actions
- **Similar items**: Items with 80%+ similarity (name, entities, structure)
- **Trigger conflicts**: Multiple automations responding to the same trigger

Usage: `/ha-find-duplicates /path/to/config` or `/ha-find-duplicates` for current directory.

## Subagents

| Agent | Description |
|-------|-------------|
| `ha-suggestions` | Smart home improvement advisor for automations, scenes, and device recommendations |

### ha-suggestions
A proactive smart home consultant that analyzes your Home Assistant configuration and provides personalized suggestions for:

- **New Automations**: Motion lighting, presence detection, time-based routines, energy saving
- **New Scenes**: Movie night, morning energy, dinner time, work from home, party mode
- **Script Improvements**: Reusable sequences and parameterized routines
- **Device Recommendations**: Sensors, switches, and integrations to enhance your setup
- **Optimization**: Consolidation, trigger efficiency, mode usage, blueprint conversion

The agent automatically discovers your configuration files, inventories entities by domain (lights, sensors, climate, etc.), and generates prioritized suggestions with complete, ready-to-use YAML code.

## Validation Scripts

This skill includes scripts to validate and analyze Home Assistant configurations.

### YAML Validator
Validates YAML syntax and checks for common HA issues (tabs, unquoted booleans, deprecated syntax):
```bash
python3 {baseDir}/scripts/validate_yaml.py /path/to/config.yaml
python3 {baseDir}/scripts/validate_yaml.py /path/to/config.yaml --strict
```

### Configuration Checker
Analyzes HA configuration structure, finds entities, tracks includes and secrets:
```bash
python3 {baseDir}/scripts/check_config.py /path/to/config/directory
python3 {baseDir}/scripts/check_config.py /path/to/config.yaml --verbose
```

### Lovelace Validator
Validates Lovelace dashboard configurations (YAML and JSON .storage format):
```bash
python3 {baseDir}/scripts/lovelace_validator.py /path/to/ui-lovelace.yaml
python3 {baseDir}/scripts/lovelace_validator.py /path/to/.storage/lovelace --strict
```
Features:
- Validates card types (built-in and custom)
- Checks entity ID formats
- Validates actions (tap_action, hold_action)
- Detects custom cards (HACS)
- Supports both YAML and JSON storage formats

### Duplicate Finder
Finds duplicate and similar automations/scripts across configuration files:
```bash
python3 {baseDir}/scripts/find_duplicates.py /path/to/config/directory
python3 {baseDir}/scripts/find_duplicates.py /path/to/automations.yaml --verbose
```
Features:
- Exact duplicate detection (identical triggers + actions)
- Similar item detection (80% threshold for names, entities, structure)
- Trigger conflict detection (multiple automations on same trigger)
- Entity overlap analysis between automations
- JSON output with detailed findings

## Pre-Save Validation Hook

This plugin includes a pre-save hook that automatically validates YAML files before saving. It checks for:
- Tab characters (HA requires spaces)
- Basic YAML syntax errors

The hook runs automatically on Write/Edit operations for `.yaml` and `.yml` files.

## YAML Requirements

- **Indentation**: 2 spaces per level (never tabs)
- **Strings**: Quote boolean-like values ("on", "off", "yes", "no")
- **Lists**: Use `-` prefix with proper indentation
- **Comments**: Use `#` for inline documentation
- **Key Terms**: Use `action:` (not `service:`), `triggers:` (not `trigger:`), `actions:` (not `action:` for sequences)

## File Organization

### Basic Includes
```yaml
# configuration.yaml
automation: !include automations.yaml
script: !include scripts.yaml
sensor: !include sensors.yaml
```

### Directory Includes
```yaml
# Merge all files in directory
automation: !include_dir_merge_list automations/
sensor: !include_dir_merge_list sensors/
```

### Secrets Management
```yaml
# secrets.yaml
mqtt_password: "super_secret_password"
api_key: "your-api-key-here"

# configuration.yaml
mqtt:
  password: !secret mqtt_password
```

## Automations (2024+ Syntax)

### Basic Structure
```yaml
automation:
  - alias: "Descriptive Name"
    id: unique_automation_id
    description: "What this automation does"
    mode: single  # single, restart, queued, parallel
    triggers:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "on"
    conditions:
      - condition: time
        after: "sunset"
    actions:
      - action: light.turn_on
        target:
          entity_id: light.living_room
```

### Common Triggers

**State Trigger**
```yaml
triggers:
  - trigger: state
    entity_id: sensor.temperature
    from: "off"
    to: "on"
    for:
      minutes: 5
```

**Time Trigger**
```yaml
triggers:
  - trigger: time
    at: "07:00:00"
```

**Numeric State Trigger**
```yaml
triggers:
  - trigger: numeric_state
    entity_id: sensor.temperature
    above: 25
    below: 30
```

**Sun Trigger**
```yaml
triggers:
  - trigger: sun
    event: sunset
    offset: "-00:30:00"
```

**Template Trigger**
```yaml
triggers:
  - trigger: template
    value_template: "{{ states('sensor.power') | float > 1000 }}"
```

**Calendar Trigger**
```yaml
triggers:
  - trigger: calendar
    entity_id: calendar.work
    event: start
    offset: "-00:15:00"  # 15 min before event
```

**Device Trigger**
```yaml
triggers:
  - trigger: device
    device_id: abc123
    domain: zwave_js
    type: event.value_notification.entry_control
```

**Event Trigger**
```yaml
triggers:
  - trigger: event
    event_type: mobile_app_notification_action
    event_data:
      action: "CONFIRM_ACTION"
```

### Trigger IDs (for multi-trigger automations)
```yaml
triggers:
  - trigger: state
    id: "motion_detected"
    entity_id: binary_sensor.motion
    to: "on"
  - trigger: state
    id: "door_opened"
    entity_id: binary_sensor.door
    to: "on"
actions:
  - choose:
      - conditions:
          - condition: trigger
            id: "motion_detected"
        sequence:
          - action: light.turn_on
            target:
              entity_id: light.hallway
```

### Common Actions

**Service Call**
```yaml
actions:
  - action: light.turn_on
    target:
      entity_id: light.bedroom
    data:
      brightness_pct: 50
      color_temp: 350
```

**Delay**
```yaml
actions:
  - delay:
      seconds: 30
```

**Conditional (Choose)**
```yaml
actions:
  - choose:
      - conditions:
          - condition: state
            entity_id: sun.sun
            state: "below_horizon"
        sequence:
          - action: light.turn_on
            target:
              entity_id: light.porch
    default:
      - action: light.turn_off
        target:
          entity_id: light.porch
```

**Repeat**
```yaml
actions:
  - repeat:
      count: 3
      sequence:
        - action: notify.mobile_app
          data:
            message: "Alert!"
        - delay:
            minutes: 1
```

**If-Then-Else**
```yaml
actions:
  - if:
      - condition: state
        entity_id: sun.sun
        state: "below_horizon"
    then:
      - action: light.turn_on
        target:
          entity_id: light.porch
    else:
      - action: light.turn_off
        target:
          entity_id: light.porch
```

**Parallel Actions**
```yaml
actions:
  - parallel:
      - action: notify.person1
        data:
          message: "Alert sent simultaneously!"
      - action: notify.person2
        data:
          message: "Alert sent simultaneously!"
      - sequence:
          - action: light.turn_on
            target:
              entity_id: light.alarm
          - delay:
              seconds: 5
          - action: light.turn_off
            target:
              entity_id: light.alarm
```

**Wait for Trigger**
```yaml
actions:
  - action: light.turn_on
    target:
      entity_id: light.porch
  - wait_for_trigger:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "off"
    timeout:
      minutes: 10
    continue_on_timeout: true
  - action: light.turn_off
    target:
      entity_id: light.porch
```

**Response Variables (get data from actions)**
```yaml
actions:
  - action: calendar.get_events
    target:
      entity_id: calendar.work
    data:
      duration:
        hours: 24
    response_variable: agenda
  - action: notify.mobile_app
    data:
      message: "You have {{ agenda['calendar.work'].events | count }} events today"
```

**Continue on Error**
```yaml
actions:
  - action: notify.unreliable_service
    data:
      message: "This might fail"
    continue_on_error: true
  - action: light.turn_on
    target:
      entity_id: light.bedroom
```

**Stop with Response**
```yaml
actions:
  - if:
      - condition: state
        entity_id: input_boolean.enabled
        state: "off"
    then:
      - stop: "Feature is disabled"
        error: true
  - action: script.do_something
```

## Scripts

```yaml
script:
  morning_routine:
    alias: "Morning Routine"
    description: "Start the day"
    fields:
      brightness:
        description: "Light brightness"
        example: 80
        default: 100
        selector:
          number:
            min: 0
            max: 100
    sequence:
      - action: light.turn_on
        target:
          area_id: bedroom
        data:
          brightness_pct: "{{ brightness }}"
      - action: media_player.play_media
        target:
          entity_id: media_player.speaker
        data:
          media_content_id: "morning_news"
          media_content_type: "music"
```

## Jinja2 Templates

### State Functions
```yaml
# Get state
{{ states('sensor.temperature') }}

# Get attribute
{{ state_attr('climate.thermostat', 'current_temperature') }}

# Check if entity exists
{{ states.sensor.temperature is defined }}
```

### Filters and Tests
```yaml
# Convert types
{{ states('sensor.temp') | float(0) }}
{{ states('sensor.count') | int(0) }}

# Math operations
{{ states('sensor.power') | float * 0.15 | round(2) }}

# Date/time
{{ now().strftime('%H:%M') }}
{{ as_timestamp(now()) }}
```

### Template Sensors
```yaml
template:
  - sensor:
      - name: "Total Power Usage"
        unit_of_measurement: "W"
        state: >
          {{ states('sensor.plug_1_power') | float(0) +
             states('sensor.plug_2_power') | float(0) }}
        availability: >
          {{ states('sensor.plug_1_power') not in ['unknown', 'unavailable'] }}
```

## Lovelace Dashboards

### Enable YAML Mode
```yaml
# configuration.yaml
lovelace:
  mode: yaml
```

### Basic Dashboard Structure
```yaml
# ui-lovelace.yaml
title: My Home
views:
  - title: Home
    path: home
    icon: mdi:home
    cards:
      - type: entities
        title: Living Room
        entities:
          - light.living_room
          - switch.fan
```

### Common Card Types

**Entities Card**
```yaml
type: entities
title: Room Controls
state_color: true
entities:
  - entity: light.ceiling
    name: Ceiling Light
  - type: divider
  - entity: climate.thermostat
```

**Button Card**
```yaml
type: button
entity: light.bedroom
name: Bedroom
icon: mdi:lightbulb
tap_action:
  action: toggle
hold_action:
  action: more-info
```

**Grid Layout**
```yaml
type: grid
columns: 3
square: true
cards:
  - type: button
    entity: light.1
  - type: button
    entity: light.2
  - type: button
    entity: light.3
```

**Area Card**
```yaml
type: area
area: living_room
display_type: compact
navigation_path: /lovelace/living-room
sensor_classes:
  - temperature
  - humidity
```

**Conditional Card**
```yaml
type: conditional
conditions:
  - condition: state
    entity: person.john
    state: home
card:
  type: entities
  entities:
    - light.johns_room
```

### Card Actions
```yaml
tap_action:
  action: toggle           # Toggle entity
  # action: more-info      # Show details
  # action: navigate       # Go to view
  #   navigation_path: /lovelace/lights
  # action: call-service   # Call action
  #   service: light.turn_on
  #   target:
  #     entity_id: light.all
```

### Popular Custom Cards (via HACS)

**Mushroom Cards**
```yaml
type: custom:mushroom-light-card
entity: light.bedroom
show_brightness_control: true
use_light_color: true
```

**Button Card (Custom)**
```yaml
type: custom:button-card
entity: light.bedroom
name: Bedroom
styles:
  card:
    - border-radius: 12px
state:
  - value: "on"
    styles:
      icon:
        - color: amber
```

## Validation Tools

1. **Developer Tools > YAML**: Check configuration syntax
2. **Developer Tools > Template**: Test Jinja2 templates
3. **Developer Tools > States**: Verify entity states
4. **Logs**: Enable debug logging for troubleshooting

```yaml
logger:
  default: info
  logs:
    homeassistant.components.automation: debug
```

## Common Issues

| Problem | Solution |
|---------|----------|
| Tab characters | Replace with 2 spaces |
| Unquoted booleans | Quote "on", "off", "yes", "no" |
| Template errors | Test in Developer Tools first |
| Entity not found | Check entity_id spelling |
| Automation not firing | Verify trigger conditions in trace |

## Blueprints

Reusable automation templates with configurable inputs:

```yaml
blueprint:
  name: Motion-activated Light
  description: Turn on a light when motion is detected
  domain: automation
  input:
    motion_sensor:
      name: Motion Sensor
      selector:
        entity:
          filter:
            - domain: binary_sensor
              device_class: motion
    target_light:
      name: Light
      selector:
        target:
          entity:
            - domain: light
    delay_time:
      name: Delay
      default: 120
      selector:
        number:
          min: 0
          max: 3600
          unit_of_measurement: seconds

triggers:
  - trigger: state
    entity_id: !input motion_sensor
    to: "on"

actions:
  - action: light.turn_on
    target: !input target_light
  - wait_for_trigger:
      - trigger: state
        entity_id: !input motion_sensor
        to: "off"
        for:
          seconds: !input delay_time
  - action: light.turn_off
    target: !input target_light
```

## Reference Files

For detailed patterns and examples, see:
- `references/patterns.md` - Common automation patterns
- `references/templates.md` - Template sensor examples
- `references/lovelace.md` - Dashboard cards and layouts
- `references/troubleshooting.md` - Error solutions
- `references/best-practices.md` - Optimization tips
- `references/blueprints.md` - Blueprint creation guide
- `examples/` - Complete working configurations
