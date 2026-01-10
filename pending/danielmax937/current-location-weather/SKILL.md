---
name: current-location-weather
description: Get current weather conditions for a location. Use this skill when users ask about weather, temperature, current conditions, forecasts, or any weather-related queries like "What's the weather?", "Is it raining?", "How hot is it outside?", "What's the temperature?", or "Should I bring an umbrella?". Supports automatic location detection via IP or specific location queries.
---

# Current Location Weather

Get current weather conditions using IP-based geolocation or a specified location.

## Quick Start

Run the weather script to get current conditions:

```bash
python scripts/get_weather.py
```

## Usage Options

### Auto-detect location (default)
```bash
python scripts/get_weather.py
```

### Specify a location
```bash
python scripts/get_weather.py --location "Tokyo, Japan"
python scripts/get_weather.py -l "New York"
```

### Get JSON output (for programmatic use)
```bash
python scripts/get_weather.py --format json
python scripts/get_weather.py -f json -l "London"
```

## Output Examples

### Text format (default)
```
📍 San Francisco, United States
San Francisco: ⛅ +15°C 72% ↙10km/h
```

### JSON format
```json
{
  "location": {
    "detected": "San Francisco, United States",
    "area": "San Francisco",
    "country": "United States of America"
  },
  "current": {
    "temperature_c": "15",
    "temperature_f": "59",
    "feels_like_c": "14",
    "condition": "Partly cloudy",
    "humidity": "72",
    "wind_kmh": "10",
    "wind_direction": "SW",
    "uv_index": "3"
  }
}
```

## How It Works

1. **Location detection**: Uses ip-api.com (free) to detect location from IP address
2. **Weather data**: Fetches from wttr.in (free, no API key required)
3. **No dependencies**: Uses only Python standard library (urllib, json)

## Notes

- Network access required for both geolocation and weather data
- IP-based location may not be precise (city-level accuracy)
- For specific locations, use `--location` flag for better accuracy
