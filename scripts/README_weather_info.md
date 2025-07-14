# Weather Info Script

A script to fetch weather data from Open-Meteo API for Stockport and store it in JSON format.

## Overview

The `weather_info.py` script fetches current weather conditions and 8-hour forecast for Stockport using the [Open-Meteo](https://open-meteo.com/) API.

## Features

- **Current weather**: Temperature, feels like temperature, and weather status
- **8-hour forecast**: Hourly predictions for the next 8 hours
- **JSON output**: Structured data saved to `data/weather_data.json`
- **Error handling**: Comprehensive logging and error recovery
- **No API key required**: Open-Meteo is completely free to use
- **High accuracy**: Based on multiple weather models

## Setup

### No Setup Required!

Open-Meteo is completely free and requires no API key or registration. Just run the script!

### Install Dependencies

The script requires the `requests` library:

```bash
pip3 install requests
```

## Usage

### Basic Usage

```bash
python3 scripts/weather_info.py
```

### Test the Script

```bash
python3 scripts/test_weather_info.py
```

## Output Format

The script saves weather data to `data/weather_data.json` in the following format:

```json
{
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
    }
    // ... 7 more hourly forecasts
  ]
}
```

## Weather Status Codes

The script uses WMO (World Meteorological Organization) weather codes:

- `clear_sky` - Clear sky
- `mainly_clear` - Mainly clear
- `partly_cloudy` - Partly cloudy
- `overcast` - Overcast sky
- `foggy` - Foggy conditions
- `light_drizzle` - Light drizzle
- `moderate_drizzle` - Moderate drizzle
- `dense_drizzle` - Heavy drizzle
- `slight_rain` - Light rain
- `moderate_rain` - Moderate rain
- `heavy_rain` - Heavy rain
- `slight_snow` - Light snow
- `moderate_snow` - Moderate snow
- `heavy_snow` - Heavy snow
- `slight_rain_showers` - Light rain showers
- `moderate_rain_showers` - Moderate rain showers
- `thunderstorm` - Thunderstorms
- `thunderstorm_with_slight_hail` - Thunderstorm with hail

## Data Fields

### Current Weather
- `time` - Timestamp (YYYY-MM-DD HH:MM)
- `temp` - Temperature in Celsius
- `feels_like` - Feels like temperature in Celsius
- `status` - Weather condition description

### Forecast
- Array of 8 hourly forecasts with the same fields as current weather

## Error Handling

The script includes comprehensive error handling:

- **Network errors**: Retry logic and timeout handling
- **API errors**: Detailed error messages with status codes
- **Data parsing errors**: Graceful fallbacks for missing data

## Logging

The script provides detailed logging:

- API request status
- Data parsing progress
- Error messages with context
- Success confirmations

## Integration

This script is designed to be integrated with other parts of the system:

- Can be called from cron jobs for regular updates
- JSON output can be consumed by other scripts
- Weather data can be displayed on the e-ink board
- Can be integrated with the existing weather plugin

## Benefits of Open-Meteo

- **Free**: No API key or registration required
- **Reliable**: High uptime and fast response times
- **Accurate**: Based on multiple weather models
- **Global**: Coverage for any location worldwide
- **Simple**: Easy to use with clear documentation

## Troubleshooting

### Common Issues

1. **Network Error**
   ```
   Request error: Connection timeout
   ```
   - Check internet connection
   - Verify API endpoint is accessible

2. **API Error**
   ```
   API request failed with status code 429
   ```
   - Rate limit exceeded (unlikely with normal usage)
   - Wait a few minutes and try again

3. **Data Error**
   ```
   No time series data found in API response
   ```
   - Check if coordinates are valid
   - Verify API response format

### Debug Mode

For detailed debugging, you can modify the logging level in the script:

```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## API Information

- **API URL**: https://api.open-meteo.com/v1/forecast
- **Documentation**: https://open-meteo.com/en/docs
- **Rate Limits**: 10,000 requests per day (free tier)
- **Data Source**: Multiple weather models including ECMWF, GFS, and others

## Future Enhancements

Potential improvements for the script:

- Support for multiple locations
- Extended forecast periods
- Additional weather parameters (wind, humidity, UV index, etc.)
- Caching to reduce API calls
- Integration with existing weather plugin
- Real-time display on e-ink board
- Historical weather data 