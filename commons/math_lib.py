import math
import numpy as np

def slicer(corners:list, length_uvec:list, width_uvec:list, spacing:float) -> list:
	""" WARNING: UNFINISHED """

	# start at the first point
	curr_point = corners[0][:]

	spacing_vec = width_uvec[:]
	# scale2D(spacing_vec, spacing)

	long_vec = length_uvec[:]
	scale2D(long_vec, 1000)

	# store up all the intersection points
	intersections = []
	midpoints = []

	# arbitrarily loop 100 times
	for a in range(100):
		# shift the center point further down
		translate2D(curr_point, spacing_vec)
		temp = curr_point[:]
		intify(temp)
		midpoints.append(temp)
		print("A:", a)

		# generate the line by extending far out in either direction # not really necessary, clean up later
		start_point = curr_point[:]
		translate2D(start_point, long_vec)
		end_point = curr_point[:]
		translate2D(end_point, long_vec, -1)

		# calculate out the intersection for every line segment
		for b in range(len(corners)):
			p1 = corners[b-1][:]
			p2 = corners[b][:]
			intersection = lineIntersect([start_point,end_point], [p1,p2])
			print("Intersection:", intersection)
			if intersection is not None:
				# check if intersection is on the polygon line
				if not overEndOfLine(intersection, p1, p2):
					intify(intersection)
					intersections.append(intersection)
	return intersections, midpoints
		

def lineIntersect(line1, line2):
	# unpack
	start1, end1 = line1
	start2, end2 = line2

	xdiff = [start1[0]-end1[0], start2[0]-end2[0]]
	ydiff = [start1[1]-end1[1], start2[1]-end2[1]]

	def det(p1, p2):
		return p1[0]*p2[1] - p1[1]*p2[0]
	
	# if lines are parallel, return None
	div = det(xdiff, ydiff)
	if div == 0:
		return None

	# find intersection
	d = [det(start1,end1), det(start2,end2)]
	x = det(d, xdiff) / div
	y = det(d, ydiff) / div
	return [x,y]


def lawnmowerPath(corners:list, spacing_m:float) -> list:
	"""
	WARNING: UNFINISHED
	generates a lawn mower pattern

	corners:
		- a list of four 2d points [x,y] where the first point is the start
		  and the second point indicates longwise direction
	spacing_m:
		- the amount of space between each row
	"""
	length_uvec = unitVector(diffVector(corners[0], corners[1]))
	
	# calculate the perpendicular vector in the direction of the 3rd point
	mid_angle = signedAngle3P(corners[0],corners[1],corners[2])
	print("Angle to 3rd:", mid_angle)

	turn_angle = 90
	if mid_angle > 0:
		turn_angle = -90

	width_uvec = length_uvec[:]
	rotate2D(width_uvec, turn_angle)
	width_uvec = unitVector(width_uvec)

	# now start plotting intersection points
	intersect_points = [corners[0], corners[1]] # assume the points form a polygon, this should always be the first line


	# DEBUG: stretch both of the vectors and shift onto the first point
	scale2D(length_uvec, 100)
	scale2D(width_uvec, 100)
	translate2D(length_uvec, corners[0])
	translate2D(width_uvec, corners[0])
	intify(length_uvec)
	intify(width_uvec)

	return length_uvec, width_uvec
	


# rescale numeric range from [-1,1] to [-1,-DEADZONE] ~ [DEADZONE,1] and back to [-1,1]
def applyDeadzone(normed_value, deadzone):
	if abs(normed_value) <= deadzone:
		normed_value = 0
	else:
		normed_value -= sign(normed_value) * deadzone
		normed_value /= (1.0 - deadzone)
	return normed_value

def getCorners(img, pos, radius):
	# unpack corners
	x,y = pos
	sx = x - radius
	ex = x + radius
	sy = y - radius
	ey = y + radius

	# clamp to edges
	h,w = img.shape[:2]
	sx = clamp(sx, 0, w)
	ex = clamp(ex, 0, w)
	sy = clamp(sy, 0, h)
	ey = clamp(ey, 0, h)
	return sx,sy,ex,ey

