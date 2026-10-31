#!/bin/bash
set -e

# Setup ROS 2 Jazzy environment
if [ -f "/opt/ros/jazzy/setup.bash" ]; then
    source "/opt/ros/jazzy/setup.bash"
fi

# Source workspace install space if it exists
if [ -f "/workspace/colcon_ws/install/setup.bash" ]; then
    source "/workspace/colcon_ws/install/setup.bash"
fi

exec "$@"
