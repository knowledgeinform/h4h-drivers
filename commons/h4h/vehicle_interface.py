# boilerplate type hinting and clarity imports
from __future__ import annotations
import sys

if sys.version_info >= (3, 12):
	from typing import override 
else:
	from typing_extensions import override
from abc import abstractmethod
from collections.abc import Callable
from typing import Optional

import time
import inspect

# import commons.mav_lib as mavlib # this import is deferred to stop every vehicle from needing pymavlink
import commons.ros2_lib2 as rlib2
import commons.utils_lib as utils
import commons.thread_lib2 as tlib2

from commons.h4h.base import H4HBase, CommonActions
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, CallbackGroup

from std_srvs.srv import Trigger
from geometry_msgs.msg import Vector3
from h4h_msgs.msg import AbstractSignal, BatchedAbstractSignal




def triggerActionWrapper(callback:Callable[...,bool]):
	""" 
	simplification ros service method wrapper that converts 
		func() -> bool
	into
		func(Trigger.Request, Trigger.Response) -> Trigger.Response
	"""

	def wrapper(request:"Trigger.Request()", response:"Trigger.Response()") -> "Trigger.Response()":
		# execute trigger callback
		response.success = callback()
		return response

	return wrapper

class MavlinkBaseMixin:
	""" 
	Mixin class that handles connection to a Mavlink vehicle
	"""

	def initMavlink(self, interface:VehicleInterfaceBase):
		# get generic mavlink environment variables
		self.address = 			utils.getEnv("MAV_ADDRESS")						# either the IP address or the serial address
		self.baudrate = 		utils.getEnv("BAUDRATE", default=57600) 		# only needed for direct serial connections
		self.max_horiz_spd = 	utils.getEnv("MAX_HORIZ_SPEED", default=1000) 	# [0, 1000]
		self.max_turn_spd = 	utils.getEnv("MAX_TURN_SPEED", default=1000) 	# [0, 1000]

		# connect to the vehicle
		self.driver = None # commons.mav_lib.ArduManualBase inheritor
		self.connectToVehicle() # <- function that connects to a vehicle and writes to self.driver

		# set callback groups
		# this callback group forces arm/disarm actions to process in-order
		self.arm_disarm_cb_group = MutuallyExclusiveCallbackGroup()

		# generic mavlink actions
		interface.registerTriggerAction(CommonActions.ARM.value, self.triggerActionArm, callback_group=self.arm_disarm_cb_group)
		interface.registerTriggerAction(CommonActions.DISARM.value, self.triggerActionDisarm, callback_group=self.arm_disarm_cb_group)

	@abstractmethod
	def connectToVehicle(self):
		""" sets self.driver to a mavlink connection to the vehicle """
		raise NotImplementedError

	def triggerActionArm(self) -> bool:
		""" tells the mavlink vehicle to arm """
		if self.driver:
			return self.driver.arm()
		return False

	def triggerActionDisarm(self) -> bool:
		""" tells the mavlink vehicle to disarm """
		if self.driver:
			return self.driver.disarm()
		return False

