#!/usr/bin/env python3

"""
Test script to verify power detection with PiJuice
"""

import os
import subprocess
import sys
from pathlib import Path

def check_pijuice_available():
    """Check if PiJuice CLI is available"""
    try:
        result = subprocess.run(['which', 'pijuice_cli'], 
                              capture_output=True, text=True, check=False)
        return result.returncode == 0
    except Exception:
        return False

def test_pijuice_utility():
    """Test the PiJuice utility script"""
    print("=== PiJuice Utility Test ===")
    
    script_dir = Path(__file__).parent
    pijuice_util = script_dir / 'pijuice_util.py'
    
    if not pijuice_util.exists():
        print("✗ pijuice_util.py not found")
        return False
    
    print(f"✓ pijuice_util.py found at {pijuice_util}")
    
    # Test input status
    try:
        result = subprocess.run(
            ['python3', str(pijuice_util), '--get-input'],
            capture_output=True, text=True, check=False, timeout=10
        )
        print(f"Input status return code: {result.returncode}")
        print(f"Input status output: {result.stdout}")
        if result.stderr:
            print(f"Input status error: {result.stderr}")
    except Exception as e:
        print(f"Input status test error: {e}")
    
    # Test battery status
    try:
        result = subprocess.run(
            ['python3', str(pijuice_util), '--get-battery'],
            capture_output=True, text=True, check=False, timeout=10
        )
        print(f"Battery status return code: {result.returncode}")
        print(f"Battery status output: {result.stdout}")
        if result.stderr:
            print(f"Battery status error: {result.stderr}")
    except Exception as e:
        print(f"Battery status test error: {e}")
    
    return True

def test_power_detection():
    """Test power detection methods"""
    print("=== Power Detection Test ===")
    
    # Check PiJuice CLI availability
    print(f"PiJuice CLI available: {check_pijuice_available()}")
    
    # Test PiJuice utility
    test_pijuice_utility()
    
    # Check system files
    print("\n=== System Files Check ===")
    
    # PiJuice-specific files
    pijuice_files = [
        "/sys/class/power_supply/pijuice/online",
        "/sys/class/power_supply/pijuice/status",
        "/sys/class/power_supply/pijuice/capacity",
        "/sys/class/power_supply/pijuice/charge_now",
        "/sys/class/power_supply/pijuice/charge_full"
    ]
    
    print("PiJuice system files:")
    for file_path in pijuice_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    content = f.read().strip()
                print(f"  ✓ {file_path}: {content}")
            except Exception as e:
                print(f"  ✗ {file_path}: Error reading - {e}")
        else:
            print(f"  ✗ {file_path}: Not found")
    
    # Standard AC power files
    print("\nStandard AC power files:")
    ac_files = [
        "/sys/class/power_supply/AC/online",
        "/sys/class/power_supply/BAT0/capacity",
        "/sys/class/power_supply/BAT1/capacity",
        "/sys/class/power_supply/battery/capacity"
    ]
    
    for file_path in ac_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    content = f.read().strip()
                print(f"  ✓ {file_path}: {content}")
            except Exception as e:
                print(f"  ✗ {file_path}: Error reading - {e}")
        else:
            print(f"  ✗ {file_path}: Not found")
    
    print("\n=== Power Detection Logic ===")
    
    # Simulate the power detection logic
    is_mains = False
    
    # Check PiJuice system files first
    if os.path.exists("/sys/class/power_supply/pijuice/online"):
        with open("/sys/class/power_supply/pijuice/online", "r") as f:
            pijuice_status = f.read().strip()
            is_mains = pijuice_status == "1"
            print(f"PiJuice online status: {pijuice_status} -> {'Mains' if is_mains else 'Battery'}")
    
    elif os.path.exists("/sys/class/power_supply/pijuice/status"):
        with open("/sys/class/power_supply/pijuice/status", "r") as f:
            status = f.read().strip().lower()
            if status in ['charging', 'full']:
                is_mains = True
                print(f"PiJuice battery status: {status} -> Mains")
            elif status == 'discharging':
                is_mains = False
                print(f"PiJuice battery status: {status} -> Battery")
    
    elif os.path.exists("/sys/class/power_supply/AC/online"):
        with open("/sys/class/power_supply/AC/online", "r") as f:
            ac_status = f.read().strip()
            is_mains = ac_status == "1"
            print(f"AC online status: {ac_status} -> {'Mains' if is_mains else 'Battery'}")
    
    else:
        print("No power detection method available -> Assuming Battery")
        is_mains = False
    
    print(f"\nFinal power detection result: {'Mains' if is_mains else 'Battery'}")

if __name__ == "__main__":
    test_power_detection() 