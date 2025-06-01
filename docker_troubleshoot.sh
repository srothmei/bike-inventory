#!/bin/bash
# Script to troubleshoot and fix Docker networking issues

# Text colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Bike Inventory Docker Troubleshooter${NC}"
echo "----------------------------------------"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${YELLOW}Note: Some commands may require root privileges${NC}"
  echo "You might need to run this script with sudo"
  echo
fi

# Check if Docker is running
echo -e "${BLUE}Checking Docker service...${NC}"
if ! systemctl is-active --quiet docker; then
  echo -e "${RED}Docker service is not running.${NC}"
  echo "Starting Docker service..."
  sudo systemctl start docker
  sleep 2
  if ! systemctl is-active --quiet docker; then
    echo -e "${RED}Failed to start Docker service. Please check Docker installation.${NC}"
    exit 1
  else
    echo -e "${GREEN}Docker service started successfully.${NC}"
  fi
else
  echo -e "${GREEN}Docker service is running.${NC}"
fi

# Check Docker Compose
echo -e "\n${BLUE}Checking Docker Compose...${NC}"
if command -v docker-compose &> /dev/null; then
  DOCKER_COMPOSE="docker-compose"
  echo -e "${GREEN}docker-compose is installed.${NC}"
elif docker compose version &> /dev/null; then
  DOCKER_COMPOSE="docker compose"
  echo -e "${GREEN}docker compose plugin is installed.${NC}"
else
  echo -e "${RED}Docker Compose not found. Please install Docker Compose.${NC}"
  exit 1
fi

# Check if container is running
echo -e "\n${BLUE}Checking container status...${NC}"
if ! docker ps | grep -q bike-inventory; then
  echo -e "${YELLOW}bike-inventory container is not running.${NC}"
  
  # Check if container exists but stopped
  if docker ps -a | grep -q bike-inventory; then
    echo -e "Container exists but is stopped."
    echo -e "${YELLOW}Would you like to start it? (y/n)${NC}"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
      echo "Starting container..."
      docker start bike-inventory
    fi
  else
    echo -e "Container doesn't exist. You need to deploy it first."
    echo -e "${YELLOW}Would you like to deploy using secure setup? (y/n)${NC}"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
      echo "Deploying with docker-compose.secure.yml..."
      $DOCKER_COMPOSE -f docker-compose.secure.yml up -d
    fi
  fi
else
  echo -e "${GREEN}bike-inventory container is running.${NC}"
  
  # Check container logs for errors
  echo -e "\n${BLUE}Checking container logs for errors...${NC}"
  ERRORS=$(docker logs --tail 50 bike-inventory 2>&1 | grep -i "error\|exception\|failure" | wc -l)
  
  if [ "$ERRORS" -gt 0 ]; then
    echo -e "${RED}Found $ERRORS potential errors in container logs.${NC}"
    echo -e "${YELLOW}Would you like to see the logs? (y/n)${NC}"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
      echo -e "\n${BLUE}Last 50 log entries:${NC}"
      docker logs --tail 50 bike-inventory
    fi
  else
    echo -e "${GREEN}No obvious errors found in logs.${NC}"
  fi
fi

# Check if SSL certificates exist for HTTPS setup
echo -e "\n${BLUE}Checking SSL certificates...${NC}"
if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
  echo -e "${YELLOW}SSL certificates missing.${NC}"
  echo -e "Would you like to generate self-signed certificates? (y/n)"
  read -r answer
  if [[ "$answer" =~ ^[Yy]$ ]]; then
    mkdir -p nginx/ssl
    echo "Generating self-signed certificates..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem \
      -subj "/CN=bike-inventory/O=Bike Inventory/C=US"
    echo -e "${GREEN}Certificates generated.${NC}"
  fi
else
  echo -e "${GREEN}SSL certificates found.${NC}"
fi

# Restart services
echo -e "\n${BLUE}Would you like to restart the services? (y/n)${NC}"
read -r answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
  echo "Restarting services..."
  $DOCKER_COMPOSE -f docker-compose.secure.yml down
  sleep 2
  $DOCKER_COMPOSE -f docker-compose.secure.yml up -d
  echo -e "${GREEN}Services restarted.${NC}"
fi

echo -e "\n${GREEN}Troubleshooting complete.${NC}"
echo -e "${BLUE}If the application is still not working, check the detailed logs with:${NC}"
echo "docker logs bike-inventory"
echo -e "${BLUE}or${NC}"
echo "docker-compose -f docker-compose.secure.yml logs"
