#!/bin/bash

# Start Xvfb in the background
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
sleep 1

# Run the Python script with provided arguments
python /app/generate_stl_previews.py "$@"