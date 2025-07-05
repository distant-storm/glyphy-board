import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def ensure_data_directories():
    """Ensure data directories exist and create them if they don't"""
    # Get the project root directory (parent of src)
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data"
    
    try:
        # Create data directory if it doesn't exist
        data_dir.mkdir(exist_ok=True)
        logger.info(f"Data directory ensured at: {data_dir}")
        return str(data_dir)
    except Exception as e:
        logger.error(f"Failed to create data directory: {str(e)}")
        raise

def validate_and_fix_json_files():
    """Validate JSON files and fix corrupted ones"""
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data"
    
    json_files = {
        "schedules.json": [],
        "schedule-items.json": []
    }
    
    corrupted_files = []
    
    for filename, default_content in json_files.items():
        file_path = data_dir / filename
        
        try:
            if file_path.exists():
                # Try to read and parse the JSON file
                with open(file_path, 'r') as f:
                    content = f.read().strip()
                    
                if not content:
                    # Empty file, initialize with default content
                    logger.warning(f"Empty JSON file found: {filename}. Initializing with default content.")
                    with open(file_path, 'w') as f:
                        json.dump(default_content, f, indent=2)
                else:
                    # Try to parse JSON
                    json.loads(content)
                    logger.info(f"JSON file validated successfully: {filename}")
            else:
                # File doesn't exist, create it with default content
                logger.info(f"JSON file not found: {filename}. Creating with default content.")
                with open(file_path, 'w') as f:
                    json.dump(default_content, f, indent=2)
                    
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted JSON detected in {filename}: {str(e)}")
            corrupted_files.append(filename)
            
            # Create backup of corrupted file
            backup_path = data_dir / f"{filename}.backup"
            try:
                if file_path.exists():
                    file_path.rename(backup_path)
                    logger.warning(f"Corrupted file backed up to: {backup_path}")
            except Exception as backup_error:
                logger.error(f"Failed to backup corrupted file: {backup_error}")
            
            # Create new file with default content
            try:
                with open(file_path, 'w') as f:
                    json.dump(default_content, f, indent=2)
                logger.info(f"Reset corrupted file {filename} to default content")
            except Exception as reset_error:
                logger.error(f"Failed to reset corrupted file: {reset_error}")
                
        except Exception as e:
            logger.error(f"Unexpected error validating {filename}: {str(e)}")
            corrupted_files.append(filename)
    
    if corrupted_files:
        error_msg = f"Corrupted JSON files detected and reset: {', '.join(corrupted_files)}. Backup files created with .backup extension."
        logger.error(error_msg)
        return False, error_msg
    
    return True, "All JSON files validated successfully"

def initialize_data_system():
    """Initialize the data system by ensuring directories exist and validating JSON files"""
    try:
        # Ensure data directory exists
        data_dir = ensure_data_directories()
        
        # Validate and fix JSON files
        success, message = validate_and_fix_json_files()
        
        if success:
            logger.info("Data system initialized successfully")
        else:
            logger.warning(f"Data system initialized with warnings: {message}")
            
        return success, message
        
    except Exception as e:
        error_msg = f"Failed to initialize data system: {str(e)}"
        logger.error(error_msg)
        return False, error_msg 