# -*- coding:utf-8 -*-
import requests
import time
from threading import Thread
from pybloom_live import BloomFilter
from lxml import etree
from queue import Queue

# 下载类
class Downloads:
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/85.0.4183.102'
    }
    def download(self,kw,retry=3):
        try:
            url = 'https://m.baidu.com/s?word={}'.format(kw)
            resp = requests.get(url,headers=self.headers,timeout=15)
        except requests.RequestException as err:
            html = None
            print('下载异常：{}'.format(err))
            if(retry > 3):
                return self.download(kw,retry -1)
        else:
            resp.encoding = 'utf-8'
            html = resp.text
        return html

class Spider(Thread,Downloads):
    def __init__(self,key_queue,save_queue):
        super(Spider, self).__init__()
        self.key_queue = key_queue
        self.save_queue = save_queue
        self.boom = BloomFilter(capacity=1e7,error_rate=0.001) #关键词重复采集过滤器

    def run(self):
        while True:
            try:
                kw = self.key_queue.get()
                # 如果存在采集过滤器中就跳过
                if kw in self.boom:
                    continue
                # 否则添加进采集过滤器中
                self.boom.add(kw)

                source = self.download(kw)
                if source is None:
                    continue
                self.parse_html(source)

                # 处理完一次，休眠3秒
                time.sleep(3)
            finally:
                self.key_queue.task_done()

    def parse_html(self,source):
        ele = etree.HTML(source)
        searchList = ele.xpath('//div[@class="c-row row-item row-item2"]/div/a/span/text()')
        for search in searchList:
            # print('{}'.format(search))
            self.key_queue.put(search)
            self.save_queue.put(search)

        relatedList = ele.xpath('//div[@class="rw-list-new rw-list-new2"]/a/span/text()')
        for related in relatedList:
            # print('{}'.format(related))
            self.key_queue.put(related)
            self.save_queue.put(related)

class Sava_key(Thread):
    def __init__(self,save_queue,filename):
        super(Sava_key, self).__init__()
        self.save_queue = save_queue
        self.filename = filename
        self.boom = BloomFilter(capacity=1e7,error_rate=0.001)

    def run(self):
        while True:
            try:
                kw = save_queue.get()
                if '实验室' in kw:
                    # 保存过的词过滤掉
                    if kw in self.boom:
                        continue
                    self.boom.add(kw)

                    print('新词：{}'.format(kw))
                    self.sava_txt(kw)
            finally:
                self.save_queue.task_done()

    def sava_txt(self,kw):
        with open(self.filename,'a',encoding='utf-8') as fs:
            fs.write('{}\n'.format(kw))


if __name__ == '__main__':
    key_queue = Queue()
    save_queue = Queue()
    filename = 'baidu_wap.txt'

    for fs in open('wap.txt','r',encoding='utf-8'):
        key_queue.put(str.strip(fs))

    for i in range(5):
        spider = Spider(key_queue,save_queue)
        spider.setDaemon(True)
        spider.start()

    # 保存使用单线程
    save_key = Sava_key(save_queue,filename)
    save_key.setDaemon(True)
    save_key.start()

    key_queue.join()
    save_queue.join()
    print('采集结束!')