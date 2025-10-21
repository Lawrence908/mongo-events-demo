#!/usr/bin/env python3
"""
Quick test runner for EVE-12: Weekend Near-Me Discovery API

Usage:
    python tests/run_eve12_test.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_eve12_weekend_api import run_weekend_api_tests

if __name__ == "__main__":
    print("🚀 Running EVE-12 Weekend API Tests")
    print("=" * 50)
    
    success = run_weekend_api_tests()
    
    if success:
        print("\n🎉 EVE-12 implementation is working perfectly!")
        print("✅ Weekend Near-Me Discovery API is ready for production")
    else:
        print("\n❌ EVE-12 implementation has issues that need to be fixed")
        sys.exit(1)
