from __future__ import annotations
import time
import threading

from collections.abc import Callable

def threadOnce(*args, func:Callable, **kwargs):
	"""Spins off a thread to call the incoming function once"""
	thread = threading.Thread(target=func, daemon=True, args=args, kwargs=kwargs)
	thread.start()
	return thread

def threadForever(func:Callable, rate_hz:int|float=10):
	"""Spins off a thread to call the incoming function repeatedly"""
	def wrapper():
		yield_time = 1.0 / rate_hz
		while True:
			func()
			time.sleep(yield_time)
		return

	thread = threading.Thread(target=wrapper, daemon=True)
	thread.start()
	return thread

def threadForeverNoWait(func:Callable):
	""" 
	WARNING: Do NOT use this unless func already has some sort of builtin sleep or wait.
	Spins off a thread to call the incoming function repeatedly as fast as possible. 
	"""
	def wrapper():
		while True:
			func()

	thread = threading.Thread(target=wrapper, daemon=True)
	thread.start()
	return thread	
