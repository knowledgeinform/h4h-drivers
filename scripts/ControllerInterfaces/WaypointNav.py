import utm
import time

import cv2
import numpy as np

import commons.ros2_lib as rlib
import commons.utils_lib as utils

from commons.logger_lib import flogger

from automation_base import AutoNavGPS, AutoNavStates

from std_msgs.msg import Float64

class CompassSubscriber(rlib.RosSubscriber):
	def __init__(self, topic, callback):
		super().__init__(
			node_name = "CompassSubscriber",
			msg_type = Float64,
			rostopic = topic,
			callback = callback,
			namespace = None)


class BaseWaypointNavController:
	def __init__(self, name, path_topic):
		# set up controller
		self.controller = AutoNavGPS(name=name)

		# set up subscriber for incoming paths
		self.waypoint_subscriber = rlib.GeoPathSubscriber(topic=path_topic)
		self.waypoints = None

	# update waypoints
	def updatePath(self):
		# pull path from subscriber buffer
		self.waypoints = self.waypoint_subscriber.pullPath()

		# check if controller is already in autonomy mode and discard path if it is
		if self.controller.state != AutoNavStates.TELEOP:
			self.waypoints = None

		# returns True if there are waypoints
		return self.waypoints is not None

	# pushes current waypoints to controller and kicks off autonomy
	def startAutonomy(self):
		self.controller.waypoints = self.waypoints
		self.controller.state = AutoNavStates.NAV_START_AUTO
		print("Starting Autonomy")

	# update controller position
	def updatePosition(self):
		raise NotImplementedError

	# update controller heading
	def updateHeading(self):
		raise NotImplementedError

	# returns whether or not we currently have 
	def hasFix(self):
		raise NotImplementedError

	# outputs debug logging data to file logger
	def logDebugFile(self):
		x,y = self.controller.pos
		heading = self.controller.heading

		outstr = "<<<"
		outstr += str(x) + " "
		outstr += str(y) + " "
		outstr += str(heading) + "\n"

		flogger.write(outstr)

	def sendControl(self):
		# update controller position
		self.updatePosition()
		self.updateHeading()

		# file debugging (only does anything if envvar FILE_LOGGER_ON=True)
		self.logDebugFile()

		# calculate and send control message
		self.controller.updateControl()


class NavSatFixAndCompassWaypointNavController(BaseWaypointNavController):
	def __init__(self):
		# pull env variables
		path_topic = utils.getEnv("PATH_TOPIC")
		nav_topic = utils.getEnv("NAV_TOPIC")
		compass_topic = utils.getEnv("COMPASS_TOPIC")
		self.target_name = utils.getEnv("TARGET_VEHICLE")

		# init parent
		super().__init__(name="NavSatFixAndCompassWaypointNavController", path_topic=path_topic)

		# set target for message
		self.controller.msg.name = self.target_name

		# set up a buffer for heading updates to prevent desyncs
		self.heading_buffer = 0.0

		# set up position subscriber
		self.nav_subscriber = rlib.NavSatFixSubscriber(
			topic=nav_topic)

		# set up heading subscriber
		self.heading_subscriber = CompassSubscriber(
			topic=compass_topic,
			callback=self.compassCallback)

	# OVERRIDE
	def updatePosition(self):
		x = self.nav_subscriber.easting_m
		y = self.nav_subscriber.northing_m
		self.controller.pos = [x,y]

	# OVERRIDE
	def updateHeading(self):
		self.controller.heading = self.heading_buffer

	# OVERRIDE
	def hasFix(self):
		return self.nav_subscriber.gps_fix

	# callback for compass heading from V60
	def compassCallback(self, msg):
		self.heading_buffer = -msg.data % 360



if __name__ == "__main__":
	waypoint_nav = NavSatFixAndCompassWaypointNavController()

	# wait for gps fix
	print("Waiting for GPS Fix...")
	while not waypoint_nav.hasFix():
		time.sleep(1.0)
	print("Got GPS Fix")

	# start main loop
	while True:
		# check for new waypoints if in teleop (not currently running autonomy)
		if waypoint_nav.controller.state == AutoNavStates.TELEOP:
			if waypoint_nav.updatePath():
				print("Got a Path")
				waypoint_nav.startAutonomy()

		# send control (won't do anything if in teleop mode)
		waypoint_nav.sendControl()
		
		print("------")
		print("Position:", waypoint_nav.controller.pos)
		print("Heading:", waypoint_nav.controller.heading)

		time.sleep(0.1)
