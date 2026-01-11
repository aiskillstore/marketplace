# Home Assistant Blueprints Guide

Blueprints are reusable automation and script templates with configurable inputs.

## Blueprint Structure

### Basic Blueprint
```yaml
blueprint:
  name: Motion-activated Light
  description: Turn on a light when motion is detected
  domain: automation  # or 'script'
  author: Your Name
  source_url: https://github.com/your-repo/blueprint.yaml

  input:
    motion_sensor:
      name: Motion Sensor
      description: The sensor that detects motion
      selector:
        entity:
          filter:
            - domain: binary_sensor
              device_class: motion

    target_light:
      name: Light
      description: The light to turn on
      selector:
        target:
          entity:
            - domain: light

    wait_time:
      name: Wait Time
      description: Time to wait after motion stops
      default: 120
      selector:
        number:
          min: 0
          max: 3600
          unit_of_measurement: seconds

# Automation configuration using inputs
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
          seconds: !input wait_time
  - action: light.turn_off
    target: !input target_light
```

## Input Selectors

### Entity Selector
```yaml
input:
  my_light:
    name: Light Entity
    selector:
      entity:
        filter:
          - domain: light
          - domain: switch
            device_class: outlet

  my_sensor:
    name: Temperature Sensor
    selector:
      entity:
        filter:
          - domain: sensor
            device_class: temperature
        multiple: true  # Allow selecting multiple entities
```

### Target Selector
```yaml
input:
  target_lights:
    name: Target Lights
    selector:
      target:
        entity:
          - domain: light
        device:
          - integration: hue
```

### Device Selector
```yaml
input:
  my_device:
    name: Device
    selector:
      device:
        filter:
          - integration: zha
            manufacturer: IKEA
          - integration: zwave_js
```

### Number Selector
```yaml
input:
  brightness:
    name: Brightness
    default: 80
    selector:
      number:
        min: 0
        max: 100
        step: 5
        unit_of_measurement: "%"
        mode: slider  # or 'box'

  temperature:
    name: Temperature
    selector:
      number:
        min: 16
        max: 30
        unit_of_measurement: "°C"
```

### Time Selector
```yaml
input:
  start_time:
    name: Start Time
    default: "07:00:00"
    selector:
      time:

  duration:
    name: Duration
    default:
      minutes: 30
    selector:
      duration:
        enable_day: false
```

### Boolean Selector
```yaml
input:
  enable_notifications:
    name: Enable Notifications
    default: true
    selector:
      boolean:
```

### Text Selector
```yaml
input:
  custom_message:
    name: Notification Message
    default: "Motion detected!"
    selector:
      text:
        multiline: false
        type: text  # or 'email', 'url', 'password'
```

### Select Selector (Dropdown)
```yaml
input:
  light_mode:
    name: Light Mode
    default: "auto"
    selector:
      select:
        options:
          - label: "Automatic"
            value: "auto"
          - label: "Always On"
            value: "on"
          - label: "Always Off"
            value: "off"
        mode: dropdown  # or 'list'
```

### Area Selector
```yaml
input:
  target_area:
    name: Area
    selector:
      area:
        multiple: false
```

### Color Selector
```yaml
input:
  light_color:
    name: Light Color
    selector:
      color_rgb:

  color_temp:
    name: Color Temperature
    selector:
      color_temp:
        min_mireds: 153
        max_mireds: 500
```

### Action Selector
```yaml
input:
  custom_actions:
    name: Additional Actions
    default: []
    selector:
      action:
```

### Trigger Selector
```yaml
input:
  additional_triggers:
    name: Extra Triggers
    default: []
    selector:
      trigger:
```

### Constant Selector
```yaml
input:
  feature_enabled:
    name: Enable Feature
    selector:
      constant:
        label: "Enabled"
        value: true
```

## Input Sections (Grouping)

```yaml
blueprint:
  name: Advanced Light Control
  domain: automation
  input:
    # Top-level inputs (always visible)
    motion_sensor:
      name: Motion Sensor
      selector:
        entity:
          filter:
            - domain: binary_sensor
              device_class: motion

    # Grouped section
    light_settings:
      name: Light Settings
      icon: mdi:lightbulb
      description: Configure how the lights behave
      collapsed: true  # Start collapsed
      input:
        brightness:
          name: Brightness
          default: 100
          selector:
            number:
              min: 0
              max: 100

        color_temp:
          name: Color Temperature
          default: 3000
          selector:
            number:
              min: 2000
              max: 6500
              unit_of_measurement: "K"

    notification_settings:
      name: Notification Settings
      icon: mdi:bell
      collapsed: true
      input:
        send_notification:
          name: Send Notification
          default: false
          selector:
            boolean:
```

## Using Inputs in Templates

### Expose Input as Variable
```yaml
blueprint:
  name: Example
  input:
    brightness_input:
      selector:
        number:
          min: 0
          max: 100

# Make input available in templates
variables:
  brightness: !input brightness_input

actions:
  - action: light.turn_on
    target:
      entity_id: light.bedroom
    data:
      brightness_pct: "{{ brightness }}"
```

