import os
import cv2
import time
import numpy as np

# records videos using opencv
class Recorder:
	def __init__(self, filename, width, height, framerate):
		fourcc = cv2.VideoWriter_fourcc('M','J','P','G');
		self.recorder = cv2.VideoWriter(filename, fourcc, framerate, (width, height));

	# save a frame
	def write(self, img):
		self.recorder.write(img);

	# close recording
	def close(self):
		self.recorder.release();

# abstract class for camera captures
# parrots the interface of OpenCV's VideoCapture
class Camera:
	def __init__(self, name = "DEFAULT", max_fps=10, res = None):
		# camera name
		self.name = name;

		# last image
		self.img = None;
		self.fresh = False;

		# state a preferred fps for threads
		self.max_fps = max_fps;

		# automatically resize image if set
		self.resize_res = res;

		# automatically apply pre-processing to image
		self.preprocess_func = None;

	# make thread compatible
	def run(self):
		self.grab();

	# sets a preprocessing step to apply to images
	def setPreprocess(self, func):
		self.preprocess_func = func;

	# grab an image
	def grab(self):
		raise NotImplementedError;

	# preps an image for return
	def prep(self):
		# make a copy
		img = np.copy(self.img);

		# resize if needed
		if self.resize_res is not None:
			img = cv2.resize(img, self.resize_res);

		# apply preprocessing step
		if self.preprocess_func is not None:
			img = self.preprocess_func(img);
		return img;

	# retrieves an image without resetting the fresh flag
	def retrieveCopy(self):
		img = self.prep();
		return (img is not None and img.size > 1), img;

	# retrieves an image
	def retrieve(self):
		img = self.prep();
		flag = self.fresh;
		self.fresh = False;
		return flag, img;

	# return the image
	def read(self):
		# get a new image
		self.fresh = False;
		self.grab();

		# return early if no good image
		if not self.fresh:
			return self.fresh, self.img;

		# process and pass new image
		return self.retrieve();


class MultiProcessorCamera(Camera):
	" pulls image from multiprocessor shared memory "
	def __init__(self, sharedmem_name:str, width:int, height:int, channels:int,
			  name:str = "MultiProcessorCamera", max_fps:int=30, res:tuple[int,int]=None):
		super(MultiProcessorCamera, self).__init__(name=name, max_fps=max_fps, res=res)

		# import multiprocessing
		from multiprocessing import shared_memory

		# calculate shape
		nshape = (height,width,channels)
		if channels == 1:
			nshape = (height,width)

		# set up a shared memory link
		self.sharedmem = shared_memory.SharedMemory(name=sharedmem_name)
		self.img_ref = np.ndarray(
			shape=nshape,
			dtype=np.uint8,
			buffer=self.sharedmem.buf
		)

	def grab(self):
		self.img = np.copy(self.img_ref)

		# print("**** shape", self.img_ref.shape)
		# print("**** mean", self.img_ref.mean())
		# cv2.imshow("Debug", self.img)
		# cv2.waitKey(1)

		self.fresh = True


# treats a folder of images as a camera source
class FolderCamera(Camera):
	def __init__(self, folder, step = 1, loop = False, name = "FolderCamera", max_fps=30, res = None):
		super(FolderCamera, self).__init__(name=name, max_fps=max_fps, res=res);

		# get list of filenames
		self.folder = folder;
		self.files = os.listdir(self.folder);
		self.size = len(self.files);

		# indexing
		self.index = 0;
		self.step = step;

		# should the "camera" loop at end
		self.loop = loop;
		self.end = False;

	# OVERRIDE
	def grab(self):
		# check for end
		if self.index >= self.size:
			if self.loop:
				self.index = 0;
			else:
				self.end = True;
				return;

		# get image
		self.img = cv2.imread(self.folder + "/" + self.files[self.index]);
		self.fresh = True;
		self.index += self.step;


