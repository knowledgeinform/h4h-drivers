import cv2
import numpy as np

# code based on https://pyimagesearch.com/2018/11/12/yolo-object-detection-with-opencv/

class YoloNet:
	def __init__(self, config_file, weights_file, labels_file, confidence_thresh=0.4, nms_thresh=0.3):
		# init network
		self.net = cv2.dnn.readNetFromDarknet(config_file, weights_file);

		# set up the labels and colors
		self.labels = open(labels_file).read().strip().split("\n");
		self.colors = np.random.randint(0, 255, size=(len(self.labels),3), dtype="uint8");
		self.colors = [[int(c) for c in self.colors[a]] for a in range(len(self.colors))];

		# get layer names
		self.layers = self.net.getLayerNames();
		self.layers = [self.layers[i-1] for i in self.net.getUnconnectedOutLayers()];

		# set confidence and nms thresholds
		self.cthresh = confidence_thresh;
		self.nthresh = nms_thresh;

	# get detections
	def getDetections(self, img):
		# digest
		blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (416,416), swapRB=True, crop=False);
		h,w = img.shape[:2];

		# process
		self.net.setInput(blob);
		outputs = self.net.forward(self.layers);

		# get output
		boxes = [];
		confidences = [];
		classIDs = [];
		for output in outputs:
			for detection in output:
				# get class and confidence
				scores = detection[5:];
				classID = np.argmax(scores);
				confidence = scores[classID];

				# set confidence filter
				if self.cthresh < confidence:
					box = detection[0:4] * np.array([w,h,w,h]);
					(cx, cy, width, height) = box.astype("int");

					# get top-left
					sx = int(cx - (width / 2));
					sy = int(cy - (height / 2));

					# update lists
					boxes.append([sx,sy,int(width),int(height)]);
					confidences.append(float(confidence));
					classIDs.append(classID);

		# apply non-maxima suppression
		idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.cthresh, self.nthresh);

		# re-gather filtered lists
		detections = [];
		if len(idxs) > 0:
			for ind in idxs.flatten():
				x,y,w,h = boxes[ind];
				classID = classIDs[ind];
				detections.append([boxes[ind], confidences[ind], self.labels[classID], self.colors[classID]]);
		return detections;

	# draw detections on image
	def drawDetections(self, img, detections):
		# unpack detections and draw
		for detection in detections:
			# unpack
			(x,y,w,h), confidence, label, color = detection;

			# draw box
			cv2.rectangle(img, (x,y), (x+w,y+h), color, 2);

			# draw text
			confidence = round(confidence, 2);
			text = str(label) + ": " + str(confidence);
			cv2.putText(img, text, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2);
		return img;

	# get and draw the detections on the image
	def processImage(self, img):
		# get detections and draw
		detections = self.getDetections(img);
		img = self.drawDetections(img, detections);
		return img;


