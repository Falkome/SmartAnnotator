#!/usr/bin/env python3
"""
Label widget for managing annotation classes.
"""

import logging
from typing import Dict, Any, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox, 
    QPushButton, QLabel, QColorDialog, QInputDialog, QMessageBox,
    QListWidget, QListWidgetItem, QDialog, QLineEdit, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

logger = logging.getLogger(__name__)


class ClassEditDialog(QDialog):
    """Dialog for editing class properties."""
    
    def __init__(self, class_info: Dict[str, Any] = None, parent=None):
        super().__init__(parent)
        
        self.class_info = class_info or {}
        self.selected_color = self.class_info.get("color", "#FF0000")
        
        # Set window flags to ensure dialog shows on top
        self.setWindowFlags(
            Qt.Dialog | 
            Qt.WindowTitleHint | 
            Qt.WindowCloseButtonHint |
            Qt.WindowStaysOnTopHint
        )
        self.setModal(True)
        self.init_ui()
        
        logger.info("ClassEditDialog: Dialog initialized")
    
    def init_ui(self):
        """Initialize the dialog UI."""
        
        if self.class_info.get("name"):
            self.setWindowTitle(f"Edit Class: {self.class_info.get('name')}")
        else:
            self.setWindowTitle("Add New Class")
        
        self.setMinimumSize(350, 250)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Class name
        name_group = QGroupBox("Class Name")
        name_layout = QVBoxLayout(name_group)
        self.name_edit = QLineEdit(self.class_info.get("name", ""))
        self.name_edit.setPlaceholderText("Enter class name (e.g., car, person, dog)")
        name_layout.addWidget(self.name_edit)
        layout.addWidget(name_group)
        
        # Color selection
        color_group = QGroupBox("Color")
        color_layout = QHBoxLayout(color_group)
        self.color_btn = QPushButton(f"  {self.selected_color}  ")
        self.color_btn.clicked.connect(self.choose_color)
        self.color_btn.setStyleSheet(f"background-color: {self.selected_color}; color: white; font-weight: bold; padding: 10px;")
        self.color_btn.setToolTip("Click to choose color")
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()
        layout.addWidget(color_group)
        
        # Description
        desc_group = QGroupBox("Description (Optional)")
        desc_layout = QVBoxLayout(desc_group)
        self.desc_edit = QTextEdit(self.class_info.get("description", ""))
        self.desc_edit.setMaximumHeight(60)
        self.desc_edit.setPlaceholderText("Brief description of this class")
        desc_layout.addWidget(self.desc_edit)
        layout.addWidget(desc_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("✅ Save")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px 20px;")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 8px 20px;")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def choose_color(self):
        """Open color chooser dialog."""
        try:
            color = QColorDialog.getColor(QColor(self.selected_color), self, "Choose Class Color")
            if color.isValid():
                self.selected_color = color.name()
                self.color_btn.setText(f"  {self.selected_color}  ")
                self.color_btn.setStyleSheet(f"background-color: {self.selected_color}; color: white; font-weight: bold; padding: 10px;")
                logger.info(f"ClassEditDialog: Color selected: {self.selected_color}")
        except Exception as e:
            logger.error(f"ClassEditDialog: Color selection error: {e}")
    
    def get_class_data(self) -> Dict[str, Any]:
        """Get the edited class data."""
        return {
            "name": self.name_edit.text().strip(),
            "color": self.selected_color,
            "description": self.desc_edit.toPlainText().strip()
        }
    
    def showEvent(self, event):
        """Handle show event to ensure dialog is visible."""
        super().showEvent(event)
        # Center on parent or screen
        if self.parent():
            parent_geo = self.parent().geometry()
            self.move(
                parent_geo.center().x() - self.width() // 2,
                parent_geo.center().y() - self.height() // 2
            )
        self.raise_()
        self.activateWindow()
        self.name_edit.setFocus()
        logger.info("ClassEditDialog: Dialog shown")


