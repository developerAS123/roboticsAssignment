#!/usr/bin/env python3
"""Simple ROS2 client that sends a NavigateToPose goal.
Place the script in scripts/navigate_to_pose.py and make it executable.
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient

def main(args=None):
    rclpy.init(args=args)
    node = Node('navigate_to_pose_client')
    client = ActionClient(node, NavigateToPose, 'navigate_to_pose')
    if not client.wait_for_server(timeout_sec=10.0):
        node.get_logger().error('NavigateToPose action server not available')
        return
    goal_msg = NavigateToPose.Goal()
    goal_msg.pose = PoseStamped()
    goal_msg.pose.header.frame_id = 'map'
    goal_msg.pose.header.stamp = node.get_clock().now().to_msg()
    # Example goal: (x=1.0, y=0.0, yaw=0.0)
    goal_msg.pose.pose.position.x = 1.0
    goal_msg.pose.pose.position.y = 0.0
    goal_msg.pose.pose.position.z = 0.0
    goal_msg.pose.pose.orientation.w = 1.0  # facing forward
    node.get_logger().info('Sending navigation goal to (1.0, 0.0)')
    send_goal_future = client.send_goal_async(goal_msg)
    rclpy.spin_until_future_complete(node, send_goal_future)
    goal_handle = send_goal_future.result()
    if not goal_handle.accepted:
        node.get_logger().error('Goal rejected')
        return
    node.get_logger().info('Goal accepted, waiting for result...')
    result_future = goal_handle.get_result_async()
    rclpy.spin_until_future_complete(node, result_future)
    result = result_future.result().result
    node.get_logger().info(f'Navigation result: {result}')
    rclpy.shutdown()

if __name__ == '__main__':
    main()

