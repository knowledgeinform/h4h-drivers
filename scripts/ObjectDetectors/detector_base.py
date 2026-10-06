import cv2
import collections

import numpy as np
import commons.ros2_lib as rlib

from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from h4h_msgs.msg import GeoPoseImage
from commons.thread_lib import SimpleThread, ThreadStopper

class GeoPoseImageSubscriber(rlib.RosSubscriber):
	def __init__(self, topic, callback, namespace=None):
		super().__init__(
			node_name="GeoPoseImageSubscriber",
			msg_type=GeoPoseImage,
			rostopic=topic,
			callback=callback,
			namespace=namespace)

class GeoPoseImagePublisher(rlib.RosPublisher):
	def __init__(self, topic, namespace=None):
		super().__init__(
			node_name="GeoPoseImagePublisher",
			msg_type=GeoPoseImage,
			rostopic=topic,
			namespace=namespace)

	def publish(self, img, lat, lon, heading):
		# build up the message
		geo_msg = GeoPoseImage()
		geo_msg.img = rlib.ros2_lib_cvbridge.cv2_to_imgmsg(img, encoding="passthrough")

		geo_msg.pose.position.latitude = lat
		geo_msg.pose.position.longitude = lon
		# TODO: heading to quaternion conversion

		# publish
		self.publisher.publish(geo_msg)

class DetectorBase:
	def __init__(self, topic, namespace=None):
		print("DetectorBase Initializing...")

		# set up ros stuff
		self.bridge = CvBridge()
		self.subscriber = GeoPoseImageSubscriber(
			topic=topic,
			callback=self.imageCallback,
			namespace=namespace)

		# set up ring buffer
		self.buffer = collections.deque(maxlen=3) # [geographic_msgs/GeoPose, OpenCV Image (numpy.array)]

		# set up the thread
		self.STOPPER = ThreadStopper()
		self.thread = SimpleThread(runner=self, yield_time = 0.10, stopper=self.STOPPER)
		self.thread.start()

		print("DetectorBase Ready")

	# halts processing
	def stop(self):
		self.STOPPER.stop()
		rlib.shutdown()

	# polling processor loop
	def run(self):
		# grab an image
		img = self.getNext()
		if img is None:
			return

		# process it
		self.process(img)

	# callback for the ImageSubscriber
	def imageCallback(self, msg):
		# convert to OpenCV image
		img = self.bridge.imgmsg_to_cv2(msg.img, desired_encoding='passthrough')

		# push into buffer
		self.buffer.append([msg.pose, img]) # [geographic_msgs/GeoPose, OpenCV Image (numpy.array)]

	# attempts to retrieve the next (oldest) image in the buffer
	# returns None if there are no images
	def getNext(self):
		try:
			return self.buffer.popleft()
		except IndexError:
			return None
		# other exceptions are legitimate, let them fall through and crash

	# process a given image
	def process(self, img):
		raise NotImplementedError
