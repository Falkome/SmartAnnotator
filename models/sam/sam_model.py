#!/usr/bin/env python3
"""
SAM Model - Segment Anything Model Integration

Smart SAM model with enhanced features for intelligent image segmentation.
"""

import numpy as np
import cv2
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# SAM model imports
try:
    from ultralytics import SAM
    SAM_AVAILABLE = True
except ImportError:
    SAM_AVAILABLE = False
    logger.warning("Ultralytics SAM not available. Install with: pip install ultralytics")


class SAMModel:
    """Smart SAM model with enhanced segmentation capabilities."""
    
    def __init__(self):
        self.model = None
        self.model_path = None
        self.is_loaded = False
        
        # Model performance tracking
        self.stats = {
            'predictions_made': 0,
            'successful_predictions': 0,
            'total_processing_time': 0.0,
            'average_confidence': 0.0
        }
        
        # Smart parameters
        self.confidence_threshold = 0.5
        self.smart_refinement = True
        
        logger.info("🎯 SAM Model initialized")
    
    def load_model(self, model_path: str = None) -> bool:
        """Load SAM model from weights."""
        
        if not SAM_AVAILABLE:
            logger.error("❌ SAM not available - ultralytics package required")
            return False
        
        try:
            # Find model if not specified
            if model_path is None:
                model_path = self._find_sam_model()
            
            if model_path is None:
                logger.warning("⚠️ No SAM model found. Please place model files in weights/sam/")
                return False
            
            logger.info(f"🤖 Loading SAM model: {model_path}")
            
            # Load the model
            self.model = SAM(model_path)
            self.model_path = model_path
            self.is_loaded = True
            
            logger.info(f"✅ SAM model loaded successfully: {Path(model_path).name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load SAM model: {e}")
            self.is_loaded = False
            return False
    
    def _find_sam_model(self) -> Optional[str]:
        """Find available SAM model in weights directory."""
        
        weights_dir = Path("weights/sam")
        if not weights_dir.exists():
            return None
        
        # Look for SAM model files
        sam_files = list(weights_dir.glob("*.pt"))
        
        if sam_files:
            # Prefer smaller models first for faster loading
            model_priority = ["sam2_t.pt", "sam2_s.pt", "sam2_b.pt", "sam2_l.pt"]
            
            for preferred in model_priority:
                for model_file in sam_files:
                    if model_file.name == preferred:
                        return str(model_file)
            
            # Return first available if no preferred found
            return str(sam_files[0])
        
        return None
    
    def predict_with_point(self, image: np.ndarray, point: Tuple[int, int]) -> Dict[str, Any]:
        """Predict segmentation mask from point prompt."""
        
        if not self.is_loaded:
            return {'error': 'SAM model not loaded'}
        
        try:
            start_time = time.time()
            
            # Run SAM prediction with point
            results = self.model(image, points=[point], labels=[1])
            
            # Process results
            processed_results = self._process_sam_results(results)
            
            # Update stats
            processing_time = time.time() - start_time
            self._update_stats(processed_results, processing_time)
            
            # Memory cleanup after prediction
            self._cleanup_prediction_memory()
            
            logger.info(f"🎯 SAM point prediction: {len(processed_results)} masks in {processing_time:.2f}s")
            
            return {
                'success': True,
                'results': processed_results,
                'processing_time': processing_time,
                'prompt_type': 'point',
                'prompt_data': point
            }
            
        except Exception as e:
            logger.error(f"❌ SAM point prediction error: {e}")
            return {'error': str(e)}
    
    def predict_with_bbox(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Dict[str, Any]:
        """Predict segmentation mask from bounding box prompt."""
        
        if not self.is_loaded:
            return {'error': 'SAM model not loaded'}
        
        try:
            start_time = time.time()
            
            # Convert bbox to SAM format [x1, y1, x2, y2]
            x1, y1, x2, y2 = bbox
            sam_bbox = [x1, y1, x2, y2]
            
            # Run SAM prediction with bbox
            results = self.model(image, bboxes=[sam_bbox])
            
            # Process results
            processed_results = self._process_sam_results(results)
            
            # Update stats
            processing_time = time.time() - start_time
            self._update_stats(processed_results, processing_time)
            
            # Memory cleanup after prediction
            self._cleanup_prediction_memory()
            
            logger.info(f"📦 SAM bbox prediction: {len(processed_results)} masks in {processing_time:.2f}s")
            
            return {
                'success': True,
                'results': processed_results,
                'processing_time': processing_time,
                'prompt_type': 'bbox',
                'prompt_data': bbox
            }
            
        except Exception as e:
            logger.error(f"❌ SAM bbox prediction error: {e}")
            return {'error': str(e)}
    
    def predict_auto(self, image: np.ndarray) -> Dict[str, Any]:
        """Predict all objects in image automatically."""
        
        if not self.is_loaded:
            return {'error': 'SAM model not loaded'}
        
        try:
            start_time = time.time()
            
            # Run SAM automatic segmentation
            results = self.model(image)
            
            # Process results
            processed_results = self._process_sam_results(results)
            
            # Filter by confidence threshold
            filtered_results = [
                result for result in processed_results 
                if result['confidence'] >= self.confidence_threshold
            ]
            
            # Update stats
            processing_time = time.time() - start_time
            self._update_stats(filtered_results, processing_time)
            
            # Memory cleanup after prediction
            self._cleanup_prediction_memory()
            
            logger.info(f" SAM auto prediction: {len(filtered_results)} objects in {processing_time:.2f}s")
            
            return {
                'success': True,
                'results': filtered_results,
                'processing_time': processing_time,
                'prompt_type': 'auto',
                'total_detections': len(processed_results),
                'filtered_detections': len(filtered_results)
            }
            
        except Exception as e:
            logger.error(f"❌ SAM auto prediction error: {e}")
            return {'error': str(e)}
    
    def _process_sam_results(self, results) -> List[Dict[str, Any]]:
        """Process SAM results into standardized format."""
        
        processed = []
        
        try:
            if results and len(results) > 0 and hasattr(results[0], 'masks'):
                masks = results[0].masks
                
                if masks is not None:
                    # Get confidence scores if available
                    confidences = None
                    if hasattr(results[0], 'boxes') and results[0].boxes is not None:
                        confidences = results[0].boxes.conf
                    
                    # Process each mask
                    for i, mask in enumerate(masks.data):
                        mask_np = mask.cpu().numpy()
                        
                        # Get confidence
                        confidence = float(confidences[i]) if confidences is not None else 0.5
                        
                        # Apply smart refinement if enabled
                        if self.smart_refinement:
                            mask_np = self._refine_mask(mask_np)
                        
                        # Calculate mask properties
                        mask_props = self._calculate_mask_properties(mask_np)
                        
                        # Create result entry
                        result = {
                            'mask': mask_np,
                            'confidence': confidence,
                            'area': mask_props['area'],
                            'bbox': mask_props['bbox'],
                            'smart_refined': self.smart_refinement,
                            'compactness': mask_props['compactness']
                        }
                        
                        processed.append(result)
            
        except Exception as e:
            logger.error(f"Result processing error: {e}")
        
        return processed
    
    def _refine_mask(self, mask: np.ndarray) -> np.ndarray:
        """Apply smart refinement to mask."""
        
        try:
            # Convert to binary
            binary_mask = (mask > 0.5).astype(np.uint8)
            
            # Morphological operations for refinement
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            
            # Close small gaps
            refined = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
            
            # Remove small noise
            refined = cv2.morphologyEx(refined, cv2.MORPH_OPEN, kernel)
            
            return refined.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Mask refinement error: {e}")
            return mask
    
    def _calculate_mask_properties(self, mask: np.ndarray) -> Dict[str, Any]:
        """Calculate properties of a mask."""
        
        try:
            # Area
            area = int(np.sum(mask > 0.5))
            
            # Bounding box
            coords = np.where(mask > 0.5)
            if len(coords[0]) > 0:
                y_min, y_max = int(np.min(coords[0])), int(np.max(coords[0]))
                x_min, x_max = int(np.min(coords[1])), int(np.max(coords[1]))
                bbox = [x_min, y_min, x_max, y_max]
            else:
                bbox = [0, 0, 0, 0]
            
            # Compactness (measure of how circular the shape is)
            try:
                binary = (mask > 0.5).astype(np.uint8)
                contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    perimeter = cv2.arcLength(contours[0], True)
                    compactness = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
                else:
                    compactness = 0
            except:
                compactness = 0
            
            return {
                'area': area,
                'bbox': bbox,
                'compactness': float(compactness)
            }
            
        except Exception as e:
            logger.error(f"Mask properties calculation error: {e}")
            return {'area': 0, 'bbox': [0, 0, 0, 0], 'compactness': 0.0}
    
    def _update_stats(self, results: List[Dict[str, Any]], processing_time: float):
        """Update model performance statistics."""
        
        self.stats['predictions_made'] += 1
        self.stats['total_processing_time'] += processing_time
        
        if results:
            self.stats['successful_predictions'] += 1
            
            # Update average confidence
            confidences = [r['confidence'] for r in results]
            if confidences:
                new_conf = np.mean(confidences)
                current_avg = self.stats['average_confidence']
                success_count = self.stats['successful_predictions']
                
                # Running average
                self.stats['average_confidence'] = (current_avg * (success_count - 1) + new_conf) / success_count
    
    def set_confidence_threshold(self, threshold: float):
        """Set confidence threshold for filtering results."""
        
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"🎯 SAM confidence threshold set to: {self.confidence_threshold:.2f}")
    
    def set_smart_refinement(self, enabled: bool):
        """Enable or disable smart mask refinement."""
        
        self.smart_refinement = enabled
        logger.info(f"✨ SAM smart refinement: {'enabled' if enabled else 'disabled'}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        
        return {
            'is_loaded': self.is_loaded,
            'model_path': self.model_path,
            'model_name': Path(self.model_path).name if self.model_path else None,
            'confidence_threshold': self.confidence_threshold,
            'smart_refinement': self.smart_refinement,
            'stats': self.stats.copy()
        }
    
    def get_performance_summary(self) -> str:
        """Get performance summary as formatted string."""
        
        if not self.is_loaded:
            return "❌ SAM model not loaded"
        
        stats = self.stats
        success_rate = stats['successful_predictions'] / max(1, stats['predictions_made'])
        avg_time = stats['total_processing_time'] / max(1, stats['predictions_made'])
        
        return f"""🎯 SAM Model Performance:
📂 Model: {Path(self.model_path).name if self.model_path else 'Unknown'}
📊 Predictions: {stats['predictions_made']}
✅ Success rate: {success_rate:.1%}
⏱️ Avg time: {avg_time:.2f}s
🎯 Avg confidence: {stats['average_confidence']:.2f}
🔧 Threshold: {self.confidence_threshold:.2f}
✨ Smart refinement: {'On' if self.smart_refinement else 'Off'}"""
    
    def _cleanup_prediction_memory(self):
        """Clean up memory after each prediction to prevent accumulation."""
        
        import gc
        gc.collect()
        
        # Clear CUDA cache if available
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
    
    def cleanup(self):
        """Clean up model resources."""
        
        if self.model is not None:
            del self.model
            self.model = None
            
        # Aggressive memory cleanup
        import gc
        gc.collect()
        
        # Clear CUDA cache if available
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
            
        self.is_loaded = False
        logger.info("🧹 SAM model resources cleaned up")
