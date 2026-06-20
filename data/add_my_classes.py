#!/usr/bin/env python3
"""
ADD YOUR CUSTOM CLASSES HERE

This script lets you add classes WITHOUT using the GUI.
Just edit the list below, run the script, then start the GUI.
Your classes will be available in the dropdown!

Usage:
    1. Edit the 'my_classes' list below
    2. Run: python add_my_classes.py
    3. Run: python main.py
    4. Your classes appear in the Labels dropdown!
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.label_manager import LabelManager

# ============================================================================
# EDIT THIS LIST TO ADD YOUR CUSTOM CLASSES
# ============================================================================

my_classes = [
    # Format: (name, color, description)
    # Color format: "#RRGGBB" (hex code)
    
    ("car", "#0000FF", "Cars and automobiles"),
    ("person", "#00FF00", "People and pedestrians"),
    ("dog", "#FF0000", "Dogs and pets"),
    ("cat", "#FFFF00", "Cats"),
    ("tree", "#008000", "Trees and plants"),
    ("sign", "#FFA500", "Signs and text"),
    
    # Add more classes here:
    # ("my_class", "#ABCDEF", "My description"),
]

# ============================================================================
# DON'T EDIT BELOW THIS LINE
# ============================================================================

def main():
    print("\n" + "=" * 70)
    print("ADD CUSTOM CLASSES TO SMART ANNOTATOR")
    print("=" * 70)
    print()
    
    print(f"📦 Loading label manager...")
    mgr = LabelManager()
    print(f"✅ Current classes: {len(mgr.classes)}")
    print()
    
    print(f"➕ Adding {len(my_classes)} custom classes...")
    print("-" * 70)
    
    added_count = 0
    skipped_count = 0
    
    for name, color, description in my_classes:
        try:
            # Check if class already exists
            existing = mgr.get_class_by_name(name)
            if existing:
                print(f"⏭️  Skipped: '{name}' (already exists with ID {existing['id']})")
                skipped_count += 1
            else:
                class_id = mgr.add_class(
                    name=name,
                    color=color,
                    description=description
                )
                print(f"✅ Added: '{name}' (ID: {class_id}, Color: {color})")
                added_count += 1
        except Exception as e:
            print(f"❌ Failed to add '{name}': {e}")
    
    print()
    print("=" * 70)
    print(f"✅ COMPLETE!")
    print("=" * 70)
    print()
    print(f"📊 Summary:")
    print(f"   Added: {added_count} new classes")
    print(f"   Skipped: {skipped_count} (already exist)")
    print(f"   Total classes now: {len(mgr.classes)}")
    print()
    print(f"📁 Saved to: data/label_classes.json")
    print()
    print(f"🚀 Next step: Run the GUI")
    print(f"   python main.py")
    print()
    print(f"   Your classes will appear in the Labels dropdown!")
    print("=" * 70)
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

