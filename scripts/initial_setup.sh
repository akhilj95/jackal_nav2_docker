#!/bin/bash
set -e # Exit immediately if any command fails

# --- Pathing Logic ---
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
echo "Running setup from Project Root: $PROJECT_ROOT"
# -------------------------


# --- Docker Permission Check ---
# This checks if the current user can run docker without sudo
if docker ps >/dev/null 2>&1; then
    DOCKER_CMD="docker"
    COMPOSE_CMD="docker compose"
else
    echo "-> Docker requires sudo privileges on this system."
    DOCKER_CMD="sudo docker"
    COMPOSE_CMD="sudo docker compose"
fi
# -------------------------	

echo "========================================"
echo "  Jackal Nav2 - Initial Setup Script  "
echo "========================================"

# 1. Create dummy folders at the project root for safe mounting
echo "-> [1/4] Creating dummy mount folders..."
mkdir -p .empty_bags .empty_maps

# 2. Check and generate .env file
if [ ! -f ".env" ]; then
    echo "-> [2/4] .env file not found. Generating default .env..."
    
    # We dynamically grab the current host user's Name, UID, and GID.
    # This completely eliminates Linux file permission issues!
    cat <<EOF > .env
USER_NAME=$USER
USER_UID=$(id -u)
USER_GID=$(id -g)
ROS_DOMAIN_ID=7
CONTAINER_NAME=jackal_nav2_container
RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Custom Data Mounts (Leave blank if not needed)
CUSTOM_BAG_DIR=
CUSTOM_MAP_DIR=
EOF
    echo "   Created .env with default values tailored to your host user ($USER)."
else
    echo "-> [2/4] .env file already exists. Skipping creation."
fi

# Load the variables from .env so the script can use them
export $(grep -v '^#' .env | xargs)

# 3. Smart Docker Startup
# Check if the container is already running to avoid unnecessary restarts
if [ "$($DOCKER_CMD ps -q -f name=${CONTAINER_NAME:-jackal_nav2_container})" ]; then
    echo "-> [3/4] Container is already running."
else
    echo "-> [3/4] Starting Docker container..."
    $COMPOSE_CMD up -d
fi

# 3.5 Wait for the container to actually be ready to accept commands
echo "Waiting for container to fully initialize..."
# We try to run a harmless 'echo' inside the container. 
# If it fails, we wait 1 second and try again.
until $DOCKER_CMD exec ${CONTAINER_NAME:-jackal_nav2_container} echo "Awake" > /dev/null 2>&1; do
    echo "Still waiting for container..."
    sleep 1
done

echo "Container is online and ready!"

# 4. Conditional Build
echo "-> [4/4] Checking workspace build status..."
BUILD_NEEDED=false
if ! $DOCKER_CMD exec ${CONTAINER_NAME:-jackal_nav2_container} ls /home/${USER_NAME:-ros2user}/ros2_ws/install/setup.bash > /dev/null 2>&1; then
    BUILD_NEEDED=true
fi

if [ "$BUILD_NEEDED" = true ]; then
    echo "   'install/setup.bash' missing. Starting colcon build..."
    $DOCKER_CMD exec -t -u ${USER_NAME:-ros2user} ${CONTAINER_NAME:-jackal_nav2_container} bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install"
else
    echo "   Workspace already built. Use 'cb' inside the container to rebuild if needed."
fi

echo "========================================"
echo "  Setup Complete! "
echo "  Your Docker environment is built, running, and compiled."
echo "  You can now drop into it using your start_robot.sh script!"
echo "========================================"
