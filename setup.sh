#!/bin/bash
set -e

# Check for Docker
if ! command -v docker >/dev/null 2>&1; then
    echo "Error: Docker is not installed."
    echo "Please install Docker from: https://docs.docker.com/engine/install/"
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "Error: Docker Compose is not installed."
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "All prerequisites are installed."

# Function to check if images exist for all services
check_images_exist() {
    # Use docker-compose images to check for existing images (works even when containers are stopped)
    local existing_images=$(docker-compose images -q 2>/dev/null | wc -l)
    if [ "$existing_images" -gt 0 ]; then
        return 0  # Images exist
    else
        return 1  # No images exist
    fi
}

# Check for existing setup
running_containers=$(docker-compose ps -q 2>/dev/null || echo "")
all_containers=$(docker-compose ps -a -q 2>/dev/null || echo "")
images_exist=false

if check_images_exist; then
    images_exist=true
fi

# If any containers exist (running or stopped) or images exist, ask user what to do
if [ -n "$all_containers" ] || [ "$images_exist" = true ]; then
    echo "======================================"
    echo "EXISTING DOCKER SETUP DETECTED"
    echo "======================================"
    
    if [ -n "$running_containers" ]; then
        echo "Running containers found:"
        docker-compose ps
        echo ""
    elif [ -n "$all_containers" ]; then
        echo "Stopped containers found:"
        docker-compose ps -a
        echo ""
    fi
    
    if [ "$images_exist" = true ]; then
        echo "Built images found for this application."
        echo ""
    fi
    
    echo "Options:"
    echo "1. START existing containers (recommended if already built)"
    echo "2. REBUILD everything (will overwrite wallet configuration!)"
    echo "3. ABORT setup"
    echo ""
    
    while true; do
        read -p "Choose option [1/2/3]: " choice
        case $choice in
            1)
                echo "Starting existing containers..."
                docker-compose up -d
                echo ""
                echo "Application started! Check the logs with: docker-compose logs -f"
                exit 0
                ;;
            2)
                echo ""
                echo "WARNING: This will REBUILD everything and OVERWRITE your wallet configuration!"
                echo "You will NOT be able to access your existing wallet after this."
                read -p "Type 'REBUILD' to confirm, or anything else to abort: " confirm
                if [ "$confirm" != "REBUILD" ]; then
                    echo "Aborting to preserve existing setup."
                    exit 1
                fi
                break
                ;;
            3)
                echo "Aborting setup."
                exit 0
                ;;
            *)
                echo "Invalid choice. Please enter 1, 2, or 3."
                ;;
        esac
    done
fi

# If we get here, either no existing setup was found, or user chose to rebuild
echo "Pulling base images..."
docker pull node:23.5.0-slim
docker pull python:3.13.1-slim  
docker pull nginx:alpine-slim

echo "Stopping any running containers..."
docker-compose down || true

echo "Building Docker images..."
docker-compose build

echo "Starting containers..."
docker-compose up -d

echo ""
echo "Setup complete! Application is starting up..."
docker-compose logs
echo "Check the logs with: docker-compose logs -f"