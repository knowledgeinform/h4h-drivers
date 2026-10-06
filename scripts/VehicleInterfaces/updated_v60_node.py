# boilerplate type hinting and clarity imports
from __future__ import annotations
import sys
if sys.version_info >= (3, 12):
	from typing import override 
else:
	from typing_extensions import override

from std_msgs.msg import UInt32
from geometry_msgs.msg import Twist

# from RosToZmq import UgvStatusToZmq  

from commons.h4h.vehicle_interface import QuadrupedBase

class GhostVehicleControl(QuadrupedBase):
	""" Concrete interface for Ghost V60 control """

	def __init__(self):
		# init parent
		super().__init__(name="GhostVehicleControl")

		# define action map (derived from V60 outputs)
		self.action_map = {}
		self.action_map["sit"] 		= 0
		self.action_map["stand"] 	= 1
		self.action_map["walk"] 	= 2
		self.GHOST_TAKE_CONTROL_ID 	= 160 # V60's predefined takeover command ID

		# movement publisher
		self.move_msg = Twist()
		self.control_publisher = self.create_publisher(
				msg_type = Twist,
				topic = "/mcu/command/manual_twist",
				qos_profile=self.qos_profile,
				callback_group=None)
		
		# set up an action mode publisher
		self.action_msg = UInt32()
		self.action_publisher = self.create_publisher(
			msg_type=UInt32, 
			topic='/command/setAction',
			qos_profile=self.qos_profile,
			callback_group=None)

		# set up control authority publisher
		self.take_control_msg = UInt32()
		self.take_control_msg.data = self.GHOST_TAKE_CONTROL_ID
		
		self.authority_publisher = self.create_publisher(
			msg_type=UInt32, 
			topic="/command/setControlMode",
			qos_profile=self.qos_profile,
			callback_group=None)
		
		# start up runner thread
		self.start()


	@override
	def update(self):
		""" Publish out move control commands"""
		# update move values
		self.move_msg.linear = self.linear
		self.move_msg.angular = self.angular

		# publish control
		self.control_publisher.publish(self.move_msg)
		self.logger.info(f"Published Linear: {self.linear} Angular: {self.angular} to {self.control_publisher.topic}")

	@override
	def softStop(self) -> bool:
		""" Send a stop (as in stay in place) command to the vehicle """
		self.move_msg.linear = self.stop_vector
		self.move_msg.angular = self.stop_vector
		self.control_publisher.publish(self.move_msg)
		return True

	def publishStanceAction(self, action_str:str) -> bool:
		""" Helper func that publishes stance actions """
		self.action_msg.data = self.action_map[action_str]
		self.action_publisher.publish(self.action_msg)
		self.logger.info(f"Published {action_str} Mode to {self.action_publisher.topic_name}")
		return True

	@override
	def triggerActionSit(self) -> bool:
		""" Commands the quadriped to change stance to Sit """
		return self.publishStanceAction("sit")

	@override
	def triggerActionStand(self) -> bool:
		""" Commands the quadriped to change stance to Stand """
		return self.publishStanceAction("stand")
	
	@override
	def triggerActionWalk(self) -> bool:
		""" Commands the quadriped to change stance to Walk """
		return self.publishStanceAction("walk")

	@override
	def triggerActionTakeover(self) -> bool:
		""" Optional Action that sends a takeover command to the quadriped """
		# tells V60 to shift to "Autonomous Control" (ignores output from normal v60 controller app)
		self.authority_publisher.publish(self.take_control_msg)
		self.logger.info(f"Published TAKEOVER to {self.authority_publisher.topic_name}")
		return True

if __name__ == "__main__":
	# init the controller
	controller = GhostVehicleControl()
	controller.spin()

	# set ZMQ config 
	# zmq_port = 5564  # see port_numbering_scheme.md 

	# ugv_status_to_zmq = UgvStatusToZmq("rlac_v60", "", "", zmq_port, "/gx5/gnss1/fix")

