import time
import json

import commons.math_lib as mlib
import commons.utils_lib as utils
import commons.simple_zmq_lib as zlib


if __name__ == "__main__":
    # spin up zmq
    port = utils.getEnv("ZMQ_GPS_PORT")
    status_publisher = zlib.SimpleZMQPublisher(port=port)

    # set up route
    # B201 Green
    # 39.158960824758154, -76.89963825600877 # bottom right
    # 39.15900687173973, -76.9003242405333 # bottom left
    # 39.1593913886169, -76.9002534392159 # top left
    # 39.159210715191215, -76.89953648916826 # top right
    points = []
    points.append([39.158960824758154, -76.89963825600877])
    points.append([39.15900687173973, -76.9003242405333])
    points.append([39.1593913886169, -76.9002534392159])
    points.append([39.159210715191215, -76.89953648916826])

    # construct gps message
    status_msg = {}
    status_msg["messageType"] = "status"
    status_msg["messageData"] = {}
    status_msg["messageData"]["name"] = "SimGPS"
    status_msg["messageData"]["alt"] = 20
    status_msg["messageData"]["powerLevel"] = 0.75

    # loop through and interpolate
    index = 0
    prev_point = points[index-1]
    curr_point = points[index]
    interp_speed_per_point = 15 # seconds
    last_point_time = time.time()
    while True:
        # update time
        now = time.time()
        dt = now - last_point_time

        # check for next point
        if dt > interp_speed_per_point:
            dt -= interp_speed_per_point
            last_point_time = now

            # pull the next point pair
            index += 1
            if index >= len(points):
                index = 0
            prev_point = points[index-1]
            curr_point = points[index]

        # calculate current position
        proportion = dt / interp_speed_per_point
        lat,lon = mlib.travelPropOnLine(proportion, prev_point, curr_point)

        # update status message
        status_msg["messageData"]["lat"] = lat
        status_msg["messageData"]["lon"] = lon

        # convert to json and publish
        json_str = json.dumps(status_msg)
        status_publisher.publish(json_str)
        print("Published ZMQ Status Message:", json_str)

        # sleep to not flood out the messages
        time.sleep(0.2)

