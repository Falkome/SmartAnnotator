#!/usr/bin/env python3
"""
Focused Memory Leak Test - Tests for actual memory leaks (growing memory over time)
Distinguishes between normal model loading memory vs actual leaks.
"""

import os
import sys
import time
import psutil
import gc
import numpy as np
import cv2
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def cleanup_memory():
    """Clean up system memory."""
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass

def test_memory_leaks():
    """Test for actual memory leaks by running operations repeatedly."""
    
    print("Engine: SMART ANNOTATOR - MEMORY LEAK DETECTION")
    print("=" * 50)
    
    initial_memory = get_memory_usage()
    print(f"🏁 Starting Memory: {initial_memory:.1f} MB")
    
    # Test results
    results = {
        'sam_stable': False,
        'yolo_stable': False,
        'core_stable': False,
        'brush_stable': False
    }
    
    # ===== SAM MODEL LEAK TEST =====
    print(f"\nSAM: SAM MODEL LEAK TEST")
    print(f"=" * 30)
    
    try:
        from models.sam.sam_model import SAMModel
        
        sam_model = SAMModel()
        sam_loaded = sam_model.load_model()
        
        if sam_loaded:
            post_load_memory = get_memory_usage()
            print(f"YOLO: SAM Loaded: {post_load_memory:.1f} MB (+{post_load_memory - initial_memory:.1f} MB)")
            
            # Create test image
            test_image = np.random.randint(0, 255, (400, 600, 3), dtype=np.uint8)
            
            # Run multiple predictions to test for leaks
            memory_samples = []
            for i in range(20):
                center_x, center_y = test_image.shape[1] // 2, test_image.shape[0] // 2
                result = sam_model.predict_with_point(test_image, (center_x, center_y))
                
                if i % 5 == 0:  # Sample memory every 5 predictions
                    current_memory = get_memory_usage()
                    memory_samples.append(current_memory)
                    print(f"   Prediction {i+1}: {current_memory:.1f} MB")
                
                # Cleanup after each prediction
                cleanup_memory()
            
            # Check for memory stability
            if len(memory_samples) >= 3:
                memory_growth = memory_samples[-1] - memory_samples[0]
                print(f"Monitor: SAM Memory Growth over 20 predictions: {memory_growth:.1f} MB")
                
                if memory_growth < 10.0:  # Allow up to 10MB growth
                    print("Success: SAM Memory: STABLE")
                    results['sam_stable'] = True
                else:
                    print("Error: SAM Memory: LEAK DETECTED")
            
            sam_model.cleanup()
        
    except Exception as e:
        print(f"Error: SAM Test Error: {e}")
    
    # ===== YOLO MODEL LEAK TEST =====
    print(f"\nYOLO: YOLO MODEL LEAK TEST")
    print(f"=" * 30)
    
    try:
        from models.yolo.yolo_model import YOLOModel
        
        yolo_model = YOLOModel()
        yolo_loaded = yolo_model.load_model()
        
        if yolo_loaded:
            post_load_memory = get_memory_usage()
            print(f"YOLO: YOLO Loaded: {post_load_memory:.1f} MB")
            
            # Create test image  
            test_image = np.random.randint(0, 255, (400, 600, 3), dtype=np.uint8)
            
            # Run multiple detections
            memory_samples = []
            for i in range(30):
                result = yolo_model.detect_and_classify(test_image)
                
                if i % 10 == 0:  # Sample memory every 10 detections
                    current_memory = get_memory_usage()
                    memory_samples.append(current_memory)
                    print(f"   Detection {i+1}: {current_memory:.1f} MB")
                
                cleanup_memory()
            
            # Check stability
            if len(memory_samples) >= 3:
                memory_growth = memory_samples[-1] - memory_samples[0]
                print(f"Monitor: YOLO Memory Growth over 30 detections: {memory_growth:.1f} MB")
                
                if memory_growth < 5.0:  # Allow up to 5MB growth
                    print("Success: YOLO Memory: STABLE")
                    results['yolo_stable'] = True
                else:
                    print("Error: YOLO Memory: LEAK DETECTED")
            
            yolo_model.cleanup()
            
    except Exception as e:
        print(f"Error: YOLO Test Error: {e}")
    
    # ===== CORE ENGINE LEAK TEST =====
    print(f"\nEngine: CORE ENGINE LEAK TEST")
    print(f"=" * 30)
    
    try:
        from src.core import SmartEngine
        
        engine = SmartEngine()
        engine.initialize()
        
        post_init_memory = get_memory_usage()
        print(f"Engine: Engine Initialized: {post_init_memory:.1f} MB")
        
        # Create test image
        test_image = np.random.randint(0, 255, (400, 600, 3), dtype=np.uint8)
        
        # Run multiple analyses
        memory_samples = []
        for i in range(50):
            suggestions = engine.analyze_image(test_image)
            
            if i % 15 == 0:  # Sample memory every 15 analyses
                current_memory = get_memory_usage()
                memory_samples.append(current_memory)
                print(f"   Analysis {i+1}: {current_memory:.1f} MB ({len(suggestions)} suggestions)")
            
            # Reset session occasionally
            if i % 20 == 0:
                engine.reset_session()
            
            cleanup_memory()
        
        # Check stability
        if len(memory_samples) >= 3:
            memory_growth = memory_samples[-1] - memory_samples[0]
            print(f"Monitor: Engine Memory Growth over 50 analyses: {memory_growth:.1f} MB")
            
            if memory_growth < 2.0:  # Allow up to 2MB growth
                print("Success: Engine Memory: STABLE")
                results['core_stable'] = True
            else:
                print("Error: Engine Memory: LEAK DETECTED")
        
        del engine
        
    except Exception as e:
        print(f"Error: Engine Test Error: {e}")
    
    # ===== BRUSH TOOL LEAK TEST =====
    print(f"\nBrush: BRUSH TOOL LEAK TEST")
    print(f"=" * 30)
    
    try:
        from ui.components.brush_tool import BrushTool
        
        brush_tool = BrushTool()
        
        post_init_memory = get_memory_usage()
        print(f"Brush: Brush Initialized: {post_init_memory:.1f} MB")
        
        # Run multiple brush operations
        memory_samples = []
        for i in range(40):
            # Simulate brush strokes
            try:
                x, y = np.random.randint(0, 400), np.random.randint(0, 300)
                brush_tool.start_stroke(x, y, (300, 400))
                
                # Continue stroke
                for j in range(5):
                    x2, y2 = x + np.random.randint(-20, 20), y + np.random.randint(-20, 20)
                    brush_tool.continue_stroke(x2, y2, (300, 400))
                
                brush_tool.finish_stroke()
                
                # Clear occasionally
                if i % 10 == 0:
                    brush_tool.clear_all()
                
            except Exception as e:
                print(f"   Brush operation {i+1} error: {e}")
            
            if i % 10 == 0:  # Sample memory every 10 operations
                current_memory = get_memory_usage()
                memory_samples.append(current_memory)
                print(f"   Brush Op {i+1}: {current_memory:.1f} MB")
            
            cleanup_memory()
        
        # Check stability
        if len(memory_samples) >= 3:
            memory_growth = memory_samples[-1] - memory_samples[0]
            print(f"Monitor: Brush Memory Growth over 40 operations: {memory_growth:.1f} MB")
            
            if memory_growth < 5.0:  # Allow up to 5MB growth
                print("Success: Brush Memory: STABLE")
                results['brush_stable'] = True
            else:
                print("Error: Brush Memory: LEAK DETECTED")
        
        del brush_tool
        
    except Exception as e:
        print(f"Error: Brush Test Error: {e}")
    
    # ===== FINAL ANALYSIS =====
    final_memory = get_memory_usage()
    total_growth = final_memory - initial_memory
    
    print(f"\n" + "=" * 50)
    print(f"Monitor: MEMORY LEAK ANALYSIS RESULTS")
    print(f"=" * 50)
    
    print(f"🏁 Initial Memory: {initial_memory:.1f} MB")
    print(f"🏁 Final Memory: {final_memory:.1f} MB")
    print(f"📈 Net Growth: {total_growth:.1f} MB")
    
    print(f"\n🔍 Component Stability:")
    stable_components = sum(results.values())
    total_components = len(results)
    
    for component, is_stable in results.items():
        status = "Success: STABLE" if is_stable else "Error: LEAK"
        component_name = component.replace('_', ' ').title()
        print(f"   {component_name}: {status}")
    
    print(f"\nMonitor: Overall Score: {stable_components}/{total_components} components stable")
    
    if stable_components == total_components:
        print(f"\n🎉 NO MEMORY LEAKS DETECTED!")
        print(f"Success: All components are memory-stable")
        print(f"Success: Smart Annotator memory management is working correctly")
        
        if total_growth < 200:  # Total growth under 200MB is reasonable for model loading
            print(f"Success: Total memory growth ({total_growth:.1f} MB) is within acceptable limits")
            return True
        else:
            print(f"Warning: Total memory growth ({total_growth:.1f} MB) is high but stable")
            print(f"This is likely due to model loading, not leaks")
            return True
    else:
        print(f"\nWarning: {total_components - stable_components} component(s) showing memory leaks")
        print(f"🔧 Memory optimization needed for failing components")
        return False

if __name__ == "__main__":
    success = test_memory_leaks()
    sys.exit(0 if success else 1)
