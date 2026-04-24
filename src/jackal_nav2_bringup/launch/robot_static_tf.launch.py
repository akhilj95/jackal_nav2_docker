from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Shared parameters for all static publishers
    static_tf_params = {'use_sim_time': use_sim_time}

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),

        # 1. Custom Ouster Lidar
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='tf_base_to_os',
            arguments=['0', '0', '0.75', '0', '0', '0', 'base_link', 'os_sensor'],
            parameters=[static_tf_params]
        ),

        # 2. Chassis Link
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='tf_base_to_chassis',
            arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'chassis_link'],
            parameters=[static_tf_params]
        ),
        
        # ... (Add the rest of your nodes here following the same pattern)
    ])
