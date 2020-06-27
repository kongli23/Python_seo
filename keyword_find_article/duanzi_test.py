# -*- coding: utf-8 -*-
from threading import Thread
from urllib import request, error, parse
import re
from socket import timeout


class Budejie(Thread):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/68.0.3440.106 Safari/537.36'
    }

    def __init__(self, url, pase_func):
        self.url = url
        self.parse_fun = pase_func
        self.result = None
        super().__init__()

    def run(self):  # 这个是必须要的，这个方法就是线程调用start方法的时候运行的方法
        html = self.download(self.url)
        if not html:
            return
        self.result = self.parse_fun(html, self.url)

    def download(self, url, encoding='utf-8'):
        """
        下载函数
        :param url:
        :param encoding:
        :return:
        """
        try:
            req = request.Request(url, headers=self.headers)
            resp = request.urlopen(req, timeout=15)
        except (error.HTTPError, error.URLError, timeout) as err:
            print(url, 'download error:', err)
            html = None
        else:
            html = resp.read().decode(encoding)
        return html


def extract(html, base_url):
    """
    解析函数
    :param html:
    :return:
    """
    urls = re.findall(r'<div class="j-r-list-c-desc">.*?'
                      r'<a href="(/detail-\d+\.html)">[^<]+</a>',
                      html, re.S)
    return [parse.urljoin(base_url, url) for url in urls]


def parse_detail(html, url):
    """
    提取详情
    :param html:
    :return:
    """
    print(url)
    h1 = re.findall(r'<h1>([^<]+)</h1>', html)
    print(''.join(h1))


if __name__ == '__main__':
    query = 'http://www.budejie.com/'
    budejie = Budejie(query, extract)
    budejie.start()
    budejie.join()
    details = budejie.result
    for link in details:
        b = Budejie(link, parse_detail)
        b.start()
