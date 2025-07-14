#!/usr/bin/env python3

"""
Test script for fact.py
Tests the fact script functionality without requiring an actual API key
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the scripts directory to the path so we can import fact
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

def test_config_loading():
    """Test configuration loading functionality"""
    print("Testing configuration loading...")
    
    # Import the fact module
    import fact
    
    # Test with valid config
    config = fact.load_config()
    print(f"✓ Configuration loaded: {len(config)} items")
    
    # Test API key validation
    if 'API_KEY' in config:
        api_key = config['API_KEY']
        if api_key == 'your_api_key_here':
            print("⚠ API key not configured (expected for testing)")
        else:
            print(f"✓ API key configured: {api_key[:10]}...")
    else:
        print("⚠ No API key found in config")
    
    return True

def test_fact_formatting():
    """Test fact data formatting"""
    print("\nTesting fact data formatting...")
    
    import fact
    
    # Test with sample facts
    sample_facts = [
        "The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after just 38 minutes.",
        "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible."
    ]
    
    formatted_data = fact.format_fact_data(sample_facts)
    
    if formatted_data:
        print("✓ Fact data formatted successfully")
        print(f"  - Timestamp: {formatted_data.get('timestamp', 'N/A')}")
        print(f"  - Source: {formatted_data.get('source', 'N/A')}")
        print(f"  - Fact count: {formatted_data.get('count', 'N/A')}")
        print(f"  - Facts: {len(formatted_data.get('facts', []))}")
        
        # Test JSON serialization
        try:
            json.dumps(formatted_data)
            print("✓ Data is JSON serializable")
        except Exception as e:
            print(f"✗ JSON serialization failed: {e}")
            return False
    else:
        print("✗ Fact data formatting failed")
        return False
    
    return True

def test_file_saving():
    """Test file saving functionality"""
    print("\nTesting file saving...")
    
    import fact
    
    # Create test data
    test_data = {
        "timestamp": "2024-01-15T10:30:45.123456",
        "source": "Test",
        "facts": ["This is a test fact."],
        "count": 1
    }
    
    # Test saving
    success = fact.save_fact_data(test_data)
    
    if success:
        print("✓ File saving test passed")
        
        # Check if file was created
        if fact.FACT_DATA_FILE.exists():
            print(f"✓ Output file created: {fact.FACT_DATA_FILE}")
            
            # Read and verify the saved data
            try:
                with open(fact.FACT_DATA_FILE, 'r') as f:
                    saved_data = json.load(f)
                
                if saved_data.get('facts') == test_data['facts']:
                    print("✓ Saved data matches test data")
                else:
                    print("✗ Saved data doesn't match test data")
                    return False
                    
            except Exception as e:
                print(f"✗ Error reading saved file: {e}")
                return False
        else:
            print("✗ Output file was not created")
            return False
    else:
        print("✗ File saving test failed")
        return False
    
    return True

def test_mock_api_call():
    """Test API call with mocked response"""
    print("\nTesting API call with mock...")
    
    import fact
    
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        "This is a mock fact for testing purposes."
    ]
    
    # Test with mock
    with patch('requests.get', return_value=mock_response):
        facts = fact.get_fact("test_key", "https://test.api.com/facts")
        
        if facts:
            print("✓ Mock API call successful")
            print(f"  - Retrieved {len(facts)} fact(s)")
            print(f"  - First fact: {facts[0][:50]}...")
        else:
            print("✗ Mock API call failed")
            return False
    
    return True

def main():
    """Run all tests"""
    print("Running fact script tests...\n")
    
    tests = [
        test_config_loading,
        test_fact_formatting,
        test_file_saving,
        test_mock_api_call
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"✗ Test failed: {test.__name__}")
        except Exception as e:
            print(f"✗ Test error in {test.__name__}: {e}")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed!")
        return True
    else:
        print("✗ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 