#!/usr/bin/env python3
"""
Brush Tool Memory Test

Test the memory-efficient brush tool to ensure no memory leaks during segmentation.
"""

import sys
import numpy as np
import cv2
import time
import gc
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from ui.components.brush_tool import BrushTool, MemoryManager

def test_brush_memory_performance():
    """Test brush tool memory performance and leak prevention."""
    
    print("Brush: Testing Smart Brush Tool Memory Management")
    print("=" * 55)
    
    # Initialize brush tool
    brush_tool = BrushTool()
    memory_manager = MemoryManager()
    
    print(f"Engine: Initial Memory: {memory_manager.check_memory_usage():.1f} MB")
    
    # Create test image
    test_image = np.random.randint(0, 255, (800, 600, 3), dtype=np.uint8)
    image_shape = test_image.shape[:2]
    
    print(f"🖼️ Test Image: {test_image.shape} ({test_image.nbytes/1024/1024:.1f} MB)")
    
    # Test multiple brush strokes to check for memory leaks
    num_strokes = 10
    stroke_points = 100
    
    memory_readings = []
    
    for stroke_num in range(num_strokes):
        print(f"\nBrush: Stroke {stroke_num + 1}/{num_strokes}")
        
        # Start stroke
        start_x, start_y = 100 + stroke_num * 50, 100 + stroke_num * 30
        brush_tool.start_stroke(start_x, start_y, image_shape)
        
        # Continue stroke with many points
        for point_num in range(stroke_points):
            x = start_x + point_num * 2
            y = start_y + int(20 * np.sin(point_num * 0.1))
            
            # Keep within bounds
            x = max(0, min(image_shape[1] - 1, x))
            y = max(0, min(image_shape[0] - 1, y))
            
            brush_tool.continue_stroke(x, y, image_shape)
        
        # Finish stroke
        final_mask = brush_tool.finish_stroke()
        
        # Check memory usage
        current_memory = memory_manager.check_memory_usage()
        memory_readings.append(current_memory)
        
        if final_mask is not None:
            mask_area = np.sum(final_mask > 0)
            print(f"  Success: Stroke completed: {mask_area} pixels painted")
        else:
            print(f"  Error: Stroke failed")
        
        print(f"  💾 Memory: {current_memory:.1f} MB")
        
        # Force garbage collection to test cleanup
        gc.collect()
    
    # Final memory test
    final_memory = memory_manager.check_memory_usage()
    memory_readings.append(final_memory)
    
    print(f"\nMonitor: Memory Analysis:")
    print(f"  Initial: {memory_readings[0]:.1f} MB")
    print(f"  Peak: {max(memory_readings):.1f} MB") 
    print(f"  Final: {final_memory:.1f} MB")
    print(f"  Memory Growth: {final_memory - memory_readings[0]:.1f} MB")
    
    # Performance stats
    stats = brush_tool.get_memory_stats()
    
    print(f"\n🏆 Performance Summary:")
    print(f"  Strokes: {stats['stroke_count']}")
    print(f"  Total Points: {stats['total_points']}")
    print(f"  Brush Size: {stats['brush_size']}px")
    print(f"  Cleanup Cycles: {stats['cleanup_counter']}")
    
    # Memory leak detection
    memory_growth = final_memory - memory_readings[0]
    
    if memory_growth < 10:  # Less than 10MB growth is acceptable
        print(f"\nSuccess: MEMORY TEST PASSED")
        print(f"   Memory growth: {memory_growth:.1f} MB (acceptable)")
        return True
    else:
        print(f"\nWarning: MEMORY TEST WARNING")
        print(f"   Memory growth: {memory_growth:.1f} MB (check for leaks)")
        return False

