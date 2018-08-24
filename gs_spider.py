# -*- coding:utf-8 -*-

import urllib.request, urllib.error
import re
import os
import queue
import time

# 定义一个类
class Spider:
    #爬取内容页分页的链接和内容页标题、描述
    def savePageInfo(self, _url, _position):

        url = _url   # 要爬的网址
        position = _position  # 本地地址
        try:

            req = urllib.request.Request(url)
            response = urllib.request.urlopen(req)
            buf = response.read()  # 获取网页源代码

            buf = buf.decode('utf-8')  # python3 参数更改了,现在读取的是bytes-like的,但参数要求是chart-like    
        
            flag = self.saveImg(url,position)

            if flag==False:
                print("no picture")
                response.close()
                return False
            
            regX = 'class="ArticleTitle".+\n.+>(.*)<' #获取图片标题
            title = re.findall(regX,buf)
            if len(title)!=0:
                title = title[0]
            

            regX = 'class="ArticleDesc".+b>(.*)</p>'
            desc = re.findall(regX,buf)  #获取图片描述
 
            if len(desc)!=0:
                desc = desc[0]
                title = title+'\n'+desc
            

            

            f = open(position + 'title.txt', 'w') #写入文件存储
            f.write(title)
            f.close()
            
            #获取同一图集的其它页面
            regX = 'class="NewPages".+\n.+\n.+'
            links = re.findall(regX,buf)
            if len(links)==0:
                return                
            links = links[0]
            regX = "<a href='(/.*?)'>[0-9]+"
            alllinks = re.findall(regX,links)

            for eachurl in alllinks:
                newlink = "http://www.umei.cc"+eachurl
                self.saveImg(newlink,position)

        except urllib.error.URLError as e:
            print('URLError: ' + str(e.reason))
        except ValueError as e:
            print('ValueError: ' + str(e))
        except Exception as e:
            time.sleep(2)
            print(e)
            return False

    #爬取内容页图片
    #'class="ImageBody".+\n.*[.|\n]?.+\n.*img.+src=["|\']{1}([^"\n]*)["|\']{1}'
    #'class="ImageBody".+\n.*[.|\n]?.+.*img.+src=["|\']{1}([^"\n]*)["|\']{1}'
    def saveImg(self,url,position,regX= 'class="ImageBody".+\n.*[.|\n]?.+[.|\n]?.*img.+src=["|\']{1}([^"\n]*)["|\']{1}'):

        headers = {'Host': 'i1.umei.cc',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
            'Referer': 'http://www.umei.cc/meinvtupian/',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            }

        try:

            req = urllib.request.Request(url)
            response = urllib.request.urlopen(req,None,10)
            buf = response.read()
            buf = buf.decode('utf-8')
            link = re.findall(regX, buf)
            print(link)
            if len(link)==0:
                response.close()
                return  False  
            if link[0] is None:
                response.close()
                return  False
            link = link[0]
            data = None
            req = urllib.request.Request(link, data, headers)
            response = urllib.request.urlopen(req)
            buf = response.read()

            pos = url.rindex('/')  # 图片url的最后一个斜杠
            pic_name = url[pos+1:-4]  # 图片的文件名
            
            f = open(position + pic_name + '.jpg', 'wb')
            f.write(buf)
            f.close()
            return True
        except urllib.error.URLError as e:
            print('URLError')
            return False
        except ValueError as e:
            print('ValueError')
            return False
        except Exception as e:
            print("timeout")
            return False
    #爬取内容页链接
    def getContentlink(self, _url, _position):

        position = _position
        url = _url
        try:
            req = urllib.request.Request(url)
            response = urllib.request.urlopen(req)
            buf = response.read()  # 获取网页源代码
            buf = buf.decode('utf-8') 

            regX = ' class="TypeList"[\s\S]*</ul>'
            tmp = re.findall(regX,buf)
            if len(tmp)==0:
                return
            tmp = tmp[0]
            regX = '<a href="(.*)".* class="TypeBigPics"'
            content = re.findall(regX,tmp)
            for eachcontent in content:
                pos = eachcontent.rindex('/')
                pic_dir_name = eachcontent[pos+1:-4]
                pos = position + pic_dir_name + '/'
                if os.path.isdir(pos):
                    continue
                os.mkdir(pos)
                print(eachcontent)
                flag = self.savePageInfo(eachcontent, pos)
                if flag == False:
                    os.rmdir(pos)
            response.close()

        except urllib.error.URLError as e:
            print("error")
        except OSError as e:
            print("OSerror")
    
    #爬取内容页分页链接
    def getContentpage(self, _url, _position):

        position = _position
        url = _url
        rep = urllib.request.Request(url)
        response = urllib.request.urlopen(rep)
        buf = response.read()
        buf = buf.decode("utf-8")

        regX = '.+href=.?(.+htm).?>末页'
        lastpage = re.findall(regX,buf)
        if len(lastpage)==0:
            lastpage = "1.htm"
        lastpage = lastpage[0]

        regX = '[0-9]+'
        pageindex = re.findall(regX,lastpage)
        if pageindex==None:
            pageindex = 1
        else:
            pageindex = pageindex[0]
        
        pageindex = int(pageindex,10)+1
        
        maxpage = 31
        if pageindex<maxpage:
            maxpage = pageindex

        time.sleep(0.3)
        for i in range(maxpage-1):

            
            tmp = i+1
            newlink = url+str(tmp)+".htm" #根据页数建立链接

            self.getContentlink(newlink, position)
            

    #获取各栏目链接，返回一个queue
    def getListpage(self,_url):

        url = _url
        try:
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)

            buf = response.read()
            buf = buf.decode('utf-8')

            regX = '(class="ShowNav".+\n.+)'
            tmp = re.findall(regX,buf)
            regX = '<a href="([^"]*)"'

            que = queue.Queue()

            for each in tmp:
                listpage = re.findall(regX,each)
                tmpregX = '.*/tushuotianxia.*'
                flag = re.search(tmpregX,listpage[0])
                if flag==None:
                    que.put(listpage)
            
            return que

        except urllib.error.URLError as e:
            print("error")


    def distrbuted_getImage(self, _url):
        url = _url
        tmp = re.findall('//(.*)',url)
        if len(tmp)==0:
            return
        tmp = tmp[0]
        newpos = 'F:/' + tmp
        if not os.path.isdir(newpos):
            os.makedirs(newpos)
        spider.getContentpage(url, newpos)
        print("finish")

