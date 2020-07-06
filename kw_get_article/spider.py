# 默认显示30条数据
#url = 'https://www.baidu.com/s?wd=seo%E6%98%AF%E4%BB%80%E4%B9%88&pn=0&rn=30&ct=1&ie=utf-8'

import requests
from threading import Thread
import re
from queue import Queue
from bluextracter import Extractor
import pymysql

class Search_key(Thread):
    '''
    依据关键词查找快照链接
    '''

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.58'
    }

    def __init__(self,kw_queue,link_queue):
        super(Search_key, self).__init__()
        self.kw_queue = kw_queue    #关键词列队
        self.link_queue = link_queue    #链接列队

    def run(self):
        while True:
            try:
                kw = self.kw_queue.get()
                source = self.download(kw)
                if source is None:
                    continue
                self.parse_html(kw,source)
            finally:
                self.kw_queue.task_done()

    def download(self,kw):
        url = 'https://www.baidu.com/s'
        params = {
            'ie': 'utf-8',
            'f': 8,
            'rsv_bp': 1,
            'tn': 'baidu',
            'wd': kw,
            'rn': 30
        }
        try:
            resp = requests.get(url,params=params, headers=self.headers, timeout=10)
        except requests.RequestException as err:
            print('{}:下载异常：{}'.format(url, err))
            html = None
        else:
            resp.encoding = 'utf-8'
            html = resp.text
        return html

    def parse_html(self,kw,source):
        links = re.compile('<div class="f13  se_st_footer"><a target="_blank" href="(.*?)"').findall(source)
        for url in links:
            url = url.replace('http://','https://')
            self.link_queue.put((kw,url))

class Decryption_url(Thread):
    '''
    解密快照url，返回真实url
    '''
    def __init__(self,link_queue,downurl_queue):
        super(Decryption_url, self).__init__()
        self.link_queue = link_queue
        self.downurl_queue = downurl_queue

    def run(self):
        while True:
            kw,url = self.link_queue.get()
            self.get_decr_url(kw,url)
            self.link_queue.task_done()

    def get_decr_url(self,kw,url):
        try:
            resp = requests.head(url)
        except requests.RequestException as err:
            print('Decrypt url failed: {}'.format(err))
        else:
            real_url = resp.headers.get('Location')
            if 'baidu.com' in real_url:
                return
            self.downurl_queue.put((kw, real_url))

class Down_article(Thread):
    headers = {
        'User-Agent':'Mozilla/5.0 (compatible; Baiduspider-render/2.0; +http://www.baidu.com/search/spider.html)'
    }

    def __init__(self,downurl_queue,dbconfig):
        super(Down_article, self).__init__()
        self.downurl_queue = downurl_queue
        self.dbconfig = dbconfig

    def run(self):
        while True:
            try:
                kw, url = self.downurl_queue.get()
                source = self.download(url)
                if source is None:
                    continue
                # 提取内容
                is_insert = self.extract_content(kw,url,source)
                if is_insert:
                    print('关键词：{} 文章入库成功.'.format(kw))
            finally:
                self.downurl_queue.task_done()

    def download(self,url):

        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
        except requests.RequestException as err:
            print('{}:下载异常：{}'.format(url, err))
            html = None
        else:
            resp.encoding = self.get_encoding(resp.text)
            html = resp.text
        return html

    def get_encoding(self,html):
        encoding = re.findall('<meta.*?charset="?([\w-]*)".*>',html,re.I)
        if encoding:
            return encoding[0]
        return 'utf-8'

    def extract_content(self,kw,url,source):
        ex = Extractor()
        ex.extract(url, source)
        if ex.score > 10000 and len(ex.title) > 10:
            title = ex.title
            content = ex.format_text
            is_success = False

            try:
                conn = pymysql.Connect(**self.dbconfig)
                try:
                    sql = "insert ignore into article(keywords,title,content) values('{}','{}','{}')".format(kw, title,
                                                                                                             content)
                    with conn.cursor() as cursor:
                        cursor.execute(sql)
                except pymysql.err.Error as err:
                    print(err)
                else:
                    is_success = True   #执行成功让它为真
                    conn.commit()
                    conn.close()
            except pymysql.err.MySQLError:
                pass

            return is_success

if __name__ == '__main__':
    kw_queue = Queue() #关键词列队
    link_queue = Queue() #快照链接列队
    downurl_queue = Queue() #下载链接列队

    # 数据库配置
    dbconfig = dict(
        host='localhost',
        user='spider',
        passwd='123456',
        db='spider',
        port=3306,
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )

    for k in open('key.txt','r',encoding='utf-8'):
        kw_queue.put(k.strip())

    for i in range(5):
        s = Search_key(kw_queue, link_queue)
        s.setDaemon(True)
        s.start()

    for i in range(5):
        d = Decryption_url(link_queue, downurl_queue)
        d.setDaemon(True)
        d.start()

    for i in range(10):
        down = Down_article(downurl_queue,dbconfig)
        down.setDaemon(True)
        down.start()

    kw_queue.join()
    link_queue.join()
    downurl_queue.join()
    print('结束！')