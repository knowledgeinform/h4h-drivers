import cv2
import copy
import numpy as np

import commons.math_lib as mlib

class VehicleBase:
	def __init__(self, points, starting_pos=None, heading=None, color=None):
		# init pose and body points and color
		self.pos = starting_pos
		self.heading = heading
		self.points = points
		self.color = color

		# init None's
		if not self.pos:
			self.pos = [0,0]
		if not self.heading:
			self.heading = 0
		if not color:
			self.color = (150,150,0)

	def draw(self, img, scale=1):
		self.drawBody(img, scale=scale)
		self.drawCenter(img)

	def drawCenter(self, img, size=None, color=None):
		# set defaults
		draw_color = (0,0,0) # black by default (BGR)
		if color:
			draw_color = color
		draw_radius = 2
		if size:
			draw_radius = size

		# draw the center circle
		px = round(self.pos[0])
		py = round(self.pos[1])
		cv2.circle(img, (px,py), draw_radius, draw_color, -1)

	def drawBody(self, img, scale=1):
		# get a copy of points
		points = copy.deepcopy(self.points)

		# move to bot frame
		for point in points:
			mlib.pointToFrame(point, self.pos, self.heading) # rounds to int

		# draw
		cv2.fillPoly(img, pts=[np.array(points)], color=self.color)

# if more controllers are added then pull into base class
# class VehicleController:
# 	def __init__(self)


class CrossTrackLineFollower:
	def __init__(self, 
		constant_drive_spd, 		# constant linear velocity
		max_turn_spd, 				# maximum angular velocity (degrees per secon)
		clamp_angle_error,			# clamp on angle error (degrees)
		clamp_crosstrack_error_m,	# clamp on crosstrack error
		max_angle_of_attack_deg,	# maximum angle of attack
		):

		# copy params
		self.constant_drive_spd = constant_drive_spd
		self.max_turn_spd = max_turn_spd
		self.clamp_angle_error = clamp_angle_error
		self.clamp_crosstrack_error_m = clamp_crosstrack_error_m
		self.max_angle_of_attack_deg = max_angle_of_attack_deg

	# returns linear_vel, angular_vel
	def getControl(self, pos, heading, line_start, line_end, angle_hint=None):
		# get crosstrack error
		crosstrack_error = mlib.crossTrackDistance(pos, line_start, line_end)
		crosstrack_error = mlib.saturate(crosstrack_error, self.clamp_crosstrack_error_m)

		# get attack angle
		attack_angle = mlib.rangeShift(crosstrack_error, self.clamp_crosstrack_error_m, self.max_angle_of_attack_deg)

		# calculate target angle
		if angle_hint is None:
			angle_hint = mlib.angleTo(line_start, line_end, convertForUTM=True)
		target_angle = angle_hint - attack_angle # turn away from error signal

		# get angle error
		angle_error = mlib.shortestAngleDiff(heading, target_angle)
		angle_error = mlib.saturate(angle_error, self.clamp_angle_error)

		# DEBUG PRINT
		print("Previous Point:", line_start)
		print("Next Point:", line_end)
		print("Angle Hint:", angle_hint)
		print("Heading:", heading)
		print("Target Angle:", target_angle)
		print("Angle Error:", angle_error)
		print("Attack Angle:", attack_angle)
		print("Crosstrack Error:", crosstrack_error)
		print("Goal:", line_end)

		# get turn speed
		turn_spd = mlib.rangeShift(angle_error, self.clamp_angle_error, self.max_turn_spd)

		# return control values
		return self.constant_drive_spd, turn_spd

