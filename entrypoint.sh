#!/bin/bash
# Entrypoint script for bike inventory application

# Create necessary directories
mkdir -p /app/static/images

# Initialize database if it doesn't exist
if [ ! -f /app/bike_inventory.db ]; then
    echo "Initializing database..."
    python -c "
import sys
sys.path.append('/app')
from db import InventoryDB
db = InventoryDB()
db.create_tables()
print('Database initialized successfully')
"
fi

# Start the Streamlit application
echo "Starting Streamlit application..."
exec streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=true \
    --server.enableXsrfProtection=false