### Conditional Logic with Inputs
```yaml
blueprint:
  name: Conditional Example
  input:
    enable_night_mode:
      default: true
      selector:
        boolean:

variables:
  night_mode: !input enable_night_mode

actions:
  - if:
      - condition: template
        value_template: "{{ night_mode }}"
    then:
      - action: light.turn_on
        data:
          brightness_pct: 20
    else:
      - action: light.turn_on
        data:
          brightness_pct: 100
```

## Trigger Variables

```yaml
blueprint:
  name: Dynamic Event Type
  input:
    event_name:
      selector:
        text:

trigger_variables:
  event_type: !input event_name

triggers:
  - trigger: event
    event_type: "{{ event_type }}"
```

## Merging Triggers from Input

```yaml
blueprint:
  name: Extensible Automation
  input:
    additional_triggers:
      name: Additional Triggers
      default: []
      selector:
        trigger:

triggers:
  - triggers: !input additional_triggers
  - trigger: time
    at: "07:00:00"
```

## Complete Blueprint Examples

### Motion Light with Options
```yaml
blueprint:
  name: Motion-activated Light with Options
  description: >
    Turn on a light when motion is detected.
    Features: adjustable delay, brightness, night mode.
  domain: automation

  input:
    motion_entity:
      name: Motion Sensor
      selector:
        entity:
          filter:
            - domain: binary_sensor
              device_class: motion

    light_target:
      name: Light
      selector:
        target:
          entity:
            - domain: light

    no_motion_wait:
      name: Wait time
      description: Time to leave the light on after motion stops
      default: 120
      selector:
        number:
          min: 0
          max: 3600
          unit_of_measurement: seconds

    light_settings:
      name: Light Settings
      icon: mdi:tune
      collapsed: true
      input:
        day_brightness:
          name: Day Brightness
          default: 100
          selector:
            number:
              min: 0
              max: 100
        night_brightness:
          name: Night Brightness
          default: 30
          selector:
            number:
              min: 0
              max: 100

mode: restart
max_exceeded: silent

variables:
  day_bright: !input day_brightness
  night_bright: !input night_brightness

triggers:
  - trigger: state
    entity_id: !input motion_entity
    to: "on"

conditions: []

actions:
  - action: light.turn_on
    target: !input light_target
    data:
      brightness_pct: >
        {% if is_state('sun.sun', 'above_horizon') %}
          {{ day_bright }}
        {% else %}
          {{ night_bright }}
        {% endif %}

  - wait_for_trigger:
      - trigger: state
        entity_id: !input motion_entity
        to: "off"
        for:
          seconds: !input no_motion_wait

  - action: light.turn_off
    target: !input light_target

```

### Notification on State Change
```yaml
blueprint:
  name: State Change Notification
  description: Send notification when entity changes state
  domain: automation

  input:
    entity:
      name: Entity
      selector:
        entity:

    notify_device:
      name: Device to notify
      selector:
        device:
          filter:
            - integration: mobile_app

    notification_settings:
      name: Notification
      input:
        title:
          name: Title
          default: "State Changed"
          selector:
            text:
        message_template:
          name: Message
          default: "{{ trigger.to_state.name }} is now {{ trigger.to_state.state }}"
          selector:
            text:
              multiline: true

variables:
  title: !input title
  message: !input message_template

triggers:
  - trigger: state
    entity_id: !input entity

conditions:
  - condition: template
    value_template: "{{ trigger.from_state.state != trigger.to_state.state }}"

actions:
  - device_id: !input notify_device
    domain: mobile_app
    type: notify
    title: "{{ title }}"
    message: "{{ message }}"
```

### Script Blueprint with Fields
```yaml
blueprint:
  name: Room Scene Script
  description: Apply scene to a room
  domain: script

  input:
    target_area:
      name: Target Area
      selector:
        area:

fields:
  brightness:
    name: Brightness
    description: Light brightness level
    required: true
    default: 100
    selector:
      number:
        min: 0
        max: 100

  color_temp:
    name: Color Temperature
    default: 3500
    selector:
      number:
        min: 2000
        max: 6500

sequence:
  - action: light.turn_on
    target:
      area_id: !input target_area
    data:
      brightness_pct: "{{ brightness }}"
      kelvin: "{{ color_temp }}"
```

## Using Blueprints

### Import from URL
```yaml
# In Home Assistant UI:
# Settings > Automations & Scenes > Blueprints > Import Blueprint
# Paste URL: https://github.com/user/repo/blob/main/blueprint.yaml
```

### Create Automation from Blueprint
```yaml
# automations.yaml
- id: "living_room_motion_light"
  alias: "Living Room Motion Light"
  use_blueprint:
    path: motion_light.yaml
    input:
      motion_entity: binary_sensor.living_room_motion
      light_target:
        entity_id: light.living_room
      no_motion_wait: 300
      day_brightness: 100
      night_brightness: 20
```

## Blueprint Best Practices

1. **Clear Descriptions**: Add helpful descriptions to all inputs
2. **Sensible Defaults**: Provide default values where appropriate
3. **Input Validation**: Use selector filters to limit invalid choices
4. **Section Organization**: Group related inputs using sections
5. **Mode Selection**: Choose appropriate mode (single, restart, queued, parallel)
6. **Variables**: Use variables block to expose inputs for templates
7. **Documentation**: Include source_url for updates and author attribution
