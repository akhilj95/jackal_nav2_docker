# Jackal Nav2 Docker Workspace 🐢

A fully containerized **ROS 2 Humble** development environment tailored for the Clearpath Jackal UGV. This workspace simplifies the process of building and running Navigation2 from source while maintaining a clean host environment.

---

## 🛠 Features
* **Containerized Environment**: Ubuntu 22.04 + ROS 2 Humble Desktop.
* **Nav2 from Source**: Integrated as a git submodule for easy customization.
* **Performance Optimized**: Uses `CycloneDDS` for robust communication.
* **Headless Visualization**: Integrated `Foxglove Bridge` for remote telemetry.
* **Persistent Build Cache**: Uses Docker volumes to keep `build`, `install`, and `log` folders outside your source tree.

---

## 📋 Prerequisites
Ensure you have the following installed on your host machine:
* [Docker](https://docs.docker.com/get-docker/) & [Docker Compose V2](https://docs.docker.com/compose/install/)
* [Git](https://git-scm.com/)
* [ROS Noetic](https://wiki.ros.org/noetic/Installation) and [ROS Foxy](https://docs.ros.org/en/foxy/Installation.html) (for bridging ros1 messages from jackal to ros2 humble)
* [Foxglove Studio](https://foxglove.dev/download) (for visualization)

---

## 🚀 Quick Start

### 1. Clone the Repository
Since Navigation2 is a submodule, you **must** clone recursively:
```bash
git clone --recursive https://github.com/akhilj95/jackal_nav2_docker.git
cd jackal_nav2_docker
```

### 2. Environment Setup
Create a `.env` file in the root directory to manage permissions and ROS settings:
```bash
# Example .env content
USER_NAME=ros2user
USER_UID=1000
USER_GID=1000
ROS_DOMAIN_ID=7
RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

### 3. Build and Start
```bash
docker compose up -d --build
```

### 4. Enter the Workspace
```bash
docker exec -it jackal_unified_ws /bin/bash
```

---

## 💻 Development Workflow

### Building the Workspace
Inside the container, a custom alias `cb` is provided for standard builds:
```bash
# Build all packages with symlink-install
cb
```

## 🛠 Utility Scripts

Convenience scripts are provided in the `scripts/` directory to simplify container interaction and bridge management.

| Script | Description |
| :--- | :--- |
| `./scripts/terminal.sh` | Opens a new interactive bash session inside the running container. |
| `./scripts/start_bridge.sh` | Launches the `ros1_bridge` using the parameters defined in `config/bridge_topics.yaml`. |

> **Note:** Ensure scripts are executable before first use: `chmod +x scripts/*.sh`

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

## 👀 Visualization (Foxglove)
Since the container is headless, use Foxglove Studio on your host machine. Inside the container, start the bridge:
```bash
ros2 run foxglove_bridge foxglove_bridge
```
> **Connect:** Open Foxglove Studio and connect to `ws://<robot or machine ip>:8765`.

---

## 📁 Project Structure
```text
.
├── docker/                 # Dockerfile and entrypoint scripts
├── config/                 # useful params
├── scripts/                # Utility shell scripts
├── src/
│   ├── navigation2/        # Submodule: Official Nav2 source code
│   └── jackal_nav2_bringup # Custom: Jackal launch and map files
├── compose.yml             # Docker Compose configuration
└── .gitignore              # Ignore rules
```

---

## 🔧 Networking & DDS
This project uses **CycloneDDS** for improved stability over Wi-Fi.

* **Domain ID**: Default is `7`. Ensure your laptop and robot share this ID.
* **Network Mode**: The container uses `network_mode: host` for direct access to the robot's network interfaces.

---

## ⚠️ Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **Missing Nav2 Source?** | Run `git submodule update --init --recursive`. |
| **DDS Issues?** | Restart the daemon: `ros2 daemon stop && ros2 daemon start`. |
| **Permission Denied?** | Ensure `USER_UID` in `.env` matches your host ID (`id -u`). |
