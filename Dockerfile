FROM python:3.9-slim

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for headless rendering
ENV DISPLAY=:99

# Create working directory
WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies with caching disabled for smaller image
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY generate_stl_previews.py /app/

# Create directories for input and output
RUN mkdir -p /app/input /app/output

# Set up entrypoint script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]