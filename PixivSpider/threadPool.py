#coding=utf-8
#! /usr/bin/env python
import queue
import threading
import time
#线程池
class Pool:
	#构造函数
	def __init__(self, thread_num = 10):
		self.works = queue.Queue(100000)
		self.threads = []
		#文件用公用锁
		self.filemutex = threading.Lock()
		self.__init_threads(thread_num)
	#初始化线程
	def __init_threads(self, thread_num):
		#类公用互斥锁
		self.mutex = threading.Lock()
		#类数据初始化
		self.data = {}
		#设置cnt
		self.set('cnt', 0)
		#设置flag
		self.set('flag', True)
		for i in range(thread_num):
			#线程锁
			mutex = threading.Lock()
			#线程数据
			data = {}
			#线程类
			thread = Consumer(self.works, mutex, data, self.mutex, self.data, self.filemutex)
			#线程字典
			tdict = {'tid':i,'mutex':mutex,'data':data,'thread':thread}
			#添加线程字典
			self.threads.append(tdict)
	#添加一个任务
	def add_job(self, func, *args):
		self.add('cnt', 1)
		self.works.put((func, list(args)))
	#获取类公用数据
	def get(self, name):
		self.mutex.acquire()
		if name not in self.data:
			ret = None
		else:
			ret = self.data[name]
		self.mutex.release()
		return ret
	#设置类公用数据
	def set(self, name, value):
		self.mutex.acquire()
		self.data[name] = value
		self.mutex.release()
	#类公用数据数值增加
	def add(self, name, value = 1):
		self.mutex.acquire()
		self.data[name] += value
		self.mutex.release()
	#获取剩余任务量
	def getSize(self):
		return self.get('cnt')
	#输出线程的所有数据
	def pr(self):
		for tdict in self.threads:
			data = tdict['data']
			print("%s %s %s"%(data['name'],data['cnt'],data['running']))
class Consumer(threading.Thread):
	#构造函数
	def __init__(self, work_queue, mutex, data, fmutex, fdata, filemutex):
		threading.Thread.__init__(self)
		self.work_queue = work_queue
		self.mutex = mutex
		self.data = data
		self.fmutex = fmutex
		self.fdata = fdata
		self.filemutex = filemutex
		self.setDaemon(True)
		self.start()
	#主运行
	def run(self):
		self.set('running',False)
		self.set('cnt', 0)
		self.set('name', threading.current_thread())
		while True:
			func,args = self.work_queue.get()
			self.set('running',True)
			while True:
				try:
					#print(func, args)
					ret = func(args, mutex = self.filemutex)
					break
				except Exception as e:
					print(threading.current_thread() ,e)
			if not ret:
				self.fset('flag', False)
			self.add('cnt', 1)
			self.fadd('cnt', -1)
			self.work_queue.task_done()
			self.set('running',False)
			#time.sleep(1)
	#公共数据自增
	def fadd(self, name, value):
		self.fmutex.acquire()
		self.fdata[name] += value
		self.fmutex.release()
	#公共数据自增
	def fset(self, name, value):
		self.fmutex.acquire()
		self.fdata[name] = value
		self.fmutex.release()
	#私有数据自增
	def add(self, name, value = 1):
		self.mutex.acquire()
		self.data[name] += value
		self.mutex.release()
	#设置私有数据
	def set(self, name, value):
		self.mutex.acquire()
		self.data[name] = value
		self.mutex.release()
	#获取私有数据
	def get(self, name):
		self.mutex.acquire()
		if name not in self.data:
			ret = None
		else:
			ret = self.data[name]
		self.mutex.release()
		return ret
#测试用job
def do_job(args, mutex):
	time.sleep(0.1)#模拟处理时间
	print(threading.current_thread(), list(args), flush=True)
	pass
if __name__ == '__main__':
	start = time.time()
	work_manager =  Pool(60)
	print("main")
	for i in range(1,1000):
	    work_manager.add_job(do_job,i)
	size = work_manager.getSize()
	print(size)
	while size != 0:
		size = work_manager.getSize()
		print(size)
		time.sleep(2)
	#work_manager.wait_allcomplete()
	end = time.time()
	print("cost all time: %s" % (end-start))
	exit(0)