### 网页爬取图片 ###


url = 'http://www.umei.cc/'


spider = Spider()


'''
listpagelink = spider.getListpage(url)
print("start spidering:")
i = 1
start = time.clock()
while listpagelink.empty()==False:
    contentlink = listpagelink.get()
    print("顶级栏目"+str(i)+":")
    k = 1
    for eachlink in contentlink:
        print("子栏目"+str(k)+":")      
        tmp = re.findall('//(.*)',eachlink)
        if len(tmp)==0:
            continue
        tmp = tmp[0]
        newpos = 'F:/' + tmp
        if not os.path.isdir(newpos):
            os.makedirs(newpos)
        spider.getContentpage(eachlink, newpos)
        print("子栏目"+str(k)+"已完成")
        end = time.clock()
        print("运行时间："+str(end-start)+"seconds")
        k = k + 1
    print("顶级栏目"+str(i)+"已完成")
    end = time.clock()
    print("运行时间："+str(end-start)+"seconds")
    i = i + 1
'''

suburl = "http://www.umei.cc/gaoxiaotupian/baoxiaotupian/"
spider.distrbuted_getImage(suburl)
#pos = "F:/beauty1/"
#url = "http://www.umei.cc/weimeitupian/oumeitupian/20378_2.htm"

#'class="ImageBody".+\n.*[.|\n]?.+img.+src=["|\']{1}([^"\n]*)["|\']{1}'
#spider.saveImg(url, pos,'class="ImageBody".+\n.*[.|\n]?.+\n.*img.+src=["|\']{1}([^"\n]*)["|\']{1}')