class MavlinkMultirotorMixin(MavlinkBaseMixin):
	""" 
	Mixin class that adds Multirotor UAV-specific parameters and functions
	"""
	def initMavlink(self, interface:VehicleInterfaceBase):
		# pull in environment vars
		self.max_vert_spd =		utils.getEnv("MAX_VERT_SPEED", default=500) 	 # [0, 500] 	# for multirotor UAVs
		self.is_px4 = 			utils.getEnv("FLIGHT_CONTROL_IS_PX4", cast=bool) # (True,False) # PX4 or Ardupilot

		# init parent after environment variables are queried
		super().initMavlink(interface)

		# set callback groups
		# this callback group makes mode changes execute in-order
		# (currently only have one mode change option so this isn't necessary)
		self.mode_change_cb_group = MutuallyExclusiveCallbackGroup()

		# UAV actions
		# sets to a direct control mode (POSITION mode for PX4, LOITER mode for Ardupilot)
		interface.registerTriggerAction(CommonActions.POSITION.value, self.triggerActionPositionMode, callback_group=self.mode_change_cb_group)
		interface.registerTriggerAction(CommonActions.HOLD.value, self.triggerActionHoldMode, callback_group=self.mode_change_cb_group)
		interface.registerTriggerAction(CommonActions.OFFBOARD.value, self.triggerActionOffboardMode, callback_group=self.mode_change_cb_group)
		interface.registerTriggerAction(CommonActions.MANUAL.value, self.triggerActionManualMode, callback_group=self.mode_change_cb_group)
		interface.registerTriggerAction(CommonActions.STABILIZE.value, self.triggerActionStabilizedMode, callback_group=self.mode_change_cb_group)
		interface.registerTriggerAction(CommonActions.ALTITUDE.value, self.triggerActionAltitudeMode, callback_group=self.mode_change_cb_group)

	@override
	def connectToVehicle(self):
		""" sets self.driver to a mavlink connection to the vehicle """
		from commons.mav_lib import ArduManualUAVDrive
		self.driver = ArduManualUAVDrive(
			mav_address=	self.address,
			baud=			self.baudrate,
			strafe_spd=		self.max_horiz_spd,
			turn_spd=		self.max_turn_spd,
			rise_spd=		self.max_vert_spd,
			is_px4=			self.is_px4
		)

	@abstractmethod
	def triggerActionPositionMode(self) -> bool:
		""" switches the vehicle over to a gps-enabled manual teleop flight mode """
		if self.driver:
			self.driver.processCommand("POSITION")
			return True # processCommand() doesn't return any confirmation right now
		return False

	@abstractmethod
	def triggerActionHoldMode(self) -> bool:
		""" switches the vehicle over to a gps-enabled hold-in-place mode """
		if self.driver:
			self.driver.processCommand("HOLD")
			return True # processCommand() doesn't return any confirmation right now
		return False

	@abstractmethod
	def triggerActionOffboardMode(self) -> bool:
		""" switches the vehicle over to an autonomous waypoint flight mode """
		if self.driver:
			self.driver.processCommand("OFFBOARD")
			return True # processCommand() doesn't return any confirmation right now
		return False

	@abstractmethod
	def triggerActionStabilizedMode(self) -> bool:
		""" switches the vehicle over to a no-gps manual teleop flight mode """
		if self.driver:
			self.driver.processCommand("STABILIZED")
			return True # processCommand() doesn't return any confirmation right now
		return False

	@abstractmethod
	def triggerActionManualMode(self) -> bool:
		""" switches the vehicle over to a no-gps manual teleop flight mode """
		if self.driver:
			self.driver.processCommand("MANUAL")
			return True # processCommand() doesn't return any confirmation right now
		return False

	@abstractmethod
	def triggerActionAltitudeMode(self) -> bool:
		""" switches the vehicle over to a manual teleop flight mode with altitude keeping"""
		if self.driver:
			self.driver.processCommand("ALTITUDE")
			return True # processCommand() doesn't return any confirmation right now
		return False



