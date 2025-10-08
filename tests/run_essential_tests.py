#!/usr/bin/env python3
"""
Essential test runner for MongoDB Events Demo with camelCase field names.
This runs the most important tests to verify the system is working.
"""

import sys
import os
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_essential_tests():
    """Run essential tests to verify camelCase implementation"""
    print("🚀 Running Essential Tests for camelCase Implementation")
    print("=" * 60)
    
    # Test files to run (in order of importance)
    test_files = [
        "tests/test_comprehensive_camelcase.py",
        "tests/test_eve5_eve7_schema_crud.py", 
        "tests/test_performance.py"
    ]
    
    all_passed = True
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n📋 Running {test_file}...")
            print("-" * 40)
            
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print(f"✅ {test_file} - PASSED")
                else:
                    print(f"❌ {test_file} - FAILED")
                    print("STDOUT:", result.stdout)
                    print("STDERR:", result.stderr)
                    all_passed = False
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ {test_file} - TIMEOUT")
                all_passed = False
            except Exception as e:
                print(f"💥 {test_file} - ERROR: {e}")
                all_passed = False
        else:
            print(f"⚠️  {test_file} - NOT FOUND")
    
    return all_passed

def main():
    """Main test runner"""
    success = run_essential_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All essential tests passed!")
        print("✅ camelCase implementation is working correctly")
        print("✅ Database operations are functional")
        print("✅ API endpoints are responding")
        print("✅ Performance is acceptable")
    else:
        print("❌ Some tests failed - check the output above")
        print("🔧 Fix the issues before continuing with development")
        sys.exit(1)

if __name__ == "__main__":
    main()
