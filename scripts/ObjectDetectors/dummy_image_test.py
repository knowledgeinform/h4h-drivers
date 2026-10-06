import cv2
import time

from detector_base import GeoPoseImagePublisher


img = cv2.imread("00092.png")

publisher = GeoPoseImagePublisher(topic="geo_image_input")

while True:
	publisher.publish(img, 10, 20, 30)
	time.sleep(1.0)	

