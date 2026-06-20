#!/usr/bin/env python3
"""
Auto-save manager for annotation workflows.
Handles automatic saving and loading during image navigation.
"""

import os
import json
import time
import logging
import gc
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import numpy as np
import cv2

logger = logging.getLogger(__name__)


class AutoSaveManager:
    """Manages automatic saving and loading of annotations during navigation."""
    
    def __init__(self, auto_save_dir: str = None):
        self.auto_save_dir = Path(auto_save_dir) if auto_save_dir else Path("data/auto_save")
        self.auto_save_dir.mkdir(parents=True, exist_ok=True)
        
        # Auto-save settings
        self.enabled = True
        self.save_on_navigation = True
        self.load_on_navigation = True
        self.auto_export_formats = True
        
        # Performance tracking
        self.save_count = 0
        self.load_count = 0
        self.total_save_time = 0.0
        self.total_load_time = 0.0
        
        # Memory management
        self.max_cached_annotations = 10
        self.annotation_cache = {}  # {image_hash: annotations}
        self.cache_order = []  # LRU cache
        
        logger.info(f"Auto Save Manager initialized: {self.auto_save_dir}")
    
    def set_auto_save_directory(self, directory: str):
        """Set auto-save directory."""
        
        self.auto_save_dir = Path(directory)
        self.auto_save_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Auto-save directory set: {self.auto_save_dir}")
    
    def enable_auto_save(self, enabled: bool = True):
        """Toggle auto-save."""
        
        self.enabled = enabled
        logger.info(f"Auto-save: {'enabled' if enabled else 'disabled'}")
    
    def save_annotations(self, image_path: str, annotations: List[Dict[str, Any]], 
                        image_shape: Tuple[int, int, int] = None) -> bool:
        """Automatically save annotations for an image."""
        
        if not self.enabled or not annotations:
            return False
        
        try:
            start_time = time.time()
            
            # Generate save file path based on image
            save_file = self._get_save_file_path(image_path)
            
            # Convert numpy arrays to serializable format
            serializable_annotations = self._serialize_annotations(annotations)
            
            # Create save data
            save_data = {
                'image_path': image_path,
                'image_shape': list(image_shape) if image_shape else None,
                'annotations': serializable_annotations,
                'annotation_count': len(annotations),
                'saved_at': time.time(),
                'auto_save_version': '2.0'
            }
            
            # Save to JSON file
            with open(save_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            # Update cache with memory limit
            image_hash = self._get_image_hash(image_path)
            self._update_cache(image_hash, annotations)
            
            # Update statistics
            save_time = time.time() - start_time
            self.save_count += 1
            self.total_save_time += save_time
            
            logger.info(f"Auto-saved {len(annotations)} annotations for {Path(image_path).name} ({save_time:.3f}s)")
            
            # Clear memory after save
            gc.collect()
            
            return True
            
        except Exception as e:
            logger.error(f"Auto-save error: {e}")
            return False
    
    def load_annotations(self, image_path: str) -> Optional[List[Dict[str, Any]]]:
        """Automatically load annotations for an image."""
        
        if not self.enabled:
            return None
        
        try:
            start_time = time.time()
            
            # Check cache first (memory efficient)
            image_hash = self._get_image_hash(image_path)
            if image_hash in self.annotation_cache:
                logger.info(f"Loaded annotations from cache for {Path(image_path).name}")
                return self.annotation_cache[image_hash]
            
            # Load from file
            save_file = self._get_save_file_path(image_path)
            
            if not save_file.exists():
                return None  # No saved annotations for this image
            
            # Load from JSON
            with open(save_file, 'r') as f:
                save_data = json.load(f)
            
            # Deserialize annotations
            annotations = self._deserialize_annotations(save_data.get('annotations', []))
            
            # Update cache with memory limit
            self._update_cache(image_hash, annotations)
            
            # Update statistics
            load_time = time.time() - start_time
            self.load_count += 1
            self.total_load_time += load_time
            
            logger.info(f"Auto-loaded {len(annotations)} annotations for {Path(image_path).name} ({load_time:.3f}s)")
            
            # Clear memory after load
            gc.collect()
            
            return annotations
            
        except Exception as e:
            logger.error(f"Auto-load error: {e}")
            return None
    
    def has_saved_annotations(self, image_path: str) -> bool:
        """Check if image has saved annotations."""
        
        save_file = self._get_save_file_path(image_path)
        return save_file.exists()
    
    def delete_saved_annotations(self, image_path: str) -> bool:
        """Delete saved annotations for an image."""
        
        try:
            save_file = self._get_save_file_path(image_path)
            
            if save_file.exists():
                save_file.unlink()
                
                # Remove from cache
                image_hash = self._get_image_hash(image_path)
                if image_hash in self.annotation_cache:
                    del self.annotation_cache[image_hash]
                    if image_hash in self.cache_order:
                        self.cache_order.remove(image_hash)
                
                logger.info(f"Deleted auto-save for {Path(image_path).name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Delete auto-save error: {e}")
            return False
    
    def clear_all_auto_saves(self) -> int:
        """Clear all auto-save files and cache."""
        
        try:
            count = 0
            
            for save_file in self.auto_save_dir.glob("*.json"):
                save_file.unlink()
                count += 1
            
            # Clear cache
            self.annotation_cache.clear()
            self.cache_order.clear()
            
            # Clear memory
            gc.collect()
            
            logger.info(f"Cleared {count} auto-save files")
            return count
            
        except Exception as e:
            logger.error(f"Clear auto-saves error: {e}")
            return 0
    
    def _get_save_file_path(self, image_path: str) -> Path:
        """Get the save file path for an image."""
        
        # Create unique filename based on image path hash
        image_hash = self._get_image_hash(image_path)
        save_filename = f"auto_save_{image_hash}.json"
        
        return self.auto_save_dir / save_filename
    
    def _get_image_hash(self, image_path: str) -> str:
        """Get a hash for the image path."""
        
        # Use MD5 hash of absolute path for consistency
        abs_path = str(Path(image_path).resolve())
        return hashlib.md5(abs_path.encode()).hexdigest()[:16]
    
    def _serialize_annotations(self, annotations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert annotations to JSON-serializable format."""
        
        serialized = []
        
        for annotation in annotations:
            serialized_ann = {}
            
            for key, value in annotation.items():
                if isinstance(value, np.ndarray):
                    if key == 'mask':
                        # Convert mask to run-length encoding for compact storage
                        serialized_ann[key] = self._mask_to_rle(value)
                        serialized_ann[key + '_format'] = 'rle'
                        serialized_ann[key + '_shape'] = value.shape
                    else:
                        serialized_ann[key] = value.tolist()
                else:
                    serialized_ann[key] = value
            
            serialized.append(serialized_ann)
        
        return serialized
    
    def _deserialize_annotations(self, annotations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert JSON annotations back to runtime format."""
        
        deserialized = []
        
        for annotation in annotations:
            deserialized_ann = {}
            
            for key, value in annotation.items():
                if key.endswith('_format') or key.endswith('_shape'):
                    continue  # Skip metadata keys
                
                if key == 'mask' and isinstance(value, dict) and value.get('format') == 'rle':
                    # Reconstruct mask from RLE
                    mask_shape = annotation.get('mask_shape', (100, 100))
                    deserialized_ann[key] = self._rle_to_mask(value, mask_shape)
                else:
                    deserialized_ann[key] = value
            
            deserialized.append(deserialized_ann)
        
        return deserialized
    
    def _mask_to_rle(self, mask: np.ndarray) -> Dict[str, Any]:
        """Convert mask to run-length encoding."""
        
        # Simple RLE encoding
        flat_mask = mask.flatten()
        
        rle = []
        current_val = int(flat_mask[0])
        count = 1
        
        for i in range(1, len(flat_mask)):
            if flat_mask[i] == current_val:
                count += 1
            else:
                rle.extend([count, current_val])
                current_val = int(flat_mask[i])
                count = 1
        
        rle.extend([count, current_val])
        
        return {
            'format': 'rle',
            'data': rle,
            'shape': list(mask.shape)
        }
    
    def _rle_to_mask(self, rle_data: Dict[str, Any], shape: Tuple[int, ...]) -> np.ndarray:
        """Reconstruct mask from run-length encoding."""
        
        rle = rle_data.get('data', [])
        mask_shape = tuple(rle_data.get('shape', shape))
        
        # Decode RLE
        flat_mask = []
        for i in range(0, len(rle), 2):
            if i + 1 < len(rle):
                count = rle[i]
                value = rle[i + 1]
                flat_mask.extend([value] * count)
        
        # Reshape to original shape
        mask = np.array(flat_mask, dtype=np.uint8).reshape(mask_shape)
        
        return mask
    
    def _update_cache(self, image_hash: str, annotations: List[Dict[str, Any]]):
        """Update cache with memory management (LRU strategy)."""
        
        # Add to cache
        self.annotation_cache[image_hash] = annotations
        
        # Update LRU order
        if image_hash in self.cache_order:
            self.cache_order.remove(image_hash)
        self.cache_order.append(image_hash)
        
        # Enforce cache size limit (memory management)
        while len(self.cache_order) > self.max_cached_annotations:
            oldest_hash = self.cache_order.pop(0)
            if oldest_hash in self.annotation_cache:
                del self.annotation_cache[oldest_hash]
                logger.debug(f"Evicted old cache entry: {oldest_hash}")
        
        # Clear memory
        if len(self.cache_order) > self.max_cached_annotations // 2:
            gc.collect()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get auto-save statistics."""
        
        avg_save_time = self.total_save_time / max(1, self.save_count)
        avg_load_time = self.total_load_time / max(1, self.load_count)
        
        # Count auto-save files
        auto_save_files = list(self.auto_save_dir.glob("*.json"))
        
        return {
            'enabled': self.enabled,
            'auto_save_directory': str(self.auto_save_dir),
            'save_count': self.save_count,
            'load_count': self.load_count,
            'avg_save_time': avg_save_time,
            'avg_load_time': avg_load_time,
            'cached_images': len(self.annotation_cache),
            'saved_files_count': len(auto_save_files),
            'cache_hit_rate': self._calculate_cache_hit_rate()
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        
        if self.load_count == 0:
            return 0.0
        
        # Estimate based on cache usage
        # This is a simplified calculation
        cache_hits = min(len(self.annotation_cache), self.load_count)
        return (cache_hits / self.load_count) * 100.0
    
    def cleanup_memory(self):
        """Clean up memory used by cache."""
        
        # Keep only most recent items
        while len(self.cache_order) > self.max_cached_annotations // 2:
            oldest_hash = self.cache_order.pop(0)
            if oldest_hash in self.annotation_cache:
                del self.annotation_cache[oldest_hash]
        
        # Force garbage collection
        gc.collect()
        
        logger.info(f"Cleanup: Auto-save cache cleaned: {len(self.annotation_cache)} items remaining")
    
    def get_formatted_statistics(self) -> str:
        """Get formatted statistics string."""
        
        stats = self.get_statistics()
        
        return f"""💾 Auto-Save Statistics:
   Status: {'Success: Enabled' if stats['enabled'] else 'Error: Disabled'}
   Saved: {stats['save_count']} images
   Loaded: {stats['load_count']} images
   Avg Save Time: {stats['avg_save_time']:.3f}s
   Avg Load Time: {stats['avg_load_time']:.3f}s
   Cache Entries: {stats['cached_images']}/{self.max_cached_annotations}
   Cache Hit Rate: {stats['cache_hit_rate']:.1f}%
   Total Auto-saves: {stats['saved_files_count']} files"""
