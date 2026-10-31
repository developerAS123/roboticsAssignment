#!/usr/bin/env bash
set -e

# Source ROS 2 environment
source /opt/ros/jazzy/setup.bash

# Launch TurtleBot3 simulation in headless mode
ros2 launch /workspace/launch/tb3_sim.launch.py headless:=true use_sim_time:=true &
SIM_PID=$!

# Give simulation a moment to start
sleep 5

# Launch SLAM Toolbox async node (online async)
ros2 run slam_toolbox async_slam_toolbox_node --ros-args -p use_sim_time:=true &
SLAM_PID=$!

# Let SLAM run to build the map (30 seconds)
sleep 30

# Save the map to workspace/maps/office_map
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap "{name: {data: '/workspace/maps/office_map'}}"

# Shut down SLAM and simulation processes
kill $SLAM_PID $SIM_PID

echo "SLAM map generation completed. Map saved to /workspace/maps/office_map.*"

