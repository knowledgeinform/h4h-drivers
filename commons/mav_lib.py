# boilerplate type hinting and clarity imports
from __future__ import annotations
import sys
if sys.version_info >= (3, 12):
	from typing import override 
else:
	from typing_extensions import override
from abc import abstractmethod

import time
from pymavlink import mavutil

import commons.math_lib as mlib
import commons.thread_lib2 as tlib2


# class MavMissionItem:
# 	def __init__(self, lat:float, lon:float, alt:float


class ArduManualBase:
	def __init__(self, mav_address: str, baud: int):
		# save address
		self.mav_address = mav_address
		self.baud = baud # baud is irrelevant for non-serial connections

		# set up connection
		self.drone = None
		self.connect()

		# print out available modes
		# modes = self.drone.mode_mapping()
		# print("----------------")
		# print("Available Modes:", list(modes))
		# print("----------------")

		# set up heartbeat thread
		tlib2.threadForever(func=self.sendHeartbeat, rate_hz=1)


	# starts up a connection to the drone
	def connect(self):
		# check if we need to connect
		if self.drone is None:
			print("Connecting to", self.mav_address, "...")
			self.drone = mavutil.mavlink_connection(self.mav_address, baud=self.baud)
			print("Waiting for Heartbeat...")
			self.drone.wait_heartbeat()
			print("Finished connecting to", self.mav_address)

	# drops connection to the drone
	def disconnect(self):
		# stop and disarm
		self.disarm()

		# disconnect from the drone
		if self.drone is not None:
			self.drone.close()
			self.drone = None
			print("Disconnected from", self.mav_address)

	# attempts to arm the vehicle (this can fail if vehicle prechecks are enabled and not cleared)
	def arm(self):
		# check if we're connected
		if self.drone is not None:
			# Send arm command
			print("Arming!")
			self.drone.mav.command_long_send(
				self.drone.target_system,                     # target system
				self.drone.target_component,                  # target component
				mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, # command ID
				5,                                            # confirmation # maybe remove confirmation?
				1,                                            # [0:Disarm, 1:Arm]
				0,                                            # force
				0, 0, 0, 0, 0                                 # unused
			)
			return True
		return False
	
	# attempts to disarm the vehicle
	def disarm(self):
		# check if we're connected
		if self.drone is not None:
			# Send disarm command
			print("Disarming!")
			self.drone.mav.command_long_send(
				self.drone.target_system,                     # target system
				self.drone.target_component,                  # target component
				mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, # command ID
				5,                                            # confirmation
				0,                                            # arm [0:Disarm, 1:Arm]
				0,                                            # force
				0, 0, 0, 0, 0                                 # unused
			)
			return True
		return False

	# receives and sends a standard heartbeat message to the vehicle
	# the Teal UAV specifically needs to have its heartbeat message get received
	# the base class __init__ spins up a thread that runs this at 1 hz
	def sendHeartbeat(self):
		self.drone.wait_heartbeat()
		self.drone.mav.heartbeat_send(
			mavutil.mavlink.MAV_TYPE_GCS, # maybe MAV_TYPE_ONBOARD_CONTROLLER
			mavutil.mavlink.MAV_AUTOPILOT_INVALID,
			0, 0, 0)
	
	def sendServo(self, servo_id:int, pwm:int):
		""" Sends a PWM signal straight to the specified servo """
		if self.drone is not None:
			self.drone.mav.command_long_send(
				self.drone.target_system,
				self.drone.target_component,
				mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
				0, # message number (technically should increment, but I don't think anything listens to this)
				servo_id,
				pwm,
				0,0,0,0,0 # unused params
			)
			return True
		return False

	def sendRC(self, rc_channel_id:int, pwm:int):
		""" Sends a PWM signal straight through via RC Channel ID (16 max) """
		# set null values (these are ignored)
		rc_channel_values = [65535 for _ in range(18)]

		# set target channel value
		rc_channel_values[rc_channel_id - 1] = pwm

		# send rc values
		self.drone.mav.rc_channels_override_send(
			self.drone.target_system,
			self.drone.target_component,
			*rc_channel_values)

	def startMission(self):
		self.drone.set_mode("MISSION")

	def sendMissionPlan(self, geo_points:list, add_takeoff_land:bool=False) -> bool:
		"""
		Sends a mission plan to the drone

		geo_points is expected to be a list of lists with each internal list having [lat,lon,altitude]
		lat in degrees
		lon in degrees
		altitude in meters relative to home position
		"""

		# send the mission prep message
		self.drone.mav.mission_count_send(
			self.drone.target_system,
			self.drone.target_component,
			len(geo_points),
			mavutil.mavlink.MAV_MISSION_TYPE_MISSION
		)

		# send each point one-by-one
		counter = 0
		while counter < len(geo_points):
			# wait for a request from the drone
			msg = self.drone.recv_match(
				type=["MISSION_REQUEST_INT", "MISSION_REQUEST", "MISSION_ACK"],
				blocking=True
			)

			# check for early rejection
			if msg.get_type() == "MISSION_ACK":
				print("!!! Failed to upload full mission!")
				print("Response message:", msg)
				return False

			# continue sending mission items
			lat,lon,alt = geo_points[msg.seq]

			# convert to mavlink format
			lat = int(round(lat * 1e7))
			lon = int(round(lon * 1e7))

			# bookend the command message with takeoff and land
			command = mavutil.mavlink.MAV_CMD_NAV_WAYPOINT
			if add_takeoff_land:
				if msg.seq == 0:
					command = mavutil.mavlink.MAV_CMD_NAV_TAKEOFF
				elif msg.seq == len(geo_points)-1:
					command = mavutil.mavlink.MAV_CMD_NAV_LAND

			# send the message
			self.drone.mav.mission_item_int_send(
				self.drone.target_system,
				self.drone.target_component,
				msg.seq,
				mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
				command,
				1 if msg.seq == 0 else 0, 	# is this the current command (start at zero)
				1, 							# should the drone autocontinue each item in the mission (yes)
				0,				# wait-at-point time (in seconds)
				0,				# acceptance radius (meters), how close to waypoint is good enough, 0 = use px4's param NAV_ACC_RAD
				0,				# pass radius (meters), how we swing past the point. 
								# 1.0 means swing a 1 meter loop around the point clockwise, -1 means counter clockwise
				float("nan"),	# yaw (degrees). What direction do we face when reaching the waypoint. 
								# NaN means px4 chooses (angle from previous point to current point)
				lat,
				lon,
				alt,
				mavutil.mavlink.MAV_MISSION_TYPE_MISSION
			)

			# increment counter
			counter += 1
		return True


