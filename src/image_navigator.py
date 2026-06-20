#!/usr/bin/env python3
"""
Image Navigator - Multi-Image Navigation System
Handles navigation through multiple images in a folder for annotation workflow.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class ImageNavigator:
    """Manages navigation through multiple images in a directory."""
    
    SUPPORTED_FORMATS = {
        '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'
    }
    
    def __init__(self):
        self.current_directory: Optional[Path] = None
        self.image_files: List[Path] = []
        self.current_index: int = -1
        self.current_image_path: Optional[Path] = None
        
        logger.info("Navigator: Image Navigator initialized")
    
    def set_directory(self, directory_path: str) -> bool:
        """Set the directory to navigate through."""
        
        try:
            dir_path = Path(directory_path)
            if not dir_path.exists() or not dir_path.is_dir():
                logger.warning(f"Directory not found: {directory_path}")
                return False
            
            self.current_directory = dir_path
            self.image_files = self._scan_images(dir_path)
            
            if self.image_files:
                self.current_index = 0
                self.current_image_path = self.image_files[0]
                logger.info(f"Navigator: Directory set: {len(self.image_files)} images found in {directory_path}")
                return True
            else:
                logger.warning(f"No supported images found in: {directory_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error: Error setting directory: {e}")
            return False
    
    def set_current_image(self, image_path: str) -> bool:
        """Set current image and automatically detect directory."""
        
        try:
            img_path = Path(image_path)
            if not img_path.exists():
                logger.warning(f"Image not found: {image_path}")
                return False
            
            # Set directory based on image location
            directory = img_path.parent
            if self.current_directory != directory:
                self.set_directory(str(directory))
            
            # Find current image in list
            for i, file_path in enumerate(self.image_files):
                if file_path.samefile(img_path):
                    self.current_index = i
                    self.current_image_path = img_path
                    logger.info(f"📷 Current image: {img_path.name} ({i+1}/{len(self.image_files)})")
                    return True
            
            # Image not in current directory list
            logger.warning(f"Image not found in directory list: {image_path}")
            return False
            
        except Exception as e:
            logger.error(f"Error: Error setting current image: {e}")
            return False
    
    def get_next_image(self) -> Optional[str]:
        """Get the next image in the sequence."""
        
        if not self.image_files or self.current_index < 0:
            logger.warning("No images available for navigation")
            return None
        
        next_index = (self.current_index + 1) % len(self.image_files)
        self.current_index = next_index
        self.current_image_path = self.image_files[next_index]
        
        logger.info(f"📷 Next image: {self.current_image_path.name} ({next_index+1}/{len(self.image_files)})")
        return str(self.current_image_path)
    
    def get_previous_image(self) -> Optional[str]:
        """Get the previous image in the sequence."""
        
        if not self.image_files or self.current_index < 0:
            logger.warning("No images available for navigation")
            return None
        
        prev_index = (self.current_index - 1) % len(self.image_files)
        self.current_index = prev_index
        self.current_image_path = self.image_files[prev_index]
        
        logger.info(f"📷 Previous image: {self.current_image_path.name} ({prev_index+1}/{len(self.image_files)})")
        return str(self.current_image_path)
    
    def get_current_image(self) -> Optional[str]:
        """Get the current image path."""
        
        if self.current_image_path:
            return str(self.current_image_path)
        return None
    
    def get_navigation_info(self) -> Tuple[int, int, str]:
        """Get navigation information (current_index, total_count, current_name)."""
        
        if not self.image_files or self.current_index < 0:
            return (0, 0, "")
        
        current_name = self.current_image_path.name if self.current_image_path else ""
        return (self.current_index + 1, len(self.image_files), current_name)
    
    def has_next(self) -> bool:
        """Check if there's a next image."""
        return bool(self.image_files and len(self.image_files) > 1)
    
    def has_previous(self) -> bool:
        """Check if there's a previous image."""
        return bool(self.image_files and len(self.image_files) > 1)
    
    def get_image_list(self) -> List[str]:
        """Get list of all image paths."""
        return [str(path) for path in self.image_files]
    
    def jump_to_image(self, index: int) -> Optional[str]:
        """Jump to a specific image by index."""
        
        if not self.image_files or index < 0 or index >= len(self.image_files):
            logger.warning(f"Invalid image index: {index}")
            return None
        
        self.current_index = index
        self.current_image_path = self.image_files[index]
        
        logger.info(f"📷 Jumped to image: {self.current_image_path.name} ({index+1}/{len(self.image_files)})")
        return str(self.current_image_path)
    
    def _scan_images(self, directory: Path) -> List[Path]:
        """Scan directory for supported image files."""
        
        image_files = []
        
        try:
            for file_path in directory.iterdir():
                if (file_path.is_file() and 
                    file_path.suffix.lower() in self.SUPPORTED_FORMATS):
                    image_files.append(file_path)
            
            # Sort alphabetically for consistent order
            image_files.sort(key=lambda x: x.name.lower())
            
            logger.info(f"Navigator: Found {len(image_files)} images in {directory}")
            return image_files
            
        except Exception as e:
            logger.error(f"Error: Error scanning directory: {e}")
            return []
    
    def get_stats(self) -> dict:
        """Get navigation statistics."""
        
        return {
            'total_images': len(self.image_files),
            'current_index': self.current_index + 1 if self.current_index >= 0 else 0,
            'current_directory': str(self.current_directory) if self.current_directory else None,
            'current_image': str(self.current_image_path) if self.current_image_path else None,
            'has_next': self.has_next(),
            'has_previous': self.has_previous()
        }
