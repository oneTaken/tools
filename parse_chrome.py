# -*- coding: utf-8 -*-
from __future__ import print_function
import os


class Chrome:
	def __init__(self):
		self.WhiteWords = ''

	def getUrlsFromChromeHistory(self):
		import sqlite3
		data_path = os.path.expanduser('~') + "\AppData\Local\Google\Chrome\User Data\Default"
		files = os.listdir(data_path)

		history_db = os.path.join(data_path, 'history')

		# querying the db
		try:
			c = sqlite3.connect(history_db)
			cursor = c.cursor()
			select_statement = "SELECT * FROM urls"
			urls = cursor.execute(select_statement).fetchall()
			return urls
		except Exception, e:
			print('The chrome brower must be closed when getting history because of the database lock protocol!')
			return None

	def getWordsFromUrl(self, urls):
		words = []
		words.extend(self.getWordsFromBaiduSearch(urls))
		words.extend(self.getWordsFromBaiduTranslate(urls))
		if '' in words:
			words.remove('')
		return list(set(words))

	def getWordsFromBaiduSearch(self, urls):
		searchWords = []
		for index, url in enumerate(urls):
			try:
				pattern = url[1]
				words = pattern.split('&')[0].split('wd=')[1]
				words = words.replace('+', ' ')
				words = words.replace('%20', ' ')
				try:
					words = words.encode('ascii')
					if self.check_words(words):
						searchWords.append(words)
					else:
						continue
				except Exception,e:
					continue
			except Exception,e:
				continue
		# unique words
		return list(set(searchWords))

	def getWordsFromBaiduTranslate(self, urls):
		translateWords = []
		pattern = '#en/zh/'
		for index, url in enumerate(urls):
			try:
				words = url[1].split(pattern)[1]
				if isinstance(words, unicode):
					words = words.encode('ascii')
				translateWords.append(words.replace('%20', ' '))
			except Exception, e:
				continue
		return list(set(translateWords))

	def check_words(self, words):
		if not isinstance(words, str):
			# print(type(words))
			print("Words must be string type ,got {} instead".format(type(words)))
			return False
		else:
			flag = True
			for word in words.split(' '):
				if not word.isalpha():
					flag = False
			return flag

	def addWhiteWords(self, word):
		# this is set for those common used words but not unknown english words
		"""
		git
		github
		linux
		baidu
		sougou
		python

		"""
		self.WhiteWords += '\n' + word

	def loadWhiteWords(self, name='WhiteWords.txt'):
		if not os.path.exists(name):
			print('{} does not exist!'.format(name))
			return False
		else:
			ww = open(name).readlines()
			# ww = list(set(ww))
			if '' in ww:
				ww.remove('')
			self.WhiteWords += ''.join(ww)
			return True

	def uniqueWhiteWords(self):
		words = self.WhiteWords.split('\n')
		self.WhiteWords = '\n'.join(list(set(words)))

	def showWhiteWords(self):
		print("The WhiteWords are as follows:")
		print(self.WhiteWords)

	def writeWhiteWords(self, mode='a'):
		if mode == 'a':
			with open('WhiteWords.txt', mode) as ww:
				ww.writelines(self.WhiteWords)
		elif mode == 'w':
			self.uniqueWhiteWords()
			self.loadWhiteWords()
			with open('WhiteWords.txt', mode) as ww:
				ww.writelines(self.WhiteWords)
		else:
			print('expected mode "a" or "w",got{} instead!'.format(mode))

	def filterWhiteWords(self, words):
		print('Filting words from WhiteWords...')
		for whiteWord in self.WhiteWords.split('\n'):
			for word in words:
				if whiteWord in word.lower():
					print("because of WhiteWOrd '{}' remove '{}'".format(whiteWord, word))
					words.remove(word)
		return words

	def saveWords(self, words, name='words',backend='.txt'):
		if backend == '.txt':
			with open(name+backend, 'w') as wordFile:
				wordFile.writelines(words)
		elif backend == '.png':
			pass
		else:
			print('Only .txt and .png are supported, got {} instead'.format(backend))

	def saveTxt(self):
		urls = self.getUrlsFromChromeHistory()
		words = self.getWordsFromUrl(urls)
		self.loadWhiteWords()
		words = self.filterWhiteWords(words)
		self.saveWords('\n'.join(words))


