# my_gazebo_learn

Panda 机械臂 Gazebo 仿真环境 —— 为后续 MoveIt + Rviz + 具身智能学习打基础。

## 环境要求

- Ubuntu 22.04
- ROS2 Humble
- Gazebo (Ignition Fortress 或 Gazebo Classic)
- moveit_resources_panda_description
- moveit_resources_panda_moveit_config
- ros2_control + ros2_controllers
- gazebo_ros2_control

## 安装依赖

`ash
# 安装 Gazebo 与 ros2_control
sudo apt install ros-humble-gazebo-ros ros-humble-gazebo-ros2-control
sudo apt install ros-humble-ros2-control ros-humble-ros2-controllers
sudo apt install ros-humble-joint-state-broadcaster ros-humble-joint-trajectory-controller
sudo apt install ros-humble-xacro ros-humble-robot-state-publisher

# 安装 moveit_resources（如果尚未安装）
sudo apt install ros-humble-moveit-resources-panda-description
sudo apt install ros-humble-moveit-resources-panda-moveit-config
`

## 构建

`ash
cd ~/ros2_ws  # 你的 ROS2 工作空间
colcon build --packages-select my_gazebo_learn --symlink-install
source install/setup.bash
`

## 启动仿真

`ash
ros2 launch my_gazebo_learn panda_gazebo.launch.py
`

启动后会看到：
- Gazebo 窗口，包含简单桌面和 Panda 机械臂模型
- 控制器自动加载：joint_state_broadcaster、panda_arm_controller、panda_hand_controller

## 验证

`ash
# 查看控制器状态
ros2 control list_controllers

# 查看话题
ros2 topic list | grep panda

# 发送关节位置指令（示例：所有关节归零）
ros2 topic pub /panda_arm_controller/joint_trajectory geometry_msgs/msg/JointTrajectory "{...}" -1
`

## 文件结构

`
my_gazebo_learn/
├── config/
│   └── panda_controllers.yaml    # 控制器参数配置
├── launch/
│   └── panda_gazebo.launch.py    # 主启动文件
├── urdf/
│   └── panda_gazebo.urdf.xacro   # Panda Gazebo 描述（含传动与 ros2_control）
├── worlds/
│   └── panda_world.world         # Gazebo 仿真世界
├── my_gazebo_learn/
│   └── __init__.py
├── package.xml
├── setup.py
├── setup.cfg
└── README.md
`

## 后续扩展方向

- 集成 MoveIt2 运动规划（利用 moveit_resources_panda_moveit_config）
- 添加 Rviz2 可视化
- 构建复杂仿真场景（物体抓取、桌面操作等）
- 实现具身智能任务（强化学习、模仿学习等）
- 添加相机/RGB-D 传感器
