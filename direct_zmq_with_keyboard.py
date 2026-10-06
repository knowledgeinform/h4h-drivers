
import cv2
import time
import numpy as np

import commons.simple_zmq_lib as zlib

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
	publisher = zlib.SimpleZMQPublisher(port=5581)

	# set target vehicle
	target_name = "h4h_rad_c100"
	# target_name = "h4h_rad_teal"
	# target_name = "h4h_mtrs_chassis"

	# set up controller
	controller = WasdIjklController()

	# set action strings
	action_list = RisingTriggerKeyList(controller)

	# map additional actions to keys
	action_map = {
		"ARM": 			'm',
		"DISARM": 		'n',
		"LAND": 		'f',
		"TAKEOFF": 		'r',
		"HOLD": 		'h', 
		"POSITION": 	'p',
		"MANUAL": 		'y', 
		"STABILIZED": 	'u',
		"OFFBOARD": 	'o',
		"ALTITUDE": 	'q',
		}
	for flight_mode, key in action_map.items():
		action_list.addAction(flight_mode, key)

	# limit the publishing speed
	limiter = Timer()

	# set up velocity vectors
	lin_vec = [0,0,0] # x,y,z
	ang_vec = [0,0,0]

	# set up message with default values
	msg = {
		"name": target_name,
		"movement": {
			"linear": [0,0,0],
			"angular": [0,0,0]
		},
		"actions": []
	}

	# main loop
	while controller.alive():
		# update rising action triggers
		for name in controller.switches:
			action_list.actions[name].update(controller.switches[name])

		# publish out controls at specified rate
		if limiter.totalTime() > 1.0 / 10:

			# update movement control # this matches DGI joystick control
			lin_vec[2] = controller.axes[0] # up/down 			# W/S
			ang_vec[2] = controller.axes[1] # yaw right/left	# D/A
			lin_vec[0] = controller.axes[2] # forward/backward	# I/K
			lin_vec[1] = controller.axes[3] # strafe right/left	# L/J

			# build action string list
			action_strs = []
			for action in action_list.actions:
				if action_list.actions[action].trigger():
					action_strs.append(action)

			# update the output message
			msg["movement"]["linear"] = lin_vec
			msg["movement"]["angular"] = ang_vec
			msg["actions"] = action_strs

			# publish the command string
			publisher.publish(msg)
			time.sleep(0.01)
			limiter.reset()

	 	# show the active window
		cv2.imshow("I'm a Window", blank)
		cv2.waitKey(1)
	cv2.destroyAllWindows()


