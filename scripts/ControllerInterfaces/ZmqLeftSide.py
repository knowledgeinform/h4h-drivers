import json

import commons.utils_lib as utils
import commons.simple_zmq_lib as zlib

from commons.h4h.controller_interface import ControllerSixDofBase


class UCCControllerInterface(ControllerSixDofBase):
	""" ZMQ-based control bridge """

	def __init__(self, zmq_topic:str, zmq_ipaddr:str):
		# init h4h parent
		super().__init__(name="UCCControllerInterface")

		# pull in the port number
		zmq_port = utils.getEnv("ZMQ_PORT")

		# create the subscriber and set the callback
		self.zmq_subscriber = zlib.SimpleZMQSubscriber(
			topic=zmq_topic,
			port=zmq_port,
			ip_address=zmq_ipaddr,
			callback=self.relayToRos
		)


		# TEMPORARY: FORMALIZE LATER
		# set up rising triggers for the actions coming from the UCC
		self.triggers = {}
		self.last_flight_mode = "NONE"
	
	def processActions(self, data:dict):

		# process the actions
		for action_str,value in data.items():
			# skip if action is called "name"
			if action_str == "name":
				continue
				
			# do a special thing for the flight mode
			if action_str == "flight_mode":
				if value != self.last_flight_mode:
					self.sendTriggerAction(value.lower())
				continue
				
			# add to the triggers list
			if not action_str in self.triggers:
				self.triggers[action_str] = False
			
			# trigger on rise
			if value:
				if not self.triggers[action_str]:
					self.sendTriggerAction(action_str)
				self.triggers[action_str] = True
			else:
				self.triggers[action_str] = False


		### SWITCH BACK TO BELOW IF THE DATA STRUCTURE IS FIXED

		# # process the actions
		# if "actions" in data:
		# 	for action_str,value in data["actions"].items():
		# 		# add to the triggers list
		# 		if not action_str in self.triggers:
		# 			self.triggers[action_str] = False
				
		# 		# trigger on rise
		# 		if value:
		# 			if not self.triggers[action_str]:
		# 				self.sendTriggerAction(action_str)
		# 			self.triggers[action_str] = True
		# 		else:
		# 			self.triggers[action_str] = False



	def processControl(self, data:dict):
		# copy axes over from data
		self.linear.x.update(float(data["linear_x"]))
		self.linear.y.update(float(data["linear_y"]))
		self.linear.z.update(float(data["linear_z"]))
		self.angular.z.update(float(data["angular_z"]))

	def relayToRos(self, msg):
		# print(">>>>>>>>>>>>>>>>>>>")
		# print("Message:")
		# print(msg)
		# print("<<<<<<<<<<<<<<<<<<<<")
		
		# load the json packet
		packet = msg["data"]
		data = packet["messageData"]
		self.logger.info(f"Received {packet}")

		# check for new vehicle target
		if self.target_vehicle != data["name"]:
			self.connectToVehicle(data["name"])

		# switch on message type
		if packet["messageType"] == "control":
			self.processControl(data)
		elif packet["messageType"] == "actions":
			self.processActions(data)

	def stop(self):
		pass


if __name__ == "__main__":
	# set up channel info
	zmq_topic = ""
	zmq_ipaddr = utils.getEnv("ZMQ_IP")

	# set up the repeater
	zmq_to_ros_repeater = UCCControllerInterface(zmq_topic, zmq_ipaddr)

	# run forever
	zmq_to_ros_repeater.spin()
