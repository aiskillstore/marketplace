# Home Assistant Template Sensors

Comprehensive guide to creating template sensors with Jinja2.

## Basic Template Sensors

### Simple State Calculation
```yaml
template:
  - sensor:
      - name: "Total Power Usage"
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        state: >
          {{ (states('sensor.plug_1_power') | float(0) +
              states('sensor.plug_2_power') | float(0) +
              states('sensor.plug_3_power') | float(0)) | round(1) }}
```

### Average Value
```yaml
template:
  - sensor:
      - name: "Average Indoor Temperature"
        unit_of_measurement: "C"
        device_class: temperature
        state: >
          {% set temps = [
            states('sensor.living_room_temp') | float(0),
            states('sensor.bedroom_temp') | float(0),
            states('sensor.kitchen_temp') | float(0)
          ] | reject('eq', 0) | list %}
          {{ (temps | sum / temps | count) | round(1) if temps else 'unknown' }}
```

### Min/Max Value
```yaml
template:
  - sensor:
      - name: "Highest Temperature"
        unit_of_measurement: "C"
        device_class: temperature
        state: >
          {% set temps = [
            states('sensor.room_1_temp') | float,
            states('sensor.room_2_temp') | float,
            states('sensor.room_3_temp') | float
          ] %}
          {{ temps | max }}

      - name: "Lowest Temperature"
        unit_of_measurement: "C"
        device_class: temperature
        state: >
          {% set temps = [
            states('sensor.room_1_temp') | float,
            states('sensor.room_2_temp') | float,
            states('sensor.room_3_temp') | float
          ] %}
          {{ temps | min }}
```

## Date and Time Templates

### Time Until Event
```yaml
template:
  - sensor:
      - name: "Time Until Sunset"
        state: >
          {% set sunset = as_timestamp(state_attr('sun.sun', 'next_setting')) %}
          {% set now_ts = as_timestamp(now()) %}
          {% set diff = sunset - now_ts %}
          {% if diff > 0 %}
            {{ (diff / 3600) | int }}h {{ ((diff % 3600) / 60) | int }}m
          {% else %}
            Past sunset
          {% endif %}
```

### Day of Week
```yaml
template:
  - sensor:
      - name: "Day Type"
        state: >
          {% set day = now().isoweekday() %}
          {% if day in [6, 7] %}
            Weekend
          {% else %}
            Weekday
          {% endif %}
```

### Time Period
```yaml
template:
  - sensor:
      - name: "Time of Day"
        state: >
          {% set hour = now().hour %}
          {% if 5 <= hour < 12 %}
            Morning
          {% elif 12 <= hour < 17 %}
            Afternoon
          {% elif 17 <= hour < 21 %}
            Evening
          {% else %}
            Night
          {% endif %}
```

## Attribute Templates

### Extract Attributes
```yaml
template:
  - sensor:
      - name: "Thermostat Target"
        unit_of_measurement: "C"
        state: "{{ state_attr('climate.thermostat', 'temperature') }}"

      - name: "Thermostat HVAC Action"
        state: "{{ state_attr('climate.thermostat', 'hvac_action') }}"
```

### With Custom Attributes
```yaml
template:
  - sensor:
      - name: "Solar Production"
        unit_of_measurement: "W"
        device_class: power
        state: "{{ states('sensor.solar_power') }}"
        attributes:
          daily_total: "{{ states('sensor.solar_daily_energy') }}"
          efficiency: >
            {% set power = states('sensor.solar_power') | float(0) %}
            {% set max_power = 5000 %}
            {{ ((power / max_power) * 100) | round(1) }}%
          status: >
            {% set power = states('sensor.solar_power') | float(0) %}
            {% if power > 3000 %}
              Excellent
            {% elif power > 1000 %}
              Good
            {% elif power > 0 %}
              Low
            {% else %}
              Not Producing
            {% endif %}
```

## Binary Sensor Templates

### Simple Threshold
```yaml
template:
  - binary_sensor:
      - name: "High Temperature Alert"
        device_class: heat
        state: "{{ states('sensor.temperature') | float > 30 }}"
```

### Complex Condition
```yaml
template:
  - binary_sensor:
      - name: "Home Occupied"
        device_class: occupancy
        state: >
          {{ is_state('person.john', 'home') or
             is_state('person.jane', 'home') or
             is_state('binary_sensor.motion', 'on') }}
        delay_off:
          minutes: 10
```

### Workday Sensor
```yaml
template:
  - binary_sensor:
      - name: "Workday"
        state: >
          {% set day = now().isoweekday() %}
          {{ day <= 5 }}
```

## Availability Templates

### Basic Availability
```yaml
template:
  - sensor:
      - name: "Calculated Value"
        state: "{{ states('sensor.source') | float * 2 }}"
        availability: >
          {{ states('sensor.source') not in ['unknown', 'unavailable', 'none'] }}
```

### Multiple Dependencies
```yaml
template:
  - sensor:
      - name: "Combined Sensor"
        state: >
          {{ states('sensor.a') | float + states('sensor.b') | float }}
        availability: >
          {{ states('sensor.a') not in ['unknown', 'unavailable'] and
             states('sensor.b') not in ['unknown', 'unavailable'] }}
```

