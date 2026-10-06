# boilerplate type hinting and clarity imports
from __future__ import annotations
import sys
if sys.version_info >= (3, 12):
	from typing import override 
else:
	from typing_extensions import override
from typing import Optional

import time

import commons.utils_lib as utils
import commons.thread_lib2 as tlib2

from commons.h4h.base import H4HBase, CommonActions, AbstractValueWrapper

from std_srvs.srv import Trigger

from h4h_msgs.msg import AbstractSignal, BatchedAbstractSignal


class Vector3:
	""" convenience struct for xyz axes """

	def __init__(self):
		self.x = AbstractValueWrapper(0.0)
		self.y = AbstractValueWrapper(0.0)
		self.z = AbstractValueWrapper(0.0)

		# wrap them in a list for iterators
		self.values = [self.x, self.y, self.z]

	def update(self, values:list):
		""" update x,y,z with each item in the values list """
		for a in range(3):
			self.values[a].update(values)

	def copy(self, other:Vector3):
		""" copies all the values from other """
		for a in range(3):
			self.values[a].update(other.values[a].getValue())

	def registerAbstractSignals(self, signal_list:[AbstractSignal,AbstractSignal,AbstractSignal]):
		""" maps xyz to abstract signals for easier output later """
		for a in range(3):
			self.values[a].updateAbstractSignal(signal_list[a])

	def getAbstractSignalMessages(self) -> [AbstractSignal,AbstractSignal,AbstractSignal]:
		""" 
		requires registerAbstractSignals() to be called prior 
		copies axis values over to their corresponding signal message
		"""
		message_list = []
		for a in range(3):
			message_list.extend(self.values[a].getMessage())
		return message_list

# class VehicleProfile:
# 	def __init__(self, name):
# 		self.name = name

# 		# assemble the topic
# 		self.publisher = self.create_publisher(
# 				msg_type = BatchedAbstractSignal,
# 				topic = self.assembleTopic(self.name, self.abstract_topic),
# 				qos_profile=self.qos_profile,
# 				callback_group=None)

# 	def assembleTopic(self, *args:str) -> str:
# 		""" 
# 		Assembles an absolute topic path from a variable list of topic string sections 
# 		"""
# 		topic_str = ""
# 		for arg in args:
# 			topic_str += "/"
# 			topic_str += arg
# 		return topic_str

