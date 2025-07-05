#!/usr/bin/env python3
"""
Photo Album Board Script

Displays images from a photos directory. If no specific image is provided,
randomly selects one from the photos directory.

Usage:
    python3 photo-album.py [image_path] [--pad] [--background-color COLOR]
"""

import os
import sys
import random
import argparse
import warnings
import logging
from datetime import datetime
from pathlib import Path

# Add src directory to Python path - it's 2 levels up from this script
sys.path.insert(0, str(Path(__file__).parents[2]))

# Suppress warning from inky library
warnings.filterwarnings("ignore", message=".*Busy Wait: Held high.*")

# Import modules (now they're in the same directory structure)
from PIL import Image, ImageOps, ImageColor
from config import Config
from display.display_manager import DisplayManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_random_photo(photos_dir):
    """Get a random photo from the photos directory"""
    supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp']
    
    photos_path = Path(photos_dir)
    if not photos_path.exists():
        raise FileNotFoundError(f"Photos directory not found: {photos_path}")
    
    photo_files = []
    for file_path in photos_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_formats:
            photo_files.append(str(file_path))
    
    if not photo_files:
        raise FileNotFoundError(f"No photos found in {photos_path}. Supported formats: {supported_formats}")
    
    selected_photo = random.choice(photo_files)
    logger.info(f"Selected random photo: {Path(selected_photo).name} from {len(photo_files)} available photos")
    return selected_photo

def process_image_with_padding(image, device_config, pad=False, background_color="white"):
    """Process image exactly like the image upload plugin does"""
    if pad:
        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]
        
        frame_ratio = dimensions[0] / dimensions[1]
        img_width, img_height = image.size
        padded_img_size = (
            int(img_height * frame_ratio) if img_width >= img_height else img_width,
            img_height if img_width >= img_height else int(img_width / frame_ratio)
        )
        
        bg_color = ImageColor.getcolor(background_color, "RGB")
        image = ImageOps.pad(image, padded_img_size, color=bg_color, method=Image.Resampling.LANCZOS)
        logger.info(f"Applied padding with background color: {background_color}")
    
    return image

def main():
    """Main function to display photo album"""
    parser = argparse.ArgumentParser(description='Display a random photo from the photo album on the eink display')
    parser.add_argument('image_path', nargs='?', help='Path to specific image file (optional)')
    parser.add_argument('--pad', action='store_true', help='Pad the image to fit the screen while maintaining aspect ratio')
    parser.add_argument('--background-color', default='white', help='Background color for padding (default: white)')
    
    args = parser.parse_args()
    
    try:
        current_time = datetime.now()
        logger.info(f"=== Photo Album Board Script Executed ===")
        logger.info(f"Current time: {current_time}")
        
        # Get the photos directory relative to this script
        photos_dir = Path(__file__).parent / 'photos'
        logger.info(f"Photos directory: {photos_dir.absolute()}")
        
        # Determine which image to use
        if args.image_path:
            image_path = args.image_path
            logger.info(f"Using specified image: {image_path}")
        else:
            image_path = get_random_photo(photos_dir)
            logger.info(f"Selected random photo: {image_path}")
        
        # Load image with PIL
        logger.info(f"Loading image: {image_path}")
        try:
            image = Image.open(image_path)
            logger.info(f"Successfully loaded image: {image_path}")
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            raise
        
        # Initialize config and display manager
        config = Config()
        display_manager = DisplayManager(config)
        
        # Process image if padding requested (exactly like image upload plugin)
        processed_image = process_image_with_padding(
            image, 
            config, 
            args.pad, 
            args.background_color
        )
        
        # Display the image (pass PIL Image object directly)
        logger.info("Displaying image on eink screen...")
        display_manager.display_image(processed_image)
        
        logger.info("Photo album display completed successfully")
        
    except Exception as e:
        logger.error(f"Error in photo album: {e}")
        raise

if __name__ == "__main__":
    main() 