#coding=utf-8
#! /usr/bin/env python
import requests,http,urllib
import sys,os,time
import re,pickle
import signal

import enum
import threadPool
import pString
import makeLog

#默认下载地址
defaultDir = r"D:/图片/pixiv/"
#默认图片下载线程数,过大可能会被网站丢包
downThread = 4
#用户配置文件
userFile = "userFile.pickle"

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
#设置访问用http头
def makeHeader(url):
	headers = {
	'Referer': url
	}
	return headers
#定制下载用http头
def makeHeaderDown(url):
	headers = {
	'Range': 'bytes=0-99999999',
	'Referer': url,
	'Cache-Control':'max-age=0'
	}
	return headers
#判断文件是否已经存在并有意义
def fileExist(filename):
	if os.path.exists(filename) and os.path.getsize(filename) != 0:
		return True
	else:
		return False

#用户信息存储类
class User:
	username = ''
	password = ''
	filename = ''
	#构造函数
	def __init__(self, fname):
		self.filename = fname
		if os.path.exists(self.filename):
			self.__load()
		else:
			self.stdio()
	#读入
	def __load(self):
		fd = open(self.filename, "rb")
		self.username = pickle.load(fd)
		self.password = pickle.load(fd)
		self.filename = pickle.load(fd)
		fd.close()
		print("从文件中读入用户名和密码成功！")
	#写入
	def __dump(self):
		fd = open(self.filename, "wb")
		pickle.dump(self.username,fd)
		pickle.dump(self.password,fd)
		pickle.dump(self.filename,fd)
		fd.close()
	#从标准输入获得值
	def stdio(self):
		self.username = input("username:")
		self.password = input("password:")
		self.__dump()
#自定义错误,参数错误
class ParameterError(Exception):
	def __init__(self, msg):
		Exception.__init__(self)
		self.message = msg
	def __str__(self):
		return str(self.message)
