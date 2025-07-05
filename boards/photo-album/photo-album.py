#!/usr/bin/env python3
"""
Photo Album Board Script

Displays images from a photos directory. If no specific image is provided,
randomly selects one from the photos directory.

Usage:
    python3 photo-album.py [image_path] [--pad] [--background-color COLOR]
    
    If no image_path is provided, randomly selects from ./photos/ directory
"""

import os
import sys
import random
import argparse
import logging
import logging.config
from pathlib import Path
from PIL import Image, ImageOps

# Add the project root to the path to access src modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from utils.display_manager import DisplayManager

# Setup logging
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def get_supported_image_extensions():
    """Get list of supported image file extensions"""
    return {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp'}

def find_random_photo(photos_dir):
    """Find a random photo from the photos directory"""
    photos_path = Path(photos_dir)
    
    if not photos_path.exists():
        logger.error(f"Photos directory not found: {photos_path}")
        return None
    
    # Get all image files from the photos directory
    supported_extensions = get_supported_image_extensions()
    image_files = []
    
    for file_path in photos_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            image_files.append(file_path)
    
    if not image_files:
        logger.error(f"No image files found in {photos_path}")
        return None
    
    # Select random image
    selected_image = random.choice(image_files)
    logger.info(f"Randomly selected photo: {selected_image.name}")
    return selected_image

def load_and_process_image(image_path, target_size, pad_to_fit=False, background_color='white'):
    """Load and process image for display"""
    try:
        # Open and convert image
        image = Image.open(image_path)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            logger.info(f"Converting image from {image.mode} to RGB")
            image = image.convert('RGB')
        
        original_size = image.size
        logger.info(f"Original image size: {original_size}")
        
        if pad_to_fit:
            # Pad image to fit display while maintaining aspect ratio
            logger.info("Padding image to fit display dimensions")
            image = ImageOps.pad(image, target_size, color=background_color)
        else:
            # Resize image to fit display
            logger.info("Resizing image to fit display dimensions")
            image = ImageOps.fit(image, target_size, Image.Resampling.LANCZOS)
        
        logger.info(f"Final image size: {image.size}")
        return image
        
    except Exception as e:
        logger.error(f"Error processing image {image_path}: {str(e)}")
        raise

def main():
    """Main function to display photo album"""
    parser = argparse.ArgumentParser(description='Display image on eink screen from photo album')
    parser.add_argument('image_path', nargs='?', help='Path to image file (optional - if not provided, selects random photo)')
    parser.add_argument('--pad', action='store_true', help='Pad image to fit screen while maintaining aspect ratio')
    parser.add_argument('--background-color', default='white', help='Background color for padding (default: white)')
    
    args = parser.parse_args()
    
    try:
        # Get the photos directory (relative to this script)
        script_dir = Path(__file__).parent
        photos_dir = script_dir / "photos"
        
        # Determine which image to use
        if args.image_path:
            # Use provided image path
            image_path = Path(args.image_path)
            if not image_path.exists():
                logger.error(f"Image file not found: {image_path}")
                return 1
            logger.info(f"Using provided image: {image_path}")
        else:
            # Select random photo from photos directory
            image_path = find_random_photo(photos_dir)
            if not image_path:
                logger.error("No photo could be selected")
                return 1
        
        # Initialize display manager
        logger.info("Initializing display manager...")
        display_manager = DisplayManager()
        
        # Get display dimensions
        width, height = display_manager.get_display_size()
        logger.info(f"Display size: {width}x{height}")
        
        # Load and process the image
        logger.info(f"Loading image: {image_path}")
        processed_image = load_and_process_image(
            image_path, 
            (width, height), 
            args.pad, 
            args.background_color
        )
        
        # Display the image
        logger.info("Displaying image on eink screen...")
        display_manager.display_image(processed_image)
        
        logger.info("Photo album display completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Error in photo album display: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 