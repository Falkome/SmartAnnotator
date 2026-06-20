#!/usr/bin/env python3
"""
Label Manager - Class/Label Management System
Manages annotation classes and labels for the Smart Annotator.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class LabelManager:
    """Manages annotation classes and labels."""
    
    def __init__(self, project_file: str = None):
        # Set default project file if none provided
        if project_file is None:
            project_file = str(Path("data") / "label_classes.json")
        
        self.project_file = project_file
        self.classes = {}  # {class_id: class_info}
        self.current_class_id = 0
        self.next_id = 1
        self.auto_save = True  # Auto-save changes to file
        
        # Load from project file if it exists, otherwise load defaults
        if Path(project_file).exists():
            logger.info(f"Label: Loading classes from {project_file}")
            if self.load_from_file(project_file):
                logger.info(f"Label: Loaded {len(self.classes)} classes from file")
            else:
                logger.warning("Label: Failed to load from file, loading defaults")
                self.load_default_classes()
        else:
            logger.info("Label: No saved classes found, loading defaults")
            self.load_default_classes()
            # Save defaults to file for future use
            self.save_to_file()
        
        logger.info("Label: Label Manager initialized")
    
    def load_default_classes(self):
        """Load default annotation classes."""
        
        default_classes = [
            {"name": "object", "color": "#FF0000", "description": "General object"},
            {"name": "person", "color": "#00FF00", "description": "Person/human"},
            {"name": "vehicle", "color": "#0000FF", "description": "Vehicle/transport"},
            {"name": "animal", "color": "#FFFF00", "description": "Animal/pet"},
            {"name": "building", "color": "#FF00FF", "description": "Building/structure"}
        ]
        
        for i, class_info in enumerate(default_classes):
            self.add_class(
                name=class_info["name"],
                color=class_info["color"], 
                description=class_info["description"],
                class_id=i
            )
        
        self.current_class_id = 0  # Start with first class
        self.next_id = len(default_classes)
        
        logger.info(f"Label: Loaded {len(default_classes)} default classes")
    
    def add_class(self, name: str, color: str = "#FF0000", description: str = "", 
                  class_id: int = None) -> int:
        """Add a new annotation class."""
        
        if class_id is None:
            class_id = self.next_id
            self.next_id += 1
        else:
            self.next_id = max(self.next_id, class_id + 1)
        
        # Check for duplicate names
        for existing_id, existing_class in self.classes.items():
            if existing_class["name"].lower() == name.lower():
                logger.warning(f"Class '{name}' already exists with ID {existing_id}")
                return existing_id
        
        class_info = {
            "id": class_id,
            "name": name,
            "color": color,
            "description": description,
            "created_at": None,  # Will be set when saved
            "annotation_count": 0
        }
        
        self.classes[class_id] = class_info
        
        logger.info(f"Label: Added class: {name} (ID: {class_id})")
        
        # Auto-save to file
        if self.auto_save and self.project_file:
            self.save_to_file()
        
        return class_id
    
    def remove_class(self, class_id: int) -> bool:
        """Remove an annotation class."""
        
        if class_id not in self.classes:
            logger.warning(f"Class ID {class_id} not found")
            return False
        
        class_name = self.classes[class_id]["name"]
        del self.classes[class_id]
        
        # Update current class if it was deleted
        if self.current_class_id == class_id:
            if self.classes:
                self.current_class_id = min(self.classes.keys())
            else:
                self.current_class_id = 0
        
        logger.info(f"Label: Removed class: {class_name} (ID: {class_id})")
        
        # Auto-save to file
        if self.auto_save and self.project_file:
            self.save_to_file()
        
        return True
    
    def update_class(self, class_id: int, name: str = None, color: str = None, 
                    description: str = None) -> bool:
        """Update an existing class."""
        
        if class_id not in self.classes:
            logger.warning(f"Class ID {class_id} not found")
            return False
        
        if name is not None:
            self.classes[class_id]["name"] = name
        if color is not None:
            self.classes[class_id]["color"] = color
        if description is not None:
            self.classes[class_id]["description"] = description
        
        logger.info(f"Label: Updated class ID {class_id}: {self.classes[class_id]['name']}")
        
        # Auto-save to file
        if self.auto_save and self.project_file:
            self.save_to_file()
        
        return True
    
    def get_class(self, class_id: int) -> Optional[Dict[str, Any]]:
        """Get class information by ID."""
        return self.classes.get(class_id, None)
    
    def get_class_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get class information by name."""
        for class_info in self.classes.values():
            if class_info["name"].lower() == name.lower():
                return class_info
        return None
    
    def get_all_classes(self) -> Dict[int, Dict[str, Any]]:
        """Get all classes."""
        return self.classes.copy()
    
    def get_class_list(self) -> List[Dict[str, Any]]:
        """Get classes as a sorted list."""
        return sorted(self.classes.values(), key=lambda x: x["id"])
    
    def set_current_class(self, class_id: int) -> bool:
        """Set the currently selected class."""
        
        if class_id not in self.classes:
            logger.warning(f"Class ID {class_id} not found")
            return False
        
        self.current_class_id = class_id
        logger.info(f"Label: Current class set to: {self.classes[class_id]['name']} (ID: {class_id})")
        return True
    
    def get_current_class(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected class."""
        return self.classes.get(self.current_class_id, None)
    
    def get_current_class_id(self) -> int:
        """Get the currently selected class ID."""
        return self.current_class_id
    
    def increment_annotation_count(self, class_id: int):
        """Increment annotation count for a class."""
        if class_id in self.classes:
            self.classes[class_id]["annotation_count"] += 1
    
    def get_class_color_hex(self, class_id: int) -> str:
        """Get class color as hex string."""
        class_info = self.get_class(class_id)
        return class_info["color"] if class_info else "#FF0000"
    
    def get_class_color_rgb(self, class_id: int) -> Tuple[int, int, int]:
        """Get class color as RGB tuple."""
        hex_color = self.get_class_color_hex(class_id)
        
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b)
        except ValueError:
            return (255, 0, 0)  # Default red
    
    def save_to_file(self, file_path: str = None) -> bool:
        """Save classes to file."""
        
        if file_path is None:
            file_path = self.project_file
        
        if file_path is None:
            logger.error("No file path provided for saving classes")
            return False
        
        try:
            # Update timestamps
            import time
            current_time = time.time()
            
            for class_info in self.classes.values():
                if class_info["created_at"] is None:
                    class_info["created_at"] = current_time
            
            # Create save data
            save_data = {
                "classes": self.classes,
                "current_class_id": self.current_class_id,
                "next_id": self.next_id,
                "saved_at": current_time,
                "version": "2.0"
            }
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(save_data, f, indent=2, default=str)
            
            logger.info(f"Label: Classes saved to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error: Failed to save classes: {e}")
            return False
    
    def load_from_file(self, file_path: str) -> bool:
        """Load classes from file."""
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.classes = data.get("classes", {})
            self.current_class_id = data.get("current_class_id", 0)
            self.next_id = data.get("next_id", 1)
            
            # Convert string keys back to integers
            self.classes = {int(k): v for k, v in self.classes.items()}
            
            logger.info(f"Label: Loaded {len(self.classes)} classes from: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error: Failed to load classes: {e}")
            return False
    
    def export_yolo_classes(self, output_file: str) -> bool:
        """Export classes in YOLO format."""
        
        try:
            class_names = []
            
            # Sort by ID to maintain order
            for class_id in sorted(self.classes.keys()):
                class_names.append(self.classes[class_id]["name"])
            
            with open(output_file, 'w') as f:
                f.write('\n'.join(class_names))
            
            logger.info(f"📋 YOLO classes exported to: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error: Failed to export YOLO classes: {e}")
            return False
    
    def import_yolo_classes(self, input_file: str, clear_existing: bool = False) -> bool:
        """Import classes from YOLO format."""
        
        try:
            if clear_existing:
                self.classes.clear()
                self.next_id = 0
            
            with open(input_file, 'r') as f:
                lines = f.readlines()
            
            imported_count = 0
            for i, line in enumerate(lines):
                class_name = line.strip()
                if class_name:
                    self.add_class(
                        name=class_name,
                        color=self._generate_color_for_id(i),
                        description=f"Imported class: {class_name}"
                    )
                    imported_count += 1
            
            # Set current class to first imported class
            if self.classes:
                self.current_class_id = min(self.classes.keys())
            
            logger.info(f"📋 Imported {imported_count} classes from: {input_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error: Failed to import YOLO classes: {e}")
            return False
    
    def _generate_color_for_id(self, class_id: int) -> str:
        """Generate a unique color for a class ID."""
        
        colors = [
            "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", 
            "#00FFFF", "#FFA500", "#800080", "#FFC0CB", "#A52A2A",
            "#808080", "#000080", "#008080", "#800000", "#808000"
        ]
        
        return colors[class_id % len(colors)]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get label manager statistics."""
        
        total_annotations = sum(c["annotation_count"] for c in self.classes.values())
        
        return {
            "total_classes": len(self.classes),
            "current_class": self.get_current_class(),
            "total_annotations": total_annotations,
            "classes_with_annotations": sum(1 for c in self.classes.values() if c["annotation_count"] > 0),
            "most_used_class": max(self.classes.values(), key=lambda x: x["annotation_count"]) if self.classes else None
        }
