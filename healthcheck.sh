#!/bin/bash
# Simple healthcheck script for the Bike Inventory app

# Check if the Streamlit server is responding
if curl -s http://localhost:8501 | grep -q "Bike"; then
  exit 0
else
  exit 1
fi
