#!/usr/bin/env python3
"""
Smart Annotator GUI Application - Main GUI Interface
Designed to work reliably across different display servers (X11, Wayland).
"""

import sys
import os
import time
import logging
from pathlib import Path
from typing import Optional

# Qt imports with error handling
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QFileDialog, QStatusBar, QMenuBar, QMessageBox,
        QGroupBox, QGridLayout, QTextEdit, QProgressBar, QSplitter
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal
    from PyQt5.QtGui import QFont, QPixmap, QIcon
    PYQT5_AVAILABLE = True
except ImportError as e:
    print(f"Error: PyQt5 not available: {e}")
    PYQT5_AVAILABLE = False

logger = logging.getLogger(__name__)

class SmartAnnotatorGUI(QMainWindow):
    """Main Smart Annotator GUI Application with robust display handling."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.current_image_path = None
        self.smart_engine = None
        self.sam_model = None
        self.yolo_model = None
        self.annotation_format = "segmentation"  # Default annotation format
        
        # Initialize label management
        from src.label_manager import LabelManager
        self.label_manager = LabelManager()
        
        # Initialize image navigator
        from src.image_navigator import ImageNavigator
        self.image_navigator = ImageNavigator()
        
        # Initialize auto-save manager
        from src.auto_save_manager import AutoSaveManager
        self.auto_save_manager = AutoSaveManager()
        self.auto_save_manager.enable_auto_save(True)
        
        logger.info("💾 Auto-Save Manager initialized and enabled")
        
        # Setup UI
        self.init_ui()
        self.init_models()
        
        logger.info("Canvas: Smart Annotator GUI initialized")
    
    def init_ui(self):
        """Initialize the user interface."""
        
        self.setWindowTitle("Engine: Smart Annotator - AI-Powered Image Annotation")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                color: #333333;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QStatusBar {
                background-color: #34495e;
                color: white;
                font-weight: bold;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Right panel - Image and annotation area (create first to initialize canvas)
        right_panel = self.create_image_panel()
        
        # Left panel - Controls (create after canvas exists)
        left_panel = self.create_control_panel()
        
        # Add panels to splitter in correct order (left, then right)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (30% left, 70% right)
        splitter.setSizes([420, 980])
        
        # Create menu bar
        self.create_menu_bar()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Engine: Smart Annotator Ready - Load an image to start")
        
        # Timer for status updates
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Update every 5 seconds
    
    def create_control_panel(self) -> QWidget:
        """Create the compact left control panel."""
        
        panel = QWidget()
        panel.setMaximumWidth(320)  # Reduced width
        panel.setMinimumWidth(280)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(4)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Compact file controls
        from ui.components.compact_controls import CompactFileControls, CompactToolControls, CompactModelStatus
        
        self.file_controls = CompactFileControls()
        self.file_controls.load_image_clicked.connect(self.load_image)
        self.file_controls.save_clicked.connect(self.save_annotations)
        self.file_controls.new_project_clicked.connect(self.new_project)
        self.file_controls.close_clicked.connect(self.close_application)
        self.file_controls.prev_image_clicked.connect(self.load_previous_image)
        self.file_controls.next_image_clicked.connect(self.load_next_image)
        layout.addWidget(self.file_controls)
        
        # Compact tool controls
        self.tool_controls = CompactToolControls()
        self.tool_controls.tool_selected.connect(self.set_tool)
        self.tool_controls.brush_size_changed.connect(self.canvas.set_brush_size)
        self.tool_controls.brush_mode_changed.connect(self.canvas.set_brush_mode)
        self.tool_controls.annotation_format_changed.connect(self.on_annotation_format_changed)
        layout.addWidget(self.tool_controls)
        
        # Compact model status
        self.model_status = CompactModelStatus()
        self.model_status.reload_btn.clicked.connect(self.init_models)
        layout.addWidget(self.model_status)
        
        # Label management section
        from ui.components.label_widget import LabelWidget
        
        label_group = QGroupBox("Labels")
        label_layout = QVBoxLayout(label_group)
        label_layout.setSpacing(2)
        
        self.label_widget = LabelWidget()
        self.label_widget.set_label_manager(self.label_manager)
        self.label_widget.class_changed.connect(self.on_class_changed)
        self.label_widget.class_added.connect(self.on_class_added)
        
        label_layout.addWidget(self.label_widget)
        layout.addWidget(label_group)
        
        # Compact performance controls
        perf_group = QGroupBox("Performance")
        perf_layout = QVBoxLayout(perf_group)
        perf_layout.setSpacing(2)
        
        perf_row = QHBoxLayout()
        perf_row.setSpacing(2)
        
        from ui.components.compact_controls import CompactButton
        
        self.memory_btn = CompactButton("Memory", "Optimize memory (Ctrl+M)")
        self.memory_btn.clicked.connect(self.optimize_memory)
        perf_row.addWidget(self.memory_btn)
        
        self.perf_btn = CompactButton("Stats", "Performance stats")
        self.perf_btn.clicked.connect(self.show_performance_stats)
        perf_row.addWidget(self.perf_btn)
        
        perf_layout.addLayout(perf_row)
        
        # Performance toggle
        self.cache_toggle = CompactButton("Cache: ON", "Performance caching")
        self.cache_toggle.setCheckable(True)
        self.cache_toggle.setChecked(True)
        self.cache_toggle.clicked.connect(self.toggle_performance_caching)
        perf_layout.addWidget(self.cache_toggle)
        
        layout.addWidget(perf_group)
        
        # Stats display (compact)
        stats_group = QGroupBox("Stats")
        stats_group.setMaximumHeight(100)
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.setSpacing(2)
        
        self.stats_text = QTextEdit()
        self.stats_text.setMaximumHeight(70)
        self.stats_text.setStyleSheet("font-size: 9px;")
        self.stats_text.setPlainText("Ready to annotate...")
        stats_layout.addWidget(self.stats_text)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(15)
        self.progress_bar.setVisible(False)
        stats_layout.addWidget(self.progress_bar)
        
        layout.addWidget(stats_group)
        
        # Add stretch to push everything up
        layout.addStretch()
        
        return panel
    
    def close_application(self):
        """Close the application directly."""
        
        try:
            # Check for unsaved work
            if self.canvas and hasattr(self.canvas, 'annotations') and self.canvas.annotations:
                reply = QMessageBox.question(
                    self,
                    "Close Smart Annotator",
                    f"You have {len(self.canvas.annotations)} unsaved annotations.\n\n"
                    f"Do you want to close without saving?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    return
            
            # Close the application
            self.close()
            
        except Exception as e:
            logger.error(f"Error: Close application error: {e}")
            # Force close anyway
            self.close()
    
    def create_image_panel(self) -> QWidget:
        """Create the right image panel."""
        
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Image display area
        image_group = QGroupBox("🖼️ Image & Annotations")
        image_layout = QVBoxLayout(image_group)
        
        # Smart Canvas for interactive annotation
        from ui.components.canvas import SmartCanvas
        self.canvas = SmartCanvas()
        
        # Connect canvas signals to GUI methods
        self.canvas.annotation_created.connect(self.on_annotation_created)
        self.canvas.point_clicked.connect(self.on_point_clicked)
        self.canvas.bbox_drawn.connect(self.on_bbox_drawn)
        self.canvas.auto_segment_requested.connect(self.on_auto_segment_requested)
        self.canvas.tool_feedback.connect(self.on_tool_feedback)
        
        # Set label manager for canvas
        self.canvas.set_label_manager(self.label_manager)
        
        image_layout.addWidget(self.canvas)
        layout.addWidget(image_group)
        
        return panel
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        
        menubar = self.menuBar()
        
        # File menu (compact)
        file_menu = menubar.addMenu('&File')
        file_menu.addAction('&New Project', self.new_project, 'Ctrl+N')
        file_menu.addAction('&Open Image', self.load_image, 'Ctrl+O')
        file_menu.addSeparator()
        file_menu.addAction('Previous Image', self.load_previous_image, 'Left')
        file_menu.addAction('Next Image', self.load_next_image, 'Right')
        file_menu.addSeparator()
        file_menu.addAction('&Export', self.save_annotations, 'Ctrl+S')
        file_menu.addAction('Preview Export', self.preview_export, 'Ctrl+P')
        file_menu.addAction('YOLO Classes', self.create_yolo_classes)
        file_menu.addSeparator()
        file_menu.addAction('E&xit', self.close_application, 'Ctrl+Q')
        
        # Edit menu
        edit_menu = menubar.addMenu('✏️ &Edit')
        edit_menu.addAction('🗑️ Delete All Annotations', self.delete_all_annotations, 'Delete')
        edit_menu.addAction('↩️ Undo Last Annotation', self.undo_last_annotation, 'Ctrl+Z')
        edit_menu.addAction('Cleanup: Clear Canvas', self.clear_canvas, 'Ctrl+Del')
        
        # Models menu
        models_menu = menubar.addMenu('Model: &Models')
        models_menu.addAction('🔄 &Reload Models', self.init_models, 'F5')
        models_menu.addAction('SAM: Test SAM', self.test_sam_model)
        models_menu.addAction('YOLO: Test YOLO', self.test_yolo_model)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tool: &Tools')
        tools_menu.addAction('SAM: Magic Wand', lambda: self.set_tool('magic_wand'), '1')
        tools_menu.addAction('YOLO: BBox Segment', lambda: self.set_tool('bbox'), '2')
        tools_menu.addAction('Brush: Smart Brush', lambda: self.set_tool('brush'), '3')
        tools_menu.addAction('🔄 Auto Segment', self.run_auto_segment, '4')
        tools_menu.addSeparator()
        tools_menu.addAction('📐 Manual Polygon', lambda: self.set_tool('polygon'), '5')
        tools_menu.addAction('🔲 Manual Rectangle', lambda: self.set_tool('rectangle'), '6')
        
        # Performance menu
        perf_menu = menubar.addMenu('App: &Performance')
        perf_menu.addAction('Cleanup: Optimize Memory', self.optimize_memory, 'Ctrl+M')
        perf_menu.addAction('Monitor: Memory Stats', self.show_memory_stats)
        perf_menu.addSeparator()
        perf_menu.addAction('Toggle Performance Caching', self.toggle_performance_caching, 'Ctrl+Shift+P')
        perf_menu.addAction('Monitor: Performance Statistics', self.show_performance_stats, 'Ctrl+Shift+S')
        perf_menu.addSeparator()
        perf_menu.addAction('💾 Auto-Save Statistics', self.show_auto_save_stats, 'Ctrl+Shift+A')
        perf_menu.addAction('💾 Toggle Auto-Save', self.toggle_auto_save)
        
        # Help menu
        help_menu = menubar.addMenu('❓ &Help')
        help_menu.addAction('📖 User Guide', self.show_help)
        help_menu.addAction('ℹ️ About', self.show_about)
    
    def init_models(self):
        """Initialize AI models with lazy loading for faster startup."""
        
        try:
            from src.core import SmartEngine
            
            self.status_bar.showMessage("Initializing Smart Engine...")
            self.model_status.reload_btn.setEnabled(False)
            
            # Initialize Smart Engine only (fast)
            if self.smart_engine is None:
                self.smart_engine = SmartEngine()
                self.smart_engine.initialize()
            
            # Set models to lazy load on first use
            self.models_lazy_loaded = False
            
            # Update status
            self.model_status.set_sam_status("Lazy Load", True)
            self.model_status.set_yolo_status("Lazy Load", True)
            self.model_status.reload_btn.setEnabled(True)
            
            # Enable tools (will trigger lazy loading when used)
            self.tool_controls.enable_tools(True)
            
            self.status_bar.showMessage("Ready - Models will load on first use")
            logger.info("Smart Engine initialized - Models set to lazy load")
            
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            self.status_bar.showMessage(f"Error: {e}")
            self.model_status.reload_btn.setEnabled(True)
    
    def lazy_load_sam(self):
        """Load SAM model on first use with progress."""
        if self.sam_model is not None and self.sam_model.is_loaded:
            return True
        
        try:
            from models.sam.sam_model import SAMModel
            
            self.status_bar.showMessage("Loading SAM model (first use)...")
            self.model_status.set_sam_status("Loading...", False)
            
            if self.sam_model is None:
                self.sam_model = SAMModel()
            
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(30)
            
            sam_loaded = self.sam_model.load_model()
            
            self.progress_bar.setValue(100)
            self.progress_bar.setVisible(False)
            
            if sam_loaded:
                self.model_status.set_sam_status("Ready", True)
                self.status_bar.showMessage("SAM model loaded successfully")
                logger.info("SAM model loaded on demand")
                return True
            else:
                self.model_status.set_sam_status("Failed", False)
                self.status_bar.showMessage("SAM model failed to load")
                return False
                
        except Exception as e:
            logger.error(f"SAM loading error: {e}")
            self.model_status.set_sam_status("Error", False)
            self.progress_bar.setVisible(False)
            return False
    
    def lazy_load_yolo(self):
        """Load YOLO model on first use with progress."""
        if self.yolo_model is not None and self.yolo_model.is_loaded:
            return True
        
        try:
            from models.yolo.yolo_model import YOLOModel
            
            self.status_bar.showMessage("Loading YOLO model (first use)...")
            self.model_status.set_yolo_status("Loading...", False)
            
            if self.yolo_model is None:
                self.yolo_model = YOLOModel()
            
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(30)
            
            yolo_loaded = self.yolo_model.load_model()
            
            self.progress_bar.setValue(100)
            self.progress_bar.setVisible(False)
            
            if yolo_loaded:
                self.model_status.set_yolo_status("Ready", True)
                self.status_bar.showMessage("YOLO model loaded successfully")
                logger.info("YOLO model loaded on demand")
                return True
            else:
                self.model_status.set_yolo_status("Failed", False)
                self.status_bar.showMessage("YOLO model failed to load")
                return False
                
        except Exception as e:
            logger.error(f"YOLO loading error: {e}")
            self.model_status.set_yolo_status("Error", False)
            self.progress_bar.setVisible(False)
            return False
    
    def auto_save_current_image(self) -> bool:
        """Auto-save annotations for current image before navigating away."""
        
        if not self.current_image_path:
            logger.debug("Auto-save skipped: No image loaded")
            return True  # Nothing to save
        
        if not self.canvas.annotations:
            logger.debug(f"Auto-save skipped: No annotations for {Path(self.current_image_path).name}")
            return True  # Nothing to save
        
        try:
            # Get image shape from canvas (using original_image, not current_image)
            image_shape = None
            if hasattr(self.canvas, 'original_image') and self.canvas.original_image is not None:
                image_shape = self.canvas.original_image.shape
            
            # Auto-save annotations
            success = self.auto_save_manager.save_annotations(
                self.current_image_path,
                self.canvas.annotations,
                image_shape
            )
            
            if success:
                logger.info(f"💾 Auto-saved {len(self.canvas.annotations)} annotations for {Path(self.current_image_path).name}")
                self.status_bar.showMessage(f"💾 Auto-saved {len(self.canvas.annotations)} annotations", 2000)
            else:
                logger.warning(f"⚠️ Auto-save returned False for {Path(self.current_image_path).name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error: Auto-save failed for {Path(self.current_image_path).name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def auto_load_annotations(self, image_path: str) -> bool:
        """Auto-load annotations for image if they exist."""
        
        try:
            # Check if annotations exist
            if not self.auto_save_manager.has_saved_annotations(image_path):
                logger.debug(f"Auto-load: No saved annotations for {Path(image_path).name}")
                return False
            
            # Load annotations
            annotations = self.auto_save_manager.load_annotations(image_path)
            
            if annotations:
                # Clear current annotations
                self.canvas.annotations.clear()
                
                # Load annotations into canvas
                for annotation in annotations:
                    self.canvas.annotations.append(annotation)
                
                # Update canvas display with high priority
                self.canvas.update_display(priority='high')
                
                logger.info(f"📥 Auto-loaded {len(annotations)} annotations for {Path(image_path).name}")
                self.status_bar.showMessage(f"📥 Auto-loaded {len(annotations)} annotations", 2000)
                return True
            else:
                logger.debug(f"Auto-load: Empty annotations list for {Path(image_path).name}")
            
            return False
            
        except Exception as e:
            logger.error(f"Error: Auto-load failed for {Path(image_path).name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_image(self):
        """Load an image for annotation."""
        
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Load Image for Annotation",
            str(Path.home()),
            "Image Files (*.png *.jpg *.jpeg *.tiff *.bmp);;All Files (*)"
        )
        
        if file_path:
            try:
                # Auto-save current image before loading new one
                if self.current_image_path:
                    self.auto_save_current_image()
                
                # Load image into canvas
                success = self.canvas.load_image(file_path)
                
                if success:
                    self.current_image_path = file_path
                    
                    # Auto-load annotations if they exist
                    auto_loaded = self.auto_load_annotations(file_path)
                    
                    # Enable annotation tools and save button
                    self.file_controls.enable_save_button(True)
                    self.tool_controls.enable_tools(True)
                    
                    # Update image navigator
                    self.image_navigator.set_current_image(file_path)
                    
                    # Update navigation buttons
                    self.update_navigation_buttons()
                    
                    # Update navigation info in compact controls
                    current, total, name = self.image_navigator.get_navigation_info()
                    if total > 1:
                        self.file_controls.update_navigation_state(
                            self.image_navigator.has_previous(),
                            self.image_navigator.has_next(),
                            f"{current}/{total}: {name}"
                        )
                    else:
                        self.file_controls.update_navigation_state(
                            False, False, f"1/1: {name}"
                        )
                    
                    # Update status
                    status_msg = f"📷 Image loaded: {Path(file_path).name}"
                    if auto_loaded:
                        status_msg += f" (Navigator: {len(self.canvas.annotations)} annotations loaded)"
                    self.status_bar.showMessage(status_msg)
                    
                    # Update image stats
                    self.update_image_stats()
                    
                    logger.info(f"📷 Image loaded: {file_path}")
                    
                else:
                    QMessageBox.warning(self, "Error", "Failed to load image file")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading image: {e}")
                logger.error(f"Error: Image loading error: {e}")
    
    def new_project(self):
        """Start a new annotation project."""
        
        try:
            # Check if there are unsaved annotations
            if self.canvas.annotations:
                reply = QMessageBox.question(
                    self,
                    "New Project",
                    "You have unsaved annotations. Do you want to start a new project?\n\n"
                    "This will clear all current annotations.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    return
            
            # Clear all annotations
            self.canvas.clear_all()
            
            # Reset image navigator
            self.image_navigator = ImageNavigator()
            
            # Reset current image
            self.current_image_path = None
            
            # Update UI
            self.update_navigation_buttons()
            self.file_controls.update_navigation_state(False, False, "No image")
            
            # Update stats
            self.stats_text.setPlainText("🆕 New Project Started\n\nReady for annotation...")
            
            self.status_bar.showMessage("🆕 New project started")
            logger.info("🆕 New project started")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start new project: {e}")
            logger.error(f"Error: New project error: {e}")
    
    def load_next_image(self):
        """Load the next image in the current directory with auto-save/load."""
        
        try:
            if not self.image_navigator.has_next():
                self.status_bar.showMessage("No more images in directory")
                return
            
            # Auto-save current image annotations before moving to next
            if self.current_image_path:
                self.auto_save_current_image()
            
            # Get next image
            next_image = self.image_navigator.get_next_image()
            
            if next_image and self.canvas.load_image(next_image):
                self.current_image_path = next_image
                
                # Auto-load annotations if they exist
                auto_loaded = self.auto_load_annotations(next_image)
                
                # Update navigation buttons and info
                self.update_navigation_buttons()
                
                # Update status with auto-load info
                status_msg = f"📷 Next image: {Path(next_image).name}"
                if auto_loaded:
                    status_msg += f" (Navigator: {len(self.canvas.annotations)} annotations loaded)"
                self.status_bar.showMessage(status_msg)
                
                # Update stats
                self.update_image_stats()
                
                logger.info(f"📷 Next image loaded: {next_image}")
            else:
                self.status_bar.showMessage("Failed to load next image")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load next image: {e}")
            logger.error(f"Error: Next image error: {e}")
    
    def load_previous_image(self):
        """Load the previous image in the current directory with auto-save/load."""
        
        try:
            if not self.image_navigator.has_previous():
                self.status_bar.showMessage("No previous images in directory")
                return
            
            # Auto-save current image annotations before moving to previous
            if self.current_image_path:
                self.auto_save_current_image()
            
            # Get previous image
            prev_image = self.image_navigator.get_previous_image()
            
            if prev_image and self.canvas.load_image(prev_image):
                self.current_image_path = prev_image
                
                # Auto-load annotations if they exist
                auto_loaded = self.auto_load_annotations(prev_image)
                
                # Update navigation buttons and info
                self.update_navigation_buttons()
                
                # Update status with auto-load info
                status_msg = f"📷 Previous image: {Path(prev_image).name}"
                if auto_loaded:
                    status_msg += f" (Navigator: {len(self.canvas.annotations)} annotations loaded)"
                self.status_bar.showMessage(status_msg)
                
                # Update stats
                self.update_image_stats()
                
                logger.info(f"📷 Previous image loaded: {prev_image}")
            else:
                self.status_bar.showMessage("Failed to load previous image")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load previous image: {e}")
            logger.error(f"Error: Previous image error: {e}")
    
    def delete_all_annotations(self):
        """Delete all annotations."""
        
        try:
            if not self.canvas.annotations:
                QMessageBox.information(self, "Delete Annotations", "No annotations to delete.")
                return
            
            reply = QMessageBox.question(
                self,
                "Delete All Annotations",
                f"Are you sure you want to delete all {len(self.canvas.annotations)} annotations?\n\n"
                f"This action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                annotation_count = len(self.canvas.annotations)
                self.canvas.clear_all()
                
                self.status_bar.showMessage(f"🗑️ Deleted {annotation_count} annotations")
                logger.info(f"🗑️ Deleted all annotations: {annotation_count}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete annotations: {e}")
            logger.error(f"Error: Delete annotations error: {e}")
    
    def undo_last_annotation(self):
        """Undo the last annotation."""
        
        try:
            if not self.canvas.annotations:
                self.status_bar.showMessage("No annotations to undo")
                return
            
            # Remove last annotation
            last_annotation = self.canvas.annotations.pop()
            annotation_type = last_annotation.get('type', 'unknown')
            
            # Update display
            self.canvas.update_display()
            
            self.status_bar.showMessage(f"↩️ Undid last annotation: {annotation_type}")
            logger.info(f"↩️ Undid annotation: {annotation_type}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to undo annotation: {e}")
            logger.error(f"Error: Undo annotation error: {e}")
    
    def clear_canvas(self):
        """Clear the entire canvas including temporary annotations."""
        
        try:
            total_annotations = len(self.canvas.annotations)
            total_temp = len(self.canvas.temp_annotations)
            
            if total_annotations == 0 and total_temp == 0:
                self.status_bar.showMessage("Canvas is already clear")
                return
            
            # Clear everything
            self.canvas.clear_all()
            self.canvas.clear_temp_annotations()
            
            self.status_bar.showMessage(f"Cleanup: Canvas cleared: {total_annotations} annotations, {total_temp} temporary")
            logger.info(f"Cleanup: Canvas cleared: {total_annotations + total_temp} items")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear canvas: {e}")
            logger.error(f"Error: Clear canvas error: {e}")
    
    def update_navigation_buttons(self):
        """Update navigation button states."""
        
        has_next = self.image_navigator.has_next()
        has_prev = self.image_navigator.has_previous()
        
        # Update compact navigation controls
        current, total, name = self.image_navigator.get_navigation_info()
        info = f"{current}/{total}: {name}" if total > 0 else "No image"
        
        self.file_controls.update_navigation_state(has_prev, has_next, info)
    
    def update_image_stats(self):
        """Update image statistics display."""
        
        if self.current_image_path and self.canvas.original_image is not None:
            h, w = self.canvas.original_image.shape[:2]
            current, total, name = self.image_navigator.get_navigation_info()
            
            image_info = f"📷 Image: {name} ({current}/{total})\n"
            image_info += f"📏 Size: {w}×{h} pixels\n"
            image_info += f"Monitor: Annotations: {len(self.canvas.annotations)}"
            
            if self.canvas.temp_annotations:
                image_info += f" (+{len(self.canvas.temp_annotations)} temp)"
            
            self.stats_text.setPlainText(image_info)
    
    def save_annotations(self):
        """Save current annotations in format-appropriate way."""
        
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "No image loaded to save annotations for")
            return
        
        try:
            # Get annotations from canvas
            canvas_stats = self.canvas.get_canvas_stats()
            annotations_count = canvas_stats['annotations_count']
            
            if annotations_count == 0:
                QMessageBox.information(self, "Save Annotations", "No annotations to save.")
                return
            
            # Choose output directory
            file_dialog = QFileDialog()
            output_dir = file_dialog.getExistingDirectory(
                self,
                "Choose Output Directory for Annotations",
                str(Path(self.current_image_path).parent)
            )
            
            if output_dir:
                # Use smart annotation exporter
                from src.annotation_exporter import export_annotations_smart
                
                self.status_bar.showMessage("💾 Exporting annotations...")
                
                # Export with format detection
                result = export_annotations_smart(
                    annotations=self.canvas.annotations,
                    image_path=self.current_image_path,
                    image_shape=canvas_stats['image_shape'],
                    output_dir=output_dir
                )
                
                if result['status'] == 'success':
                    # Show detailed results
                    message = f"Success: Successfully exported {result['total_annotations']} annotations!\n\n"
                    
                    if result['yolo_annotations'] > 0:
                        message += f"YOLO: YOLO Format: {result['yolo_annotations']} rectangle/bbox annotations\n"
                        message += f"   → .txt file for object detection training\n\n"
                    
                    if result['mask_annotations'] > 0:
                        message += f"🎭 Mask Images: {result['mask_annotations']} segmentation annotations\n"
                        message += f"   → .png files for segmentation training\n\n"
                    
                    message += f"📄 JSON Backup: Complete annotation data\n"
                    message += f"File: Output: {result['output_directory']}"
                    
                    self.status_bar.showMessage(f"Success: Exported to {len(result['formats_exported'])} formats")
                    
                    QMessageBox.information(
                        self, 
                        "Export Complete", 
                        message
                    )
                    
                    # Update stats
                    export_info = f"📤 Export Summary:\n"
                    export_info += f"   Total: {result['total_annotations']} annotations\n"
                    export_info += f"   YOLO: {result['yolo_annotations']} rectangles\n"
                    export_info += f"   Masks: {result['mask_annotations']} segmentations\n"
                    export_info += f"   Formats: {', '.join(result['formats_exported'])}"
                    
                    self.stats_text.setPlainText(export_info)
                    
                else:
                    self.status_bar.showMessage("Error: Export failed")
                    QMessageBox.critical(
                        self, 
                        "Export Error", 
                        f"Failed to export annotations:\n{result.get('message', 'Unknown error')}"
                    )
                
        except Exception as e:
            self.status_bar.showMessage("Error: Export error")
            QMessageBox.critical(self, "Save Error", f"Failed to save annotations: {e}")
            logger.error(f"Error: Save annotations error: {e}")
    
    def set_tool(self, tool_name: str):
        """Set the current annotation tool."""
        
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "Please load an image first")
            return
        
        # Set tool on canvas
        self.canvas.set_tool(tool_name)
        
        self.status_bar.showMessage(f"Tool: Tool: {tool_name}")
        logger.info(f"Tool: Tool changed to: {tool_name}")
        
        # Update stats
        tool_names = {
            'magic_wand': 'Magic Wand (SAM)',
            'bbox': 'BBox Segment',
            'brush': 'Smart Brush',
            'auto': 'Auto Segment',
            'polygon': 'Manual Polygon',
            'rectangle': 'Manual Rectangle'
        }
        
        current_stats = self.stats_text.toPlainText()
        stats_lines = current_stats.split('\n')
        # Update the last line to show current tool
        if len(stats_lines) >= 3:
            stats_lines[-1] = f"Tool: Active Tool: {tool_names.get(tool_name, tool_name)}"
            self.stats_text.setPlainText('\n'.join(stats_lines))
    
    def run_auto_segment(self):
        """Run automatic segmentation on the current image."""
        
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "Please load an image first")
            return
        
        # Lazy load SAM if needed
        if not self.sam_model or not self.sam_model.is_loaded:
            if not self.lazy_load_sam():
                QMessageBox.warning(self, "Warning", "SAM model failed to load")
                return
        
        try:
            import cv2
            
            self.status_bar.showMessage("Running auto segmentation...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            # Load image
            image = cv2.imread(self.current_image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Run auto segmentation
            result = self.sam_model.predict_auto(image_rgb)
            
            self.progress_bar.setVisible(False)
            
            if result.get('success'):
                segments = result['results']
                processing_time = result['processing_time']
                
                # Add detected segments to canvas as annotations
                for segment in segments:
                    annotation = {
                        'type': 'auto_segmentation',
                        'mask': segment['mask'],
                        'confidence': segment.get('confidence', 0.5),
                        'processing_time': processing_time,
                        'timestamp': time.time()
                    }
                    self.canvas.add_annotation(annotation)
                
                self.status_bar.showMessage(f"Success: Added {len(segments)} objects in {processing_time:.1f}s")
                
                # Update stats
                stats_text = f"🔄 Auto Segmentation Results:\n"
                stats_text += f"   Objects found: {len(segments)}\n"
                stats_text += f"   Annotations added: {len(segments)}\n"
                stats_text += f"   Processing time: {processing_time:.1f}s\n"
                stats_text += f"   Status: Success: Complete"
                
                self.stats_text.setPlainText(stats_text)
                
                logger.info(f"Auto-segment: Added {len(segments)} annotations to canvas")
                
            else:
                error_msg = result.get('error', 'Unknown error')
                self.status_bar.showMessage(f"Error: Auto segmentation failed: {error_msg}")
                QMessageBox.warning(self, "Segmentation Failed", f"Auto segmentation failed: {error_msg}")
                
        except Exception as e:
            self.progress_bar.setVisible(False)
            logger.error(f"Error: Auto segmentation error: {e}")
            self.status_bar.showMessage(f"Error: Error: {e}")
            QMessageBox.critical(self, "Error", f"Auto segmentation error: {e}")
    
    def test_sam_model(self):
        """Test SAM model functionality."""
        
        if not self.sam_model or not self.sam_model.is_loaded:
            QMessageBox.warning(self, "Warning", "SAM model not loaded")
            return
        
        model_info = self.sam_model.get_model_info()
        performance = self.sam_model.get_performance_summary()
        
        QMessageBox.information(
            self,
            "SAM Model Info",
            f"Model Status: {'Success: Loaded' if model_info['is_loaded'] else 'Error: Not Loaded'}\n"
            f"Model Path: {model_info.get('model_name', 'Unknown')}\n\n"
            f"{performance}"
        )
    
    def test_yolo_model(self):
        """Test YOLO model functionality."""
        
        if not self.yolo_model or not self.yolo_model.is_loaded:
            QMessageBox.warning(self, "Warning", "YOLO model not loaded")
            return
        
        model_info = self.yolo_model.get_model_info()
        performance = self.yolo_model.get_performance_summary()
        
        QMessageBox.information(
            self,
            "YOLO Model Info",
            f"Model Status: {'Success: Loaded' if model_info['is_loaded'] else 'Error: Not Loaded'}\n"
            f"Model Path: {model_info.get('model_name', 'Unknown')}\n"
            f"Classes: {len(model_info.get('class_names', []))}\n\n"
            f"{performance}"
        )
    
    def optimize_memory(self):
        """Optimize memory usage."""
        
        try:
            import gc
            import psutil
            
            # Get initial memory
            process = psutil.Process()
            initial_memory = process.memory_info().rss / (1024 * 1024)
            
            # Run cleanup
            gc.collect()
            
            # Cleanup models if available
            if self.sam_model and hasattr(self.sam_model, '_cleanup_prediction_memory'):
                self.sam_model._cleanup_prediction_memory()
                
            if self.yolo_model and hasattr(self.yolo_model, 'cleanup'):
                pass  # Don't fully cleanup, just clean prediction memory
            
            # Cleanup auto-save cache
            if self.auto_save_manager:
                self.auto_save_manager.cleanup_memory()
            
            # Cleanup canvas cache if available
            if hasattr(self.canvas, 'invalidate_cache'):
                self.canvas.invalidate_cache()
            
            # Get final memory
            final_memory = process.memory_info().rss / (1024 * 1024)
            memory_saved = initial_memory - final_memory
            
            self.status_bar.showMessage(f"Cleanup: Memory optimized: {final_memory:.1f} MB")
            
            QMessageBox.information(
                self,
                "Memory Optimization",
                f"Memory optimization completed!\n\n"
                f"Before: {initial_memory:.1f} MB\n"
                f"After: {final_memory:.1f} MB\n"
                f"Saved: {memory_saved:.1f} MB"
            )
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Memory optimization failed: {e}")
    
    def show_memory_stats(self):
        """Show detailed memory statistics."""
        
        try:
            import psutil
            
            process = psutil.Process()
            memory_info = process.memory_info()
            
            stats = f"Monitor: Memory Statistics:\n\n"
            stats += f"RSS Memory: {memory_info.rss / (1024 * 1024):.1f} MB\n"
            stats += f"VMS Memory: {memory_info.vms / (1024 * 1024):.1f} MB\n"
            stats += f"Memory %: {process.memory_percent():.1f}%\n\n"
            
            if self.sam_model and self.sam_model.is_loaded:
                stats += f"SAM Model: Success: Loaded\n"
            else:
                stats += f"SAM Model: Error: Not Loaded\n"
                
            if self.yolo_model and self.yolo_model.is_loaded:
                stats += f"YOLO Model: Success: Loaded\n"
            else:
                stats += f"YOLO Model: Error: Not Loaded\n"
            
            QMessageBox.information(self, "Memory Statistics", stats)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to get memory stats: {e}")
    
    def show_help(self):
        """Show help dialog."""
        
        help_text = """Engine: Smart Annotator - User Guide

