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

docker pull node:23.5.0-slim
docker pull python:3.13.1-slim

echo "All prerequisites are installed."

# Check for existing containers from docker-compose
existing_containers=$(docker-compose ps -q)
if [ -n "$existing_containers" ]; then
    echo "WARNING: Existing container(s) detected!"
    echo "Proceeding will OVERWRITE your wallet configuration and you will NOT be able to access your wallet again."
    read -p "ARE YOU ABSOLUTELY SURE YOU WANT TO PROCEED? Type 'OVERWRITE' to continue, or any other key to abort: " confirm
    if [ "$confirm" != "OVERWRITE" ]; then
        echo "Aborting setup to preserve your current wallet configuration."
        exit 1
    fi
fi

echo "Stopping any running containers..."
docker-compose down || true

echo "Building Docker images..."
docker-compose build

