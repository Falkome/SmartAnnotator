#!/usr/bin/env python3
"""
Smart Canvas - Interactive Image Annotation Canvas

Enhanced canvas with smart features for AI-powered annotation interactions.
"""

import numpy as np
import cv2
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QFont, QCursor

# Import brush tool for memory-efficient brush segmentation
from .brush_tool import BrushTool

logger = logging.getLogger(__name__)


class SmartCanvas(QLabel):
    """Smart interactive canvas for image annotation."""
    
    # Signals for communication with main application
    annotation_created = pyqtSignal(dict)
    point_clicked = pyqtSignal(int, int)
    bbox_drawn = pyqtSignal(int, int, int, int)
    auto_segment_requested = pyqtSignal()
    tool_feedback = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Canvas setup
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QLabel {
                border: 3px solid #3498db;
                border-radius: 12px;
                background-color: #f8f9fa;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(False)
        self.setMouseTracking(True)
        
        # Image state
        self.original_image = None
        self.display_image = None
        self.current_image_path = None
        self.scale_factor = 1.0
        
        # Annotation state
        self.annotations = []
        self.temp_annotations = []
        self.current_tool = "magic_wand"
        
        # Interaction state
        self.drawing_bbox = False
        self.bbox_start = None
        self.current_bbox = None
        self.mouse_position = (0, 0)
        
        # Manual annotation state
        self.drawing_polygon = False
        self.current_polygon = []
        self.drawing_rectangle = False
        self.rectangle_start = None
        self.current_rectangle = None
        
        # Brush tool state
        self.brush_tool = BrushTool()
        self.drawing_brush = False
        self.brush_mask = None
        
        # Smart features
        self.show_smart_hints = True
        self.smart_suggestions = []
        self.detected_objects = []
        
        # Label management
        self.label_manager = None
        self.current_class_id = 0
        
        # Performance optimization
        from src.performance_monitor import PerformanceMonitor, OptimizedUpdateManager
        self.performance_monitor = PerformanceMonitor()
        self.update_manager = OptimizedUpdateManager(self.performance_monitor)
        
        # Cached rendering
        self.cached_base_image = None
        self.cached_annotations_image = None
        self.annotations_hash = None
        self.enable_caching = True
        
        # Visual settings
        self.colors = {
            'annotation': QColor(0, 255, 0, 180),     # Green for annotations
            'temp_annotation': QColor(255, 165, 0, 150),  # Orange for temp
            'bbox_drawing': QColor(255, 0, 255, 200),  # Magenta for drawing
            'smart_hint': QColor(255, 255, 0, 100),   # Yellow for hints
            'detected_object': QColor(0, 255, 255, 120),  # Cyan for detected
            'polygon_drawing': QColor(255, 100, 100, 200), # Red for polygon
            'rectangle_drawing': QColor(100, 100, 255, 200), # Blue for rectangle
            'manual_annotation': QColor(128, 255, 128, 160)  # Light green for manual
        }
        
        # Performance tracking
        self.interaction_stats = {
            'clicks': 0,
            'annotations_created': 0,
            'processing_time': 0.0
        }
        
        logger.info("Canvas: Smart Canvas initialized")
    
    def load_image(self, image_path: str) -> bool:
        """Load image into canvas."""
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return False
            
            # Convert to RGB
            self.original_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self.current_image_path = image_path
            
            # Clear previous annotations
            self.annotations.clear()
            self.temp_annotations.clear()
            self.smart_suggestions.clear()
            self.detected_objects.clear()
            
            # Update display
            self.update_display()
            
            # Show feedback
            self.tool_feedback.emit(f"📷 Image loaded: {Path(image_path).name} ({self.original_image.shape[1]}x{self.original_image.shape[0]})")
            
            logger.info(f"Image loaded: {image_path} {self.original_image.shape}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return False
    
    def update_display(self, priority: str = 'normal'):
        """Optimized canvas display update with performance monitoring."""
        
        if self.original_image is None:
            self.setText("Canvas: Smart Canvas\n\nLoad an image to start annotating")
            self.setStyleSheet(self.styleSheet() + "font-size: 16px; color: #7f8c8d;")
            return
        
        # Check if update should be skipped for performance
        if priority != 'high' and not self.update_manager.should_update_now():
            return
        
        # Start performance timing
        start_time = self.performance_monitor.start_update_timing()
        
        try:
            # Use cached rendering when possible
            display_img = self._get_optimized_display_image()
            
            # Convert to QPixmap and display
            self.display_numpy_image(display_img)
            
            # Mark update as completed
            self.update_manager.mark_update_completed()
            
        except Exception as e:
            logger.error(f"Error: Display update error: {e}")
        finally:
            # End performance timing
            self.performance_monitor.end_update_timing(start_time, len(self.annotations))
    
    def _get_optimized_display_image(self):
        """Get display image using caching and optimization."""
        
        # Calculate hash for cache invalidation
        current_hash = self._calculate_annotations_hash()
        
        # Check if we can use cached base image with annotations
        if (self.enable_caching and 
            self.cached_annotations_image is not None and 
            self.annotations_hash == current_hash):
            
            # Use cached base, only add interactive elements
            display_img = self.cached_annotations_image.copy()
            
            # Only draw dynamic elements
            self.draw_current_interaction(display_img)
            
            return display_img
        
        # Full render needed
        return self._full_render_display_image(current_hash)
    
    def _full_render_display_image(self, annotations_hash: str):
        """Perform full render and update cache."""
        
        # Create base display image
        display_img = self.original_image.copy()
        
        # Draw static elements
        self.draw_detected_objects(display_img)
        self.draw_annotations(display_img)
        self.draw_temp_annotations(display_img)
        
        # Cache the base image with annotations
        if self.enable_caching:
            self.cached_annotations_image = display_img.copy()
            self.annotations_hash = annotations_hash
        
        # Draw dynamic elements
        self.draw_current_interaction(display_img)
        
        # Draw smart hints
        if self.show_smart_hints:
            self.draw_smart_hints(display_img)
        
        return display_img
    
    def _calculate_annotations_hash(self) -> str:
        """Calculate hash for annotation state to detect changes."""
        
        # Simple hash based on annotation count and types
        hash_components = [
            len(self.annotations),
            len(self.temp_annotations), 
            len(self.detected_objects),
            str([ann.get('type', 'unknown') for ann in self.annotations]),
        ]
        
        return str(hash(tuple(str(c) for c in hash_components)))
    
    def invalidate_cache(self):
        """Invalidate cached images to force full redraw."""
        
        self.cached_base_image = None
        self.cached_annotations_image = None
        self.annotations_hash = None
    
    def update_display_interactive(self):
        """Fast update for interactive elements only (mouse movements)."""
        
        if self.original_image is None:
            return
        
        # Skip if we've updated very recently
        if not self.update_manager.should_update_now():
            return
        
        # Use cached base if available
        if self.cached_annotations_image is not None:
            display_img = self.cached_annotations_image.copy()
            
            # Only draw interactive elements
            self.draw_current_interaction(display_img)
            
            # Quick display update
            self.display_numpy_image(display_img)
        else:
            # Fall back to full update
            self.update_display('high')
    
    def draw_detected_objects(self, image: np.ndarray):
        """Draw detected objects with smart highlighting."""
        
        for obj in self.detected_objects:
            if 'bbox' in obj:
                x1, y1, x2, y2 = obj['bbox']
                confidence = obj.get('confidence', 0.5)
                class_name = obj.get('class_name', 'object')
                
                # Draw bounding box
                color = (0, 255, 255) if confidence > 0.7 else (255, 255, 0)  # Cyan or yellow
                thickness = 2 if confidence > 0.7 else 1
                cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)
                
                # Draw label
                label = f"{class_name} {confidence:.2f}"
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                cv2.rectangle(image, (int(x1), int(y1) - label_size[1] - 10), 
                            (int(x1) + label_size[0] + 10, int(y1)), color, -1)
                cv2.putText(image, label, (int(x1) + 5, int(y1) - 5), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    
    def draw_annotations(self, image: np.ndarray):
        """Draw permanent annotations."""
        
        for annotation in self.annotations:
            if annotation['type'] == 'segmentation' and 'mask' in annotation:
                self.draw_segmentation_mask(image, annotation['mask'], self.colors['annotation'])
            elif annotation['type'] == 'bbox' and 'bbox' in annotation:
                self.draw_bounding_box(image, annotation['bbox'], self.colors['annotation'])
    
    def draw_temp_annotations(self, image: np.ndarray):
        """Draw temporary annotations."""
        
        for annotation in self.temp_annotations:
            if annotation['type'] == 'segmentation' and 'mask' in annotation:
                self.draw_segmentation_mask(image, annotation['mask'], self.colors['temp_annotation'])
    
    def draw_current_interaction(self, image: np.ndarray):
        """Draw current interaction state (e.g., bbox being drawn, brush strokes)."""
        
        if self.drawing_bbox and self.current_bbox:
            x1, y1, x2, y2 = self.current_bbox
            cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 255), 3)  # Magenta
            
            # Show size info
            width, height = x2 - x1, y2 - y1
            size_text = f"{width}x{height}"
            cv2.putText(image, size_text, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
        
        # Draw brush stroke in progress
        if self.drawing_brush and self.brush_tool.brush_mask is not None:
            self._draw_brush_overlay(image)
    
    def draw_smart_hints(self, image: np.ndarray):
        """Draw smart hints and suggestions."""
        
        # Draw cursor position indicator
        if hasattr(self, 'mouse_position'):
            x, y = self.mouse_position
            if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
                cv2.circle(image, (int(x), int(y)), 8, (255, 255, 0), 2)  # Yellow circle
                
                # Tool indicator
                tool_indicators = {
                    'magic_wand': '🎯',
                    'bbox': '📦',
                    'auto': '🔄'
                }
                indicator = tool_indicators.get(self.current_tool, '🔧')
                # Note: cv2.putText doesn't support emojis, so we use simple text
                tool_text = f"{self.current_tool.upper()}"
                cv2.putText(image, tool_text, (int(x) + 15, int(y)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
    
    def draw_segmentation_mask(self, image: np.ndarray, mask: np.ndarray, color: QColor):
        """Draw segmentation mask overlay with proper alpha blending."""
        
        try:
            # Convert QColor to RGB tuple
            rgb_color = (color.red(), color.green(), color.blue())
            alpha = color.alpha() / 255.0
            
            # Create overlay without modifying original
            overlay = np.zeros_like(image, dtype=np.uint8)
            overlay[mask > 0.5] = rgb_color
            
            # Blend properly without darkening the original image
            mask_area = mask > 0.5
            image[mask_area] = (1 - alpha) * image[mask_area] + alpha * overlay[mask_area]
            
            # Draw contours for better visibility
            mask_uint8 = (mask > 0.5).astype(np.uint8) * 255
            contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(image, contours, -1, rgb_color, 2)
            
        except Exception as e:
            logger.error(f"Error drawing segmentation mask: {e}")
    
    def draw_bounding_box(self, image: np.ndarray, bbox: Tuple[int, int, int, int], color: QColor):
        """Draw bounding box."""
        
        x1, y1, x2, y2 = bbox
        rgb_color = (color.red(), color.green(), color.blue())
        cv2.rectangle(image, (x1, y1), (x2, y2), rgb_color, 3)
    
    def display_numpy_image(self, image: np.ndarray):
        """Convert numpy image to QPixmap and display."""
        
        try:
            height, width, channels = image.shape
            bytes_per_line = channels * width
            
            # Create QImage
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # Scale to fit widget while maintaining aspect ratio
            widget_size = self.size()
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(widget_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Calculate scale factor for coordinate conversion
            self.scale_factor = min(widget_size.width() / width, widget_size.height() / height)
            
            self.setPixmap(scaled_pixmap)
            
        except Exception as e:
            logger.error(f"Error displaying image: {e}")
    
    def _draw_brush_overlay(self, image: np.ndarray):
        """Draw brush stroke overlay with proper alpha blending."""
        try:
            if self.brush_tool.brush_mask is not None:
                mask = self.brush_tool.brush_mask
                
                # Choose brush color (blue for paint, red for erase)
                if self.brush_tool.brush_mode == "paint":
                    brush_color = (100, 150, 255)  # Light blue
                else:
                    brush_color = (255, 100, 100)  # Light red
                
                # Create overlay for brush
                overlay = np.zeros_like(image, dtype=np.uint8)
                overlay[mask > 0] = brush_color
                
                # Apply alpha blending only to brush area
                alpha = 0.4
                brush_area = mask > 0
                image[brush_area] = (1 - alpha) * image[brush_area] + alpha * overlay[brush_area]
                
                # Draw brush outline for better visibility
                mask_uint8 = (mask > 0).astype(np.uint8) * 255
                contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(image, contours, -1, (0, 255, 255), 2)  # Cyan outline
                
        except Exception as e:
            logger.error(f"Error drawing brush overlay: {e}")
    
    def set_brush_size(self, size: int):
        """Set brush tool size with memory management."""
        self.brush_tool.set_brush_size(size)
        self.tool_feedback.emit(f"Brush: Brush size: {size}px")
    
    def set_brush_mode(self, mode: str):
        """Set brush mode (paint/erase)."""
        self.brush_tool.set_brush_mode(mode)
        mode_text = "Canvas: Paint" if mode == "paint" else "🗑️ Erase" 
        self.tool_feedback.emit(f"Brush: Brush mode: {mode_text}")
    
    def get_brush_memory_stats(self) -> Dict[str, Any]:
        """Get brush tool memory statistics."""
        return self.brush_tool.get_memory_stats()
    
    def optimize_brush_memory(self):
        """Optimize brush tool memory usage."""
        self.brush_tool.optimize_memory()
        self.tool_feedback.emit("Cleanup: Brush memory optimized")
    
    # Note: set_tool method is defined later at line ~791 to avoid duplicate definition
    
    def add_annotation(self, annotation: Dict[str, Any]):
        """Add permanent annotation."""
        
        annotation['timestamp'] = time.time()
        self.annotations.append(annotation)
        self.interaction_stats['annotations_created'] += 1
        
        # Emit signal
        self.annotation_created.emit(annotation)
        
        # Update display
        self.update_display()
        
        logger.info(f"Annotation added: {annotation['type']}")
    
    def add_temp_annotation(self, annotation: Dict[str, Any]):
        """Add temporary annotation (for preview)."""
        
        self.temp_annotations.clear()  # Clear previous temp annotations
        self.temp_annotations.append(annotation)
        
        # Invalidate cache since temp annotations changed
        self.invalidate_cache()
        
        # High priority update for SAM preview
        self.update_display('high')
    
    def confirm_temp_annotations(self):
        """Convert temporary annotations to permanent ones."""
        
        for temp_annotation in self.temp_annotations:
            self.add_annotation(temp_annotation)
        
        self.temp_annotations.clear()
        
        # Invalidate cache since annotations changed  
        self.invalidate_cache()
        
        # High priority update after confirming
        self.update_display('high')
    
    def clear_temp_annotations(self):
        """Clear temporary annotations."""
        
        self.temp_annotations.clear()
        
        # Invalidate cache since temp annotations changed
        self.invalidate_cache()
        
        # High priority update for clearing
        self.update_display('high')
    
    def set_detected_objects(self, objects: List[Dict[str, Any]]):
        """Set detected objects for display."""
        
        self.detected_objects = objects
        self.update_display()
        
        logger.info(f"Set {len(objects)} detected objects")
    
    def widget_to_image_coords(self, widget_x: int, widget_y: int) -> Optional[Tuple[int, int]]:
        """Convert widget coordinates to image coordinates."""
        
        if self.original_image is None or self.scale_factor == 0:
            return None
        
        try:
            # Get pixmap rectangle
            pixmap = self.pixmap()
            if not pixmap:
                return None
            
            widget_rect = self.rect()
            pixmap_rect = pixmap.rect()
            
            # Calculate offset (image is centered in widget)
            x_offset = (widget_rect.width() - pixmap_rect.width()) // 2
            y_offset = (widget_rect.height() - pixmap_rect.height()) // 2
            
            # Adjust for centering
            adjusted_x = widget_x - x_offset
            adjusted_y = widget_y - y_offset
            
            # Check bounds
            if (0 <= adjusted_x <= pixmap_rect.width() and 
                0 <= adjusted_y <= pixmap_rect.height()):
                
                # Convert to image coordinates
                image_x = int(adjusted_x / self.scale_factor)
                image_y = int(adjusted_y / self.scale_factor)
                
                # Clamp to image bounds
                h, w = self.original_image.shape[:2]
                image_x = max(0, min(w - 1, image_x))
                image_y = max(0, min(h - 1, image_y))
                
                return (image_x, image_y)
            
        except Exception as e:
            logger.error(f"Coordinate conversion error: {e}")
        
        return None
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        
        if event.button() == Qt.LeftButton and self.original_image is not None:
            pos = event.pos()
            image_coords = self.widget_to_image_coords(pos.x(), pos.y())
            
            if image_coords:
                x, y = image_coords
                self.interaction_stats['clicks'] += 1
                
                if self.current_tool == 'magic_wand':
                    self.point_clicked.emit(x, y)
                    self.tool_feedback.emit(f"SAM: Magic Wand clicked at ({x}, {y})")
                
                elif self.current_tool == 'bbox':
                    self.drawing_bbox = True
                    self.bbox_start = (x, y)
                    self.current_bbox = (x, y, x, y)
                
                elif self.current_tool == 'auto':
                    self.auto_segment_requested.emit()
                    self.tool_feedback.emit("🔄 Auto segmentation requested")
                
                elif self.current_tool == 'brush':
                    # Start brush stroke with memory-efficient brush tool
                    self.drawing_brush = True
                    self.brush_tool.start_stroke(x, y, self.original_image.shape[:2])
                    self.tool_feedback.emit(f"Brush: Brush stroke started ({self.brush_tool.brush_mode} mode)")
                
                elif self.current_tool == 'polygon':
                    # Add point to polygon
                    if not self.drawing_polygon:
                        # Start new polygon
                        self.drawing_polygon = True
                        self.current_polygon = [(x, y)]
                        self.tool_feedback.emit(f"📐 Polygon started at ({x}, {y})")
                    else:
                        # Add point to existing polygon
                        self.current_polygon.append((x, y))
                        self.tool_feedback.emit(f"📐 Point added: ({x}, {y}) [{len(self.current_polygon)} points]")
                    
                    self.update_display()
                
                elif self.current_tool == 'rectangle':
                    # Start rectangle drawing
                    self.drawing_rectangle = True
                    self.rectangle_start = (x, y)
                    self.current_rectangle = (x, y, x, y)
                    self.tool_feedback.emit(f"🔲 Rectangle started at ({x}, {y})")
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        
        pos = event.pos()
        image_coords = self.widget_to_image_coords(pos.x(), pos.y())
        
        if image_coords:
            self.mouse_position = image_coords
            
            if self.drawing_bbox and self.bbox_start:
                x, y = image_coords
                x1, y1 = self.bbox_start
                self.current_bbox = (min(x1, x), min(y1, y), max(x1, x), max(y1, y))
                self.update_display_interactive()  # Fast update during interaction
            
            elif self.drawing_brush:
                # Continue brush stroke with memory management
                x, y = image_coords
                self.brush_tool.continue_stroke(x, y, self.original_image.shape[:2])
                self.update_display_interactive()  # Fast update during interaction
            
            elif self.drawing_rectangle and self.rectangle_start:
                # Update rectangle during drag
                x, y = image_coords
                x1, y1 = self.rectangle_start
                self.current_rectangle = (min(x1, x), min(y1, y), max(x1, x), max(y1, y))
                self.update_display_interactive()  # Fast update during interaction
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        
        if event.button() == Qt.LeftButton and self.drawing_bbox and self.current_bbox:
            x1, y1, x2, y2 = self.current_bbox
            
            # Minimum size check
            if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:
                self.bbox_drawn.emit(x1, y1, x2, y2)
                width, height = x2 - x1, y2 - y1
                self.tool_feedback.emit(f"YOLO: BBox drawn: {width}x{height} at ({x1}, {y1})")
            
            # Reset drawing state
            self.drawing_bbox = False
            self.current_bbox = None
            self.bbox_start = None
            self.update_display()
        
        # Handle brush stroke completion
        if event.button() == Qt.LeftButton and self.drawing_brush:
            # Finish brush stroke and get final mask
            brush_mask = self.brush_tool.finish_stroke()
            
            if brush_mask is not None and np.any(brush_mask > 0):
                # Create brush annotation
                brush_annotation = {
                    'type': 'brush_segmentation',
                    'mask': brush_mask,
                    'brush_size': self.brush_tool.brush_size,
                    'brush_mode': self.brush_tool.brush_mode,
                    'timestamp': time.time()
                }
                
                self.add_annotation(brush_annotation)
                self.tool_feedback.emit(f"Success: Brush annotation created ({self.brush_tool.brush_mode} mode)")
                
                # Show memory usage
                memory_stats = self.brush_tool.get_memory_stats()
                memory_mb = memory_stats['current_memory_mb']
                self.tool_feedback.emit(f"💾 Memory usage: {memory_mb:.1f} MB")
            
            # Reset brush state
            self.drawing_brush = False
        
        # Handle rectangle completion
        if event.button() == Qt.LeftButton and self.drawing_rectangle and self.current_rectangle:
            x1, y1, x2, y2 = self.current_rectangle
            
            # Minimum size check
            if abs(x2 - x1) > 5 and abs(y2 - y1) > 5:
                # Create rectangle annotation
                rectangle_annotation = {
                    'type': 'manual_rectangle',
                    'rectangle': (x1, y1, x2, y2),
                    'width': x2 - x1,
                    'height': y2 - y1,
                    'timestamp': time.time()
                }
                
                self.add_annotation(rectangle_annotation)
                self.tool_feedback.emit(f"Success: Rectangle created: {x2-x1}x{y2-y1} at ({x1}, {y1})")
            
            # Reset rectangle state
            self.drawing_rectangle = False
            self.current_rectangle = None
            self.rectangle_start = None
            self.update_display()
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click to confirm temporary annotations or finish polygon."""
        
        if self.drawing_polygon and len(self.current_polygon) >= 3:
            # Finish polygon
            self.finish_polygon()
        elif self.temp_annotations:
            self.confirm_temp_annotations()
            self.tool_feedback.emit("Success: Temporary annotations confirmed")
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        
        if event.key() == Qt.Key_Escape:
            # Cancel current operation
            self.drawing_bbox = False
            self.current_bbox = None
            self.drawing_rectangle = False
            self.current_rectangle = None
            self.rectangle_start = None
            
            if self.drawing_polygon:
                self.drawing_polygon = False
                self.current_polygon.clear()
                self.tool_feedback.emit("🚫 Polygon cancelled")
            
            self.clear_temp_annotations()
            self.update_display()
            self.tool_feedback.emit("🚫 Operation cancelled")
        
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            # Confirm temporary annotations or finish polygon
            if self.drawing_polygon and len(self.current_polygon) >= 3:
                self.finish_polygon()
            elif self.temp_annotations:
                self.confirm_temp_annotations()
                self.tool_feedback.emit("Success: Annotations confirmed")
        
        elif event.key() == Qt.Key_Delete:
            # Clear all annotations
            self.annotations.clear()
            self.temp_annotations.clear()
            self.update_display()
            self.tool_feedback.emit("🗑️ All annotations cleared")
    
    def get_canvas_stats(self) -> Dict[str, Any]:
        """Get canvas interaction statistics."""
        
        return {
            'image_loaded': self.original_image is not None,
            'image_path': self.current_image_path,
            'image_shape': self.original_image.shape if self.original_image is not None else None,
            'annotations_count': len(self.annotations),
            'temp_annotations_count': len(self.temp_annotations),
            'current_tool': self.current_tool,
            'interaction_stats': self.interaction_stats.copy(),
            'detected_objects_count': len(self.detected_objects)
        }
    
    def set_tool(self, tool_name: str):
        """Set the current annotation tool with proper state management."""
        
        self.current_tool = tool_name
        
        # Reset any current drawing states
        self.drawing_bbox = False
        self.drawing_brush = False
        self.drawing_polygon = False
        self.drawing_rectangle = False
        self.current_bbox = None
        self.bbox_start = None
        self.current_polygon.clear()
        self.current_rectangle = None
        self.rectangle_start = None
        
        # Update cursor based on tool
        cursor_map = {
            'magic_wand': Qt.PointingHandCursor,
            'bbox': Qt.CrossCursor,
            'auto': Qt.ArrowCursor,
            'brush': Qt.CrossCursor,
            'polygon': Qt.CrossCursor,
            'rectangle': Qt.CrossCursor
        }
        self.setCursor(QCursor(cursor_map.get(tool_name, Qt.ArrowCursor)))
        
        # Show helpful tool feedback messages
        tool_messages = {
            'magic_wand': "SAM: Magic Wand - Click on objects to segment them",
            'bbox': "YOLO: BBox Segment - Click and drag to draw bounding boxes",
            'auto': "🔄 Auto Segment - Click anywhere to automatically detect all objects",
            'brush': "Brush: Smart Brush - Paint to create segmentation mask",
            'polygon': "📐 Polygon - Click points to create custom polygons (Enter to finish)",
            'rectangle': "🔲 Rectangle - Click and drag to draw rectangles"
        }
        
        message = tool_messages.get(tool_name, f"Tool: {tool_name}")
        self.tool_feedback.emit(message)
        
        logger.info(f"Tool: Tool set to: {tool_name}")
    
    def set_label_manager(self, label_manager):
        """Set the label manager for class assignment."""
        
        self.label_manager = label_manager
        if label_manager:
            self.current_class_id = label_manager.get_current_class_id()
        
        logger.info("Label: Label manager set for canvas")
    
    def set_current_class(self, class_id: int):
        """Set the current class ID for new annotations."""
        
        self.current_class_id = class_id
        
        if self.label_manager:
            class_info = self.label_manager.get_class(class_id)
            if class_info:
                self.tool_feedback.emit(f"Label: Current class: {class_info['name']}")
        
        logger.info(f"Label: Canvas class set to: {class_id}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get canvas performance statistics."""
        
        stats = self.performance_monitor.get_performance_stats()
        recommendations = self.performance_monitor.get_optimization_recommendations()
        
        return {
            **stats,
            'optimization_recommendations': recommendations,
            'caching_enabled': self.enable_caching,
            'cache_valid': self.cached_annotations_image is not None
        }
    
    def enable_performance_caching(self, enabled: bool = True):
        """Enable or disable performance caching."""
        
        self.enable_caching = enabled
        if not enabled:
            self.invalidate_cache()
        
        logger.info(f"App: Performance caching: {'enabled' if enabled else 'disabled'}")
    
    def add_annotation(self, annotation: dict):
        """Add an annotation to the canvas with automatic class assignment."""
        
        # Add class information if not present
        if 'class_id' not in annotation and self.label_manager:
            annotation['class_id'] = self.current_class_id
            
            # Get class info for additional metadata
            class_info = self.label_manager.get_class(self.current_class_id)
            if class_info:
                annotation['class_name'] = class_info['name']
                annotation['class_color'] = class_info['color']
                
                # Increment annotation count for this class
                self.label_manager.increment_annotation_count(self.current_class_id)
        
        # Add annotation ID for tracking
        annotation['annotation_id'] = len(self.annotations) + 1
        
        self.annotations.append(annotation)
        self.interaction_stats['annotations_created'] += 1
        
        # Invalidate cache since annotations changed
        self.invalidate_cache()
        
        # High priority update for user actions
        self.update_display('high')
        
        # Emit signal
        self.annotation_created.emit(annotation)
        
        # Show class info in feedback
        class_name = annotation.get('class_name', f"Class {annotation.get('class_id', 'Unknown')}")
        self.tool_feedback.emit(f"Success: {annotation['type']} created (Label: {class_name})")
        
        logger.info(f"Annotation added: {annotation['type']} with class {class_name}")
    
    def finish_polygon(self):
        """Finish the current polygon and create annotation."""
        
        if not self.drawing_polygon or len(self.current_polygon) < 3:
            return
        
        # Create polygon annotation
        polygon_annotation = {
            'type': 'manual_polygon',
            'polygon': self.current_polygon.copy(),
            'points_count': len(self.current_polygon),
            'timestamp': time.time()
        }
        
        self.add_annotation(polygon_annotation)
        self.tool_feedback.emit(f"Success: Polygon created with {len(self.current_polygon)} points")
        
        # Reset polygon state
        self.drawing_polygon = False
        self.current_polygon.clear()
        self.update_display()
    
    def clear_all(self):
        """Clear all annotations and reset canvas."""
        
        self.annotations.clear()
        self.temp_annotations.clear()
        self.detected_objects.clear()
        self.smart_suggestions.clear()
        
        # Reset interaction state
        self.drawing_bbox = False
        self.current_bbox = None
        self.bbox_start = None
        self.drawing_polygon = False
        self.current_polygon.clear()
        self.drawing_rectangle = False
        self.current_rectangle = None
        self.rectangle_start = None
        
        self.update_display()
        self.tool_feedback.emit("Cleanup: Canvas cleared")
        
        logger.info("Canvas cleared")
    
    def draw_current_interaction(self, image: np.ndarray):
        """Draw current interaction state (bbox, polygon, rectangle being drawn)."""
        
        # Draw current bbox
        if self.drawing_bbox and self.current_bbox:
            x1, y1, x2, y2 = self.current_bbox
            color = (255, 0, 255)  # Magenta
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            
            # Draw size info
            width, height = x2 - x1, y2 - y1
            label = f"{width}x{height}"
            cv2.putText(image, label, (int(x1), int(y1) - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw current rectangle
        if self.drawing_rectangle and self.current_rectangle:
            x1, y1, x2, y2 = self.current_rectangle
            color = (100, 100, 255)  # Blue
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            
            # Draw size info
            width, height = x2 - x1, y2 - y1
            label = f"Rectangle: {width}x{height}"
            cv2.putText(image, label, (int(x1), int(y1) - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw current polygon
        if self.drawing_polygon and len(self.current_polygon) > 0:
            color = (255, 100, 100)  # Red
            
            # Draw lines between points
            if len(self.current_polygon) > 1:
                for i in range(len(self.current_polygon) - 1):
                    pt1 = (int(self.current_polygon[i][0]), int(self.current_polygon[i][1]))
                    pt2 = (int(self.current_polygon[i+1][0]), int(self.current_polygon[i+1][1]))
                    cv2.line(image, pt1, pt2, color, 2)
            
            # Draw points
            for i, point in enumerate(self.current_polygon):
                x, y = int(point[0]), int(point[1])
                cv2.circle(image, (x, y), 5, color, -1)
                cv2.circle(image, (x, y), 5, (255, 255, 255), 2)
                
                # Number the points
                cv2.putText(image, str(i+1), (x+8, y+8), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Draw instruction
            if len(self.current_polygon) >= 3:
                cv2.putText(image, "Double-click or Enter to finish", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            else:
                cv2.putText(image, f"Polygon: {len(self.current_polygon)} points (need 3+)", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    def draw_annotations(self, image: np.ndarray):
        """Draw permanent annotations with class colors."""
        
        for annotation in self.annotations:
            annotation_type = annotation.get('type', 'unknown')
            
            # Get class-specific color
            if 'class_color' in annotation:
                hex_color = annotation['class_color']
                # Convert hex to RGB
                hex_color = hex_color.lstrip('#')
                try:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16) 
                    b = int(hex_color[4:6], 16)
                    color = (r, g, b)
                except ValueError:
                    color = (128, 255, 128)  # Default light green
            else:
                color = (128, 255, 128)  # Default light green
            
            if annotation_type == 'manual_polygon' and 'polygon' in annotation:
                # Draw manual polygon
                polygon = annotation['polygon']
                
                # Draw polygon outline
                if len(polygon) > 2:
                    # Convert to numpy array for cv2
                    pts = np.array([(int(p[0]), int(p[1])) for p in polygon], np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    
                    # Draw filled polygon with proper alpha blending
                    overlay = np.zeros_like(image, dtype=np.uint8)
                    cv2.fillPoly(overlay, [pts], color)
                    
                    # Create mask for polygon area
                    mask = np.zeros(image.shape[:2], dtype=np.uint8)
                    cv2.fillPoly(mask, [pts], 255)
                    
                    # Apply alpha blending only to polygon area
                    alpha = 0.3  # 30% transparency
                    polygon_area = mask > 0
                    image[polygon_area] = (1 - alpha) * image[polygon_area] + alpha * overlay[polygon_area]
                    
                    # Draw outline
                    cv2.polylines(image, [pts], True, color, 2)
                    
                    # Draw class label
                    class_name = annotation.get('class_name', f"Class {annotation.get('class_id', '?')}")
                    points_count = annotation.get('points_count', len(polygon))
                    label = f"{class_name} [{points_count}pts]"
                    
                    # Find top-left point for label placement
                    min_x = min(p[0] for p in polygon)
                    min_y = min(p[1] for p in polygon)
                    
                    # Draw label background
                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                    cv2.rectangle(image, (int(min_x), int(min_y) - label_size[1] - 10), 
                                (int(min_x) + label_size[0] + 10, int(min_y)), color, -1)
                    
                    # Draw label text
                    cv2.putText(image, label, (int(min_x) + 5, int(min_y) - 5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                
                # Draw points
                for i, point in enumerate(polygon):
                    x, y = int(point[0]), int(point[1])
                    cv2.circle(image, (x, y), 3, color, -1)
            
            elif annotation_type == 'manual_rectangle' and 'rectangle' in annotation:
                # Draw manual rectangle with proper alpha blending
                x1, y1, x2, y2 = annotation['rectangle']
                
                # Create overlay for rectangle fill
                overlay = np.zeros_like(image, dtype=np.uint8)
                cv2.rectangle(overlay, (int(x1), int(y1)), (int(x2), int(y2)), color, -1)
                
                # Create mask for rectangle area
                mask = np.zeros(image.shape[:2], dtype=np.uint8)
                cv2.rectangle(mask, (int(x1), int(y1)), (int(x2), int(y2)), 255, -1)
                
                # Apply alpha blending only to rectangle area
                alpha = 0.2  # 20% transparency for rectangles
                rect_area = mask > 0
                image[rect_area] = (1 - alpha) * image[rect_area] + alpha * overlay[rect_area]
                
                # Draw rectangle outline (always visible)
                cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                
                # Draw class label and size
                width, height = x2 - x1, y2 - y1
                class_name = annotation.get('class_name', f"Class {annotation.get('class_id', '?')}")
                label = f"{class_name} [{width}x{height}]"
                
                # Draw label background with proper positioning
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                label_y = max(int(y1) - 5, label_size[1] + 5)  # Ensure label stays visible
                cv2.rectangle(image, (int(x1), label_y - label_size[1] - 5), 
                            (int(x1) + label_size[0] + 10, label_y + 5), color, -1)
                
                # Draw label text with white color for better contrast
                cv2.putText(image, label, (int(x1) + 5, label_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            elif annotation_type == 'brush_segmentation' and 'mask' in annotation:
                # Draw brush segmentation mask with proper alpha blending
                mask = annotation['mask']
                if mask is not None and mask.size > 0:
                    # Create overlay for brush strokes
                    overlay = np.zeros_like(image, dtype=np.uint8)
                    overlay[mask > 0] = color
                    
                    # Apply alpha blending only to brush area
                    alpha = 0.4  # 40% transparency for brush strokes
                    brush_area = mask > 0
                    image[brush_area] = (1 - alpha) * image[brush_area] + alpha * overlay[brush_area]
                    
                    # Draw contours for better visibility
                    mask_uint8 = (mask > 0).astype(np.uint8) * 255
                    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    cv2.drawContours(image, contours, -1, color, 1)
            
            elif 'mask' in annotation:
                # Draw other segmentation masks (SAM results) with proper alpha blending
                mask = annotation['mask']
                if mask is not None and mask.size > 0:
                    # Use class color if available, otherwise use type-based color
                    sam_color = color  # Use the class color from above
                    
                    # Create overlay for mask
                    overlay = np.zeros_like(image, dtype=np.uint8)
                    overlay[mask > 0] = sam_color
                    
                    # Apply alpha blending only to mask area
                    alpha = 0.3  # 30% transparency for SAM results
                    mask_area = mask > 0
                    image[mask_area] = (1 - alpha) * image[mask_area] + alpha * overlay[mask_area]
                    
                    # Draw contours for better visibility
                    mask_uint8 = (mask > 0).astype(np.uint8) * 255
                    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    cv2.drawContours(image, contours, -1, sam_color, 2)
    
    def draw_temp_annotations(self, image: np.ndarray):
        """Draw temporary annotations with proper alpha blending."""
        
        for annotation in self.temp_annotations:
            # Similar to draw_annotations but with different colors/transparency
            if 'mask' in annotation:
                mask = annotation['mask']
                if mask is not None and mask.size > 0:
                    # Use orange color for temporary annotations
                    temp_color = (255, 165, 0)  # Orange for temp
                    
                    # Create overlay for temporary mask
                    overlay = np.zeros_like(image, dtype=np.uint8)
                    overlay[mask > 0] = temp_color
                    
                    # Apply alpha blending only to mask area
                    alpha = 0.5  # 50% transparency for temp annotations (more visible)
                    mask_area = mask > 0
                    image[mask_area] = (1 - alpha) * image[mask_area] + alpha * overlay[mask_area]
                    
                    # Draw contours for better visibility
                    mask_uint8 = (mask > 0).astype(np.uint8) * 255
                    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    cv2.drawContours(image, contours, -1, temp_color, 2)
    
    def draw_smart_hints(self, image: np.ndarray):
        """Draw smart hints and suggestions."""
        
        for hint in self.smart_suggestions:
            if 'bbox' in hint:
                x1, y1, x2, y2 = hint['bbox']
                color = (255, 255, 0)  # Yellow
                cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, 1, cv2.LINE_DASHED)
                
                # Draw hint text
                hint_text = hint.get('text', 'Smart suggestion')
                cv2.putText(image, hint_text, (int(x1), int(y1) - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    def display_numpy_image(self, image: np.ndarray):
        """Convert numpy image to QPixmap and display."""
        
        try:
            # Convert to RGB if needed
            if len(image.shape) == 3:
                h, w, ch = image.shape
                if ch == 3:
                    # Convert BGR to RGB for Qt
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                else:
                    image_rgb = image
            else:
                # Grayscale to RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                h, w, ch = image_rgb.shape
            
            # Calculate scale factor to fit widget
            widget_size = self.size()
            scale_x = widget_size.width() / w
            scale_y = widget_size.height() / h
            self.scale_factor = min(scale_x, scale_y, 1.0)  # Don't upscale
            
            # Resize if needed
            if self.scale_factor < 1.0:
                new_w = int(w * self.scale_factor)
                new_h = int(h * self.scale_factor)
                image_rgb = cv2.resize(image_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
                h, w, ch = image_rgb.shape
            
            # Convert to QPixmap
            bytes_per_line = ch * w
            q_image = QImage(image_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            # Set pixmap
            self.setPixmap(pixmap)
            
        except Exception as e:
            logger.error(f"Display image error: {e}")
            self.setText(f"Error: Display error: {e}")
    
    def confirm_temp_annotations(self):
        """Confirm temporary annotations by moving them to permanent annotations."""
        
        self.annotations.extend(self.temp_annotations)
        self.temp_annotations.clear()
        self.update_display()
        
        logger.info(f"Confirmed {len(self.temp_annotations)} temporary annotations")
    
    def clear_temp_annotations(self):
        """Clear temporary annotations."""
        
        self.temp_annotations.clear()
        self.update_display()
        
        logger.info("Cleared temporary annotations")
