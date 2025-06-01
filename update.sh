#!/bin/bash
# Update script for the Bike Inventory application

set -e

# Text colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Updating Bike Inventory...${NC}"

# Check if we're in a git repository
if [ -d ".git" ]; then
    echo -e "${YELLOW}Git repository detected. Pulling latest changes...${NC}"
    git pull
    
    echo -e "${GREEN}Repository updated.${NC}"
else
    echo -e "${YELLOW}Not a git repository. Skipping code update.${NC}"
fi

# Check if Docker is running
if command -v docker &> /dev/null; then
    if docker ps &> /dev/null; then
        # Check if container is running
        if docker ps | grep -q bike-inventory; then
            echo -e "${YELLOW}Bike Inventory container is running. Updating...${NC}"
            
            # Use the management script if available
            if [ -x "./bike-inventory.sh" ]; then
                ./bike-inventory.sh rebuild
            else
                # Fallback to docker-compose
                if command -v docker-compose &> /dev/null; then
                    docker-compose up -d --build
                else
                    docker compose up -d --build
                fi
            fi
            
            echo -e "${GREEN}Container updated successfully.${NC}"
        else
            echo -e "${YELLOW}Bike Inventory container is not running.${NC}"
            echo "You can start it with: ./bike-inventory.sh start"
        fi
    else
        echo -e "${YELLOW}Docker is not running. Please start Docker first.${NC}"
    fi
else
    echo -e "${YELLOW}Docker is not installed. Skipping container update.${NC}"
    
    # Check if running in development mode
    if command -v pip &> /dev/null; then
        echo -e "${YELLOW}Updating dependencies...${NC}"
        pip install -r requirements.txt --upgrade
        
        echo -e "${GREEN}Dependencies updated.${NC}"
    fi
fi

echo -e "${GREEN}Update complete!${NC}"