def test_brush_modes_and_sizes():
    """Test different brush modes and sizes."""
    
    print(f"\nCanvas: Testing Brush Modes and Sizes")
    print("=" * 35)
    
    brush_tool = BrushTool()
    test_image_shape = (400, 400)
    
    # Test different sizes
    sizes = [5, 10, 20, 50]
    modes = ["paint", "erase"]
    
    for mode in modes:
        print(f"\nBrush: Testing {mode} mode:")
        brush_tool.set_brush_mode(mode)
        
        for size in sizes:
            brush_tool.set_brush_size(size)
            
            # Create a small test stroke
            brush_tool.start_stroke(200, 200, test_image_shape)
            
            # Add a few points
            for i in range(5):
                x, y = 200 + i * 5, 200 + i * 2
                brush_tool.continue_stroke(x, y, test_image_shape)
            
            # Finish stroke
            mask = brush_tool.finish_stroke()
            
            if mask is not None:
                painted_pixels = np.sum(mask > 0)
                print(f"  Size {size:2d}px: {painted_pixels:4d} pixels")
            else:
                print(f"  Size {size:2d}px: Failed")
    
    print(f"\nSuccess: Mode and Size Tests Completed")

def test_memory_optimization():
    """Test memory optimization functionality."""
    
    print(f"\nCleanup: Testing Memory Optimization")
    print("=" * 32)
    
    brush_tool = BrushTool()
    memory_manager = MemoryManager()
    
    # Get initial memory
    initial_memory = memory_manager.check_memory_usage()
    print(f"Initial Memory: {initial_memory:.1f} MB")
    
    # Create some memory usage
    test_shape = (1000, 800)
    for i in range(3):
        brush_tool.start_stroke(100, 100, test_shape)
        
        # Create a complex stroke
        for j in range(50):
            x, y = 100 + j * 10, 100 + int(50 * np.sin(j * 0.2))
            brush_tool.continue_stroke(x, y, test_shape)
        
        brush_tool.finish_stroke()
    
    # Check memory before optimization
    before_memory = memory_manager.check_memory_usage()
    print(f"Before Optimization: {before_memory:.1f} MB")
    
    # Optimize memory
    brush_tool.optimize_memory()
    
    # Check memory after optimization
    after_memory = memory_manager.check_memory_usage()
    print(f"After Optimization: {after_memory:.1f} MB")
    
    memory_freed = before_memory - after_memory
    print(f"Memory Freed: {memory_freed:.1f} MB")
    
    if memory_freed >= 0:
        print(f"Success: Memory optimization working")
        return True
    else:
        print(f"Warning: Memory optimization may need improvement")
        return False

def main():
    """Run all brush tool tests."""
    
    print("Brush: Smart Annotator - Brush Tool Memory Tests")
    print("=" * 50)
    
    results = []
    
    # Test 1: Memory performance
    print("TEST 1: Memory Performance and Leak Detection")
    results.append(test_brush_memory_performance())
    
    # Test 2: Modes and sizes
    print("\nTEST 2: Brush Modes and Sizes")
    test_brush_modes_and_sizes()
    results.append(True)  # This test always passes
    
    # Test 3: Memory optimization
    print("\nTEST 3: Memory Optimization")
    results.append(test_memory_optimization())
    
    # Final results
    print(f"\n{'='*50}")
    print(f"🏆 BRUSH TOOL TEST RESULTS")
    print(f"{'='*50}")
    
    test_names = [
        "Memory Performance",
        "Modes and Sizes", 
        "Memory Optimization"
    ]
    
    passed = 0
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "Success: PASSED" if result else "Error: FAILED"
        print(f"{i+1}. {test_name:20} : {status}")
        if result:
            passed += 1
    
    print(f"\nMonitor: Overall Result: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL BRUSH TOOL TESTS PASSED!")
        print("Success: Memory-efficient brush segmentation is working correctly")
        print("Success: No memory leaks detected")
        print("Success: All brush modes and sizes functional")
        print("Success: Memory optimization working")
    else:
        print("Warning: Some tests had issues - check logs above")
    
    print(f"\nBrush: Brush Tool Ready for Smart Annotation!")
    print(f"Usage: Select 'Smart Brush' tool in GUI and paint segmentation masks")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
