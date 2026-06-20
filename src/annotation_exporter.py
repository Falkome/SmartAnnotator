#!/usr/bin/env python3
"""
Annotation Exporter - Format-Aware Annotation Saving
Exports annotations in appropriate formats based on annotation type.
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

import numpy as np
import cv2

logger = logging.getLogger(__name__)


class AnnotationExporter:
    """Export annotations in various formats based on annotation type."""
    
    def __init__(self):
        self.supported_formats = {
            'yolo': ['manual_rectangle', 'bbox_segmentation'],
            'mask': ['magic_wand_segmentation', 'brush_segmentation', 'manual_polygon'],
            'json': ['all']  # Fallback format for all types
        }
        
        logger.info(" AnnotationExporter initialized")
    
    def export_annotations(self, annotations: List[Dict], image_path: str, 
                          image_shape: Tuple[int, int, int], output_dir: str = None) -> Dict[str, str]:
        """Export annotations based on their types."""
        
        if not annotations:
            logger.warning("No annotations to export")
            return {'status': 'warning', 'message': 'No annotations to export'}
        
        # Create output directory
        if output_dir is None:
            output_dir = Path(image_path).parent / "annotations"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Group annotations by export format
        yolo_annotations = []
        mask_annotations = []
        other_annotations = []
        
        for annotation in annotations:
            annotation_type = annotation.get('type', 'unknown')
            
            if annotation_type in self.supported_formats['yolo']:
                yolo_annotations.append(annotation)
            elif annotation_type in self.supported_formats['mask']:
                mask_annotations.append(annotation)
            else:
                other_annotations.append(annotation)
        
        results = {}
        image_name = Path(image_path).stem
        
        # Export YOLO format for rectangle/bbox annotations
        if yolo_annotations:
            yolo_result = self._export_yolo_format(
                yolo_annotations, image_shape, output_path / f"{image_name}.txt"
            )
            results['yolo'] = yolo_result
        
        # Export mask images for segmentation annotations
        if mask_annotations:
            mask_result = self._export_mask_format(
                mask_annotations, image_shape, output_path, image_name
            )
            results['mask'] = mask_result
        
        # Export JSON format for all annotations (backup)
        json_result = self._export_json_format(
            annotations, image_path, image_shape, output_path / f"{image_name}.json"
        )
        results['json'] = json_result
        
        # Summary
        total_exported = len(yolo_annotations) + len(mask_annotations) + len(other_annotations)
        
        summary = {
            'status': 'success',
            'total_annotations': total_exported,
            'yolo_annotations': len(yolo_annotations),
            'mask_annotations': len(mask_annotations),
            'output_directory': str(output_path),
            'formats_exported': list(results.keys())
        }
        
        logger.info(f" Exported {total_exported} annotations in {len(results)} formats")
        return summary
    
    def _export_yolo_format(self, annotations: List[Dict], image_shape: Tuple[int, int, int], 
                           output_file: Path) -> Dict[str, Any]:
        """Export rectangle/bbox annotations in YOLO format."""
        
        try:
            h, w, _ = image_shape
            yolo_lines = []
            
            for annotation in annotations:
                annotation_type = annotation.get('type', 'unknown')
                
                if annotation_type == 'manual_rectangle':
                    # Convert rectangle to YOLO format
                    x1, y1, x2, y2 = annotation['rectangle']
                    
                    # Convert to YOLO format (center_x, center_y, width, height) normalized
                    center_x = (x1 + x2) / 2.0 / w
                    center_y = (y1 + y2) / 2.0 / h
                    bbox_w = abs(x2 - x1) / w
                    bbox_h = abs(y2 - y1) / h
                    
                    # Class ID (default to 0 for manual annotations)
                    class_id = annotation.get('class_id', 0)
                    
                    yolo_line = f"{class_id} {center_x:.6f} {center_y:.6f} {bbox_w:.6f} {bbox_h:.6f}"
                    yolo_lines.append(yolo_line)
                    
                elif annotation_type == 'bbox_segmentation':
                    # Convert SAM bbox result to YOLO format
                    if 'bbox' in annotation:
                        x1, y1, x2, y2 = annotation['bbox']
                        
                        center_x = (x1 + x2) / 2.0 / w
                        center_y = (y1 + y2) / 2.0 / h
                        bbox_w = abs(x2 - x1) / w
                        bbox_h = abs(y2 - y1) / h
                        
                        class_id = annotation.get('class_id', 1)  # Class 1 for AI-detected
                        confidence = annotation.get('confidence', 1.0)
                        
                        # YOLO format with confidence (if supported by your YOLO version)
                        yolo_line = f"{class_id} {center_x:.6f} {center_y:.6f} {bbox_w:.6f} {bbox_h:.6f}"
                        yolo_lines.append(yolo_line)
            
            # Write YOLO format file
            with open(output_file, 'w') as f:
                f.write('\n'.join(yolo_lines))
            
            result = {
                'status': 'success',
                'file': str(output_file),
                'annotations_count': len(yolo_lines),
                'format': 'YOLO'
            }
            
            logger.info(f"YOLO: YOLO format: {len(yolo_lines)} annotations → {output_file}")
            return result
            
        except Exception as e:
            logger.error(f"Error: YOLO export error: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'format': 'YOLO'
            }
    
    def _export_mask_format(self, annotations: List[Dict], image_shape: Tuple[int, int, int], 
                           output_dir: Path, image_name: str) -> Dict[str, Any]:
        """Export segmentation annotations as mask images."""
        
        try:
            h, w, _ = image_shape
            exported_masks = []
            
            for i, annotation in enumerate(annotations):
                annotation_type = annotation.get('type', 'unknown')
                mask_data = None
                
                if 'mask' in annotation and annotation['mask'] is not None:
                    mask_data = annotation['mask']
                elif annotation_type == 'manual_polygon' and 'polygon' in annotation:
                    # Convert polygon to mask
                    mask_data = self._polygon_to_mask(annotation['polygon'], (h, w))
                
                if mask_data is not None:
                    # Create individual mask file for each annotation
                    mask_filename = f"{image_name}_{annotation_type}_{i+1:03d}.png"
                    mask_path = output_dir / mask_filename
                    
                    # Ensure mask is proper format
                    if mask_data.dtype != np.uint8:
                        mask_data = (mask_data * 255).astype(np.uint8)
                    
                    # Save mask as PNG
                    cv2.imwrite(str(mask_path), mask_data)
                    
                    exported_masks.append({
                        'file': str(mask_path),
                        'type': annotation_type,
                        'confidence': annotation.get('confidence', 1.0)
                    })
            
            # Create combined mask with different values for each annotation
            if len(exported_masks) > 1:
                combined_mask = np.zeros((h, w), dtype=np.uint8)
                
                for i, annotation in enumerate(annotations):
                    mask_data = None
                    
                    if 'mask' in annotation and annotation['mask'] is not None:
                        mask_data = annotation['mask']
                    elif annotation['type'] == 'manual_polygon' and 'polygon' in annotation:
                        mask_data = self._polygon_to_mask(annotation['polygon'], (h, w))
                    
                    if mask_data is not None:
                        # Use different values for each mask (1, 2, 3, ...)
                        mask_binary = (mask_data > 0).astype(np.uint8)
                        combined_mask[mask_binary > 0] = i + 1
                
                # Save combined mask
                combined_path = output_dir / f"{image_name}_combined_mask.png"
                cv2.imwrite(str(combined_path), combined_mask)
                
                exported_masks.append({
                    'file': str(combined_path),
                    'type': 'combined_mask',
                    'annotation_count': len(annotations)
                })
            
            result = {
                'status': 'success',
                'masks': exported_masks,
                'masks_count': len(exported_masks),
                'format': 'PNG_MASK'
            }
            
            logger.info(f"🎭 Mask format: {len(exported_masks)} masks → {output_dir}")
            return result
            
        except Exception as e:
            logger.error(f"Error: Mask export error: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'format': 'PNG_MASK'
            }
    
    def _export_json_format(self, annotations: List[Dict], image_path: str, 
                           image_shape: Tuple[int, int, int], output_file: Path) -> Dict[str, Any]:
        """Export all annotations in JSON format (backup/complete format)."""
        
        try:
            # Convert numpy arrays to lists for JSON serialization
            serializable_annotations = []
            
            for annotation in annotations:
                serializable_annotation = {}
                
                for key, value in annotation.items():
                    if isinstance(value, np.ndarray):
                        if key == 'mask':
                            # Convert mask to run-length encoding for efficiency
                            serializable_annotation[key] = self._mask_to_rle(value)
                            serializable_annotation[key + '_format'] = 'rle'
                        else:
                            serializable_annotation[key] = value.tolist()
                    else:
                        serializable_annotation[key] = value
                
                serializable_annotations.append(serializable_annotation)
            
            # Create complete annotation file
            annotation_data = {
                'image_path': image_path,
                'image_shape': image_shape,
                'annotations': serializable_annotations,
                'annotation_count': len(annotations),
                'exported_at': time.time(),
                'exporter_version': '2.0',
                'format_info': {
                    'coordinate_system': 'image_pixels',
                    'mask_encoding': 'run_length_encoding',
                    'polygon_format': 'xy_pairs'
                }
            }
            
            # Write JSON file
            with open(output_file, 'w') as f:
                json.dump(annotation_data, f, indent=2, default=str)
            
            result = {
                'status': 'success',
                'file': str(output_file),
                'annotations_count': len(annotations),
                'format': 'JSON'
            }
            
            logger.info(f"📄 JSON format: {len(annotations)} annotations → {output_file}")
            return result
            
        except Exception as e:
            logger.error(f"Error: JSON export error: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'format': 'JSON'
            }
    
    def _polygon_to_mask(self, polygon: List[Tuple[int, int]], shape: Tuple[int, int]) -> np.ndarray:
        """Convert polygon points to binary mask."""
        
        h, w = shape
        mask = np.zeros((h, w), dtype=np.uint8)
        
        if len(polygon) >= 3:
            # Convert polygon to numpy array
            pts = np.array([(int(p[0]), int(p[1])) for p in polygon], dtype=np.int32)
            pts = pts.reshape((-1, 1, 2))
            
            # Fill polygon
            cv2.fillPoly(mask, [pts], 255)
        
        return mask
    
    def _mask_to_rle(self, mask: np.ndarray) -> Dict[str, Any]:
        """Convert binary mask to run-length encoding for efficient storage."""
        
        # Flatten mask
        flat_mask = mask.flatten()
        
        # Find run lengths
        runs = []
        current_val = flat_mask[0]
        current_len = 1
        
        for i in range(1, len(flat_mask)):
            if flat_mask[i] == current_val:
                current_len += 1
            else:
                runs.extend([current_len, current_val])
                current_val = flat_mask[i]
                current_len = 1
        
        # Add final run
        runs.extend([current_len, current_val])
        
        return {
            'runs': runs,
            'shape': mask.shape
        }
    
    def create_class_names_file(self, output_dir: str, class_names: List[str] = None):
        """Create YOLO class names file."""
        
        if class_names is None:
            class_names = ['manual_annotation', 'ai_detection']
        
        classes_file = Path(output_dir) / "classes.txt"
        
        with open(classes_file, 'w') as f:
            f.write('\n'.join(class_names))
        
        logger.info(f"📋 YOLO classes file created: {classes_file}")
        return str(classes_file)


def export_annotations_smart(annotations: List[Dict], image_path: str, 
                            image_shape: Tuple[int, int, int], output_dir: str = None) -> Dict[str, Any]:
    """Smart annotation export function - detects types and exports appropriately."""
    
    exporter = AnnotationExporter()
    return exporter.export_annotations(annotations, image_path, image_shape, output_dir)
