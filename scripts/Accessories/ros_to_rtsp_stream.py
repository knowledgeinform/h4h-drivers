import cv2
import time

import numpy as np

import commons.utils_lib as utils

import commons.ros2_lib as rlib
from commons.stream_lib import startRTSPServer


if __name__ == "__main__":
	# pull ENV parameters
	image_topic = utils.getEnv("IMAGE_TOPIC")
	width = utils.getEnv("WIDTH", 640)
	height = utils.getEnv("HEIGHT", 480)
	fps = utils.getEnv("FRAMERATE", 5)
	port = utils.getEnv("PORT", cast=str)

	# start up a ROS2Cam
	cam = rlib.ROS2Cam(
		topic=image_topic,
		max_fps=fps,
		res=(width,height))

	# spin the RTSP server
	startRTSPServer(
		cameraCapture=cam, 
		ip_addr="/video", 
		port=port, 
		width=width, 
		height=height, 
		fps=fps)



