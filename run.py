#!/usr/bin/env python3
"""
Universal run script for Smart Annotator.
Works on Windows, Linux, and macOS.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import and run universal launcher
from launcher import main

if __name__ == "__main__":
    main()

