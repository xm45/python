#coding=utf-8
#! /usr/bin/env python
import requests,http,urllib
import sys,os,time
import re,pickle
import signal

import threadPool
import xnString
import makeLog

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
#
userFile = "userFile.pickle"
#
class User:
	username = ''
	password = ''
	filename = ''
	def __init__(self, fname):
		self.filename = fname
		if os.path.exists(self.filename):
			self.__load()
		else:
			self.stdio()
	def __load(self):
		fd = open(self.filename, "rb")
		self.username = pickle.load(fd)
		self.password = pickle.load(fd)
		self.filename = pickle.load(fd)
		fd.close()
		print("从文件中读入用户名和密码成功！")
	def __dump(self):
		fd = open(self.filename, "wb")
		pickle.dump(self.username,fd)
		pickle.dump(self.password,fd)
		pickle.dump(self.filename,fd)
		fd.close()
	def stdio(self):
		self.username = input("username:")
		self.password = input("password:")
		self.__dump()

class Spider:
	#
	__pool = threadPool.Pool(50)
	__session = requests.session()
	#
	__albumlist = []
	__cnt = 0
	#
	flag_pwm = True #print work message flag
	flag_pdm = True #print download message flag
	#
	def __init__(self,prwork = True, prdown = True):
		self.flag_pwm = prwork
		self.flag_pdm = prdown
	#
	def login(self, user):
		#定义post的参数
		reqdata={'email':user.username,
		'password':user.password,
		'autoLogin':'true',
		'origURL':'http://www.renren.com/home',
		'domain':'renren.com'
		}
		response = self.__session.post("http://www.renren.com/ajaxLogin/login?1=1",data=reqdata)
		tjson = response.text
		resdict = xnString.j2o(tjson)
		if resdict['code'] == True:
			if self.flag_pwm:
				print("\n登陆成功！")
			return True
		else:
			if self.flag_pwm:
				print("\n登录失败！")
				print(retdict['failDescription'])
			return False
	def logout(self):
		response = self.__session.get("http://www.renren.com/Logout.do")
		print(response)
	#
	def recount(self):
		self.__cnt = 0
	def __count(self, num = 1):
		self.__cnt += num
	def count(self):
		return self.__cnt
	def wait_allcomplete(self, data):
		self.__pool.wait_allcomplete(data)
	#
	def getList(self, Uid):
		response = self.__session.get("http://photo.renren.com/photo/%s/albumlist/v7"%Uid)
		alist = xnString.getAlbumlistFromHtml(response.text)
		if alist:
			self.albumlist = alist
		else:
			if self.flag_pwm:
				print("获取用户信息失败")
			return
	def getAlbum(self, Uid, Aid, directory = r'renren/'):
		plist = r'http://photo.renren.com/photo/%s/album-%s/bypage/ajax/v7?page=%d&pageSize=100'
		address = "http://photo.renren.com/photo/%s/album-%s/v7"%(Uid,Aid)
		response = self.__session.get(address)
		#
		metadata = xnString.getAlbumFromHtml(response.text)
		if metadata == None:
			if self.flag_pwm:
				print("获取相册信息失败，可能是因为加密")
			return
		#
		self.__cnt += metadata['photoCount']
		#
		if metadata['photoCount'] == 0:
			return
		pageId = 1
		adir = directory + xnString.checkDirName(metadata['albumName'])+'/'
		createFile(adir)
		while (pageId-1)*100 <= metadata['photoCount']:
			page = plist%(Uid, Aid, pageId)
			response = self.__session.get(page)
			photolist = xnString.getPhotolist(response.text)
			if photolist:
				for photo in photolist:
					self.__pool.add_job(self.getPicT, photo, adir)
					#getPic(photo, adir)
			else:
				if self.flag_pwm:
					print("找不到photoList, User:%s Album:%s Page:%d",Uid,Aid,pageId)
			pageId += 1
		#__pool.wait_allcomplete()
		if self.flag_pdm:
			print("相册<%s>开始下载了"%metadata['albumName'],end="")
		else:
			print("相册<%s>开始下载了"%metadata['albumName'])
	def getPic(self, photo, directory = r'renren/'):
		url = photo['url']
		pos = str(photo['position'])
		filename = directory + pos + xnString.getSuffix(url)
		if os.path.exists(filename):
			if self.flag_pdm:
				print('|',end="",flush=True)
			if os.path.getsize(filename) != 0:
				return
		response = self.__session.get(url,stream = True)
		with open(filename,"wb") as fd:
			fd.write(response.content)
		if self.flag_pdm:
			print('*',end="",flush = True)
	def getPicT(self, args):
		self.getPic(args[0],args[1])
	#
	def getUser(self, Uid, Uname="", directory = r'renren/'):
		self.albumlist = []
		if Uname == "":
			response = self.__session.get(r"http://www.renren.com/%s/profile"%Uid)
			Uname = xnString.getNameFromHtml(response.text)
			#fname = directory+str(Uid)+'/'
		if self.flag_pwm:
			print(Uid,Uname)
		self.getList(Uid)
		fname = directory+str(Uname)+'/'
		for albumId in self.albumlist:
			self.getAlbum(Uid,albumId,fname)
	def getAll(self):
		temp = self.flag_pdm
		self.flag_pdm = False
		response = self.__session.get("http://friend.renren.com/groupsdata")
		res_nospace = response.text.strip()
		lines = res_nospace.split('\n')
		line_friend = lines[6].strip()
		friends = xnString.j2o(line_friend[11:-1])
		for f in friends:
			self.getUser(f['fid'], f['fname'])
			if self.flag_pwm:
				self.wait_allcomplete("该用户下载完成\n")
				pass
		self.flag_pdm = temp
	def getByDomain(self):
		domain = input(":")
		mode,idDict = xnString.analysisDomain(domain)
