# -*- coding:utf-8 -*-
import requests
# import chardet
import cchardet
import re
import time
import pymysql
from threading import Thread
from queue import Queue
from top_50_article.extractor import Extractor
from top_50_article.filter_keys import clean_content

# 根据关键词下载前50名的链接快照
class Spider_top_50_link(Thread):
    '''
    根据关键词下载前50名的链接快照
    '''
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.58'
    }

    def __init__(self,kw_queue,link_queue):
        super(Spider_top_50_link, self).__init__()
        self.kw_queue = kw_queue
        self.link_queue = link_queue

    def run(self):
        while True:
            try:
                kw = self.kw_queue.get()
                # print('正在下载：{}，源码'.format(kw))
                source = self.download(kw)
                if source is None:
                    continue
                self.extract_links(kw,source)
            finally:
                self.kw_queue.task_done()

    def download(self,kw,retrys=3):
        '''
        下载源码
        :param kw:
        :return:
        '''
        query = 'https://www.baidu.com/s?wd={}&pn=0&ie=utf-8'.format(kw)
        try:
            resp = requests.get(query, headers=self.headers, timeout=15)
        except requests.RequestException as err:
            print('{}:下载异常：{}'.format(query, err))
            html = None
            print('暂停2秒重试!')
            if retrys > 0:
                time.sleep(2)
                return self.download(kw,retrys -1)
        else:
            resp.encoding = 'utf-8'
            html = resp.text
        return html

    def extract_links(self,kw,source):
        '''
        提取链接
        :param kw:
        :param source:
        :return:
        '''
        links = re.compile('<div class="f13  se_st_footer"><a target="_blank" href="(.*?)"').findall(source)
        for url in links:
            url = url.replace('http://','https://')
            self.link_queue.put((kw,url))

# 解析得到的快照链接,获取真实文章url地址
class Decry_url(Thread):
    '''
    解析得到的快照链接,获取真实文章url地址
    '''
    def __init__(self,link_queue,download_queue,filter_url):
        super(Decry_url, self).__init__()
        self.link_queue = link_queue
        self.download_queue = download_queue
        self.filter_url = filter_url

    def run(self):
        while True:
            kw,url = self.link_queue.get()
            self.get_decr_url(kw,url)
            self.link_queue.task_done()

    def get_decr_url(self,kw,url):
        try:
            resp = requests.head(url)
        except requests.RequestException as err:
            print('解析快照链接异常: {}'.format(err))
        else:
            real_url = resp.headers.get('Location')
            for con in self.filter_url:
                if con in real_url:
                    return
            self.download_queue.put((kw, real_url))

# 根据快照解析后的真实地址采集文章
class Download_article(Thread):
    '''
    根据快照解析后的真实地址采集文章
    '''
    headers = {
        'User-Agent':'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)'
    }

    def __init__(self,download_queue,db_config):
        super(Download_article, self).__init__()
        self.download_queue = download_queue
        self.db_config = db_config

    def run(self):
        while True:
            try:
                kw,url = self.download_queue.get()
                source = self.download(kw,url)
                if source is None:
                    continue
                self.extract_content(kw,url,source)
            finally:
                self.download_queue.task_done()

    def download(self,kw,url,retrys=3):
        '''
        下载文章源码
        :param kw:
        :return:
        '''

        html = None
        try:
            resp = requests.get(url, headers=self.headers, timeout=15)
        except requests.RequestException as err:
            html = None
            print('{}:下载文章异常：{}'.format(url, err))

            if retrys > 0:
                return self.download(kw,url,retrys -1)
        else:
            # try:
            #     # 自动识别编码,如果没识别出来编码则返回空值,防止乱码数据
            #     coding = chardet.detect(resp.content)
            #     if (coding['encoding'] != ''):
            #         try:
            #             html = resp.content.decode(str(coding['encoding'].strip()))  # 自动设置网页源码
            #         except AttributeError:
            #             pass
            # except UnicodeDecodeError as err:
            #     html = None
            #     print('解码错误！{}'.format(err))
            # ======================================
            text = resp.content  # 这里返回的是二进制的内容
            encoding = cchardet.detect(text)['encoding']
            if encoding is None:
                encoding = 'gbk'
            html = text.decode(encoding=encoding, errors='ignore')
            # ======================================
        return html

    def extract_content(self,kw,url,source):
        ex = Extractor()
        ex.extract(url,source)

        # 过滤文章,质量不少于10000分, 并且字数超过5000的不要(字数太多,翻译容易出错)
        if ex.score > 10000 and ex.text_count < 5000:
            title = ex.title
            if len(title) > 5 and len(title) < 37:
                # 得到文本源码,并过滤特征词跟网址,并翻译
                print('正在清洗内容过滤...')
                content = clean_content(ex.format_text)

                # text = ex.format_text
                # 将内容进行翻译伪原创
                # content = tran_method(text)


                # 判断翻译结果,不为None时才入库
                if content is not None:
                    print('得到标题：{}'.format(title))
                    # 开始入库
                    try:
                        conn = pymysql.Connect(**self.db_config)
                        try:
                            sql = "insert ignore into top_50_article(keywords,title,content,source) values(%s,%s,%s,%s)"
                            with conn.cursor() as cursor:
                                cursor.execute(sql,args=(kw,title,content,url))
                        except pymysql.err.Error as err:
                            print('插入数据出错，标题：{},url：{},异常：{}'.format(title,url,err))
                        else:
                            conn.commit()
                            conn.close()
                    except pymysql.err.MySQLError:
                        print('链接数据库出错!')

if __name__ == '__main__':
    kw_queue = Queue()
    link_queue = Queue()
    download_queue = Queue()

    # 加载过滤url
    filter_url = []
    for k in open('filter_url.txt', 'r', encoding='utf-8'):
        filter_url.append(k.strip())

    # 数据库配置
    db_config = dict(
        host='localhost',
        user='spider',
        passwd='123456',
        db='spider',
        port=3306,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    for k in open('result.txt', 'r', encoding='utf-8'):
        kw_queue.put(k.strip())

    # 下载快照链接类
    for i in range(15):
        s = Spider_top_50_link(kw_queue, link_queue)
        s.setDaemon(True)
        s.start()

    # 解析快照链接类
    for i in range(15):
        d = Decry_url(link_queue,download_queue,filter_url)
        d.setDaemon(True)
        d.start()

    # 下载文章处理类
    for i in range(10):
        d = Download_article(download_queue,db_config)
        d.setDaemon(True)
        d.start()

    kw_queue.join()
    link_queue.join()
    download_queue.join()
    print('采集结束！')