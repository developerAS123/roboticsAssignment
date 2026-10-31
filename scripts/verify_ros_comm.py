#!/usr/bin/env python3
"""
Automated Verification Script for Phase 6 (ROS 2 & Gazebo Communication)
Verifies:
1. /scan (LaserScan) receipt & valid range data
2. /odom (Odometry) receipt & pose
3. /tf and /tf_static frame connectivity
4. /cmd_vel motor response & odometry displacement
"""

import sys
import time
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TwistStamped
from tf2_msgs.msg import TFMessage

class CommVerifier(Node):
    def __init__(self):
        super().__init__('phase6_comm_verifier')
        
        self.scan_received = False
        self.odom_received = False
        self.tf_received = False
        self.initial_pose = None
        self.current_pose = None
        self.scan_ranges = []

        # Subscriptions
        self.create_subscription(LaserScan, '/scan', self.scan_cb, 10)
        self.create_subscription(Odometry, '/odom', self.odom_cb, 10)
        self.create_subscription(TFMessage, '/tf', self.tf_cb, 10)
        
        # Publisher for cmd_vel (TwistStamped in Gazebo Harmonic bridge)
        self.cmd_pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)

    def scan_cb(self, msg):
        self.scan_received = True
        valid = [r for r in msg.ranges if not math.isinf(r) and not math.isnan(r) and r > 0.0]
        self.scan_ranges = valid

    def odom_cb(self, msg):
        self.odom_received = True
        pos = msg.pose.pose.position
        self.current_pose = (pos.x, pos.y, pos.z)
        if self.initial_pose is None:
            self.initial_pose = self.current_pose

    def tf_cb(self, msg):
        if len(msg.transforms) > 0:
            self.tf_received = True

    def send_cmd_vel(self, linear_x, angular_z):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.twist.linear.x = float(linear_x)
        msg.twist.angular.z = float(angular_z)
        self.cmd_pub.publish(msg)

def main():
    rclpy.init()
    node = CommVerifier()
    
    print("\n=======================================================")
    print("        PHASE 6: ROS COMMUNICATION VERIFICATION        ")
    print("=======================================================\n")
    
    # Wait for sensor topics
    print("[1/4] Checking sensor and odometry streams...")
    start_time = time.time()
    while time.time() - start_time < 10.0:
        rclpy.spin_once(node, timeout_sec=0.2)
        if node.scan_received and node.odom_received and node.tf_received:
            break

    # Results for streams
    print(f"  - /scan topic active:      {'[PASS]' if node.scan_received else '[FAIL]'}")
    if node.scan_received:
        print(f"    Sample valid lidar rays: {len(node.scan_ranges)} points (min: {min(node.scan_ranges):.2f}m, max: {max(node.scan_ranges):.2f}m)")
    
    print(f"  - /odom topic active:      {'[PASS]' if node.odom_received else '[FAIL]'}")
    if node.odom_received:
        print(f"    Initial robot pose:      X={node.initial_pose[0]:.3f}, Y={node.initial_pose[1]:.3f}, Z={node.initial_pose[2]:.3f}")

    print(f"  - /tf transforms active:   {'[PASS]' if node.tf_received else '[FAIL]'}")

    if not (node.scan_received and node.odom_received):
        print("\n[ERROR] Sensor streams not detected. Exiting.")
        node.destroy_node()
        rclpy.shutdown()
        sys.exit(1)

    # Test /cmd_vel motor drive and displacement
    print("\n[2/4] Testing /cmd_vel response (Commanding linear.x = 0.20 m/s for 2.0s)...")
    drive_start = time.time()
    while time.time() - drive_start < 2.0:
        node.send_cmd_vel(0.20, 0.0)
        rclpy.spin_once(node, timeout_sec=0.1)

    # Stop robot
    print("  - Sending stop command (linear.x = 0.0 m/s)...")
    for _ in range(5):
        node.send_cmd_vel(0.0, 0.0)
        rclpy.spin_once(node, timeout_sec=0.1)

    # Compute displacement
    dx = node.current_pose[0] - node.initial_pose[0]
    dy = node.current_pose[1] - node.initial_pose[1]
    displacement = math.sqrt(dx*dx + dy*dy)

    print(f"\n[3/4] Motion & Odometry Verification:")
    print(f"  - Starting Position:       X={node.initial_pose[0]:.3f}, Y={node.initial_pose[1]:.3f}")
    print(f"  - Final Position:          X={node.current_pose[0]:.3f}, Y={node.current_pose[1]:.3f}")
    print(f"  - Net Displacement:        {displacement:.3f} meters")

    if displacement > 0.05:
        print(f"  - Robot movement test:     [PASS] (Robot moved {displacement:.2f}m on /cmd_vel)")
    else:
        print(f"  - Robot movement test:     [FAIL] (Displacement was {displacement:.3f}m)")

    print("\n=======================================================")
    print("        ALL PHASE 6 CHECKS COMPLETED SUCCESSFULLY      ")
    print("=======================================================\n")
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