class ArduManualUAVDrive(ArduManualBase):
	"""
	Creates a Mavlink connection to a UAV

	mav_address (str):
		the ip address to connect to the vehicle 
			example: mav_address="udpin:0.0.0.0:14550" <for a px4 drone>
			example: mav_address="udpin:192.168.168.12:14550" <for an ardupilot drone>
			example: mav_address="dev/ttyUSB0"
	
	baud (int):
		the baudrate of the connection; this only matters for SERIAL connections

	move_range (list):
		a [lower_bound, upper_bound] range for the RC output expected by the vehicle
	
	turn_range (list):
		a [lower_bound, upper_bound] range for the RC output expected by the vehicle
	
	throttle_range (list):
		a [lower_bound, upper_bound] range for the RC output expected by the vehicle
		
	is_px4 (bool):
		if True then the MANUAL command will use PX4 POSITION mode. if False then it'll use Ardupilot LOITER mode 
	"""

	def __init__(self, mav_address:str, baud:int=0, strafe_spd:int=1000, turn_spd:int=1000, rise_spd:int=500, is_px4:bool=False):
		# init parent
		super().__init__(mav_address, baud)

		# record move and turn limits
		self.MOVE_RANGE = [-strafe_spd, strafe_spd]
		self.TURN_RANGE = [-turn_spd, turn_spd]

		# set throttle range
		THROTTLE_MIDPOINT = 500
		self.THROTTLE_RANGE = [THROTTLE_MIDPOINT - rise_spd, THROTTLE_MIDPOINT + rise_spd]

		# check between ardupilot or px4
		self.is_px4 = is_px4

