# Bike Inventory App Deployment Guide

This guide explains how to deploy the Bike Inventory application using Docker on a local network.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Deployment Steps

1. **Clone or Copy the Repository**
   
   Clone this repository or copy all files to your deployment server.

2. **Build and Start the Docker Container**

   Navigate to the directory containing the `docker-compose.yml` file and run:

   ```bash
   docker-compose up -d
   ```

   This will:
   - Build the Docker image
   - Start the container in detached mode
   - Create the necessary volumes for data persistence

3. **Access the Application**

   The application will be available at:

   ```
   http://SERVER_IP:8501
   ```

   Replace `SERVER_IP` with the IP address of your server/computer.

## Data Persistence

The application uses Docker volumes to ensure data persistence:

- `bike_inventory_images`: Stores all the images of your inventory items
- `bike_inventory_db`: Stores the SQLite database file

These volumes will persist even if the container is removed or updated.

## Managing the Container

- **View logs**:
  ```bash
  docker-compose logs -f
  ```

- **Stop the container**:
  ```bash
  docker-compose down
  ```

- **Restart the container**:
  ```bash
  docker-compose restart
  ```

- **Update after code changes**:
  ```bash
  docker-compose up -d --build
  ```

## Backup and Restore

### Backup

To backup your data:

```bash
# Create a backup directory
mkdir -p backups

# Backup the database
docker run --rm --volumes-from bike-inventory -v $(pwd)/backups:/backup alpine sh -c "cp /app/bike_inventory.db /backup/"

# Backup images
docker run --rm --volumes-from bike-inventory -v $(pwd)/backups:/backup alpine sh -c "tar czf /backup/images.tar.gz -C /app/static/images ."
```

### Restore

To restore from backup:

```bash
# Restore database
docker run --rm --volumes-from bike-inventory -v $(pwd)/backups:/backup alpine sh -c "cp /backup/bike_inventory.db /app/"

# Restore images
docker run --rm --volumes-from bike-inventory -v $(pwd)/backups:/backup alpine sh -c "mkdir -p /app/static/images && tar xzf /backup/images.tar.gz -C /app/static/images"
```

## Network Configuration

By default, the application is accessible on port 8501. If you need to use a different port, edit the `docker-compose.yml` file and change the port mapping:

```yaml
ports:
  - "YOUR_PORT:8501"
```

## Security Considerations

This deployment is intended for local network use. For public internet deployment, consider:

- Adding authentication (e.g., using Nginx as a reverse proxy with basic auth)
- Using HTTPS encryption
- Implementing network level security measures

## Troubleshooting

- **Camera access issues**: Camera access requires HTTPS for many browsers. For local deployment, you may need to configure special exemptions in your browser, or set up HTTPS.
- **Container fails to start**: Check logs using `docker-compose logs -f`
- **Database errors**: Ensure the volumes are properly mounted and have correct permissions
