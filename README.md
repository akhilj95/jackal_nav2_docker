# Jackal Nav2 Docker Workspace 🐢

A fully containerized **ROS 2 Humble** development environment tailored for the Clearpath Jackal UGV. This workspace simplifies the process of building and running Navigation2 from source while maintaining a clean host environment.

---

## 🛠 Features
* **Containerized Environment**: Ubuntu 22.04 + ROS 2 Humble Desktop.
* **Nav2 from Source**: Integrated as a git submodule for easy customization.
* **Persistent Build Cache**: Uses Docker volumes to keep `build`, `install`, and `log` folders outside your source tree.
* **Performance Optimized**: Uses `CycloneDDS` for robust communication.
* **Headless Visualization**: Integrated `Foxglove Bridge` for remote telemetry.

---
## ⚠️ Important Warning
* Docker Desktop vs. Native Docker Engine: Do not use Docker Desktop (on Linux or Windows) if you intend to connect to physical hardware. Native Docker Engine is required for `network_mode: host` to function correctly. Docker Desktop runs in a VM, which isolates the container from the robot's network and complicates X11 GUI forwarding.
* To use the [Ros1_bridge](https://github.com/ros2/ros1_bridge) for communicating with a jackal configured with ROS 1, you need Ubuntu 20.04 or 22.04. Certain combinations require building both the bridge and ROS from source.

---

## 📋 Prerequisites
Ensure you have the following installed on your host machine:
* [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) & [Docker Compose](https://docs.docker.com/compose/install/)
* [Git](https://git-scm.com/)
* [ROS Noetic](https://wiki.ros.org/noetic/Installation) and [ROS Foxy](https://docs.ros.org/en/foxy/Installation.html) (for bridging ros1 messages from jackal to ros2)
* [Foxglove Studio](https://foxglove.dev/download) (if needed visualization)

---

## 🚀 Quick Start

### 1. Clone the Repository
Since Navigation2 is a submodule, you **must** clone recursively:
```bash
git clone --recursive https://github.com/akhilj95/jackal_nav2_docker.git
cd jackal_nav2_docker
```

### 2. Script Permissions
Before running any utility, ensure all scripts are executable:
```bash
chmod +x scripts/*.sh
```

### 3. Automated Initial Setup
This takes around 15 mins or more! Run the setup script to generate your .env file (tailored to your host UID/GID), create dummy mount folders, and perform the initial workspace build:
```bash
./scripts/initial_setup.sh
```

### 4. Enter the Workspace
Use the convenience script to open a new terminal session. This drops you into the workspace as your local user:
```bash
./scripts/terminal.sh
```

---

## 💻 Development Workflow

### Building the Workspace
The initial_setup script would have already built the workspace. After making any changes you can rebuild from inside the container.
* Build artifacts are stored in a Docker volume (nav2_build_cache) so they persist even if the container is removed.
* A custom alias `cb` is provided for standard builds:
```bash
# Build all packages with symlink-install
cb
```
---

## 🔄 Lifecycle Management
### Start and Stop
```bash
# Start container in detached mode
docker compose up -d

# Stop container without removing it
docker compose stop

# Stop container and remove it
docker compose down
```

### Cleanup & Reset
```bash
# Option 1: Remove container and ALL volumes (including build cache)
docker compose down -v

# Option 2: Remove only the specific build cache volume
docker volume rm jackal_nav2_docker_nav2_build_cache
```
---

## 🌉 ROS 1 Bridge Configuration

Because the Jackal hardware typically runs **ROS 1 Noetic**, this workspace uses a `ros1_bridge` to communicate with **ROS 2 Humble**.

### Topic Mapping (`config/bridge_topics.yaml`)

The bridge uses a declarative YAML format to map topics between versions. To add a new topic to the bridge, edit this file following this structure:

```yaml
# Example entry in config/bridge_topics.yaml
- topic_name: "/cmd_vel"
  type: "geometry_msgs/msg/Twist"
  queue_size: 10
```

### Running the Bridge

The bridge requires a workspace where both ROS 1(noetic) and ROS 2(foxy) are sourced. The `./scripts/start_bridge.sh` script sources the ros versions and starts the `parameter_bridge`.

```bash
# Start the bridge from the host
./scripts/start_bridge.sh
```
---

## 🧭 Running Navigation
To launch the Jackal-specific navigation stack:
```bash
ros2 launch jackal_nav2_bringup bringup.launch.py
```

---

## 📁 Project Structure
```text
.
├── docker/                 # Dockerfile and entrypoint scripts
├── config/                 # useful ROS 1 related config
├── scripts/                # Utility shell scripts
├── src/
│   ├── navigation2/        # Submodule: Official Nav2 source code
│   └── jackal_nav2_bringup # Custom: Jackal launch and ROS 2 config files
├── compose.yml             # Docker Compose configuration
├── .env                    # Auto-generated permissions and ROS config  
└── .gitignore              # Ignore rules
```

---

## ⚙️ Configuration (.env)

The `.env` file is your control center. It allows you to customize the environment without touching the core Docker code. You would have clean the build cache and re-reun the install-setup script if you change `USER_NAME`,`USER_UID` or `USER_GID`.

| Variable | Description |
| :--- | :--- |
| **USER_NAME** | The username inside the container. Defaults to host name. |
| **USER_UID / USER_GID** | Matches container permissions to host user to avoid errors. |
| **ROS_DOMAIN_ID** | Separates ROS traffic. Ensure this matches your robot (default: **7**). |
| **CONTAINER_NAME** | Identification for the container (default: **jackal_nav2_container**). |
| **RMW_IMPLEMENTATION** | Middleware choice. Default: `rmw_cyclonedds_cpp` for better stability. |
| **CUSTOM_BAG_DIR** | **Hook:** Absolute path to mount host rosbags into `/home/$USER/bags`. |
| **CUSTOM_MAP_DIR** | **Hook:** Absolute path to mount host maps into `/home/$USER/maps`. |

> **Note:** If you leave the custom directory hooks blank, the setup script will automatically mount empty dummy folders to prevent container startup errors.

---

## 👀 Visualization (Foxglove)
Since the container is headless, use Foxglove Studio on your host machine. Inside the container, start the bridge:
```bash
ros2 run foxglove_bridge foxglove_bridge
```
> **Connect:** Open Foxglove Studio and connect to `ws://<robot or machine ip>:8765`.

---

## ⚠️ Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **Missing Nav2 Source?** | Run `git submodule update --init --recursive`. |
| **DDS Issues?** | Restart the daemon: `ros2 daemon stop && ros2 daemon start`. |
| **DDS "no traffic"** | Check that your `.env` and the robot share the same `ROS_DOMAIN_ID`|
| **Permission Denied?** | Ensure `USER_UID` in `.env` matches your host ID (`id -u`). |
| **Cannot open display** | Run `xhost +local:docker` on your host or ensure `~/.Xauthority` exists. |
