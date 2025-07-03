#!/usr/bin/env python3
"""
Test script to validate the Python environment and imports
This verifies the setup is correct before testing with the actual Realtime API
"""

import sys
import os

def test_imports():
    """Test that all required imports are available"""
    print("Testing imports...")
    
    try:
        import asyncio
        print("✅ asyncio - OK")
    except ImportError as e:
        print(f"❌ asyncio - FAILED: {e}")
        return False
    
    try:
        import json
        print("✅ json - OK")
    except ImportError as e:
        print(f"❌ json - FAILED: {e}")
        return False
    
    try:
        import websockets
        print(f"✅ websockets - OK (version: {websockets.__version__})")
    except ImportError as e:
        print(f"❌ websockets - FAILED: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv - OK")
    except ImportError as e:
        print(f"❌ python-dotenv - FAILED: {e}")
        return False
    
    return True

def test_environment():
    """Test environment variable loading"""
    print("\nTesting environment...")
    
    # Test loading from .env file
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env", override=True)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_openai_api_key_here":
        print("✅ OPENAI_API_KEY found in environment")
        print(f"   Key starts with: {api_key[:8]}...")
        return True
    else:
        print("⚠️  OPENAI_API_KEY not found or not configured")
        print("   Please copy .env.example to .env and add your API key")
        return False

def test_basic_async():
    """Test basic async functionality"""
    print("\nTesting async functionality...")
    
    import asyncio
    
    async def simple_async_test():
        await asyncio.sleep(0.1)
        return "async works"
    
    try:
        result = asyncio.run(simple_async_test())
        print(f"✅ Async test - OK: {result}")
        return True
    except Exception as e:
        print(f"❌ Async test - FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Python environment for OpenAI Realtime API")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test imports
    if test_imports():
        tests_passed += 1
    
    # Test environment
    if test_environment():
        tests_passed += 1
    
    # Test async
    if test_basic_async():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"Tests completed: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("✅ Environment is ready for Realtime API testing!")
        print("\nNext steps:")
        print("1. Add your OpenAI API key to .env file")
        print("2. Run: python realtime_poc.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()