#主功能类
class Spider:
	#构造函数
	def __init__(self,logdir = "lg",prwork = True, prdown = True):
		self.__session = requests.session()
		#线程池
		self.__pool = {}
		self.__pool['find'] = threadPool.Pool(128)
		self.__pool['get'] = threadPool.Pool(128)
		self.__pool['down'] = threadPool.Pool(downThread)
		self.__pool['write'] = threadPool.Pool(128)
		#线程池使用的参数列表
		self.poolpara = {}
		self.poolpara['find'] = ['key','pageid','logfd']
		self.poolpara['get'] = ['id', 'adir', 'logfd']
		self.poolpara['down'] = ['id', 'url[]', 'refer[]', 'filename[]', 'logfd']
		self.poolpara['write'] = ['id', 'res[]', 'filename[]', 'logfd']
		pass
	#登录
	def login(self, user):
		#定义post的参数
		reqdata={'mode':'login',
		'pass':user.password,
		'pixiv_id':user.username,
		'skip':'1'
		}
		domain = r"https://www.secure.pixiv.net/login.php"
		response = self.__session.post(domain, data = reqdata)
		#判断是否登陆成功
		ret = response.text.find("var user_id") != -1
		return ret
	#登出
	def logout(self):
		pass
	#从地址获取获取内容
	def getHtml(self, domain, stream = False, timeout = 50, headers = None):
		while True:
			try:
				if headers:
					ret = self.__session.get(domain, stream = stream, headers = headers)
					return ret
				else:
					ret = self.__session.get(domain, stream = stream)
					return ret
			except Exception as e:
				#为网络错误预留
				#print("domain: ",domain)
				#print(e)
				pass
	#获取cookies
	def getcookies(self, domain = r""):
		response = self.getHtml(domain)
		return response.cookies.get_dict()
	#计数函数
	def recount(self):
		self.__cnt = 0
	def __count(self, num = 1):
		slf.__cnt += num
	def count(self):
		return self.__cnt
	#添加任务
	def add_job(self, pname, *args):
		if not pname in self.__pool:
			raise ParameterError("%s为不存在的线程池"%pname)
		if len(args) != len(self.poolpara[pname]):
			errmsg = "add_job [%s] 的额外参数应为%d个 %s : %s"%\
			(pname, len(self.poolpara[pname]), self.poolpara[pname], args)
			ParameterError(errmsg)
		if pname == "find":
			self.__pool[pname].add_job(self.findT, args[0], args[1], args[2])
		elif pname == "get":
			self.__pool[pname].add_job(self.getT, args[0], args[1], args[2])
		elif pname == "down":
			self.__pool[pname].add_job(self.downT, args[0], args[1], args[2], args[3], args[4])
		elif pname == "write":
			self.__pool[pname].add_job(self.writeT, args[0], args[1], args[2], args[3])
	#设置线程池的状态参数
	def set_stat(self, pname, name, value):
		if not pname in self.__pool:
			raise ParameterError("%s为不存在的线程池"%pname)
		self.__pool[pname].set('flag', value)
	#获取线程池的状态参数
	def get_stat(self, pname, name):
		if not pname in self.__pool:
			raise ParameterError("%s为不存在的线程池"%pname)
		ret = self.__pool[pname].get(name)
		return ret
	#等待下载任务结束
	def wait_allcomplete(self, data = ""):
		while True:
			size = 0
			ret = ""
			lt = ['find','get','down','write']
			for poolId in lt:
				s =self.__pool[poolId].getSize()
				ret += "%5s %5s "%(str(poolId), str(s))
				size += s
			print(ret, flush = True)
			if size == 0:
				break
			time.sleep(5)
		print(data)
	#从关键字和页码中获取内容,写入日志文件logfd
	def find(self, key, pageid, logfd, mutex = None):
		domain = \
		r"http://www.pixiv.net/search.php?word=%s&order=date_d"%key+r"&p=%d"%pageid
		enum = 0
		num = 0
		html = self.getHtml(domain).text
		if pString.isNoItem(html):
			return False
		ilist = pString.getIidByFind(html)
		for iid in ilist:
			if iid == "":
				#print(domain,"HAS null iid")
				continue
			enum += logfd.begin(iid + '_0')
			num += 1
		#print(domain,num,enum)
		return True
	def findT(self, args, mutex):
		return self.find(args[0], args[1], args[2], mutex)
	#从图片id中获取图像下载信息
	def get(self, iid, adir,logfd, mutex = None):
		url = self.getIid(iid)
		if url == []:
			return True
		if len(url)>1:
			adir += 'pixiv%s/'%iid
			createFile(adir)
		#相册的处理
		for i in range(len(url)):
			filename = adir + 'pixiv%s%s%s'%\
			(iid, '' if len(url) == 1 else ("_" + str(i)), pString.getSuffix(url[i]))
			if not fileExist(filename):
				self.__count()
			ret = []
			ret.append(url[i])
			ret.append(self.getDomain(iid))
			ret.append(filename)
			logfd.work(iid + '_' + str(i), ret)
		return True
	def getT(self, args, mutex):
		return self.get(args[0], args[1], args[2], mutex)
	#下载
	def down(self, iid, url, refer, filename, logfd, mutex = None):
		if fileExist(filename):
			self.add_job('write', iid, None, filename, logfd)
			return True
		response = self.getHtml(url, stream = True, headers = makeHeader(refer))
		if mutex: mutex.acquire()
		createFile(filename)
		self.add_job('write', iid, response, filename, logfd)
		if mutex: mutex.release()
		return True
	def downT(self, args, mutex):
		return self.down(args[0], args[1], args[2], args[3], args[4], mutex)
	#写入文件
	def write(self, iid, res, filename, logfd, mutex = None):
		#为句柄错误预留
		#if mutex: mutex.acquire()
		if res == None:
			logfd.end(iid)
			return True
		with open(filename, "wb") as fd:
			fd.write(res.content)
			fd.flush()
		#if mutex: mutex.release()
		logfd.end(iid)
		return True
	def writeT(self, args, mutex):
		return self.write(args[0], args[1], args[2], args[3], mutex)
	#从图片id获取图片地址
	def getDomain(self, iid, mode = 'medium'):
		domain = r"http://www.pixiv.net/member_illust.php?mode=%s&illust_id=%s"%(mode,iid)
		return domain
	#从图片id中获取图片下载地址
	def getIid(self, iid):
		domain = self.getDomain(iid)
		html = self.getHtml(domain).text
		big = pString.getBig(html)
		#如果是mode=big的图片
		if len(big) !=0:
			bigD = self.getDomain(big[0],'big')
			html = self.getHtml(bigD, headers = makeHeader(domain)).text
			ret = pString.getBigPic(html)
			return ret
		else:
			mg = pString.getManga(html)
			#如果是mode=manga类型的图片
			if len(mg) != 0:
				domain = self.getDomain(mg[0],'manga')
				html = self.getHtml(domain).text
				ret = pString.getMangaPic(html)
				pagelen = len(ret)
				ret = []
				for i in range(pagelen):
					mangaD = self.getDomain(mg[0],'manga_big')+"&page=%d"%i
					html = self.getHtml(mangaD).text
					url = pString.getBigPic(html)
					ret.append(url[0])
				return ret
			#普通的单张图片
			else:
				ret = pString.getPic(html)
				return ret
	#为按照画师下载预留
	def getPid(self):
		pass
