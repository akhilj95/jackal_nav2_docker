#!/bin/bash
set -e 

# --- 1. Smart Pathing Logic ---
# Find where THIS script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Go up one level to the project root (assuming this is in a /scripts folder)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# --- 2. Load Configuration ---
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

# Fallback values if .env is missing
CONTAINER_NAME="${CONTAINER_NAME:-jackal_nav2_container}"
USER_NAME="${USER_NAME:-ros2user}"

COMPOSE_FILE="$PROJECT_ROOT/compose.yml"
WORKSPACE="/home/$USER_NAME/ros2_ws"

# --- 3. Docker Permission Check ---
if docker ps >/dev/null 2>&1; then
    DOCKER_CMD="docker"
else
    DOCKER_CMD="sudo docker"
fi

# --- 4. Robust Container Check ---
# Check for exact name match
if [ ! "$($DOCKER_CMD ps -q -f name=^/${CONTAINER_NAME}$)" ]; then
    echo "Container '${CONTAINER_NAME}' is not running! Starting it up..."
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo "Error: Compose file not found at $COMPOSE_FILE"
        exit 1
    fi
    
    # Run compose from the project root context
    $DOCKER_CMD compose -f "$COMPOSE_FILE" up -d
    sleep 2 
fi

# --- 5. Drop into the container ---
echo "Entering ROS 2 Humble Workspace as $USER_NAME..."
# -u: Ensure you aren't 'root'
# -w: Drop straight into your workspace folder
$DOCKER_CMD exec -it -u "$USER_NAME" -w "$WORKSPACE" "$CONTAINER_NAME" bash
