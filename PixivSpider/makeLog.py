#coding=utf-8
#! /usr/bin/env python
import sys,os,time
import pickle
import pString
import threading
import enum
from functools import reduce
#创建文件需要的父文件夹(们)
def createFile(filename):
	directory = ""
	name = ""
	for c in filename:
		if c == '/':
			directory = name
		name += c
	if directory != "":
		if os.path.isdir(directory):
			pass
		else:
			os.makedirs(directory)
#格式错误
class FormatError(Exception):
	def __init__(self, msg):
		Exception.__init__(self)
		self.message = msg
	def __str__(self):
		return str(self.message)
#文件操作类
class File:
	#构造函数
	def __init__(self, filename):
		self.name = filename
		if not os.path.exists(self.name):
			self.create()
		self.dict = {}
		with open(self.name, "r") as fd:
			lines = fd.read().split('\n')
		for line in lines:
			if line == "": continue
			lt = line.split(' ')
			self.dict[lt[0]] = lt[1:]
			#print(lt[0], lt[1:])
		self.__refresh()
	#刷新文件
	def __refresh(self):
		with open(self.name, "w") as fd:
			for key in self.dict:
				data = ' '.join([key] + self.dict[key])
				fd.write(data + '\n')
	#创建文件
	def create(self):
		with open(self.name, "w") as fd:
			pass
	#删除文件
	def delete(self):
		if os.path.exists(self.name):
			os.path.remove(self.name)
	#添加一行
	def append(self, key, value):
		if type(value) != list:
			raise FormatError("value必须为list类型")
		if key in self.dict:
			raise FormatError("%s已存在于%s"%(key, self.name))
		self.dict[key] = value
		with open(self.name, "a") as fd:
			data = ' '.join([key] + value)
			fd.write(data + '\n')
	#删除一行
	def remove(self, key):
		if not key in self.dict:
			raise FormatError("%s不存在于%s"%(key, self.name))
		del self.dict[key]
		self.__refresh()
	#全部删除
	def renew(self):
		self.create()
		self.dict = {}
	#获取一条
	def get(self):
		return self.dict
		#test
		if len(self.dict) == 0:
			return None
		for key in self.dict:
			return [key] + self.dict[key]
	#判断key存在
	def isExist(self, key):
		return key in self.dict
#日志类
class Log:
	#构造函数
	def __init__(self, name, directory):
		self.aname = directory + name + "_准备分析" + ".txt"
		self.bname = directory + name + "_准备下载" + ".txt"
		self.cname = directory + name + "_下载完成" + ".txt"
		self.afd = File(self.aname)
		self.bfd = File(self.bname)
		self.cfd = File(self.cname)
		self.mutex = threading.Lock()
	#删除
	def delete(self):
		self.mutex.acquire()
		try:
			self.afd.delete()
			self.bfd.delete()
			self.cfd.delete()
		except Exception as e:
			raise e
		finally:
			self.mutex.release()
	#开始分析
	def begin(self, key):
		self.mutex.acquire()
		try:
			if self.isExist(key, False):
				#print(key,"isExist")
				return 1
			self.afd.append(key, [])
			return 0
		except Exception as e:
			raise e
		finally:
			self.mutex.release()
	#分析完成,开始下载
	def work(self, key, *args):
		self.mutex.acquire()
		try:
			if self.bfd.isExist(key) or self.cfd.isExist(key):
				#print(key,"isExist")
				pass
			else:
				if len(args) == 1 and type(args[0]) != str:
					args = args[0]
				self.bfd.append(key, list(args))
			if self.afd.isExist(key):
				if key[-2:] == "_0":
					self.afd.remove(key)
		except Exception as e:
			raise e
		finally:
			self.mutex.release()
	#下载完成
	def end(self, key):
		self.mutex.acquire()
		try:
			if self.cfd.isExist(key):
				#print(key,"isExist")
				pass
			else:
				self.cfd.append(key, [])
			if self.bfd.isExist(key):
				self.bfd.remove(key)
		except Exception as e:
			raise e
		finally:
			self.mutex.release()
	def endall(self):
		self.mutex.acquire()
		try:
			keylist = self.bfd.get()
			for key in keylist:
				if self.cfd.isExist(key):
					#print(key,"isExist")
					pass
				else:
					self.cfd.append(key, [])
			self.bfd.renew()
		except Exception as e:
			raise e
		finally:
			self.mutex.release()
	#判断是否存在
	def isExist(self, key, mutex = True):
		if mutex: self.mutex.acquire()
		try:
			ret = \
			self.afd.isExist(key) or\
			self.bfd.isExist(key) or \
			self.cfd.isExist(key)
			return ret
		except Exception as e:
			raise e
		finally:
			if mutex: self.mutex.release()
	#获取一条分析
	def get(self):
		self.mutex.acquire()
		try:
			ret = self.afd.get()
			return ret
		except Exception as e:
			raise e
		finally:
			self.mutex.release()
	#获取一条下载
	def getDown(self):
		self.mutex.acquire()
		try:
			ret = self.bfd.get()
			return ret
		except Exception as e:
			raise e
		finally:
			self.mutex.release()
#条目管理类
class mainLog:
	#构造函数
	def __init__(self):
		self.directory = "logfile/"
		self.name = self.directory + "main.txt"
		createFile(self.name)
		if not os.path.exists(self.name):
			with open(self.name, "w") as fd: pass
		with open(self.name, "r") as fd:
			lines = fd.read().split('\n')
		self.dict = {}
		self.log = {}
		for line in lines:
			if line == "": continue
			lt = line.split(' ')
			#print(lt)
			self.dict[lt[0]] = lt[1:]
			self.log[lt[0]] = Log(lt[0], self.directory)
	#刷新文件
	def __refresh(self):
		with open(self.name, "w") as fd:
			for key in self.dict:
				data = ' '.join([key] + self.dict[key])
				fd.write(data + '\n')
	#添加一条
	def append(self, args):
		if type(args) != str:
			raise FormatError("args必须为str类型: %s"%type(args))
		lt = args.split(' ')
		key = lt[0]
		value = lt[1:]
		if key in self.dict:
			for v in value:
				if not v in self.dict[key]:
					self.dict[key].append(v)
		else:
			self.dict[key] = value
			self.log[key] = Log(key, self.directory)
		self.__refresh()
	#删除一条
	def delete(self, args):
		if type(args) != str:
			raise FormatError("args必须为str类型: %s"%type(args))
		lt = args.split(' ')
		key = lt[0]
		value = lt[1:]
		if not key in self.dict:
			raise FormatError("%s不存在于%s"%(key, self.name))
		else:
			if value == []:
				del self.dict[key]
				del self.log[key]
			else:
				for v in value:
					if not v in self.dict[key]:
						raise FormatError("%s不存在于%s[%s]"%(v, self.name,key))
					else:
						self.dict[key].remove(v)
		self.__refresh()
	#获取名字
	def getName(self):
		return list(self.dict)
	#获取管理类
	def getLog(self, name):
		if not self.isExist(name):
			raise FormatError("%s不存在于%s"%(name,self.name))
		return self.log[name]
	#获取条目关键字
	def getTag(self, name):
		if not self.isExist(name):
			raise FormatError("%s不存在于%s"%(name,self.name))
		return self.dict[name]
	#判断条目存在
	def isExist(self, name):
		if type(name) != str: FormatError("name必须为str类型:%s"%type(name))
		return name in self.dict
def main():
	log = mainLog()
if __name__ == '__main__':
	main()