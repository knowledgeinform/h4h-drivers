import time
import rospy

import commons.simple_zmq_lib as zlib
import commons.rlac_comms_lib as rclib

import commons.utils_lib as utils

from iop_msgs.msg import SelfCollisionAvoidanceConfiguration

from resource_controller_msgs.msg import AxisCommand, Int32Command, BoolCommand

def sign(value):
	if value > 0:
		return 1
	elif value < 0:
		return -1
	return 0

class JointPublisher:
	def __init__(self, topic, limit, priority):
		self.limit = limit
		self.topic = topic
		self.priority = priority
		self.publisher = rospy.Publisher(self.topic, AxisCommand, queue_size=10)

		# pre-define a generic AxisCommand message
		self.msg = AxisCommand()
		self.msg.header.valid = True
		self.msg.type = AxisCommand.VELOCITY
		self.msg.header.priority = priority
		self.msg.header.lifespan_secs = 0.30

	# assume normalized input [-1,1]
	def publishNorm(self, value):
		value *= self.limit
		self.publish(value)

	def publish(self, value):
		# clamp to limit
		if abs(value) > self.limit:
			value = self.limit * sign(value)

		# update command message
		self.msg.header.timestamp = rospy.get_rostime()
		self.msg.command = value

		# publish out
		self.publisher.publish(self.msg)

class MTRSArmDriver:
	def __init__(self, topic_scale_map, msg_priority):
		# set up the joint publishers
		self.arm_publishers = []
		for topic in topic_scale_map:
			scale_value = topic_scale_map[topic]
			self.arm_publishers.append(JointPublisher(topic, scale_value, msg_priority))

	def processArmCommand(self, command):
		# set order for commands
		commands = []
		commands.append(command.linear.y) # turret
		commands.append(command.linear.x) # shoulder
		commands.append(command.linear.z) # elbow
		# commands.append(command.angular.z) # wrist
		commands.append(0.0) # wrist
		commands.append(0.0) # roll
		commands.append(command.angular.z) # grip

		# fill in the rest with zeros
		while len(commands) < len(self.arm_publishers):
			commands.append(0)

		# publisher all the commands
		for a in range(len(self.arm_publishers)):
			self.arm_publishers[a].publishNorm(commands[a])
			time.sleep(0.001) # IMPORTANT: back-to-back messages with no sleep sometimes get lost

class MTRSGripperArmDriver(MTRSArmDriver):
	def __init__(self, msg_priority):
		# hard-code the topic names for now
		turret_topic = 		"/kamino_manipulator_driver/resource/turret/set_command"
		shoulder_topic = 	"/kamino_manipulator_driver/resource/shoulder/set_command"
		elbow_topic = 		"/kamino_manipulator_driver/resource/elbow/set_command"
		wrist_topic = 		"/kamino_manipulator_driver/resource/wrist/set_command"
		roll_topic = 		"/kamino_manipulator_driver/resource/roll/set_command"
		grip_topic = 		"/kamino_manipulator_driver/resource/grip/set_command"

		# build up control map # relative values observed from controller input
		topic_map = {}
		topic_map[turret_topic] = 0.1
		topic_map[shoulder_topic] = 0.1
		topic_map[elbow_topic] = 0.1
		topic_map[wrist_topic] = 0.05
		topic_map[roll_topic] = 0.4
		topic_map[grip_topic] = 0.2

		# init parent
		super().__init__(topic_map, msg_priority)

