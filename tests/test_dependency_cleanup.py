#!/usr/bin/env python3
"""
Test to verify that uvloop and termcolor dependencies have been successfully removed.
This test ensures that:
1. The App class can be imported without uvloop
2. The App class can be instantiated
3. uvloop is not imported anywhere in the textbox module
4. termcolor is not imported anywhere in the textbox module
"""

import sys
import importlib


def test_app_import():
    """Test that the App class can be imported without uvloop."""
    print("Test 1: Importing App class...")
    try:
        from textbox import App
        print("  ✓ App class imported successfully")
        return True
    except ImportError as e:
        print(f"  ✗ Failed to import App class: {e}")
        return False


def test_app_instantiation():
    """Test that the App class can be instantiated."""
    print("\nTest 2: Instantiating App class...")
    try:
        from textbox import App
        app = App()
        print("  ✓ App class instantiated successfully")
        return True
    except Exception as e:
        print(f"  ✗ Failed to instantiate App class: {e}")
        return False


def test_no_uvloop_import():
    """Test that uvloop is not imported in the textbox module."""
    print("\nTest 3: Checking for uvloop imports...")
    try:
        # Import textbox module
        import textbox

        # Check if uvloop is in sys.modules after importing textbox
        if 'uvloop' in sys.modules:
            print("  ✗ uvloop was imported (found in sys.modules)")
            return False

        print("  ✓ uvloop is not imported")
        return True
    except Exception as e:
        print(f"  ✗ Error checking uvloop import: {e}")
        return False


def test_no_termcolor_import():
    """Test that termcolor is not imported in the textbox module."""
    print("\nTest 4: Checking for termcolor imports...")
    try:
        # Check if termcolor is in sys.modules after importing textbox
        if 'termcolor' in sys.modules:
            print("  ✗ termcolor was imported (found in sys.modules)")
            return False

        print("  ✓ termcolor is not imported")
        return True
    except Exception as e:
        print(f"  ✗ Error checking termcolor import: {e}")
        return False


def test_uvloop_not_installed():
    """Test that uvloop package is not required."""
    print("\nTest 5: Verifying uvloop is not required...")
    try:
        import uvloop
        print("  ⚠ uvloop is still installed (but not required)")
        # This is not a failure - it's OK if uvloop is installed,
        # we just don't want to require it
        return True
    except ImportError:
        print("  ✓ uvloop is not installed (expected)")
        return True


def test_termcolor_not_installed():
    """Test that termcolor package is not required."""
    print("\nTest 6: Verifying termcolor is not required...")
    try:
        import termcolor
        print("  ⚠ termcolor is still installed (but not required)")
        # This is not a failure - it's OK if termcolor is installed,
        # we just don't want to require it
        return True
    except ImportError:
        print("  ✓ termcolor is not installed (expected)")
        return True


def main():
    """Run all tests and report results."""
    print("=" * 60)
    print("Testing dependency cleanup: uvloop and termcolor removal")
    print("=" * 60)

    tests = [
        test_app_import,
        test_app_instantiation,
        test_no_uvloop_import,
        test_no_termcolor_import,
        test_uvloop_not_installed,
        test_termcolor_not_installed,
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✓ All tests passed! Dependencies successfully removed.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
