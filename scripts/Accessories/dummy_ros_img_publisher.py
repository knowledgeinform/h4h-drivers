import cv2
import time
import random

import numpy as np

import commons.ros2_lib as rlib
import commons.utils_lib as utils

# fast draw text (bottom-left positioned, the documentation is lying)
def drawText(img, pos, text, font=cv2.FONT_HERSHEY_SIMPLEX, scale=1, 
    color=(255,255,255), thickness = 1, lineType=cv2.LINE_AA):
    x,y = pos
    cv2.putText(img, text, (x,y), font, scale, color, thickness, lineType);


def getRandomColor():
    return [random.randint(0,255) for a in range(3)]

if __name__ == "__main__":
    # generate dummy image
    img = np.zeros((480,640,3), np.uint8)

    # spin up a publisher
    publisher = rlib.ImagePublisher(topic="/dummy_img_output")

    # spin up a twist publisher
    twist_publisher = rlib.TwistPublisher(
        topic="/dummy_twist_output"
    )

    # loop forever
    counter = 0
    while True:
        # change something about the image
        py = random.randint(0,480-1)
        img[py,:] = getRandomColor()

        # make a copy and draw time
        display = np.copy(img)
        drawText(display, (50,50), str(round(time.time(),2)))


        # publish the image
        publisher.publish(display)
        twist_publisher.publish([1,2])

        counter += 1
        print("Published Image:", counter)
        time.sleep(0.1)




    