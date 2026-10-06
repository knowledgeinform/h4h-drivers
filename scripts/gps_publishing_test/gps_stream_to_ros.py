"""
Reads NMEA from GPS module over serial, publishes a ROS2
sensor_msgs/NavSatFix on a chosen topic and prints each message as
JSON for debugging.

to check serial device name of gps sensor:
ls /dev/cu.*


open /dev/cu.usbserial-XXXXX and forward it to localhost:5000:

socat \
  TCP-LISTEN:5000,reuseaddr,fork,raw,echo=0 \
  /dev/cu.usbserial-XXXXX,raw,echo=0



if having issues:

0. killall gpsd screen picocom || true #kill any process holding the port

1. ensure all commands uses cu.* instead of tty.* for the serial port, tty sometimes has issues
2. reconnect GPS sensor

3. check gps data flow on host machine using:
    stty -f /dev/cu.usbserial-XXXX 9600 raw -echo
    cat /dev/cu.usbserial-XXXX


example command:
    python3 gps_stream_to_ros.py /dev/ttyGPS 9600 \
        --ros-topic /gps/fix --frame-id gps_link
"""
import os
import sys
import time
import json
import argparse

import serial
import pynmea2

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix, NavSatStatus

import commons.utils_lib as utils
import commons.simple_zmq_lib as zlib


def iso_to_ros_time():
    now = time.time()
    sec = int(now)
    nsec = int((now - sec) * 1e9)
    return sec, nsec

class GPSPublisher(Node):
    def __init__(self, port, baud, topic, frame_id):
        super().__init__('gps_streamer')

        self.gps_platform_name = os.environ.get("GPS_PLATFORM_NAME")
        self.gps_topic = os.environ.get("GPS_TOPIC_NAME")
        self.port = utils.getEnv("ZMQ_GPS_PORT") # gets rid of the str|None type warning

        self.pub = self.create_publisher(NavSatFix, self.gps_topic, 10)
        self.frame_id = frame_id
        try:
            self.ser = serial.Serial(port, baud, timeout=1)
        except serial.SerialException as e:
            self.get_logger().error(f"Cannot open {port}: {e}")
            sys.exit(1)
        self.get_logger().info(f"Listening on {port}@{baud}, publishing to '{self.gps_topic}'")
        self.cov = [0.0] * 9
        self.cov_type = NavSatFix.COVARIANCE_TYPE_UNKNOWN
        self.timer = self.create_timer(0.05, self.read_and_publish)

        self.status_publisher = zlib.SimpleZMQPublisher(port=self.port)
        self.status_msg = {}
        self.status_msg["messageType"] = "status"
        self.status_msg["messageData"] = {}


    def read_and_publish(self):
        raw = ''
        try:
            raw = self.ser.readline().decode('ascii', errors='ignore').strip()
            msg = pynmea2.parse(raw)
            # if isinstance(msg, pynmea2.RMC) and msg.status == 'A':
            #     lat, lon, alt = msg.latitude, msg.longitude, 0.0
            #     status = NavSatStatus.STATUS_FIX
            if isinstance(msg, pynmea2.GGA) and int(msg.gps_qual) > 0:
                lat, lon, alt = msg.latitude, msg.longitude, float(msg.altitude)
                status = NavSatStatus.STATUS_FIX
            else:
                raise ValueError("No valid fix")
        except Exception:
            # publishes dummy fix if parse error or no fix
            lat, lon, alt = 0.0, 0.0, 0.0
            status = NavSatStatus.STATUS_NO_FIX

        # check for invalid lat/lon
        if abs(lat) < 0.0001 or abs(lon) < 0.0001:
            # lat = 39.15911
            # lon = -76.89963
            return

        # Build NavSatFix message
        fix = NavSatFix()
        sec, nsec = iso_to_ros_time()
        fix.header.stamp.sec = sec
        fix.header.stamp.nanosec = nsec
        fix.header.frame_id = self.frame_id
        fix.status.status = status
        fix.status.service = NavSatStatus.SERVICE_GPS
        fix.latitude = lat
        fix.longitude = lon
        fix.altitude = alt
        fix.position_covariance = self.cov
        fix.position_covariance_type = self.cov_type

        # Publish and mirror as JSON
        self.pub.publish(fix)
        out = {
            'header': {'stamp': {'sec': sec, 'nanosec': nsec}, 'frame_id': self.frame_id},
            'status': {'status': status, 'service': NavSatStatus.SERVICE_GPS},
            'latitude': round(lat, 6),
            'longitude': round(lon, 6),
            'altitude': alt,
            'position_covariance': self.cov,
            'position_covariance_type': self.cov_type,
            'raw_nmea': raw
        }
        print(json.dumps(out), flush=True)

        # build up the ZMQ message
        self.status_msg["messageData"]["name"] = self.gps_platform_name

        self.status_msg["messageData"]["lat"] = lat
        self.status_msg["messageData"]["lon"] = lon
        self.status_msg["messageData"]["alt"] = alt # meters above home position
        self.status_msg["messageData"]["powerLevel"] = 0.75 # fixed value for now to match UCC's expected format

        # convert to json and publish
        json_str = json.dumps(self.status_msg)
        self.status_publisher.publish(json_str)
        self.get_logger().info(f"Published ZMQ Status Message: {json_str}")

def main():
    parser = argparse.ArgumentParser(
        description="GPS NMEA to ROS2 NavSatFix streamer"
    )
    parser.add_argument('port', nargs='?', default='/dev/cu.usbserial-XXXXX',
                        help='serial port (e.g. /dev/cu.usbserial-XXXXX)')
    parser.add_argument('baud', nargs='?', type=int, default=9600,
                        help='baud rate (default 9600)')
    parser.add_argument('--ros-topic', dest='ros_topic', required=True,
                        help='ROS2 topic to publish NavSatFix on')
    parser.add_argument('--frame-id', dest='frame_id', default='gps',
                        help='frame ID for NavSatFix header (default "gps")')
    args = parser.parse_args()

    rclpy.init()
    node = GPSPublisher(args.port, args.baud, args.ros_topic, args.frame_id)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.ser.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
