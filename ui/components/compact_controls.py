#!/usr/bin/env python3
"""
Compact Controls - Space-Efficient UI Components
Optimized UI components with minimal space usage and professional appearance.
"""

import logging
from typing import Dict, List, Any, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, 
    QLabel, QComboBox, QSlider, QSpinBox, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

logger = logging.getLogger(__name__)


class CompactButton(QPushButton):
    """Space-efficient button with minimal padding."""
    
    def __init__(self, text: str, tooltip: str = "", parent=None):
        super().__init__(text, parent)
        
        # Compact styling
        self.setMaximumHeight(28)
        self.setMinimumHeight(28)
        
        if tooltip:
            self.setToolTip(tooltip)
        
        # Remove extra padding and margins
        self.setStyleSheet("""
            QPushButton {
                padding: 2px 6px;
                margin: 1px;
                font-size: 12px;
                border-radius: 3px;
            }
        """)


class CompactGroup(QGroupBox):
    """Space-efficient group box with minimal padding."""
    
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        
        # Compact font
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.setFont(font)
        
        # Minimal margins
        self.setStyleSheet("""
            QGroupBox {
                margin-top: 5px;
                padding-top: 10px;
                font-size: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 0 3px 0 3px;
            }
        """)


class CompactFileControls(QWidget):
    """Compact file operation controls."""
    
    # Signals
    load_image_clicked = pyqtSignal()
    save_clicked = pyqtSignal()
    new_project_clicked = pyqtSignal()
    close_clicked = pyqtSignal()
    prev_image_clicked = pyqtSignal()
    next_image_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.init_ui()
        logger.info("File: Compact file controls initialized")
    
    def init_ui(self):
        """Initialize compact file controls UI."""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # File operations
        file_group = CompactGroup("File")
        file_layout = QVBoxLayout(file_group)
        file_layout.setSpacing(2)
        
        # Top row: New, Open, Save
        top_row = QHBoxLayout()
        top_row.setSpacing(2)
        
        self.new_btn = CompactButton("New", "New project (Ctrl+N)")
        self.new_btn.clicked.connect(self.new_project_clicked)
        top_row.addWidget(self.new_btn)
        
        self.open_btn = CompactButton("Open", "Open image (Ctrl+O)")
        self.open_btn.clicked.connect(self.load_image_clicked)
        top_row.addWidget(self.open_btn)
        
        self.save_btn = CompactButton("Export", "Smart export (Ctrl+S)")
        self.save_btn.clicked.connect(self.save_clicked)
        self.save_btn.setEnabled(False)
        top_row.addWidget(self.save_btn)
        
        file_layout.addLayout(top_row)
        
        # Navigation row
        nav_row = QHBoxLayout()
        nav_row.setSpacing(2)
        
        self.prev_btn = CompactButton("◀", "Previous image")
        self.prev_btn.clicked.connect(self.prev_image_clicked)
        self.prev_btn.setEnabled(False)
        self.prev_btn.setMaximumWidth(30)
        nav_row.addWidget(self.prev_btn)
        
        self.image_info = QLabel("No image")
        self.image_info.setAlignment(Qt.AlignCenter)
        self.image_info.setStyleSheet("font-size: 10px; color: #666;")
        nav_row.addWidget(self.image_info)
        
        self.next_btn = CompactButton("▶", "Next image") 
        self.next_btn.clicked.connect(self.next_image_clicked)
        self.next_btn.setEnabled(False)
        self.next_btn.setMaximumWidth(30)
        nav_row.addWidget(self.next_btn)
        
        file_layout.addLayout(nav_row)
        
        # Close button (prominent)
        self.close_btn = QPushButton("✕ Close")
        self.close_btn.clicked.connect(self.close_clicked)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 4px 8px;
                margin: 2px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        file_layout.addWidget(self.close_btn)
        
        layout.addWidget(file_group)
    
    def update_navigation_state(self, has_prev: bool, has_next: bool, info: str = ""):
        """Update navigation button states."""
        
        self.prev_btn.setEnabled(has_prev)
        self.next_btn.setEnabled(has_next)
        
        if info:
            self.image_info.setText(info)
        else:
            self.image_info.setText("No image")
    
    def enable_save_button(self, enabled: bool):
        """Enable or disable the save button."""
        self.save_btn.setEnabled(enabled)


