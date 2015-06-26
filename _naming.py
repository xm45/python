#coding=utf-8
#! /usr/bin/env python
import sys,os
import re
import base64
import uuid
import imghdr

flag = True

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
selfname = __file__
cwpath = os.getcwd()
print(cwpath)
wt = []
for filename in os.listdir(cwpath):
	if filename == selfname:
		continue
	if not os.path.isfile(filename):
		continue
	if 'pixiv' in filename:
		print(filename, filename)
		continue
	suf = getSuffix(filename)
	imgType = imghdr.what(filename)
	if imgType:
		suf = '.' + str(imgType)
	if suf == '.jpeg':
		suf = '.jpg'
	suf = suf.lower()
	print(suf)
	if not suf in ['.bmp','.jpg','.png','.gif']:
		continue
	#print(cwpath,filename)
	with open(cwpath+'/'+filename,"rb") as fd:
		data = base64.b64encode(fd.read())
	data = str(data, encoding = 'utf-8')
	uu = uuid.uuid3(uuid.NAMESPACE_DNS, data)
	uustr = u2str(uu)
	uuint = str(uu.int)
	uuint10 = int(uuint[-10:])
	uustr = "%010d"%uuint10
	newname = uustr + suf
	if newname == filename:
		print(filename, newname)
		continue
	if os.path.exists(newname):
		wt.append((filename,int(uuint10),suf))
	else:
		if flag:
			os.rename(filename, newname)
		print(filename, newname)
for filename,uuint10,suf in wt:
	newname = "%010d"%uuint10 + suf
	while os.path.exists(newname):
		if filename == newname:
			break
		uuint10 += 1
		newname = "%010d"%uuint10 + suf
	if filename == newname:
		print(filename, newname)
		continue
	if flag:
		os.rename(filename, newname)
	print(filename, newname)
import winsound
winsound.PlaySound('SystemHand', winsound.SND_ALIAS)
