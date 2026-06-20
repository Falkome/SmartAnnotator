#!/usr/bin/env python3
"""
YOLO Model - You Only Look Once Object Detection

Smart YOLO model integration for object detection and classification.
"""

import numpy as np
import cv2
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# YOLO model imports
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("Ultralytics YOLO not available. Install with: pip install ultralytics")


class YOLOModel:
    """Smart YOLO model with enhanced detection capabilities."""
    
    def __init__(self):
        self.model = None
        self.model_path = None
        self.is_loaded = False
        
        # Model performance tracking
        self.stats = {
            'detections_made': 0,
            'objects_detected': 0,
            'total_processing_time': 0.0,
            'average_confidence': 0.0
        }
        
        # Smart parameters
        self.confidence_threshold = 0.25
        self.nms_threshold = 0.45  # Non-Maximum Suppression
        self.max_detections = 100
        
        # Class names (will be loaded from model)
        self.class_names = []
        
        logger.info("📦 YOLO Model initialized")
    
    def load_model(self, model_path: str = None) -> bool:
        """Load YOLO model from weights."""
        
        if not YOLO_AVAILABLE:
            logger.error("❌ YOLO not available - ultralytics package required")
            return False
        
        try:
            # Find model if not specified
            if model_path is None:
                model_path = self._find_yolo_model()
            
            if model_path is None:
                logger.info("📦 No custom YOLO model found, using default YOLOv8n")
                model_path = "yolov8n.pt"  # Use default small model
            
            logger.info(f"🤖 Loading YOLO model: {model_path}")
            
            # Load the model
            self.model = YOLO(model_path)
            self.model_path = model_path
            self.is_loaded = True
            
            # Get class names
            self.class_names = list(self.model.names.values())
            
            logger.info(f"✅ YOLO model loaded: {Path(model_path).name} ({len(self.class_names)} classes)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load YOLO model: {e}")
            self.is_loaded = False
            return False
    
    def _find_yolo_model(self) -> Optional[str]:
        """Find available YOLO model in weights directory."""
        
        weights_dir = Path("weights/yolo")
        if not weights_dir.exists():
            return None
        
        # Look for YOLO model files
        yolo_files = list(weights_dir.glob("*.pt"))
        
        if yolo_files:
            # Prefer smaller models first for faster loading
            model_priority = ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt", "yolov8x.pt"]
            
            for preferred in model_priority:
                for model_file in yolo_files:
                    if model_file.name == preferred:
                        return str(model_file)
            
            # Return first available if no preferred found
            return str(yolo_files[0])
        
        return None
    
    def detect_objects(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect objects in image."""
        
        if not self.is_loaded:
            return {'error': 'YOLO model not loaded'}
        
        try:
            start_time = time.time()
            
            # Run YOLO detection
            results = self.model(
                image,
                conf=self.confidence_threshold,
                iou=self.nms_threshold,
                max_det=self.max_detections,
                verbose=False
            )
            
            # Process results
            processed_results = self._process_yolo_results(results)
            
            # Update stats
            processing_time = time.time() - start_time
            self._update_stats(processed_results, processing_time)
            
            logger.info(f"📦 YOLO detection: {len(processed_results)} objects in {processing_time:.2f}s")
            
            return {
                'success': True,
                'results': processed_results,
                'processing_time': processing_time,
                'model_type': 'detection'
            }
            
        except Exception as e:
            logger.error(f"❌ YOLO detection error: {e}")
            return {'error': str(e)}
    
    def detect_and_classify(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect and classify objects with detailed information."""
        
        detection_result = self.detect_objects(image)
        
        if not detection_result.get('success'):
            return detection_result
        
        # Add classification statistics
        results = detection_result['results']
        
        # Count objects by class
        class_counts = {}
        confidence_by_class = {}
        
        for result in results:
            class_name = result['class_name']
            confidence = result['confidence']
            
            if class_name in class_counts:
                class_counts[class_name] += 1
                confidence_by_class[class_name].append(confidence)
            else:
                class_counts[class_name] = 1
                confidence_by_class[class_name] = [confidence]
        
        # Calculate average confidence by class
        avg_confidence_by_class = {
            cls: np.mean(confidences) 
            for cls, confidences in confidence_by_class.items()
        }
        
        detection_result.update({
            'class_counts': class_counts,
            'avg_confidence_by_class': avg_confidence_by_class,
            'total_objects': len(results),
            'unique_classes': len(class_counts)
        })
        
        return detection_result
    
    def _process_yolo_results(self, results) -> List[Dict[str, Any]]:
        """Process YOLO results into standardized format."""
        
        processed = []
        
        try:
            if results and len(results) > 0:
                result = results[0]  # Get first result
                
                # Check if we have detections
                if hasattr(result, 'boxes') and result.boxes is not None:
                    boxes = result.boxes
                    
                    # Extract data
                    xyxy = boxes.xyxy.cpu().numpy()  # Bounding boxes
                    conf = boxes.conf.cpu().numpy()  # Confidences
                    cls = boxes.cls.cpu().numpy()   # Class indices
                    
                    # Process each detection
                    for i in range(len(xyxy)):
                        x1, y1, x2, y2 = xyxy[i]
                        confidence = float(conf[i])
                        class_id = int(cls[i])
                        
                        # Get class name
                        class_name = self.class_names[class_id] if class_id < len(self.class_names) else f"class_{class_id}"
                        
                        # Calculate additional properties
                        width = x2 - x1
                        height = y2 - y1
                        area = width * height
                        center_x = (x1 + x2) / 2
                        center_y = (y1 + y2) / 2
                        
                        # Create detection entry
                        detection = {
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': confidence,
                            'class_id': class_id,
                            'class_name': class_name,
                            'center': [float(center_x), float(center_y)],
                            'width': float(width),
                            'height': float(height),
                            'area': float(area)
                        }
                        
                        processed.append(detection)
                    
                    # Sort by confidence (highest first)
                    processed.sort(key=lambda x: x['confidence'], reverse=True)
        
        except Exception as e:
            logger.error(f"YOLO result processing error: {e}")
        
        return processed
    
    def filter_by_class(self, detections: List[Dict[str, Any]], target_classes: List[str]) -> List[Dict[str, Any]]:
        """Filter detections by specific classes."""
        
        filtered = [
            detection for detection in detections 
            if detection['class_name'] in target_classes
        ]
        
        logger.info(f"📋 Filtered {len(filtered)}/{len(detections)} detections for classes: {target_classes}")
        return filtered
    
    def filter_by_confidence(self, detections: List[Dict[str, Any]], min_confidence: float) -> List[Dict[str, Any]]:
        """Filter detections by minimum confidence."""
        
        filtered = [
            detection for detection in detections 
            if detection['confidence'] >= min_confidence
        ]
        
        logger.info(f"🎯 Filtered {len(filtered)}/{len(detections)} detections with confidence >= {min_confidence:.2f}")
        return filtered
    
    def filter_by_size(self, detections: List[Dict[str, Any]], min_area: float = 0, max_area: float = float('inf')) -> List[Dict[str, Any]]:
        """Filter detections by bounding box area."""
        
        filtered = [
            detection for detection in detections 
            if min_area <= detection['area'] <= max_area
        ]
        
        logger.info(f"📐 Filtered {len(filtered)}/{len(detections)} detections by size ({min_area}-{max_area})")
        return filtered
    
    def get_detection_summary(self, detections: List[Dict[str, Any]]) -> str:
        """Get formatted summary of detections."""
        
        if not detections:
            return "📦 No objects detected"
        
        # Count by class
        class_counts = {}
        for detection in detections:
            class_name = detection['class_name']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        # Format summary
        summary = f"📦 YOLO Detection Summary:\n"
        summary += f"Total objects: {len(detections)}\n"
        summary += f"Unique classes: {len(class_counts)}\n\n"
        
        # List classes with counts
        for class_name, count in sorted(class_counts.items()):
            summary += f"  {class_name}: {count}\n"
        
        # Add confidence stats
        confidences = [d['confidence'] for d in detections]
        summary += f"\nConfidence range: {min(confidences):.2f} - {max(confidences):.2f}"
        
        return summary
    
    def _update_stats(self, results: List[Dict[str, Any]], processing_time: float):
        """Update model performance statistics."""
        
        self.stats['detections_made'] += 1
        self.stats['total_processing_time'] += processing_time
        self.stats['objects_detected'] += len(results)
        
        if results:
            # Update average confidence
            confidences = [r['confidence'] for r in results]
            if confidences:
                new_conf = np.mean(confidences)
                current_avg = self.stats['average_confidence']
                total_detections = self.stats['detections_made']
                
                # Running average
                self.stats['average_confidence'] = (current_avg * (total_detections - 1) + new_conf) / total_detections
    
    def set_confidence_threshold(self, threshold: float):
        """Set confidence threshold for detections."""
        
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"📦 YOLO confidence threshold set to: {self.confidence_threshold:.2f}")
    
    def set_nms_threshold(self, threshold: float):
        """Set Non-Maximum Suppression threshold."""
        
        self.nms_threshold = max(0.0, min(1.0, threshold))
        logger.info(f" YOLO NMS threshold set to: {self.nms_threshold:.2f}")
    
    def set_max_detections(self, max_det: int):
        """Set maximum number of detections."""
        
        self.max_detections = max(1, max_det)
        logger.info(f"📊 YOLO max detections set to: {self.max_detections}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        
        return {
            'is_loaded': self.is_loaded,
            'model_path': self.model_path,
            'model_name': Path(self.model_path).name if self.model_path else None,
            'num_classes': len(self.class_names),
            'class_names': self.class_names.copy(),
            'confidence_threshold': self.confidence_threshold,
            'nms_threshold': self.nms_threshold,
            'max_detections': self.max_detections,
            'stats': self.stats.copy()
        }
    
    def get_performance_summary(self) -> str:
        """Get performance summary as formatted string."""
        
        if not self.is_loaded:
            return "❌ YOLO model not loaded"
        
        stats = self.stats
        avg_time = stats['total_processing_time'] / max(1, stats['detections_made'])
        avg_objects = stats['objects_detected'] / max(1, stats['detections_made'])
        
        return f"""📦 YOLO Model Performance:
📂 Model: {Path(self.model_path).name if self.model_path else 'Unknown'}
🎯 Classes: {len(self.class_names)}
📊 Detections: {stats['detections_made']}
🔍 Objects found: {stats['objects_detected']}
📈 Avg objects/image: {avg_objects:.1f}
⏱️ Avg time: {avg_time:.2f}s
🎯 Avg confidence: {stats['average_confidence']:.2f}
🔧 Conf threshold: {self.confidence_threshold:.2f}
🔄 NMS threshold: {self.nms_threshold:.2f}"""
    
    def get_class_list(self) -> List[str]:
        """Get list of available classes."""
        
        return self.class_names.copy()
    
    def cleanup(self):
        """Clean up model resources."""
        
        if self.model is not None:
            del self.model
            self.model = None
            
        self.is_loaded = False
        logger.info("🧹 YOLO model resources cleaned up")
