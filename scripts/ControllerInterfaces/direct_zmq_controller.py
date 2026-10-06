import commons.utils_lib as utils
import commons.simple_zmq_lib as zlib

from commons.h4h.controller_interface import ControllerSixDofBase


""" 
Incoming messages look like this:
{
	name: "VehicleName",
	movement: {
		"linear": [0.0, 0.0, 0.0]
		"angular": [0.0, 0.0, 0.0]
	}
	actions: ["ARM", "POSITION", "DO_A_THING"]
}
"""


class ZMQControllerInterface(ControllerSixDofBase):
	""" A more direct ZMQ-based control bridge """

	def __init__(self, zmq_ipaddr:str, zmq_port:str|int):
		# init h4h parent
		super().__init__(name="UCCControllerInterface")

		# pull in the port number
		zmq_port = utils.getEnv("ZMQ_PORT")

		# create the subscriber and set the callback
		self.zmq_subscriber = zlib.SimpleZMQSubscriber(
			port=zmq_port,
			ip_address=zmq_ipaddr,
			callback=self.relayToRos
		)

	def processActions(self, data:list):
		# process the actions
		for action_str in data:			
			self.sendTriggerAction(action_str)

	def processControl(self, data:dict):
		# copy axes over from data
		self.linear.update(data["linear"])
		self.angular.update(data["angular"])

	def relayToRos(self, msg):
		# check for new vehicle target
		if self.target_vehicle != msg["name"]:
			self.connectToVehicle(msg["name"])

		# switch on message type
		self.processControl(msg["movement"]) # dictionary of linear x,y,z and angular x,y,z
		self.processActions(msg["actions"]) # list of strings

if __name__ == "__main__":
	# get the connection info
	zmq_ipaddr = utils.getEnv("ZMQ_IP")
	zmq_port = utils.getEnv("ZMQ_PORT")

	# set up the repeater
	zmq_to_ros_repeater = ZMQControllerInterface(zmq_ipaddr, zmq_port)

	# run forever
	zmq_to_ros_repeater.spin()
