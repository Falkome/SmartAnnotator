#!/usr/bin/env python3
"""
Smart Dialogs - Dialog Windows for Smart Annotator

User-friendly dialogs for help, about, and other information.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QMessageBox, QTabWidget, QWidget, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap


def show_about(parent=None):
    """Show About Smart Annotator dialog."""
    
    msg = QMessageBox(parent)
    msg.setWindowTitle("About Smart Annotator")
    msg.setIcon(QMessageBox.Information)
    
    about_text = """
    Engine: Smart Annotator v1.0
    AI-Powered Image Annotation System
    
    ✨ Features:
    • Smart SAM integration for precise segmentation
    • YOLO object detection and classification  
    • Intelligent tool recommendations
    • AI-powered suggestions and automation
    • Modern, user-friendly interface
    
    App: Built with:
    • Python & PyQt5
    • Ultralytics YOLO & SAM
    • OpenCV & NumPy
    • Smart AI algorithms
    
    📧 Support: Smart annotation made simple!
    
    Engine: Where AI meets Human Intelligence
    """
    
    msg.setText(about_text)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


def show_help(parent=None):
    """Show Smart Annotator Help dialog."""
    
    dialog = SmartHelpDialog(parent)
    dialog.exec_()


class SmartHelpDialog(QDialog):
    """Comprehensive help dialog for Smart Annotator."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Engine: Smart Annotator - User Guide")
        self.setModal(True)
        self.resize(700, 600)
        
        # Apply styling
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QTabWidget::pane {
                border: 1px solid #3498db;
                border-radius: 4px;
                background-color: #34495e;
            }
            QTabBar::tab {
                background-color: #34495e;
                color: #ecf0f1;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
            }
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #3498db;
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
            }
            QLabel {
                color: #ecf0f1;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize help dialog UI."""
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Engine: Smart Annotator - Complete User Guide")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #3498db; padding: 10px;")
        layout.addWidget(title)
        
        # Tab widget for different help sections
        tab_widget = QTabWidget()
        
        # Getting Started tab
        tab_widget.addTab(self.create_getting_started_tab(), "App: Getting Started")
        
        # Tools tab  
        tab_widget.addTab(self.create_tools_tab(), "Tool: Annotation Tools")
        
        # AI Features tab
        tab_widget.addTab(self.create_ai_features_tab(), "Engine: AI Features")
        
        # Tips & Tricks tab
        tab_widget.addTab(self.create_tips_tab(), "Tips & Tricks")
        
        # Troubleshooting tab
        tab_widget.addTab(self.create_troubleshooting_tab(), "🔧 Troubleshooting")
        
        layout.addWidget(tab_widget)
        
        # Close button
        close_btn = QPushButton("Success: Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setMaximumWidth(100)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
    
    def create_getting_started_tab(self) -> QWidget:
        """Create getting started tab."""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        content = """
        App: Getting Started with Smart Annotator
        
        Welcome to the AI-powered image annotation system! Follow these steps to get started:
        
        📋 STEP 1: Load an Image
        ========================
        1. Click "Navigator: Load Image" in the control panel
        2. Select your image file (PNG, JPG, TIFF, etc.)
        3. The image will appear in the main canvas
        
        Model: STEP 2: Load AI Models
        =========================
        1. Select your preferred model:
           • SAM (Segment Anything) - Best for precise segmentation
           • YOLO - Best for object detection
           • Auto Select - Let AI choose the best model
        
        2. Click "Model: Load Model" to initialize
        3. Wait for "Status: Ready" confirmation
        
        SAM: STEP 3: Start Annotating
        ===========================
        1. Choose an annotation tool:
           • SAM: Magic Wand - Click objects to segment
           • YOLO: BBox Segment - Draw boxes around objects
           • 🔄 Auto Segment - Automatically find all objects
        
        2. Click or draw on your image
        3. Review AI-generated annotations
        4. Double-click to confirm or press ESC to cancel
        
        💾 STEP 4: Save Your Work
        =========================
        1. Click "💾 Save Annotations" when done
        2. Choose JSON format for compatibility
        3. Your annotations and metadata will be saved
        
        🎉 That's it! You're ready to annotate smartly!
        
        Quick Tips:
        • Use Smart Mode for intelligent suggestions
        • Adjust confidence threshold for better results
        • Check session statistics for productivity insights
        """
        
        text_edit.setText(content)
        layout.addWidget(text_edit)
        
        return widget
    
    def create_tools_tab(self) -> QWidget:
        """Create annotation tools tab."""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        content = """
        Tool: Annotation Tools Guide
        
        Smart Annotator provides three intelligent tools for different annotation needs:
        
        SAM: MAGIC WAND TOOL
        ==================
        Purpose: Precise object segmentation with single clicks
        
        How to use:
        1. Select "SAM: Magic Wand" tool
        2. Click anywhere on the object you want to segment  
        3. AI will automatically create precise mask
        4. Review the yellow preview overlay
        5. Double-click to confirm or ESC to cancel
        
        Best for:
        Success: Well-defined objects with clear boundaries
        Success: High-contrast images
        Success: When you need pixel-perfect segmentation
        
        YOLO: BBOX SEGMENT TOOL  
        ====================
        Purpose: Draw bounding boxes for object detection/segmentation
        
        How to use:
        1. Select "YOLO: BBox Segment" tool
        2. Click and drag to draw a rectangle around object
        3. AI will segment everything inside the box
        4. Adjust box size while drawing
        5. Release mouse to complete
        
        Best for:
        Success: Multiple objects in one area
        Success: Complex backgrounds
        Success: When you want to control the region precisely
        
        🔄 AUTO SEGMENT TOOL
        ====================
        Purpose: Automatic detection and segmentation of all objects
        
        How to use:
        1. Select "🔄 Auto Segment" tool
        2. Click anywhere on the image
        3. AI will automatically find and segment ALL objects
        4. Review all detected objects with confidence scores
        5. Individual objects can be accepted or rejected
        
        Best for:
        Success: Images with multiple clear objects
        Success: Batch annotation workflows  
        Success: Initial object discovery
        Success: When you want comprehensive coverage
        
        ⌨️ KEYBOARD SHORTCUTS
        =====================
        • ESC - Cancel current operation
        • ENTER - Confirm temporary annotations  
        • DELETE - Clear all annotations
        • Double-click - Confirm single annotation
        
        Canvas: VISUAL FEEDBACK
        ==================
        • Green overlay: Confirmed annotations
        • Orange overlay: Temporary/preview annotations  
        • Magenta box: Bounding box being drawn
        • Yellow circle: Tool cursor position
        • Cyan boxes: AI-detected objects
        """
        
        text_edit.setText(content)
        layout.addWidget(text_edit)
        
        return widget
    
    def create_ai_features_tab(self) -> QWidget:
        """Create AI features tab."""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        content = """
        Engine: AI Features & Smart Capabilities
        
        Smart Annotator uses advanced AI to make annotation faster and more accurate:
        
        SAM: SMART MODEL SELECTION
        ========================
        • Automatically chooses the best AI model for your image
        • Considers image size, complexity, and content type
        • Switches between SAM and YOLO based on task requirements
        • Optimizes for speed vs accuracy based on your preferences
        
        Engine: INTELLIGENT SUGGESTIONS
        ===========================
        Smart Annotator analyzes your image and provides recommendations:
        
        Monitor: Image Analysis:
        • Edge density analysis for tool recommendations
        • Brightness and contrast evaluation
        • Object complexity assessment
        • Size optimization suggestions
        
        Smart Recommendations:
        • "High edge density - SAM Magic Wand optimal"
        • "Large image - consider BBox tool for efficiency"
        • "Low contrast - adjust confidence threshold"
        • "Multiple objects detected - try Auto Segment"
        
        ⚙️ ADAPTIVE SETTINGS
        =====================
        SAM: Confidence Threshold:
        • Automatically adjusts based on image characteristics
        • Learns from your corrections and preferences
        • Higher threshold = fewer but more accurate results
        • Lower threshold = more detections, some false positives
        
        ✨ Smart Refinement:
        • Automatically improves mask boundaries
        • Removes noise and fills small gaps
        • Smooths jagged edges for cleaner results
        • Can be toggled on/off based on preference
        
        📈 PERFORMANCE OPTIMIZATION
        ============================
        App: Speed Improvements:
        • Caches frequently used models
        • Optimizes processing based on image size
        • Smart memory management prevents crashes
        • Progressive loading for large images
        
        Monitor: Quality Enhancements:
        • Multi-model ensemble for better accuracy
        • Context-aware post-processing
        • Confidence-based result filtering
        • Automatic quality assessment
        
        🔍 OBJECT DETECTION INTELLIGENCE
        =================================
        When using YOLO detection:
        • Recognizes 80+ common object classes
        • Provides confidence scores for each detection
        • Filters out low-quality detections automatically  
        • Groups similar objects intelligently
        • Avoids duplicate detections with smart NMS
        
        📚 LEARNING CAPABILITIES
        ========================
        Smart Annotator learns from your usage:
        • Remembers your preferred tools for different images
        • Adjusts confidence thresholds based on your corrections
        • Learns annotation patterns and suggests optimizations
        • Improves recommendations over time
        
        💾 SMART MEMORY MANAGEMENT
        ==========================
        • Automatically frees unused model memory
        • Prevents memory leaks during long sessions
        • Optimizes GPU usage for better performance
        • Smart caching for frequently used models
        
        🔧 CUSTOMIZATION OPTIONS
        ========================
        All AI features can be customized:
        • Toggle Smart Mode on/off
        • Adjust confidence thresholds manually
        • Enable/disable auto suggestions
        • Control smart refinement settings
        • Set maximum detection limits
        """
        
        text_edit.setText(content)
        layout.addWidget(text_edit)
        
        return widget
    
    def create_tips_tab(self) -> QWidget:
        """Create tips & tricks tab."""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        content = """
        Tips & Tricks for Better Annotations
        
        App: WORKFLOW OPTIMIZATION
        ========================
        
        📈 Start with Auto Segment:
        • Use "🔄 Auto Segment" first to discover all objects
        • Review AI suggestions before manual annotation
        • Accept obvious correct detections to save time
        • Use other tools for missed or incorrect objects
        
        SAM: Tool Selection Strategy:
        • Magic Wand: Single, well-defined objects
        • BBox Segment: Complex scenes, multiple objects
        • Auto Segment: Initial discovery, batch processing
        
        ⚙️ SETTINGS OPTIMIZATION
        ========================
        
        SAM: Confidence Threshold Tuning:
        • Start with default 0.5 for balanced results
        • Increase (0.7+) for fewer, higher-quality detections
        • Decrease (0.3-) to catch more objects, expect noise
        • Adjust based on image quality and requirements
        
        Engine: Smart Mode Benefits:
        • Keep enabled for intelligent suggestions
        • Provides context-aware tool recommendations
        • Automatically optimizes settings for each image
        • Learn from your annotation patterns
        
        Canvas: IMAGE PREPARATION TIPS
        =========================
        
        📸 Best Image Practices:
        • Use high-resolution images when possible
        • Ensure good contrast between objects and background
        • Avoid overly compressed JPEGs for precision work
        • Consider image orientation for optimal results
        
        🖼️ Format Recommendations:
        • PNG: Best for screenshots, graphics, text
        • TIFF: Ideal for scientific/medical images
        • JPEG: Good for photos, but watch compression
        • WebP: Modern format with good compression
        
        PRODUCTIVITY HACKS
        =====================
        
        ⌨️ Use Keyboard Shortcuts:
        • ESC: Quick cancel for mistakes
        • ENTER: Fast confirmation
        • DELETE: Clear all and start over
        • Double-click: Confirm individual annotations
        
        Monitor: Monitor Your Stats:
        • Check session statistics regularly
        • Identify your most productive tools
        • Track annotation speed improvements
        • Use stats to optimize workflow
        
        💾 Save Strategy:
        • Save frequently to avoid losing work
        • Use descriptive filenames with dates
        • JSON format preserves all metadata
        • Consider version control for important projects
        
        🔧 TROUBLESHOOTING QUICK FIXES
        ==============================
        
        Error: Poor Segmentation Results:
        • Try different tools (Magic Wand vs BBox)
        • Adjust confidence threshold
        • Enable Smart Refinement
        • Check image quality and contrast
        
        Slow Performance:
        • Close other applications to free memory
        • Use smaller images for initial testing
        • Enable Smart Mode for optimization
        • Consider using faster models (tiny vs large)
        
        SAM: Missed Objects:
        • Lower confidence threshold
        • Try Auto Segment for comprehensive detection
        • Use BBox tool to manually specify regions
        • Check if objects are in model's training classes
        
        📈 ADVANCED TECHNIQUES
        ======================
        
        🔄 Iterative Refinement:
        1. Start with Auto Segment for overview
        2. Use Magic Wand for precise corrections
        3. Use BBox for complex regions
        4. Review and refine with Smart Mode suggestions
        
        Canvas: Quality Control:
        • Always review AI suggestions before confirming
        • Use different tools to verify results
        • Check edge quality with Smart Refinement
        • Compare results with different confidence levels
        
        Monitor: Batch Processing:
        • Load similar images in sequence
        • Use consistent settings for image series
        • Save settings templates for reuse
        • Monitor statistics for quality consistency
        
        Engine: LEARNING FROM AI
        ====================
        • Pay attention to AI suggestions and learn patterns
        • Experiment with different tools on same objects
        • Use AI feedback to improve your technique
        • Share successful strategies with team members
        """
        
        text_edit.setText(content)
        layout.addWidget(text_edit)
        
        return widget
    
    def create_troubleshooting_tab(self) -> QWidget:
        """Create troubleshooting tab."""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        content = """
        🔧 Troubleshooting Guide
        
        Common issues and solutions for Smart Annotator:
        
        Error: MODEL LOADING ISSUES
        =======================
        
        Problem: "SAM model not available" error
        Solutions:
        • Install ultralytics: pip install ultralytics
        • Check internet connection for model download
        • Verify weights/sam/ folder exists
        • Try different model size (tiny vs large)
        
        Problem: "YOLO model failed to load"
        Solutions:
        • Ensure PyTorch is installed properly
        • Check CUDA compatibility if using GPU
        • Try CPU mode if GPU issues persist
        • Restart application and try again
        
        Problem: "No models detected"
        Solutions:
        • Place model files in weights/ directory
        • Check file permissions
        • Verify .pt file integrity
        • Download models manually if auto-download fails
        
        🖼️ IMAGE LOADING PROBLEMS
        =========================
        
        Problem: "Failed to load image" error
        Solutions:
        • Check image file format (PNG, JPG, TIFF supported)
        • Verify file is not corrupted
        • Try smaller image size
        • Check file permissions
        • Ensure file path has no special characters
        
        Problem: Image appears blank or corrupted
        Solutions:
        • Try opening image in another program first
        • Convert to standard format (PNG recommended)
        • Check color space (RGB preferred)
        • Reduce image size if extremely large
        
        PERFORMANCE ISSUES
        ====================
        
        Problem: Application runs slowly
        Solutions:
        • Close other memory-intensive applications
        • Use smaller model sizes (tiny instead of large)
        • Reduce image resolution
        • Enable Smart Mode for optimization
        • Restart application periodically
        
        Problem: Out of memory errors
        Solutions:
        • Use CPU mode instead of GPU
        • Process smaller images
        • Clear annotations frequently
        • Restart application
        • Add more system RAM if possible
        
        Problem: GPU not detected
        Solutions:
        • Install CUDA toolkit
        • Update graphics drivers
        • Check PyTorch CUDA installation
        • Use CPU mode as fallback
        
        SAM: ANNOTATION QUALITY ISSUES
        ============================
        
        Problem: Poor segmentation results
        Solutions:
        • Adjust confidence threshold
        • Try different annotation tools
        • Enable Smart Refinement
        • Use higher resolution images
        • Check image contrast and quality
        
        Problem: Objects not detected
        Solutions:
        • Lower confidence threshold
        • Use Manual tools instead of Auto
        • Try different model (SAM vs YOLO)
        • Check if object type is supported
        • Improve image quality
        
        Problem: Too many false detections
        Solutions:
        • Increase confidence threshold
        • Enable Smart Mode filtering
        • Use more precise tools (Magic Wand)
        • Review and clean results manually
        
        💾 SAVING/LOADING PROBLEMS
        ==========================
        
        Problem: Cannot save annotations
        Solutions:
        • Check disk space availability
        • Verify write permissions in target folder
        • Use different file location
        • Try shorter filename
        • Close other applications using files
        
        Problem: Saved files are corrupted
        Solutions:
        • Always use .json format
        • Avoid special characters in filenames
        • Don't interrupt saving process
        • Use UTF-8 encoding
        • Backup important annotations
        
        🖥️ GUI/INTERFACE ISSUES
        =======================
        
        Problem: Interface elements not visible
        Solutions:
        • Check screen resolution compatibility
        • Try different system scaling settings
        • Restart application
        • Update PyQt5: pip install --upgrade PyQt5
        
        Problem: Buttons not responding
        Solutions:
        • Wait for current operation to complete
        • Check if model is still loading
        • Restart application
        • Verify PyQt5 installation
        
        Problem: Canvas not updating
        Solutions:
        • Try loading different image
        • Clear all annotations and retry
        • Restart application
        • Check graphics drivers
        
        🚨 CRITICAL ERRORS
        ==================
        
        Problem: Application crashes
        Solutions:
        1. Check error logs in console
        2. Reduce image size and complexity
        3. Use CPU mode instead of GPU
        4. Update all dependencies
        5. Restart system if memory issues persist
        
        Problem: "Module not found" errors
        Solutions:
        1. Reinstall requirements: pip install -r requirements.txt
        2. Check Python version compatibility
        3. Use virtual environment
        4. Verify package versions
        
        📞 GETTING HELP
        ===============
        
        If problems persist:
        
        1. 📝 Note exact error messages
        2. 🖼️ Record system specifications
        3. 📋 List steps to reproduce issue
        4. 💾 Save example files that cause problems
        5. 🔄 Try with minimal test case
        
        Remember: Many issues are resolved by:
        • Restarting the application
        • Using smaller, higher-quality images
        • Updating dependencies
        • Checking internet connection for model downloads
        """
        
        text_edit.setText(content)
        layout.addWidget(text_edit)
        
        return widget


def show_model_info(model_info: dict, parent=None):
    """Show model information dialog."""
    
    dialog = QMessageBox(parent)
    dialog.setWindowTitle("Model Information")
    dialog.setIcon(QMessageBox.Information)
    
    info_text = f"""
    Model: Model Information
    
    Navigator: Model: {model_info.get('model_name', 'Unknown')}
    Monitor: Status: {'Success: Loaded' if model_info.get('is_loaded') else 'Error: Not Loaded'}
    SAM: Confidence: {model_info.get('confidence_threshold', 0.5):.2f}
    📈 Predictions: {model_info.get('predictions_made', 0)}
    ⏱️ Avg Time: {model_info.get('avg_time', 0):.2f}s
    
    ✨ Smart Features:
    • Smart Refinement: {'On' if model_info.get('smart_refinement') else 'Off'}
    • Performance Tracking: Active
    • Memory Management: Optimized
    """
    
    dialog.setText(info_text)
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.exec_()


def show_error_dialog(error_message: str, details: str = None, parent=None):
    """Show error dialog with optional details."""
    
    dialog = QMessageBox(parent)
    dialog.setWindowTitle("Smart Annotator Error")
    dialog.setIcon(QMessageBox.Critical)
    dialog.setText(f"Error: Error: {error_message}")
    
    if details:
        dialog.setDetailedText(details)
    
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.exec_()


def show_success_dialog(message: str, parent=None):
    """Show success dialog."""
    
    dialog = QMessageBox(parent)
    dialog.setWindowTitle("Success")
    dialog.setIcon(QMessageBox.Information)
    dialog.setText(f"Success: {message}")
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.exec_()
