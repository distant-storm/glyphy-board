#!/usr/bin/env python3
"""
Scheduling Engine for Glyphy Board

This script checks the current time against active schedules and executes
the appropriate board script based on matching schedule items.
"""

import json
import sys
import os
import subprocess
import logging
from datetime import datetime, time
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ScheduleEngine:
    def __init__(self):
        self.data_dir = Path("data")
        self.boards_dir = Path("src") / "boards"
        self.schedules_file = self.data_dir / "schedules.json"
        self.schedule_items_file = self.data_dir / "schedule-items.json"
        
    def load_schedules(self):
        """Load schedules from JSON file"""
        try:
            if self.schedules_file.exists():
                with open(self.schedules_file, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        return []
                    return json.loads(content)
            return []
        except Exception as e:
            logger.error(f"Error loading schedules: {e}")
            return []
    
    def load_schedule_items(self):
        """Load schedule items from JSON file"""
        try:
            if self.schedule_items_file.exists():
                with open(self.schedule_items_file, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        return []
                    return json.loads(content)
            return []
        except Exception as e:
            logger.error(f"Error loading schedule items: {e}")
            return []
    
    def is_time_in_absolute_range(self, current_time, start_datetime, end_datetime):
        """Check if current time is within absolute datetime range"""
        try:
            start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
            
            # Remove timezone info for comparison if present
            if start_dt.tzinfo:
                start_dt = start_dt.replace(tzinfo=None)
            if end_dt.tzinfo:
                end_dt = end_dt.replace(tzinfo=None)
            
            return start_dt <= current_time <= end_dt
        except Exception as e:
            logger.error(f"Error parsing absolute datetime: {e}")
            return False
    
    def is_time_in_relative_range(self, current_time, pattern_type, start_time, end_time, **kwargs):
        """Check if current time is within relative pattern range"""
        try:
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            current_time_obj = current_time.time()
            
            # Check if current time is within the time range
            if start_time_obj <= end_time_obj:
                # Same day range (e.g., 09:00 - 17:00)
                time_matches = start_time_obj <= current_time_obj <= end_time_obj
            else:
                # Overnight range (e.g., 22:00 - 06:00)
                time_matches = current_time_obj >= start_time_obj or current_time_obj <= end_time_obj
            
            if not time_matches:
                return False
            
            # Check pattern-specific conditions
            if pattern_type == 'daily':
                return True
            elif pattern_type == 'weekly':
                weekly_day = kwargs.get('weekly_day', 1)
                return current_time.weekday() == (weekly_day - 1) % 7  # Convert to Python weekday
            elif pattern_type == 'monthly':
                monthly_day = kwargs.get('monthly_day', 1)
                return current_time.day == monthly_day
            
            return False
        except Exception as e:
            logger.error(f"Error parsing relative time pattern: {e}")
            return False
    
    def find_active_schedule_item(self):
        """Find the first active schedule item that matches current time"""
        current_time = datetime.now()
        logger.info(f"Checking schedules at {current_time}")
        
        # Load data
        schedules = self.load_schedules()
        schedule_items = self.load_schedule_items()
        
        if not schedules:
            logger.warning("No schedules found")
            return None
        
        if not schedule_items:
            logger.warning("No schedule items found")
            return None
        
        # Find active schedules
        active_schedules = [s for s in schedules if s.get('active', False)]
        if not active_schedules:
            logger.warning("No active schedules found")
            return None
        
        logger.info(f"Found {len(active_schedules)} active schedules")
        
        # Check each active schedule for matching items
        for schedule in active_schedules:
            schedule_id = schedule['id']
            schedule_name = schedule['name']
            
            # Find items for this schedule
            schedule_items_for_schedule = [
                item for item in schedule_items 
                if item.get('schedule_id') == schedule_id
            ]
            
            logger.info(f"Schedule '{schedule_name}' has {len(schedule_items_for_schedule)} items")
            
            # Check each item for time match
            for item in schedule_items_for_schedule:
                if self.is_item_active_now(item, current_time):
                    logger.info(f"Found active item: {item['board_name']} in schedule '{schedule_name}'")
                    return item
        
        logger.info("No active schedule items found for current time")
        return None
    
    def is_item_active_now(self, item, current_time):
        """Check if a schedule item is active at the current time"""
        schedule_type = item.get('schedule_type', 'absolute')
        
        if schedule_type == 'absolute':
            start_datetime = item.get('start_datetime')
            end_datetime = item.get('end_datetime')
            
            if not start_datetime or not end_datetime:
                logger.warning(f"Missing datetime fields in absolute item: {item.get('id')}")
                return False
            
            return self.is_time_in_absolute_range(current_time, start_datetime, end_datetime)
        
        elif schedule_type == 'relative':
            pattern_type = item.get('pattern_type', 'daily')
            start_time = item.get('start_time')
            end_time = item.get('end_time')
            
            if not start_time or not end_time:
                logger.warning(f"Missing time fields in relative item: {item.get('id')}")
                return False
            
            kwargs = {}
            if pattern_type == 'weekly':
                kwargs['weekly_day'] = item.get('weekly_day', 1)
            elif pattern_type == 'monthly':
                kwargs['monthly_day'] = item.get('monthly_day', 1)
            
            return self.is_time_in_relative_range(
                current_time, pattern_type, start_time, end_time, **kwargs
            )
        
        return False
    
    def execute_board_script(self, board_name):
        """Execute the board script for the given board name"""
        script_path = self.boards_dir / board_name / f"{board_name}.py"
        
        if not script_path.exists():
            error_msg = f"Board script not found: {script_path}"
            logger.error(error_msg)
            self.display_error(error_msg)
            return False
        
        try:
            logger.info(f"Executing board script: {script_path}")
            
            # Use the virtual environment python if available, otherwise use sys.executable
            venv_python = Path("/usr/local/inkypi/venv_inkypi/bin/python")
            python_executable = str(venv_python) if venv_python.exists() else sys.executable
            
            result = subprocess.run(
                [python_executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Board script executed successfully: {board_name}")
                logger.debug(f"Script output: {result.stdout}")
                return True
            else:
                error_msg = f"Board script failed with return code {result.returncode}: {result.stderr}"
                logger.error(error_msg)
                self.display_error(error_msg)
                return False
                
        except subprocess.TimeoutExpired:
            error_msg = f"Board script timed out: {board_name}"
            logger.error(error_msg)
            self.display_error(error_msg)
            return False
        except Exception as e:
            error_msg = f"Error executing board script {board_name}: {str(e)}"
            logger.error(error_msg)
            self.display_error(error_msg)
            return False
    
    def display_error(self, error_message):
        """Display error message on the eink screen"""
        try:
            # Try to use the dashboard script to display the error
            dashboard_script = self.boards_dir / "dashboard" / "dashboard.py"
            if dashboard_script.exists():
                logger.info("Attempting to display error using dashboard script")
                subprocess.run([sys.executable, str(dashboard_script)], timeout=60)
            else:
                logger.warning("Dashboard script not found, cannot display error on screen")
        except Exception as e:
            logger.error(f"Failed to display error on screen: {e}")
    
    def run_scheduler(self):
        """Main scheduler execution"""
        logger.info("=== Scheduler Engine Starting ===")
        
        try:
            # Find active schedule item
            active_item = self.find_active_schedule_item()
            
            if active_item:
                board_name = active_item['board_name']
                schedule_type = active_item.get('schedule_type', 'absolute')
                
                logger.info(f"Active schedule found - Board: {board_name}, Type: {schedule_type}")
                
                # Execute the board script
                success = self.execute_board_script(board_name)
                
                if success:
                    logger.info(f"Successfully executed board script: {board_name}")
                else:
                    logger.error(f"Failed to execute board script: {board_name}")
            else:
                logger.info("No active schedule items found for current time")
                # Optionally display default content or dashboard
                dashboard_script = self.boards_dir / "dashboard" / "dashboard.py"
                if dashboard_script.exists():
                    logger.info("No active schedule, showing dashboard")
                    self.execute_board_script("dashboard")
                
        except Exception as e:
            error_msg = f"Scheduler engine error: {str(e)}"
            logger.error(error_msg)
            self.display_error(error_msg)
        
        logger.info("=== Scheduler Engine Complete ===")

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == '--debug':
        logging.getLogger().setLevel(logging.DEBUG)
    
    engine = ScheduleEngine()
    engine.run_scheduler()

if __name__ == "__main__":
    main() 