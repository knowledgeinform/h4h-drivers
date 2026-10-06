
### DEPRECATED !!! ###

import math
import time

import rclpy
from rclpy.node import Node

from cv_bridge import CvBridge


from sensor_msgs.msg import Image, NavSatFix
from geometry_msgs.msg import TwistStamped, Twist, Vector3


from commons.thread_lib import SimpleThread, ThreadStopper
from commons.camera_lib import Camera

# init by default
rclpy.init()

# set up a shared CvBridge
ros2_lib_cvbridge = CvBridge()

def shutdown():
    rclpy.shutdown()

### Subscribers ###

class RosMultiSubscriber:
    def __init__(self):
        self.ready = False
        self.readyup()

    def readyup(self):
        if not self.ready:
            self.executor = rclpy.executors.MultiThreadedExecutor()
            self.stopper = ThreadStopper()
            self.thread = SimpleThread(
                yield_time=1.0, # doesn't matter here
                runner=self,
                stopper=self.stopper)
            self.thread.start()
            self.ready = True

    def addNode(self, node):
        self.executor.add_node(node)

    def run(self):
        self.executor.spin()

    def stop(self):
        self.stopper.stop()

RosSubscriberHandler = RosMultiSubscriber()

class RosSubscriber(Node):
    def __init__(self, node_name, msg_type, rostopic, callback, namespace=None, callback_group=None):
        super().__init__(node_name, namespace=namespace)
        
        # create a default quality of service policy
        qos_policy = rclpy.qos.QoSProfile(
            reliability=rclpy.qos.ReliabilityPolicy.BEST_EFFORT,
            history=rclpy.qos.HistoryPolicy.KEEP_LAST,
            depth=5)

        # create subscription
        self.subscription = self.create_subscription(
            msg_type, 
            rostopic, 
            callback, 
            qos_profile=qos_policy, 
            callback_group=callback_group)

        # copy metadata
        self.type = msg_type
        self.topic = self.subscription.topic_name
        print(node_name, "Subscribed to", self.topic)

        # register with subscriber thread
        global RosSubscriberHandler
        RosSubscriberHandler.addNode(self)

    def callback(self):
        raise NotImplementedError

class TwistControlSubscriber(RosSubscriber):
    def __init__(self, control_hook, namespace=None):
        super().__init__(
            node_name="Twist",
            msg_type=Twist,
            rostopic="cmd_vel",
            callback=self.callback,
            namespace=namespace)
        self.control = control_hook

    def callback(self, msg):
        self.control[0] = msg.linear.x
        self.control[1] = math.degrees(msg.angular.z)

class TwistSubscriber(RosSubscriber):
    def __init__(self, callback, topic="cmd_vel", namespace=None):
        super().__init__(
            node_name = "TwistSubscriber",
            msg_type = Twist,
            rostopic = topic,
            callback = callback,
            namespace = namespace)

class NavSatFixSubscriber(RosSubscriber):
    def __init__(self, topic, callback=None, namespace=None):
        # only import if in use
        import utm

        # look for custom callback
        if callback is None:
            callback = self.callback

        super().__init__(
            node_name = "NavSatFixSubscriber",
            msg_type = NavSatFix,
            rostopic = topic,
            callback = callback,
            namespace = namespace)

        # set up local store
        self.lat = 0.0
        self.lon = 0.0
        self.northing_m = 0.0
        self.easting_m = 0.0
        self.gps_fix = False

    def callback(self, msg):
        # this second import is for scope
        import utm

        # look for satellite fix
        self.gps_fix = msg.status.status
        self.gps_fix = True # DEBUG DEBUG DEBUG # for some reason msg.status.status is never true for V60
        if not self.gps_fix:
            return

        # pull lat lon
        self.lat = msg.latitude
        self.lon = msg.longitude

        # convert to UTM
        easting, northing, zone_number, zone_letter = utm.from_latlon(self.lat, self.lon)
        self.easting_m = easting
        self.northing_m = northing

class GeoPathSubscriber(RosSubscriber):
    def __init__(self, topic, callback=None, namespace=None):
        # only import if this class is in use
        import utm
        from geographic_msgs.msg import GeoPath

        # keep a local copy of the latest path (in UTM coordinates)
        self.path = []
        self.fresh = False

        # look for custom callback
        if callback is None:
            callback = self.callback

        super().__init__(
            node_name = "GeoPathSubscriber",
            msg_type = GeoPath,
            rostopic = topic,
            callback = callback,
            namespace = namespace)

    def pullPath(self):
        if self.fresh:
            self.fresh = False
            return self.path[:]
        return None

    def callback(self, msg):
        # this second import is for scope
        import utm
        
        # decode the message
        self.path = []
        for pose in msg.poses:
            # pull latitude and longitude of each pose
            lat = pose.pose.position.latitude
            lon = pose.pose.position.longitude

            # convert to UTM
            easting, northing, zone_number, zone_letter = utm.from_latlon(lat, lon)

            # save in path
            self.path.append([easting, northing])
        self.fresh = True

        print("GeoPathSubscriber got a new path:", self.path)


