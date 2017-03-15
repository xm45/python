#coding=utf-8
#! /usr/bin/env python
import sys,os
#是否递归
recursion = True
#是否直接删除
canDelete = True
#是否展开不检测的文件夹
recdiscount = False
#
count = {}
linenum = 0
classnum = 0
countsuf = {}
def dfs(dirname, name, tab = 0):
	global recursion
	#print(tab + repr(dirname))
	filelist = os.listdir(dirname)
	isEmpty = True
	print(tab*"\t" + repr(name) + "\t:")
	for filename in filelist:
		child = os.path.join(dirname, filename)
		if os.path.isdir(child):
			if recursion:
				childEmpty = dfs(child, filename, tab + 1)
				isEmpty = isEmpty and childEmpty
		else:
			print((tab+1)*"\t" + repr(filename) + "\t*")
			isEmpty = False
		#print(child)
	if isEmpty and canDelete:
		os.rmdir(dirname)
	print(tab*"\t" + repr(name) + ("\t!" if isEmpty else "\t$"))
	return isEmpty
selfname = __file__
cwpath = os.getcwd()
dfs(cwpath, cwpath)