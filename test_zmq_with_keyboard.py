
import cv2
import time
import numpy as np

import commons.simple_zmq_lib as zlib
import commons.rlac_comms_lib as rclib

from commons.input_lib import WasdIjklController
from commons.utils_lib import Timer, RisingTrigger


class RisingTriggerKeyList:
	def __init__(self, controller:WasdIjklController):
		self.controller = controller
		self.actions = {}
	
	def addAction(self, action_name:str, key:str):
		self.actions[action_name] = RisingTrigger()
		self.controller.addKey(action_name, key)

if __name__ == "__main__":
	# make a blank canvas as an active window
	blank = np.zeros((300,300,3), np.uint8)

	# set up a zmq publisher (as host)
	publisher = zlib.SimpleZMQPublisher(port="5581")

	# set target vehicle
	target_name = "h4h_rad_c100"
	# target_name = "h4h_rad_teal"
	# target_name = "h4h_mtrs_chassis"

	# set up controller
	controller = WasdIjklController()

	# set action strings
	action_list = RisingTriggerKeyList(controller)

	action_list.addAction("arm", 'm')
	action_list.addAction("disarm", 'n')

	action_list.addAction("land", 'f')
	action_list.addAction("takeoff", 'r')

	# flight modes are now handled in a custom way
	flight_mode_actions = {
		"HOLD": 'h', 
		"POSITION": 'p',
		"MANUAL": 'y', 
		"STABILIZED": 'u',
		"OFFBOARD": 'o',
		"ALTITUDE": 'q',
		}
	for flight_mode, key in flight_mode_actions.items():
		action_list.addAction(flight_mode, key)

	# special controller key for turning off control to test failsafe behaviors
	special_action = "nocontrol"
	special_flag = False
	action_list.addAction(special_action, 'z')

	limiter = Timer()

	# set up velocity vectors
	lin_vec = rclib.Vec3()
	ang_vec = rclib.Vec3()

	# main loop
	while controller.alive():
		# update action triggers
		for name in controller.switches:
			if name != special_action:
				action_list.actions[name].update(controller.switches[name])
			else:
				# special_flag = not special_flag
				# print("Special Flag:", special_flag)
				pass

		# publish out controls at specified rate
		if limiter.totalTime() > 1.0 / 10:
			# update movement control # this matches DGI joystick control
			lin_vec.z = controller.axes[0] # up/down 			# W/S
			ang_vec.z = controller.axes[1] # yaw				# D/A
			lin_vec.x = controller.axes[2] # forward/backward	# I/K
			lin_vec.y = controller.axes[3] # strafe left/right	# L/J

			# build action string dictionary
			action_str_dict = {}
			for name in action_list.actions:
				action_str_dict[name] = action_list.actions[name].trigger()

			# custom shim for the flight modes
			for flight_mode in flight_mode_actions.keys():
				if action_str_dict[flight_mode]:
					action_str_dict["flight_mode"] = flight_mode

			# FLIP FOR V60 FOR SOME REASON: TODO: fix this properly, probably on the vehicle-side interface
			# ang_vec.z = -ang_vec.z

			# build up the message string
			target = target_name
			if special_flag:
				target = "none"
			control_msg = rclib.toRlacJsonControlCommand(target_name, lin_vec, ang_vec)
			action_msg = rclib.toRlacJsonActionsCommand(target_name, action_str_dict)
			# print(msg)

			# publish the command string
			publisher.publish(control_msg)
			time.sleep(0.01)
			publisher.publish(action_msg)
			limiter.reset()

	# 	# show the active window
		cv2.imshow("I'm a Window", blank)
		cv2.waitKey(1)
	cv2.destroyAllWindows()


