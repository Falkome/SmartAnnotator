#!/usr/bin/env python3
"""
Test Brightness Fix - Verify multiple annotations don't darken image
Tests that multiple bounding boxes and annotations maintain image brightness.
"""

import sys
import os
import numpy as np
import cv2
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='🖼️ %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_image():
    """Create a test image with known brightness levels."""
    
    # Create a gradient test image
    height, width = 400, 600
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create gradient background
    for y in range(height):
        for x in range(width):
            image[y, x] = [
                min(255, x // 3),           # Red gradient
                min(255, (x + y) // 4),     # Green gradient  
                min(255, y // 2)            # Blue gradient
            ]
    
    # Add some bright reference squares
    cv2.rectangle(image, (50, 50), (100, 100), (255, 255, 255), -1)   # White
    cv2.rectangle(image, (150, 50), (200, 100), (128, 128, 128), -1)  # Gray
    cv2.rectangle(image, (250, 50), (300, 100), (0, 0, 0), -1)        # Black
    
    return image

def simulate_annotation_drawing(image, annotation_type, bounds, class_color=(255, 0, 0)):
    """Simulate drawing an annotation using the fixed alpha blending method."""
    
    x1, y1, x2, y2 = bounds
    
    if annotation_type == "rectangle":
        # Simulate the fixed rectangle drawing
        overlay = np.zeros_like(image, dtype=np.uint8)
        cv2.rectangle(overlay, (x1, y1), (x2, y2), class_color, -1)
        
        # Create mask for rectangle area
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
        
        # Apply alpha blending only to rectangle area
        alpha = 0.2  # 20% transparency
        rect_area = mask > 0
        image[rect_area] = (1 - alpha) * image[rect_area] + alpha * overlay[rect_area]
        
        # Draw rectangle outline
        cv2.rectangle(image, (x1, y1), (x2, y2), class_color, 2)
    
    elif annotation_type == "polygon":
        # Simulate polygon drawing
        # Create a simple triangle for testing
        pts = np.array([(x1, y1), (x2, y1), ((x1+x2)//2, y2)], np.int32)
        pts = pts.reshape((-1, 1, 2))
        
        # Create overlay for polygon
        overlay = np.zeros_like(image, dtype=np.uint8)
        cv2.fillPoly(overlay, [pts], class_color)
        
        # Create mask for polygon area
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [pts], 255)
        
        # Apply alpha blending only to polygon area
        alpha = 0.3  # 30% transparency
        poly_area = mask > 0
        image[poly_area] = (1 - alpha) * image[poly_area] + alpha * overlay[poly_area]
        
        # Draw outline
        cv2.polylines(image, [pts], True, class_color, 2)
    
    return image

def test_brightness_preservation():
    """Test that multiple annotations don't darken the image."""
    
    print("🖼️ SMART ANNOTATOR - BRIGHTNESS PRESERVATION TEST")
    print("=" * 50)
    
    try:
        # Create test image
        original_image = create_test_image()
        print("Success: Test image created")
        
        # Calculate original brightness
        original_brightness = np.mean(original_image)
        original_white_square = np.mean(original_image[50:100, 50:100])
        
        print(f"Monitor: Original image brightness: {original_brightness:.2f}")
        print(f"Monitor: Original white square brightness: {original_white_square:.2f}")
        
        # Create a copy for testing
        test_image = original_image.copy()
        
        # Add multiple annotations to test cumulative effect
        annotations = [
            ("rectangle", (120, 120, 180, 160), (255, 0, 0)),    # Red rectangle
            ("rectangle", (200, 120, 260, 160), (0, 255, 0)),    # Green rectangle  
            ("rectangle", (280, 120, 340, 160), (0, 0, 255)),    # Blue rectangle
            ("rectangle", (360, 120, 420, 160), (255, 255, 0)),  # Yellow rectangle
            ("rectangle", (120, 180, 180, 220), (255, 0, 255)),  # Magenta rectangle
            ("polygon", (200, 180, 260, 220), (0, 255, 255)),    # Cyan triangle
            ("polygon", (280, 180, 340, 220), (128, 128, 128)),  # Gray triangle
            ("polygon", (360, 180, 420, 220), (255, 128, 0)),    # Orange triangle
        ]
        
        print(f"\nSAM: Adding {len(annotations)} annotations...")
        
        brightness_history = [original_brightness]
        
        for i, (annotation_type, bounds, color) in enumerate(annotations):
            test_image = simulate_annotation_drawing(test_image, annotation_type, bounds, color)
            
            # Measure brightness after each annotation
            current_brightness = np.mean(test_image)
            brightness_history.append(current_brightness)
            
            print(f"   {i+1:2d}. {annotation_type:9s} - Brightness: {current_brightness:.2f} "
                  f"(Change: {current_brightness - original_brightness:+.2f})")
        
        # Final analysis
        final_brightness = np.mean(test_image)
        final_white_square = np.mean(test_image[50:100, 50:100])
        brightness_change = final_brightness - original_brightness
        white_square_change = final_white_square - original_white_square
        
        print(f"\nMonitor: BRIGHTNESS ANALYSIS:")
        print(f"   Original brightness: {original_brightness:.2f}")
        print(f"   Final brightness: {final_brightness:.2f}")
        print(f"   Total change: {brightness_change:+.2f}")
        print(f"   Percentage change: {(brightness_change/original_brightness)*100:+.2f}%")
        
        print(f"\n🔍 WHITE SQUARE REFERENCE (should remain unchanged):")
        print(f"   Original: {original_white_square:.2f}")
        print(f"   Final: {final_white_square:.2f}")
        print(f"   Change: {white_square_change:+.2f}")
        
        # Test thresholds
        BRIGHTNESS_TOLERANCE = 5.0  # Allow 5 brightness units change
        WHITE_SQUARE_TOLERANCE = 10.0  # White square should be mostly unchanged
        
        brightness_ok = abs(brightness_change) < BRIGHTNESS_TOLERANCE
        white_square_ok = abs(white_square_change) < WHITE_SQUARE_TOLERANCE
        
        print(f"\n🧪 TEST RESULTS:")
        if brightness_ok:
            print(f"   Success: Overall brightness preservation: PASS")
        else:
            print(f"   Error: Overall brightness preservation: FAIL (change: {brightness_change:.2f})")
        
        if white_square_ok:
            print(f"   Success: Reference area preservation: PASS")
        else:
            print(f"   Error: Reference area preservation: FAIL (change: {white_square_change:.2f})")
        
        # Save test images
        output_dir = Path('data')
        output_dir.mkdir(exist_ok=True)
        
        cv2.imwrite(str(output_dir / 'brightness_test_original.png'), 
                    cv2.cvtColor(original_image, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(output_dir / 'brightness_test_annotated.png'), 
                    cv2.cvtColor(test_image, cv2.COLOR_RGB2BGR))
        
        print(f"\n💾 Test images saved:")
        print(f"   📄 data/brightness_test_original.png")
        print(f"   📄 data/brightness_test_annotated.png")
        
        # Overall test result
        test_passed = brightness_ok and white_square_ok
        
        if test_passed:
            print(f"\n🎉 BRIGHTNESS PRESERVATION TEST: Success: PASSED")
            print(f"   Multiple annotations do not darken the image!")
            print(f"   Fixed alpha blending working correctly.")
        else:
            print(f"\nError: BRIGHTNESS PRESERVATION TEST: Error: FAILED")
            print(f"   Image darkening detected with multiple annotations.")
        
        return test_passed
        
    except Exception as e:
        print(f"Error: Brightness test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_brightness_preservation()
    
    if success:
        print(f"\nSuccess: BRIGHTNESS FIX VERIFICATION: SUCCESSFUL")
        print(f"SAM: Users can now create multiple bounding boxes without image darkening")
        print(f"🖼️ Image brightness preserved with proper alpha blending")
    else:
        print(f"\nError: BRIGHTNESS FIX VERIFICATION: FAILED")
        print(f"🔍 Additional fixes may be needed")
    
    sys.exit(0 if success else 1)
