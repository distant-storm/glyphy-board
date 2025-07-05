from flask import Blueprint, request, jsonify, current_app, render_template
import json
import os
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)
schedules_bp = Blueprint("schedules", __name__)

# Path to data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data"
SCHEDULES_FILE = DATA_DIR / "schedules.json"
SCHEDULE_ITEMS_FILE = DATA_DIR / "schedule-items.json"

def load_schedules():
    """Load schedules from JSON file"""
    try:
        if SCHEDULES_FILE.exists():
            with open(SCHEDULES_FILE, 'r') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)  # Use json.loads() instead of json.load()
        else:
            # File doesn't exist, create it
            save_schedules([])
            return []
    except json.JSONDecodeError as e:
        logger.error(f"Corrupted schedules.json file: {str(e)}")
        # Backup corrupted file and create new one
        backup_file = SCHEDULES_FILE.with_suffix('.json.backup')
        try:
            SCHEDULES_FILE.rename(backup_file)
            logger.warning(f"Corrupted schedules.json backed up to {backup_file}")
        except Exception:
            pass
        save_schedules([])
        return []
    except Exception as e:
        logger.error(f"Error loading schedules: {str(e)}")
        return []

def save_schedules(schedules):
    """Save schedules to JSON file"""
    try:
        # Ensure data directory exists
        SCHEDULES_FILE.parent.mkdir(exist_ok=True)
        with open(SCHEDULES_FILE, 'w') as f:
            json.dump(schedules, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving schedules: {str(e)}")
        raise

def load_schedule_items():
    """Load schedule items from JSON file"""
    try:
        if SCHEDULE_ITEMS_FILE.exists():
            with open(SCHEDULE_ITEMS_FILE, 'r') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)  # Use json.loads() instead of json.load()
        else:
            # File doesn't exist, create it
            save_schedule_items([])
            return []
    except json.JSONDecodeError as e:
        logger.error(f"Corrupted schedule-items.json file: {str(e)}")
        # Backup corrupted file and create new one
        backup_file = SCHEDULE_ITEMS_FILE.with_suffix('.json.backup')
        try:
            SCHEDULE_ITEMS_FILE.rename(backup_file)
            logger.warning(f"Corrupted schedule-items.json backed up to {backup_file}")
        except Exception:
            pass
        save_schedule_items([])
        return []
    except Exception as e:
        logger.error(f"Error loading schedule items: {str(e)}")
        return []

