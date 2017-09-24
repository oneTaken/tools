import requests
import os
import glob
from bs4 import BeautifulSoup
import json
import bs4
import re
import time
import random


def downImgs(start, end, startUrlIndex):
    urlContent = os.getcwd() + os.sep + 'urls_updated' + os.sep
    urlTxt = glob.glob(urlContent + '*.txt')
    for txtName in urlTxt[start:end]:
        downImgsByTxtName(txtName, startUrlIndex)
        startUrlIndex = 0


def downImgsByTxtName(txtName, startUrlIndex):
    # proxies = getProxies()
    imgSaveContent = 'D:\project\imgLabeling'
    total = 0

    fi = open(txtName)
    imgUrls = fi.readlines()
    url_pre = 'http://www.3lian.com'
    print('Parsing {0}.'.format(txtName))
    urls = imgUrls[0][1:-1].replace(' ', '')

    urls = urls.replace('"', '')
    urls = urls.split(',')
    lenUrl = len(urls)

    htmlStart = '<div class="container">'
    htmlEnd = '<div class="art_bottom">'
    for j, url in enumerate(urls[startUrlIndex:]):
        print('{0}/{1}. parsing url:{2}'.format(j + startUrlIndex, lenUrl, url))
        r = requests.get(url_pre + url)
        try:
            html = r.content.decode('gbk')
        except UnicodeDecodeError:
            with open('decodeError.txt', 'a') as ft:
                ft.writelines(url + '\n')
                continue
        soupHtml = BeautifulSoup(html, 'html.parser')

        try:
            start_html = re.split(htmlStart, html)[1]
            end_html = re.split(htmlEnd, start_html)[0]
            soupMain = BeautifulSoup(end_html, 'html.parser')
            mainContent = soupMain.find_all(checkImg2)
        except IndexError:
            mainContent = soupHtml.find_all(checkImg3)

        if len(mainContent):
            tips = soupHtml.find('div', class_='tips')
            try:
                if hasattr(tips, 'contents'):
                    if isinstance(tips.contents[0], bs4.element.Tag):
                        tips = str(tips.p.string) if tips.p is not None else ''
                    elif isinstance(tips.contents[0], bs4.element.NavigableString):
                        tips = str(tips.contents[0])
                    else:
                        tips = ''
                else:
                    tips = ''
            except:
                tips = ''
            try:
                alt = soupHtml.find('div', class_='art_tit').h1
                alt = '' if alt is None else alt.string
            except:
                alt = ''

            if 'logo_L' in html:
                categoryTag = soupHtml.find('div', class_='logo_L')
            elif 'gg_cnt_left' in html:
                categoryTag = soupHtml.find('div', class_='gg_cnt_left')
            elif 'adr_items' in html:
                categoryTag = soupHtml.find(class_='li_cont')
            else:
                categoryTag = None
            if categoryTag is None:
                continue

            categorys = []
            for tag in categoryTag.descendants:
                if hasattr(tag, 'has_attr') and tag.has_attr('href'):
                    categorys.append(nameInWindows(str(tag.string).strip()))
            catContent = imgSaveContent + os.sep + os.sep.join(categorys)

            urlContent = catContent + os.sep + url.strip().replace('/', '_')

            if not os.path.exists(urlContent):
                try:
                    os.makedirs(urlContent)
                except FileExistsError:
                    pass
            urlClean = []
            lenImg = len(mainContent)
            for k, imgTag in enumerate(mainContent):
                gifUrl = imgTag['src']
                downImgName = urlContent + os.sep + gifUrl.split('/')[-1]
                if os.path.exists(downImgName):
                    continue
                    # pass
                # print(downImgName)
                urlClean.append(gifUrl)
                with open(downImgName, 'wb') as imgFi:
                    binary_file = requests.get(gifUrl).content
                    imgFi.write(binary_file)
                    imgFi.close()
                total += 1
                print('downloading {0}/{1} imgs.total:{2}'.format(k, lenImg, total))
                # time.sleep(0.5)

            if len(urlClean):
                jsonDict = dict()
                jsonDict['tips'] = tips
                jsonDict['alt'] = alt
                jsonDict['urlClean'] = urlClean
                json.dump(jsonDict, open(urlContent+'/info.json', 'w'))
                print('url:{}json writing done.'.format(url))

    fi.close()


