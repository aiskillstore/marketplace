---
name: home-assistant-manager
description: Expert-level Home Assistant configuration management with efficient deployment workflows (git and rapid scp iteration), remote CLI access via SSH and hass-cli, automation verification protocols, log analysis, reload vs restart optimization, and comprehensive Lovelace dashboard management for tablet-optimized UIs. Includes template patterns, card types, debugging strategies, and real-world examples.
---

# Home Assistant Manager

Expert-level Home Assistant configuration management with efficient workflows, remote CLI access, and verification protocols.

## Core Capabilities

- Remote Home Assistant instance management via SSH and hass-cli
- Smart deployment workflows (git-based and rapid iteration)
- Configuration validation and safety checks
- Automation testing and verification
- Log analysis and error detection
- Reload vs restart optimization
- Lovelace dashboard development and optimization
- Template syntax patterns and debugging
- Tablet-optimized UI design

## Prerequisites

Before starting, verify the environment has:
1. SSH access to Home Assistant instance (`root@homeassistant.local`)
2. `hass-cli` installed locally
3. Environment variables loaded (HASS_SERVER, HASS_TOKEN)
4. Git repository connected to HA `/config` directory
5. Context7 MCP server with Home Assistant docs (recommended)

## Remote Access Patterns

### Using hass-cli (Local, via REST API)

All `hass-cli` commands use environment variables automatically:

```bash
# List entities
hass-cli state list

# Get specific state
hass-cli state get sensor.entity_name

# Call services
hass-cli service call automation.reload
hass-cli service call automation.trigger --arguments entity_id=automation.name
```

### Using SSH for HA CLI

```bash
# Check configuration validity
ssh root@homeassistant.local "ha core check"

# Restart Home Assistant
ssh root@homeassistant.local "ha core restart"

# View logs
ssh root@homeassistant.local "ha core logs"

# Tail logs with grep
ssh root@homeassistant.local "ha core logs | grep -i error | tail -20"
```

## Deployment Workflows

### Standard Git Workflow (Final Changes)

Use for changes you want in version control:

```bash
# 1. Make changes locally
# 2. Check validity
ssh root@homeassistant.local "ha core check"

# 3. Commit and push
git add file.yaml
git commit -m "Description"
git push

# 4. CRITICAL: Pull to HA instance
ssh root@homeassistant.local "cd /config && git pull"

# 5. Reload or restart
hass-cli service call automation.reload  # if reload sufficient
# OR
ssh root@homeassistant.local "ha core restart"  # if restart needed

# 6. Verify
hass-cli state get sensor.new_entity
ssh root@homeassistant.local "ha core logs | grep -i error | tail -20"
```

### Rapid Development Workflow (Testing/Iteration)

Use `scp` for quick testing before committing:

```bash
# 1. Make changes locally
# 2. Quick deploy
scp automations.yaml root@homeassistant.local:/config/

# 3. Reload/restart
hass-cli service call automation.reload

# 4. Test and iterate (repeat 1-3 as needed)

# 5. Once finalized, commit to git
git add automations.yaml
git commit -m "Final tested changes"
git push
```

**When to use scp:**
- 🚀 Rapid iteration and testing
- 🔄 Frequent small adjustments
- 🧪 Experimental changes
- 🎨 UI/Dashboard work

**When to use git:**
- ✅ Final tested changes
- 📦 Version control tracking
- 🔒 Important configs
- 👥 Changes to document

## Reload vs Restart Decision Making

**ALWAYS assess if reload is sufficient before requiring a full restart.**

### Can be reloaded (fast, preferred):
- ✅ Automations: `hass-cli service call automation.reload`
- ✅ Scripts: `hass-cli service call script.reload`
- ✅ Scenes: `hass-cli service call scene.reload`
- ✅ Template entities: `hass-cli service call template.reload`
- ✅ Groups: `hass-cli service call group.reload`
- ✅ Themes: `hass-cli service call frontend.reload_themes`

### Require full restart:
- ❌ Min/Max sensors and platform-based sensors
- ❌ New integrations in configuration.yaml
- ❌ Core configuration changes
- ❌ MQTT sensor/binary_sensor platforms

## Automation Verification Workflow

**ALWAYS verify automations after deployment:**

### Step 1: Deploy
```bash
git add automations.yaml && git commit -m "..." && git push
ssh root@homeassistant.local "cd /config && git pull"
```

