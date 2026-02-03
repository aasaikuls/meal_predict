#!/bin/bash

echo "========================================"
echo "Setting up Backend Virtual Environment"
echo "========================================"

#cd backend

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
# source venv/bin/activate
source venv/Scripts/activate

# Install dependencies
echo "Installing/Updating dependencies..."
pip install -r requirements.txt

echo ""
echo "========================================"
echo "Starting Backend Server (FastAPI)"
echo "========================================"
python main.py
