FROM node:20-bookworm

# Install system dependencies including barcode detection tools
RUN apt-get update && apt-get install -y \
    zbar-tools \
    imagemagick \
    python3-pil \
    python3-pip \
    libzbar0 \
    curl \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Create vscode user
RUN groupadd --gid 1000 vscode \
    && useradd --uid 1000 --gid vscode --shell /bin/bash --create-home vscode

# Install global npm packages for development
RUN npm install -g nodemon concurrently

# Set working directory
WORKDIR /workspace

# Install Python barcode detection packages
RUN pip3 install --break-system-packages pillow pyzbar opencv-python

# Create a test script for barcode detection
RUN echo '#!/bin/bash\n\
echo "Testing barcode detection tools..."\n\
echo "Available tools:"\n\
which zbarimg && echo "✓ zbarimg available" || echo "✗ zbarimg not found"\n\
which convert && echo "✓ ImageMagick available" || echo "✗ ImageMagick not found"\n\
echo ""\n\
echo "Testing with example images:"\n\
for img in /workspace/example_data/*.jpg /workspace/example_data/*.JPG; do\n\
  if [ -f "$img" ]; then\n\
    echo "Scanning $img:"\n\
    zbarimg --quiet --raw "$img" 2>/dev/null || echo "  No barcode found"\n\
  fi\n\
done\n\
' > /usr/local/bin/test-barcodes && chmod +x /usr/local/bin/test-barcodes

# Create a helper script to debug image formats
RUN echo '#!/bin/bash\n\
echo "Image analysis for: $1"\n\
if [ -f "$1" ]; then\n\
  echo "File info:"\n\
  file "$1"\n\
  echo ""\n\
  echo "Image details:"\n\
  identify "$1" 2>/dev/null || echo "Could not identify image"\n\
  echo ""\n\
  echo "Barcode scan:"\n\
  zbarimg --verbose "$1" 2>&1 || echo "No barcode detected"\n\
else\n\
  echo "File not found: $1"\n\
fi\n\
' > /usr/local/bin/analyze-image && chmod +x /usr/local/bin/analyze-image

# Install Python barcode detection as backup
# RUN pip3 install --break-system-packages pillow pyzbar opencv-python

# Create Python barcode test script
RUN echo '#!/usr/bin/env python3\n\
import sys\n\
from PIL import Image\n\
from pyzbar import pyzbar\n\
import cv2\n\
import numpy as np\n\
\n\
def detect_barcodes(image_path):\n\
    try:\n\
        # Try with PIL\n\
        image = Image.open(image_path)\n\
        barcodes = pyzbar.decode(image)\n\
        \n\
        if barcodes:\n\
            for barcode in barcodes:\n\
                print(f"Found {barcode.type}: {barcode.data.decode()}")\n\
            return True\n\
        \n\
        # Try with OpenCV preprocessing\n\
        img = cv2.imread(image_path)\n\
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\n\
        \n\
        # Try different preprocessing\n\
        for processed in [gray, cv2.GaussianBlur(gray, (5,5), 0)]:\n\
            barcodes = pyzbar.decode(processed)\n\
            if barcodes:\n\
                for barcode in barcodes:\n\
                    print(f"Found {barcode.type} (preprocessed): {barcode.data.decode()}")\n\
                return True\n\
        \n\
        print("No barcodes detected")\n\
        return False\n\
        \n\
    except Exception as e:\n\
        print(f"Error: {e}")\n\
        return False\n\
\n\
if __name__ == "__main__":\n\
    if len(sys.argv) != 2:\n\
        print("Usage: python3 detect_barcode.py <image_path>")\n\
        sys.exit(1)\n\
    \n\
    detect_barcodes(sys.argv[1])\n\
' > /usr/local/bin/detect-barcode-py && chmod +x /usr/local/bin/detect-barcode-py

# Switch to vscode user
USER vscode

# Set up shell environment
RUN echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
RUN echo 'alias test-barcodes="test-barcodes"' >> ~/.bashrc
RUN echo 'alias analyze="analyze-image"' >> ~/.bashrc

WORKDIR /workspace