class VehicleInterfaceBase(H4HBase):
	""" 
	Abstract class for defining common interface of all H4H vehicles 

	Note: Inheritors must call self.start() after finishing their __init__()
	"""

	def __init__(self, name:str, override_namespace:Optional[str]=None):
		# init parent
		super().__init__(name=name, override_namespace=override_namespace)

		### Start of ENV vars ###

		# how often the control message is sent
		self.control_hz: float = utils.getEnv("CONTROL_UPDATE_RATE_HZ", default=10.0) 

		# how long until a controller's priority lock dies after receiving no messages from that controller
		self.priority_lifespan = utils.getEnv("CONTROL_PRIORITY_LIFESPAN_SEC", default=0.5) 

		# how long since last control message until we trigger a failsafe behavior (mostly just sending a stop command)
		self.failsafe_timeout_sec = utils.getEnv("FAILSAFE_TIMEOUT_SEC", default=3.0)
		self.failsafe_poll_hz = utils.getEnv("FAILSAFE_POLL_RATE", default=1.0) # how often we check for the failsafe trigger
		self.failsafe_disable_flag = utils.getEnv("DISABLE_FAILSAFE", default=True)

		self.last_control_msg_time = time.time()
		self.failsafe_once_flag = False # so that we only trigger the failsafe once, not repeatedly

		### End of ENV vars ###

		# set up heartbeat registration link
		# self.registration = RegistrationLink(name=self.namespace) # self.namespace is derived from H4HBase
		
		# set up the subscriber on its own callback group 
		# (all incoming control messages are processed in-order)
		self.abstract_signal_group = MutuallyExclusiveCallbackGroup()
		self.abstract_signal_subscriber = self.create_subscription(
			msg_type=BatchedAbstractSignal,
			topic="batched_abstract_signal",
			callback=self._batchCallback,
			qos_profile=self.qos_profile,
			callback_group=self.abstract_signal_group)


		# create a ros service that responds with a list of this vehicle's actions
		# starting with Trigger type for now, switch to custom type later
		self.actions = {}
		self.registerAction(CommonActions.GET_ACTION_LIST.value, Trigger, self.serveActionList)

		# message priority
		self.priority_watermark = 255 # [0-255] # lower is stronger
		self.priority_timer = utils.Timer()

	def _run(self):
		""" 
		This function repeats at a rate of self.control_hz.
		It calls on update(), but adds a failsafe timeout check before calling update().
		"""
		# check for failsafe bypass
		if self.failsafe_disable_flag:
			self.update()
			return
		
		# check failsafe or stop conditions

		# control message timeout failsafe
		if (time.time() - self.last_control_msg_time) > self.failsafe_timeout_sec:
			return
		
		# passed all checks, finally call update to allow normal control
		self.update()

	@abstractmethod
	def update(self):
		""" 
		This function repeats at a rate of self.control_hz and 
		dictates how messages are translated to the target vehicle.
		It is called by run() so long as we haven't triggered a failsafe flag.
		"""	
		raise NotImplementedError

	@abstractmethod
	def callback(self, msg:AbstractSignal):
		"""
		Processes individual AbstractSignal messages.
		Each inheritor should call super().callback(msg) to chain the decoding of AbstractSignals.
		"""
		pass


	def _batchCallback(self, msg:BatchedAbstractSignal):
		"""
		Processes BatchedAbstractSignal messages.
		It tracks the priority of incoming messages and filters the response
		before sending it down to the inheritor's definition of callback()
		"""

		# skip if the message empty
		if len(msg.signals) == 0:
			return

		self.logger.info(f"Got Message: {msg}")

		# refresh the last message time tracker
		now = time.time()
		self.last_control_msg_time = now
		self.failsafe_once_flag = False

		# check for priority expiration
		if self.priority_timer.totalTime() > self.priority_lifespan:
			self.priority_watermark = 256
			self.priority_timer.reset()

		# check for priority washout (lower is stronger)
		if self.priority_watermark < msg.priority:
			msg.signals = []
			return

		# update priority
		self.priority_watermark = msg.priority
		self.priority_timer.reset()

		# process each AbstractSignal in signals list
		for signal in msg.signals:
			self.callback(signal)

	def start(self):
		""" Launches the control thread that calls run() forever """
		# set up control loop
		tlib2.threadForever(func=self._run, rate_hz=self.control_hz)

		# set up failsafe loop
		if not self.failsafe_disable_flag:
			tlib2.threadForever(func=self.checkAndTriggerFailsafes, rate_hz=self.failsafe_poll_hz)
	
	def checkAndTriggerFailsafes(self):
		""" Runs the various failsafe checks and triggers failsafe() if any of them fail """
		# check for the control message timeout failsafe
		now = time.time()
		dt = now - self.last_control_msg_time
		if dt > self.failsafe_timeout_sec and not self.failsafe_once_flag:
			# print warning
			self.failsafe_once_flag = True
			self.logger.warning(f"!!! Haven't heard control in {self.failsafe_timeout_sec} seconds. Triggering failsafe !!!")
			self.logger.warning(f"!!! Last message heard {dt} seconds ago !!!")
			self.failsafe()
			return

	@abstractmethod
	def failsafe(self) -> bool:
		""" Failsafe command that triggers automatically after FAILSAFE_TIMEOUT_SEC seconds without control input """
		raise NotImplementedError
	
	@abstractmethod
	def softStop(self) -> bool:
		""" Send a stop (as in stay in place) command to the vehicle """
		raise NotImplementedError

	def serveActionList(self, request:"Service Request", response:"Service Response") -> "Service Response":
		"""
		Service callback for CommonActions.GET_ACTION_LIST  
		which returns the list of actions this vehicle responds to.

		The request arg is empty.
		"""
		# return the list as a string for now
		response_str = ""
		for action in self.actions:
			response_str += action + ","

		response.message = response_str
		response.success = True
		return response

	def registerAction(
		self, 
		action_name:str, 
		service_type:"ROS2 Service",
		callback:Callable[["Service.Request()", "Service.Response()"], "Service.Response()"],
		callback_group:CallbackGroup=None):

		"""
		Registers a new action with the list and creates a corresponding ROS2 service.
		If no callback_group is specified then the concurrency group is used by default.
		This allows this service to run concurrently with itself and other registered services.	
		"""

		# use the concurrent callbackgroup of None specified
		if callback_group is None:
			callback_group = rlib2.g_concurrent_callbackgroup

		# create the service
		# this persists even if we don't store it somewhere
		service = self.create_service(service_type, action_name, callback, callback_group=callback_group)

		# create an info string for the action list
		callback_info = self.__class__.__name__ + "." + callback.__name__
		callback_info += str(inspect.signature(callback)) # can also get docstring if desired		

		# register it on the list
		self.actions[action_name] = callback_info


	def registerTriggerAction(self, action_name:str, callback:Callable[[], bool], callback_group:CallbackGroup=None):
		"""
		Registers a new Trigger action with the list and creates a corresponding ROS2 Trigger service.
		If no callback_group is specified then the concurrency group is used by default.
		This allows this service to run concurrently with itself and other registered services.
		"""
		self.registerAction(action_name, Trigger, triggerActionWrapper(callback), callback_group)


