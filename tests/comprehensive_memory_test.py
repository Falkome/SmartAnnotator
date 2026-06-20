#!/usr/bin/env python3
"""
Comprehensive Memory Leakage Test for Smart Annotator
Tests all components for memory leaks and optimization.
"""

import os
import sys
import time
import psutil
import gc
import numpy as np
import cv2
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='Engine: %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def cleanup_system_memory():
    """Clean up system memory."""
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass

def create_test_image(size=(800, 600)):
    """Create a test image for memory testing."""
    return np.random.randint(0, 255, (*size, 3), dtype=np.uint8)

def test_memory_leaks():
    """Run comprehensive memory leak tests."""
    
    print("Engine: SMART ANNOTATOR - COMPREHENSIVE MEMORY LEAK TEST")
    print("=" * 60)
    
    initial_memory = get_memory_usage()
    print(f"🏁 Initial Memory: {initial_memory:.1f} MB")
    
    # Test results tracking
    test_results = {
        'brush_tool': False,
        'sam_model': False, 
        'yolo_model': False,
        'core_engine': False,
        'overall_leak': False
    }
    
    # ===== TEST 1: BRUSH TOOL MEMORY =====
    print("\n" + "="*50)
    print("Brush: TEST 1: BRUSH TOOL MEMORY")
    print("="*50)
    
    try:
        from ui.components.brush_tool import BrushTool
        
        brush_start = get_memory_usage()
        brush_tool = BrushTool()
        
        # Simulate intensive brush usage
        for cycle in range(5):
            print(f"🔄 Brush Cycle {cycle + 1}/5")
            
            # Create strokes
            for stroke in range(20):
                brush_tool.set_brush_mode("paint")
                brush_tool.set_brush_size(10)
                
                # Start and finish stroke
                try:
                    x, y = np.random.randint(0, 800), np.random.randint(0, 600)
                    brush_tool.start_stroke(x, y, (600, 800))
                    
                    # Continue stroke
                    for point in range(10):
                        x2, y2 = np.random.randint(0, 800), np.random.randint(0, 600) 
                        brush_tool.continue_stroke(x2, y2, (600, 800))
                    
                    # Finish stroke
                    brush_tool.finish_stroke()
                    
                except Exception as e:
                    print(f"   Stroke error: {e}")
                
                # Clear occasionally
                if stroke % 5 == 0:
                    brush_tool.clear_all()
                    cleanup_system_memory()
            
            cycle_memory = get_memory_usage()
            print(f"   Memory after cycle: {cycle_memory:.1f} MB")
        
        # Final cleanup
        brush_tool.cleanup_memory()
        del brush_tool
        cleanup_system_memory()
        
        brush_end = get_memory_usage()
        brush_growth = brush_end - brush_start
        
        print(f"\nMonitor: Brush Tool Results:")
        print(f"   Start: {brush_start:.1f} MB")
        print(f"   End: {brush_end:.1f} MB") 
        print(f"   Growth: {brush_growth:.1f} MB")
        
        if brush_growth < 5.0:  # Allow up to 5MB growth
            print("Success: Brush Tool: PASSED")
            test_results['brush_tool'] = True
        else:
            print("Error: Brush Tool: FAILED - Excessive memory growth")
            
    except Exception as e:
        print(f"Error: Brush Tool Test Error: {e}")
    
    # ===== TEST 2: SAM MODEL MEMORY =====
    print("\n" + "="*50)
    print("SAM: TEST 2: SAM MODEL MEMORY")
    print("="*50)
    
    try:
        from models.sam.sam_model import SAMModel
        
        sam_start = get_memory_usage()
        sam_model = SAMModel()
        
        # Load model
        sam_loaded = sam_model.load_model()
        if sam_loaded:
            print("Success: SAM model loaded successfully")
            
            # Test predictions with memory monitoring
            test_image = create_test_image()
            
            for prediction_cycle in range(3):
                print(f"🔄 SAM Prediction Cycle {prediction_cycle + 1}/3")
                
                # Multiple predictions
                for pred in range(5):
                    try:
                        # Use correct SAM model method
                        center_x, center_y = test_image.shape[1] // 2, test_image.shape[0] // 2
                        result = sam_model.predict_with_point(test_image, (center_x, center_y))
                        
                        if result.get('success'):
                            segments = len(result.get('results', []))
                            print(f"   Prediction {pred + 1}: {segments} segments")
                        else:
                            print(f"   Prediction {pred + 1}: Error - {result.get('error', 'Failed')}")
                        
                        # Cleanup after each prediction
                        cleanup_system_memory()
                        
                    except Exception as e:
                        print(f"   Prediction {pred + 1}: Error - {e}")
                
                cycle_memory = get_memory_usage()
                print(f"   Memory after cycle: {cycle_memory:.1f} MB")
        
        # Cleanup SAM model
        sam_model.cleanup()
        del sam_model
        cleanup_system_memory()
        
        sam_end = get_memory_usage()
        sam_growth = sam_end - sam_start
        
        print(f"\nMonitor: SAM Model Results:")
        print(f"   Start: {sam_start:.1f} MB")
        print(f"   End: {sam_end:.1f} MB")
        print(f"   Growth: {sam_growth:.1f} MB")
        
        if sam_growth < 50.0:  # Allow up to 50MB growth for model loading
            print("Success: SAM Model: PASSED")
            test_results['sam_model'] = True
        else:
            print("Error: SAM Model: FAILED - Excessive memory growth")
            
    except Exception as e:
        print(f"Error: SAM Model Test Error: {e}")
    
    # ===== TEST 3: YOLO MODEL MEMORY =====
    print("\n" + "="*50)
    print("YOLO: TEST 3: YOLO MODEL MEMORY")
    print("="*50)
    
    try:
        from models.yolo.yolo_model import YOLOModel
        
        yolo_start = get_memory_usage()
        yolo_model = YOLOModel()
        
        # Load model
        yolo_loaded = yolo_model.load_model()
        if yolo_loaded:
            print("Success: YOLO model loaded successfully")
            
            # Test predictions
            test_image = create_test_image()
            
            for detection_cycle in range(3):
                print(f"🔄 YOLO Detection Cycle {detection_cycle + 1}/3")
                
                # Multiple detections
                for det in range(10):
                    try:
                        result = yolo_model.detect_and_classify(test_image)
                        
                        if result.get('success'):
                            objects = len(result.get('results', []))
                            print(f"   Detection {det + 1}: {objects} objects")
                        else:
                            print(f"   Detection {det + 1}: Error - {result.get('error', 'Failed')}")
                        
                        # Cleanup after each detection
                        cleanup_system_memory()
                        
                    except Exception as e:
                        print(f"   Detection {det + 1}: Error - {e}")
                
                cycle_memory = get_memory_usage()
                print(f"   Memory after cycle: {cycle_memory:.1f} MB")
        
        # Cleanup YOLO model
        yolo_model.cleanup()
        del yolo_model
        cleanup_system_memory()
        
        yolo_end = get_memory_usage()
        yolo_growth = yolo_end - yolo_start
        
        print(f"\nMonitor: YOLO Model Results:")
        print(f"   Start: {yolo_start:.1f} MB")
        print(f"   End: {yolo_end:.1f} MB")
        print(f"   Growth: {yolo_growth:.1f} MB")
        
        if yolo_growth < 30.0:  # Allow up to 30MB growth for model loading
            print("Success: YOLO Model: PASSED")
            test_results['yolo_model'] = True
        else:
            print("Error: YOLO Model: FAILED - Excessive memory growth")
            
    except Exception as e:
        print(f"Error: YOLO Model Test Error: {e}")
    
    # ===== TEST 4: CORE ENGINE MEMORY =====
    print("\n" + "="*50)
    print("Engine: TEST 4: CORE ENGINE MEMORY")
    print("="*50)
    
    try:
        from src.core import SmartEngine
        
        engine_start = get_memory_usage()
        smart_engine = SmartEngine()
        
        # Test image analysis
        test_image = create_test_image()
        
        for analysis_cycle in range(10):
            print(f"🔄 Analysis Cycle {analysis_cycle + 1}/10")
            
            # Multiple analyses
            for analysis in range(5):
                try:
                    suggestions = smart_engine.analyze_image(test_image)
                    print(f"   Analysis {analysis + 1}: {len(suggestions) if suggestions else 0} suggestions")
                    
                except Exception as e:
                    print(f"   Analysis {analysis + 1}: Error - {e}")
            
            # Reset session periodically to clear any cached data
            if analysis_cycle % 3 == 0:
                smart_engine.reset_session()
                cleanup_system_memory()
            
            cycle_memory = get_memory_usage()
            print(f"   Memory after cycle: {cycle_memory:.1f} MB")
        
        # Final cleanup
        smart_engine.reset_session()
        del smart_engine
        cleanup_system_memory()
        
        engine_end = get_memory_usage()
        engine_growth = engine_end - engine_start
        
        print(f"\nMonitor: Core Engine Results:")
        print(f"   Start: {engine_start:.1f} MB")
        print(f"   End: {engine_end:.1f} MB")
        print(f"   Growth: {engine_growth:.1f} MB")
        
        if engine_growth < 10.0:  # Allow up to 10MB growth
            print("Success: Core Engine: PASSED")
            test_results['core_engine'] = True
        else:
            print("Error: Core Engine: FAILED - Excessive memory growth")
            
    except Exception as e:
        print(f"Error: Core Engine Test Error: {e}")
    
    # ===== OVERALL ANALYSIS =====
    final_memory = get_memory_usage()
    total_growth = final_memory - initial_memory
    
    print("\n" + "="*60)
    print("Monitor: OVERALL MEMORY ANALYSIS")
    print("="*60)
    
    print(f"🏁 Initial Memory: {initial_memory:.1f} MB")
    print(f"🏁 Final Memory: {final_memory:.1f} MB")
    print(f"📈 Total Growth: {total_growth:.1f} MB")
    
    if total_growth < 100.0:  # Allow up to 100MB total growth
        print("Success: Overall Memory: PASSED")
        test_results['overall_leak'] = True
    else:
        print("Error: Overall Memory: FAILED - Significant memory leak detected")
    
    # ===== FINAL RESULTS =====
    print("\n" + "="*60)
    print("🏆 COMPREHENSIVE MEMORY TEST RESULTS")
    print("="*60)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, passed in test_results.items():
        status = "Success: PASSED" if passed else "Error: FAILED"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nMonitor: Overall Score: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL MEMORY TESTS PASSED!")
        print("Success: No memory leaks detected")
        print("Success: All components are memory-optimized")
        print("Success: Smart Annotator is ready for production use")
        return True
    else:
        print(f"\nWarning:  {total_tests - passed_tests} test(s) failed")
        print("Error: Memory optimization needed")
        return False

if __name__ == "__main__":
    success = test_memory_leaks()
    sys.exit(0 if success else 1)
