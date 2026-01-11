# Lovelace Dashboard Reference

Complete guide for creating Home Assistant dashboards with Lovelace UI.

## Dashboard Configuration

### Enable YAML Mode
```yaml
# configuration.yaml
lovelace:
  mode: yaml
  # Resources for custom cards
  resources:
    - url: /local/custom-cards/button-card.js
      type: module
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
      - type: markdown
        content: Welcome to your **dashboard**.
```

## View Types and Layouts

### Standard View
```yaml
views:
  - title: Living Room
    path: living-room
    icon: mdi:sofa
    theme: dark-mode
    cards:
      - type: entities
        entities:
          - light.living_room
```

### Sidebar Layout
```yaml
views:
  - title: Dashboard
    type: sidebar
    cards:
      # Main column (larger cards)
      - type: weather-forecast
        entity: weather.home
      # Sidebar column (smaller cards)
      - type: gauge
        entity: sensor.temperature
```

### Panel View (Single Card)
```yaml
views:
  - title: Map
    path: map
    panel: true
    cards:
      - type: map
        entities:
          - person.john
```

### Sections Layout (Modern)
```yaml
views:
  - title: Home
    type: sections
    sections:
      - title: Living Room
        cards:
          - type: light
            entity: light.living_room
      - title: Climate
        cards:
          - type: thermostat
            entity: climate.main
```

## Built-in Card Types

### Entities Card
```yaml
type: entities
title: Living Room
show_header_toggle: true
state_color: true
entities:
  - entity: light.ceiling
    name: Ceiling Light
    icon: mdi:ceiling-light
  - entity: switch.fan
  - type: divider
  - entity: sensor.temperature
    secondary_info: last-changed
  - type: section
    label: Controls
  - entity: input_boolean.party_mode
```

### Button Card
```yaml
type: button
entity: light.bedroom
name: Bedroom Light
icon: mdi:lightbulb
show_name: true
show_icon: true
show_state: true
icon_height: 50px
tap_action:
  action: toggle
hold_action:
  action: more-info
```

### Glance Card
```yaml
type: glance
title: Family
show_name: true
show_state: true
columns: 4
entities:
  - entity: person.john
    name: John
  - entity: person.jane
    name: Jane
  - entity: device_tracker.car
    name: Car
```

### Light Card
```yaml
type: light
entity: light.living_room
name: Living Room
icon: mdi:lamp
```

### Thermostat Card
```yaml
type: thermostat
entity: climate.living_room
name: Thermostat
features:
  - type: climate-hvac-modes
    hvac_modes:
      - heat
      - cool
      - "off"
```

### Area Card
```yaml
type: area
area: living_room
display_type: picture
aspect_ratio: "16:9"
navigation_path: /lovelace/living-room
alert_classes:
  - motion
  - moisture
sensor_classes:
  - temperature
  - humidity
features:
  - type: light-brightness
```

### Picture Elements Card
```yaml
type: picture-elements
image: /local/floorplan.png
elements:
  - type: state-icon
    entity: light.living_room
    style:
      top: 30%
      left: 40%
  - type: state-label
    entity: sensor.temperature
    style:
      top: 50%
      left: 60%
      color: white
  - type: service-button
    title: All Off
    style:
      top: 90%
      left: 50%
    service: light.turn_off
    service_data:
      entity_id: all
```

### Media Control Card
```yaml
type: media-control
entity: media_player.living_room
```

### Weather Forecast Card
```yaml
type: weather-forecast
entity: weather.home
show_current: true
show_forecast: true
forecast_type: daily
```

### History Graph Card
```yaml
type: history-graph
title: Temperature History
hours_to_show: 24
entities:
  - sensor.living_room_temperature
  - sensor.bedroom_temperature
```

### Statistics Graph Card
```yaml
type: statistics-graph
title: Energy Usage
entities:
  - sensor.energy_consumption
stat_types:
  - mean
  - min
  - max
period:
  calendar:
    period: day
```

### Gauge Card
```yaml
type: gauge
entity: sensor.cpu_usage
name: CPU
min: 0
max: 100
needle: true
severity:
  green: 0
  yellow: 60
  red: 80
```

### Calendar Card
```yaml
type: calendar
entities:
  - calendar.personal
  - calendar.work
initial_view: dayGridMonth
```

### Map Card
```yaml
type: map
entities:
  - person.john
  - device_tracker.car
default_zoom: 15
hours_to_show: 24
```

### Logbook Card
```yaml
type: logbook
entities:
  - light.living_room
  - switch.kitchen
hours_to_show: 12
```

### Alarm Panel Card
```yaml
type: alarm-panel
entity: alarm_control_panel.home
states:
  - arm_home
  - arm_away
  - arm_night
```

