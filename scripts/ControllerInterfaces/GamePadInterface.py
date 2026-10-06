import os
import time

import pygame as pyg

import commons.math_lib as mlib
import commons.utils_lib as utils

from commons.h4h.controller_interface import ControllerSixDofBase

# CONTROLLER MAPPINGS:

# Axis 0 = Left thumbstick (+1 is right)
# Axis 1 = Left thumbstick (+1 is down)
# Axis 2 = Right thumbstick (+1 is right)
# Axis 3 = Right thumbstick (+1 is down)
# Axis 4 = Left Trigger (+1 is pressed)
# Axis 5 = Right Trigger (+1 is pressed)

# N/S/E/W Face buttons are the four buttons on the right side of the controller

# Button 0 = South Face button (+1 is pressed)
# Button 1 = East Face button (+1 is pressed)
# Button 2 = West Face button (+1 is pressed)
# Button 3 = North Face button (+1 is pressed)
# I'm done mapping buttons, there are 16 of them

class GamePadControllerInterface(ControllerSixDofBase):
	def __init__(self):
		# init h4h parent
		super().__init__(name="GamePadControllerInterface")

		# set up pygame
		# allow gamepad control to continue without window focus
		os.environ['SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS'] = "1"
		pyg.init()
		pyg.joystick.init()
		self.clock = pyg.time.Clock()

		# pull environment variables
		self.poll_rate = 	utils.getEnv("UPDATE_RATE", 20)
		self.joystick_id = 	utils.getEnv("JOY_ID", 0)
		self.fb_deadzone = 	utils.getEnv("FB_DEADZONE", 0.02)
		self.lr_deadzone = 	utils.getEnv("LR_DEADZONE", 0.02)

		# connect to controller
		self.controller = pyg.joystick.Joystick(self.joystick_id)

	def shutdown(self):
		pyg.joystick.quit()
		pyg.quit()

	def start(self):
		stop_flag = False
		while not stop_flag:
			# check for quit event
			for event in pyg.event.get():
				if event.type == pyg.QUIT:
					stop_flag = True

			# get "button down" events
			east_button_down = self.controller.get_button(1) # quit entire program (may remove later)
			# west_button_down = self.contorller.get_button(2) # unused for now
			north_button_down = self.controller.get_button(3) # activate controller
			south_button_down = self.controller.get_button(0) # deactivate controller

			# check "quit" button press
			if east_button_down == 1:
				stop_flag = True

			# check arm/disarm
			if north_button_down: 
				self.controller.arm()
			if south_button_down:
				self.controller.disarm()


			# get leftstick x-axis for left/right turn
			leftstick_lr = controller.get_axis(0) # left stick, left-right axis
			turn_input = mlib.applyDeadzone(leftstick_lr, self.lr_deadzone)

			# get triggers for throttle
			right_trigger = controller.get_axis(5) # forward
			left_trigger = controller.get_axis(4) # reverse

			# shift trigger output numerical range from [-1,1] to [0,1]
			right_trigger += 1.0 # [0,2]
			right_trigger /= 2.0 # [0,1]
			left_trigger += 1.0
			left_trigger /= 2.0

			# add up trigger inputs (with left as negative)
			trigger_combined = right_trigger - left_trigger

			# apply deadzone
			throttle_input = mlib.applyDeadzone(trigger_combined, self.fb_deadzone)

			# publish command
			self.setTwoAxis(throttle_input, turn_input)
			self.publish()

			# limit poll rate
			self.clock.tick(self.poll_rate)


if __name__ == "__main__":
	# set up the controller
	controller = GamePadControllerInterface()
	controller.spin()
