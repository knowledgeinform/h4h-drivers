from __future__ import annotations

import math
import time

import rclpy
from rclpy.node import Node

from cv_bridge import CvBridge

import commons.thread_lib2 as tlib2

# init by default
rclpy.init()

# set up a shared CvBridge
ros2_lib2_cvbridge = CvBridge()

# overall shutdown for ROS2
def shutdown():
    rclpy.shutdown()

# set up global multithread executor
_g_executor = rclpy.executors.MultiThreadedExecutor()
tlib2.threadOnce(func=_g_executor.spin)

# set up global funcs to interact with this executor in a more anonymous way
def addNodeToExec(node:Node):
    _g_executor.add_node(node)


# set up a global concurrent callback group to take advantage of the executor
g_concurrent_callbackgroup = rclpy.callback_groups.ReentrantCallbackGroup()

