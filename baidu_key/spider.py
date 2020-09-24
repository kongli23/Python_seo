# -*- coding:utf-8 -*-
import requests
import time
import pymysql
import gc
from threading import Thread
from lxml import etree
from queue import Queue
from pybloom_live import BloomFilter


# 下载类
class Downloads:
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36 Edg/84.0.522.52'
    }
    def download(self,kw,retries=3):
        url = 'https://www.baidu.com/s?wd={}&pn=0&oq={}&tn=baiduhome_pg&ie=utf-8&usm=1&rsv_idx=2&rsv_pq=fc92530f001c53d7&rsv_t=4c7a%2BSikQx8cwZpNbcESt1hDi%2B2x0ceYQGiqkyPCwvTYzBQVLSKl5iOye84LdNhXgTWF'.format(kw,kw)
        try:
            resp = requests.get(url,headers=self.headers,timeout=15)
        except requests.RequestException as err:
            html = None
            print('下载内容异常：{}'.format(err))

            if retries > 0:
                return self.download(kw,retries -1)
                # 如果采集有限制可以在此处添加廷时
                # 出现异常,则一次休眠5秒
                time.sleep(5)
        else:
            resp.encoding = 'utf-8'
            html = resp.text
        return html

# 采集类
class Spider(Thread,Downloads):
    def __init__(self,key_queue,save_queue):
        super(Spider, self).__init__()
        self.key_queue = key_queue  #采集关键词列队
        self.save_queue = save_queue #关键词保存列队
        self.bloom = BloomFilter(capacity=1e7,error_rate=0.001) #关键词重复采集过滤器

    def run(self):
        while True:
            try:
                kw = self.key_queue.get()   #从关键词列队中提取一个

                # 判断采集过滤器中是否已采集，如果有则跳过，没有则添加
                if kw in self.bloom:
                    continue
                self.bloom.add(kw)

                # 开始下载源码
                source = self.download(kw)
                if source is None:
                    continue

                # 开始提取源码中的内容
                self.parse_html(source)

            finally:
                self.key_queue.task_done()  #无论怎样都要把消息队列处理完

    def parse_html(self,source):
        # 相关    //table//tr//th/a/text()
        elt = etree.HTML(source)

        # 相关
        related_list = elt.xpath('//table//tr//th/a/text()')
        for related in related_list:
            self.key_queue.put(related)
            self.save_queue.put(related)

# 保存类
class Save_key(Thread):
    def __init__(self,save_queue,contain,db_config,filename):
        super(Save_key, self).__init__()
        self.save_queue = save_queue    #保存列队
        self.contain = contain  #必须包含词
        self.db_config = db_config    #数据库配置
        self.filename = filename    #保存文件名

    def run(self):
        while True:
            wd = self.save_queue.get()
            for con in self.contain:
                if con in wd:
                    if len(wd) >5:
                        print('得到新词：{}\n'.format(wd))
                        self.save_file(wd)
            self.save_queue.task_done()

    def save_file(self,wd):
        # 方式一：
        try:
            conn = pymysql.Connect(**self.db_config)
            try:
                sql = "insert ignore into sys(keywords) values(%s)"
                with conn.cursor() as cursor:
                    cursor.execute(sql, args=(wd))
            except pymysql.err.Error as err:
                print('插入数据出错，新词：{},异常：{}'.format(wd, err))
            else:
                conn.commit()
                conn.close()
        except pymysql.err.MySQLError:
            print('链接数据库出错!')

        # 方式二：
        # with open(self.filename, mode='a', encoding='utf-8') as f:
        #         f.write('{}\n'.format(wd))

if __name__ == '__main__':
    key_queue = Queue() #关键词采集列队
    save_queue = Queue() #关键词保存列队
    filename = 'result.txt' #保存文件名

    # 向列队中添加初始值
    for k in open('init1.txt', 'r', encoding='utf-8'):
        key_queue.put(k.strip())

    contain = []  # 必须包含词
    for con in open('contain.txt', 'r', encoding='utf-8'):
        contain.append(con.strip())

    # 数据库配置
    db_config = dict(
        host='127.0.0.1',
        user='spider',
        passwd='123456',
        db='spider',
        port=3306,
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )

    # 采集列队,10个线程
    for i in range(10):
        spider = Spider(key_queue,save_queue)
        spider.setDaemon(True)  #设置为背景线程，即程序终止流程即终止
        spider.start()

    # 保存列队,不使用线程,使用线程速度太快,容易出现乱码
    for i in range(5):
        savekey = Save_key(save_queue,contain,db_config,filename)
        savekey.setDaemon(True)
        savekey.start()

    key_queue.join()
    save_queue.join()
    print('采集完成！')