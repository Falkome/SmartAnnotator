#!/usr/bin/env python3
"""
Universal Launcher for Smart Annotator

Works on any system - handles paths, folders, and dependencies automatically.
"""

import sys
import os
import platform
import subprocess
from pathlib import Path

class SmartLauncher:
    """Universal launcher that handles all system setup."""
    
    def __init__(self):
        self.system = platform.system()
        self.project_root = Path(__file__).parent.parent
        self.python_exe = sys.executable
        
    def setup_paths(self):
        """Setup all necessary paths."""
        # Add project root to Python path
        sys.path.insert(0, str(self.project_root))
        
        # Add src directory
        src_path = self.project_root / 'src'
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Add ui directory
        ui_path = self.project_root / 'ui'
        if str(ui_path) not in sys.path:
            sys.path.insert(0, str(ui_path))
        
        # Add models directory
        models_path = self.project_root / 'models'
        if str(models_path) not in sys.path:
            sys.path.insert(0, str(models_path))
        
        return True
    
    def create_folders(self):
        """Create all required folders if they don't exist."""
        required_folders = [
            'data',
            'data/test_images',
            'data/auto_save',
            'models',
            'models/sam',
            'models/yolo',
            'src',
            'ui',
            'ui/components',
            'ui/dialogs',
            'weights',
            'weights/sam',
            'weights/yolo',
            'tests',
            'docs'
        ]
        
        print("Checking folders...")
        created = []
        for folder in required_folders:
            folder_path = self.project_root / folder
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                created.append(folder)
        
        if created:
            print(f"  Created {len(created)} folders")
        else:
            print("  All folders exist")
        
        return True
    
    def check_python_version(self):
        """Check if Python version is compatible."""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"Error: Python 3.8+ required")
            print(f"You have: Python {version.major}.{version.minor}.{version.micro}")
            return False
        
        print(f"Python: {version.major}.{version.minor}.{version.micro} ✓")
        return True
    
    def check_dependencies(self):
        """Check if all required packages are installed."""
        required = {
            'PyQt5': 'PyQt5==5.15.9',
            'torch': 'torch>=2.0.1',
            'cv2': 'opencv-python>=4.8.1',
            'numpy': 'numpy>=1.24.3',
            'PIL': 'Pillow>=9.5.0'
        }
        
        missing = []
        print("Checking dependencies...")
        
        for module, package in required.items():
            try:
                __import__(module)
                print(f"  {module}: OK")
            except ImportError:
                print(f"  {module}: Missing")
                missing.append(package)
        
        return missing
    
    def install_dependencies(self, packages):
        """Install missing packages."""
        print("\nInstalling dependencies...")
        print("This may take a few minutes...")
        
        try:
            # Try using requirements.txt first
            req_file = self.project_root / 'requirements.txt'
            if req_file.exists():
                cmd = [self.python_exe, '-m', 'pip', 'install', '-r', str(req_file)]
            else:
                # Install specific packages
                cmd = [self.python_exe, '-m', 'pip', 'install'] + packages
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )
            
            if result.returncode == 0:
                print("Dependencies installed successfully!")
                return True
            else:
                print(f"Installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error installing dependencies: {e}")
            return False
    
    def detect_display(self):
        """Detect display system for GUI."""
        if self.system == 'Windows':
            print("Platform: Windows")
            return True
        elif self.system == 'Darwin':
            print("Platform: macOS")
            return True
        else:
            # Linux - check for display
            print("Platform: Linux")
            if os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'):
                print("Display: Available")
                return True
            else:
                print("Display: Not available")
                return False
    
    def launch_application(self):
        """Launch the main application."""
        print("\nLaunching Smart Annotator...")
        
        try:
            # Import main after all setup is complete
            import main
            main.main()
            return True
            
        except KeyboardInterrupt:
            print("\nApplication closed by user")
            return True
            
        except Exception as e:
            print(f"\nApplication error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self, auto_install=True):
        """Run the complete launcher sequence."""
        print("=" * 60)
        print("Smart Annotator - Universal Launcher")
        print("=" * 60)
        print()
        
        # Step 1: Check Python version
        if not self.check_python_version():
            return False
        
        # Step 2: Setup paths
        self.setup_paths()
        print("Paths: Configured ✓")
        
        # Step 3: Create folders
        if not self.create_folders():
            return False
        
        # Step 4: Detect display
        has_display = self.detect_display()
        
        # Step 5: Check dependencies
        missing = self.check_dependencies()
        
        if missing:
            print("\n" + "=" * 60)
            print(f"Missing {len(missing)} dependencies")
            print("=" * 60)
            
            if auto_install:
                print("\nAttempting automatic installation...")
                if not self.install_dependencies(missing):
                    print("\nManual installation required:")
                    print("  pip install -r requirements.txt")
                    return False
            else:
                print("\nInstall with:")
                print("  pip install -r requirements.txt")
                
                try:
                    response = input("\nInstall now? (y/n): ").lower().strip()
                    if response == 'y':
                        if not self.install_dependencies(missing):
                            return False
                    else:
                        return False
                except (EOFError, KeyboardInterrupt):
                    print("\n\nManual installation required:")
                    print("  pip install -r requirements.txt")
                    return False
        
        # Step 6: Launch application
        print("\n" + "=" * 60)
        print("All checks passed - Starting application")
        print("=" * 60)
        print()
        
        if not has_display:
            print("Note: No display detected - GUI may not be available")
        
        return self.launch_application()


def main():
    """Main entry point for launcher."""
    launcher = SmartLauncher()
    
    # Check if running in CI/automated mode
    auto_install = '--auto' in sys.argv or os.environ.get('AUTO_INSTALL') == '1'
    
    try:
        success = launcher.run(auto_install=auto_install)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nLauncher cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\nLauncher error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

