#!/bin/bash

# Check if the container is running
if [ ! "$(docker ps -q -f name=jackal_unified_ws)" ]; then
    echo "Container is not running! Starting it up..."
    docker compose -f ~/jackal_nav2_docker/compose.yml up -d
fi

# Drop into the container
echo "Entering ROS 2 Humble Workspace..."
docker exec -it jackal_unified_ws bash
