#!/usr/bin/env python3

"""
Debug script to capture and analyze PiJuice utility output
"""

import subprocess
import re
from pathlib import Path

def debug_pijuice_output():
    """Debug the PiJuice utility output"""
    print("=== PiJuice Utility Output Debug ===")
    
    script_dir = Path(__file__).parent / 'scripts'
    pijuice_util = script_dir / 'pijuice_util.py'
    
    if not pijuice_util.exists():
        print(f"❌ PiJuice utility not found at: {pijuice_util}")
        return
    
    print(f"✅ PiJuice utility found at: {pijuice_util}")
    
    # Test battery output
    print("\n--- Testing Battery Output ---")
    try:
        result = subprocess.run(
            ['/home/webdev/.virtualenvs/pimoroni/bin/python3', str(pijuice_util), '--get-battery'],
            capture_output=True, text=True, check=False, timeout=10
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT:")
        print("=" * 50)
        print(result.stdout)
        print("=" * 50)
        
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        
        if result.returncode == 0:
            # Analyze the output
            print("\n--- Analyzing Output ---")
            output_lines = result.stdout.split('\n')
            
            for i, line in enumerate(output_lines):
                print(f"Line {i}: '{line}'")
                if 'chargeLevel' in line:
                    print(f"  -> Found chargeLevel in line {i}")
                    
                    # Test different regex patterns
                    patterns = [
                        (r"'chargeLevel':\s*(\d+)|"chargeLevel":\s*(\d+)", "New pattern"),
                        (r"'chargeLevel':\s*(\d+)", "Single quote pattern"),
                        (r'"chargeLevel":\s*(\d+)', "Double quote pattern"),
                        (r'chargeLevel.*?(\d+)', "Simple pattern"),
                        (r'(\d+)', "Original pattern")
                    ]
                    
                    for pattern, name in patterns:
                        match = re.search(pattern, line)
                        if match:
                            groups = match.groups()
                            print(f"    {name}: {groups}")
                        else:
                            print(f"    {name}: No match")
                    
                    # Try to extract the actual value
                    print(f"  -> Raw line content: '{line}'")
                    
    except Exception as e:
        print(f"❌ Error running PiJuice utility: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pijuice_output() 