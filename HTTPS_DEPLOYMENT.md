# HTTPS Deployment Guide for Bike Inventory App

This guide explains how to deploy the Bike Inventory app with HTTPS support for enhanced security and better mobile camera access.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Domain name (optional)
- SSL certificate and key (self-signed or from a certificate authority)

## SSL Certificate Generation

### Option 1: Self-signed Certificate (for testing)

1. Create the SSL directory:

   ```bash
   mkdir -p nginx/ssl
   ```

2. Generate the self-signed certificate:

   ```bash
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem \
     -subj "/CN=bike-inventory/O=Bike Inventory/C=US"
   ```

   Note: Self-signed certificates will show security warnings in browsers.

### Option 2: Let's Encrypt Certificate (for production)

If you have a domain name pointing to your server, you can use Let's Encrypt for free certificates:

1. Install certbot:

   ```bash
   apt-get update
   apt-get install certbot
   ```

2. Generate certificates:

   ```bash
   certbot certonly --standalone -d your-domain.com
   ```

3. Copy certificates to your project:

   ```bash
   mkdir -p nginx/ssl
   cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
   cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
   ```

## Deployment Steps

1. **Create Environment Configuration**

   Copy the example environment file to create your configuration:

   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file to set your preferences.

2. **Start the Secure Stack**

   ```bash
   docker-compose -f docker-compose.secure.yml up -d
   ```

3. **Access the Application**

   The application will be available at:

   ```
   https://SERVER_IP
   ```

   or if you have a domain:

   ```
   https://your-domain.com
   ```

## Troubleshooting

### Certificate Issues

If you see certificate warnings:
- For self-signed certificates, this is normal. Click "Advanced" and "Proceed" in your browser.
- For Let's Encrypt, make sure your domain is correctly pointing to your server IP.

### NGINX Errors

Check the NGINX container logs:

```bash
docker logs bike-inventory-nginx
```

### Permissions Issues

If NGINX can't read the certificates:

```bash
chmod 644 nginx/ssl/cert.pem
chmod 600 nginx/ssl/key.pem
```

## Certificate Renewal

For Let's Encrypt certificates, set up auto-renewal:

```bash
echo "0 0,12 * * * root certbot renew --quiet --standalone --pre-hook \"docker-compose -f /path/to/docker-compose.secure.yml down\" --post-hook \"cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /path/to/nginx/ssl/cert.pem && cp /etc/letsencrypt/live/your-domain.com/privkey.pem /path/to/nginx/ssl/key.pem && docker-compose -f /path/to/docker-compose.secure.yml up -d\"" | sudo tee -a /etc/crontab > /dev/null
```

This will attempt renewal twice daily and restart the containers if the certificate is renewed.