class Translate:
	def __init__(self):
		pass

	def searchFromBaiduTranslate(self, words):
		# not implemented
		import requests
		searchUrl = 'http://fanyi.baidu.com/'
		searchWay = '#en/zh/'
		head={'User-Agent':'Mozilla/5.0(Windows NT 6.1; win64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 59.0.3071.86Safari / 537.36'}
		result = requests.get(searchUrl + searchWay + words)
		return result

	def searchFromV2transapi(self, words):
		import requests
		import re
		request_url = 'http://fanyi.baidu.com/v2transapi'
		data = {'from': 'en', 'to': 'zh', 'query': words, 'transtype': 'translang', 'simple_means_flag': '3'}
		respond = requests.post(request_url, data=data)
		text = respond.content
		start = '"result":[[0,"'
		end = '"'
		# [\][u]\w{4} can't be rightly recognitized pattern '\uaaaa'
		pattern = '[u]\w{4}'
		part_text = text.split(start)[1].split(end)[0]
		result_like = re.compile(pattern)
		list_result = result_like.findall(part_text)
		result = ''.join(list_result).replace('u', r'\u')
		return result

	def parseUnicode(self, unicodeString):
		# param is like '\uaaaa\ubbbb'
		result = unicodeString.decode('unicode-escape')
		return result


class Work:
	def __init__(self,name='words.txt'):
		print("""
		You can manually change the words set you want to translate.
		delete some simple words or some you don't wang to translate
		""")
		self.name = name

	def txt2img(self):
		from PIL import Image, ImageFont, ImageDraw
		translate = Translate()
		BasicWidth = 300
		BasicHeight = 25

		with open(self.name) as wordsFile:
			text = wordsFile.readlines()
		for index, line in enumerate(text):
			try:
				translateResult = translate.searchFromV2transapi(line.replace('\n', ''))
				start = text[index].decode('utf-8')
				end = translate.parseUnicode(translateResult)
				text[index] = start.replace('\n', '') + ' '*(30-len(start)) + end + u'\n'
			except Exception,e:
				print('index: {}, line: {}'.format(index, line))
				continue

		im = Image.new("RGB", (BasicWidth, BasicHeight*len(text)), (255, 255, 255))
		dr = ImageDraw.Draw(im)
		font = ImageFont.truetype(os.path.join("fonts", "msyh.ttf"), 14)

		dr.multiline_text((10, 5), ''.join(text), font=font, fill="#000000")

		im.show()
		im.save("words.png")


class Test:
	def __init__(self):
		print("Test...")

	class TestChrome:
		def __init__(self):
			self.test = Chrome()
			self.className = "Chrome"

		def testGetUrlsFromChromeHistory(self):
			print("Testing class {0} function 'getUrlsFromChromeHistory'".format(self.className))
			print(self.test.getUrlsFromChromeHistory())

		def testGetWordsFromUrl(self):
			print("Testing class {0} function 'getWordsFromUrl'".format(self.className))
			urls = self.test.getUrlsFromChromeHistory()
			print(self.test.getWordsFromUrl(urls))

		def testAll(self):
			test = Chrome()
			urls = test.getUrlsFromChromeHistory()
			words = test.getWordsFromUrl(urls)
			test.loadWhiteWords()
			test.showWhiteWords()
			print('words before filtering are as follows:\n{}\n{}'.format(words, len(words)))
			words = test.filterWhiteWords(words)
			test.saveWords('\n'.join(words))
			print('words after filtering are as follows:\n{}\n{}'.format(words, len(words)))

	class TestTranslate:
		def __init__(self, words='english teacher'):
			self.words = words
			self.className = 'Translate'

		def testTranslate(self):
			print('Testing class "{0}" function "searchFromV2transapi"...'.format(self.className))
			translate = Translate()
			result = translate.searchFromV2transapi(self.words)
			unicode_result = translate.parseUnicode(result)
			print('word "{}" is translated into '.format(self.words), end='')
			print(unicode_result)

	def testAll(self):
		test1 = Test().TestTranslate()
		test1.testTranslate()
		test2 = Test().TestChrome()
		test2.testAll()
		work = Work()
		work.txt2img()


def run():
	chrome = Chrome()
	chrome.saveTxt()
	work = Work()
	work.txt2img()


if __name__ == "__main__":
	# test = Test()
	# test.testAll()
	run()
