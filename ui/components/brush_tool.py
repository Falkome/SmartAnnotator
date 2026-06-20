#!/usr/bin/env python3
"""
Brush Tool - Memory-Efficient Brush Segmentation

Smart brush tool with memory management for annotation without memory leaks.
"""

import numpy as np
import cv2
import gc
import logging
from typing import Dict, List, Any, Tuple, Optional
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor

logger = logging.getLogger(__name__)

# Memory management
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class MemoryManager:
    """Smart memory management for brush operations."""
    
    def __init__(self):
        self.memory_threshold = 1024 * 1024 * 1024  # 1GB threshold
        self.cleanup_counter = 0
        self.cleanup_frequency = 10  # Clean every 10 operations
        
    def check_memory_usage(self) -> float:
        """Check current memory usage in MB."""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                return process.memory_info().rss / 1024 / 1024
            except:
                return 0.0
        return 0.0
    
    def cleanup_memory(self):
        """Perform memory cleanup."""
        try:
            # Python garbage collection
            gc.collect()
            
            # PyTorch GPU cache cleanup
            if TORCH_AVAILABLE and torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.debug("Cleanup: Memory cleanup performed")
        except Exception as e:
            logger.error(f"Memory cleanup error: {e}")
    
    def smart_cleanup(self):
        """Smart cleanup based on counter and memory usage."""
        self.cleanup_counter += 1
        
        if self.cleanup_counter >= self.cleanup_frequency:
            memory_mb = self.check_memory_usage()
            
            if memory_mb > 500:  # If using more than 500MB
                self.cleanup_memory()
            
            self.cleanup_counter = 0