File: Getting Started:
1. Start new project (Ctrl+N) or load image (Ctrl+O)
2. Wait for AI models to load (SAM & YOLO)  
3. Select a class/label for your annotations
4. Choose an annotation tool from the toolbar
5. Create annotations (they'll be labeled automatically)
6. Navigate images (Left/Right arrows) and save (Ctrl+S)

Tool: Annotation Tools:

Model: AI-Powered Tools:
• Magic Wand (1): Click-based segmentation using SAM
• BBox Segment (2): Draw bounding box for segmentation
• Smart Brush (3): Manual pixel-level painting
• Auto Segment (4): Automatic object detection

✏️ Manual Tools:
• Manual Polygon (5): Click points to draw custom polygons
  - Click points to add to polygon
  - Double-click or press Enter to finish
  - Press Escape to cancel
• Manual Rectangle (6): Drag to draw rectangles
  - Click and drag to create rectangle
  - Release to finish

Label: Labeling System:
• Current Label: Shows active class for new annotations
• Class Management: Add, edit, remove annotation classes
• Color Coding: Each class has unique color for visual identification
• Automatic Assignment: All annotations get current class label
• Statistics: Track annotation count per class

⌨️ Keyboard Shortcuts:
File: File Operations:
• Ctrl+N: New Project (clear all annotations)
• Ctrl+O: Open Image
• Ctrl+S: Smart Export (format-aware saving)
• Ctrl+P: Preview Export
• Ctrl+Q: Exit Application

🖼️ Image Navigation:  
• Left Arrow: Previous Image
• Right Arrow: Next Image
• (Works with multiple images in same folder)

✏️ Editing Operations:
• Delete: Delete All Annotations
• Ctrl+Z: Undo Last Annotation  
• Ctrl+Del: Clear Canvas (including temp annotations)

Tool: Tools & Models:
• F5: Reload AI Models
• Ctrl+M: Optimize Memory
• 1-6: Select annotation tools (Magic Wand, BBox, Brush, Auto, Polygon, Rectangle)

Model: AI Models:
• SAM: Segment Anything Model for precise segmentation
• YOLO: Object detection and classification

Tips:
• Start with Ctrl+N for new project, Ctrl+O to load first image
• Use Left/Right arrows for quick image navigation
• Press F5 to reload models if needed, Ctrl+M for memory optimization  
• Use Delete to remove annotations, Ctrl+Z to undo last action
• Select class BEFORE creating annotations for proper labeling
• Use color coding to visually identify different classes
• Export with Ctrl+S for training-ready formats (YOLO/masks)
• Check Memory menu for usage statistics"""
        
        QMessageBox.information(self, "Smart Annotator - Help", help_text)
    
    def show_about(self):
        """Show about dialog."""
        
        about_text = """Engine: Smart Annotator v2.0
Memory Optimized Edition

AI-Powered Image Annotation Tool

Features:
Success: SAM (Segment Anything) Integration
Success: YOLO Object Detection  
Success: Smart Brush Tool
Success: Memory Leak Prevention
Success: Professional UI/UX

© 2025 Smart Annotator Project"""
        
        QMessageBox.about(self, "About Smart Annotator", about_text)
    
    def update_status(self):
        """Update status bar with system info."""
        
        if self.current_image_path:
            try:
                import psutil
                memory_mb = psutil.Process().memory_info().rss / (1024 * 1024)
                self.status_bar.showMessage(f"📷 {Path(self.current_image_path).name} | 💾 {memory_mb:.1f} MB")
            except:
                self.status_bar.showMessage(f"📷 {Path(self.current_image_path).name}")
        else:
            self.status_bar.showMessage("Engine: Smart Annotator Ready - Load an image to start")
    
    # Canvas Signal Handlers
    def on_annotation_created(self, annotation: dict):
        """Handle annotation created signal from canvas."""
        
        self.status_bar.showMessage(f"Success: Annotation created: {annotation.get('type', 'unknown')}")
        
        # Update stats
        canvas_stats = self.canvas.get_canvas_stats()
        current_stats = self.stats_text.toPlainText().split('\n')
        if len(current_stats) >= 3:
            current_stats[-2] = f"Monitor: Annotations: {canvas_stats['annotations_count']}"
            self.stats_text.setPlainText('\n'.join(current_stats))
        
        logger.info(f"Success: Annotation created: {annotation}")
    
    def on_point_clicked(self, x: int, y: int):
        """Handle point click for Magic Wand tool."""
        
        # Lazy load SAM if needed
        if not self.sam_model or not self.sam_model.is_loaded:
            if not self.lazy_load_sam():
                QMessageBox.warning(self, "Warning", "SAM model failed to load")
                return
        
        try:
            self.status_bar.showMessage(f"SAM: Processing Magic Wand at ({x}, {y})...")
            
            # Get image from canvas
            if self.canvas.original_image is None:
                return
            
            # Run SAM prediction
            result = self.sam_model.predict_with_point(self.canvas.original_image, (x, y))
            
            if result.get('success'):
                segments = result['results']
                processing_time = result['processing_time']
                
                # Add segmentation results to canvas
                for segment in segments:
                    annotation = {
                        'type': 'magic_wand_segmentation',
                        'mask': segment['mask'],
                        'confidence': segment['confidence'],
                        'point': (x, y),
                        'processing_time': processing_time,
                        'timestamp': time.time()
                    }
                    self.canvas.add_annotation(annotation)
                
                self.status_bar.showMessage(f"Success: Magic Wand: {len(segments)} segments in {processing_time:.1f}s")
                
            else:
                error_msg = result.get('error', 'Unknown error')
                self.status_bar.showMessage(f"Error: Magic Wand failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error: Magic Wand error: {e}")
            self.status_bar.showMessage(f"Error: Error: {e}")
    
    def on_bbox_drawn(self, x1: int, y1: int, x2: int, y2: int):
        """Handle bbox drawn for BBox Segment tool."""
        
        logger.info(f"BBox drawn signal received: ({x1}, {y1}, {x2}, {y2})")
        
        # Lazy load SAM if needed
        if not self.sam_model or not self.sam_model.is_loaded:
            logger.warning("SAM model not loaded, attempting to load...")
            if not self.lazy_load_sam():
                QMessageBox.warning(self, "Warning", "SAM model failed to load")
                return
        
        try:
            self.status_bar.showMessage(f"Processing BBox segmentation...")
            logger.info("Starting BBox segmentation...")
            
            # Get image from canvas
            if self.canvas.original_image is None:
                logger.error("No image loaded in canvas")
                self.status_bar.showMessage("Error: No image loaded")
                return
            
            logger.info(f"Image shape: {self.canvas.original_image.shape}")
            logger.info(f"BBox: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
            
            # Run SAM bbox prediction
            result = self.sam_model.predict_with_bbox(self.canvas.original_image, (x1, y1, x2, y2))
            
            logger.info(f"SAM prediction result: success={result.get('success')}")
            
            if result.get('success'):
                segments = result['results']
                processing_time = result['processing_time']
                
                logger.info(f"Got {len(segments)} segments from SAM")
                
                if len(segments) == 0:
                    # No segments found in bbox
                    self.status_bar.showMessage(f"⚠️ No objects found in drawn rectangle. Try a different area.")
                    QMessageBox.information(
                        self,
                        "No Objects Found",
                        "SAM didn't detect any clear objects in the drawn rectangle.\n\n"
                        "Tips:\n"
                        "• Draw the rectangle around a specific object\n"
                        "• Make sure the object has clear boundaries\n"
                        "• Try Magic Wand tool (click) instead\n"
                        "• Check that the area contains visible features"
                    )
                    logger.warning("No segments found in bbox area")
                    return
                
                # Add segmentation results to canvas
                for i, segment in enumerate(segments):
                    logger.info(f"Adding segment {i+1}: mask shape = {segment['mask'].shape if 'mask' in segment else 'NO MASK'}")
                    
                    annotation = {
                        'type': 'bbox_segmentation',
                        'mask': segment['mask'],
                        'confidence': segment.get('confidence', 0.5),
                        'bbox': (x1, y1, x2, y2),
                        'processing_time': processing_time,
                        'timestamp': time.time()
                    }
                    self.canvas.add_annotation(annotation)
                    logger.info(f"Annotation added to canvas")
                
                self.status_bar.showMessage(f"Success: BBox Segment: {len(segments)} segments in {processing_time:.1f}s")
                logger.info(f"BBox segmentation completed successfully")
                
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"SAM bbox prediction failed: {error_msg}")
                self.status_bar.showMessage(f"Error: BBox Segment failed: {error_msg}")
                QMessageBox.warning(self, "Segmentation Failed", f"BBox segmentation failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error: BBox Segment error: {e}")
            import traceback
            traceback.print_exc()
            self.status_bar.showMessage(f"Error: {e}")
            QMessageBox.critical(self, "Error", f"BBox segmentation error: {e}")
    
    def on_auto_segment_requested(self):
        """Handle auto segmentation request."""
        self.run_auto_segment()
    
    def on_tool_feedback(self, message: str):
        """Handle tool feedback from canvas."""
        self.status_bar.showMessage(message)
    
    def on_annotation_format_changed(self, format_type: str):
        """Handle annotation format change (segmentation vs bbox)."""
        
        # Store format preference
        self.annotation_format = format_type
        
        # Update canvas if it has this method
        if hasattr(self.canvas, 'set_annotation_format'):
            self.canvas.set_annotation_format(format_type)
        
        # Update status
        format_names = {
            'segmentation': '🎭 Segmentation Mask',
            'bbox': '📦 Bounding Box'
        }
        self.status_bar.showMessage(f"Format: Output format: {format_names.get(format_type, format_type)}")
        logger.info(f"Format: Annotation format changed to: {format_type}")
    
    def on_class_changed(self, class_id: int):
        """Handle class selection change."""
        self.canvas.set_current_class(class_id)
        if self.label_manager:
            class_info = self.label_manager.get_class(class_id)
            if class_info:
                self.status_bar.showMessage(f"Label: {class_info['name']}")
        logger.info(f"Label: Class changed to: {class_id}")
    
    def on_class_added(self, class_data: Dict[str, Any]):
        """Handle new class addition."""
        self.status_bar.showMessage(f"Added: {class_data['name']}")
        logger.info(f"Label: Added class: {class_data['name']}")
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        
        key = event.key()
        modifiers = event.modifiers()
        
        try:
            # Navigation shortcuts
            if key == Qt.Key_Right and modifiers == Qt.NoModifier:
                self.load_next_image()
            elif key == Qt.Key_Left and modifiers == Qt.NoModifier:
                self.load_previous_image()
            
            # Delete shortcuts  
            elif key == Qt.Key_Delete and modifiers == Qt.NoModifier:
                self.delete_all_annotations()
            elif key == Qt.Key_Delete and modifiers == Qt.ControlModifier:
                self.clear_canvas()
            
            # Other shortcuts are handled by menu actions automatically
            # (Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+Q, Ctrl+Z, F5, etc.)
            
            else:
                # Pass unhandled events to parent
                super().keyPressEvent(event)
                
        except Exception as e:
            logger.error(f"Error: Keyboard shortcut error: {e}")
            super().keyPressEvent(event)
    
    def preview_export(self):
        """Preview what formats will be exported based on current annotations."""
        
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "No image loaded")
            return
        
        try:
            canvas_stats = self.canvas.get_canvas_stats()
            annotations_count = canvas_stats['annotations_count']
            
            if annotations_count == 0:
                QMessageBox.information(self, "Export Preview", "No annotations to export.")
                return
            
            # Analyze annotations
            yolo_count = 0
            mask_count = 0
            annotation_types = {}
            
            for annotation in self.canvas.annotations:
                annotation_type = annotation.get('type', 'unknown')
                
                # Count for each export format
                if annotation_type in ['manual_rectangle', 'bbox_segmentation']:
                    yolo_count += 1
                elif annotation_type in ['magic_wand_segmentation', 'brush_segmentation', 'manual_polygon']:
                    mask_count += 1
                
                # Count annotation types
                annotation_types[annotation_type] = annotation_types.get(annotation_type, 0) + 1
            
            # Create preview message
            preview_msg = f"📋 Export Preview for {annotations_count} annotations:\n\n"
            
            if yolo_count > 0:
                preview_msg += f"YOLO: YOLO Format Export:\n"
                preview_msg += f"   → {yolo_count} rectangle/bbox annotations\n"
                preview_msg += f"   → Will create .txt file for YOLO training\n"
                preview_msg += f"   → Format: class_id center_x center_y width height\n\n"
            
            if mask_count > 0:
                preview_msg += f"🎭 Mask Image Export:\n"
                preview_msg += f"   → {mask_count} segmentation annotations\n"
                preview_msg += f"   → Will create individual .png mask files\n"
                preview_msg += f"   → Will create combined mask with different values\n\n"
            
            preview_msg += f"📄 JSON Backup Export:\n"
            preview_msg += f"   → Complete annotation data in JSON format\n"
            preview_msg += f"   → Includes all metadata and timestamps\n\n"
            
            preview_msg += f"Monitor: Annotation Breakdown:\n"
            for ann_type, count in annotation_types.items():
                format_info = ""
                if ann_type in ['manual_rectangle', 'bbox_segmentation']:
                    format_info = " → YOLO"
                elif ann_type in ['magic_wand_segmentation', 'brush_segmentation', 'manual_polygon']:
                    format_info = " → Mask"
                
                preview_msg += f"   • {ann_type}: {count}{format_info}\n"
            
            QMessageBox.information(self, "Export Preview", preview_msg)
            
        except Exception as e:
            QMessageBox.critical(self, "Preview Error", f"Failed to preview export: {e}")
            logger.error(f"Error: Preview export error: {e}")
    
    def create_yolo_classes(self):
        """Create YOLO classes.txt file."""
        
        try:
            # Choose output directory
            file_dialog = QFileDialog()
            output_dir = file_dialog.getExistingDirectory(
                self,
                "Choose Directory for YOLO Classes File",
                str(Path.home())
            )
            
            if output_dir:
                from src.annotation_exporter import AnnotationExporter
                
                # Default class names (user can modify)
                class_names = [
                    'manual_annotation',
                    'ai_detection',
                    'object',
                    'person',
                    'vehicle'
                ]
                
                # Ask user for custom class names
                from PyQt5.QtWidgets import QInputDialog
                
                text, ok = QInputDialog.getMultiLineText(
                    self, 
                    'YOLO Class Names',
                    'Enter class names (one per line):\n\n' +
                    'Default classes:\n' + '\n'.join(class_names),
                    '\n'.join(class_names)
                )
                
                if ok and text.strip():
                    class_names = [line.strip() for line in text.split('\n') if line.strip()]
                
                # Create classes file
                exporter = AnnotationExporter()
                classes_file = exporter.create_class_names_file(output_dir, class_names)
                
                self.status_bar.showMessage(f"📋 YOLO classes file created")
                
                QMessageBox.information(
                    self, 
                    "Classes File Created", 
                    f"Created YOLO classes file:\n{classes_file}\n\n"
                    f"Classes ({len(class_names)}):\n" + 
                    '\n'.join(f"{i}: {name}" for i, name in enumerate(class_names))
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Classes Error", f"Failed to create classes file: {e}")
            logger.error(f"Error: Create classes error: {e}")
    
    def toggle_performance_caching(self):
        """Toggle performance caching on/off."""
        
        try:
            enabled = self.performance_caching_btn.isChecked()
            
            # Enable/disable caching in canvas
            if hasattr(self.canvas, 'enable_performance_caching'):
                self.canvas.enable_performance_caching(enabled)
            
            # Update button text
            if enabled:
                self.performance_caching_btn.setText("Disable Performance Caching")
                self.status_bar.showMessage("App: Performance caching enabled")
            else:
                self.performance_caching_btn.setText("Enable Performance Caching")
                self.status_bar.showMessage("🐌 Performance caching disabled")
            
            logger.info(f"App: Performance caching: {'enabled' if enabled else 'disabled'}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to toggle performance caching: {e}")
            logger.error(f"Error: Toggle performance caching error: {e}")
    
    def show_performance_stats(self):
        """Show canvas performance statistics."""
        
        try:
            # Get performance stats from canvas
            if hasattr(self.canvas, 'get_performance_stats'):
                stats = self.canvas.get_performance_stats()
                
                # Format performance information
                perf_info = f"""Monitor: Canvas Performance Statistics:

⏱️ Update Performance:
   Average Update Time: {stats['avg_update_time']:.3f}s
   Maximum Update Time: {stats['max_update_time']:.3f}s
   Total Updates: {stats['total_updates']}
   Slow Updates: {stats['slow_updates']}

📈 Performance Score: {stats['performance_score']:.1f}/100

Monitor: Annotation Load:
   Average Annotation Count: {stats['avg_annotation_count']:.1f}
   Memory Usage: {stats['memory_usage_mb']:.1f} MB

App: Optimization Status:
   Performance Caching: {'Success: Enabled' if stats['caching_enabled'] else 'Error: Disabled'}
   Cache Status: {'Success: Valid' if stats['cache_valid'] else '🔄 Building'}

Recommendations:"""
                
                for rec in stats.get('optimization_recommendations', []):
                    perf_info += f"\n   • {rec}"
                
                # Add auto-save statistics
                if self.auto_save_manager:
                    auto_save_stats = self.auto_save_manager.get_statistics()
                    
                    perf_info += f"""

💾 Auto-Save Performance:
   Status: {'Success: Enabled' if auto_save_stats['enabled'] else 'Error: Disabled'}
   Saved: {auto_save_stats['save_count']} images
   Loaded: {auto_save_stats['load_count']} images
   Avg Save Time: {auto_save_stats['avg_save_time']:.3f}s
   Avg Load Time: {auto_save_stats['avg_load_time']:.3f}s
   Cache Entries: {auto_save_stats['cached_images']}
   Total Auto-saves: {auto_save_stats['saved_files_count']} files"""
                
                # Show performance dialog
                QMessageBox.information(self, "Performance Statistics", perf_info)
                
            else:
                QMessageBox.information(self, "Performance Stats", 
                                      "Performance monitoring not available in this version.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get performance stats: {e}")
            logger.error(f"Error: Show performance stats error: {e}")
    
    def show_auto_save_stats(self):
        """Show detailed auto-save statistics."""
        
        try:
            if not self.auto_save_manager:
                QMessageBox.warning(self, "Auto-Save Stats", "Auto-save manager not initialized.")
                return
            
            # Get formatted statistics
            stats_text = self.auto_save_manager.get_formatted_statistics()
            
            # Add directory information
            stats = self.auto_save_manager.get_statistics()
            stats_text += f"\n\n📁 Directory: {stats['auto_save_directory']}"
            
            QMessageBox.information(self, "Auto-Save Statistics", stats_text)
            logger.info("Displayed auto-save statistics")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get auto-save stats: {e}")
            logger.error(f"Error: Show auto-save stats error: {e}")
    
    def toggle_auto_save(self):
        """Toggle auto-save on/off."""
        
        try:
            if not self.auto_save_manager:
                QMessageBox.warning(self, "Auto-Save", "Auto-save manager not initialized.")
                return
            
            # Get current state
            stats = self.auto_save_manager.get_statistics()
            current_state = stats['enabled']
            
            # Toggle
            new_state = not current_state
            self.auto_save_manager.enable_auto_save(new_state)
            
            # Update status
            if new_state:
                self.status_bar.showMessage("💾 Auto-save enabled")
                QMessageBox.information(
                    self, 
                    "Auto-Save Enabled", 
                    "Auto-save is now enabled.\n\n"
                    "Your annotations will be automatically saved when navigating between images."
                )
            else:
                self.status_bar.showMessage("⚠️ Auto-save disabled")
                QMessageBox.warning(
                    self, 
                    "Auto-Save Disabled", 
                    "Auto-save is now disabled.\n\n"
                    "Warning: You will need to manually save your annotations.\n"
                    "Use Ctrl+S to export your work."
                )
            
            logger.info(f"Auto-save toggled: {'enabled' if new_state else 'disabled'}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to toggle auto-save: {e}")
            logger.error(f"Error: Toggle auto-save error: {e}")
    
    def closeEvent(self, event):
        """Handle application close event."""
        
        # Cleanup models
        try:
            if self.sam_model:
                self.sam_model.cleanup()
            if self.yolo_model:
                self.yolo_model.cleanup()
        except:
            pass
        
        logger.info("Exit: Smart Annotator GUI closing")
        event.accept()


def create_smart_gui_app() -> Optional[QApplication]:
    """Create and configure Smart Annotator GUI application."""
    
    if not PYQT5_AVAILABLE:
        print("Error: PyQt5 not available - cannot create GUI")
        return None
    
    try:
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("Smart Annotator")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("Smart Annotator Project")
        
        # Set application style
        app.setStyle('Fusion')  # Modern cross-platform style
        
        return app
        
    except Exception as e:
        print(f"Error: Failed to create GUI application: {e}")
        return None


def run_smart_gui():
    """Run the Smart Annotator GUI application."""
    
    print("Canvas: Starting Smart Annotator GUI...")
    
    app = create_smart_gui_app()
    if not app:
        return False
    
    try:
        # Create main window
        window = SmartAnnotatorGUI()
        window.show()
        
        print("Success: Smart Annotator GUI launched successfully!")
        logger.info("App: Smart Annotator GUI application started")
        
        # Run application event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Error: GUI application error: {e}")
        logger.error(f"GUI application error: {e}")
        return False


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='Engine: %(asctime)s - %(levelname)s - %(message)s'
    )
    
    run_smart_gui()
