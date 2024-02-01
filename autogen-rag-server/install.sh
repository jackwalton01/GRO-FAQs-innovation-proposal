#!/bin/bash

# Create a new virtual environment
echo "creating python virtual environment"
python3 -m venv myenv

# Activate the virtual environment
echo "activating environment"
source myenv/bin/activate

# Install the necessary packages
echo "installing dependencies..."
pip install -r requirements.txt
echo "completed dependencies"

# Start the service
echo "starting service"
python src/autogen-rag.py

