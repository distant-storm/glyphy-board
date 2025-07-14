# Fact Script

This script fetches random facts from the API Ninjas Facts API and saves them to a JSON file.

## Features

- Fetches random facts from API Ninjas
- Configurable number of facts to retrieve
- Saves facts to JSON format in the data directory
- Comprehensive error handling and logging
- SSL verification with fallback
- Easy configuration via text file

## Setup

### 1. Get API Key

1. Visit [API Ninjas](https://api-ninjas.com/)
2. Sign up for a free account
3. Get your API key from the dashboard

### 2. Configure the Script

1. Edit `scripts/fact_config.txt`
2. Replace `your_api_key_here` with your actual API key:

```txt
API_KEY=your_actual_api_key_here
```

### 3. Install Dependencies

The script requires the `requests` library. Install it if not already available:

```bash
pip3 install requests
```

## Usage

### Basic Usage

```bash
python3 scripts/fact.py
```

### Configuration Options

Edit `scripts/fact_config.txt` to customize:

- `API_KEY`: Your API Ninjas API key (required)
- `API_URL`: API endpoint (default: https://api.api-ninjas.com/v1/facts)

**Note**: The limit parameter is only available for premium users. Free users get 1 fact per request.

## Output

The script saves fact data to `data/fact_data.json` in the following format:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "source": "API Ninjas",
  "facts": [
    "The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after just 38 minutes."
  ],
  "count": 1
}
```

## Error Handling

The script includes comprehensive error handling for:

- Missing or invalid API key
- Network connectivity issues
- SSL certificate problems (with fallback)
- API rate limiting
- Invalid responses

## Logging

The script provides detailed logging including:

- Configuration loading status
- API request attempts
- Success/failure messages
- Retrieved facts display

## API Ninjas Facts API

- **Endpoint**: https://api.api-ninjas.com/v1/facts
- **Method**: GET
- **Authentication**: X-Api-Key header
- **Parameters**: limit (number of facts to return)
- **Rate Limit**: 50,000 requests per month (free tier)

## Examples

### Fetch a single fact:
```bash
python3 scripts/fact.py
```

### Fetch multiple facts:
For premium users only, you can modify the API call to include a limit parameter.

## Troubleshooting

### Common Issues

1. **"API key not configured"**
   - Make sure you've updated `fact_config.txt` with your actual API key

2. **"API request failed"**
   - Check your internet connection
   - Verify your API key is correct
   - Check if you've exceeded the rate limit

3. **SSL errors**
   - The script automatically retries without SSL verification as a fallback

### Getting Help

- Check the logs for detailed error messages
- Verify your API key at https://api-ninjas.com/
- Ensure the `data/` directory exists and is writable

## Files

- `scripts/fact.py` - Main script
- `scripts/fact_config.txt` - Configuration file
- `data/fact_data.json` - Output file (created automatically)
- `scripts/README_fact.md` - This documentation 