## Icon Templates

### Dynamic Icons
```yaml
template:
  - sensor:
      - name: "Battery Level"
        unit_of_measurement: "%"
        state: "{{ states('sensor.phone_battery') }}"
        icon: >
          {% set level = states('sensor.phone_battery') | int(0) %}
          {% if level >= 90 %}
            mdi:battery
          {% elif level >= 70 %}
            mdi:battery-80
          {% elif level >= 50 %}
            mdi:battery-60
          {% elif level >= 30 %}
            mdi:battery-40
          {% elif level >= 10 %}
            mdi:battery-20
          {% else %}
            mdi:battery-alert
          {% endif %}
```

## Loop Templates

### Count Entities in State
```yaml
template:
  - sensor:
      - name: "Lights On Count"
        state: >
          {{ states.light | selectattr('state', 'eq', 'on') | list | count }}

      - name: "Open Doors"
        state: >
          {{ states.binary_sensor
             | selectattr('attributes.device_class', 'eq', 'door')
             | selectattr('state', 'eq', 'on')
             | list | count }}
```

### List Active Entities
```yaml
template:
  - sensor:
      - name: "Active Lights"
        state: >
          {% set lights = states.light | selectattr('state', 'eq', 'on') | list %}
          {{ lights | count }} lights on
        attributes:
          list: >
            {{ states.light
               | selectattr('state', 'eq', 'on')
               | map(attribute='name')
               | list }}
```

## Trigger-Based Templates

### Last Changed
```yaml
template:
  - trigger:
      - trigger: state
        entity_id: binary_sensor.front_door
        to: "on"
    sensor:
      - name: "Last Door Open"
        state: "{{ now().strftime('%H:%M:%S') }}"
        attributes:
          timestamp: "{{ now().isoformat() }}"
```

### Event Counter
```yaml
template:
  - trigger:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "on"
    sensor:
      - name: "Motion Events Today"
        state: "{{ (this.state | int(0)) + 1 }}"
```

## Utility Helpers

### Format Numbers
```yaml
template:
  - sensor:
      - name: "Energy Cost"
        unit_of_measurement: "EUR"
        state: >
          {% set kwh = states('sensor.energy_today') | float(0) %}
          {% set rate = 0.25 %}
          {{ (kwh * rate) | round(2) }}
```

### Unit Conversion
```yaml
template:
  - sensor:
      - name: "Temperature Fahrenheit"
        unit_of_measurement: "F"
        state: >
          {% set celsius = states('sensor.temperature') | float(0) %}
          {{ ((celsius * 9/5) + 32) | round(1) }}
```

## Response Variable Templates

### Weather Forecast Sensor
```yaml
template:
  - triggers:
      - trigger: time_pattern
        hours: /1
    actions:
      - action: weather.get_forecasts
        data:
          type: hourly
        target:
          entity_id: weather.home
        response_variable: hourly
    sensor:
      - name: "Weather Forecast Hourly"
        unique_id: weather_forecast_hourly
        state: "{{ now().isoformat() }}"
        attributes:
          forecast: "{{ hourly['weather.home'].forecast }}"
          next_temp: "{{ hourly['weather.home'].forecast[0].temperature }}"
          next_condition: "{{ hourly['weather.home'].forecast[0].condition }}"
```

### Calendar Events Sensor
```yaml
template:
  - triggers:
      - trigger: time_pattern
        minutes: /30
    actions:
      - action: calendar.get_events
        target:
          entity_id: calendar.work
        data:
          duration:
            hours: 24
        response_variable: events
    sensor:
      - name: "Today's Events Count"
        unique_id: todays_events_count
        state: "{{ events['calendar.work'].events | count }}"
        attributes:
          events: "{{ events['calendar.work'].events }}"
          next_event: >
            {% set e = events['calendar.work'].events | first %}
            {{ e.summary if e else 'None' }}
```

### Merge Multiple Responses
```yaml
template:
  - triggers:
      - trigger: time_pattern
        hours: /6
    actions:
      - action: weather.get_forecasts
        data:
          type: daily
        target:
          entity_id:
            - weather.home
            - weather.work
        response_variable: forecasts
    sensor:
      - name: "Combined Weather"
        unique_id: combined_weather
        state: "{{ now().isoformat() }}"
        attributes:
          home_forecast: "{{ forecasts['weather.home'].forecast }}"
          work_forecast: "{{ forecasts['weather.work'].forecast }}"
```

## Advanced Filter Usage

### Apply Filter (call macros as filters)
```yaml
template:
  - sensor:
      - name: "Doubled Values"
        state: >
          {% macro double(x) %}{{ x * 2 }}{% endmacro %}
          {{ [1, 2, 3, 4] | map('apply', double) | list | join(', ') }}
```

