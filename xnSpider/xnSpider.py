#coding=utf-8
#! /usr/bin/env python
import requests,http,urllib
import sys,os,time
import re,pickle

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
	pool = threadPool.Pool(50)
	session = requests.session()
	#
	albumlist = []
	cnt = 0
	def __init__(self):
		pass
	def login(self, user, retry=True):
		#定义post的参数
		reqdata={'email':user.username,
		'password':user.password,
		'autoLogin':'true',
		'origURL':'http://www.renren.com/home',
		'domain':'renren.com'
		}
		response = self.session.post("http://www.renren.com/ajaxLogin/login?1=1",data=reqdata)
		tjson = response.text
		resdict = xnString.j2o(tjson)
		if resdict['code'] == True:
			print("\n登陆成功！")
			return True
		else:
			print("\n登录失败！")
			print(retdict['failDescription'])
			return False
	def logout(self):
		response = self.session.get("http://www.renren.com/Logout.do")
		print(response)
	def getList(self, Uid):
		response = self.session.get("http://photo.renren.com/photo/%s/albumlist/v7"%Uid)
		r = re.compile("'albumList': \[.*\]")
		reslist = r.findall(response.text)
		if reslist == []:
			print("获取用户信息失败")
			return
		tjson = reslist[0][13:]
		alist = xnString.j2o(tjson)
		for adict in alist:
			self.albumlist.append(adict["albumId"])
	def getAlbum(self, Uid, Aid, directory = r'renren/', prflag = True):
		plist = r'http://photo.renren.com/photo/%s/album-%s/bypage/ajax/v7?page=%d&pageSize=100'
		address = "http://photo.renren.com/photo/%s/album-%s/v7"%(Uid,Aid)
		response = self.session.get(address)
		rstr = r'"photoList":\{[\s\S]*\}\}'
		r = re.compile(rstr)
		reslist = r.findall(response.text)
		if reslist == []:
			print("获取相册信息失败")
			return
		tjson = reslist[0][12:len(reslist[0])-1]
		albumId,albumName,count = xnString.getLineInAlbum(tjson,3,4,7)
		#
		self.cnt += count
		#
		if count == 0:
			return
		pageId = 1
		adir = directory+xnString.checkDirName(albumName)+'/'
		createFile(adir)
		while (pageId-1)*100 <= count:
			page = plist%(Uid, Aid, pageId)
			response = self.session.get(page)
			tjson = response.text
			pdict = xnString.j2o(tjson)
			if "photoList" in pdict:
				photolist = pdict['photoList']
				for photo in photolist:
					self.pool.add_job(self.getPicT, photo, adir, prflag)
					#getPic(photo, adir)
			else:
				print("no photoList in User:%s Album:%s Page:%d",Uid,Aid,pageId)
			pageId += 1
		#pool.wait_allcomplete()
		if prflag:
			print("相册<%s>开始下载了"%albumName,end="")
		else:
			print("相册<%s>开始下载了"%albumName)
	def getPic(self, photo, directory = r'renren/', prflag = True):
		url = photo['url']
		pos = str(photo['position'])
		filename = directory+pos+xnString.getSuffix(url)
		if os.path.exists(filename):
			if prflag:
				print('|',end="",flush=True)
			return
		else:
			response = self.session.get(url,stream = True)
			with open(filename,"wb") as fd:
				fd.write(response.content)
			if prflag:
				print('*',end="",flush=True)
	def getPicT(self, args):
		self.getPic(args[0],args[1],args[2])
	#
	def getbyUser(self, Uid, Uname="", directory = r'renren/',prflag = True):
		self.albumlist = []
		self.getList(Uid)
		if Uname == "":
			fname = directory+str(Uid)+'/'
		else:
			fname = directory+str(Uname)+'/'
		for albumId in self.albumlist:
			self.getAlbum(Uid,albumId,fname,prflag)
	def getAll(self):
		response = self.session.get("http://friend.renren.com/groupsdata")
		res_nospace = response.text.strip()
		lines = res_nospace.split('\n')
		line_friend = lines[6].strip()
		friends = xnString.j2o(line_friend[11:-1])
		for f in friends:
			print("\n",f['fname'],f['fid'])
			self.getbyUser(f['fid'], f['fname'], prflag = True)
			self.pool.wait_allcomplete("该用户下载完成")

def controller():
	work = Spider()
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
			3.下载指定相册\n')
		if mode == "0":
			return
		elif mode == "1":
			work.getAll()
		elif mode == "2":
			Uid = input('假设该用户主页为：http://www.renren.com/用户id/profile，请输入该id：')
			print("开始解析与下载\n\
				'|'代表检索到一张已存在图片\n\
				'*'代表下载完一张未下载图片\n")
			work.cnt = 0
			start = time.time()
			work.getbyUser(Uid)
			work.pool.wait_allcomplete()
			end = time.time()
			print("总共 %s 张图片  耗时 %s"%(work.cnt, end-start))
		elif mode == "3":
			Uid = input('假设该用户主页为：http://photo.renren.com/photo/用户id/album-相册id，请输入用户id：')
			Aid = input('假设该用户主页为：http://photo.renren.com/photo/用户id/album-相册id，请输入相册id：')
			print("开始解析与下载\n\
				'|'代表检索到一张已存在图片\n\
				'*'代表下载完一张未下载图片\n")
			work.cnt = 0
			start = time.time()
			work.getAlbum(Uid,Aid)
			work.pool.wait_allcomplete()
			end = time.time()
			print("总共 %s 张图片  耗时 %s"%(work.cnt, end-start))
		else:
			print("序号错误")
def main():
	controller()
if __name__ == '__main__':
	main()