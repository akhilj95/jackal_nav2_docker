FROM osrf/ros:humble-desktop

ARG USERNAME=ros2user
ARG USER_UID=1000
ARG USER_GID=1000
ARG DEBIAN_FRONTEND=noninteractive

# 1. Install ROS 2 Dev Tools, CycloneDDS, etc.
RUN apt-get update && apt-get install -y \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-foxglove-bridge \
    sudo git wget nano vim \
    python3-pip python3-colcon-common-extensions \
    python3-rosdep python3-vcstool \
    ament-cmake clang clang-format clang-tidy ccls \
    && rm -rf /var/lib/apt/lists/*

# 2. Safely create the user with the ID passed from Compose
# FIRST: Delete the default 'ubuntu' user if it exists to free up UID 1000
RUN if getent passwd ubuntu > /dev/null 2>&1; then userdel -r ubuntu; fi && \
    # THEN: Create the intended group and user
    if ! getent group $USER_GID > /dev/null 2>&1; then groupadd --gid $USER_GID $USERNAME; fi && \
    if ! getent passwd $USER_UID > /dev/null 2>&1; then useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash $USERNAME; fi && \
    # Grant sudo privileges
    echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

# 3. Initialize rosdep as ROOT
RUN rosdep init || true

# 4. Create the entrypoint in a system-wide location (For container boot)
RUN echo "#!/bin/bash" > /usr/local/bin/entrypoint.sh && \
    echo "source /opt/ros/humble/setup.bash" >> /usr/local/bin/entrypoint.sh && \
    echo "if [ -f /home/$USERNAME/ros2_ws/install/setup.bash ]; then source /home/$USERNAME/ros2_ws/install/setup.bash; fi" >> /usr/local/bin/entrypoint.sh && \
    echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> /usr/local/bin/entrypoint.sh && \
    echo 'exec "$@"' >> /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh 

# 5. Switch to the user FIRST
USER $USERNAME
ENV HOME=/home/$USERNAME

# 6. NEW: Inject ROS environment and aliases into .bashrc for docker exec sessions
RUN echo "source /opt/ros/humble/setup.bash" >> $HOME/.bashrc && \
    echo "if [ -f $HOME/ros2_ws/install/setup.bash ]; then source $HOME/ros2_ws/install/setup.bash; fi" >> $HOME/.bashrc && \
    echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> $HOME/.bashrc && \
    echo "alias cb='colcon build --symlink-install'" >> $HOME/.bashrc

# 7. Final workspace setup
RUN rosdep update
WORKDIR $HOME/ros2_ws

# --- START OF NAV2 DEPENDENCY FIX ---
# Temporarily copy src so rosdep can "read" your source code's dependencies
# Note: The context must be the root of your project where 'src' lives
COPY --chown=$USERNAME:$USERNAME src ./src

# Install the dependencies found in your source code's package.xml files
# This installs libraries like libbondcpp, ompl, etc., WITHOUT installing binary Nav2
RUN sudo apt-get update && \
    rosdep install -i --from-path src --rosdistro humble -y && \
    sudo rm -rf /var/lib/apt/lists/*

# Clean up the copied src inside the image. 
# Your docker-compose volume will mount your real 'src' here at runtime.
RUN rm -rf ./src
# --- END OF NAV2 DEPENDENCY FIX ---

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["/bin/bash"]
