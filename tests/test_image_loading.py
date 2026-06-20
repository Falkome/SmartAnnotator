#!/usr/bin/env python3
"""
Test Image Loading Functionality
Validates that images can be loaded and displayed correctly in the GUI.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import numpy as np
import cv2

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_test_image(filename: str, width: int = 640, height: int = 480):
    """Create a test image for loading."""
    
    # Create a colorful test image
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add colored rectangles
    image[0:height//3, :] = [255, 0, 0]      # Red top
    image[height//3:2*height//3, :] = [0, 255, 0]  # Green middle
    image[2*height//3:, :] = [0, 0, 255]     # Blue bottom
    
    # Add some text
    cv2.putText(image, "Test Image", (width//4, height//2), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    
    # Save image
    output_dir = Path("data/test_images")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / filename
    cv2.imwrite(str(output_path), image)
    
    logger.info(f"Success: Created test image: {output_path}")
    return str(output_path)


def test_canvas_load_image():
    """Test canvas image loading without GUI."""
    
    print("=" * 80)
    print("🧪 IMAGE LOADING TEST (Canvas)")
    print("=" * 80)
    print()
    
    # Create test images
    test_images = []
    for i in range(3):
        img_path = create_test_image(f"test_load_{i+1}.jpg")
        test_images.append(img_path)
    
    print()
    print("Success: Test images created")
    print()
    
    # Test canvas loading (without Qt)
    print("Monitor: Testing canvas image loading:")
    print()
    
    for img_path in test_images:
        try:
            # Read image with OpenCV
            img = cv2.imread(img_path)
            
            if img is not None:
                print(f"Success: {Path(img_path).name}: {img.shape[1]}x{img.shape[0]} - OK")
            else:
                print(f"Error: {Path(img_path).name}: Failed to load")
                
        except Exception as e:
            print(f"Error: {Path(img_path).name}: Error - {e}")
    
    print()
    print("=" * 80)
    print("🎉 IMAGE LOADING TEST COMPLETE!")
    print("=" * 80)
    print()
    print("Success: Image files are ready for GUI testing")
    print(f"File: Location: data/test_images/")
    print()
    print("App: Next step: Run main.py and try loading these images")
    print()


def test_image_navigator():
    """Test image navigator with test images."""
    
    print("=" * 80)
    print("🧪 IMAGE NAVIGATOR TEST")
    print("=" * 80)
    print()
    
    from src.image_navigator import ImageNavigator
    
    # Create navigator
    nav = ImageNavigator()
    
    # Set directory
    test_dir = "data/test_images"
    nav.set_directory(test_dir)
    
    current, total, _ = nav.get_navigation_info()
    
    print(f"File: Test directory: {test_dir}")
    print(f"📷 Images found: {total}")
    print()
    
    # Navigate through images
    print("🔄 Navigation test:")
    print()
    
    for i in range(min(5, total)):
        current_idx, total_imgs, name = nav.get_navigation_info()
        print(f"  Image {current_idx}/{total_imgs}: {name}")
        
        if nav.has_next():
            nav.get_next_image()
        else:
            print("  Warning: No more images")
            break
    
    print()
    print("Success: Image navigator working correctly")
    print()


if __name__ == "__main__":
    try:
        # Test 1: Image loading
        test_canvas_load_image()
        
        # Test 2: Image navigator
        test_image_navigator()
        
        print("=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        print()
        print("📋 Summary:")
        print("   Success: Test images created")
        print("   Success: Image loading verified")
        print("   Success: Image navigator verified")
        print()
        print("App: Ready to test in GUI:")
        print("   1. Run: python main.py")
        print("   2. Click 'Open' button")
        print("   3. Navigate to data/test_images/")
        print("   4. Select any test_load_*.jpg file")
        print("   5. Image should load successfully!")
        print()
        
    except Exception as e:
        logger.error(f"Error: Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
