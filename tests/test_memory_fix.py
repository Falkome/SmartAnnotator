#!/usr/bin/env python3
"""
Test script to validate memory leak fixes in DigitalSreeni Image Annotator
"""

import sys
import os
import gc
import time
import psutil

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import torch
    TORCH_AVAILABLE = True
    print("PyTorch available for GPU memory testing")
except ImportError:
    TORCH_AVAILABLE = False
    print("PyTorch not available - CPU memory testing only")

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def test_sam_utils_memory():
    """Test SAM utilities memory management"""
    print("\n=== Testing SAM Utils Memory Management ===")
    
    try:
        from digitalsreeni_image_annotator.sam_utils import SAMUtils
        
        initial_memory = get_memory_usage()
        print(f"Initial memory: {initial_memory:.1f} MB")
        
        # Create SAM utils instance
        sam_utils = SAMUtils()
        after_init_memory = get_memory_usage()
        print(f"After SAM init: {after_init_memory:.1f} MB")
        
        # Test model loading and cleanup
        print("Testing model loading...")
        sam_utils.change_sam_model("SAM 2 tiny")
        after_model_memory = get_memory_usage()
        print(f"After model load: {after_model_memory:.1f} MB")
        
        # Test cleanup
        print("Testing model cleanup...")
        sam_utils.cleanup_sam_model()
        after_cleanup_memory = get_memory_usage()
        print(f"After cleanup: {after_cleanup_memory:.1f} MB")
        
        # Force garbage collection
        gc.collect()
        if TORCH_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        final_memory = get_memory_usage()
        print(f"Final memory: {final_memory:.1f} MB")
        
        memory_diff = final_memory - initial_memory
        print(f"Memory difference: {memory_diff:+.1f} MB")
        
        if memory_diff < 50:  # Less than 50MB difference is acceptable
            print("Success: SAM Utils memory test PASSED")
            return True
        else:
            print("Error: SAM Utils memory test FAILED - significant memory leak detected")
            return False
            
    except Exception as e:
        print(f"Error: SAM Utils test failed with error: {e}")
        return False

def test_memory_cleanup_functions():
    """Test memory cleanup utility functions"""
    print("\n=== Testing Memory Cleanup Functions ===")
    
    try:
        # Test basic memory monitoring
        initial_memory = get_memory_usage()
        print(f"Initial memory: {initial_memory:.1f} MB")
        
        # Create some memory load
        large_arrays = []
        for i in range(10):
            import numpy as np
            large_arrays.append(np.random.rand(1000, 1000))
        
        peak_memory = get_memory_usage()
        print(f"Peak memory: {peak_memory:.1f} MB")
        
        # Cleanup
        del large_arrays
        gc.collect()
        
        if TORCH_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        final_memory = get_memory_usage()
        print(f"Final memory: {final_memory:.1f} MB")
        
        memory_recovered = peak_memory - final_memory
        print(f"Memory recovered: {memory_recovered:.1f} MB")
        
        if memory_recovered > 50:  # Should recover at least 50MB
            print("Success: Memory cleanup test PASSED")
            return True
        else:
            print("Error: Memory cleanup test FAILED - insufficient memory recovery")
            return False
            
    except Exception as e:
        print(f"Error: Memory cleanup test failed with error: {e}")
        return False

def test_requirements():
    """Test that all required dependencies are available"""
    print("\n=== Testing Requirements ===")
    
    required_modules = [
        'PyQt5',
        'numpy',
        'cv2',
        'PIL',
        'psutil'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"Success: {module} - Available")
        except ImportError:
            print(f"Error: {module} - Missing")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\nError: Missing required modules: {', '.join(missing_modules)}")
        print("Please install missing dependencies:")
        print("pip install -r requirements.txt")
        return False
    else:
        print("\nSuccess: All required modules available")
        return True

def main():
    """Run all memory tests"""
    print("DigitalSreeni Image Annotator - Memory Fix Validation")
    print("=" * 55)
    
    # Test requirements first
    if not test_requirements():
        print("\nError: Requirements test failed - cannot proceed")
        return False
    
    # Run memory tests
    tests_passed = 0
    total_tests = 2
    
    if test_memory_cleanup_functions():
        tests_passed += 1
    
    if test_sam_utils_memory():
        tests_passed += 1
    
    # Summary
    print(f"\n=== Test Summary ===")
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All memory tests PASSED!")
        print("\nMemory leak fixes are working correctly.")
        print("The application should now handle memory more efficiently during annotation.")
        return True
    else:
        print("Warning:  Some memory tests FAILED!")
        print("There may still be memory issues that need attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