### Step 2: Check Configuration
```bash
ssh root@homeassistant.local "ha core check"
```

### Step 3: Reload
```bash
hass-cli service call automation.reload
```

### Step 4: Manually Trigger
```bash
hass-cli service call automation.trigger --arguments entity_id=automation.name
```

**Why trigger manually?**
- Instant feedback (don't wait for scheduled triggers)
- Verify logic before production
- Catch errors immediately

### Step 5: Check Logs
```bash
sleep 3
ssh root@homeassistant.local "ha core logs | grep -i 'automation_name' | tail -20"
```

**Success indicators:**
- `Initialized trigger AutomationName`
- `Running automation actions`
- `Executing step ...`
- No ERROR or WARNING messages

**Error indicators:**
- `Error executing script`
- `Invalid data for call_service`
- `TypeError`, `Template variable warning`

### Step 6: Verify Outcome

**For notifications:**
- Ask user if they received it
- Check logs for mobile_app messages

**For device control:**
```bash
hass-cli state get switch.device_name
```

**For sensors:**
```bash
hass-cli state get sensor.new_sensor
```

### Step 7: Fix and Re-test if Needed
If errors found:
1. Identify root cause from error messages
2. Fix the issue
3. Re-deploy (steps 1-2)
4. Re-verify (steps 3-6)

## Dashboard Management

### Dashboard Fundamentals

**What are Lovelace Dashboards?**
- JSON files in `.storage/` directory (e.g., `.storage/lovelace.control_center`)
- UI configuration for Home Assistant frontend
- Optimizable for different devices (mobile, tablet, wall panels)

**Critical Understanding:**
- Creating dashboard file is NOT enough - must register in `.storage/lovelace_dashboards`
- Dashboard changes don't require HA restart (just browser refresh)
- Use panel view for full-screen content (maps, cameras)
- Use sections view for organized multi-card layouts

### Dashboard Development Workflow

**Rapid Iteration with scp (Recommended for dashboards):**

```bash
# 1. Make changes locally
vim .storage/lovelace.control_center

# 2. Deploy immediately (no git commit yet)
scp .storage/lovelace.control_center root@homeassistant.local:/config/.storage/

# 3. Refresh browser (Ctrl+F5 or Cmd+Shift+R)
# No HA restart needed!

# 4. Iterate: Repeat 1-3 until perfect

# 5. Commit when stable
git add .storage/lovelace.control_center
git commit -m "Update dashboard layout"
git push
ssh root@homeassistant.local "cd /config && git pull"
```

**Why scp for dashboards:**
- Instant feedback (no HA restart)
- Iterate quickly on visual changes
- Commit only stable versions

### Creating New Dashboard

**Complete workflow:**

```bash
# Step 1: Create dashboard file
cp .storage/lovelace.my_home .storage/lovelace.new_dashboard

# Step 2: Register in lovelace_dashboards
# Edit .storage/lovelace_dashboards to add:
{
  "id": "new_dashboard",
  "show_in_sidebar": true,
  "icon": "mdi:tablet-dashboard",
  "title": "New Dashboard",
  "require_admin": false,
  "mode": "storage",
  "url_path": "new-dashboard"
}

# Step 3: Deploy both files
scp .storage/lovelace.new_dashboard root@homeassistant.local:/config/.storage/
scp .storage/lovelace_dashboards root@homeassistant.local:/config/.storage/

# Step 4: Restart HA (required for registry changes)
ssh root@homeassistant.local "ha core restart"
sleep 30

# Step 5: Verify appears in sidebar
```

**Update .gitignore to track:**
```gitignore
# Exclude .storage/ by default
.storage/

# Include dashboard files
!.storage/lovelace.new_dashboard
!.storage/lovelace_dashboards
```

### View Types Decision Matrix

**Use Panel View when:**
- Displaying full-screen map (vacuum, cameras)
- Single large card needs full width
- Want zero margins/padding
- Minimize scrolling

**Use Sections View when:**
- Organizing multiple cards
- Need responsive grid layout
- Building multi-section dashboards

**Layout Example:**
```json
// Panel view - full width, no margins
{
  "type": "panel",
  "title": "Vacuum Map",
  "path": "map",
  "cards": [
    {
      "type": "custom:xiaomi-vacuum-map-card",
      "entity": "vacuum.dusty"
    }
  ]
}

// Sections view - organized, has ~10% margins
{
  "type": "sections",
  "title": "Home",
  "sections": [
    {
      "type": "grid",
      "cards": [...]
    }
  ]
}
```

### Card Types Quick Reference

**Mushroom Cards (Modern, Touch-Optimized):**
```json
{
  "type": "custom:mushroom-light-card",
  "entity": "light.living_room",
  "use_light_color": true,
  "show_brightness_control": true,
  "collapsible_controls": true,
  "fill_container": true
}
```
- Best for tablets and touch screens
- Animated, colorful icons
- Built-in slider controls

**Mushroom Template Card (Dynamic Content):**
```json
{
  "type": "custom:mushroom-template-card",
  "primary": "All Doors",
  "secondary": "{% set sensors = ['binary_sensor.front_door'] %}\n{% set open = sensors | select('is_state', 'on') | list | length %}\n{{ open }} / {{ sensors | length }} open",
  "icon": "mdi:door",
  "icon_color": "{% if open > 0 %}red{% else %}green{% endif %}"
}
```
- Use Jinja2 templates for dynamic content
- Color-code status with icon_color
- Multi-line templates use `\n` in JSON

**Tile Card (Built-in, Modern):**
```json
{
  "type": "tile",
  "entity": "climate.thermostat",
  "features": [
    {"type": "climate-hvac-modes", "hvac_modes": ["heat", "cool", "fan_only", "off"]},
    {"type": "target-temperature"}
  ]
}
```
- No custom cards required
- Built-in features for controls

### Common Template Patterns

**Counting Open Doors:**
```jinja2
{% set door_sensors = [
  'binary_sensor.front_door',
  'binary_sensor.back_door'
] %}
{% set open = door_sensors | select('is_state', 'on') | list | length %}
{{ open }} / {{ door_sensors | length }} open
```

**Color-Coded Days Until:**
```jinja2
{% set days = state_attr('sensor.bin_collection', 'daysTo') | int %}
{% if days <= 1 %}red
{% elif days <= 3 %}amber
{% elif days <= 7 %}yellow
{% else %}grey
{% endif %}
```

**Conditional Display:**
```jinja2
{% set bins = [] %}
{% if days and days | int <= 7 %}
  {% set bins = bins + ['Recycling'] %}
{% endif %}
{% if bins %}This week: {{ bins | join(', ') }}{% else %}None this week{% endif %}
```

**IMPORTANT:** Always use `| int` or `| float` to avoid type errors when comparing

### Tablet Optimization

**Screen-specific layouts:**
- 11-inch tablets: 3-4 columns
- Touch targets: minimum 44x44px
- Minimize scrolling: Use panel view for full-screen
- Visual feedback: Color-coded status (red/green/amber)

**Grid Layout for Tablets:**
```json
{
  "type": "grid",
  "columns": 3,
  "square": false,
  "cards": [
    {"type": "custom:mushroom-light-card", "entity": "light.living_room"},
    {"type": "custom:mushroom-light-card", "entity": "light.bedroom"}
  ]
}
```

### Common Dashboard Pitfalls

**Problem 1: Dashboard Not in Sidebar**
- **Cause:** File created but not registered
- **Fix:** Add to `.storage/lovelace_dashboards` and restart HA

**Problem 2: "Configuration Error" in Card**
- **Cause:** Custom card not installed, wrong syntax, template error
- **Fix:**
  - Check HACS for card installation
  - Check browser console (F12) for details
  - Test templates in Developer Tools → Template

**Problem 3: Auto-Entities Fails**
- **Cause:** `card_param` not supported by card type
- **Fix:** Use cards that accept `entities` parameter:
  - ✅ Works: `entities`, `vertical-stack`, `horizontal-stack`
  - ❌ Doesn't work: `grid`, `glance` (without specific syntax)

**Problem 4: Vacuum Map Has Margins/Scrolling**
- **Cause:** Using sections view (has margins)
- **Fix:** Use panel view for full-width, no scrolling

**Problem 5: Template Type Errors**
- **Error:** `TypeError: '<' not supported between instances of 'str' and 'int'`
- **Fix:** Use type filters: `states('sensor.days') | int < 7`

### Dashboard Debugging

**1. Browser Console (F12):**
- Check for red errors when loading dashboard
- Common: "Custom element doesn't exist" → Card not installed

**2. Validate JSON Syntax:**
```bash
python3 -m json.tool .storage/lovelace.control_center > /dev/null
```

**3. Test Templates:**
```
Home Assistant → Developer Tools → Template
Paste template to test before adding to dashboard
```

**4. Verify Entities:**
```bash
hass-cli state get binary_sensor.front_door
```

**5. Clear Browser Cache:**
- Hard refresh: Ctrl+F5 or Cmd+Shift+R
- Try incognito window

## Real-World Examples

### Quick Controls Dashboard Section
```json
{
  "type": "grid",
  "title": "Quick Controls",
  "cards": [
    {
      "type": "custom:mushroom-template-card",
      "primary": "All Doors",
      "secondary": "{% set doors = ['binary_sensor.front_door', 'binary_sensor.back_door'] %}\n{% set open = doors | select('is_state', 'on') | list | length %}\n{{ open }} / {{ doors | length }} open",
      "icon": "mdi:door",
      "icon_color": "{% if open > 0 %}red{% else %}green{% endif %}"
    },
    {
      "type": "tile",
      "entity": "climate.thermostat",
      "features": [
        {"type": "climate-hvac-modes", "hvac_modes": ["heat", "cool", "fan_only", "off"]},
        {"type": "target-temperature"}
      ]
    }
  ]
}
```

### Individual Light Cards (Touch-Friendly)
```json
{
  "type": "grid",
  "title": "Lights",
  "columns": 3,
  "cards": [
    {
      "type": "custom:mushroom-light-card",
      "entity": "light.office_studio",
      "name": "Office",
      "use_light_color": true,
      "show_brightness_control": true,
      "collapsible_controls": true
    }
  ]
}
```

### Full-Screen Vacuum Map
```json
{
  "type": "panel",
  "title": "Vacuum",
  "path": "vacuum-map",
  "cards": [
    {
      "type": "custom:xiaomi-vacuum-map-card",
      "vacuum_platform": "Tasshack/dreame-vacuum",
      "entity": "vacuum.dusty"
    }
  ]
}
```

## Common Commands Quick Reference

```bash
# Configuration
ssh root@homeassistant.local "ha core check"
ssh root@homeassistant.local "ha core restart"

# Logs
ssh root@homeassistant.local "ha core logs | tail -50"
ssh root@homeassistant.local "ha core logs | grep -i error | tail -20"

# State/Services
hass-cli state list
hass-cli state get entity.name
hass-cli service call automation.reload
hass-cli service call automation.trigger --arguments entity_id=automation.name

# Deployment
git add . && git commit -m "..." && git push
ssh root@homeassistant.local "cd /config && git pull"
scp file.yaml root@homeassistant.local:/config/

# Dashboard deployment
scp .storage/lovelace.my_dashboard root@homeassistant.local:/config/.storage/
python3 -m json.tool .storage/lovelace.my_dashboard > /dev/null  # Validate JSON

# Quick test cycle
scp automations.yaml root@homeassistant.local:/config/
hass-cli service call automation.reload
hass-cli service call automation.trigger --arguments entity_id=automation.name
ssh root@homeassistant.local "ha core logs | grep -i 'automation' | tail -10"
```

## Best Practices Summary

1. **Always check configuration** before restart: `ha core check`
2. **Prefer reload over restart** when possible
3. **Test automations manually** after deployment
4. **Check logs** for errors after every change
5. **Use scp for rapid iteration**, git for final changes
6. **Verify outcomes** - don't assume it worked
7. **Use Context7** for current documentation
8. **Test templates in Dev Tools** before adding to dashboards
9. **Validate JSON syntax** before deploying dashboards
10. **Test on actual device** for tablet dashboards
11. **Color-code status** for visual feedback (red/green/amber)
12. **Commit only stable versions** - test with scp first

## Workflow Decision Tree

```
Configuration Change Needed
├─ Is this final/tested?
│  ├─ YES → Use git workflow
│  └─ NO → Use scp workflow
├─ Check configuration valid
├─ Deploy (git pull or scp)
├─ Needs restart?
│  ├─ YES → ha core restart
│  └─ NO → Use appropriate reload
├─ Verify in logs
└─ Test outcome

Dashboard Change Needed
├─ Make changes locally
├─ Deploy via scp for testing
├─ Refresh browser (Ctrl+F5)
├─ Test on target device
├─ Iterate until perfect
└─ Commit to git when stable
```

---

This skill encapsulates efficient Home Assistant management workflows developed through iterative optimization and real-world dashboard development. Apply these patterns to any Home Assistant instance for reliable, fast, and safe configuration management.