class MTRSChassisDriver:
	def __init__(self, msg_priority, max_drive_effort):
		# hard-code the topic names for now
		gear_topic = 		"/kamino/kamino_chassis_driver/resource/gearbox/set_command"
		rotate_topic = 		"/kamino/chassis/kamino_chassis_driver/resource/rotate/set_command"
		translate_topic = 	"/kamino/chassis/kamino_chassis_driver/resource/translate/set_command"
		brake_topic = 		"/kamino/chassis/kamino_chassis_driver/resource/chassis_brake/set_command"

		# init ros1
		self.rotate_publisher = rospy.Publisher(rotate_topic, AxisCommand, queue_size=10)
		self.translate_publisher = rospy.Publisher(translate_topic, AxisCommand, queue_size=10)
		self.gear_publisher = rospy.Publisher(gear_topic, Int32Command, queue_size=10)
		self.brake_publisher = rospy.Publisher(brake_topic, BoolCommand, queue_size=10)

		# disable collision avoidance
		self.collision_publisher = rospy.Publisher(
			"/kamino/collision_avoidance/cmd", 
			SelfCollisionAvoidanceConfiguration,
			queue_size=5)
		
		self.collision_msg = SelfCollisionAvoidanceConfiguration()
		self.collision_msg.state = 0
		self.collision_msg.priority = 0
		self.collision_msg.status = 0

		# copy drive effort
		self.max_drive_effort = max_drive_effort

		# publish out an initial set-gear command
		gear_msg = Int32Command()
		gear_msg.header.valid = True
		gear_msg.command = 0
		self.gear_publisher.publish(gear_msg)

		self.translate_msg = AxisCommand()
		self.translate_msg.type = AxisCommand.EFFORT
		self.translate_msg.header.valid = True
		self.translate_msg.header.priority = msg_priority
		self.translate_msg.header.lifespan_secs = 0.50

		self.rotate_msg = AxisCommand()
		self.rotate_msg.type = AxisCommand.EFFORT
		self.rotate_msg.header.valid = True
		self.rotate_msg.header.priority = msg_priority
		self.rotate_msg.header.lifespan_secs = 0.50

	def printOutMessage(self, msg:"Any_ROS_Message"):
		""" Debug func that serves as a ROS Callback that prints out the received message """
		print("!!!!!!!!!!!!!!!!")
		print("Debug Message:")
		print(msg)
		print("!!!!!!!!!!!!!!!!")


	def processChassisCommand(self, command):
		# get timestamp
		now = rospy.get_rostime()

		# send a drive command
		self.translate_msg.header.timestamp = now
		self.translate_msg.command = command.linear.x * self.max_drive_effort

		print("Sending Translate:", self.translate_msg)
		self.translate_publisher.publish(self.translate_msg)
		time.sleep(0.001) # IMPORTANT: back-to-back messages with no sleep sometimes get lost

		# send a turn command
		self.rotate_msg.header.timestamp = now
		self.rotate_msg.command = command.angular.z * self.max_drive_effort

		print("Sending Rotate:", self.rotate_msg)
		self.rotate_publisher.publish(self.rotate_msg)
		time.sleep(0.001) # IMPORTANT: back-to-back messages with no sleep sometimes get lost

		self.collision_publisher.publish(self.collision_msg)
		time.sleep(0.001) # IMPORTANT: back-to-back messages with no sleep sometimes get lost



class MTRSDriver:
	def __init__(self, zmq_topic, msg_priority, max_drive_effort):
		# set up part drivers
		self.chassis_driver = MTRSChassisDriver(msg_priority, max_drive_effort)
		self.gripper_driver = MTRSGripperArmDriver(msg_priority)

		# pull zmq ports from env
		GRIPPER_PORT = utils.getEnv("ZMQ_GRIPPER_PORT")
		CHASSIS_PORT = utils.getEnv("ZMQ_CHASSIS_PORT")

		# pull names from env
		self.GRIPPER_NAME = utils.getEnv("GRIPPER_NAME")
		self.CHASSIS_NAME = utils.getEnv("CHASSIS_NAME")

		# connect to the brake topic
		brake_topic = "/kamino/chassis/kamino_chassis_driver/resource/chassis_brake/set_command"
		self.brake_publisher = rospy.Publisher(brake_topic, BoolCommand, queue_size=10)

		# set up brake message
		self.brake_msg = BoolCommand()
		self.brake_msg.header.valid = True
		self.brake_msg.header.priority = msg_priority
		self.brake_msg.header.lifespan_secs = 0.25
		self.brake_msg.command = False # set Brake to OFF

		# set up separate links for chassis and gripper
		self.chassis_sub = zlib.SimpleZMQSubscriber(
			topic=zmq_topic,
			port=CHASSIS_PORT,
			ip_address="127.0.0.1",
			callback=self.processCommand
		)

		self.gripper_sub = zlib.SimpleZMQSubscriber(
			topic=zmq_topic,
			port=GRIPPER_PORT,
			ip_address="127.0.0.1",
			callback=self.processCommand,
		)


	def processCommand(self, msg):
		# parse the json command
		print("Got Message:", msg)
		command = rclib.fromRlacJsonControlCommand(msg["data"])

		# send the brake OFF command
		self.brake_publisher.publish(self.brake_msg)
		time.sleep(0.001) # IMPORTANT: back-to-back messages with no sleep sometimes get lost

		# split the send based on name
		if command.name == self.CHASSIS_NAME:
			self.chassis_driver.processChassisCommand(command)
		elif command.name == self.GRIPPER_NAME:
			self.gripper_driver.processArmCommand(command)


if __name__ == "__main__":
	# init ROS1
	rospy.init_node("ZMQMtrsDriver", anonymous=True)

	# network params
	zmq_topic = ""
	priority = 			utils.getEnv("PRIORITY", cast=int) # this is the priority for the MTRS control message
	max_drive_effort = 	utils.getEnv("MAX_EFFORT", cast=int) # 30 is the max of what the controller puts out

	# start up the driver
	driver = MTRSDriver(
		zmq_topic=zmq_topic,
		msg_priority=priority,
		max_drive_effort=max_drive_effort)

	# idle
	while True:
		time.sleep(0.1)


