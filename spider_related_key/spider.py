import threading
import requests
from queue import Queue
from lxml import etree
import time
from pybloom_live import ScalableBloomFilter, BloomFilter
from spider_related_key.random_ua import random_ua

class Downloader():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': '{}'.format(random_ua())
    }

    def download(self,keys):
        url = 'https://www.baidu.com/s?wd={0}&pn=0'.format(keys)
        try:
            resp = requests.get(url,headers=self.headers, timeout=10)
        except requests.RequestException:
            html = None
        else:
            resp.encoding = 'utf-8'
            html = resp.text
        return html

class Spider_related(threading.Thread,Downloader):
    def __init__(self,keyList_queue,writer,contain):
        super(Spider_related, self).__init__()
        self.keyList_queue = keyList_queue
        self.writer = writer
        self.contain = contain

        # 可自动扩容的布隆过滤器
        self.bloom = ScalableBloomFilter(initial_capacity=100, error_rate=0.001)


    def run(self):
        while True:
            key = self.keyList_queue.get()

            # 过滤重复词,如果它存在seo中就跳过
            if key in self.bloom:
                self.keyList_queue.task_done()
                continue

            # 依据关键词下载当页的源码
            source = self.download(key)
            self.bloom.add(key)    #每采一个就添加一个，用来过滤重复

            # 如果返回的源码为 None则跳过
            if source is None:
                # task_done() 的作用：只有消费者把队列所有的数据处理完毕，queue.join()才会停止阻塞
                self.keyList_queue.task_done()
                continue

            # 解析源码中的新关键词
            self.parse_keyList(source)
            self.writer.flush() #每执行一次刷新一次文件记录
            self.keyList_queue.task_done()

    def parse_keyList(self,source):
        ele = etree.HTML(source)
        keyList = ele.xpath('//table//tr//th/a/text()')
        for key in keyList:

            for con in self.contain:
                if con in key:
                    if key in self.bloom:
                        return
                    else:
                        self.writer.write('{}\n'.format(key))
                        self.keyList_queue.put(key)
                        print('新词：{}'.format(key))

if __name__ == '__main__':
    init = []
    with open('init.txt','r',encoding='utf-8') as file:
        for key in file:
            init.append(key.strip())

    contain = []
    with open('contain.txt','r',encoding='utf-8') as file:
        for key in file:
            contain.append(key.strip())

    keyList_queue = Queue()

    for ini in init:
        keyList_queue.put(ini)

    sf = open('spider_key.txt',mode='w',encoding='utf-8')
    for i in range(15):
        related = Spider_related(keyList_queue,sf,contain)
        related.setDaemon(True)
        related.start()
        time.sleep(0.1)

    keyList_queue.join()
    sf.close()
    print('采集完毕！')