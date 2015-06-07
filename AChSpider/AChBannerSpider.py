#coding=utf-8
#! /usr/bin/env python
import urllib.request
import re
import os

#
directory = r'acfunh/'
domain = r"http://cover.acfunwiki.org/h/";

#
suffix = ['jpg','jpeg','jpe','png','gif','bmp']
rootname = '%%0%dd.%s'

#
align = 4
error_num = 30
#
def getSuf(html, suf):
	name = rootname%(align,suf)
	url = domain + name
	dname = directory+suf+'/'
	fname = dname + name;
	i,err,num,flag = 1,0,0,0
	if os.path.isdir(dname):
		pass
	else:
		os.mkdir(dname)
	while err<error_num:
		if os.path.exists(fname%i):
			err,flag = 0,1
		else:
			try:
				urllib.request.urlretrieve(url%i, fname%i);
				err,flag = 0,1
				num += 1
				print("%s get"%url%i,end="\n")
			except:
				err += 1
				print("%s can't found"%url%i,end="\n")
		i += 1
	if flag==0:
		os.rmdir(dname)
	print("%s have %d new picture"%(suf,num))
#
def main():
	if os.path.isdir(directory):
		pass
	else:
		os.mkdir(directory)
	for suf in suffix:
		getSuf(domain,suf)
#
if __name__ == '__main__':
	main()