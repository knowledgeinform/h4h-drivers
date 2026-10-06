# boilerplate type hinting and clarity imports
from __future__ import annotations
import sys
if sys.version_info >= (3, 12):
	from typing import override 
else:
	from typing_extensions import override

import commons.utils_lib as utils
import commons.mav_lib as mavlib
import commons.thread_lib2 as tlib2
import commons.simple_zmq_lib as zlib

from commons.h4h.vehicle_interface import MavMultirotorBase

def renameDict(dict:dict, curr_name:str, new_name:str):
	dict["new_name"] = dict["curr_name"]
	del dict["curr_name"]

class RLACMultirotorControl(MavMultirotorBase):
	""" concrete implementation for Mavlink multirotor vehicle control for RLAC """

	def __init__(self):
		# init parents
		super().__init__(name="RLACMultirotorControl")

		# DEBUG: waypoints for testing mission plan sending
		# "lat": 47.397971, "lon": 8.5461641
		# self.length = .001
		# self.sent_waypoints = False
		# self.debug_waypoints = []
		# self.debug_waypoints.append([47.397971, 8.5461641, 10.0]) # lat,lon,alt
		# self.debug_waypoints.append([47.397971 - self.length, 8.5461641, 15.0]) 
		# self.debug_waypoints.append([47.397971 - self.length, 8.5461641 - self.length, 20.0])
		# self.debug_waypoints.append([47.397971, 8.5461641 - self.length, 15.0])
		# self.debug_waypoints.append([47.397971, 8.5461641, 10.0])
		
		
		# set up mavlink listener
		self.listener_interface = mavlib.MavlinkListenerPluginInterface(self.driver)

		tomahawk_status_filter = ["lat", "lon", "relative_alt", "hdg", "battery_remaining", "system_status", "custom_mode"]
		self.tomahawk_status_group = mavlib.MavlinkListenerGroup(
			self.listener_interface,
			filter=tomahawk_status_filter)

		self.tomahawk_status_group.registerListener(mavlib.GPSMavlinkListenerPlugin())
		self.tomahawk_status_group.registerListener(mavlib.HeartbeatMavlinkListenerPlugin())
		self.tomahawk_status_group.registerListener(mavlib.BatteryMavlinkListenerPlugin())

		# set up a zmq link to publish out the status
		self.status_port = utils.getEnv("STATUS_PORT")
		self.status_publisher = zlib.SimpleZMQPublisher(port=self.status_port)
		self.status_msg = {}
		self.status_msg["messageType"] = "status"
		self.status_msg["messageData"] = {}

		# set up a zmq link to publish out the position and orientation for the vision pipeline
		self.orientation_publisher = zlib.SimpleZMQPublisher(port=utils.getEnv("VISION_PORT"))

		orientation_status_filter = ["lat", "lon", "relative_alt", "roll", "pitch", "yaw"]
		self.orientation_status_group = mavlib.MavlinkListenerGroup(
			self.listener_interface,
			filter=orientation_status_filter)

		self.orientation_status_group.registerListener(mavlib.GPSMavlinkListenerPlugin())
		self.orientation_status_group.registerListener(mavlib.AttitudeMavlinkListenerPlugin())

		# mapping for flight modes
		self.flight_mode_dict = {
			84148224:	"RTL",
			100925440:	"LAND",
			393216: 	"OFFBOARD",
			196608: 	"POSITION",
			50593792: 	"HOLD",
			458752: 	"STABILIZED", 
			65536: 		"MANUAL",
			131072:		"ALTITUDE",
			67371008:	"MISSION",
		}

		# start status publisher loop
		tlib2.threadForever(func=self.publishStatusToTomahawk, rate_hz=1.0)
		tlib2.threadForever(func=self.publishToVisionPipeline, rate_hz=10.0)
		
		# start control loop
		self.start()
	
	def publishToVisionPipeline(self):
		""" publishes orientation and position to the Vision Pipeline """
		# preprocess the built-up data in the listener interface
		data = self.orientation_status_group.getData()

		# early exit if listener hasn't heard at least one of each message
		if data is None:
			return

		# publish
		self.orientation_publisher.publish(data)
		print(f"Published Orientation Message: {data}")


		# DEBUG: try sending mission plan to drone
		# if not self.sent_waypoints:
		# 	self.sent_waypoints = self.driver.sendMissionPlan(self.debug_waypoints, add_takeoff_land=True)
		# 	if self.sent_waypoints:
		# 		self.driver.startMission()
				
	
	def publishStatusToTomahawk(self):
		""" publishes a ZMQ message with status to the Tomahawk UCC Controller """
		# DEBUG DEBUG DEBUG: print out the message counts
		# print(">>>Counts: ", self.listener_interface.getCounts())

		# preprocess the built-up data in the listener interface
		data = self.tomahawk_status_group.getDataWithoutTimestamps()

		# early exit if listener hasn't heard at least one of each message
		if data is None:
			return

		# build up the message
		self.status_msg["messageData"]["name"] = self.namespace
		self.status_msg["messageData"].update(data)

		# change some names
		renameDict(self.status_msg["messageData"], "hdg", "heading")
		renameDict(self.status_msg["messageData"], "relative_alt", "alt")

		# reformat some values
		self.status_msg["messageData"]["powerLevel"] = data["battery_remaining"] / 100.0
		del self.status_msg["messageData"]["battery_remaining"]

		self.status_msg["messageData"]["armed"] = (data["system_status"] == 4) # 4 = Armed
		del self.status_msg["messageData"]["system_status"]

		# parse flight mode
		flight_mode = "NONE"
		flight_num = int(data["custom_mode"])
		# print(f"Custom Mode Number: {flight_num}")
		if flight_num in self.flight_mode_dict:
			flight_mode = self.flight_mode_dict[flight_num]
			self.status_msg["messageData"]["flight_mode"] = flight_mode

		# publish
		self.status_publisher.publish(self.status_msg)
		print(f"Published Status Message: {self.status_msg}")


if __name__ == "__main__":
	# init the controller
	controller = RLACMultirotorControl()
	controller.spin()