# Common Home Assistant Automation Patterns

Proven patterns for common automation scenarios.

## Lighting Patterns

### Motion-Activated Lights with Timer
```yaml
automation:
  - alias: "Motion Lights - Living Room"
    triggers:
      - trigger: state
        entity_id: binary_sensor.living_room_motion
        to: "on"
    conditions:
      - condition: numeric_state
        entity_id: sensor.living_room_illuminance
        below: 50
    actions:
      - action: light.turn_on
        target:
          entity_id: light.living_room
        data:
          brightness_pct: 80
      - wait_for_trigger:
          - trigger: state
            entity_id: binary_sensor.living_room_motion
            to: "off"
            for:
              minutes: 5
      - action: light.turn_off
        target:
          entity_id: light.living_room
```

### Adaptive Brightness Based on Time
```yaml
automation:
  - alias: "Adaptive Brightness"
    triggers:
      - trigger: state
        entity_id: light.bedroom
        to: "on"
    actions:
      - action: light.turn_on
        target:
          entity_id: light.bedroom
        data:
          brightness_pct: >
            {% set hour = now().hour %}
            {% if hour < 7 %}
              20
            {% elif hour < 20 %}
              100
            {% else %}
              50
            {% endif %}
```

### Circadian Lighting
```yaml
automation:
  - alias: "Circadian Color Temperature"
    triggers:
      - trigger: time_pattern
        minutes: "/15"
    conditions:
      - condition: state
        entity_id: light.office
        state: "on"
    actions:
      - action: light.turn_on
        target:
          entity_id: light.office
        data:
          color_temp_kelvin: >
            {% set elevation = state_attr('sun.sun', 'elevation') %}
            {% if elevation < 0 %}
              2700
            {% elif elevation < 20 %}
              {{ 2700 + (elevation * 75) | int }}
            {% else %}
              4500
            {% endif %}
```

### All Lights Off When Leaving
```yaml
automation:
  - alias: "Goodbye - All Lights Off"
    triggers:
      - trigger: state
        entity_id: group.family
        from: "home"
        to: "not_home"
    actions:
      - action: light.turn_off
        target:
          entity_id: all
```

## Climate Control Patterns

### Smart Thermostat Based on Occupancy
```yaml
automation:
  - alias: "Climate - Occupancy Based"
    triggers:
      - trigger: state
        entity_id: binary_sensor.home_occupied
    actions:
      - choose:
          - conditions:
              - condition: state
                entity_id: binary_sensor.home_occupied
                state: "on"
            sequence:
              - action: climate.set_temperature
                target:
                  entity_id: climate.thermostat
                data:
                  temperature: 22
          - conditions:
              - condition: state
                entity_id: binary_sensor.home_occupied
                state: "off"
            sequence:
              - action: climate.set_temperature
                target:
                  entity_id: climate.thermostat
                data:
                  temperature: 18
```

### Window Open - Pause Heating
```yaml
automation:
  - alias: "Climate - Window Open"
    triggers:
      - trigger: state
        entity_id: binary_sensor.window_contact
        to: "on"
        for:
          minutes: 2
    conditions:
      - condition: state
        entity_id: climate.thermostat
        state: "heat"
    actions:
      - action: climate.turn_off
        target:
          entity_id: climate.thermostat
      - action: notify.mobile_app
        data:
          message: "Heating paused - window open"
```

## Security Patterns

### Door Left Open Alert
```yaml
automation:
  - alias: "Security - Door Open Alert"
    triggers:
      - trigger: state
        entity_id: binary_sensor.front_door
        to: "on"
        for:
          minutes: 5
    actions:
      - action: notify.mobile_app
        data:
          title: "Security Alert"
          message: "Front door has been open for 5 minutes"
      - repeat:
          while:
            - condition: state
              entity_id: binary_sensor.front_door
              state: "on"
          sequence:
            - delay:
                minutes: 5
            - action: notify.mobile_app
              data:
                message: "Front door still open"
```

### Motion While Away - Alarm
```yaml
automation:
  - alias: "Security - Motion While Away"
    triggers:
      - trigger: state
        entity_id: binary_sensor.motion_sensor
        to: "on"
    conditions:
      - condition: state
        entity_id: alarm_control_panel.home
        state: "armed_away"
    actions:
      - action: alarm_control_panel.alarm_trigger
        target:
          entity_id: alarm_control_panel.home
      - action: notify.mobile_app
        data:
          title: "SECURITY ALERT"
          message: "Motion detected while away!"
          data:
            priority: high
      - action: camera.snapshot
        target:
          entity_id: camera.front_door
        data:
          filename: "/config/snapshots/alert_{{ now().strftime('%Y%m%d_%H%M%S') }}.jpg"
```

