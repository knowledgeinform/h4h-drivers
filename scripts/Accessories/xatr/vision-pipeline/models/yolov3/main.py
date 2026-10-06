import cv2
import numpy as np

from yolo import YoloNet


# open video capture (laptop webcam)
cap = cv2.VideoCapture(0);

# initialize network
net = YoloNet(config="yolov3.cfg", weights="yolov3.weights", labels="coco.names", confidence=0.5, nms=0.3);

img = cv2.imread("person1.png")
img = net.processImage(img)
cv2.imshow("Image", img)
cv2.waitKey(0)

# # main loop
# done = False;
# while not done:
# 	# get frame
# 	ret, frame = cap.read();
# 	if not ret:
# 		continue;

# 	# process frame
# 	frame = net.processImage(frame);

# 	# show image
# 	cv2.imshow("Image", frame);
# 	done = cv2.waitKey(1) == ord('q');