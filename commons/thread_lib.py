### DEPRECATED !!!! ###

import time
from queue import Queue
import threading

# task pool for threads
class TaskPool:
	def __init__(self, max_size = 0):
		self.queue = Queue(max_size); # 0 = no size limit, be careful
		self.lock = threading.Lock();

	# query size
	def size(self):
		return self.queue.qsize();

	# acquires a lock for pushing
	# WARNING: it is on the caller to release the lock
	def pushLock(self):
		# get lock
		self.lock.acquire(blocking=1);
		return not self.queue.full();

	# adds a batch to the queue
	def pushBatch(self, items):
		flag = self.pushLock();
		if flag:
			# push as many items as possible
			for item in items:
				if self.queue.full():
					flag = False;
					break;
				self.queue.put(item);

		# release and return
		self.lock.release();
		return flag;

	# adds an item to queue
	def push(self, item):
		flag = self.pushLock();
		if flag:
			self.queue.put(item);
		self.lock.release();
		return flag;

	# returns a task item
	def get(self):
		# return if empty
		if self.queue.empty():
			return None;
		# return if busy
		ret = self.lock.acquire(blocking=0);
		if not ret:
			return None;

		# get item
		item = self.queue.get();
		self.lock.release();
		return item;

# helper to send stop command to all threads
# could technically just be a list, but this makes the intent clear
class ThreadStopper:
	def __init__(self):
		self.STOP_THREADS = False;

	def stop(self):
		self.STOP_THREADS = True;

# helper to temporarily pause execution of threads
class ThreadPauser:
	def __init__(self):
		self.FREEZE = False;

	def pause(self):
		self.FREEZE = True;

	def go(self):
		self.FREEZE = False;

# further simplified for single thread pool instance
class SimplifiedThreadPool:
	def __init__(self, num_workers, runner, runner_args, yield_time=0.10, max_size=0):
		# create a runner list
		runners = [];
		for a in range(num_workers):
			runners.append(runner(*runner_args));

		# set up the thread pool
		self.STOPPER = ThreadStopper();
		self.pool = SimpleThreadPool(
			num_workers=num_workers, 
			yield_time=yield_time, 
			runner=None, 
			stopper=self.STOPPER, 
			max_size=max_size);
		self.pool.setRunnerList(runners);
		self.pool.start();

	def push(self, task):
		self.pool.push(task);
	def pushBatch(self, tasks):
		self.pool.pushBatch(tasks);

	def size(self):
		return self.pool.bufferSize();
	def bufferSize(self):
		return self.size();

	# ONLY USE IF YOU'VE REPLACED THE THREADSTOPPER
	def join(self):
		self.pool.join();
	def setStopper(self, stopper):
		self.STOPPER = stopper;
		self.pool.setStopper(self.STOPPER);

	def setPauser(self, pauser):
		self.pool.setPauser(pauser);

	def stop(self):
		self.STOPPER.stop();
		self.pool.join();

# generic thread pool
class SimpleThreadPool:
	def __init__(self, num_workers = 4, yield_time=0.10, runner=None, stopper=None, max_size = 0):
		# create a task pool buffer
		self.buffer = TaskPool(max_size); # 0 = no limit, be careful

		# initialize worker threads
		self.num_workers = num_workers;
		self.threads = [];
		for a in range(self.num_workers):
			name = "Thread_" + str(a).zfill(2);
			thread = SimplePoolRunner(name=name, yield_time=yield_time, runner=runner, stopper=stopper, taskPool=self.buffer);
			self.threads.append(thread);

	def bufferSize(self):
		return self.buffer.size();

	def pushBatch(self, items):
		return self.buffer.pushBatch(items);

	def push(self, item):
		return self.buffer.push(item);

	def setYieldTime(self, yield_time):
		for thread in self.threads:
			thread.yield_time = yield_time;

	def setRunnerList(self, runner_list):
		for a in range(self.num_workers):
			thread = self.threads[a];
			runner = runner_list[a];
			thread.runner = runner;

	def setRunner(self, runner):
		for thread in self.threads:
			thread.runner = runner;

	def setStopper(self, stopper):
		for thread in self.threads:
			thread.stopper = stopper;

	def setPauser(self, pauser):
		for thread in self.threads:
			thread.pauser = pauser;

	def start(self):
		for thread in self.threads:
			thread.start();

	def join(self):
		for thread in self.threads:
			thread.join();

# a threadpool runner (is used by the thread pool)
class SimplePoolRunner(threading.Thread):
	def __init__(self, name="SimplePoolRunner", yield_time=0.05, runner=None, stopper=None, pauser=None, taskPool=None):
		threading.Thread.__init__(self);
		self.daemon = True;

		self.name = name;
		self.yield_time = yield_time;
		self.runner = runner;
		self.stopper = stopper;
		self.pauser = pauser;
		self.taskPool = taskPool;

	def run(self):
		while not self.stopper.STOP_THREADS:
			# check for a pause
			if self.pauser is None or not self.pauser.FREEZE:

				# get a task
				task = self.taskPool.get();
				if task is not None:
					self.runner.runPool(task);

			# yield
			time.sleep(self.yield_time);

# generic thread class
class SimpleThread(threading.Thread):
	def __init__(self, name="SimpleThread", yield_time=0.10, runner=None, stopper=None):
		threading.Thread.__init__(self);
		self.daemon = True;

		self.name = name;
		self.yield_time = yield_time;
		self.runner = runner; # must be set before start

		# give the option for a self contained stopper
		self.stopper = stopper
		if self.stopper is None:
			self.stopper = ThreadStopper()

	# Note: if the stopper provided at init is shared, then this will stop everyone
	def stop():
		self.stopper.stop()
		
	def run(self):
		while not self.stopper.STOP_THREADS:
			self.runner.run();
			time.sleep(self.yield_time);

# generic action pool (runner_args must be wrapped as a list)
def processThreadableTasks(tasks, runner, runner_args, num_workers, yield_time=0.10, print_progress=True, print_interval=1.0):
    # download the files
    # create runners
    start_time = time.time()
    STOPPER = ThreadStopper();
    runners = [];
    for a in range(num_workers):
        runners.append(runner(*runner_args));
    pool = SimpleThreadPool(num_workers=num_workers, yield_time=yield_time, stopper = STOPPER);
    pool.setRunnerList(runners);

    # start downloading
    pool.pushBatch(tasks)
    pool.start();

    # loop and print progress
    while pool.bufferSize() > 0:
        time.sleep(print_interval);
        if print_progress:
            print("Remaining Tasks:", pool.bufferSize());

    # finish up threads
    STOPPER.stop();
    print("Closing Threads");
    pool.join();
    print("Finished Task:", (time.time() - start_time));