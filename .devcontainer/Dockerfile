FROM node:20-bookworm

# Install system dependencies including barcode detection tools
RUN apt-get update && apt-get install -y \
    zbar-tools \
    imagemagick \
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

# Switch to vscode user
USER vscode

# Set up shell environment
RUN echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc

WORKDIR /workspace
