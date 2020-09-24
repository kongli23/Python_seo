# -*- coding:utf-8 -*-
import requests
import time
from lxml import etree
from threading import Thread
from queue import Queue
from pybloom_live import BloomFilter

# 下载类
class Downloads:
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'referer': 'https://m.sm.cn/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 9; SM-N9500 Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 9)'
    }
    def download(self,kw,retries=3):
        query = 'https://m.sm.cn/s?q={}&from=smor&safe=1&snum=6'.format(kw)
        try:
            resp = requests.get(query, headers=self.headers, timeout=15)
        except requests.RequestException as err:
            html = None
            print('下载异常：{}'.format(err))

            if retries > 0:
                return self.download(kw,retries -1)
                # 出现异常,则一次休眠5秒
                print('休眠中...')
                time.sleep(10)
        else:
            resp.encoding = 'utf-8'
            html = resp.text
        return html

# 采集类
class Spider(Thread,Downloads):
    def __init__(self,key_queue,save_queue):
        super(Spider, self).__init__()
        self.key_queue = key_queue
        self.save_queue = save_queue
        self.bloom = BloomFilter(capacity=1e7,error_rate=0.001) #关键词重复采集过滤器

    def run(self):
        while True:
            try:
                kw = self.key_queue.get()
                if kw in self.bloom:
                    continue
                self.bloom.add(kw)

                source = self.download(kw)
                if source is None:
                    continue

                self.parse_html(source)
            finally:
                self.key_queue.task_done()
            time.sleep(3)   #执行完一次休眠3秒

    def parse_html(self,source):
        # 推荐2   //div[@class="sider-card relative-keywords"]//ul/li/a/p/span/text()
        # 推荐3   //li[@class="c-btn-col-2"]//div/span/span/text()
        elt = etree.HTML(source)
        related_two = elt.xpath('//div[@class="sider-card relative-keywords"]//ul/li/a/p/span/text()')
        for two in related_two:
            self.key_queue.put(two)
            self.save_queue.put(two)

        related_three = elt.xpath('//li[@class="c-btn-col-2"]//div/span/span/text()')
        for three in related_three:
            self.key_queue.put(three)
            self.save_queue.put(three)

class Save_key(Thread):
    def __init__(self,save_queue,contain,filename):
        super(Save_key, self).__init__()
        self.save_queue = save_queue
        self.contain = contain
        self.filename = filename

    def run(self):
        while True:
            try:
                wd = self.save_queue.get()
                for con in self.contain:
                    if con in wd:
                        print('得到新词：{}'.format(wd))
                        self.save_file(wd)
            finally:
                self.save_queue.task_done()

    def save_file(self,wd):
        with open(self.filename,mode='a',encoding='utf-8') as fs:
            fs.write('{}\n'.format(str.strip(wd)))

if __name__ == '__main__':
    key_queue = Queue() #采集列队
    save_queue = Queue() #保存列队
    filename = 'result.txt'

    # 添加起始词
    for key in open('init1.txt', 'r', encoding='utf-8'):
        key_queue.put(key.strip())

    contain = []    #必须包含词列表
    for con in open('contain.txt','r',encoding='utf-8'):
        contain.append(con.strip())

    # 采集列队 10个线程
    for i in range(10):
        spider = Spider(key_queue,save_queue)
        spider.setDaemon(True)
        spider.start()

    # 保存列队 5个线程
    for i in range(5):
        save_key = Save_key(save_queue,contain,filename)
        save_key.setDaemon(True)
        save_key.start()

    key_queue.join()
    save_queue.join()
    print('采集完成!')