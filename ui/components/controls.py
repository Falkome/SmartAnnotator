#!/usr/bin/env python3
"""
Control Panel - Smart Annotator Control Interface

Smart control panel with AI-enhanced controls and intelligent feedback.
"""

import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QPushButton, QComboBox, QSlider, QCheckBox, QTextEdit,
    QProgressBar, QFileDialog, QMessageBox, QSpinBox, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette

logger = logging.getLogger(__name__)


class ControlPanel(QFrame):
    """Smart control panel for annotation tools and settings."""
    
    # Signals
    image_loaded = pyqtSignal(str)           # Image path
    tool_changed = pyqtSignal(str)           # Tool name
    model_changed = pyqtSignal(str)          # Model name
    setting_changed = pyqtSignal(str, object)  # Setting name, value
    save_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.setFrameStyle(QFrame.StyledPanel)
        self.setMaximumWidth(350)
        self.setMinimumWidth(300)
        
        # Current state
        self.current_tool = "magic_wand"
        self.current_model = None
        self.current_image_path = None
        
        # Settings
        self.settings = {
            'confidence_threshold': 0.5,
            'smart_mode': True,
            'auto_suggestions': True,
            'smart_refinement': True,
            'max_detections': 100
        }
        
        # Statistics
        self.session_stats = {
            'images_loaded': 0,
            'annotations_created': 0,
            'tools_used': {},
            'session_start': time.time()
        }
        
        # Initialize UI
        self.init_ui()
        
        # Setup auto-update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats_display)
        self.update_timer.start(2000)  # Update every 2 seconds
        
        logger.info("🎛️ Control Panel initialized")
    
    def init_ui(self):
        """Initialize the control panel UI."""
        
        # Apply styling
        self.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                color: #ecf0f1;
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 10px;
            }
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                color: #3498db;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
            QComboBox {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #3498db;
                border-radius: 4px;
                padding: 4px;
                font-size: 11px;
                min-height: 20px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                border: none;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 11px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #3498db;
                height: 6px;
                background: #2c3e50;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #3498db;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QCheckBox {
                color: #ecf0f1;
                font-size: 11px;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border: 1px solid #3498db;
            }
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #3498db;
                border-radius: 4px;
                font-size: 10px;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Engine: Smart Controls")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #3498db; font-size: 16px; padding: 5px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # File operations
        layout.addWidget(self.create_file_group())
        
        # Model selection
        layout.addWidget(self.create_model_group())
        
        # Annotation tools
        layout.addWidget(self.create_tools_group())
        
        # Smart settings
        layout.addWidget(self.create_settings_group())
        
        # Statistics
        layout.addWidget(self.create_stats_group())
        
        # Actions
        layout.addWidget(self.create_actions_group())
        
        layout.addStretch()
    
    def create_file_group(self) -> QGroupBox:
        """Create file operations group."""
        
        group = QGroupBox("File: File Operations")
        layout = QVBoxLayout(group)
        
        # Load image button
        self.load_image_btn = QPushButton("Navigator: Load Image")
        self.load_image_btn.clicked.connect(self.load_image)
        layout.addWidget(self.load_image_btn)
        
        # Current image info
        self.image_info_label = QLabel("No image loaded")
        self.image_info_label.setStyleSheet("color: #95a5a6; font-size: 10px;")
        layout.addWidget(self.image_info_label)
        
        return group
    
    def create_model_group(self) -> QGroupBox:
        """Create model selection group."""
        
        group = QGroupBox("Model: AI Models")
        layout = QVBoxLayout(group)
        
        # Model selector
        layout.addWidget(QLabel("Active Model:"))
        self.model_selector = QComboBox()
        self.model_selector.addItems([
            "SAM (Segment Anything)",
            "YOLO (Object Detection)",
            "Auto Select"
        ])
        self.model_selector.currentTextChanged.connect(self.on_model_changed)
        layout.addWidget(self.model_selector)
        
        # Model status
        self.model_status_label = QLabel("Status: Ready")
        self.model_status_label.setStyleSheet("color: #2ecc71; font-size: 10px;")
        layout.addWidget(self.model_status_label)
        
        # Load model button
        self.load_model_btn = QPushButton("Model: Load Model")
        self.load_model_btn.clicked.connect(self.load_model)
        layout.addWidget(self.load_model_btn)
        
        return group
    
    def create_tools_group(self) -> QGroupBox:
        """Create annotation tools group."""
        
        group = QGroupBox("Tool: Annotation Tools")
        layout = QVBoxLayout(group)
        
        # Tool buttons
        self.tool_buttons = {}
        
        tools = [
            ("magic_wand", "SAM: Magic Wand", "Click objects to segment"),
            ("bbox", "YOLO: BBox Segment", "Draw boxes around objects"),
            ("brush", "Brush: Smart Brush", "Paint segmentation mask (memory-efficient)"),
            ("auto", "🔄 Auto Segment", "Automatically detect all objects")
        ]
        
        for tool_id, tool_name, tool_desc in tools:
            btn = QPushButton(tool_name)
            btn.setToolTip(tool_desc)
            btn.clicked.connect(lambda checked, t=tool_id: self.set_tool(t))
            self.tool_buttons[tool_id] = btn
            layout.addWidget(btn)
        
        # Set default tool
        self.set_tool("magic_wand")
        
        return group
    
    def create_settings_group(self) -> QGroupBox:
        """Create smart settings group."""
        
        group = QGroupBox("⚙️ Smart Settings")
        layout = QVBoxLayout(group)
        
        # Confidence threshold
        layout.addWidget(QLabel("Confidence Threshold:"))
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(10, 95)
        self.confidence_slider.setValue(50)
        self.confidence_slider.valueChanged.connect(self.on_confidence_changed)
        layout.addWidget(self.confidence_slider)
        
        self.confidence_value_label = QLabel("0.50")
        self.confidence_value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.confidence_value_label)
        
        # Brush tool controls
        layout.addWidget(QLabel("Brush Size:"))
        self.brush_size_slider = QSlider(Qt.Horizontal)
        self.brush_size_slider.setRange(1, 50)
        self.brush_size_slider.setValue(10)
        self.brush_size_slider.valueChanged.connect(self.on_brush_size_changed)
        layout.addWidget(self.brush_size_slider)
        
        self.brush_size_label = QLabel("10px")
        self.brush_size_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.brush_size_label)
        
        # Brush mode selector
        layout.addWidget(QLabel("Brush Mode:"))
        self.brush_mode_selector = QComboBox()
        self.brush_mode_selector.addItems(["Canvas: Paint", "🗑️ Erase"])
        self.brush_mode_selector.currentTextChanged.connect(self.on_brush_mode_changed)
        layout.addWidget(self.brush_mode_selector)
        
        # Smart mode checkbox
        self.smart_mode_cb = QCheckBox("Engine: Smart Mode")
        self.smart_mode_cb.setChecked(True)
        self.smart_mode_cb.toggled.connect(self.on_smart_mode_changed)
        layout.addWidget(self.smart_mode_cb)
        
        # Auto suggestions checkbox
        self.auto_suggestions_cb = QCheckBox("Auto Suggestions")
        self.auto_suggestions_cb.setChecked(True)
        self.auto_suggestions_cb.toggled.connect(self.on_auto_suggestions_changed)
        layout.addWidget(self.auto_suggestions_cb)
        
        # Smart refinement checkbox
        self.smart_refinement_cb = QCheckBox("✨ Smart Refinement")
        self.smart_refinement_cb.setChecked(True)
        self.smart_refinement_cb.toggled.connect(self.on_smart_refinement_changed)
        layout.addWidget(self.smart_refinement_cb)
        
        # Max detections
        layout.addWidget(QLabel("Max Detections:"))
        self.max_detections_spin = QSpinBox()
        self.max_detections_spin.setRange(10, 500)
        self.max_detections_spin.setValue(100)
        self.max_detections_spin.valueChanged.connect(self.on_max_detections_changed)
        layout.addWidget(self.max_detections_spin)
        
        return group
    
    def create_stats_group(self) -> QGroupBox:
        """Create statistics group."""
        
        group = QGroupBox("Monitor: Session Stats")
        layout = QVBoxLayout(group)
        
        # Stats display
        self.stats_text = QTextEdit()
        self.stats_text.setMaximumHeight(120)
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)
        
        # Progress bar for current operation
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        return group
    
    def create_actions_group(self) -> QGroupBox:
        """Create actions group."""
        
        group = QGroupBox("🎮 Actions")
        layout = QVBoxLayout(group)
        
        # Save annotations
        self.save_btn = QPushButton("💾 Save Annotations")
        self.save_btn.clicked.connect(self.save_annotations)
        self.save_btn.setEnabled(False)
        layout.addWidget(self.save_btn)
        
        # Clear all
        self.clear_btn = QPushButton("🗑️ Clear All")
        self.clear_btn.clicked.connect(self.clear_all)
        layout.addWidget(self.clear_btn)
        
        # Reset session
        self.reset_btn = QPushButton("🔄 Reset Session")
        self.reset_btn.clicked.connect(self.reset_session)
        layout.addWidget(self.reset_btn)
        
        # Memory optimization for brush tool
        self.memory_optimize_btn = QPushButton("Cleanup: Optimize Memory")
        self.memory_optimize_btn.clicked.connect(self.optimize_memory)
        layout.addWidget(self.memory_optimize_btn)
        
        return group
    
    def load_image(self):
        """Load image for annotation."""
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Load Image for Smart Annotation", 
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp);;All Files (*)"
        )
        
        if file_path:
            self.current_image_path = file_path
            self.session_stats['images_loaded'] += 1
            
            # Update UI
            image_name = Path(file_path).name
            image_info = f"{image_name}"
            self.image_info_label.setText(image_info)
            
            # Enable save button
            self.save_btn.setEnabled(True)
            
            # Emit signal
            self.image_loaded.emit(file_path)
            
            logger.info(f"Image loaded: {file_path}")
    
    def load_model(self):
        """Load selected model."""
        
        model_name = self.model_selector.currentText()
        
        # Show progress
        self.show_progress("Loading model...", 50)
        
        # Update status
        self.model_status_label.setText("Status: Loading...")
        self.model_status_label.setStyleSheet("color: #f39c12; font-size: 10px;")
        
        # Emit signal
        self.model_changed.emit(model_name)
        
        # Simulate loading delay (in real app, this would be handled by the model)
        QTimer.singleShot(1000, self.on_model_loaded)
        
        logger.info(f"Model load requested: {model_name}")
    
    def on_model_loaded(self):
        """Handle model loaded event."""
        
        self.hide_progress()
        self.model_status_label.setText("Status: Ready")
        self.model_status_label.setStyleSheet("color: #2ecc71; font-size: 10px;")
    
    def set_tool(self, tool_name: str):
        """Set active annotation tool."""
        
        # Update button states
        for tool_id, button in self.tool_buttons.items():
            if tool_id == tool_name:
                button.setStyleSheet(button.styleSheet() + "background-color: #2980b9;")
                self.current_tool = tool_name
            else:
                button.setStyleSheet(button.styleSheet().replace("background-color: #2980b9;", ""))
        
        # Update stats
        if tool_name in self.session_stats['tools_used']:
            self.session_stats['tools_used'][tool_name] += 1
        else:
            self.session_stats['tools_used'][tool_name] = 1
        
        # Emit signal
        self.tool_changed.emit(tool_name)
        
        logger.info(f"Tool changed to: {tool_name}")
    
    def on_model_changed(self, model_name: str):
        """Handle model selection change."""
        
        self.current_model = model_name
        logger.info(f"Model selected: {model_name}")
    
    def on_confidence_changed(self, value: int):
        """Handle confidence threshold change."""
        
        confidence = value / 100.0
        self.settings['confidence_threshold'] = confidence
        self.confidence_value_label.setText(f"{confidence:.2f}")
        
        # Emit signal
        self.setting_changed.emit('confidence_threshold', confidence)
    
    def on_smart_mode_changed(self, enabled: bool):
        """Handle smart mode change."""
        
        self.settings['smart_mode'] = enabled
        self.setting_changed.emit('smart_mode', enabled)
        
        logger.info(f"Smart mode: {'enabled' if enabled else 'disabled'}")
    
    def on_auto_suggestions_changed(self, enabled: bool):
        """Handle auto suggestions change."""
        
        self.settings['auto_suggestions'] = enabled
        self.setting_changed.emit('auto_suggestions', enabled)
    
    def on_smart_refinement_changed(self, enabled: bool):
        """Handle smart refinement change."""
        
        self.settings['smart_refinement'] = enabled
        self.setting_changed.emit('smart_refinement', enabled)
    
    def on_max_detections_changed(self, value: int):
        """Handle max detections change."""
        
        self.settings['max_detections'] = value
        self.setting_changed.emit('max_detections', value)
    
    def on_brush_size_changed(self, value: int):
        """Handle brush size change."""
        
        self.brush_size_label.setText(f"{value}px")
        self.setting_changed.emit('brush_size', value)
        
        logger.info(f"Brush size changed to: {value}px")
    
    def on_brush_mode_changed(self, mode_text: str):
        """Handle brush mode change."""
        
        mode = "paint" if "Paint" in mode_text else "erase"
        self.setting_changed.emit('brush_mode', mode)
        
        logger.info(f"Brush mode changed to: {mode}")
    
    def optimize_memory(self):
        """Request memory optimization."""
        
        # Show progress
        self.show_progress("Optimizing memory...", 75)
        
        # Emit memory optimization request
        self.setting_changed.emit('optimize_memory', True)
        
        # Hide progress after delay
        QTimer.singleShot(1000, self.hide_progress)
        
        logger.info("Memory optimization requested")
    
    def save_annotations(self):
        """Save annotations to file."""
        
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "No image loaded!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Smart Annotations",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            # Show progress
            self.show_progress("Saving annotations...", 75)
            
            # Emit signal
            self.save_requested.emit()
            
            # Simulate save delay
            QTimer.singleShot(500, self.hide_progress)
            
            logger.info(f"Save requested: {file_path}")
    
    def clear_all(self):
        """Clear all annotations."""
        
        reply = QMessageBox.question(
            self,
            "Clear All",
            "Are you sure you want to clear all annotations?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.clear_requested.emit()
            logger.info("Clear all requested")
    
    def reset_session(self):
        """Reset session statistics."""
        
        reply = QMessageBox.question(
            self,
            "Reset Session",
            "Reset session statistics and settings?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.session_stats = {
                'images_loaded': 0,
                'annotations_created': 0,
                'tools_used': {},
                'session_start': time.time()
            }
            
            self.update_stats_display()
            logger.info("Session reset")
    
    def show_progress(self, message: str, value: int):
        """Show progress bar with message."""
        
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(message)
        self.progress_bar.setVisible(True)
    
    def hide_progress(self):
        """Hide progress bar."""
        
        self.progress_bar.setVisible(False)
    
    def update_stats_display(self):
        """Update statistics display."""
        
        session_time = time.time() - self.session_stats['session_start']
        hours = int(session_time // 3600)
        minutes = int((session_time % 3600) // 60)
        
        stats_text = f"""Monitor: Session Statistics
        
⏱️ Time: {hours:02d}:{minutes:02d}
📷 Images: {self.session_stats['images_loaded']}
📝 Annotations: {self.session_stats['annotations_created']}
Tool: Current Tool: {self.current_tool}

🔧 Tools Used:"""
        
        for tool, count in self.session_stats['tools_used'].items():
            stats_text += f"\n  {tool}: {count}"
        
        if not self.session_stats['tools_used']:
            stats_text += "\n  None yet"
        
        stats_text += f"""

⚙️ Settings:
  SAM: Confidence: {self.settings['confidence_threshold']:.2f}
  Engine: Smart Mode: {'On' if self.settings['smart_mode'] else 'Off'}
  Suggestions: {'On' if self.settings['auto_suggestions'] else 'Off'}"""
        
        self.stats_text.setText(stats_text)
    
    def increment_annotations(self):
        """Increment annotation counter."""
        
        self.session_stats['annotations_created'] += 1
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current settings."""
        
        return self.settings.copy()
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        
        return self.session_stats.copy()
    
    def set_model_status(self, status: str, color: str = "#2ecc71"):
        """Set model status message."""
        
        self.model_status_label.setText(f"Status: {status}")
        self.model_status_label.setStyleSheet(f"color: {color}; font-size: 10px;")
    
    def enable_controls(self, enabled: bool):
        """Enable or disable controls."""
        
        for button in self.tool_buttons.values():
            button.setEnabled(enabled)
        
        self.load_model_btn.setEnabled(enabled)
        self.save_btn.setEnabled(enabled and self.current_image_path is not None)