def getProxies():
    proxies = []
    with open('proxy.txt') as fi:
        lines = fi.readlines()
        for line in lines:
            proxies.append(line.strip())
    return proxies

def checkImg(tag):
    return tag.has_attr('alt') and tag.has_attr('src') and tag['src'].split('.')[-1] in ['jpg', 'png', 'jpeg']


def checkImg2(tag):
    # 使用中间部分的内容，只需要包含src标签就可以了
    return tag.has_attr('src') and tag['src'].split('.')[-1] in ['jpg', 'png', 'jpeg']


def checkImg3(tag):
    return tag.name == 'img' and tag['src'].split('.')[-1] in ['jpg', 'jpeg', 'png']

def checkImgBackend(tag):
    return tag.has_attr('alt') and tag.has_attr('src')


def nameInWindows(nameString):
    '''
    for symbol in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        nameString = nameString.replace(symbol, '_')
    return nameString
    '''
    symbol = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    nameList = list(nameString)
    for i in range(len(nameList)):
        if nameList[i] in symbol:
            nameList[i] = '_'
    return ''.join(nameList)


def countDownedImg():
    pass


def checkUrlsUpdated():
    files = glob.glob(os.getcwd() + os.sep + 'urls_updated' + os.sep + '*.txt')
    for fileName in files:
        fi = open(fileName)
        lines = fi.readlines()
        for line in lines:
            line = line[1:-1].replace(' ','')
            line = line.replace('"','')
            urls = line.split(',')
            print('{}\t{}\t{}'.format(fileName,len(urls),len(list(set(urls)))))


def showImgBackend():
    backend = {'gif': 30014, 'jpg':	117820, 'png':	2159,'jpeg':	522}
    count = 150516
    urlContent = os.getcwd() + os.sep + 'urls/'
    urlTxt = glob.glob(urlContent + '*.txt')
    for i, txtName in enumerate(urlTxt):
        done = [0,1,2,10,11,12,13,14,15,16,17,18,19,20,21]
        number = txtName.split('_')[-1].split('.')[0]
        if int(number) in done:
            continue
        fi = open(txtName)
        imgUrls = fi.readlines()
        url_pre = 'http://www.3lian.com'
        print('checking ' + txtName)
        for j, url in enumerate(imgUrls[0][1:-1].split(',')):
            urlMod = url.replace(' ','')
            r = requests.get(url_pre + urlMod.replace('"', ''))
            r.encoding = 'utf-8'

            html = r.text
            print(html)
            soup = BeautifulSoup(html, 'html.parser')
            tags = soup.find_all(checkImgBackend)
            for k, tag in enumerate(tags):
                imgBackend = tag['src'].split('.')[-1]
                if imgBackend not in backend.keys():
                    backend[imgBackend] = 1
                else:
                    backend[imgBackend] += 1
                count += 1
                print('{}\t{}\t{}\t{}'.format(i,j,k,count))
        fi.close()
        with open('backend.txt', 'a') as ff:
            line = txtName + '\n'
            for x in backend.keys():
                line = line + x + '\t' + str(backend[x]) + '\n'
            line += 'total:\t%d'%(count) + '\n'
            ff.writelines(line)
        print(backend)


def testProxy():
    proxies = getProxies()
    time = 2
    for i in proxies:
        proxies = {
        'http': 'http://' + i
        }
        try:
            r = requests.get('http://httpbin.org/get', proxies=proxies)
            print(r.text)
        except :
            print(i)
            continue
            # print(i)

if __name__ == "__main__":
    testProxy()