# -*- coding: utf-8 -*-
from threading import Thread
from queue import Queue
from urllib import request, error, parse
import json
import time


class CheckIndex(Thread):
    def __init__(self, url_queue):
        super().__init__()
        self.url_queue = url_queue
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/68.0.3440.106 Safari/537.36'
        }

    def run(self):
        while True:
            url = self.url_queue.get()
            html = self.download(url)
            if html is None:
                self.url_queue.task_done()
                continue  # 出错跳过
            self.parser(html, url)
            self.url_queue.task_done()

    def download(self, url):
        query = 'https://www.baidu.com/s?ie=UTF-8&wd={}&tn=json'.format(url)
        try:
            req = request.Request(query, headers=self.headers)
            resp = request.urlopen(req, timeout=10)
        except (error.URLError, error.HTTPError):
            html = None
        else:
            html = resp.read().decode('utf-8')
        return html

    @staticmethod
    def parser(html, base_url):
        try:
            result = json.loads(html)  # 将json数据转为dict
        except ValueError:
            return
        try:
            entry = result['feed']['entry']
        except KeyError:
            return

        for item in entry[:-1]:
            title = item['title']
            url = item['url']
            snapshot = item['time']
            snapshot = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(snapshot))
            if url == base_url:
                print('{}\n{} -- 已索引\n{}\n'.format(title, url, snapshot))
                break
        else:
            print('{} --未收录'.format(base_url))


if __name__ == '__main__':
    q = Queue()
    with open('links.txt') as f:
        for link in f:
            q.put(link.strip())

    for i in range(5):  # 设置10个线程
        c = CheckIndex(q)
        c.setDaemon(True)  # 设置为守护线程，可以随着主线程一起退出
        c.start()
    q.join()  # 等待队列的任务完成
    print('Done.')