# interface for a typical usb camera (and laptop webcam on port 0)
class USBCamera(Camera):
	def __init__(self, portnum = 0, name = "USBCamera", res = None):
		super(USBCamera, self).__init__(name=name, res=res);
		self.cap = cv2.VideoCapture(int(portnum));

	# OVERRIDE
	def grab(self):
		ret, frame = self.cap.read();
		if ret:
			self.img = frame;
			self.fresh = True;

# interface for using an Oak Camera (DepthAI) as a normal rgb camera
try:
	import depthai as dai
	class DaiCamera(Camera):
		def __init__(self, width=960, height=540, name = "DaiCamera", max_fps=45, res = None):
			super(DaiCamera, self).__init__(name=name, max_fps=max_fps, res=res);

			# set up basic pipeline
			self.pipeline = dai.Pipeline();

			# set up camera
			self.cam = self.pipeline.create(dai.node.ColorCamera);
			self.cam.setPreviewSize(width, height);
			self.cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P);
			self.cam.setInterleaved(False);

			# set up output node
			self.xout = self.pipeline.create(dai.node.XLinkOut);
			self.xout.setStreamName("rgb");
			self.cam.preview.link(self.xout.input);

			# set up the device and queue
			self.device = dai.Device(self.pipeline);
			self.rgb_q = self.device.getOutputQueue("rgb");
			time.sleep(0.5);

		# OVERRIDE
		def grab(self):
			frame = self.rgb_q.get();
			if frame is not None:
				self.img = frame.getCvFrame();
				self.fresh = True;

	class DaiYoloCamera(Camera):
		def __init__(self, 
			yoloBlob, 
			labelNames, 
			confidence=0.5,
			iou=0.5,
			width=1920, 
			height=1080, 
			name = "DaiYoloCamera", 
			max_fps=30, 
			res = None,):
			super(DaiYoloCamera, self).__init__(name=name, max_fps=max_fps, res=res);

			# labels
			self.labels = labelNames

			# frame and detection buffer
			self.frame = None
			self.detections = None

			# set up basic pipeline
			self.pipeline = dai.Pipeline()

			# set up camera
			self.cam = self.pipeline.create(dai.node.ColorCamera)
			self.cam.setPreviewSize(416, 416) # hardcoded for yolo
			self.cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
			self.cam.setInterleaved(False)
			self.cam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
			self.cam.setFps(max_fps)

			# init yolo
			self.yoloNet = self.pipeline.create(dai.node.YoloDetectionNetwork)
			self.cam.preview.link(self.yoloNet.input)

			# yolo network settings
			self.yoloNet.setConfidenceThreshold(confidence)
			self.yoloNet.setNumClasses(len(self.labels))
			self.yoloNet.setCoordinateSize(4)
			self.yoloNet.setAnchors([10, 14, 23, 27, 37, 58, 81, 82, 135, 169, 344, 319])
			self.yoloNet.setAnchorMasks({"side26": [1, 2, 3], "side13": [3, 4, 5]})
			self.yoloNet.setIouThreshold(iou)
			self.yoloNet.setBlobPath(yoloBlob)
			self.yoloNet.setNumInferenceThreads(2)
			self.yoloNet.input.setBlocking(False)

			# init yolo out link
			self.yoloOut = self.pipeline.create(dai.node.XLinkOut)
			self.yoloOut.setStreamName("yolo")
			self.yoloNet.out.link(self.yoloOut.input)

			# full-res output link
			self.imageOut = self.pipeline.create(dai.node.XLinkOut)
			self.imageOut.setStreamName("cameraToImage")
			self.cam.video.link(self.imageOut.input)

			# set up the device and queue
			self.device = dai.Device(self.pipeline);
			self.qImage = self.device.getOutputQueue(name="cameraToImage")
			self.qYolo = self.device.getOutputQueue(name="yolo")
			time.sleep(0.5);

		# nn data, being the bounding box locations, are in <0..1> range - they need to be normalized with frame width/height
		def frameNorm(self, frame, bbox):
			normVals = np.full(len(bbox), frame.shape[0])
			normVals[::2] = frame.shape[1]
			return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)

		def drawDetections(self, frame, detections):
			color = (255, 0, 0)
			for detection in detections:
				bbox = self.frameNorm(frame, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
				cv2.putText(frame, self.labels[detection.label], (bbox[0] + 10, bbox[1] + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
				# cv2.putText(frame, f"{int(detection.confidence * 100)}%", (bbox[0] + 10, bbox[1] + 40), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
				cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
			return frame

		# OVERRIDE
		def grab(self):
			# pull
			newData = False
			imgData = self.qImage.tryGet()
			yoloData = self.qYolo.tryGet()

			# update buffers
			if imgData is not None:
				self.frame = imgData.getCvFrame()
				newData = True
			if yoloData is not None:
				self.detections = yoloData.detections
				newData = True

			# draw the new frame
			if newData and self.frame is not None and self.detections is not None:
				self.img = self.drawDetections(self.frame, self.detections)
				self.fresh = True

except Exception as e:
	print("Exception importing depthai: ", str(e));
	print("Warning: DaiCamera won't be available");
	class DaiCamera(Camera):
		def __init__(self, camera_id, max_fps=5, res=None):
			super(DaiCamera, self).__init__(name = camera_id, max_fps=max_fps, res=res);
			print("WARNING: DaiCamera is not Available, you'll get nothing from this camera");

		def grab(self):
			return False;

# gets images from a REST api (or any online image source)
try:
	import requests
	class RESTCamera(Camera):
		def __init__(self, url, max_fps=5, res=None):
			super(RESTCamera, self).__init__(name = url, max_fps=max_fps, res=res);

			# url string
			self.url = url;

		# OVERRIDE
		def grab(self):
			res = requests.get(self.url, stream=True);
			if res.status_code == 200:
				nump_img = np.frombuffer(res.content, np.uint8);
				img = cv2.imdecode(nump_img, cv2.IMREAD_COLOR);
				self.img = img;
				self.fresh = True;

except Exception as e:
	print("Exception importing astlib: ", str(e));
	print("Warning: RESTCamera won't be available");
	class RESTCamera(Camera):
		def __init__(self, camera_id, max_fps=5, res=None):
			super(RESTCamera, self).__init__(name = camera_id, max_fps=max_fps, res=res);
			print("WARNING: RESTCamera is not Available, you'll get nothing from this camera");

		def grab(self):
			return False;

# get images from the AST Client
try:
	import astlib as ast
	class ASTCameraClient(Camera):
		def __init__(self, camera_id, max_fps=5, res=None):
			super(ASTCameraClient, self).__init__(name = camera_id, max_fps=max_fps, res=res);

			# set up client
			self.client = ast.client.Client('lc-farnsworth', client_id='daemon');
			self.camera = camera_id;

		# OVERRIDE
		def grab(self):
			results = self.client.get_latest_results_multiple('spidrlab', self.camera, ['ast-analytic-fast-mot'], sync=False);
			if results is not None and len(results) >= 2 and results[0] is not None and results[1] is not None:
				self.img = self.client.visualize(results);
				if self.img is not None and self.img.size > 1:
					self.fresh = True;
				return True;
			return False;

except Exception as e:
	print("Exception importing astlib: ", str(e));
	print("Warning: ASTCameraClient won't be available");
	class ASTCameraClient(Camera):
		def __init__(self, camera_id, max_fps=5, res=None):
			super(ASTCameraClient, self).__init__(name = camera_id, max_fps=max_fps, res=res);
			print("WARNING: ASTCameraClient is not Available, you'll get nothing from this camera");

		def grab(self):
			return False;


class SequentialFolderCamera(Camera):
	def __init__(self, folder, camera_id, max_fps=15, skip=1, debug_log=False, res=None):
		super(SequentialFolderCamera, self).__init__(name = camera_id, max_fps=max_fps, res=res);

		# pull list of everything in input
		files = os.listdir(folder);
		self.files = [folder + file for file in files];

		# skips for videos
		self.skip = skip;

		# debug output flag
		self.debug = debug_log;
		self.finish_once = False;

		# prepare a camera for each
		self.current_index = 0;
		self.cam = None;

		# tile buffer
		self.tile_width = 1920;
		self.tile_height = 1080;
		self.tiles = [];
		self.tiles_on = True;

		# frame counter
		self.frame_count = 0;

	# image "camera"
	class ImageCam:
		def __init__(self, filename):
			self.filename = filename;

		def read(self):
			img = cv2.imread(self.filename);
			if img is None:
				return False, img, True;
			else:
				return True, img, True;

	# video file "camera"
	class VideoCam:
		def __init__(self, filename, skip):
			self.cap = cv2.VideoCapture(filename);
			self.skip = skip;
			self.frame_count = 0;

		def read(self):
			ret, frame = self.cap.read();
			self.frame_count += 1;
			# print("Frame Read: ", self.frame_count);
			for a in range(self.skip-1):
				_,_ = self.cap.read();
			return ret, frame, not ret;

	# make tiles
	def makeTiles(self, img):
		h,w = img.shape[:2];
		if h > self.tile_height or w > self.tile_width:
			columns = w / self.tile_width;
			if columns > int(columns):
				columns = int(columns) + 1;
			else:
				columns = int(columns);

			rows = h / self.tile_height;
			if rows > int(rows):
				rows = int(rows) + 1;
			else:
				rows = int(rows);

			for x in range(columns):
				for y in range(rows):
					sx = x * self.tile_width;
					sy = y * self.tile_height;
					ex = (x+1) * self.tile_width;
					ey = (y+1) * self.tile_height;
					ex = min(ex, w);
					ey = min(ey, h);
					self.tiles.append(np.copy(img[sy:ey,sx:ex]))
		else:
			self.tiles.append(np.copy(img));

	# get an image
	# OVERRIDE
	def grab(self):
		# check if image is still fresh
		if self.fresh:
			return True;

		# check for tiles
		if self.tiles_on and len(self.tiles) > 0:
			self.img = self.tiles.pop();
			self.fresh = True;
			return True;

		# generate a new camera
		if self.cam is None:
			self.makeCamera();
			if self.cam is None:
				if not self.finish_once:
					self.finish_once = True;
					if self.debug:
						print("Finished");
				return False;

		# grab an image
		ret, img, finished = self.cam.read();
		if ret:
			# check the image for tiling
			if self.tiles_on:
				self.makeTiles(img);
				self.img = self.tiles.pop();
				self.fresh = True;
			else:
				self.img = img;
				self.fresh = True;
		if finished:
			self.cam = None;
		return ret;

	# create a camera
	def makeCamera(self):
		# check filename suffixes
		if self.current_index >= len(self.files):
			return;
		filename = self.files[self.current_index];
		self.current_index += 1;
		_,suffix = filename.split(".");

		# debug output
		if self.debug:
			print(filename);
			print(self.current_index, "of", len(self.files));

		# create camera
		if suffix.lower() in ["png", "jpg", "jpeg", "bmp", "tiff", "tif"]:
			self.cam = SequentialFolderCamera.ImageCam(filename);
		else:
			self.cam = SequentialFolderCamera.VideoCam(filename, self.skip);

	


if __name__ == "__main__":
	# create camera for testing
	cam = RESTCamera("http://lc-calculon:5000/image/camera-w2-ptz", res=(340,200));
	# cam = USBCamera(0);

	# show images
	while cv2.waitKey(1) != ord('q'):
		ret, frame = cam.read();
		if ret:
			cv2.imshow("Frame", frame);