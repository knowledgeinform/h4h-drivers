import cv2
import imagezmq as imgq


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