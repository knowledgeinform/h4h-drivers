#!/usr/bin/env python3

from platform import platform
import rclpy
from rclpy.node import Node
import asyncio
import threading
import logging

from takbridge.cot_icd import ContactCoT
from sensor_msgs.msg import NavSatFix
from std_msgs.msg import Float64



class ContactCoT(Node):
    def __init__(self, tx_queue):
        super().__init__("contact_publisher")
        self.tx_queue = tx_queue
        self.heading = 0.0
        
        self.type = "a-h-G-U-S-X-O" # hostile
        self.ce = 10
        self.le =10
        self.platform = None
        self.effector = None
        self.priority = 0.0
        self.task_complete = bool
        self.target_status = None
        
        self.declare_parameter("uid", "")
        self.declare_parameter("callsign", "")
        self.declare_parameter("pos_topic", "")
        self.declare_parameter("compass_topic", "")
        
    def setup(self):
        self.uid = self.get_param("uid")
        self.callsign = self.get_param("callsign")
        pos_topic = self.get_param("pos_topic")
        compass_topic = self.get_param("compass_topic")
        
        self.pos_sub = self.create_subscription(
            NavSatFix,
            pos_topic,
            self.pos_callback,
            10
        )

        self.heading_sub = self.create_subscription(
            Float64,
            compass_topic,
            self.heading_callback,
            10
        )
        
        self.get_logger().info(f"Subscribed to: {pos_topic}, {compass_topic}")
        self.get_logger().info(f"UID={self.uid}, Callsign={self.callsign}")
    

    def get_param(self, name: str) -> str:
        
        param = self.get_parameter_or(
            name, rclpy.parameter.Parameter(name, rclpy.Parameter.Type.STRING, "")
            )
        value = param.value
        return value

    def contact_callback(self, msg):
        self.get_logger().info(f"NavSatMsg Received: location is {msg.latitude}, {msg.longitude}, alt={msg.altitude}")
        
        data = {
            "uid": self.uid,
            "type": self.type,
            "latitude": msg.latitude,
            "longitude": msg.longitude,
            "altitude": msg.altitude,
            "ce": self.ce,
            "le": self.le,
            "speed": 0.0,
            "course": self.heading,
            "callsign": self.callsign,            
        }
        
        cot_xml = ContactCoT(
            data=data,
            callsign=self.callsign,
            platform=self.platform,
            effector=self.effector,
            priority=self.priority,
            task_complete=self.task_complete,
            target_status=self.target_status
        ).gen_cot()
        self.get_logger().info(f"Generated Contact CoT XML:\n{cot_xml}")
        self.tx_queue.put_nowait(cot_xml.encode("utf-8")) 

    def compass_callback(self, msg): 
        self.heading = msg.data % 360