class ControllerInterfaceBase(H4HBase):
	""" Abstract class for defining the controller-side interface for H4H """

	def __init__(self, name:str, override_namespace:Optional[str]=None):
		# init parent
		super().__init__(name, override_namespace)

		### GET ENVIRONMENT VARIABLES ###
		self.priority = 		utils.getEnv("PRIORITY", default=255) # default is weakest priority [0,255]
		self.control_rate = 	utils.getEnv("CONTROL_RATE_HZ", default=10)

		# set up a message with pre-set priority from environment variable
		self.msg = BatchedAbstractSignal()
		self.msg.priority = self.priority # lower is stronger

		# set up a BatchedAbstractSignal Publisher
		self.publisher = None
		self.publisher_cache = {}

		# currently controlled vehicle
		self.target_vehicle = "NO_VEHICLE_ASSIGNED"
		self.available_actions = []

		# spin up a control thread
		tlib2.threadForever(func=self.publish, rate_hz=self.control_rate)

	def assembleTopic(self, *args:str) -> str:
		""" 
		Assembles an absolute topic path from a variable list of topic string sections 
		"""
		topic_str = ""
		for arg in args:
			topic_str += "/"
			topic_str += arg
		return topic_str

	def requestVehicleActions(self) -> str:
		"""
		Sends a blocking request to the vehicle for a list of action services it responds to
		"""
		# set the request
		client = self.create_client(Trigger, self.assembleTopic(self.target_vehicle, CommonActions.GET_ACTION_LIST.value))
		future = client.call_async(Trigger.Request())
		
		# wait for response
		# may use future.add_done_callback(callback) in the future
		while not future.done():
			time.sleep(0.1)
		return future.result()

	def sendActionNoResponse(self, action_name:str, service_type:"ROS2 Service"):
		"""
		Sends a non-blocking ROS2 service call to the target vehicle 
		This function doesn't care about or wait for any response
		"""
		service_topic = self.assembleTopic(self.target_vehicle, action_name)
		print("Service Type:", service_type)
		print("Topic:", service_topic)
		client = self.create_client(service_type, service_topic)
		client.call_async(service_type.Request())

	def sendTriggerAction(self, action_name:str):
		""" 
		Sends a non-blocking ROS2 Trigger service call to the target vehicle 
		This function doesn't care about or wait for any response
		"""
		self.sendActionNoResponse(action_name, Trigger)
	
	def sendTriggerActionFiltered(self, action_name:str):
		"""
		Sends a non-blocking ROS2 Trigger service call 
		only if the target vehicle supports that action
		"""
		if action_name in self.available_actions:
			self.sendTriggerAction(action_name)
	
	def sendTriggerActionFilteredList(self, action_names:list[str]):
		"""
		Sends a non-blocking ROS2 Trigger service call for each action
		only if the target vehicle supports that action
		"""
		for action in action_names:
			self.sendTriggerActionFiltered(action)

	def connectToVehicle(self, vehicle_name:str):
		""" opens up a BatchedAbstractSignal publisher with the designated vehicle """
		# clear out the previous publisher
		if self.publisher is not None:
			if not self.target_vehicle in self.publisher_cache:
				self.publisher_cache[self.target_vehicle] = self.publisher
			hold = self.publisher
			self.publisher = None
			self.destroy_publisher(hold)

		# assign new target
		self.target_vehicle = vehicle_name

		# wait for capability list and parse
		self.logger.debug(f"Requesting Actions From: {self.target_vehicle}")
		action_list_str = self.requestVehicleActions().message # TODO: change the return type to something more formal
		actions_parse = action_list_str.split(",")
		self.available_actions = [action for action in actions_parse]

		# create a new publisher if not cached
		print("Connecting to", vehicle_name)
		if self.target_vehicle in self.publisher_cache:
			self.publisher = self.publisher_cache[self.target_vehicle]
			print("Connected with cache")
		else:
			print("connected fresh")
			self.publisher = self.create_publisher(
					msg_type = BatchedAbstractSignal,
					topic = self.assembleTopic(vehicle_name, self.abstract_topic),
					qos_profile=self.qos_profile,
					callback_group=None)


	def buildMessage(self):
		""" 
		updates and builds up the BatchedAbstractSignal control message

		Each inheritor should call super().buildMessage() at the start
		to chain the building of the BatchedAbstractSignal message
		"""
		
		# reset the messages signal list
		self.msg.signals = []

	def publish(self, priority:Optional[int]=None):
		""" 
		publishes control to our currently selected vehicle 
		"""

		# check if we're connected to anything
		if self.publisher is None:
			self.logger.debug("Not connected to any vehicle yet")
			return

		# build up the message
		self.buildMessage()

		# add in custom priority if defined
		if priority:
			self.msg.priority = priority
		else:
			self.msg.priority = self.priority

		# publish
		self.publisher.publish(self.msg)
		# self.logger.pub(self.msg, self.publisher.topic)


class ControllerSixDofBase(ControllerInterfaceBase):
	""" 
	base class for a controller that predefines six DOF output of Linear_XYZ and Angular_XYZ
	"""

	def __init__(self, name:str, override_namespace:Optional[str]=None):
		# init parent
		super().__init__(name, override_namespace)

		# set up linear and angular axes
		self.linear = Vector3()
		self.angular = Vector3()

		# assign AbstractSignals to vectors
		linear_signals = [AbstractSignal.FORWARD_BACKWARD,AbstractSignal.RIGHT_LEFT,AbstractSignal.UP_DOWN]
		self.linear.registerAbstractSignals(linear_signals)

		angular_signals = [AbstractSignal.ROLL,AbstractSignal.PITCH,AbstractSignal.YAW]
		self.angular.registerAbstractSignals(angular_signals)

	def setTwoAxis(self, forward:float, turn:float):
		""" directly sets the linear.x and angular.z axes """
		self.linear.x.update(forward) # TODO: try overriding __eq__ to make this nicer (but post a clear warning)
		self.linear.y.update(0.0)
		self.linear.z.update(0.0)

		self.angular.x.update(0.0)
		self.angular.y.update(0.0)
		self.angular.z.update(turn)

	def setVelocities(self, lin_vec3:Vector3, ang_vec3:Vector3):
		""" directly set 6DOF linear and angular axes """
		self.linear.copy(lin_vec3)
		self.angular.copy(ang_vec3)

	@override
	def buildMessage(self):
		""" 
		updates and builds up the BatchedAbstractSignal control message

		Each inheritor should call super().publish(priority) at the start
		to chain the building of the BatchedAbstractSignal message
		"""

		# call on parent's buildMessage
		super().buildMessage()

		# build our message
		self.msg.signals.extend(self.linear.getAbstractSignalMessages())
		self.msg.signals.extend(self.angular.getAbstractSignalMessages())