class SpiderCmd(Spider):
	def __init__(self):
		super(SpiderCmd, self).__init__()
	def getByAll(self):
		self.recount()
		start = time.time()
		self.getAll()
		self.wait_allcomplete("")
		end = time.time()
		print("总共 %s 张图片  耗时 %s"%(self.count(), end-start))
	def getByUser(self):
		Uid = input('假设该用户主页为：http://www.renren.com/用户id/profile，请输入该id：')
		print("开始解析与下载\n\
			'|'代表检索到一张已存在图片\n\
			'*'代表下载完一张未下载图片\n")
		self.__cnt = 0
		start = time.time()
		self.getUser(Uid)
		self.wait_allcomplete("")
		end = time.time()
		print("总共 %s 张图片  耗时 %s"%(self.count(), end-start))
	def getByAlbum(self):
		Uid = input('假设该用户主页为：http://photo.renren.com/photo/用户id/album-相册id，请输入用户id：')
		Aid = input('假设该用户主页为：http://photo.renren.com/photo/用户id/album-相册id，请输入相册id：')
		print("开始解析与下载\n\
			'|'代表检索到一张已存在图片\n\
			'*'代表下载完一张未下载图片\n")
		self.__cnt = 0
		start = time.time()
		self.getAlbum(Uid,Aid)
		self.wait_allcomplete()
		end = time.time()
		print("总共 %s 张图片  耗时 %s"%(self.count(), end-start))
def controller():
	global userFile
	work = SpiderCmd()
	while True:
		user = User(userFile)
		print("删除%s文件即可重新设置账户信息\n"%userFile)
		print("本程序未使用验证码，短时间内多次启动将无法使用")
		print("重复登录严重者将被暂时冻结人人账号(可自行解封)")
		if work.login(user):
			break
		if os.path.exists("userFile.pickle"):
			os.remove("userFile.pickle")
	while True:
		mode = input('\n输入序号启动指定功能\n\
			0.退出\n\
			1.下载本账户全部好友的相册\n\
			2.下载指定用户的全部相册\n\
			3.下载指定相册\n\
			4.输入网址，自动分析类型\n')
		if mode == "0":
			break
		elif mode == "1":
			work.getByAll()
		elif mode == "2":
			work.getByUser()
		elif mode == "3":
			work.getByAlbum()
		elif mode == "4":
			work.getByDomain()
		else:
			print("序号错误")
def main():
	controller()
if __name__ == '__main__':
	main()