## Presence Detection Patterns

### Welcome Home
```yaml
automation:
  - alias: "Welcome Home"
    triggers:
      - trigger: state
        entity_id: person.me
        to: "home"
    conditions:
      - condition: sun
        after: sunset
    actions:
      - action: light.turn_on
        target:
          entity_id: light.entryway
      - action: climate.set_preset_mode
        target:
          entity_id: climate.thermostat
        data:
          preset_mode: "home"
      - action: lock.unlock
        target:
          entity_id: lock.front_door
```

### Last Person Left
```yaml
automation:
  - alias: "Goodbye - Last Person Left"
    triggers:
      - trigger: state
        entity_id: zone.home
        attribute: persons
    conditions:
      - condition: numeric_state
        entity_id: zone.home
        attribute: persons
        below: 1
    actions:
      - action: script.turn_on
        target:
          entity_id: script.goodbye_routine
```

## Notification Patterns

### Actionable Notification
```yaml
automation:
  - alias: "Notification - Garage Door Left Open"
    triggers:
      - trigger: state
        entity_id: cover.garage_door
        to: "open"
        for:
          minutes: 15
    actions:
      - action: notify.mobile_app
        data:
          title: "Garage Door Open"
          message: "Close the garage door?"
          data:
            actions:
              - action: "CLOSE_GARAGE"
                title: "Close Door"
              - action: "IGNORE"
                title: "Ignore"

  - alias: "Notification - Handle Garage Response"
    triggers:
      - trigger: event
        event_type: mobile_app_notification_action
        event_data:
          action: "CLOSE_GARAGE"
    actions:
      - action: cover.close_cover
        target:
          entity_id: cover.garage_door
```

### Morning Summary
```yaml
automation:
  - alias: "Morning Summary"
    triggers:
      - trigger: time
        at: "07:00:00"
    conditions:
      - condition: state
        entity_id: person.me
        state: "home"
    actions:
      - action: notify.mobile_app
        data:
          title: "Good Morning"
          message: >
            Weather: {{ states('weather.home') }}
            Temperature: {{ states('sensor.outside_temperature') }}C
            Calendar: {{ state_attr('calendar.personal', 'message') | default('No events') }}
```

## Energy Management Patterns

### High Power Usage Alert
```yaml
automation:
  - alias: "Energy - High Usage Alert"
    triggers:
      - trigger: numeric_state
        entity_id: sensor.total_power
        above: 5000
        for:
          minutes: 10
    actions:
      - action: notify.mobile_app
        data:
          title: "High Energy Usage"
          message: >
            Current usage: {{ states('sensor.total_power') }}W
            Top consumers:
            {% for entity in states.sensor
               | selectattr('attributes.device_class', 'eq', 'power')
               | sort(attribute='state', reverse=true)
               | list
               | slice(3)
               | first %}
            - {{ entity.name }}: {{ entity.state }}W
            {% endfor %}
```

## Media Patterns

### Pause Media on Doorbell
```yaml
automation:
  - alias: "Media - Pause on Doorbell"
    triggers:
      - trigger: state
        entity_id: binary_sensor.doorbell
        to: "on"
    actions:
      - action: media_player.media_pause
        target:
          entity_id: media_player.living_room_tv
      - action: tts.speak
        target:
          entity_id: tts.google_en
        data:
          media_player_entity_id: media_player.speaker
          message: "Someone is at the door"
```

## Time-Based Patterns

### Weekday Only Alarm
```yaml
automation:
  - alias: "Weekday Alarm"
    triggers:
      - trigger: time
        at: "06:30:00"
    conditions:
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
    actions:
      - action: light.turn_on
        target:
          entity_id: light.bedroom
        data:
          brightness_pct: 30
          transition: 300
```

### Seasonal Adjustment
```yaml
automation:
  - alias: "Seasonal Brightness"
    triggers:
      - trigger: state
        entity_id: light.outdoor
        to: "on"
    actions:
      - action: light.turn_on
        target:
          entity_id: light.outdoor
        data:
          brightness_pct: >
            {% set month = now().month %}
            {% if month in [11, 12, 1, 2] %}
              100
            {% elif month in [3, 4, 9, 10] %}
              75
            {% else %}
              50
            {% endif %}
```

## Calendar-Based Patterns

