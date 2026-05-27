#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launch file for Panda robot arm in Gazebo simulation.

Starts Gazebo with a simple world, spawns the Panda robot using
moveit_resources_panda_description, and loads ros2_control controllers.

Usage:
    ros2 launch my_gazebo_learn panda_gazebo.launch.py

Dependencies:
    - moveit_resources_panda_description
    - gazebo_ros
    - gazebo_ros2_control
    - ros2_control
    - ros2_controllers
"""

import os
from pathlib import Path
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    RegisterEventHandler,
    TimerAction,
)
from launch.conditions import IfCondition, UnlessCondition, LaunchConfigurationEquals
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # ================================================================
    # Paths
    # ================================================================
    pkg_my_gazebo_learn = get_package_share_directory('my_gazebo_learn')
    pkg_moveit_panda_desc = get_package_share_directory(
        'moveit_resources_panda_description'
    )
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    world_file = os.path.join(pkg_my_gazebo_learn, 'worlds', 'panda_world.world')
    xacro_file = os.path.join(pkg_my_gazebo_learn, 'urdf', 'panda_gazebo.urdf.xacro')
    controllers_file = os.path.join(
        pkg_my_gazebo_learn, 'config', 'panda_controllers.yaml'
    )

    # ================================================================
    # Launch arguments
    # ================================================================
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world = LaunchConfiguration('world', default=world_file)

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use simulation (Gazebo) clock'
    )
    declare_world = DeclareLaunchArgument(
        'world', default_value=world_file,
        description='Path to the Gazebo world file'
    )

    # ================================================================
    # Robot Description (xacro -> URDF)
    # ================================================================
    robot_description_content = Command([
        FindExecutable(name='xacro'), ' ',
        xacro_file,
        ' hand:=true',
    ])

    robot_description = {'robot_description': robot_description_content}

    # ================================================================
    # Gazebo Launch
    # ================================================================
    # gazebo = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([
    #         PathJoinSubstitution([pkg_gazebo_ros, 'launch', 'gazebo.launch.py'])
    #     ]),
    #     launch_arguments={
    #         'world': world,
    #         'verbose': 'false',
    #     }.items(),
    # )

    gazebo = ExecuteProcess(
        cmd=[
            'gazebo',
            '--verbose',

            '-s', 'libgazebo_ros_init.so',
            '-s', 'libgazebo_ros_factory.so',

            world
        ],
        output='screen'
    )
    # ================================================================
    # Spawn Panda robot in Gazebo
    # ================================================================
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'panda',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.05',
            '-R', '0.0',
            '-P', '0.0',
            '-Y', '0.0',
        ],
        output='screen',
    )

    # ================================================================
    # Robot State Publisher
    # ================================================================
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[
            robot_description,
            {'use_sim_time': use_sim_time},
        ],
    )

    # ================================================================
    # Controller Manager (ros2_control)
    # ================================================================
    # Wait for the controller_manager service to become available,
    # then load and start the controllers.
    load_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager', '/controller_manager',
        ],
        output='screen',
    )

    load_panda_arm_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'panda_arm_controller',
            '--controller-manager', '/controller_manager',
        ],
        output='screen',
    )

    load_panda_hand_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'panda_hand_controller',
            '--controller-manager', '/controller_manager',
        ],
        output='screen',
    )

    # Sequence: arm controller loads after joint_state_broadcaster
    delay_arm_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=load_joint_state_broadcaster,
            on_exit=[load_panda_arm_controller],
        )
    )

    # Sequence: hand controller loads after arm controller
    delay_hand_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=load_panda_arm_controller,
            on_exit=[load_panda_hand_controller],
        )
    )

    # ================================================================
    # Launch Description
    # ================================================================
    ld = LaunchDescription()

    # Arguments
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_world)

    # Robot description
    ld.add_action(robot_state_publisher)

    # Gazebo + spawn
    ld.add_action(gazebo)
    ld.add_action(spawn_entity)

    # Controllers (with sequencing)
    ld.add_action(load_joint_state_broadcaster)
    ld.add_action(delay_arm_controller)
    ld.add_action(delay_hand_controller)

    return ld
