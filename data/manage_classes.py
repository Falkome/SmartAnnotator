#!/usr/bin/env python3
"""
MANAGE CLASSES - Complete Class Management Tool

This script lets you ADD, EDIT, and REMOVE classes without using the GUI.
Since the GUI buttons may not work due to Qt/display issues, use this instead!

Usage:
    python manage_classes.py
    
Then follow the interactive menu to:
- View all classes
- Add new classes
- Edit existing classes
- Remove classes
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.label_manager import LabelManager

def show_classes(mgr):
    """Display all classes."""
    print("\n" + "=" * 70)
    print("CURRENT CLASSES")
    print("=" * 70)
    
    if not mgr.classes:
        print("No classes defined yet.")
        return
    
    print(f"\nTotal classes: {len(mgr.classes)}\n")
    
    for class_id in sorted(mgr.classes.keys()):
        class_info = mgr.classes[class_id]
        current_marker = " ← CURRENT" if class_id == mgr.current_class_id else ""
        print(f"  [{class_id}] {class_info['name']:<20} {class_info['color']:<10} {current_marker}")
        if class_info.get('description'):
            print(f"      Description: {class_info['description']}")
        print()

def add_class(mgr):
    """Add a new class interactively."""
    print("\n" + "=" * 70)
    print("ADD NEW CLASS")
    print("=" * 70)
    print()
    
    # Get name
    name = input("Class name: ").strip()
    if not name:
        print("❌ Name cannot be empty!")
        return
    
    # Check if exists
    if mgr.get_class_by_name(name):
        print(f"❌ Class '{name}' already exists!")
        return
    
    # Get color
    print("\nColor (hex format, e.g., #FF0000 for red)")
    print("Common colors: #FF0000=Red, #00FF00=Green, #0000FF=Blue, #FFFF00=Yellow")
    color = input("Color [#FF0000]: ").strip() or "#FF0000"
    
    if not color.startswith('#') or len(color) != 7:
        print("❌ Invalid color format! Use #RRGGBB")
        return
    
    # Get description
    description = input("Description (optional): ").strip()
    
    # Add the class
    try:
        class_id = mgr.add_class(
            name=name,
            color=color,
            description=description
        )
        print(f"\n✅ Successfully added class!")
        print(f"   ID: {class_id}")
        print(f"   Name: {name}")
        print(f"   Color: {color}")
        if description:
            print(f"   Description: {description}")
    except Exception as e:
        print(f"\n❌ Failed to add class: {e}")

def edit_class(mgr):
    """Edit an existing class interactively."""
    print("\n" + "=" * 70)
    print("EDIT CLASS")
    print("=" * 70)
    print()
    
    # Show classes
    for class_id in sorted(mgr.classes.keys()):
        class_info = mgr.classes[class_id]
        print(f"  [{class_id}] {class_info['name']}")
    
    # Get class ID
    try:
        class_id = int(input("\nEnter class ID to edit: ").strip())
    except ValueError:
        print("❌ Invalid ID!")
        return
    
    # Check if exists
    current = mgr.get_class(class_id)
    if not current:
        print(f"❌ Class ID {class_id} not found!")
        return
    
    print(f"\nEditing: {current['name']}")
    print(f"Current color: {current['color']}")
    print(f"Current description: {current.get('description', '(none)')}")
    print()
    
    # Get new values
    print("Enter new values (press Enter to keep current value):")
    
    new_name = input(f"Name [{current['name']}]: ").strip()
    new_name = new_name if new_name else None
    
    new_color = input(f"Color [{current['color']}]: ").strip()
    if new_color and (not new_color.startswith('#') or len(new_color) != 7):
        print("❌ Invalid color format! Keeping current color.")
        new_color = None
    
    new_desc = input(f"Description [{current.get('description', '')}]: ").strip()
    new_desc = new_desc if new_desc else None
    
    # Update
    try:
        success = mgr.update_class(
            class_id=class_id,
            name=new_name,
            color=new_color,
            description=new_desc
        )
        
        if success:
            updated = mgr.get_class(class_id)
            print(f"\n✅ Successfully updated class!")
            print(f"   Name: {updated['name']}")
            print(f"   Color: {updated['color']}")
            print(f"   Description: {updated.get('description', '(none)')}")
        else:
            print(f"\n❌ Failed to update class!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def remove_class(mgr):
    """Remove a class interactively."""
    print("\n" + "=" * 70)
    print("REMOVE CLASS")
    print("=" * 70)
    print()
    
    # Show classes
    for class_id in sorted(mgr.classes.keys()):
        class_info = mgr.classes[class_id]
        print(f"  [{class_id}] {class_info['name']} (annotations: {class_info['annotation_count']})")
    
    # Get class ID
    try:
        class_id = int(input("\nEnter class ID to remove: ").strip())
    except ValueError:
        print("❌ Invalid ID!")
        return
    
    # Check if exists
    current = mgr.get_class(class_id)
    if not current:
        print(f"❌ Class ID {class_id} not found!")
        return
    
    # Confirm
    print(f"\n⚠️  About to remove: {current['name']}")
    print(f"   This class has {current['annotation_count']} annotations.")
    confirm = input("Are you sure? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Cancelled")
        return
    
    # Remove
    try:
        success = mgr.remove_class(class_id)
        if success:
            print(f"\n✅ Successfully removed class: {current['name']}")
        else:
            print(f"\n❌ Failed to remove class!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def quick_add(mgr):
    """Quickly add multiple classes from a list."""
    print("\n" + "=" * 70)
    print("QUICK ADD MULTIPLE CLASSES")
    print("=" * 70)
    print()
    print("Enter classes in format: name,color,description")
    print("One per line. Empty line to finish.")
    print("Example: car,#0000FF,Cars and vehicles")
    print()
    
    added = 0
    while True:
        line = input("> ").strip()
        if not line:
            break
        
        parts = line.split(',')
        if len(parts) < 2:
            print("❌ Need at least name and color!")
            continue
        
        name = parts[0].strip()
        color = parts[1].strip()
        description = parts[2].strip() if len(parts) > 2 else ""
        
        if not color.startswith('#'):
            color = '#' + color
        
        try:
            if not mgr.get_class_by_name(name):
                class_id = mgr.add_class(name=name, color=color, description=description)
                print(f"  ✅ Added: {name} (ID: {class_id})")
                added += 1
            else:
                print(f"  ⏭️  Skipped: {name} (already exists)")
        except Exception as e:
            print(f"  ❌ Failed: {name} - {e}")
    
    print(f"\n✅ Added {added} classes")

def main():
    """Main interactive menu."""
    
    print("\n" + "=" * 70)
    print("🏷️  SMART ANNOTATOR - CLASS MANAGEMENT TOOL")
    print("=" * 70)
    print()
    print("This tool manages annotation classes without using the GUI.")
    print("All changes are saved immediately to data/label_classes.json")
    print()
    
    # Load label manager
    mgr = LabelManager()
    
    while True:
        print("\n" + "=" * 70)
        print("MENU")
        print("=" * 70)
        print()
        print("  1. View all classes")
        print("  2. Add new class")
        print("  3. Edit class")
        print("  4. Remove class")
        print("  5. Quick add multiple classes")
        print("  6. Exit")
        print()
        
        choice = input("Choose option (1-6): ").strip()
        
        if choice == '1':
            show_classes(mgr)
        elif choice == '2':
            add_class(mgr)
        elif choice == '3':
            edit_class(mgr)
        elif choice == '4':
            remove_class(mgr)
        elif choice == '5':
            quick_add(mgr)
        elif choice == '6':
            print("\n✅ Done! Changes saved to data/label_classes.json")
            print("   Run 'python main.py' to use your classes in the GUI")
            print()
            break
        else:
            print("❌ Invalid choice!")
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        print("✅ All changes were saved")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

