# Home Assistant Best Practices

Optimization, organization, and maintenance guidelines.

## File Organization

### Split Configuration
```yaml
# configuration.yaml
homeassistant:
  name: Home
  unit_system: metric

automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml
```

### Directory Structure for Large Setups
```yaml
# configuration.yaml
automation: !include_dir_merge_list automations/
sensor: !include_dir_merge_list sensors/
script: !include_dir_merge_named scripts/

# Directory structure
config/
├── automations/
│   ├── lights.yaml
│   ├── climate.yaml
│   └── security.yaml
├── sensors/
│   ├── weather.yaml
│   └── energy.yaml
└── scripts/
    ├── routines.yaml
    └── notifications.yaml
```

### Package Organization
```yaml
# packages/kitchen.yaml
homeassistant:
  customize:
    light.kitchen:
      friendly_name: "Kitchen Lights"

automation:
  - alias: "Kitchen - Motion Lights"
    triggers:
      - trigger: state
        entity_id: binary_sensor.kitchen_motion
        to: "on"
    actions:
      - action: light.turn_on
        target:
          entity_id: light.kitchen

sensor:
  - platform: template
    sensors:
      kitchen_temperature:
        value_template: "{{ state_attr('climate.kitchen', 'current_temperature') }}"
```

## Naming Conventions

### Entity Naming
```yaml
# Use consistent prefixes
light.living_room_ceiling
light.living_room_lamp
sensor.living_room_temperature
binary_sensor.living_room_motion

# Automation naming
"Room - Function - Detail"
"Living Room - Lights - Motion Activated"
"Kitchen - Climate - Window Open"
```

### Automation IDs
```yaml
automation:
  - alias: "Living Room - Auto Lights"
    id: living_room_auto_lights  # Required for UI editing
    # Use snake_case, descriptive, unique
```

## Secrets Management

### Secure Sensitive Data
```yaml
# secrets.yaml (never commit to git)
wifi_password: "your_password"
api_key: "your_api_key"
latitude: 12.3456
longitude: 78.9012

# configuration.yaml
homeassistant:
  latitude: !secret latitude
  longitude: !secret longitude
```

### .gitignore for HA
```
secrets.yaml
*.db
*.log
.storage/
home-assistant_v2.db*
```

## Automation Best Practices

### Use Meaningful Aliases
```yaml
# Bad
- alias: "Automation 1"

# Good
- alias: "Kitchen - Turn off lights after 30min inactivity"
```

### Add Descriptions
```yaml
automation:
  - alias: "Security - Arm at Night"
    description: >
      Arms the security system at 11 PM if no one is awake.
      Checks motion sensors and media players before arming.
```

### Set Appropriate Modes
```yaml
# Single - prevents duplicate runs
mode: single

# Restart - for things like motion lights
mode: restart

# Queued - for sequential actions that shouldn't overlap
mode: queued
max: 5

# Parallel - independent actions
mode: parallel
max: 10
```

### Use Variables for Clarity
```yaml
automation:
  - alias: "Example with Variables"
    variables:
      brightness_day: 100
      brightness_night: 30
      room: "living_room"
    actions:
      - action: light.turn_on
        target:
          entity_id: "light.{{ room }}"
        data:
          brightness_pct: >
            {{ brightness_day if is_state('sun.sun', 'above_horizon')
               else brightness_night }}
```

## Template Optimization

### Cache Repeated Values
```yaml
# Bad - calculates multiple times
state: >
  {{ states('sensor.temp') | float * 1.8 + 32 }}
attributes:
  celsius: "{{ states('sensor.temp') }}"
  fahrenheit: "{{ states('sensor.temp') | float * 1.8 + 32 }}"

# Good - calculate once
state: >
  {% set temp = states('sensor.temp') | float %}
  {{ temp * 1.8 + 32 }}
```

### Use Trigger-Based for High Frequency
```yaml
# Instead of time_pattern with short intervals
template:
  - trigger:
      - trigger: state
        entity_id: sensor.power
    sensor:
      - name: "Power Status"
        state: >
          {% if trigger.to_state.state | float > 1000 %}
            High
          {% else %}
            Normal
          {% endif %}
```

### Provide Defaults
```yaml
# Always provide fallback values
{{ states('sensor.temp') | float(0) }}
{{ state_attr('entity', 'attr') | default('unknown') }}
```

## Performance Guidelines

### Recorder Optimization
```yaml
recorder:
  purge_keep_days: 10
  commit_interval: 30
  exclude:
    domains:
      - automation
      - updater
    entity_globs:
      - sensor.sun*
    entities:
      - sensor.date
```

### History Optimization
```yaml
history:
  exclude:
    domains:
      - automation
      - script
```

### Avoid Excessive Polling
```yaml
# Use event-driven when possible
# Set appropriate scan_interval for REST/scrape sensors
sensor:
  - platform: rest
    scan_interval: 300  # 5 minutes, not default 30 seconds
```

## Error Handling

### Safe Automation Actions
```yaml
actions:
  - action: light.turn_on
    target:
      entity_id: light.bedroom
    continue_on_error: true  # Don't stop on failure
```

### Validate Before Acting
```yaml
conditions:
  - condition: template
    value_template: >
      {{ states('sensor.value') not in ['unknown', 'unavailable'] }}
```

### Timeout for Wait Actions
```yaml
actions:
  - wait_for_trigger:
      - trigger: state
        entity_id: binary_sensor.door
        to: "off"
    timeout:
      minutes: 30
    continue_on_timeout: true
```

## Maintenance

### Regular Backups
- Use built-in backup feature
- Schedule automatic backups
- Store backups off-device

### Version Control
```bash
# Initialize git in config directory
cd /config
git init
git add .
git commit -m "Initial configuration"
```

### Documentation
```yaml
# Add comments to complex automations
automation:
  # This automation handles the morning routine
  # Triggers: Weekdays at 6:30 AM
  # Requirements: Person must be home
  - alias: "Morning Routine"
```

### Review Unused Entities
1. Check Settings > Devices & Services
2. Remove unused integrations
3. Clean up orphaned entities

## Testing

### Test Automations
1. Use Developer Tools > Services to test actions
2. Check automation traces after triggering
3. Use temporary notifications for debugging

### Validate Configuration
```bash
# Before restart
ha core check
```

### Staging Environment
- Consider a test instance for major changes
- Use snapshots before big updates
