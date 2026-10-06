import cv2
import math
import numpy as np

import io
import base64

from commons.utils_lib import Timer

# class manager for interactive displays
class CanvasManager:
	def __init__(self, background_img=None, width=None, height=None, mouse_callback=None):
		# mirror background image if available
		if background_img is not None:
			self.bg = background_img
			self.height, self.width = self.bg.shape[:2]
		else: # default black background with input width+height
			self.width = width
			self.height = height 
			self.bg = np.zeros((self.height,self.width,3), np.uint8)

		# set a display name
		self.display = np.copy(self.bg)
		self.window_name = "Display"
		cv2.namedWindow(self.window_name)

		# set callback
		if mouse_callback:
			cv2.setMouseCallback(self.window_name, mouse_callback)

		# set up a Timer
		self.clock = Timer()

	# run as "while" loop condition
	def top(self, wait_time=100):
		# show
		key = self.show()

		# check for quit
		if key == ord('q'):
			return False

		# refresh display
		self.refresh()
		return True

	def show(self, wait_time=100):
		cv2.imshow(self.window_name, self.display)
		return cv2.waitKey(wait_time)

	def tick(self):
		return self.clock.tick()

	def refresh(self):
		self.display = np.copy(self.bg)


# class manager for mouse events
class MouseManager:
	def __init__(self, window_name):
		# copy vars
		self.window_name = window_name

		# set up mouse trackers
		self.mouse_pos = [0,0]
		self.click_pos = [0,0]
		self.click_flag = False

		cv2.namedWindow(self.window_name)
		cv2.setMouseCallback(self.window_name, self.trackAndClick)

	def trackAndClick(self, event, x, y, flags, param):
		# track mouse
		self.mouse_pos = [x,y]

		# track click (on release)
		if event == cv2.EVENT_LBUTTONUP:
			self.click_pos = [x,y]
			self.click_flag = True

	def getMousePos(self):
		return self.mouse_pos

	def hasClick(self):
		return self.click_flag

	def getClickPos(self):
		self.click_flag = False
		return self.click_pos

# max image resizing
def resizeToLimit(img, max_width=0, max_height=0):
	h,w = img.shape[:2]
	hscale = 1 if max_height == 0 else max_height / h
	wscale = 1 if max_width == 0 else max_width / w
	rescale = min(hscale, wscale)
	if rescale < 1:
		new_width = int(w * rescale)
		new_height = int(h * rescale)
		img = cv2.resize(img, (new_width, new_height))
	return img

# does a pseudo raycast to check if a line is clear
def isUnobstructedLine(occupancy_mask, start, end):
	# find corners
	sx,sy = start
	ex,ey = end
	tx = min([sx,ex]) # top-left
	ty = min([sy,ey])
	bx = max([sx,ex]) + 1 # bottom-right
	by = max([sy,ey]) + 1

	# apply offset
	sx -= tx
	sy -= ty
	ex -= tx
	ey -= ty

	# chop out window
	window = occupancy_mask[ty:by, tx:bx]
	canvas = np.zeros_like(window)

	# draw the line
	cv2.line(canvas, [sx,sy], [ex,ey], 255, 1)

	# combine and check
	bitmask = cv2.bitwise_and(window, canvas)
	return not np.any(bitmask)

# convert image to base64
def imgToBase64(img, ftype=".jpg"):
	# convert to b64
    _, buffer_img = cv2.imencode(ftype, img)
    data = base64.b64encode(buffer_img)
    return str(data.decode('ascii'))

# convert base64 to image
def base64ToImg(bstring):
	import imageio
	
	# decode base64
	rgb_img = imageio.imread(io.BytesIO(base64.b64decode(bstring)))
	img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)
	return img

# calculates fitted axis bounds
def fitBounds(center_val, margin, minval, maxval):
	start = center_val - margin
	end = center_val + margin + 1
	return boundShift(start, end, minval, maxval)

