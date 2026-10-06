# boilerplate type hinting and clarity imports
from __future__ import annotations
import sys
if sys.version_info >= (3, 12):
	from typing import override 
else:
	from typing_extensions import override
from abc import abstractmethod
from collections.abc import Callable
from typing import Any, Optional

import time
from enum import Enum

import rclpy
from rclpy.node import Node

import commons.ros2_lib2 as rlib2
import commons.utils_lib as utils
from commons.logger_lib import logger

from h4h_msgs.msg import AbstractSignal


class CommonActions(Enum):
	# All Vehicles
	GET_ACTION_LIST =	"get_available_actions"

	# Mavlink
	ARM =				"arm"
	DISARM =			"disarm"

	# UAVs
	LAND =				"land"
	TAKEOFF =			"takeoff"
	POSITION = 			"position"
	HOLD = 				"hold"
	OFFBOARD = 			"offboard"
	STABILIZE =			"stabilized"
	MANUAL =			"manual"
	ALTITUDE =			"altitude"


	# Quadripeds
	SIT = 				"sit"
	STAND =				"stand"
	WALK =				"walk"
	TAKE_CONTROL =		"take_control"

class AbstractValueWrapper:
	""" Wraps a specific value in an OnChangeNotifier and manages the message output """
	def __init__(self, value:Any, signal:AbstractSignal=AbstractSignal.NOOP, stale_limit:int=3):
		self.value_notifier = OnChangeNotifier(value, stale_limit=stale_limit)
		self.msg = AbstractSignal()
		self.msg.signal = signal

		# mirror through the update call from OnChangeNotifier
		self.update = self.value_notifier.update
	
	def getValue(self):
		""" Digs down and returns the underlying value in the OnChangeNotifier """
		return self.value_notifier.value
	
	def updateAbstractSignal(self, signal:AbstractSignal):
		self.msg.signal = signal
	
	def getMessage(self) -> list[AbstractSignal]:
		""" 
		Returns the message wrapped in a list so that 
		the caller can use list extension to manage empty lists. 
		Returns an empty list if the tracked value has gone stale.
		"""
		message_list = []
		if self.value_notifier.checkFresh():
			self.msg.value = self.value_notifier.value
			message_list.append(self.msg)
		return message_list

class OnChangeNotifier:
	""" 
	A simple class that detects changes in its tracked value.
	value:Any = the value to be tracked
	stale_limit:int = how many times to send a non-changed value before stopping
	"""
	def __init__(self, value:Any, stale_limit:int=3):
		self.value = value
		self.stale_limit = stale_limit
		self.counter = 0 # counts how many times we've sent a stale message
		self.fresh = True
	
	def checkFresh(self) -> bool:
		""" 
		Increments the counter if not fresh. Returns True if the counter is less than
		"""
		# check freshness
		if self.fresh:
			self.fresh = False
			self.counter = 0
		else:
			self.counter += 1
		
		# check if we've exceeded the replay count
		return self.counter < self.stale_limit

	def update(self, value:Any):
		""" 
		If: the incoming value is different, reset self.counter to zero
		"""
		# update counter
		if self.value != value:
			self.counter = 0
		else:
			self.counter += 1
		self.value = value




class H4HBase(Node):
	""" Abstract base class that defines in-common standards for all H4H ROS nodes """

	def __init__(self, name:str, override_namespace:Optional[str]=None):
		# pull the ROS namespace
		if override_namespace is None:
			self.namespace = utils.getEnv("ROS_NAMESPACE", default="h4h")
		else:
			self.namespace = override_namespace

		# set up Node
		self.name = name
		super().__init__(self.name, namespace=self.namespace)

		# predefine the name of the core topic
		self.abstract_topic = "batched_abstract_signal"

		# predefine a default Quality-of-Service (QOS) profile
		self.qos_profile = rclpy.qos.QoSProfile(
			reliability=rclpy.qos.QoSReliabilityPolicy.BEST_EFFORT, 
			depth=10)

		# register self with the MultithreadedExecutor
		rlib2.addNodeToExec(self)

		# set up the logger
		self.logger = logger

		# announce namespace
		self.logger.info(f"Initialized with namespace {self.namespace}")

	def spin(self):
		""" Convenience keepalive func for interfaces that don't need any additional event loop actions. """
		while True:
			time.sleep(9999)