# !/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import requests
import datetime
import json
import csv
import time
import random
import re
#----------module document----------
__pyVersion__ = '3.6.0'
__author__ = 'Zhongxin Yue'
#----------module document----------

__doc__ = '''                           A Page Scraper for Ctrip.
获取携程网单程机票信息 url:'http://flights.ctrip.com/domestic/Search/FirstRoute' 爬取方式：asyncio

默认爬取内容：默认爬取厦门到上海2017-4-4至2017-4-6 的机票信息,默认存储方式：csv

使用说明：可以在创建实例时依次给入参数
city1对应出发城市
city2对应到达城市
day1对应起始时间
day2对应最终时间
如crawler = Xiecheng(city1='BJS'，city='SHA',day1=(2017,4,4),day2=(2017,4,6)) 爬取北京到上海2017-4-4到2017-4-6的机票信息

更多功能进一步讨论后再添加...
'''

class Xiecheng(object):
#默认爬取   XMN SHA day1=(2017, 4, 4)-day2 =(2017, 4, 6)
    def __init__(self,city1 ='XMN',city2 ='SHA',day1=(2017, 4, 4),day2 =(2017, 4, 6)):
#爬取单程机票的爬虫 缺少参数依次为（出发城市，到达城市，日期）
        self.init_url = 'http://flights.ctrip.com/domesticsearch/search/SearchFirstRouteFlights?DCity1={DCity1}&ACity1={ACity1}&DDate1={DDate1}'
#初始化爬取的参数
        self.from_city = city1
        self.to_city = city2
        self.st_day = day1
        self.end_day = day2
#作为存储文件的名字
        self.save_name = self.from_city + '-'+self.to_city


#用于返回一个时间list来构造url
    def datelist(self,start, end):
        start_date = datetime.date(*start)
        end_date = datetime.date(*end)

        result = []
        curr_date = start_date
        while curr_date != end_date:
            result.append("%04d-%02d-%02d" % (curr_date.year, curr_date.month, curr_date.day))
            curr_date += datetime.timedelta(1)
        result.append("%04d-%02d-%02d" % (curr_date.year, curr_date.month, curr_date.day))
        return result

#用于构造url的list
    def join_url(self):
        '''
        payload 输入三个参数分别为出发城市，到达城市，出发日期  并构造储存名
        '''
        date_list = self.datelist(self.st_day, self.end_day)

        joinurls = []
        for i in date_list:
            joinurls.append(self.init_url.format(DCity1=self.from_city, ACity1= self.to_city, DDate1=i))

        return joinurls

#抓取函数
    def get_html(self,url):
        USER_AGENT_LIST = [
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36 SE 2.X MetaSr 1.0'

            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
            'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',

            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',

        ]

        user_agent = (random.choice(USER_AGENT_LIST))
        headers = {'User-Agent': user_agent,
                   'Accept': '* / *',
                   'Host': 'flights.ctrip.com',
                   'Referer': 'http://flights.ctrip.com/booking/{}-{}----s-adu-1/?ddate1={}'.format(self.from_city,self.to_city,re.findall(r'DDate1=(.*)', url)[0]),
                    }
        try:
            r = requests.get(url, headers)
            print('成功获取',url)
            return r.text
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            print('Fail to get', url)
            return None
#解析爬取的html（json格式的信息）

#解析函数

    def parse_json(self, html):
        if html:
            info = json.loads(html)
            fis = info['fis']
            info_list = []
            for i in fis:
                slist = []
                slist.append(i['fn'])
                slist.append(str(i['dcn']))
                slist.append(str(i['dpbn']))
                slist.append(str(i['acn']))
                slist.append(str(i['apbn']))
                slist.append(str(i['dt']))
                slist.append(str(i['at']))
                slist.append(str(i['lp']))

                info_list.append(slist)

            self.save_csv(info_list)
            print('存储成功')

        else:
            print('Fail to get info')

#将爬取的数据存储为csv格式

#存储函数

    def save_csv(self,info_list):
        with open(self.save_name, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(info_list)

#构建文件的函数

    def create_csv(self):
        titles = ['fn','dpt_city', 'dpt_airport', 'at_city', 'at_airport', 'dpt_time', 'at_time', 'price']
        with open(self.save_name, 'w',newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(titles)

    async def running(self,url):
        html = self.get_html(url)
        self.parse_json(html)

    def run(self):
        self.create_csv()
        loop = asyncio.get_event_loop()
        urls = self.join_url()
        tasks = [self.running(url) for url in urls]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()
        with open(self.save_name, 'r') as csvfile:
            reader = csv.reader(csvfile)
            rows = [row for row in reader]
        print('总共抓取：', len(rows)-1,'条')

if __name__ == '__main__':
    print(__doc__)
    st = time.time()

    crawler = Xiecheng()
    crawler.run()

    end = time.time()
    print('爬取时间',datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
    print('耗时:',end-st)
