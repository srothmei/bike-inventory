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

# Check if we're running behind a proxy by seeing if STREAMLIT_SERVER_HEADLESS is set to true
# We assume this means we're running in the secure setup with nginx
if [[ "$STREAMLIT_SERVER_HEADLESS" == "true" ]]; then
    echo "Running in proxy mode behind Nginx..."
    
    # Start the application with proxy-aware settings
    echo "Starting Streamlit application with proxy-optimized settings..."
    exec streamlit run app.py \
        --server.port=8501 \
        --server.address=0.0.0.0 \
        --server.headless=true \
        --server.enableCORS=true \
        --server.enableXsrfProtection=false \
        --server.enableWebsocketCompression=true \
        --server.maxUploadSize=200 \
        --server.baseUrlPath="/" \
        --browser.serverAddress="localhost" \
        --browser.gatherUsageStats=false \
        --global.developmentMode=false \
        --logger.level=info
else
    # Start the application normally
    echo "Starting Streamlit application in standard mode..."
    exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0
fi
