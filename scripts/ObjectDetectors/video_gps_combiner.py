import cv2
import time
import numpy as np

import commons.utils_lib as utils
import commons.ros2_lib as rlib

from detector_base import GeoPoseImagePublisher


if __name__ == "__main__":
	# pull in environment variables
	video_stream_address = utils.getEnv("VIDEO_ADDRESS")
	gps_topic = utils.getEnv("GPS_TOPIC")
	publish_topic = utils.getEnv("PUBLISH_TOPIC")
	stream_rate_hz = utils.getEnv("FPS", default=0.5)

	# open up the video stream
	cap = cv2.VideoCapture(video_stream_address)

	# open up a subscriber to NavSatFix topic
	subscriber = rlib.NavSatFixSubscriber(topic=gps_topic)

	# open up a publisher for GeoPosImage
	publisher = GeoPoseImagePublisher(topic=publish_topic)

	# save image publishing rate
	rate = 1.0 / stream_rate_hz

	# loop and limit
	clock = utils.Timer()
	while True:
		# get image
		ret,frame = cap.read()
		if not ret:
			continue

		# check for fix
		if not subscriber.gps_fix:
			continue

		# publish data
		self.publisher.publish(
			img=frame,
			lat=subscriber.lat,
			lon=subscriber.lon,
			heading=0.0)

		# sleep until rate
		sleep_time = rate - clock.tick()
		if sleep_time > 0:
			time.sleep(sleep_time) # typically sleeps slightly too long
		


