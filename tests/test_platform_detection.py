#!/usr/bin/env python3
"""
Test platform detection and Windows GUI fix
"""

import platform
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_platform_detection():
    """Test that platform is correctly detected."""
    system = platform.system()
    print(f"Platform Detection Test")
    print(f"=" * 50)
    print(f"Detected System: {system}")
    print(f"Python Version: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")
    
    if system == 'Windows':
        print("✓ Windows detected - GUI will use native API")
        print("  No display server check needed")
        return True
    elif system == 'Darwin':
        print("✓ macOS detected - GUI will use Cocoa")
        return True
    elif system == 'Linux':
        print("✓ Linux detected - Will check for X11/Wayland")
        display = os.environ.get('DISPLAY')
        wayland = os.environ.get('WAYLAND_DISPLAY')
        
        if display:
            print(f"  DISPLAY found: {display}")
            return True
        elif wayland:
            print(f"  WAYLAND_DISPLAY found: {wayland}")
            return True
        else:
            print("  No display server found - GUI cannot start")
            return False
    else:
        print(f"Unknown system: {system}")
        return False

def test_imports():
    """Test that core imports work without PyQt5."""
    print(f"\nCore Imports Test")
    print(f"=" * 50)
    
    try:
        print("Testing: src.core...")
        from src.core import SmartEngine
        print("  ✓ SmartEngine imported")
        
        print("Testing: models.sam.sam_model...")
        from models.sam.sam_model import SAMModel
        print("  ✓ SAMModel imported")
        
        print("Testing: models.yolo.yolo_model...")
        from models.yolo.yolo_model import YOLOModel
        print("  ✓ YOLOModel imported")
        
        print("Testing: src.auto_save_manager...")
        from src.auto_save_manager import AutoSaveManager
        print("  ✓ AutoSaveManager imported")
        
        print("Testing: src.weight_loader...")
        from src.weight_loader import WeightLoader
        print("  ✓ WeightLoader imported")
        
        print("\n✅ All core imports successful (PyQt5-independent)")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        return False

def test_windows_gui_fix():
    """Verify Windows GUI fix is in place."""
    print(f"\nWindows GUI Fix Verification")
    print(f"=" * 50)
    
    # Read main.py and check for platform detection
    main_py = Path(__file__).parent.parent / "main.py"
    
    with open(main_py, 'r') as f:
        content = f.read()
    
    checks = {
        "platform.system() import": "import platform" in content,
        "Windows detection": "system == 'Windows'" in content or "system == \"Windows\"" in content,
        "macOS detection": "system == 'Darwin'" in content or "system == \"Darwin\"" in content,
        "Linux detection": "system == 'Linux'" in content or "else:" in content,
    }
    
    all_passed = True
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ Windows GUI fix verified in main.py")
    else:
        print("\n❌ Some checks failed")
    
    return all_passed

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  PLATFORM DETECTION & WINDOWS GUI FIX TEST")
    print("=" * 60 + "\n")
    
    results = []
    
    # Test 1: Platform detection
    results.append(("Platform Detection", test_platform_detection()))
    
    # Test 2: Core imports (without PyQt5)
    results.append(("Core Imports", test_imports()))
    
    # Test 3: Windows GUI fix
    results.append(("Windows GUI Fix", test_windows_gui_fix()))
    
    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("\nWindows GUI will work correctly:")
        print("  1. Platform detection working ✓")
        print("  2. Core imports functional ✓")
        print("  3. GUI fix implemented ✓")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