### Prepare for Meeting
```yaml
automation:
  - alias: "Calendar - Meeting Prep"
    triggers:
      - trigger: calendar
        entity_id: calendar.work
        event: start
        offset: "-00:05:00"
    actions:
      - action: light.turn_on
        target:
          entity_id: light.office
        data:
          brightness_pct: 100
          color_temp_kelvin: 4000
      - action: notify.mobile_app
        data:
          title: "Meeting Starting Soon"
          message: "{{ trigger.calendar_event.summary }} in 5 minutes"
```

### Daily Schedule from Calendar
```yaml
automation:
  - alias: "Calendar - Morning Briefing"
    triggers:
      - trigger: time
        at: "07:30:00"
    actions:
      - action: calendar.get_events
        target:
          entity_id: calendar.work
        data:
          duration:
            hours: 12
        response_variable: agenda
      - action: notify.mobile_app
        data:
          title: "Today's Schedule"
          message: >
            {% set events = agenda['calendar.work'].events %}
            {% if events | count > 0 %}
              You have {{ events | count }} events:
              {% for event in events %}
              - {{ event.summary }} at {{ event.start | as_timestamp | timestamp_custom('%H:%M') }}
              {% endfor %}
            {% else %}
              No events scheduled today
            {% endif %}
```

## Actionable Notification Patterns

### Confirm Before Action
```yaml
automation:
  - alias: "Notify - Confirm Garage Close"
    triggers:
      - trigger: state
        entity_id: cover.garage
        to: "open"
        for:
          minutes: 30
    actions:
      - variables:
          action_close: "{{ 'CLOSE_GARAGE_' ~ context.id }}"
          action_ignore: "{{ 'IGNORE_' ~ context.id }}"
      - action: notify.mobile_app
        data:
          title: "Garage Door Open"
          message: "The garage has been open for 30 minutes"
          data:
            actions:
              - action: "{{ action_close }}"
                title: "Close Door"
              - action: "{{ action_ignore }}"
                title: "Leave Open"
      - wait_for_trigger:
          - trigger: event
            event_type: mobile_app_notification_action
            event_data:
              action: "{{ action_close }}"
          - trigger: event
            event_type: mobile_app_notification_action
            event_data:
              action: "{{ action_ignore }}"
        timeout:
          minutes: 10
      - if:
          - condition: template
            value_template: "{{ wait.trigger and wait.trigger.event.data.action == action_close }}"
        then:
          - action: cover.close_cover
            target:
              entity_id: cover.garage
```

### Multi-Choice Actions
```yaml
automation:
  - alias: "Notify - Climate Override"
    triggers:
      - trigger: numeric_state
        entity_id: sensor.indoor_temperature
        above: 28
    actions:
      - variables:
          action_cool: "{{ 'AC_ON_' ~ context.id }}"
          action_fans: "{{ 'FANS_' ~ context.id }}"
          action_ignore: "{{ 'IGNORE_' ~ context.id }}"
      - action: notify.mobile_app
        data:
          title: "Home is Hot!"
          message: "Indoor temperature is {{ states('sensor.indoor_temperature') }}°C"
          data:
            actions:
              - action: "{{ action_cool }}"
                title: "Turn on AC"
              - action: "{{ action_fans }}"
                title: "Turn on Fans"
              - action: "{{ action_ignore }}"
                title: "Ignore"
      - wait_for_trigger:
          - trigger: event
            event_type: mobile_app_notification_action
            event_data:
              action: "{{ action_cool }}"
          - trigger: event
            event_type: mobile_app_notification_action
            event_data:
              action: "{{ action_fans }}"
        timeout:
          minutes: 5
      - choose:
          - conditions: "{{ wait.trigger.event.data.action == action_cool }}"
            sequence:
              - action: climate.set_hvac_mode
                target:
                  entity_id: climate.main
                data:
                  hvac_mode: cool
          - conditions: "{{ wait.trigger.event.data.action == action_fans }}"
            sequence:
              - action: fan.turn_on
                target:
                  entity_id:
                    - fan.living_room
                    - fan.bedroom
```

## Parallel Execution Patterns

### Simultaneous Room Setup
```yaml
automation:
  - alias: "Scene - Movie Night"
    triggers:
      - trigger: event
        event_type: call_service
        event_data:
          domain: scene
          service: turn_on
          service_data:
            entity_id: scene.movie_night
    actions:
      - parallel:
          - sequence:
              - action: light.turn_on
                target:
                  entity_id: light.bias_lighting
                data:
                  brightness_pct: 30
                  rgb_color: [255, 147, 41]
              - action: light.turn_off
                target:
                  entity_id: light.ceiling
          - action: cover.close_cover
            target:
              entity_id: cover.blinds
          - action: media_player.turn_on
            target:
              entity_id: media_player.projector
          - action: climate.set_temperature
            target:
              entity_id: climate.living_room
            data:
              temperature: 22
```

