#!/usr/bin/env python3

"""
Test script for weather_info.py
Demonstrates the expected JSON structure and tests the script
"""

import json
import sys
from pathlib import Path

def create_sample_weather_data():
    """Create sample weather data to demonstrate the JSON structure"""
    sample_data = {
        "location": "Stockport",
        "latitude": 53.4084,
        "longitude": -2.1496,
        "last_updated": "2025-07-14 21:15:00",
        "current": {
            "time": "2025-07-14 21:00",
            "temp": 18.5,
            "feels_like": 17.2,
            "status": "partly_cloudy"
        },
        "forecast": [
            {
                "time": "2025-07-14 22:00",
                "temp": 17.8,
                "feels_like": 16.5,
                "status": "overcast"
            },
            {
                "time": "2025-07-14 23:00",
                "temp": 16.2,
                "feels_like": 15.1,
                "status": "slight_rain"
            },
            {
                "time": "2025-07-15 00:00",
                "temp": 15.7,
                "feels_like": 14.8,
                "status": "slight_rain"
            },
            {
                "time": "2025-07-15 01:00",
                "temp": 15.3,
                "feels_like": 14.4,
                "status": "light_drizzle"
            },
            {
                "time": "2025-07-15 02:00",
                "temp": 14.9,
                "feels_like": 14.0,
                "status": "overcast"
            },
            {
                "time": "2025-07-15 03:00",
                "temp": 14.5,
                "feels_like": 13.6,
                "status": "overcast"
            },
            {
                "time": "2025-07-15 04:00",
                "temp": 14.1,
                "feels_like": 13.2,
                "status": "partly_cloudy"
            },
            {
                "time": "2025-07-15 05:00",
                "temp": 13.8,
                "feels_like": 12.9,
                "status": "clear_sky"
            }
        ]
    }
    return sample_data

def main():
    """Main function"""
    print("=== Weather Info Test Script (Open-Meteo) ===")
    print()
    
    # Create sample data
    sample_data = create_sample_weather_data()
    
    # Display the JSON structure
    print("Expected JSON Structure:")
    print(json.dumps(sample_data, indent=2))
    print()
    
    # Check if weather_info.py exists
    weather_script = Path(__file__).parent / "weather_info.py"
    if weather_script.exists():
        print("✓ weather_info.py script found")
        print()
        print("To use the script:")
        print("1. No API key required - Open-Meteo is free!")
        print("2. Run: python3 scripts/weather_info.py")
        print()
        print("The script will save weather data to: data/weather_data.json")
    else:
        print("✗ weather_info.py script not found")
    
    print()
    print("Weather Status Codes (WMO):")
    print("- clear_sky: Clear sky")
    print("- mainly_clear: Mainly clear")
    print("- partly_cloudy: Partly cloudy")
    print("- overcast: Overcast sky")
    print("- foggy: Foggy conditions")
    print("- light_drizzle: Light drizzle")
    print("- moderate_drizzle: Moderate drizzle")
    print("- dense_drizzle: Heavy drizzle")
    print("- slight_rain: Light rain")
    print("- moderate_rain: Moderate rain")
    print("- heavy_rain: Heavy rain")
    print("- slight_snow: Light snow")
    print("- moderate_snow: Moderate snow")
    print("- heavy_snow: Heavy snow")
    print("- slight_rain_showers: Light rain showers")
    print("- moderate_rain_showers: Moderate rain showers")
    print("- thunderstorm: Thunderstorms")
    print("- thunderstorm_with_slight_hail: Thunderstorm with hail")
    print()
    print("Benefits of Open-Meteo:")
    print("- Free to use, no API key required")
    print("- High accuracy weather data")
    print("- Global coverage")
    print("- Reliable and fast API")
    print("- Based on multiple weather models")

if __name__ == "__main__":
    main() 