import rospy
from sensor_msgs.msg import PointCloud2
import sensor_msgs.point_cloud2 as pc2

def callback(data):
    # 1. Get the ROS time when this message actually arrived at our script
    arrival_time = rospy.get_time()
    
    # 2. Get the header stamp (when the rotation started)
    header_start = data.header.stamp.to_sec()
    
    # 3. Read the 't' (timestamp) field from the first and last points
    # This proves how long the hardware was actually spinning
    points = list(pc2.read_points(data, field_names=("t"), skip_nans=True))
    first_point_offset = points[0][0] / 1e9  # Convert ns to sec
    last_point_offset = points[-1][0] / 1e9  # Convert ns to sec
    
    print("-" * 30)
    print(f"Hardware Rotation Duration: {last_point_offset - first_point_offset:.4f}s")
    print(f"Time from Start to Publish: {arrival_time - header_start:.4f}s")
    print(f"Pure Computer/Network Lag:  {(arrival_time - header_start) - (last_point_offset - first_point_offset):.4f}s")

rospy.init_node('ouster_audit')
rospy.Subscriber('/ouster/points', PointCloud2, callback)
rospy.spin()