# https://discuss.px4.io/t/mav-cmd-do-set-mode-all-possible-modes/8495/2
# Manual: base_mode:217, main_mode:1, sub_mode:0
# Stabilized: base_mode:209, main_mode:7, sub_mode:0
# Acro: base_mode:209, main_mode:5, sub_mode:0
# Rattitude: base_mode:193, main_mode:8, sub_mode:0
# Altitude: base_mode:193, main_mode:2, sub_mode:0
# Offboard: base_mode:209, main_mode:6, sub_mode:0
# Position: base_mode:209, main_mode:3, sub_mode:0
# Hold: base_mode:217, main_mode:4, sub_mode:3
# Missition: base_mode:157, main_mode:4, sub_mode:4
# Return: base_mode:157, main_mode:4, sub_mode:5
# Follow me: base_mode:157, main_mode:4, sub_mode:8


	def processCommand(self, command: str):
		"""
		processes string commands for mode changes and arm/disarm
		"""

		print("Sending Command:", command)
		if command == "ARM":
			self.arm()
		elif command == "DISARM":
			self.disarm()
		elif command == "POSITION":
			if self.is_px4:
				# print("************************* TRYING TO SET POSITION MODE")
				self.setCustomMode(209,3,0) # POSITION mode
			else:
				self.setMode(5) # LOITER mode
		elif command == "HOLD":
			if self.is_px4:
				self.setCustomMode(217,4,3) # HOLD mode
			else:
				pass
		elif command == "OFFBOARD":
			if self.is_px4:
				self.setCustomMode(209,6,0) # OFFBOARD mode
			else:
				pass
		elif command == "MANUAL":
			if self.is_px4:
				self.setCustomMode(217,1,0) # MANUAL mode (same as STABILIZED for PX4)
			else:
				pass
		elif command == "STABILIZED":
			if self.is_px4:
				self.setCustomMode(209,7,0) # STABILIZED mode
			else:
				pass
		elif command == "ALTITUDE":
			if self.is_px4:
				self.setCustomMode(193,2,0) # ALTITUDE mode
			else:
				pass


	# sends control outputs [x,y,z,r] directly as-is to the rc channels
	def sendDirect(self, control: list):
		x,y,z,r = control
		# send mavlink control
		if self.drone is not None:
			# print("Control", [x,y,z,r])
			self.drone.mav.manual_control_send(
				self.drone.target_system,
				x, # forward/backward
				y, # left/right
				z, # up/down
				r, # yaw left/right
				0)

	def sendMove(self, control: list):
		"""
		Takes normalized [x,y,z,r] [-1,1] and converts to the RC range before sending to vehicle
		x is forward/backward
		y is left/right
		z is up/down
		r is yaw left/right
		
		control (list):
			[x,y,z,r] in the [-1,1] range
		"""

		# break down the control and scale by speed
		x,y,z,r = control # x: forward/backward, y: left/right, z: up/down, r: yaw left/right
		x = int(mlib.linearReframe(x, -1, 1, self.MOVE_RANGE[0], self.MOVE_RANGE[1]))
		y = int(mlib.linearReframe(y, -1, 1, self.MOVE_RANGE[0], self.MOVE_RANGE[1]))
		z = int(mlib.linearReframe(z, -1, 1, self.THROTTLE_RANGE[0], self.THROTTLE_RANGE[1]))
		r = int(mlib.linearReframe(r, -1, 1, self.TURN_RANGE[0], self.TURN_RANGE[1]))

		# send scaled controls
		self.sendDirect([x,y,z,r])

	def setMode(self, mode_id: int):
		# check if we're connected
		if self.drone is not None:
			print("Setting Mode:", mode_id)
			self.drone.mav.set_mode_send(
				self.drone.target_system,
				mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
				mode_id)
	
	def setCustomMode(self, base_mode:int, main_mode:int, sub_mode:int) -> bool:
		if self.drone is not None:
			print("Setting Custom Mode:", [base_mode,main_mode,sub_mode])
			self.drone.mav.command_long_send(
				self.drone.target_system,
				self.drone.target_component,
				mavutil.mavlink.MAV_CMD_DO_SET_MODE,
				0,
				base_mode,
				main_mode,
				sub_mode,
				0,0,0,0)	
			return True
		return False

	@override
	def arm(self) -> bool:
		# check if we're connected
		print("UAV Arming")
		if self.drone is not None:
			# send a true zero command (required for arming on some drone systems)
			for a in range(5):
				self.sendDirect([0,0,0,0])
			time.sleep(0.2) # the sleep is required 
			# otherwise it can fail with "AP: Arm: Throttle (RC3) is not neutral"

			# continue with parent's arm() func
			super().arm()
			return True
		return False

	def land(self) -> bool:
		""" Sends a Land Command to the drone """
		if self.drone is not None:
			self.drone.mav.command_long_send(
				self.drone.target_system,
				self.drone.target_component,
				mavutil.mavlink.MAV_CMD_NAV_LAND,
				0, # Confirmation
				0, # param1: abort alt (m)
				0, # param2: precision land mode
				0, # param3: empty
				0, # param4: yaw angle (NaN/0 for current system yaw)
				0, # param5: latitude (0 = land at current position)
				0, # param6: longitude (0 = land at current position)
				0  # param7: altitude (0 = land to surface)
			)
			return True
		return False

	def takeoff(self, altitude_m) -> bool:
		""" 
		This isn't working correctly right now. 
		Sends a Takeoff command to the drone 
		"""
		if self.drone is not None:
			print("Taking off to", altitude_m, "meters")
			self.drone.mav.command_long_send(
				self.drone.target_system,
				self.drone.target_component,
				mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
				0, # Confirmation
				0, # param 1: Pitch/Climb Angle (Plane only, 0 for Copter)
				0, # param 2: Empty
				0, # param 3: Empty
				0, # param 4: Yaw angle (0 = unchanged)
				0, # param 5: Latitude (0 = current location)
				0, # param 6: Longitude (0 = current location)
				altitude_m # param 7: Altitude
			)
			return True
		return False
	

