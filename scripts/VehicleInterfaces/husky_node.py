# boilerplate type hinting and clarity imports
from __future__ import annotations
import sys
if sys.version_info >= (3, 12):
	from typing import override 
else:
	from typing_extensions import override

from geometry_msgs.msg import Twist
from commons.h4h.vehicle_interface import UGVBase


# right-side controller for the Husky
class HuskyController(UGVBase):
	""" Vehicle Interface for the Husky robot (and most other Clearpath robots) """
	def __init__(self):
		# init parent
		super().__init__(name="HuskyController")

		# set up a cmd_vel publisher
		self.publisher = self.create_publisher(
				msg_type = Twist,
				topic = "/cmd_vel",
				qos_profile=self.qos_profile,
				callback_group=None)

		# predefine Twist
		self.msg = Twist()
		
		# start control loop
		self.start()

	# publish out control
	@override
	def update(self):
		# update values
		self.msg.linear.x = self.linear.x
		self.msg.angular.z = self.angular.z

		# publish
		self.publisher.publish(self.msg)
		self.logger.info(f"Published Linear: {self.msg.linear.x} Angular: {self.msg.angular.z} to {self.publisher.topic}")
	
	@override
	def softStop(self) -> bool:
		""" Send a stop (as in stay in place) command to the vehicle """
		# zero out the message
		self.msg.linear = self.stop_vector
		self.msg.angular = self.stop_vector

		# publish
		self.publisher.publish(self.msg)
		return True


if __name__ == "__main__":
	# init the controller
	controller = HuskyController()
	controller.spin()