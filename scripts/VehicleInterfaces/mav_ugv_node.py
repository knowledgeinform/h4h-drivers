# boilerplate type hinting and clarity imports
from __future__ import annotations
import sys
if sys.version_info >= (3, 12):
	from typing import override 
else:
	from typing_extensions import override

from commons.mav_lib import ArduManualDrive
from commons.h4h.vehicle_interface import SixDofVehicleBase, MavlinkBaseMixin

class MavUGVControl(SixDofVehicleBase, MavlinkBaseMixin):
	""" concrete implementation for Mavlink UGV control """

	def __init__(self):
		# init parent
		super().__init__(name="MavUGVControl")
		self.initMavlink(self) # from MavlinkBaseMixin
		
		# start control loop
		self.start()

	@override
	def update(self):
		# send movement command
		self.driver.sendManualControl(self.linear.x, self.angular.z)
		self.logger.info(f"Sent Linear: {self.linear.x} Angular: {self.angular.z} to {self.address}")

	@override
	def connectToVehicle(self):
		""" sets self.driver to a mavlink connection to the vehicle """
		self.driver = ArduManualDrive(self.address, self.baudrate, self.max_horiz_spd, self.max_turn_spd)

if __name__ == "__main__":
	# init the controller
	controller = MavUGVControl()
	controller.spin()
