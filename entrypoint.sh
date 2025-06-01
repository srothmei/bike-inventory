#!/bin/bash
# Container initialization script

echo "Initializing Bike Inventory container..."

# Create necessary directories
mkdir -p /app/static/images

# Set permissions
chmod -R 755 /app/static

# Initialize environment
echo "Setting up environment..."

# Create .env file if it doesn't exist
if [ ! -f /app/.env ]; then
    echo "Creating default .env file..."
    cp /app/.env.example /app/.env 2>/dev/null || true
fi

# Start the application
echo "Starting Streamlit application..."
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0
