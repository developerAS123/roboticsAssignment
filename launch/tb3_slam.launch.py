#!/usr/bin/env python3
"""Launch TurtleBot3 simulation together with SLAM Toolbox, save a map, and shut down.
The generated map will be stored as /workspace/maps/office_map.{pgm,yaml}.
"""
import os
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    TimerAction,
    ExecuteProcess,
    LogInfo,
    EmitEvent,
    RegisterEventHandler,
    Shutdown,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Start the TurtleBot3 simulation (headless, use_sim_time)
    tb3_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([
            '/workspace/launch', 'tb3_sim.launch.py'
        ])),
        launch_arguments={
            'headless': 'true',
            'use_sim_time': 'true',
        }.items(),
    )

    # 2. Include the official SLAM Toolbox online_async launch
    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([
            '/opt/ros/jazzy/share/slam_toolbox/launch', 'online_async_launch.py'
        ])),
        launch_arguments={'use_sim_time': 'true'}.items(),
    )

    # 3. After 30 seconds, call the save_map service and then shut everything down
    save_map = ExecuteProcess(
        cmd=[
            'ros2', 'service', 'call', '/slam_toolbox/save_map',
            'slam_toolbox/srv/SaveMap',
            "{name: {data: '/workspace/maps/office_map'}}"
        ],
        output='screen',
        shell=False,
    )

    shutdown = Shutdown()

    timer = TimerAction(
        period=30.0,
        actions=[
            LogInfo(msg='Saving map after SLAM run...'),
            save_map,
            LogInfo(msg='Map saved – shutting down simulation and SLAM'),
            shutdown,
        ],
    )

    ld = LaunchDescription()
    ld.add_action(tb3_sim)
    ld.add_action(slam_toolbox)
    ld.add_action(timer)
    return ld

