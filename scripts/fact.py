#!/usr/bin/env python3

"""
Fact Script
Fetches random facts from API Ninjas
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime
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
FACT_DATA_FILE = DATA_DIR / 'fact_data.json'
CONFIG_FILE = SCRIPT_DIR / 'fact_config.txt'

def load_config() -> Dict:
    """Load configuration from fact_config.txt"""
    config = {}
    
    if not CONFIG_FILE.exists():
        logger.error(f"Configuration file not found: {CONFIG_FILE}")
        logger.info("Please create fact_config.txt with your API key")
        return config
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        
        logger.info("Configuration loaded successfully")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return config

def get_fact(api_key: str, api_url: str) -> Optional[List[str]]:
    """Fetch facts from API Ninjas"""
    try:
        headers = {
            'X-Api-Key': api_key
        }
        
        logger.info("Fetching fact from API Ninjas")
        
        # Try with SSL verification first
        try:
            response = requests.get(api_url, headers=headers, timeout=30, verify=True)
            if response.status_code == 200:
                logger.info("Successfully fetched facts from API Ninjas (with SSL verification)")
                return response.json()
        except requests.exceptions.SSLError as ssl_error:
            logger.warning(f"SSL verification failed: {ssl_error}")
            logger.info("Retrying without SSL verification...")
            
            # Fallback: try without SSL verification
            try:
                response = requests.get(api_url, headers=headers, timeout=30, verify=False)
                if response.status_code == 200:
                    logger.info("Successfully fetched facts from API Ninjas (without SSL verification)")
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
        logger.error(f"Unexpected error fetching facts: {e}")
        return None

def format_fact_data(facts: List[str]) -> Dict:
    """Format facts into our desired JSON structure"""
    try:
        if not facts:
            logger.error("No facts received from API")
            return {}
        
        # Create the final data structure
        fact_data = {
            "timestamp": datetime.now().isoformat(),
            "source": "API Ninjas",
            "facts": facts,
            "count": len(facts)
        }
        
        logger.info(f"Formatted {len(facts)} fact(s)")
        return fact_data
        
    except Exception as e:
        logger.error(f"Error formatting fact data: {e}")
        return {}

def save_fact_data(fact_data: Dict) -> bool:
    """Save fact data to JSON file"""
    try:
        # Ensure data directory exists
        DATA_DIR.mkdir(exist_ok=True)
        
        # Save to JSON file
        with open(FACT_DATA_FILE, 'w') as f:
            json.dump(fact_data, f, indent=2)
        
        logger.info(f"Fact data saved to: {FACT_DATA_FILE}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving fact data: {e}")
        return False

def main():
    """Main function"""
    logger.info("Starting fact script")
    
    # Load configuration
    config = load_config()
    
    # Check for required configuration
    api_key = config.get('API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        logger.error("API key not configured. Please update fact_config.txt with your API key.")
        logger.info("Get a free API key from: https://api-ninjas.com/")
        return False
    
    api_url = config.get('API_URL', 'https://api.api-ninjas.com/v1/facts')
    
    # Fetch facts
    facts = get_fact(api_key, api_url)
    if not facts:
        logger.error("Failed to fetch facts")
        return False
    
    # Format the data
    fact_data = format_fact_data(facts)
    if not fact_data:
        logger.error("Failed to format fact data")
        return False
    
    # Save the data
    if not save_fact_data(fact_data):
        logger.error("Failed to save fact data")
        return False
    
    # Display the fact(s)
    logger.info("Facts retrieved:")
    for i, fact in enumerate(facts, 1):
        logger.info(f"{i}. {fact}")
    
    logger.info("Fact script completed successfully")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 