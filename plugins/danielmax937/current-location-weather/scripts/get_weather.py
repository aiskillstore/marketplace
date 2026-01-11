#!/usr/bin/env python3
"""
Get current weather for the user's location based on IP geolocation.

Usage:
    python get_weather.py [--format json|text] [--location "City, Country"]

Examples:
    python get_weather.py                      # Get weather for current IP location
    python get_weather.py --format json        # Get weather as JSON
    python get_weather.py --location "Tokyo"   # Get weather for specific location
"""

import argparse
import json
import sys
import urllib.request
import urllib.error


def get_location_from_ip() -> dict:
    """Get location based on IP address using ip-api.com (free, no key required)."""
    try:
        with urllib.request.urlopen("http://ip-api.com/json/", timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get("status") == "success":
                return {
                    "city": data.get("city", "Unknown"),
                    "region": data.get("regionName", ""),
                    "country": data.get("country", ""),
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                    "query": f"{data.get('city', '')}"
                }
    except Exception as e:
        print(f"Warning: Could not detect location from IP: {e}", file=sys.stderr)
    return {"query": "", "city": "Unknown", "region": "", "country": ""}


def get_weather(location: str = None, format_type: str = "text") -> dict | str:
    """
    Get weather data from wttr.in (free, no API key required).
    
    Args:
        location: City name or coordinates. If None, uses IP-based location.
        format_type: "json" for structured data, "text" for human-readable output.
    
    Returns:
        Weather data as dict (json) or formatted string (text).
    """
    if not location:
        loc_info = get_location_from_ip()
        location = loc_info.get("query", "")
        detected_location = f"{loc_info.get('city', '')}, {loc_info.get('country', '')}"
    else:
        detected_location = location

    # URL encode the location
    encoded_location = urllib.parse.quote(location) if location else ""
    
    if format_type == "json":
        url = f"https://wttr.in/{encoded_location}?format=j1"
    else:
        # Compact format for terminal
        url = f"https://wttr.in/{encoded_location}?format=%l:+%c+%t+%h+%w"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read().decode()
            
            if format_type == "json":
                weather_data = json.loads(data)
                # Extract and simplify the most useful information
                current = weather_data.get("current_condition", [{}])[0]
                area = weather_data.get("nearest_area", [{}])[0]
                
                result = {
                    "location": {
                        "detected": detected_location,
                        "area": area.get("areaName", [{}])[0].get("value", "Unknown"),
                        "region": area.get("region", [{}])[0].get("value", ""),
                        "country": area.get("country", [{}])[0].get("value", ""),
                    },
                    "current": {
                        "temperature_c": current.get("temp_C", "N/A"),
                        "temperature_f": current.get("temp_F", "N/A"),
                        "feels_like_c": current.get("FeelsLikeC", "N/A"),
                        "feels_like_f": current.get("FeelsLikeF", "N/A"),
                        "condition": current.get("weatherDesc", [{}])[0].get("value", "Unknown"),
                        "humidity": current.get("humidity", "N/A"),
                        "wind_kmh": current.get("windspeedKmph", "N/A"),
                        "wind_mph": current.get("windspeedMiles", "N/A"),
                        "wind_direction": current.get("winddir16Point", "N/A"),
                        "uv_index": current.get("uvIndex", "N/A"),
                        "visibility_km": current.get("visibility", "N/A"),
                        "pressure_mb": current.get("pressure", "N/A"),
                        "cloud_cover": current.get("cloudcover", "N/A"),
                    },
                    "observation_time": current.get("observation_time", "N/A"),
                }
                return result
            else:
                return f"📍 {detected_location}\n{data}"
                
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP Error: {e.code}", "message": str(e)}
    except urllib.error.URLError as e:
        return {"error": "Network Error", "message": str(e)}
    except json.JSONDecodeError:
        return {"error": "Invalid response", "message": "Could not parse weather data"}
    except Exception as e:
        return {"error": "Unknown error", "message": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="Get current weather for your location",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s                         # Weather for current location (IP-based)
    %(prog)s --format json           # Output as JSON
    %(prog)s --location "New York"   # Weather for specific city
    %(prog)s -l "Paris, France"      # Weather for Paris
        """
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--location", "-l",
        type=str,
        default=None,
        help="Location to get weather for (default: auto-detect from IP)"
    )
    
    args = parser.parse_args()
    
    # Import urllib.parse here for URL encoding
    import urllib.parse
    
    result = get_weather(location=args.location, format_type=args.format)
    
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(result)


if __name__ == "__main__":
    main()

