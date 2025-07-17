"""
Test script to verify power parsing logic
"""

def test_power_parsing():
    """Test the power parsing logic with expected PiJuice utility output"""
    
    # Simulate the expected output from pijuice_util.py --get-input
    test_outputs = [
        # Mains power connected
        "{'ioVoltage': 5.0, 'ioCurrent': 0.5, 'gpioPowerStatus': 'PRESENT', 'usbPowerInput': 'PRESENT'}",
        
        # Battery power only
        "{'ioVoltage': 3.7, 'ioCurrent': 0.1, 'gpioPowerStatus': 'NOT_PRESENT', 'usbPowerInput': 'NOT_PRESENT'}",
        
        # Mixed case
        "{'ioVoltage': 5.0, 'ioCurrent': 0.3, 'gpioPowerStatus': 'PRESENT', 'usbPowerInput': 'Present'}",
    ]
    
    for i, output in enumerate(test_outputs):
        print(f"\nTest {i+1}: {output}")
        
        # Parse the output to find power input status
        output_lines = output.split('\n')
        for line in output_lines:
            if 'usbPowerInput' in line:
                # Extract the power input status - be more specific about the value
                if "'usbPowerInput': 'PRESENT'" in line or '"usbPowerInput": "PRESENT"' in line:
                    print("  Result: Mains power detected")
                    break
                elif "'usbPowerInput': 'NOT_PRESENT'" in line or '"usbPowerInput": "NOT_PRESENT"' in line:
                    print("  Result: Battery power detected")
                    break
        else:
            print("  Result: No usbPowerInput found in output")

if __name__ == "__main__":
    test_power_parsing() 