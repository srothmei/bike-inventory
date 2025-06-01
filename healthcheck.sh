#!/bin/bash
# Simple healthcheck script for the Bike Inventory app

# Try Streamlit's dedicated health check endpoint first
if curl -s --fail http://localhost:8501/healthz > /dev/null; then
  exit 0
fi

# If that fails, check if the main page is responding
if curl -s http://localhost:8501 | grep -q "Bike"; then
  exit 0
fi

# If both checks fail, the service is unhealthy
exit 1