def save_schedule_items(schedule_items):
    """Save schedule items to JSON file"""
    try:
        # Ensure data directory exists
        SCHEDULE_ITEMS_FILE.parent.mkdir(exist_ok=True)
        with open(SCHEDULE_ITEMS_FILE, 'w') as f:
            json.dump(schedule_items, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving schedule items: {str(e)}")
        raise

def generate_id():
    """Generate a simple ID based on timestamp"""
    return str(int(datetime.now().timestamp() * 1000))

@schedules_bp.route('/schedules')
def schedules_page():
    """Display the schedules management page"""
    schedules = load_schedules()
    schedule_items = load_schedule_items()
    
    # Get data initialization status from app config
    data_init_success = current_app.config.get('DATA_INIT_SUCCESS', True)
    data_init_message = current_app.config.get('DATA_INIT_MESSAGE', '')
    
    return render_template('schedules.html', 
                         schedules=schedules, 
                         schedule_items=schedule_items,
                         data_init_success=data_init_success,
                         data_init_message=data_init_message)

@schedules_bp.route('/schedules/create', methods=['POST'])
def create_schedule():
    """Create a new schedule"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        active = data.get('active', True)

        if not name:
            return jsonify({"error": "Schedule name is required"}), 400

        schedules = load_schedules()
        
        # Check if schedule name already exists
        if any(s['name'] == name for s in schedules):
            return jsonify({"error": "Schedule name already exists"}), 400

        new_schedule = {
            "id": generate_id(),
            "name": name,
            "active": active,
            "created_at": datetime.now().isoformat()
        }

        schedules.append(new_schedule)
        save_schedules(schedules)

        return jsonify({"success": True, "message": "Schedule created successfully", "schedule": new_schedule})
    
    except Exception as e:
        logger.error(f"Error creating schedule: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@schedules_bp.route('/schedules/<schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    """Update an existing schedule"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        active = data.get('active', True)

        if not name:
            return jsonify({"error": "Schedule name is required"}), 400

        schedules = load_schedules()
        
        # Find and update the schedule
        for schedule in schedules:
            if schedule['id'] == schedule_id:
                # Check if new name conflicts with another schedule
                if any(s['name'] == name and s['id'] != schedule_id for s in schedules):
                    return jsonify({"error": "Schedule name already exists"}), 400
                
                schedule['name'] = name
                schedule['active'] = active
                schedule['updated_at'] = datetime.now().isoformat()
                break
        else:
            return jsonify({"error": "Schedule not found"}), 404

        save_schedules(schedules)
        return jsonify({"success": True, "message": "Schedule updated successfully"})
    
    except Exception as e:
        logger.error(f"Error updating schedule: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@schedules_bp.route('/schedules/<schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """Delete a schedule and all its items"""
    try:
        schedules = load_schedules()
        schedule_items = load_schedule_items()

        # Remove schedule
        schedules = [s for s in schedules if s['id'] != schedule_id]
        
        # Remove all schedule items for this schedule
        schedule_items = [item for item in schedule_items if item['schedule_id'] != schedule_id]

        save_schedules(schedules)
        save_schedule_items(schedule_items)

        return jsonify({"success": True, "message": "Schedule deleted successfully"})
    
    except Exception as e:
        logger.error(f"Error deleting schedule: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@schedules_bp.route('/schedules/<schedule_id>/items', methods=['POST'])
def create_schedule_item(schedule_id):
    """Create a new schedule item"""
    try:
        data = request.json
        board_name = data.get('board_name', '').strip()
        schedule_type = data.get('schedule_type', 'absolute')

        if not board_name:
            return jsonify({"error": "Board name is required"}), 400

        # Check if schedule exists
        schedules = load_schedules()
        if not any(s['id'] == schedule_id for s in schedules):
            return jsonify({"error": "Schedule not found"}), 404

        schedule_items = load_schedule_items()
        
        new_item = {
            "id": generate_id(),
            "schedule_id": schedule_id,
            "board_name": board_name,
            "schedule_type": schedule_type,
            "created_at": datetime.now().isoformat()
        }

        if schedule_type == 'absolute':
            start_datetime = data.get('start_datetime', '').strip()
            end_datetime = data.get('end_datetime', '').strip()

            if not all([start_datetime, end_datetime]):
                return jsonify({"error": "Start datetime and end datetime are required"}), 400

            # Validate datetime format
            try:
                start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid datetime format"}), 400

            if end_dt <= start_dt:
                return jsonify({"error": "End datetime must be after start datetime"}), 400

            new_item.update({
                "start_datetime": start_datetime,
                "end_datetime": end_datetime
            })
        else:
            # Relative pattern
            pattern_type = data.get('pattern_type', 'daily')
            start_time = data.get('start_time', '').strip()
            end_time = data.get('end_time', '').strip()

            if not all([start_time, end_time]):
                return jsonify({"error": "Start time and end time are required"}), 400

            # Validate time format
            try:
                start_time_obj = datetime.strptime(start_time, '%H:%M').time()
                end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            except ValueError:
                return jsonify({"error": "Invalid time format"}), 400

            if end_time_obj <= start_time_obj:
                return jsonify({"error": "End time must be after start time"}), 400

            new_item.update({
                "pattern_type": pattern_type,
                "start_time": start_time,
                "end_time": end_time
            })

            if pattern_type == 'weekly':
                weekly_day = data.get('weekly_day', '1')
                new_item["weekly_day"] = int(weekly_day)
            elif pattern_type == 'monthly':
                monthly_day = data.get('monthly_day', '1')
                new_item["monthly_day"] = int(monthly_day)

        schedule_items.append(new_item)
        save_schedule_items(schedule_items)

        return jsonify({"success": True, "message": "Schedule item created successfully", "item": new_item})
    
    except Exception as e:
        logger.error(f"Error creating schedule item: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@schedules_bp.route('/schedules/<schedule_id>/items/<item_id>', methods=['PUT'])
def update_schedule_item(schedule_id, item_id):
    """Update an existing schedule item"""
    try:
        data = request.json
        board_name = data.get('board_name', '').strip()
        schedule_type = data.get('schedule_type', 'absolute')

        if not board_name:
            return jsonify({"error": "Board name is required"}), 400

        schedule_items = load_schedule_items()
        
        # Find the schedule item
        item_to_update = None
        for item in schedule_items:
            if item['id'] == item_id and item['schedule_id'] == schedule_id:
                item_to_update = item
                break
        
        if not item_to_update:
            return jsonify({"error": "Schedule item not found"}), 404

        # Update common fields
        item_to_update['board_name'] = board_name
        item_to_update['schedule_type'] = schedule_type
        item_to_update['updated_at'] = datetime.now().isoformat()

        # Clear old fields
        for field in ['start_datetime', 'end_datetime', 'pattern_type', 'start_time', 'end_time', 'weekly_day', 'monthly_day']:
            if field in item_to_update:
                del item_to_update[field]

        if schedule_type == 'absolute':
            start_datetime = data.get('start_datetime', '').strip()
            end_datetime = data.get('end_datetime', '').strip()

            if not all([start_datetime, end_datetime]):
                return jsonify({"error": "Start datetime and end datetime are required"}), 400

            # Validate datetime format
            try:
                start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid datetime format"}), 400

            if end_dt <= start_dt:
                return jsonify({"error": "End datetime must be after start datetime"}), 400

            item_to_update.update({
                "start_datetime": start_datetime,
                "end_datetime": end_datetime
            })
        else:
            # Relative pattern
            pattern_type = data.get('pattern_type', 'daily')
            start_time = data.get('start_time', '').strip()
            end_time = data.get('end_time', '').strip()

            if not all([start_time, end_time]):
                return jsonify({"error": "Start time and end time are required"}), 400

            # Validate time format
            try:
                start_time_obj = datetime.strptime(start_time, '%H:%M').time()
                end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            except ValueError:
                return jsonify({"error": "Invalid time format"}), 400

            if end_time_obj <= start_time_obj:
                return jsonify({"error": "End time must be after start time"}), 400

            item_to_update.update({
                "pattern_type": pattern_type,
                "start_time": start_time,
                "end_time": end_time
            })

            if pattern_type == 'weekly':
                weekly_day = data.get('weekly_day', '1')
                item_to_update["weekly_day"] = int(weekly_day)
            elif pattern_type == 'monthly':
                monthly_day = data.get('monthly_day', '1')
                item_to_update["monthly_day"] = int(monthly_day)

        save_schedule_items(schedule_items)
        return jsonify({"success": True, "message": "Schedule item updated successfully"})
    
    except Exception as e:
        logger.error(f"Error updating schedule item: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@schedules_bp.route('/schedules/<schedule_id>/items/<item_id>', methods=['DELETE'])
def delete_schedule_item(schedule_id, item_id):
    """Delete a schedule item"""
    try:
        schedule_items = load_schedule_items()
        
        # Remove the schedule item
        original_count = len(schedule_items)
        schedule_items = [item for item in schedule_items if not (item['id'] == item_id and item['schedule_id'] == schedule_id)]
        
        if len(schedule_items) == original_count:
            return jsonify({"error": "Schedule item not found"}), 404

        save_schedule_items(schedule_items)
        return jsonify({"success": True, "message": "Schedule item deleted successfully"})
    
    except Exception as e:
        logger.error(f"Error deleting schedule item: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500 