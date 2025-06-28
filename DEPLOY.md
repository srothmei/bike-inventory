# 🚀 Deployment Guide

## Prerequisites

1. **SSL Certificates**: Required for HTTPS camera access
2. **Docker & Docker Compose**: For containerized deployment

## Setup Steps

### 1. SSL Certificates

Place your SSL certificates in the `nginx/ssl/` directory:
```
nginx/ssl/
├── cert.pem    (SSL certificate)
└── key.pem     (Private key)
```

For development, you can generate self-signed certificates:
```bash
openssl req -x509 -newkey rsa:4096 -nodes -out nginx/ssl/cert.pem -keyout nginx/ssl/key.pem -days 365
```

### 2. Deploy Application

```bash
# Start the application
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Access Application

- **HTTPS (Recommended)**: https://localhost
- **HTTP (Limited)**: http://localhost

## 📱 Mobile Access

For mobile devices (especially iPhone), use HTTPS to enable camera access:

1. Accept the self-signed certificate warning (for development)
2. Grant camera permissions when prompted
3. Use "Upload Photo" method for best barcode scanning results

## 🔧 Troubleshooting

- **SSL Issues**: Ensure certificates are properly placed in `nginx/ssl/`
- **Camera Access**: Use HTTPS and grant permissions
- **Port Conflicts**: Check if ports 80/443 are available

## 🛑 Stop Application

```bash
docker-compose down
```