# center-shifted bounds
def boundShift(start, end, minval, maxval):
	# null check
	if end - start > maxval - minval:
		return minval, maxval

	# right shift
	if start < minval:
		over = minval - start
		start = minval
		end += over

	# left shift
	if end > maxval:
		over = end - maxval
		end = maxval
		start -= over
	return start, end

# crop bounded view window
def viewWindow(canvas, center, res):
	# unpack vars
	x,y = center
	vw,vh = res
	vwh = int(vw / 2)
	vhh = int(vh / 2)
	ch,cw = canvas.shape[:2]

	# get corners
	sx, ex = fitBounds(x, vwh, 0, cw)
	sy, ey = fitBounds(y, vhh, 0, ch)

	# return crop
	return canvas[sy:ey, sx:ex]
        
# fast draw text (bottom-left positioned, the documentation is lying)
def drawText(img, pos, text, font=cv2.FONT_HERSHEY_SIMPLEX, scale=1, 
	color=(255,255,255), thickness = 1, lineType=cv2.LINE_AA):
	x,y = pos
	cv2.putText(img, text, (x,y), font, scale, color, thickness, lineType);

# slow draw text centered
def drawTextCentered(img, pos, text, font=cv2.FONT_HERSHEY_SIMPLEX, scale=1, 
	color=(255,255,255), thickness = 1, lineType=cv2.LINE_AA, bottomAlign=False):
	# create a dummy box
	px = 50;
	py = 100;
	bg = np.zeros((200, 1600, 1), np.uint8); # remember (y,x,channels)
	drawText(bg, pos=(px,py), text=text, font=font, scale=scale, color=255, thickness=thickness, lineType=lineType);

	# get bounding rect
	pix = np.nonzero(bg);
	points = [];
	for a in range(len(pix[0])):
		y = pix[0][a];
		x = pix[1][a];
		points.append([[x,y]]);
	points = np.array(points);
	x,y,w,h = cv2.boundingRect(points);

	# calculate center
	cx = int(x + w/2);
	cy = int(y + h/2);
	if bottomAlign:
		cy = int(y+h);
	
	# calculate offset
	ox = cx - px;
	oy = cy - py;

	# draw centered
	x,y = pos;
	new_pos = (x-ox, y-oy);
	drawText(img, pos=new_pos, text=text, font=font, scale=scale, color=color, thickness=thickness, lineType=lineType);

# color hasher
def colorHash(color):
	hashstr = "";
	for channel in color:
		hashstr += str(channel).zfill(3);
	return hashstr;

# color unhash
def unhashColor(colorHash):
	color = [];
	for a in range(0, len(colorHash), 3):
		color.append(int(colorHash[a:a+3]));
	return color;

# color distance measurements
def colorEuclidDist(c1, c2):
	dist = 0
	for a in range(len(c1)):
		diff = c1[a] - c2[a];
		diff *= diff;
		dist += diff;
	return math.sqrt(dist)

# custom color diff that de-emphasizes changes in brightness (color focused)
def lessLightColorDist(c1, c2):
	dist = 0;
	dist += int(abs(c1[0] - c2[0]) / 10);
	dist += abs(c1[1] - c1[1]);
	dist += abs(c1[2] - c2[2]);
	return dist;

# a faster palettizer
def palettize(img, margin=10):
	# convert to LAB
	lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB);
	height, width = lab.shape[:2];

	# create a color list
	colors = {};
	for y in range(height):
		for x in range(width):
			color = lab[y,x];
			chash = colorHash(color);
			if not chash in colors:
				colors[chash] = [];
			colors[chash].append([x,y]);

	# palettize the colors
	palette = [];
	for color in colors:
		# check if the color is already in the palette
		color = unhashColor(color);
		new_color_flag = True;
		for smear in palette:
			if lessLightColorDist(smear, color) <= margin:
				new_color_flag = False;
				break;

		# add to palette
		if new_color_flag:
			palette.append(color);

	# convert the colors back to bgr
	canvas = np.zeros((1,len(palette),3), np.uint8);
	for a in range(len(palette)):
		canvas[0][a] = palette[a];
	canvas = cv2.cvtColor(canvas, cv2.COLOR_LAB2BGR);
	colors = [];
	for x in range(len(palette)):
		colors.append(canvas[0][x]);
	return colors;

