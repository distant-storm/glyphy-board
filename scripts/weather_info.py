"""
Weather Info Script
Fetches weather data from Open-Meteo API for Stockport
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / 'data'
WEATHER_DATA_FILE = DATA_DIR / 'weather_data.json'

# Stockport coordinates (approximate)
STOCKPORT_LAT = 53.4084
STOCKPORT_LON = -2.1496

# Open-Meteo API endpoints
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1"
FORECAST_URL = f"{OPEN_METEO_BASE_URL}/forecast"

def get_weather_data() -> Optional[Dict]:
    """Fetch weather data from Open-Meteo API"""
    try:
        params = {
            'latitude': STOCKPORT_LAT,
            'longitude': STOCKPORT_LON,
            'hourly': 'temperature_2m,apparent_temperature,weather_code',
            'timezone': 'Europe/London',
            'forecast_days': 1  # We only need current + 8 hours
        }
        
        logger.info(f"Fetching weather data for Stockport (lat: {STOCKPORT_LAT}, lon: {STOCKPORT_LON})")
        
        # Try with SSL verification first
        try:
            response = requests.get(FORECAST_URL, params=params, timeout=30, verify=True)
            if response.status_code == 200:
                logger.info("Successfully fetched weather data from Open-Meteo API (with SSL verification)")
                return response.json()
        except requests.exceptions.SSLError as ssl_error:
            logger.warning(f"SSL verification failed: {ssl_error}")
            logger.info("Retrying without SSL verification...")
            
            # Fallback: try without SSL verification
            try:
                response = requests.get(FORECAST_URL, params=params, timeout=30, verify=False)
                if response.status_code == 200:
                    logger.info("Successfully fetched weather data from Open-Meteo API (without SSL verification)")
                    return response.json()
                else:
                    logger.error(f"API request failed with status code {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return None
            except requests.exceptions.RequestException as e2:
                logger.error(f"Request error (without SSL verification): {e2}")
                return None
        
        # If we get here, the first attempt failed for non-SSL reasons
        if response.status_code != 200:
            logger.error(f"API request failed with status code {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching weather data: {e}")
        return None

def parse_weather_code(code: int) -> str:
    """Convert WMO weather code to human-readable status"""
    # WMO (World Meteorological Organization) weather codes
    weather_codes = {
        0: "clear_sky",
        1: "mainly_clear",
        2: "partly_cloudy",
        3: "overcast",
        45: "foggy",
        48: "depositing_rime_fog",
        51: "light_drizzle",
        53: "moderate_drizzle",
        55: "dense_drizzle",
        56: "light_freezing_drizzle",
        57: "dense_freezing_drizzle",
        61: "slight_rain",
        63: "moderate_rain",
        65: "heavy_rain",
        66: "light_freezing_rain",
        67: "heavy_freezing_rain",
        71: "slight_snow",
        73: "moderate_snow",
        75: "heavy_snow",
        77: "snow_grains",
        80: "slight_rain_showers",
        81: "moderate_rain_showers",
        82: "violent_rain_showers",
        85: "slight_snow_showers",
        86: "heavy_snow_showers",
        95: "thunderstorm",
        96: "thunderstorm_with_slight_hail",
        99: "thunderstorm_with_heavy_hail"
    }
    
    return weather_codes.get(code, "unknown")

def format_weather_data(raw_data: Dict) -> Dict:
    """Format raw API data into our desired JSON structure"""
    try:
        hourly = raw_data.get('hourly', {})
        times = hourly.get('time', [])
        temperatures = hourly.get('temperature_2m', [])
        feels_like = hourly.get('apparent_temperature', [])
        weather_codes = hourly.get('weather_code', [])
        
        if not times or not temperatures:
            logger.error("No time series data found in API response")
            return {}
        
        # Get current time to find the current hour
        now = datetime.now()
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        
        # Find the current hour index and get current + next 8 hours
        weather_entries = []
        current_index = None
        
        # Find the current hour in the API response
        for i, time_str in enumerate(times):
            try:
                api_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                if api_time >= current_hour:
                    current_index = i
                    break
            except Exception as e:
                logger.warning(f"Could not parse time {time_str}: {e}")
                continue
        
        if current_index is None:
            logger.error("Could not find current hour in API response")
            return {}
        
        # Process current and next 8 hours (9 total entries)
        for i in range(9):
            if current_index + i >= len(times):
                break
                
            idx = current_index + i
            time_str = times[idx]
            temp = temperatures[idx] if idx < len(temperatures) else None
            feels = feels_like[idx] if idx < len(feels_like) else None
            weather_code = weather_codes[idx] if idx < len(weather_codes) else None
            
            # Parse the time
            try:
                dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                # Convert to UK time
                uk_time = dt.strftime('%Y-%m-%d %H:%M')
            except Exception as e:
                logger.warning(f"Could not parse time {time_str}: {e}")
                continue
            
            # Get weather status
            status = parse_weather_code(weather_code) if weather_code is not None else "unknown"
            
            weather_entry = {
                "time": uk_time,
                "temp": round(temp, 1) if temp is not None else None,
                "feels_like": round(feels, 1) if feels is not None else None,
                "status": status
            }
            
            weather_entries.append(weather_entry)
            
            if i == 0:
                logger.info(f"Current weather: {temp}°C, feels like {feels}°C, {status}")
        
        # Create the final data structure
        weather_data = {
            "location": "Stockport",
            "latitude": STOCKPORT_LAT,
            "longitude": STOCKPORT_LON,
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "current": weather_entries[0] if weather_entries else {},
            "forecast": weather_entries[1:] if len(weather_entries) > 1 else []
        }
        
        return weather_data
        
    except Exception as e:
        logger.error(f"Error formatting weather data: {e}")
        return {}

def save_weather_data(weather_data: Dict) -> bool:
    """Save weather data to JSON file"""
    try:
        # Ensure data directory exists
        DATA_DIR.mkdir(exist_ok=True)
        
        # Save to JSON file
        with open(WEATHER_DATA_FILE, 'w') as f:
            json.dump(weather_data, f, indent=2)
        
        logger.info(f"Weather data saved to {WEATHER_DATA_FILE}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving weather data: {e}")
        return False

def main():
    """Main function"""
    logger.info("=== Weather Info Script Started (Open-Meteo) ===")
    
    # Fetch weather data (no API key needed for Open-Meteo)
    raw_data = get_weather_data()
    if not raw_data:
        logger.error("Failed to fetch weather data")
        return False
    
    # Format the data
    weather_data = format_weather_data(raw_data)
    if not weather_data:
        logger.error("Failed to format weather data")
        return False
    
    # Save the data
    if save_weather_data(weather_data):
        logger.info("=== Weather Info Script Completed Successfully ===")
        return True
    else:
        logger.error("Failed to save weather data")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 