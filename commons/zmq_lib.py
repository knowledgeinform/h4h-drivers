import zmq
import copy
from commons.thread_lib import SimpleThread, ThreadStopper


class ZMQReceiver:
	def __init__(self, port, callback, isHost=False, topic="", ip_addr=None, isPyObj=False):
		# set up receiver context
		self.topic = topic
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.SUB)

		# set topic filter
		self.socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)

		# set up default ip address if None
		if ip_addr is None:
			ip_addr = "localhost"

		# bind or connect?
		if isHost:
			address = "tcp://*:" + str(port)
			print("Binding to Address:", address)
			self.socket.bind(address)
			print("Finished Binding to", address)
		else:
			address = "tcp://" + ip_addr + ":" + str(port)
			print("Connecting to Address:", address)
			self.socket.connect(address)
			print("Finished Connecting to ", address)
		
		
		# flag for pulling either strings or serializable python objects (like lists)
		self.isPyObj = isPyObj

		# set up threaded callback
		self.callback = callback
		self.STOPPER = ThreadStopper()
		self.thread = SimpleThread(runner=self, yield_time=0.03, stopper=self.STOPPER) # is blocking
		self.thread.start()

	def stop(self):
		self.STOPPER.stop()

	def run(self):
		if not self.isPyObj:
			msg = self.socket.recv_string()
		else:
			msg = self.socket.recv_pyobj()
		self.callback(msg)

class ZMQSender:
	def __init__(self, port, isHost=False, topic="", ip_addr=None, isPyObj=False, max_publish_rate=20):
		# set up sender context
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.PUB)

		# bind or connect
		if isHost:
			print("Binding To:", "tcp://*:" + str(port))
			self.socket.bind("tcp://*:" + str(port))
		else:
			address = "tcp://" + ip_addr + ":" + str(port)
			print("Connecting To:", address)
			self.socket.connect(address)
			print("Finished Connecting to ", address)

		self.topic = topic

		# flag for pulling either strings or serializable python objects (like lists)
		self.isPyObj = isPyObj

		# calculate sleep time
		self.yield_time = 1.0 / max_publish_rate

		# set up a message buffer
		self.msg_buffer = None

		# set up threaded callback
		self.STOPPER = ThreadStopper()
		self.thread = SimpleThread(runner=self, yield_time=self.yield_time, stopper=self.STOPPER) # is blocking
		self.thread.start()

	def stop(self):
		self.STOPPER.stop()

	def run(self):
		msg = copy.deepcopy(self.msg_buffer)
		self.msg_buffer = None
		if msg is not None:
			self.publish(msg)

	def send(self, msg):
		self.msg_buffer = msg

	def publish(self, msg):
		# notify topic
		self.socket.send_string(self.topic, zmq.SNDMORE)

		# send message
		if self.isPyObj:
			self.socket.send_pyobj(msg)
		else:
			self.socket.send_string(msg)
