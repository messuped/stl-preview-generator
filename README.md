# STL Preview Generator

A Docker-based tool to generate PNG previews from STL files. The tool processes STL files in the input directory and its subdirectories, creating PNG previews using multiple rendering methods:

1. 3D Matplotlib rendering (primary method)
2. 2D wireframe rendering (fallback)
3. Simple bounding box preview (final fallback)

## Features

- Process multiple STL files recursively
- Multiple rendering fallback methods for maximum compatibility
- Configurable output image size
- Docker-based for easy deployment and portability
- Handles failed renders gracefully

## Prerequisites

- Docker installed on your system
- Basic familiarity with command line operations

## Quick Start

1. Clone this repository:
```bash
git clone <repository-url>
cd stl-preview-extrator
```

2. Build the Docker image:
```bash
docker build -t stl-preview-generator .
```

3. Run the container:
```bash
docker run --rm \
    -v "$(pwd)/stl_files:/app/input" \
    -v "$(pwd)/previews:/app/output" \
    stl-preview-generator \
    /app/input /app/output
```

Replace `$(pwd)/stl_files` with the path to your STL files directory, and `$(pwd)/previews` with where you want the PNG files to be saved.

## Usage

### Basic Usage

```bash
./generate-previews.sh <input_directory> <output_directory> [image_size]
```

Parameters:
- `input_directory`: Directory containing STL files (will be searched recursively)
- `output_directory`: Where to save the PNG previews
- `image_size`: Optional. Image dimensions in pixels (default: "512 512")

Example:
```bash
./generate-previews.sh ./my_stl_files ./my_previews "1024 1024"
```

### Manual Docker Usage

If you prefer to run the Docker container directly:

```bash
docker run --rm \
    -v "/absolute/path/to/stl/files:/app/input" \
    -v "/absolute/path/to/output:/app/output" \
    stl-preview-generator \
    /app/input /app/output --size 512 512
```

## Output

For each STL file found, a corresponding PNG file will be created in the output directory. The tool will attempt three different rendering methods in case of failures:

1. Full 3D render with lighting and surface details
2. Wireframe render showing the mesh structure
3. Simple 2D bounding box with file information

## Development

### Project Structure

```
.
├── Dockerfile              # Docker image definition
├── requirements.txt        # Python dependencies
├── generate_stl_previews.py # Main Python script
├── docker-entrypoint.sh   # Container entrypoint script
└── generate-previews.sh   # Convenience script for running the container
```

### Dependencies

The project uses the following main Python packages:
- trimesh: For STL file processing
- matplotlib: For 3D rendering
- Pillow: For image processing
- numpy: For numerical operations

## Troubleshooting

1. **Image appears blank or black**
   - This might happen with complex STL files
   - The tool will automatically try alternative rendering methods

2. **Permission denied errors**
   - Ensure your user has write permissions to the output directory
   - When using Docker, make sure the mounted volumes are accessible

3. **Memory issues with large STL files**
   - Try processing fewer files at once
   - Consider running with a larger Docker container memory limit

## License

[Your chosen license]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.