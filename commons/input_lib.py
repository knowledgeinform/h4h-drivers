import functools
from pynput.keyboard import Key, Listener

class Controller:
	def __init__(self, on_press, on_release):
		self.listener = Listener(on_press=on_press, on_release=on_release)
		self.listener.start()

	def alive(self):
		return self.listener.is_alive()

class WasdIjklController(Controller):
	""" Four Axes controller with optional keymapping for boolean switches """

	def __init__(self):
		super().__init__(on_press=self.on_press, on_release=self.on_release)

		# store movement controls as
		# ws: self.axes[0]
		# ad: self.axes[1]
		# ik: self.axes[2]
		# jl: self.axes[3]
		self.axes = [0,0,0,0]

		# keymap for all other extra keys
		self.keymap = {} # maps switch names to keycodes
		self.switches = {} # maps switch names to activation state. registers True if pressed, False if not pressed

	def addKey(self, name:str, keycode:str):
		""" Add a named boolean switch along with a keycode (one character) that maps to it """
		self.keymap[name] = keycode
		self.switches[name] = False
	
	def on_press(self, key):
		# exit condition
		if key == Key.esc:
			print("LISTENER STOPPED")
			return False

		# filter for only character keys (alphanumeric)
		try:
			kc = key.char
		except AttributeError as ae:
			return True

		# get axes
		if kc == 'w':
			self.axes[0] = 1
			return True
		if kc == 's':
			self.axes[0] = -1
			return True
		
		if kc == 'd':
			self.axes[1] = 1
			return True
		if kc == 'a':
			self.axes[1] = -1
			return True
		
		if kc == 'i':
			self.axes[2] = 1
			return True
		if kc == 'k':
			self.axes[2] = -1
			return True
		
		if kc == 'l':
			self.axes[3] = 1
			return True
		if kc == 'j':
			self.axes[3] = -1
			return True
		
		# check extra keys
		for switch_name in self.keymap:
			keycode = self.keymap[switch_name]
			if kc == keycode:
				self.switches[switch_name] = True
				return True
		return True
	
	def on_release(self, key):
		# filter for only character keys (alphanumeric)
		try:
			kc = key.char
		except AttributeError as ae:
			return True
		
		# zero out the axes
		if kc in 'ws':
			self.axes[0] = 0
			return True
		if kc in 'da':
			self.axes[1] = 0
			return True
		if kc in 'ik':
			self.axes[2] = 0
			return True
		if kc in 'jl':
			self.axes[3] = 0
			return True

		# zero out the switches
		for switch_name in self.keymap:
			keycode = self.keymap[switch_name]
			if kc == keycode:
				self.switches[switch_name] = False
				return True
		return True



class WasdControl(Controller):
	def __init__(self, hook):
		self.hook = hook
		super().__init__(on_press=self.wasd_on_press, on_release=self.wasd_on_release)

	def wasd_on_press(self, key):
		# exit condition
		if key == Key.esc:
			print("LISTENER STOPPED") # throws a fake, attribute error?
			return False

		# check non-special key
		try:
			kc = key.char
		except AttributeError as ae:
			return True

		# move
		if kc == 'w':
			self.hook[0] = 1
		if kc == 's':
			self.hook[0] = -1

		# turn
		if kc == 'd':
			self.hook[1] = 1
		if kc == 'a':
			self.hook[1] = -1

		if kc == 'i':
			self.hook[2] = 1
		if kc == 'k':
			self.hook[2] = -1

		if kc == 'l':
			self.hook[3] = 1
		if kc == 'j':
			self.hook[3] = -1

		if kc == 'q':
			self.hook[4] = 1
		if kc == 'e':
			self.hook[5] = 1
		if kc == 'r':
			self.hook[6] = 1

		if kc in 'o':
			self.hook[7] = 1
		if kc in 'p':
			self.hook[8] = 1
		if kc in 'm':
			self.hook[9] = 1
		if kc in 'n':
			self.hook[10] = 1

	def wasd_on_release(self, key):
		# check non-special key
		try:
			kc = key.char
		except AttributeError as ae:
			return True

		if kc in 'ws':
			self.hook[0] = 0

		if kc in 'ad':
			self.hook[1] = 0

		if kc in 'ik':
			self.hook[2] = 0

		if kc in 'jl':
			self.hook[3] = 0

		if kc in 'q':
			self.hook[4] = 0
		if kc in 'e':
			self.hook[5] = 0
		if kc in'r':
			self.hook[6] = 0

		if kc in 'o':
			self.hook[7] = 0
		if kc in 'p':
			self.hook[8] = 0
		if kc in 'm':
			self.hook[9] = 0
		if kc in 'n':
			self.hook[10] = 0





# import pygame as pyg

# # returns the numeric sign of the input value
# def sign(value):
# 	if value < 0:
# 		return -1
# 	if value > 0:
# 		return 1
# 	return 0

# # rescale numeric range from [-1,1] to [-1,-DEADZONE] ~ [DEADZONE,1] and back to [-1,1]
# def applyDeadzone(normed_value, deadzone):
# 	if abs(normed_value) <= deadzone:
# 		normed_value = 0
# 	else:
# 		normed_value -= sign(normed_value) * deadzone
# 		normed_value /= (1.0 - deadzone)
# 	return normed_value

