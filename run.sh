#!/bin/bash
# Smart Annotator - Linux/Mac Launcher
# Run this script on Linux or macOS

echo ""
echo "===================================================="
echo "Smart Annotator - Starting..."
echo "===================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found"
    echo ""
    echo "Install Python 3.8+ from your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  Fedora:        sudo dnf install python3 python3-pip"
    echo "  macOS:         brew install python3"
    echo ""
    exit 1
fi

# Run universal launcher
python3 run.py

exit $?

