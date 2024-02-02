#!/bin/bash

# Setup frontend
echo "Installing frontend"
cd govuk-frontend-prototype
npm install
cd ..

# Set up backend
echo "Installing backend"
cd autogen-rag-server

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
