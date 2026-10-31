#!/usr/bin/env python3
"""Python navigation client that can send one or multiple NavigateToPose goals.
Usage examples:
  python navigate_multi_goal.py 1.0 0.0 0.0          # single goal (x, y, yaw)
  python navigate_multi_goal.py 1.0 0.0 0.0 2.0 0.5 0.0   # two goals sequentially
  python navigate_multi_goal.py --file goals.txt      # file with lines: x y yaw
"""
import sys
import argparse
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient

def send_goal(node, x, y, yaw):
    client = ActionClient(node, NavigateToPose, 'navigate_to_pose')
    if not client.wait_for_server(timeout_sec=10.0):
        node.get_logger().error('NavigateToPose action server not available')
        return False
    goal_msg = NavigateToPose.Goal()
    goal_msg.pose = PoseStamped()
    goal_msg.pose.header.frame_id = 'map'
    goal_msg.pose.header.stamp = node.get_clock().now().to_msg()
    goal_msg.pose.pose.position.x = x
    goal_msg.pose.pose.position.y = y
    goal_msg.pose.pose.position.z = 0.0
    # Convert yaw (rad) to quaternion (only yaw rotation)
    import math
    half_yaw = yaw * 0.5
    goal_msg.pose.pose.orientation.x = 0.0
    goal_msg.pose.pose.orientation.y = 0.0
    goal_msg.pose.pose.orientation.z = math.sin(half_yaw)
    goal_msg.pose.pose.orientation.w = math.cos(half_yaw)
    node.get_logger().info(f'Sending navigation goal to ({x:.2f}, {y:.2f}, yaw={yaw:.2f})')
    send_future = client.send_goal_async(goal_msg)
    rclpy.spin_until_future_complete(node, send_future)
    goal_handle = send_future.result()
    if not goal_handle.accepted:
        node.get_logger().error('Goal rejected')
        return False
    result_future = goal_handle.get_result_async()
    rclpy.spin_until_future_complete(node, result_future)
    result = result_future.result().result
    node.get_logger().info(f'Navigation result: {result}')
    return True

def main(argv=None):
    rclpy.init(args=argv)
    node = Node('navigate_multi_goal_client')
    parser = argparse.ArgumentParser(description='Send one or more navigation goals')
    parser.add_argument('coords', nargs='*', help='Sequence of x y yaw values')
    parser.add_argument('--file', type=str, help='Path to a text file with goal lines: "x y yaw"')
    args = parser.parse_args()
    goals = []
    if args.file:
        try:
            with open(args.file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) != 3:
                        continue
                    goals.append((float(parts[0]), float(parts[1]), float(parts[2])))
        except Exception as e:
            node.get_logger().error(f'Failed to read goals file: {e}')
    else:
        # Expect multiples of three numbers
        if len(args.coords) % 3 != 0:
            node.get_logger().error('Provide coordinates as triples: x y yaw')
            return
        for i in range(0, len(args.coords), 3):
            x = float(args.coords[i])
            y = float(args.coords[i+1])
            yaw = float(args.coords[i+2])
            goals.append((x, y, yaw))
    if not goals:
        node.get_logger().error('No goals specified')
        return
    for (x, y, yaw) in goals:
        success = send_goal(node, x, y, yaw)
        if not success:
            node.get_logger().error('Stopping further goals due to failure')
            break
    rclpy.shutdown()

if __name__ == '__main__':
    main()

