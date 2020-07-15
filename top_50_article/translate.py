# -*- coding:utf-8 -*-
import re
from threading import Thread
from queue import Queue
from top_50_article.google import google
from top_50_article.baidu import baidu

new_text = []
class translate(Thread):
    def __init__(self,p_queue):
        super(translate, self).__init__()
        self.p_queue = p_queue

    def run(self):
        while True:
            try:
                text = self.p_queue.get()

                # 开始谷歌翻译
                g_text = google(text)
                if g_text is None:
                    continue

                # 开始百度翻译
                b_text = baidu(g_text)
                if b_text is None:
                    continue

                # 添加到结果集
                new_text.append(r'<p>{}</p>'.format(b_text))
            finally:
                self.p_queue.task_done()

def start_translate(text):
    q_queue = Queue()
    # 提取段落
    exp = re.compile(r'<p>([^>]+)</p>', re.I | re.S)
    # 提取文章段落
    sentences = exp.findall(text)
    for p in sentences:
        q_queue.put(p)

    for i in range(5):
        ts = translate(q_queue)
        ts.setDaemon(True)
        ts.start()

    q_queue.join()
    source =', '.join(new_text)
    return source