class ImageSubscriber(RosSubscriber):
    def __init__(self, topic, callback=None, namespace=None):
        # keep local copy of image
        self.img = None
        self.fresh = False

        # check callback override
        if callback is None:
            callback = self.callback
            print("Using Own Callback")
        else:
            print("Using Custom Callback")

        super().__init__(
            node_name = "ImageSubscriber",
            msg_type = Image,
            rostopic = topic,
            callback = callback,
            namespace = namespace)

    def grab(self):
        # record freshness
        is_fresh = self.fresh

        # flip
        if self.fresh:
            self.fresh = False

        # return
        return is_fresh, self.img

    def callback(self, msg):
        self.img = ros2_lib_cvbridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        self.fresh = True

### Publishers ###

class RosPublisher(Node):
    def __init__(self, node_name, msg_type, rostopic, namespace=None):
        super().__init__(node_name, namespace=namespace)

        # save info
        self.type = msg_type

        # set up publisher
        self.publisher = self.create_publisher(self.type, rostopic, 5)
        self.topic = self.publisher.topic_name
        print(node_name, "Publishing to", self.topic)


    def publish(self, data):
        raise NotImplementedError

class GeoPathPublisher(RosPublisher):
    def __init__(self, topic, namespace=None):
        # only import if this class is in use
        from geographic_msgs.msg import GeoPath

        # init GeoPath message
        self.msg = GeoPath()

        super().__init__(
            node_name = "GeoPathPublisher",
            msg_type = GeoPath,
            rostopic = topic,
            namespace = namespace)

    # input as list of "[lat,lon]" coordinates
    def publish(self, path):
        from geographic_msgs.msg import GeoPoseStamped

        # clear list
        self.msg.poses = []

        # parse each coordinate
        for pos in path:
            lat,lon = pos

            pose_msg = GeoPoseStamped()
            pose_msg.pose.position.latitude = lat
            pose_msg.pose.position.longitude = lon
            self.msg.poses.append(pose_msg)

        # publish message
        self.publisher.publish(self.msg)


class ImagePublisher(RosPublisher):
    def __init__(self, topic, namespace=None):
        super().__init__(
            node_name = "ImagePublisher",
            msg_type = Image,
            rostopic = topic,
            namespace = namespace)

    def publish(self, cv_img):
        # convert to Image message and publish
        msg = ros2_lib_cvbridge.cv2_to_imgmsg(cv_img, encoding="passthrough")
        self.publisher.publish(msg)

class TwistPublisher(RosPublisher):
    def __init__(self, topic="cmd_vel", namespace=None):
        super().__init__(
            node_name = "TwistPublisher",
            msg_type = Twist,
            rostopic = topic,
            namespace = namespace)

    def publish(self, control):
        # create twist message
        move, turn = control
        msg = Twist()
        msg.linear.x = float(move)
        msg.angular.z = float(turn)
        # msg.header.stamp = self.get_clock().now().to_msg()
        self.publisher.publish(msg)

# a proxy for geometry_msgs/Vector3 to avoid extra import statements
class Vector3Proxy:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

    def getCopy(self):
        vec_copy = Vector3Proxy()
        vec_copy.x = self.x
        vec_copy.y = self.y
        vec_copy.z = self.z
        return vec_copy

    def reset(self):
        self.setNumber(0)

    def setNumber(self, num):
        self.x = num
        self.y = num
        self.z = num

    def multiply(self, other):
        result = Vector3Proxy()
        result.x = self.x * other.x
        result.y = self.y * other.y
        result.z = self.z * other.z
        return result

    def multiplyScalar(self, number):
        result = Vector3Proxy()
        result.x = self.x * number
        result.y = self.y * number
        result.z = self.z * number
        return result

    def toVector3(self):
        msg = Vector3(
            x=self.x,
            y=self.y,
            z=self.z)
        return msg

    def __str__(self):
        return f"x: {self.x}, y: {self.y}, z: {self.z}"

# publish control via Vector3Proxy
class TwistVelocityPublisher(RosPublisher):
    def __init__(self, name="TwistVelocityPublisher", topic="cmd_vel", namespace=None):
        super().__init__(
            node_name = name,
            msg_type = Twist,
            rostopic = topic,
            namespace = namespace)

    def publish(self, linear_vel: Vector3Proxy, angular_vel: Vector3Proxy):
        # create twist message
        msg = Twist()
        msg.linear = linear_vel.toVector3()
        msg.angular = angular_vel.toVector3()

        # msg.header.stamp = self.get_clock().now().to_msg()
        self.publisher.publish(msg)

### Miscellaneous ###

# serves as a special ROS2 camera
class ROS2Cam(Camera):
    def __init__(self, topic, name="ROS2Cam", max_fps=10, res=None):
        # init parent
        super().__init__(
            name=name,
            max_fps=max_fps,
            res=res)

        # set up ROS subscriber
        self.subscriber = ImageSubscriber(topic=topic)

    def grab(self):
        is_fresh, img = self.subscriber.grab()
        self.fresh = is_fresh
        self.img = img



