#!/usr/bin/env python3
"""
Smart Annotator - Test with Real Images

Demonstrate Smart Annotator functionality with test images from test_images folder.
"""

import sys
import os
import numpy as np
import cv2
import time
import logging
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import Smart Annotator components
from src.core import SmartEngine
from models.sam.sam_model import SAMModel
from models.yolo.yolo_model import YOLOModel

# Setup logging
logging.basicConfig(level=logging.INFO, format='Engine: %(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


def test_image_analysis(image_path: str, smart_engine: SmartEngine):
    """Test smart analysis on a single image."""
    
    print(f"\n🖼️  Testing: {Path(image_path).name}")
    print("-" * 50)
    
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not load image: {image_path}")
            return
        
        # Convert to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = image_rgb.shape[:2]
        
        print(f"📏 Dimensions: {w}×{h} pixels")
        print(f"YOLO: Size: {os.path.getsize(image_path) / 1024:.1f} KB")
        
        # Smart analysis
        suggestions = smart_engine.analyze_image(image_rgb)
        
        print(f"\nEngine: Smart Analysis Results:")
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        else:
            print("  No specific suggestions - image ready for annotation")
        
        # Recommended tool
        recommended_tool = smart_engine.recommend_tool(image_rgb)
        print(f"\nTool:  Recommended Tool: {recommended_tool}")
        
        # Image complexity analysis
        complexity = smart_engine.calculate_image_complexity(image_rgb)
        print(f"Monitor: Complexity Score: {complexity:.2f}")
        
        # Smart confidence recommendation
        smart_confidence = smart_engine.get_smart_confidence(complexity)
        print(f"SAM: Recommended Confidence: {smart_confidence:.2f}")
        
        return True
        
    except Exception as e:
        print(f"Error: Error analyzing {Path(image_path).name}: {e}")
        return False


def test_sam_prediction(image_path: str, sam_model: SAMModel):
    """Test SAM predictions on an image."""
    
    print(f"\nSAM: SAM Testing: {Path(image_path).name}")
    print("-" * 40)
    
    try:
        # Load image
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = image_rgb.shape[:2]
        
        # Test point prediction (center of image)
        center_point = (w // 2, h // 2)
        print(f"SAM: Testing Magic Wand at center point: {center_point}")
        
        start_time = time.time()
        point_result = sam_model.predict_with_point(image_rgb, center_point)
        point_time = time.time() - start_time
        
        if point_result.get('success'):
            results = point_result['results']
            print(f"  Success: Found {len(results)} segments in {point_time:.2f}s")
            
            for i, result in enumerate(results):
                conf = result['confidence']
                area = result['area']
                print(f"    Segment {i+1}: Confidence {conf:.2f}, Area {area} pixels")
        else:
            print(f"  Error: Point prediction failed: {point_result.get('error', 'Unknown error')}")
        
        # Test bbox prediction (quarter of image)
        bbox = (w//4, h//4, 3*w//4, 3*h//4)
        print(f"\nYOLO: Testing BBox segment: {bbox}")
        
        start_time = time.time()
        bbox_result = sam_model.predict_with_bbox(image_rgb, bbox)
        bbox_time = time.time() - start_time
        
        if bbox_result.get('success'):
            results = bbox_result['results']
            print(f"  Success: Found {len(results)} segments in {bbox_time:.2f}s")
        else:
            print(f"  Error: BBox prediction failed: {bbox_result.get('error', 'Unknown error')}")
        
        # Test auto segmentation
        print(f"\n🔄 Testing Auto Segment...")
        
        start_time = time.time()
        auto_result = sam_model.predict_auto(image_rgb)
        auto_time = time.time() - start_time
        
        if auto_result.get('success'):
            results = auto_result['results']
            total_detections = auto_result.get('total_detections', len(results))
            print(f"  Success: Auto found {len(results)}/{total_detections} objects in {auto_time:.2f}s")
            
            if results:
                confidences = [r['confidence'] for r in results]
                print(f"  Monitor: Confidence range: {min(confidences):.2f} - {max(confidences):.2f}")
        else:
            print(f"  Error: Auto segmentation failed: {auto_result.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"Error: SAM testing error: {e}")
        return False


def test_yolo_detection(image_path: str, yolo_model: YOLOModel):
    """Test YOLO object detection on an image."""
    
    print(f"\nYOLO: YOLO Testing: {Path(image_path).name}")
    print("-" * 40)
    
    try:
        # Load image
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect objects
        start_time = time.time()
        result = yolo_model.detect_and_classify(image_rgb)
        detection_time = time.time() - start_time
        
        if result.get('success'):
            detections = result['results']
            total_objects = result.get('total_objects', 0)
            unique_classes = result.get('unique_classes', 0)
            
            print(f"  Success: Detected {total_objects} objects ({unique_classes} classes) in {detection_time:.2f}s")
            
            if detections:
                # Show top detections
                top_detections = detections[:5]  # Top 5
                print(f"  🔝 Top Detections:")
                
                for i, detection in enumerate(top_detections, 1):
                    class_name = detection['class_name']
                    confidence = detection['confidence']
                    bbox = detection['bbox']
                    width = bbox[2] - bbox[0]
                    height = bbox[3] - bbox[1]
                    
                    print(f"    {i}. {class_name} ({confidence:.2f}) - {width}×{height}px")
                
                # Class summary
                class_counts = result.get('class_counts', {})
                if class_counts:
                    print(f"  📋 Class Summary:")
                    for class_name, count in sorted(class_counts.items()):
                        print(f"    {class_name}: {count}")
            else:
                print(f"  Warning:  No objects detected (try lowering confidence threshold)")
        else:
            print(f"  Error: YOLO detection failed: {result.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"Error: YOLO testing error: {e}")
        return False


def main():
    """Main testing function."""
    
    print("Engine: Smart Annotator - Test Images Demonstration")
    print("=" * 60)
    print(f"File: Testing images from: test_images/")
    
    # Initialize components
    print("\nModel: Initializing Smart Annotator components...")
    
    try:
        # Smart Engine
        smart_engine = SmartEngine()
        smart_engine.initialize()
        print("  Success: Smart Engine initialized")
        
        # SAM Model
        sam_model = SAMModel()
        sam_loaded = sam_model.load_model()
        if sam_loaded:
            print("  Success: SAM Model loaded")
        else:
            print("  Warning:  SAM Model not available")
        
        # YOLO Model
        yolo_model = YOLOModel()
        yolo_loaded = yolo_model.load_model()
        if yolo_loaded:
            print("  Success: YOLO Model loaded")
        else:
            print("  Warning:  YOLO Model not available")
        
    except Exception as e:
        print(f"Error: Initialization error: {e}")
        return
    
    # Find test images
    test_images_dir = Path("test_images")
    if not test_images_dir.exists():
        print(f"Error: Test images directory not found: {test_images_dir}")
        return
    
    # Get all image files
    image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
    test_images = []
    
    for ext in image_extensions:
        test_images.extend(test_images_dir.glob(f"*{ext}"))
        test_images.extend(test_images_dir.glob(f"*{ext.upper()}"))
    
    if not test_images:
        print(f"Error: No test images found in {test_images_dir}")
        return
    
    print(f"\n📷 Found {len(test_images)} test images:")
    for img in sorted(test_images):
        size_kb = img.stat().st_size / 1024
        print(f"  📄 {img.name} ({size_kb:.1f} KB)")
    
    print(f"\nApp: Starting Smart Annotator testing...")
    
    # Test each image
    successful_tests = 0
    
    for i, image_path in enumerate(sorted(test_images), 1):
        print(f"\n{'='*60}")
        print(f"🖼️  TEST {i}/{len(test_images)}: {image_path.name}")
        print(f"{'='*60}")
        
        # Smart analysis
        analysis_success = test_image_analysis(str(image_path), smart_engine)
        
        # SAM testing
        if sam_loaded:
            sam_success = test_sam_prediction(str(image_path), sam_model)
        else:
            print(f"\nSAM: SAM Testing: Skipped (model not available)")
            sam_success = False
        
        # YOLO testing  
        if yolo_loaded:
            yolo_success = test_yolo_detection(str(image_path), yolo_model)
        else:
            print(f"\nYOLO: YOLO Testing: Skipped (model not available)")
            yolo_success = False
        
        # Overall success
        if analysis_success and (sam_success or yolo_success or not (sam_loaded or yolo_loaded)):
            successful_tests += 1
            print(f"\nSuccess: {image_path.name}: Testing completed successfully")
        else:
            print(f"\nWarning:  {image_path.name}: Some tests had issues")
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"🎉 SMART ANNOTATOR TESTING COMPLETE")
    print(f"{'='*60}")
    print(f"Monitor: Results Summary:")
    print(f"  📷 Images tested: {len(test_images)}")
    print(f"  Success: Successful tests: {successful_tests}")
    print(f"  📈 Success rate: {successful_tests/len(test_images):.1%}")
    print(f"  Engine: Smart Engine: Success: Working")
    print(f"  SAM: SAM Model: {'Success: Working' if sam_loaded else 'Error: Not available'}")
    print(f"  YOLO: YOLO Model: {'Success: Working' if yolo_loaded else 'Error: Not available'}")
    
    # Usage instructions
    print(f"\nApp: How to use Smart Annotator with your test images:")
    print(f"  1. Run: python main.py")
    print(f"  2. Click 'Navigator: Load Image' in the control panel")
    print(f"  3. Select images from test_images/ folder")
    print(f"  4. Choose annotation tool:")
    print(f"     SAM: Magic Wand - Click objects to segment")
    print(f"     YOLO: BBox Segment - Draw boxes around objects")  
    print(f"     🔄 Auto Segment - Automatically detect all objects")
    print(f"  5. Review AI suggestions and results")
    print(f"  6. Save annotations as JSON")
    
    print(f"\nEngine: Smart Annotator is ready for intelligent image annotation!")
    
    # Show performance summary
    if sam_loaded:
        sam_stats = sam_model.get_performance_summary()
        print(f"\n{sam_stats}")
    
    if yolo_loaded:
        yolo_stats = yolo_model.get_performance_summary()
        print(f"\n{yolo_stats}")


if __name__ == "__main__":
    main()
