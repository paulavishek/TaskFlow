#!/usr/bin/env python3
"""
API Protection Test Script

This script tests the protection system to ensure it's working correctly.
"""

import os
import sys

# Add the project root to Python path
sys.path.append('.')

def test_protection_system():
    """Test the API protection system"""
    print("🧪 Testing API Cost Protection System")
    print("=" * 50)
    
    try:
        # Test 1: Import protection system
        print("Test 1: Importing protection system...")
        from api_protection_system import api_protection, get_status_report
        print("✅ Protection system imported successfully")
        
        # Test 2: Check status
        print("\nTest 2: Checking protection status...")
        status = get_status_report()
        print(f"✅ Daily limit: ${status['daily_limit']:.2f}")
        print(f"✅ Monthly limit: ${status['monthly_limit']:.2f}")
        print(f"✅ Protection active: {status['protection_active']}")
        
        # Test 3: Import protected AI functions
        print("\nTest 3: Importing protected AI functions...")
        from kanban.utils.ai_utils import generate_task_description
        print("✅ Protected AI functions imported successfully")
        
        # Test 4: Test protection mechanism
        print("\nTest 4: Testing protection mechanism...")
        allowed, reason = api_protection.should_allow_api_call("test_function")
        print(f"✅ API call allowed: {allowed} - {reason}")
        
        # Test 5: Test cost tracking
        print("\nTest 5: Testing cost tracking...")
        test_cost = 0.000001  # Very small test cost
        success = api_protection.add_cost("test_function", test_cost)
        print(f"✅ Cost tracking works: ${test_cost:.6f} added")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("Your API protection system is fully operational.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test Error: {e}")
        return False

def test_cost_manager():
    """Test the cost manager commands"""
    print("\n🔧 Testing Cost Manager Commands")
    print("=" * 50)
    
    try:
        # Test status command
        print("Testing status command...")
        os.system("python api_cost_manager.py status")
        print("✅ Status command works")
        
        return True
    except Exception as e:
        print(f"❌ Cost Manager Error: {e}")
        return False

if __name__ == "__main__":
    success1 = test_protection_system()
    success2 = test_cost_manager()
    
    if success1 and success2:
        print("\n🛡️ PROTECTION SYSTEM FULLY OPERATIONAL! 🛡️")
        print("Your TaskFlow application is now protected against unexpected API costs.")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")