class BrushTool:
    """Memory-efficient brush tool for annotation."""
    
    def __init__(self):
        self.brush_size = 10
        self.brush_strength = 1.0
        self.brush_mode = "paint"  # "paint" or "erase"
        
        # Memory management
        self.memory_manager = MemoryManager()
        
        # Brush state
        self.current_stroke = []
        self.brush_mask = None
        self.last_position = None
        
        # Performance tracking
        self.stroke_count = 0
        self.total_points = 0
        
        logger.info("Brush: Brush Tool initialized with memory management")
    
    def create_brush_kernel(self, size: int) -> np.ndarray:
        """Create circular brush kernel."""
        try:
            # Create circular kernel for brush
            kernel_size = max(3, size * 2 + 1)
            center = kernel_size // 2
            
            # Use smaller data type to save memory
            kernel = np.zeros((kernel_size, kernel_size), dtype=np.uint8)
            
            # Draw circle
            cv2.circle(kernel, (center, center), size, 255, -1)
            
            return kernel
            
        except Exception as e:
            logger.error(f"Error creating brush kernel: {e}")
            # Fallback to simple kernel
            return np.ones((3, 3), dtype=np.uint8) * 255
    
    def start_stroke(self, x: int, y: int, image_shape: Tuple[int, int]):
        """Start a new brush stroke."""
        try:
            h, w = image_shape
            
            # Initialize brush mask with minimal memory
            self.brush_mask = np.zeros((h, w), dtype=np.uint8)
            self.current_stroke = [(x, y)]
            self.last_position = (x, y)
            
            # Apply first brush point
            self._apply_brush_point(x, y, h, w)
            
            logger.debug(f"Brush: Started brush stroke at ({x}, {y})")
            
        except Exception as e:
            logger.error(f"Error starting brush stroke: {e}")
    
    def continue_stroke(self, x: int, y: int, image_shape: Tuple[int, int]):
        """Continue brush stroke with interpolation."""
        try:
            if self.brush_mask is None:
                self.start_stroke(x, y, image_shape)
                return
            
            h, w = image_shape
            
            # Interpolate between last position and current
            if self.last_position:
                points = self._interpolate_line(self.last_position, (x, y))
                
                # Apply brush to all interpolated points
                for point_x, point_y in points:
                    self._apply_brush_point(point_x, point_y, h, w)
                    self.current_stroke.append((point_x, point_y))
                    self.total_points += 1
            else:
                self._apply_brush_point(x, y, h, w)
                self.current_stroke.append((x, y))
                self.total_points += 1
            
            self.last_position = (x, y)
            
            # Smart memory management
            self.memory_manager.smart_cleanup()
            
        except Exception as e:
            logger.error(f"Error continuing brush stroke: {e}")
    
    def _apply_brush_point(self, x: int, y: int, img_height: int, img_width: int):
        """Apply brush at specific point with memory efficiency."""
        try:
            # Get brush kernel
            kernel = self.create_brush_kernel(self.brush_size)
            kernel_h, kernel_w = kernel.shape
            
            # Calculate bounds to avoid out-of-bounds access
            half_h, half_w = kernel_h // 2, kernel_w // 2
            
            y_start = max(0, y - half_h)
            y_end = min(img_height, y + half_h + 1)
            x_start = max(0, x - half_w)
            x_end = min(img_width, x + half_w + 1)
            
            # Calculate kernel crop bounds
            ky_start = max(0, half_h - y)
            ky_end = kernel_h - max(0, (y + half_h + 1) - img_height)
            kx_start = max(0, half_w - x)
            kx_end = kernel_w - max(0, (x + half_w + 1) - img_width)
            
            # Apply brush with memory-efficient operations
            if self.brush_mode == "paint":
                # Paint mode - add to mask
                mask_region = self.brush_mask[y_start:y_end, x_start:x_end]
                kernel_region = kernel[ky_start:ky_end, kx_start:kx_end]
                
                # Use maximum to overlay brush strokes
                np.maximum(mask_region, kernel_region, out=mask_region)
                
            elif self.brush_mode == "erase":
                # Erase mode - subtract from mask
                mask_region = self.brush_mask[y_start:y_end, x_start:x_end]
                kernel_region = kernel[ky_start:ky_end, kx_start:kx_end]
                
                # Erase by setting to zero where kernel is active
                mask_region[kernel_region > 0] = 0
            
        except Exception as e:
            logger.error(f"Error applying brush point: {e}")
    
    def _interpolate_line(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Interpolate points between start and end for smooth strokes."""
        try:
            x1, y1 = start
            x2, y2 = end
            
            # Calculate distance
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            distance = max(dx, dy)
            
            # If distance is small, return just the endpoints
            if distance <= 1:
                return [end]
            
            # Interpolate points
            points = []
            for i in range(distance + 1):
                t = i / distance
                x = int(x1 + t * (x2 - x1))
                y = int(y1 + t * (y2 - y1))
                points.append((x, y))
            
            return points
            
        except Exception as e:
            logger.error(f"Error interpolating line: {e}")
            return [end]
    
    def finish_stroke(self) -> Optional[np.ndarray]:
        """Finish current stroke and return the mask."""
        try:
            if self.brush_mask is None:
                return None
            
            # Copy the mask before cleanup
            final_mask = self.brush_mask.copy()
            
            # Clean up stroke data
            self.current_stroke.clear()
            self.brush_mask = None
            self.last_position = None
            self.stroke_count += 1
            
            # Memory cleanup
            self.memory_manager.cleanup_memory()
            
            logger.info(f"Brush: Finished brush stroke with {len(self.current_stroke)} points")
            
            return final_mask
            
        except Exception as e:
            logger.error(f"Error finishing brush stroke: {e}")
            return None
    
    def cancel_stroke(self):
        """Cancel current stroke and cleanup memory."""
        try:
            # Clear all stroke data
            self.current_stroke.clear()
            self.brush_mask = None
            self.last_position = None
            
            # Memory cleanup
            self.memory_manager.cleanup_memory()
            
            logger.info("Brush: Brush stroke cancelled")
            
        except Exception as e:
            logger.error(f"Error cancelling brush stroke: {e}")
    
    def set_brush_size(self, size: int):
        """Set brush size with validation."""
        self.brush_size = max(1, min(100, size))  # Limit size to prevent memory issues
        logger.debug(f"Brush: Brush size set to: {self.brush_size}")
    
    def set_brush_mode(self, mode: str):
        """Set brush mode (paint/erase)."""
        if mode in ["paint", "erase"]:
            self.brush_mode = mode
            logger.debug(f"Brush: Brush mode set to: {mode}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        return {
            'current_memory_mb': self.memory_manager.check_memory_usage(),
            'stroke_count': self.stroke_count,
            'total_points': self.total_points,
            'cleanup_counter': self.memory_manager.cleanup_counter,
            'brush_size': self.brush_size,
            'brush_mode': self.brush_mode
        }
    
    def optimize_memory(self):
        """Force memory optimization."""
        try:
            # Cancel any active stroke
            if self.brush_mask is not None:
                self.cancel_stroke()
            
            # Force cleanup
            self.memory_manager.cleanup_memory()
            
            # Reset counters
            self.memory_manager.cleanup_counter = 0
            
            logger.info("Cleanup: Brush tool memory optimized")
            
        except Exception as e:
            logger.error(f"Error optimizing memory: {e}")
    
    def get_performance_summary(self) -> str:
        """Get performance summary."""
        stats = self.get_memory_stats()
        
        summary = f"""Brush: Brush Tool Performance:
Monitor: Strokes completed: {stats['stroke_count']}
📍 Total points: {stats['total_points']}
💾 Current memory: {stats['current_memory_mb']:.1f} MB
🔧 Brush size: {stats['brush_size']}px
Canvas: Mode: {stats['brush_mode']}
Cleanup: Memory cleanups: {stats['cleanup_counter']}"""
        
        return summary