def createBlob(max_range, max_val = 255):
	# dimensions
	width = max_range*2 + 1;
	height = max_range*2 + 1;
	center = [max_range, max_range];

	# create canvas
	blob = np.zeros((height,width), np.uint8);

	# assign scores
	for y in range(height):
		for x in range(width):
			# calculate score
			dist = dist2D([x,y], center);
			score = 0;
			if dist < max_range:
				score = linearReframe(dist, 0, max_range, 0, max_val);
				score = max_val - score;
				score = int(score);
			blob[y,x] = score;
	return blob;

# manhatten distance
def manHatDist(p1, p2):
	total = 0
	for a in range(len(p1)):
		total += abs(p1[a]-p2[a])
	return total

# maps value from [min1, max1] -> [min2, max2]
def linearReframe(value, min1, max1, min2, max2):
	value -= min1
	value /= (max1-min1)
	value *= (max2-min2)
	value += min2
	return value

# simplifier for linearReframe [-range1, range1] -> [-range2, range2]
def rangeShift(value, range1, range2):
	return linearReframe(value, -range1, range1, -range2, range2)

def mag(vec):
	return math.sqrt(vec[0]*vec[0] + vec[1]*vec[1])

def unitVector(vec):
	vx, vy = vec
	dist = mag(vec)
	vx /= dist
	vy /= dist
	return [vx,vy]

def dot(vec1, vec2):
	return vec1[0] * vec2[0] + vec1[1] * vec2[1]


# start, middle, end
# returns the shortest angle # no sense of directionality
def angle3P(start, middle, end):
	# convert to vectors
	front = [middle[0] - start[0], middle[1] - start[1]]
	back = [end[0] - middle[0], end[1] - middle[1]]

	# dot product
	dot_product = dot(front, back)

	# get magnitudes
	mag_front = mag(front)
	mag_back = mag(back)

	# get angle
	angle = math.acos(dot_product/mag_back/mag_front)
	return 180 - math.degrees(angle)

def signedAngle3P(start, middle, end) -> float:
	""" returns the signed angle formed by start->middle->end """
	vec_a = diffVector(middle, start)
	vec_b = diffVector(middle, end)
	
	# (x1y2 − y1x2,  x1x2 + y1y2)
	dy = vec_a[0]*vec_b[1] - vec_a[1]*vec_b[0]
	dx = vec_a[0]*vec_b[0] + vec_a[1]*vec_b[1]
	return math.degrees(math.atan2(dy, dx))


def positiveAngle(value):
	return value % 360
	# if value < 0:
	# 	value += 360
	# return value

def angleInRange(value, left, right):
	# make all positive
	value = positiveAngle(value)
	left = positiveAngle(left)
	right = positiveAngle(right)

	# check for wraparound
	if left > right:
		if value < right:
			value += 360
		right += 360
	return left <= value and value <= right

# returns the shortest angle diff (a2 - a1)
def shortestAngleDiff(a1, a2):
	dt = a2 - a1
	pos = dt%360
	neg = dt%-360

	if abs(pos) < abs(neg):
		return pos
	else:
		return neg

# returns the angle from p1 -> p2
def angleTo(p1, p2, convertForUTM=False):
	dx,dy = diffVector(p1,p2)
	angle_deg = math.degrees(math.atan2(dy,dx))

	# check for UTM (Easting, Northing) conversion
	if convertForUTM:
		angle_deg = angle_deg - 90
	return angle_deg

# returns difference vector from p1 -> p2
def diffVector(p1, p2):
	dx = p2[0] - p1[0];
	dy = p2[1] - p1[1];
	return [dx,dy]