class ArduManualDrive(ArduManualBase):
	def __init__(self, mav_address: str, baud=0, max_throttle=250, max_turn=500):
		# init parent
		super().__init__(mav_address, baud)

		# drive scaling parameters
		self.THROTTLE_MAX = max_throttle
		self.TURN_MAX = max_turn

	# sends a stop moving command
	def sendStop(self):
		self.sendDrive(0,0)

	# rescales inputs from [-1,1] to [-MAX,MAX] before sending to drone
	def sendManualControl(self, throttle_norm: float, turn_norm: float):
		# rescale
		throttle = throttle_norm * self.THROTTLE_MAX
		turn = turn_norm * self.TURN_MAX

		# intify
		throttle = int(throttle)
		turn = int(turn)

		self.sendDrive(throttle, turn)
	
	# sends a drive command
	def sendDrive(self, throttle: int, turn: int):
		if self.drone is not None:
			print("Sending Command:", [throttle,turn])
			self.drone.mav.manual_control_send(
				self.drone.target_system, # target system
				0,                        # x-axis / pitch [-1000, 1000]
				turn,                     # y-axis / yaw [-1000, 1000]
				throttle,                 # z-axis / throttle [-1000, 1000]
				0,                        # r-axis / roll [-1000, 1000]
				0                         # buttons (unused)
			)

class MavlinkListenerPlugin:
	def __init__(self):
		self.msg_type = "MISSING_MESSAGE_TYPE"
		self.count = 0
		self.data = {} # [key: [timestamp, data]]

	def update(self, msg_dict:dict):
		""" updates data from message """
		# record current time for timestamping
		now = time.time()

		# preprocess data as needed
		self.process(msg_dict)

		# copy over the data
		for key in msg_dict:
			self.data[key] = [now, msg_dict[key]]
		self.count += 1
	
	def filter(self, msg_dict:dict) -> bool:
		"""
		Optional function that checks if a message should be accepted
		"""
		return True
	
	def process(self, data:dict):
		""" 
		Optional function that runs unit or coordinate frame conversions 
		before passing on the data to publish
		"""
		pass

class GPSMavlinkListenerPlugin(MavlinkListenerPlugin):
	""" Plugin listener that processes Mavlink GLOBAL_POSITION_INT messages """
	def __init__(self):
		super().__init__()
		self.msg_type = "GLOBAL_POSITION_INT"

	@override
	def process(self, data:dict):
		""" 
		Optional function that runs unit or coordinate frame conversions 
		before passing on the data to publish
		"""
		# convert lat/lon to degrees
		data['lat'] /= 1.0e7
		data['lon'] /= 1.0e7

		# convert altitude to meters
		data['relative_alt'] /= 1000.0
		data['alt'] /= 1000.0

		# convert heading to degrees
		data['hdg'] /= 100.0

