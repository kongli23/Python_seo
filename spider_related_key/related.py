import requests
from threading import Thread
from lxml import etree
from queue import Queue
from pybloom_live import BloomFilter

class Downloader:
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36 Edg/83.0.478.54'
    }
    def download(self,kw,retries=3):
        params = {
            'wd':kw,
            'pn':0
        }
        query = 'https://www.baidu.com/s?'
        try:
            resp = requests.get(query,params=params,headers=self.headers,timeout=10)
        except requests.RequestException as err:
            html = None
            print('{}: download err：{}'.format(query,err))

            # 重试次数
            if retries > 0:
                return self.download(kw,retries - 1)
        else:
            resp.encoding = 'utf-8'
            html = resp.text
        return html

class Related_Key(Thread,Downloader):
    def __init__(self,key_queue,save_queue):
        super(Related_Key, self).__init__()
        self.key_queue = key_queue  # 采集列队
        self.save_queue = save_queue    #保存列队
        self.bloom = BloomFilter(capacity=1e7,error_rate=0.001) #过滤器

    def run(self):
        while True:
            try:
                kw = self.key_queue.get()
                # 过滤抓取，如果存在则不抓，不存在则添加进列表并抓取
                if kw in self.bloom:
                    continue
                self.bloom.add(kw)

                # 下载源码
                source = self.download(kw)
                if source is None:
                    continue
                self.parse_html(source)
            finally:
                self.key_queue.task_done()

    def parse_html(self,html):
        ele = etree.HTML(html)
        keyList = ele.xpath('//table//tr//th/a/text()')
        for key in keyList:
            self.key_queue.put(key) #添加采集列队
            self.save_queue.put(key)    #添加保存列队

# 关键词过滤,保存类
class Filter_key(Thread):
    def __init__(self, save_queue,contain,filename):
        super().__init__()
        self.save_queue = save_queue    #保存列队
        self.contain = contain  #必须包含词
        self.filename = filename  # 文件名
        self.bloom = BloomFilter(capacity=1e7,error_rate=0.001)

    def run(self):
        while True:
            wd = self.save_queue.get()
            # 判断是否包含某词
            for con in self.contain:
                if con in wd:

                    # 关键词长度大于4个字才保存
                    if len(wd) > 10:
                        # 符合包含词再进行去重
                        if wd in self.bloom:
                            continue
                        self.bloom.add(wd)
                        print('得到新词：{}'.format(wd))
                        self.save_file(wd)
                        self.save_queue.task_done()

    # 保存文件函数
    def save_file(self,wd):
        with open(self.filename, mode='a', encoding='utf-8') as f:
                f.write('{}\n'.format(wd))

if __name__ == '__main__':
    key_queue = Queue() #采集列队
    save_queue = Queue()    #保存列队
    filename = "result.txt"  # 结果保存文件名

    for k in open('init.txt','r',encoding='utf-8'):
        key_queue.put(k.strip())

    contain = []    #必须包含词
    for con in open('contain.txt','r',encoding='utf-8'):
        contain.append(con.strip())

    # 采集列队,10个线程
    for i in range(15):
        related = Related_Key(key_queue,save_queue)
        related.setDaemon(True)
        related.start()

    # 过滤使用单线程,使用多线程会乱码,占用大量资源
    f = Filter_key(save_queue, contain, filename)
    f.setDaemon(True)
    f.start()

    key_queue.join()
    save_queue.join()
    print('采集结束！')