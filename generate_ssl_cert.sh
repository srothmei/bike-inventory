#!/bin/bash
# Script to generate self-signed SSL certificates for the Bike Inventory app

# Create SSL directory if it doesn't exist
mkdir -p nginx/ssl

# Generate self-signed certificate
echo "Generating self-signed SSL certificate for local usage..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem \
  -subj "/CN=bike-inventory/O=Bike Inventory/C=US"

# Set appropriate permissions
chmod 644 nginx/ssl/cert.pem
chmod 600 nginx/ssl/key.pem

echo "SSL certificate generated successfully!"
echo "You can now deploy the application using:"
echo "docker-compose -f docker-compose.secure.yml up -d"
echo ""
echo "NOTE: This is a self-signed certificate and will generate browser warnings."
echo "For production use, consider using Let's Encrypt or another CA."
