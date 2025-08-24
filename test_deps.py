#!/usr/bin/env python3
"""
Test script to check if aiosignal version conflicts are resolved
"""
import sys

def test_aiosignal_import():
    try:
        import aiosignal
        print(f"aiosignal version: {aiosignal.__version__}")
        return True
    except ImportError as e:
        print(f"Failed to import aiosignal: {e}")
        return False

def test_aiohttp_import():
    try:
        import aiohttp
        print(f"aiohttp version: {aiohttp.__version__}")
        return True
    except ImportError as e:
        print(f"Failed to import aiohttp: {e}")
        return False

if __name__ == "__main__":
    print("Testing dependency compatibility...")
    aiosignal_ok = test_aiosignal_import()
    aiohttp_ok = test_aiohttp_import()

    if aiosignal_ok and aiohttp_ok:
        print("✅ Dependencies are compatible!")
        sys.exit(0)
    else:
        print("❌ Dependency issues detected")
        sys.exit(1)
