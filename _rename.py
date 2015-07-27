#coding=utf-8
#! /usr/bin/env python
import sys,os
import re
import base64
import uuid
import imghdr

flag = True
double = False

def getSuffix(name):
	suffix = r".*(?P<suffix>\.[^\/\\]*)$"
	regex = re.compile(suffix)
	ans = regex.search(name)
	if ans:
		return ans.groupdict()['suffix']
	else:
		return ''
def u2str(uu):
	#8-4-4-4-12
	uu = str(uu)
	ret = uu[0:8]+uu[9:13]+uu[14:18]+uu[19:23]+uu[24:36]
	return ret
def getNname(filename):
	if not os.path.isfile(filename):
		return None
	if 'pixiv' in filename:
		return None
	suf = getSuffix(filename)
	imgType = imghdr.what(filename)
	if imgType:
		suf = '.' + str(imgType)
	if suf == '.jpeg':
		suf = '.jpg'
	suf = suf.lower()
	if not suf in ['.bmp','.jpg','.png','.gif']:
		return None
	with open(filename,"rb") as fd:
		data = base64.b64encode(fd.read())
	data = str(data, encoding = 'utf-8')
	uu = uuid.uuid3(uuid.NAMESPACE_DNS, data)
	uustr = u2str(uu)
	uuint = str(uu.int)
	uuint10 = int(uuint[-10:])
	uustr = "%010d"%uuint10
	newname = uustr + suf
	return newname
def dfs(cwpath, tab):
	global nameset
	print(tab + cwpath)
	dirname = os.listdir(cwpath)
	for filename in dirname:
		child = os.path.join(cwpath, filename)
		if os.path.isdir(child):
			dfs(child, tab + '\t')
		else:
			#nname = getNname(child)
			nname = filename
			while nname in nameset:
				nname = '_' + nname
			#print(child, nname)
			os.rename(child, nname)
			#print(tab + '\t' + child , 'file' , nname)
		#print(child)
selfname = __file__
cwpath = os.getcwd()
with open('_uuid.txt') as fd:
	data = fd.read()
nameset = set(data.split('\n'))
#print(nameset)
dfs(cwpath, "")

import winsound
#winsound.PlaySound('SystemHand', 0)