### Shopping List Card
```yaml
type: shopping-list
title: Groceries
```

### Markdown Card
```yaml
type: markdown
title: Welcome
content: |
  ## Good {{ 'morning' if now().hour < 12 else 'afternoon' }}!

  Current temperature: **{{ states('sensor.temperature') }}C**

  {% if is_state('binary_sensor.door', 'on') %}
  **Warning:** Front door is open!
  {% endif %}
```

### Conditional Card
```yaml
type: conditional
conditions:
  - condition: state
    entity: person.john
    state: home
card:
  type: entities
  title: John is Home
  entities:
    - light.johns_room
```

### Entity Filter Card
```yaml
type: entity-filter
entities:
  - light.living_room
  - light.bedroom
  - light.kitchen
state_filter:
  - "on"
card:
  type: glance
  title: Lights On
```

## Layout Cards

### Grid Card
```yaml
type: grid
title: Controls
columns: 3
square: true
cards:
  - type: button
    entity: light.1
  - type: button
    entity: light.2
  - type: button
    entity: light.3
  - type: button
    entity: light.4
  - type: button
    entity: light.5
  - type: button
    entity: light.6
```

### Horizontal Stack
```yaml
type: horizontal-stack
cards:
  - type: button
    entity: script.scene_morning
    name: Morning
  - type: button
    entity: script.scene_evening
    name: Evening
  - type: button
    entity: script.scene_night
    name: Night
```

### Vertical Stack
```yaml
type: vertical-stack
cards:
  - type: entities
    title: Lights
    entities:
      - light.living_room
  - type: entities
    title: Climate
    entities:
      - climate.thermostat
```

## Card Actions

### Tap, Hold, and Double-Tap Actions
```yaml
type: button
entity: light.bedroom
tap_action:
  action: toggle
hold_action:
  action: more-info
double_tap_action:
  action: call-service
  service: light.turn_on
  data:
    brightness_pct: 100
```

### Available Actions
```yaml
# Toggle entity
tap_action:
  action: toggle

# Show more info dialog
tap_action:
  action: more-info

# Navigate to another view
tap_action:
  action: navigate
  navigation_path: /lovelace/lights

# Open URL
tap_action:
  action: url
  url_path: https://www.home-assistant.io

# Call service/action
tap_action:
  action: call-service
  service: light.turn_on
  target:
    entity_id: light.bedroom
  data:
    brightness_pct: 50

# Perform action (2024+ syntax)
tap_action:
  action: perform-action
  perform_action: light.turn_on
  target:
    entity_id: light.bedroom
  data:
    brightness_pct: 50

# Fire event (for automations)
tap_action:
  action: fire-dom-event
  browser_mod:
    command: popup
    title: Settings

# No action
tap_action:
  action: none

# Confirmation before action
tap_action:
  action: toggle
  confirmation:
    text: Are you sure?
```

## Card Features (Tile Cards)

### Light Features
```yaml
type: tile
entity: light.living_room
features:
  - type: light-brightness
  - type: light-color-temp
```

### Climate Features
```yaml
type: tile
entity: climate.thermostat
features:
  - type: climate-hvac-modes
    hvac_modes:
      - heat
      - cool
      - heat_cool
      - "off"
  - type: target-temperature
```

### Cover Features
```yaml
type: tile
entity: cover.garage
features:
  - type: cover-open-close
  - type: cover-position
  - type: cover-tilt-position
```

### Fan Features
```yaml
type: tile
entity: fan.bedroom
features:
  - type: fan-speed
```

## Themes

### Apply Theme to View
```yaml
views:
  - title: Home
    theme: dark-mode
    cards: []
```

### Custom Theme Definition
```yaml
# themes.yaml (included via configuration.yaml)
dark_blue:
  primary-color: "#1E88E5"
  accent-color: "#82B1FF"
  primary-background-color: "#121212"
  secondary-background-color: "#1E1E1E"
  paper-card-background-color: "#1E1E1E"
  primary-text-color: "#FFFFFF"
  secondary-text-color: "#B0B0B0"
```

## Popular Custom Cards