class CompactToolControls(QWidget):
    """Compact annotation tool controls."""
    
    # Signals
    tool_selected = pyqtSignal(str)
    brush_size_changed = pyqtSignal(int)
    brush_mode_changed = pyqtSignal(str)
    annotation_format_changed = pyqtSignal(str)  # New signal for format selection
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_tool = "magic_wand"
        self.current_format = "segmentation"  # Default format
        self.tool_buttons = {}
        
        self.init_ui()
        logger.info("Tool: Compact tool controls initialized")
    
    def init_ui(self):
        """Initialize compact tool controls UI."""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # AI Tools group
        ai_group = CompactGroup("AI Tools")
        ai_layout = QVBoxLayout(ai_group)
        ai_layout.setSpacing(2)
        
        # AI tools row 1
        ai_row1 = QHBoxLayout()
        ai_row1.setSpacing(2)
        
        self.magic_wand_btn = CompactButton("Wand", "Magic wand SAM (1)")
        self.magic_wand_btn.clicked.connect(lambda: self.select_tool('magic_wand'))
        self.tool_buttons['magic_wand'] = self.magic_wand_btn
        ai_row1.addWidget(self.magic_wand_btn)
        
        self.bbox_btn = CompactButton("BBox", "BBox segment (2)")
        self.bbox_btn.clicked.connect(lambda: self.select_tool('bbox'))
        self.tool_buttons['bbox'] = self.bbox_btn
        ai_row1.addWidget(self.bbox_btn)
        
        ai_layout.addLayout(ai_row1)
        
        # AI tools row 2
        ai_row2 = QHBoxLayout()
        ai_row2.setSpacing(2)
        
        self.auto_btn = CompactButton("Auto", "Auto segment (4)")
        self.auto_btn.clicked.connect(lambda: self.select_tool('auto'))
        self.tool_buttons['auto'] = self.auto_btn
        ai_row2.addWidget(self.auto_btn)
        
        self.brush_btn = CompactButton("Brush", "Smart brush (3)")
        self.brush_btn.clicked.connect(lambda: self.select_tool('brush'))
        self.tool_buttons['brush'] = self.brush_btn
        ai_row2.addWidget(self.brush_btn)
        
        ai_layout.addLayout(ai_row2)
        
        layout.addWidget(ai_group)
        
        # Annotation Format Selector
        format_group = CompactGroup("Output Format")
        format_layout = QHBoxLayout(format_group)
        format_layout.setSpacing(2)
        
        self.seg_format_btn = CompactButton("Segmentation", "Output as segmentation mask")
        self.seg_format_btn.setCheckable(True)
        self.seg_format_btn.setChecked(True)
        self.seg_format_btn.clicked.connect(lambda: self.set_annotation_format('segmentation'))
        format_layout.addWidget(self.seg_format_btn)
        
        self.bbox_format_btn = CompactButton("BBox", "Output as bounding box")
        self.bbox_format_btn.setCheckable(True)
        self.bbox_format_btn.clicked.connect(lambda: self.set_annotation_format('bbox'))
        format_layout.addWidget(self.bbox_format_btn)
        
        layout.addWidget(format_group)
        
        # Manual Tools group
        manual_group = CompactGroup("Manual")
        manual_layout = QHBoxLayout(manual_group)
        manual_layout.setSpacing(2)
        
        self.polygon_btn = CompactButton("Polygon", "Manual polygon (5)")
        self.polygon_btn.clicked.connect(lambda: self.select_tool('polygon'))
        self.tool_buttons['polygon'] = self.polygon_btn
        manual_layout.addWidget(self.polygon_btn)
        
        self.rectangle_btn = CompactButton("Rect", "Manual rectangle (6)")
        self.rectangle_btn.clicked.connect(lambda: self.select_tool('rectangle'))
        self.tool_buttons['rectangle'] = self.rectangle_btn
        manual_layout.addWidget(self.rectangle_btn)
        
        layout.addWidget(manual_group)
        
        # Brush controls (compact)
        self.brush_controls = QWidget()
        brush_layout = QVBoxLayout(self.brush_controls)
        brush_layout.setContentsMargins(0, 0, 0, 0)
        brush_layout.setSpacing(1)
        
        # Size control
        size_row = QHBoxLayout()
        size_row.setSpacing(2)
        size_row.addWidget(QLabel("Size:"))
        
        self.brush_size_slider = QSlider(Qt.Horizontal)
        self.brush_size_slider.setRange(1, 50)
        self.brush_size_slider.setValue(10)
        self.brush_size_slider.setMaximumHeight(20)
        self.brush_size_slider.valueChanged.connect(self.brush_size_changed)
        size_row.addWidget(self.brush_size_slider)
        
        self.brush_size_spin = QSpinBox()
        self.brush_size_spin.setRange(1, 50)
        self.brush_size_spin.setValue(10)
        self.brush_size_spin.setMaximumWidth(50)
        self.brush_size_spin.setMaximumHeight(22)
        self.brush_size_spin.valueChanged.connect(self.brush_size_changed)
        size_row.addWidget(self.brush_size_spin)
        
        # Connect slider and spinbox
        self.brush_size_slider.valueChanged.connect(self.brush_size_spin.setValue)
        self.brush_size_spin.valueChanged.connect(self.brush_size_slider.setValue)
        
        brush_layout.addLayout(size_row)
        
        # Mode control
        mode_row = QHBoxLayout()
        mode_row.setSpacing(2)
        
        self.paint_btn = CompactButton("Paint", "Paint mode")
        self.paint_btn.setCheckable(True)
        self.paint_btn.setChecked(True)
        self.paint_btn.clicked.connect(lambda: self.set_brush_mode('paint'))
        mode_row.addWidget(self.paint_btn)
        
        self.erase_btn = CompactButton("Erase", "Erase mode")
        self.erase_btn.setCheckable(True)
        self.erase_btn.clicked.connect(lambda: self.set_brush_mode('erase'))
        mode_row.addWidget(self.erase_btn)
        
        brush_layout.addLayout(mode_row)
        
        self.brush_controls.hide()  # Hidden by default
        layout.addWidget(self.brush_controls)
        
        # Set default tool
        self.select_tool('magic_wand')
    
    def select_tool(self, tool_name: str):
        """Select annotation tool with visual feedback."""
        
        self.current_tool = tool_name
        
        # Update button states
        for name, button in self.tool_buttons.items():
            if name == tool_name:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        font-weight: bold;
                        padding: 2px 6px;
                        margin: 1px;
                        border-radius: 3px;
                        font-size: 12px;
                    }
                """)
            else:
                button.setStyleSheet("")  # Reset to default
        
        # Show/hide brush controls
        if tool_name == 'brush':
            self.brush_controls.show()
        else:
            self.brush_controls.hide()
        
        # Emit signal
        self.tool_selected.emit(tool_name)
        
        logger.info(f"Tool: Tool selected: {tool_name}")
    
    def set_brush_mode(self, mode: str):
        """Set brush mode with exclusive selection."""
        
        if mode == 'paint':
            self.paint_btn.setChecked(True)
            self.erase_btn.setChecked(False)
        else:
            self.paint_btn.setChecked(False)
            self.erase_btn.setChecked(True)
        
        self.brush_mode_changed.emit(mode)
    
    def set_annotation_format(self, format_type: str):
        """Set annotation output format (segmentation or bbox)."""
        
        self.current_format = format_type
        
        # Update button states with color feedback
        if format_type == 'segmentation':
            self.seg_format_btn.setChecked(True)
            self.bbox_format_btn.setChecked(False)
            self.seg_format_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    font-weight: bold;
                    padding: 2px 6px;
                    border-radius: 3px;
                }
            """)
            self.bbox_format_btn.setStyleSheet("""
                QPushButton {
                    background-color: #7f8c8d;
                    color: white;
                    padding: 2px 6px;
                    border-radius: 3px;
                }
            """)
        else:  # bbox
            self.seg_format_btn.setChecked(False)
            self.bbox_format_btn.setChecked(True)
            self.seg_format_btn.setStyleSheet("""
                QPushButton {
                    background-color: #7f8c8d;
                    color: white;
                    padding: 2px 6px;
                    border-radius: 3px;
                }
            """)
            self.bbox_format_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e67e22;
                    color: white;
                    font-weight: bold;
                    padding: 2px 6px;
                    border-radius: 3px;
                }
            """)
        
        self.annotation_format_changed.emit(format_type)
        logger.info(f"Format: Annotation format set to: {format_type}")
    
    def get_current_format(self) -> str:
        """Get current annotation format."""
        return self.current_format
    
    def enable_tools(self, enabled: bool):
        """Enable or disable all tool buttons."""
        
        for button in self.tool_buttons.values():
            button.setEnabled(enabled)


class CompactStatusBar(QWidget):
    """Compact status display with essential information."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.init_ui()
        logger.info("Monitor: Compact status bar initialized")
    
    def init_ui(self):
        """Initialize compact status UI."""
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)
        
        # Current status
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-size: 11px; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setMaximumHeight(16)
        layout.addWidget(separator)
        
        # Annotation count
        self.annotation_count = QLabel("0 annotations")
        self.annotation_count.setStyleSheet("font-size: 10px; color: #666;")
        layout.addWidget(self.annotation_count)
        
        # Spacer
        layout.addStretch()
        
        # Performance indicator
        self.performance_indicator = QLabel("●")
        self.performance_indicator.setToolTip("Performance status")
        self.performance_indicator.setStyleSheet("color: #2ecc71; font-size: 12px;")  # Green
        layout.addWidget(self.performance_indicator)
    
    def set_status(self, message: str):
        """Set status message."""
        self.status_label.setText(message)
    
    def set_annotation_count(self, count: int):
        """Set annotation count display."""
        self.annotation_count.setText(f"{count} annotations")
    
    def set_performance_status(self, status: str):
        """Set performance indicator."""
        
        colors = {
            'good': '#2ecc71',     # Green
            'warning': '#f39c12',  # Orange  
            'poor': '#e74c3c'      # Red
        }
        
        color = colors.get(status, '#95a5a6')
        self.performance_indicator.setStyleSheet(f"color: {color}; font-size: 12px;")


