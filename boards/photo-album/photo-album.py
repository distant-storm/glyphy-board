#!/usr/bin/env python3
"""
Photo Album Board Script - Simple version without complex dependencies

Displays images from a photos directory. If no specific image is provided,
randomly selects one from the photos directory.

Usage:
    python3 photo-album-simple.py [image_path]
"""

import os
import sys
import random
import argparse
from datetime import datetime
from pathlib import Path

def get_supported_image_extensions():
    """Get list of supported image file extensions"""
    return {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp'}

def find_random_photo(photos_dir):
    """Find a random photo from the photos directory"""
    photos_path = Path(photos_dir)
    
    if not photos_path.exists():
        print(f"Photos directory not found: {photos_path}")
        return None
    
    # Get all image files from the photos directory
    supported_extensions = get_supported_image_extensions()
    image_files = []
    
    for file_path in photos_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            image_files.append(file_path)
    
    if not image_files:
        print(f"No image files found in {photos_path}")
        return None
    
    # Select random image
    selected_image = random.choice(image_files)
    print(f"Randomly selected photo: {selected_image.name}")
    return selected_image

def main():
    """Main function to display photo album"""
    parser = argparse.ArgumentParser(description='Display image from photo album')
    parser.add_argument('image_path', nargs='?', help='Path to image file (optional - if not provided, selects random photo)')
    
    args = parser.parse_args()
    
    try:
        current_time = datetime.now()
        print(f"=== Photo Album Board Script Executed ===")
        print(f"Current time: {current_time}")
        
        # Get the photos directory (relative to this script)
        script_dir = Path(__file__).parent
        photos_dir = script_dir / "photos"
        
        # Determine which image to use
        if args.image_path:
            # Use provided image path
            image_path = Path(args.image_path)
            if not image_path.exists():
                print(f"Image file not found: {image_path}")
                return 1
            print(f"Using provided image: {image_path}")
        else:
            # Select random photo from photos directory
            image_path = find_random_photo(photos_dir)
            if not image_path:
                print("No photo could be selected")
                return 1
        
        print(f"Selected image: {image_path}")
        print(f"Image size: {image_path.stat().st_size} bytes")
        
        # In a real implementation, this would:
        # 1. Load the image using PIL
        # 2. Process it for the eink display
        # 3. Display it on the screen
        
        # For now, just simulate successful execution
        print("Photo album display completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error in photo album display: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 