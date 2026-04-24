#!/bin/bash
echo "Initializing Cross-Distro Bridge (Noetic -> Humble via CycloneDDS)..."

# 1. Get the directory where THIS script is located
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

# 1. Source the base ROS distros
source /opt/ros/noetic/setup.bash
source /opt/ros/foxy/setup.bash

# 2. Auto-Detect Jackal Network
JACKAL_IP="169.254.126.137"
MINI_PC_IP="169.254.179.150"

echo "Pinging Jackal Base at $JACKAL_IP..."
# Send 1 ping, wait max 1 second. If successful, setup Jackal network.
if ping -c 1 -W 1 $JACKAL_IP &> /dev/null; then
    echo "[SUCCESS] Jackal base detected! Routing ROS 1 to external master."
    export ROS_MASTER_URI=http://$JACKAL_IP:11311
    export ROS_IP=$MINI_PC_IP
else
    echo "[INFO] Jackal base is OFF or unreachable. Routing ROS 1 to local master."
    export ROS_MASTER_URI=http://localhost:11311
    export ROS_IP=127.0.0.1
fi

# 3. Force CycloneDDS for the ROS 2 side of the bridge
#export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_DOMAIN_ID=7

# 4. Flush the ROS 2 Daemon cache
echo "Flushing ROS 2 Daemon cache..."
ros2 daemon stop

# Load the topics whitelist into the ROS 1 Parameter Server
rosparam load "$SCRIPT_DIR/../config/bridge_topics.yaml"

# 5. Start the dynamic bridge
echo "Bridge Active. Waiting for matched subscribers..."
#ros2 run ros1_bridge dynamic_bridge --bridge-all-topics
ros2 run ros1_bridge parameter_bridge
