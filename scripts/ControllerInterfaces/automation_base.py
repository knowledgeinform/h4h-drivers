import cv2
import copy
import math
import random

import numpy as np
import commons.h4h_lib as hlib
import commons.ros2_lib as rlib
import commons.math_lib as mlib
import commons.utils_lib as utils

from commons.logger_lib import flogger

from enum import Enum
from h4h_msgs.msg import ControlInput
from commons.vehicle_lib import VehicleBase, CrossTrackLineFollower


class AutoNavStates(Enum):
	TELEOP 					= 0 # Default state. Don't allow AutoNav to send messages
	NAV_LINE_FOLLOWING 		= 1 # AutoNav's line following behavior
	NAV_TURN_IN_PLACE 		= 2 # AutoNav's turn-in-place behavior
	NAV_START_AUTO			= 3 # AutoNav's Startup State


class AutoNavBase(hlib.ControllerInterfaceBase):
	def __init__(self, name):
		# init parent
		super().__init__(name=name)

		# vehicle pose
		self.pos = [0,0] # [meters Easting, meters Northing]
		self.heading = 0 # degrees

		# waypoint targets
		self.waypoints = [] # points are [meters Easting, meters Northing]
		self.previous_target = None # point is [meters Easting, meters Northing]
		self.current_target = None # point is [meters Easting, meters Northing]

		# set up a line follower controller
		self.line_controller = CrossTrackLineFollower(
			constant_drive_spd = 1.0, # [0,1]
			max_turn_spd = 0.2, # [0,1]
			clamp_angle_error = 45.0,
			clamp_crosstrack_error_m = 5.0,
			max_angle_of_attack_deg = 45.0)

		# line following vars
		self.target_heading = 0.0 # degrees # angle from PREVIOUS to CURRENT

		# turn-in-place vars
		self.static_turn_spd = 1.0 # [0,1]
		self.static_target_heading = 0.0 # degrees # angle from ME to TARGET
		self.close_enough_deg = 2.0 # degrees

		self.target_sign = 0 # (-1, 0, 1) direction of target heading to prevent wobble

		# simple states for different driving behaviors
		self.state = AutoNavStates.TELEOP

	# writes debug output using the file logger
	def writeToDebugFile(self, move, turn):
		outstr = ">>>"
		outstr += str(move) + " "
		outstr += str(turn) + "\n"

		flogger.write(outstr)

	def resetAndStop(self):
		self.publishSoftEstop()
		self.state = AutoNavStates.TELEOP
		self.current_target = None
		self.previous_target = None

	def updateControl(self):
		print("INTERNAL STATE:", self.state)
		# switch behavior on state
		if self.state == AutoNavStates.TELEOP:
			return

		# update target
		if self.current_target is None:
			print("Getting New Target")
			# set a current and previous target
			if len(self.waypoints) > 0:
				self.current_target = self.waypoints.pop(0)
			else:
				# done navigating
				self.resetAndStop()
				return

			if self.previous_target is None:
				self.previous_target = self.pos

			# update state
			self.state = AutoNavStates.NAV_TURN_IN_PLACE
			self.static_target_heading = mlib.angleTo(self.pos, self.current_target, convertForUTM=True)
			self.target_heading = mlib.angleTo(self.previous_target, self.current_target, convertForUTM=True)
			self.target_sign = mlib.sign(mlib.shortestAngleDiff(self.heading, self.static_target_heading))
			print("End of New Target State:", self.state)

		# get command output
		move = 0.0
		turn = 0.0
		if self.state == AutoNavStates.NAV_TURN_IN_PLACE:
			move, turn = self.turnInPlace()

		elif self.state == AutoNavStates.NAV_LINE_FOLLOWING:
			move, turn = self.lineFollowing()

		# debug file logging (only does anything if FILE_LOGGER_ON=True)
		self.writeToDebugFile()
		
		# publish command
		self.setTwoAxis(forward=move, turn=turn)
		self.publish()

	def turnInPlace(self):
		# check end state
		angle_diff = mlib.shortestAngleDiff(self.heading, self.static_target_heading)
		print("Angle Diff:", angle_diff)
		print("Target Heading:", self.static_target_heading)
		print("Heading:", self.heading)
		print("Target Sign:", self.target_sign)

		# check for overshoot (wobble protection)
		if mlib.sign(angle_diff) != self.target_sign:
			self.state = AutoNavStates.NAV_LINE_FOLLOWING
			return

		# check for target reached
		if abs(angle_diff) < self.close_enough_deg:
			self.state = AutoNavStates.NAV_LINE_FOLLOWING
			return

		# calculate command
		linear_vel = 0.1
		angular_vel = self.static_turn_spd * self.target_sign
		return linear_vel, angular_vel

	def lineFollowing(self):
		# check end state
		if mlib.overEndOfLine(self.pos, self.previous_target, self.current_target):
			self.previous_target = self.current_target
			self.current_target = None
			return

		# get control from line follower
		linear_vel, angular_vel = self.line_controller.getControl(
			self.pos,
			self.heading,
			self.previous_target,
			self.current_target,
			angle_hint=self.target_heading)

		# return command
		return linear_vel, angular_vel

class AutoNavGPS(AutoNavBase):
	def __init__(self, name):
		# init parent
		super().__init__(name)

		# set current GPS position (noisy position)
		self.pos = [0,0]
		self.heading = 0

class AutoNavDummyGPS(AutoNavBase):
	def __init__(self, pos, heading, pos_noise, heading_noise, name, topic, name_map_file):
		# init parent
		super().__init__(name, topic, name_map_file)

		# set current GPS position (noisy position)
		self.pos = pos[:]
		self.heading = heading

		# set true position
		self.true_pos = pos[:]
		self.true_heading = heading

		# set noise
		self.pos_noise = pos_noise
		self.heading_noise = heading_noise
		self.updateNoisyPos()


	def updateNoisyPos(self):
		nx = random.gauss(self.true_pos[0], self.pos_noise)
		ny = random.gauss(self.true_pos[1], self.pos_noise)
		self.pos = [nx,ny]

		self.heading = random.gauss(self.true_heading, self.heading_noise)