class CompactModelStatus(QWidget):
    """Compact model status display."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.init_ui()
        logger.info("Model: Compact model status initialized")
    
    def init_ui(self):
        """Initialize compact model status UI."""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        
        # Model status group
        models_group = CompactGroup("AI Models")
        models_layout = QVBoxLayout(models_group)
        models_layout.setSpacing(1)
        
        # SAM status
        sam_row = QHBoxLayout()
        sam_row.setSpacing(4)
        sam_row.addWidget(QLabel("SAM:"))
        self.sam_status = QLabel("Loading...")
        self.sam_status.setStyleSheet("font-size: 10px;")
        sam_row.addWidget(self.sam_status)
        sam_row.addStretch()
        models_layout.addLayout(sam_row)
        
        # YOLO status  
        yolo_row = QHBoxLayout()
        yolo_row.setSpacing(4)
        yolo_row.addWidget(QLabel("YOLO:"))
        self.yolo_status = QLabel("Loading...")
        self.yolo_status.setStyleSheet("font-size: 10px;")
        yolo_row.addWidget(self.yolo_status)
        yolo_row.addStretch()
        models_layout.addLayout(yolo_row)
        
        # Reload button
        self.reload_btn = CompactButton("Reload", "Reload models (F5)")
        models_layout.addWidget(self.reload_btn)
        
        layout.addWidget(models_group)
    
    def set_sam_status(self, status: str, success: bool = True):
        """Set SAM status with color coding."""
        
        color = "#2ecc71" if success else "#e74c3c"
        self.sam_status.setText(status)
        self.sam_status.setStyleSheet(f"font-size: 10px; color: {color}; font-weight: bold;")
    
    def set_yolo_status(self, status: str, success: bool = True):
        """Set YOLO status with color coding."""
        
        color = "#2ecc71" if success else "#e74c3c"
        self.yolo_status.setText(status)
        self.yolo_status.setStyleSheet(f"font-size: 10px; color: {color}; font-weight: bold;")
