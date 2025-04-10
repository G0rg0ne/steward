#!/bin/bash

# Pull the latest code changes
git pull origin main

# Stop and remove all containers, networks, and volumes
docker-compose down --volumes --remove-orphans

# Remove all unused images to ensure we get the latest
docker image prune -f

# Pull the latest image
docker-compose pull flight-agent

# Build the services (in case there are local changes)
docker-compose build --no-cache

# Start the services
docker-compose up -d

# Log the deployment
echo "$(date) - Deployment completed with full rebuild and code update" >> /steward/webhook/deployment.log 