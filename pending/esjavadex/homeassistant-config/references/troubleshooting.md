# Home Assistant Troubleshooting Guide

Common issues and their solutions.

## YAML Syntax Errors

### Tab Characters
**Error**: `while scanning for the next token found character '\t'`

**Solution**: Replace tabs with spaces (2 spaces per indentation level)
```bash
# Find tabs in files
grep -P '\t' configuration.yaml
```

### Incorrect Indentation
**Error**: `mapping values are not allowed here`

**Solution**: Ensure consistent 2-space indentation
```yaml
# Wrong
automation:
  - alias: Test
   triggers:  # Wrong - 3 spaces
    - trigger: state

# Correct
automation:
  - alias: Test
    triggers:  # Correct - 4 spaces (2 levels)
      - trigger: state
```

### Unquoted Special Values
**Error**: Boolean conversion issues or unexpected behavior

**Solution**: Quote boolean-like strings
```yaml
# Wrong - interpreted as boolean
name: on
state: "yes"

# Correct
name: "on"
state: "yes"
```

### Missing Colons
**Error**: `expected '<document start>'`

**Solution**: Ensure all keys have colons
```yaml
# Wrong
automation
  - alias: Test

# Correct
automation:
  - alias: Test
```

## Template Errors

### Undefined Variables
**Error**: `UndefinedError: 'states' is undefined`

**Solution**: Use the correct syntax
```yaml
# Wrong
{{ sensor.temperature }}

# Correct
{{ states('sensor.temperature') }}
```

### Type Conversion
**Error**: `could not convert string to float`

**Solution**: Provide default values
```yaml
# Wrong - fails if unavailable
{{ states('sensor.temp') | float }}

# Correct - with default
{{ states('sensor.temp') | float(0) }}
```

### Unavailable States
**Issue**: Template shows "unavailable" or fails

**Solution**: Handle unavailable states
```yaml
{% if states('sensor.temp') not in ['unknown', 'unavailable'] %}
  {{ states('sensor.temp') | float }}
{% else %}
  N/A
{% endif %}
```

### Testing Templates
1. Go to **Developer Tools > Template**
2. Paste your template
3. Check the result in real-time

## Automation Issues

### Automation Not Triggering

**Check 1**: Is it enabled?
```yaml
# In automations.yaml
- alias: My Automation
  id: my_automation_id  # Required for UI management
```

**Check 2**: Verify trigger conditions
- Developer Tools > States - check entity states
- Check automation trace for details

**Check 3**: Mode conflicts
```yaml
mode: single  # Won't run if already running
mode: restart  # Stops current run, starts new
mode: queued  # Queues multiple runs
mode: parallel  # Runs simultaneously
```

### Wrong Entity ID
**Error**: `Entity not found`

**Solution**:
1. Check exact entity_id in Developer Tools > States
2. Entity IDs are case-sensitive
3. Look for typos

### Condition Always False
**Debug**: Add temporary notification
```yaml
actions:
  - action: notify.mobile_app
    data:
      message: "Automation triggered - checking conditions"
  - condition: state
    entity_id: binary_sensor.test
    state: "on"
  - action: notify.mobile_app
    data:
      message: "Condition passed"
```

## Service Call Errors

### Invalid Service
**Error**: `Service not found`

**Solution**: Check correct service name
```yaml
# Old syntax (deprecated)
service: homeassistant.turn_on

# New syntax (2024+)
action: homeassistant.turn_on
```

### Missing Target
**Error**: `No entities targeted`

**Solution**: Use proper target format
```yaml
# Wrong
action: light.turn_on
data:
  entity_id: light.bedroom

# Correct
action: light.turn_on
target:
  entity_id: light.bedroom
```

### Invalid Data
**Error**: `Invalid value for brightness`

**Solution**: Check parameter types
```yaml
# Wrong - string instead of int
data:
  brightness: "255"

# Correct
data:
  brightness: 255

# Or with template
data:
  brightness: "{{ 255 }}"
```

## Integration Issues

### Entity Unavailable
**Causes**:
- Device offline
- Integration not loaded
- Network issues

**Debug**:
1. Check integration status in Settings > Devices & Services
2. Check Home Assistant logs
3. Reload the integration

### Slow Entities
**Issue**: State updates delayed

**Solutions**:
- Check polling interval in integration settings
- Use webhooks/push if available
- Consider `scan_interval` for sensors

## Log Analysis

### Enable Debug Logging
```yaml
logger:
  default: warning
  logs:
    homeassistant.components.automation: debug
    homeassistant.components.script: debug
    homeassistant.helpers.template: debug
    custom_components.my_integration: debug
```

### Common Log Messages

| Message | Meaning | Solution |
|---------|---------|----------|
| `Error while executing automation` | Action failed | Check service calls |
| `Automation triggered but all conditions False` | Conditions not met | Review conditions |
| `Template error` | Jinja2 syntax error | Test in Developer Tools |
| `Entity not found` | Wrong entity_id | Check spelling |

## Configuration Validation

### Check Configuration
```bash
# In terminal
ha core check

# Or in HA
Settings > System > General > Check Configuration
```

### Restart Options
1. **YAML Reload**: For automations, scripts, groups
2. **Quick Reload**: For templates, input helpers
3. **Full Restart**: For configuration.yaml changes

## Performance Issues

### Slow Startup
**Causes**:
- Too many integrations
- Large automations file
- Template sensors with heavy calculations

**Solutions**:
- Split configuration into multiple files
- Use trigger-based templates
- Optimize template calculations

### High CPU Usage
**Debug**:
```yaml
# Check recorder database size
# Settings > System > Repairs

# Exclude high-frequency entities
recorder:
  exclude:
    entities:
      - sensor.high_frequency_sensor
```

## Common Mistakes Checklist

- [ ] YAML uses spaces, not tabs
- [ ] Boolean strings are quoted
- [ ] Entity IDs match exactly
- [ ] Templates tested in Developer Tools
- [ ] Automations have unique IDs
- [ ] Service calls use correct syntax
- [ ] Conditions use proper format
- [ ] Configuration validated before restart
