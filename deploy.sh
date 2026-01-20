#!/bin/bash
# Deployment script for Galactic Unicorn Dexcom Monitor

set -e  # Exit on error

echo "===================================="
echo "Deploying to Galactic Unicorn"
echo "===================================="

# Check if mpremote is available
if ! command -v mpremote &> /dev/null; then
    echo "Error: mpremote not found"
    echo "Run: pip install mpremote"
    exit 1
fi

# Compile Python files to .mpy
echo "Compiling Python files..."
cd src

# Compile modules (not main.py - it runs as source)
mpy-cross dexcom.py
mpy-cross display.py
mpy-cross font.py

# Check if secrets.py exists
if [ ! -f "secrets.py" ]; then
    echo "Error: src/secrets.py not found!"
    echo "Please create secrets.py with your credentials"
    exit 1
fi

# Compile secrets for obfuscation
mpy-cross secrets.py

echo "Copying files to device..."
# Copy compiled modules
mpremote cp dexcom.mpy :dexcom.mpy
mpremote cp display.mpy :display.mpy
mpremote cp font.mpy :font.mpy
mpremote cp secrets.mpy :secrets.mpy

# Copy main.py as source (easier to debug)
mpremote cp main.py :main.py

cd ..

echo "===================================="
echo "Deployment complete!"
echo "===================================="
echo ""
echo "To run: mpremote run src/main.py"
echo "Or reset the device to auto-run"
echo ""
echo "See docs/README.md for full documentation"
