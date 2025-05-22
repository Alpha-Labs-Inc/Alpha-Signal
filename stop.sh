#!/usr/bin/env bash

docker-compose stop || true
echo "Containers stopped successfully."
echo "To start containers again, run: bash start.sh"