### Complex List Processing
```yaml
template:
  - sensor:
      - name: "High Power Devices"
        state: >
          {% set devices = states.sensor
             | selectattr('attributes.device_class', 'eq', 'power')
             | selectattr('state', 'is_number')
             | rejectattr('state', 'in', ['unknown', 'unavailable'])
             | list %}
          {% set high_power = devices | selectattr('state', 'gt', '100') | list %}
          {{ high_power | count }}
        attributes:
          devices: >
            {{ states.sensor
               | selectattr('attributes.device_class', 'eq', 'power')
               | selectattr('state', 'is_number')
               | rejectattr('state', 'in', ['unknown', 'unavailable'])
               | selectattr('state', 'gt', '100')
               | map(attribute='entity_id')
               | list }}
```

### Groupby Filter
```yaml
template:
  - sensor:
      - name: "Lights by Area"
        state: "{{ states.light | count }}"
        attributes:
          by_area: >
            {% set lights = states.light | list %}
            {% set grouped = {} %}
            {% for light in lights %}
              {% set area = area_name(light.entity_id) or 'Unknown' %}
              {% set _ = grouped.__setitem__(area, grouped.get(area, []) + [light.name]) %}
            {% endfor %}
            {{ grouped }}
```

## JSON Processing Templates

### Parse Nested JSON
```yaml
template:
  - sensor:
      - name: "API Response Value"
        state: >
          {% set data = {"name": "Outside", "device": "weather", "data": {"temp": "24", "hum": "35%"}} %}
          {{ data.data.hum[:-1] | int }}
        unit_of_measurement: "%"
```

### Extract from JSON Array
```yaml
template:
  - sensor:
      - name: "First Prime"
        state: >
          {% set data = {"primes": [2, 3, 5, 7, 11, 13]} %}
          {{ data.primes[0] }}
```

## State Change History Templates

### Time Since Last Change
```yaml
template:
  - sensor:
      - name: "Door Last Opened"
        state: >
          {% set last = states.binary_sensor.front_door.last_changed %}
          {% set diff = now() - last %}
          {% set hours = (diff.total_seconds() / 3600) | int %}
          {% set minutes = ((diff.total_seconds() % 3600) / 60) | int %}
          {% if hours > 0 %}
            {{ hours }}h {{ minutes }}m ago
          {% else %}
            {{ minutes }}m ago
          {% endif %}
```

### Track State Duration Today
```yaml
template:
  - trigger:
      - trigger: state
        entity_id: binary_sensor.motion
    sensor:
      - name: "Motion Active Today"
        state: >
          {% set current = this.state | float(0) %}
          {% if trigger.to_state.state == 'on' %}
            {{ current }}
          {% else %}
            {% set duration = (as_timestamp(trigger.to_state.last_changed) -
                               as_timestamp(trigger.from_state.last_changed)) / 60 %}
            {{ (current + duration) | round(1) }}
          {% endif %}
        unit_of_measurement: "min"
```

## Area and Device Templates

### Devices in Area
```yaml
template:
  - sensor:
      - name: "Living Room Devices"
        state: >
          {{ area_entities('living_room') | count }}
        attributes:
          entities: "{{ area_entities('living_room') | list }}"
          lights: >
            {{ area_entities('living_room')
               | select('match', 'light.')
               | list }}
```

### Device Battery Levels
```yaml
template:
  - sensor:
      - name: "Low Battery Devices"
        state: >
          {% set low = states.sensor
             | selectattr('attributes.device_class', 'eq', 'battery')
             | selectattr('state', 'is_number')
             | selectattr('state', 'lt', '20')
             | list %}
          {{ low | count }}
        attributes:
          devices: >
            {% set low = states.sensor
               | selectattr('attributes.device_class', 'eq', 'battery')
               | selectattr('state', 'is_number')
               | selectattr('state', 'lt', '20')
               | list %}
            {% for sensor in low %}
            - {{ sensor.name }}: {{ sensor.state }}%
            {% endfor %}
```

## Time and Date Advanced Templates

### Next Occurrence
```yaml
template:
  - sensor:
      - name: "Next Trash Day"
        state: >
          {% set today = now().date() %}
          {% set weekday = 2 %}  {# Wednesday = 2 #}
          {% set days_ahead = weekday - today.weekday() %}
          {% if days_ahead <= 0 %}
            {% set days_ahead = days_ahead + 7 %}
          {% endif %}
          {% set next_date = today + timedelta(days=days_ahead) %}
          {{ next_date.strftime('%A, %B %d') }}
        attributes:
          days_until: >
            {% set today = now().date() %}
            {% set weekday = 2 %}
            {% set days_ahead = weekday - today.weekday() %}
            {% if days_ahead <= 0 %}
              {% set days_ahead = days_ahead + 7 %}
            {% endif %}
            {{ days_ahead }}
```

### Relative Time Display
```yaml
template:
  - sensor:
      - name: "Uptime"
        state: >
          {% set uptime = as_timestamp(now()) - as_timestamp(states('sensor.ha_uptime')) %}
          {% set days = (uptime / 86400) | int %}
          {% set hours = ((uptime % 86400) / 3600) | int %}
          {% set minutes = ((uptime % 3600) / 60) | int %}
          {{ days }}d {{ hours }}h {{ minutes }}m
```
