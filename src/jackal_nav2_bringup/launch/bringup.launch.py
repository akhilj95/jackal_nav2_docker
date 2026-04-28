import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

def generate_launch_description():
    # Path Setup
    my_pkg = get_package_share_directory('jackal_nav2_bringup')
    nav2_pkg = get_package_share_directory('nav2_bringup')	

    # Map Configurations to variables
    use_sim_time = LaunchConfiguration('use_sim_time')
    lidar_z = LaunchConfiguration('lidar_z')
    lidar_roll = LaunchConfiguration('lidar_roll')
    lidar_pitch = LaunchConfiguration('lidar_pitch')
    lidar_yaw = LaunchConfiguration('lidar_yaw')

    return LaunchDescription([
        # 1. Declare Arguments (Exposes them to the terminal)
        DeclareLaunchArgument(
            'use_sim_time', 
            default_value='false',
            description='Use simulation clock if true'
        ),
        DeclareLaunchArgument(
            'map_name',
            default_value='floor0_map.yaml',
            description='Name of the map file in the maps folder'
        ),
        DeclareLaunchArgument('lidar_z',     default_value='0.75'),
        DeclareLaunchArgument('lidar_roll',  default_value='0.01557'), 
        DeclareLaunchArgument('lidar_pitch', default_value='-0.04089'),
        DeclareLaunchArgument('lidar_yaw',   default_value='0.0'),

        # 2. Include TF Skeleton (Passing all lidar calibrations)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(my_pkg, 'launch', 'robot_static_tf.launch.py')
            ),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'lidar_z':      lidar_z,
                'lidar_roll':   lidar_roll,
                'lidar_pitch':  lidar_pitch,
                'lidar_yaw':    lidar_yaw,
            }.items()
        ),

        # 3. Include Official Nav2 Bringup (Map + AMCL + Servers)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav2_pkg, 'launch', 'bringup_launch.py')
            ),
            launch_arguments={
                'map': PathJoinSubstitution([my_pkg, 'maps', LaunchConfiguration('map_name')]),
                'use_sim_time': use_sim_time,
                'params_file': os.path.join(my_pkg, 'config', 'nav2_params.yaml'),
                'autostart': 'true'
            }.items()
        ),
    ])
