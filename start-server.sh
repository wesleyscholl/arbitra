#!/bin/bash

# Start Arbitra Backend Server

echo "🚀 Starting Arbitra Backend..."

# Activate virtual environment
source venv/bin/activate

# Export SSL certificate bundle variable (bypass corporate SSL for development)
# WARNING: This disables SSL verification - use with caution!
export REQUESTS_CA_BUNDLE=""
export CURL_CA_BUNDLE=""
export SSL_CERT_FILE=""
export PYTHONHTTPSVERIFY=0

echo "⚠️  SSL verification disabled for development"

# Start the server
echo "📡 Starting FastAPI server on http://localhost:8000"
python -m backend.main

