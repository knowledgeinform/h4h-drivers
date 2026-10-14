import os
import time
import shutil
from datetime import datetime
from typing import Any

class RisingTrigger:
	""" 
	Each rising signal only triggers once to avoid spammed output. 
	Queues each rising signal if update() is called multiple times between trigger() calls.
	"""
	def __init__(self):
		self.flag = False # switches to true on trigger value from update()
		self.queue_count = 0 # counts how many signals from this trigger are still unprocessed
	
	def update(self, value:bool):
		""" Sets the trigger on True, resets the trigger on False """
		if value:
			# trigger on rise
			if not self.flag:
				self.queue_count += 1
			self.flag = True
		else:
			# reset on false
			self.flag = False

	def trigger(self):
		""" Returns true if there's still a rising signal in the queue. """
		if self.queue_count > 0:
			self.queue_count -= 1
			return True
		return False
	
	def flush(self):
		""" Resets the flag and flushes all queued signals """
		self.flag = False
		self.queue_count = 0

# timer decorator
def timeit(func):
	def wrapper(*args, **kwargs):
		timer = Timer()
		retval = func(*args, **kwargs)
		print(func.__name__ + "()", "Run Time:", timer.totalTime())
		return retval
	return wrapper

# convert lat,lon to utm easting,northing
def latLonToUTM(lat:float, lon:float):
	import utm
	# easting, northing, zone_number, zone_letter = utm.from_latlon(self.lat, self.lon)
	return utm.from_latlon(lat, lon)

def latLonFromUTM(easting_m:float, northing_m:float, zone_num:int, zone_char:str):
	import utm
	# lat, lon = utm.to_latlon(easting_m, northing_m, zone_num, zone_char)
	return utm.to_latlon(easting_m, northing_m, zone_num, zone_char)

# convert epoch time to utc string
def EpochToUtc(epoch_time):
    utc_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch_time))
    return utc_time

# convert utc string to epoch time
def UtcToEpoch(utc_time):
    zero = datetime(1970, 1, 1)
    utc_time = datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%SZ")
    return (utc_time - zero).total_seconds()

# get environment variable value with auto typecasting
def getEnv(env_str:str, default=None, cast=None) -> Any:
	# use default if present
	if default is not None:
		# get environment value with default if missing
		value = os.environ.get(env_str, default)
	else: 
		# raise a KeyError if missing
		value = os.environ[env_str]

	# cast to the specified type
	if cast is not None:
		# special case for bools
		if cast is bool:
			return value == "True" or value == "true"
		return cast(value)

	elif default is not None:
		# special case for bools
		if type(default) is bool:
			return value == "True" or value == "true"
		return type(default)(value)

	else:
		return value

# clears and rebuilds folder
def clearMakeNewFolder(folder_path):
	if os.path.exists(folder_path):
		shutil.rmtree(folder_path);
	os.mkdir(folder_path);

# determines if a file is an image or a video
# 0 = Image, 1 = Video, -1 = Neither
def isImageOrVideo(filename):
	# sorting criteria
	img_exts = ["png", "jpg", "jpeg", "bmp", "tiff"];
	vid_exts = ["mp4", "avi", "mov"];

	# cut out the extension
	front, back = filename.split(".");
	back = back.lower();

	# compare to known extensions
	if back in img_exts:
		return 0;
	elif back in vid_exts:
		return 1;
	return -1;

# recursively crawls a folder for files
# returns a list of filepaths (starting from root)
def crawlFolder(root):
	# recursively retrieve filenames from source
	queue = [root];
	filepaths = [];
	while len(queue) > 0:
		# grab file
		currpath = queue.pop();

		# check if directory
		if os.path.isdir(currpath):
			# standardize path
			if currpath[-1] != "/":
				currpath = currpath + "/";

			# add files to queue
			files = os.listdir(currpath);
			for file in files:
				queue.append(currpath + file);

		else: # is a file
			filepaths.append(currpath);
	return filepaths;

# provides basic stopwatch functions
class Timer:
	def __init__(self, fps_history_size=10):
		self.last_time = 0;
		self.dt = 0;
		self.elapsed = 0;
		self.fps_hist = [0.0 for a in range(fps_history_size)]
		self.reset();

	def getFPS(self):
		return 1.0 / (sum(self.fps_hist) / len(self.fps_hist))

	def resetElapsed(self):
		self.elapsed = 0

	def reset(self):
		self.last_time = time.time();
		self.dt = 0;
		self.elapsed = 0;

	def tick(self):
		now = time.time();
		self.dt = now - self.last_time;
		self.last_time = now;
		self.elapsed += self.dt;

		# update fps
		self.fps_hist.append(self.dt)
		self.fps_hist.pop(0)
		return self.dt;

	def totalTime(self):
		self.tick();
		return self.elapsed;


# returns the last known input
# set max_size to one if just using as a holding space
class CircularBuffer:
	def __init__(self, max_size=3):
		self.size = max_size;
		self.buffer = [None for a in range(self.size)];

		# iterating
		self.index = -1;
		self.fresh = False;

	def add(self, item):
		self.index = (self.index + 1) % self.size;
		self.buffer[self.index] = item;
		self.fresh = True;

	def read(self):
		hold = self.fresh;
		self.fresh = False;
		return hold, self.buffer[self.index];

	# actually read like a circular buffer
	def readBack(self):
		item = self.buffer[self.index];
		self.index = (self.index - 1) % self.size; # negative is fine
		return (item is not None), item;

# parses simple config files
class ConfigParser:
	def __init__(self, filepath, delimiter="="):
		self.delimiter = delimiter;
		self.params = {};
		self.parse(filepath);

	def parse(self, filepath):
		self.params = {};
		file = open(filepath, 'r');
		for line in file:
			# sanitize and skip comments
			line = line.strip();
			if len(line) < 2 or line[0] == "#":
				continue;

			# parse line
			front,back = line.split(self.delimiter);
			front = front.strip();
			back = back.strip();
			self.params[front] = back;
		file.close();

	# returns a matching param, or default if not found in dictionary
	# if not default is supplied and the parameter isn't found, force an exception
	def getParam(self, param, default=None, cast=None):
		if param in self.params:
			if cast is not None:
				return cast(self.params[param])
			else:
				return self.params[param];
				
		if default is not None:
			return default;
		else:
			# raise a natural KeyError
			return self.params[param];
