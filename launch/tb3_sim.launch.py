#!/usr/bin/env python3
"""
Custom Simulation Bringup Launch File for TurtleBot3 Burger in Gazebo Harmonic
Supports both headless (server-only) and GUI simulation modes for optimal memory safety.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable,
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable
)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    tb3_gazebo_share = get_package_share_directory('turtlebot3_gazebo')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')
    
    # Paths
    default_world = os.path.join('/workspace/worlds/indoor_world.sdf')
    urdf_path = os.path.join(tb3_gazebo_share, 'models', 'turtlebot3_burger', 'model.sdf')
    bridge_params = os.path.join(tb3_gazebo_share, 'params', 'turtlebot3_burger_bridge.yaml')
    
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    headless = LaunchConfiguration('headless', default='true')
    x_pose = LaunchConfiguration('x_pose', default='-2.0')
    y_pose = LaunchConfiguration('y_pose', default='-0.5')
    world = LaunchConfiguration('world', default=default_world)

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use simulation (Gazebo) clock if true')

    declare_headless = DeclareLaunchArgument(
        'headless', default_value='true',
        description='Run Gazebo headless (server only) to conserve RAM/VRAM')

    declare_world = DeclareLaunchArgument(
        'world', default_value=default_world,
        description='Full path to simulation world file')

    declare_x_pose = DeclareLaunchArgument(
        'x_pose', default_value='-2.0',
        description='Initial robot X coordinate')

    declare_y_pose = DeclareLaunchArgument(
        'y_pose', default_value='-0.5',
        description='Initial robot Y coordinate')

    # Environment variables for Gazebo models
    set_model_env = SetEnvironmentVariable('TURTLEBOT3_MODEL', 'burger')
    append_resource_path = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        os.path.join(tb3_gazebo_share, 'models')
    )

    # 1. Gazebo Server (always runs)
    gz_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': ['-r -s -v2 ', world],
            'on_exit_shutdown': 'true'
        }.items()
    )

    # 2. Gazebo GUI Client (runs only when headless=false)
    gz_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-g -v2 ', 'on_exit_shutdown': 'true'}.items(),
        condition=UnlessCondition(headless)
    )

    # 3. Robot State Publisher
    robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(tb3_gazebo_share, 'launch', 'robot_state_publisher.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # 4. Spawn Robot into Gazebo
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'burger',
            '-file', urdf_path,
            '-x', x_pose,
            '-y', y_pose,
            '-z', '0.01'
        ],
        output='screen'
    )

    # 5. Parameter Bridge (publishes /scan, /odom, /tf, /cmd_vel)
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args',
            '-p', f'config_file:={bridge_params}',
        ],
        output='screen'
    )

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_headless)
    ld.add_action(declare_world)
    ld.add_action(declare_x_pose)
    ld.add_action(declare_y_pose)
    ld.add_action(set_model_env)
    ld.add_action(append_resource_path)
    ld.add_action(gz_server)
    ld.add_action(gz_client)
    ld.add_action(robot_state_publisher)
    ld.add_action(spawn_robot)
    ld.add_action(bridge_node)

    return ld