### Mushroom Cards
```yaml
# Entity Card
type: custom:mushroom-entity-card
entity: sensor.temperature
icon: mdi:thermometer
icon_color: blue
primary_info: name
secondary_info: state

# Light Card
type: custom:mushroom-light-card
entity: light.bedroom
show_brightness_control: true
show_color_temp_control: true
use_light_color: true
collapsible_controls: true

# Climate Card
type: custom:mushroom-climate-card
entity: climate.thermostat
show_temperature_control: true
hvac_modes:
  - heat
  - cool
  - "off"
collapsible_controls: true

# Cover Card
type: custom:mushroom-cover-card
entity: cover.garage
show_position_control: true
show_buttons_control: true

# Template Card
type: custom:mushroom-template-card
entity: light.living_room
icon: mdi:lightbulb
color: |
  {% if is_state(entity, 'on') %}
    amber
  {% else %}
    disabled
  {% endif %}
primary: "{{ state_attr(entity, 'friendly_name') }}"
secondary: "{{ states(entity) }}"
tap_action:
  action: toggle

# Chips Card
type: custom:mushroom-chips-card
alignment: center
chips:
  - type: entity
    entity: sensor.temperature
    icon: mdi:thermometer
  - type: weather
    entity: weather.home
    show_temperature: true
  - type: action
    icon: mdi:lightbulb
    tap_action:
      action: call-service
      service: light.toggle
      target:
        entity_id: light.all
```

### Button Card (Custom)
```yaml
type: custom:button-card
entity: light.bedroom
name: Bedroom
icon: mdi:bed
show_state: true
show_name: true
styles:
  card:
    - border-radius: 12px
    - padding: 12px
  icon:
    - color: var(--primary-color)
  name:
    - font-weight: bold
state:
  - value: "on"
    styles:
      card:
        - background-color: var(--primary-color)
      icon:
        - color: white
      name:
        - color: white
tap_action:
  action: toggle
```

### Mini Graph Card
```yaml
type: custom:mini-graph-card
entities:
  - entity: sensor.temperature
    name: Temperature
    color: "#e74c3c"
  - entity: sensor.humidity
    name: Humidity
    color: "#3498db"
    y_axis: secondary
hours_to_show: 24
points_per_hour: 4
line_width: 2
show:
  labels: true
  points: false
  legend: true
```

## Badge Configuration

```yaml
views:
  - title: Home
    badges:
      - entity: person.john
      - entity: sensor.temperature
        name: Temp
      - type: entity
        entity: binary_sensor.door
        color: red
```

## Complete Dashboard Example

```yaml
title: Smart Home
views:
  - title: Home
    path: home
    icon: mdi:home
    badges:
      - person.john
      - person.jane
    cards:
      - type: vertical-stack
        cards:
          - type: weather-forecast
            entity: weather.home
          - type: horizontal-stack
            cards:
              - type: button
                entity: scene.morning
                icon: mdi:weather-sunny
                name: Morning
              - type: button
                entity: scene.evening
                icon: mdi:weather-sunset
                name: Evening
              - type: button
                entity: scene.night
                icon: mdi:weather-night
                name: Night

      - type: entities
        title: Living Room
        state_color: true
        entities:
          - entity: light.living_room
            name: Main Light
          - entity: light.lamp
            name: Floor Lamp
          - type: divider
          - entity: climate.living_room
          - entity: media_player.tv

  - title: Lights
    path: lights
    icon: mdi:lightbulb-group
    cards:
      - type: entity-filter
        entities:
          - light.living_room
          - light.bedroom
          - light.kitchen
          - light.bathroom
        state_filter:
          - "on"
        card:
          type: glance
          title: Lights On

      - type: grid
        columns: 2
        square: false
        cards:
          - type: light
            entity: light.living_room
          - type: light
            entity: light.bedroom
          - type: light
            entity: light.kitchen
          - type: light
            entity: light.bathroom

  - title: Climate
    path: climate
    icon: mdi:thermostat
    cards:
      - type: thermostat
        entity: climate.main
        features:
          - type: climate-hvac-modes
            hvac_modes:
              - heat
              - cool
              - "off"

      - type: history-graph
        title: Temperature History
        hours_to_show: 24
        entities:
          - sensor.indoor_temperature
          - sensor.outdoor_temperature

  - title: Security
    path: security
    icon: mdi:shield-home
    cards:
      - type: alarm-panel
        entity: alarm_control_panel.home

      - type: entities
        title: Doors & Windows
        entities:
          - binary_sensor.front_door
          - binary_sensor.back_door
          - binary_sensor.garage_door

      - type: picture-glance
        title: Front Door
        camera_image: camera.front_door
        entities:
          - binary_sensor.front_door_motion
```

## Styling Tips

### Card Mod (Custom Styling)
```yaml
type: entities
title: Styled Card
entities:
  - light.bedroom
card_mod:
  style: |
    ha-card {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 16px;
      color: white;
    }
```

### CSS Variables
```yaml
# Available CSS variables
--primary-color
--accent-color
--primary-background-color
--secondary-background-color
--paper-card-background-color
--primary-text-color
--secondary-text-color
--disabled-text-color
--divider-color
```
