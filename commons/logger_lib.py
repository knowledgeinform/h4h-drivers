import os
import logging

import commons.utils_lib as utils

# ************** STDOUT LOGGER **************

# define format for logging
logging.basicConfig(
	format='%(asctime)s,%(msecs)d %(levelname)-8s [%(funcName)s] %(message)s',
	datefmt='%Y-%m-%d:%H:%M:%S',
	level=logging.WARNING
)

# set up the logger
log_level = str(os.environ.get('LOG_LEVEL')) or 'INFO'
logger = logging.getLogger(__name__)
if (log_level == "WARNING"):
	logger.setLevel(logging.WARNING)
elif (log_level == "DEBUG"):
	logger.setLevel(logging.DEBUG)
else:
	logger.setLevel(logging.INFO)

# add some convenience functions

# returns the appropriate logging call for the level
# returns logger.info on miss
log_level_dict = {
	"INFO" : logger.info,
	"DEBUG" : logger.debug,
	"WARNING" : logger.warning,
	"ERROR" : logger.error,
	"CRITICAL" : logger.critical,
	"EXCEPTION" : logger.exception,
}
def loggerSwitch(log_level):
	log_level = log_level.upper()
	if log_level in log_level_dict:
		return log_level_dict[log_level]
	else:
		logger.warning(f"{log_level} not found in log_level_dict! Defaulting to INFO")
		return log_level_dict["INFO"]
logger.switch = loggerSwitch


# for ROS Publish messages
def loggerPublish(ros_msg, rostopic, log_level="INFO"):
	logger.switch(log_level)(f"Published {ros_msg} to {rostopic}", stacklevel=2)
logger.pub = loggerPublish


# add more common log message formats as needed
# NOTE: use stacklevel=2 to get the caller's name for logging


# ************** FILE OUT LOGGER **************

file_writter_active = utils.getEnv("FILE_LOGGER_ON", default=False)
file_writter_filename = utils.getEnv("FILE_LOGGER_PATH", default="NO_FILEPATH_SPECIFIED")

class FileLogger:
	def __init__(self, filename, is_active):
		self.filename = filename

		# check for activation
		self.active = is_active
		if not self.active:
			return

		# open up a file
		self.file = open(self.filename, 'w')

	def write(self, msg):
		if not self.active:
			return

		self.file.write(msg)
		self.file.flush()

	def close(self):
		if not self.active:
			return

		self.file.close()

flogger = FileLogger(filename=file_writter_filename, is_active=file_writter_active)