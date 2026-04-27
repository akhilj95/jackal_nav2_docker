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

        # 1. Custom Ouster Lidar (Updated with IMU calibration)
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='tf_base_to_os',
            arguments=[
                '--x', '0.0', 
                '--y', '0.0', 
                '--z', '0.75',
                '--roll', '0.01557', 
                '--pitch', '-0.04089', 
                '--yaw', '0.0',
                '--frame-id', 'base_link', 
                '--child-frame-id', 'os_sensor'
            ],
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
