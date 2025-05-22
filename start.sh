#!/bin/bash
set -e

echo "Starting containers in detached mode..."
docker-compose up -d

echo "Containers started successfully."
echo "To follow logs, run: docker-compose logs -f"
