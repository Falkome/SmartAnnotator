#!/usr/bin/env python3
"""
Smart Engine - Core Intelligence for Smart Annotator

Provides AI-powered analysis and smart features for image annotation.
"""

import numpy as np
import cv2
import time
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class SmartEngine:
    """Core smart engine for AI-powered image analysis and recommendations."""
    
    def __init__(self):
        self.initialized = False
        self.session_stats = {
            'images_processed': 0,
            'annotations_created': 0,
            'smart_suggestions_used': 0,
            'processing_time': 0.0
        }
        
        # Smart parameters
        self.adaptive_confidence = 0.5
        self.smart_mode = True
        self.learning_enabled = True
        
        logger.info("Engine: Smart Engine created")
    
    def initialize(self) -> bool:
        """Initialize the smart engine."""
        
        try:
            logger.info("Engine: Initializing Smart Engine...")
            
            # Initialize smart components
            self.initialized = True
            
            logger.info("Success: Smart Engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error: Smart Engine initialization failed: {e}")
            return False
    
    def analyze_image(self, image: np.ndarray) -> List[str]:
        """Analyze image and provide smart suggestions."""
        
        if not self.initialized:
            return ["Warning: Smart Engine not initialized"]
        
        try:
            start_time = time.time()
            
            # Basic image analysis
            h, w = image.shape[:2]
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
            
            suggestions = []
            
            # Size analysis
            total_pixels = h * w
            if total_pixels > 2000000:  # Large image
                suggestions.append("YOLO: Large image detected - consider using BBox tool for efficiency")
            elif total_pixels < 100000:  # Small image
                suggestions.append("🔍 Small image - Magic Wand tool recommended for precision")
            
            # Edge analysis
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            if edge_density > 0.15:
                suggestions.append("SAM: High edge density - objects well-defined, Magic Wand optimal")
            elif edge_density < 0.05:
                suggestions.append("🔄 Low edge density - Auto Segment recommended for detection")
            else:
                suggestions.append("YOLO: Moderate complexity - BBox Segment for controlled annotation")
            
            # Brightness analysis
            mean_brightness = np.mean(gray)
            if mean_brightness < 80:
                suggestions.append("🌙 Dark image - consider adjusting confidence threshold")
            elif mean_brightness > 180:
                suggestions.append("☀️ Bright image - standard settings should work well")
            
            # Contrast analysis
            contrast = np.std(gray)
            if contrast < 30:
                suggestions.append("Monitor: Low contrast - may need careful threshold adjustment")
            elif contrast > 80:
                suggestions.append("📈 High contrast - excellent for automatic detection")
            
            # Default suggestion if no specific ones
            if not suggestions:
                suggestions.append("Engine: Image ready for smart annotation - try Magic Wand first")
            
            # Update stats
            processing_time = time.time() - start_time
            self.session_stats['processing_time'] += processing_time
            self.session_stats['images_processed'] += 1
            
            logger.info(f"Engine: Image analyzed in {processing_time:.3f}s - {len(suggestions)} suggestions")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error: Image analysis error: {e}")
            return ["Error: Analysis failed - please try again"]
    
    def get_smart_confidence(self, image_complexity: float) -> float:
        """Get adaptive confidence threshold based on image complexity."""
        
        # Adjust confidence based on complexity
        if image_complexity < 0.3:
            return max(0.3, self.adaptive_confidence - 0.1)  # Lower threshold for simple images
        elif image_complexity > 0.7:
            return min(0.8, self.adaptive_confidence + 0.1)  # Higher threshold for complex images
        else:
            return self.adaptive_confidence
    
    def calculate_image_complexity(self, image: np.ndarray) -> float:
        """Calculate image complexity score (0-1)."""
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
            
            # Edge density
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Texture analysis (using gradient magnitude)
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
            texture_strength = np.mean(magnitude) / 100.0  # Normalize
            
            # Combine metrics
            complexity = (edge_density * 0.6 + min(1.0, texture_strength) * 0.4)
            
            return min(1.0, complexity)
            
        except Exception as e:
            logger.error(f"Complexity calculation error: {e}")
            return 0.5  # Default medium complexity
    
    def recommend_tool(self, image: np.ndarray) -> str:
        """Recommend the best annotation tool for the image."""
        
        try:
            complexity = self.calculate_image_complexity(image)
            h, w = image.shape[:2]
            image_size = h * w
            
            # Tool recommendation logic
            if complexity < 0.3 and image_size < 500000:
                return "magic_wand"  # Simple, small images
            elif complexity > 0.7 or image_size > 2000000:
                return "bbox"  # Complex or large images
            elif complexity > 0.5:
                return "auto"  # Medium complexity - let AI find objects
            else:
                return "magic_wand"  # Default to magic wand
                
        except Exception as e:
            logger.error(f"Tool recommendation error: {e}")
            return "magic_wand"  # Safe default
    
    def learn_from_annotation(self, annotation_data: Dict[str, Any]):
        """Learn from user annotation to improve future suggestions."""
        
        if not self.learning_enabled:
            return
        
        try:
            # Update stats
            self.session_stats['annotations_created'] += 1
            
            # Simple learning: adjust confidence based on results
            if annotation_data.get('successful', True):
                # Annotation was successful, slightly lower threshold for next time
                self.adaptive_confidence = max(0.2, self.adaptive_confidence * 0.99)
            else:
                # Annotation had issues, slightly raise threshold
                self.adaptive_confidence = min(0.8, self.adaptive_confidence * 1.01)
            
            logger.debug(f"Engine: Learning: Adaptive confidence now {self.adaptive_confidence:.3f}")
            
        except Exception as e:
            logger.error(f"Learning error: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics."""
        
        return {
            'session_stats': self.session_stats.copy(),
            'adaptive_confidence': self.adaptive_confidence,
            'smart_mode': self.smart_mode,
            'learning_enabled': self.learning_enabled,
            'initialized': self.initialized
        }
    
    def reset_session(self):
        """Reset session statistics."""
        
        self.session_stats = {
            'images_processed': 0,
            'annotations_created': 0,
            'smart_suggestions_used': 0,
            'processing_time': 0.0
        }
        
        logger.info(" Session statistics reset")
    
    def set_smart_mode(self, enabled: bool):
        """Enable or disable smart mode."""
        
        self.smart_mode = enabled
        logger.info(f"Engine: Smart mode: {'enabled' if enabled else 'disabled'}")
    
    def set_learning_mode(self, enabled: bool):
        """Enable or disable learning mode."""
        
        self.learning_enabled = enabled
        logger.info(f"📚 Learning mode: {'enabled' if enabled else 'disabled'}")
    
    def get_smart_summary(self) -> str:
        """Get a summary of smart engine status."""
        
        if not self.initialized:
            return "Error: Smart Engine not initialized"
        
        stats = self.session_stats
        
        summary = f"""Engine: Smart Engine Status:
Success: Initialized and ready
Monitor: Images processed: {stats['images_processed']}
📝 Annotations created: {stats['annotations_created']}
Suggestions used: {stats['smart_suggestions_used']}
⏱️ Processing time: {stats['processing_time']:.1f}s
SAM: Adaptive confidence: {self.adaptive_confidence:.2f}
Engine: Smart mode: {'On' if self.smart_mode else 'Off'}
📚 Learning: {'On' if self.learning_enabled else 'Off'}"""
        
        return summary
