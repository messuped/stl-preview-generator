#!/bin/bash

# Default values
IMAGE_NAME="stl-preview-generator"
DEFAULT_INPUT_DIR="./stl_files"
DEFAULT_OUTPUT_DIR="./previews"
DEFAULT_IMAGE_SIZE="512 512"

# Function to show usage
show_usage() {
    echo "Usage: $0 [input_dir] [output_dir] [image_size]"
    echo
    echo "Parameters:"
    echo "  input_dir   : Directory containing STL files (default: $DEFAULT_INPUT_DIR)"
    echo "  output_dir  : Directory for PNG previews (default: $DEFAULT_OUTPUT_DIR)"
    echo "  image_size  : Image dimensions in pixels (default: $DEFAULT_IMAGE_SIZE)"
    echo
    echo "Example: $0 ./my_stls ./my_previews \"1024 1024\""
}

# Show help if requested
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_usage
    exit 0
fi

# Get parameters with defaults
INPUT_DIR="${1:-$DEFAULT_INPUT_DIR}"
OUTPUT_DIR="${2:-$DEFAULT_OUTPUT_DIR}"
IMAGE_SIZE="${3:-$DEFAULT_IMAGE_SIZE}"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Ensure input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Input directory '$INPUT_DIR' does not exist"
    show_usage
    exit 1
fi

# Build the Docker image
echo "Building Docker image..."
if ! docker build -t "$IMAGE_NAME" .; then
    echo "Error: Docker build failed!"
    exit 1
fi

echo "Running STL preview generator..."
echo "Input directory : $INPUT_DIR"
echo "Output directory: $OUTPUT_DIR"
echo "Image size      : $IMAGE_SIZE"

# Run the container
if ! docker run --rm \
    -v "$(realpath "$INPUT_DIR"):/app/input" \
    -v "$(realpath "$OUTPUT_DIR"):/app/output" \
    "$IMAGE_NAME" \
    /app/input /app/output --size $IMAGE_SIZE; then
    
    echo "Error: Container execution failed!"
    exit 1
fi

echo "Done! Check $OUTPUT_DIR for generated previews."