class SixDofVehicleBase(VehicleInterfaceBase):
	"""
	Decodes 6-DOF Linear-XYZ and Angular-XYZ movement axes
	"""

	def __init__(self, name:str, override_namespace:Optional[str]=None):
		# init parent
		super().__init__(name=name, override_namespace=override_namespace)

		# movement vars
		self.linear = Vector3() # these are ROS2 geometry.msgs for convenience
		self.angular = Vector3()

		# keep a set of zeros for stop commands
		self.stop_vector = Vector3()

	def resetLinAng(self):
		""" convenience function for resetting axes to all zeros """
		self.linear.x = 0
		self.linear.y = 0
		self.linear.z = 0

		self.angular.x = 0
		self.angular.y = 0
		self.angular.z = 0


	@override
	def callback(self, msg:AbstractSignal):
		# pass message to parent
		super().callback(msg)

		# forward/backwards
		if msg.signal == AbstractSignal.FORWARD_BACKWARD:
			self.linear.x = msg.value

		# left/right
		elif msg.signal == AbstractSignal.RIGHT_LEFT:
			self.linear.y = msg.value

		# up/down
		elif msg.signal == AbstractSignal.UP_DOWN:
			self.linear.z = msg.value

		# pitch
		elif msg.signal == AbstractSignal.ROLL:
			self.angular.x = msg.value

		# roll
		elif msg.signal == AbstractSignal.PITCH:
			self.angular.y = msg.value

		# yaw
		elif msg.signal == AbstractSignal.YAW:
			self.angular.z = msg.value

class MultirotorUAVBase(SixDofVehicleBase):
	"""
	Generic multirotor UAV base. Adds Takeoff/Land actions
	"""
	def __init__(self, name:str, override_namespace:Optional[str]=None):
		# init parent
		super().__init__(name=name, override_namespace=override_namespace)

		# Multirotor environment variables
		self.takeoff_height_m = utils.getEnv("TAKEOFF_HEIGHT_METERS", default=5.0)
		self.failsafe_behavior = utils.getEnv("FAILSAFE_BEHAVIOR", default="none") # land, hover, rtl, none
		
		# verifiy valid behavior
		if not self.failsafe_behavior in ["land","hover","rtl","none"]:
			self.logger.error(f"Invalid FAILSAFE_BEHAVIOR param {self.failsafe_behavior}")
			raise ValueError

		# put autonomous flight actions on non-parallel callback group
		self.autonomous_action_cb_group = MutuallyExclusiveCallbackGroup()

		# register autonomous mode actions
		self.registerTriggerAction(CommonActions.LAND.value, self.triggerActionLand, callback_group=self.autonomous_action_cb_group)
		self.registerTriggerAction(CommonActions.TAKEOFF.value, self.triggerActionTakeoff, callback_group=self.autonomous_action_cb_group)

	@override
	def failsafe(self) -> bool:
		""" Failsafe command that triggers automatically after FAILSAFE_TIMEOUT_SEC seconds without control input """
		self.logger.warning(f"!!! Failsafe triggered with behavior: {self.failsafe_behavior} !!!")
		if self.failsafe_behavior == "land":
			return self.triggerActionLand()
		elif self.failsafe_behavior == "hover":
			self.softStop()
			return True
		else:
			# TODO: add an RTL behavior to the class
			return False

	def triggerActionLand(self) -> bool:
		""" Optional action to trigger an autonomous landing sequence """
		return False

	def triggerActionTakeoff(self) -> bool:
		""" Optional action to trigger an autonomous takeoff sequence """
		return False


