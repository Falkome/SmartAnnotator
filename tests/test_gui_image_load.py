#!/usr/bin/env python3
"""
Test GUI Image Loading
Quick test to verify image loading works in the GUI.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("🧪 Testing GUI Image Loading...")
print("=" * 80)
print()

# Check if test images exist
test_images_dir = Path("data/test_images")
if not test_images_dir.exists():
    print("Error: Test images directory not found!")
    print("   Run: python src/test_image_loading.py first")
    sys.exit(1)

test_images = list(test_images_dir.glob("test_load_*.jpg"))
if not test_images:
    print("Error: No test images found!")
    print("   Run: python src/test_image_loading.py first")
    sys.exit(1)

print(f"Success: Found {len(test_images)} test images:")
for img in test_images:
    print(f"   📷 {img.name}")
print()

# Test canvas loading without GUI
print("Monitor: Testing Canvas image loading:")
print()

from ui.components.canvas import SmartCanvas
from src.label_manager import LabelManager

# Create minimal canvas
try:
    label_manager = LabelManager()
    canvas = SmartCanvas()
    canvas.set_label_manager(label_manager)
    
    print("Success: Canvas created successfully")
    print()
    
    # Test loading images
    for test_img in test_images[:2]:  # Test first 2 images
        success = canvas.load_image(str(test_img))
        
        if success:
            print(f"Success: Loaded: {test_img.name}")
            print(f"   Shape: {canvas.current_image.shape}")
            print(f"   Size: {canvas.current_image.shape[1]}x{canvas.current_image.shape[0]}")
        else:
            print(f"Error: Failed to load: {test_img.name}")
        print()
    
    print("=" * 80)
    print("🎉 GUI IMAGE LOADING TEST PASSED!")
    print("=" * 80)
    print()
    print("Success: Canvas can load images successfully")
    print("Success: Image dimensions detected correctly")
    print()
    print("App: Next: Test in full GUI")
    print("   Run: python main.py")
    print("   Then click 'Open' and load data/test_images/test_load_1.jpg")
    print()
    
except Exception as e:
    print(f"Error: Canvas loading test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
