# boilerplate type hinting and clarity imports
from __future__ import annotations
import sys
if sys.version_info >= (3, 12):
	from typing import override 
else:
	from typing_extensions import override

import time

import commons.utils_lib as utils
import commons.simple_zmq_lib as zlib
import commons.rlac_comms_lib as rclib

from geometry_msgs.msg import Vector3
from commons.h4h.vehicle_interface import UGVBase

# spins up a Ros-to-Zmq MTRS driver for each MTRS namespace
class RosToZmqMTRSDrivers:
	def __init__(self):
		# pull MTRS names from env
		GRIPPER_NAME = utils.getEnv("GRIPPER_NAME", cast=str)
		CHASSIS_NAME = utils.getEnv("CHASSIS_NAME", cast=str)

		# pull zmq ports from env
		GRIPPER_PORT = utils.getEnv("ZMQ_GRIPPER_PORT")
		CHASSIS_PORT = utils.getEnv("ZMQ_CHASSIS_PORT")

		# set up zmq publishers
		self.gripper_pub = zlib.SimpleZMQPublisher(port=GRIPPER_PORT)
		self.chassis_pub = zlib.SimpleZMQPublisher(port=CHASSIS_PORT)

		# set up drivers
		self.gripper_driver = ZmqDriveController(zmq_publisher=self.gripper_pub, override_namespace=GRIPPER_NAME)
		self.chassis_driver = ZmqDriveController(zmq_publisher=self.chassis_pub, override_namespace=CHASSIS_NAME)


# right-side controller for the Zmq Driver
# converts ROS2 -> ZMQ for the MTRS driver
# MTRS driver converts ZMQ -> ROS1
class ZmqDriveController(UGVBase):
	def __init__(self, zmq_publisher, override_namespace=None):
		# DEBUG DEBUG DEBUG: log runtime
		self.start_time = time.time()

		# init parent
		self.target_name = override_namespace
		super().__init__(name="ZmqDriverController", override_namespace=override_namespace)

		# init ZMQ publisher
		self.zmq_pub = zmq_publisher

		# start up runner thread
		self.start()


	# publish out zmq control message
	@override
	def update(self):
		# reverse the direction of turning (angular z)
		fixed_angular = Vector3()
		fixed_angular.x = self.angular.x
		fixed_angular.y = self.angular.y
		fixed_angular.z = -self.angular.z
		
		# build out the command as json # use the [0,1] range outputs
		command_json_str = rclib.toRlacJsonControlCommand(self.target_name, self.linear, fixed_angular)

		# publish out the drive command
		self.zmq_pub.publish(command_json_str)

		# publish out log
		self.logger.info(f"Published {command_json_str} to ZMQ")

	@override
	def softStop(self) -> bool:
		""" Send a stop (as in stay in place) command to the vehicle """
		print("Sending softstop() to", self.target_name)
		# build out a zero command in json
		command_json_str = rclib.toRlacJsonControlCommand(self.target_name, self.stop_vector, self.stop_vector)

		# publish out the drive command
		self.zmq_pub.publish(command_json_str)
		return True


if __name__ == "__main__":
	# init the controller
	controller = RosToZmqMTRSDrivers()

	# idle
	while True:
		time.sleep(9999)

