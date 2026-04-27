#!/usr/bin/env python3
import rospy
import numpy as np
import tf.transformations as tf_trans
from sensor_msgs.msg import Imu

class IMUAverager:
    def __init__(self, duration=30.0):
        rospy.init_node('imu_averager', anonymous=True)
        
        self.duration = duration
        self.start_time = None
        self.collecting = True
        
        # Buffers to store samples
        self.samples = {"ouster": [], "jackal": []}

        # Subscribers
        # IMPORTANT: Make sure these match your actual topics in 'rostopic list'
        rospy.Subscriber("/ouster/imu/filtered", Imu, self.ouster_callback)
        rospy.Subscriber("/imu/data", Imu, self.jackal_callback)

        rospy.loginfo(f"Waiting for data... Will average for {self.duration}s once started.")

    def calculate_metrics_filtered(self, msg):
        """Calculates metrics from a filtered IMU topic (uses Orientation)."""
        qx = msg.orientation.x
        qy = msg.orientation.y
        qz = msg.orientation.z
        qw = msg.orientation.w
        
        # Convert Quaternion to Euler Angles (Roll, Pitch, Yaw)
        euler = tf_trans.euler_from_quaternion([qx, qy, qz, qw])
        
        roll = np.degrees(euler[0])
        pitch = np.degrees(euler[1])
        
        # Calculate true tilt from vertical using roll and pitch
        total_tilt = np.degrees(np.arccos(np.cos(euler[0]) * np.cos(euler[1])))
        
        return np.array([roll, pitch, total_tilt])

    def calculate_metrics_raw(self, msg):
        """Calculates metrics from raw IMU data (uses Acceleration)."""
        ax = msg.linear_acceleration.x
        ay = msg.linear_acceleration.y
        az = msg.linear_acceleration.z
        
        mag = np.sqrt(ax**2 + ay**2 + az**2)
        if mag == 0: return np.array([0.0, 0.0, 0.0])

        roll = np.degrees(np.arctan2(ay, az))
        pitch = np.degrees(np.arctan2(-ax, np.sqrt(ay**2 + az**2)))
        total_tilt = np.degrees(np.arccos(az / mag))
        
        return np.array([roll, pitch, total_tilt])

    def process_message(self, msg, sensor_name, use_filtered=True):
        if not self.collecting:
            return

        current_time = rospy.get_time()
        
        # Handle the jump from 0.0 (uninitialized) to Bag Time
        if current_time == 0:
            return

        if self.start_time is None:
            self.start_time = current_time
            rospy.loginfo(f"Recording started at sim time: {self.start_time}")

        if current_time - self.start_time <= self.duration:
            if use_filtered:
                metrics = self.calculate_metrics_filtered(msg)
            else:
                metrics = self.calculate_metrics_raw(msg)
            
            self.samples[sensor_name].append(metrics)
        else:
            self.collecting = False
            self.report_averages()

    def ouster_callback(self, msg):
        # We know the Ouster is using the filtered topic now
        self.process_message(msg, "ouster", use_filtered=True)

    def jackal_callback(self, msg):
        # Determine if Jackal IMU is filtered (has orientation) or raw
        # Checking if the quaternion w component is exactly 0.0
        # If it's a real quaternion, w is almost never exactly 0.0 while xyz are also 0.0
        has_orientation = (msg.orientation.w != 0.0)
        self.process_message(msg, "jackal", use_filtered=has_orientation)

    def report_averages(self):
        if not self.samples["ouster"] or not self.samples["jackal"]:
            rospy.logerr("Stopped collection, but one or both sensors provided no data!")
            rospy.signal_shutdown("No data received.")
            return

        o_data = np.mean(self.samples["ouster"], axis=0)
        j_data = np.mean(self.samples["jackal"], axis=0)
        offset = o_data - j_data

        print("\n" + "="*50)
        print(f"RESULTS AFTER {self.duration}s OF DATA")
        print("="*50)
        print(f"{'Metric':<12} | {'Ouster Avg':<12} | {'Jackal Avg':<12} | {'Offset'}")
        print("-" * 50)

        labels = ["Roll (X)", "Pitch (Y)", "Total Tilt"]
        for i in range(3):
            print(f"{labels[i]:<12} | {o_data[i]:>12.4f} | {j_data[i]:>12.4f} | {offset[i]:>8.4f}")
        
        print("-" * 50)
        print("Suggested Correction for Static Transform (RPY):")
        print(f"Roll: {-offset[0]:.4f}, Pitch: {-offset[1]:.4f}, Yaw: 0.0000")
        print("="*50)
        rospy.signal_shutdown("Finished averaging.")

if __name__ == '__main__':
    averager = IMUAverager(duration=30.0)
    rospy.spin()
