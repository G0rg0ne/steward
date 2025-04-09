#!/bin/bash

# Change to the directory containing docker-compose.yml
cd /etc/webhook

# Pull the latest image
docker-compose pull flight-agent

# Stop and remove the old containers
docker-compose down

# Start the services
docker-compose up -d

# Log the deployment
echo "$(date) - Deployment completed" >> /etc/webhook/deployment.log 