# # class Axis:
# # 	def __init__(self, low, high, deadzone):
# # 		self.low = low
# # 		self.high = high
# # 		self.deadzone = deadzone

# # 	def update

# class GamePad:
# 	def __init__(self, joystick_id, throttle_deadzone=0.02, turn_deadzone=0.02):
# 		# copy params
# 		self.jid = joystick_id
# 		self.throttle_deadzone = throttle_deadzone
# 		self.turn_deadzone = turn_deadzone

# 		# initialize pygame things
# 		pyg.init()
# 		pyg.joystick.init()
# 		clock = pyg.time.Clock()

# 		# connect to the gamepad
# 		print("Number of Controllers Detected:", pyg.joystick.get_count())
# 		self.controller = pyg.joystick.Joystick(JOYSTICK_ID)
# 		print("Connected to Joystick ID", self.jid)

# 		# define axes
# 		# self.left_stick

# 	# def 

# CONTROLLER MAPPINGS:

# Axis 0 = Left thumbstick (+1 is right)
# Axis 1 = Left thumbstick (+1 is down)
# Axis 2 = Right thumbstick (+1 is right)
# Axis 3 = Right thumbstick (+1 is down)
# Axis 4 = Left Trigger (+1 is pressed)
# Axis 5 = Right Trigger (+1 is pressed)

# N/S/E/W Face buttons are the four buttons on the right side of the controller

# Button 0 = South Face button (+1 is pressed)
# Button 1 = East Face button (+1 is pressed)
# Button 2 = West Face button (+1 is pressed)
# Button 3 = North Face button (+1 is pressed)
# I'm done mapping buttons, there are 16 of them




# if __name__ == "__main__":
# 	# TWEAKABLES
# 	UPDATES_PER_SECOND = 20 # limits how fast we poll and send commands
# 	MAV_ADDRESS = "udpin:10.42.0.1:60201" # the address that connects to the Cube
# 	JOYSTICK_ID = 0 # 0 = the first controller detected
# 	MAX_THROTTLE = 250 # [0,1000] 0 is none, 1000 is full power
# 	MAX_TURN = 500 # [0,1000] 0 is none, 1000 is full steer
# 	THROTTLE_DEAD_ZONE = 0.02 # [0,1] How far off zero before throttle starts 
# 	TURN_DEAD_ZONE = 0.02 # [0,1] How far off-center before steering starts


# 	# initialize pygame things
# 	pyg.init()
# 	pyg.joystick.init()
# 	clock = pyg.time.Clock()

# 	# connect to the gamepad
# 	print("Number of Controllers Detected:", pyg.joystick.get_count())
# 	controller = pyg.joystick.Joystick(JOYSTICK_ID)

# 	print("Number of Joysticks Detected:", controller.get_numaxes())
# 	print("Number of Buttons Detected:", controller.get_numbuttons())

# 	# connect to mavlink
# 	mav_controller = ArduManualDrive(
#         mav_address=MAV_ADDRESS,
#         max_throttle=MAX_THROTTLE,
#         max_turn=MAX_TURN,
#         baud=57600) # don't mess with this unless you have a VERY good reason

# 	# create a window (just a black screen, must be the active window for pygame to do things)
# 	screen = pyg.display.set_mode((200,50))

# 	# main event loop
# 	stop_flag = False
# 	while not stop_flag:
# 		# check for quit (click the 'x' on window)
# 		for event in pyg.event.get():
# 			if event.type == pyg.QUIT:
# 				stop_flag = True

# 		# alternate quit condition (see mappings at top of file)
# 		east_button_down = controller.get_button(1)
# 		if east_button_down == 1:
# 			stop_flag = True

# 		# check arm/disarm (see mappings at top of file)
# 		# A vehicle needs to be ARMED before it can be driven (we auto-arm on start)
# 		# If a vehicle is DISARMED it can be steered, but not moved (wheels will turn, but it won't go foward/backwards)
# 		# Note: I don't have an actual vehicle to test arm/disarm on
# 		north_button_down = controller.get_button(3)
# 		south_button_down = controller.get_button(0)
# 		if north_button_down:
# 			mav_controller.arm()
# 		if south_button_down:
# 			mav_controller.disarm()

# 		# pull the thumbsticks and triggers (see mappings at top of file)
# 		leftstick_lr = controller.get_axis(0) # left stick, left-right axis
# 		left_trigger = controller.get_axis(4) # reverse
# 		right_trigger = controller.get_axis(5) # forward

# 		# shift trigger output numerical range from [-1,1] to [0,1]
# 		right_trigger += 1.0
# 		right_trigger /= 2.0
# 		left_trigger += 1.0
# 		left_trigger /= 2.0

# 		# add up trigger inputs (with left as negative)
# 		trigger_combined = right_trigger - left_trigger

# 		# apply deadzones
# 		trigger_combined = applyDeadzone(trigger_combined, THROTTLE_DEAD_ZONE)
# 		leftstick_lr = applyDeadzone(leftstick_lr, TURN_DEAD_ZONE)

# 		# send controls to mavlink
# 		mav_controller.sendManualControl(trigger_combined, leftstick_lr)

# 		# limit poll rate
# 		clock.tick(UPDATES_PER_SECOND)

# 	# cleanup
# 	mav_controller.disconnect()
# 	pyg.joystick.quit()
# 	pyg.quit()
