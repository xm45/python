#coding=utf-8
#! /usr/bin/env python
import sys,os
import re
import base64
import uuid
import imghdr
#模式类型
mode = ["line", "char", "class"]
#选择模式与是否递归文件夹
flag = "line"
recursion = True
#文件类型
doc = ['.txt', '.md','.conf']
code = ['.c', '.cpp', '.h', '.cs', '.py', '.pyw', '.php', '.java', '.js','.sh']
web = ['.html', '.css']
suf = []
#选择检测的文件
suf += code
suf += web
suf += doc
#选择不检测的文件夹与文件
discount = []
distj = []
#discount += ['config','org','errors','system','user_guide','lib']
#distj += ['welcome_message.php','index.html','Welcome.php',"license.txt","index.php"]
#是否展开不检测的文件夹
recdiscount = False
#
count = {}
linenum = 0
classnum = 0
countsuf = {}
#
encoding = ['utf-8', 'gbk', 'ansi', 'ascii','big5']
#
comment = False
def getSuffix(name):
	suffix = r".*(?P<suffix>\.[^\/\\]*)$"
	regex = re.compile(suffix)
	ans = regex.search(name)
	if ans:
		return ans.groupdict()['suffix']
	else:
		return ''
def tjchar(data):
	global count
	for c in data:
		if re.match('[\u4e00-\u9fa5]+', c):
			continue
		if c in count:
			count[c] += 1
		else:
			count[c] = 1
	return data.count('\n')
def isUse(line):
	global comment
	if line.find("//") != -1:
		return False
	if line.find("/*") != -1:
		if line.find("*/") == -1:
			comment = True
		return False
	if line.find("*/") != -1:
		comment = False
		return False
	if line.find("\t#") != -1:
		return False
	if line == "\n" or line == "":
		return False
	return not comment
def tjline(data):
	global linenum
	ret = 0
	dataline = data.split('\n')
	for line in dataline:
		if isUse(line):
			ret += 1;
	linenum += ret
	return ret
def tjclass(data):
	global classnum
	ret = data.count("class ")
	classnum += ret
	return ret
def tj(data, nowsuf):
	global flag,countsuf,comment
	comment = False
	ret = 0;
	if flag == "char":
		ret = tjchar(data)
	elif flag == "line":
		ret = tjline(data)
	elif flag == "class":
		ret = tjclass(data)
	if nowsuf in countsuf:
		countsuf[nowsuf] += ret
	else:
		countsuf[nowsuf] = ret
	return ret;
def dfs(cwpath, tab, tjflag = True):
	global suf,recursion,encoding,recdiscount,discount
	#print(tab + repr(cwpath))
	dirname = os.listdir(cwpath)
	for filename in dirname:
		child = os.path.join(cwpath, filename)
		if os.path.isdir(child):
			print("\t" + tab + repr(filename) + ":", end = "")
			nowdis = filename in discount
			if not recdiscount and nowdis:
				print("...")
			else:
				print()
			if recursion:
				if not nowdis or recdiscount:
					dfs(child, tab + '\t', tjflag and not nowdis)
		else:
			#过滤掉开头为下划线的文件
			if filename[0] == "_": continue
			#过滤掉后缀不符合的文件
			nowsuf = getSuffix(child)
			if not nowsuf in suf:
				print("\t" + tab + repr(filename))
				continue
			print("\t" + tab + repr(filename) + "*", end = "\t")
			if tjflag and not filename in distj:
				for ecd in encoding:
					try:
						with open(child, "r", encoding = ecd) as fd:
							print(tj(fd.read(), nowsuf), end = "")
						break
					except:
						pass
			print()
		#print(child)
selfname = __file__
cwpath = os.getcwd()
print(repr(cwpath))
dfs(cwpath, "")
if flag == "char":
	count = sorted(count.items(), key = lambda d:d[1])
	for c in count:
		print(repr(c))
	print(sum(map(lambda x: x[1], count)))
elif flag == "line":
	print(linenum)
elif flag == "class":
	print(classnum)
print()
for nowsuf in countsuf:
	print("%s : %d"%(nowsuf,countsuf[nowsuf]))