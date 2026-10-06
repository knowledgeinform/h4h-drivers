#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import asyncio
import threading
import yaml

from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy, HistoryPolicy

import os
from takbridge.cot_icd import UVPCoT
from takbridge.tak_config import TAKConfig

from sensor_msgs.msg import NavSatFix
from std_msgs.msg import Float64
import time
from rclpy.executors import MultiThreadedExecutor

from rclpy.parameter import Parameter

# class UVPCotBridge(Node):
#     def __init__(self, tx_queue):
#         # init ROS Node
#         super().__init__("UVP_COT_Publisher")

#         # tak messaging queue
#         self.tx_queue = tx_queue
#         self.type = "a-f-G-E-V"

#         # position data
#         self.latitude = 0.0
#         self.longitude = 0.0
#         self.heading = 0.0

#         # set up parameters to be read from the config.yaml
#         self.declare_parameter("uid", "")
#         self.declare_parameter("callsign", "")
#         self.declare_parameter("pos_topic", "")
#         self.declare_parameter("compass_topic", "")

#     def setup(self):
#         # pull parameters
#         self.uid = self.get_param("uid")
#         self.callsign = self.get_param("callsign")
#         pos_topic = self.get_param("pos_topic")
#         compass_topic = self.get_param("compass_topic")

#         # set up subscribers


#         self.pos_sub = self.create_subscription(
#             NavSatFix,
#             pos_topic,
#             self.uvp_callback,
#             10
#         )

#         self.heading_sub = self.create_subscription(
#             Float64,
#             compass_topic,
#             self.compass_callback,
#             10
#         )
        
#         self.get_logger().info(f"Subscribed to GPS topic: {pos_topic}")
#         self.get_logger().info(f"Subscribed to Compass topic: {compass_topic}")
#         self.get_logger().info(f"UID: {self.uid}, Callsign: {self.callsign}")

#     def get_param(self, name: str) -> str:    
#         param = self.get_parameter_or(
#             name, rclpy.parameter.Parameter(name, rclpy.Parameter.Type.STRING, "")
#             )
#         value = param.value
#         return value


class UVPBridge(Node):
    def __init__(self, tx_queue):
        super().__init__("uvp_publisher")
        self.tx_queue = tx_queue
        self.heading = 0.0
        self.type = "a-f-G-E-V"

        self.declare_parameter("uid", "")
        self.declare_parameter("callsign", "")
        self.declare_parameter("pos_topic", "")
        self.declare_parameter("compass_topic", "")

    def setup(self):
        self.uid = self.get_param("uid")
        self.callsign = self.get_param("callsign")
        pos_topic = self.get_param("pos_topic")
        compass_topic = self.get_param("compass_topic")

        # Define a custom QoS profile # Note: BEST_EFFORT is ALWAYS compatable, it's the least restrictive
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,  # Matching the Mavros GPS publishers (/mavros/global_position/global)
            durability=DurabilityPolicy.VOLATILE,       # Messages are not stored for late-joining subscribers
            history=HistoryPolicy.KEEP_LAST,            # Keep only the last 'depth' messages
            depth=5                                     # Queue depth
        )


        self.pos_sub = self.create_subscription(
            NavSatFix,
            pos_topic,
            self.uvp_callback,
            qos_profile=qos_profile
        )

        self.heading_sub = self.create_subscription(
            Float64,
            compass_topic,
            self.compass_callback,
            qos_profile=qos_profile
        )
        
        self.get_logger().info(f"Subscribed to GPS topic: {pos_topic}")
        self.get_logger().info(f"Subscribed to Compass topic: {compass_topic}")
        self.get_logger().info(f"UID: {self.uid}, Callsign: {self.callsign}")
    
    def get_param(self, name: str) -> str:
        
        param = self.get_parameter_or(
            name, rclpy.parameter.Parameter(name, rclpy.Parameter.Type.STRING, "")
            )
        value = param.value
        return value

    def uvp_callback(self, msg):
        self.get_logger().info(f"NavSatMsg Received: location is {msg.latitude}, {msg.longitude}, alt={msg.altitude}")
        
        data = {
            "uid": self.uid,
            "type": self.type,
            "latitude": msg.latitude,
            "longitude": msg.longitude,
            "altitude": msg.altitude,
            "ce": 10,
            "le": 10,
            "speed": 0.0,
            "course": self.heading,
            "callsign": self.callsign,            
        }
        
        cot_xml = UVPCoT(data).gen_cot()
        self.get_logger().info(f"Generated CoT XML:\n{cot_xml}")
        self.tx_queue.put_nowait(cot_xml.encode("utf-8")) 

    def compass_callback(self, msg): 
        self.heading = msg.data % 360



def load_ros_params_from_namespace(config, namespace: str):
    if namespace not in config:
        raise KeyError(f"Namespace '{namespace}' not found in config.")
    return config[namespace]['ros__parameters']

# def ros_spin_thread(node):
#     rclpy.spin(node)
#     node.destroy_node()

async def main():
    rclpy.init()

    tak_config = TAKConfig()
    clitool = await tak_config.setup_config()

    config_path = os.path.join(os.path.dirname(__file__), "..", "takbridge", "config", "config.yaml")
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    executor = MultiThreadedExecutor()
    publisher_keys = [k for k in config if k.endswith("_publisher")]
    uvp_nodes = []

    for key in publisher_keys:
        ros_params = load_ros_params_from_namespace(config, key)
        sanitized_uid = ros_params['uid'].replace("-", "_")
        node = UVPBridge(tak_config.tx_queue)
        node.set_parameters([Parameter(name=name, value=value) for name, value in ros_params.items()])
        node.setup()

        print(f"\n=== Started UVPBridge for {ros_params.get('callsign')} ===")
        for param in ["uid", "callsign", "pos_topic", "compass_topic"]:
            print(f"{param}: {ros_params.get(param)}")

        executor.add_node(node)
        uvp_nodes.append(node)

    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()

    # Run TAK loop
    await clitool.run()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        executor.shutdown()
        rclpy.shutdown()


if __name__ == "__main__":
    asyncio.run(main())



