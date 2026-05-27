#!/usr/bin/env python3
#
# Copyright 2023 6-robot.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Zhang Wanjie

import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():
    launch_file_dir = os.path.join(get_package_share_directory('wpr_simulation2'), 'launch')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    pkg_my_gazebo_learn = get_package_share_directory('my_gazebo_learn')
    pkg_wpr = get_package_share_directory('wpr_simulation2')


    urdf_path = os.path.join(
        pkg_wpr,
        'models',
        'wpb_home_lidar.model'
    )
    with open(urdf_path, 'r') as infp:
        robot_desc = infp.read()
        doc = xacro.parse(robot_desc)
        xacro.process_doc(doc)
        robot_description = doc.toxml()

    robot_state_publisher_cmd = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description
            }],
        )
    

    pose_x = LaunchConfiguration('pose_x', default='0.0')
    pose_y = LaunchConfiguration('pose_y', default='0.0')
    pose_theta = LaunchConfiguration('pose_theta', default='0.0')

    start_gazebo_ros_spawner_cmd = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', "wpb_home",
            '-x', pose_x,
            '-y', pose_y,
            '-Y', pose_theta
        ],
        output='screen',
    )


    spawn_bookshelft = Node(
            package='gazebo_ros',
            namespace='',
            executable='spawn_entity.py',
            name='spawn_entity',
            arguments=['-file', [os.path.join(pkg_wpr, 'models', 'bookshelft.model')] , 
            '-entity', 'bookshelft_01',
            '-x', '3.0',
            '-y', '0.0',
            '-Y', '3.1415926']
        )
    
    world_file = os.path.join(pkg_my_gazebo_learn, 'worlds', 'panda_world.world')
    world_file2 = os.path.join(pkg_wpr, 'worlds', 'wpb_simple.world')
    
    # world = LaunchConfiguration('world', default=world_file2)
    world = LaunchConfiguration(
        'world',
        default=os.path.join(
            get_package_share_directory('gazebo_ros'),
            'worlds',
            'empty.world'
        )
    )
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


    ld = LaunchDescription()

    # Add the commands to the launch description
    ld.add_action(gazebo)
    # ld.add_action(robot_state_publisher_cmd)
    # ld.add_action(start_gazebo_ros_spawner_cmd)
    ld.add_action(spawn_bookshelft)
    return ld
