#!/bin/bash
# Bike Inventory Docker Management Script

# Text colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display help
show_help() {
    echo -e "${BLUE}Bike Inventory Docker Management Script${NC}"
    echo
    echo "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  start          - Start the application (standard mode)"
    echo "  start-prod     - Start the application (production mode)"
    echo "  start-secure   - Start the application with HTTPS"
    echo "  stop           - Stop running containers"
    echo "  logs           - Show container logs"
    echo "  status         - Show container status"
    echo "  backup         - Create a backup of database and images"
    echo "  restore FILE   - Restore from a backup file"
    echo "  rebuild        - Rebuild the container"
    echo "  ssl            - Generate self-signed SSL certificate"
    echo "  help           - Show this help message"
    echo
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed.${NC}"
        echo "Please visit https://docs.docker.com/get-docker/ to install Docker."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}Error: Docker Compose is not installed.${NC}"
        echo "Please visit https://docs.docker.com/compose/install/ to install Docker Compose."
        exit 1
    fi
}

# Function to check if docker compose command exists or use docker-compose
get_docker_compose_cmd() {
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    else
        echo "docker compose"
    fi
}

# Function to start the application
start_app() {
    local mode=$1
    local compose_cmd=$(get_docker_compose_cmd)
    
    echo -e "${BLUE}Starting Bike Inventory in ${mode} mode...${NC}"
    
    case $mode in
        standard)
            $compose_cmd up -d
            ;;
        production)
            $compose_cmd -f docker-compose.prod.yml up -d
            ;;
        secure)
            if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
                echo -e "${YELLOW}SSL certificates not found. Generating self-signed certificates...${NC}"
                ./generate_ssl_cert.sh
            fi
            $compose_cmd -f docker-compose.secure.yml up -d
            ;;
        *)
            echo -e "${RED}Invalid mode: ${mode}${NC}"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}Bike Inventory started successfully.${NC}"
    
    # Show IP address and access instructions
    local ip_address=$(hostname -I | awk '{print $1}')
    
    echo -e "${GREEN}---------------------------------------------------${NC}"
    echo -e "${GREEN}Bike Inventory is now running!${NC}"
    echo
    if [ "$mode" == "secure" ]; then
        echo -e "Access the application at: ${BLUE}https://${ip_address}${NC}"
    else
        echo -e "Access the application at: ${BLUE}http://${ip_address}:8501${NC}"
    fi
    echo -e "${GREEN}---------------------------------------------------${NC}"
}

# Function to create backup
create_backup() {
    local backup_dir="backups"
    local date_str=$(date +%Y%m%d_%H%M%S)
    local backup_file="${backup_dir}/bike_inventory_backup_${date_str}.tar.gz"
    
    # Create backup directory if it doesn't exist
    mkdir -p $backup_dir
    
    echo -e "${BLUE}Creating backup...${NC}"
    
    # Check if Docker container is running
    if docker ps | grep -q bike-inventory; then
        # Create a temporary directory
        local temp_dir=$(mktemp -d)
        
        # Copy database and images from container
        echo "- Copying database from container..."
        docker cp bike-inventory:/app/bike_inventory.db $temp_dir/
        
        echo "- Copying images from container..."
        mkdir -p $temp_dir/images
        docker cp bike-inventory:/app/static/images/. $temp_dir/images/
        
        # Create archive
        echo "- Creating archive..."
        tar -czf $backup_file -C $temp_dir .
        
        # Clean up
        rm -rf $temp_dir
        
        echo -e "${GREEN}Backup created: ${backup_file}${NC}"
    else
        # Fallback to local files if container is not running
        echo "- Backing up local files..."
        
        tar -czf $backup_file bike_inventory.db static/images
        
        echo -e "${GREEN}Backup created: ${backup_file}${NC}"
    fi
}

# Function to restore from backup
restore_backup() {
    local backup_file=$1
    
    if [ ! -f "$backup_file" ]; then
        echo -e "${RED}Error: Backup file not found: ${backup_file}${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Warning: This will overwrite your current database and images.${NC}"
    read -p "Are you sure you want to continue? (y/n) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Restore cancelled.${NC}"
        exit 0
    fi
    
    echo -e "${BLUE}Restoring from backup...${NC}"
    
    # Create a temporary directory
    local temp_dir=$(mktemp -d)
    
    # Extract backup to temporary directory
    echo "- Extracting backup..."
    tar -xzf $backup_file -C $temp_dir
    
    # Check if Docker container is running
    if docker ps | grep -q bike-inventory; then
        # Copy files to container
        echo "- Copying database to container..."
        docker cp $temp_dir/bike_inventory.db bike-inventory:/app/
        
        echo "- Copying images to container..."
        docker cp $temp_dir/images/. bike-inventory:/app/static/images/
    else
        # Restore to local files
        echo "- Restoring local files..."
        
        # Backup originals first, just in case
        if [ -f "bike_inventory.db" ]; then
            mv bike_inventory.db bike_inventory.db.bak
        fi
        
        cp $temp_dir/bike_inventory.db .
        mkdir -p static/images
        cp -r $temp_dir/images/. static/images/
    fi
    
    # Clean up
    rm -rf $temp_dir
    
    echo -e "${GREEN}Restore completed successfully.${NC}"
}

# Main script starts here
check_docker

# Process commands
case $1 in
    start)
        start_app "standard"
        ;;
    start-prod)
        start_app "production"
        ;;
    start-secure)
        start_app "secure"
        ;;
    stop)
        echo -e "${BLUE}Stopping Bike Inventory...${NC}"
        $(get_docker_compose_cmd) down
        echo -e "${GREEN}Bike Inventory stopped.${NC}"
        ;;
    logs)
        echo -e "${BLUE}Showing logs (Ctrl+C to exit):${NC}"
        $(get_docker_compose_cmd) logs -f
        ;;
    status)
        echo -e "${BLUE}Container status:${NC}"
        docker ps -a | grep bike-inventory
        ;;
    backup)
        create_backup
        ;;
    restore)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Missing backup file.${NC}"
            echo "Usage: $0 restore BACKUP_FILE"
            exit 1
        fi
        restore_backup "$2"
        ;;
    rebuild)
        echo -e "${BLUE}Rebuilding container...${NC}"
        $(get_docker_compose_cmd) up -d --build
        echo -e "${GREEN}Container rebuilt successfully.${NC}"
        ;;
    ssl)
        ./generate_ssl_cert.sh
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac

exit 0
