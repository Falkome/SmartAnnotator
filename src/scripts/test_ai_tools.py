#!/usr/bin/env python3
"""
Comprehensive AI Tools Test Script

This script tests all AI tool functionality without requiring GUI interaction.
Run this to diagnose issues with AI tools (SAM model, YOLO model, etc.)
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

def test_ai_tools():
    """Comprehensive AI tools testing."""
    
    print("\n" + "=" * 70)
    print("AI TOOLS COMPREHENSIVE TEST")
    print("=" * 70)
    
    all_passed = True
    
    # Test 1: Import Models
    print("\n📦 Test 1: Import AI Models")
    print("-" * 70)
    
    try:
        from models.sam.sam_model import SAMModel
        print("✅ SAMModel imported")
    except Exception as e:
        print(f"❌ Failed to import SAMModel: {e}")
        all_passed = False
        return False
    
    try:
        from models.yolo.yolo_model import YOLOModel
        print("✅ YOLOModel imported")
    except Exception as e:
        print(f"❌ Failed to import YOLOModel: {e}")
        all_passed = False
    
    # Test 2: Check Weight Files
    print("\n📁 Test 2: Check Model Weight Files")
    print("-" * 70)
    
    sam_weights = list(Path('weights/sam').glob('*.pt'))
    if sam_weights:
        print(f"✅ Found {len(sam_weights)} SAM weight file(s):")
        for weight in sam_weights:
            size_mb = weight.stat().st_size / (1024 * 1024)
            print(f"   - {weight.name} ({size_mb:.1f} MB)")
    else:
        print("❌ No SAM weight files found in weights/sam/")
        print("   Download models using: data/download_SAM_models.txt")
        all_passed = False
    
    yolo_weights = list(Path('weights/yolo/detection').glob('*.pt'))
    if yolo_weights:
        print(f"✅ Found {len(yolo_weights)} YOLO weight file(s):")
        for weight in yolo_weights:
            size_mb = weight.stat().st_size / (1024 * 1024)
            print(f"   - {weight.name} ({size_mb:.1f} MB)")
    else:
        print("⚠️  No YOLO weight files found (optional)")
    
    # Test 3: Initialize SAM Model
    print("\n🤖 Test 3: Initialize SAM Model")
    print("-" * 70)
    
    try:
        sam = SAMModel()
        print("✅ SAM model instance created")
        print(f"   Is loaded: {sam.is_loaded}")
        print(f"   Has methods:")
        print(f"     - predict_with_point: {hasattr(sam, 'predict_with_point')}")
        print(f"     - predict_with_bbox: {hasattr(sam, 'predict_with_bbox')}")
        print(f"     - predict_auto: {hasattr(sam, 'predict_auto')}")
    except Exception as e:
        print(f"❌ Failed to create SAM model: {e}")
        all_passed = False
        return False
    
    # Test 4: Load SAM Model
    print("\n⚙️  Test 4: Load SAM Model")
    print("-" * 70)
    
    if not sam_weights:
        print("⏭️  Skipping - no SAM weights available")
    else:
        try:
            print("   Loading model (this may take 10-30 seconds)...")
            success = sam.load_model()
            
            if success:
                print(f"✅ SAM model loaded successfully")
                print(f"   Model path: {sam.model_path}")
                print(f"   Is loaded: {sam.is_loaded}")
            else:
                print("❌ SAM model failed to load")
                all_passed = False
        except Exception as e:
            print(f"❌ Exception during SAM model loading: {e}")
            all_passed = False
    
    # Test 5: Test with Sample Image
    print("\n🖼️  Test 5: Test AI Tools with Sample Image")
    print("-" * 70)
    
    # Look for a test image
    test_images = [
        'data/marbles.jpg',
        'data/test.jpg',
        'data/test_images/test_load_1.jpg'
    ]
    
    test_image_path = None
    for img_path in test_images:
        if Path(img_path).exists():
            test_image_path = img_path
            break
    
    if test_image_path:
        print(f"   Using test image: {test_image_path}")
        
        try:
            import cv2
            image = cv2.imread(test_image_path)
            
            if image is None:
                print(f"❌ Failed to load image: {test_image_path}")
            else:
                h, w = image.shape[:2]
                print(f"✅ Image loaded: {w}x{h} pixels")
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                if sam.is_loaded:
                    # Test Auto Segmentation
                    print("\n   Testing Auto Segmentation...")
                    try:
                        result = sam.predict_auto(image_rgb)
                        
                        if result.get('success'):
                            segments = result.get('results', [])
                            time_taken = result.get('processing_time', 0)
                            print(f"✅ Auto segment successful")
                            print(f"   - Objects detected: {len(segments)}")
                            print(f"   - Processing time: {time_taken:.2f}s")
                        else:
                            error = result.get('error', 'Unknown error')
                            print(f"⚠️  Auto segment returned no results: {error}")
                    except Exception as e:
                        print(f"❌ Auto segment failed: {e}")
                        all_passed = False
                    
                    # Test Point-based Segmentation
                    print("\n   Testing Point-based Segmentation...")
                    try:
                        center_x, center_y = w // 2, h // 2
                        result = sam.predict_with_point(image_rgb, (center_x, center_y))
                        
                        if result.get('success'):
                            print(f"✅ Point segment successful at ({center_x}, {center_y})")
                        else:
                            error = result.get('error', 'Unknown error')
                            print(f"⚠️  Point segment failed: {error}")
                    except Exception as e:
                        print(f"❌ Point segment exception: {e}")
                        all_passed = False
                    
                    # Test BBox-based Segmentation
                    print("\n   Testing BBox-based Segmentation...")
                    try:
                        # Use center quarter of image
                        x1, y1 = w // 4, h // 4
                        x2, y2 = 3 * w // 4, 3 * h // 4
                        result = sam.predict_with_bbox(image_rgb, (x1, y1, x2, y2))
                        
                        if result.get('success'):
                            segments = result.get('results', [])
                            print(f"✅ BBox segment successful")
                            print(f"   - Objects in box: {len(segments)}")
                        else:
                            error = result.get('error', 'Unknown error')
                            print(f"⚠️  BBox segment failed: {error}")
                    except Exception as e:
                        print(f"❌ BBox segment exception: {e}")
                        all_passed = False
                else:
                    print("⏭️  Skipping AI tests - SAM model not loaded")
                    
        except Exception as e:
            print(f"❌ Image processing failed: {e}")
            all_passed = False
    else:
        print("⏭️  No test images found - skipping image tests")
        print("   Place a test image at: data/test.jpg")
    
    # Test 6: GUI Signal System
    print("\n🎨 Test 6: GUI Signal System")
    print("-" * 70)
    
    try:
        from PyQt5.QtCore import pyqtSignal, QObject
        
        class TestSignals(QObject):
            tool_selected = pyqtSignal(str)
            auto_segment_requested = pyqtSignal()
        
        test_obj = TestSignals()
        
        # Test signal connections
        received_signals = []
        test_obj.tool_selected.connect(lambda x: received_signals.append(('tool', x)))
        test_obj.auto_segment_requested.connect(lambda: received_signals.append(('auto', None)))
        
        # Emit signals
        test_obj.tool_selected.emit('auto')
        test_obj.auto_segment_requested.emit()
        
        if len(received_signals) == 2:
            print("✅ Qt signals working correctly")
            print(f"   - tool_selected received: {received_signals[0][1]}")
            print(f"   - auto_segment_requested received")
        else:
            print(f"❌ Signal test failed - received {len(received_signals)}/2 signals")
            all_passed = False
            
    except Exception as e:
        print(f"❌ Qt signal test failed: {e}")
        all_passed = False
    
    # Final Summary
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED - AI Tools are working correctly!")
        print("\nIf tools still don't work in GUI:")
        print("  1. Make sure to LOAD AN IMAGE first (File → Load Image)")
        print("  2. Click the tool button to SELECT it (button turns blue)")
        print("  3. Click on the IMAGE to activate the tool")
        print("  4. Wait for model to load on first use (10-30 seconds)")
        print("\nSee data/docs/AI_TOOLS_DIAGNOSTIC.md for detailed guide")
    else:
        print("⚠️  SOME TESTS FAILED - Check errors above")
        print("\nCommon fixes:")
        print("  - Download SAM weights: see data/download_SAM_models.txt")
        print("  - Install dependencies: pip install ultralytics torch opencv-python")
        print("  - Check Python environment: conda activate ml")
    print("=" * 70)
    print()
    
    return all_passed

if __name__ == "__main__":
    try:
        success = test_ai_tools()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

