import time

from yolo import YoloNet
from detector_base import DetectorBase

class YoloDetector(DetectorBase):
	def __init__(self, topic, namespace=None):
		# init parent
		super().__init__(topic=topic, namespace=namespace)

		# hardcode the yolo filepaths
		self.network = YoloNet(
			config_file="yolov3.cfg",
			weights_file="yolov3.weights",
			labels_file="coco.names",
			confidence_thresh=0.5)

	# define the callback
	# OVERRIDE
	def process(self, geo_image):
		# unstack the data
		pose, img = geo_image
		# pose.position
		# pose.orientation
		print("Got Image:", img.shape)

		# get the image detection data
		detections = self.network.getDetections(img)
		# [boxes[ind], confidences[ind], self.labels[classID], self.colors[classID]]

		# TODO: if the detector sees something, generate a COT message
		# until then, just print things
		if len(detections) > 0:
			print("Location:", pose.position)
			for detection in detections:
				print("Objects: ", detection[2])

if __name__ == "__main__":
	detector = YoloDetector("/geo_image_input")
	while True:
		time.sleep(10)