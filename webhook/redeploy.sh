#!/bin/bash

# Exit on error
set -e

# Log function
log() {
    echo "$(date) - $1" >> /etc/webhook/deployment.log
}

# Start deployment
log "Starting deployment..."

# Pull the latest code changes
log "Pulling latest code changes..."
cd /home/deployer/steward
git pull origin main || { log "Failed to pull code changes"; exit 1; }

# Stop and remove all containers, networks, and volumes
log "Stopping and removing containers..."
docker-compose down --volumes --remove-orphans || { log "Failed to stop containers"; exit 1; }

# Remove all unused images to ensure we get the latest
log "Pruning unused images..."
docker image prune -f || { log "Failed to prune images"; exit 1; }

# Pull the latest image
log "Pulling latest image..."
docker-compose pull flight-agent || { log "Failed to pull image"; exit 1; }

# Build the services (in case there are local changes)
log "Building services..."
docker-compose build --no-cache || { log "Failed to build services"; exit 1; }

# Start the services
log "Starting services..."
docker-compose up -d || { log "Failed to start services"; exit 1; }

# Log successful deployment
log "Deployment completed successfully" 