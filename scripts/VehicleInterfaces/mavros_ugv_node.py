import time

import commons.h4h_lib as hlib
import commons.ros2_lib as rlib
import commons.utils_lib as utils

from mavros_msgs.msg import ManualControl
from RosToZmq import MavStatusToZmq  

# ros2 topic pub /mavros/manual_control/send mavros_msgs/msg/ManualControl "{x:0, y:0, z:1000, r:0, buttons: 0}"

# -z is forward # WARNING: this is negative z
# +y is right

class MavrosControlPublisher(rlib.RosPublisher):
	def __init__(self, topic, namespace=None):
		super(). __init__(
			node_name = "MavrosControlPublisher",
			msg_type = ManualControl,
			rostopic = topic,
			namespace = namespace)

	def publish(self, msg):
		self.publisher.publish(msg)

class MavrosUGVControl(hlib.SixDofVehicleBase):
	def __init__(self):
		# init parent
		super().__init__(name="MavrosUGVControl")

		# pull in environment vars
		self.control_topic = utils.getEnv("MAVROS_CONTROL_TOPIC", "/mavros/manual_control/send")
		self.max_speed = utils.getEnv("MAX_SPEED_INPUT", 500) # [0, 1000]
		self.max_turn = utils.getEnv("MAX_TURN_INPUT", 500) # [0, 1000]

		# set up base message
		self.mavcontrol_msg = ManualControl()

		# set up publisher
		self.control_publisher = MavrosControlPublisher(topic=self.control_topic)

		# start runner thread
		self.start()

	def update(self):
		# scale controls
		throttle = self.max_speed * self.linear.x
		turn = self.max_turn * self.angular.z

		# update message
		self.mavcontrol_msg.z = -throttle # negative z is forwards
		self.mavcontrol_msg.y = -turn # traxxis turns clockwise

		# publish
		self.control_publisher.publish(self.mavcontrol_msg)
		self.logger.info(f"Sent Throttle: {throttle} Turn: {turn} to {self.control_topic}")


if __name__ == "__main__":
	# init the controller
	controller = MavrosUGVControl()

	# setup ZMQ streamer for status  
	zmq_port = 5565  # see port_numbering_scheme.md 
	ugv_status_to_zmq = MavStatusToZmq("", "", zmq_port, "rlac_mavros", "/mavros/global_position/global")

	# idle
	while True:
		time.sleep(1.0)

	# close ros context 
	# (not currently reachable, but here in case we add a shutdown signal)
	controller.shutdown()
