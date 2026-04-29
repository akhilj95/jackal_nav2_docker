from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # 1. Declare Configurations
    use_sim_time = LaunchConfiguration('use_sim_time')
    lidar_z = LaunchConfiguration('lidar_z')
    lidar_roll = LaunchConfiguration('lidar_roll')
    lidar_pitch = LaunchConfiguration('lidar_pitch')
    lidar_yaw = LaunchConfiguration('lidar_yaw')

    return LaunchDescription([
        # 2. Declare Arguments (Match Noetic defaults)
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('lidar_z', default_value='0.83'),
        DeclareLaunchArgument('lidar_roll', default_value='0.0'),
        DeclareLaunchArgument('lidar_pitch', default_value='0.0'),
        DeclareLaunchArgument('lidar_yaw', default_value='0.0'),

        # 3. Ouster Lidar TF
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='tf_base_to_os',
            arguments=[
                '--x', '0.0', 
                '--y', '0.0', 
                '--z', lidar_z,
                '--roll', lidar_roll, 
                '--pitch', lidar_pitch, 
                '--yaw', lidar_yaw,
                '--frame-id', 'base_link', 
                '--child-frame-id', 'os_sensor'
            ],
            parameters=[{'use_sim_time': use_sim_time}]
        ),

        # 4. Chassis Link
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='tf_base_to_chassis',
            arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'chassis_link'],
            parameters=[{'use_sim_time': use_sim_time}]
        ),
    ])
