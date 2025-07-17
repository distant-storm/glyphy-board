import sys
from pathlib import Path

# Add src directory to Python path - it's 2 levels up from this script
sys.path.insert(0, str(Path(__file__).parents[2]))

from config import Config
from display.display_manager import DisplayManager
import logging
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Display an image on the eink display')
    parser.add_argument('image_path', help='Path to the image file')
    parser.add_argument('--pad', action='store_true', help='Pad the image to fit the screen while maintaining aspect ratio')
    parser.add_argument('--background-color', default='white', help='Background color for padding (default: white)')
    
    args = parser.parse_args()
    
    try:
        config = Config()
        display_manager = DisplayManager(config)
        
        display_manager.display_image(
            image_path=args.image_path,
            pad=args.pad,
            background_color=args.background_color
        )
        
        logger.info(f"Image displayed successfully: {args.image_path}")
        
    except Exception as e:
        logger.error(f"Error displaying image: {e}")
        raise

if __name__ == "__main__":
    main() 