# returns the projection of a point onto a line
def pointToLine(point, start, end, clamp_to_line=True):
	# numpify it all
	point = np.array(point)
	start = np.array(start)
	end = np.array(end)

	# get the vectors
	front = point - start
	line = end - start

	# proportional distance along the line
	dt = np.dot(front, line) / np.dot(line, line)

	# clamp to line
	if clamp_to_line:
		dt = clamp(dt, 0, 1)

	# project
	proj_point = start + (dt * line)

	# turn it back into a list
	x = proj_point[0]
	y = proj_point[1]
	return x,y

# signs left or right of a point to a line
# https://stackoverflow.com/questions/1560492/how-to-tell-whether-a-point-is-to-the-right-or-left-side-of-a-line
# sign((Bx - Ax) * (Y - Ay) - (By - Ay) * (X - Ax))
def signOfPointToLine(point, start, end):
	return sign((end[0] - start[0]) * (point[1] - start[1]) - (end[1] - start[1]) * (point[0] - start[0]))

# return True if projected point is not on the line segment
def overEndOfLine(point, start, end):
	# numpify it all
	point = np.array(point)
	start = np.array(start)
	end = np.array(end)

	# get the vectors
	front = point - start
	line = end - start

	# proportional distance along the line
	dt = np.dot(front, line) / np.dot(line, line)
	not_on_line = dt > 1.0 or dt < 0
	return not_on_line


# returns the perpendicular distance of a point to a line
def crossTrackDistance(point, start, end, clamp_to_line=False):
	projected_point = pointToLine(point, start, end, clamp_to_line)
	return dist2D(point, projected_point) * signOfPointToLine(point, start, end)

# returns the point a certain proportion along the line
def travelPropOnLine(proportion, start, end):
	# get the travel step
	sx, sy = start
	ex, ey = end

	dx = ex - sx
	dy = ey - sy

	dx *= proportion
	dy *= proportion

	# move
	return [sx + dx, sy + dy]
	

# returns the point a certain distance along the line
def travelOnLine(distance, start, end):
	prop = distance / dist2D(start, end)
	return travelPropOnLine(prop, start, end)

# returns rounded integer point positions
def intify(point):
	point[0] = int(point[0] + 0.5);
	point[1] = int(point[1] + 0.5);
	return point

# return sign of diff (first - second)
# -1 is less than
# 1 is greater than
# 0 is equal to
def diffSign(first, second):
	dx = first - second;
	return sign(dx);

def sign(value):
	if value > 0:
		return 1;
	if value < 0:
		return -1;
	return 0;

# scales a 2d point (direct multiplication)
def scale2D(point, scale):
	point[0] = point[0] * scale;
	point[1] = point[1] * scale;

# translate 2d point in-place
def translate2D(point, shift, sign=1):
	x = point[0] + (shift[0] * sign);
	y = point[1] + (shift[1] * sign);
	point[0] = x;
	point[1] = y;

# rotate a 2d point in-place
def rotate2D(point, angle_deg, anchor=[0,0]):
	rads = math.radians(angle_deg);
	translate2D(point, anchor, sign=-1);
	x,y = point;
	rx = x * math.cos(rads) - y * math.sin(rads);
	ry = x * math.sin(rads) + y * math.cos(rads);
	point[0] = rx;
	point[1] = ry;
	translate2D(point, anchor, sign=1);

# moves a point to a new origin frame
def pointToFrame(point, pos, angle, no_round=False):
	rotate2D(point, angle)
	translate2D(point, pos)
	if not no_round:
		intify(point)

# distance between two points
def dist2D(p1, p2):
	dx = p1[0] - p2[0];
	dy = p1[1] - p2[1];
	return math.sqrt(dx*dx + dy*dy);

# squared distance between two points
def distSquared2D(p1, p2):
	dx = p1[0] - p2[0]
	dy = p1[1] - p2[1]
	return dx*dx + dy*dy

# saturates value [low, high]
def clamp(value, low, high):
	if value < low:
		return low
	if value > high:
		return high
	return value

# saturates value (reflective)
def saturate(value, sat):
	return clamp(value, -sat, sat)