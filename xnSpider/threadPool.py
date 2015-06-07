#coding=utf-8
#! /usr/bin/env python
import queue
import threading
import time
#no lock !!!
class Pool:
	works = queue.Queue()
	threads = []
	def __init__(self, thread_num = 10):
		self.__init_threads(thread_num)
	def __init_threads(self, thread_num):
		for i in range(thread_num):
			#print(i)
			self.threads.append(Consumer(self.works))
	def add_job(self, func, *args):
		self.works.put((func, list(args)))
	def wait_allcomplete(self, inf = "all complete"):
		while self.works.qsize()!=0:
			pass#print(self.works.qsize(),flush=True)
		for item in self.threads:
			if item.isAlive():
				while item.running == True:
					pass
		#print("")
		print(inf)
class Consumer(threading.Thread):
	running = True
	data = threading.local()
	def __init__(self, work_queue):
		threading.Thread.__init__(self)
		self.work_queue = work_queue
		self.running = False
		self.setDaemon(True)
		self.start()
	def run(self):
		while True:
			#try:
				func,args = self.work_queue.get()
				self.running = True
				#print(threading.current_thread(), flush=True)
				func(args)
				self.work_queue.task_done()
				self.running = False
				#print(threading.current_thread(), flush=True)
			#except:
				#print("consumer dead",flush=True)
				#break
def do_job(args):
	time.sleep(0.01)#模拟处理时间
	#print(threading.current_thread(), list(args),flush=True)

if __name__ == '__main__':
	start = time.time()
	work_manager =  Pool(60)
	print("main")
	for i in range(1,10000):
	    work_manager.add_job(do_job,i)
	work_manager.wait_allcomplete()
	end = time.time()
	print("cost all time: %s" % (end-start))
	exit(0)