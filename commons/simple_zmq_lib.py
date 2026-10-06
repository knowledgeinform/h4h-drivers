from __future__ import annotations

import zmq
import json
import contextlib

from collections.abc import Callable
from commons.thread_lib2 import threadForeverNoWait

def registerCallback(callback, subscriber):
	""" 
	This function will call callback() 
	for each return from subscriber.receive() 
	This will consume everything from this subscriber's receive function
	"""
	# stop any other thread from calling subscriber.receive()
	subscriber.is_threaded = True

	# wrap the functions together and start the callback thread
	def wrapper():
		callback(subscriber._receive())
	threadForeverNoWait(func=wrapper)

class Serializeable:
	"""
	This class is meant to serve as a Mixin that gives a class 
	the ability to serialize its state and send it over as bytes through ZMQ.

	The default serialize() and deserialize() functions should work
	so long as the class has no unserializeable attributes (variables)
	"""

	def serialize(self) -> bytes:
		""" 
		default attempt to serialize myself with vars(self) 

		inheritors should override this if they need custom behavior
		"""
		return json.dumps(vars(self))

	def _deserialize(self, data:dict):
		""" 
		default attempt to reconstitute state from data with vars(self).update(data)

		inheritors should override this if they need custom behavior
		"""
		vars(self).update(data)


	def deserialize(self, data:bytes|dict):
		""" 
		if the data is a byte string then this function 
		will use json.loads to convert it to a dictionary
		before passing it along to _deserialize()
		"""
		if isinstance(data, str):
			data = json.loads(data)
		self._deserialize(data)


class SimpleZMQPublisher:
	"""
	A ZMQ Publisher wrapper. Python objects are disallowed for security reasons

	port (Required): 
		the port number to bind to
	ip_address (Optional|None): 
		if set, then we will make a socket connection, 
		if not, then this is the binding-side of the pair
	"""
	def __init__(self, port:str|int, ip_address:str|None = None):
		# set up a publisher socket
		self.socket = (zmq.Context().socket(zmq.PUB))

		# convert port number to string in case it's an int
		port = str(port)

		# set up warning
		self.warning_str = "FAILED TO PUBLISH. We can only publish strings or json-serializeable objects."
		self.warning_str += " Python object publishing is disallowed for security reasons!"

		# if address is None, then we are host, otherwise we are not
		if ip_address:
			address_str = "tcp://" + ip_address + ":" + port
			print("SimpleZMQPublisher: Connecting to address:", address_str)
			self.socket.connect(address_str)
		else:
			address_str = "tcp://*:" + port
			print("SimpleZMQPublisher: Binding to address:", address_str)
			self.socket.bind(address_str)

	def _publish(self, data:str|object, topic:str):
		""" a helper func that actually publishes the data on a specified topic """
		# send out the topic
		if topic != "":
			topic = topic.encode("utf-8")
			self.socket.send(topic, zmq.SNDMORE)
		
		# check if data is a string (may also be an already-serialized json str)
		if isinstance(data, str):
			self.socket.send_string(data)
			return

		# otherwise attempt to serialize it as json
		with contextlib.suppress(TypeError):
			self.socket.send_json(json.dumps(data))
			return

		# print out a warning if we reach here
		print(self.warning_str)
		print("Failed to publish the following:", data)


	def publish(self, data:str|object, topic:str|list=""):
		""" publish data to topic. If topic is a list then publish to each """
		# check if the topic var is a list
		if isinstance(topic, list):
			for topic_str in topic:
				self._publish(topic=topic_str, data=data)
		else:
			self._publish(topic=topic, data=data)


class SimpleZMQSubscriber:
	"""
	A ZMQ Subscriber wrapper that uses a slow decode method to handle strings or json
	Python objects are disallowed for security reasons

	port (Required): 
		the port number to bind to
	ip_address (Optional|None): 
		if set, then we will make a socket connection, 
		if not, then this is the binding-side of the pair
	topic (Optional|""):
		if set, then this subscriber will filter by the given topic
		additionally, a list of strings can be provided and we'll subscribe to all of them
	"""
	def __init__(self, port:str|int, ip_address:str|None = None, topic:str|list = "", callback:Callable = None):
		# set up a publisher socket
		self.socket = (zmq.Context().socket(zmq.SUB))

		# convert port number to string in case it's an int
		port = str(port)

		# set a flag that indicates if this subscriber is held by a callback thread
		# if it is then it will prevent callers from call retrieve() and emit a warning
		self._is_threaded = False

		# if address is None, then we are host, otherwise we are not
		if ip_address:
			address_str = "tcp://" + ip_address + ":" + port
			print("SimpleZMQPublisher: Connecting to address:", address_str)
			self.socket.connect(address_str)
		else:
			address_str = "tcp://*:" + port
			print("SimpleZMQPublisher: Binding to address:", address_str)
			self.socket.bind(address_str)

		# subscribe to topic(s)
		if isinstance(topic, list):
			for item in topic:
				print("Subscribing to:", item)
				self.socket.subscribe(item.encode())
		else:
			if topic == "":
				print("Subscribing to All Topics")
			else:
				print("Subscribing to:", topic)
			self.socket.subscribe(topic.encode())

		# register callback if provided
		if callback is not None:
			registerCallback(callback, self)

	def decode(self, data_element:bytes) -> str|dict|None:
		data = data_element

		# try to decode it further as json
		with contextlib.suppress(json.JSONDecodeError):
			data = json.loads(data)

			# check for double-nested data
			if type(data) != dict:
				data = json.loads(data)

		# try to decode it as a string
		with contextlib.suppress(UnicodeDecodeError, AttributeError):
			data = data.decode()

		return data

	def _receive(self) -> dict:
		""" returns the next message from the publisher """
		msg = self.socket.recv_multipart()
		
		# set up a dictionary to split topics and data
		output = {}
		output["topic"] = ""
		output["data"] = None

		# check if the message has a topic (more than one part)
		if len(msg) > 1:
			output["topic"] = msg[0].decode()

			# decode the data of the message
			output["data"] = self.decode(msg[1])
		else:
			output["data"] = self.decode(msg[0])

		return output

	def receive(self) -> dict|None:
		""" returns the next message from the publisher """
		if not self._is_threaded:
			return self._receive()
		
		# issue a warning if this subscriber has a callback thread registered to it
		print("!!! receive() is disabled because this subscriber has a callback thread")
		return None