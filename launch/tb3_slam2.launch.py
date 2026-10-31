#!/usr/bin/env python3
"""Launch TurtleBot3 headless + SLAM Toolbox (online_async) and save a map.
Uses the correct service type `slam_toolbox/srv/SaveMap`.
"""
import os
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    TimerAction,
    ExecuteProcess,
    LogInfo,
    EmitEvent,
    Shutdown,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution

def generate_launch_description():
    # Simulation (headless, use_sim_time)
    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([
            '/workspace/launch', 'tb3_sim.launch.py'
        ])),
        launch_arguments={
            'headless': 'true',
            'use_sim_time': 'true',
        }.items(),
    )

    # SLAM Toolbox async launch (online_async)
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([
            '/opt/ros/jazzy/share/slam_toolbox/launch', 'online_async_launch.py'
        ])),
        launch_arguments={'use_sim_time': 'true'}.items(),
    )

    # After 25 seconds, call save_map service and shut down
    save_map = ExecuteProcess(
        cmd=[
            'ros2', 'service', 'call', '/slam_toolbox/save_map',
            'slam_toolbox/srv/SaveMap',
            "name: {data: '/workspace/maps/office_map'}"
        ],
        output='screen',
        shell=False,
    )
    shutdown = EmitEvent(event=Shutdown())
    timer = TimerAction(
        period=25.0,
        actions=[LogInfo(msg='Saving map...'), save_map, LogInfo(msg='Map saved – shutting down'), shutdown],
    )

    ld = LaunchDescription()
    ld.add_action(sim)
    ld.add_action(slam)
    ld.add_action(timer)
    return ld

