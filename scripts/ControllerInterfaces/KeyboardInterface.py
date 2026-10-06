import cv2

import commons.utils_lib as utils
from commons.h4h.controller_interface import ControllerSixDofBase

from commons.input_lib import WasdIjklController

class KeyboardControllerInterface(ControllerSixDofBase):
	""" Direct Keyboard Controller Interface """

	def __init__(self):
		# init h4h parent
		super().__init__(name="KeyboardControllerInterface")

		# set action strings
		action_triggers = {}
		action_triggers["arm"] = utils.RisingTrigger()
		action_triggers["disarm"] = utils.RisingTrigger()
		action_triggers["take_control"] = utils.RisingTrigger()

		# set up controller
		controller = WasdIjklController()
		controller.addKey("arm", 'm')
		controller.addKey("disarm", 'n')
		controller.addKey("take_control", 'p')


	def processControl(self, data:dict):
		# check for new vehicle target
		if self.target_vehicle != data["name"]:
			self.connectToVehicle(data["name"])

		# copy axes over from data
		self.linear.x = float(data["linear_x"])
		self.linear.y = float(data["linear_y"])
		self.linear.z = float(data["linear_z"])
		self.angular.z = float(data["angular_z"])

		# process the actions
		if "actions" in data:
			for action_str,value in data["actions"].items():
				if value:
					self.sendTriggerAction(action_str)

	def relayToRos(self, msg):
		if len(msg) < 10:
			return
		
		# load the json packet
		packet = json.loads(msg)
		data = packet["messageData"]
		self.logger.info(f"Received {packet}")

		# switch on message type
		if packet["messageType"] == "control":
			self.processControl(data)

	# halts the zmq receivers
	def stop(self):
		for zmq_sub in self.zmq_subscribers:
			zmq_sub.stop()


if __name__ == "__main__":
	# set up channel info
	zmq_topic = ""
	zmq_ipaddr = utils.getEnv("ZMQ_IP")

	# set up the repeater
	zmq_to_ros_repeater = UCCControllerInterface(zmq_topic, zmq_ipaddr)

	# run forever
	zmq_to_ros_repeater.spin()
