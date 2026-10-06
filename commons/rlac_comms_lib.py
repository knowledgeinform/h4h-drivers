import json

class Vec3:
	def __init__(self):
		self.x = 0
		self.y = 0
		self.z = 0

class JsonCommand:
	def __init__(self):
		self.name = ""
		self.linear = Vec3()
		self.angular = Vec3()
		self.actions = []


    # {
    #     "messageType":  "control", 
    #     "messageData": {
    #         "name": "<string>",
    #         "linear_x": "<float>",
    #         "linear_y": "<float>",
    #         "linear_z": "<float>",
    #         "angular_z": "<float>",
    #         "autonomy": "<bool>",
    #         "takeoff": "<bool>", 
    #         "land": "<bool>", 
    #         "rtl": "<bool>" 
    #     }
    # }


				# "actions": {
				# "autonomy" : False,
				# "takeOver" : False,
				# "sit" : False,
				# "walk" : False,
				# "takeoff" : False,
				# "land" : False,
				# "rtl" : False,
				# "take_control" : False,
				# "arm" : False,
				# "disarm": False,
				# "posctl": False
				# }


# >>>>>>>>>>>>>>>>>>>
# Message:
# {"messageData":{"angular_z":0.0,"linear_x":-0.0,"linear_y":0.0,"linear_z":-0.0,"name":"h4h_rad_c100"},"messageType":"control"}
# <<<<<<<<<<<<<<<<<<<<



def toRlacJsonControlCommand(name, linear_vec3, angular_vec3):
	command = {
		"messageType": "control",
		"messageData": {
			"name" : name,
			"linear_x" : linear_vec3.x,
			"linear_y" : linear_vec3.y,
			"linear_z" : linear_vec3.z,
			"angular_z" : angular_vec3.z,
			}
		}
	return json.dumps(command) 

# >>>>>>>>>>>>>>>>>>>
# Message:
# {
# 	"messageType":"actions"
# 	"messageData":{
# 		"arm":true,
# 		"autonomy":false,
# 		"disarm":false,
# 		"flight_mode":"HOLD",
# 		"name":"h4h_rad_c100",
# 		"sender":"startArm"
# 		},
# 	}
# <<<<<<<<<<<<<<<<<<<<


def toRlacJsonActionsCommand(name, action_bools_dict):
	# list of all the available actions
	action_bools_list = ["flight_mode", "autonomy", "takeOver", "sit", "walk", "takeoff", "land", "rtl", "take_control", "arm", "disarm"]

	# build the dictionary with default values


	command = {
		"messageType": "actions",
		"messageData": {
			"name":"h4h_rad_c100",
			"arm":True,
			"autonomy":False,
			"disarm":False,
			"sit": False,
			"walk": False,
			"takeoff": False,
			"land": False,
			"rtl": False,
			"take_control": False,
			"takeOver": False,
			"flight_mode":"None",	
			}
		}		

	# copy over the actions
	for action in action_bools_list:
		if action in action_bools_dict:
			command["messageData"][action] = action_bools_dict[action]

	return json.dumps(command)

def fromRlacJsonControlCommand(json_command_str):
	msg_dict = json.loads(json_command_str)["messageData"]

	command = JsonCommand()
	command.name = msg_dict["name"]

	command.linear.x = msg_dict["linear_x"]
	command.linear.y = msg_dict["linear_y"]
	command.linear.z = msg_dict["linear_z"]

	command.angular.x = 0
	command.angular.y = 0
	command.angular.z = msg_dict["angular_z"]

	# command.actions = msg_dict["actions"]

	return command