# palette mapping
def paletteMap(img, palette):
	# convert to LAB
	lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB);
	height, width = lab.shape[:2]; 

	# convert palette to LAB
	transfer = np.zeros((1,len(palette),3), np.uint8);
	for x in range(len(palette)):
		transfer[0,x] = palette[x];
	transfer = cv2.cvtColor(transfer, cv2.COLOR_BGR2LAB);
	palette = [];
	for x in range(transfer.shape[1]):
		palette.append(transfer[0,x]);

	# create a color list
	colors = {};
	for y in range(height):
		for x in range(width):
			color = lab[y,x];
			chash = colorHash(color);
			if not chash in colors:
				colors[chash] = [];
			colors[chash].append([x,y]);

	# remap the colors
	for key in colors:
		# get closest remap
		color = unhashColor(key);
		best_score = 9999999999;
		best_smear = None;
		for smear in palette:
			score = lessLightColorDist(color, smear);
			if score < best_score:
				best_score = score;
				best_smear = smear;

		# remap the color
		for pos in colors[key]:
			x,y = pos;
			lab[y,x] = best_smear;

	# convert back to bgr
	remapped = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR);
	return remapped;

def blit(canvas, img, pos, mode="normal"):
	# get canvas dims
	ch, cw = canvas.shape[:2];

	# get image dims
	ih, iw = img.shape[:2];
	hh = int(ih/2);
	hw = int(iw/2);

	# calculate bounds
	x,y = pos;

	sx = x - hw;
	sy = y - hh;
	ex = x + hw+1;
	ey = y + hh+1;

	# adjust
	left = 0;
	if sx < 0:
		left += abs(sx);
		sx = 0;

	right = iw;
	if ex > cw:
		right -= ex - cw;
		ex = cw;

	top = 0;
	if sy < 0:
		top += abs(sy);
		sy = 0;

	bottom = ih;
	if ey > ch:
		bottom -= ey - ch;
		ey = ch;

	# finally blit
	if mode == "normal":
		canvas[sy:ey, sx:ex] = img[top:bottom, left:right];
	elif mode == "max":
		canvas[sy:ey, sx:ex] = maxBlit(canvas[sy:ey, sx:ex], img[top:bottom, left:right]);
	elif mode == "add":
		canvas[sy:ey, sx:ex] = addBlit(canvas[sy:ey, sx:ex], img[top:bottom, left:right]);
	else:
		print("INVALID MODE:", mode, "FOR BLIT()"); 

def maxBlit(left, right):
	return np.maximum(left, right);

def addBlit(left, right):
	return np.add(left, right);

def alphaMaxOverlay(background, foreground, mask):
	# prep the foreground mask
	foreground[mask != 255] = background[mask != 255]

	# set the alpha channel
	alpha = mask.astype(np.float32) / 255.0

	# multiply
	foreground = cv2.multiply(alpha, foreground)
	background = cv2.multiply(1.0-alpha, background)
	return cv2.add(foreground, background)

if __name__ == "__main__":
	img = cv2.imread("test.png");
	colors = palettize(img, margin=20);
	canvas = np.zeros((100,100,3), np.uint8);
	for color in colors:
		print(color);
		canvas[::] = color;
		cv2.imshow("Color", canvas);
		cv2.waitKey(0);

	# remap back
	remapped = paletteMap(img, colors);
	cv2.imshow("Original", img);
	cv2.imshow("Remapped", remapped);
	cv2.waitKey(0);

