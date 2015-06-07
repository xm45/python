#coding=utf-8
#! /usr/bin/env python
import json
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
			continue
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
def getLineInAlbum(data, *args):
	lines = data.split('\n')
	retlist = []
	for arg in args:
		retlist.append(getValueByLine(lines[arg-1]))
	return retlist
def getSuffix(name):
	flag = False
	suf = ""
	for i in range(-1,-(len(name)+1),-1):
		suf = name[i] + suf
		if name[i] == '.':
			flag = True
			break
		elif name[i] == '/':
			break
	return suf
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