# 默认显示30条数据
#url = 'https://www.baidu.com/s?wd=seo%E6%98%AF%E4%BB%80%E4%B9%88&pn=0&rn=30&ct=1&ie=utf-8'

import requests
from threading import Thread
import re
from queue import Queue
from kw_get_article.extractor import Extractor
import pymysql
from translation.content_fanyi import fanyi_content
from kw_get_article.article_filter import content_filter
import chardet

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
                if is_insert is None:
                    print('关键词：{},标题：**{}**,url：{},入库失败！--->'.format(kw,is_insert,url))
                else:
                    print('关键词：{},入库成功标题：<<<----------{}---------->>>'.format(kw,is_insert))
            finally:
                self.downurl_queue.task_done()

    def download(self,url):

        try:
            requests.packages.urllib3.disable_warnings()  # 忽略urllib3 https警告
            resp = requests.get(url, headers=self.headers, timeout=10)
        except requests.RequestException as err:
            print('{}:下载异常：{}'.format(url, err))
            html = None
        else:
            # 自动识别编码
            coding = chardet.detect(resp.content)
            if (coding['encoding'] != ''):
                html = resp.content.decode(coding['encoding'])  # 自动设置网页源码

        return html

    def extract_content(self,kw,url,source):
        ex = Extractor()
        ex.extract(url, source)

        is_success = None
        # 分值大于 10000 说明文章内容较可观
        # if ex.score > 10000: 网页分值,分数越高说明html内容越足 10000
        # ex.text_count > 300  网页字数
        if ex.text_count > 300:
            title = ex.title.replace("'",'').replace('\\','').replace('?','')
            tag_content = ex.format_text

            # print('标题：{}'.format(title))
            # print('内容：{}'.format(tag_content))

            # 过滤文章,标题长度大于6,小于37 的则保留,太长太短说明质量有问题
            if len(title) > 6 and len(title) < 37:

                print('得到内容,标题：{}，正在伪原创,过滤'.format(title))
                tep_content = fanyi_content(tag_content)
                if tep_content is None:
                    return
                content = content_filter(tep_content)

                print('处理完成,等待入库中...')

                try:
                    conn = pymysql.Connect(**self.dbconfig)
                    try:
                        sql = "insert ignore into article(keywords,title,content) values('{}','{}','{}')".format(kw, title,
                                                                                                                 content)
                        with conn.cursor() as cursor:
                            cursor.execute(sql)
                    except pymysql.err.Error as err:
                        print('数据入库出错，标题：{},url：{},异常：{}'.format(title,url,err))
                    else:
                        conn.commit()
                        conn.close()
                        is_success = title  # 执行成功让它 =标题
                except pymysql.err.MySQLError:
                    pass
            else:
                print('文章标题过短|或过长：抛弃!')
        else:
            print('文章内容不合格：抛弃!')
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
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    for k in open('seo词.txt','r',encoding='utf-8'):
        kw_queue.put(k.strip())

    for i in range(15):
        s = Search_key(kw_queue, link_queue)
        s.setDaemon(True)
        s.start()

    for i in range(15):
        d = Decryption_url(link_queue, downurl_queue)
        d.setDaemon(True)
        d.start()

    for i in range(15):
        down = Down_article(downurl_queue,dbconfig)
        down.setDaemon(True)
        down.start()

    kw_queue.join()
    link_queue.join()
    downurl_queue.join()
    print('结束！')