class BatteryMavlinkListenerPlugin(MavlinkListenerPlugin):
	""" Plugin listener that processes Mavlink BATTERY_STATUS messages """
	def __init__(self):
		super().__init__()
		self.msg_type = "BATTERY_STATUS"

class HeartbeatMavlinkListenerPlugin(MavlinkListenerPlugin):
	""" Plugin listener that processes Mavlink HEARTBEAT messages """
	def __init__(self):
		super().__init__()
		self.msg_type = "HEARTBEAT"

	@override
	def filter(self, msg_dict:dict) -> bool:
		if msg_dict['base_mode'] == 0 and msg_dict['custom_mode'] == 0: 
			return False
		return True

class AttitudeMavlinkListenerPlugin(MavlinkListenerPlugin):
	""" Plugin listener that processes Mavlink ATTITUDE messages """
	def __init__(self):
		super().__init__()
		self.msg_type = "ATTITUDE"


class MavlinkListenerPluginInterface:
	"""
	A mavlink listener class that can filter and parse Mavlink messages
	Should only have a single instance across the forwarded link
	"""
	def __init__(self, connection:ArduManualBase):
		# copy the connection to the vehicle
		self.drone = connection.drone

		# set up a message filter
		self.msg_filter = []

		# set up a plugin dictionary
		self.plugins = {}

		# sping up processing thread
		tlib2.threadForeverNoWait(func=self.processMessage)
	
	def registerListener(self, plugin:MavlinkListenerPlugin):
		""" Adds the plugin's message type to the processing list """
		# register it to the lists if new
		if not plugin.msg_type in self.plugins:
			self.msg_filter.append(plugin.msg_type)
			self.plugins[plugin.msg_type] = plugin

	def getCounts(self) -> dict:
		""" Returns the count of messages for each plugin """
		counts = {}
		for msg_type, plugin in self.plugins.items():
			counts[msg_type] = plugin.count
		return counts
	
	def processMessage(self):
		""" 
		Reads and updates self.vars with data from any 
		message that matches our filtered list
		"""
		# if no plugins have been registered yet, just wait
		if len(self.msg_filter) == 0:
			time.sleep(0.1)
			return

		# filter by message type and update plugins
		msg = self.drone.recv_match(type=self.msg_filter, blocking=True)
		if msg:
			msg_dict = msg.to_dict()
			if self.plugins[msg.get_type()].filter(msg_dict):
				# update the plugin to track message counts
				self.plugins[msg.get_type()].update(msg_dict)



class MavlinkListenerGroup:
	def __init__(self, plugin_interface:MavlinkListenerPluginInterface, filter:None|list = None):
		self.interface = plugin_interface
		self.plugin_keys = []

		self.filter_list = None # only returns data in the list if active
		if filter is not None:
			self.filter_list = filter

	def registerListener(self, plugin:MavlinkListenerPlugin):
		""" Adds the plugin's message type to filter out for data groups """
		# register it to the lists
		self.plugin_keys.append(plugin.msg_type)
		self.interface.registerListener(plugin)

	def getData(self) -> dict|None:
		""" 
		returns the data as a dictionary with a timestamp 
		returns None if not all registered listeners have received data
		"""
		# check if all listener plugins have received at least one message
		for key in self.plugin_keys:
			if self.interface.plugins[key].count == 0:
				return None

		# pull data from all of the registered listeners
		data = {}
		for key in self.plugin_keys:
			data.update(self.interface.plugins[key].data)
		
		# filter by list
		if self.filter_list is not None:
			filtered_data = {}
			for key in data:
				if key in self.filter_list:
					filtered_data[key] = data[key]
			return filtered_data

		return data


	def getDataWithoutTimestamps(self) -> dict|None:
		"""
		returns the data as a dictionary without a timestamp
		returns None if not all registered listeners have received data
		"""
		# get data and check for none
		data_with_timestamps = self.getData()
		if data_with_timestamps is None:
			return None

		# reformat without the timestamps
		data = {}
		for key,item in data_with_timestamps.items():
			data[key] = item[1] # [timestamp, data]
		return data