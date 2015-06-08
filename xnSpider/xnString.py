#coding=utf-8
#! /usr/bin/env python
import json,re
import inspect

def getFuncName():
	return inspect.stack()[1][3]

def j2o(data):
	try:
		return json.loads(data)
	except Exception as e:
		print("Error: json to object")
		print("    data  :",data)
		print("    error :",e)
def o2j(data):
	return json.dumps(data)
def replaceBackSlash(data):
	data.replace("\\","/")
	return data
def jsonFormat(data):
	ret = ""
	for c in data:
		if c == "\n":
			#continue
			pass
		elif c == "'":
			ret = ret + '"'
		else:
			ret = ret + c
	return ret
def getValueByLine(data):
	ret = ""
	flag = False
	for c in data:
		if flag:
			ret += c
		if c == ':':
			flag = True
	ret = ret[:-1]
	if ret[0] == "'" and ret [-1]== "'":
		ret = ret[1:-1]
	else:
		ret = int(ret)
	return ret
def checkDirName(name):
	ret = ""
	for c in name:
		if c in "/\\:*?\"<>|\n\r\t":
			ret += "特殊字符"
		elif c == '.':
			ret += "。"
		else:
			ret += c
	return ret
#
def getSuffix(name):
	suffix = r".*(?P<suffix>\.[^\/\\]*)$"
	regex = re.compile(suffix)
	ans = regex.search(name)
	if ans:
		return ans.groupdict()['suffix']
	else:
		return ''
def __testgetSuf():
	print(getFuncName()+"():")
	print(getSuffix("a.jpg"))
	print(getSuffix("/b.jpg"))
	print(getSuffix("a.b/c.jpg"))
	print(getSuffix("abds.dac.dw/"))
	print(getSuffix("abds.dac.dw/a\\"))
	print("")
#

#
httpPre = r"^(?:http://){0,1}"
suffix = r".*$"
userD = httpPre + r"www\.renren\.com/(?P<Uid>[0-9]*)\/profile" + suffix
listD = httpPre + r"photo\.renren\.com/photo/(?P<Uid>[0-9]*)/albumlist/v7" + suffix
albumD = httpPre + r"photo\.renren\.com/photo/(?P<Uid>[0-9]*)/album-(?P<Aid>[0-9]*)" + suffix
friendD = httpPre + r"friend\.renren\.com/(?:groupsdata|managefriends)" + suffix
__regex_domain_user = re.compile(userD)
__regex_domain_list = re.compile(listD)
__regex_domain_album = re.compile(albumD)
__regex_domain_friend = re.compile(friendD)
__regex_domain = {__regex_domain_user:'User',
				__regex_domain_list:'User',
				__regex_domain_album:'Album',
				__regex_domain_friend:'Friend'}
def analysisDomain(domain):
	global __regex_domain
	regex_list = __regex_domain
	#print(domain)
	for (regex,ret) in regex_list.items():
		ans = regex.search(domain)
		if ans:
			return [ret,ans.groupdict()]
def __testDomain():
	print(getFuncName(),"():")
	print(analysisDomain(r"http://www.renren.com/315134008/profile"))
	print(analysisDomain(r"http://photo.renren.com/photo/315134008/albumlist/v7#"))
	print(analysisDomain(r"http://photo.renren.com/photo/315134008/album-315134008/v7"))
	print(analysisDomain(r"http://friend.renren.com/managefriends"))
	print("")
#

#
title = r"\<title\>人人网 - (?P<Name>.*)\<\/title\>"
__regex_title = re.compile(title)
def getNameFromHtml(html):
	global __regex_title
	regex = __regex_title
	ans = regex.search(html)
	if ans:
		return ans.groupdict()['Name']
	else:
		return "NULL"
def __testgetNFH():
	print(getFuncName(),"():")
	with open("test/profile.html","r",encoding = 'UTF-8') as fd:
		print(getNameFromHtml(fd.read()))
	print("")
#

#
albumListFormat = r"'albumList': (?P<albumlist>\[.*\])"
__regex_albumlist = re.compile(albumListFormat)
def getAlbumlistFromHtml(html):
	global __regex_albumlist
	regex = __regex_albumlist
	ans = regex.search(html)
	if ans:
		albumlist = []
		albumdict = j2o(ans.groupdict()['albumlist'])
		for album in albumdict:
			albumlist.append(album['albumId'])
		return albumlist
	else:
		return []
def __testgetALFH():
	print(getFuncName(),"():")
	with open("test/albumlist.html","r",encoding = 'UTF-8') as fd:
		print(getAlbumlistFromHtml(fd.read()))
	print("")
#
albumMetadataFormat = r"nx\.data\.photo = \{\"photoList\":(?P<metadata>\{(?:.*\n)*\})\}\;\n"
__regex_album = re.compile(albumMetadataFormat)
def getAlbumFromHtml(html):
	global __regex_album
	regex = __regex_album
	ans = regex.search(html)
	if ans:
		metadata = ans.groupdict()['metadata']
		tjson = jsonFormat(metadata)
		album = j2o(tjson)
		return album
	else:
		return None
def __testgetAFH():
	print(getFuncName(),"():")
	with open("test/album.html","r",encoding = 'UTF-8') as fd:
		print(getAlbumFromHtml(fd.read()))
	print("")
#

#
def getPhotolist(text):
	lines = j2o(text)
	if 'photoList' in lines:
		ans = lines['photoList']
		return ans
	else:
		return None
def __testgetP():
	print(getFuncName(),"():")
	with open("test/photolist.html","r",encoding = 'UTF-8') as fd:
		print(getPhotolist(fd.read()))
	print("")
#

#
def __test():
	__testgetSuf()
	__testDomain()
	__testgetNFH()
	__testgetALFH()
	__testgetAFH()
	__testgetP()
#
def main():
	__test()
if __name__ == '__main__':
	main()