class MavMultirotorBase(MultirotorUAVBase, MavlinkMultirotorMixin):
	"""
	Mixes in Mavlink multirotor control with SixDofVehicleBase
	"""	
	def __init__(self, name:str, override_namespace:Optional[str]=None):
		# init parent
		super().__init__(name=name, override_namespace=override_namespace)

		# init the Mavlink mixin
		self.initMavlink(self) # from MavlinkMultirotorMixin

	
	@override
	def update(self):
		""" 
		Override of VehicleInterface.update()
		Implements the repeating control command that goes out to the vehicle
		"""
		# send movement command
		if self.driver:
			self.driver.sendMove([self.linear.x, self.linear.y, self.linear.z, self.angular.z])
			# self.logger.info(f"Sent Linear: {self.linear} Angular: {self.angular} to {self.address}")
	
	@override
	def triggerActionLand(self) -> bool:
		""" Optional action to trigger an autonomous landing sequence """
		if self.driver:
			return self.driver.land()	
		return False
	
	@override
	def triggerActionTakeoff(self) -> bool:
		""" Optional action to trigger an autonomous takeoff sequence """
		if self.driver:
			return self.driver.takeoff(self.takeoff_height_m)
		return False

	@override
	def softStop(self) -> bool:
		""" Send a stop command to the vehicle """
		if self.driver:
			self.driver.sendMove([0,0,0,0])
			self.logger.info("Triggered softStop()")
			return True
		return False


class UGVBase(SixDofVehicleBase):
	""" Generic ground vehicle base """
	def __init__(self, name:str, override_namespace:Optional[str]=None):
		# pass name up the chain
		super().__init__(name=name, override_namespace=override_namespace)

	@override
	def failsafe(self) -> bool:
		""" Failsafe command that triggers automatically after FAILSAFE_TIMEOUT_SEC seconds without control input """
		# stop the vehicle
		return self.softStop()				


class QuadrupedBase(UGVBase):
	""" Generic quadruped base. Adds additional [sit,stand,walk] actions """
	def __init__(self, name:str, override_namespace:Optional[str]=None):
		# pass name up the chain
		super().__init__(name=name, override_namespace=override_namespace)

		# set up callback groups
		self.stance_cb_group = MutuallyExclusiveCallbackGroup() # stance actions are processed in order one-by-one

		# register stance actions
		self.registerTriggerAction(CommonActions.SIT.value, self.triggerActionSit, callback_group=self.stance_cb_group)
		self.registerTriggerAction(CommonActions.STAND.value, self.triggerActionStand, callback_group=self.stance_cb_group)
		self.registerTriggerAction(CommonActions.WALK.value, self.triggerActionWalk, callback_group=self.stance_cb_group)

		# register take_over action
		self.registerTriggerAction(CommonActions.TAKE_CONTROL.value, self.triggerActionTakeover)


	@abstractmethod
	def triggerActionSit(self) -> bool:
		""" Commands the quadruped to change stance to Sit """
		raise NotImplementedError

	@abstractmethod
	def triggerActionStand(self) -> bool:
		""" Commands the quadruped to change stance to Stand """
		raise NotImplementedError
	
	@abstractmethod
	def triggerActionWalk(self) -> bool:
		""" Commands the quadruped to change stance to Walk """
		raise NotImplementedError

	def triggerActionTakeover(self) -> bool:
		""" Optional Action that sends a takeover command to the quadruped """
		return True
