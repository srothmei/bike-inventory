FROM node:20-bookworm

# Install system dependencies for barcode detection and development
RUN apt-get update && apt-get install -y \
    zbar-tools \
    imagemagick \
    python3 \
    python3-pip \
    python3-venv \
    libzbar0 \
    libzbar-dev \
    curl \
    git \
    vim \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create vscode user with sudo privileges
RUN groupadd --gid 1000 vscode || true \
    && useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home vscode \
    && echo vscode ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/vscode \
    && chmod 0440 /etc/sudoers.d/vscode

# Install global npm packages
RUN npm install -g nodemon concurrently

# Install Python packages for barcode detection
RUN python3 -m pip install --break-system-packages pillow pyzbar opencv-python-headless

# Create barcode testing script
RUN echo '#!/bin/bash' > /usr/local/bin/test-barcodes && \
    echo 'echo "=== Barcode Detection Test ==="' >> /usr/local/bin/test-barcodes && \
    echo 'echo "Available tools:"' >> /usr/local/bin/test-barcodes && \
    echo 'which zbarimg && echo "✓ zbarimg (CLI tool)" || echo "✗ zbarimg not found"' >> /usr/local/bin/test-barcodes && \
    echo 'which convert && echo "✓ ImageMagick convert" || echo "✗ ImageMagick not found"' >> /usr/local/bin/test-barcodes && \
    echo 'python3 -c "import pyzbar; print(\"✓ pyzbar (Python)\")" 2>/dev/null || echo "✗ pyzbar (Python) not available"' >> /usr/local/bin/test-barcodes && \
    echo 'echo ""' >> /usr/local/bin/test-barcodes && \
    echo 'if [ -d "/workspace/example_data" ]; then' >> /usr/local/bin/test-barcodes && \
    echo '    echo "Testing barcode detection on example images:"' >> /usr/local/bin/test-barcodes && \
    echo '    for img in /workspace/example_data/*.jpg /workspace/example_data/*.JPG /workspace/example_data/*.png /workspace/example_data/*.PNG 2>/dev/null; do' >> /usr/local/bin/test-barcodes && \
    echo '        if [ -f "$img" ]; then' >> /usr/local/bin/test-barcodes && \
    echo '            echo "Scanning $(basename "$img"):"' >> /usr/local/bin/test-barcodes && \
    echo '            result=$(zbarimg --quiet --raw "$img" 2>/dev/null)' >> /usr/local/bin/test-barcodes && \
    echo '            if [ -n "$result" ]; then' >> /usr/local/bin/test-barcodes && \
    echo '                echo "  ✓ Found: $result"' >> /usr/local/bin/test-barcodes && \
    echo '            else' >> /usr/local/bin/test-barcodes && \
    echo '                echo "  ✗ No barcode detected"' >> /usr/local/bin/test-barcodes && \
    echo '            fi' >> /usr/local/bin/test-barcodes && \
    echo '        fi' >> /usr/local/bin/test-barcodes && \
    echo '    done' >> /usr/local/bin/test-barcodes && \
    echo 'else' >> /usr/local/bin/test-barcodes && \
    echo '    echo "No example_data directory found. Create some test images first."' >> /usr/local/bin/test-barcodes && \
    echo 'fi' >> /usr/local/bin/test-barcodes && \
    echo 'echo ""' >> /usr/local/bin/test-barcodes && \
    echo 'echo "To test with your own image: zbarimg path/to/image.jpg"' >> /usr/local/bin/test-barcodes && \
    chmod +x /usr/local/bin/test-barcodes

# Switch to vscode user
USER vscode
WORKDIR /workspace

# Set up user environment
USER vscode
RUN echo 'export PATH="/usr/local/bin:$PATH"' >> /home/vscode/.bashrc
