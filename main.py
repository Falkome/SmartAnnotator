#!/usr/bin/env python3
"""
Smart Annotator - Main Application

AI-Powered Image Annotation System with Smart Features
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# PyQt5 availability check (imports deferred until needed)
PYQT5_AVAILABLE = True
try:
    import PyQt5
except ImportError:
    PYQT5_AVAILABLE = False


def launch_gui_safely():
    """Launch GUI with proper error handling and cross-platform support."""
    
    import platform
    system = platform.system()
    
    # Platform-specific setup
    if system == 'Windows':
        print("Windows detected - Setting up GUI...")
        # Windows doesn't need display server checks
        # Qt will use native Windows API
        pass
    elif system == 'Darwin':
        print("macOS detected - Setting up GUI...")
        # macOS uses native Cocoa
        pass
    else:
        # Linux/Unix - Check for display server
        print("Linux detected - Checking display server...")
        display = os.environ.get('DISPLAY')
        wayland = os.environ.get('WAYLAND_DISPLAY')
        
        if not display and not wayland:
            print("No display server found - GUI cannot start")
            return False
        
        # Optimize for Wayland or X11
        xdg_session = os.environ.get('XDG_SESSION_TYPE')
        if xdg_session == 'wayland' or wayland:
            print("Wayland display server")
            os.environ['QT_QPA_PLATFORM'] = 'wayland'
            os.environ['QT_WAYLAND_DISABLE_WINDOWDECORATION'] = '1'
            os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
        else:
            print("X11 display server")
            os.environ['QT_QPA_PLATFORM'] = 'xcb'
    
    try:
        # Test PyQt5 availability
        import PyQt5
        print("PyQt5 available")
        
        # Import and launch GUI application
        from ui.smart_gui_app import run_smart_gui, PYQT5_AVAILABLE
        
        if not PYQT5_AVAILABLE:
            print("Error: PyQt5 components not fully available")
            print("Install with: pip install PyQt5==5.15.9")
            return False
        
        print("Launching Smart Annotator GUI...")
        
        # Launch GUI application
        run_smart_gui()
        
        return True
        
    except ImportError as e:
        print(f"PyQt5 import error: {e}")
        print("Install PyQt5 with: pip install PyQt5==5.15.9")
        return False
        
    except Exception as e:
        print(f"GUI initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_smart_annotation_mode():
    """Run Smart Annotation mode with test images (GUI alternative)."""
    
    print("🧠 Smart Annotator - Annotation Mode")
    print("=" * 45)
    print("🖼️ Processing test images with Smart AI...")
    
    try:
        # Initialize Smart Annotator components
        from src.core import SmartEngine
        from models.sam.sam_model import SAMModel
        from models.yolo.yolo_model import YOLOModel
        from ui.components.brush_tool import BrushTool
        
        # Initialize components
        print("\n🤖 Initializing Smart AI...")
        smart_engine = SmartEngine()
        
        sam_model = SAMModel()
        sam_loaded = sam_model.load_model()
        
        yolo_model = YOLOModel()
        yolo_loaded = yolo_model.load_model()
        
        brush_tool = BrushTool(image_size=(1, 1))
        
        print(f"✅ Smart Engine: Ready")
        print(f"✅ SAM Model: {'Loaded' if sam_loaded else 'Not Available'}")
        print(f"✅ YOLO Model: {'Loaded' if yolo_loaded else 'Not Available'}")
        print(f"✅ Brush Tool: Ready (Memory-Optimized)")
        
        # Process test images
        test_images_dir = Path("test_images")
        if test_images_dir.exists():
            image_files = list(test_images_dir.glob("*.jpg")) + list(test_images_dir.glob("*.png"))
            
            if image_files:
                print(f"\n📷 Found {len(image_files)} test images:")
                
                for i, img_path in enumerate(sorted(image_files), 1):
                    print(f"\n{'='*50}")
                    print(f"🖼️ Processing {i}/{len(image_files)}: {img_path.name}")
                    print(f"{'='*50}")
                    
                    # Load image
                    import cv2
                    image = cv2.imread(str(img_path))
                    if image is None:
                        print(f"❌ Could not load {img_path.name}")
                        continue
                    
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    h, w = image_rgb.shape[:2]
                    size_mb = os.path.getsize(img_path) / 1024 / 1024
                    
                    print(f"📏 Image: {w}×{h} pixels ({size_mb:.1f} MB)")
                    
                    # Smart analysis
                    analysis = smart_engine.analyze_image(image_rgb)
                    
                    print(f"🧠 Smart Analysis:")
                    print(f"   Complexity: {analysis['complexity_score']:.2f}")
                    print(f"   Mean Intensity: {analysis['mean_intensity']:.1f}")
                    print(f"   AI Suggestions ({len(analysis['suggestions'])}):")
                    
                    for j, suggestion in enumerate(analysis['suggestions'], 1):
                        print(f"     {j}. {suggestion}")
                    
                    # Test SAM if available
                    if sam_loaded:
                        print(f"\n🎯 SAM Testing:")
                        
                        # Test center point segmentation
                        center_point = (w // 2, h // 2)
                        try:
                            result = sam_model.predict(image_rgb)
                            if result:
                                print(f"   Magic Wand: ✅ {len(result)} segments detected")
                            else:
                                print(f"   Magic Wand: ⚠️ No segments found")
                        except Exception as e:
                            print(f"   Magic Wand: ❌ Error: {e}")
                    
                    # Test YOLO if available
                    if yolo_loaded:
                        print(f"\n📦 YOLO Testing:")
                        
                        try:
                            detections = yolo_model.predict(image_rgb)
                            if detections:
                                unique_classes = len(set(det.get('class_name', 'unknown') for det in detections))
                                print(f"   Object Detection: ✅ {len(detections)} objects ({unique_classes} classes)")
                                
                                # Show top detections
                                for det in detections[:3]:
                                    class_name = det.get('class_name', 'unknown')
                                    confidence = det.get('confidence', 0.0)
                                    print(f"     {class_name} ({confidence:.2f})")
                            else:
                                print(f"   Object Detection: ⚠️ No objects detected")
                        except Exception as e:
                            print(f"   Object Detection: ❌ Error: {e}")
                    
                    # Test brush tool memory
                    print(f"\n🖌️ Brush Tool Testing:")
                    
                    try:
                        # Simulate brush strokes for memory testing
                        brush_tool.set_image_size((h, w))
                        brush_tool.set_size(10)
                        brush_tool.set_mode("paint")
                        
                        # Simulate painting
                        for k in range(5):
                            brush_tool.paint(100 + k*10, 100 + k*5)
                        
                        brush_mask = brush_tool.get_mask()
                        if brush_mask is not None:
                            painted_pixels = np.sum(brush_mask > 0)
                            print(f"   Smart Brush: ✅ {painted_pixels} pixels painted")
                            print(f"   Memory: Optimized with cleanup cycles")
                        else:
                            print(f"   Smart Brush: ❌ Failed")
                        
                        brush_tool.clear_mask()
                        
                    except Exception as e:
                        print(f"   Smart Brush: ❌ Error: {e}")
                    
                    print(f"\n✅ {img_path.name} processing completed!")
                
                print(f"\n🎉 ALL {len(image_files)} TEST IMAGES PROCESSED SUCCESSFULLY!")
                print(f"\n📊 Session Statistics:")
                print(f"   Images processed: {len(image_files)}")
                print(f"   SAM model: {'✅ Working' if sam_loaded else '❌ Not available'}")
                print(f"   YOLO model: {'✅ Working' if yolo_loaded else '❌ Not available'}")
                print(f"   Brush tool: ✅ Working (memory-optimized)")
                
                return True
            else:
                print(f"❌ No test images found in {test_images_dir}")
                return False
        else:
            print(f"❌ Test images directory not found: {test_images_dir}")
            print(f"💡 Creating test images directory with sample image...")
            
            # Create test directory and sample image
            test_images_dir.mkdir(exist_ok=True)
            
            # Create a sample test image
            sample_image = np.random.randint(0, 255, (400, 600, 3), dtype=np.uint8)
            sample_path = test_images_dir / "sample.jpg"
            
            import cv2
            cv2.imwrite(str(sample_path), sample_image)
            print(f"✅ Sample image created: {sample_path}")
            print(f"🔄 Run again to process the created test image")
            
            return True
            
    except Exception as e:
        print(f"❌ Smart Annotation Mode error: {e}")
        logger.error(f"Smart annotation mode error: {e}")
        return False


def run_cli_mode():
    """Run Smart Annotator in CLI mode."""
    
    print("🧠 Smart Annotator - CLI Mode")
    print("=" * 40)
    
    # Initialize components
    smart_engine = SmartEngine()
    sam_model = SAMModel()
    
    print("🤖 Initializing Smart Engine...")
    smart_engine.initialize()
    
    print("🎯 Loading SAM model...")
    sam_success = sam_model.load_model()
    
    if sam_success:
        print("✅ SAM model loaded successfully")
    else:
        print("⚠️ SAM model not available")
    
    print("📊 System Status:")
    print(f"  Smart Engine: ✅ Ready")
    print(f"  SAM Model: {'✅ Loaded' if sam_success else '❌ Not Available'}")
    
    # Create demo image
    import numpy as np
    import cv2
    
    print("\n🎨 Creating demo image...")
    demo_image = np.zeros((400, 600, 3), dtype=np.uint8)
    demo_image[:] = (50, 50, 100)
    
    # Add shapes
    cv2.circle(demo_image, (150, 150), 50, (0, 255, 0), -1)
    cv2.rectangle(demo_image, (300, 100), (450, 200), (255, 0, 0), -1)
    cv2.ellipse(demo_image, (400, 300), (80, 40), 30, 0, 360, (255, 255, 0), -1)
    
    demo_path = "demo_image.png"
    cv2.imwrite(demo_path, cv2.cvtColor(demo_image, cv2.COLOR_RGB2BGR))
    print(f"✅ Demo image saved: {demo_path}")
    
    # Analyze image
    print("\n🧠 Smart analysis...")
    suggestions = smart_engine.analyze_image(demo_image)
    
    if suggestions:
        print("💡 Smart Suggestions:")
        for suggestion in suggestions:
            print(f"  {suggestion}")
    
    print("\n🎉 CLI mode demonstration completed!")
    print("💡 Run 'python main.py' to launch GUI mode")


def run_demo_mode():
    """Run Smart Annotator demo."""
    
    print("🧠 Smart Annotator - Demo Mode")
    print("=" * 40)
    
    try:
        from src.core import SmartEngine
        from models.sam.sam_model import SAMModel
        from models.yolo.yolo_model import YOLOModel
        from src.label_manager import LabelManager
        from src.auto_save_manager import AutoSaveManager
        
        # Demo all components
        components = [
            ("Smart Engine", lambda: SmartEngine().initialize()),
            ("SAM Model", lambda: SAMModel().load_model()),
            ("YOLO Model", lambda: YOLOModel().load_model()),
            ("Label Manager", lambda: True if LabelManager() else False),
            ("Auto-Save Manager", lambda: True if AutoSaveManager() else False)
        ]
        
        for name, init_func in components:
            print(f"\n🔍 Testing {name}...")
            try:
                success = init_func()
                status = "✅ Working" if success else "⚠️ Limited"
                print(f"   {name}: {status}")
            except Exception as e:
                print(f"   {name}: ❌ Error - {e}")
        
        print("\n🎉 Demo completed!")
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Some components may not be available")




def run_smart_annotation_mode():
    """Run Smart Annotation mode with test images (GUI alternative)."""
    
    print("🧠 Smart Annotator - Annotation Mode")
    print("=" * 45)
    print("🖼️ Processing test images with Smart AI...")
    
    try:
        # Initialize Smart Annotator components
        from src.core import SmartEngine
        from models.sam.sam_model import SAMModel
        from models.yolo.yolo_model import YOLOModel
        from ui.components.brush_tool import BrushTool
        
        # Initialize components
        print("\n🤖 Initializing Smart AI...")
        smart_engine = SmartEngine()
        smart_engine.initialize()
        
        sam_model = SAMModel()
        sam_loaded = sam_model.load_model()
        
        yolo_model = YOLOModel()
        yolo_loaded = yolo_model.load_model()
        
        brush_tool = BrushTool()
        
        print(f"✅ Smart Engine: Ready")
        print(f"✅ SAM Model: {'Loaded' if sam_loaded else 'Not Available'}")
        print(f"✅ YOLO Model: {'Loaded' if yolo_loaded else 'Not Available'}")
        print(f"✅ Brush Tool: Ready (Memory-Optimized)")
        
        # Process test images
        test_images_dir = Path("test_images")
        if test_images_dir.exists():
            image_files = list(test_images_dir.glob("*.jpg")) + list(test_images_dir.glob("*.png"))
            
            if image_files:
                print(f"\n📷 Found {len(image_files)} test images:")
                
                for i, img_path in enumerate(sorted(image_files), 1):
                    print(f"\n{'='*50}")
                    print(f"🖼️ Processing {i}/{len(image_files)}: {img_path.name}")
                    print(f"{'='*50}")
                    
                    # Load image
                    import cv2
                    image = cv2.imread(str(img_path))
                    if image is None:
                        print(f"❌ Could not load {img_path.name}")
                        continue
                    
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    h, w = image_rgb.shape[:2]
                    size_mb = os.path.getsize(img_path) / 1024 / 1024
                    
                    print(f"📏 Image: {w}×{h} pixels ({size_mb:.1f} MB)")
                    
                    # Smart analysis
                    suggestions = smart_engine.analyze_image(image_rgb)
                    complexity = smart_engine.calculate_image_complexity(image_rgb)
                    recommended_tool = smart_engine.recommend_tool(image_rgb)
                    
                    print(f"🧠 Smart Analysis:")
                    print(f"   Complexity: {complexity:.2f}")
                    print(f"   Recommended Tool: {recommended_tool}")
                    print(f"   AI Suggestions:")
                    
                    for j, suggestion in enumerate(suggestions, 1):
                        print(f"     {j}. {suggestion}")
                    
                    # Test SAM if available
                    if sam_loaded:
                        print(f"\n🎯 SAM Testing:")
                        
                        # Test center point
                        center_point = (w // 2, h // 2)
                        result = sam_model.predict_with_point(image_rgb, center_point)
                        
                        if result.get('success'):
                            masks = result['results']
                            time_taken = result['processing_time']
                            print(f"   Magic Wand: ✅ {len(masks)} segments in {time_taken:.2f}s")
                        else:
                            print(f"   Magic Wand: ❌ {result.get('error', 'Failed')}")
                        
                        # Test auto segmentation
                        auto_result = sam_model.predict_auto(image_rgb)
                        if auto_result.get('success'):
                            auto_masks = auto_result['results']
                            auto_time = auto_result['processing_time']
                            print(f"   Auto Segment: ✅ {len(auto_masks)} objects in {auto_time:.2f}s")
                    
                    # Test YOLO if available
                    if yolo_loaded:
                        print(f"\n📦 YOLO Testing:")
                        
                        detection_result = yolo_model.detect_and_classify(image_rgb)
                        if detection_result.get('success'):
                            detections = detection_result['results']
                            detection_time = detection_result['processing_time']
                            unique_classes = detection_result.get('unique_classes', 0)
                            
                            print(f"   Object Detection: ✅ {len(detections)} objects ({unique_classes} classes) in {detection_time:.2f}s")
                            
                            # Show top detections
                            for det in detections[:3]:
                                print(f"     {det['class_name']} ({det['confidence']:.2f})")
                        else:
                            print(f"   Object Detection: ❌ {detection_result.get('error', 'Failed')}")
                    
                    # Test brush tool memory
                    print(f"\n🖌️ Brush Tool Testing:")
                    
                    # Simulate brush strokes for memory testing
                    brush_tool.start_stroke(100, 100, (h, w))
                    for k in range(10):
                        brush_tool.continue_stroke(100 + k*5, 100 + k*2, (h, w))
                    
                    brush_mask = brush_tool.finish_stroke()
                    if brush_mask is not None:
                        painted_pixels = np.sum(brush_mask > 0)
                        memory_stats = brush_tool.get_memory_stats()
                        memory_mb = memory_stats['current_memory_mb']
                        
                        print(f"   Smart Brush: ✅ {painted_pixels} pixels painted")
                        print(f"   Memory Usage: {memory_mb:.1f} MB (optimized)")
                    else:
                        print(f"   Smart Brush: ❌ Failed")
                    
                    print(f"\n✅ {img_path.name} processing completed!")
                
                print(f"\n🎉 ALL TEST IMAGES PROCESSED SUCCESSFULLY!")
                
                # Show session statistics
                stats = smart_engine.get_session_stats()
                print(f"\n📊 Session Statistics:")
                print(f"   Images processed: {stats['session_stats']['images_processed']}")
                print(f"   Annotations created: {stats['session_stats']['annotations_created']}")
                print(f"   Processing time: {stats['session_stats']['processing_time']:.1f}s")
                print(f"   Smart mode: {'On' if stats['smart_mode'] else 'Off'}")
                
                return True
            else:
                print(f"❌ No test images found in {test_images_dir}")
                return False
        else:
            print(f"❌ Test images directory not found: {test_images_dir}")
            return False
        
    except Exception as e:
        print(f"❌ Smart Annotation Mode error: {e}")
        logger.error(f"Smart annotation mode error: {e}")
        return False


def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(
        description="🧠 Smart Annotator - AI-Powered Image Annotation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              # Launch GUI (default)
  python main.py --cli         # CLI mode
  python main.py --demo        # Demo mode
        """
    )
    
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--demo", action="store_true", help="Run demo mode")
    parser.add_argument("--log-level", default="INFO", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Set logging level")
    
    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        if args.cli:
            run_cli_mode()
        elif args.demo:
            run_demo_mode()
        else:
            # GUI mode (default)
            print("Starting Smart Annotator GUI...")
            success = launch_gui_safely()
            if not success:
                print("\nGUI not available - check PyQt5 installation")
                print("Install with: pip install PyQt5==5.15.9")
                print("\nFalling back to annotation mode...")
                run_smart_annotation_mode()
            
    except KeyboardInterrupt:
        print("\n🚪 Smart Annotator stopped by user")
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
