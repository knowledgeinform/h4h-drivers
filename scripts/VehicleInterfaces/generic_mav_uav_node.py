from commons.h4h.vehicle_interface import MavMultirotorBase

class GenericMultirotorControl(MavMultirotorBase):
	""" concrete implementation for Mavlink multirotor vehicle control with zero additions """

	def __init__(self):
		# init parents
		super().__init__(name="GenericMultirotorControl")

		# start control loop
		self.start()

if __name__ == "__main__":
	# init the controller
	controller = GenericMultirotorControl()
	controller.spin()