### Alert Multiple People Simultaneously
```yaml
automation:
  - alias: "Alert - Emergency Parallel"
    triggers:
      - trigger: state
        entity_id: binary_sensor.smoke_detector
        to: "on"
    actions:
      - parallel:
          - action: notify.mobile_app_person1
            data:
              title: "FIRE ALERT"
              message: "Smoke detected at home!"
              data:
                priority: high
          - action: notify.mobile_app_person2
            data:
              title: "FIRE ALERT"
              message: "Smoke detected at home!"
              data:
                priority: high
          - action: siren.turn_on
            target:
              entity_id: siren.alarm
          - sequence:
              - action: light.turn_on
                target:
                  entity_id: all
                data:
                  flash: long
              - delay:
                  seconds: 2
              - action: light.turn_on
                target:
                  entity_id: all
                data:
                  flash: long

```

## Multi-Trigger Patterns with IDs

### Smart Button Controller
```yaml
automation:
  - alias: "Button - Multi-Action"
    mode: queued
    triggers:
      - trigger: event
        event_type: zha_event
        event_data:
          device_id: abc123
          command: "on"
        id: "single_press"
      - trigger: event
        event_type: zha_event
        event_data:
          device_id: abc123
          command: "off"
        id: "double_press"
      - trigger: event
        event_type: zha_event
        event_data:
          device_id: abc123
          command: "move_with_on_off"
        id: "long_press"
    actions:
      - choose:
          - conditions:
              - condition: trigger
                id: "single_press"
            sequence:
              - action: light.toggle
                target:
                  entity_id: light.bedroom
          - conditions:
              - condition: trigger
                id: "double_press"
            sequence:
              - action: light.toggle
                target:
                  entity_id: light.bathroom
          - conditions:
              - condition: trigger
                id: "long_press"
            sequence:
              - action: scene.turn_on
                target:
                  entity_id: scene.goodnight
```

### Day/Night Motion Response
```yaml
automation:
  - alias: "Motion - Adaptive Response"
    triggers:
      - trigger: state
        entity_id: binary_sensor.hallway_motion
        to: "on"
        id: "day"
      - trigger: state
        entity_id: binary_sensor.hallway_motion
        to: "on"
        id: "night"
    conditions:
      - condition: or
        conditions:
          - condition: and
            conditions:
              - condition: trigger
                id: "day"
              - condition: sun
                after: sunrise
                before: sunset
          - condition: and
            conditions:
              - condition: trigger
                id: "night"
              - condition: sun
                after: sunset
                before: sunrise
    actions:
      - choose:
          - conditions:
              - condition: trigger
                id: "day"
            sequence:
              - action: light.turn_on
                target:
                  entity_id: light.hallway
                data:
                  brightness_pct: 100
          - conditions:
              - condition: trigger
                id: "night"
            sequence:
              - action: light.turn_on
                target:
                  entity_id: light.hallway
                data:
                  brightness_pct: 10
                  color_temp_kelvin: 2200
```

## Device Automation Patterns

### MQTT Button Press
```yaml
automation:
  - alias: "MQTT - Doorbell Press"
    triggers:
      - trigger: mqtt
        topic: "zigbee2mqtt/doorbell/action"
        payload: "single"
    actions:
      - parallel:
          - action: media_player.play_media
            target:
              entity_id: media_player.speaker
            data:
              media_content_id: "media-source://media_source/local/doorbell.mp3"
              media_content_type: "audio/mpeg"
          - action: notify.mobile_app
            data:
              title: "Doorbell"
              message: "Someone is at the door"
              data:
                image: "/api/camera_proxy/camera.front_door"
```

### Zigbee Remote Control
```yaml
automation:
  - alias: "Remote - IKEA Dimmer"
    triggers:
      - trigger: device
        device_id: ikea_remote_123
        domain: zha
        type: remote_button_short_press
        subtype: dim_up
        id: "up"
      - trigger: device
        device_id: ikea_remote_123
        domain: zha
        type: remote_button_short_press
        subtype: dim_down
        id: "down"
    actions:
      - choose:
          - conditions:
              - condition: trigger
                id: "up"
            sequence:
              - action: light.turn_on
                target:
                  entity_id: light.bedroom
                data:
                  brightness_step_pct: 20
          - conditions:
              - condition: trigger
                id: "down"
            sequence:
              - action: light.turn_on
                target:
                  entity_id: light.bedroom
                data:
                  brightness_step_pct: -20
```
