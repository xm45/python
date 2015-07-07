#coding=utf-8
#! /usr/bin/env python
import json,re
import inspect
import enum
#获取函数名
def getFuncName():
	return inspect.stack()[1][3]
#json转换
def j2o(data, prerr=True, **args):
	try:
		return json.loads(data)
	except Exception as e:
		if prerr:
			print("Error: json to object")
			print("    data  :",data)
			print("    error :",e)
			print("    args  :",args)
		else:
			pass#raise e
		return None
def o2j(data):
	return json.dumps(data)
#替换斜杠
def replaceBackSlash(data):
	data = data.replace("\\","/")
	return data
#转化为json的格式
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
#检查文件名内容是否符合windows的条件
def checkDirName(name):
	ret = ""
	for c in name:
		if c in "/\\:*?\"<>|\n\r\t":
			ret += "#"
		elif c == '.':
			ret += "。"
		else:
			ret += c
	return ret
#获取文件的后缀名
def getSuffix(name):
	suffix = r".*(?P<suffix>\.[^\/\\\?]*)(?:\?[^\/\\\?]*){0,1}$"
	regex = re.compile(suffix)
	ans = regex.search(name)
	if ans:
		return ans.groupdict()['suffix']
	else:
		return ''
#判断是否是'未找到'网页
def isNoItem(html):
	return html.find("_no-item") != -1
#由查询网页获取图片id
def getIidByFind(html):
	restr = r"member_illust.php\?mode=medium&amp;illust_id=([0-9]*)"
	regex = re.compile(restr)
	ans = regex.findall(html)
	if ans:
		return set(ans)
	else:
		return set([])
#由图片网页获取相册信息
def getManga(html):
	rstr = r"member_illust\.php\?mode=manga&amp;illust_id=([0-9]*)"
	regex = re.compile(rstr)
	ans = regex.findall(html)
	return ans
#由图片网页获取动图(zip)信息
def getUgoku(html):
	rstr = r"ugokuIllustFullscreenData  = \{\"src\":\"([^ ,]*)\","
	regex = re.compile(rstr)
	ans = regex.findall(html)
	if ans:
		ans[0] = ans[0].replace("\\/","/")
		return ans
	else:
		return []
#由图片网页获取大图信息
def getBig(html):
	rstr = r"member_illust\.php\?mode=big&amp;illust_id=([0-9]*)"
	regex = re.compile(rstr)
	ans = regex.findall(html)
	if ans:
		return ans
	else:
		return []
#获取大图下载地址
def getBigPic(html):
	rstr = r"img src=\"([^ ,]*)\" onclick"
	regex = re.compile(rstr)
	ans = regex.findall(html)
	if ans:
		return ans
	else:
		return []
#获取相册图片下载地址
def getMangaPic(html):
	ans = getPic(html)
	if ans == []:
		rstr = r"pixiv.context.originalImages\[[0-9]*\] = \"([^ ,]*)\""
		regex = re.compile(rstr)
		ans = regex.findall(html)
		if ans:
			for i in range(len(ans)):
				ans[i] = ans[i].replace("\\/","/")
			return ans
	else:
		return ans
#获取图片下载地址,通用
def getPic(html):
	ans = getUgoku(html)
	if ans:
		return ans
	rstr = r"data-src=\"([^ ,]*)\" [^a]"
	regex = re.compile(rstr)
	ans = regex.findall(html)
	return ans
#获取origin-image图片地址,弃用
def getPicOrigin(html):
	rstr = r"data-src=\"([^ ,]*)\" class=\"original-image\""
	regex = re.compile(rstr)
	ans = regex.findall(html)
	return ans
#单个测试
def test(fun, filename):
	filename = "test/" + filename
	with open(filename, "r" , encoding = 'UTF-8') as fd:
		data = fd.read()
	ret = fun(data)
	print(fun,filename)
	print(type(ret))
	if type(ret) in [list,set,dict,tuple]:
		for i in ret:
			print(repr(i))
	else:
		print(repr(ret))
	print()
#全部测试
def __test():
	test(isNoItem,"noitem.html")
	test(getIidByFind,"findpage.html")
	test(getManga,"plist.html")
	test(getManga,"origin.html")
	test(getPic,"manga.html")
	test(getPicOrigin,"origin.html")
	test(getUgoku,"plist.html")
	test(getPic,"manga.html")
	test(getPic,"origin.html")
	test(getPic,"ugoku.html")

	test(getBig,"big.html")
	test(getBig,"big2.html")
	test(getBigPic,"bigpic.html")
	test(getBigPic,"bigpic2.html")
	test(getBigPic,"mangabig.html")

	test(getMangaPic,"manga_ct.html")
	test(getMangaPic,"manga.html")
	print("suf",getSuffix("/.a?1/b.dcd?s"))
#运行测试
def main():
	__test()
if __name__ == '__main__':
	main()