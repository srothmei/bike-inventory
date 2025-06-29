#!/bin/bash
# Health check script for Streamlit application

# Check if Streamlit is responding locally
curl -f http://localhost:8501/healthz 2>/dev/null || curl -f http://localhost:8501 2>/dev/null || exit 1
