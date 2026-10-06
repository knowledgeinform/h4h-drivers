import cv2
import imagezmq as imq

from commons.thread_lib import SimpleThread, ThreadStopper

class ImageSender:
    def __init__(self, name, target_address, target_port):
        self.name = name

        # build connection string
        connect_str = "tcp://" + str(target_address) + ":" + str(target_port)

        # connect to ImageReceiver
        self.sender = imq.ImageSender(connect_to=connect_str)

    def send(self, img):
        self.sender.send_image(self.name, img)


class ImageReceiver:
    def __init__(self, port):
        # build connection string
        connect_str = "tcp://*:" + str(port)

        # open up and image hub
        self.receiver = imq.ImageHub(open_port=connect_str)

    def run(self):
        # retrieve the source name and the image as a tuple
        source, img = self.receiver.recv_image()

        # show
        cv2.imshow(source, img)
        cv2.waitKey(1)

        # request another image
        self.receiver.send_reply(b'OK')


class BackgroundImageReceiver:
    def __init__(self, port, fps=20):
        # set up an image Receiver
        self.receiver_hook = ImageReceiver(port)

        # hook it into a background thread
        self.stopper = ThreadStopper()
        self.thread = SimpleThread(
            yield_time = 1.0 / fps,
            runner=self.receiver,
            stopper=self.stopper)
        self.thread.start()

    def stop(self):
        self.stopper.stop()


if __name__ == "__main__":
    # set this up as the debug receiver
    image_hub = imgq.ImageHub(open_port='tcp://*:5555')

    while True:
        # get source name and image tuple
        source, image = image_hub.recv_image()
        print("Received Frame:", image.shape)

        # show
        cv2.imshow(source, image)
        cv2.waitKey(1)

        # request another image
        image_hub.send_reply(b'OK')