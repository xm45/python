#coding=utf-8
#! /usr/bin/env python
import sys,os
import re
import base64
import uuid
import imghdr

recursion = True
suf = ['.txt','.c','.cpp','.h','.java','.cs','.py','.pyw','.md']
count = {}

def getSuffix(name):
	suffix = r".*(?P<suffix>\.[^\/\\]*)$"
	regex = re.compile(suffix)
	ans = regex.search(name)
	if ans:
		return ans.groupdict()['suffix']
	else:
		return ''
def tj(data):
	global count
	for c in data:
		if c in count:
			count[c] += 1
		else:
			count[c] = 1
def dfs(cwpath, tab):
	global suf,recursion
	print(tab + cwpath)
	dirname = os.listdir(cwpath)
	for filename in dirname:
		child = os.path.join(cwpath, filename)
		if filename == "org": continue
		if os.path.isdir(child):
			if recursion: dfs(child, tab + '\t')
		else:
			if filename[0] == "_": continue
			if not getSuffix(child) in suf: continue
			print("\t" + tab + child)
			with open(child, "r", encoding = "UTF-8") as fd:
				tj(fd.read())
		#print(child)
selfname = __file__
cwpath = os.getcwd()
dfs(cwpath, "")
count = sorted(count.items(), key = lambda d:d[1])
for c in count:
	print(repr(c))
import winsound
#winsound.PlaySound('SystemHand', 0)
