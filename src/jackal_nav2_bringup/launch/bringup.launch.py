import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    my_pkg = get_package_share_directory('jackal_nav2_bringup')
    nav2_pkg = get_package_share_directory('nav2_bringup')

    return LaunchDescription([
        # 1. Include your TF Skeleton
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(my_pkg, 'launch', 'robot_static_tf.launch.py')),
            launch_arguments={'use_sim_time': 'true'}.items()
        ),

        # 2. Include Official Nav2 Bringup (Map + AMCL + Servers)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(nav2_pkg, 'launch', 'bringup_launch.py')),
            launch_arguments={
                'map': os.path.join(my_pkg, 'maps', 'floor0_map.yaml'),
                'use_sim_time': 'true',
                'params_file': os.path.join(my_pkg, 'config', 'nav2_params.yaml')
            }.items()
        ),
    ])
