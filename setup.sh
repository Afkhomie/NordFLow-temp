#!/bin/bash

echo "Setting up NodeFlow..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.11"

if (( $(echo "$python_version < $required_version" | bc -l) )); then
    echo "Error: Python $required_version or higher required"
    exit 1
fi

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements based on OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Installing Linux dependencies..."
    pip install -r requirements-linux.txt
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Installing macOS dependencies..."
    pip install -r requirements-base.txt
    pip install playsound3
fi

echo "Setup complete! Run 'source venv/bin/activate' to activate the environment."
