"""
Optimized weight loader for faster model loading on Windows.
Implements caching, lazy loading, and progress tracking.
"""

import os
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import pickle

logger = logging.getLogger(__name__)


class WeightLoader:
    """Optimized weight loading with caching for Windows."""
    
    def __init__(self, cache_dir: str = "weights/.cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_models = {}
        
    def get_cache_path(self, model_name: str) -> Path:
        """Get cache file path for a model."""
        return self.cache_dir / f"{model_name}.cache"
    
    def is_cached(self, model_name: str) -> bool:
        """Check if model is cached."""
        return self.get_cache_path(model_name).exists()
    
    def load_with_progress(self, model_path: str, model_name: str, 
                          progress_callback=None) -> Any:
        """
        Load model weights with progress tracking.
        
        Args:
            model_path: Path to model weights
            model_name: Name of the model
            progress_callback: Function to call with progress updates
            
        Returns:
            Loaded model or model info
        """
        start_time = time.time()
        
        # Check if already loaded in memory
        if model_name in self.loaded_models:
            logger.info(f"Using cached {model_name} from memory")
            if progress_callback:
                progress_callback(100, "Loaded from memory")
            return self.loaded_models[model_name]
        
        if progress_callback:
            progress_callback(10, f"Loading {model_name}...")
        
        # Check file exists
        if not os.path.exists(model_path):
            logger.warning(f"Model file not found: {model_path}")
            if progress_callback:
                progress_callback(0, "Model file not found")
            return None
        
        if progress_callback:
            progress_callback(30, "Reading weights...")
        
        try:
            # Import here to avoid slow imports at startup
            import torch
            
            if progress_callback:
                progress_callback(50, "Loading into memory...")
            
            # Load weights with map_location for Windows compatibility
            weights = torch.load(
                model_path, 
                map_location='cpu'  # Load to CPU first for faster loading
            )
            
            if progress_callback:
                progress_callback(80, "Initializing model...")
            
            # Cache the model info
            self.loaded_models[model_name] = {
                'path': model_path,
                'weights': weights,
                'loaded_at': time.time()
            }
            
            load_time = time.time() - start_time
            logger.info(f"Loaded {model_name} in {load_time:.2f}s")
            
            if progress_callback:
                progress_callback(100, f"Ready ({load_time:.1f}s)")
            
            return weights
            
        except Exception as e:
            logger.error(f"Error loading {model_name}: {e}")
            if progress_callback:
                progress_callback(0, f"Error: {str(e)}")
            return None
    
    def preload_models(self, model_configs: Dict[str, str], 
                       progress_callback=None):
        """
        Preload multiple models in background.
        
        Args:
            model_configs: Dict of model_name -> model_path
            progress_callback: Function for progress updates
        """
        total = len(model_configs)
        
        for idx, (name, path) in enumerate(model_configs.items()):
            if progress_callback:
                overall_progress = int((idx / total) * 100)
                progress_callback(overall_progress, f"Loading {name}...")
            
            self.load_with_progress(path, name)
    
    def clear_cache(self):
        """Clear loaded models from memory."""
        self.loaded_models.clear()
        logger.info("Cleared model cache")
    
    def get_memory_usage(self) -> int:
        """Get approximate memory usage in MB."""
        try:
            import sys
            total = 0
            for model_data in self.loaded_models.values():
                if 'weights' in model_data:
                    total += sys.getsizeof(model_data['weights'])
            return total // (1024 * 1024)  # Convert to MB
        except:
            return 0


class LazyModelLoader:
    """Lazy loader that only loads models when needed."""
    
    def __init__(self):
        self.sam_model = None
        self.yolo_model = None
        self.weight_loader = WeightLoader()
        
    def get_sam_model(self, progress_callback=None):
        """Load SAM model on first access."""
        if self.sam_model is None:
            logger.info("Lazy loading SAM model...")
            from models.sam.sam_model import SAMModel
            
            self.sam_model = SAMModel()
            
            if progress_callback:
                progress_callback(50, "Loading SAM...")
            
            self.sam_model.load_model()
            
            if progress_callback:
                progress_callback(100, "SAM ready")
        
        return self.sam_model
    
    def get_yolo_model(self, progress_callback=None):
        """Load YOLO model on first access."""
        if self.yolo_model is None:
            logger.info("Lazy loading YOLO model...")
            from models.yolo.yolo_model import YOLOModel
            
            self.yolo_model = YOLOModel()
            
            if progress_callback:
                progress_callback(50, "Loading YOLO...")
            
            self.yolo_model.load_model()
            
            if progress_callback:
                progress_callback(100, "YOLO ready")
        
        return self.yolo_model
    
    def unload_models(self):
        """Unload models to free memory."""
        if self.sam_model:
            if hasattr(self.sam_model, 'cleanup'):
                self.sam_model.cleanup()
            self.sam_model = None
            
        if self.yolo_model:
            if hasattr(self.yolo_model, 'cleanup'):
                self.yolo_model.cleanup()
            self.yolo_model = None
        
        # Clear CUDA cache if available
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except:
            pass
        
        logger.info("Models unloaded")


# Global lazy loader instance
_lazy_loader = None

def get_lazy_loader() -> LazyModelLoader:
    """Get global lazy loader instance."""
    global _lazy_loader
    if _lazy_loader is None:
        _lazy_loader = LazyModelLoader()
    return _lazy_loader