#包装好的命令行操作, cFunc系列应该写入底层
class SpiderCmd(Spider):
	#构造函数
	def __init__(self):
		super(SpiderCmd, self).__init__()
		self.log = makeLog.mainLog()
		self.flag_login = False
	#登录
	def clogin(self):
		global userFile
		while True:
			user = User(userFile)
			print("登录中...")
			if self.login(user):
				print("登陆成功！\n")
				break
			else:
				print("登录失败!\n")
			if os.path.exists("userFile.pickle"):
				os.remove("userFile.pickle")
		self.flag_login = True
	#获取所有图片id
	def cFind(self):
		if not self.flag_login: self.clogin()
		keylist = self.log.getName()
		for key in keylist:
			logfd = self.log.getLog(key)
			tags = self.log.getTag(key)
			for tag in tags:
				self.set_stat('find', 'flag', True)
				pageid = 1
				while self.get_stat('find','flag'):
					for i in range(200):
						p = pageid + i
						self.add_job('find', tag, p, logfd)
					pageid += 200
					self.wait_allcomplete("查询 条目 [%s]  关键词 [%s] 前 %s 页完成"%(key, tag, pageid-1))
	#获取所有下载地址
	def cGet(self):
		if not self.flag_login: self.clogin()
		keylist = self.log.getName()
		for key in keylist:
			adir = defaultDir + pString.checkDirName(key) + '/'
			logfd = self.log.getLog(key)
			iidlist = logfd.get()
			locallist = []
			for iid in iidlist:
				locallist.append(iid)
			for iid in locallist:
				self.add_job('get', iid[:-2], adir, logfd)
			self.wait_allcomplete("获取下载地址完成")
	#下载图片
	def cDown(self):
		keylist = self.log.getName()
		for key in keylist:
			logfd = self.log.getLog(key)
			ddict = logfd.getDown()
			#使用深复制
			localdict = {}
			for iid in ddict:
				localdict[iid] = ddict[iid]
			for iid in localdict:
				d = localdict[iid]
				url = d[0]
				refer = d[1]
				filename = d[2]
				self.add_job('down', iid, url, refer, filename, logfd)
		self.wait_allcomplete("下载完成")
	#一个工作进程
	def work(self):
		self.recount()
		self.cFind()
		self.cGet()
		self.cDown()
	#添加条目
	def add(self):
		msg = "输入一个图片条目，按照如下格式\n\
		\t条目名称 关键字1 关键字2 ....\n关键字和条目间用空格隔开\n"
		data = input(msg)
		self.log.append(data)
	#删除条目
	def remove(self):
		msg = "请输入需要删除的条目名称:\n\t"
		data = input(msg)
		try:
			self.log.delete(data)
			print("删除成功!\n")
		except Exception as e:
			print(e)
	#输出所有条目
	def prtag(self):
		namelist = self.log.getName()
		print("    %s\t['%s']"%('条目名'+(17*' '),'关键字'))
		for name in namelist:
			tags = self.log.getTag(name)
			print("    %s\t"%(name+' '*(20-len(name))),end = "")
			for tag in tags:
				print(repr(tag), end = " ")
			print()
#命令行交互控制器
def controller():
	work = SpiderCmd()
	while True:
		print("程序首页")
		print("当前存在条目:")
		work.prtag()
		msg = '\n输入序号启动指定功能\n\
			0.退出\n\
			1.下载所有Tag\n\
			2.新建Tag\n\
			3.删除Tag\n'
		mode = input(msg)
		if mode == "0":
			break
		elif mode == "1":
			work.work()
		elif mode == "2":
			work.add()
		elif mode == "3":
			work.remove()
		else:
			print("序号错误")
def main():
	controller()
	pass
if __name__ == '__main__':
	main()
