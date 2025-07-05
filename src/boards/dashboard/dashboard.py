#!/usr/bin/env python3

import sys
from pathlib import Path

# Add src directory to Python path - it's 2 levels up from this script
sys.path.insert(0, str(Path(__file__).parents[2]))

from config import Config
from display.display_manager import DisplayManager
import logging
from PIL import Image, ImageDraw, ImageFont

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    try:
        config = Config()
        display_manager = DisplayManager(config)
        
        # Get screen dimensions from config
        width, height = config.get_resolution()
        
        # Create a new image with white background
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Choose font size based on screen size
        font_size = min(width, height) // 8
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Get text and calculate position to center it
        text = "dashboard"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw the text
        draw.text((x, y), text, fill='black', font=font)
        
        # Display the image
        display_manager.display_pil_image(image)
        
        logger.info("Dashboard displayed successfully")
        
    except Exception as e:
        logger.error(f"Error displaying dashboard: {e}")
        raise

if __name__ == "__main__":
    main() 