class LabelWidget(QWidget):
    """Widget for managing annotation classes and labels."""
    
    # Signals
    class_changed = pyqtSignal(int)  # Emitted when current class changes
    class_added = pyqtSignal(dict)   # Emitted when new class is added
    class_updated = pyqtSignal(int, dict)  # Emitted when class is updated
    class_removed = pyqtSignal(int)  # Emitted when class is removed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.label_manager = None  # Will be set externally
        self.current_class_id = 0
        
        self.init_ui()
        logger.info("Label: Label Widget initialized")
    
    def init_ui(self):
        """Initialize the label widget UI."""
        
        layout = QVBoxLayout(self)
        
        # Current class selection
        current_group = QGroupBox("Label: Current Label")
        current_layout = QVBoxLayout(current_group)
        
        # Class selector dropdown
        self.class_combo = QComboBox()
        self.class_combo.currentIndexChanged.connect(self.on_class_selected)
        current_layout.addWidget(self.class_combo)
        
        # Current class info display
        self.current_class_label = QLabel("No class selected")
        self.current_class_label.setStyleSheet("""
            QLabel {
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 8px;
                background-color: #ecf0f1;
                font-weight: bold;
            }
        """)
        current_layout.addWidget(self.current_class_label)
        
        layout.addWidget(current_group)
        
        # Class management
        management_group = QGroupBox("📝 Class Management")
        management_layout = QVBoxLayout(management_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.add_class_btn = QPushButton("➕ Add Class")
        self.add_class_btn.clicked.connect(self.add_class)
        button_layout.addWidget(self.add_class_btn)
        
        self.edit_class_btn = QPushButton("✏️ Edit Class")
        self.edit_class_btn.clicked.connect(self.edit_current_class)
        button_layout.addWidget(self.edit_class_btn)
        
        self.remove_class_btn = QPushButton("🗑️ Remove")
        self.remove_class_btn.clicked.connect(self.remove_current_class)
        button_layout.addWidget(self.remove_class_btn)
        
        management_layout.addLayout(button_layout)
        
        # Classes list
        self.classes_list = QListWidget()
        self.classes_list.setMaximumHeight(150)
        self.classes_list.itemClicked.connect(self.on_list_item_clicked)
        management_layout.addWidget(self.classes_list)
        
        layout.addWidget(management_group)
        
        # Statistics
        stats_group = QGroupBox("Monitor: Label Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel("No statistics available")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        
        layout.addWidget(stats_group)
    
    def set_label_manager(self, label_manager):
        """Set the label manager and update UI."""
        
        self.label_manager = label_manager
        self.refresh_ui()
        
        logger.info("Label: Label manager set")
    
    def refresh_ui(self):
        """Refresh the UI with current label manager data."""
        
        if not self.label_manager:
            return
        
        # Update combo box
        self.class_combo.blockSignals(True)
        self.class_combo.clear()
        
        classes = self.label_manager.get_class_list()
        for class_info in classes:
            self.class_combo.addItem(
                f"{class_info['id']}: {class_info['name']}", 
                class_info['id']
            )
        
        # Set current selection
        current_class = self.label_manager.get_current_class()
        if current_class:
            for i in range(self.class_combo.count()):
                if self.class_combo.itemData(i) == current_class['id']:
                    self.class_combo.setCurrentIndex(i)
                    break
        
        self.class_combo.blockSignals(False)
        
        # Update current class display
        self.update_current_class_display()
        
        # Update classes list
        self.refresh_classes_list()
        
        # Update statistics
        self.update_statistics()
    
    def update_current_class_display(self):
        """Update the current class display."""
        
        if not self.label_manager:
            self.current_class_label.setText("No label manager")
            return
        
        current_class = self.label_manager.get_current_class()
        if current_class:
            class_name = current_class['name']
            class_color = current_class['color']
            class_desc = current_class.get('description', '')
            annotation_count = current_class.get('annotation_count', 0)
            
            display_text = f"Label: {class_name}"
            if class_desc:
                display_text += f"\n📝 {class_desc}"
            display_text += f"\nMonitor: Annotations: {annotation_count}"
            
            self.current_class_label.setText(display_text)
            self.current_class_label.setStyleSheet(f"""
                QLabel {{
                    border: 2px solid {class_color};
                    border-radius: 5px;
                    padding: 8px;
                    background-color: {class_color}20;
                    font-weight: bold;
                }}
            """)
        else:
            self.current_class_label.setText("No class selected")
            self.current_class_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #95a5a6;
                    border-radius: 5px;
                    padding: 8px;
                    background-color: #ecf0f1;
                    font-weight: bold;
                }
            """)
    
    def refresh_classes_list(self):
        """Refresh the classes list widget."""
        
        self.classes_list.clear()
        
        if not self.label_manager:
            return
        
        classes = self.label_manager.get_class_list()
        for class_info in classes:
            item_text = f"ID {class_info['id']}: {class_info['name']} ({class_info['annotation_count']})"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, class_info['id'])
            
            # Set background color
            color = QColor(class_info['color'])
            color.setAlpha(50)  # Make it semi-transparent
            item.setBackground(color)
            
            self.classes_list.addItem(item)
    
    def update_statistics(self):
        """Update the statistics display."""
        
        if not self.label_manager:
            self.stats_label.setText("No statistics available")
            return
        
        stats = self.label_manager.get_statistics()
        
        stats_text = f"Monitor: Label Statistics:\n"
        stats_text += f"   Total Classes: {stats['total_classes']}\n"
        stats_text += f"   Total Annotations: {stats['total_annotations']}\n"
        stats_text += f"   Classes Used: {stats['classes_with_annotations']}/{stats['total_classes']}"
        
        if stats['most_used_class']:
            most_used = stats['most_used_class']
            stats_text += f"\n\n🏆 Most Used:\n   {most_used['name']} ({most_used['annotation_count']} annotations)"
        
        self.stats_label.setText(stats_text)
    
    def on_class_selected(self, index: int):
        """Handle class selection change."""
        
        if not self.label_manager or index < 0:
            return
        
        class_id = self.class_combo.itemData(index)
        if class_id is not None:
            self.label_manager.set_current_class(class_id)
            self.current_class_id = class_id
            self.update_current_class_display()
            self.class_changed.emit(class_id)
            
            logger.info(f"Label: Class selected: {class_id}")
    
    def on_list_item_clicked(self, item):
        """Handle list item click."""
        
        class_id = item.data(Qt.UserRole)
        if class_id is not None:
            # Find and select in combo box
            for i in range(self.class_combo.count()):
                if self.class_combo.itemData(i) == class_id:
                    self.class_combo.setCurrentIndex(i)
                    break
    
    def add_class(self):
        """Add a new class."""
        
        logger.info("Label: Add class button clicked")
        
        if not self.label_manager:
            QMessageBox.warning(self, "Warning", "No label manager available")
            logger.warning("Label: No label manager available")
            return
        
        try:
            dialog = ClassEditDialog(parent=self)
            logger.info("Label: Opening add class dialog")
            
            result = dialog.exec_()
            logger.info(f"Label: Dialog result: {result}")
            
            if result == QDialog.Accepted:
                class_data = dialog.get_class_data()
                logger.info(f"Label: Class data: {class_data}")
                
                if class_data["name"]:
                    class_id = self.label_manager.add_class(
                        name=class_data["name"],
                        color=class_data["color"],
                        description=class_data["description"]
                    )
                    
                    # Refresh UI
                    self.refresh_ui()
                    
                    # Select the new class
                    for i in range(self.class_combo.count()):
                        if self.class_combo.itemData(i) == class_id:
                            self.class_combo.setCurrentIndex(i)
                            break
                    
                    self.class_added.emit(class_data)
                    logger.info(f"Label: Added class: {class_data['name']} (ID: {class_id})")
                    QMessageBox.information(self, "Success", f"Added class: {class_data['name']}")
                else:
                    QMessageBox.warning(self, "Error", "Class name cannot be empty")
            else:
                logger.info("Label: Add class dialog cancelled")
                
        except Exception as e:
            logger.error(f"Label: Error in add_class: {e}")
            # Fallback to simple input dialog
            self._add_class_simple()
    
    def edit_current_class(self):
        """Edit the currently selected class."""
        
        logger.info("Label: Edit class button clicked")
        
        if not self.label_manager:
            QMessageBox.warning(self, "Warning", "No label manager available")
            logger.warning("Label: No label manager available")
            return
        
        current_class = self.label_manager.get_current_class()
        if not current_class:
            QMessageBox.warning(self, "Warning", "No class selected. Please select a class first.")
            logger.warning("Label: No class selected")
            return
        
        try:
            dialog = ClassEditDialog(current_class, parent=self)
            logger.info(f"Label: Opening edit dialog for class: {current_class['name']}")
            
            result = dialog.exec_()
            logger.info(f"Label: Edit dialog result: {result}")
            
            if result == QDialog.Accepted:
                class_data = dialog.get_class_data()
                logger.info(f"Label: Updated data: {class_data}")
                
                if class_data["name"]:
                    success = self.label_manager.update_class(
                        current_class["id"],
                        name=class_data["name"],
                        color=class_data["color"],
                        description=class_data["description"]
                    )
                    
                    if success:
                        self.refresh_ui()
                        self.class_updated.emit(current_class["id"], class_data)
                        logger.info(f"Label: Updated class: {class_data['name']}")
                        QMessageBox.information(self, "Success", f"Updated class: {class_data['name']}")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to update class")
                        logger.error("Label: Failed to update class")
                else:
                    QMessageBox.warning(self, "Error", "Class name cannot be empty")
            else:
                logger.info("Label: Edit dialog cancelled")
                
        except Exception as e:
            logger.error(f"Label: Error in edit_current_class: {e}")
            # Fallback to simple input dialog
            self._edit_class_simple(current_class)
    
    def _add_class_simple(self):
        """Fallback: Add class using simple input dialogs."""
        try:
            name, ok = QInputDialog.getText(self, "Add Class", "Enter class name:")
            if ok and name.strip():
                color = QColorDialog.getColor(QColor("#FF0000"), self, "Choose Color")
                if color.isValid():
                    self.label_manager.add_class(
                        name=name.strip(),
                        color=color.name(),
                        description=""
                    )
                    self.refresh_ui()
                    QMessageBox.information(self, "Success", f"Added: {name}")
                    logger.info(f"Label: Added class via simple dialog: {name}")
        except Exception as e:
            logger.error(f"Label: Simple add failed: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add class: {e}")
    
    def _edit_class_simple(self, current_class):
        """Fallback: Edit class using simple input dialogs."""
        try:
            name, ok = QInputDialog.getText(
                self, "Edit Class", 
                "Enter new class name:",
                text=current_class['name']
            )
            if ok and name.strip():
                color = QColorDialog.getColor(
                    QColor(current_class['color']), 
                    self, "Choose Color"
                )
                if color.isValid():
                    self.label_manager.update_class(
                        current_class["id"],
                        name=name.strip(),
                        color=color.name()
                    )
                    self.refresh_ui()
                    QMessageBox.information(self, "Success", f"Updated class: {name}")
                    logger.info(f"Label: Updated class via simple dialog: {name}")
        except Exception as e:
            logger.error(f"Label: Simple edit failed: {e}")
            QMessageBox.critical(self, "Error", f"Failed to edit class: {e}")
    
    def remove_current_class(self):
        """Remove the currently selected class."""
        
        if not self.label_manager:
            return
        
        current_class = self.label_manager.get_current_class()
        if not current_class:
            QMessageBox.warning(self, "Warning", "No class selected")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete class '{current_class['name']}'?\n\n"
            f"This class has {current_class.get('annotation_count', 0)} annotations.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.label_manager.remove_class(current_class["id"])
            if success:
                self.refresh_ui()
                self.class_removed.emit(current_class["id"])
                logger.info(f"Label: Removed class: {current_class['name']}")
            else:
                QMessageBox.warning(self, "Error", "Failed to remove class")
    
    def get_current_class_info(self) -> Optional[Dict[str, Any]]:
        """Get current class information."""
        
        if self.label_manager:
            return self.label_manager.get_current_class()
        return None
    
    def get_current_class_id(self) -> int:
        """Get current class ID."""
        
        if self.label_manager:
            return self.label_manager.get_current_class_id()
        return 0
